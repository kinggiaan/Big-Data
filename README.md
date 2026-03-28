# Hybrid Search for Academic Papers (Elasticsearch)

Project: **Building a Hybrid Search System for Academic Documents using Elasticsearch**.

## What you have in this repo
- Elasticsearch indexing (BM25 + dense vectors)
- Hybrid search using **manual RRF** (because native RRF requires paid license)
- Streamlit UI with **year range** + **category multiselect** filters
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

### 6) Launch Streamlit UI
```powershell
.\venv\Scripts\streamlit.exe run .\src\app.py
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
- `src/ui/`: Streamlit UI implementation
- `src/evaluation/`: evaluation + benchmark scripts
- `src/utils/`: sanity checks and data helpers

Note: The files in `src/*.py` are mainly **entry-point wrappers** so older commands still work.

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

