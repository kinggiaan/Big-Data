# KỊCH BẢN TRÌNH BÀY CHI TIẾT (SPEAKER NOTES)
## HỆ THỐNG TÌM KIẾM KẾT HỢP TÀI LIỆU HỌC THUẬT (HYBRID SEARCH FOR ACADEMIC DOCUMENTS)

- **Tổng thời lượng dự kiến:** 20 - 25 phút
- **Phân chia người trình bày (Speaker Blocks):**
  1. **Nguyễn Thanh Huyền (Huyền):** Slide 1 đến Slide 12 (~11 phút) — Phần mở đầu, Bối cảnh, Bài toán, Mục tiêu, Dữ liệu & Cơ sở lý thuyết.
  2. **Trịnh Sơn Lam (Lam):** Slide 13 đến Slide 18 (~6 phút) — Kiến trúc hệ thống & GPU Embedding Pipeline.
  3. **Dương Gia An (An):** Slide 19 đến Slide 39 (~12-14 phút) — Chi tiết Triển khai tìm kiếm, Đánh giá chất lượng, Benchmarking hiệu năng, Demo, Kết luận & Q&A.

---

## PHẦN 1: MỞ ĐẦU, BỐI CẢNH & CƠ SỞ LÝ THUYẾT (Slide 1 - 12)
**Người trình bày: Nguyễn Thanh Huyền (Huyền)**

### Slide 1: Trang tiêu đề (0.5 phút) — Người trình bày: Huyền
> "Kính chào thầy Thoại Nam và các bạn. Em là Thanh Huyền, đại diện cho Nhóm 11. Hôm nay nhóm chúng em xin phép được báo cáo đề tài cuối kỳ môn Big Data: **'Building a Hybrid Search System for Academic Documents using Elasticsearch'** - Xây dựng Hệ thống Tìm kiếm Kết hợp cho Tài liệu Học thuật sử dụng Elasticsearch. Đề tài được thực hiện dưới sự hướng dẫn của PGS.TS Thoại Nam trong học kỳ 252 này."

**Visual Cues (Gợi ý trình chiếu):**
* Chào hội đồng và các bạn với phong thái tự tin, chuyên nghiệp.
* Hướng tay về phía màn hình chiếu có Logo trường Đại học Bách khoa TP.HCM và tên đề tài.

---

### Slide 2: Phân công công việc (0.5 phút) — Người trình bày: Huyền
> "Trước khi đi vào chi tiết, em xin giới thiệu sơ lược về đóng góp của các thành viên trong nhóm. Chúng em phân chia công việc đồng đều với tỷ lệ đóng góp là 33.33% cho mỗi thành viên:
> - Bạn **Dương Gia An** phụ trách thiết kế Kiến trúc hệ thống, Elasticsearch Indexing, thiết lập Search Pipeline và thực hiện Evaluation & Benchmarking.
> - Bạn **Trịnh Sơn Lam** đảm nhận phần Data Preprocessing, thiết kế GPU Embedding Pipeline và dán nhãn Ground Truth.
> - Em, **Nguyễn Thanh Huyền**, chịu trách nhiệm nghiên cứu Cơ sở lý thuyết, phân tích kết quả đánh giá chất lượng và tổng hợp báo cáo final."

**Visual Cues (Gợi ý trình chiếu):**
* Chỉ vào bảng phân công công việc trên slide để chứng minh sự phân bổ đồng đều về khối lượng công việc.

---

### Slide 3: Nội dung trình bày (0.5 phút) — Người trình bày: Huyền
> "Nội dung thuyết trình hôm nay được chia thành 8 phần chính tương ứng với cấu trúc báo cáo của nhóm:
> - Đầu tiên, em sẽ trình bày phần **Giới thiệu** bài toán và **Cơ sở lý thuyết**.
> - Tiếp theo, bạn **Sơn Lam** sẽ đi sâu vào phần **Kiến trúc hệ thống** và **Embedding Pipeline**.
> - Cuối cùng, bạn **Gia An** sẽ trình bày về **Search Implementation**, **Đánh giá chất lượng**, **Benchmarking hiệu năng**, tiến hành **Demo hệ thống** và rút ra **Kết luận** cùng phần **Q&A**."

**Visual Cues (Gợi ý trình chiếu):**
* Lướt nhanh qua hai cột mục lục trên slide để người nghe hình dung rõ lộ trình buổi thuyết trình.

---

### Slide 4: Bối cảnh và Động lực (1 phút) — Người trình bày: Huyền
> "Đi vào phần bối cảnh, như thầy và các bạn đã biết, thế giới số ngày nay tạo ra một khối lượng khổng lồ dữ liệu mỗi ngày, ước tính khoảng **2.5 quintillion bytes**. Trong đó, phần lớn là dữ liệu phi cấu trúc như văn bản học thuật. Hiện nay, các kho lưu trữ bài báo khoa học vô cùng đồ sộ: **arXiv** có hơn 2.4 triệu bài báo, **Google Scholar** có 380 triệu và **PubMed** có hơn 36 triệu bài báo.
> Việc khai thác thông tin từ các kho học thuật này gặp thách thức rất lớn do sự tiến hóa của công nghệ tìm kiếm qua ba thế hệ:
> 1. Thế hệ thứ nhất là **Lexical Search (Keyword Search)** xuất hiện từ những năm 1970, chỉ thực hiện đối khớp từ khóa chính xác nên dễ bỏ sót từ đồng nghĩa.
> 2. Thế hệ thứ hai là **Semantic Search (Tìm kiếm ngữ nghĩa)** bùng nổ từ năm 2018 nhờ các mô hình học sâu, hiểu được ngữ cảnh nhưng lại mất độ chính xác đối với các thuật ngữ chuyên ngành viết tắt hoặc công thức toán học.
> 3. Từ đó dẫn đến sự ra đời của thế hệ thứ ba - **Hybrid Search** từ năm 2022 trở lại đây, kết hợp song song cả hai thế giới."

**Visual Cues (Gợi ý trình chiếu):**
* Trỏ vào các con số thống kê quy mô dữ liệu để nhấn mạnh yếu tố Big Data.
* Chỉ vào sơ đồ ba thế hệ tìm kiếm ở cột bên phải để làm nổi bật sự dịch chuyển công nghệ.

---

### Slide 5: Bài toán nghiên cứu (1 phút) — Người trình bày: Huyền
> "Từ thực tế đó, nhóm xác định bài toán nghiên cứu cốt lõi: Cho một câu truy vấn $q$, hệ thống cần tìm kiếm và xếp hạng các tài liệu liên quan từ kho dữ liệu hơn **1.2 triệu bài báo khoa học** thuộc lĩnh vực Computer Science trên arXiv. Hệ thống phải kết hợp song song luồng **Keyword search (BM25)** giúp khớp từ vựng chính xác và luồng **Semantic search (Dense Vectors)** giúp hiểu ngữ nghĩa sâu sắc, sau đó tích hợp kết quả bằng thuật toán **RRF**.
> Hãy nhìn vào ví dụ cụ thể trên slide để thấy rõ tại sao các phương thức đơn lẻ thất bại:
> - Đối với Keyword Search, khi gõ truy vấn *'methods to detect fake images'*, nó sẽ hoàn toàn bỏ qua bài báo chứa từ khóa *'deepfake detection'* vì không có từ khóa nào khớp chính xác.
> - Ngược lại đối với Semantic Search, khi gõ thuật ngữ đặc thù *'ViT-B/16 fine-tuning'*, mô hình nhúng chỉ hiểu chung chung đây là một *'vision model'* và trả về các bài báo Vision tổng quát, đánh mất hoàn toàn tính chính xác tuyệt đối."

