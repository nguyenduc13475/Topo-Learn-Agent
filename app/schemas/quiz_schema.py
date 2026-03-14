from pydantic import BaseModel
from typing import List


class QuizOption(BaseModel):
    pass


class QuizQuestionResponse(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    explanation: str


class QuizSubmission(BaseModel):
    user_id: int
    concept_id: int
    answers: List[str]  # List of chosen options
