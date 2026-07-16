"""
Multi-scale scalability benchmark (100k / 500k / 1M / 1.16M).

Measures per-index:
- index size (MB) and doc_count
- kNN/BM25/Hybrid (manual RRF) query latency percentiles (P50/P95/P99)

Usage:
  .\venv\Scripts\python.exe src\benchmark_multiscale.py ^
    --indices "100k:arxiv_papers_v2_100k,500k:arxiv_papers_v2_500k,1M:arxiv_papers_v2_1m,1.16M:arxiv_papers_v2_full"
"""

import argparse
import json
import os
import statistics
import time
from datetime import datetime

from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer


ES_URL_DEFAULT = "http://localhost:9200"

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


def parse_indices_arg(s: str):
    pairs = []
    for part in s.split(","):
        part = part.strip()
        if not part:
            continue
        if ":" not in part:
            raise SystemExit(f"Bad --indices entry (expected label:index): {part}")
        label, idx = part.split(":", 1)
        label = label.strip()
        idx = idx.strip()
        if not label or not idx:
            raise SystemExit(f"Bad --indices entry (empty label/index): {part}")
        pairs.append({"label": label, "index": idx})
    if not pairs:
        raise SystemExit("No indices provided")
    return pairs


def percentile(data, p):
    s = sorted(data)
    if not s:
        return None
    k = (len(s) - 1) * (p / 100)
    f = int(k)
    c = min(f + 1, len(s) - 1)
    return s[f] + (k - f) * (s[c] - s[f])


def build_bm25_body(query_text: str):
    word_count = len(query_text.strip().split())
    msm = "100%" if word_count <= 2 else "75%"
    return {
        "bool": {
            "must": [
                {
                    "multi_match": {
                        "query": query_text,
                        "fields": ["title^2", "abstract"],
                        "type": "best_fields",
                        "minimum_should_match": msm,
                    }
                }
            ]
        }
    }


def run_bm25(es, index, query_text, size, request_timeout=60):
    start = time.perf_counter()
    es.search(index=index, query=build_bm25_body(query_text), size=size, request_timeout=request_timeout, _source=False)
    return (time.perf_counter() - start) * 1000


def run_knn(es, index, model, query_text, size, num_candidates, request_timeout=60):
    vec = model.encode(query_text, normalize_embeddings=True).tolist()
    start = time.perf_counter()
    es.search(
        index=index,
        knn={"field": "embedding", "query_vector": vec, "k": size, "num_candidates": num_candidates},
        size=size,
        request_timeout=request_timeout,
        _source=False,
    )
    return (time.perf_counter() - start) * 1000


def run_hybrid_rrf(es, index, model, query_text, size, num_candidates, rrf_k=60, request_timeout=60):
    vec = model.encode(query_text, normalize_embeddings=True).tolist()
    start = time.perf_counter()

    bm25_resp = es.search(index=index, query=build_bm25_body(query_text), size=20, request_timeout=request_timeout)
    knn_resp = es.search(
        index=index,
        knn={"field": "embedding", "query_vector": vec, "k": 20, "num_candidates": num_candidates},
        size=20,
        request_timeout=request_timeout,
    )

    scores = {}
    for rank, hit in enumerate(bm25_resp["hits"]["hits"], 1):
        scores[hit["_id"]] = scores.get(hit["_id"], 0) + 1.0 / (rrf_k + rank)
    for rank, hit in enumerate(knn_resp["hits"]["hits"], 1):
        scores[hit["_id"]] = scores.get(hit["_id"], 0) + 1.0 / (rrf_k + rank)
    _ = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:size]

    return (time.perf_counter() - start) * 1000


def get_index_info(es, index):
    stats = es.indices.stats(index=index)
    idx = stats["indices"][index]
    doc_count = idx["total"]["docs"]["count"]
    size_mb = idx["total"]["store"]["size_in_bytes"] / (1024 * 1024)
    return {"doc_count": doc_count, "size_mb": size_mb}


def get_jvm_info(es):
    nodes = es.nodes.stats(metric="jvm")
    for _, info in nodes["nodes"].items():
        heap = info["jvm"]["mem"]
        return {
            "heap_used_mb": heap["heap_used_in_bytes"] / (1024 * 1024),
            "heap_max_mb": heap["heap_max_in_bytes"] / (1024 * 1024),
            "heap_percent": heap["heap_used_percent"],
        }
    return {}


def lat_stats(latencies):
    return {
        "avg_ms": round(statistics.mean(latencies), 1),
        "p50_ms": round(percentile(latencies, 50), 1),
        "p95_ms": round(percentile(latencies, 95), 1),
        "p99_ms": round(percentile(latencies, 99), 1),
        "min_ms": round(min(latencies), 1),
        "max_ms": round(max(latencies), 1),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--es-url", default=ES_URL_DEFAULT)
    parser.add_argument("--indices", required=True, help='Format: "label:index,label2:index2,..."')
    parser.add_argument("--topk", type=int, default=10)
    parser.add_argument("--num-candidates", type=int, default=100)
    parser.add_argument("--warmup", type=int, default=3)
    # Keep filename aligned with project plan.
    parser.add_argument("--output", default="data/benchmark_results.json")
    args = parser.parse_args()

    indices = parse_indices_arg(args.indices)
    es = Elasticsearch(args.es_url, request_timeout=60)
    if not es.ping():
        raise SystemExit(f"Elasticsearch not reachable: {args.es_url}")

    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print(f"Model ready (device: {model.device})")

    results = {
        "timestamp": datetime.now().isoformat(),
        "es_url": args.es_url,
        "num_queries": len(TEST_QUERIES),
        "topk": args.topk,
        "indices": [],
    }

    for entry in indices:
        label = entry["label"]
        index = entry["index"]
        print(f"\n== [{label}] index={index} ==")

        if not es.indices.exists(index=index):
            raise SystemExit(f"Index not found: {index}")

        idx_info = get_index_info(es, index)
        jvm = get_jvm_info(es)
        print(f"Docs: {idx_info['doc_count']:,} | Size: {idx_info['size_mb']:.1f} MB | Heap: {jvm.get('heap_used_mb', 0):.1f} MB")

        for q in TEST_QUERIES[: args.warmup]:
            _ = run_bm25(es, index, q, size=1)
            _ = run_knn(es, index, model, q, size=1, num_candidates=args.num_candidates)
            _ = run_hybrid_rrf(es, index, model, q, size=1, num_candidates=args.num_candidates)

        bm25_lats, knn_lats, hyb_lats = [], [], []
        for q in TEST_QUERIES:
            bm25_lats.append(run_bm25(es, index, q, size=args.topk))
            knn_lats.append(run_knn(es, index, model, q, size=args.topk, num_candidates=args.num_candidates))
            hyb_lats.append(run_hybrid_rrf(es, index, model, q, size=args.topk, num_candidates=args.num_candidates))

        results["indices"].append({
            "label": label,
            "index": index,
            "index_info": idx_info,
            "jvm": jvm,
            "bm25": lat_stats(bm25_lats),
            "knn": lat_stats(knn_lats),
            "hybrid_rrf": lat_stats(hyb_lats),
        })

        out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", args.output))
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Saved partial results to: {args.output}")

    out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", args.output))
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nDone. Results saved to: {args.output}")


if __name__ == "__main__":
    main()