**Visual Cues (Gợi ý trình chiếu):**
* Nhấn mạnh định nghĩa bài toán (Problem Statement) đóng khung ở phía trên.
* Chỉ vào hai ví dụ minh họa thất bại (Keyword Search vs Semantic Search) để người nghe cảm nhận rõ tính thực tế của bài toán.

---

### Slide 6: Mục tiêu dự án (1 phút) — Người trình bày: Huyền
> "Để giải quyết triệt để bài toán trên, dự án của nhóm đặt ra 5 mục tiêu kỹ thuật cụ thể:
> 1. Xây dựng một **Hệ thống Hybrid Search** kết hợp BM25 và kNN Vector Search trên nền tảng Elasticsearch phiên bản 8.12.
> 2. Thiết kế một **GPU Embedding Pipeline** có hiệu năng cao, nhúng thành công hơn 1.2 triệu tài liệu mà không bị lỗi Out of Memory.
> 3. Triển khai kiến trúc **Microservice** với giải pháp **Dual-Index** trên môi trường Docker container.
> 4. Tiến hành đánh giá chất lượng hệ thống một cách khoa học bằng các độ đo chuẩn là **NDCG@10** và **MRR@10** trên tập 30 câu truy vấn mẫu.
> 5. Phát triển hoàn chỉnh một **Web Application** chạy thực tế với giao diện React và Backend FastAPI."

**Visual Cues (Gợi ý trình chiếu):**
* Chỉ vào từng mục tiêu trên slide.
* Đọc to các từ khóa công nghệ chính: Elasticsearch 8.12, GPU Pipeline, Dual-Index, NDCG@10, MRR@10, Web App.

---

### Slide 7: Dataset — arXiv Paper Abstracts (1 phút) — Người trình bày: Huyền
> "Về dữ liệu thử nghiệm, nhóm sử dụng **arXiv Dataset** được Cornell University công bố trên Kaggle với quy mô ban đầu hơn 2.7 triệu bài báo khoa học dạng raw JSON nặng khoảng 4.8 GB. Nhóm đã thực hiện quy trình streaming lọc lấy các bài báo thuộc lĩnh vực Computer Science (các subcategories có tiền tố cs.*).
> Kết quả thu được tập dữ liệu sạch gồm **1,203,108** bài báo khoa học. Thống kê mô tả cho thấy tập dữ liệu này bao gồm 40 subcategories, trải dài từ năm 1993 đến năm 2024. Độ dài tiêu đề trung bình khoảng 10 từ và Abstract trung bình khoảng 150 từ. Quy trình xử lý dữ liệu được thiết kế tối ưu để tránh OOM bằng cách đọc luồng trực tiếp từ file nén."

**Visual Cues (Gợi ý trình chiếu):**
* Chỉ vào bảng thống kê mô tả (Descriptive Statistics) ở cột bên phải.
* Trình bày quy trình làm sạch dữ liệu ở góc trái dưới: Streaming -> Lọc cs.* -> Loại JSON lỗi -> Trích xuất năm -> Xuất JSONL.

---

### Slide 8: Cấu trúc dữ liệu — 6 Fields (1 phút) — Người trình bày: Huyền
> "Dữ liệu sạch được tổ chức cấu trúc hóa thành 6 trường thông tin chính để đẩy vào Elasticsearch:
> - Trường `id` định danh bài báo được map kiểu `keyword` để tìm kiếm chính xác.
> - Trường `title` và `abstract` được map kiểu `text` để xây dựng **Inverted Index**, hỗ trợ phân tích từ tố (tokenization, lowercase, stop-word removal) phục vụ tìm kiếm BM25. Tiêu đề được gán hệ số boost gấp 2 lần.
> - Trường `categories` và `year` map kiểu `keyword` phục vụ việc lọc dữ liệu (filtering) và gom cụm phân tích (aggregations) với cấu trúc **Doc Values** tối ưu tốc độ.
> - Trường `authors` lưu tên các tác giả kiểu `text`.
> - Việc phân biệt rõ ràng kiểu dữ liệu `text` và `keyword` giúp Elasticsearch tối ưu hóa vùng nhớ RAM và đĩa cứng một cách tối đa."

**Visual Cues (Gợi ý trình chiếu):**
* Trỏ vào bảng Data Schema để giải thích vai trò của từng trường dữ liệu.
* Giải thích nhanh sự khác biệt giữa cấu trúc Inverted Index (cho kiểu text) và Doc Values (cho kiểu keyword) ở phía dưới slide.

---

### Slide 9: Elasticsearch và Inverted Index (1 phút) — Người trình bày: Huyền
> "Chuyển sang Chương 4 về Cơ sở lý thuyết. Công cụ tìm kiếm cốt lõi của hệ thống là **Elasticsearch**, một bộ máy tìm kiếm phân tán xây dựng trên Apache Lucene, hỗ trợ cả tìm kiếm văn bản thông thường lẫn kNN vector search.
> Trái tim của tìm kiếm văn bản truyền thống là cấu trúc **Inverted Index (Chỉ mục đảo ngược)**. Hãy quan sát bảng so sánh trên slide: thay vì dùng Forward Index quét tuần tự độ phức tạp $O(N)$ rất chậm, Inverted Index tách văn bản thành các từ tố (terms) và xây dựng Posting List ánh xạ ngược lại danh sách các tài liệu chứa từ đó. Khi người dùng tìm kiếm từ 'NLP', hệ thống chỉ việc tra cứu bảng index để trả về ngay tài liệu $D_1$ và $D_3$ với độ phức tạp cực kỳ nhanh $O(1)$ lookup."

**Visual Cues (Gợi ý trình chiếu):**
* So sánh sự khác biệt trực quan giữa bảng Forward Index (bên trái) và Inverted Index (bên phải) trên slide.
* Nhấn mạnh sự chuyển đổi độ phức tạp từ O(N) sang O(1) lookup.

---

