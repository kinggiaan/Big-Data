# Script Thuyết Trình — Hybrid Search Seminar
## Thời lượng: 10–15 phút | 17 slides (15 chính + 2 backup)

### Phân công trình bày theo Khối liên tục (Continuous Speaker Blocks):
- **Khối 1: Nguyễn Thanh Huyền (Huyền)** — **Slides 1 đến 3 (Thời lượng: ~1.5 phút)**: Phần giới thiệu, tổng quan chương trình, bối cảnh bài toán tìm kiếm (IR). *Đảm nhận phần mở đầu hoàn toàn phi kỹ thuật.*
- **Khối 2: Trịnh Sơn Lâm (Lâm)** — **Slides 4 đến 8 (Thời lượng: ~6 phút)**: Đi sâu vào kỹ thuật cốt lõi của Tìm kiếm từ khóa (Inverted Index, BM25) và Tìm kiếm ngữ nghĩa (Embedding, Cosine, kNN vs ANN/HNSW).
- **Khối 3: Dương Gia An (An)** — **Slides 9 đến 15 (Thời lượng: ~7.5 phút)**: Trình bày sự cần thiết của Hybrid Search, thuật toán Rank Fusion/RRF, các Case Studies thực tế, phần Kết luận & Xu hướng, và điều phối phần Q&A.

---

## [KHỐI 1: GIỚI THIỆU & ĐẶT VẤN ĐỀ] — NGƯỜI TRÌNH BÀY: HUYỀN

### Slide 1: Title (15 giây) — Người trình bày: Huyền

> Xin chào thầy và các bạn! Hôm nay nhóm mình sẽ chia sẻ về chủ đề **Hybrid Search** — phương pháp kết hợp tìm kiếm từ khóa truyền thống và tìm kiếm ngữ nghĩa bằng AI để tối ưu hóa kết quả tìm kiếm. Đây là kiến trúc đang được áp dụng rộng rãi tại các hệ thống lớn như Google, Shopee, Amazon.

---

### Slide 2: Nội dung trình bày (15 giây) — Người trình bày: Huyền

> Bài thuyết trình của nhóm sẽ đi qua 6 nội dung chính: 
> 1. Tổng quan về **Bài toán tìm kiếm (Information Retrieval)**.
> 2. Phương pháp **Tìm kiếm từ khóa (Keyword Search)**.
> 3. Phương pháp **Tìm kiếm ngữ nghĩa (Semantic Search)**.
> 4. Sự kết hợp thành **Tìm kiếm kết hợp (Hybrid Search)**.
> 5. Hai **Nghiên cứu thực tế (Case Studies)**.
> 6. **Kết luận & Xu hướng phát triển**.

---

### Slide 3: Sự bùng nổ dữ liệu (1 phút) — Người trình bày: Huyền

> Chúng ta đang sống trong kỷ nguyên bùng nổ thông tin. Hằng ngày, một lượng dữ liệu khổng lồ được tạo ra dưới dạng **phi cấu trúc** như văn bản, hình ảnh, âm thanh...
>
> Để hình dung quy mô, hãy nhìn vào các kho dữ liệu: Google đã index hơn 130 nghìn tỷ trang web, thư viện arXiv chứa hơn 2.4 triệu bài báo khoa học, và Wikipedia có hơn 60 triệu bài viết đa ngôn ngữ.
>
> Thử thách lớn nhất là: **làm thế nào để tìm đúng thông tin cần thiết** trong biển dữ liệu này? Đó là nhiệm vụ của bài toán **Information Retrieval (IR)**. Trải qua hơn 50 năm phát triển, công nghệ tìm kiếm đã tiến hóa từ thế hệ **Lexical** (đối khớp từ khóa từ thập niên 70) sang thế hệ **Semantic** (hiểu ngữ nghĩa bằng AI từ 2018), và giờ đây là thế hệ **Hybrid** (kết hợp cả hai).

**🔗 Chuyển tiếp (Huyền bàn giao cho Lâm):** *"Sau đây, để đi sâu vào chi tiết kỹ thuật của hai thế hệ tìm kiếm đầu tiên, bạn Lâm sẽ tiếp tục trình bày về Keyword Search và Semantic Search."*

---

## [KHỐI 2: TÌM KIẾM TỪ KHÓA & TÌM KIẾM NGỮ NGHĨA] — NGƯỜI TRÌNH BÀY: LÂM

