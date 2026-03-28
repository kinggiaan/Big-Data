# BÁO CÁO GIỮA KỲ (MIDTERM REPORT)
**Môn học:** CO5135 - Big Data
**Đề tài:** Building a Hybrid Search System for Academic Documents using Elasticsearch
**Nhóm:** 11

**Thành viên:**
1. Dương Gia An - 2470293
2. Trịnh Sơn Lâm - 2470287
3. Nguyễn Thanh Huyền - 2570416

---

## Phần 1 - Giới thiệu (Introduction)

### 1.1. Bối cảnh vấn đề
Việc tìm kiếm tài liệu học thuật hiệu quả là một nhu cầu thiết yếu đối với sinh viên và các nhà nghiên cứu. Tuy nhiên, các hệ thống tìm kiếm truyền thống bộc lộ nhiều hạn chế khi phải xử lý khối lượng dữ liệu khổng lồ (Big Data). Người dùng thường gặp khó khăn trong việc tìm kiếm chính xác ngữ cảnh hoặc bị nhiễu thông tin bởi các từ khóa đa nghĩa.

### 1.2. Mục tiêu dự án
Dự án hướng tới việc xây dựng một hệ thống tìm kiếm lai (Hybrid Search) sử dụng Elasticsearch làm core engine. Hệ thống sẽ kết hợp cả tìm kiếm văn bản truyền thống (Keyword Search) và tìm kiếm vector (Vector Search) để mang lại kết quả chính xác nhất.

### 1.3. Phạm vi (Scope)
- **Dữ liệu:** Sử dụng bộ dữ liệu arXiv open-access archive.
- **Phạm vi Midterm:** Triển khai hạ tầng Elasticsearch, xử lý làm sạch dữ liệu và thực hiện thành công tìm kiếm từ khóa (BM25) trên tập con (subset) 100,000 bài báo thuộc lĩnh vực Computer Science.

---

## Phần 2 - Dataset (Dữ liệu)