### Slide 10: Keyword Search — Thuật toán xếp hạng BM25 (1.5 phút) — Người trình bày: Huyền
> "Thuật toán xếp hạng văn bản mặc định được sử dụng trong Elasticsearch là **BM25**. Công thức toán học của BM25 được hiển thị trên slide. Trọng số BM25 được quyết định bởi 3 yếu tố chính:
> 1. **Term Frequency (TF):** Tần suất từ khóa xuất hiện trong tài liệu. Tuy nhiên, BM25 áp dụng hàm bão hòa để hạn chế việc một từ khóa xuất hiện quá nhiều lần làm ảnh hưởng tiêu cực đến điểm số.
> 2. **Inverse Document Frequency (IDF):** Những từ khóa càng hiếm gặp trong toàn bộ kho tài liệu sẽ có trọng số càng cao. Ví dụ, từ 'transformer' sẽ có trọng số IDF lớn hơn rất nhiều so với các stop-words như 'the' hay 'of'.
> 3. **Document Length:** Phạt các tài liệu quá dài để tránh việc chứa nhiều từ khóa loãng, thông qua tham số b.
> Các tham số chuẩn trong hệ thống được thiết lập mặc định là $k_1 = 1.2$ và $b = 0.75$. Mặc dù tối ưu về mặt tốc độ, hạn chế cốt lõi của BM25 vẫn là tính cứng nhắc của việc khớp từ khóa chính xác mà không hiểu nghĩa của từ."

**Visual Cues (Gợi ý trình chiếu):**
* Chỉ vào công thức BM25 và giải thích ngắn gọn các ký hiệu: $f(q_i, D)$ là term frequency, $|D|/\text{avgdl}$ là tỷ lệ độ dài tài liệu.
* Nhấn mạnh hạn chế cốt lõi ở hộp Alertblock bên phải: Chỉ hiểu từ vựng (lexical), không hiểu ngữ nghĩa (semantic).

---

### Slide 11: Semantic Search — Sentence Embedding và HNSW (1.5 phút) — Người trình bày: Huyền
> "Để mang lại khả năng hiểu ngữ nghĩa sâu sắc, hệ thống sử dụng phương pháp **Sentence Embedding** kết hợp giải thuật **HNSW**. Lịch sử của embedding bắt đầu từ Word2Vec năm 2013 biểu diễn từng từ riêng lẻ, sau đó là BERT năm 2018 hiểu từ trong ngữ cảnh, và Sentence Transformers năm 2019 giúp nhúng toàn bộ câu hoặc đoạn văn thành một vector số thực duy nhất. Độ tương đồng ngữ nghĩa giữa hai văn bản được tính bằng **Cosine Similarity** của hai vector biểu diễn.
> Để tìm kiếm nhanh chóng trong không gian hàng triệu vector mà không phải tính khoảng cách tuyến tính, giải thuật **HNSW** được áp dụng. HNSW tổ chức không gian vector thành đồ thị đa tầng tương tự như cấu trúc Skip List. Các tầng trên có các liên kết nhảy xa giúp định vị nhanh vùng lân cận, trong khi các tầng dưới chi tiết hơn giúp tìm chính xác láng giềng gần nhất. Nhờ vậy, độ phức tạp tìm kiếm giảm từ $O(N)$ xuống mức logarit $O(\log N)$. Cấu hình HNSW trong Elasticsearch của nhóm sử dụng số liên kết mỗi node $M = 16$ và tham số xây dựng $ef\_construction = 100$."

**Visual Cues (Gợi ý trình chiếu):**
* Giải thích nhanh công thức Cosine Similarity trên slide.
* Chỉ vào sơ đồ HNSW (ở cột bên phải) để mô tả cách tìm kiếm chuyển từ tầng cao xuống tầng thấp của đồ thị đa tầng.

---

### Slide 12: Hybrid Search — Reciprocal Rank Fusion (RRF) (1.5 phút) — Người trình bày: Huyền
> "Khi kết hợp cả BM25 và Vector search, chúng ta đối mặt với thách thức là điểm số của hai phương pháp có thang đo hoàn toàn khác nhau: BM25 chạy từ 0 đến vài chục không giới hạn, còn Cosine Similarity của kNN chỉ chạy từ 0 đến 1. Giải pháp tối ưu nhất là thuật toán **Reciprocal Rank Fusion (RRF)**.
> RRF không quan tâm đến điểm số thô của tài liệu, mà chỉ quan tâm đến thứ hạng của nó trong danh sách trả về của từng luồng tìm kiếm. Điểm RRF của một tài liệu $d$ được tính bằng tổng nghịch đảo thứ hạng cộng với một hằng số làm mịn $k$, thông thường $k$ được chọn bằng 60. RRF là thuật toán parameter-free, không cần huấn luyện hay tinh chỉnh trọng số phức tạp.
> Trên slide có một ví dụ trực quan: Giả sử tài liệu $D_A$ đứng thứ 1 ở luồng Keyword và thứ 2 ở luồng Semantic. Điểm RRF của nó sẽ là $\frac{1}{61} + \frac{1}{62} = 0.0325$, giúp nó vượt qua tài liệu $D_C$ vốn đứng thứ 3 ở Keyword nhưng đứng thứ 1 ở Semantic. Cơ chế này giúp các tài liệu được đồng thuận bởi cả hai luồng được ưu tiên xếp lên đầu một cách tự nhiên nhất.
> 
> Đến đây em xin kết thúc phần trình bày của mình. Tiếp theo, xin mời bạn Sơn Lam trình bày về Kiến trúc hệ thống và Embedding Pipeline."

**Visual Cues (Gợi ý trình chiếu):**
* Chỉ vào công thức RRF đóng khung nổi bật trên slide.
* Đi qua từng dòng của bảng ví dụ tính điểm RRF cho tài liệu $D_A$ và $D_C$ để người nghe hiểu rõ cách thức hoạt động thực tế.
* 🔗 **Chuyển tiếp:** Quay sang hướng tay về phía bạn Trịnh Sơn Lam để bàn giao lượt nói.

---

## PHẦN 2: KIẾN TRÚC HỆ THỐNG & EMBEDDING PIPELINE (Slide 13 - 18)
**Người trình bày: Trịnh Sơn Lam (Lam)**

### Slide 13: Kiến trúc tổng quan hệ thống (1 phút) — Người trình bày: Lam
> "Cảm ơn phần trình bày của bạn Thanh Huyền. Em xin tiếp tục với Chương 5: Kiến trúc hệ thống.
> Sơ đồ trên slide mô tả kiến trúc tổng quan của hệ thống tìm kiếm được thiết kế theo các phân lớp rõ ràng. Bắt đầu từ **Data Layer** chứa tệp tin arXiv JSON thô nặng 4.8 GB. Dữ liệu này qua **Processing Layer** để làm sạch và sinh vector nhúng bằng GPU. Sau đó, hệ thống áp dụng kiến trúc **Dual-Index** trong **Storage Layer** chạy trên Elasticsearch: index `arxiv_text` lưu metadata văn bản phục vụ BM25 chiếm 1.5 GB, còn index `arxiv_vectors` lưu vector nhúng chiếm 10.4 GB.
> **API Layer** được xây dựng bằng FastAPI đóng vai trò Backend điều phối truy vấn, và **UI Layer** là giao diện React Frontend tương tác trực quan với người dùng. Toàn bộ hạ tầng Elasticsearch và Kibana được đóng gói và vận hành dễ dàng thông qua **Docker Compose**."

