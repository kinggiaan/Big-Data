"""
Auto-label ground truth using majority voting across search methods.

A document is labeled "relevant" if it appears in >= 2 out of 3 methods
(BM25, kNN, Hybrid). This provides a reasonable proxy for relevance
when manual labeling is not feasible.

Usage:
  python -m src.evaluation.auto_label_ground_truth \
    --ground-truth data/ground_truth.json \
    --output data/ground_truth_labeled.json
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import argparse
import json
import os


def auto_label(gt_path: str, output_path: str, min_methods: int = 2):
    """
    Auto-label ground truth using majority voting.

    A document is labeled relevant if it appears in >= `min_methods`
    out of the 3 search methods (bm25, knn, hybrid).
    """
    with open(gt_path, "r", encoding="utf-8") as f:
        gt = json.load(f)

    queries = gt.get("queries", [])
    total_labeled = 0

    for entry in queries:
        candidates = entry.get("candidates", {})
        bm25_ids = set(candidates.get("bm25", []))
        knn_ids = set(candidates.get("knn", []))
        hybrid_ids = set(candidates.get("hybrid", []))

        # Count how many methods returned each document
        all_ids = bm25_ids | knn_ids | hybrid_ids
        relevant = []

        for doc_id in all_ids:
            count = 0
            if doc_id in bm25_ids:
                count += 1
            if doc_id in knn_ids:
                count += 1
            if doc_id in hybrid_ids:
                count += 1

            if count >= min_methods:
                relevant.append(doc_id)

        entry["relevant_ids"] = relevant
        total_labeled += len(relevant)

    # Preserve metadata
    gt["auto_labeled"] = True
    gt["labeling_method"] = f"majority_voting (>= {min_methods}/3 methods)"

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(gt, f, indent=2, ensure_ascii=False)

    print(f"Auto-labeled {total_labeled} relevant documents across {len(queries)} queries")
    print(f"Average relevant per query: {total_labeled / len(queries):.1f}")
    print(f"Output: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Auto-label ground truth via majority voting")
    parser.add_argument("--ground-truth", default="data/ground_truth.json", help="Input ground truth template")
    parser.add_argument("--output", default="data/ground_truth_labeled.json", help="Output labeled ground truth")
    parser.add_argument("--min-methods", type=int, default=2, help="Min methods a doc must appear in to be relevant")
    args = parser.parse_args()

    auto_label(args.ground_truth, args.output, args.min_methods)


if __name__ == "__main__":
    main()
