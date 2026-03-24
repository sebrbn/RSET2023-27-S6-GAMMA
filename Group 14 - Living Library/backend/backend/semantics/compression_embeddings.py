from sentence_transformers import SentenceTransformer
import numpy as np
def compress_triples(triples):
    """
    Converts triples into compressed semantic strings.
    """
    compressed = []
    for s, r, o in triples:
        compressed.append(f"{s} {r} {o}")
    return compressed
def generate_embeddings(sentences):
    """
    Converts compressed semantic sentences into vector embeddings
    using Sentence-BERT.
    """
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(sentences)
    return embeddings

if __name__ == "__main__":
    triples = [
        ("system", "extracts", "semantic triples"),
        ("students", "use", "platform"),
        ("model", "stores", "knowledge")
    ]
    print("Original Triples:")
    for t in triples:
        print(t)
    compressed_triples = compress_triples(triples)
    print("\nCompressed Semantic Facts:")
    for c in compressed_triples:
        print(c)
    embeddings = generate_embeddings(compressed_triples)
    print("\nEmbedding Details:")
    print("Embedding shape:", embeddings.shape)
    print("Sample embedding (first 10 values):")
    print(embeddings[0][:10])
