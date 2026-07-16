# 📝 CÂU HỎI TRẮC NGHIỆM ÔN TẬP (60+ CÂU)

> **Cấu trúc đề thi**: 20 câu trắc nghiệm = 5 điểm  
> **Cách dùng**: Làm bài → kiểm tra đáp án ở cuối mỗi phần → xem giải thích

---

## PHẦN 1: LSH (10 CÂU)

**Câu 1**: Mục đích chính của LSH (Locality Sensitive Hashing) là gì?

A. Mã hóa dữ liệu bảo mật  
B. **Tìm nhanh các cặp items tương tự trong tập dữ liệu lớn** ✅  
C. Sắp xếp dữ liệu  
D. Nén dữ liệu

> 💡 LSH giảm O(n²) pairwise comparison xuống gần O(n)

---

**Câu 2**: Pipeline LSH gồm 3 bước theo thứ tự:

A. Hashing → Clustering → Filtering  
B. MinHash → Shingling → Banding  
C. **Shingling → MinHashing → LSH Banding** ✅  
D. Sampling → Hashing → Comparing

---

**Câu 3**: Jaccard Similarity của A = {1,2,3,4} và B = {2,3,4,5,6} là bao nhiêu?

A. 4/6  
B. **3/6 = 0.5** ✅  
C. 3/4  
D. 4/5

> 💡 A∩B = {2,3,4} = 3 phần tử. A∪B = {1,2,3,4,5,6} = 6 phần tử. J = 3/6

---

**Câu 4**: Tính chất quan trọng nhất của MinHash là gì?

A. MinHash luôn cho kết quả chính xác  
B. MinHash nhanh hơn Jaccard  
C. **P(MinHash(A) = MinHash(B)) = Jaccard(A, B)** ✅  
D. MinHash không cần hàm hash

> 💡 Xác suất 2 tập có cùng MinHash = đúng bằng Jaccard Similarity

---

**Câu 5**: Trong LSH Banding, signature có 100 thành phần chia thành b=20 bands, r=5 rows/band. Threshold t xấp xỉ bao nhiêu?

A. 0.20  
B. 0.80  
C. **0.55** ✅  
D. 0.95

> 💡 t ≈ (1/b)^(1/r) = (1/20)^(1/5) = 0.05^0.2 ≈ 0.55

---

**Câu 6**: Khi tăng số bands (b), điều gì xảy ra?

A. Threshold tăng, ít false positives  
B. **Threshold giảm, nhiều false positives, ít false negatives** ✅  
C. Không ảnh hưởng gì  
D. Tốc độ giảm

---

**Câu 7**: Công thức tính xác suất 2 documents là candidate pair khi Jaccard = s?

A. s^b  
B. (1 - s^r)^b  
C. **1 - (1 - s^r)^b** ✅  
D. 1 - s^(b×r)

---

**Câu 8**: LSH cho Cosine Similarity sử dụng kỹ thuật gì?

A. MinHash  
B. **Random Hyperplanes** ✅  
C. Bloom Filter  
D. Reservoir Sampling

> 💡 P(h(u)=h(v)) = 1 - θ/π

---

**Câu 9**: Cho h(x) = (2x + 1) mod 5. Tính h(0), h(1), h(2):

A. 0, 1, 2  
B. **1, 3, 0** ✅  
C. 1, 2, 3  
D. 2, 4, 1

> 💡 h(0) = (0+1)%5 = 1, h(1) = (2+1)%5 = 3, h(2) = (4+1)%5 = 0

---

**Câu 10**: b=5, r=3, s=0.8. P(candidate pair) = ?

A. 0.512  
B. 0.718  
C. **0.972** ✅  
D. 0.999

> 💡 s^r = 0.8^3 = 0.512. 1-0.512 = 0.488. 0.488^5 = 0.028. P = 1-0.028 = 0.972

---

## PHẦN 2: CLUSTERING (10 CÂU)

**Câu 11**: K-means sử dụng độ đo khoảng cách mặc định nào?

A. Manhattan  
B. Cosine  
C. **Euclidean** ✅  
D. Jaccard

