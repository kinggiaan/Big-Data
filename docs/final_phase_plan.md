# Kế Hoạch Chi Tiết: Phase 2 → Final (21/03 - 15/05/2026)

**Ngày cập nhật:** 26/03/2026 (v4 -- đồng bộ lại trạng thái repo hiện tại)
**Trạng thái hiện tại (repo):** ✅ 100k end-to-end (Docker + ES + v2 index + BM25/kNN/Hybrid + Streamlit UI + benchmark/eval latency+overlap)
**Trạng thái scale-up 1.16M:** ⏳ Chưa hoàn tất (thiếu `*_full_with_vectors.jsonl`, chưa index 500k/1M/1.16M, chưa có ground truth để tính NDCG/MRR)

---

## Số Liệu Thực Tế Từ Dataset

| Metric | Giá trị |
|---|---|
| Tổng papers trong arXiv dataset | **2,982,054** |
| Papers thuộc CS (có chứa `cs.`) | **1,163,999** |
| File gốc (line-delimited JSON) | **4.8 GB** |
| File clean 100k (midterm) | **114.6 MB** |
| Thời gian scan toàn bộ file gốc | **~84 giây** |

---

## Chiến Lược Scale-Up (Điểm khác biệt so với Midterm)

### Midterm → Final: Thay đổi cốt lõi

| Hạng mục | Midterm (100k) | Final (1.16M) | Thách thức Big Data |
|---|---|---|---|
| Data size | 114 MB | ~1.3 GB (text) + ~1.7 GB (vectors) = **~3 GB** | Không thể `json.load()` vào RAM |
| Indexing | `json.load()` cả file | **Streaming line-by-line** | Cần generator + chunked bulk |
| ES Shards | 1 shard | **5 shards** | Parallel search across shards |
| ES Heap | 2 GB | **4-6 GB (khi scale-up)** | JVM memory management |
| Embedding | 100k × 384 dims (~150 MB) | 1.16M × 384 dims (~1.7 GB) | Cần GPU hoặc Kaggle notebook |
| Indexing time | ~30 giây | Ước tính **15-30 phút** | Cần progress tracking, error recovery |
| Custom analyzer | Không | **Academic English analyzer** | Stemming, stop words, synonyms |

### Data Processing Strategy cho 1.16M papers

```
Phase A: data_prep_full.py (streaming, ~2 phút)
  - Đọc line-by-line từ 4.8GB file gốc
  - Lọc CS papers → ghi ra file JSONL (line-delimited, KHÔNG json.dump cả array)
  - Output: data/arxiv_cs_full.jsonl (~1.3 GB, 1.16M lines)

Phase B: embed_data.py (trên Kaggle GPU, ~30-45 phút) — **chưa chạy full trong repo**
  - Đọc JSONL streaming
  - Encode title + abstract → 384-dim vector
  - Ghi ra: data/arxiv_cs_full_with_vectors.jsonl (**hiện repo chưa có file này**)
  - Checkpoint mỗi 50k records

Phase C: index_data_v2.py (streaming bulk, ~15-30 phút)
  - Đọc JSONL line-by-line (KHÔNG json.load cả file)
  - Generator yield từng doc cho helpers.bulk()
  - Batch size 5,000, request timeout 120s
```

---

## Phase 2: Vector & Hybrid Search (21/03 → 10/04)

### Tuần 1 (21/03 - 27/03): Vector Embeddings

**Mục tiêu:** Embed 100k papers trước (validate pipeline), sau đó scale lên 1.16M.

