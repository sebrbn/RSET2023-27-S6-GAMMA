from core.ingestion import ingest_text
from storage.triple_vector_store import TripleVectorStore
from core.triple_extraction import extract_triples_from_text
from storage.neo4j_store import Neo4jStore

from semantics.audit import audit_report
from semantics.compression_embeddings import compress_triples, generate_embeddings
from analytics.metrics import compute_memory_stats

import numpy as np


class KnowledgePipeline:

    def __init__(self, vector_store: TripleVectorStore, neo4j_store: Neo4jStore = None):
        self.vector_store = vector_store
        self.neo4j_store = neo4j_store

        self.memory_history = []

        self.last_ingested_text = ""
        self.last_triples = []

    # ==========================================================
    # INGEST
    # ==========================================================
    def ingest_file(self, filepath: str):

        try:
            with open(filepath, "rb") as f:
                header = f.read(4)
            
            if header == b"%PDF":
                import pypdf
                reader = pypdf.PdfReader(filepath)
                text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            else:
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        text = f.read()
                except UnicodeDecodeError:
                    with open(filepath, "r", encoding="latin-1") as f:
                        text = f.read()
        except Exception as e:
            raise ValueError(f"Could not read file. Error: {str(e)}")

        self.last_ingested_text = text

        # Extract triples from full document (with pronoun resolution)
        all_triples = extract_triples_from_text(text)

        print("\n========== INGEST DEBUG ==========")
        print("Total triples extracted:", len(all_triples))

        for t in all_triples:
            print(t)

        print("===================================\n")

        # Store triples in vector DB
        if all_triples:
            self.vector_store.add_triples(all_triples)

            if self.neo4j_store:
                try:
                    for s, r, o in all_triples:
                        self.neo4j_store.store_triple(s, r, o)
                except Exception as e:
                    print(f"DEBUG: Neo4j storage failed: {e}")

        # ==============================
        # MEMORY ANALYTICS
        # ==============================

        compressed = compress_triples(all_triples)
        embeddings = generate_embeddings(compressed)

        stats = compute_memory_stats(text, all_triples, embeddings)

        stats["estimated_graph_bytes"] = len(all_triples) * 150

        self.memory_history.append(stats)
        self.last_triples = all_triples

        return {
            "triples_ingested": len(all_triples),
            "memory_stats": stats
        }

    # ==========================================================
    # QUERY
    # ==========================================================
    def query(self, question: str):

        answer = self.vector_store.reconstruct_answer(question)

        stored_triples = self.vector_store.query_triples(question, n_results=10)

        stored_facts = [
            f"{t['subject']} {t['relation']} {t['object']}"
            for t in stored_triples["triples"]
        ]

        audit_data = audit_report(
            original_text=question,
            generated_answer=answer,
            stored_facts=stored_facts
        )

        truth_score = audit_data["truth_analysis"]["truth_score"]
        drift_score = audit_data["drift_analysis"]["drift_score"]

        return {
            "answer": answer,
            "audit": audit_data,
            "confidence": truth_score,
            "drift": drift_score,
            "triples_used": stored_triples["triples"],
            "knowledge_graph": [
                {
                    "subject": t["subject"],
                    "relation": t["relation"],
                    "object": t["object"]
                }
                for t in stored_triples["triples"]
            ]
        }

    # ==========================================================
    # RESET
    # ==========================================================
    def reset_system(self):
        self.vector_store.delete_collection()
        if self.neo4j_store:
            try:
                self.neo4j_store.clear_database()
                print("✓ Neo4j database cleared.")
            except Exception as e:
                print(f"DEBUG: Neo4j clear failed: {e}")
                
        self.memory_history = []
        self.last_ingested_text = ""
        self.last_triples = []
        print("✓ System reset complete.")

    # ==========================================================
    # SYSTEM STATS
    # ==========================================================
    def get_system_stats(self):
        return {
            "vector_store": self.vector_store.get_stats(),
            "documents_processed": len(self.memory_history)
        }

    # ==========================================================
    # MEMORY DASHBOARD
    # ==========================================================
    def get_memory_dashboard(self):

        if not self.memory_history:
            return {"status": "No memory data available"}

        latest = self.memory_history[-1]

        raw_sizes = [d["raw_text_bytes"] for d in self.memory_history]
        compressed_sizes = [d["compressed_bytes"] for d in self.memory_history]
        embedding_sizes = [d["embedding_bytes"] for d in self.memory_history]
        graph_sizes = [d["estimated_graph_bytes"] for d in self.memory_history]

        dashboard = {
            "total_documents_processed": len(self.memory_history),
            "latest_run": latest,
            "historical_summary": {
                "avg_raw_bytes": int(np.mean(raw_sizes)),
                "avg_compressed_bytes": int(np.mean(compressed_sizes)),
                "avg_embedding_bytes": int(np.mean(embedding_sizes)),
                "avg_graph_bytes": int(np.mean(graph_sizes)),
                "avg_compression_ratio": round(
                    np.mean([d.get("compression_ratio", 0) for d in self.memory_history]), 3
                )
            }
        }

        total_raw = sum(raw_sizes)
        total_compressed = sum(compressed_sizes)

        overall_reduction = (
            ((total_raw - total_compressed) / total_raw) * 100
            if total_raw else 0
        )

        dashboard["living_library_memory_claim"] = {
            "overall_reduction_percent": round(overall_reduction, 2),
            "claim": "Living Library reduces memory footprint"
        }

        return dashboard

    # ==========================================================
    def close(self):
        if self.neo4j_store:
            self.neo4j_store.close()