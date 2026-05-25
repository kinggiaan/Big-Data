"""
Shared configuration for all search, evaluation, and benchmark modules.
Centralized here to avoid parameter inconsistencies across scripts.
"""

# === Search Parameters ===
TITLE_BOOST = 2
QUERY_TYPE = "best_fields"
NUM_CANDIDATES = 100
RRF_K = 60
RRF_FETCH_SIZE = 30
RESULT_SIZE = 10

# === Model ===
MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

# === Index Names ===
INDEX_V1 = "arxiv_papers"
INDEX_V2 = "arxiv_papers_v2"

# === Dual-Index Architecture ===
# arxiv_text: metadata only (BM25 search) — no embedding field
# arxiv_vectors: alias → arxiv_bench (kNN search) — id + embedding
INDEX_TEXT = "arxiv_text"
INDEX_VECTORS = "arxiv_vectors"

# === Elasticsearch ===
ES_URL = "http://localhost:9200"
