"""
FastAPI backend for Academic Paper Search — Dual-Index Architecture.

Indices:
  - arxiv_text:    metadata + BM25 search (no embeddings)
  - arxiv_vectors: kNN vector search (id + 384-dim embedding)

Endpoints:
  GET  /api/search       — BM25, kNN, or Hybrid (RRF) search
  GET  /api/categories   — Top categories aggregation
  GET  /api/years        — Year range aggregation
  GET  /api/stats        — Document count per index
  POST /api/ingest       — Push new paper(s) into both indices
"""
import time
import sys
import os
from typing import List, Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from src.config import (
    ES_URL, INDEX_TEXT, INDEX_VECTORS,
    MODEL_NAME, RRF_K, RRF_FETCH_SIZE, RESULT_SIZE, NUM_CANDIDATES,
)

# ── Shared clients ──────────────────────────────────────────────────────────
es = Elasticsearch(ES_URL, request_timeout=30)
model = SentenceTransformer(MODEL_NAME)

app = FastAPI(title="Academic Paper Search API — Dual Index")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic Models ─────────────────────────────────────────────────────────
class PaperInput(BaseModel):
    id: str
    title: str
    abstract: str
    authors: str = ""
    year: str = ""
    categories: str = ""  # space-separated, e.g. "cs.AI cs.CL"


class IngestResponse(BaseModel):
    status: str
    ingested: int
    ids: List[str]


# ── Helpers ──────────────────────────────────────────────────────────────────
def format_hits(es_hits, score_field="_score"):
    results = []
    for hit in es_hits:
        src = hit.get("_source") or {}
        results.append({
            "id": hit["_id"],
            "title": src.get("title", "N/A"),
            "abstract": src.get("abstract", ""),
            "authors": src.get("authors", "Unknown"),
            "year": src.get("year", "N/A"),
            "categories": src.get("categories", []),
            "score": hit.get(score_field, 0),
        })
    return results


def _enrich_knn_hits(knn_hits):
    """
    kNN results come from arxiv_vectors (id + embedding only).
    Fetch full metadata from arxiv_text via mget.
    """
    if not knn_hits:
        return knn_hits

    ids = [h["_id"] for h in knn_hits]
    meta_resp = es.mget(index=INDEX_TEXT, ids=ids, _source=["title", "abstract", "authors", "year", "categories"])

    meta_map = {}
    for doc in meta_resp.get("docs", []):
        if doc.get("found"):
            meta_map[doc["_id"]] = doc["_source"]

    for hit in knn_hits:
        meta = meta_map.get(hit["_id"], {})
        hit.setdefault("_source", {}).update(meta)

    return knn_hits


def rrf_merge(bm25_hits, knn_hits, k=RRF_K, final_size=RESULT_SIZE):
    """Reciprocal Rank Fusion: merge two ranked lists."""
    scores = {}
    docs = {}

    for rank, hit in enumerate(bm25_hits, start=1):
        doc_id = hit["_id"]
        scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank)
        docs[doc_id] = hit

    for rank, hit in enumerate(knn_hits, start=1):
        doc_id = hit["_id"]
        scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank)
        if doc_id not in docs:
            docs[doc_id] = hit

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    results = []
    for doc_id, rrf_score in ranked[:final_size]:
        hit = docs[doc_id]
        hit["_rrf_score"] = rrf_score
        results.append(hit)
    return results


