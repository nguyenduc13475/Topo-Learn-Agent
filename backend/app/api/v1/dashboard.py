from typing import List

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.api.dependencies import get_current_user, get_db
from app.models.document import Concept, Document
from app.models.sm2_progress import SM2Progress

router = APIRouter()


class SearchResult(BaseModel):
    id: int
    name: str
    document_name: str
    definition_snippet: str


@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    """
    Fetch real-time statistics for the user's dashboard.
    """
    user_id = current_user["user_id"]

    # 1. Count analyzed documents
    analyzed_docs = (
        db.query(Document)
        .filter(Document.user_id == user_id, Document.status == "completed")
        .count()
    )

    # 2. Count concepts in review (SM-2 progress records)
    review_concepts = (
        db.query(SM2Progress).filter(SM2Progress.user_id == user_id).count()
    )

    # 3. Calculate average score based on SM-2 Easiness Factor (Mapped roughly
    # to 5.0 scale) EF usually starts at 2.5 and goes up. We'll normalize it for
    # display.
    avg_ef = (
        db.query(func.avg(SM2Progress.easiness_factor))
        .filter(SM2Progress.user_id == user_id)
        .scalar()
        or 2.5
    )

    # Normalize EF to a 0-5 score (assuming max EF is around 3.5 for a "perfect" streak)
    average_score = round(min((avg_ef / 3.0) * 5.0, 5.0), 1)

    # 4. Get the most urgent concept to review globally
    due_progress = (
        db.query(SM2Progress)
        .filter(
            SM2Progress.user_id == user_id, SM2Progress.next_review_date <= func.now()
        )
        .order_by(SM2Progress.next_review_date.asc())
        .first()
    )

    next_concept = None
    if due_progress:
        concept = (
            db.query(Concept).filter(Concept.id == due_progress.concept_id).first()
        )
        if concept:
            doc = db.query(Document).filter(Document.id == concept.document_id).first()
            next_concept = {
                "id": concept.id,
                "name": concept.name,
                "document_name": doc.title if doc else "Unknown Document",
            }
    else:
        # Fallback to the latest document if no reviews are due
        latest_doc = (
            db.query(Document)
            .filter(Document.user_id == user_id, Document.status == "completed")
            .order_by(Document.uploaded_at.desc())
            .first()
        )
        if latest_doc:
            from app.services.recommendation_svc import RecommendationService

            rec = RecommendationService.get_next_concept_to_study(
                user_id=user_id, document_id=latest_doc.id, db=db
            )
            if rec:
                next_concept = {
                    "id": rec["id"],
                    "name": rec["name"],
                    "document_name": latest_doc.title,
                }

    return {
        "analyzed_docs": analyzed_docs,
        "review_concepts": review_concepts,
        "average_score": str(average_score),
        "learning_streak": "Active",
        "next_concept": {
            "id": next_concept["id"] if next_concept else None,
            "name": next_concept["name"] if next_concept else "All caught up!",
            "document_name": next_concept["document_name"] if next_concept else "",
        },
    }


@router.get("/search", response_model=List[SearchResult])
def search_concepts(
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Global search for concepts across all user documents."""
    user_id = current_user["user_id"]
    search_term = f"%{q}%"

    results = (
        db.query(Concept, Document.title)
        .join(Document)
        .filter(
            Document.user_id == user_id,
            (Concept.name.ilike(search_term)) | (Concept.definition.ilike(search_term)),
        )
        .limit(5)
        .all()
    )

    formatted_results = []
    for concept, doc_title in results:
        # Create a short snippet of the definition
        snippet = (
            concept.definition[:80] + "..."
            if len(concept.definition) > 80
            else concept.definition
        )
        formatted_results.append(
            {
                "id": concept.id,
                "name": concept.name,
                "document_name": doc_title,
                "definition_snippet": snippet,
            }
        )

    return formatted_results
