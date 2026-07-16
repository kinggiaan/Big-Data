# 📋 Academic Review: Hybrid Search for Academic Papers

**Reviewer perspective**: Master-level Big Data practitioner  
**Project scope**: Bài tập lớn môn học Big Data  
**Date**: 2026-05-21

---

## 1. TỔNG QUAN ĐỀ TÀI

**Đề bài**: Xây dựng hệ thống Hybrid Search cho tài liệu khoa học sử dụng Elasticsearch, kết hợp BM25 (keyword search) và kNN (vector/semantic search) thông qua thuật toán Reciprocal Rank Fusion (RRF).

**Nhận xét chung**: Đề tài này **rất phù hợp** cho một bài tập lớn môn Big Data vì nó đụng đến hầu hết các trụ cột chính của lĩnh vực:
- **Volume**: Dataset arXiv có hơn 2.4 triệu bài báo, trích xuất 1.16M bài CS (~4-5 GB sau khi xử lý)
- **Variety**: Dữ liệu bán cấu trúc (JSON), kết hợp text (title, abstract) với dense vector (384 chiều)
- **Velocity**: Benchmark latency cho thấy yêu cầu real-time search (<100ms)
- **Veracity**: Đánh giá chất lượng tìm kiếm qua NDCG, MRR, overlap analysis

---

## 2. REVIEW LÝ THUYẾT (Theory Assessment)

### 2.1 BM25 — Okapi Best Matching 25 ✅ Chính xác
Bạn sử dụng BM25 thông qua Elasticsearch, đây là **chuẩn vàng** cho keyword-based information retrieval. Cách tiếp cận của bạn:

```
multi_match: { query: "...", fields: ["title^2", "abstract"] }
```

**Đúng về lý thuyết**:
- Boosting `title^2` là hợp lý vì tiêu đề bài báo thường chứa các thuật ngữ quan trọng nhất, mật độ thuật ngữ (term density) cao hơn abstract
- Elasticsearch sử dụng BM25 mặc định với k₁=1.2, b=0.75 — đây là giá trị chuẩn trong cộng đồng IR

**Cần cải thiện về lý thuyết**:
- Trong `benchmark_multiscale.py`, bạn nâng boosting lên `title^3` và dùng `cross_fields` + `minimum_should_match`. Sự không nhất quán này giữa các module (search dùng `^2` + `best_fields`, benchmark dùng `^3` + `cross_fields`) **sẽ làm sai kết quả benchmark so với search thật**. Cần thống nhất.
- Bạn có custom analyzer `academic_english` (stopwords + stemmer) trong `index_data_v2.py` — đây là best practice tốt, nhưng chỉ áp dụng cho `title` và `abstract`. Trường `authors` dùng analyzer mặc định `standard`, hợp lý vì tên tác giả không cần stemming.

### 2.2 kNN Dense Vector Search ✅ Chính xác
- **Model**: `all-MiniLM-L6-v2` (384 chiều, 22.7M params) — lựa chọn hợp lý cho quy mô bài tập. Model này đạt top-tier trong MTEB benchmark cho tốc độ/chất lượng tradeoff.
- **Similarity**: Cosine similarity — phù hợp vì bạn đã `normalize_embeddings=True` khi encode, nghĩa là cosine similarity tương đương dot product trên unit vectors.
- **Embedding strategy**: `f"{title} [SEP] {abstract}"` — cách nối title và abstract bằng `[SEP]` token là **chuẩn kỹ thuật** cho sentence-transformers. Mô hình BERT-based hiểu `[SEP]` như ranh giới giữa hai đoạn văn bản.

**Cần cải thiện**:
- `num_candidates=50` trong `vector_search.py` nhưng `num_candidates=100` trong `evaluate.py` và `benchmark_multiscale.py`. Giá trị `num_candidates` ảnh hưởng trực tiếp đến recall và latency. **Cần thống nhất** giá trị này trong toàn bộ project.

