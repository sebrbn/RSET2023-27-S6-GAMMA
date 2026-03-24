from neo4j import GraphDatabase

class Neo4jStore:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def store_triple(self, s, r, o):
        query = f"""
        MERGE (a:Entity {{name: $s}})
        MERGE (b:Entity {{name: $o}})
        MERGE (a)-[:{r}]->(b)
        """
        with self.driver.session() as session:
            session.run(query, s=s, o=o)

    def clear_database(self):
        query = "MATCH (n) DETACH DELETE n"
        with self.driver.session() as session:
            session.run(query)
