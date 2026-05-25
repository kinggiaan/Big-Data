"""
Sequential multi-scale benchmark: index → benchmark → delete → next scale.
Avoids keeping multiple large indices in memory simultaneously.

Usage:
  python -m src.evaluation.benchmark_sequential
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import os
import time
import statistics
from datetime import datetime
from elasticsearch import Elasticsearch, helpers
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

ES_URL = "http://localhost:9200"
INDEX_NAME = "arxiv_bench"  # Single reusable index name
OUTPUT_FILE = "data/benchmark_results.json"

SCALES = [
    {"label": "1.2M", "file": "data/arxiv_cs_full_with_vectors.jsonl", "docs": 1203108},
]

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

INDEX_SETTINGS = {
    "settings": {
        "number_of_shards": 2,
        "number_of_replicas": 0,
        "refresh_interval": "-1",
        "analysis": {
            "analyzer": {
                "academic_english": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "english_stop", "english_stemmer"]
                }
            },
            "filter": {
                "english_stop": {"type": "stop", "stopwords": "_english_"},
                "english_stemmer": {"type": "stemmer", "language": "english"}
            }
        }
    },
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "title": {"type": "text", "analyzer": "academic_english", "fields": {"raw": {"type": "keyword"}}},
            "abstract": {"type": "text", "analyzer": "academic_english"},
            "categories": {"type": "keyword"},
            "authors": {"type": "text"},
            "year": {"type": "keyword"},
            "embedding": {"type": "dense_vector", "dims": 384, "index": True, "similarity": "cosine"},
        }
    }
}


def percentile(data, p):
    s = sorted(data)
    k = (len(s) - 1) * (p / 100)
    f = int(k)
    c = min(f + 1, len(s) - 1)
    return s[f] + (k - f) * (s[c] - s[f])


def lat_stats(latencies):
    return {
        "avg_ms": round(statistics.mean(latencies), 1),
        "p50_ms": round(percentile(latencies, 50), 1),
        "p95_ms": round(percentile(latencies, 95), 1),
        "p99_ms": round(percentile(latencies, 99), 1),
        "min_ms": round(min(latencies), 1),
        "max_ms": round(max(latencies), 1),
    }


def stream_actions(input_file, index_name):
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            categories = record.get("categories", "")
            if isinstance(categories, str):
                categories = categories.split()
            yield {
                "_index": index_name,
                "_id": record["id"],
                "_source": {
                    "title": record.get("title", ""),
                    "abstract": record.get("abstract", ""),
                    "categories": categories,
                    "authors": record.get("authors", ""),
                    "year": record.get("year"),
                    "embedding": record["embedding"],
                }
            }


def index_scale(es, scale_info):
    """Index one scale and return indexing stats."""
    label = scale_info["label"]
    input_file = scale_info["file"]

    if not os.path.exists(input_file):
        print(f"  ERROR: File not found: {input_file}")
        return None

    # Delete old index if exists
    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME, ignore=[404])

    # Create index
    es.indices.create(index=INDEX_NAME, body=INDEX_SETTINGS)

    # Count lines
    total = 0
    with open(input_file, "r", encoding="utf-8") as f:
        for _ in f:
            total += 1

    print(f"  Indexing {total:,} docs from {input_file}...")
    start = time.time()

    pbar = tqdm(total=total, desc=f"  [{label}] Indexing", unit="doc")
    success = 0
    errors = 0
    for ok, result in helpers.streaming_bulk(
        es, stream_actions(input_file, INDEX_NAME),
        chunk_size=1000, request_timeout=120, raise_on_error=False,
    ):
        if ok:
            success += 1
        else:
            errors += 1
        pbar.update(1)
    pbar.close()

    indexing_time = time.time() - start

    # Restore refresh
    es.indices.put_settings(index=INDEX_NAME, body={"index": {"refresh_interval": "1s"}})
    es.indices.refresh(index=INDEX_NAME)

    # Stats
    count = es.count(index=INDEX_NAME)["count"]
    stats = es.indices.stats(index=INDEX_NAME)
    size_mb = stats["indices"][INDEX_NAME]["total"]["store"]["size_in_bytes"] / (1024 * 1024)

    print(f"  Indexed: {count:,} docs | Size: {size_mb:.1f} MB | Time: {indexing_time:.0f}s | Speed: {count/indexing_time:.0f} docs/sec")

    return {
        "doc_count": count,
        "size_mb": round(size_mb, 1),
        "indexing_time_sec": round(indexing_time, 1),
        "indexing_speed_docs_per_sec": round(count / indexing_time, 0),
        "errors": errors,
    }


def benchmark_queries(es, model, num_candidates=100, topk=10):
    """Run BM25, kNN, Hybrid benchmarks on current index."""

    # Warm up
    for q in TEST_QUERIES[:5]:
        es.search(index=INDEX_NAME, query={"match": {"title": q}}, size=1)
        vec = model.encode(q, normalize_embeddings=True).tolist()
        es.search(index=INDEX_NAME, knn={"field": "embedding", "query_vector": vec, "k": 1, "num_candidates": 10}, size=1)

    bm25_lats, knn_lats, hyb_lats = [], [], []

    for q in TEST_QUERIES:
        # BM25
        start = time.perf_counter()
        es.search(
            index=INDEX_NAME,
            query={"multi_match": {"query": q, "fields": ["title^2", "abstract"]}},
            size=topk, _source=False,
        )
        bm25_lats.append((time.perf_counter() - start) * 1000)

        # kNN
        vec = model.encode(q, normalize_embeddings=True).tolist()
        start = time.perf_counter()
        es.search(
            index=INDEX_NAME,
            knn={"field": "embedding", "query_vector": vec, "k": topk, "num_candidates": num_candidates},
            size=topk, _source=False,
        )
        knn_lats.append((time.perf_counter() - start) * 1000)

        # Hybrid RRF
        start = time.perf_counter()
        bm25_resp = es.search(
            index=INDEX_NAME,
            query={"multi_match": {"query": q, "fields": ["title^2", "abstract"]}},
            size=20, _source=False,
        )
        knn_resp = es.search(
            index=INDEX_NAME,
            knn={"field": "embedding", "query_vector": vec, "k": 20, "num_candidates": num_candidates},
            size=20, _source=False,
        )
        scores = {}
        for rank, hit in enumerate(bm25_resp["hits"]["hits"], 1):
            scores[hit["_id"]] = scores.get(hit["_id"], 0) + 1.0 / (60 + rank)
        for rank, hit in enumerate(knn_resp["hits"]["hits"], 1):
            scores[hit["_id"]] = scores.get(hit["_id"], 0) + 1.0 / (60 + rank)
        _ = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:topk]
        hyb_lats.append((time.perf_counter() - start) * 1000)

    return {
        "bm25": lat_stats(bm25_lats),
        "knn": lat_stats(knn_lats),
        "hybrid_rrf": lat_stats(hyb_lats),
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
    es = Elasticsearch(ES_URL, request_timeout=120)
    if not es.ping():
        print("ERROR: Elasticsearch not reachable")
        return

    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print(f"Device: {model.device}\n")

    loaded_indices = []
    for fn in ["data/benchmark_results_partial.json", OUTPUT_FILE]:
        if os.path.exists(fn):
            try:
                with open(fn, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict) and "indices" in loaded:
                        loaded_indices = loaded["indices"]
                        print(f"Successfully loaded existing results from {fn}")
                        break
            except Exception as e:
                print(f"Failed to load from {fn}: {e}")

    results = {
        "timestamp": datetime.now().isoformat(),
        "es_url": ES_URL,
        "num_queries": len(TEST_QUERIES),
        "topk": 10,
        "strategy": "sequential (index → benchmark → delete → next)",
        "indices": [idx for idx in loaded_indices if idx["label"] != "1.2M"],
    }

    for scale in SCALES:
        label = scale["label"]
        print(f"\n{'='*60}")
        print(f"  SCALE: {label}")
        print(f"{'='*60}")

        # Index
        idx_info = index_scale(es, scale)
        if idx_info is None:
            continue

        # Benchmark queries
        print(f"  Running benchmark ({len(TEST_QUERIES)} queries × 3 modes)...")
        latency = benchmark_queries(es, model)

        bm25 = latency["bm25"]
        knn = latency["knn"]
        hyb = latency["hybrid_rrf"]
        print(f"  BM25:   Avg={bm25['avg_ms']}ms  P50={bm25['p50_ms']}ms  P95={bm25['p95_ms']}ms")
        print(f"  kNN:    Avg={knn['avg_ms']}ms  P50={knn['p50_ms']}ms  P95={knn['p95_ms']}ms")
        print(f"  Hybrid: Avg={hyb['avg_ms']}ms  P50={hyb['p50_ms']}ms  P95={hyb['p95_ms']}ms")

        # JVM stats
        jvm = get_jvm_info(es)
        print(f"  JVM:    Heap {jvm.get('heap_used_mb', '?')} / {jvm.get('heap_max_mb', '?')} MB ({jvm.get('heap_percent', '?')}%)")

        results["indices"].append({
            "label": label,
            "index": INDEX_NAME,
            "index_info": idx_info,
            "jvm": jvm,
            **latency,
        })

        # Save partial results after each scale
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"  Saved partial results to {OUTPUT_FILE}")

        # Delete index to free memory for next scale (except the last one)
        if scale != SCALES[-1]:
            print(f"  Deleting index to free memory...")
            es.indices.delete(index=INDEX_NAME, ignore=[404])
            # Wait a moment for GC
            time.sleep(5)

    print(f"\n{'='*60}")
    print(f"  ALL SCALES COMPLETE")
    print(f"{'='*60}")
    print(f"  Results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
