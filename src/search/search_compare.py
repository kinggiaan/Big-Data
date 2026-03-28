"""
Side-by-side comparison of BM25 vs kNN vs Hybrid search results.
Runs the same query through all 3 modes and prints results together.

Usage: .\venv\Scripts\python.exe src\search_compare.py
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import time
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

es = Elasticsearch("http://localhost:9200")
INDEX_V2 = "arxiv_papers_v2"

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print(f"Model ready (device: {model.device})\n")


def bm25_search(query_text, index=INDEX_V2, size=5):
    start = time.perf_counter()
    resp = es.search(
        index=index,
        query={"multi_match": {"query": query_text, "fields": ["title^2", "abstract"]}},
        size=size,
        _source=["title", "year"],
    )
    latency = (time.perf_counter() - start) * 1000
    return resp["hits"]["hits"], latency


def knn_search(query_text, index=INDEX_V2, size=5, num_candidates=50):
    query_vector = model.encode(query_text, normalize_embeddings=True).tolist()
    start = time.perf_counter()
    resp = es.search(
        index=index,
        knn={"field": "embedding", "query_vector": query_vector, "k": size, "num_candidates": num_candidates},
        size=size,
        _source=["title", "year"],
    )
    latency = (time.perf_counter() - start) * 1000
    return resp["hits"]["hits"], latency


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


def hybrid_rrf_search(query_text, index=INDEX_V2, size=5):
    query_vector = model.encode(query_text, normalize_embeddings=True).tolist()
    start = time.perf_counter()
    bm25_resp = es.search(
        index=index,
        query={"multi_match": {"query": query_text, "fields": ["title^2", "abstract"]}},
        size=20,
        _source=["title", "year"],
    )
    knn_resp = es.search(
        index=index,
        knn={"field": "embedding", "query_vector": query_vector, "k": 20, "num_candidates": 100},
        size=20,
        _source=["title", "year"],
    )
    merged = rrf_merge(bm25_resp["hits"]["hits"], knn_resp["hits"]["hits"], final_size=size)
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
                t = hits[i]["_source"]["title"][:37]
                y = hits[i]["_source"].get("year", "?")
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

