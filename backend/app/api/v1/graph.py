from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.db.neo4j import neo4j_conn
from app.models.document import Concept, Document
from app.models.sm2_progress import SM2Progress
from app.services.graph_tasks import build_knowledge_graph_task

router = APIRouter()


@router.post("/{document_id}/build")
def trigger_knowledge_graph_build(document_id: int, db: Session = Depends(get_db)):
    """
    Trigger the background extraction of concepts and dependencies.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.status != "completed":
        raise HTTPException(
            status_code=400, detail="Document ingestion is not complete yet."
        )

    if document.graph_status == "building":
        return {"message": "Graph is already building", "status": "building"}

    # Trigger Celery Task
    build_knowledge_graph_task.delay(document_id)

    document.graph_status = "building"
    db.commit()

    return {"message": "Graph build triggered successfully", "status": "building"}


@router.get("/{document_id}/status")
def get_graph_status(document_id: int, db: Session = Depends(get_db)):
    """Check the status of the graph building process."""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": document.graph_status}


@router.get("/concepts/{concept_id}")
def get_concept_details(
    concept_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Fetch concept details for the learning page."""
    concept = (
        db.query(Concept)
        .join(Document)
        .filter(Concept.id == concept_id, Document.user_id == current_user["user_id"])
        .first()
    )

    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")

    return {
        "id": concept.id,
        "name": concept.name,
        "definition": concept.definition,
        "context_index": concept.context_index,
        "document_id": concept.document_id,
        "file_url": concept.document.file_url,
        "file_type": concept.document.file_type,
    }


@router.get("/{document_id}/flow")
def get_knowledge_graph_flow(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Fetch nodes and edges formatted for React Flow."""
    # Verify ownership
    doc = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user["user_id"])
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # 1. Get all concepts from Postgres (to get definitions and IDs)
    concepts = db.query(Concept).filter(Concept.document_id == document_id).all()
    concept_map = {c.id: {"id": c.id, "name": c.name} for c in concepts}

    # Fetch user's learned progress
    progress_records = (
        db.query(SM2Progress)
        .filter(
            SM2Progress.user_id == current_user["user_id"],
            SM2Progress.concept_id.in_([c.id for c in concepts]),
        )
        .all()
    )
    mastered_ids = [
        p.concept_id
        for p in progress_records
        if p.easiness_factor > 1.3 and p.repetitions > 0
    ]

    # 2. Query Neo4j for edges & Calculate Prerequisite Map
    session = neo4j_conn.get_session()
    edges = []
    prereqs_map = {c.id: [] for c in concepts}
    try:
        query = """
        MATCH (s:Concept {document_id: $doc_id})-[:IS_PREREQUISITE_OF]->(t:Concept {document_id: $doc_id})
        RETURN s.id AS source_id, t.id AS target_id
        """
        result = session.run(query, doc_id=document_id)
        for record in result:
            source_id = record["source_id"]
            target_id = record["target_id"]
            if source_id in concept_map and target_id in concept_map:
                prereqs_map[target_id].append(source_id)
                edges.append(
                    {
                        "id": f"e{source_id}-{target_id}",
                        "source": str(source_id),
                        "target": str(target_id),
                        "animated": True,
                    }
                )
    finally:
        session.close()

    # 3. Format Nodes for React Flow (Enforcing Dependencies)
    nodes = []
    for c in concepts:
        if c.id in mastered_ids:
            status = "completed"
        else:
            # A node is 'current' (unlocked) ONLY if ALL of its strict
            # prerequisites are mastered
            my_prereqs = prereqs_map.get(c.id, [])
            if all(p in mastered_ids for p in my_prereqs):
                status = "current"
            else:
                status = "locked"

        nodes.append(
            {
                "id": str(c.id),
                "type": "concept",
                "position": {"x": 0, "y": 0},
                "data": {"label": c.name, "status": status},
            }
        )

    return {"nodes": nodes, "edges": edges}
