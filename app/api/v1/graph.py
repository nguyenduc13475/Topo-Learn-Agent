from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.models.document import Document, Concept
from app.services.graph_svc import GraphService
from app.schemas.graph_schema import GraphBuildResponse

router = APIRouter()


@router.post("/{document_id}/build", response_model=GraphBuildResponse)
def build_knowledge_graph(document_id: int, db: Session = Depends(get_db)):
    """
    Trigger the extraction of concepts and dependencies from a specific document,
    then save the structure to Neo4j and Postgres.
    """
    print(f"Starting knowledge graph build for document ID: {document_id}")

    # 1. Fetch document from Postgres
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # 2. Extract concepts (using mock chunking for now)
    # In a real scenario, you would chunk document.content_text properly
    text_chunk = document.content_text[:1000]
    concepts_data = GraphService.extract_concepts_from_chunk(text_chunk)

    if not concepts_data:
        raise HTTPException(status_code=500, detail="Failed to extract concepts via AI")

    # 3. Save Concepts to Postgres
    saved_concepts = []
    for c_data in concepts_data:
        new_concept = Concept(
            document_id=document.id,
            name=c_data.get("concept", "Unknown"),
            definition=c_data.get("definition", ""),
            context_index=c_data.get("context_index", ""),
        )
        db.add(new_concept)
        saved_concepts.append(new_concept)

    db.commit()

    # 4. Resolve Dependencies via AI
    concept_names = [c.name for c in saved_concepts]
    dependencies = GraphService.resolve_dependencies(concept_names)

    # 5. Save to Neo4j and sort
    GraphService.save_concepts_to_neo4j(document_id, dependencies)
    topological_order = GraphService.build_and_sort_graph(dependencies)

    print("Knowledge Graph build completed successfully.")

    return GraphBuildResponse(
        message="Graph built successfully",
        total_concepts=len(saved_concepts),
        dependencies_found=len(dependencies),
        topological_order=topological_order,
    )
