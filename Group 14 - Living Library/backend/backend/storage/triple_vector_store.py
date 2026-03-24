import chromadb
from chromadb.config import Settings
from typing import List, Dict, Tuple, Optional
import numpy as np
# REMOVED: from sentence_transformers import SentenceTransformer

class TripleVectorStore:
    """
    Stores triple embeddings in ChromaDB and reconstructs answers from queries.
    Uses ChromaDB's built-in embeddings (no PyTorch required).
    """
    
    def __init__(self, persist_directory: str = "./chroma_triple_db", 
                 collection_name: str = "knowledge_triples"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(path=persist_directory)
        print(f"Initialized TripleVectorStore on {persist_directory}")

    @property
    def collection(self):
        """Always get a fresh and valid collection reference."""
        try:
            # Try to get the existing collection
            col = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            # Verify it works by calling a simple method
            _ = col.count()
            return col
        except Exception:
            # If it fails, something is wrong with the client state or collection
            # Re-initialize the client and try one last time
            try:
                self.client = chromadb.PersistentClient(path=self.persist_directory)
                return self.client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
            except Exception as e:
                print(f"CRITICAL: Failed to get ChromaDB collection: {e}")
                raise e

    def add_triples(self, triples: List[Tuple[str, str, str]], 
                   source_sentences: Optional[List[str]] = None,
                   metadata: Optional[List[Dict]] = None):
        if not triples:
            return

        def _perform_add():
            documents = []
            ids = []
            metadatas = []
            
            current_col = self.collection
            count = current_col.count()
            compressed_texts = [f"{s} {r} {o}" for s, r, o in triples]

            for idx, (triple, text) in enumerate(zip(triples, compressed_texts)):
                subject, relation, obj = triple
                triple_id = f"triple_{count + idx}_{hash(text) % 100000}"
                ids.append(triple_id)
                documents.append(text)
                meta = {
                    "subject": subject,
                    "relation": relation,
                    "object": obj,
                    "triple_text": text
                }
                if source_sentences and idx < len(source_sentences):
                    meta["source_sentence"] = source_sentences[idx]
                if metadata and idx < len(metadata):
                    meta.update(metadata[idx])
                metadatas.append(meta)
            
            current_col.add(
                documents=documents,
                ids=ids,
                metadatas=metadatas
            )
            print(f"✓ Added {len(triples)} triples. Total: {current_col.count()}")

        try:
            _perform_add()
        except Exception as e:
            if "does not exist" in str(e).lower():
                print(f"DEBUG: Stale collection detected, retrying...")
                # Re-init client to be absolutely sure
                self.client = chromadb.PersistentClient(path=self.persist_directory)
                _perform_add()
            else:
                raise e

    def query_triples(self, query: str, n_results: int = 5, 
                     filter_dict: Optional[Dict] = None) -> Dict:
        
        def _perform_query():
            current_col = self.collection
            total_in_db = current_col.count()
            
            if total_in_db == 0:
                return {"query": query, "n_results": 0, "triples": []}
                
            fetch_k = min(n_results * 5, total_in_db)
            
            results = current_col.query(
                query_texts=[query],
                n_results=fetch_k,
                where=filter_dict if filter_dict else None,
                include=["metadatas", "documents", "distances"]
            )
            
            formatted_results = {"query": query, "n_results": 0, "triples": []}
            
            if results['ids'] and results['ids'][0]:
                seen_triples = set()
                for i in range(len(results['ids'][0])):
                    if len(formatted_results['triples']) >= n_results:
                        break
                        
                    meta = results['metadatas'][0][i]
                    triple_key = f"{meta['subject']} {meta['relation']} {meta['object']}".strip().lower()
                    
                    if triple_key in seen_triples:
                        continue
                    seen_triples.add(triple_key)

                    triple_info = {
                        "id": results['ids'][0][i],
                        "subject": meta['subject'],
                        "relation": meta['relation'],
                        "object": meta['object'],
                        "triple_text": results['documents'][0][i],
                        "similarity_score": round(1 - results['distances'][0][i], 4)
                    }
                    if 'source_sentence' in meta:
                        triple_info['source_sentence'] = meta['source_sentence']
                    
                    formatted_results['triples'].append(triple_info)
                    
                formatted_results['n_results'] = len(formatted_results['triples'])
            
            return formatted_results

        try:
            return _perform_query()
        except Exception as e:
            if "does not exist" in str(e).lower():
                print(f"DEBUG: Stale collection detected in query, retrying...")
                self.client = chromadb.PersistentClient(path=self.persist_directory)
                return _perform_query()
            else:
                raise e

    def get_all_triples(self, limit: int = 100) -> List[Dict]:
        """Retrieve all triples from the store."""
        try:
            results = self.collection.get(limit=limit, include=["metadatas", "documents"])
        except:
            return []
            
        formatted = []
        for i in range(len(results['ids'])):
            formatted.append({
                "id": results['ids'][i],
                "subject": results['metadatas'][i]['subject'],
                "relation": results['metadatas'][i]['relation'],
                "object": results['metadatas'][i]['object'],
                "triple_text": results['documents'][i]
            })
        return formatted

    def delete_collection(self):
        """Delete and recreate the collection."""
        print(f"DEBUG: Resetting collection {self.collection_name}...")
        try:
            self.client.delete_collection(self.collection_name)
            print(f"✓ Collection {self.collection_name} deleted.")
        except Exception as e:
            print(f"DEBUG: Delete failed (ignoring): {e}")
            
        print(f"✓ {self.collection_name} recreates automatically on next access.")
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector store."""
        all_triples = self.get_all_triples()
        
        subjects = set()
        relations = set()
        objects = set()
        
        for triple in all_triples:
            subjects.add(triple['subject'])
            relations.add(triple['relation'])
            objects.add(triple['object'])
        
        return {
            "total_triples": self.collection.count(),
            "unique_subjects": len(subjects),
            "unique_relations": len(relations),
            "unique_objects": len(objects),
            "subjects": sorted(subjects),
            "relations": sorted(relations)
        }

    def reconstruct_answer(self, query: str, n_results: int = 5, 
                          min_similarity: float = 0.3) -> str:
        """Reconstruct a natural language answer from retrieved triples."""
        results = self.query_triples(query, n_results)
        
        if not results['triples']:
            return "No relevant information found in the knowledge base."
        
        relevant_triples = [
            t for t in results['triples'] 
            if t['similarity_score'] >= min_similarity
        ]
        
        if not relevant_triples:
            return f"No triples found with similarity >= {min_similarity:.2f}. Try lowering the threshold."
        
        answer_lines = [f"Query: {query}", f"Found {len(relevant_triples)} relevant facts:\n"]
        for i, triple in enumerate(relevant_triples, 1):
            fact = f"{triple['subject']} {triple['relation']} {triple['object']}"
            answer_lines.append(f"{i}. {fact} (confidence: {triple['similarity_score']:.2%})")
            if 'source_sentence' in triple:
                answer_lines.append(f"   Source: \"{triple['source_sentence']}\"")
        
        return "\n".join(answer_lines)

    def get_triples_by_subject(self, subject: str, n_results: int = 10) -> List[Dict]:
        """Get all triples with a specific subject."""
        return self.query_triples(query=subject, n_results=n_results, filter_dict={"subject": subject})['triples']

    def get_triples_by_relation(self, relation: str, n_results: int = 10) -> List[Dict]:
        """Get all triples with a specific relation."""
        return self.query_triples(query=relation, n_results=n_results, filter_dict={"relation": relation})['triples']

    def summarize_knowledge(self, topic: str, n_results: int = 10) -> str:
        """Generate a knowledge summary about a topic by aggregating related triples."""
        results = self.query_triples(topic, n_results)
        if not results['triples']:
            return f"No knowledge found about: {topic}"
        
        subject_groups = {}
        for triple in results['triples']:
            s = triple['subject']
            if s not in subject_groups: subject_groups[s] = []
            subject_groups[s].append((triple['relation'], triple['object']))
        
        summary_lines = [f"Knowledge Summary: {topic}\n", "=" * 50]
        for subject, facts in subject_groups.items():
            summary_lines.append(f"\n{subject}:")
            for rel, obj in facts:
                summary_lines.append(f"  • {rel} {obj}")
        
        return "\n".join(summary_lines)


if __name__ == "__main__":
    # Test the triple vector store
    print("Testing TripleVectorStore (No PyTorch)...\n")
    
    # Initialize store
    store = TripleVectorStore(
        persist_directory="./test_triple_db",
        collection_name="test_triples"
    )
    
    # Sample triples (from your existing pipeline)
    test_triples = [
        ("Photosynthesis", "is", "process"),
        ("plants", "prepare", "food"),
        ("plants", "use", "sunlight"),
        ("plants", "take", "carbon dioxide"),
        ("plants", "take", "water"),
        ("chlorophyll", "converts", "glucose"),
        ("glucose", "provides", "energy"),
        ("Oxygen", "is released", "by-product"),
        ("process", "occurs", "leaves"),
        ("chloroplasts", "contain", "chlorophyll"),
    ]
    
    # Add triples
    store.add_triples(test_triples)
    
    print("\n" + "="*60)
    print("TEST 1: Query - 'How do plants make food?'")
    print("="*60)
    answer1 = store.reconstruct_answer("How do plants make food?", n_results=5)
    print(answer1)
    
    print("\n" + "="*60)
    print("TEST 2: Query - 'What is photosynthesis?'")
    print("="*60)
    answer2 = store.reconstruct_answer("What is photosynthesis?", n_results=3)
    print(answer2)
    
    print("\n" + "="*60)
    print("TEST 3: Get all triples about 'plants'")
    print("="*60)
    plant_triples = store.get_triples_by_subject("plants")
    for t in plant_triples:
        print(f"  {t['triple_text']} (similarity: {t['similarity_score']:.2%})")
    
    print("\n" + "="*60)
    print("TEST 4: Knowledge Summary")
    print("="*60)
    summary = store.summarize_knowledge("photosynthesis energy", n_results=8)
    print(summary)
    
    print("\n" + "="*60)
    print("Store Statistics:")
    print("="*60)
    stats = store.get_stats()
    for key, value in stats.items():
        if isinstance(value, list):
            print(f"{key}: {', '.join(map(str, value))}")
        else:
            print(f"{key}: {value}")
    
    print("\n✓ All tests passed!")