# ── Search Endpoint ──────────────────────────────────────────────────────────
@app.get("/api/search")
def search(
    q: str = Query(..., min_length=1),
    mode: str = "hybrid",
    size: int = RESULT_SIZE,
    yearMin: int = None,
    yearMax: int = None,
    categories: str = None,
):
    start = time.perf_counter()

    # Build filter block
    filters = []
    if yearMin or yearMax:
        range_filter = {}
        if yearMin:
            range_filter["gte"] = str(yearMin)
        if yearMax:
            range_filter["lte"] = str(yearMax)
        filters.append({"range": {"year": range_filter}})

    if categories:
        cats = categories.split(",")
        filters.append({"terms": {"categories": cats}})

    base_query = {
        "bool": {
            "must": [{"multi_match": {"query": q, "fields": ["title^2", "abstract"]}}]
        }
    }
    if filters:
        base_query["bool"]["filter"] = filters

    fetch_size = size * 2 if mode == "hybrid" else size
    _source_fields = ["title", "year", "authors", "abstract", "categories"]

    try:
        if mode == "bm25":
            # ── BM25 on arxiv_text ──
            resp = es.search(index=INDEX_TEXT, query=base_query, size=fetch_size, _source=_source_fields)
            hits = format_hits(resp["hits"]["hits"], "_score")
            total = resp["hits"]["total"]["value"]

        elif mode == "knn":
            # ── kNN on arxiv_vectors ──
            query_vector = model.encode(q, normalize_embeddings=True).tolist()
            knn_query = {
                "field": "embedding",
                "query_vector": query_vector,
                "k": fetch_size,
                "num_candidates": NUM_CANDIDATES,
            }
            if filters:
                knn_query["filter"] = filters

            resp = es.search(index=INDEX_VECTORS, knn=knn_query, size=fetch_size, _source=False)
            knn_hits = _enrich_knn_hits(resp["hits"]["hits"])
            hits = format_hits(knn_hits, "_score")
            total = len(hits)

        else:  # hybrid
            # ── BM25 on arxiv_text ──
            resp_bm25 = es.search(index=INDEX_TEXT, query=base_query, size=fetch_size, _source=_source_fields)
            bm25_hits = resp_bm25["hits"]["hits"]

            # ── kNN on arxiv_vectors ──
            query_vector = model.encode(q, normalize_embeddings=True).tolist()
            knn_query = {
                "field": "embedding",
                "query_vector": query_vector,
                "k": fetch_size,
                "num_candidates": NUM_CANDIDATES,
            }
            if filters:
                knn_query["filter"] = filters
            resp_knn = es.search(index=INDEX_VECTORS, knn=knn_query, size=fetch_size, _source=False)
            knn_hits = _enrich_knn_hits(resp_knn["hits"]["hits"])

            # ── RRF Merge ──
            merged = rrf_merge(bm25_hits, knn_hits, k=RRF_K, final_size=size)
            hits = format_hits(merged, "_rrf_score")
            total = resp_bm25["hits"]["total"]["value"]

        latency = (time.perf_counter() - start) * 1000
        return {"total": total, "latency_ms": int(latency), "mode": mode, "hits": hits[:size]}

    except Exception as e:
        return {"error": str(e)}


# ── Aggregation Endpoints ────────────────────────────────────────────────────
@app.get("/api/categories")
def get_categories():
    try:
        resp = es.search(
            index=INDEX_TEXT, size=0,
            aggs={"top_categories": {"terms": {"field": "categories", "size": 30}}},
        )
        buckets = resp["aggregations"]["top_categories"]["buckets"]
        return {"categories": [{"name": b["key"], "count": b["doc_count"]} for b in buckets]}
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/years")
def get_years():
    try:
        resp = es.search(
            index=INDEX_TEXT, size=0,
            aggs={"min_year": {"min": {"field": "year"}}, "max_year": {"max": {"field": "year"}}},
        )
        aggs = resp["aggregations"]
        return {
            "min": int(aggs["min_year"]["value"]) if aggs["min_year"]["value"] else 1990,
            "max": int(aggs["max_year"]["value"]) if aggs["max_year"]["value"] else 2026,
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/stats")
def get_stats():
    try:
        text_count = es.count(index=INDEX_TEXT)["count"]
        vector_count = es.count(index=INDEX_VECTORS)["count"]
        return {
            "index_text": {"name": INDEX_TEXT, "documents": text_count},
            "index_vectors": {"name": INDEX_VECTORS, "documents": vector_count},
            "total_documents": text_count,
        }
    except Exception as e:
        return {"error": str(e)}


# ── Ingestion Endpoint ───────────────────────────────────────────────────────
@app.post("/api/ingest", response_model=IngestResponse)
def ingest_papers(papers: List[PaperInput]):
    """
    Push one or more new papers into both indices.
    Generates embeddings on-the-fly and upserts into arxiv_text + arxiv_vectors.
    """
    ingested_ids = []

    for paper in papers:
        # Prepare text for embedding (same logic as embed_data.py)
        text = f"{paper.title} [SEP] {paper.abstract[:960]}"
        embedding = model.encode(text, normalize_embeddings=True).tolist()

        categories = paper.categories.split() if paper.categories else []

        # Upsert to arxiv_text (metadata only)
        es.index(index=INDEX_TEXT, id=paper.id, document={
            "title": paper.title,
            "abstract": paper.abstract,
            "authors": paper.authors,
            "year": paper.year,
            "categories": categories,
        })

        # Upsert to arxiv_vectors (embedding only)
        es.index(index=INDEX_VECTORS, id=paper.id, document={
            "embedding": embedding,
        })

        ingested_ids.append(paper.id)

    # Refresh both indices so new docs are searchable immediately
    es.indices.refresh(index=INDEX_TEXT)
    es.indices.refresh(index=INDEX_VECTORS)

    return IngestResponse(status="ok", ingested=len(ingested_ids), ids=ingested_ids)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