**Visual Cues (Gợi ý trình chiếu):**
* Sử dụng con trỏ chỉ vào từng khối lớp trên sơ đồ TikZ theo thứ tự từ trên xuống dưới: Data Layer -> Processing -> Storage -> API Layer -> Presentation (UI).
* Nhấn mạnh cụm từ "Docker Compose" và "Kiến trúc Dual-Index" nằm ở trung tâm của slide.

---

### Slide 14: Data Ingestion Flow (1 phút) — Người trình bày: Lam
> "Hãy đi sâu hơn vào luồng nạp dữ liệu (Data Ingestion Flow). Quy trình này gồm 6 bước tuần tự tương ứng với 3 script chính được viết bằng Python:
> 1. Đầu tiên, file raw arXiv JSON được đọc theo dạng luồng (**Streaming**) để tránh lỗi tràn bộ nhớ RAM (OOM), đồng thời lọc ra các tài liệu thuộc Computer Science và loại bỏ các bản ghi lỗi.
> 2. Tiếp theo, dữ liệu sạch được đưa vào **GPU Embedding Pipeline** trên Google Colab để nhúng văn bản thành các vector 384 chiều với batch size 512.
> 3. Dữ liệu đầu ra sau khi nhúng được đưa vào Elasticsearch thông qua Bulk API với kích thước lô **5,000 tài liệu** mỗi lần gửi nhằm tối ưu băng thông mạng.
> 4. Cuối cùng, chúng em kiểm tra tính toàn vẹn và cấu trúc dữ liệu trên giao diện Kibana Dev Tools."

**Visual Cues (Gợi ý trình chiếu):**
* Trỏ vào từng bước trên sơ đồ ngang (từ s1 đến s6).
* Chỉ ra các tên script tương ứng phía trên mũi tên (`data_prep.py`, `embed_data.py`, `index_data.py`).
* Chỉ ra sự thay đổi kích thước file và định dạng ở dòng dưới: 4.8 GB -> 1.2M docs -> 384-dim -> 11.9 GB.

---

### Slide 15: Search Flow — Hybrid Search Pipeline (1 phút) — Người trình bày: Lam
> "Đối với luồng tìm kiếm, khi người dùng nhập câu truy vấn, FastAPI Backend sẽ tiếp nhận và điều phối hai nhánh truy vấn song song:
> - **Nhánh thứ nhất là Keyword Search:** Gửi truy vấn văn bản trực tiếp đến index `arxiv_text` thực hiện tìm kiếm BM25 trên title và abstract để lấy ra top 30 ứng viên.
> - **Nhánh thứ hai là Semantic Search:** Câu truy vấn được chuyển đổi thành vector 384 chiều nhờ mô hình MiniLM chạy local, sau đó thực hiện tìm kiếm vector HNSW với Cosine Similarity trên index `arxiv_vectors` để lấy ra top 30 ứng viên tương ứng.
> Kết quả từ hai nhánh được gộp lại tại tầng ứng dụng bằng thuật toán **RRF** với hằng số $k=60$. Danh sách sau khi gộp sẽ được sắp xếp và lấy ra top 10 kết quả tốt nhất để trả về cho người dùng kèm theo metadata đầy đủ."

**Visual Cues (Gợi ý trình chiếu):**
* Chỉ vào sơ đồ phân nhánh tìm kiếm song song: Một đường đi lên BM25 và Inverted Index, một đường đi xuống Encode Query và HNSW Graph.
* Trỏ vào điểm hội tụ "RRF Merge" và kết quả đầu ra "Top-10 Results".

---

### Slide 16: Lựa chọn Embedding Model (1 phút) — Người trình bày: Lam
> "Tiếp theo là Chương 6: Embedding Pipeline. Để chọn ra mô hình nhúng tối ưu nhất, nhóm đã so sánh nhiều ứng viên trên bảng xếp hạng MTEB như trong bảng. Mặc dù e5-large-v2 hay bge-small có điểm MTEB nhỉnh hơn, nhóm đã quyết định chọn **all-MiniLM-L6-v2** vì nó đạt được sự cân bằng hoàn hảo cho bài toán Big Data:
> - Kích thước vector chỉ 384 chiều giúp tiết kiệm dung lượng index HNSW đáng kể.
> - Dung lượng mô hình chỉ 22M tham số cực nhẹ có thể chạy ổn định trên các GPU miễn phí.
> - Tốc độ suy luận cực nhanh.
> Đầu vào của mô hình được ghép nối theo công thức: **Title + token SEP + Abstract**. Với giới hạn 256 tokens của MiniLM, chúng em phân bổ khoảng 15 tokens cho Title và 240 tokens cho Abstract. Nếu Abstract quá dài, nhóm áp dụng thuật toán **Cắt Abstract Thông minh (Smart Abstract Truncation)** theo ranh giới câu để giữ tối đa cấu trúc ngữ nghĩa tự nhiên."

**Visual Cues (Gợi ý trình chiếu):**
* Chỉ vào dòng tô đậm của mô hình `all-MiniLM-L6-v2` trong bảng so sánh.
* Giải thích nhanh công thức ghép văn bản đầu vào và giới hạn token budget được minh họa trên slide.

---

### Slide 17: GPU Acceleration và Batch Processing (1 phút) — Người trình bày: Lam
> "Khi thực hiện nhúng trên quy mô hơn 1.2 triệu bài báo, việc chạy trên CPU cục bộ là hoàn toàn không khả thi vì tốc độ chỉ đạt dưới 10 tài liệu/giây và mất tới gần 3 ngày chạy liên tục. Giải pháp của nhóm là chuyển sang Google Colab tận dụng sức mạnh tăng tốc phần cứng của **GPU NVIDIA Tesla T4**.
> Chúng em tối ưu hóa quy trình bằng cách thiết lập kích thước batch là **512 tài liệu**, kết hợp với **Dynamic Padding** để co giãn độ dài vector trong mỗi batch giúp tiết kiệm VRAM tối đa. Nhờ các kỹ thuật tối ưu này, tốc độ sinh vector tăng vọt lên mức **500 đến 800 tài liệu mỗi giây** (nhanh gấp $\sim$80 lần CPU). Toàn bộ quá trình nhúng cho 1,203,108 tài liệu hoàn thành chỉ trong vòng vỏn vẹn **35 phút**."

**Visual Cues (Gợi ý trình chiếu):**
* Chỉ vào hộp Alertblock "CPU quá chậm" và đối chiếu với hộp "Giải pháp GPU".
* Chỉ vào bảng kết quả ở góc phải dưới hiển thị con số ấn tượng: "35 phút" cho 1.2 triệu tài liệu.

---

