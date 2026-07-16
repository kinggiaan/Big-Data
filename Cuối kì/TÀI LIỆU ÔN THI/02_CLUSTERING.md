# CHƯƠNG 2: CLUSTERING (PHÂN CỤM)

> 🎯 **Mục tiêu**: Nhóm các điểm dữ liệu tương tự vào cùng cluster  
> Chương này hay ra trắc nghiệm: Các độ đo khoảng cách, K-means, BFR, CURE

---

## 1. CÁC ĐỘ ĐO KHOẢNG CÁCH

### ⭐ Bảng tổng hợp

| Độ đo | Công thức | Khi nào dùng |
|-------|-----------|-------------|
| **Euclidean** (L2) | √(Σ(xᵢ - yᵢ)²) | K-means (mặc định), dữ liệu số |
| **Manhattan** (L1) | Σ\|xᵢ - yᵢ\| | Grid-based, robust với outliers hơn L2 |
| **Cosine Distance** | 1 - (A·B)/(‖A‖·‖B‖) | Text/TF-IDF, không phụ thuộc độ dài |
| **Jaccard Distance** | 1 - \|A∩B\|/\|A∪B\| | Dữ liệu binary, tập hợp (sets) |

### 📝 Ví dụ tính

```
A = (1, 2, 3),  B = (4, 6, 8)

Euclidean: √((4-1)² + (6-2)² + (8-3)²) = √(9+16+25) = √50 ≈ 7.07
Manhattan: |4-1| + |6-2| + |8-3| = 3 + 4 + 5 = 12
Cosine Sim: (1×4+2×6+3×8)/(√14 × √116) = 40/40.3 ≈ 0.993
Cosine Dist: 1 - 0.993 = 0.007
```

### ⚠️ Câu hỏi hay thi

> **Q: K-means dùng độ đo mặc định nào?**  
> A: **Euclidean distance**

> **Q: Trong text clustering, độ đo nào tốt nhất?**  
> A: **Cosine distance** (không phụ thuộc độ dài văn bản)

> **Q: Jaccard dùng khi nào?**  
> A: Dữ liệu **binary** hoặc **tập hợp** (sets)

---

## 2. K-MEANS CLUSTERING

### ⭐ Thuật toán Lloyd's

```
Input: K (số clusters), tập dữ liệu X
Output: K clusters

1. KHỞI TẠO: Chọn K centroids ngẫu nhiên c₁, c₂, ..., cₖ
2. ASSIGN: Gán mỗi điểm x vào cluster có centroid GẦN NHẤT
   → Cluster(x) = argmin_k ||x - cₖ||²
3. UPDATE: Tính lại centroid = TRUNG BÌNH các điểm trong cluster
   → cₖ = (1/|Cₖ|) × Σ(x ∈ Cₖ) x
4. LẶP LẠI bước 2-3 cho đến khi:
   - Centroids KHÔNG THAY ĐỔI, hoặc
   - Đạt số lần lặp tối đa
```

### 📝 Ví dụ giải tay

**Đề**: Cho 6 điểm: A(1,1), B(2,1), C(4,3), D(5,4), E(1,2), F(5,3). K=2.

**Lần 1**: Chọn C₁=A(1,1), C₂=D(5,4) làm centroids ban đầu

| Điểm | d(·, C₁) | d(·, C₂) | Cluster |
|------|----------|----------|---------|
| A(1,1) | 0 | √25 = 5 | **Cluster 1** |
| B(2,1) | 1 | √18 ≈ 4.24 | **Cluster 1** |
| C(4,3) | √13 ≈ 3.61 | √2 ≈ 1.41 | **Cluster 2** |
| D(5,4) | √25 = 5 | 0 | **Cluster 2** |
| E(1,2) | 1 | √20 ≈ 4.47 | **Cluster 1** |
| F(5,3) | √20 ≈ 4.47 | 1 | **Cluster 2** |

**Cập nhật centroids**:
- C₁ = mean(A, B, E) = ((1+2+1)/3, (1+1+2)/3) = **(4/3, 4/3)**
- C₂ = mean(C, D, F) = ((4+5+5)/3, (3+4+3)/3) = **(14/3, 10/3)**

**Lần 2**: Tính lại khoảng cách tới centroids mới → gán lại → ...

### ⭐ K-means++ (Khởi tạo tốt hơn)

```
1. Chọn centroid ĐẦU TIÊN ngẫu nhiên từ X
2. Cho mỗi điểm x, tính D(x) = khoảng cách tới centroid GẦN NHẤT
3. Chọn centroid tiếp theo với xác suất ~ D(x)²
   (điểm xa centroid hiện tại → xác suất được chọn CAO hơn)
4. Lặp lại bước 2-3 cho đến khi có K centroids
5. Chạy K-means chuẩn với các centroids này
```

### ⚠️ Hạn chế K-means