### Slide 4: Inverted Index (1 phút) — Người trình bày: Lâm

> Xin chào mọi người, mình là Lâm. Mình xin phép đi vào cấu trúc nền tảng của Tìm kiếm từ khóa: **Inverted Index**.
>
> Ý tưởng của Inverted Index rất đơn giản nhưng cực kỳ hiệu quả. Thay vì lưu trữ dạng Forward Index (tài liệu chứa những từ gì), chúng ta **đảo ngược** lại: mỗi **từ khóa** sẽ trỏ đến danh sách các tài liệu chứa từ khóa đó.
>
> Nhìn vào ví dụ: với Forward Index, để tìm tài liệu chứa từ "NLP", ta phải duyệt qua toàn bộ N tài liệu — độ phức tạp O(N). Nhưng với Inverted Index, ta chỉ cần tra từ khóa "NLP" và lập tức có kết quả là tài liệu D1 và D3 — độ phức tạp lúc này chỉ là O(1). Đây là cấu trúc dữ liệu xương sống của mọi search engine lớn như Elasticsearch, Solr hay Google.

---

### Slide 5: BM25 (1.5 phút) — Người trình bày: Lâm

> Để xếp hạng các tài liệu trong Inverted Index, thuật toán chuẩn ngành được sử dụng phổ biến nhất là **BM25 (Best Matching 25)**.
>
> Điểm số BM25 của một tài liệu dựa trên 3 yếu tố cốt lõi:
> - **TF (Term Frequency)**: Tần suất từ khóa xuất hiện trong tài liệu. BM25 thiết kế mức độ bão hòa TF (thông qua tham số k1) giúp tránh hiện tượng spam từ khóa (keyword stuffing).
> - **IDF (Inverse Document Frequency)**: Từ khóa càng hiếm trên toàn bộ hệ thống thì trọng số của nó càng cao.
> - **Document Length**: Phạt các tài liệu quá dài để tránh việc chứa từ khóa ngẫu nhiên (thông qua tham số b).
>
> Mặc dù rất nhanh và chính xác cho đối khớp từ khóa, BM25 có hạn chế lớn là **chỉ hiểu mặt chữ, không hiểu ngữ nghĩa**. Ví dụ, tìm "car" sẽ không ra tài liệu chứa từ "automobile" dù chúng đồng nghĩa.

---

### Slide 6: Vector Embedding (1.5 phút) — Người trình bày: Lâm

> Để giải quyết vấn đề hiểu ngữ nghĩa, thế hệ thứ hai ra đời: **Semantic Search (Tìm kiếm ngữ nghĩa)** dựa trên công nghệ **Vector Embedding**.
>
> Vector Embedding biểu diễn ý nghĩa của một đoạn văn bản dưới dạng một vector số thực nhiều chiều. Trong không gian vector này, các tài liệu có nghĩa tương đồng sẽ nằm **gần nhau**.
>
> Nhìn sơ đồ bên phải, ta thấy các bài báo về xử lý ngôn ngữ tự nhiên (NLP) như BERT, GPT tự động gom thành một nhóm, trong khi các bài báo về thị giác máy tính (CV) như CNN, ResNet nằm ở một nhóm khác. Khi người dùng nhập query, hệ thống chuyển query thành vector và tìm các vector tài liệu gần nhất bằng phép đo **Cosine Similarity** (giá trị từ -1 đến 1, càng gần 1 càng tương đồng).
>
> Quá trình này đã tiến hóa từ Word2Vec (2013 - cấp độ từ), qua BERT (2018 - cấp độ ngữ cảnh), đến Sentence Transformers (2019 - cấp độ câu/đoạn văn).

---

### Slide 7: Embedding Models & Cosine Similarity (1 phút) — Người trình bày: Lâm

> Slide này so sánh các mô hình embedding phổ biến và ví dụ cụ thể về điểm tương đồng Cosine.
>
> Bảng bên trái cho thấy sự đánh đổi (trade-off): các mô hình gọn nhẹ như `all-MiniLM-L6-v2` chỉ có 384 chiều, chạy rất nhanh và tốn ít tài nguyên; trong khi các mô hình như `text-embedding-3-large` của OpenAI lên tới 3072 chiều, biểu diễn ngữ nghĩa tốt hơn nhưng đòi hỏi tài nguyên tính toán và lưu trữ lớn hơn rất nhiều.
>
> Bảng bên phải minh họa khả năng hiểu ngữ cảnh của mô hình: 
> - Cặp câu đồng nghĩa "fake images" và "image forgery" đạt điểm tương đồng rất cao (0.70) dù không chung từ nào.
> - Ngược lại, từ "bank" trong ngữ cảnh tài chính và "bank" trong ngữ cảnh bờ sông chỉ đạt 0.35, cho thấy mô hình phân biệt từ đồng âm khác nghĩa cực kỳ tốt.

