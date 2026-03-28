"""
Create JSONL subsets by truncating (optionally with offset).

Example:
  .\venv\Scripts\python.exe src\truncate_jsonl.py ^
    --input data/arxiv_cs_full_with_vectors.jsonl ^
    --output data/arxiv_cs_500k_with_vectors.jsonl ^
    --lines 500000
"""

import argparse


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--lines", type=int, required=True)
    p.add_argument("--offset", type=int, default=0)
    args = p.parse_args()

    if args.lines < 0 or args.offset < 0:
        raise SystemExit("--lines and --offset must be >= 0")

    kept = 0
    with open(args.input, "r", encoding="utf-8") as fin, open(args.output, "w", encoding="utf-8") as fout:
        for i, line in enumerate(fin):
            if i < args.offset:
                continue
            if kept >= args.lines:
                break
            line = line.strip()
            if not line:
                continue
            fout.write(line + "\n")
            kept += 1

    print(f"Done. Wrote {kept} JSONL records to: {args.output}")


if __name__ == "__main__":
    main()

