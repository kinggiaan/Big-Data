"""
Incremental ingestion pipeline for the dual-index Elasticsearch architecture.

Pushes new papers into BOTH indices:
  - arxiv_text   : metadata only (title, abstract, authors, year, categories)
  - arxiv_vectors : paper id + 384-dim dense embedding

Supports single-paper mode (--paper JSON) and batch mode (--file JSONL).
Uses the same abstract truncation logic as embed_data.py (960 chars max).

Usage:
  python -m src.pipeline.ingest --paper '{"id":"2401.12345", ...}'
  python -m src.pipeline.ingest --file new_papers.jsonl
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import argparse
import json

from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

from src.config import ES_URL, INDEX_TEXT, INDEX_VECTORS, MODEL_NAME

# Abstract truncation threshold (same as embed_data.py)
# Title ~15 tokens + [SEP] ~1 token → ~240 tokens left for abstract
# 1 token ≈ 4 chars → 240 × 4 = 960 chars
MAX_ABSTRACT_CHARS = 960


# ---------------------------------------------------------------------------
# Embedding helpers
# ---------------------------------------------------------------------------

def truncate_abstract(abstract: str) -> str:
    """Truncate abstract to fit model's max_seq_length (256 tokens).

    Tries to cut at the last sentence boundary within the first 960 chars.
    Falls back to a hard cut if no good boundary is found.
    """
    if len(abstract) <= MAX_ABSTRACT_CHARS:
        return abstract

    cut = abstract[:MAX_ABSTRACT_CHARS]
    last_period = cut.rfind(". ")
    if last_period > MAX_ABSTRACT_CHARS * 0.6:
        return cut[:last_period + 1]
    return cut


def build_text(title: str, abstract: str) -> str:
    """Build the input string for the embedding model: title [SEP] abstract."""
    return f"{title} [SEP] {truncate_abstract(abstract)}"


def generate_embedding(model: SentenceTransformer, title: str, abstract: str) -> list:
    """Generate a single 384-dim embedding vector for a paper."""
    text = build_text(title, abstract)
    vector = model.encode(text, normalize_embeddings=True)
    return vector.tolist()


# ---------------------------------------------------------------------------
# Elasticsearch helpers
# ---------------------------------------------------------------------------

def index_to_text(es: Elasticsearch, paper: dict) -> None:
    """Upsert a paper's metadata into the arxiv_text index (BM25)."""
    categories = paper.get("categories", "")
    if isinstance(categories, str):
        categories = categories.split()

    doc = {
        "title":      paper.get("title", ""),
        "abstract":   paper.get("abstract", ""),
        "authors":    paper.get("authors", ""),
        "year":       paper.get("year"),
        "categories": categories,
    }

    es.index(index=INDEX_TEXT, id=paper["id"], document=doc)


def index_to_vectors(es: Elasticsearch, paper_id: str, embedding: list) -> None:
    """Upsert a paper's embedding into the arxiv_vectors index (kNN)."""
    doc = {
        "embedding": embedding,
    }

    es.index(index=INDEX_VECTORS, id=paper_id, document=doc)


def get_doc_count(es: Elasticsearch, index: str) -> int:
    """Return the document count for an index, refreshing first."""
    es.indices.refresh(index=index)
    return es.count(index=index)["count"]


# ---------------------------------------------------------------------------
# Ingestion logic
# ---------------------------------------------------------------------------

def ingest_paper(es: Elasticsearch, model: SentenceTransformer, paper: dict) -> None:
    """Ingest a single paper into both indices."""
    paper_id = paper["id"]
    title = paper.get("title", "")
    abstract = paper.get("abstract", "")

    # Generate embedding
    embedding = generate_embedding(model, title, abstract)

    # Upsert into both indices
    index_to_text(es, paper)
    index_to_vectors(es, paper_id, embedding)


def ingest_batch(es: Elasticsearch, model: SentenceTransformer, file_path: str) -> int:
    """Ingest papers from a JSONL file. Returns the number of papers ingested."""
    # Count total lines for progress reporting
    total = 0
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                total += 1

    print(f"Found {total:,} papers in {file_path}")

    ingested = 0
    with open(file_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            paper = json.loads(line)
            ingest_paper(es, model, paper)
            ingested += 1

            # Print progress every 10 papers or at the end
            if ingested % 10 == 0 or ingested == total:
                print(f"  Progress: {ingested}/{total} papers ingested", end="\r")

    print()  # newline after progress
    return ingested


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Ingest new papers into both Elasticsearch indices "
                    "(arxiv_text + arxiv_vectors)."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--paper",
        type=str,
        help="JSON string with paper fields: id, title, abstract, authors, year, categories",
    )
    group.add_argument(
        "--file",
        type=str,
        help="Path to a JSONL file (one JSON object per line)",
    )
    args = parser.parse_args()

    # --- Connect to Elasticsearch ---
    es = Elasticsearch(ES_URL, request_timeout=30)
    if not es.ping():
        print(f"ERROR: Cannot connect to Elasticsearch at {ES_URL}")
        print("Make sure Docker is running: docker compose up -d")
        sys.exit(1)
    print(f"Connected to Elasticsearch at {ES_URL}")

    # --- Load embedding model ---
    print(f"Loading model '{MODEL_NAME}'...")
    model = SentenceTransformer(MODEL_NAME)
    print(f"Model loaded (device: {model.device})")
    print()

    # --- Ingest ---
    if args.paper:
        # Single paper mode
        paper = json.loads(args.paper)
        print(f"Ingesting single paper: {paper['id']}")
        ingest_paper(es, model, paper)
        print(f"Paper '{paper['id']}' ingested successfully.")
    else:
        # Batch mode
        print(f"Batch ingestion from: {args.file}")
        count = ingest_batch(es, model, args.file)
        print(f"Batch complete: {count:,} papers ingested.")

    # --- Verification ---
    print()
    print("Verification:")
    text_count = get_doc_count(es, INDEX_TEXT)
    vectors_count = get_doc_count(es, INDEX_VECTORS)
    print(f"  {INDEX_TEXT:20s} : {text_count:,} documents")
    print(f"  {INDEX_VECTORS:20s} : {vectors_count:,} documents")
    print()
    print("Done!")


if __name__ == "__main__":
    main()