---

### Slide 8: Tìm kiếm chính xác vs Tìm kiếm xấp xỉ (1 phút) — Người trình bày: Lâm

> Khi triển khai Tìm kiếm ngữ nghĩa ở quy mô lớn, chúng ta gặp thách thức về hiệu năng.
>
> Với **Tìm kiếm chính xác (Exact Search - brute-force kNN)**, ta phải tính khoảng cách từ query vector đến **tất cả** vector trong hệ thống. Nếu có 1 triệu vector 384 chiều, hệ thống phải thực hiện tới **384 triệu phép tính số thực cho mỗi query**! Độ phức tạp O(N) khiến hệ thống bị nghẽn (như cảnh báo màu đỏ ở đây).
>
> Để khắc phục, chúng ta sử dụng **Tìm kiếm xấp xỉ (Approximate Nearest Neighbor - ANN)** nhằm đánh đổi một chút độ chính xác lấy tốc độ vượt trội (đưa độ phức tạp về O(log N)).
>
> Có 4 hướng tiếp cận chính:
> - **LSH (Locality Sensitive Hashing)**: Băm các vector gần nhau vào cùng một giỏ.
> - **IVF (Inverted File Indexing)**: Phân cụm không gian vector, chỉ tìm kiếm trên cụm gần nhất.
> - **Quantization (ScaNN)**: Nén kích thước vector để tính toán nhanh trong RAM.
> - **Graph-based (HNSW)**: Xây dựng đồ thị đa tầng như Skip List, là giải pháp mặc định hiệu quả nhất hiện nay được dùng trong Elasticsearch.

**🔗 Chuyển tiếp (Lâm bàn giao cho An):** *"Chúng ta đã hiểu rõ hai phương pháp tìm kiếm. Sau đây, bạn An sẽ trình bày cách kết hợp chúng thành Hybrid Search và kết quả ứng dụng thực tế."*

---

## [KHỐI 3: HYBRID SEARCH & CASE STUDIES] — NGƯỜI TRÌNH BÀY: AN

### Slide 9: Tại sao Hybrid Search? (1 phút) — Người trình bày: An

> Xin chào mọi người, mình là An. Mình xin giải thích lý do tại sao chúng ta bắt buộc phải kết hợp hai phương pháp này.
>
> Bản chất là vì mỗi phương pháp đều có điểm mạnh và điểm yếu riêng biệt:
> - **Keyword Search (Tìm kiếm từ khóa)** cực giỏi khi đối khớp chính xác (Exact Match) như tên riêng, mã sản phẩm (ví dụ "ResNet-50"), viết tắt... nhưng thất bại khi người dùng dùng từ đồng nghĩa hoặc paraphrase.
> - **Semantic Search (Tìm kiếm ngữ nghĩa)** cực mạnh khi hiểu ý định người dùng, truy vấn bằng ngôn ngữ tự nhiên... nhưng tốn tài nguyên và dễ bỏ sót các từ khóa đặc biệt, mã sản phẩm.
>
> Do đó, **Hybrid Search (Tìm kiếm kết hợp)** ra đời để lấy điểm mạnh của phương pháp này bù đắp cho điểm yếu của phương pháp kia. Đây là kiến trúc tiêu chuẩn đang được áp dụng trong Elasticsearch 8.x, Azure AI Search, Pinecone, v.v.

---

### Slide 10: Rank Fusion (1.5 phút) — Người trình bày: An

