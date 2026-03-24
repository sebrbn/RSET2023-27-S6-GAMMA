from pipeline import KnowledgePipeline
from storage.triple_vector_store import TripleVectorStore
from storage.neo4j_store import Neo4jStore

vector_store = TripleVectorStore()

neo4j_store = Neo4jStore(
    uri="neo4j+s://0f85211f.databases.neo4j.io",
    user="0f85211f",
    password="96Ln3X9CFt8SISzhezeUe10PEeAcpRoAAAt_R-P4INw"
)

pipeline = KnowledgePipeline(vector_store, neo4j_store)

while True:
    cmd = input("\n>> ").strip()

    if cmd.startswith("ingest"):
        _, file = cmd.split()
        triples = pipeline.ingest_file(file)
        print(f"Ingested {len(triples)} triples")

    elif cmd.startswith("ask"):
        question = cmd[4:].strip()

        result = pipeline.query(question)

        print("\nQUESTION")
        print("--------")
        print(question)

        print("\nANSWER")
        print("--------")
        print(result["answer"])

        print("\nCONFIDENCE")
        print("--------")
        print(f"Truth Score: {result['confidence']}%")

        print("\nDRIFT ANALYSIS")
        print("--------")
        print(f"Drift Score: {result['drift']}")

        print("\nSYSTEM STATUS")
        print("--------")
        print(result["audit"]["action_recommendation"])

        print("\nEVIDENCE USED")
        print("--------")

        for i, triple in enumerate(result["triples_used"][:3], 1):
            print(f"{i}. {triple['triple_text']}")

    

    elif cmd == "exit":
        pipeline.close()
        break
