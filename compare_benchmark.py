"""Compare Old Single-Index vs New Dual-Index performance."""
import sys
import time
import statistics
sys.path.insert(0, ".")

from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from src.config import ES_URL, MODEL_NAME

es = Elasticsearch(ES_URL, request_timeout=60)
model = SentenceTransformer(MODEL_NAME)

QUERIES = [
    "deep learning for image classification",
    "natural language processing transformers",
    "reinforcement learning robotics",
    "graph neural networks",
    "federated learning privacy",
    "generative adversarial network",
    "object detection real-time",
    "quantum computing algorithms",
    "recommendation system collaborative filtering",
    "speech recognition end-to-end"
]

def measure_bm25(index):
    lats = []
    for q in QUERIES:
        t0 = time.perf_counter()
        es.search(index=index, query={"multi_match": {"query": q, "fields": ["title^2", "abstract"]}}, size=10)
        lats.append((time.perf_counter() - t0) * 1000)
    return round(statistics.mean(lats), 1)

def measure_hybrid(text_idx, vec_idx):
    lats = []
    for q in QUERIES:
        vec = model.encode(q, normalize_embeddings=True).tolist()
        t0 = time.perf_counter()
        # Single index uses same index for both
        es.search(index=text_idx, query={"multi_match": {"query": q, "fields": ["title^2", "abstract"]}}, size=20)
        es.search(index=vec_idx, knn={"field": "embedding", "query_vector": vec, "k": 20, "num_candidates": 100}, size=20)
        lats.append((time.perf_counter() - t0) * 1000)
    return round(statistics.mean(lats), 1)

print("\n--- WARM UP ---")
measure_bm25("arxiv_bench")
measure_bm25("arxiv_text")
measure_hybrid("arxiv_bench", "arxiv_bench")
measure_hybrid("arxiv_text", "arxiv_bench") # arxiv_bench has the vectors

print("\n=== BM25 BENCHMARK ===")
old_bm25 = measure_bm25("arxiv_bench")
new_bm25 = measure_bm25("arxiv_text")
print(f"OLD (Single 10.4GB Index): {old_bm25} ms")
print(f"NEW (Dual 1.5GB Index)   : {new_bm25} ms")
print(f"-> Speedup: {round((old_bm25 - new_bm25) / old_bm25 * 100, 1)}%")

print("\n=== HYBRID BENCHMARK ===")
old_hyb = measure_hybrid("arxiv_bench", "arxiv_bench")
new_hyb = measure_hybrid("arxiv_text", "arxiv_bench")
print(f"OLD (Single 10.4GB Index): {old_hyb} ms")
print(f"NEW (Dual-Index Arch)    : {new_hyb} ms")
print(f"-> Speedup: {round((old_hyb - new_hyb) / old_hyb * 100, 1)}%")
