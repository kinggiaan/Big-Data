# Checklist Báo Cáo - CO5135 Big Data (Group 11)

**Topic:** Building a Hybrid Search System for Academic Documents using Elasticsearch

---

## 1. Project Introduction (Deadline: 27/02/2026) -- DA HOAN THANH

- [x] Slide 1: Topic -- tieu de, ten nhom, MSSV
- [x] Slide 2: Data source -- arXiv (2.7M+ papers, 130 disciplines, Kaggle link)
- [x] Slide 3: Problems -- 3 van de (Keyword rigidity, AI misses terminology, Multidisciplinary noise)

---

## 2. MIDTERM REPORT (Deadline: 20/03/2026) -- HOAN THANH

> Format: Bao cao van ban (LaTeX)

### A. Bao cao Midterm -- DA HOAN THANH

- [x] Phan 1 - Gioi thieu: boi canh, han che, muc tieu, pham vi
- [x] Phan 2 - Dataset: nguon du lieu, quy mo, bang cau truc, quy trinh lam sach
- [x] Phan 3 - Van de va Giai phap: 3 problems + ES solutions
- [x] Phan 4 - Co so ly thuyet: IR pipeline, Inverted Index, BM25, text vs keyword, kNN, RRF (cong thuc)
- [x] Phan 5 - Kien truc: TikZ data flow diagram, Docker Compose, mapping code, Bulk strategy
- [x] Phan 6 - Hien trang: ket qua thuc te (JSON responses tu ES), code listings
- [x] Phan 7 - Roadmap: bang 4 Phase voi phan cong
- [x] Phan 8 - Ket luan: tom tat, danh gia kha thi, buoc tiep theo
- [x] References: 8 tai lieu tham khao phu hop (BM25, RRF, ES docs, Sentence-BERT, ...)

### B. Kiem tra ky thuat -- DA HOAN THANH

- [x] Docker + Elasticsearch 8.12 dang chay on dinh
- [x] Kibana truy cap duoc (localhost:5601)
- [x] 100k papers da duoc bulk index thanh cong (count = 100,000)
- [x] Script BM25 keyword search chay duoc, tra ket qua dung (73ms response time)
- [ ] Chup 3 screenshot (docker_containers, kibana_count, kibana_search) dan vao report

### C. Checklist cuoi cung truoc nop Midterm (19-20/03)

- [x] Bao cao da viet xong (LaTeX, 8 chapters)
- [x] Format nhat quan (font, heading, page numbers, header/footer)
- [ ] Co du screenshot/hinh minh hoa (dang chup)
- [ ] Cac thanh vien review cheo lan nhau
- [ ] Export PDF va backup

---

## 3. FINAL REPORT (Deadline: 15/05/2026)

> Chi tiet xem: docs/final_phase_plan.md

### A. Phase 2 - Vector & Hybrid Search + SCALE-UP (21/03 - 10/04) -- CHECKPOINTS

> Dataset: 2,982,054 total → 1,163,999 CS papers (4.8 GB raw)

- [ ] **24/03 - Embedding pipeline validated (100k):**
  - [ ] Cai sentence-transformers + torch
  - [ ] Viet embed_data.py (streaming JSONL, checkpoint 50k, model: all-MiniLM-L6-v2)
  - [ ] Chay embedding 100k tren local CPU -> validate pipeline
  - [ ] Test cosine similarity > 0.7 giua cau giong nghia
- [ ] **27/03 - Full data ready (1.16M):**
  - [ ] Viet data_prep_full.py: trich xuat toan bo 1,163,999 CS papers -> arxiv_cs_full.jsonl
  - [ ] Chay embedding 1.16M tren Kaggle GPU -> arxiv_cs_full_with_vectors.jsonl
- [ ] **31/03 - Full index on ES:**
  - [ ] Cap nhat docker-compose: ES heap 4GB
  - [ ] Viet index_data_v2.py: streaming JSONL, 5 shards, custom academic_english analyzer, dense_vector
  - [ ] Index 1.16M docs, verify _count = 1,163,999
