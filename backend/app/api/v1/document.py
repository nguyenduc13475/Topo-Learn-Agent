from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import os
import shutil

from app.api.dependencies import get_db
from app.services.ingestion_svc import IngestionService
from app.schemas.document_schema import DocumentResponse
from app.models.document import Document

router = APIRouter()
UPLOAD_DIR = "data/uploads"


@router.post("/upload", response_model=DocumentResponse)
def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a document (PDF/Video), extract its content, and save to Postgres.
    """
    print(f"Received file: {file.filename}")

    # 1. Save file locally
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. Process based on file type
    content_text = ""
    file_type = "unknown"

    if file.filename.endswith(".pdf"):
        file_type = "pdf"
        content_text = IngestionService.process_pdf_document(file_path)
    elif file.filename.endswith(".mp4"):
        file_type = "video"
        content_text = IngestionService.process_video_document(file_path)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # 3. Save metadata and full text to Postgres
    new_doc = Document(
        title=file.filename, file_type=file_type, content_text=content_text
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    print(f"Document saved with ID: {new_doc.id}")
    return new_doc