| Task | Mô tả | Người | Deadline | Output |
|---|---|---|---|---|
| 2.1.1 | Cài `sentence-transformers`, `torch` vào venv | Gia An | 21/03 | requirements.txt cập nhật |
| 2.1.2 | Viết `src/embed_data.py`: streaming read JSONL, encode, streaming write JSONL, checkpoint mỗi 50k | Gia An | 23/03 | Script chạy được trên 100k |
| 2.1.3 | Chạy embedding 100k trên local (CPU, ~15-30 phút) để validate | Gia An | 24/03 | `data/arxiv_cs_100k_with_vectors.jsonl` |
| 2.1.4 | Sanity check: cosine similarity giữa 2 câu giống nghĩa > 0.7 | Gia An | 24/03 | Test pass |
| 2.1.5 | Viết `src/data_prep_full.py`: trích xuất toàn bộ 1.16M CS papers → JSONL | Gia An | 25/03 | `data/arxiv_cs_full.jsonl` (~1.3 GB) |
| 2.1.6 | Chạy embedding 1.16M trên **Kaggle notebook** (free GPU T4, ~30-45 phút) | Gia An | 27/03 | `data/arxiv_cs_full_with_vectors.jsonl` |

**Chi tiết kỹ thuật `embed_data.py`:**
```
- Input: data/arxiv_cs_full.jsonl (JSONL format, streaming)
- Model: sentence-transformers/all-MiniLM-L6-v2 (384 dimensions)
- Encode: title + " [SEP] " + abstract
- Batch size: 512 (GPU) hoặc 64 (CPU)
- Checkpoint: save progress mỗi 50k records (phòng crash)
- Output: data/arxiv_cs_full_with_vectors.jsonl (mỗi dòng có thêm "embedding" field)
- QUAN TRỌNG: dùng JSONL (1 JSON object/dòng), KHÔNG dùng json.dump([...]) cả array
```

### Tuần 2 (28/03 - 03/04): kNN Search + Scale-Up Indexing

**Mục tiêu:** Index 1.16M docs vào ES, implement Vector Search.

| Task | Mô tả | Người | Deadline | Output |
|---|---|---|---|---|
| 2.2.1 | (Tuỳ chọn) tăng heap ES lên 4GB khi scale-up (`ES_HEAP=4g`) | Gia An | 28/03 | Docker config |
| 2.2.2 | Viết `src/index_data_v2.py`: streaming JSONL reader + mapping 5 shards + dense_vector + custom analyzer | Gia An | 29/03 | Script hoàn chỉnh |
| 2.2.3 | Index 100k trước để validate, rồi chạy full 1.16M (~15-30 phút) | Gia An | 31/03 | 1.16M docs indexed |
| 2.2.4 | Viết `src/vector_search.py`: implement kNN query | Gia An | 01/04 | Script chạy được |
| 2.2.5 | So sánh nhanh BM25 vs kNN trên cùng queries | Gia An | 02/04 | Ghi nhận kết quả |

**Mapping mới (v2) -- Full scale:**
```json
{
  "settings": {
    "number_of_shards": 5,
    "number_of_replicas": 0,
    "analysis": {
      "analyzer": {
        "academic_english": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase", "english_stop", "english_stemmer"]
        }
      },
      "filter": {
        "english_stop": { "type": "stop", "stopwords": "_english_" },
        "english_stemmer": { "type": "stemmer", "language": "english" }
      }
    }
  },
  "mappings": {
    "properties": {
      "id": { "type": "keyword" },
      "title": {
        "type": "text",
        "analyzer": "academic_english",
        "fields": { "raw": { "type": "keyword" } }
      },
      "abstract": { "type": "text", "analyzer": "academic_english" },
      "categories": { "type": "keyword" },
      "authors": { "type": "text" },
      "year": { "type": "keyword" },
      "embedding": {
        "type": "dense_vector",
        "dims": 384,
        "index": true,
        "similarity": "cosine"
      }
    }
  }
}
```

### Tuần 3 (04/04 - 10/04): Hybrid Search + Scalability Benchmark

**Mục tiêu:** RRF hoàn chỉnh + chạy benchmark ở nhiều mức scale.

| Task | Mô tả | Người | Deadline | Output |
|---|---|---|---|---|
| 2.3.1 | Viết `src/hybrid_search.py`: BM25 + kNN qua `sub_searches` + `rank: { rrf: {} }` | Gia An | 06/04 | Script chạy được |
| 2.3.2 | Viết `src/search_compare.py`: chạy 1 query qua 3 mode, in cạnh nhau | Gia An | 07/04 | So sánh trực quan |
| 2.3.3 | **Viết `src/benchmark.py`: scalability experiment** (xem chi tiết bên dưới) | Gia An | 09/04 | Bảng + biểu đồ |
| 2.3.4 | Test 10 queries thủ công, ghi nhận Hybrid tốt/kém hơn | Cả nhóm | 10/04 | Ghi chú evaluation |

