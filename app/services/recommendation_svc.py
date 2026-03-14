from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from app.db.neo4j import neo4j_conn
from app.models.sm2_progress import SM2Progress
from app.models.document import Concept


class RecommendationService:
    @staticmethod
    def get_next_concept_to_study(
        user_id: int, document_id: int, db: Session
    ) -> Optional[Dict[str, Any]]:
        """
        Determine the next optimal concept for the user to study based on SM-2 progress
        and the Knowledge Graph dependencies.
        """
        print(
            f"Calculating next concept for user {user_id} in document {document_id}..."
        )

        # 1. Check Postgres for concepts that are due for review (Spaced Repetition priority)
        current_time = datetime.now(timezone.utc)
        due_concept = (
            db.query(SM2Progress)
            .join(Concept)
            .filter(
                SM2Progress.user_id == user_id,
                Concept.document_id == document_id,
                SM2Progress.next_review_date <= current_time,
            )
            .order_by(SM2Progress.next_review_date.asc())
            .first()
        )

        if due_concept:
            print(f"Found concept due for review: ID {due_concept.concept_id}")
            # TODO: Fetch concept details and return
            return {"concept_id": due_concept.concept_id, "reason": "review_due"}

        # 2. Query Neo4j to find the next unlearned concept
        session = neo4j_conn.get_session()
        unlearned_concept_name = None
        try:
            # Query explained:
            # Match concepts in the current document.
            # Find concepts where ALL their prerequisite concepts (if any) are ALREADY in SM2Progress (meaning they have been studied).
            # AND the concept itself is NOT in the user's SM2Progress.
            # Order by node degree (simpler concepts first) and return 1.

            query = """
            MATCH (target:Concept {document_id: $doc_id})
            // Check if it has NOT been learned yet
            WHERE NOT EXISTS {
                // We use Postgres for SM2Progress, but we pass learned concept names as a list parameter here
                // Assuming we pass $learned_concept_names
            }
            // For MVP, let's just get the root nodes (concepts with no prerequisites) 
            // OR nodes where all prerequisites are in the learned list.
            OPTIONAL MATCH (prereq:Concept)-[:REQUIRES]->(target)
            WITH target, collect(prereq.name) AS prerequisites
            WHERE all(p IN prerequisites WHERE p IN $learned_concepts) AND NOT target.name IN $learned_concepts
            RETURN target.name AS concept_name LIMIT 1
            """

            # Fetch learned concepts from Postgres first
            learned_records = (
                db.query(Concept)
                .join(SM2Progress)
                .filter(
                    SM2Progress.user_id == user_id, Concept.document_id == document_id
                )
                .all()
            )
            learned_concepts = [c.name for c in learned_records]

            result = session.run(
                query, doc_id=document_id, learned_concepts=learned_concepts
            )
            record = result.single()
            if record:
                unlearned_concept_name = record["concept_name"]
                print(f"Next optimal concept found in Graph: {unlearned_concept_name}")
            else:
                print("No unlearned concepts with fulfilled prerequisites found.")
        finally:
            session.close()

        # 3. Fetch from Postgres and return
        if unlearned_concept_name:
            next_concept = (
                db.query(Concept)
                .filter(
                    Concept.name == unlearned_concept_name,
                    Concept.document_id == document_id,
                )
                .first()
            )
            return next_concept

        return None
