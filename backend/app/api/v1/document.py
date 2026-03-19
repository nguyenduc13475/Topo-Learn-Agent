import os
import re

import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.core.celery_app import celery_app
from app.core.rate_limit import limiter
from app.db.neo4j import neo4j_conn
from app.models.document import Document
from app.services.ingestion_svc import process_document_task
from app.services.s3_svc import s3_service

router = APIRouter()
UPLOAD_DIR = "data/uploads"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB limit
ALLOWED_MIMES = {
    "application/pdf": "pdf",
    "video/mp4": "video",
    "video/x-m4v": "video",
}


@limiter.limit("5/minute")
@router.post("/upload")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Securely upload document linked to current user with size and MIME validation."""
    if file.content_type not in ALLOWED_MIMES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type. Only PDF and MP4 are allowed.",
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    # Strictly sanitize the filename to prevent path traversal attacks
    clean_name = re.sub(r"[^a-zA-Z0-9_\-\.]", "", file.filename)
    safe_filename = f"{os.urandom(8).hex()}_{clean_name}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    file_size = 0
    try:
        # Stream file to disk to prevent loading large files entirely into RAM
        async with aiofiles.open(file_path, "wb") as out_file:
            while chunk := await file.read(1024 * 1024):  # Read in 1MB chunks
                file_size += len(chunk)
                if file_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="File exceeds the 50MB limit.",
                    )
                await out_file.write(chunk)
    except Exception as e:
        # Guarantee cleanup of partial file stream if limits trigger or client
        # disconnects
        if os.path.exists(file_path):
            os.remove(file_path)
        raise e

    file_type = ALLOWED_MIMES[file.content_type]

    new_doc = Document(
        user_id=current_user["user_id"],
        title=file.filename,
        file_type=file_type,
        status="processing",
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    task = process_document_task.delay(new_doc.id, file_path)
    new_doc.task_id = task.id
    db.commit()

    return {"id": new_doc.id, "title": new_doc.title, "status": new_doc.status}


@router.get("/")
def get_documents(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    """Fetch only documents belonging to the user."""
    docs = (
        db.query(Document)
        .filter(Document.user_id == current_user["user_id"])
        .order_by(Document.uploaded_at.desc())
        .limit(100)  # Added pagination limit for safety
        .all()
    )
    return docs


@router.get("/{document_id}/status")
def get_document_status(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    doc = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user["user_id"])
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"id": doc.id, "status": doc.status, "error_message": doc.error_message}


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Delete a document and trigger cascade delete for concepts/graphs across DBs."""
    print(f"[API] User {current_user['user_id']} deleting document {document_id}")

    doc = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user["user_id"])
        .first()
    )

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete files on S3 to save space
    if doc.file_url:
        s3_service.delete_file(doc.file_url)

    # Prevent wasted GPU resources if task is still running
    if doc.status == "processing" and doc.task_id:
        celery_app.control.revoke(doc.task_id, terminate=True)
        print(
            f"[API] Revoked Celery ML task {doc.task_id} for deleted document {document_id}"
        )

    # Delete from PostgreSQL (Cascades to Concepts and SM2Progress automatically)
    # We do this FIRST to ensure our primary source of truth is updated safely.
    db.delete(doc)
    db.commit()

    # Delete associated nodes in Neo4j Graph Database
    try:
        with neo4j_conn.get_session() as session:
            session.run(
                "MATCH (n:Concept {document_id: $doc_id}) DETACH DELETE n",
                doc_id=document_id,
            )
        print(f"[API] Successfully purged Neo4j nodes for document {document_id}")
    except Exception as e:
        print(f"[API] Error deleting Neo4j nodes: {e}")
        # In a larger scale, we would queue a Celery retry task here to prevent
        # orphaned nodes.

    return {"message": "Document and associated graph deleted successfully"}