- [ ] **03/04 - kNN search working:**
  - [ ] Viet vector_search.py, test kNN tren 1.16M docs
  - [ ] So sanh BM25 vs kNN tren cung queries
- [ ] **10/04 - Hybrid + Benchmark done:**
  - [ ] Viet hybrid_search.py (sub_searches + RRF)
  - [ ] Viet search_compare.py (3 mode canh nhau)
  - [ ] **Viet benchmark.py: scalability test 100k/500k/1M/1.16M**
  - [ ] Output: bang latency + bieu do matplotlib
  - [ ] Test 10 queries thu cong tren 1.16M

### B. Phase 3 - UI & Evaluation (11/04 - 30/04) -- CHECKPOINTS

- [ ] **20/04 - Streamlit UI done:**
  - [ ] Tao src/app.py voi Streamlit
  - [ ] O search + dropdown mode (Keyword/Vector/Hybrid) + filter year/category
  - [ ] Hien thi ket qua: title, authors, year, abstract, score
  - [ ] Sidebar thong ke: so ket qua, latency, category chart
- [ ] **30/04 - Evaluation done:**
  - [ ] Tao 30 test queries (10 exact term + 10 semantic + 10 mixed)
  - [ ] Manual relevance labeling: top-10 ket qua x 3 mode x 30 queries
  - [ ] Viet evaluate.py: tinh NDCG@10, MRR, Average Latency
  - [ ] So sanh default analyzer vs custom academic_english analyzer
  - [ ] Tao bang so sanh + bieu do (matplotlib/plotly)
  - [ ] Phan tich truong hop Hybrid thang/thua

### C. Phase 4 - Finalization (01/05 - 15/05) -- CHECKPOINTS

- [ ] **07/05 - Report & slides draft:**
  - [ ] Mo rong report LaTeX: them chapters Vector, Hybrid, **Scalability Analysis**
  - [ ] Them chapter: Scale-Up challenges (streaming, 5 shards, analyzer, benchmark)
  - [ ] Them hinh: Hybrid pipeline, evaluation charts, UI screenshots, **benchmark graphs**
  - [ ] Tao slide final (15-20 slides)
  - [ ] Review cheo giua cac thanh vien
- [ ] **15/05 - SUBMIT:**
  - [ ] Refactor code, docstrings, cau truc module
  - [ ] Viet README.md (setup -> index -> search -> UI)
  - [ ] Test end-to-end: clone repo moi -> chay pipeline hoan chinh
  - [ ] Finalize report + slides
  - [ ] Rehearsal: moi nguoi trinh bay phan minh
  - [ ] Nop: Slide + Report PDF + Source code

### D. Deliverables cuoi ky

- [ ] **Final Report** (PDF/LaTeX): ~30-40 trang, day du ly thuyet + evaluation
- [ ] **Final Slides** (PDF/PPTX): 15-20 slides
- [ ] **Source Code** (ZIP/GitHub): docker-compose + 10 Python scripts + README
- [ ] **Live Demo**: Streamlit UI, 3 search modes

---

## Phan cong (da cap nhat)

| Thanh vien | Phase 2 (21/03 - 10/04) | Phase 3 (11/04 - 30/04) | Phase 4 (01/05 - 15/05) |
|---|---|---|---|
| **Gia An** | Embedding, scale-up indexing, kNN, Hybrid RRF, benchmark.py | Streamlit UI, evaluate.py | Code refactor, README |
| **Son Lam** | Ho tro test, data_prep_full.py | Streamlit sidebar, 30 queries, manual labeling | Slide final, E2E test |
| **Thanh Huyen** | Ly thuyet Vector/kNN, Kaggle notebook | 30 queries, labeling, bieu do | Report final (incl. Scalability chapter) |