### Slide 18: Checkpoint & Resume + Kết quả (1 phút) — Người trình bày: Lam
> "Một thách thức lớn khi chạy tác vụ nặng trên Google Colab phiên bản miễn phí là giới hạn thời gian kết nối 12 giờ và nguy cơ mất kết nối mạng giữa chừng. Để đảm bảo tính bền vững, hệ thống được trang bị cơ chế **Checkpoint và Resume** tự động.
> Cứ sau mỗi 50,000 bài báo được nhúng thành công, script sẽ tự động cập nhật tiến trình vào file `progress.json` và đồng bộ tệp kết quả JSONL lên Google Drive. Nếu phiên làm việc bị ngắt đột ngột, ở lần chạy tiếp theo hệ thống sẽ tự động đọc file tiến trình và resume ngay tại vị trí đang dang dở mà không mất công chạy lại từ đầu. Kết quả cuối cùng của Embedding Pipeline là file JSONL hoàn chỉnh nặng 11.05 GB chứa đầy đủ thông tin metadata và vector nhúng.
> 
> Đến đây em xin khép lại phần trình bày của mình về Pipeline dữ liệu. Tiếp theo, xin mời bạn Gia An trình bày về triển khai tìm kiếm và các đánh giá thực nghiệm."

**Visual Cues (Gợi ý trình chiếu):**
* Trỏ vào sơ đồ hoạt động của checkpoint: progress.json -> Google Drive -> Resume.
* Chỉ vào bảng tổng kết Embedding Pipeline ở cột bên phải để chốt lại toàn bộ các thông số kỹ thuật.
* 🔗 **Chuyển tiếp:** Quay sang và nhường lời thuyết trình cho bạn Dương Gia An.

---

## PHẦN 3: TRIỂN KHAI TÌM KIẾM, ĐÁNH GIÁ VÀ HƯỚNG PHÁT TRIỂN (Slide 19 - 39)
**Người trình bày: Dương Gia An (An)**

### Slide 19: Keyword Search — Keyword Matching (1 phút) — Người trình bày: An
> "Cảm ơn phần trình bày của bạn Sơn Lam. Em là Gia An, tiếp tục trình bày từ Chương 7: Search Implementation.
> Đầu tiên là truy vấn **Keyword Search** bằng Elasticsearch DSL. Cú pháp DSL sử dụng query `multi_match` trên hai trường `title` và `abstract`. Tiêu đề được áp dụng hệ số tăng cường `title^2` nhằm ưu tiên bài viết khớp từ khóa ngay trên tiêu đề. Kiểu truy vấn là `best_fields` giúp lấy điểm số cao nhất của trường khớp tốt nhất.
> Chỉ mục tương ứng là `arxiv_text` dung lượng chỉ 1.5 GB. Ưu điểm nổi bật của phương pháp này là tốc độ phản hồi cực kỳ nhanh, khoảng 70ms cho phân vị P50 trên quy mô 1.2 triệu bài báo, rất chính xác cho các tên riêng, mã số hay thuật ngữ công nghệ chính xác và tiêu tốn rất ít tài nguyên hệ thống."

**Visual Cues (Gợi ý trình chiếu):**
* Chỉ vào khối mã Query DSL (đặc biệt là `"multi_match"`, `"fields": ["title^2", "abstract"]`).
* Chỉ ra các gạch đầu dòng về ưu điểm ở cột bên phải: P50 ~70ms, chính xác thuật ngữ viết tắt.

---

### Slide 20: Semantic Search — Semantic Understanding (1 phút) — Người trình bày: An
> "Đối với luồng **Semantic Search**, hệ thống sử dụng truy vấn `knn` trong Elasticsearch DSL. Điểm tìm kiếm được tính dựa trên trường `embedding` lưu trữ vector 384 chiều. Chúng em cấu hình tham số `k=10` để trả về 10 láng giềng gần nhất và `num_candidates = 100` cho mỗi phân mảnh để giới hạn không gian tìm kiếm trên đồ thị HNSW.
> Quy trình xử lý gồm: chuyển đổi câu truy vấn thô của người dùng thành vector 384 chiều nhờ mô hình nhúng cục bộ, duyệt đồ thị HNSW để tìm các ứng viên lân cận và xếp hạng theo Cosine Similarity. Ưu điểm lớn nhất là hệ thống hiểu được các từ đồng nghĩa và cách diễn đạt khác nhau, cho phép tìm kiếm bằng các câu mô tả khái niệm tự nhiên mà không cần khớp từ khóa chính xác."

**Visual Cues (Gợi ý trình chiếu):**
* Chỉ vào khối mã Query DSL kNN (đặc biệt là các tham số `"k": 10`, `"num_candidates": 100`).
* Trỏ vào sơ đồ Pipeline xử lý vector ở góc dưới bên trái.

---

### Slide 21: Hybrid Search — Kết hợp tất cả (1.5 phút) — Người trình bày: An
> "Để đạt được kết quả tối ưu nhất, **Hybrid Search** kết hợp song song cả hai luồng: Một truy vấn BM25 được gửi đến index `arxiv_text` và một truy vấn kNN gửi đến `arxiv_vectors`. Cả hai luồng này đều lấy về top 30 ứng viên thay vì top 10 để làm phong phú tập kết quả. Sau đó, hệ thống trích xuất ID tài liệu, áp dụng công thức RRF với $k=60$ để xếp hạng lại, chọn ra top 10 kết quả tốt nhất.
> Điểm đặc biệt của kiến trúc Dual-Index của nhóm là việc tách biệt hoàn toàn hai chỉ mục: `arxiv_text` chỉ chứa văn bản nhẹ nhàng và `arxiv_vectors` chứa vector nhúng lớn. Điều này giúp tối ưu hóa dung lượng RAM và CPU khi thực hiện các truy vấn độc lập, đồng thời hỗ trợ cập nhật dữ liệu gia tăng thời gian thực thông qua API mà không cần đánh lại chỉ mục toàn bộ. Khi nạp dữ liệu lớn, chúng em cũng áp dụng các tối ưu hóa như tắt `refresh_interval`, đặt `replicas = 0` và chạy lệnh `_forcemerge` để tối ưu hóa đồ thị HNSW."

**Visual Cues (Gợi ý trình chiếu):**
* Đi qua 6 bước của quy trình hoạt động được liệt kê chi tiết ở cột bên trái.
* Trỏ vào hộp "Kiến trúc Dual-Index" và phần cấu hình tối ưu hóa Elasticsearch ở cột bên phải.

---

### Slide 22: Phương pháp đánh giá (1 phút) — Người trình bày: An
> "Tiếp theo là Chương 8: Đánh giá chất lượng. Để đánh giá hệ thống một cách khách quan và chính xác, nhóm đã xây dựng một tập Ground Truth gồm **30 test queries** chia đều thành 3 nhóm đặc trưng:
> - **Nhóm A (Exact):** Chứa các từ khóa chính xác như *'BERT fine-tuning'*.
> - **Nhóm B (Semantic):** Là các truy vấn khái niệm tự nhiên như *'methods to detect fake images'*.
> - **Nhóm C (Mixed):** Là dạng truy vấn kết hợp cả hai yếu tố.
> Quy trình dán nhãn được thực hiện qua kỹ thuật Gom cụm ứng viên (**Query Pooling**) bằng cách lấy top 10 kết quả của cả 3 phương thức tìm kiếm, gộp lại để tạo ra danh sách từ 15 đến 25 ứng viên cho mỗi query. Sau đó, nhóm áp dụng phương pháp biểu quyết đa số **Silver Standard**: một tài liệu được coi là liên quan (nhãn 1) nếu được đồng thuận bởi ít nhất 2 trên 3 phương pháp tìm kiếm, kết hợp với công cụ kiểm tra thủ công. Quy trình này tạo ra khoảng 600 lượt dán nhãn chất lượng cao."

