# Hybrid Search for Academic Papers (Elasticsearch)

Project: **Building a Hybrid Search System for Academic Documents using Elasticsearch**.

## What you have in this repo
- Elasticsearch indexing (BM25 + dense vectors)
- Hybrid search using **manual RRF** (because native RRF requires paid license)
- Cloudflare Worker API + static HTML/JS frontend (Cloudflare Pages or any static host)
- Benchmark / evaluation scripts

## Prerequisites
1. **Docker** running  
   - **Windows/macOS:** Docker Desktop  
   - **Linux:** Docker Engine + [Compose plugin](https://docs.docker.com/engine/install/) (`docker compose` hoặc `docker-compose`). Nếu lỗi permission, thêm user vào nhóm `docker` (`sudo usermod -aG docker "$USER"`) rồi đăng nhập lại.
2. **Python 3.10+** và virtual environment (xem bên dưới — Windows dùng `.\venv`, Linux/macOS dùng `venv/` sau `python3 -m venv venv`)
3. Download Kaggle dataset and place this file into:
   - `data/arxiv-metadata-oai-snapshot.json`

### Linux / macOS — chuẩn bị môi trường
```bash
chmod +x setup-linux.sh
./setup-linux.sh
source venv/bin/activate   # mỗi lần mở terminal mới
```
Hoặc thủ công: `python3 -m venv venv` → `source venv/bin/activate` → `pip install -r requirements.txt`.

**Heap Elasticsearch (tùy chọn):** trước khi `docker compose up -d`, có thể tăng RAM cho ES:
```bash
export ES_HEAP=4g
docker compose up -d
```

**Tương đương lệnh:** sau `source venv/bin/activate`, dùng `python` / `streamlit` thay cho đường dẫn `.\venv\Scripts\...`. Ví dụ: `python src/data_prep.py`, `streamlit run src/app.py`. Các lệnh nhiều dòng: PowerShell dùng ký tự backtick để xuống dòng; bash dùng `\` ở cuối dòng hoặc gộp một dòng.

### Đưa project lên GitHub (lưu trữ & clone sang máy Linux)
1. **Không commit** thư mục `venv/` và dữ liệu lớn — đã cấu hình trong `.gitignore` và `data/.gitignore` (chỉ giữ `data/test_queries.json` trong repo).
2. Trên máy có Git:
   ```bash
   cd /path/to/Big\ Data
   git init
   git add .
   git commit -m "Initial commit: hybrid search Elasticsearch project"
   ```
3. Tạo repo trống trên [GitHub](https://github.com/new), sau đó:
   ```bash
   git branch -M main
   git remote add origin https://github.com/<user>/<repo>.git
   git push -u origin main
   ```
4. Trên **máy Linux** sau này: `git clone ...` → `./setup-linux.sh` → tải lại file Kaggle vào `data/` → chạy pipeline như README.

## Quick Start (Midterm: 100k)

### 1) Start Elasticsearch + Kibana
```bash
docker compose up -d
```
Kibana Dashboard sẽ mở tại: `http://localhost:5601`

### 2) Prepare data (trích xuất các bài báo CS)
Lệnh này lọc dữ liệu gốc để lấy 100k bài báo thuộc lĩnh vực Computer Science:
- Tạo ra file: `data/arxiv_cs_100k_clean.json`
```bash
python src/data_prep.py
```
*(Windows dùng: `.\venv\Scripts\python.exe src/data_prep.py`)*

### 3) Embed (Title + Abstract -> Dense Vectors 384-dim)
Sinh vector embedding cho các bài báo (nếu teammate có sẵn file `.jsonl` đã embed từ Google Drive thì có thể bỏ qua bước này):
- Tạo ra file: `data/arxiv_cs_100k_with_vectors.jsonl`
```bash
python src/embed_data.py
```
*(Windows dùng: `.\venv\Scripts\python.exe src/embed_data.py`)*

### 4) Cấu hình Dual-Index Architecture
Hệ thống sử dụng kiến trúc **Dual-Index** (tách riêng index tìm kiếm văn bản BM25 và index tìm kiếm kNN vector) nhằm tối ưu hiệu năng và dung lượng. Các bước thiết lập như sau:

#### Bước A: Đẩy toàn bộ dữ liệu (metadata + vector) vào index cơ sở `arxiv_bench`
```bash
python src/index_data_v2.py --input data/arxiv_cs_100k_with_vectors.jsonl --index arxiv_bench
```
*(Windows dùng: `.\venv\Scripts\python.exe src/index_data_v2.py ...`)*

#### Bước B: Chạy Script tự động phân tách cấu trúc Dual-Index
```bash
python src/setup_dual_index.py
```
*(Windows dùng: `.\venv\Scripts\python.exe src/setup_dual_index.py`)*

**Ý nghĩa các file cấu hình Elasticsearch trong thư mục `data/` được sử dụng trong script:**
* 📄 **`data/es_text_mapping.json`**: Chứa cài đặt cấu trúc cho index **`arxiv_text`** (dùng cho tìm kiếm text BM25). Index này sử dụng bộ phân tách từ tùy chỉnh `academic_english` (hỗ trợ chữ thường, lọc stopword học thuật) và **loại bỏ hoàn toàn trường vector** để giữ index nhẹ tối đa.
* 📄 **`data/es_reindex.json`**: Cú pháp lệnh gửi tới API `_reindex` của Elasticsearch để đồng bộ dữ liệu từ `arxiv_bench` sang `arxiv_text`, chỉ lọc lấy các trường text và loại trừ trường `embedding`.
* 📄 **`data/es_alias.json`**: Lệnh gán nhãn Alias **`arxiv_vectors`** trỏ vào index `arxiv_bench` chứa vector, giúp truy vấn kNN hoạt động ổn định thông qua bí danh.

---

## 💻 Khởi chạy Local API & Giao diện React UI

### 1) Chạy FastAPI Backend
Dịch vụ API cục bộ hỗ trợ tìm kiếm Hybrid (RRF), BM25, kNN, lấy danh sách categories, years, và Ingest dữ liệu mới:
```bash
python src/api.py
```
* API hoạt động tại: `http://localhost:8000`
* Tài liệu Swagger UI: `http://localhost:8000/docs`

### 2) Chạy React + Vite Frontend
Giao diện tìm kiếm học thuật được thiết kế Premium Dark Glassmorphism, bộ lọc năm và chuyên mục được hiển thị trực quan, kiểm thử logic năm tự động:
```bash
cd local-ui
npm install
npm run dev
```
* Giao diện hoạt động tại: `http://localhost:5173`

---

## 🧪 Đánh giá & Phân tích (Evaluation)

### 1) Run evaluation (30 queries)
Đánh giá chất lượng tìm kiếm bằng các độ đo học thuật:
- Tạo ra file: `data/evaluation_results.json`
```bash
python src/evaluate.py
```

### 2) Cloudflare API Deployment (Tùy chọn)
Nếu muốn triển khai API lên Cloudflare Worker thay vì chạy server local:
1. Tạo API token có quyền "Edit Cloudflare Workers" tại: https://dash.cloudflare.com/profile/api-tokens.
2. Lưu token vào file `.env` tại `cloudflare/worker/.env`:
   ```env
   CLOUDFLARE_API_TOKEN=your_token_goes_here
   ```
3. Deploy Worker:
   ```bash
   export $(grep CLOUDFLARE_API_TOKEN cloudflare/worker/.env)
   cd cloudflare/worker
   npx wrangler deploy
   ```



## Scale-Up (Final: 1.16M)

### 1) Extract full CS dataset
Generates:
- `data/arxiv_cs_full.jsonl`
```powershell
.\venv\Scripts\python.exe .\src\data_prep_full.py
```

### 2) Embed full vectors (GPU recommended)
Generates:
- `data/arxiv_cs_full_with_vectors.jsonl`
```powershell
.\venv\Scripts\python.exe .\src\embed_data.py --input data/arxiv_cs_full.jsonl
```

### 3) Create 500k and 1M subsets (no re-embedding)
```powershell
.\venv\Scripts\python.exe .\src\truncate_jsonl.py --input data/arxiv_cs_full_with_vectors.jsonl --output data/arxiv_cs_500k_with_vectors.jsonl --lines 500000
.\venv\Scripts\python.exe .\src\truncate_jsonl.py --input data/arxiv_cs_full_with_vectors.jsonl --output data/arxiv_cs_1m_with_vectors.jsonl --lines 1000000
```

### 4) Index multiple scales
Examples:
```powershell
.\venv\Scripts\python.exe .\src\index_data_v2.py --input data/arxiv_cs_500k_with_vectors.jsonl --index arxiv_papers_v2_500k
.\venv\Scripts\python.exe .\src\index_data_v2.py --input data/arxiv_cs_1m_with_vectors.jsonl --index arxiv_papers_v2_1m
.\venv\Scripts\python.exe .\src\index_data_v2.py --input data/arxiv_cs_full_with_vectors.jsonl --index arxiv_papers_v2_full
```

### 5) Multi-scale benchmark
```powershell
.\venv\Scripts\python.exe .\src\benchmark_multiscale.py --indices "100k:arxiv_papers_v2,500k:arxiv_papers_v2_500k,1M:arxiv_papers_v2_1m,1.16M:arxiv_papers_v2_full" --topk 10 --num-candidates 100
```
Output:
- `data/benchmark_results.json` (multiscale)

### 6) Evaluation NDCG/MRR cho full 1.16M (cần ground truth)
1. Tạo template `data/ground_truth.json`:
```powershell
.\venv\Scripts\python.exe .\src\evaluation\generate_ground_truth_template.py `
  --index arxiv_papers_v2_full --topk 10 --output data/ground_truth.json
```
2. Manual label: sửa field `relevant_ids` cho từng query `id` trong `data/ground_truth.json`.
3. Chạy evaluation (sẽ bật NDCG/MRR nếu `relevant_ids` đã được điền):
```powershell
.\venv\Scripts\python.exe .\src\evaluate.py `
  --index arxiv_papers_v2_full `
  --output data/evaluation_results_full.json `
  --ground-truth data/ground_truth.json `
  --topk 10
```

## Code layout (high level)
- `src/pipeline/`: data prep, embedding, indexing
- `src/search/`: BM25 / kNN / Hybrid + compare utilities
- `src/evaluation/`: evaluation + benchmark scripts
- `src/utils/`: sanity checks and data helpers

Note: The files in `src/*.py` are mainly **entry-point wrappers** so older commands still work.

## Dual-Index Architecture

The system uses a **two-index** design for optimal performance and storage efficiency:

| Index | Alias | Purpose | Size | Documents |
|-------|-------|---------|------|-----------|
| `arxiv_text` | — | BM25 full-text search (title, abstract, categories, authors) | ~1.5 GB | 1,203,108 |
| `arxiv_bench` | `arxiv_vectors` | kNN dense-vector search (id + 384-dim embedding) | ~10.4 GB | 1,203,108 |

- **`arxiv_text`** stores all metadata fields but **no embedding vectors**, keeping the index compact and BM25 queries fast.
- **`arxiv_vectors`** (alias → `arxiv_bench`) stores only the document `id` and a 384-dimensional dense vector produced by `all-MiniLM-L6-v2`. This index is used exclusively for kNN approximate nearest-neighbor queries.
- **Hybrid search** runs BM25 on `arxiv_text` and kNN on `arxiv_vectors` in parallel, then merges results using **manual Reciprocal Rank Fusion (RRF)** with `k=60`.

Configuration lives in [`src/config.py`](src/config.py):
```python
INDEX_TEXT    = "arxiv_text"      # BM25 index
INDEX_VECTORS = "arxiv_vectors"  # kNN index (alias → arxiv_bench)
```

## Incremental Ingestion

New documents can be ingested without rebuilding the full index:

```bash
# CLI — ingest a JSONL file (with optional embedding)
python -m src.pipeline.ingest --input data/new_papers.jsonl

# REST API — POST a batch of documents
curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d @data/new_papers.json
```

The ingestion pipeline will:
1. Parse and validate each document.
2. Generate embeddings (if not already present) using `all-MiniLM-L6-v2`.
3. Bulk-index metadata into `arxiv_text` and vectors into `arxiv_vectors`.
4. Report per-batch progress and final counts.

## Common Errors & Fixes

- **`Elasticsearch not reachable` / `localhost:9200` fails**
  - **Windows/macOS:** bật Docker Desktop. **Linux:** `sudo systemctl start docker` (hoặc tương đương), đảm bảo user có quyền gọi `docker` (nhóm `docker`).
  - `docker compose up -d`
  - Check containers: `docker ps`

- **`File not found: data/...jsonl`**
  - Run steps in order (prep -> embed -> index).
  - For full scale, make sure `data/arxiv_cs_full_with_vectors.jsonl` exists before truncate/index.

- **kNN/Hybrid returns unexpected year/category**
  - Verify you are querying index `arxiv_papers_v2` (or the intended scale index).
  - In UI, ensure year filter checkbox is enabled and category selected.

- **Streamlit command not found**
  - Run with venv executable:
  - `.\venv\Scripts\streamlit.exe run .\src\app.py`

- **Very slow embedding on CPU**
  - Use GPU environment (Kaggle/Colab) for full 1.16M embedding.
  - Keep resume behavior by using the same output file.

- **`docker compose` warns about `version` being obsolete**
  - Safe to ignore for now (compose still works).

