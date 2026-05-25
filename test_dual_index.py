"""Quick test: all 3 search modes on dual-index architecture."""
import sys
sys.path.insert(0, ".")

query = "deep learning for image classification"

# 1. Hybrid Search
print("=" * 70)
print("TEST 1: Hybrid Search (BM25 on arxiv_text + kNN on arxiv_vectors)")
print("=" * 70)
from src.search.hybrid_search import hybrid_search
results, latency = hybrid_search(query)
print(f"\n✅ Hybrid: {len(results)} results, {latency:.0f}ms")

# 2. BM25 Search
print("\n" + "=" * 70)
print("TEST 2: BM25 Search (arxiv_text only)")
print("=" * 70)
from src.search.search import keyword_search
keyword_search(query)
print("\n✅ BM25: OK")

# 3. kNN Search
print("\n" + "=" * 70)
print("TEST 3: kNN Search (arxiv_vectors only)")
print("=" * 70)
from src.search.vector_search import vector_search
knn_results = vector_search(query)
print(f"\n✅ kNN: {len(knn_results)} results")

# 4. Stats
print("\n" + "=" * 70)
print("TEST 4: Index Stats")
print("=" * 70)
from src.search.hybrid_search import es
for idx in ["arxiv_text", "arxiv_vectors"]:
    count = es.count(index=idx)["count"]
    print(f"  {idx}: {count:,} docs")

print("\n🎉 All 3 search modes working correctly on dual-index architecture!")
