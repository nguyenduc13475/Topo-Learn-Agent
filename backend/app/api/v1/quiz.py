from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from app.api.dependencies import get_db, get_current_user
from app.models.document import Concept
from app.models.sm2_progress import SM2Progress
from app.services.tutor_svc import TutorService
from app.services.sm2_svc import calculate_sm2
from app.schemas.quiz_schema import QuizQuestionResponse, QuizSubmission

router = APIRouter()


@router.get("/{concept_id}/generate", response_model=list[QuizQuestionResponse])
def generate_quiz(concept_id: int, db: Session = Depends(get_db)):
    """
    Generate multiple-choice questions for a specific concept using Gemini.
    """
    print(f"Fetching concept ID {concept_id} to generate quiz...")
    concept = db.query(Concept).filter(Concept.id == concept_id).first()

    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")

    quiz_data = TutorService.generate_quiz_for_concept(
        concept_name=concept.name,
        definition=concept.definition,
        context=concept.context_index or "",
    )

    return quiz_data


@router.post("/submit")
def submit_quiz(
    submission: QuizSubmission,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Submit user answers, grade them dynamically, and trigger SM-2 update.
    """
    print(
        f"User {current_user['user_id']} submitted quiz for concept {submission.concept_id}"
    )

    # Dynamically grade based on payload
    score = TutorService.grade_quiz(submission.answers)

    # Fetch existing progress or create new
    progress = (
        db.query(SM2Progress)
        .filter(
            SM2Progress.user_id == current_user["user_id"],
            SM2Progress.concept_id == submission.concept_id,
        )
        .first()
    )

    if not progress:
        progress = SM2Progress(
            user_id=current_user["user_id"], concept_id=submission.concept_id
        )
        db.add(progress)

    # Calculate SM-2
    sm2_results = calculate_sm2(
        quality_response=score,
        repetitions=progress.repetitions,
        previous_interval=progress.interval,
        previous_ef=progress.easiness_factor,
    )

    # Update DB
    progress.repetitions = sm2_results["repetitions"]
    progress.interval = sm2_results["interval"]
    progress.easiness_factor = sm2_results["ef"]
    progress.last_reviewed_at = datetime.now(timezone.utc)
    progress.next_review_date = datetime.now(timezone.utc) + timedelta(
        days=sm2_results["interval"]
    )

    db.commit()
    print(f"SM-2 progress successfully updated for concept {submission.concept_id}.")

    return {
        "message": "Quiz submitted successfully",
        "score_assigned": score,
        "sm2_updated": {
            "next_review_date": progress.next_review_date,
            "new_ef": progress.easiness_factor,
        },
    }
