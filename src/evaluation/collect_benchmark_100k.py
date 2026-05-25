"""
Collect benchmark data from the existing 100k ES index.
Run this AFTER Docker + ES is up: .\venv\Scripts\python.exe src\collect_benchmark_100k.py
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import time
import statistics
from elasticsearch import Elasticsearch

from src.config import ES_URL, INDEX_V1

es = Elasticsearch(ES_URL)

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


def measure_bm25_latency(queries):
    latencies = []
    for q in queries:
        body = {
            "size": 10,
            "query": {
                "multi_match": {
                    "query": q,
                    "fields": ["title^2", "abstract"]
                }
            }
        }
        start = time.perf_counter()
        es.search(index=INDEX_V1, body=body)
        elapsed_ms = (time.perf_counter() - start) * 1000
        latencies.append(elapsed_ms)
    return latencies


def get_index_stats(index_name):
    try:
        stats = es.indices.stats(index=index_name)
        idx_stats = stats["indices"][index_name]
        size_bytes = idx_stats["total"]["store"]["size_in_bytes"]
        doc_count = idx_stats["total"]["docs"]["count"]
        return {
            "doc_count": doc_count,
            "size_mb": round(size_bytes / (1024 * 1024), 1),
            "size_bytes": size_bytes,
        }
    except Exception as e:
        return {"error": str(e)}


def get_jvm_stats():
    try:
        nodes = es.nodes.stats(metric="jvm")
        for _, node_info in nodes["nodes"].items():
            heap = node_info["jvm"]["mem"]
            return {
                "heap_used_mb": round(heap["heap_used_in_bytes"] / (1024 * 1024), 1),
                "heap_max_mb": round(heap["heap_max_in_bytes"] / (1024 * 1024), 1),
                "heap_percent": heap["heap_used_percent"],
            }
    except Exception as e:
        return {"error": str(e)}


def percentile(data, p):
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * (p / 100)
    f = int(k)
    c = f + 1 if f + 1 < len(sorted_data) else f
    d = k - f
    return sorted_data[f] + d * (sorted_data[c] - sorted_data[f])


def main():
    print("=" * 60)
    print("  BENCHMARK: 100k Elasticsearch Index")
    print("=" * 60)

    if not es.ping():
        print("ERROR: Elasticsearch is not reachable at localhost:9200")
        print("Please start Docker Desktop first.")
        return

    print("\n[1/3] Index Statistics")
    print("-" * 40)
    stats = get_index_stats(INDEX_V1)
    if "error" in stats:
        print(f"  Error: {stats['error']}")
        return
    print(f"  Documents:  {stats['doc_count']:,}")
    print(f"  Index size: {stats['size_mb']} MB")

    print("\n[2/3] JVM / Heap Statistics")
    print("-" * 40)
    jvm = get_jvm_stats()
    if "error" in jvm:
        print(f"  Error: {jvm['error']}")
    else:
        print(f"  Heap used:  {jvm['heap_used_mb']} MB ({jvm['heap_percent']}%)")
        print(f"  Heap max:   {jvm['heap_max_mb']} MB")

    print("\n[3/3] BM25 Query Latency (20 queries)")
    print("-" * 40)
    # Warm up
    print("  Warming up (5 queries)...")
    for q in TEST_QUERIES[:5]:
        es.search(index=INDEX_V1, body={"size": 1, "query": {"match": {"title": q}}})

    latencies = measure_bm25_latency(TEST_QUERIES)
    p50 = percentile(latencies, 50)
    p95 = percentile(latencies, 95)
    p99 = percentile(latencies, 99)
    avg = statistics.mean(latencies)

    print(f"  Average:  {avg:.1f} ms")
    print(f"  P50:      {p50:.1f} ms")
    print(f"  P95:      {p95:.1f} ms")
    print(f"  P99:      {p99:.1f} ms")
    print(f"  Min:      {min(latencies):.1f} ms")
    print(f"  Max:      {max(latencies):.1f} ms")

    results = {
        "dataset": "100k_midterm",
        "doc_count": stats["doc_count"],
        "index_size_mb": stats["size_mb"],
        "heap_used_mb": jvm.get("heap_used_mb"),
        "heap_max_mb": jvm.get("heap_max_mb"),
        "bm25_latency": {
            "num_queries": len(latencies),
            "avg_ms": round(avg, 1),
            "p50_ms": round(p50, 1),
            "p95_ms": round(p95, 1),
            "p99_ms": round(p99, 1),
            "min_ms": round(min(latencies), 1),
            "max_ms": round(max(latencies), 1),
        }
    }

    output_file = "data/benchmark_100k.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n  Results saved to: {output_file}")


if __name__ == "__main__":
    main()

