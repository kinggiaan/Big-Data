"""
Vector (kNN) search on Elasticsearch using dense_vector embeddings.
Encodes the query text on-the-fly, then runs a kNN search on the arxiv_papers_v2 index.

Usage: .\venv\Scripts\python.exe src\vector_search.py
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import time
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

es = Elasticsearch("http://localhost:9200")
INDEX_NAME = "arxiv_papers_v2"

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print(f"Model ready (device: {model.device})\n")


def vector_search(query_text, size=5, num_candidates=50):
    """kNN search using cosine similarity on dense_vector field."""
    print(f"\n--- VECTOR (kNN) SEARCH: '{query_text}' ---")

    query_vector = model.encode(query_text, normalize_embeddings=True).tolist()

    start = time.perf_counter()
    response = es.search(
        index=INDEX_NAME,
        knn={
            "field": "embedding",
            "query_vector": query_vector,
            "k": size,
            "num_candidates": num_candidates,
        },
        size=size,
        _source=["title", "year", "authors", "abstract"],
    )
    latency = (time.perf_counter() - start) * 1000

    hits = response["hits"]["hits"]
    print(f"Results: {len(hits)} | Latency: {latency:.0f}ms")

    for i, hit in enumerate(hits, 1):
        score = hit["_score"]
        src = hit["_source"]
        title = src.get("title", "N/A")
        year = src.get("year", "N/A")
        abstract = src.get("abstract", "")[:120]
        print(f"\n  [{i}] Score: {score:.4f} | Year: {year}")
        print(f"      Title: {title}")
        print(f"      Abstract: {abstract}...")

    return hits, latency


if __name__ == "__main__":
    if not es.ping():
        print("ERROR: Cannot connect to Elasticsearch!")
        exit(1)

    vector_search("methods to detect fake images")
    vector_search("training robots with reward-based algorithms")
    vector_search("efficient attention mechanism for long sequences")
    vector_search("BERT")