**Chi tiết `benchmark.py` -- Scalability Experiment:**
```
Mục tiêu: Đo hiệu năng hệ thống ở 4 mức scale khác nhau

Quy trình:
1. Tạo 4 index riêng biệt: arxiv_100k, arxiv_500k, arxiv_1m, arxiv_full (1.16M)
2. Với mỗi index, đo:
   a. Indexing time (giây)
   b. Index size on disk (GB) -- GET /_cat/indices?v
   c. BM25 query latency: chạy 20 queries, lấy P50/P95/P99
   d. kNN query latency: chạy 20 queries, lấy P50/P95/P99
   e. Hybrid query latency: chạy 20 queries, lấy P50/P95/P99
   f. Memory usage -- GET /_nodes/stats/jvm

Output:
- data/benchmark_results.json
- Biểu đồ matplotlib: latency vs dataset_size (3 đường cho 3 mode)
- Biểu đồ: index_size vs dataset_size
```

**Bảng benchmark mẫu (sẽ điền số thật):**

| Metric | 100k v1 (text-only) | 100k v2 (text+vector) | 500k | 1M | 1.16M |
|---|---|---|---|---|---|
| Index size (MB) | **105.4** | **916.6** (9x) | ? | ? | ? |
| BM25 P50 / P95 (ms) | 96.6 / 236.7 | **66.0 / 92.2** | ? | ? | ? |
| kNN P50 / P95 (ms) | N/A | **68.6 / 118.0** | ? | ? | ? |
| Hybrid RRF P50 / P95 (ms) | N/A | **156.4 / 278.6** | ? | ? | ? |
| ES heap (MB) | 476/2048 (23%) | **982/2048** (48%) | ? | ? | ? |

> v2 đo 25/03/2026, ES 8.12.2, single node, 5 shards, heap 2GB, custom academic_english analyzer.
> Hybrid RRF = manual Python (k=60), vì ES free license không hỗ trợ native RRF.

**Evaluation Results (30 queries — 25/03/2026):**

| Metric | BM25 | kNN | Hybrid (RRF) |
|---|---|---|---|
| Avg Latency (ms) | **67.7** | **71.8** | **175.6** |
| Avg BM25∩kNN Overlap | 1.5/10 | — | — |
| Avg BM25∩Hybrid Overlap | 5.5/10 | — | — |
| Avg kNN∩Hybrid Overlap | — | 5.2/10 | — |

**Key findings:**
- BM25 ∩ kNN overlap chỉ **1.5/10** → hai mode tìm kết quả rất khác nhau → Hybrid có giá trị
- Nhóm B_semantic: overlap chỉ **0.8/10** → kNN tìm ra kết quả BM25 hoàn toàn bỏ lỡ
- Hybrid kết hợp cân bằng: ~5.5 từ BM25 + ~5.2 từ kNN
- Index size tăng 9x do 384-dim vector embeddings

---

## Phase 3: UI & Evaluation (11/04 → 30/04)

### Tuần 4-5 (11/04 - 20/04): Streamlit UI

| Task | Mô tả | Người | Deadline | Output |
|---|---|---|---|---|
| 3.1.1 | Cài `streamlit`, tạo `src/app.py` | Gia An | 12/04 | ✅ App chạy localhost:8501 |
| 3.1.2 | Search input + mode selector (BM25/kNN/Hybrid) + filter year/category | Gia An + Sơn Lâm | 15/04 | ✅ UI hoàn chỉnh |
| 3.1.3 | Result cards: title, authors, year, abstract snippet, score, highlight | Gia An | 17/04 | ✅ UI đẹp |
| 3.1.4 | Sidebar: total results, latency, category chart, dataset info | Sơn Lâm | 20/04 | ✅ Dashboard |

