from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.models.document import Document, Concept
from app.services.graph_svc import GraphService
from app.services.ingestion_svc import IngestionService
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

    if not document.content_text:
        raise HTTPException(status_code=400, detail="Document content is empty")

    # 2. Chunk the entire document to respect LLM context limits
    print("Chunking document text for AI processing...")
    chunks = IngestionService.chunk_text(document.content_text, chunk_size=1000)
    all_concepts_data = []

    # Process each chunk sequentially
    for index, chunk in enumerate(chunks):
        print(f"Extracting concepts from chunk {index + 1}/{len(chunks)}...")
        concepts_data = GraphService.extract_concepts_from_chunk(chunk)
        if concepts_data:
            all_concepts_data.extend(concepts_data)

    if not all_concepts_data:
        raise HTTPException(
            status_code=500,
            detail="Failed to extract concepts via AI from the document.",
        )

    # 3. Save Concepts to Postgres and deduplicate
    print("Deduplicating and saving concepts to Postgres...")
    seen_concept_names = set()
    saved_concepts = []

    for c_data in all_concepts_data:
        c_name = c_data.get("concept", "Unknown").strip()

        # Skip empty names or duplicates
        if c_name not in seen_concept_names and c_name != "Unknown" and c_name:
            new_concept = Concept(
                document_id=document.id,
                name=c_name,
                definition=c_data.get("definition", ""),
                context_index=c_data.get("context_index", ""),
            )
            db.add(new_concept)
            saved_concepts.append(new_concept)
            seen_concept_names.add(c_name)

    db.commit()
    print(f"Saved {len(saved_concepts)} unique concepts to Database.")

    # 4. Resolve Dependencies via AI using the unique list
    concept_names = [c.name for c in saved_concepts]
    dependencies = GraphService.resolve_dependencies(concept_names)

    # 5. Save to Neo4j and sort topologically
    GraphService.save_concepts_to_neo4j(document_id, dependencies)
    topological_order = GraphService.build_and_sort_graph(dependencies)

    print("Knowledge Graph build completed successfully.")

    return GraphBuildResponse(
        message="Graph built successfully",
        total_concepts=len(saved_concepts),
        dependencies_found=len(dependencies),
        topological_order=topological_order,
    )
