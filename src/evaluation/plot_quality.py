import json
import os
import matplotlib.pyplot as plt
import numpy as np

def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    eval_100k = load_json("data/evaluation_results_100k.json")
    eval_full = load_json("data/evaluation_results_full.json")

    if not eval_100k or not eval_full:
        print("ERROR: Evaluation JSONs not found.")
        return

    # Extract overall NDCG and MRR
    # 100k
    ndcg_100k = [
        eval_100k["ranking_metrics"]["ndcg@10_avg"]["bm25"],
        eval_100k["ranking_metrics"]["ndcg@10_avg"]["knn"],
        eval_100k["ranking_metrics"]["ndcg@10_avg"]["hybrid"]
    ]
    mrr_100k = [
        eval_100k["ranking_metrics"]["mrr_avg"]["bm25"],
        eval_100k["ranking_metrics"]["mrr_avg"]["knn"],
        eval_100k["ranking_metrics"]["mrr_avg"]["hybrid"]
    ]

    # 1.2M
    ndcg_full = [
        eval_full["ranking_metrics"]["ndcg@10_avg"]["bm25"],
        eval_full["ranking_metrics"]["ndcg@10_avg"]["knn"],
        eval_full["ranking_metrics"]["ndcg@10_avg"]["hybrid"]
    ]
    mrr_full = [
        eval_full["ranking_metrics"]["mrr_avg"]["bm25"],
        eval_full["ranking_metrics"]["mrr_avg"]["knn"],
        eval_full["ranking_metrics"]["mrr_avg"]["hybrid"]
    ]

    methods = ["BM25", "kNN (Dense)", "Hybrid (RRF)"]
    x = np.arange(len(methods))
    width = 0.35

    # 1. Plot NDCG
    fig, ax = plt.subplots(figsize=(8, 5))
    rects1 = ax.bar(x - width/2, ndcg_100k, width, label="100k Scale", color="#4EA8DE")
    rects2 = ax.bar(x + width/2, ndcg_full, width, label="1.2M Scale", color="#5E60CE")

    ax.set_ylabel("NDCG@10 Score")
    ax.set_title("Search Quality (NDCG@10) Comparison by Scale")
    ax.set_xticks(x)
    ax.set_xticklabels(methods)
    ax.set_ylim(0, 1.15)
    ax.legend(loc="upper left")
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    ax.bar_label(rects1, fmt="%.3f", padding=3)
    ax.bar_label(rects2, fmt="%.3f", padding=3)

    plt.tight_layout()
    os.makedirs("data/charts", exist_ok=True)
    os.makedirs("Report_Final/images", exist_ok=True)
    
    plt.savefig("data/charts/ndcg_comparison.png", dpi=150)
    plt.savefig("Report_Final/images/ndcg_comparison.png", dpi=150)
    print("Saved: ndcg_comparison.png")
    plt.close()

    # 2. Plot MRR
    fig, ax = plt.subplots(figsize=(8, 5))
    rects1 = ax.bar(x - width/2, mrr_100k, width, label="100k Scale", color="#FF9F1C")
    rects2 = ax.bar(x + width/2, mrr_full, width, label="1.2M Scale", color="#2EC4B6")

    ax.set_ylabel("MRR Score")
    ax.set_title("Search Quality (MRR) Comparison by Scale")
    ax.set_xticks(x)
    ax.set_xticklabels(methods)
    ax.set_ylim(0, 1.15)
    ax.legend(loc="upper left")
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    ax.bar_label(rects1, fmt="%.3f", padding=3)
    ax.bar_label(rects2, fmt="%.3f", padding=3)

    plt.tight_layout()
    plt.savefig("data/charts/mrr_comparison.png", dpi=150)
    plt.savefig("Report_Final/images/mrr_comparison.png", dpi=150)
    print("Saved: mrr_comparison.png")
    plt.close()

if __name__ == "__main__":
    main()
