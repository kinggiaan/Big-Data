# Project Plan: Academic Document Hybrid Search with Elasticsearch

**Timeline:**
*   **Start Date:** March 6, 2026
*   **Midterm Report Deadline:** March 20, 2026 (2 weeks)
*   **Final Report Deadline:** May 15, 2026 (~2.5 months)

**Team Structure:**
*   **Lead Developer (You):** Core architecture, Elasticsearch setup, Python backend, algorithms.
*   **Support Members (2):** Data cleaning, documentation, testing, presentation slides.

---

## Phase P (Parallel): Reporting & Documentation Track (Continuous)
*Goal: 2 Support Members handle all documentation & slides in parallel with the Lead's coding.*

### P.1 Midterm Documentation (March 6 - March 20)
- [ ] **Task P.1.1:** Research & write the introductory sections (Problem context, why Hybrid Search, Dataset overview).
- [ ] **Task P.1.2:** Draft the Midterm Report detailing the proposed architecture (based on the Lead's Docker setup).
- [ ] **Task P.1.3:** Create presentation slides illustrating the Data Flow and Elasticsearch architecture.
- [ ] **Task P.1.4:** Record a quick screen-capture demo of the working keyword search (after Task 1.3 is done).

### P.2 Final Documentation (March 21 - May 15)
- [ ] **Task P.2.1:** Viết phần lý thuyết bổ sung: Vector Embedding chi tiết, kNN algorithm, RRF formula.
- [ ] **Task P.2.2:** Viết phần Evaluation Methodology: bộ 30 queries, labeling rubric, NDCG/MRR giải thích.
- [ ] **Task P.2.3:** Viết phần Kết quả & Thảo luận: bảng số liệu, biểu đồ, phân tích Hybrid vs Keyword vs Vector.
- [ ] **Task P.2.4:** Tạo Final Slides (15-20 slides): kiến trúc + demo + evaluation.
- [ ] **Task P.2.5:** Submit all deliverables (Source code, Slide, Final Report) by May 15.

---

## Phase 1: Foundation & Midterm Preparation (March 6 - March 20) ✅ COMPLETED
*Goal: Have a working keyword search demo and high-level architecture ready for the Midterm Report.*

### 1.1 Data Preparation (Support Team + Lead)
- [x] **Task 1.1.1:** Download the arXiv dataset from Kaggle. → `data/arxiv-metadata-oai-snapshot.json` (3GB+)
- [x] **Task 1.1.2:** Write Python script to extract 100,000 CS papers. → `src/data_prep.py` (streaming, line-by-line)
- [x] **Task 1.1.3:** Clean data and export JSON. → `data/arxiv_cs_100k_clean.json` (~350MB)

### 1.2 Elasticsearch Environment Setup (Lead)
- [x] **Task 1.2.1:** Docker Desktop installed.
- [x] **Task 1.2.2:** `docker-compose.yml` created (ES 8.12.2 + Kibana 8.12.2, single-node, 2GB heap).
- [x] **Task 1.2.3:** ES verified via Kibana Dev Tools + Python script.

### 1.3 Baseline Search Implementation (Lead)
- [x] **Task 1.3.1:** Index mapping created (text + keyword fields). → `src/index_data.py`
- [x] **Task 1.3.2:** 100k papers bulk indexed (batch 5,000, ~30 seconds). → count = 100,000
- [x] **Task 1.3.3:** BM25 keyword search working with year filter. → `src/search.py`

---

## Phase 2: Vector & Hybrid Search + Scale-Up (March 21 - April 10)
*Goal: Scale to full 1.16M CS papers, implement Vector + Hybrid Search, run scalability benchmark.*
*Dataset: 2,982,054 total papers → 1,163,999 CS papers (4.8GB raw file)*

### 2.1 Vector Embeddings (Lead) — Deadline: 27/03
- [ ] **Task 2.1.1:** Install `sentence-transformers` + `torch`. Update requirements.txt.
- [ ] **Task 2.1.2:** Write `src/embed_data.py`: **streaming JSONL** read/write, checkpoint every 50k, batch 512 (GPU) / 64 (CPU).
- [ ] **Task 2.1.3:** Validate on 100k first (local CPU, ~15-30 min). → `data/arxiv_cs_100k_with_vectors.jsonl`
- [ ] **Task 2.1.4:** Sanity check: cosine similarity between similar sentences > 0.7.
- [ ] **Task 2.1.5:** Write `src/data_prep_full.py`: extract all 1,163,999 CS papers → `data/arxiv_cs_full.jsonl` (~1.3GB).
- [ ] **Task 2.1.6:** Run full 1.16M embedding on **Kaggle notebook** (free GPU T4, ~30-45 min). → `data/arxiv_cs_full_with_vectors.jsonl`

### 2.2 Scale-Up Indexing + kNN Search (Lead) — Deadline: 03/04
- [ ] **Task 2.2.1:** Update `docker-compose.yml`: ES heap 4GB (`-Xms4g -Xmx4g`).
- [ ] **Task 2.2.2:** Write `src/index_data_v2.py`: **streaming JSONL** bulk indexer, 5 shards, custom `academic_english` analyzer, `dense_vector` field.
    - *CRITICAL: Must NOT use `json.load()` — streaming line-by-line only.*
- [ ] **Task 2.2.3:** Index 100k first to validate, then full 1.16M (~15-30 min). Verify `_count` = 1,163,999.
- [ ] **Task 2.2.4:** Write `src/vector_search.py`: kNN query implementation.
- [ ] **Task 2.2.5:** Quick comparison: BM25 vs kNN on same queries over 1.16M docs.

### 2.3 Hybrid Search + Scalability Benchmark (Lead) — Deadline: 10/04
- [ ] **Task 2.3.1:** Write `src/hybrid_search.py`: ES `sub_searches` + `rank: { rrf: {} }`.
- [ ] **Task 2.3.2:** Write `src/search_compare.py`: 3-mode side-by-side comparison.
- [ ] **Task 2.3.3:** Write `src/benchmark.py`: **scalability experiment** at 4 scales (100k/500k/1M/1.16M).
    - Measure: indexing time, index size, BM25/kNN/Hybrid latency P50/P95, heap usage.
    - Output: `data/benchmark_results.json` + matplotlib charts.
- [ ] **Task 2.3.4:** Manual test 10 queries on full 1.16M dataset, document Hybrid win/lose cases.

---

## Phase 3: Application Interface & Evaluation (April 11 - April 30)
*Goal: Build a user-friendly interface and prove Hybrid Search effectiveness with metrics.*

### 3.1 Streamlit UI (Lead + Support) — Deadline: 20/04
- [ ] **Task 3.1.1:** Install `streamlit`, create `src/app.py` with basic layout.
- [ ] **Task 3.1.2:** Search input + dropdown mode (Keyword/Vector/Hybrid) + filter year/category.
- [ ] **Task 3.1.3:** Result cards: title, authors, year, abstract snippet, relevance score, highlight.
- [ ] **Task 3.1.4:** Sidebar stats: total results, latency (ms), category distribution chart.

### 3.2 Evaluation & Testing (Entire Team) — Deadline: 30/04
- [ ] **Task 3.2.1:** Create 30 test queries: 10 exact-term, 10 semantic/rephrase, 10 mixed. → `data/test_queries.json`
- [ ] **Task 3.2.2:** Manual relevance labeling: top-10 results × 3 modes × 30 queries. → `data/ground_truth.json`
- [ ] **Task 3.2.3:** Write `src/evaluate.py`: compute NDCG@10, MRR, Average Latency per mode.
- [ ] **Task 3.2.4:** Compare default analyzer vs custom `academic_english` analyzer results.
- [ ] **Task 3.2.5:** Generate comparison tables + charts (matplotlib/plotly) for the report.
- [ ] **Task 3.2.6:** Analyze: when does Hybrid win/lose? Why?

---

## Phase 4: Finalization (May 1 - May 15)
*Goal: Polish everything and prepare for final submission. Extended to 15 days for buffer.*

### 4.1 Report & Slides (Support Team) — Deadline: 07/05
- [ ] **Task 4.1.1:** Expand LaTeX report: add chapters Vector Embedding, Hybrid Search, **Scalability Analysis**.
- [ ] **Task 4.1.2:** Add chapter: Scale-Up challenges (streaming, 5 shards, custom analyzer, benchmark results).
- [ ] **Task 4.1.3:** Add figures: Hybrid pipeline, evaluation charts, UI screenshots, **benchmark graphs**.
- [ ] **Task 4.1.4:** Create final slides (15-20 slides).
- [ ] **Task 4.1.5:** Cross-review: each member reads others' sections.

### 4.2 Code Cleanup & Packaging (Lead) — Deadline: 12/05
- [ ] **Task 4.2.1:** Refactor Python scripts: clear module structure, docstrings.
- [ ] **Task 4.2.2:** Write `README.md`: full setup guide (Docker → index → search → UI).
- [ ] **Task 4.2.3:** End-to-end test: fresh clone → run entire pipeline successfully.

### 4.3 Final Submission (Entire Team) — Deadline: 15/05
- [ ] **Task 4.3.1:** Finalize report + slides (last edits).
- [ ] **Task 4.3.2:** Rehearsal: each member presents their part (15 min total).
- [ ] **Task 4.3.3:** Submit: Slide PDF + Report PDF + Source code (ZIP/GitHub).
