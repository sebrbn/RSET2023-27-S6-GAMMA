import sys
import numpy as np
import matplotlib.pyplot as plt


def compute_memory_stats(text, triples, embeddings):
    """
    Computes memory statistics for:
    - Raw text
    - Triple representation
    - Compressed triples
    - Vector embeddings
    """

    #Raw text size
    raw_text_size = len(text.encode("utf-8"))

    #Triple tuple memory
    triple_size = sum(sys.getsizeof(t) for t in triples)

    #Compressed triple strings
    compressed = [f"{s} {r} {o}" for s, r, o in triples]
    compressed_size = sum(len(c.encode("utf-8")) for c in compressed)

    #Embedding size
    embedding_size = embeddings.nbytes if isinstance(embeddings, np.ndarray) else 0

    #Compression ratio
    compression_ratio = (
        raw_text_size / compressed_size
        if compressed_size > 0 else 0
    )

    #Memory reduction
    percent_reduction = (
        ((raw_text_size - compressed_size) / raw_text_size) * 100
        if raw_text_size > 0 else 0
    )

    stats = {
        "raw_text_bytes": raw_text_size,
        "triple_bytes": triple_size,
        "compressed_bytes": compressed_size,
        "embedding_bytes": embedding_size,
        "compression_ratio": round(compression_ratio, 2),
        "percent_reduction": round(percent_reduction, 2)
    }

    return stats


def plot_memory_bar(stats):
    """
    Bar graph: Raw vs Compressed vs Embeddings
    """
    labels = ["Raw Text", "Compressed Triples", "Embeddings"]
    values = [
        stats["raw_text_bytes"],
        stats["compressed_bytes"],
        stats["embedding_bytes"]
    ]

    plt.figure(figsize=(8, 5))
    plt.bar(labels, values)
    plt.title("Memory Usage Comparison")
    plt.ylabel("Memory (Bytes)")
    plt.xlabel("Representation Type")
    plt.tight_layout()
    plt.show()

def prepare_graph_data(stats):
    return {
        "labels": ["Raw Text", "Compressed Triples", "Embeddings"],
        "values": [
            stats["raw_text_bytes"],
            stats["compressed_bytes"],
            stats["embedding_bytes"]
        ]
    }
def plot_memory_trend(document_stats):
    """
    Trend graph across multiple documents
    document_stats = list of dicts returned from compute_memory_stats
    """

    raw = [doc["raw_text_bytes"] for doc in document_stats]
    compressed = [doc["compressed_bytes"] for doc in document_stats]

    plt.figure(figsize=(8, 5))
    plt.plot(raw, label="Raw Text")
    plt.plot(compressed, label="Compressed Triples")

    plt.title("Memory Trend Across Documents")
    plt.xlabel("Document Index")
    plt.ylabel("Memory (Bytes)")
    plt.legend()
    plt.tight_layout()
    plt.show()