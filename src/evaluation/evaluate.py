"""
Evaluate BM25 vs kNN vs Hybrid search quality and latency.
Runs 30 test queries, measures latency, and computes overlap metrics.
Manual relevance labeling can be added later for NDCG/MRR.

Usage: .\venv\Scripts\python.exe src\evaluate.py
"""
import argparse
import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import os
import time
import statistics
import math
from datetime import datetime
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

ES_URL = "http://localhost:9200"
INDEX = "arxiv_papers_v2"
QUERIES_FILE = "data/test_queries.json"
GROUND_TRUTH_FILE = "data/ground_truth.json"
OUTPUT_FILE = "data/evaluation_results.json"
RRF_K = 60
TOP_K = 10


def percentile(data, p):
    s = sorted(data)
    k = (len(s) - 1) * (p / 100)
    f = int(k)
    c = min(f + 1, len(s) - 1)
    return s[f] + (k - f) * (s[c] - s[f])


def run_bm25(es, query, size=TOP_K):
    start = time.perf_counter()
    resp = es.search(
        index=INDEX,
        query={"multi_match": {"query": query, "fields": ["title^2", "abstract"]}},
        size=size,
        _source=["title"],
    )
    latency = (time.perf_counter() - start) * 1000
    return [h["_id"] for h in resp["hits"]["hits"]], latency


def run_knn(es, model, query, size=TOP_K):
    vec = model.encode(query, normalize_embeddings=True).tolist()
    start = time.perf_counter()
    resp = es.search(
        index=INDEX,
        knn={"field": "embedding", "query_vector": vec, "k": size, "num_candidates": 100},
        size=size,
        _source=["title"],
    )
    latency = (time.perf_counter() - start) * 1000
    return [h["_id"] for h in resp["hits"]["hits"]], latency


def run_hybrid(es, model, query, size=TOP_K):
    vec = model.encode(query, normalize_embeddings=True).tolist()
    start = time.perf_counter()
    bm25_resp = es.search(
        index=INDEX,
        query={"multi_match": {"query": query, "fields": ["title^2", "abstract"]}},
        size=30, _source=["title"],
    )
    knn_resp = es.search(
        index=INDEX,
        knn={"field": "embedding", "query_vector": vec, "k": 30, "num_candidates": 100},
        size=30, _source=["title"],
    )

    scores = {}
    for rank, h in enumerate(bm25_resp["hits"]["hits"], 1):
        scores[h["_id"]] = scores.get(h["_id"], 0) + 1.0 / (RRF_K + rank)
    for rank, h in enumerate(knn_resp["hits"]["hits"], 1):
        scores[h["_id"]] = scores.get(h["_id"], 0) + 1.0 / (RRF_K + rank)

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:size]
    latency = (time.perf_counter() - start) * 1000
    return [did for did, _ in ranked], latency


def compute_ndcg(ranked_ids, relevant_ids, k=10):
    """Compute NDCG@k given ranked doc IDs and a set of relevant IDs."""
    if not relevant_ids:
        return 0.0

    dcg = 0.0
    for i, doc_id in enumerate(ranked_ids[:k]):
        rel = 1.0 if doc_id in relevant_ids else 0.0
        dcg += rel / math.log2(i + 2)

    num_rel = min(len(relevant_ids), k)
    if num_rel == 0:
        return 0.0
    idcg = sum(1.0 / math.log2(i + 2) for i in range(num_rel))
    return dcg / idcg if idcg > 0 else 0.0


def compute_mrr(ranked_ids, relevant_ids):
    """Compute MRR: 1/rank of first relevant result."""
    for i, doc_id in enumerate(ranked_ids):
        if doc_id in relevant_ids:
            return 1.0 / (i + 1)
    return 0.0


def load_ground_truth(path: str):
    """
    Optional manual relevance labels.

    Supported formats:
    - {"1": ["docid1", "docid2"], "2": [...], ...}              (query id -> relevant doc ids)
    - {"queries": [{"id": 1, "relevant_ids": [...]}, ...]}      (list form)
    """
    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as f:
        gt = json.load(f)

    if isinstance(gt, dict) and "queries" in gt and isinstance(gt["queries"], list):
        out = {}
        for q in gt["queries"]:
            qid = q.get("id")
            rel = q.get("relevant_ids") or q.get("relevant") or q.get("relevant_docs") or []
            if qid is None:
                continue
            out[str(qid)] = set(rel)
        return out

    if isinstance(gt, dict):
        out = {}
        for k, v in gt.items():
            if isinstance(v, list):
                out[str(k)] = set(v)
        return out or None

    return None