> Thử thách lớn nhất của Hybrid Search là: làm thế nào để gộp điểm số từ 2 danh sách kết quả (Keyword và Semantic) khi chúng ở hai thang đo hoàn toàn khác nhau (điểm BM25 có thể từ 0 đến hàng chục, còn điểm Cosine luôn từ -1 đến 1)?
>
> Có hai hướng tiếp cận:
> - **Score-level Fusion**: Cộng điểm trực tiếp sau khi chuẩn hóa. Cách này đòi hỏi phải thiết lập trọng số alpha và rất nhạy cảm với phân phối điểm số.
> - **Rank-level Fusion (tiêu biểu là RRF - Reciprocal Rank Fusion)**: Ý tưởng rất đột phá là **bỏ qua điểm số, chỉ sử dụng thứ hạng**.
> Công thức RRF tính điểm của một tài liệu bằng tổng nghịch đảo thứ hạng của nó trên các danh sách, cộng thêm một hằng số k (mặc định k = 60). Phương pháp này hoàn toàn không cần chuẩn hóa điểm số hay tối ưu tham số (parameter-free), và hiện là giải pháp gộp mặc định trong Elasticsearch.

---

### Slide 11: RRF Ví dụ (1 phút) — Người trình bày: An

> Hãy cùng nhìn vào một ví dụ minh họa trực quan cho thuật toán RRF.
>
> Với truy vấn "transformer architecture for NLP tasks", hệ thống chạy song song:
> - Tìm kiếm từ khóa trả về top tài liệu với tài liệu D_A xếp thứ 1.
> - Tìm kiếm ngữ nghĩa trả về top tài liệu với tài liệu D_A xếp thứ 2.
>
> Áp dụng công thức RRF với hằng số k = 60:
> - Điểm RRF của D_A = 1/(60+1) + 1/(60+2) = 0.0325. Đây là điểm số cao nhất.
> - Tài liệu D_C xếp thứ 3 ở danh sách từ khóa và thứ 1 ở danh sách ngữ nghĩa đạt điểm 0.0323, xếp ngay sau D_A.
>
> **Key insight**: Những tài liệu nằm ở **vị trí cao trên cả hai danh sách** sẽ được thuật toán RRF ưu tiên đẩy lên top đầu của kết quả cuối cùng.

---

### Slide 12: Case Study 1 — E-commerce (1.5 phút) — Người trình bày: An

> Để thấy rõ hiệu quả, hãy xem Case Study đầu tiên về Tìm kiếm trong Thương mại điện tử (Shopee, Amazon).
>
> Truy vấn của người mua hàng được chia làm 3 nhóm rõ rệt:
> 1. **Nhóm tìm chính xác (Exact)**: "iPhone 15 Pro Max 256GB" -> Tìm kiếm từ khóa sẽ hoạt động hoàn hảo để trả về đúng sản phẩm.
> 2. **Nhóm tìm theo ý định (Semantic)**: "quà sinh nhật cho bạn gái" -> Không có sản phẩm nào tên là "quà sinh nhật". Tìm kiếm từ khóa sẽ trả về 0 kết quả. Nhưng Tìm kiếm ngữ nghĩa sẽ hiểu ý và gợi ý mỹ phẩm, trang sức, hoa tươi...
> 3. **Nhóm hỗn hợp (Mixed)**: "áo khoác chống nước đi mưa" -> Từ khóa sẽ bắt từ "áo khoác", ngữ nghĩa sẽ hiểu "chống nước" tương đương "waterproof".
>
> Kiến trúc Hybrid Search gom hai nhánh lại qua bộ gộp RRF giúp **tăng tỷ lệ chuyển đổi mua hàng (conversion rate) từ 15-25%** và **giảm tỷ lệ tìm kiếm không ra kết quả (zero-result) tới 40-60%**.

---

### Slide 13: Case Study 2 — Project nhóm (1 phút) — Người trình bày: An

> Case Study thứ hai là hệ thống tìm kiếm bài báo khoa học do nhóm mình tự phát triển trên tập dữ liệu **1.2 triệu bài báo từ arXiv**.
>
> Kết quả đánh giá bằng chỉ số NDCG@10 (chỉ số đo lường chất lượng xếp hạng kết quả) cho thấy:
> - Tìm kiếm từ khóa đạt khoảng 0.64 - 0.70.
> - Tìm kiếm ngữ nghĩa đạt khoảng 0.66 - 0.68.
> - Nhưng khi kết hợp **Hybrid Search, điểm số NDCG tăng vượt trội lên 0.95 - 0.98**.
>
> Phân tích sâu hơn, chúng mình phát hiện hai danh sách kết quả từ hai nhánh chỉ **trùng nhau 1.5 trên 10 tài liệu** (overlap 15%). Điều này chứng minh hai phương pháp này tìm ra các kết quả rất khác nhau và bổ trợ cho nhau cực tốt.
>
> Về công nghệ, nhóm sử dụng Elasticsearch 8.12, mô hình embedding `all-MiniLM-L6-v2`, thuật toán RRF (k=60), backend FastAPI và frontend React.

