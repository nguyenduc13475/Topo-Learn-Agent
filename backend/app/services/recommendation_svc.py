from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from app.db.neo4j import neo4j_conn
from app.models.sm2_progress import SM2Progress
from app.models.document import Concept


class RecommendationService:
    @staticmethod
    def get_next_concept_to_study(
        user_id: int, document_id: int, db: Session
    ) -> Optional[Dict[str, Any]]:
        """
        Determine the next optimal concept for the user to study based on SM-2 progress
        and the Knowledge Graph dependencies (Production Version).
        """
        print(
            f"Calculating next concept for user {user_id} in document {document_id}..."
        )

        # 1. Check Postgres for concepts that are due for review (Spaced Repetition priority)
        current_time = datetime.now(timezone.utc)
        due_progress = (
            db.query(SM2Progress)
            .join(Concept)
            .filter(
                SM2Progress.user_id == user_id,
                Concept.document_id == document_id,
                SM2Progress.next_review_date <= current_time,
            )
            .order_by(SM2Progress.next_review_date.asc())
            .first()
        )

        if due_progress:
            print(f"Found concept due for review: ID {due_progress.concept_id}")
            concept = (
                db.query(Concept).filter(Concept.id == due_progress.concept_id).first()
            )
            if concept:
                return {
                    "id": concept.id,
                    "name": concept.name,
                    "definition": concept.definition,
                    "context_index": concept.context_index,
                    "reason": "review_due",
                }

        # 2. Query Neo4j to find the next unlearned concept in the Dependency Graph
        session = neo4j_conn.get_session()
        unlearned_concept_name = None
        try:
            # Cypher Query Logic (Production):
            # 1. Find all concepts in this document.
            # 2. Filter out concepts the user has already learned.
            # 3. Find their prerequisite concepts.
            # 4. Only select concepts where ALL their prerequisites exist in the 'learned_concepts' list (or they have no prerequisites).
            query = """
            MATCH (target:Concept {document_id: $doc_id})
            WHERE NOT target.name IN $learned_concepts
            OPTIONAL MATCH (prereq:Concept)-[:REQUIRES]->(target)
            WITH target, collect(prereq.name) AS prerequisites
            // prerequisites = [null] means it has no prerequisites (root node)
            WHERE prerequisites = [null] OR all(p IN prerequisites WHERE p IN $learned_concepts)
            RETURN target.name AS concept_name
            ORDER BY size(prerequisites) ASC
            LIMIT 1
            """

            # Fetch learned concepts from Postgres
            learned_records = (
                db.query(Concept)
                .join(SM2Progress)
                .filter(
                    SM2Progress.user_id == user_id, Concept.document_id == document_id
                )
                .all()
            )
            learned_concepts = [c.name for c in learned_records]
            print(f"User has learned {len(learned_concepts)} concepts so far.")

            result = session.run(
                query, doc_id=document_id, learned_concepts=learned_concepts
            )
            record = result.single()

            if record:
                unlearned_concept_name = record["concept_name"]
                print(f"Next optimal concept found in Graph: {unlearned_concept_name}")
            else:
                print(
                    "No unlearned concepts with fulfilled prerequisites found. Course might be completed."
                )
        except Exception as e:
            print(f"Error querying Knowledge Graph: {e}")
        finally:
            session.close()

        # 3. Fetch from Postgres and return
        if unlearned_concept_name:
            next_concept = (
                db.query(Concept)
                .filter(
                    Concept.name == unlearned_concept_name,
                    Concept.document_id == document_id,
                )
                .first()
            )
            if next_concept:
                return {
                    "id": next_concept.id,
                    "name": next_concept.name,
                    "definition": next_concept.definition,
                    "context_index": next_concept.context_index,
                    "reason": "new_learning",
                }

        return None