---

**Câu 12**: Nhược điểm nào KHÔNG phải của K-means?

A. Phải chọn trước K  
B. Nhạy cảm với outliers  
C. **Cần xây dựng dendrogram** ✅  
D. Có thể rơi vào local optimum

> 💡 Dendrogram là của Hierarchical Clustering, không phải K-means

---

**Câu 13**: Trong K-means++, centroid tiếp theo được chọn với xác suất tỉ lệ với:

A. 1/D(x)  
B. D(x)  
C. **D(x)²** ✅  
D. log(D(x))

> 💡 D(x) = khoảng cách tới centroid gần nhất. P ∝ D(x)²

---

**Câu 14**: Trong BFR, mỗi cluster được tóm tắt bằng:

A. Centroid và bán kính  
B. **N, SUM, SUMSQ** ✅  
C. Tất cả các điểm dữ liệu  
D. Mean và variance

> 💡 Từ (N, SUM, SUMSQ) có thể tính mean = SUM/N và variance = SUMSQ/N - (SUM/N)²

---

**Câu 15**: BFR algorithm có 3 tập hợp. Tập nào chứa các outliers?

A. Discard Set (DS)  
B. Compression Set (CS)  
C. **Retained Set (RS)** ✅  
D. Không có tập nào

---

**Câu 16**: CURE algorithm khác K-means chủ yếu ở điểm nào?

A. CURE nhanh hơn  
B. CURE dùng Euclidean distance  
C. **CURE dùng nhiều representative points thay vì 1 centroid** ✅  
D. CURE cần chọn K trước

---

**Câu 17**: Trong BFR, khi merge 2 clusters (N₁,SUM₁,SUMSQ₁) và (N₂,SUM₂,SUMSQ₂), N mới = ?

A. max(N₁, N₂)  
B. N₁ × N₂  
C. **N₁ + N₂** ✅  
D. (N₁ + N₂) / 2

---

**Câu 18**: Trong text clustering, độ đo khoảng cách phù hợp nhất là:

A. Euclidean  
B. Manhattan  
C. **Cosine** ✅  
D. Hamming

> 💡 Cosine không phụ thuộc vào độ dài document

---

**Câu 19**: Single linkage trong HAC sử dụng:

A. Khoảng cách trung bình  
B. Khoảng cách lớn nhất  
C. **Khoảng cách nhỏ nhất** ✅  
D. Tổng khoảng cách

---

**Câu 20**: Mahalanobis Distance trong BFR dùng để:

A. Tính centroid mới  
B. Merge 2 clusters  
C. **Quyết định điểm mới có đủ gần cluster để thêm vào DS** ✅  
D. Khởi tạo K centroids

---

## PHẦN 3: RECOMMENDER SYSTEMS (8 CÂU)

**Câu 21**: Content-Based Filtering gợi ý dựa trên:

A. Hành vi users tương tự  
B. **Đặc trưng items tương tự với items user đã thích** ✅  
C. Ma trận phân rã  
D. Xu hướng phổ biến

---

**Câu 22**: Trong Collaborative Filtering, phương pháp tốt nhất để tính user similarity khi các user có scale đánh giá khác nhau là:

A. Euclidean distance  
B. Jaccard similarity  
C. Cosine similarity  
D. **Pearson Correlation** ✅

> 💡 Pearson normalize mức đánh giá → user rate 1-3 và user rate 3-5 vẫn so sánh được

---

**Câu 23**: Cold Start problem xảy ra khi:

A. Hệ thống chạy chậm  
B. **User mới hoặc item mới chưa có rating** ✅  
C. Ma trận ratings quá dày  
D. Thuật toán không hội tụ

---

**Câu 24**: Matrix Factorization R ≈ P × Q^T, trong đó d là:

A. Số users  
B. Số items  
C. **Số latent factors (nhân tố tiềm ẩn)** ✅  
D. Số ratings

---

**Câu 25**: Nhược điểm chính của Content-Based Filtering là:

A. Cần nhiều users  
B. Chậm  
C. **Overspecialization — chỉ gợi ý items giống cái đã thích** ✅  
D. Không xử lý được new items

