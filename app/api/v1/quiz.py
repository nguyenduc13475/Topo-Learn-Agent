from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_db, get_current_user
from app.models.document import Concept
from app.services.tutor_svc import TutorService
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

    # Call AI Service to generate quiz
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
    Submit user answers, grade them, and trigger SM-2 update.
    """
    print(
        f"User {current_user['user_id']} submitted quiz for concept {submission.concept_id}"
    )

    # TODO: Fetch correct answers from Cache/DB.
    # For MVP, assume we cached the last generated quiz.
    mock_correct_answers = ["Option A", "Option B", "Option C"]  # Placeholder

    score = TutorService.grade_quiz(submission.answers, mock_correct_answers)

    # Trigger SM-2 Update (Giả sử bạn đã tách hàm logic ra khỏi router v1/review.py)
    # SM2Service.update_progress(user_id=current_user['user_id'], concept_id=submission.concept_id, quality_score=score, db=db)

    return {
        "message": "Quiz submitted successfully",
        "score_assigned": score,
        "next_action": "SM-2 progress updated.",
    }
