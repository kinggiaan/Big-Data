"""
Scalability benchmark: measure indexing time, index size, query latency
across BM25, kNN, and Hybrid modes using the dual-index architecture.

- BM25 queries  → INDEX_TEXT   (arxiv_text, metadata only)
- kNN queries   → INDEX_VECTORS (arxiv_vectors → arxiv_bench, embeddings)
- Hybrid (RRF)  → both indices

Usage: .\venv\Scripts\python.exe src\benchmark.py
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import os
import time
import statistics
from datetime import datetime
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

from src.config import (
    ES_URL, INDEX_TEXT, INDEX_VECTORS, INDEX_V1,
    MODEL_NAME, TITLE_BOOST, RESULT_SIZE, NUM_CANDIDATES, RRF_K,
)

OUTPUT_FILE = "data/benchmark_results.json"

TEST_QUERIES = [
    "deep learning",
    "natural language processing",
    "convolutional neural network image classification",
    "reinforcement learning robotics",
    "graph neural networks",
    "transformer attention mechanism",
    "federated learning privacy",
    "generative adversarial network",
    "object detection real-time",
    "quantum computing algorithms",
    "recommendation system collaborative filtering",
    "speech recognition end-to-end",
    "anomaly detection time series",
    "knowledge graph embedding",
    "multi-task learning NLP",
    "neural architecture search",
    "transfer learning domain adaptation",
    "adversarial robustness",
    "point cloud 3D",
    "BERT fine-tuning",
]


def percentile(data, p):
    s = sorted(data)
    k = (len(s) - 1) * (p / 100)
    f = int(k)
    c = min(f + 1, len(s) - 1)
    return s[f] + (k - f) * (s[c] - s[f])


def measure_bm25(es, queries, index, size=RESULT_SIZE):
    latencies = []
    for q in queries:
        start = time.perf_counter()
        es.search(
            index=index,
            query={"multi_match": {"query": q, "fields": [f"title^{TITLE_BOOST}", "abstract"]}},
            size=size,
        )
        latencies.append((time.perf_counter() - start) * 1000)
    return latencies


def measure_knn(es, model, queries, index, size=RESULT_SIZE, num_candidates=NUM_CANDIDATES):
    latencies = []
    for q in queries:
        vec = model.encode(q, normalize_embeddings=True).tolist()
        start = time.perf_counter()
        es.search(
            index=index,
            knn={"field": "embedding", "query_vector": vec, "k": size, "num_candidates": num_candidates},
            size=size,
        )
        latencies.append((time.perf_counter() - start) * 1000)
    return latencies


def measure_hybrid(es, model, queries, index_text, index_vectors, size=RESULT_SIZE):
    latencies = []
    for q in queries:
        vec = model.encode(q, normalize_embeddings=True).tolist()
        start = time.perf_counter()
        bm25_resp = es.search(
            index=index_text,
            query={"multi_match": {"query": q, "fields": [f"title^{TITLE_BOOST}", "abstract"]}},
            size=20,
        )
        knn_resp = es.search(
            index=index_vectors,
            knn={"field": "embedding", "query_vector": vec, "k": 20, "num_candidates": NUM_CANDIDATES},
            size=20,
        )
        # RRF merge (included in latency)
        scores = {}
        for rank, hit in enumerate(bm25_resp["hits"]["hits"], 1):
            scores[hit["_id"]] = scores.get(hit["_id"], 0) + 1.0 / (RRF_K + rank)
        for rank, hit in enumerate(knn_resp["hits"]["hits"], 1):
            scores[hit["_id"]] = scores.get(hit["_id"], 0) + 1.0 / (RRF_K + rank)
        sorted(scores.items(), key=lambda x: x[1], reverse=True)[:size]
        latencies.append((time.perf_counter() - start) * 1000)
    return latencies


def lat_stats(latencies):
    return {
        "avg_ms": round(statistics.mean(latencies), 1),
        "p50_ms": round(percentile(latencies, 50), 1),
        "p95_ms": round(percentile(latencies, 95), 1),
        "p99_ms": round(percentile(latencies, 99), 1),
        "min_ms": round(min(latencies), 1),
        "max_ms": round(max(latencies), 1),
    }


def get_index_info(es, index):
    stats = es.indices.stats(index=index)
    # stats["indices"] contains actual index names (not aliases), so we get the first value
    idx = list(stats["indices"].values())[0]
    return {
        "doc_count": idx["total"]["docs"]["count"],
        "size_bytes": idx["total"]["store"]["size_in_bytes"],
        "size_mb": round(idx["total"]["store"]["size_in_bytes"] / (1024 * 1024), 1),
    }


def get_jvm_info(es):
    nodes = es.nodes.stats(metric="jvm")
    for _, info in nodes["nodes"].items():
        heap = info["jvm"]["mem"]
        return {
            "heap_used_mb": round(heap["heap_used_in_bytes"] / (1024 * 1024), 1),
            "heap_max_mb": round(heap["heap_max_in_bytes"] / (1024 * 1024), 1),
            "heap_percent": heap["heap_used_percent"],
        }
    return {}


def main():
    es = Elasticsearch(ES_URL, request_timeout=60)
    if not es.ping():
        print("ERROR: Elasticsearch not reachable")
        return

    print("Loading embedding model...")
    model = SentenceTransformer(MODEL_NAME)
    print(f"Device: {model.device}\n")

    print("=" * 70)
    print(f"  BENCHMARK: dual-index ({INDEX_TEXT} + {INDEX_VECTORS})")
    print("=" * 70)

    # Index info
    print("\n[1/5] Index Statistics")
    print("-" * 50)
    text_info = get_index_info(es, INDEX_TEXT)
    print(f"  [{INDEX_TEXT}] Documents: {text_info['doc_count']:,}  Size: {text_info['size_mb']} MB")
    vec_info = get_index_info(es, INDEX_VECTORS)
    print(f"  [{INDEX_VECTORS}] Documents: {vec_info['doc_count']:,}  Size: {vec_info['size_mb']} MB")

    # JVM
    print("\n[2/5] JVM / Heap")
    print("-" * 50)
    jvm = get_jvm_info(es)
    print(f"  Heap used:  {jvm.get('heap_used_mb', '?')} MB ({jvm.get('heap_percent', '?')}%)")
    print(f"  Heap max:   {jvm.get('heap_max_mb', '?')} MB")

    # Warm up
    print("\n[3/5] Warming up (5 queries each mode)...")
    print("-" * 50)
    for q in TEST_QUERIES[:5]:
        es.search(index=INDEX_TEXT, query={"match": {"title": q}}, size=1)
        vec = model.encode(q, normalize_embeddings=True).tolist()
        es.search(index=INDEX_VECTORS, knn={"field": "embedding", "query_vector": vec, "k": 1, "num_candidates": 10}, size=1)
    print("  Done")

    # BM25 benchmark
    print(f"\n[4/5] Query Latency ({len(TEST_QUERIES)} queries × 3 modes)")
    print("-" * 50)

    print(f"  Running BM25 on {INDEX_TEXT}...")
    bm25_lats = measure_bm25(es, TEST_QUERIES, INDEX_TEXT)
    bm25_stats = lat_stats(bm25_lats)
    print(f"    Avg={bm25_stats['avg_ms']}ms  P50={bm25_stats['p50_ms']}ms  P95={bm25_stats['p95_ms']}ms")

    print(f"  Running kNN on {INDEX_VECTORS}...")
    knn_lats = measure_knn(es, model, TEST_QUERIES, INDEX_VECTORS)
    knn_stats = lat_stats(knn_lats)
    print(f"    Avg={knn_stats['avg_ms']}ms  P50={knn_stats['p50_ms']}ms  P95={knn_stats['p95_ms']}ms")

    print(f"  Running Hybrid (BM25 + kNN + RRF) on {INDEX_TEXT} + {INDEX_VECTORS}...")
    hyb_lats = measure_hybrid(es, model, TEST_QUERIES, INDEX_TEXT, INDEX_VECTORS)
    hyb_stats = lat_stats(hyb_lats)
    print(f"    Avg={hyb_stats['avg_ms']}ms  P50={hyb_stats['p50_ms']}ms  P95={hyb_stats['p95_ms']}ms")

    # Compare with v1 if exists
    v1_info = None
    v1_bm25_stats = None
    if es.indices.exists(index=INDEX_V1):
        print(f"\n[5/5] Comparing with v1 ({INDEX_V1}, text-only index)")
        print("-" * 50)
        v1_info = get_index_info(es, INDEX_V1)
        print(f"  v1 docs: {v1_info['doc_count']:,}  |  v1 size: {v1_info['size_mb']} MB")
        v1_bm25_lats = measure_bm25(es, TEST_QUERIES, INDEX_V1)
        v1_bm25_stats = lat_stats(v1_bm25_lats)
        print(f"  v1 BM25: Avg={v1_bm25_stats['avg_ms']}ms  P50={v1_bm25_stats['p50_ms']}ms  P95={v1_bm25_stats['p95_ms']}ms")
    else:
        print(f"\n[5/5] v1 index ({INDEX_V1}) not found, skipping comparison")

    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "index_text": INDEX_TEXT,
        "index_vectors": INDEX_VECTORS,
        "index_info_text": text_info,
        "index_info_vectors": vec_info,
        "jvm": jvm,
        "num_queries": len(TEST_QUERIES),
        "bm25": bm25_stats,
        "knn": knn_stats,
        "hybrid_rrf": hyb_stats,
    }
    if v1_info:
        results["v1_index_info"] = v1_info
    if v1_bm25_stats:
        results["v1_bm25"] = v1_bm25_stats

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n  Results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

