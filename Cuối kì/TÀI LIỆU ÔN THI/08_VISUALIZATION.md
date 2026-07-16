# CHƯƠNG 8: BIG DATA VISUALIZATION (TRỰC QUAN HÓA)

> 🎯 Trực quan hóa giúp hiểu dữ liệu lớn nhanh chóng  
> Chương này thường ra 1-2 câu trắc nghiệm

---

## 1. THÁCH THỨC KHI TRỰC QUAN HÓA BIG DATA

| Đặc tính (4V) | Thách thức | Giải pháp |
|----------------|-----------|-----------|
| **Volume** | Quá nhiều data để hiển thị | Aggregation, sampling, progressive rendering |
| **Velocity** | Data cập nhật liên tục | Dynamic/streaming visualization, low latency |
| **Variety** | Nhiều loại data (text, ảnh, số) | Tích hợp nhiều loại chart |
| **Veracity** | Chất lượng data kém | Hiển thị uncertainty, data quality indicators |

---

## 2. CÁC KỸ THUẬT TRỰC QUAN HÓA

### ⭐ Bảng tổng hợp — KHI NÀO DÙNG CHART NÀO

| Kỹ thuật | Mục đích | Dùng khi |
|----------|---------|---------|
| **Bar Chart** | So sánh categories | Ranking, so sánh nhóm |
| **Line Chart** | Xu hướng theo thời gian | Time series, trends |
| **Scatter Plot** | Mối quan hệ giữa 2 biến | Correlation, clusters, outliers |
| **Heat Map** | Mật độ/cường độ | Pattern đa chiều, ma trận correlation |
| **Network Graph** | Kết nối, quan hệ | Dependencies, social networks, PageRank |
| **Parallel Coordinates** | Dữ liệu đa chiều | So sánh nhiều features cùng lúc |
| **Treemap** | Dữ liệu phân cấp | Part-to-whole, tiết kiệm không gian |
| **Word Cloud** | Tần suất từ | Text analysis, topic overview |
| **Choropleth Map** | Dữ liệu địa lý | So sánh vùng miền (dùng RATE, không dùng tổng) |
| **Sunburst Diagram** | Phân cấp nhiều lớp | Multi-level part-to-whole |
| **Box Plot** | Phân phối dữ liệu | Median, quartiles, outliers |
| **Histogram** | Phân phối tần suất | Distribution shape |

---

## 3. NGUYÊN TẮC THIẾT KẾ

### ⭐ Principles of Good Visualization

1. **"Above all else, show the data"** (Edward Tufte)
   - Minimize chart junk (trang trí không cần thiết)
   - Data-ink ratio cao → tốt

2. **Visual Encoding phù hợp**
   - **Vị trí** → so sánh chính xác nhất
   - **Chiều dài/diện tích** → so sánh lượng
   - **Màu sắc** → phân loại
   - **Độ đậm** → cường độ

3. **Lie Factor** = (% thay đổi visual) / (% thay đổi data)
   - Lie Factor = 1: trung thực
   - Lie Factor >> 1: phóng đại
   - Lie Factor << 1: thu nhỏ

### ⚠️ Sai lầm thường gặp

| Sai lầm | Tại sao sai |
|---------|-----------|
| Cắt trục Y không bắt đầu từ 0 | Phóng đại sự khác biệt |
| Dùng 3D cho data 2D | Bóp méo nhận thức |
| Quá nhiều categories cùng 1 chart | Rối, không đọc được |
| Choropleth map dùng total thay vì rate | Bias bởi population size |
| Pie chart nhiều hơn 5-6 phần | Khó so sánh |

---

## 4. TƯƠNG TÁC (INTERACTIVITY)

### Kỹ thuật tương tác cho Big Data

| Kỹ thuật | Mô tả |
|----------|-------|
| **Zooming** | Phóng to chi tiết |
| **Filtering** | Lọc theo tiêu chí |
| **Brushing** | Chọn subset, highlight trên nhiều view |
| **Linking** | Nhiều charts cùng data, chọn 1 → highlight tất cả |
| **Details on Demand** | Hover/click để xem chi tiết |
| **Overview + Detail** | Cái nhìn tổng quan + zoom vào phần cụ thể |

---

## 5. DECISION FRAMEWORK — CHỌN CHART

```
Bạn muốn...
├── SO SÁNH categories?  → Bar Chart
├── XEM xu hướng?        → Line Chart
├── TÌM mối quan hệ?    → Scatter Plot
├── THẤY mật độ?         → Heat Map
├── VẼ kết nối?          → Network Graph
├── ĐA CHIỀU?            → Parallel Coordinates
├── PHÂN CẤP?            → Treemap / Sunburst
├── TEXT analysis?        → Word Cloud
├── ĐỊA LÝ?              → Choropleth Map
├── PHÂN PHỐI?            → Histogram / Box Plot
└── THÀNH PHẦN?           → Pie Chart (≤5) / Stacked Bar
```

---

## ⚠️ TÓM TẮT — GHI NHỚ NHANH

```
┌──────────────────────────────────────────────────┐
│  4V CHALLENGES: Volume → aggregate/sample         │
│                 Velocity → streaming viz           │
│                 Variety → multi-type charts         │
│                 Veracity → show uncertainty          │
│                                                    │
│  KEY PRINCIPLE: "Show the data, minimize junk"    │
│                                                    │
│  CHỌN CHART:                                       │
│    So sánh → Bar    Xu hướng → Line                │
│    Quan hệ → Scatter  Mật độ → Heat Map           │
│    Kết nối → Network  Đa chiều → Parallel Coord   │
│    Phân cấp → Treemap  Địa lý → Choropleth        │
│                                                    │
│  Lie Factor = visual change% / data change%        │
│  Choropleth: dùng RATE, không dùng TOTAL           │
└──────────────────────────────────────────────────┘
```
