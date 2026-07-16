# 📝 PHẦN TỰ LUẬN: ỨNG DỤNG BIG DATA (5 CÂU — 5 ĐIỂM)

> **Cấu trúc**: Mỗi câu hỏi về ỨNG DỤNG Big Data trong 1 lĩnh vực cụ thể  
> **Yêu cầu**: Phải ghi CỤ THỂ cách xây dựng hệ thống Big Data, không chỉ nêu chung chung  
> **Các lĩnh vực thường gặp**: Nông nghiệp, Giao thông, Giáo dục, Môi trường, Y tế, Khuyến nghị

---

## ⭐ TEMPLATE TRẢ LỜI TỰ LUẬN (ÁP DỤNG CHO MỌI LĨNH VỰC)

Mỗi câu nên trả lời theo **5 phần**:

```
1. BÀI TOÁN (Problem): Vấn đề cần giải quyết là gì?
2. NGUỒN DỮ LIỆU (Data Sources): Thu thập data từ đâu? Loại data gì?
3. KIẾN TRÚC HỆ THỐNG (Architecture): Pipeline xử lý dữ liệu
4. KỸ THUẬT BIG DATA (Techniques): Thuật toán/mô hình nào được áp dụng?
5. KẾT QUẢ & GIÁ TRỊ (Output/Value): Hệ thống đem lại gì?
```

### ⭐ Kiến trúc chung (vẽ được sơ đồ này là ăn điểm)

```
[Data Sources] → [Data Ingestion] → [Storage] → [Processing] → [Analytics] → [Visualization/Action]
   Sensors         Kafka/Flume       HDFS/S3     Spark/MR        ML/DL          Dashboard/Alert
   IoT             NiFi              NoSQL       Streaming       Clustering      Report
   APIs            Sqoop             Data Lake   Batch           RecSys          Notification
   Social Media                                                  PageRank
```

---

## CÂU 1: ỨNG DỤNG BIG DATA TRONG NÔNG NGHIỆP 🌾

### 1. Bài toán
**Nông nghiệp chính xác (Precision Agriculture)**: Tối ưu hóa tưới tiêu, bón phân, phun thuốc, dự báo sâu bệnh dựa trên dữ liệu thực tế.

### 2. Nguồn dữ liệu

| Nguồn | Loại dữ liệu | Volume |
|-------|-------------|--------|
| **Sensors IoT** | Nhiệt độ, độ ẩm đất, pH, ánh sáng | Streaming, hàng triệu datapoints/ngày |
| **Drone/Vệ tinh** | Ảnh NDVI (chỉ số xanh thực vật) | Batch, hàng TB dữ liệu ảnh |
| **Trạm thời tiết** | Nhiệt độ, lượng mưa, gió | Time-series |
| **Lịch sử mùa vụ** | Năng suất, giống, phân bón | Structured data |

### 3. Kiến trúc hệ thống

```
Sensors IoT  ──→  Apache Kafka (message queue)
Drone images ──→  HDFS / S3 (lưu trữ)
Weather API  ──→  Apache NiFi (data ingestion)
                       ↓
              Apache Spark Streaming
              (xử lý real-time: phát hiện bất thường)
                       ↓
              Spark MLlib / TensorFlow
              (dự đoán sâu bệnh, tối ưu tưới tiêu)
                       ↓
              Dashboard + Mobile Alert
              (nông dân nhận cảnh báo trên điện thoại)
```

### 4. Kỹ thuật Big Data áp dụng

| Kỹ thuật | Ứng dụng cụ thể |
|----------|-----------------|
| **Data Streaming** (Chương 6) | Xử lý real-time dữ liệu sensors; Bloom Filter lọc sensor lỗi |
| **Clustering** (K-means) | Phân vùng đất theo đặc tính (soil zoning) |
| **Regression/ML** | Dự đoán năng suất dựa trên weather + soil features |
| **MapReduce** | Batch processing ảnh vệ tinh lớn |
| **Time Series Analysis** | Dự báo thời tiết, xu hướng sâu bệnh |

### 5. Kết quả & Giá trị
- **Tiết kiệm 20-30% nước tưới** nhờ tưới đúng lúc, đúng lượng
- **Giảm 15-20% chi phí phân bón** nhờ bón đúng vùng
- **Phát hiện sớm sâu bệnh** → giảm thiệt hại mùa vụ
- **Tăng năng suất 10-15%** nhờ quyết định dựa trên dữ liệu