### Tuần 5-6 (18/04 - 30/04): Evaluation

| Task | Mô tả | Người | Deadline | Output |
|---|---|---|---|---|
| 3.2.1 | Tạo 30 test queries (10 exact + 10 semantic + 10 mixed) | Thanh Huyền + Sơn Lâm | 20/04 | ✅ `data/test_queries.json` |
| 3.2.2 | Manual relevance labeling: top-10 × 3 modes × 30 queries | Cả nhóm | 24/04 | `data/ground_truth.json` (**chưa có trong repo**) |
| 3.2.3 | Viết `src/evaluate.py`: NDCG@10, MRR, Avg Latency | Gia An | 26/04 | ✅ Script có sẵn; **NDCG/MRR chỉ chạy khi có ground truth** |
| 3.2.4 | So sánh default analyzer vs custom `academic_english` analyzer | Gia An | 27/04 | Bảng so sánh |
| 3.2.5 | Tạo bảng + biểu đồ cho report | Thanh Huyền | 28/04 | Figures |
| 3.2.6 | Phân tích: khi nào Hybrid thắng/thua, tại sao | Cả nhóm | 30/04 | Ghi chú |

**30 test queries (3 nhóm):**

| Nhóm | Số lượng | Ví dụ | Mục đích |
|---|---|---|---|
| A. Exact term | 10 | "BERT", "ResNet-50", "Adam optimizer" | BM25 phải thắng kNN |
| B. Semantic | 10 | "methods to detect fake images" (= deepfake detection) | kNN phải thắng BM25 |
| C. Mixed | 10 | "transformer architecture for NLP tasks 2022" | Hybrid phải thắng |

---

## Phase 4: Finalization (01/05 → 15/05)

### Tuần 7 (01/05 - 07/05): Report & Slides

| Task | Mô tả | Người | Deadline | Output |
|---|---|---|---|---|
| 4.1.1 | Mở rộng report: Vector Embedding, Hybrid Search, Scale-Up challenges | Thanh Huyền | 04/05 | Report draft |
| 4.1.2 | Thêm chapter **Scalability Analysis**: benchmark table + biểu đồ latency vs scale | Gia An | 05/05 | Key chapter |
| 4.1.3 | Thêm hình: Hybrid pipeline, evaluation charts, UI screenshots, benchmark graphs | Sơn Lâm | 05/05 | Figures |
| 4.1.4 | Tạo slide final (15-20 slides) | Thanh Huyền + Sơn Lâm | 06/05 | Slide draft |
| 4.1.5 | Review chéo | Cả nhóm | 07/05 | Feedback |

### Tuần 8 (08/05 - 15/05): Code Cleanup & Submission

| Task | Mô tả | Người | Deadline | Output |
|---|---|---|---|---|
| 4.2.1 | Refactor code, docstrings, module structure | Gia An | 10/05 | Code clean |
| 4.2.2 | README.md: setup guide (Docker → data_prep → embed → index → search → UI) | Gia An | 11/05 | ✅ README đã có (100k + hướng dẫn scale-up) |
| 4.2.3 | E2E test: fresh clone → full pipeline | Sơn Lâm | 12/05 | Test pass |
| 4.2.4 | Finalize report + slides | Thanh Huyền | 13/05 | Final versions |
| 4.2.5 | Rehearsal | Cả nhóm | 14/05 | Sẵn sàng |
| 4.2.6 | Submit | Gia An | 15/05 | DONE |

---

## Cấu Trúc Source Code Cuối Kỳ

