"""
Encode title + abstract of arXiv CS papers into 384-dim dense vectors
using sentence-transformers (all-MiniLM-L6-v2).

Supports both JSON array and JSONL input formats.
Writes JSONL output with checkpoint/resume capability.

Usage:
  .\venv\Scripts\python.exe src\embed_data.py                        # default: 100k
  .\venv\Scripts\python.exe src\embed_data.py --input data/arxiv_cs_full.jsonl  # full 1.16M
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import argparse
import json
import os
import time
from tqdm import tqdm
from sentence_transformers import SentenceTransformer


CHECKPOINT_INTERVAL = 10_000
MODEL_NAME = "all-MiniLM-L6-v2"
BATCH_SIZE_CPU = 64
BATCH_SIZE_GPU = 512


def count_lines(path):
    """Fast line count for progress bar."""
    if path.endswith(".jsonl"):
        count = 0
        with open(path, "r", encoding="utf-8") as f:
            for _ in f:
                count += 1
        return count
    else:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return len(data)


def read_records(path):
    """Yield records from JSON array or JSONL file."""
    if path.endswith(".jsonl"):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield json.loads(line)
    else:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for record in data:
            yield record


def count_existing(output_path):
    """Count already-processed records in output file (for resume)."""
    if not os.path.exists(output_path):
        return 0
    count = 0
    with open(output_path, "r", encoding="utf-8") as f:
        for _ in f:
            count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description="Embed arXiv papers")
    parser.add_argument("--input", default="data/arxiv_cs_100k_clean.json", help="Input file (JSON array or JSONL)")
    parser.add_argument("--output", default=None, help="Output JSONL file (auto-generated if not set)")
    parser.add_argument("--batch-size", type=int, default=None, help="Encoding batch size (auto-detect CPU/GPU)")
    args = parser.parse_args()

    if args.output is None:
        base = os.path.splitext(os.path.basename(args.input))[0]
        args.output = f"data/{base}_with_vectors.jsonl"

    print(f"Input:  {args.input}")
    print(f"Output: {args.output}")
    print(f"Model:  {MODEL_NAME}")
    print()

    print("Loading model...")
    model = SentenceTransformer(MODEL_NAME)
    device = str(model.device)
    batch_size = args.batch_size or (BATCH_SIZE_GPU if "cuda" in device else BATCH_SIZE_CPU)
    print(f"Device: {device}, Batch size: {batch_size}")

    already_done = count_existing(args.output)
    if already_done > 0:
        print(f"Resuming from record {already_done:,} (checkpoint found)")

    print("Counting input records...")
    total = count_lines(args.input)
    print(f"Total records: {total:,}, Skipping: {already_done:,}, To process: {total - already_done:,}")
    print()

    texts_batch = []
    records_batch = []
    processed = 0
    skipped = 0
    start_time = time.time()

    out_file = open(args.output, "a", encoding="utf-8")

    try:
        pbar = tqdm(total=total, initial=already_done, desc="Embedding", unit="doc")

        for record in read_records(args.input):
            skipped += 1
            if skipped <= already_done:
                continue

            title = record.get("title", "")
            abstract = record.get("abstract", "")
            # Truncate abstract to fit model's max_seq_length (256 tokens)
            # Title ~15 tokens + [SEP] ~1 token → ~240 tokens left for abstract
            # 1 token ≈ 4 chars → 240 × 4 = 960 chars
            MAX_ABSTRACT_CHARS = 960
            if len(abstract) > MAX_ABSTRACT_CHARS:
                cut = abstract[:MAX_ABSTRACT_CHARS]
                last_period = cut.rfind(". ")
                if last_period > MAX_ABSTRACT_CHARS * 0.6:
                    abstract = cut[:last_period + 1]
                else:
                    abstract = cut
            text = f"{title} [SEP] {abstract}"

            texts_batch.append(text)
            records_batch.append(record)

            if len(texts_batch) >= batch_size:
                embeddings = model.encode(texts_batch, show_progress_bar=False, normalize_embeddings=True)
                for rec, emb in zip(records_batch, embeddings):
                    rec["embedding"] = emb.tolist()
                    out_file.write(json.dumps(rec, ensure_ascii=False) + "\n")

                processed += len(texts_batch)
                pbar.update(len(texts_batch))
                texts_batch.clear()
                records_batch.clear()

                if processed % CHECKPOINT_INTERVAL == 0:
                    out_file.flush()

        if texts_batch:
            embeddings = model.encode(texts_batch, show_progress_bar=False, normalize_embeddings=True)
            for rec, emb in zip(records_batch, embeddings):
                rec["embedding"] = emb.tolist()
                out_file.write(json.dumps(rec, ensure_ascii=False) + "\n")
            processed += len(texts_batch)
            pbar.update(len(texts_batch))

        pbar.close()

    finally:
        out_file.flush()
        out_file.close()

    elapsed = time.time() - start_time
    speed = processed / elapsed if elapsed > 0 else 0
    print(f"\nDone! Processed {processed:,} records in {elapsed:.1f}s ({speed:.0f} docs/sec)")
    print(f"Output: {args.output}")

    final_count = count_existing(args.output)
    print(f"Total records in output: {final_count:,}")


if __name__ == "__main__":
    main()

