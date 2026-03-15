import re
from typing import List, Dict
from app.ai_modules.llm.gemini_client import gemini_client
from app.ai_modules.llm.prompts import QUIZ_GENERATION_SYSTEM_PROMPT
from app.schemas.quiz_schema import AnswerSubmission


class TutorService:
    @staticmethod
    def generate_quiz_for_concept(
        concept_name: str, definition: str, context: str
    ) -> List[Dict]:
        """
        Calls Gemini API to generate a multiple-choice quiz for a specific concept.
        """
        print(f"Generating quiz for concept: {concept_name}...")

        prompt = (
            f"Concept: {concept_name}\n"
            f"Definition: {definition}\n"
            f"Context from document: {context}\n\n"
            f"Please generate 3 multiple-choice questions to test the user's understanding."
        )

        quiz_json = gemini_client.generate_json_output(
            prompt=prompt, system_instruction=QUIZ_GENERATION_SYSTEM_PROMPT
        )

        return quiz_json if isinstance(quiz_json, list) else []

    @staticmethod
    def grade_quiz(submitted_answers: List[AnswerSubmission]) -> int:
        """
        Calculate score from 0 to 5 to feed into the SM-2 algorithm.
        Uses smart string normalization for better matching.
        """
        print("Grading user submission with smart normalization...")
        if not submitted_answers:
            print("No answers provided for grading.")
            return 0

        def normalize_text(text: str) -> str:
            # Convert to lowercase, remove punctuation, and strip extra whitespaces
            text = text.lower()
            text = re.sub(r"[^\w\s]", "", text)
            return " ".join(text.split())

        correct_count = 0
        for ans in submitted_answers:
            user_ans = normalize_text(ans.user_answer)
            correct_ans = normalize_text(ans.correct_answer)

            if (
                user_ans == correct_ans
                or user_ans in correct_ans
                or correct_ans in user_ans
            ):
                correct_count += 1
            else:
                print(
                    f"Incorrect answer found. Expected: '{ans.correct_answer}', Got: '{ans.user_answer}'"
                )

        # Map ratio to a 0-5 scale for SM-2
        ratio = correct_count / len(submitted_answers)
        score = int(ratio * 5)

        print(f"Grading completed. Score: {score}/5")
        return score
