from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, Integer
from sqlalchemy.orm import relationship

from app.db.postgres import Base


class SM2Progress(Base):
    __tablename__ = "sm2_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=False, index=True)

    # SM-2 Algorithm variables
    repetitions = Column(Integer, default=0)
    interval = Column(Integer, default=1)
    easiness_factor = Column(Float, default=2.5)

    next_review_date = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
    last_reviewed_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    concept = relationship("Concept", back_populates="sm2_progress")

    # Composite index to instantly find due reviews for a specific user
    __table_args__ = (
        Index("ix_sm2_user_next_review", "user_id", "next_review_date"),
        Index("ix_sm2_user_concept", "user_id", "concept_id", unique=True),
    )