---

### Slide 14: Key Takeaways & Xu hướng (1.5 phút) — Người trình bày: An

> Mình xin tóm tắt lại 3 thông điệp cốt lõi (Key Takeaways):
> 1. Tìm kiếm từ khóa và ngữ nghĩa là hai trường phái **bổ trợ cho nhau**, không thay thế nhau. Kết hợp chúng luôn mang lại kết quả tốt nhất.
> 2. **RRF** là phương pháp gộp kết quả đơn giản, cực kỳ hiệu quả và không tốn công tối ưu hóa tham số.
> 3. **Tìm kiếm xấp xỉ (ANN)**, đặc biệt là đồ thị HNSW, là chìa khóa để triển khai tìm kiếm vector trên quy mô hàng triệu tài liệu với thời gian thực.
>
> Về xu hướng tương lai, chúng ta sẽ thấy sự bùng nổ của:
> - **RAG (Retrieval-Augmented Generation)**: Đưa kết quả Hybrid Search làm ngữ cảnh cho các mô hình ngôn ngữ lớn (LLM) như ChatGPT.
> - **Learned Sparse Models (SPLADE, ColBERT)**: Tích hợp cả tìm kiếm từ khóa và ngữ nghĩa vào trong một mô hình duy nhất.
> - **Multimodal Search**: Cho phép tìm kiếm kết hợp cả văn bản, hình ảnh và âm thanh cùng lúc.

---

### Slide 15: Q&A (tùy) — Người trình bày: An (điều phối chính)

> Cảm ơn thầy và các bạn đã chú ý lắng nghe bài thuyết trình của nhóm! Sau đây nhóm xin phép bước vào phần thảo luận và trả lời câu hỏi từ thầy cũng như các bạn.
>
> *(Nếu thầy hoặc các bạn đặt câu hỏi đi sâu vào kỹ thuật → An và Lâm sẽ hỗ trợ chiếu và trả lời các slide backup tương ứng).*

---

## [CÁC SLIDE BACKUP - HỖ TRỢ TRẢ LỜI Q&A]

### Backup Slide 16: Latency Benchmark — Người phụ trách trả lời: Lâm

> *(Chỉ dùng khi được hỏi về hiệu năng hoặc latency)*
>
> Ở quy mô nhỏ 100k tài liệu, thời gian phản hồi của tất cả các phương pháp đều dưới 60ms. Tuy nhiên khi lên quy mô 1.2 triệu tài liệu, tìm kiếm chính xác (kNN) gặp hiện tượng "cold start" (độ trễ P95 lên tới 1206ms) do phải load đồ thị HNSW từ đĩa SSD vào RAM lần đầu. Sau khi cache được làm ấm (warm-up), thời gian tìm kiếm Hybrid rút ngắn chỉ còn 99ms (P50), hoàn toàn đáp ứng thời gian thực.
>
> Về dung lượng lưu trữ tăng tuyến tính, từ 860MB (100k) lên 11.9GB (1.2M), trong đó dữ liệu vector chiếm tới 87% dung lượng lưu trữ.

---

### Backup Slide 17: BM25 Step-by-step — Người phụ trách trả lời: An hoặc Lâm

> *(Chỉ dùng khi được hỏi chi tiết về cách tính toán điểm BM25)*
>
> Bảng này minh họa cách tính điểm BM25 chi tiết cho câu truy vấn "attention mechanism" trên tài liệu D42 ("Attention Is All You Need").
>
> Đầu tiên, bộ phân tách (Analyzer) tách câu truy vấn thành các token gốc `attent` và `mechan`. Sau khi tra cứu Inverted Index, ta tính được tần suất từ (TF), tần suất tài liệu chứa từ (IDF), áp dụng hệ số phạt độ dài tài liệu và nhân hệ số boost tiêu đề (x2) thu được tổng điểm 12.8.
>
> Slide này cũng cho thấy ví dụ Tìm kiếm từ khóa **thất bại** khi người dùng tìm kiếm "methods to detect fake images" vì tài liệu đích sử dụng từ chuyên ngành "deepfake detection" (không có từ nào trùng với từ khóa truy vấn). Đây là lý do ta bắt buộc phải sử dụng tìm kiếm ngữ nghĩa hỗ trợ.
