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
```powershell
docker compose up -d
```
Then you should be able to open Kibana at:
- `http://localhost:5601`

### 2) Prepare data (extract CS papers)
This generates:
- `data/arxiv_cs_100k_clean.json`
```powershell
.\venv\Scripts\python.exe .\src\data_prep.py
```

### 3) Embed (title + abstract -> dense vectors)
This generates (default output):
- `data/arxiv_cs_100k_with_vectors.jsonl`
```powershell
.\venv\Scripts\python.exe .\src\embed_data.py
```

### 4) Index into Elasticsearch (v2 index with vectors)
This (default) builds:
- index: `arxiv_papers_v2`
```powershell
.\venv\Scripts\python.exe .\src\index_data_v2.py
```

### 5) Run evaluation (30 queries)
Output:
- `data/evaluation_results.json`
```powershell
.\venv\Scripts\python.exe .\src\evaluate.py
```

### 6) Cloudflare UI & API Deployment

The UI is now served via static HTML/JS (e.g., Cloudflare Pages), talking to the Cloudflare Worker API.
- Point your browser to the deployed frontend (or open `index.html` + set `API_BASE`).
- Backend does not require local Python server or Streamlit anymore.

#### Deploy or Update Cloudflare Worker API
1. Create a classic API token with "Edit Cloudflare Workers" permissions at: https://dash.cloudflare.com/profile/api-tokens.
2. Save the token in a file `.env` inside `cloudflare/worker/`:
   ```
   CLOUDFLARE_API_TOKEN=your_token_goes_here
   ```
3. When you want to deploy/update the Worker, run:
   ```sh
   export $(grep CLOUDFLARE_API_TOKEN cloudflare/worker/.env)
   cd cloudflare/worker
   npx wrangler deploy
   ```
4. Wrangler (the deployment tool) only works if the `CLOUDFLARE_API_TOKEN` environment variable is exported at deploy time!

- If using CI/CD, make sure to set up your secret token as an environment variable there too.


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