def main():
    parser = argparse.ArgumentParser(description="Evaluate BM25/kNN/Hybrid quality and latency (optional NDCG/MRR).")
    parser.add_argument("--es-url", default=ES_URL, help="Elasticsearch URL")
    parser.add_argument("--index", default=INDEX, help="Index name to evaluate (default: arxiv_papers_v2)")
    parser.add_argument("--queries", default=QUERIES_FILE, help="Test queries JSON file")
    parser.add_argument("--ground-truth", default=GROUND_TRUTH_FILE, help="Optional relevance labels JSON file")
    parser.add_argument("--output", default=OUTPUT_FILE, help="Output evaluation results JSON")
    parser.add_argument("--topk", type=int, default=TOP_K, help="Cutoff for ranked metrics / retrieval size")
    parser.add_argument("--rrf-k", type=int, default=RRF_K, help="RRF k constant for Hybrid")
    args = parser.parse_args()

    global ES_URL, INDEX, QUERIES_FILE, GROUND_TRUTH_FILE, OUTPUT_FILE, RRF_K, TOP_K
    ES_URL = args.es_url
    INDEX = args.index
    QUERIES_FILE = args.queries
    GROUND_TRUTH_FILE = args.ground_truth
    OUTPUT_FILE = args.output
    RRF_K = args.rrf_k
    TOP_K = args.topk

    es = Elasticsearch(ES_URL, request_timeout=30)
    if not es.ping():
        print("ERROR: Elasticsearch not reachable")
        return

    print("Loading model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    with open(QUERIES_FILE, "r", encoding="utf-8") as f:
        queries = json.load(f)

    ground_truth = load_ground_truth(GROUND_TRUTH_FILE)
    if ground_truth:
        print(f"Loaded ground truth: {GROUND_TRUTH_FILE}")
    else:
        print("No ground truth found (skipping NDCG/MRR).")

    print(f"Loaded {len(queries)} test queries")
    print(f"Index: {INDEX}")
    print()

    # Warm up
    print("Warming up...")
    for q in queries[:3]:
        run_bm25(es, q["query"], size=TOP_K)
        run_knn(es, model, q["query"], size=TOP_K)
    print()

    results_per_query = []
    bm25_lats, knn_lats, hyb_lats = [], [], []
    overlap_bk, overlap_bh, overlap_kh = [], [], []

    bm25_ndcgs, knn_ndcgs, hyb_ndcgs = [], [], []
    bm25_mrrs, knn_mrrs, hyb_mrrs = [], [], []

    for q in queries:
        qtext = q["query"]
        group = q["group"]
        qid = q.get("id")

        bm25_ids, bm25_lat = run_bm25(es, qtext, size=TOP_K)
        knn_ids, knn_lat = run_knn(es, model, qtext, size=TOP_K)
        hyb_ids, hyb_lat = run_hybrid(es, model, qtext, size=TOP_K)

        bm25_lats.append(bm25_lat)
        knn_lats.append(knn_lat)
        hyb_lats.append(hyb_lat)

        bm25_set = set(bm25_ids)
        knn_set = set(knn_ids)
        hyb_set = set(hyb_ids)

        o_bk = len(bm25_set & knn_set)
        o_bh = len(bm25_set & hyb_set)
        o_kh = len(knn_set & hyb_set)
        overlap_bk.append(o_bk)
        overlap_bh.append(o_bh)
        overlap_kh.append(o_kh)

        ndcg_b = ndcg_k = ndcg_h = None
        mrr_b = mrr_k = mrr_h = None
        if ground_truth and qid is not None:
            rel_ids = ground_truth.get(str(qid)) or set()
            ndcg_b = compute_ndcg(bm25_ids, rel_ids, k=TOP_K)
            ndcg_k = compute_ndcg(knn_ids, rel_ids, k=TOP_K)
            ndcg_h = compute_ndcg(hyb_ids, rel_ids, k=TOP_K)
            mrr_b = compute_mrr(bm25_ids, rel_ids)
            mrr_k = compute_mrr(knn_ids, rel_ids)
            mrr_h = compute_mrr(hyb_ids, rel_ids)
            bm25_ndcgs.append(ndcg_b)
            knn_ndcgs.append(ndcg_k)
            hyb_ndcgs.append(ndcg_h)
            bm25_mrrs.append(mrr_b)
            knn_mrrs.append(mrr_k)
            hyb_mrrs.append(mrr_h)

        results_per_query.append({
            "id": q["id"],
            "group": group,
            "query": qtext,
            "bm25_ids": bm25_ids,
            "knn_ids": knn_ids,
            "hybrid_ids": hyb_ids,
            "bm25_latency_ms": round(bm25_lat, 1),
            "knn_latency_ms": round(knn_lat, 1),
            "hybrid_latency_ms": round(hyb_lat, 1),
            "overlap_bm25_knn": o_bk,
            "overlap_bm25_hybrid": o_bh,
            "overlap_knn_hybrid": o_kh,
            f"ndcg@{TOP_K}": {
                "bm25": round(ndcg_b, 4) if isinstance(ndcg_b, float) else None,
                "knn": round(ndcg_k, 4) if isinstance(ndcg_k, float) else None,
                "hybrid": round(ndcg_h, 4) if isinstance(ndcg_h, float) else None,
            },
            "mrr": {
                "bm25": round(mrr_b, 4) if isinstance(mrr_b, float) else None,
                "knn": round(mrr_k, 4) if isinstance(mrr_k, float) else None,
                "hybrid": round(mrr_h, 4) if isinstance(mrr_h, float) else None,
            },
        })

        print(
            f"  [{q['id']:2d}] {group:12s} | BM25={bm25_lat:6.0f}ms kNN={knn_lat:6.0f}ms Hyb={hyb_lat:6.0f}ms | "
            f"Overlap B∩K={o_bk} B∩H={o_bh} K∩H={o_kh} | {qtext[:50]}"
        )

    # Summary
    print("\n" + "=" * 80)
    print("  EVALUATION SUMMARY")
    print("=" * 80)

    def _stats(lats):
        return {
            "avg": round(statistics.mean(lats), 1),
            "p50": round(percentile(lats, 50), 1),
            "p95": round(percentile(lats, 95), 1),
        }

    bm25_s = _stats(bm25_lats)
    knn_s = _stats(knn_lats)
    hyb_s = _stats(hyb_lats)

    print(f"\n  Latency (ms) over {len(queries)} queries:")
    print(f"  {'Mode':<12} {'Avg':>8} {'P50':>8} {'P95':>8}")
    print(f"  {'-'*12} {'-'*8} {'-'*8} {'-'*8}")
    print(f"  {'BM25':<12} {bm25_s['avg']:>8} {bm25_s['p50']:>8} {bm25_s['p95']:>8}")
    print(f"  {'kNN':<12} {knn_s['avg']:>8} {knn_s['p50']:>8} {knn_s['p95']:>8}")
    print(f"  {'Hybrid':<12} {hyb_s['avg']:>8} {hyb_s['p50']:>8} {hyb_s['p95']:>8}")

    avg_bk = statistics.mean(overlap_bk)
    avg_bh = statistics.mean(overlap_bh)
    avg_kh = statistics.mean(overlap_kh)
    print(f"\n  Avg Overlap (out of {TOP_K}):")
    print(f"    BM25 ∩ kNN:    {avg_bk:.1f}")
    print(f"    BM25 ∩ Hybrid: {avg_bh:.1f}")
    print(f"    kNN  ∩ Hybrid: {avg_kh:.1f}")

    # Save
    output = {
        "timestamp": datetime.now().isoformat(),
        "index": INDEX,
        "num_queries": len(queries),
        "top_k": TOP_K,
        "latency_summary": {
            "bm25": bm25_s,
            "knn": knn_s,
            "hybrid": hyb_s,
        },
        "overlap_summary": {
            "avg_bm25_knn": round(avg_bk, 2),
            "avg_bm25_hybrid": round(avg_bh, 2),
            "avg_knn_hybrid": round(avg_kh, 2),
        },
        "ground_truth": {
            "enabled": bool(ground_truth),
            "path": GROUND_TRUTH_FILE if ground_truth else None,
        },
        "per_query": results_per_query,
    }

    if ground_truth and bm25_ndcgs:
        output["ranking_metrics"] = {
            f"ndcg@{TOP_K}_avg": {
                "bm25": round(statistics.mean(bm25_ndcgs), 4),
                "knn": round(statistics.mean(knn_ndcgs), 4),
                "hybrid": round(statistics.mean(hyb_ndcgs), 4),
            },
            "mrr_avg": {
                "bm25": round(statistics.mean(bm25_mrrs), 4),
                "knn": round(statistics.mean(knn_mrrs), 4),
                "hybrid": round(statistics.mean(hyb_mrrs), 4),
            },
        }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n  Results saved to: {OUTPUT_FILE}")
    print()


if __name__ == "__main__":
    main()