---

## CÂU 2: ỨNG DỤNG BIG DATA TRONG GIAO THÔNG 🚗

### 1. Bài toán
**Hệ thống giao thông thông minh (ITS)**: Giám sát, dự đoán tắc đường, tối ưu tín hiệu đèn, phát hiện tai nạn real-time.

### 2. Nguồn dữ liệu

| Nguồn | Loại dữ liệu | Đặc điểm |
|-------|-------------|-----------|
| **Camera giám sát** | Video, nhận diện biển số | Streaming, dung lượng lớn |
| **GPS taxi/xe buýt** | Tọa độ, tốc độ, hướng | Streaming, millions points/phút |
| **Cảm biến đường** | Lưu lượng xe, tốc độ trung bình | IoT streaming |
| **Ứng dụng di động** | Google Maps, Grab | Crowdsourced data |
| **Dữ liệu lịch sử** | Tai nạn, sự kiện, thời tiết | Batch |

### 3. Kiến trúc hệ thống

```
GPS Devices    ──→  Apache Kafka
Traffic Camera ──→  (real-time stream)
Road Sensors   ──→        ↓
                   Spark Streaming
                   (xử lý real-time: phát hiện tắc, tai nạn)
                          ↓
                   ┌──────┴──────┐
                   ↓              ↓
             Real-time         Batch (Spark/MR)
             Dashboard         (phân tích pattern,
             + Alert           dự đoán tắc đường)
                                    ↓
                              ML Models
                              (dự đoán thời gian di chuyển)
                                    ↓
                              Google Maps-like
                              Navigation App
```

### 4. Kỹ thuật Big Data áp dụng

| Kỹ thuật | Ứng dụng cụ thể |
|----------|-----------------|
| **Data Streaming** | Xử lý GPS real-time; DGIM đếm xe qua trạm trong sliding window |
| **PageRank/Graph** | Tìm nút giao quan trọng nhất trong mạng lưới đường |
| **Clustering** (DBSCAN) | Phát hiện hotspot tắc đường, khu vực hay tai nạn |
| **Flajolet-Martin** | Ước lượng số xe riêng biệt đi qua trạm |
| **MapReduce** | Xử lý batch data lịch sử giao thông |
| **Recommender System** | Gợi ý tuyến đường tối ưu cho từng user |

### 5. Kết quả & Giá trị
- **Giảm 15-25% thời gian di chuyển** nhờ định tuyến thông minh
- **Phát hiện tai nạn trong vài giây** → cứu hộ nhanh hơn
- **Tối ưu đèn tín hiệu** giảm 20% thời gian chờ
- **Dự đoán tắc đường** trước 30 phút → người lái chọn đường khác

---

## CÂU 3: ỨNG DỤNG BIG DATA TRONG GIAO THÔNG (BÀI 2) — Quản lý xe buýt công cộng 🚌

### 1. Bài toán
**Tối ưu hóa hệ thống xe buýt công cộng**: Dự đoán thời gian đến, tối ưu tuyến, phân tích nhu cầu hành khách.

### 2. Nguồn dữ liệu
- GPS trên xe buýt (vị trí real-time)
- Thẻ quẹt hành khách (IC card)
- Dữ liệu lịch sử: thời gian, tuyến, lưu lượng
- Thời tiết, sự kiện, lịch lễ

### 3. Kiến trúc
```
Bus GPS ──→ Kafka ──→ Spark Streaming ──→ ETA Prediction
IC Card ──→ HDFS  ──→ Spark Batch     ──→ Demand Analysis
Weather ──→                            ──→ Route Optimization
```

### 4. Kỹ thuật Big Data

| Kỹ thuật | Ứng dụng |
|----------|---------|
| **Streaming (Kafka + Spark)** | Real-time tracking vị trí xe buýt |
| **Clustering** | Phân nhóm trạm theo lưu lượng → tối ưu tần suất |
| **Regression** | Dự đoán ETA (Estimated Time of Arrival) |
| **AMS Algorithm** | Ước lượng moments của phân phối hành khách |
| **Graph/PageRank** | Tìm trạm quan trọng nhất trong mạng lưới |

### 5. Giá trị
- Hành khách biết chính xác khi nào xe đến
- Tối ưu tuyến + tần suất theo nhu cầu thực tế
- Giảm xe rỗng, tiết kiệm nhiên liệu

---

## CÂU 4: ỨNG DỤNG BIG DATA TRONG GIÁO DỤC 📚

