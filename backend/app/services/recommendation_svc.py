from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.db.neo4j import neo4j_conn
from app.models.document import Concept
from app.models.sm2_progress import SM2Progress


class RecommendationService:
    @staticmethod
    def get_next_concept_to_study(
        user_id: int, document_id: int, db: Session
    ) -> Optional[Dict[str, Any]]:
        """
        Determine the next optimal concept for the user to study based on SM-2 progress
        and the Knowledge Graph dependencies (Production Version).
        """
        print(
            f"Calculating next concept for user {user_id} in document {document_id}..."
        )

        # 1. Check Postgres for concepts that are due for review (Spaced
        #    Repetition priority)
        current_time = datetime.now(timezone.utc)
        due_progress = (
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

        if due_progress:
            print(f"Found concept due for review: ID {due_progress.concept_id}")
            concept = (
                db.query(Concept).filter(Concept.id == due_progress.concept_id).first()
            )
            if concept:
                return {
                    "id": concept.id,
                    "name": concept.name,
                    "definition": concept.definition,
                    "context_index": concept.context_index,
                    "reason": "review_due",
                }

        # 2. Query Neo4j to find the next unlearned concept in the Dependency Graph
        session = neo4j_conn.get_session()
        unlearned_concept_id = None
        try:
            # We strictly check for repetition > 0 to ensure they actually passed a quiz
            learned_records = (
                db.query(Concept)
                .join(SM2Progress)
                .filter(
                    SM2Progress.user_id == user_id,
                    Concept.document_id == document_id,
                    SM2Progress.repetitions > 0,
                    SM2Progress.easiness_factor >= 1.3,
                )
                .all()
            )
            learned_concept_ids = [c.id for c in learned_records]

            # Use Integer IDs for absolute accuracy
            query = """
            MATCH (target:Concept {document_id: $doc_id})
            WHERE NOT target.id IN $learned_concept_ids
            OPTIONAL MATCH (prereq:Concept)-[:IS_PREREQUISITE_OF]->(target)
            WITH target, collect(prereq.id) AS prerequisites
            WHERE size(prerequisites) = 0 
               OR all(p IN prerequisites WHERE p IN $learned_concept_ids)
            RETURN target.id AS concept_id
            ORDER BY size(prerequisites) ASC
            LIMIT 1
            """
            result = session.run(
                query, doc_id=document_id, learned_concept_ids=learned_concept_ids
            )
            record = result.single()

            if record:
                unlearned_concept_id = record["concept_id"]
        except Exception as e:
            print(f"Error querying Knowledge Graph: {e}")
        finally:
            session.close()

        # 3. Fetch from Postgres and return
        if unlearned_concept_id:
            next_concept = (
                db.query(Concept).filter(Concept.id == unlearned_concept_id).first()
            )
            if next_concept:
                return {
                    "id": next_concept.id,
                    "name": next_concept.name,
                    "definition": next_concept.definition,
                    "context_index": next_concept.context_index,
                    "reason": "new_learning",
                }

        return None
