"""
Streamlit UI for Hybrid Academic Paper Search.
Supports BM25, kNN (Vector), and Hybrid (RRF) search modes.

Run: .\venv\Scripts\streamlit.exe run src/app.py
"""
import streamlit as st
import time
import plotly.express as px
import pandas as pd
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer


@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


@st.cache_resource
def get_es():
    return Elasticsearch("http://localhost:9200", request_timeout=30)


INDEX = "arxiv_papers_v2"
RRF_K = 60
FETCH_SIZE = 30


def bm25_search(es, query, size, year_range=None, cat_filter=None):
    word_count = len(query.strip().split())
    msm = "100%" if word_count <= 2 else "75%"
    must = [{"multi_match": {
        "query": query,
        "fields": ["title^3", "abstract"],
        "type": "cross_fields",
        "minimum_should_match": msm,
    }}]
    filters = _build_filters(year_range, cat_filter)
    body_query = {"bool": {"must": must, "filter": filters}} if filters else {"bool": {"must": must}}

    resp = es.search(
        index=INDEX, query=body_query, size=size,
        _source=["title", "abstract", "authors", "year", "categories"],
        highlight={"fields": {"title": {}, "abstract": {"fragment_size": 200}}}
    )
    return resp


def knn_search(es, model, query, size, year_filter=None, cat_filter=None):
    vec = model.encode(query, normalize_embeddings=True).tolist()
    filters = _build_filters(year_filter, cat_filter)
    num_candidates = 300 if filters else 100
    knn_body = {"field": "embedding", "query_vector": vec, "k": size, "num_candidates": num_candidates}
    if filters:
        knn_body["filter"] = {"bool": {"filter": filters}}
    resp = es.search(
        index=INDEX,
        knn=knn_body,
        size=size,
        _source=["title", "abstract", "authors", "year", "categories"],
    )
    return resp


def hybrid_search(es, model, query, size, year_range=None, cat_filter=None):
    word_count = len(query.strip().split())
    msm = "100%" if word_count <= 2 else "75%"
    must = [{"multi_match": {
        "query": query,
        "fields": ["title^3", "abstract"],
        "type": "cross_fields",
        "minimum_should_match": msm,
    }}]
    filters = _build_filters(year_range, cat_filter)
    body_query = {"bool": {"must": must, "filter": filters}} if filters else {"bool": {"must": must}}

    bm25_resp = es.search(
        index=INDEX, query=body_query, size=FETCH_SIZE,
        _source=["title", "abstract", "authors", "year", "categories"],
        highlight={"fields": {"title": {}, "abstract": {"fragment_size": 200}}}
    )

    vec = model.encode(query, normalize_embeddings=True).tolist()
    num_candidates = 300 if filters else 100
    knn_body = {"field": "embedding", "query_vector": vec, "k": FETCH_SIZE, "num_candidates": num_candidates}
    if filters:
        knn_body["filter"] = {"bool": {"filter": filters}}
    knn_resp = es.search(
        index=INDEX,
        knn=knn_body,
        size=FETCH_SIZE,
        _source=["title", "abstract", "authors", "year", "categories"],
    )

    scores = {}
    docs = {}
    highlights = {}

    for rank, hit in enumerate(bm25_resp["hits"]["hits"], 1):
        did = hit["_id"]
        scores[did] = scores.get(did, 0) + 1.0 / (RRF_K + rank)
        docs[did] = hit["_source"]
        if "highlight" in hit:
            highlights[did] = hit["highlight"]

    for rank, hit in enumerate(knn_resp["hits"]["hits"], 1):
        did = hit["_id"]
        scores[did] = scores.get(did, 0) + 1.0 / (RRF_K + rank)
        if did not in docs:
            docs[did] = hit["_source"]

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:size]

    fake_hits = []
    for did, rrf_score in ranked:
        fake_hit = {
            "_id": did,
            "_score": rrf_score,
            "_source": docs[did],
        }
        if did in highlights:
            fake_hit["highlight"] = highlights[did]
        fake_hits.append(fake_hit)

    return {"hits": {"hits": fake_hits, "total": {"value": len(scores)}}}


def _build_filters(year_range, cat_filter):
    filters = []
    if year_range:
        y_min, y_max = year_range
        filters.append({"range": {"year": {"gte": str(y_min), "lte": str(y_max)}}})
    if cat_filter and cat_filter != "All":
        if isinstance(cat_filter, list):
            filters.append({"terms": {"categories": cat_filter}})
        else:
            filters.append({"term": {"categories": cat_filter}})
    return filters


@st.cache_data(ttl=300)
def get_available_categories(_es):
    r = _es.search(
        index=INDEX, size=0,
        aggs={"cats": {"terms": {"field": "categories", "size": 80}}}
    )
    return [b["key"] for b in r["aggregations"]["cats"]["buckets"]]


@st.cache_data(ttl=300)
def get_year_range(_es):
    r = _es.search(
        index=INDEX, size=0,
        aggs={"years": {"terms": {"field": "year", "size": 100, "order": {"_key": "asc"}}}}
    )
    years = [int(b["key"]) for b in r["aggregations"]["years"]["buckets"] if b["key"].isdigit()]
    if not years:
        return 2007, 2026
    return min(years), max(years)


