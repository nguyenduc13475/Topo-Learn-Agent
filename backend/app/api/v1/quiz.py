import os
from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from google.genai import types
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai_modules.llm.gemini_client import gemini_client
from app.api.dependencies import get_current_user, get_db
from app.core.rate_limit import limiter
from app.models.document import Concept, Document
from app.models.sm2_progress import SM2Progress
from app.schemas.quiz_schema import QuizQuestionResponse, QuizSubmission
from app.services.sm2_svc import calculate_sm2
from app.services.tutor_svc import TutorService

router = APIRouter()


@router.get("/{concept_id}/generate", response_model=list[QuizQuestionResponse])
@limiter.limit("5/minute")
def generate_quiz(request: Request, concept_id: int, db: Session = Depends(get_db)):
    """
    Generate multiple-choice questions for a specific concept using Gemini.
    """
    print(f"Fetching concept ID {concept_id} to generate quiz...")
    concept = db.query(Concept).filter(Concept.id == concept_id).first()

    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")

    # FETCH PARENT DOCUMENT TO PROVIDE DEEP CONTEXT
    document = db.query(Document).filter(Document.id == concept.document_id).first()

    # Leverage Gemini's large context window. Increased safe limit to 500,000 chars.
    raw_text = document.content_text if document and document.content_text else ""
    context_text = (
        raw_text[:500000] + "\n...[Content truncated for performance]..."
        if len(raw_text) > 500000
        else raw_text
    )
    # Append the specific context location index for better AI targeting
    if concept.context_index:
        context_text += f"\n\n[Target Concept Location: {concept.context_index}]"

    quiz_data = TutorService.generate_quiz_for_concept(
        concept_name=concept.name,
        definition=concept.definition,
        context=context_text,
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

    # Grace Buffer: If the interval is 1 day (failed/new concept), push it at
    # least 2 hours into the future to avoid the user getting stuck in a loop
    # immediately on the dashboard.
    added_time = timedelta(days=sm2_results["interval"])
    if sm2_results["interval"] <= 1:
        progress.next_review_date = datetime.now(timezone.utc) + timedelta(hours=2)
    else:
        progress.next_review_date = datetime.now(timezone.utc) + added_time

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


class ChatMessageInput(BaseModel):
    role: str
    content: str


class ChatPayload(BaseModel):
    message: str
    history: List[ChatMessageInput] = []


@router.post("/{concept_id}/chat")
def chat_with_tutor(
    concept_id: int,
    payload: ChatPayload,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    concept = (
        db.query(Concept)
        .join(Document)
        .filter(Concept.id == concept_id, Document.user_id == current_user["user_id"])
        .first()
    )

    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")

    # Fetch the parent document to inject deep context
    document = db.query(Document).filter(Document.id == concept.document_id).first()

    # CRITICAL: Leverage large context while maintaining safe processing boundaries
    raw_text = document.content_text if document and document.content_text else ""
    document_text = (
        raw_text[:500000] + "\n...[Content truncated for performance]..."
        if len(raw_text) > 500000
        else raw_text
    )

    if not document_text.strip():
        document_text = "No document content available."

    # Construct the base context instructions leveraging Gemini's large context window
    system_context = f"""
    You are a friendly AI tutor helping a student learn a specific concept.
    Concept: {concept.name}
    Definition: {concept.definition}
    Original Context Location: {concept.context_index}
    
    DOCUMENT REFERENCE TEXT:
    ---
    {document_text}  
    ---
    
    Use the document reference text above to provide highly accurate, contextual answers.
    Reference specific examples from the document if asked. Provide a clear, easy-to-understand explanation. Keep it concise.
    """

    formatted_contents = []
    last_role = None

    for msg in payload.history:
        role = "user" if msg.role == "user" else "model"

        # Gemini strictly requires the first message to be from 'user'
        if not formatted_contents and role == "model":
            continue

        # Prevent consecutive messages from the same role (Combines them safely)
        if role == last_role:
            formatted_contents[-1]["parts"].append({"text": f"\n\n{msg.content}"})
        else:
            formatted_contents.append({"role": role, "parts": [{"text": msg.content}]})
            last_role = role

    # Add the latest user message safely
    if last_role == "user":
        formatted_contents[-1]["parts"].append({"text": f"\n\n{payload.message}"})
    else:
        formatted_contents.append(
            {"role": "user", "parts": [{"text": payload.message}]}
        )

    try:
        config = types.GenerateContentConfig(
            system_instruction=system_context,
            temperature=0.5,
        )
        # Hardcode the premium model for Chat/Tutor interactions to ensure the
        # highest reasoning quality
        response = gemini_client.client.models.generate_content(
            model=os.getenv("LLM_MODEL_TUTOR", "gemini-3.1-flash-lite-preview"),
            contents=formatted_contents,
            config=config,
        )
        return {"response": response.text}
    except Exception as e:
        print(f"Chat API Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get AI response")
