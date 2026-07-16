"""
Migrate papers from JSONL to Cloudflare D1.
Reads the local JSONL file and generates SQL INSERT batches,
then executes them on D1 via wrangler CLI.

Usage:
    python cloudflare/scripts/migrate_to_d1.py
    python cloudflare/scripts/migrate_to_d1.py --input data/arxiv_cs_100k_clean_with_vectors.jsonl
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

# Project root
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DEFAULT_INPUT = os.path.join(ROOT, "data", "arxiv_cs_100k_clean_with_vectors.jsonl")
DB_NAME = "arxiv-search"
BATCH_SIZE = 50  # D1 has a limit on SQL statement size


def escape_sql(s):
    """Escape single quotes for SQL."""
    if s is None:
        return ""
    return str(s).replace("'", "''")


def build_insert_batch(records):
    """Build a single INSERT statement for a batch of records."""
    values = []
    for r in records:
        cats = r.get("categories", "")
        if isinstance(cats, list):
            cats = " ".join(cats)
        values.append(
            f"('{escape_sql(r['id'])}', "
            f"'{escape_sql(r.get('title', ''))}', "
            f"'{escape_sql(r.get('abstract', ''))}', "
            f"'{escape_sql(r.get('authors', ''))}', "
            f"'{escape_sql(r.get('year', ''))}', "
            f"'{escape_sql(cats)}')"
        )
    return (
        "INSERT OR IGNORE INTO papers (id, title, abstract, authors, year, categories) VALUES\n"
        + ",\n".join(values)
        + ";"
    )


def count_lines(path):
    count = 0
    with open(path, "r", encoding="utf-8") as f:
        for _ in f:
            count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description="Migrate papers to Cloudflare D1")
    parser.add_argument("--input", default=DEFAULT_INPUT, help="Input JSONL file")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    parser.add_argument("--dry-run", action="store_true", help="Only generate SQL, don't execute")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"ERROR: File not found: {args.input}")
        sys.exit(1)

    # Check for API token
    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not token and not args.dry_run:
        print("ERROR: CLOUDFLARE_API_TOKEN environment variable not set")
        sys.exit(1)

    total = count_lines(args.input)
    print(f"Input: {args.input}")
    print(f"Total records: {total}")
    print(f"Batch size: {args.batch_size}")
    print()

    batch = []
    batch_num = 0
    success = 0
    errors = 0

    with open(args.input, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            record = json.loads(line)
            # Strip embedding field - D1 doesn't need it
            record.pop("embedding", None)
            batch.append(record)

            if len(batch) >= args.batch_size or line_num == total:
                batch_num += 1
                sql = build_insert_batch(batch)

                if args.dry_run:
                    print(f"--- Batch {batch_num} ({len(batch)} records) ---")
                    print(sql[:500] + "..." if len(sql) > 500 else sql)
                    print()
                    success += len(batch)
                else:
                    # Write SQL to temp file and execute via wrangler
                    with tempfile.NamedTemporaryFile(
                        mode="w", suffix=".sql", delete=False, encoding="utf-8"
                    ) as tmp:
                        tmp.write(sql)
                        tmp_path = tmp.name

                    try:
                        result = subprocess.run(
                            [
                                "wrangler", "d1", "execute", DB_NAME,
                                "--remote", f"--file={tmp_path}", "--yes"
                            ],
                            capture_output=True,
                            encoding="utf-8",
                            env={**os.environ, "CLOUDFLARE_API_TOKEN": token},
                            cwd=os.path.join(ROOT, "cloudflare", "worker"),
                        )
                        if result.returncode == 0:
                            success += len(batch)
                            print(f"  Batch {batch_num}: {len(batch)} records OK ({success}/{total})")
                        else:
                            errors += len(batch)
                            print(f"  Batch {batch_num}: ERROR")
                            print(f"    stderr: {result.stderr[:300]}")
                    finally:
                        os.unlink(tmp_path)

                batch = []

    print(f"\nDone! Success: {success}, Errors: {errors}")


if __name__ == "__main__":
    main()