| Hạn chế | Giải thích |
|---------|-----------|
| Phải chọn trước K | Không tự tìm được số cluster tối ưu |
| Nhạy cảm với khởi tạo | Centroid ban đầu khác → kết quả khác (local optimum) |
| Nhạy cảm với outliers | 1 outlier có thể kéo centroid lệch |
| Chỉ tìm được cụm **hình cầu** | Không tìm được cluster hình dạng bất kỳ |
| Tất cả cluster kích thước gần bằng nhau | Cluster lớn/nhỏ không cân bằng → kém |

---

## 3. HIERARCHICAL AGGLOMERATIVE CLUSTERING (HAC)

### ⭐ Thuật toán (Bottom-Up)

```
1. Khởi tạo: Mỗi điểm là 1 cluster riêng (n clusters)
2. Tính khoảng cách giữa TẤT CẢ cặp clusters
3. MERGE 2 clusters GẦN NHẤT thành 1
4. Cập nhật ma trận khoảng cách
5. Lặp lại bước 3-4 cho đến khi:
   - Còn 1 cluster duy nhất, hoặc
   - Đạt số cluster mong muốn K
```

### ⭐ Linkage Criteria (Cách tính khoảng cách giữa 2 clusters)

| Linkage | Công thức | Đặc điểm |
|---------|-----------|----------|
| **Single** (MIN) | min d(a,b): a∈C₁, b∈C₂ | Chaining effect, tìm được hình dạng dài |
| **Complete** (MAX) | max d(a,b): a∈C₁, b∈C₂ | Cụm compact, tròn |
| **Average** | avg d(a,b): a∈C₁, b∈C₂ | Trung dung |
| **Ward's** | Minimize tổng variance nội cụm | Giống K-means, cluster đều |

### 📝 Ví dụ

```
5 điểm: A, B, C, D, E
Ma trận khoảng cách (single linkage):

    A   B   C   D   E
A   0   1   5   9   7
B   1   0   4   8   6
C   5   4   0   3   5
D   9   8   3   0   2
E   7   6   5   2   0

Bước 1: Min = d(A,B) = 1 → Merge {A,B}
Bước 2: Min = d(D,E) = 2 → Merge {D,E}
Bước 3: Min = d(C,{D,E}) = min(3,5) = 3 → Merge {C,D,E}
Bước 4: Merge {A,B} + {C,D,E}

Dendrogram:
    ┌─────────── {A,B,C,D,E}
    │       ┌─── {C,D,E}
    │   ┌───┤
    │   │   └─── C
    │   └─── {D,E}
    │       ┌─── D
    │       └─── E
    └─── {A,B}
        ┌─── A
        └─── B
```

### So sánh K-means vs HAC

| | K-means | HAC |
|--|---------|-----|
| Chọn K trước? | ✅ Phải | ❌ Không cần |
| Complexity | O(n × K × iterations) | O(n² log n) hoặc O(n³) |
| Big Data? | ✅ Tốt | ❌ Chậm |
| Hình dạng | Chỉ hình cầu | Linh hoạt hơn |
| Output | K clusters | Dendrogram |

---

## 4. BFR ALGORITHM (Bradley-Fayyad-Reina)

> 🎯 **K-means cho Big Data** — dữ liệu KHÔNG VỪA bộ nhớ  
> **Giả định**: Clusters có phân phối CHUẨN (Gaussian), axes-aligned

### ⭐ 3 Cấu trúc dữ liệu

| Cấu trúc | Viết tắt | Mô tả |
|-----------|----------|-------|
| **Discard Set** | DS | Điểm ĐÃ GÁN vào cluster → chỉ lưu thống kê |
| **Compression Set** | CS | Mini-clusters (điểm gần nhau nhưng xa centroid chính) |
| **Retained Set** | RS | Outliers — lưu riêng lẻ từng điểm |

### ⭐⭐ Mỗi cluster lưu 3 giá trị (N, SUM, SUMSQ)

| Giá trị | Ý nghĩa | Ví dụ (3 điểm 2D: (1,2), (3,4), (5,6)) |
|---------|---------|------------------------------------------|
| **N** | Số điểm | N = 3 |
| **SUM** | Vector tổng tọa độ | SUM = (1+3+5, 2+4+6) = (9, 12) |
| **SUMSQ** | Vector tổng bình phương | SUMSQ = (1+9+25, 4+16+36) = (35, 56) |

### ⭐ Tính Centroid và Variance từ (N, SUM, SUMSQ)

$$\text{Centroid}_i = \frac{SUM_i}{N}$$

$$\sigma_i^2 = \frac{SUMSQ_i}{N} - \left(\frac{SUM_i}{N}\right)^2$$

### 📝 Ví dụ

```
N = 3, SUM = (9, 12), SUMSQ = (35, 56)

Centroid = (9/3, 12/3) = (3, 4)

Variance_x = 35/3 - (9/3)² = 11.67 - 9 = 2.67
Variance_y = 56/3 - (12/3)² = 18.67 - 16 = 2.67

Std_x = √2.67 ≈ 1.63
Std_y = √2.67 ≈ 1.63
```

