"""
Automate the setup of Dual-Index Architecture on Elasticsearch.
This script:
1. Creates the metadata-only index 'arxiv_text' using mappings in data/es_text_mapping.json.
2. Reindexes metadata from 'arxiv_bench' (the index with vectors) to 'arxiv_text'.
3. Configures the alias 'arxiv_vectors' to point to 'arxiv_bench'.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import json
from elasticsearch import Elasticsearch

ES_URL = "http://localhost:9200"
INDEX_BENCH = "arxiv_bench"
INDEX_TEXT = "arxiv_text"
ALIAS_VECTORS = "arxiv_vectors"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEXT_MAPPING_FILE = os.path.join(BASE_DIR, "data", "es_text_mapping.json")
REINDEX_FILE = os.path.join(BASE_DIR, "data", "es_reindex.json")
ALIAS_FILE = os.path.join(BASE_DIR, "data", "es_alias.json")

def main():
    es = Elasticsearch(ES_URL, request_timeout=300) # Reindexing large scales can take time

    if not es.ping():
        print(f"ERROR: Cannot connect to Elasticsearch at {ES_URL}")
        print("Please ensure Docker is running: docker compose up -d")
        sys.exit(1)
    print("Connected to Elasticsearch successfully.")

    # 1. Verify source index exists
    if not es.indices.exists(index=INDEX_BENCH):
        print(f"\nERROR: Source index '{INDEX_BENCH}' does not exist.")
        print("Please run index_data_v2.py first to load your dataset, for example:")
        print(f"  python -m src.pipeline.index_data_v2 --input data/arxiv_cs_100k_with_vectors.jsonl --index {INDEX_BENCH}")
        sys.exit(1)

    doc_count = es.count(index=INDEX_BENCH)["count"]
    print(f"Found source index '{INDEX_BENCH}' with {doc_count:,} documents.")

    # 2. Setup arxiv_text index
    print(f"\n--- Setting up '{INDEX_TEXT}' index ---")
    if not os.path.exists(TEXT_MAPPING_FILE):
        print(f"ERROR: Mapping file '{TEXT_MAPPING_FILE}' not found.")
        sys.exit(1)

    with open(TEXT_MAPPING_FILE, "r", encoding="utf-8") as f:
        text_mapping = json.load(f)

    if es.indices.exists(index=INDEX_TEXT):
        print(f"Index '{INDEX_TEXT}' already exists. Deleting and recreating...")
        es.indices.delete(index=INDEX_TEXT)

    es.indices.create(index=INDEX_TEXT, body=text_mapping)
    print(f"Index '{INDEX_TEXT}' created with academic_english analyzer.")

    # 3. Reindex metadata (excluding embeddings)
    print(f"\n--- Reindexing from '{INDEX_BENCH}' to '{INDEX_TEXT}' ---")
    if not os.path.exists(REINDEX_FILE):
        print(f"ERROR: Reindex configuration '{REINDEX_FILE}' not found.")
        sys.exit(1)

    with open(REINDEX_FILE, "r", encoding="utf-8") as f:
        reindex_body = json.load(f)

    print("Reindexing in progress (this might take a few minutes for larger scales)...")
    res = es.reindex(body=reindex_body, wait_for_completion=True)
    print(f"Reindex complete! Created/updated {res.get('created', 0):,} documents in '{INDEX_TEXT}'.")

    # 4. Setup alias
    print(f"\n--- Configuring alias '{ALIAS_VECTORS}' -> '{INDEX_BENCH}' ---")
    if not os.path.exists(ALIAS_FILE):
        print(f"ERROR: Alias file '{ALIAS_FILE}' not found.")
        sys.exit(1)

    with open(ALIAS_FILE, "r", encoding="utf-8") as f:
        alias_body = json.load(f)

    # Remove alias if it exists
    if es.indices.exists_alias(name=ALIAS_VECTORS):
        print(f"Alias '{ALIAS_VECTORS}' already exists. Updating...")
        # Get indices currently associated with the alias
        old_indices = list(es.indices.get_alias(name=ALIAS_VECTORS).keys())
        actions = []
        for old_idx in old_indices:
            actions.append({"remove": {"index": old_idx, "alias": ALIAS_VECTORS}})
        actions.extend(alias_body.get("actions", []))
        es.indices.update_aliases(body={"actions": actions})
    else:
        es.indices.update_aliases(body=alias_body)
    print(f"Alias '{ALIAS_VECTORS}' configured successfully.")

    # 5. Verification
    print("\n--- Verifying Setup ---")
    es.indices.refresh(index=INDEX_TEXT)
    es.indices.refresh(index=INDEX_BENCH)

    text_docs = es.count(index=INDEX_TEXT)["count"]
    vector_docs = es.count(index=ALIAS_VECTORS)["count"]

    print(f"  {INDEX_TEXT:20s}: {text_docs:,} documents")
    print(f"  {ALIAS_VECTORS:20s}: {vector_docs:,} documents (pointing to {INDEX_BENCH})")

    if text_docs == doc_count and vector_docs == doc_count:
        print("\n🎉 Dual-index configuration setup successfully!")
    else:
        print("\n⚠️ WARNING: Document count mismatch. Please run 'verify_sync.sh' to inspect.")

if __name__ == "__main__":
    main()