### 2.1. Nguồn dữ liệu
Dự án sử dụng bộ dữ liệu arXiv từ Kaggle (https://www.kaggle.com/datasets/Cornell-University/arxiv), một kho lưu trữ mở chứa các bài báo học thuật.

### 2.2. Quy mô và Đặc điểm
- **Tổng số lượng:** Hơn 2.7 triệu bài báo.
- **Độ phủ:** Hơn 130 lĩnh vực (Computer Science, Physics, Mathematics,...).
- **Cấu trúc dữ liệu khai thác:**
  - `Title` & `Abstract`: Lưu trữ dưới dạng văn bản thuần (plain text) cho Midterm, và sẽ được chuyển đổi thêm thành dense vectors cho Final.
  - `Metadata`: `Publication Year` và `Category` được sử dụng để xây dựng các bộ lọc (filters) nghiêm ngặt.

### 2.3. Quy trình làm sạch dữ liệu (Data Cleaning)
*(Trình bày các bước đã làm: loại bỏ các dòng thiếu Title/Abstract, lọc riêng các bài báo thuộc danh mục Computer Science để tạo tập subset 100k dòng, xuất ra định dạng JSON chuẩn bị cho bulk indexing).*

---

## Phần 3 - Vấn đề và Giải pháp (Problems & Proposed Solutions)

### 3.1. Problem 1: Sự cứng nhắc của tìm kiếm từ khóa (The Rigidity of Keyword Search)
- **Vấn đề:** Người dùng phải gõ chính xác từ khóa. Các từ đồng nghĩa (synonyms) hoặc cách diễn đạt khác (rephrasing) sẽ trả về 0 kết quả.
- **Giải pháp Elasticsearch:** Cung cấp khả năng Vector Search (kNN) để hiểu "ngữ nghĩa ngữ cảnh" của câu truy vấn thay vì chỉ khớp từng từ.

### 3.2. Problem 2: AI bỏ sót các thuật ngữ chuyên ngành (AI Misses Specialized Terminology)
- **Vấn đề:** AI hiểu ngữ cảnh tốt nhưng lại kém trong việc tìm kiếm chính xác tên tác giả hoặc các từ viết tắt hiếm gặp.
- **Giải pháp Elasticsearch:** Chạy song song cả hai luồng (Hybrid Search) và tích hợp sẵn thuật toán Reciprocal Rank Fusion (RRF) để tự động tính điểm và gộp kết quả từ AI và Keyword với độ chính xác cao.

### 3.3. Problem 3: Nhiễu tìm kiếm đa ngành (Search Skewed by Multidisciplinary Noise)
- **Vấn đề:** Một từ khóa có thể có nhiều nghĩa. Việc áp dụng các bộ lọc cứng (năm, danh mục) vào hệ thống AI thường làm phá vỡ cấu trúc tìm kiếm, gây thiếu sót kết quả hoặc độ trễ cao.
- **Giải pháp Elasticsearch:** Tính năng Automatic Optimization filtering giúp tự động chuyển đổi giữa các thuật toán quét (scanning algorithms) dựa trên độ nghiêm ngặt của bộ lọc, đảm bảo phản hồi nhanh và chính xác.

---

## Phần 4 - Cơ sở lý thuyết (Theoretical Background)

### 4.1. Information Retrieval Pipeline
Một hệ thống tìm kiếm cơ bản bao gồm 3 giai đoạn: Ingestion (Thu thập và làm sạch) -> Indexing (Lập chỉ mục) -> Query Processing (Xử lý truy vấn).

### 4.2. Inverted Index và Thuật toán BM25
- **Inverted Index:** Cấu trúc dữ liệu cốt lõi giúp Elasticsearch tìm kiếm văn bản cực nhanh bằng cách ánh xạ từ khóa ngược lại các documents chứa nó.
- **BM25 (Best Matching 25):** Là thuật toán chấm điểm (scoring) dựa trên TF-IDF cải tiến.
  - **TF (Term Frequency):** Tần suất xuất hiện của từ khóa trong tài liệu.
  - **IDF (Inverse Document Frequency):** Độ hiếm của từ khóa trên toàn bộ tập dữ liệu.

### 4.3. Vector Embedding và kNN (Định hướng Final)
*(Giới thiệu ngắn gọn về việc dùng AI model để biến văn bản thành vector số thực, và dùng thuật toán k-Nearest Neighbors để tìm các văn bản có ý nghĩa tương đồng).*

### 4.4. Reciprocal Rank Fusion - RRF (Định hướng Final)
*(Giới thiệu ngắn gọn thuật toán RRF giúp kết hợp thứ hạng của BM25 và kNN).*

---

## Phần 5 - Kiến trúc hệ thống (System Architecture)

### 5.1. Sơ đồ luồng dữ liệu (Data Flow)
`Raw JSON (arXiv)` -> `Python Cleaning Script` -> `Clean JSON (100k subset)` -> `Elasticsearch Bulk API` -> `Elasticsearch Index` -> `Query Processing` -> `Results`.

### 5.2. Kiến trúc Elasticsearch
- **Công nghệ:** Python, Elasticsearch 8.x, Docker, Kibana.
- **Mô hình triển khai:** Single-node cluster chạy trên Docker.
- **Thành phần:** Node, Cluster, Shard, Replica (Giải thích ngắn gọn lý do ES phù hợp với Big Data nhờ khả năng phân tán - distributed).

### 5.3. Index Mapping & Bulk Strategy
- **Mapping hiện tại:** Các trường `title`, `abstract` được map dạng `text`. Các trường `year`, `category` map dạng `keyword` để filter.
- **Bulk Indexing:** Sử dụng hàm `helpers.bulk()` của thư viện `elasticsearch-py` để đẩy dữ liệu theo từng batch (ví dụ: 5000 docs/lần) nhằm tối ưu RAM và thời gian.

---

## Phần 6 - Hiện trạng triển khai (Current Progress)

### 6.1. Các hạng mục đã hoàn thành
- [x] Thiết lập thành công môi trường Docker với Elasticsearch 8.x và Kibana.
- [x] Tiền xử lý dữ liệu: Trích xuất thành công 100,000 bài báo lĩnh vực Computer Science.
- [x] Indexing: Đẩy thành công 100k documents vào Elasticsearch.
- [x] Truy vấn: Thực hiện thành công các câu lệnh tìm kiếm BM25 cơ bản và có sử dụng filter (Year/Category).

*(Chèn các hình ảnh screenshot minh chứng vào đây: Hình Docker đang chạy, Hình Kibana Dashboard, Hình kết quả JSON trả về khi query).*

### 6.2. Các hạng mục chưa thực hiện (Dành cho Final)
- Chuyển đổi dữ liệu sang Vector (Embedding).
- Cấu hình kNN Search và Hybrid Search (RRF).
- Xây dựng giao diện người dùng (Streamlit UI).
- Đánh giá mô hình bằng các metrics khoa học (NDCG, MRR).

---

## Phần 7 - Kế hoạch triển khai (Roadmap)

| Giai đoạn | Thời gian | Công việc chính | Người phụ trách |
|---|---|---|---|
| **Phase 1 (Midterm)** | 06/03 - 20/03 | Data cleaning, Docker ES setup, BM25 Indexing & Search | Cả nhóm |
| **Phase 2** | 21/03 - 15/04 | Vector Embeddings, kNN Search, Hybrid RRF | Gia An |
| **Phase 3** | 16/04 - 05/05 | Thiết kế Streamlit UI, Đánh giá mô hình (NDCG/MRR) | Sơn Lâm, Thanh Huyền |
| **Phase 4 (Final)** | 06/05 - 15/05 | Viết báo cáo Final, làm Slide, dọn dẹp Source code | Cả nhóm |

---

## Phần 8 - Kết luận tạm thời

### 8.1. Đánh giá tính khả thi
Dự án hiện tại đang bám sát tiến độ. Việc thu hẹp phạm vi xuống 100,000 bài báo cho giai đoạn Midterm giúp nhóm kiểm soát tốt tài nguyên phần cứng (RAM/CPU) khi chạy Elasticsearch trên Docker cục bộ, đồng thời vẫn thể hiện được tư duy xử lý Big Data thông qua Bulk API.

### 8.2. Bước tiếp theo
Ngay sau khi báo cáo giữa kỳ, nhóm sẽ tiến hành nghiên cứu thư viện `SentenceTransformers` để bắt đầu quá trình tạo Vector Embeddings cho tập dữ liệu 100k bài báo này, chuẩn bị cho tính năng cốt lõi là Vector Search.