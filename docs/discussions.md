# Project Discussions & Insights Log

**Project:** Building a Hybrid Search System for Academic Documents using Elasticsearch
**Course:** CO5135 - Big Data (HK252)
**Last updated:** 25/03/2026

---

## Discussion #1: Tại sao BM25 match quá rộng?

**Ngày:** 25/03/2026
**Context:** User search "hyper search" trả về 4,171 docs không liên quan.

**Root cause:**
- Elasticsearch `multi_match` với `type: best_fields` mặc định dùng **OR logic**
- Query "hyper search" → match bất kỳ doc chứa "hyper" HOẶC "search"
- Hầu hết CS papers đều chứa từ "search" ở đâu đó → 4,171 matches

**Solution:**
- Đổi sang `type: cross_fields` — tìm across cả title + abstract thay vì chọn field tốt nhất
- Thêm `minimum_should_match: 100%` cho query 1-2 từ (phải match TẤT CẢ), `75%` cho query dài hơn
- Tăng title boost từ `^2` lên `^3`

**Result:**
| Query | Trước (OR) | Sau (cross_fields + msm) |
|---|---|---|
| "hyper search" | 4,171 docs | 10 docs |
| "attention mechanism" | 10,000 docs | 170 docs |
| "deep learning medical image" | 9,972 docs | 48 docs |

**Takeaway cho report:**
BM25 cần tuning để phù hợp use case. Default config không tối ưu cho academic search.
Tham số quan trọng: `type`, `minimum_should_match`, field boosting.

---

## Discussion #2: Dataset 100k bị lệch thời gian nghiêm trọng

**Ngày:** 25/03/2026
**Context:** User search "BERT" → 0 results. Search "attention mechanism" → toàn bài về cognitive science, không phải Transformer attention.

**Root cause:**
- Script `data_prep.py` lấy **100k bài ĐẦU TIÊN** trong file gốc (theo thứ tự thời gian)
- Kết quả: 96.7% papers từ 2007-2016, chỉ 3.3% từ 2017+
- Các khái niệm hiện đại (BERT 2018, GPT 2018, Transformer 2017) **gần như không tồn tại** trong dataset

**Year distribution:**
```
2007-2010:  27,473 papers (27.5%)
2011-2013:  46,479 papers (46.5%)  ← peak
2014-2016:  23,753 papers (23.7%)
2017+:       3,295 papers (3.3%)   ← gần như không có
```

**Impact:**
- BM25 cho "BERT" → 0 results (không có bài nào)
- kNN cho "attention mechanism" → trả về bài cognitive science (vì không có Transformer attention trong data)
- User frustration: search engine "không hoạt động" nhưng thực ra là data thiếu

**Solution:**
- Short-term: Chấp nhận limitation, note trong report
- Long-term: Scale lên full 1.16M papers → có đầy đủ 2007-2026
- Alternative: Tạo 100k random sample thay vì 100k đầu tiên (nhưng cần re-embed)

**Takeaway cho report:**
- Data quality & coverage quyết định search quality hơn cả algorithm
- Đây là bài học Big Data: volume matters, nhưng **representativeness** cũng quan trọng
- So sánh 100k (biased) vs 1.16M (full) là một scalability insight hay

---

## Discussion #3: kNN filter bị thiếu — Hybrid trả kết quả sai year

**Ngày:** 25/03/2026
**Context:** User chọn filter Year=2024, search "hyper search" → có kết quả từ 2013.

**Root cause:**
- Elasticsearch kNN query hỗ trợ tham số `filter` nhưng code ban đầu **không truyền filter vào kNN**
- BM25 search có filter → chỉ trả papers 2024
- kNN search KHÔNG có filter → trả papers từ mọi năm
- Hybrid RRF merge cả hai → papers 2013 từ kNN lọt vào kết quả

**Bug location:**
```python
# BEFORE (bug): kNN không nhận filter
def knn_search(es, model, query, size, num_candidates=100):
    ...  # không có year_filter, cat_filter

# Hybrid: phần kNN cũng không filter
knn_body = {"field": "embedding", "query_vector": vec, "k": 30, "num_candidates": 100}
# thiếu: knn_body["filter"] = ...
```

