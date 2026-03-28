"""
Generate a ground-truth template for NDCG/MRR (manual labeling).

Creates `data/ground_truth.json` in the format:
{
  "queries": [
    { "id": 1, "relevant_ids": [], "candidates": { "bm25": [...], "knn": [...], "hybrid": [...] } },
    ...
  ]
}

You only need to fill `relevant_ids` after this is generated.
"""

import argparse
import json
import sys
import time
import os

from datetime import datetime

from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer


def run_bm25(es, index: str, query: str, size: int):
    resp = es.search(
        index=index,
        query={"multi_match": {"query": query, "fields": ["title^2", "abstract"]}},
        size=size,
        _source=False,
    )
    return [h["_id"] for h in resp["hits"]["hits"]]


def run_knn(es, index: str, model, query: str, size: int, num_candidates: int):
    vec = model.encode(query, normalize_embeddings=True).tolist()
    resp = es.search(
        index=index,
        knn={"field": "embedding", "query_vector": vec, "k": size, "num_candidates": num_candidates},
        size=size,
        _source=False,
    )
    return [h["_id"] for h in resp["hits"]["hits"]]


def run_hybrid_rrf(es, index: str, model, query: str, size: int, rrf_k: int, num_candidates: int):
    # Mirror evaluate.py logic: BM25 + kNN top-N then RRF merge, then cut to `size`.
    retrieval_size = max(30, size)

    bm25_ids = run_bm25(es, index, query, size=retrieval_size)
    knn_ids = run_knn(es, index, query, size=retrieval_size, num_candidates=num_candidates)

    scores = {}
    for rank, did in enumerate(bm25_ids, 1):
        scores[did] = scores.get(did, 0.0) + 1.0 / (rrf_k + rank)
    for rank, did in enumerate(knn_ids, 1):
        scores[did] = scores.get(did, 0.0) + 1.0 / (rrf_k + rank)

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:size]
    return [did for did, _ in ranked]


def main():
    parser = argparse.ArgumentParser(description="Create ground_truth.json template (manual labeling for NDCG/MRR).")
    parser.add_argument("--es-url", default="http://localhost:9200")
    parser.add_argument("--index", default="arxiv_papers_v2_full", help="Index to generate labels for")
    parser.add_argument("--queries", default="data/test_queries.json")
    parser.add_argument("--output", default="data/ground_truth.json")
    parser.add_argument("--topk", type=int, default=10)
    parser.add_argument("--rrf-k", type=int, default=60)
    parser.add_argument("--num-candidates", type=int, default=100)
    args = parser.parse_args()

    es = Elasticsearch(args.es_url, request_timeout=60)
    if not es.ping():
        raise SystemExit(f"Elasticsearch not reachable: {args.es_url}")

    if not os.path.exists(args.queries):
        raise SystemExit(f"Queries file not found: {args.queries}")

    with open(args.queries, "r", encoding="utf-8") as f:
        queries = json.load(f)

    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print(f"Model ready (device={model.device})")

    out = {"generated_at": datetime.now().isoformat(), "queries": []}

    for q in queries:
        qid = q.get("id")
        qtext = q["query"]
        group = q.get("group")

        t0 = time.perf_counter()
        bm25_ids = run_bm25(es, args.index, qtext, size=args.topk)
        knn_ids = run_knn(es, args.index, model, qtext, size=args.topk, num_candidates=args.num_candidates)
        hyb_ids = run_hybrid_rrf(es, args.index, model, qtext, size=args.topk, rrf_k=args.rrf_k, num_candidates=args.num_candidates)
        dt = time.perf_counter() - t0

        if qid is None:
            raise SystemExit("Each test query must have an `id` field.")

        out["queries"].append({
            "id": qid,
            "group": group,
            "query": qtext,
            "relevant_ids": [],
            "candidates": {
                "bm25": bm25_ids,
                "knn": knn_ids,
                "hybrid": hyb_ids,
            },
            "generation_latency_sec": round(dt, 3),
        })

        print(f"Generated template for query id={qid} in {dt:.2f}s")

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"\nSaved template to: {args.output}")


if __name__ == "__main__":
    main()

