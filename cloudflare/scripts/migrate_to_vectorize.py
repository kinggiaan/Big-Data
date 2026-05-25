"""
Migrate vectors from JSONL to Cloudflare Vectorize.
Uses wrangler vectorize insert command to upload NDJSON vectors.

Usage:
    python3 cloudflare/scripts/migrate_to_vectorize.py
    python3 cloudflare/scripts/migrate_to_vectorize.py --input data/arxiv_cs_100k_clean_with_vectors.jsonl --max-vectors 13000
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_INPUT = os.path.join(ROOT, "data", "arxiv_cs_100k_clean_with_vectors.jsonl")
INDEX_NAME = "arxiv-vectors"
# Free plan: 5M stored dimensions / 384 dims = ~13,000 vectors max
DEFAULT_MAX = 13000
BATCH_SIZE = 500  # Vectorize insert batch limit


def main():
    parser = argparse.ArgumentParser(description="Migrate vectors to Cloudflare Vectorize")
    parser.add_argument("--input", default=DEFAULT_INPUT, help="Input JSONL file with embeddings")
    parser.add_argument("--max-vectors", type=int, default=DEFAULT_MAX,
                        help="Max vectors to upload (free plan limit ~13000 at 384d)")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"ERROR: File not found: {args.input}")
        sys.exit(1)

    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not token:
        print("ERROR: CLOUDFLARE_API_TOKEN environment variable not set")
        sys.exit(1)

    print(f"Input: {args.input}")
    print(f"Max vectors: {args.max_vectors}")
    print(f"Batch size: {args.batch_size}")
    print()

    batch = []
    total_uploaded = 0
    batch_num = 0

    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if total_uploaded + len(batch) >= args.max_vectors:
                break

            record = json.loads(line)
            embedding = record.get("embedding")
            if not embedding:
                continue

            # Vectorize NDJSON format: {"id": "...", "values": [...], "metadata": {...}}
            vec_record = {
                "id": record["id"],
                "values": embedding,
                "metadata": {
                    "title": (record.get("title", ""))[:200],  # Metadata limit 10KB
                    "year": record.get("year", ""),
                    "categories": record.get("categories", ""),
                }
            }
            batch.append(vec_record)

            if len(batch) >= args.batch_size:
                ok = upload_batch(batch, batch_num + 1, token)
                if ok:
                    total_uploaded += len(batch)
                batch_num += 1
                batch = []

    # Upload remaining
    if batch:
        ok = upload_batch(batch, batch_num + 1, token)
        if ok:
            total_uploaded += len(batch)
        batch_num += 1

    print(f"\nDone! Uploaded {total_uploaded} vectors in {batch_num} batches.")


def upload_batch(records, batch_num, token):
    """Write NDJSON to temp file and upload via wrangler."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".ndjson", delete=False, encoding="utf-8"
    ) as tmp:
        for r in records:
            tmp.write(json.dumps(r) + "\n")
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            [
                "wrangler", "vectorize", "insert", INDEX_NAME,
                f"--file={tmp_path}"
            ],
            capture_output=True,
            encoding="utf-8",
            env={**os.environ, "CLOUDFLARE_API_TOKEN": token},
            cwd=os.path.join(ROOT, "cloudflare", "worker"),
        )
        if result.returncode == 0:
            print(f"  Batch {batch_num}: {len(records)} vectors OK")
            return True
        else:
            print(f"  Batch {batch_num}: ERROR")
            print(f"    {result.stderr[:300]}")
            return False
    finally:
        os.unlink(tmp_path)


if __name__ == "__main__":
    main()