**Visual Cues (Gợi ý trình chiếu):**
* Chỉ vào bảng mô tả 3 nhóm truy vấn (Exact, Semantic, Mixed) trên slide.
* Chỉ vào sơ đồ quy trình dán nhãn ở cột bên phải: Pooling -> Silver Standard (Majority Voting Proxy) -> Manual verification.

---

### Slide 23: Metrics: NDCG@10 và MRR@10 (1 phút) — Người trình bày: An
> "Nhóm lựa chọn hai độ đo chuẩn trong Information Retrieval để đánh giá chất lượng xếp hạng là **NDCG@10** và **MRR@10**:
> - **NDCG@10 (Normalized Discounted Cumulative Gain):** Đánh giá chất lượng của toàn bộ top 10 kết quả, trong đó các tài liệu liên quan được xếp ở vị trí càng cao thì điểm số đóng góp càng lớn nhờ hàm logarit giảm dần. Điểm số nằm trong khoảng $[0.0, 1.0]$.
> - **MRR@10 (Mean Reciprocal Rank):** Tập trung vào việc đo lường tốc độ tiếp cận thông tin của người dùng bằng cách tính nghịch đảo vị trí của tài liệu liên quan đầu tiên xuất hiện trong danh sách. Nếu tài liệu đúng xuất hiện ngay vị trí đầu tiên, điểm Reciprocal Rank đạt tối đa là 1.0.
> Việc chọn điểm cắt tại vị trí số 10 (cutoff @10) phản ánh chính xác hành vi thực tế của người dùng trên giao diện web tìm kiếm học thuật."

**Visual Cues (Gợi ý trình chiếu):**
* Chỉ vào công thức toán học của $DCG@p$ và $NDCG@p$ ở cột bên trái.
* Chỉ vào công thức $RR$ và giải thích tham số $rank^*$ ở cột bên phải.

---

### Slide 24: Kết quả đánh giá — Bảng tổng quan (1 phút) — Người trình bày: An
> "Bảng tổng hợp kết quả đánh giá trên slide thể hiện hiệu năng vượt trội của Hybrid Search. Trên cả 3 nhóm truy vấn:
> - **BM25 và kNN đơn lẻ** chỉ đạt điểm NDCG trung bình từ 0.64 đến 0.70.
> - **Hybrid Search sử dụng RRF** đã cải thiện vượt bậc, đạt điểm số NDCG@10 ấn tượng từ **0.94 đến 0.98**.
> - Điểm MRR@10 của Hybrid Search cũng gần như đạt mức tuyệt đối 1.0 trên hầu hết các nhóm (Nhóm A và C đạt 1.0000; Nhóm B đạt 0.9250), nghĩa là tài liệu liên quan gần như luôn xuất hiện ngay ở vị trí đầu tiên hoặc thứ hai trong danh sách kết quả.
> Kết quả này chứng minh sự kết hợp thông minh giữa khớp từ khóa chính xác và hiểu ngữ nghĩa sâu sắc giúp cải thiện đáng kể chất lượng tìm kiếm."

**Visual Cues (Gợi ý trình chiếu):**
* Chỉ vào bảng kết quả so sánh, nhấn mạnh các con số in đậm của phương pháp Hybrid (RRF) ở hàng cuối cùng.
* Trỏ vào hộp nhận xét tổng quan ở phía dưới để đúc kết nhận định.

---

### Slide 25: Kết quả đánh giá — Biểu đồ so sánh (0.5 phút) — Người trình bày: An
> "Hai biểu đồ trên slide trực quan hóa điểm số NDCG@10 và MRR@10 của các phương pháp. Nhìn vào biểu đồ cột, chúng ta có thể thấy rõ khoảng cách chênh lệch lớn giữa đường biểu diễn của Hybrid Search màu xanh teal so với hai đường màu xanh blue và cam đại diện cho BM25 và kNN đơn lẻ. Sự vượt trội này diễn ra đồng đều trên cả hai độ đo chất lượng xếp hạng."

**Visual Cues (Gợi ý trình chiếu):**
* Chỉ vào hai biểu đồ so sánh NDCG và MRR trên màn hình để khán giả thấy rõ sự chênh lệch cột điểm số.

---

### Slide 26: Phân tích chi tiết (1.5 phút) — Người trình bày: An
> "Đi sâu vào phân tích chi tiết, nhóm nhận thấy một chỉ số rất thú vị: chỉ có trung bình **1.5 trên 10 tài liệu** trùng lặp giữa kết quả của BM25 và Vector search. Điều này chứng tỏ hai phương pháp này tiếp cận thông tin theo hai hướng hoàn toàn khác nhau và tìm ra các tập tài liệu bổ trợ cho nhau. Khi RRF kết hợp chúng, những tài liệu được cả hai luồng đồng thuận sẽ được đẩy lên vị trí cao nhất, đồng thời giữ lại được các tài liệu liên quan mà một trong hai phương pháp đơn lẻ bỏ sót.
> Khi đánh giá độ ổn định theo quy mô dữ liệu từ 100K lên 1.2M bài báo, chúng em thấy điểm NDCG của BM25 giảm nhẹ từ 0.72 xuống 0.67 do nhiễu từ khóa tăng lên khi dữ liệu phình to. Ngược lại, kNN duy trì độ ổn định cao ở mức 0.66 nhờ không gian vector bền vững. Đặc biệt, Hybrid Search giữ vững hiệu năng tối ưu nhất với NDCG luôn đạt từ **0.96 đến 0.97** ở mọi quy mô dữ liệu, khẳng định tính bền vững và khả năng mở rộng tuyệt vời của kiến trúc này."

**Visual Cues (Gợi ý trình chiếu):**
* Chỉ vào con số "1.5/10 docs" trùng lặp để giải thích lý do hiệu năng Hybrid tăng vọt.
* Chỉ vào bảng so sánh quy mô dữ liệu (100K vs 1.2M) ở cột bên phải để chỉ ra xu hướng tăng/giảm hiệu năng của các thuật toán.

---

