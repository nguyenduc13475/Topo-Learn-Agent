from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.sm2_progress import SM2Progress
from app.services.recommendation_svc import RecommendationService
from app.services.sm2_svc import calculate_sm2

router = APIRouter()


class ReviewSubmit(BaseModel):
    quality_score: int


@router.post("/{concept_id}/update")
def update_review_progress(
    concept_id: int,
    payload: ReviewSubmit,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Update the SM-2 learning progress for a specific concept after a quiz.
    """
    print(
        f"Updating SM-2 progress for user {current_user['user_id']}, concept {concept_id}..."
    )

    progress = (
        db.query(SM2Progress)
        .filter(
            SM2Progress.user_id == current_user["user_id"],
            SM2Progress.concept_id == concept_id,
        )
        .first()
    )

    if not progress:
        # First time learning this concept
        progress = SM2Progress(user_id=current_user["user_id"], concept_id=concept_id)
        db.add(progress)

    # Calculate new SM-2 parameters
    try:
        sm2_results = calculate_sm2(
            quality_response=payload.quality_score,
            repetitions=progress.repetitions,
            previous_interval=progress.interval,
            previous_ef=progress.easiness_factor,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Update record
    progress.repetitions = sm2_results["repetitions"]
    progress.interval = sm2_results["interval"]
    progress.easiness_factor = sm2_results["ef"]
    progress.last_reviewed_at = datetime.now(timezone.utc)
    progress.next_review_date = datetime.now(timezone.utc) + timedelta(
        days=sm2_results["interval"]
    )

    db.commit()
    print("SM-2 progress updated successfully.")

    return {
        "message": "Review schedule updated",
        "next_review_date": progress.next_review_date,
        "new_ef": progress.easiness_factor,
    }


@router.get("/documents/{document_id}/next")
def get_next_learning_item(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get the next concept the user should study or review based on SM-2 and Graph.
    """
    print(f"Fetching next learning item for user {current_user['user_id']}...")

    next_item = RecommendationService.get_next_concept_to_study(
        user_id=current_user["user_id"], document_id=document_id, db=db
    )

    if not next_item:
        return {
            "message": "You have mastered all concepts in this document!",
            "concept": None,
        }

    return {"message": "Next item ready", "concept": next_item}