**Fix:**
```python
# AFTER: kNN có filter
def knn_search(es, model, query, size, year_filter=None, cat_filter=None):
    filters = _build_filters(year_filter, cat_filter)
    knn_body = {"field": "embedding", "query_vector": vec, "k": size, "num_candidates": num_candidates}
    if filters:
        knn_body["filter"] = {"bool": {"filter": filters}}
```

**Related fix — num_candidates quá thấp khi có filter:**
- ES kNN tìm `num_candidates` nearest neighbors TRƯỚC, rồi mới apply filter
- Nếu chỉ 5% docs thuộc năm 2024 → 100 candidates × 5% = chỉ ~5 results sau filter
- Solution: tăng `num_candidates` từ 100 → 300 khi có filter active

**Takeaway cho report:**
- Hybrid search cần đảm bảo filter được áp dụng **nhất quán** trên TẤT CẢ sub-queries
- kNN pre-filtering vs post-filtering là trade-off quan trọng trong vector search
- `num_candidates` ảnh hưởng trực tiếp đến recall khi có filter

---

## Discussion #4: Embedding model tổng quát vs domain-specific

**Ngày:** 25/03/2026
**Context:** kNN search cho "attention mechanism" trả về bài cognitive science thay vì Transformer attention.

**Analysis:**
Model `all-MiniLM-L6-v2` được train trên general English text (Wikipedia, web data), không chuyên biệt cho academic CS.

**Cosine similarity tests:**
```
cosine("hyper search", "hyperparameter tuning")     = 0.4953  ← thấp!
cosine("hyper search", "search algorithm optimization") = 0.6268
cosine("methods to detect fake images", "image forgery detection") = 0.7005
cosine("methods to detect fake images", "deepfake detection")      = 0.4052  ← thấp!
cosine("deep learning medical image", "clinical diagnosis with CNN") = 0.5814
```

**Observations:**
- Model hiểu paraphrase tốt ("fake images" ↔ "image forgery") nhưng không hiểu domain abbreviations ("deepfake")
- "attention mechanism" bị hiểu theo nghĩa tâm lý học, không phải Transformer
- Cosine > 0.7 = good match, 0.5-0.7 = weak, < 0.5 = miss

**Takeaway cho report:**
- General-purpose vs domain-specific embedding model là trade-off: dễ dùng vs chính xác
- Có thể fine-tune model trên academic CS corpus để cải thiện (future work)
- Hybrid search giúp bù đắp: khi kNN miss, BM25 có thể catch (và ngược lại)
- Overlap chỉ 1.5/10 giữa BM25 và kNN → chứng minh hai phương pháp bổ sung nhau

---

## Discussion #5: Native RRF bị chặn bởi ES license

**Ngày:** 24/03/2026
**Context:** Elasticsearch `sub_searches` + `rank: { rrf: {} }` trả lỗi 403 license.

**Error:**
```
BadRequestError(403, 'security_exception',
'current license is non-compliant for [Reciprocal Rank Fusion (RRF)]')
```

**Root cause:**
- Native RRF trong ES 8.12 yêu cầu **Platinum/Enterprise license** (trả phí)
- Free/Basic license không hỗ trợ