### Slide 27: Latency Analysis — Bảng tổng quan (1 phút) — Người trình bày: An
> "Chuyển sang Chương 9: Đánh giá hiệu năng hệ thống. Bảng trên slide ghi nhận thời gian phản hồi thực tế của hệ thống ở các phân vị P50 và P95 qua ba quy mô dữ liệu:
> - BM25 luôn giữ độ trễ rất thấp, tối đa chỉ 71ms P50 ở quy mô 1.2M.
> - Đối với Hybrid Search sử dụng RRF, hệ thống đạt độ trễ ấn tượng là **99ms P50** ở quy mô tối đa 1.2 triệu bài báo khoa học.
> Thời gian này hoàn toàn đáp ứng được tiêu chuẩn thời gian thực dưới 100ms trong các ứng dụng tìm kiếm công nghiệp, mang lại trải nghiệm mượt mà cho người dùng cuối."

**Visual Cues (Gợi ý trình chiếu):**
* Chỉ vào bảng số liệu thời gian phản hồi, nhấn mạnh cột "1.2M" và dòng in đậm của "Hybrid (RRF)" với giá trị "99 ms" P50.
* Chỉ vào hộp nhận xét màu xanh lá cây ở phía dưới slide.

---

### Slide 28: Latency Analysis — Trực quan hóa & Thách thức (1 phút) — Người trình bày: An
> "Tuy nhiên, trong quá trình đo đạc thực tế, nhóm đã phát hiện một thách thức lớn: ở lượt truy vấn đầu tiên trên quy mô 1.2M bài báo, độ trễ P95 của Vector Search độc lập tăng vọt lên tới **1,206 mili-giây**. Hiện tượng này gọi là **Semantic Cold Start**.
> Nguyên nhân là do cấu trúc đồ thị HNSW của index `arxiv_vectors` quá lớn, khoảng 10.4 GB, vượt quá dung lượng Heap và phải load phân đoạn từ ổ đĩa SSD vào OS Page Cache trong lần truy vấn đầu tiên, gây nghẽn I/O. Giải pháp thực tế để khắc phục hiện tượng này là tiến hành chạy các truy vấn warmup để làm ấm cache trước khi đưa hệ thống vào phục vụ người dùng thực tế."

**Visual Cues (Gợi ý trình chiếu):**
* Chỉ vào biểu đồ độ trễ bên trái để thấy cột P95 của Vector Search cao vọt.
* Chỉ vào hộp giải thích thách thức "Semantic Cold Start" và giải pháp "warmup cache" ở cột bên phải.

---

### Slide 29: Latency Scaling — Tăng trưởng theo quy mô (1 phút) — Người trình bày: An
> "Biểu đồ bên trái mô tả xu hướng tăng trưởng độ trễ P50 theo quy mô dữ liệu. Đường BM25 tăng trưởng tuyến tính rất chậm. Đường kNN tăng nhanh hơn do sự phức tạp của đồ thị HNSW và các thao tác đọc ghi đĩa. Đường Hybrid Search chạy song song nên độ trễ bị giới hạn bởi luồng kNN chậm hơn, tuy nhiên nhờ cấu hình tối ưu luồng chạy song song nên vẫn duy trì ở mức 99ms P50.
> Môi trường thử nghiệm hiệu năng được cấu hình trên máy tính cá nhân dùng chip Intel Core i7 (8 nhân, 16 luồng), 16GB RAM và SSD NVMe. Elasticsearch chạy trong môi trường Docker trên nền tảng WSL2 Ubuntu."

**Visual Cues (Gợi ý trình chiếu):**
* Chỉ vào đường biểu diễn xu hướng tăng trưởng độ trễ trên biểu đồ bên trái.
* Giới thiệu nhanh cấu hình phần cứng thử nghiệm ở cột bên phải để khẳng định tính thực tế của các con số benchmarking.

---

### Slide 30: Storage Analysis — Dung lượng lưu trữ (1 phút) — Người trình bày: An
> "Về khía cạnh lưu trữ, bảng số liệu trên slide cho thấy dung lượng đĩa tăng trưởng tuyến tính theo số lượng tài liệu. Điểm thú vị là kích thước index vật lý trên Elasticsearch luôn nhỏ hơn dung lượng file JSONL thô sau khi nhúng (ví dụ ở quy mô 1.2M, index chỉ chiếm 11.9 GB so với file raw JSONL là 12 GB). Điều này có được nhờ cơ chế nén cột cực kỳ hiệu quả của Lucene như thuật toán LZ4 cho text và nén mảng float cho vector.
> Ở quy mô lớn nhất 1.2M tài liệu, hệ thống áp dụng kiến trúc Dual-Index: index `arxiv_text` phục vụ BM25 chỉ nặng 1.5 GB, còn index `arxiv_vectors` phục vụ kNN nặng tới 10.4 GB. Tổng dung lượng đĩa tiêu thụ là 11.9 GB."

**Visual Cues (Gợi ý trình chiếu):**
* Chỉ vào bảng dung lượng lưu trữ ở các mức 100K -> 500K -> 1.2M.
* Chỉ vào bảng chi tiết Dual-Index ở cột bên phải để thấy rõ sự chênh lệch dung lượng giữa text index và vector index.

---

### Slide 31: Storage Analysis — Trực quan hóa (0.5 phút) — Người trình bày: An
> "Biểu đồ hình tròn trên slide trực quan hóa cơ cấu dung lượng lưu trữ của hệ thống. Dữ liệu vector nhúng và đồ thị HNSW chiếm tới **87%** tổng dung lượng lưu trữ đĩa cứng của Elasticsearch.
> Điều này khẳng định chi phí lưu trữ chính của một hệ thống Hybrid Search nằm ở dữ liệu vector chứ không phải ở phần văn bản truyền thống. Việc tách biệt Dual-Index giúp giảm đáng kể áp lực bộ nhớ JVM Heap cho các truy vấn chỉ sử dụng văn bản BM25 thông thường."

**Visual Cues (Gợi ý trình chiếu):**
* Chỉ vào biểu đồ tròn, nhấn mạnh phân khúc 87% dành cho `arxiv_vectors`.

---

### Slide 32: Tóm tắt kết quả đạt được (1 phút) — Người trình bày: An
> "Đến với Chương 11: Kết luận. Dự án của nhóm đã đạt được 6 kết quả quan trọng:
> 1. Xây dựng thành công **Big Data Pipeline** xử lý streaming và lọc 1.2 triệu bài báo khoa học từ arXiv không bị OOM.
> 2. Hoàn thành **GPU Embedding Pipeline** nhúng 1.2 triệu bài báo chỉ trong **35 phút** nhờ tận dụng Tesla T4.
> 3. Thiết lập kiến trúc **Dual-Index** tối ưu hóa lưu trữ và truy vấn độc lập trên Elasticsearch.
> 4. Hệ thống Hybrid Search đạt chất lượng xếp hạng vượt trội với **NDCG@10 = 0.97** và **MRR@10 = 0.99**.
> 5. Thực hiện đánh giá hiệu năng đa quy mô một cách khoa học.
> 6. Hoàn thiện ứng dụng **Web Application** chạy trên Docker với đầy đủ tính năng tìm kiếm lai và bộ lọc thời gian thực."

**Visual Cues (Gợi ý trình chiếu):**
* Điểm qua các dấu tick xanh lá cây thể hiện các mục tiêu đã hoàn thành xuất sắc.
* Nhấn mạnh hai chỉ số chất lượng: NDCG 0.97 và MRR 0.99.

