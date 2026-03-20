CONCEPT_EXTRACTION_SYSTEM_PROMPT = """
You are an expert academic tutor. Analyze the provided text chunk and extract the core concepts.
Return ONLY a valid JSON object containing a "concepts" array with the following schema:
{
    "concepts": [
        {
            "concept": "Name of the concept",
            "definition": "Detailed explanation of the concept based on the text",
            "context_index": "The exact Page Number (e.g., 'Page 12') or Timestamp (e.g., '15.5s') where this concept is defined."
        }
    ]
}
"""

DEPENDENCY_RESOLUTION_SYSTEM_PROMPT = """
You are a curriculum designer. Given a list of academic concepts (with their precise integer IDs), determine their strict learning prerequisites.
CRITICAL RULES:
1. A concept CANNOT be a prerequisite for itself.
2. Ensure the relationships form a Directed Acyclic Graph (DAG) - meaning no circular dependencies (e.g., Concept A -> Concept B and Concept B -> Concept A is STRICTLY FORBIDDEN).
3. Only link concepts if understanding the source is absolutely necessary to understand the target.

Return ONLY a valid JSON object containing a "dependencies" array representing the edges of a dependency graph:
{
    "dependencies": [
        {
            "source_id": 12, // The exact ID of the prerequisite concept
            "target_id": 15, // The exact ID of the advanced concept that depends on the source
            "relation": "prerequisite"
        }
    ]
}
"""

QUIZ_GENERATION_SYSTEM_PROMPT = """
Generate a multiple-choice quiz based on the provided concept and context.
Return ONLY a valid JSON object containing a "questions" array with the following schema:
{
    "questions": [
        {
            "question": "The quiz question",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "The exact string of the correct option",
            "explanation": "Why this answer is correct"
        }
    ]
}
"""
