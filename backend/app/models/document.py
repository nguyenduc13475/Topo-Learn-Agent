from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.postgres import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    file_type = Column(String(50))  # e.g., 'pdf', 'video'
    content_text = Column(
        Text, nullable=False
    )  # The concatenated string of the entire document
    uploaded_at = Column(DateTime, default=datetime.now(timezone.utc))

    # Relationships
    concepts = relationship(
        "Concept", back_populates="document", cascade="all, delete-orphan"
    )


class Concept(Base):
    __tablename__ = "concepts"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    name = Column(String(255), nullable=False)
    definition = Column(Text, nullable=False)
    context_index = Column(String(255))  # Location in the document

    # Relationships
    document = relationship("Document", back_populates="concepts")
    sm2_progress = relationship(
        "SM2Progress", back_populates="concept", cascade="all, delete-orphan"
    )
