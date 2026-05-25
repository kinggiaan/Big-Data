"""
Extract ALL Computer Science papers from the full arXiv dataset.
Streams line-by-line to handle the 4.8GB file without loading into RAM.
Output: JSONL format (one JSON object per line).

Usage: .\venv\Scripts\python.exe src\data_prep_full.py
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import os
import time
from tqdm import tqdm

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")

INPUT_FILE = os.path.join(DATA_DIR, "arxiv-metadata-oai-snapshot.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "arxiv_cs_full.jsonl")


def extract_cs_papers():
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: {INPUT_FILE} not found!")
        print("Download from: https://www.kaggle.com/datasets/Cornell-University/arxiv")
        return

    print(f"Input:  {INPUT_FILE}")
    print(f"Output: {OUTPUT_FILE}")
    print("Streaming full dataset, filtering CS papers...\n")

    total_scanned = 0
    cs_count = 0
    skipped = 0
    start = time.time()

    with open(INPUT_FILE, "r", encoding="utf-8") as fin, open(OUTPUT_FILE, "w", encoding="utf-8") as fout:
        for line in tqdm(fin, desc="Scanning", unit=" lines"):
            total_scanned += 1
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                skipped += 1
                continue

            categories = record.get("categories", "")
            if "cs." not in categories:
                continue

            title = record.get("title", "").replace("\n", " ").strip()
            abstract = record.get("abstract", "").replace("\n", " ").strip()

            if not title or not abstract:
                skipped += 1
                continue

            # Parse year from arXiv ID (more accurate than update_date)
            arxiv_id = record.get("id", "")
            year = None
            if "." in arxiv_id:
                prefix = arxiv_id.split(".")[0]
                if "/" in prefix:
                    prefix = prefix.split("/")[-1]
                if len(prefix) == 4 and prefix.isdigit():
                    yy = int(prefix[:2])
                    year = str(2000 + yy) if yy < 90 else str(1900 + yy)
            if year is None:
                update_date = record.get("update_date", "")
                year = update_date.split("-")[0] if update_date else None

            clean = {
                "id": record.get("id"),
                "title": title,
                "abstract": abstract,
                "categories": categories,
                "authors": record.get("authors", ""),
                "year": year,
            }

            fout.write(json.dumps(clean, ensure_ascii=False) + "\n")
            cs_count += 1

    elapsed = time.time() - start
    output_size = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)

    print(f"\nDone in {elapsed:.1f}s")
    print(f"  Scanned:  {total_scanned:,} records")
    print(f"  CS found: {cs_count:,} papers")
    print(f"  Skipped:  {skipped:,} (bad JSON or missing title/abstract)")
    print(f"  Output:   {OUTPUT_FILE} ({output_size:.1f} MB)")


if __name__ == "__main__":
    extract_cs_papers()

