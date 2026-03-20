from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.postgres import Base

from .user import User


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    file_type = Column(String(50))
    content_text = Column(Text, nullable=True)
    file_url = Column(String, nullable=True)

    # Ingestion Status
    status = Column(String(50), default="processing")
    task_id = Column(String(255), nullable=True)

    # Graph Building Status
    graph_status = Column(
        String(50), default="pending"
    )  # pending, building, completed, failed

    error_message = Column(Text, nullable=True)
    uploaded_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user = relationship(User)
    concepts = relationship(
        "Concept", back_populates="document", cascade="all, delete-orphan"
    )


class Concept(Base):
    __tablename__ = "concepts"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), index=True)
    name = Column(String(255), nullable=False)
    definition = Column(Text, nullable=False)
    context_index = Column(String(255))

    document = relationship("Document", back_populates="concepts")
    sm2_progress = relationship(
        "SM2Progress", back_populates="concept", cascade="all, delete-orphan"
    )
