from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os

from pipeline import KnowledgePipeline
from storage.triple_vector_store import TripleVectorStore
from storage.neo4j_store import Neo4jStore

# Initialize stores
vector_store = TripleVectorStore(persist_directory="./chroma_triple_db")

try:
    neo4j_store = Neo4jStore(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="password"
    )
except:
    neo4j_store = None

pipeline = KnowledgePipeline(vector_store, neo4j_store)

app = FastAPI()

# Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:8080",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.post("/api/ingest")
async def ingest(file: UploadFile = File(...)):
    print(f"DEBUG: Received ingest request for file: {file.filename}")
    contents = await file.read()

    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(contents)
        temp_path = temp.name

    try:
        print(f"DEBUG: Processing file {temp_path} with pipeline...")
        result = pipeline.ingest_file(temp_path)
    except ValueError as e:
        os.remove(temp_path)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        os.remove(temp_path)
        print(f"CRITICAL ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"v1.5-ERROR: {str(e)}")

    os.remove(temp_path)

    return {
        "message": "File processed",
        "version": "v1.5-robust-retry",
        "triples_ingested": result["triples_ingested"],
        "memory_stats": result["memory_stats"]
    }


@app.post("/api/query")
async def query(data: dict):
    question = data.get("question", "")

    result = pipeline.query(question)

    return {
        "answer": result["answer"],
        "audit": result["audit"]
    }


@app.get("/api/stats")
def stats():
    return pipeline.get_system_stats()


@app.get("/api/dashboard")
def dashboard():
    return pipeline.get_memory_dashboard()


@app.get("/api/triples")
def triples():
    results = vector_store.query_triples("", n_results=100)

    return {
        "triples": results.get("triples", [])
    }

@app.delete("/api/reset")
def reset_database():
    try:
        pipeline.reset_system()
        return {"message": "Database reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")