---

**Câu 26**: Item-Item CF thường ổn định hơn User-User CF vì:

A. Items ít hơn users  
B. **Items ít thay đổi theo thời gian hơn users** ✅  
C. Items dễ tính hơn  
D. Item-Item nhanh hơn

---

**Câu 27**: Netflix Prize chứng minh rằng:

A. Collaborative Filtering là tốt nhất  
B. Content-Based là tốt nhất  
C. **Cần kết hợp (ensemble) nhiều phương pháp** ✅  
D. Deep Learning là tốt nhất

---

**Câu 28**: Để giải quyết Cold Start cho New Item, phương pháp phù hợp nhất là:

A. User-User CF  
B. **Content-Based Filtering** ✅  
C. Matrix Factorization  
D. Popularity-based

> 💡 Content-Based dùng metadata/features của item → không cần ratings

---

## PHẦN 4: PAGERANK & GRAPH (7 CÂU)

**Câu 29**: PageRank mô phỏng hành vi của:

A. Crawler  
B. **Random Surfer (người lướt web ngẫu nhiên)** ✅  
C. Search Engine  
D. Indexer

---

**Câu 30**: Spider Trap trong PageRank gây ra vấn đề gì?

A. PageRank rò rỉ về 0  
B. **Nhóm trang hấp thụ toàn bộ PageRank** ✅  
C. Ma trận không hội tụ  
D. Trang web bị xóa

---

**Câu 31**: Damping factor β = 0.8 nghĩa là:

A. 80% teleport, 20% follow link  
B. **80% follow link, 20% teleport ngẫu nhiên** ✅  
C. 80% PageRank được giữ  
D. 80% trang được index

---

**Câu 32**: Dead End (trang không có outgoing link) gây ra vấn đề gì?

A. Spider trap  
B. Trang bị xóa  
C. **PageRank rò rỉ → tổng PR → 0** ✅  
D. Ma trận không khả nghịch

---

**Câu 33**: Trong HITS, Authority score cao nghĩa là:

A. Trang link tới nhiều trang khác  
B. **Trang được nhiều Hub chất lượng link tới** ✅  
C. Trang có nhiều content  
D. Trang có PageRank cao

---

**Câu 34**: Cho graph: A→B, A→C, B→C, C→A. Ma trận transition M[j][i] cho cột A là:

A. [0, 1, 0]  
B. [0, 0, 1]  
C. **[0, 1/2, 1/2]** ✅  
D. [1/3, 1/3, 1/3]

> 💡 A có 2 outgoing links (B, C) → mỗi link chia 1/2. M[B][A]=1/2, M[C][A]=1/2

---

**Câu 35**: Power Iteration khởi tạo vector r với:

A. Random values  
B. Zeros  
C. **[1/n, 1/n, ..., 1/n]** ✅  
D. [1, 0, 0, ..., 0]

---

## PHẦN 5: DIMENSIONALITY REDUCTION (5 CÂU)

**Câu 36**: SVD phân rã ma trận A thành:

A. A = L × D × L^T  
B. **A = U × Σ × V^T** ✅  
C. A = P × Q^T  
D. A = C × U × R

---

**Câu 37**: Singular values trong Σ được sắp xếp theo thứ tự:

A. Tăng dần  
B. **Giảm dần** ✅  
C. Ngẫu nhiên  
D. Theo alphabet

---

**Câu 38**: CUR decomposition ưu việt hơn SVD khi:

A. Ma trận nhỏ và dense  
B. Cần kết quả chính xác tuyệt đối  
C. **Ma trận lớn và thưa (sparse)** ✅  
D. Ma trận vuông

> 💡 CUR giữ sparsity và dùng columns/rows thật → dễ giải thích

---

**Câu 39**: Cho SVD có singular values σ = {10, 5, 2, 1}. Energy retained khi giữ 2 thành phần?

A. 10/18 = 55.6%  
B. 15/18 = 83.3%  
C. **125/130 ≈ 96.2%** ✅  
D. 100/130 ≈ 76.9%