> ⚠️ **Lưu ý**: Câu giáo dục phải ghi CỤ THỂ cách xây dựng hệ thống Big Data

### 1. Bài toán
**Learning Analytics & Adaptive Learning**: Phân tích hành vi học sinh để cá nhân hóa việc học, dự đoán học sinh có nguy cơ bỏ học, đánh giá hiệu quả giảng dạy.

### 2. Nguồn dữ liệu

| Nguồn | Loại dữ liệu | Ví dụ |
|-------|-------------|-------|
| **LMS** (Moodle, Canvas) | Logs hoạt động | Thời gian online, bài nộp, điểm |
| **Hệ thống thi online** | Kết quả thi, thời gian làm bài | Câu đúng/sai, thời gian/câu |
| **Video lecture** | Xem/pause/rewind | Đoạn nào hay bị rewind |
| **Forum/Chat** | Text, sentiment | Câu hỏi, phản hồi |
| **Thông tin SV** | Demographics | GPA, lớp, khoa, năm |

### 3. Kiến trúc hệ thống CỤ THỂ

```
┌──────────────────────────────────────────────────────────┐
│                    DATA SOURCES                           │
│  LMS Logs ──┐                                            │
│  Exam Data ─┤                                            │
│  Video Logs ┤──→ Apache Kafka / Flume (Data Ingestion)   │
│  Forum Text ┤                                            │
│  Student DB ┘                                            │
└──────────────────────┬───────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────┐
│                    DATA STORAGE                           │
│  HDFS (raw logs, video metadata)                         │
│  HBase / MongoDB (student profiles, semi-structured)     │
│  Elasticsearch (text search: forum, chat)                │
└──────────────────────┬───────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────┐
│                    PROCESSING                             │
│                                                           │
│  BATCH (Spark/MapReduce):                                │
│  • Tính GPA trends, attendance patterns                  │
│  • WordCount trên forum → tìm topics khó                 │
│  • Clustering SV theo hành vi học tập                    │
│                                                           │
│  REAL-TIME (Spark Streaming):                            │
│  • Phát hiện SV "at-risk" khi không login > 7 ngày       │
│  • Alert khi điểm giữa kỳ < threshold                    │
└──────────────────────┬───────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────┐
│                    ANALYTICS / ML                         │
│                                                           │
│  • Classification (Random Forest, SVM):                  │
│    Dự đoán SV có nguy cơ bỏ học (dropout prediction)     │
│    Features: GPA, attendance, login freq, assignment      │
│                                                           │
│  • Recommender System:                                    │
│    Gợi ý tài liệu/bài tập phù hợp trình độ SV          │
│    Content-Based: dựa trên topics SV đã học tốt/kém     │
│    Collaborative: SV có profile giống → gợi ý giống     │
│                                                           │
│  • Clustering (K-means):                                  │
│    Phân nhóm SV theo learning style                       │
│    → Nhóm chăm chỉ, nhóm học theo đợt, nhóm at-risk    │
│                                                           │
│  • NLP / Text Mining:                                     │
│    Phân tích forum: tìm topics SV hay hỏi → điều chỉnh  │
│    Sentiment analysis: SV hài lòng hay bức xúc?          │
└──────────────────────┬───────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────┐
│                    OUTPUT / ACTION                         │
│                                                           │
│  DASHBOARD cho giáo viên:                                │
│  • Biểu đồ phân bố điểm, attendance trends               │
│  • Danh sách SV at-risk (cần can thiệp)                  │
│  • Heat map: topic nào SV yếu nhất                        │
│                                                           │
│  ADAPTIVE LEARNING cho SV:                                │
│  • Gợi ý bài tập theo mức độ: dễ → khó                  │
│  • Recommend tài liệu bổ sung cho topics yếu             │
│  • Personalized study path                                │
│                                                           │
│  ALERT System:                                            │
│  • Email/SMS khi SV có dấu hiệu bỏ học                  │
│  • Notify giáo viên để can thiệp sớm                     │
└──────────────────────────────────────────────────────────┘
```

### 4. Kỹ thuật Big Data CỤ THỂ

