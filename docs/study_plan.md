# Lộ Trình Học Tập Song Song Dự Án Big Data

Kế hoạch này giúp bạn vừa học vừa làm. Vì bạn đang thiếu các kiến thức nền tảng (Base) về Big Data và Search Engine, chúng ta sẽ bắt đầu bằng 1 Giai đoạn "Lý thuyết nền" trước khi đụng vào code.

## Giai đoạn 0: Kiến thức Nền tảng (Foundation Theory) - Rất Quan Trọng
*Mục tiêu: Trả lời được các câu hỏi lý thuyết cốt lõi nếu thầy giáo chất vấn bảo vệ đồ án.*

### 1. Kiến thức nền về Information Retrieval (IR - Truy xuất thông tin)
* **Search Engine là gì?** Cấu tạo cơ bản của 1 công cụ tìm kiếm gồm 3 phần: *Ingestion* (Thu thập data) -> *Indexer* (Lập chỉ mục, phân loại data) -> *Query Processor* (Nhận câu lệnh của User và map vào Index để trả kết quả).
* **Bài toán Match:** Tại sao gõ "Học máy" lại tìm ra "Machine Learning"? (Hiểu khái niệm Tokenization, Stop words, Lemmatization / Stemming).
* **Thuật toán BM25 (TF-IDF cải tiến):** Học cách máy tính chấm điểm (Scoring) một bài báo văn bản thuần túy dưạ vào **tần suất xuất hiện của từ khóa** (Term Frequency) và **độ hiếm của từ khóa đó trong toàn bộ thư viện** (Inverse Document Frequency).

### 2. Kiến thức nền về "Big Data" trong dự án này
* **Tại sao bài toán này là Big Data?**
  * **Volume (Khối lượng):** 2.7 triệu bài báo (Text file vài GBs). Khi chuyển sang Dense Vectors (mỗi bài báo cõng thêm 1 mảng 384 hoặc 768 số thực), dung lượng bộ nhớ (RAM) và ổ cứng đòi hỏi sẽ phình to ra gấp 10-20 lần.
  * **Velocity (Tốc độ):** Đòi hỏi query trả về kết quả RRF (vừa Text vừa Vector) dưới mili-giây trên hàng triệu document.
* **Tư duy Distributed (Phân tán):** Máy tính bàn 16GB RAM của bạn không thể gánh 1 cục database khổng lồ. Cách giải quyết: Chia nhỏ database đó thành nhiều mảnh (Sharding) và xử lý/tìm kiếm song song trên các mảnh đó rồi gộp kết quả lại.

---

## Giai đoạn 1: Infrastructure & Big Data Processing (Tuần 1: 06/03 - 13/03)
*Mục tiêu: Đưa lý thuyết Giai đoạn 0 vào thực hành, xây dựng pipeline để xử lý dữ liệu khổng lồ.*

### 1. Data Engineering với PySpark / Dask (1-2 ngày)
* **Tại sao không dùng Pandas?** Pandas nạp toàn bộ data vào RAM. Với 3+ GB JSON, máy bạn có thể treo.
* **Học gì?** Cách dùng PySpark (hoặc Dask) để đọc file lớn, filter cột, và ghi ra định dạng **Parquet** (định dạng nén dữ liệu cực tốt cho Big Data).
* **Khái niệm Chunking:** Chia file 3GB thành 30 file 100MB để xử lý dần dần.

### 2. Elasticsearch Architecture & Bulk API (2-3 ngày)
* **Kiến trúc ES:** Nắm khái niệm **Node, Cluster, Shard, và Replica**. Hiểu tại sao Elasticsearch lại nhanh (Inverted Index).
* **Elasticsearch Bulk API:** KHÔNG dùng vòng lặp `for` để `POST` từng dòng. Học cách dùng hàm `helpers.bulk()` trong thư viện Python `elasticsearch` để nhét 5,000 document vào ES chỉ mất 1 giây.
* **Thực hành:** Hoàn thành toàn bộ **Phase 1** trong `task.md`. Cài Docker, viết script nạp 300k vectors vào ES ngay tuần này.

