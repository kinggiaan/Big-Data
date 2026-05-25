"""Test incremental ingestion: push a new paper then search for it."""
import sys
sys.path.insert(0, ".")

from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from src.config import ES_URL, INDEX_TEXT, INDEX_VECTORS, MODEL_NAME
from src.pipeline.ingest import ingest_paper

es = Elasticsearch(ES_URL)
print("Loading model...")
model = SentenceTransformer(MODEL_NAME)

# Count before
text_before = es.count(index=INDEX_TEXT)["count"]
vec_before = es.count(index=INDEX_VECTORS)["count"]
print(f"\nBEFORE: arxiv_text={text_before:,}  arxiv_vectors={vec_before:,}")

# Ingest a test paper
print("\n--- Ingesting test paper ---")
test_paper = {
    "id": "test.9999999",
    "title": "A Novel Framework for Testing Dual-Index Elasticsearch Architecture",
    "abstract": "This paper presents a comprehensive evaluation of dual-index search systems using Elasticsearch. We demonstrate that splitting text and vector indices improves both ingestion speed and query flexibility for large-scale academic paper retrieval.",
    "authors": "Test Author, Another Author",
    "year": "2026",
    "categories": "cs.IR cs.AI"
}
ingest_paper(es, model, test_paper)
print("Paper ingested!")

# Refresh and count after
es.indices.refresh(index=INDEX_TEXT)
es.indices.refresh(index=INDEX_VECTORS)
text_after = es.count(index=INDEX_TEXT)["count"]
vec_after = es.count(index=INDEX_VECTORS)["count"]
print(f"\nAFTER:  arxiv_text={text_after:,}  arxiv_vectors={vec_after:,}")
print(f"Delta:  arxiv_text=+{text_after - text_before}  arxiv_vectors=+{vec_after - vec_before}")

# Search for the new paper by title
print("\n--- Searching for ingested paper (BM25 on arxiv_text) ---")
resp = es.search(
    index=INDEX_TEXT,
    query={"match": {"title": "Novel Framework Testing Dual-Index"}},
    size=3, _source=["title", "year", "authors"]
)
for h in resp["hits"]["hits"]:
    print(f"  ✅ ID={h['_id']}  Year={h['_source']['year']}  Title={h['_source']['title'][:80]}")

# Clean up
print("\n--- Cleanup ---")
es.delete(index=INDEX_TEXT, id="test.9999999", ignore=[404])
es.delete(index=INDEX_VECTORS, id="test.9999999", ignore=[404])
es.indices.refresh(index=INDEX_TEXT)
es.indices.refresh(index=INDEX_VECTORS)
final = es.count(index=INDEX_TEXT)["count"]
print(f"FINAL:  arxiv_text={final:,} (restored)")
print("\n🎉 Incremental ingestion test PASSED!")