**Solution — Manual RRF implementation:**
```python
def rrf_merge(bm25_hits, knn_hits, k=60):
    scores = {}
    for rank, hit in enumerate(bm25_hits, start=1):
        scores[hit["_id"]] = scores.get(hit["_id"], 0) + 1.0 / (k + rank)
    for rank, hit in enumerate(knn_hits, start=1):
        scores[hit["_id"]] = scores.get(hit["_id"], 0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

**RRF Formula:** `RRF_score(doc) = Σ 1/(k + rank_i)` where k=60 (constant), rank_i = rank in each result list.

**Takeaway cho report:**
- Biến constraint thành opportunity: tự implement RRF chứng minh hiểu sâu algorithm
- Manual RRF cho phép customize (thay đổi k, weight cho BM25 vs kNN)
- Trade-off: 2 queries thay vì 1 → latency ~2x (~156ms vs ~67ms BM25)
- k=60 là giá trị phổ biến trong literature (Microsoft, Elastic documentation)

---

## Discussion #6: Benchmark 100k — Phân tích kết quả

**Ngày:** 25/03/2026
**Context:** Chạy scalability benchmark trên 100k dataset.

**Key metrics:**
| Metric | v1 (text-only) | v2 (text+vector) | Change |
|---|---|---|---|
| Index size | 105.4 MB | 916.6 MB | **+9x** |
| BM25 P50 | 96.6 ms | 66.0 ms | -32% (better) |
| kNN P50 | N/A | 68.6 ms | — |
| Hybrid P50 | N/A | 156.4 ms | ≈ BM25 + kNN |
| Heap used | 476 MB (23%) | 982 MB (48%) | +2x |

**Why v2 BM25 is faster than v1?**
- v2 has 5 shards (parallel search) vs v1 has 1 shard
- Custom `academic_english` analyzer reduces token count (stemming, stop words removal)
- Fewer unique tokens → smaller inverted index → faster lookup

**Why index is 9x bigger?**
- 384-dim float32 vector per doc = 384 × 4 bytes = 1,536 bytes/doc
- 100k docs × 1,536 bytes ≈ 146 MB just for raw vectors
- Plus HNSW graph index overhead ≈ 650+ MB

**Evaluation (30 queries):**
| Query group | BM25∩kNN overlap | Interpretation |
|---|---|---|
| A_exact (10q) | 1.9/10 | Even for exact terms, kNN finds different relevant papers |
| B_semantic (10q) | 0.8/10 | Almost no overlap → kNN finds what BM25 completely misses |
| C_mixed (10q) | 1.9/10 | Mixed queries also show low overlap |
| **Overall** | **1.5/10** | **Strong evidence that Hybrid adds value** |

**Takeaway cho report:**
- Low overlap (1.5/10) = STRONG justification for Hybrid approach
- Vector storage dominates index size — important Big Data consideration
- Heap doubles with vectors — need to plan for 1.16M scale
- BM25 benefits from sharding — relevant for scalability chapter

---

## Discussion #7: UX — Year range filter + Category dropdown

**Ngày:** 25/03/2026
**Context:** User muốn filter year theo khoảng (2015-2020) thay vì chọn 1 năm, và chọn category từ danh sách có sẵn thay vì tự nhập.

**Thay đổi:**

1. **Year filter:** Đổi từ `st.selectbox("Year", ["All", "2024", "2023", ...])` sang `st.slider("Year range", min, max, (min, max))` với checkbox bật/tắt. ES query dùng `range` thay vì `term`:
```python
# Trước: chỉ match 1 năm
{"term": {"year": "2024"}}
# Sau: match khoảng
{"range": {"year": {"gte": "2015", "lte": "2020"}}}
```

2. **Category filter:** Đổi từ `st.text_input()` sang `st.multiselect()` với options lấy từ ES aggregation. User chọn nhiều category cùng lúc, dùng `terms` query (OR logic):
```python
# Trước: chỉ match 1 category, user phải biết tên chính xác
{"term": {"categories": "cs.AI"}}
# Sau: match nhiều categories, chọn từ dropdown
{"terms": {"categories": ["cs.AI", "cs.CL", "cs.LG"]}}
```

3. **Categories sorted:** CS categories hiển thị trước (cs.AI, cs.CL...), other categories sau (physics, math, stat...).

4. **Dynamic data:** Min/max year và danh sách categories được query từ ES (cached 5 phút), tự động cập nhật khi dataset thay đổi.

**Takeaway cho report:**
- UX quan trọng cho search system — filter phải trực quan, không yêu cầu user biết exact syntax
- ES aggregations hỗ trợ dynamic faceted search (category counts, year range)
- `range` query trên keyword field vẫn hoạt động vì ES so sánh lexicographic trên strings
