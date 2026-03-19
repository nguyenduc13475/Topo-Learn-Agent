import json

import redis
from pydantic import BaseModel

from app.ai_modules.llm.gemini_client import gemini_client
from app.ai_modules.llm.prompts import (
    CONCEPT_EXTRACTION_SYSTEM_PROMPT,
    DEPENDENCY_RESOLUTION_SYSTEM_PROMPT,
)
from app.core.celery_app import celery_app
from app.core.config import settings
from app.db.postgres import SessionLocal
from app.models.document import Concept, Document
from app.services.graph_svc import GraphService
from app.services.ingestion_svc import IngestionService

redis_client = redis.from_url(settings.CELERY_BROKER_URL)


def publish_graph_event(user_id: int, document_id: int, status: str, error: str = None):
    """
    A helper function for packaging messages and sending them via Redis Pub/Sub.
    The frontend will receive this event via WebSocket.
    """
    payload = {"document_id": document_id, "status": status}
    if error:
        payload["error"] = error

    message = {"user_id": user_id, "event": "GRAPH_STATUS_UPDATED", "payload": payload}
    # Shoot into the "user_notifications" channel that ws_manager is listening on.
    redis_client.publish("user_notifications", json.dumps(message))


# Define strict Pydantic schemas for Gemini
class ConceptExtractionItem(BaseModel):
    concept: str
    definition: str
    context_index: str


class ConceptExtractionList(BaseModel):
    concepts: list[ConceptExtractionItem]


class DependencyItem(BaseModel):
    source_id: int
    target_id: int
    relation: str


class DependencyList(BaseModel):
    dependencies: list[DependencyItem]


@celery_app.task(bind=True, name="build_knowledge_graph_task")
def build_knowledge_graph_task(self, document_id: int):
    print(
        f"[Celery] Starting async knowledge graph build for document ID: {document_id}"
    )
    db = SessionLocal()

    document = db.query(Document).filter(Document.id == document_id).first()
    if not document or not document.content_text:
        db.close()
        return

    try:
        document.graph_status = "building"
        db.commit()

        # 1. Chunking: 4000 words to utilize Gemini 1.5 Flash's long context and
        # reduce API calls, while safely avoiding the 8k structured output token
        # limit.
        chunks = IngestionService.chunk_text(
            document.content_text, max_words_per_chunk=4000
        )
        all_concepts_data = []

        # 2. Extract Concepts sequentially
        for chunk in chunks:
            prompt = f"Extract concepts from the following text:\n\n{chunk}"
            result_dict = gemini_client.generate_structured_output(
                prompt=prompt,
                response_schema=ConceptExtractionList,
                system_instruction=CONCEPT_EXTRACTION_SYSTEM_PROMPT,
            )
            if "concepts" in result_dict:
                all_concepts_data.extend(result_dict["concepts"])

        # 3. Save to DB (Deduplication)
        seen_concept_names = set()
        saved_concepts = []
        for c_data in all_concepts_data:
            c_name_raw = c_data.get("concept", "Unknown").strip()
            c_name_lower = c_name_raw.lower()

            # Use case-insensitive check to prevent Neo4j duplicate nodes
            if (
                c_name_lower not in seen_concept_names
                and c_name_lower != "unknown"
                and c_name_raw
            ):
                new_concept = Concept(
                    document_id=document.id,
                    name=c_name_raw,  # Preserve original casing for the UI
                    definition=c_data.get("definition", ""),
                    context_index=c_data.get("context_index", ""),
                )
                db.add(new_concept)
                saved_concepts.append(new_concept)
                seen_concept_names.add(c_name_lower)
        db.commit()

        # 4. Resolve Dependencies in BATCHES to prevent JSON Output Truncation
        # limit. INJECT DEFINITION so the LLM doesn't hallucinate dependencies
        # based on names alone
        concept_list = [
            {
                "id": c.id,
                "name": c.name,
                "definition": (
                    c.definition[:200] + "..."
                    if len(c.definition) > 200
                    else c.definition
                ),
            }
            for c in saved_concepts
        ]
        dependencies = []

        batch_size = 30  # Safe limit for output token generation
        for i in range(0, len(concept_list), batch_size):
            batch = concept_list[i : i + batch_size]
            prompt = (
                f"Determine prerequisites ONLY for these target concepts: {batch}. "
                f"You may choose prerequisites from the full list of available concepts here: {concept_list}. "
                f"Ensure you use the exact integer IDs provided in the JSON."
            )
            deps_dict = gemini_client.generate_structured_output(
                prompt=prompt,
                response_schema=DependencyList,
                system_instruction=DEPENDENCY_RESOLUTION_SYSTEM_PROMPT,
            )
            dependencies.extend(deps_dict.get("dependencies", []))

        # Sanitize to absolutely guarantee no hallucinated IDs slip into Neo4j
        valid_ids = {c.id for c in saved_concepts}
        unique_edges = set()
        sanitized_dependencies = []
        for dep in dependencies:
            try:
                # Force cast to int in case the LLM returns string IDs
                src_id = int(dep.get("source_id"))
                tgt_id = int(dep.get("target_id"))
            except (TypeError, ValueError):
                continue

            if src_id in valid_ids and tgt_id in valid_ids:
                edge = (src_id, tgt_id)
                # Prevent AI-hallucinated self-loops and duplicate edges
                if edge not in unique_edges and src_id != tgt_id:
                    unique_edges.add(edge)
                    sanitized_dependencies.append(
                        {"source_id": src_id, "target_id": tgt_id}
                    )

        # 5. Cycle Detection to prevent Neo4j / Recommendation infinite loops
        dag_check_format = [
            {"source": dep["source_id"], "target": dep["target_id"]}
            for dep in sanitized_dependencies
        ]
        sorted_concepts = GraphService.build_and_sort_graph(dag_check_format)

        if not sorted_concepts and len(sanitized_dependencies) > 0:
            print(
                "[Celery] Warning: LLM hallucinated a cyclic dependency graph. Stripping edges to prevent infinite loops."
            )
            sanitized_dependencies = []

        # 6. Save to Neo4j
        GraphService.save_concepts_to_neo4j(document_id, sanitized_dependencies)

        # Mark as complete
        document.graph_status = "completed"
        db.commit()
        print(f"[Celery] Graph build completed for document {document_id}.")
        publish_graph_event(document.user_id, document.id, "completed")

    except Exception as e:
        print(f"[Celery] Error building graph for document {document_id}: {e}")
        db.rollback()
        document.graph_status = "failed"
        document.error_message = str(e)
        db.commit()
        publish_graph_event(document.user_id, document.id, "failed", str(e))
    finally:
        db.close()