---

### Slide 33: Hạn chế và Hướng phát triển (1 phút) — Người trình bày: An
> "Bên cạnh các kết quả đạt được, hệ thống vẫn tồn tại một số hạn chế nhất định:
> - Việc gộp RRF đang được xử lý ở application layer làm tăng thêm một chút độ trễ phản hồi so với BM25 gốc.
> - Mô hình nhúng all-MiniLM-L6-v2 tuy nhẹ nhưng có phần hạn chế khi biểu diễn các khái niệm khoa học chuyên sâu và phức tạp.
> - Hệ thống mới triển khai trên single-node nên chưa đánh giá được khả năng chịu lỗi và tính sẵn sàng cao.
> 
> Từ đó, hướng phát triển tương lai của dự án bao gồm:
> - Nâng cấp sử dụng các **API RRF tích hợp sẵn (Native RRF)** ở cấp truy vấn của Elasticsearch phiên bản mới để giảm độ trễ.
> - Áp dụng cơ chế tái xếp hạng **Cross-Encoder Re-ranking** cho top 100 kết quả đầu ra của Hybrid Search để nâng cao độ chính xác.
> - Triển khai mô hình **Multi-node cluster** với Docker Swarm hoặc Kubernetes từ 3 nodes trở lên.
> - Thử nghiệm nâng cấp lên các mô hình nhúng chuyên sâu cho tài liệu khoa học như **SPECTER2** hoặc **E5-large**."

**Visual Cues (Gợi ý trình chiếu):**
* Chỉ vào cột "Hạn chế" (bên trái) và đối chiếu sang cột "Hướng phát triển" (bên phải) tương ứng để thể hiện lộ trình cải tiến rõ ràng.

---

### Slide 34: Demo hệ thống (2 phút) — Người trình bày: An
> "Bây giờ, em xin phép được trình chiếu video demo thực tế ứng dụng tìm kiếm của nhóm chúng em. Giao diện web được thiết kế hiện đại, hỗ trợ người dùng tìm kiếm trực quan theo 3 chế độ độc lập: Keyword Search, Semantic Search và Hybrid Search.
> Người dùng có thể dễ dàng lọc kết quả theo năm xuất bản và theo các danh mục thuộc Computer Science trực tiếp trên thanh công cụ lọc. Hệ thống truy vấn trực tiếp trên kho dữ liệu hơn 1.2 triệu bài báo của arXiv và trả về kết quả kèm theo tiêu đề, tên tác giả, tóm tắt nội dung, năm xuất bản và các thẻ phân loại của bài viết. Video sau đây sẽ minh họa cách hệ thống xử lý các câu truy vấn phức tạp và cho thấy sự khác biệt rõ rệt về chất lượng kết quả giữa các chế độ tìm kiếm..."

**Visual Cues (Gợi ý trình chiếu):**
* Chuyển sang màn hình trình chiếu video demo.
* Thuyết minh trực tiếp các thao tác trong video: gõ query chuyên ngành, click chọn chế độ search, chọn bộ lọc năm và quan sát tốc độ trả về kết quả.

---

### Slide 35: Tài liệu tham khảo (0.5 phút) — Người trình bày: An
> "Trên đây là danh sách các tài liệu tham khảo chính được nhóm sử dụng trong suốt quá trình nghiên cứu và phát triển dự án, bao gồm các công trình nghiên cứu kinh điển về thuật toán BM25 của Robertson, giải thuật RRF của Cormack, Sentence-BERT của Reimers, đồ thị HNSW của Malkov và tài liệu hướng dẫn chính thức của Elasticsearch."

**Visual Cues (Gợi ý trình chiếu):**
* Đi lướt nhanh qua danh sách tài liệu tham khảo trên slide.

---

### Slide 36: Cảm ơn và Q&A (open) — Người trình bày: An
> "Bài thuyết trình của Nhóm 11 đến đây là kết thúc. Chúng em xin chân thành cảm ơn thầy Thoại Nam và các bạn đã dành thời gian chú ý lắng nghe. Sau đây, nhóm chúng em rất mong nhận được những câu hỏi, ý kiến đóng góp từ thầy và các bạn để hoàn thiện đề tài hơn nữa. Xin cảm ơn thầy và các bạn!"

**Visual Cues (Gợi ý trình chiếu):**
* Cúi đầu chào và mỉm cười thân thiện với thầy và các bạn.
* Mở slide Q&A sẵn sàng nhận câu hỏi.

---

## PHẦN 4: HỖ TRỢ TRẢ LỜI CÂU HỎI PHỤ (BACKUP SLIDES - Slide 37 - 39)
*(Dùng khi thầy đặt câu hỏi sâu trong phiên Q&A)*

### Slide 37: Backup: Latency & Storage — Chi tiết — Người trình bày: An
> "Dạ thưa thầy, slide này là phần phụ lục chi tiết về so sánh thời gian phản hồi ở các phân vị lẻ P50, P95 cùng bảng phân tích đánh đổi (trade-off) giữa các phương pháp.
> Như thầy có thể thấy, BM25 có chi phí đĩa và RAM cực thấp nhưng chất lượng trung bình. Trong khi Hybrid Search mang lại chất lượng xếp hạng tốt nhất nhưng đánh đổi lại chi phí lưu trữ cao hơn, khoảng 11.9 GB và đòi hỏi tài nguyên RAM tối ưu để lưu đồ thị HNSW."

---

### Slide 38: Backup: Keyword Search (BM25) — Ví dụ tính điểm step-by-step — Người trình bày: An
> "Dạ thưa thầy, để minh họa chi tiết cách tính điểm BM25 của Elasticsearch, chúng em có chuẩn bị slide phụ lục này.
> Khi người dùng nhập truy vấn 'attention mechanism', hệ thống sẽ phân tích cú pháp thành hai token gốc là 'attent' và 'mechan'. Sau đó tra cứu Inverted Index để tìm các tài liệu chứa cả hai token này. Đối với tài liệu $D_{42}$, hệ thống tính tần suất xuất hiện của từ khóa trong tiêu đề và tóm tắt, áp dụng hệ số tăng cường title^2 và tính toán điểm số BM25 cuối cùng đạt 12.8 để đưa bài viết lên đầu kết quả."

---

### Slide 39: Backup: Kiến trúc Dual-Index — Chi tiết — Người trình bày: An
> "Dạ thưa thầy, về kiến trúc Dual-Index chi tiết của nhóm, chúng em tách thành index `arxiv_text` lưu văn bản thuần và `arxiv_vectors` lưu vector nhúng cùng đồ thị HNSW.
> Khi có bài báo mới được nạp qua API, hệ thống thực hiện sinh vector nhúng thời gian thực và đẩy song song vào cả hai chỉ mục này, sau đó gọi API refresh để bài viết mới có thể sẵn sàng tìm kiếm ngay lập tức mà không cần rebuild lại toàn bộ cơ sở dữ liệu."