### 2.3 Reciprocal Rank Fusion (RRF) ✅ Chính xác
Công thức RRF bạn implement:
```
RRF(d) = Σ 1/(k + rank_i(d))   với k = 60
```

**Đúng theo paper gốc** (Cormack, Clarke & Buettcher, 2009). Giá trị k=60 là giá trị được đề xuất trong paper và cũng là giá trị mặc định của Elasticsearch native RRF (bản trả phí).

**Phân tích sâu hơn**:
- RRF là phương pháp **rank-level fusion** (không phải score-level fusion). Điều này có nghĩa nó không cần normalize score giữa BM25 và kNN — đây chính là ưu điểm lớn nhất của RRF so với weighted linear combination.
- Bạn gọi BM25 và kNN **tuần tự** (sequential) trong Python, nhưng **song song** (parallel via `Promise.all()`) trong Cloudflare Worker. Phiên bản Worker là đúng kỹ thuật hơn vì RRF chỉ cần ranking chứ không cần score phụ thuộc lẫn nhau. Phía Python cũng nên chạy song song (dùng `asyncio` hoặc `threading`) để giảm latency.

### 2.4 Evaluation Metrics ✅ Chính xác
- **NDCG@k** (Normalized Discounted Cumulative Gain): Đo chất lượng ranking có xét vị trí
- **MRR** (Mean Reciprocal Rank): Đo vị trí trung bình của kết quả đúng đầu tiên
- **Overlap Analysis**: BM25∩kNN, BM25∩Hybrid, kNN∩Hybrid — cho thấy Hybrid có đang thực sự kết hợp cả hai phương pháp hay không

**Cần cải thiện**:
- Hiện tại **chưa có ground truth thật sự** (file `ground_truth.json` chưa được điền `relevant_ids`), nên NDCG/MRR bị skip. Đây là **thiếu sót lớn nhất** của project. Nên label ít nhất 30 queries × top-10 results = 300 cặp relevance judgments.

---

## 3. REVIEW PIPELINE XỬ LÝ DỮ LIỆU

### 3.1 Data Ingestion & Preparation

```
arxiv-metadata-oai-snapshot.json (3.6GB, ~2.4M records)
        │
        ▼ data_prep.py / data_prep_full.py
        │  - Filter: categories chứa "cs."
        │  - Clean: title/abstract remove newlines
        │  - Extract: year từ update_date
        │
        ▼ Output: arxiv_cs_100k_clean.json (JSON array) 
                  hoặc arxiv_cs_full.jsonl (JSONL streaming)
```

**Điểm mạnh**:
- `data_prep_full.py` dùng **streaming** (đọc từng dòng) — đây là cách đúng khi xử lý file 3.6 GB, tránh OOM
- Xuất ra JSONL (JSON Lines) thay vì JSON array — đúng best practice cho Big Data pipeline vì JSONL có thể stream, resume, và parallel process

**Vấn đề phát hiện**:

| # | Vấn đề | Mức độ | Giải thích |
|---|--------|--------|------------|
| 1 | **`data_prep.py` load toàn bộ vào RAM** | 🟡 Trung bình | `json.dump(extracted_records, f, ...)` giữ toàn bộ 100k records trong list `extracted_records`. Với 100k records, RAM cần ~1-2 GB. Với full 1.16M, **chắc chắn OOM**. Nên dùng streaming như `data_prep_full.py`. |
| 2 | **`year` lấy từ `update_date` thay vì submission date** | 🟡 Trung bình | `update_date` là ngày cập nhật cuối cùng, không phải ngày xuất bản. Một bài submit 2018 nhưng cập nhật 2023 sẽ có `year=2023`. Điều này **ảnh hưởng đến tính chính xác** khi lọc theo năm. Nên parse năm từ arXiv ID (format `YYMM.nnnnn`, ví dụ `2301.00001` → year=2023). |
| 3 | **Không deduplicate** | 🟢 Nhẹ | Dataset arXiv gốc có thể có bản ghi trùng ID. Nên thêm kiểm tra `seen_ids = set()` trong data_prep. |

