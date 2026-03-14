import networkx as nx
from typing import List, Dict
from app.ai_modules.llm.gemini_client import gemini_client
from app.ai_modules.llm.prompts import (
    CONCEPT_EXTRACTION_SYSTEM_PROMPT,
    DEPENDENCY_RESOLUTION_SYSTEM_PROMPT,
)
from app.db.neo4j import neo4j_conn


class GraphService:
    @staticmethod
    def extract_concepts_from_chunk(text_chunk: str) -> List[Dict]:
        """
        Send a text chunk to Gemini to extract concepts and definitions in JSON format.
        """
        print(f"Extracting concepts from chunk (length: {len(text_chunk)})...")
        prompt = f"Extract concepts from the following text:\n\n{text_chunk}"

        # gemini_client is imported from the global instance
        concepts_json = gemini_client.generate_json_output(
            prompt=prompt, system_instruction=CONCEPT_EXTRACTION_SYSTEM_PROMPT
        )
        return concepts_json if isinstance(concepts_json, list) else []

    @staticmethod
    def resolve_dependencies(concept_names: List[str]) -> List[Dict]:
        """
        Send a list of concepts to Gemini to find prerequisite relationships.
        """
        print(f"Resolving dependencies for {len(concept_names)} concepts...")
        prompt = (
            f"Determine prerequisites for these concepts: {', '.join(concept_names)}"
        )

        dependencies_json = gemini_client.generate_json_output(
            prompt=prompt, system_instruction=DEPENDENCY_RESOLUTION_SYSTEM_PROMPT
        )
        return dependencies_json if isinstance(dependencies_json, list) else []

    @staticmethod
    def build_and_sort_graph(dependencies: List[Dict]) -> List[str]:
        """
        Use NetworkX to build a directed graph and perform topological sorting.
        """
        print("Building directed graph and performing topological sort...")
        G = nx.DiGraph()

        for dep in dependencies:
            source = dep.get("source")
            target = dep.get("target")
            if source and target:
                G.add_edge(source, target)

        try:
            sorted_concepts = list(nx.topological_sort(G))
            return sorted_concepts
        except nx.NetworkXUnfeasible:
            print("Error: Cycle detected in dependencies! Graph is not a DAG.")
            return []

    @staticmethod
    def save_concepts_to_neo4j(document_id: int, dependencies: List[Dict]):
        """
        Persist the structured graph into the Neo4j database.
        """
        print(f"Saving graph for document_id {document_id} to Neo4j...")
        session = neo4j_conn.get_session()
        try:
            for dep in dependencies:
                # Cypher query to merge nodes and create relationships
                query = """
                MERGE (s:Concept {name: $source, document_id: $doc_id})
                MERGE (t:Concept {name: $target, document_id: $doc_id})
                MERGE (s)-[:REQUIRES]->(t)
                """
                session.run(
                    query,
                    source=dep["source"],
                    target=dep["target"],
                    doc_id=document_id,
                )
            print("Successfully saved to Neo4j.")
        except Exception as e:
            print(f"Neo4j Transaction Failed: {e}")
        finally:
            session.close()