```
Big Data/
├── docker-compose.yml          (heap mặc định 2GB; có thể set `ES_HEAP=4g` khi scale-up)
├── requirements.txt            (updated: + sentence-transformers, torch, streamlit, plotly, matplotlib)
├── README.md                   (MỚI: full setup guide)
├── data/
│   ├── arxiv-metadata-oai-snapshot.json   (4.8 GB raw - NOT in git)
│   ├── arxiv_cs_100k_clean.json           (midterm subset)
│   ├── arxiv_cs_full.jsonl                (1.16M CS papers, ~1.3 GB)
│   ├── arxiv_cs_full_with_vectors.jsonl   (1.16M + embeddings, ~3 GB) (**planned / chưa có trong repo**)
│   ├── test_queries.json                  (30 evaluation queries)
│   ├── evaluation_results.json            (30-query evaluation output)
│   ├── ground_truth.json                  (manual relevance labels) (**planned / chưa có trong repo**)
│   └── benchmark_results.json             (scalability experiment data)
├── src/
│   ├── data_prep.py            (Phase 1 - 100k subset)
│   ├── data_prep_full.py       (Phase 2 - MỚI: full 1.16M CS extraction)
│   ├── embed_data.py           (Phase 2 - MỚI: streaming embedding)
│   ├── index_data.py           (Phase 1 - 100k, json.load)
│   ├── index_data_v2.py        (Phase 2 - MỚI: streaming JSONL, 5 shards, custom analyzer)
│   ├── search.py               (Phase 1 - BM25 only)
│   ├── vector_search.py        (Phase 2 - MỚI: kNN search)
│   ├── hybrid_search.py        (Phase 2 - MỚI: BM25 + kNN + RRF)
│   ├── search_compare.py       (Phase 2 - MỚI: side-by-side 3 modes)
│   ├── benchmark.py            (Phase 2 - MỚI: scalability experiment)
│   ├── evaluate.py             (Phase 3 - MỚI: NDCG/MRR metrics)
│   └── app.py                  (Phase 3 - MỚI: Streamlit UI)
├── docs/
│   └── ...
├── notebooks/
│   └── kaggle_embedding.ipynb  (MỚI: Kaggle notebook cho GPU embedding)
└── Report_Midterm/
    └── ...
```

---

## Rủi Ro & Biện Pháp (cập nhật)

| Rủi ro | Xác suất | Biện pháp |
|---|---|---|
| **Embedding 1.16M quá chậm trên CPU** | **Cao** | Dùng Kaggle notebook (free GPU T4, ~30-45 phút) |
| **ES hết RAM với 1.16M + vectors** | Trung bình | Tăng heap 4-6GB. Fallback: embed 500k, text-only cho phần còn lại |
| **json.load() crash với file lớn** | **Chắc chắn** | Chuyển sang JSONL + streaming reader (BẮT BUỘC) |
| **Index 1.16M mất quá lâu** | Trung bình | Streaming bulk + chunk 5000. Ước tính 15-30 phút |
| RRF API khác syntax ở ES 8.12 | ~~Thấp~~ **Đã xảy ra** | ✅ Đã implement RRF thủ công bằng Python (k=60) |
| Evaluation thiếu ground truth | Trung bình | Mỗi người label 10 queries × 10 results = 100 judgments |
| Streamlit chậm khi query 1.16M | Thấp | `@st.cache_data`, pre-encode query vector |

---

## Milestone Checkpoints (cập nhật)

| Ngày | Checkpoint | Tiêu chí pass |
|---|---|---|
| **24/03** | Embedding pipeline validated | 100k vectors ok, cosine similarity test pass |
| **27/03** | Full data ready | 1.16M CS papers extracted + embedded (via Kaggle) (**chưa đạt trong repo hiện tại**) |
| **31/03** | Full index on ES | 1.16M docs indexed (5 shards), `_count` = 1,163,999 (**chưa đạt trong repo hiện tại**) |
| **03/04** | kNN search working | Vector search trên 1.16M trả về kết quả đúng |
| **09/04** | Benchmark done | Bảng latency 4 mức scale + biểu đồ matplotlib |
| **10/04** | Hybrid search done | 3 mode đều chạy trên 1.16M docs |
| **20/04** | UI done | Streamlit app tìm kiếm 1.16M docs |
| **30/04** | Evaluation done | NDCG/MRR/Latency cho 3 modes |
| **07/05** | Report & slides draft | Bản nháp có chapter Scalability Analysis |
| **15/05** | SUBMIT | Mọi thứ đã nộp |
