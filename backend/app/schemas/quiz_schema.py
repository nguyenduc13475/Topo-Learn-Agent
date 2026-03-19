from typing import List

from pydantic import BaseModel


class QuizQuestionResponse(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    explanation: str


class AnswerSubmission(BaseModel):
    question: str
    user_answer: str
    correct_answer: str


class QuizSubmission(BaseModel):
    concept_id: int
    answers: List[AnswerSubmission]


class QuizList(BaseModel):
    questions: List[QuizQuestionResponse]