> 💡 Energy = (10²+5²)/(10²+5²+2²+1²) = 125/130 ≈ 96.2%

---

**Câu 40**: PCA bước đầu tiên là:

A. Tính eigenvalues  
B. Chọn k components  
C. **Chuẩn hóa dữ liệu (trừ mean)** ✅  
D. Tính covariance matrix

---

## PHẦN 6: DATA STREAMING (10 CÂU)

**Câu 41**: Bloom Filter có thể xảy ra loại lỗi nào?

A. False Negative  
B. **False Positive** ✅  
C. Cả hai  
D. Không có lỗi

> 💡 ⚠️ Bloom Filter: NO false negatives. Có false positives.

---

**Câu 42**: Bloom Filter query: nếu BẤT KỲ bit nào = 0, kết quả là:

A. Có thể có  
B. Không chắc  
C. **CHẮC CHẮN KHÔNG CÓ** ✅  
D. Cần kiểm tra thêm

---

**Câu 43**: Flajolet-Martin algorithm ước lượng số phần tử distinct ≈ ?

A. 2^n (n là tổng phần tử)  
B. R (số trailing zeros lớn nhất)  
C. **2^R (R = max trailing zeros)** ✅  
D. log(R)

---

**Câu 44**: DGIM algorithm có sai số tối đa bao nhiêu?

A. 10%  
B. 25%  
C. **50%** ✅  
D. 100%

---

**Câu 45**: Trong DGIM, khi có 3 buckets cùng size, cần:

A. Xóa 1 bucket  
B. **Merge 2 buckets CŨ NHẤT thành 1 bucket gấp đôi** ✅  
C. Chia thành 6 buckets nhỏ hơn  
D. Giữ nguyên

---

**Câu 46**: Reservoir Sampling giữ k mẫu. Element thứ i (i > k) được thêm với xác suất:

A. 1/k  
B. k/(k+1)  
C. **k/i** ✅  
D. i/k

---

**Câu 47**: AMS algorithm ước lượng F₂ = Σfᵢ². Estimate cho mỗi biến là:

A. n × c  
B. n × c²  
C. **n × (2c - 1)** ✅  
D. 2^c

> 💡 c = số lần xuất hiện từ vị trí được chọn trở đi

---

**Câu 48**: Optimal k (số hàm hash) cho Bloom Filter là:

A. m × n  
B. n/m  
C. **k = (m/n) × ln2** ✅  
D. √(m×n)

---

**Câu 49**: Bộ nhớ DGIM cần bao nhiêu?

A. O(N)  
B. O(N log N)  
C. **O(log²N)** ✅  
D. O(√N)

---

**Câu 50**: F₂ (Second Frequency Moment) đo:

A. Số phần tử distinct  
B. Chiều dài stream  
C. **Mức độ lệch (skew) phân phối — "surprise number"** ✅  
D. Phần tử xuất hiện nhiều nhất

---

## PHẦN 7: MAPREDUCE & SPARK (10 CÂU)

**Câu 51**: Combiner trong MapReduce có thể dùng cho phép toán nào?

A. Average  
B. Median  
C. **Sum, Max, Min** ✅  
D. Standard deviation

> 💡 Combiner chỉ cho associative + commutative operations

---

**Câu 52**: Trong Spark, reduceByKey là:

A. Action  
B. **Transformation** ✅  
C. Cả hai  
D. Không phải RDD operation

---

**Câu 53**: Lazy Evaluation trong Spark nghĩa là:

A. Spark chạy chậm  
B. **Transformations chỉ được ghi nhận, chưa thực thi cho đến khi có Action** ✅  
C. Spark bỏ qua các phép tính không cần  
D. Data được load chậm

---

**Câu 54**: Spark nhanh hơn MapReduce chủ yếu nhờ:

A. Thuật toán tốt hơn  
B. Dùng GPU  
C. **Xử lý in-memory (RAM) thay vì disk** ✅  
D. Code ngắn hơn

---

**Câu 55**: Narrow transformation trong Spark là:

A. Transformation cần shuffle  
B. **Transformation mỗi partition input → 1 partition output (KHÔNG shuffle)** ✅  
C. Transformation trả về ít dữ liệu  
D. Transformation nhanh

> 💡 Narrow: map, filter. Wide (cần shuffle): groupByKey, reduceByKey, join

---

**Câu 56**: RDD trong Spark có 3 đặc tính:

A. Read-only, Dynamic, Distributed  
B. **Resilient, Distributed, Dataset (Immutable)** ✅  
C. Real-time, Deterministic, Distributed  
D. Redundant, Durable, Dataset

---

**Câu 57**: Broadcast variable trong Spark là:

A. Biến ghi được  
B. **Biến read-only, cache trên mỗi worker** ✅  
C. Biến chia sẻ giữa drivers  
D. Biến mã hóa

---

**Câu 58**: Communication Cost trong MapReduce là:

A. Thời gian chạy  
B. Số reducer  
C. **r × |I| (replication rate × input size)** ✅  
D. Bandwidth mạng

---

**Câu 59**: Natural Join R(A,B) ⋈ S(B,C) bằng MapReduce, key emit là:

A. A  
B. **B (cột join chung)** ✅  
C. C  
D. (A, C)

---

**Câu 60**: Khi nào nên dùng cache()/persist() trong Spark?

A. Mọi RDD  
B. RDD đầu tiên  
C. **RDD được sử dụng NHIỀU LẦN** ✅  
D. RDD lớn

---

## PHẦN 8: VISUALIZATION (4 CÂU)

**Câu 61**: Choropleth map nên dùng dữ liệu dạng:

A. Tổng (total count)  
B. **Tỷ lệ (rate/per capita)** ✅  
C. Số tuyệt đối  
D. Ranking

> 💡 Dùng total → bias bởi dân số (bang đông dân luôn cao hơn)

---

**Câu 62**: Lie Factor = 1 nghĩa là:

A. Chart bị lừa  
B. **Chart trung thực, visual thay đổi đúng tỉ lệ data** ✅  
C. Chart hoàn hảo  
D. Chart không có nghĩa

---

**Câu 63**: Để hiển thị mối quan hệ giữa 2 biến số, chart phù hợp nhất là:

A. Bar Chart  
B. Pie Chart  
C. **Scatter Plot** ✅  
D. Line Chart

---

**Câu 64**: Parallel Coordinates phù hợp cho:

A. Time series  
B. Geographic data  
C. **Dữ liệu đa chiều (multivariate)** ✅  
D. Text data

---

## 🎯 BẢNG ĐÁP ÁN NHANH

| Câu | Đáp án | Câu | Đáp án | Câu | Đáp án | Câu | Đáp án |
|-----|--------|-----|--------|-----|--------|-----|--------|
| 1 | B | 17 | C | 33 | B | 49 | C |
| 2 | C | 18 | C | 34 | C | 50 | C |
| 3 | B | 19 | C | 35 | C | 51 | C |
| 4 | C | 20 | C | 36 | B | 52 | B |
| 5 | C | 21 | B | 37 | B | 53 | B |
| 6 | B | 22 | D | 38 | C | 54 | C |
| 7 | C | 23 | B | 39 | C | 55 | B |
| 8 | B | 24 | C | 40 | C | 56 | B |
| 9 | B | 25 | C | 41 | B | 57 | B |
| 10 | C | 26 | B | 42 | C | 58 | C |
| 11 | C | 27 | C | 43 | C | 59 | B |
| 12 | C | 28 | B | 44 | C | 60 | C |
| 13 | C | 29 | B | 45 | B | 61 | B |
| 14 | B | 30 | B | 46 | C | 62 | B |
| 15 | C | 31 | B | 47 | C | 63 | C |
| 16 | C | 32 | C | 48 | C | 64 | C |

---

> 💡 **Mẹo**: Nếu sai nhiều câu ở phần nào → quay lại đọc chương tương ứng  
> Phần hay thi nhiều nhất: **LSH** (S-curve), **Streaming** (Bloom Filter, FM), **Clustering** (BFR)
