"""
Helper script to view candidate papers for ground truth labeling.
Shows title + abstract for each candidate in each query,
so human annotators can decide which papers are relevant.

Usage:
  python src/evaluation/view_candidates.py --query-id 1
  python src/evaluation/view_candidates.py --all
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import argparse
import json
from elasticsearch import Elasticsearch

from src.config import ES_URL, INDEX_TEXT


def load_ground_truth(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_paper(es, index, doc_id):
    """Fetch a single paper by ID."""
    try:
        resp = es.get(index=index, id=doc_id, _source=["title", "abstract", "year", "categories"])
        return resp["_source"]
    except Exception:
        return None


def display_query(es, index, query_entry):
    """Display all candidates for one query."""
    qid = query_entry["id"]
    qtext = query_entry["query"]
    group = query_entry.get("group", "?")
    relevant = query_entry.get("relevant_ids", [])
    candidates = query_entry.get("candidates", {})

    print(f"\n{'='*80}")
    print(f"Query #{qid} [{group}]: \"{qtext}\"")
    print(f"Already labeled relevant: {len(relevant)} papers")
    print(f"{'='*80}")

    # Collect all unique candidate IDs
    all_ids = set()
    for method, ids in candidates.items():
        all_ids.update(ids)

    print(f"\nTotal unique candidates: {len(all_ids)}")
    print(f"Sources: BM25={len(candidates.get('bm25',[]))}, "
          f"kNN={len(candidates.get('knn',[]))}, "
          f"Hybrid={len(candidates.get('hybrid',[]))}")

    # Show each candidate
    for i, doc_id in enumerate(sorted(all_ids), 1):
        paper = fetch_paper(es, index, doc_id)
        if not paper:
            print(f"\n  [{i}] ID: {doc_id} — NOT FOUND IN INDEX")
            continue

        # Which methods returned this paper?
        sources = []
        for method, ids in candidates.items():
            if doc_id in ids:
                rank = ids.index(doc_id) + 1
                sources.append(f"{method}(#{rank})")

        is_relevant = "✅ RELEVANT" if doc_id in relevant else "⬜ NOT LABELED"

        title = paper.get("title", "N/A")
        abstract = paper.get("abstract", "N/A")[:300]
        year = paper.get("year", "?")
        cats = paper.get("categories", [])
        if isinstance(cats, list):
            cats = ", ".join(cats)

        print(f"\n  [{i}] {is_relevant}")
        print(f"      ID:    {doc_id}")
        print(f"      From:  {', '.join(sources)}")
        print(f"      Year:  {year} | Categories: {cats}")
        print(f"      Title: {title}")
        print(f"      Abstract: {abstract}...")


def main():
    parser = argparse.ArgumentParser(description="View candidates for ground truth labeling")
    parser.add_argument("--ground-truth", default="data/ground_truth.json")
    parser.add_argument("--index", default=INDEX_TEXT,
                        help="ES index for fetching paper metadata (default: INDEX_TEXT)")
    parser.add_argument("--es-url", default=ES_URL)
    parser.add_argument("--query-id", type=int, default=None, help="Show specific query ID")
    parser.add_argument("--all", action="store_true", help="Show all queries")
    args = parser.parse_args()

    es = Elasticsearch(args.es_url, request_timeout=30)
    if not es.ping():
        print(f"ERROR: Cannot connect to Elasticsearch at {args.es_url}")
        return

    gt = load_ground_truth(args.ground_truth)
    queries = gt.get("queries", [])

    if args.query_id is not None:
        entry = next((q for q in queries if q["id"] == args.query_id), None)
        if not entry:
            print(f"Query ID {args.query_id} not found in ground truth file")
            return
        display_query(es, args.index, entry)
    elif args.all:
        for entry in queries:
            display_query(es, args.index, entry)
    else:
        print("Usage: specify --query-id N or --all")
        print(f"Available query IDs: {[q['id'] for q in queries]}")


if __name__ == "__main__":
    main()
