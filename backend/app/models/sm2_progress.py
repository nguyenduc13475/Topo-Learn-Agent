from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.postgres import Base


class SM2Progress(Base):
    __tablename__ = "sm2_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=False)

    # SM-2 Algorithm variables
    repetitions = Column(Integer, default=0)
    interval = Column(Integer, default=1)
    easiness_factor = Column(Float, default=2.5)

    next_review_date = Column(DateTime, default=datetime.utcnow)
    last_reviewed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    concept = relationship("Concept", back_populates="sm2_progress")