### 3.2 Embedding Generation

```
arxiv_cs_100k_clean.json
        │
        ▼ embed_data.py
        │  - Model: all-MiniLM-L6-v2
        │  - Input: "{title} [SEP] {abstract}"
        │  - Batch: 64 (CPU) / 512 (GPU)
        │  - Checkpoint: mỗi 10,000 records
        │
        ▼ Output: arxiv_cs_100k_with_vectors.jsonl
```

**Điểm mạnh**:
- **Checkpoint/Resume**: Đếm dòng đã xử lý trong file output, nếu bị gián đoạn thì tiếp tục từ chỗ dừng. Đây là pattern **rất quan trọng** trong Big Data pipeline.
- **Normalize embeddings**: `normalize_embeddings=True` đảm bảo tất cả vector nằm trên unit sphere, làm cho cosine similarity = dot product. Điều này cho phép Elasticsearch dùng HNSW index hiệu quả hơn.
- **Adaptive batch size**: Tự detect CPU/GPU và chọn batch size phù hợp.

**Vấn đề**:

| # | Vấn đề | Mức độ | Giải thích |
|---|--------|--------|------------|
| 1 | **Không truncate input text** | 🟡 Trung bình | `all-MiniLM-L6-v2` có max sequence length = 256 tokens. Nhiều abstract arXiv dài hơn 256 tokens. Model sẽ tự cắt phần thừa, nhưng phần bị cắt sẽ không được encode. Nên **truncate abstract** trước khi nối với title, ví dụ giữ 200 tokens abstract. |
| 2 | **Đọc toàn bộ JSON array** (nếu input là `.json`) | 🟡 Trung bình | `read_records()` xử lý cả JSON array và JSONL. Với JSON array, `json.load(f)` load toàn bộ file vào RAM. Nên **ưu tiên JSONL input** cho pipeline lớn. |

### 3.3 Indexing

```
arxiv_cs_100k_with_vectors.jsonl
        │
        ▼ index_data_v2.py (Elasticsearch)
        │  - 5 shards, 0 replicas
        │  - Custom analyzer: academic_english
        │  - dense_vector: 384 dims, cosine, HNSW indexed
        │  - Bulk streaming (500 docs/chunk)
        │  - Disable refresh during indexing
        │
        ▼ Index: arxiv_papers_v2
```

**Điểm mạnh rất tốt**:
- `refresh_interval: -1` + `replicas: 0` trong quá trình indexing, khôi phục `1s` sau khi xong. Đây là **chuẩn best practice** cho bulk indexing Elasticsearch, giảm overhead write từ 30-50%.
- **Streaming bulk** (`stream_actions` generator + `helpers.streaming_bulk`): Không load toàn bộ data vào RAM. Đây là cách đúng khi index 100k-1M+ documents.
- `chunk_size=500`: Hợp lý cho documents có embedding (mỗi doc ~2KB text + 384×4 bytes vector ≈ 3.5KB, 500 docs ≈ 1.75MB/request).

**Vấn đề**:

| # | Vấn đề | Mức độ | Giải thích |
|---|--------|--------|------------|
| 1 | **5 shards cho single-node** | 🟡 Trung bình | Bạn chạy Elasticsearch single-node (1 container Docker). 5 shards trên 1 node gây thêm overhead mà không tăng throughput. Cho 100k docs, **1-2 shards** là đủ. 5 shards phù hợp hơn cho scale 1M+ hoặc multi-node cluster. |
| 2 | **Xóa index cũ không hỏi** | 🟢 Nhẹ | `es.indices.delete(index=args.index)` xóa toàn bộ index mà không confirm. Trong production nên có flag `--force` hoặc prompt xác nhận. |

### 3.4 Data Format Evolution

Bạn có 2 phiên bản indexing song song:

