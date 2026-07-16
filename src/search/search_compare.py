"""
Side-by-side comparison of BM25 vs kNN vs Hybrid search results.
Runs the same query through all 3 modes and prints results together.

Dual-index architecture:
    - BM25   → INDEX_TEXT   (metadata only, no embeddings)
    - kNN    → INDEX_VECTORS (embeddings only) + mget metadata from INDEX_TEXT
    - Hybrid → BM25 from INDEX_TEXT + kNN from INDEX_VECTORS, RRF merge, backfill

Usage: ./venv/bin/python src/search/search_compare.py
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import time
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

from src.config import INDEX_TEXT, INDEX_VECTORS, ES_URL, MODEL_NAME, RRF_K, NUM_CANDIDATES

es = Elasticsearch(ES_URL)

print("Loading embedding model...")
model = SentenceTransformer(MODEL_NAME)
print(f"Model ready (device: {model.device})\n")


def _fetch_metadata(doc_ids):
    """Fetch title/year from INDEX_TEXT for a list of doc IDs."""
    if not doc_ids:
        return {}
    meta_resp = es.mget(
        index=INDEX_TEXT,
        body={"ids": doc_ids},
        _source=["title", "year"],
    )
    meta_map = {}
    for doc in meta_resp["docs"]:
        if doc.get("found"):
            meta_map[doc["_id"]] = doc["_source"]
    return meta_map


def bm25_search(query_text, size=5):
    """BM25 search on INDEX_TEXT."""
    start = time.perf_counter()
    resp = es.search(
        index=INDEX_TEXT,
        query={"multi_match": {"query": query_text, "fields": ["title^2", "abstract"]}},
        size=size,
        _source=["title", "year"],
    )
    latency = (time.perf_counter() - start) * 1000
    return resp["hits"]["hits"], latency


def knn_search(query_text, size=5, num_candidates=50):
    """kNN search on INDEX_VECTORS, with metadata backfill from INDEX_TEXT."""
    query_vector = model.encode(query_text, normalize_embeddings=True).tolist()
    start = time.perf_counter()
    resp = es.search(
        index=INDEX_VECTORS,
        knn={"field": "embedding", "query_vector": query_vector, "k": size, "num_candidates": num_candidates},
        size=size,
        _source=False,  # INDEX_VECTORS has no metadata fields
    )
    hits = resp["hits"]["hits"]

    # Backfill metadata from INDEX_TEXT
    meta_map = _fetch_metadata([h["_id"] for h in hits])
    for hit in hits:
        hit["_source"] = meta_map.get(hit["_id"], {})

    latency = (time.perf_counter() - start) * 1000
    return hits, latency


def rrf_merge(bm25_hits, knn_hits, k=60, final_size=5):
    scores = {}
    docs = {}
    for rank, hit in enumerate(bm25_hits, 1):
        doc_id = hit["_id"]
        scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank)
        docs[doc_id] = hit
    for rank, hit in enumerate(knn_hits, 1):
        doc_id = hit["_id"]
        scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank)
        docs[doc_id] = hit
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [docs[did] for did, _ in ranked[:final_size]]


def hybrid_rrf_search(query_text, size=5):
    """Hybrid search: BM25 from INDEX_TEXT + kNN from INDEX_VECTORS, then RRF merge."""
    query_vector = model.encode(query_text, normalize_embeddings=True).tolist()
    start = time.perf_counter()

    # BM25 from INDEX_TEXT
    bm25_resp = es.search(
        index=INDEX_TEXT,
        query={"multi_match": {"query": query_text, "fields": ["title^2", "abstract"]}},
        size=20,
        _source=["title", "year"],
    )

    # kNN from INDEX_VECTORS
    knn_resp = es.search(
        index=INDEX_VECTORS,
        knn={"field": "embedding", "query_vector": query_vector, "k": 20, "num_candidates": NUM_CANDIDATES},
        size=20,
        _source=False,  # INDEX_VECTORS has no metadata fields
    )
    knn_hits = knn_resp["hits"]["hits"]

    # Backfill metadata for kNN-only docs
    meta_map = _fetch_metadata([h["_id"] for h in knn_hits])
    for hit in knn_hits:
        hit["_source"] = meta_map.get(hit["_id"], {})

    merged = rrf_merge(bm25_resp["hits"]["hits"], knn_hits, k=RRF_K, final_size=size)
    latency = (time.perf_counter() - start) * 1000
    return merged, latency


def compare(query_text, size=5):
    print("=" * 90)
    print(f"  QUERY: \"{query_text}\"")
    print("=" * 90)

    bm25_hits, bm25_lat = bm25_search(query_text, size=size)
    knn_hits, knn_lat = knn_search(query_text, size=size)
    hyb_hits, hyb_lat = hybrid_rrf_search(query_text, size=size)

    print(f"\n  {'#':<3} {'BM25':<40} {'kNN':<40} {'Hybrid (RRF)':<40}")
    print(f"  {'-'*3} {'-'*40} {'-'*40} {'-'*40}")

    for i in range(size):
        cols = []
        for hits in [bm25_hits, knn_hits, hyb_hits]:
            if i < len(hits):
                src = hits[i].get("_source", {})
                t = src.get("title", "N/A")[:37]
                y = src.get("year", "?")
                cols.append(f"{t}.. ({y})")
            else:
                cols.append("--")
        print(f"  {i+1:<3} {cols[0]:<40} {cols[1]:<40} {cols[2]:<40}")

    print(f"\n  Latency:  BM25={bm25_lat:.0f}ms  |  kNN={knn_lat:.0f}ms  |  Hybrid={hyb_lat:.0f}ms")

    bm25_ids = {h["_id"] for h in bm25_hits}
    knn_ids = {h["_id"] for h in knn_hits}
    hyb_ids = {h["_id"] for h in hyb_hits}
    overlap_bk = len(bm25_ids & knn_ids)
    overlap_bh = len(bm25_ids & hyb_ids)
    overlap_kh = len(knn_ids & hyb_ids)
    print(f"  Overlap:  BM25&kNN={overlap_bk}/{size}  |  BM25&Hyb={overlap_bh}/{size}  |  kNN&Hyb={overlap_kh}/{size}")
    print()


if __name__ == "__main__":
    if not es.ping():
        print("ERROR: Cannot connect to Elasticsearch!")
        exit(1)

    queries = [
        "BERT",
        "methods to detect fake images",
        "efficient attention mechanism for long sequences",
        "graph neural networks node classification",
        "training robots with reward-based algorithms",
    ]

    for q in queries:
        compare(q)
