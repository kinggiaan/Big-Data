"""
Index arXiv CS papers WITH vectors into Elasticsearch.
Streaming JSONL reader — does NOT load entire file into RAM.
Supports dense_vector for kNN search, custom academic_english analyzer, 2 shards.

Usage:
  .\venv\Scripts\python.exe src\index_data_v2.py
  .\venv\Scripts\python.exe src\index_data_v2.py --input data/arxiv_cs_full_with_vectors.jsonl --index arxiv_papers_v2
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import argparse
import json
import os
import time
from elasticsearch import Elasticsearch, helpers
from tqdm import tqdm

ES_URL = "http://localhost:9200"
DEFAULT_INPUT = "data/arxiv_cs_100k_with_vectors.jsonl"
DEFAULT_INDEX = "arxiv_papers_v2"

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


def count_lines(path):
    count = 0
    with open(path, "r", encoding="utf-8") as f:
        for _ in f:
            count += 1
    return count


def stream_actions(input_file, index_name):
    """Yield bulk actions by streaming JSONL line-by-line."""
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


def main():
    parser = argparse.ArgumentParser(description="Index arXiv papers + vectors into ES")
    parser.add_argument("--input", default=DEFAULT_INPUT, help="Input JSONL file with embeddings")
    parser.add_argument("--index", default=DEFAULT_INDEX, help="ES index name")
    parser.add_argument("--chunk-size", type=int, default=500, help="Bulk chunk size")
    args = parser.parse_args()

    es = Elasticsearch(ES_URL, request_timeout=120)

    if not es.ping():
        print("ERROR: Cannot connect to Elasticsearch at", ES_URL)
        print("Make sure Docker is running: docker compose up -d")
        return

    print(f"Connected to Elasticsearch")
    print(f"Input:  {args.input}")
    print(f"Index:  {args.index}")
    print(f"Chunk:  {args.chunk_size}")
    print()

    if not os.path.exists(args.input):
        print(f"ERROR: File not found: {args.input}")
        return

    print("Counting records...")
    total = count_lines(args.input)
    file_size = os.path.getsize(args.input) / (1024 * 1024)
    print(f"Records: {total:,}  |  File size: {file_size:.1f} MB")
    print()

    if es.indices.exists(index=args.index):
        print(f"Index '{args.index}' exists. Deleting...")
        es.indices.delete(index=args.index)

    print(f"Creating index '{args.index}' (2 shards, academic_english analyzer, dense_vector)...")
    es.indices.create(index=args.index, body=INDEX_SETTINGS)
    print("Index created!\n")

    print(f"Indexing {total:,} documents...")
    start = time.time()

    pbar = tqdm(total=total, desc="Indexing", unit="doc")
    success_count = 0
    error_count = 0

    for ok, result in helpers.streaming_bulk(
        es,
        stream_actions(args.input, args.index),
        chunk_size=args.chunk_size,
        request_timeout=120,
        raise_on_error=False,
    ):
        if ok:
            success_count += 1
        else:
            error_count += 1
            if error_count <= 5:
                print(f"  Error: {result}")
        pbar.update(1)

    pbar.close()
    elapsed = time.time() - start

    print(f"\nIndexing complete in {elapsed:.1f}s ({total / elapsed:.0f} docs/sec)")
    print(f"  Success: {success_count:,}")
    if error_count:
        print(f"  Errors:  {error_count:,}")

    print("\nRestoring refresh interval...")
    es.indices.put_settings(index=args.index, body={"index": {"refresh_interval": "1s"}})
    es.indices.refresh(index=args.index)

    count = es.count(index=args.index)["count"]
    stats = es.indices.stats(index=args.index)
    size_mb = stats["indices"][args.index]["total"]["store"]["size_in_bytes"] / (1024 * 1024)

    print(f"\nVerification:")
    print(f"  Documents in index: {count:,}")
    print(f"  Index size: {size_mb:.1f} MB")
    print(f"\nDone! Index '{args.index}' is ready for BM25 + kNN search.")


if __name__ == "__main__":
    main()