| Version | File | Index | Shards | Analyzer | Vector |
|---------|------|-------|--------|----------|--------|
| v1 | `index_data.py` | `arxiv_papers` | 1 | default | ❌ Không |
| v2 | `index_data_v2.py` | `arxiv_papers_v2` | 5 | `academic_english` | ✅ 384-dim cosine |

Sự tiến hóa v1 → v2 cho thấy quá trình phát triển rõ ràng: **BM25-only → BM25 + kNN hybrid**. Đây là narrative tốt cho báo cáo.

---

## 4. REVIEW KIẾN TRÚC HỆ THỐNG

### 4.1 Dual Architecture (Local + Serverless)

```
┌─── LOCAL (Development & Evaluation) ──────────────┐
│  Docker Compose                                     │
│  ├── Elasticsearch 8.12 (BM25 + kNN HNSW)          │
│  └── Kibana (monitoring)                            │
│                                                     │
│  Python Scripts                                     │
│  ├── Pipeline: data_prep → embed → index            │
│  ├── Search: BM25 / kNN / Hybrid comparison         │
│  └── Evaluation: NDCG, MRR, latency benchmark       │
└─────────────────────────────────────────────────────┘

┌─── SERVERLESS (Production Deployment) ────────────┐
│  Cloudflare Workers (TypeScript + Hono)             │
│  ├── D1 (SQLite) + FTS5 → thay thế ES BM25         │
│  ├── Vectorize → thay thế ES kNN                    │
│  └── Workers AI (BGE-small) → query embedding       │
│                                                     │
│  Cloudflare Pages                                   │
│  └── Static HTML/CSS/JS frontend                    │
└─────────────────────────────────────────────────────┘
```

**Nhận xét**: Kiến trúc dual này **vượt mức yêu cầu** của một bài tập lớn. Nó cho thấy bạn hiểu sự khác biệt giữa development environment và production deployment. Tuy nhiên, có một vấn đề lý thuyết quan trọng:

> [!WARNING]
> **Embedding Model Mismatch**: Local dùng `all-MiniLM-L6-v2` (384 dims) để encode query, nhưng Cloudflare Worker dùng `@cf/baai/bge-small-en-v1.5` (cũng 384 dims nhưng **khác model hoàn toàn**). Hai model này tạo ra embedding spaces khác nhau. Khi query vector được tạo bởi BGE-small nhưng document vectors được tạo bởi MiniLM-L6-v2, **cosine similarity sẽ không có ý nghĩa** (comparing vectors from different embedding spaces). Đây là lỗi lý thuyết nghiêm trọng trong phiên bản Cloudflare.

### 4.2 Multi-scale Benchmark Design ✅ Tốt

```
100k → 500k → 1M → 1.16M (full CS)
```

Thiết kế benchmark multi-scale cho thấy bạn muốn đo **scalability** — một khái niệm core của Big Data. Đo latency P50/P95/P99 ở từng quy mô để vẽ biểu đồ scaling behavior là cách đúng.

---

## 5. REVIEW BỘ TEST QUERIES ✅ Thiết kế tốt

File `test_queries.json` chia 30 queries thành 3 nhóm:
- **Group A (10 queries)**: `A_exact` — thuật ngữ chính xác (BERT, ResNet, GAN...) → BM25 nên thắng
- **Group B (10 queries)**: `B_semantic` — diễn đạt lại ý tưởng (rephrased) → kNN nên thắng
- **Group C (10 queries)**: `C_mixed` — kết hợp thuật ngữ + ngữ cảnh → Hybrid nên thắng

**Đây là thiết kế rất tốt** vì nó trực tiếp kiểm chứng giả thuyết nghiên cứu:
> *"Hybrid search (BM25 + kNN via RRF) outperforms both pure BM25 and pure kNN across diverse query types"*

Nếu kết quả cho thấy Hybrid thắng ở Group C nhưng không thua nhiều ở Group A và B, **giả thuyết được xác nhận**.

