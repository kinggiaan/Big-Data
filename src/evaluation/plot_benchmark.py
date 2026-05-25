"""
Generate benchmark charts from benchmark_results.json.
Outputs PNG files for the Final Report.

Usage: python src/evaluation/plot_benchmark.py
"""
import json
import os
import matplotlib.pyplot as plt
import numpy as np

INPUT_FILE = "data/benchmark_results.json"
OUTPUT_DIR = "data/charts"


def load_results(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def plot_latency_comparison(results):
    """Bar chart: BM25 vs kNN vs Hybrid latency (single scale)."""
    if "indices" in results:
        # Multi-scale format — use the last (largest) index
        data = results["indices"][-1]
    else:
        data = results

    methods = ["BM25", "kNN", "Hybrid"]
    p50 = [data["bm25"]["p50_ms"], data["knn"]["p50_ms"], data["hybrid_rrf"]["p50_ms"]]
    p95 = [data["bm25"]["p95_ms"], data["knn"]["p95_ms"], data["hybrid_rrf"]["p95_ms"]]

    x = np.arange(len(methods))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    bars1 = ax.bar(x - width/2, p50, width, label="P50", color="#4CAF50")
    bars2 = ax.bar(x + width/2, p95, width, label="P95", color="#FF9800")

    ax.set_xlabel("Search Method")
    ax.set_ylabel("Latency (ms)")
    ax.set_title("Query Latency Comparison (P50 vs P95)")
    ax.set_xticks(x)
    ax.set_xticklabels(methods)
    ax.legend()
    ax.bar_label(bars1, fmt="%.1f")
    ax.bar_label(bars2, fmt="%.1f")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "latency_comparison.png"), dpi=150)
    print("Saved: latency_comparison.png")
    plt.close()


def plot_scaling(results):
    """Line chart: latency vs document count (multi-scale)."""
    if "indices" not in results:
        print("No multi-scale data found, skipping scaling chart")
        return

    indices = results["indices"]
    labels = [idx["label"] for idx in indices]
    doc_counts = [idx["index_info"]["doc_count"] for idx in indices]

    bm25_p50 = [idx["bm25"]["p50_ms"] for idx in indices]
    knn_p50 = [idx["knn"]["p50_ms"] for idx in indices]
    hybrid_p50 = [idx["hybrid_rrf"]["p50_ms"] for idx in indices]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(doc_counts, bm25_p50, 'o-', label="BM25", linewidth=2, markersize=8)
    ax.plot(doc_counts, knn_p50, 's-', label="kNN", linewidth=2, markersize=8)
    ax.plot(doc_counts, hybrid_p50, '^-', label="Hybrid (RRF)", linewidth=2, markersize=8)

    ax.set_xlabel("Number of Documents")
    ax.set_ylabel("P50 Latency (ms)")
    ax.set_title("Search Latency Scaling")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Format x-axis
    ax.set_xticks(doc_counts)
    ax.set_xticklabels(labels)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "latency_scaling.png"), dpi=150)
    print("Saved: latency_scaling.png")
    plt.close()


def plot_index_size(results):
    """Bar chart: index size vs document count."""
    if "indices" not in results:
        print("No multi-scale data found, skipping index size chart")
        return

    indices = results["indices"]
    labels = [idx["label"] for idx in indices]
    sizes = [idx["index_info"]["size_mb"] for idx in indices]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, sizes, color=["#2196F3", "#4CAF50", "#FF9800", "#F44336"][:len(labels)])
    ax.set_xlabel("Dataset Scale")
    ax.set_ylabel("Index Size (MB)")
    ax.set_title("Elasticsearch Index Size by Scale")
    ax.bar_label(bars, fmt="%.0f MB")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "index_size.png"), dpi=150)
    print("Saved: index_size.png")
    plt.close()


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: {INPUT_FILE} not found. Run benchmark first.")
        return

    results = load_results(INPUT_FILE)
    print(f"Loaded benchmark results from {INPUT_FILE}")

    plot_latency_comparison(results)
    plot_scaling(results)
    plot_index_size(results)

    print(f"\nAll charts saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
