"""
Vector (kNN) search on Elasticsearch using dense_vector embeddings.
Encodes the query text on-the-fly, then runs a kNN search on INDEX_VECTORS.
Metadata (title, year, authors, abstract) is fetched from INDEX_TEXT via mget.

Usage: ./venv/bin/python src/search/vector_search.py
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import time
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

from src.config import INDEX_VECTORS, INDEX_TEXT, ES_URL, MODEL_NAME

es = Elasticsearch(ES_URL)

print("Loading embedding model...")
model = SentenceTransformer(MODEL_NAME)
print(f"Model ready (device: {model.device})\n")


def vector_search(query_text, size=5, num_candidates=100):
    """kNN search using cosine similarity on dense_vector field."""
    print(f"\n--- VECTOR (kNN) SEARCH: '{query_text}' ---")

    query_vector = model.encode(query_text, normalize_embeddings=True).tolist()

    start = time.perf_counter()
    response = es.search(
        index=INDEX_VECTORS,
        knn={
            "field": "embedding",
            "query_vector": query_vector,
            "k": size,
            "num_candidates": num_candidates,
        },
        size=size,
        _source=False,  # INDEX_VECTORS has no metadata fields
    )

    hits = response["hits"]["hits"]

    # Fetch metadata from INDEX_TEXT via mget
    if hits:
        doc_ids = [hit["_id"] for hit in hits]
        meta_resp = es.mget(
            index=INDEX_TEXT,
            body={"ids": doc_ids},
            _source=["title", "year", "authors", "abstract"],
        )
        meta_map = {}
        for doc in meta_resp["docs"]:
            if doc.get("found"):
                meta_map[doc["_id"]] = doc["_source"]

        # Merge metadata into kNN results
        for hit in hits:
            hit["_source"] = meta_map.get(hit["_id"], {})

    latency = (time.perf_counter() - start) * 1000

    print(f"Results: {len(hits)} | Latency: {latency:.0f}ms")

    for i, hit in enumerate(hits, 1):
        score = hit["_score"]
        src = hit.get("_source", {})
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