---

## 6. ĐÁNH GIÁ TỔNG THỂ

### Điểm mạnh (Strengths)

| # | Tiêu chí | Đánh giá |
|---|----------|----------|
| 1 | **Lý thuyết IR chuẩn** | BM25, kNN cosine, RRF k=60 — tất cả đều đúng theo literature |
| 2 | **Pipeline có tính sản xuất** | Streaming I/O, checkpoint/resume, bulk indexing optimization |
| 3 | **Evaluation methodology** | 3 nhóm query thiết kế có chủ đích, NDCG + MRR + overlap |
| 4 | **Multi-scale benchmark** | 100k → 500k → 1M → 1.16M cho thấy scalability analysis |
| 5 | **Dual deployment** | Local ES + Serverless Cloudflare, cho thấy hiểu biết production |
| 6 | **Code organization** | Tách rõ pipeline / search / evaluation / utils / cloudflare |

### Điểm yếu cần khắc phục (Weaknesses)

| # | Vấn đề | Priority | Hành động khắc phục |
|---|--------|----------|---------------------|
| 1 | **Chưa có ground truth** | 🔴 Cao | Label `relevant_ids` cho ít nhất 30 queries. Không có ground truth thì NDCG/MRR = 0, đánh giá chất lượng search không có ý nghĩa. |
| 2 | **Embedding model mismatch** (Cloudflare) | 🔴 Cao | Dùng chung model hoặc re-embed documents bằng BGE-small trước khi upload Vectorize. |
| 3 | **Year field sai** (`update_date` vs submission) | 🟡 Trung bình | Parse year từ arXiv ID prefix (`YYMM.nnnnn`). |
| 4 | **Tham số không nhất quán** giữa các module | 🟡 Trung bình | Thống nhất `num_candidates`, `title boost factor`, `query type` trong một file config chung. |
| 5 | **Data pipeline hiện chỉ có 3 records** | 🟡 Trung bình | Cần chạy lại pipeline trên dữ liệu thật (xử lý trên Colab). |
| 6 | **Thiếu data validation** | 🟢 Nhẹ | Thêm kiểm tra: embedding dimension = 384, no NaN values, no duplicate IDs. |

---

## 7. GỢI Ý ĐỂ NÂNG CAO ĐIỂM BÀI TẬP LỚN

### 7.1 Điều bắt buộc phải có (cho điểm tốt)
1. **Chạy pipeline thật trên dữ liệu 100k+** — không thể nộp bài với 3 records
2. **Label ground truth** cho 30 queries — chạy `generate_ground_truth_template.py`, xem candidates, đánh dấu relevant papers
3. **Tạo bảng kết quả NDCG/MRR** so sánh BM25 vs kNN vs Hybrid — đây là kết quả chính của bài

### 7.2 Điều nên có (để nổi bật)
4. **Biểu đồ scaling** (đã có script `benchmark_multiscale.py`): vẽ latency P50/P95 theo số lượng documents (100k → 500k → 1M) — chứng minh Big Data scalability
5. **Phân tích per-group**: Tách kết quả NDCG theo Group A/B/C để chứng minh khi nào BM25 tốt hơn, khi nào kNN tốt hơn, và Hybrid là tối ưu tổng thể
6. **Fix year parsing từ arXiv ID**: Thể hiện sự chú ý đến data quality

### 7.3 Điều bonus (nếu còn thời gian)
7. **So sánh RRF k-value**: Thử k=20, k=60, k=100 để thấy impact
8. **A/B test embedding models**: So sánh MiniLM-L6-v2 vs BGE-small vs E5-small
9. **Confusion matrix**: Bao nhiêu phần trăm kết quả BM25 cũng xuất hiện trong kNN (overlap analysis đã có, chỉ cần visualize)

---

*Review này được thực hiện dựa trên phân tích toàn bộ source code, cấu trúc dữ liệu, và knowledge graph (GitNexus) của project.*
