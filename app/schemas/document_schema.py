from pydantic import BaseModel
from datetime import datetime


class DocumentBase(BaseModel):
    title: str
    file_type: str


class DocumentCreate(DocumentBase):
    pass


class DocumentResponse(DocumentBase):
    id: int
    uploaded_at: datetime

    class Config:
        from_attributes = True  # Allow ORM mapping
