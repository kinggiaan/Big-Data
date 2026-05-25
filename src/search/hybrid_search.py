"""
Hybrid search: BM25 + kNN combined via manual Reciprocal Rank Fusion (RRF).
Fetches top results from both BM25 and kNN separately, then merges using RRF formula:
    RRF(d) = sum( 1 / (k + rank(d)) ) for each ranking list

Dual-index architecture:
    - BM25 queries INDEX_TEXT  (metadata only, no embeddings)
    - kNN  queries INDEX_VECTORS (alias → arxiv_bench, embeddings only)
    - After RRF merge, missing metadata is backfilled from INDEX_TEXT via mget

Usage: ./venv/bin/python src/search/hybrid_search.py
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import time
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

from src.config import INDEX_TEXT, INDEX_VECTORS, ES_URL, MODEL_NAME, RRF_K

es = Elasticsearch(ES_URL)

# Backward compatibility: api.py imports INDEX_NAME from this module
INDEX_NAME = INDEX_TEXT

print("Loading embedding model...")
model = SentenceTransformer(MODEL_NAME)
print(f"Model ready (device: {model.device})\n")


def _bm25_results(query_text, size=20):
    """BM25 search on INDEX_TEXT (metadata index, no embeddings)."""
    resp = es.search(
        index=INDEX_TEXT,
        query={"multi_match": {"query": query_text, "fields": ["title^2", "abstract"]}},
        size=size,
        _source=["title", "year", "authors", "abstract"],
    )
    return resp["hits"]["hits"]


def _knn_results(query_text, size=20, num_candidates=100):
    """kNN search on INDEX_VECTORS (embeddings index)."""
    query_vector = model.encode(query_text, normalize_embeddings=True).tolist()
    resp = es.search(
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
    return resp["hits"]["hits"]


def _backfill_metadata(merged_hits):
    """
    For docs that came only from kNN (no _source / missing metadata),
    fetch their title/abstract/year/authors from INDEX_TEXT via mget.
    """
    ids_to_fetch = [
        hit["_id"]
        for hit in merged_hits
        if not hit.get("_source") or not hit["_source"].get("title")
    ]
    if not ids_to_fetch:
        return

    meta_resp = es.mget(
        index=INDEX_TEXT,
        body={"ids": ids_to_fetch},
        _source=["title", "year", "authors", "abstract"],
    )
    meta_map = {}
    for doc in meta_resp["docs"]:
        if doc.get("found"):
            meta_map[doc["_id"]] = doc["_source"]

    for hit in merged_hits:
        if hit["_id"] in meta_map:
            hit["_source"] = meta_map[hit["_id"]]


def rrf_merge(bm25_hits, knn_hits, k=60, final_size=5):
    """
    Reciprocal Rank Fusion.
    RRF(d) = 1/(k + rank_bm25(d)) + 1/(k + rank_knn(d))
    """
    scores = {}
    docs = {}

    for rank, hit in enumerate(bm25_hits, start=1):
        doc_id = hit["_id"]
        scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank)
        docs[doc_id] = hit

    for rank, hit in enumerate(knn_hits, start=1):
        doc_id = hit["_id"]
        scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank)
        docs[doc_id] = hit

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    results = []
    for doc_id, rrf_score in ranked[:final_size]:
        hit = docs[doc_id]
        hit["_rrf_score"] = rrf_score
        results.append(hit)

    return results


def hybrid_search(query_text, size=5, fetch_size=20, rrf_k=60):
    """Hybrid BM25 + kNN with manual RRF."""
    print(f"\n--- HYBRID SEARCH (BM25 + kNN + RRF): '{query_text}' ---")

    start = time.perf_counter()
    bm25_hits = _bm25_results(query_text, size=fetch_size)
    knn_hits = _knn_results(query_text, size=fetch_size)
    merged = rrf_merge(bm25_hits, knn_hits, k=rrf_k, final_size=size)

    # Backfill metadata for docs that came only from kNN
    _backfill_metadata(merged)

    latency = (time.perf_counter() - start) * 1000

    print(f"Results: {len(merged)} | Latency: {latency:.0f}ms (BM25 {len(bm25_hits)} + kNN {len(knn_hits)} → RRF merge)")

    for i, hit in enumerate(merged, 1):
        src = hit.get("_source", {})
        title = src.get("title", "N/A")
        year = src.get("year", "N/A")
        abstract = src.get("abstract", "")[:120]
        rrf_score = hit.get("_rrf_score", 0)
        print(f"\n  [{i}] RRF Score: {rrf_score:.6f} | Year: {year}")
        print(f"      Title: {title}")
        print(f"      Abstract: {abstract}...")

    return merged, latency


if __name__ == "__main__":
    if not es.ping():
        print("ERROR: Cannot connect to Elasticsearch!")
        exit(1)

    hybrid_search("methods to detect fake images")
    hybrid_search("training robots with reward-based algorithms")
    hybrid_search("efficient attention mechanism for long sequences")
    hybrid_search("BERT")