| Kỹ thuật (môn học) | Ứng dụng trong Giáo dục |
|---------------------|------------------------|
| **MapReduce** (Ch.7) | Batch processing logs LMS hàng triệu dòng, WordCount forum |
| **Spark** (Ch.7) | Real-time analytics, ML pipeline |
| **Recommender System** (Ch.3) | Gợi ý tài liệu/bài tập cho SV |
| **Clustering** (Ch.2) | Phân nhóm SV theo learning style |
| **Data Streaming** (Ch.6) | Real-time monitoring hoạt động SV |
| **Bloom Filter** (Ch.6) | Kiểm tra nhanh SV đã hoàn thành assignment chưa |
| **LSH** (Ch.1) | Phát hiện đạo văn (document similarity) |
| **Dimensionality Reduction** (Ch.5) | Giảm chiều features SV để visualization |

### 5. Kết quả & Giá trị
- **Giảm 20-30% tỷ lệ bỏ học** nhờ phát hiện sớm + can thiệp
- **Cá nhân hóa lộ trình học** → SV học hiệu quả hơn
- **Giáo viên nắm rõ** SV nào yếu, topic nào khó → điều chỉnh giảng dạy
- **Phát hiện đạo văn** tự động bằng LSH

---

## CÂU 5: ỨNG DỤNG BIG DATA — HỆ THỐNG KHUYẾN NGHỊ (Recommender Systems) 🛒

### 1. Bài toán
**Xây dựng hệ thống gợi ý sản phẩm** cho e-commerce (như Amazon, Shopee) hoặc nội dung (như Netflix, YouTube).

### 2. Nguồn dữ liệu

| Nguồn | Dữ liệu | Đặc điểm |
|-------|---------|-----------|
| **Explicit feedback** | Ratings, reviews, likes | Ít nhưng chính xác |
| **Implicit feedback** | Click, view, purchase, time spent | Nhiều nhưng noisy |
| **User profile** | Demographics, preferences | Structured |
| **Item metadata** | Category, description, price, images | Content features |
| **Social network** | Friends, follows, shares | Graph data |

### 3. Kiến trúc hệ thống

```
User Actions ──→ Kafka ──→ ┌── Real-time RecSys
                            │   (trending, recently viewed)
Item Catalog ──→ HDFS  ──→ │
                            ├── Batch RecSys (Spark MLlib)
User Profiles ──→         │   ├── Collaborative Filtering
                            │   ├── Content-Based
                            │   └── Matrix Factorization
                            │
                            └── Model Serving API
                                    ↓
                              Web/Mobile App
                              "Có thể bạn cũng thích..."
```

### 4. Kỹ thuật Big Data CỤ THỂ (liên kết với môn học)

| Kỹ thuật (môn học) | Ứng dụng |
|--------------------|---------|
| **Content-Based** (Ch.3) | TF-IDF mô tả sản phẩm → User Profile → Cosine Similarity |
| **Collaborative Filtering** (Ch.3) | User-User CF (Pearson) hoặc Item-Item CF |
| **Matrix Factorization** (Ch.3) | UV Decomposition, SGD optimization |
| **LSH** (Ch.1) | Tìm nhanh users/items tương tự (thay vì O(n²)) |
| **Clustering** (Ch.2) | Phân nhóm users theo sở thích → giảm search space |
| **Dimensionality Reduction** (Ch.5) | SVD cho Latent Factor Model, giảm chiều features |
| **MapReduce** (Ch.7) | Batch training model trên dữ liệu ratings lớn |
| **Data Streaming** (Ch.6) | Real-time update recommendations khi user click/buy |

### 5. Xử lý Cold Start
- **New User**: Hỏi sở thích ban đầu, dùng demographics
- **New Item**: Content-Based từ metadata, promote trong "New arrivals"
- **Hybrid approach**: Kết hợp nhiều phương pháp

### 6. Đánh giá hệ thống
- **RMSE**: Root Mean Square Error trên ratings
- **Precision@K, Recall@K**: Trong top K gợi ý, bao nhiêu % user thực sự thích
- **A/B Testing**: So sánh trực tiếp 2 thuật toán trên production

---

## CÂU BỔ SUNG: ỨNG DỤNG BIG DATA TRONG MÔI TRƯỜNG 🌍

### 1. Bài toán
**Giám sát chất lượng không khí real-time & dự báo ô nhiễm**

### 2. Nguồn dữ liệu
- **Sensors IoT**: AQI, PM2.5, CO₂, NO₂, O₃ → Streaming
- **Vệ tinh**: Ảnh bề mặt, cloud cover → Batch
- **Trạm thời tiết**: Nhiệt độ, gió, độ ẩm → Time-series
- **Dữ liệu giao thông**: Lưu lượng xe (nguồn ô nhiễm) → Streaming
- **Social media**: Báo cáo ô nhiễm từ người dân → Text

