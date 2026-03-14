from neo4j import GraphDatabase
from app.core.config import settings


class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def get_session(self):
        return self.driver.session()


# Singleton initialization
neo4j_conn = Neo4jConnection(
    settings.NEO4J_URI, settings.NEO4J_USER, settings.NEO4J_PASSWORD
)
