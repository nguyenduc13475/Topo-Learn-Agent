import time

from neo4j import GraphDatabase

from app.core.config import settings


class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        if self.driver:
            self.driver.close()

    def get_session(self):
        return self.driver.session()

    def initialize_constraints(self):
        """Ensure uniqueness constraints for optimal MERGE performance with a
        retry mechanism."""
        max_retries = 5
        for attempt in range(max_retries):
            try:
                with self.driver.session() as session:
                    # Neo4j 5.x syntax requires named constraints
                    session.run(
                        "CREATE CONSTRAINT concept_id_unique IF NOT EXISTS FOR (c:Concept) REQUIRE c.id IS UNIQUE"
                    )
                    session.run(
                        "CREATE INDEX concept_doc_id IF NOT EXISTS FOR (c:Concept) ON (c.document_id)"
                    )
                print("[Neo4j] Constraints and indexes initialized successfully.")
                return
            except Exception as e:
                print(
                    f"[Neo4j] Warning during constraint initialization (Attempt {attempt + 1}/{max_retries}): {e}"
                )
                if attempt < max_retries - 1:
                    time.sleep(5)  # Wait for Neo4j to fully boot


neo4j_conn = Neo4jConnection(
    settings.NEO4J_URI, settings.NEO4J_USER, settings.NEO4J_PASSWORD
)