def main():
    st.set_page_config(page_title="Academic Paper Search", page_icon="🔍", layout="wide")

    st.title("Academic Paper Search Engine")

    es = get_es()
    model = load_model()

    if not es.ping():
        st.error("Cannot connect to Elasticsearch. Make sure Docker is running.")
        return

    try:
        doc_count = es.count(index=INDEX)["count"]
        st.caption(f"Hybrid search over {doc_count:,} arXiv CS papers — BM25 + kNN + RRF")
    except Exception:
        st.caption("Hybrid search over arXiv CS papers — BM25 + kNN + RRF")

    # Sidebar
    with st.sidebar:
        st.header("Settings")
        mode = st.radio("Search Mode", ["Hybrid (RRF)", "BM25 (Keyword)", "kNN (Vector)"], index=0)
        num_results = st.slider("Results", 5, 20, 10)

        st.markdown("---")
        st.header("Filters")

        y_min, y_max = get_year_range(es)
        use_year = st.checkbox("Filter by year range", value=False)
        if use_year:
            year_range = st.slider("Year range", y_min, y_max, (y_min, y_max))
        else:
            year_range = None

        # Dataset: data_prep_full.py chỉ chọn paper có chứa "cs." trong `categories`.
        # Nhưng một paper CS vẫn có thể mang thêm các nhãn khác (physics/math/...) dưới dạng tag phụ.
        categories = get_available_categories(es)
        cs_cats = sorted([c for c in categories if c.startswith("cs.")])
        other_cats = sorted([c for c in categories if not c.startswith("cs.")])
        all_cats_sorted = cs_cats + other_cats

        st.caption("Chọn category để lọc theo nhãn trong field `categories` của mỗi paper (CS papers có thể có thêm tag phụ khác `cs.*`).")
        cat_filter = st.multiselect(
            "Categories",
            options=all_cats_sorted,
            default=[],
            placeholder="All categories",
        )
        if not cat_filter:
            cat_filter = "All"

        st.markdown("---")
        st.header("Index Info")
        try:
            count = es.count(index=INDEX)["count"]
            stats = es.indices.stats(index=INDEX)
            size_mb = stats["indices"][INDEX]["total"]["store"]["size_in_bytes"] / (1024 * 1024)
            st.metric("Documents", f"{count:,}")
            st.metric("Index Size", f"{size_mb:.0f} MB")
            st.metric("Search Mode", mode.split(" ")[0])
        except Exception:
            st.warning("Could not fetch index info")

    # Search
    query = st.text_input("Enter your search query", placeholder="e.g. efficient attention mechanism for long sequences")

    if query:
        start = time.perf_counter()

        try:
            if mode == "BM25 (Keyword)":
                response = bm25_search(es, query, num_results, year_range, cat_filter)
            elif mode == "kNN (Vector)":
                response = knn_search(es, model, query, num_results, year_filter=year_range, cat_filter=cat_filter)
            else:
                response = hybrid_search(es, model, query, num_results, year_range, cat_filter)

            latency = (time.perf_counter() - start) * 1000
            hits = response["hits"]["hits"]
            total = response["hits"]["total"]["value"] if isinstance(response["hits"]["total"], dict) else response["hits"]["total"]

            col1, col2, col3 = st.columns(3)
            col1.metric("Results", f"{len(hits)}")
            col2.metric("Latency", f"{latency:.0f} ms")
            col3.metric("Mode", mode.split(" ")[0])

            st.markdown("---")

            if not hits:
                st.info("No results found. Try a different query or search mode.")
            else:
                for i, hit in enumerate(hits, 1):
                    src = hit["_source"]
                    score = hit.get("_score") or 0
                    title = src.get("title") or "Untitled"
                    abstract = src.get("abstract") or ""
                    authors = src.get("authors") or "Unknown"
                    year = src.get("year") or "N/A"
                    cats = src.get("categories") or []
                    if isinstance(cats, list):
                        cats = ", ".join(cats)
                    doc_id = hit.get("_id", "")

                    hl = hit.get("highlight") or {}
                    hl_title = hl.get("title", [title])[0] if hl else title
                    hl_abstract = hl.get("abstract", [abstract[:300]])[0] if hl else abstract[:300]
                    ellipsis = "..." if len(abstract) > 300 and not hl.get("abstract") else ""

                    with st.container():
                        st.markdown(f"### {i}. {hl_title}", unsafe_allow_html=True)
                        c1, c2, c3 = st.columns([2, 1, 1])
                        c1.caption(f"Authors: {authors[:120]}{'...' if len(authors) > 120 else ''}")
                        c2.caption(f"Year: {year}")
                        c3.caption(f"Score: {score:.4f}")
                        st.markdown(f"*{hl_abstract}{ellipsis}*", unsafe_allow_html=True)
                        st.caption(f"Categories: {cats} | ID: {doc_id}")
                        st.markdown("---")

                # Category distribution
                if hits:
                    all_cats = []
                    for h in hits:
                        c = h["_source"].get("categories", [])
                        if isinstance(c, str):
                            c = c.split()
                        all_cats.extend(c)
                    if all_cats:
                        cat_df = pd.DataFrame({"category": all_cats})
                        cat_counts = cat_df["category"].value_counts().head(10).reset_index()
                        cat_counts.columns = ["Category", "Count"]
                        fig = px.bar(cat_counts, x="Category", y="Count", title="Top Categories in Results")
                        st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Search error: {e}")


if __name__ == "__main__":
    main()

