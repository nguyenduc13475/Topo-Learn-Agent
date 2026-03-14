from typing import List, Dict
from app.ai_modules.llm.gemini_client import gemini_client
from app.ai_modules.llm.prompts import QUIZ_GENERATION_SYSTEM_PROMPT


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
    def grade_quiz(submitted_answers: List[str], correct_answers: List[str]) -> int:
        """
        Calculate score from 0 to 5 to feed into the SM-2 algorithm.
        """
        print("Grading user submission...")
        if not submitted_answers or not correct_answers:
            print("Missing answers for grading.")
            return 0

        correct_count = 0
        for sub, cor in zip(submitted_answers, correct_answers):
            if sub.strip().lower() == cor.strip().lower():
                correct_count += 1

        # Map ratio to a 0-5 scale for SM-2
        ratio = correct_count / len(correct_answers)
        score = int(ratio * 5)

        print(f"Grading completed. Score: {score}/5")
        return score