---

## Giai đoạn 2: Vector & Hybrid Search (Sau Midterm - Tháng 4)
*Mục tiêu: Hiểu "Vector" là gì và cách ES kết hợp AI vào tìm kiếm.*

### 1. AI & Vector Embeddings (2-3 ngày)
* **Embedding là gì?** Hiểu cách AI biến 1 đoạn văn (Text) thành 1 mảng các con số (Vector/Array). Các đoạn văn có ý nghĩa *giống nhau* sẽ có mảng số *gần giống nhau*.
* **HuggingFace & SentenceTransformers:** Thử nghiệm thư viện này bằng Python. Gõ `model.encode("hello world")` xem vector nó ra hình thù gì.
* **Thực hành:** Làm **Task 2.1**. Chuyển vài chục ngàn bài Abstract thành file Parquet chứa Vector.

### 2. Vector Search (kNN) trong ES (2-3 ngày)
* **kNN (k-Nearest Neighbors) là gì?** Thuật toán tìm các vector "gần" nhau nhất trong không gian (đo đạc bằng tính toán Cosine Similarity/Dot Product).
* **Áp dụng vào ES:** Học cách định nghĩa field type là `dense_vector` trong Mapping của ES.
* **Thực hành:** Làm **Task 2.2**. Đẩy file Parquet có chứa Vector vào ES và chạy câu lệnh `_search` dùng thuật toán `knn`.

### 3. Đỉnh cao: Hybrid Search & RRF (1-2 ngày)
* **Tại sao cần Hybrid?** BM25 tìm từ khóa y hệt rất tốt (VD: mã lỗi "ERR_404"). kNN tìm ý tưởng giống nhau rất tốt (VD: "bài báo về AI" -> "Machine Learning Paper"). Kết hợp 2 cái lại gọi là Hybrid.
* **RRF (Reciprocal Rank Fusion) là gì?** Thuật toán xếp hạng (Ranking) có sẵn trong ES 8.x. Nó lấy Top 10 của BM25 kết hợp với Top 10 của kNN để đưa ra Top 10 kết quả chuẩn xác nhất cuối cùng.
* **Thực hành:** Làm **Task 2.3**. Lắp ghép 2 câu Query lại với nhau thông qua API Retriever.

---

## Giai đoạn 3: UI và Kỹ thuật Đánh giá Khoa học (Tháng 5)
*Mục tiêu: Đóng gói thành sản phẩm và chứng minh hệ thống tốt bằng toán học.*

### 1. Build UI tốc độ cao (1 ngày)
* **Làm quen Streamlit:** Học cách tạo giao diện Web bằng Python siêu nhanh để demo sản phẩm.
* **Thực hành:** Làm **Task 3.1**.

### 2. Kỹ thuật Đánh giá (Information Retrieval Metrics) (2 ngày)
Bỏ qua các cách test "nhìn bằng mắt". Là sinh viên CS, bạn cần dùng Metric chuẩn:
* **NDCG (Normalized Discounted Cumulative Gain):** Dùng để đánh giá thứ hạng. Kết quả đúng nằm ở Top 1 sẽ được điểm cao hơn nằm ở Top 5.
* **MRR (Mean Reciprocal Rank):** Đánh giá xem kết quả đúng *đầu tiên* xuất hiện sớm cỡ nào.
* **Thực hành:** Dùng thư viện `scikit-learn` (hoặc tự code hàm) để tính NDCG/MRR. Cung cấp số liệu này để Support team vẽ biểu đồ báo cáo cuối kỳ.

## 💡 Lời Khuyên Tuyệt Đối:
> **TUẦN ĐẦU TIÊN LÀ TUẦN QUYẾT ĐỊNH.** Đừng trì hoãn việc setup Elasticsearch và chạy Embedding. Hãy làm phần khó nhất trước, phần làm mượt giao diện (UI) để sát deadline làm cũng được.