### 3. Kiến trúc
```
IoT Sensors  ──→  Kafka  ──→  Spark Streaming  ──→  AQI Dashboard
Satellite    ──→  HDFS   ──→  Spark Batch      ──→  Pollution Map
Weather API  ──→                                ──→  Forecast Model
Traffic Data ──→                                ──→  Alert System
```

### 4. Kỹ thuật Big Data

| Kỹ thuật | Ứng dụng |
|----------|---------|
| **Data Streaming** | Real-time monitoring AQI; Bloom Filter lọc sensors lỗi |
| **Flajolet-Martin** | Đếm số khu vực vượt ngưỡng ô nhiễm |
| **DGIM** | Đếm số lần AQI > threshold trong sliding window |
| **Clustering** | Phân vùng ô nhiễm tương tự |
| **Regression** | Dự báo AQI 24-48 giờ tới |
| **MapReduce** | Xử lý batch ảnh vệ tinh |

### 5. Giá trị
- Cảnh báo sớm khi AQI vượt ngưỡng → người dân tránh ra ngoài
- Xác định nguồn ô nhiễm chính → chính sách kiểm soát
- Dự báo ô nhiễm → lên kế hoạch hoạt động ngoài trời

---

## CÂU BỔ SUNG: ỨNG DỤNG BIG DATA TRONG Y TẾ 🏥

### 1. Bài toán
**Dự đoán bệnh, hỗ trợ chẩn đoán, quản lý bệnh viện**

### 2. Nguồn dữ liệu
- Hồ sơ bệnh án điện tử (EMR): triệu chứng, chẩn đoán, thuốc
- Thiết bị đeo IoT: nhịp tim, SpO₂, huyết áp real-time
- Hình ảnh y khoa: X-ray, MRI, CT scan
- Genomics data: dữ liệu gen (rất lớn)

### 3. Kỹ thuật Big Data

| Kỹ thuật | Ứng dụng |
|----------|---------|
| **Streaming** | Real-time monitoring bệnh nhân ICU |
| **Clustering** | Phân nhóm bệnh nhân theo triệu chứng |
| **Recommender System** | Gợi ý phác đồ điều trị dựa trên ca bệnh tương tự |
| **LSH** | Tìm nhanh ca bệnh tương tự trong hàng triệu hồ sơ |
| **MapReduce** | Xử lý batch genomics data |
| **Dim Reduction** | Giảm chiều gene features (hàng ngàn genes) |

---

## ⭐ CHIẾN LƯỢC LÀM BÀI TỰ LUẬN

### Bước 1: Đọc đề → Xác định lĩnh vực
### Bước 2: Viết theo template 5 phần

```
1. Nêu BÀI TOÁN cụ thể (1-2 dòng)
2. Liệt kê NGUỒN DỮ LIỆU (bảng)
3. Vẽ KIẾN TRÚC (sơ đồ pipeline)  ← QUAN TRỌNG NHẤT
4. Nêu KỸ THUẬT BIG DATA từ môn học  ← LIÊN KẾT VỚI LÝ THUYẾT
5. Nêu KẾT QUẢ/GIÁ TRỊ (2-3 gạch đầu dòng)
```

### Bước 3: Đảm bảo LIÊN KẾT với nội dung MÔN HỌC

> ⚠️ **QUAN TRỌNG**: Phải đề cập ít nhất 3-4 kỹ thuật ĐÃ HỌC TRONG MÔN  
> (Streaming, Clustering, RecSys, LSH, MapReduce, PageRank, DimRed)

### 💡 Mẹo ghi nhớ

Mỗi lĩnh vực → nhớ 1 KEYWORD + 1 KỸ THUẬT CHÍNH:

| Lĩnh vực | Keyword | Kỹ thuật chính |
|-----------|---------|---------------|
| Nông nghiệp | Sensors IoT + Precision farming | **Data Streaming** + Clustering |
| Giao thông | GPS real-time + tắc đường | **Streaming** + PageRank |
| Giáo dục | LMS logs + dropout prediction | **RecSys** + Clustering |
| Môi trường | AQI sensors + dự báo ô nhiễm | **Streaming** + DGIM/Bloom Filter |
| Khuyến nghị | Ratings + gợi ý sản phẩm | **CF/Matrix Factorization** + LSH |
| Y tế | EMR + chẩn đoán | **Clustering** + LSH |
