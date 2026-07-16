import json
import os
import statistics

def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    bench = load_json("data/benchmark_results.json")
    eval_100k = load_json("data/evaluation_results_100k.json")
    eval_full = load_json("data/evaluation_results_full.json")

    print("=== LATENCY AND STORAGE BENCHMARK DATA ===")
    if bench and "indices" in bench:
        for idx in bench["indices"]:
            label = idx["label"]
            size = idx["index_info"]["size_mb"]
            docs = idx["index_info"]["doc_count"]
            print(f"Scale: {label} ({docs:,} docs), Size: {size:.1f} MB")
            print(f"  BM25:       P50={idx['bm25']['p50_ms']}ms, P95={idx['bm25']['p95_ms']}ms")
            print(f"  kNN:        P50={idx['knn']['p50_ms']}ms, P95={idx['knn']['p95_ms']}ms")
            print(f"  Hybrid RRF: P50={idx['hybrid_rrf']['p50_ms']}ms, P95={idx['hybrid_rrf']['p95_ms']}ms")
    else:
        print("benchmark_results.json not found or invalid format")

    print("\n=== SEARCH QUALITY METRICS BY SCALE AND GROUP ===")
    
    for label, eval_data in [("100k", eval_100k), ("1.2M", eval_full)]:
        if not eval_data:
            print(f"Evaluation data for {label} not found.")
            continue
            
        print(f"\nScale: {label} (Index: {eval_data.get('index')})")
        per_query = eval_data.get("per_query", [])
        
        # Group metrics
        groups = {}
        for q in per_query:
            g = q["group"]
            if g not in groups:
                groups[g] = {"ndcg": {"bm25": [], "knn": [], "hybrid": []},
                             "mrr": {"bm25": [], "knn": [], "hybrid": []}}
            
            # Extract scores
            ndcgs = q.get("ndcg@10", {})
            mrrs = q.get("mrr", {})
            
            for method in ["bm25", "knn", "hybrid"]:
                if ndcgs.get(method) is not None:
                    groups[g]["ndcg"][method].append(ndcgs[method])
                if mrrs.get(method) is not None:
                    groups[g]["mrr"][method].append(mrrs[method])
        
        # Calculate and print averages
        print(f"  {'Group':<12} | {'Metric':<6} | {'BM25':<6} | {'kNN':<6} | {'Hybrid':<6}")
        print(f"  {'-'*12}-+-{'-'*6}-+-{'-'*6}-+-{'-'*6}-+-{'-'*6}")
        for g in sorted(groups.keys()):
            for metric in ["ndcg", "mrr"]:
                b_avg = statistics.mean(groups[g][metric]["bm25"]) if groups[g][metric]["bm25"] else 0.0
                k_avg = statistics.mean(groups[g][metric]["knn"]) if groups[g][metric]["knn"] else 0.0
                h_avg = statistics.mean(groups[g][metric]["hybrid"]) if groups[g][metric]["hybrid"] else 0.0
                print(f"  {g:<12} | {metric:<6} | {b_avg:.4f} | {k_avg:.4f} | {h_avg:.4f}")
                
        # Overall averages
        if "ranking_metrics" in eval_data:
            print(f"  Overall Average:")
            ndcgs = eval_data["ranking_metrics"].get("ndcg@10_avg", {})
            mrrs = eval_data["ranking_metrics"].get("mrr_avg", {})
            print(f"    NDCG@10: BM25={ndcgs.get('bm25'):.4f}, kNN={ndcgs.get('knn'):.4f}, Hybrid={ndcgs.get('hybrid'):.4f}")
            print(f"    MRR:     BM25={mrrs.get('bm25'):.4f}, kNN={mrrs.get('knn'):.4f}, Hybrid={mrrs.get('hybrid'):.4f}")

if __name__ == "__main__":
    main()
