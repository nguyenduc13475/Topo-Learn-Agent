from app.services.tutor_svc import TutorService
from app.schemas.quiz_schema import AnswerSubmission


def test_grade_quiz_perfect_score():
    """Test the grading logic when all answers are correct."""
    print("Testing: TutorService grading with perfect answers...")
    answers = [
        AnswerSubmission(
            question="Q1",
            user_answer="Knowledge Graph",
            correct_answer="Knowledge Graph",
        ),
        AnswerSubmission(
            question="Q2",
            user_answer="Topological Sort",
            correct_answer="Topological Sort",
        ),
    ]
    score = TutorService.grade_quiz(answers)
    assert score == 5
    print(f"Success: Perfect score graded correctly (Score: {score}).")


def test_grade_quiz_partial_score():
    """Test the grading logic with partially correct answers."""
    print("Testing: TutorService grading with partial correctness...")
    answers = [
        AnswerSubmission(
            question="Q1",
            user_answer="Knowledge Graph",
            correct_answer="Knowledge Graph",
        ),
        AnswerSubmission(
            question="Q2", user_answer="Wrong Answer", correct_answer="Topological Sort"
        ),
    ]
    score = TutorService.grade_quiz(answers)
    # 1 out of 2 is correct -> 50% -> ratio 0.5 * 5 = 2.5 -> int() -> 2
    assert score == 2
    print(f"Success: Partial score graded correctly (Score: {score}).")


def test_grade_quiz_smart_normalization():
    """Test the grading logic with messy strings, different cases, and punctuation."""
    print("Testing: TutorService grading string normalization...")
    answers = [
        AnswerSubmission(
            question="Q1",
            user_answer="   kNowledge GraPh!!!  ",
            correct_answer="Knowledge Graph",
        ),
    ]
    score = TutorService.grade_quiz(answers)
    assert score == 5
    print("Success: Smart string normalization matched the answer perfectly.")
