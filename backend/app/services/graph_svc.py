from typing import Dict, List

import networkx as nx

from app.db.neo4j import neo4j_conn


class GraphService:
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

        # Detect and selectively break cycles to guarantee a DAG without wiping
        # the whole graph
        while True:
            try:
                sorted_concepts = list(nx.topological_sort(G))
                return sorted_concepts
            except nx.NetworkXUnfeasible:
                try:
                    cycle = nx.find_cycle(G, orientation="original")
                    print(
                        f"[GraphService] Cycle detected: {cycle}. Breaking edge: {cycle[-1]}"
                    )
                    G.remove_edge(cycle[-1][0], cycle[-1][1])
                except nx.NetworkXNoCycle:
                    break
        return list(nx.topological_sort(G))

    @staticmethod
    def save_concepts_to_neo4j(document_id: int, dependencies: List[Dict]):
        """
        Persist the structured graph into the Neo4j database.
        """
        print(f"Saving graph for document_id {document_id} to Neo4j...")
        session = neo4j_conn.get_session()
        try:
            for dep in dependencies:
                # Merge strictly by ID, not string name
                query = """
                MERGE (s:Concept {id: $source_id, document_id: $doc_id})
                MERGE (t:Concept {id: $target_id, document_id: $doc_id})
                MERGE (s)-[:IS_PREREQUISITE_OF]->(t)
                """
                session.run(
                    query,
                    source_id=dep["source_id"],
                    target_id=dep["target_id"],
                    doc_id=document_id,
                )
            print("Successfully saved to Neo4j.")
        except Exception as e:
            print(f"Neo4j Transaction Failed: {e}")
        finally:
            session.close()