### ⭐ Mahalanobis Distance (quyết định "đủ gần" để thêm vào cluster)

$$MD(x, c) = \sqrt{\sum_i \left(\frac{x_i - c_i}{\sigma_i}\right)^2}$$

> Nếu MD < threshold (thường **2σ** hoặc **3σ**) → thêm điểm vào DS

### 📝 Ví dụ Mahalanobis

```
Centroid c = (3, 4), σ = (1.63, 1.63)
Điểm x = (4, 5)

MD = √(((4-3)/1.63)² + ((5-4)/1.63)²)
   = √((0.613)² + (0.613)²)
   = √(0.376 + 0.376)
   = √0.752 = 0.867

→ MD = 0.867 < 2 (threshold) → THÊM vào cluster ✓
```

### ⭐ Quy trình BFR

```
1. Khởi tạo K centroids (từ mẫu nhỏ hoặc ngẫu nhiên)
2. VỚI MỖI CHUNK dữ liệu mới:
   a. Tính MD tới mỗi centroid:
      - MD < threshold → thêm vào DS, CẬP NHẬT (N, SUM, SUMSQ)
      - MD ≥ threshold → kiểm tra CS
        - Gần CS nào đó → thêm vào CS
        - KHÔNG gần → thêm vào RS
   b. Cluster các điểm trong RS:
      - Tạo CS mới nếu có mini-cluster
      - Merge CS nếu chúng đủ gần
3. Kết thúc: Gán RS và CS vào cluster gần nhất
```

### ⭐ Merge 2 clusters (N₁, SUM₁, SUMSQ₁) và (N₂, SUM₂, SUMSQ₂)

```
N = N₁ + N₂
SUM = SUM₁ + SUM₂
SUMSQ = SUMSQ₁ + SUMSQ₂
```

💡 **Đây là lý do BFR chỉ cần lưu (N, SUM, SUMSQ)** — merge chỉ cần cộng!

---

## 5. CURE ALGORITHM (Clustering Using REpresentatives)

> 🎯 Tìm cluster **KHÔNG hình cầu**, chống outliers

### ⭐ Ý tưởng chính
Thay vì 1 centroid, dùng **nhiều representative points** phân tán trong cluster.

### Quy trình

```
1. LẤY MẪU ngẫu nhiên vừa bộ nhớ
2. PHÂN CỤM mẫu bằng hierarchical clustering
3. CHỌN representative points (k điểm phân tán nhất trong mỗi cluster)
4. THU HẸP (SHRINK): Dời representative points về phía centroid
   → rep_new = rep + α × (centroid - rep)
   α ∈ (0, 1): hệ số shrink → GIẢM ẢNH HƯỞNG outliers
5. GÁN toàn bộ dữ liệu vào cluster có representative point GẦN NHẤT
```

### So sánh BFR vs CURE

| | BFR | CURE |
|--|-----|------|
| **Giả định** | Cluster hình cầu, Gaussian | Hình dạng bất kỳ |
| **Đại diện** | 1 centroid + (N, SUM, SUMSQ) | Nhiều representative points |
| **Outliers** | RS giữ riêng | Shrink factor α giảm ảnh hưởng |
| **Khi nào dùng** | Data chuẩn, hình cầu | Data hình dạng phức tạp |

---

## 6. ĐÁNH GIÁ CHẤT LƯỢNG CLUSTERING

### ⭐ Các tiêu chí

| Tiêu chí | Mô tả |
|----------|-------|
| **SSE** (Sum of Squared Errors) | Σ Σ ‖x - cₖ‖² — càng nhỏ càng tốt |
| **Silhouette Score** | (b-a)/max(a,b) — a: intra-cluster, b: nearest-cluster. Giá trị [-1, 1], càng cao càng tốt |
| **Elbow Method** | Vẽ SSE theo K, chọn K tại "khuỷu tay" |

---

## ⚠️ TÓM TẮT — GHI NHỚ NHANH

```
┌──────────────────────────────────────────────────┐
│  K-MEANS: Assign → Update → Lặp                 │
│    Mặc định: Euclidean distance                  │
│    K-means++: chọn centroid theo D(x)²           │
│                                                   │
│  HAC: Merge 2 cluster gần nhất → dendrogram      │
│    Single/Complete/Average/Ward                   │
│                                                   │
│  BFR: K-means cho Big Data                       │
│    Lưu (N, SUM, SUMSQ) cho mỗi cluster          │
│    Centroid = SUM/N                               │
│    σ² = SUMSQ/N - (SUM/N)²                       │
│    Mahalanobis Distance để kiểm tra              │
│    3 sets: DS, CS, RS                             │
│                                                   │
│  CURE: Nhiều representative points               │
│    Shrink về centroid: giảm outlier impact        │
│    Tìm được cluster KHÔNG TRÒN                    │
└──────────────────────────────────────────────────┘
```
