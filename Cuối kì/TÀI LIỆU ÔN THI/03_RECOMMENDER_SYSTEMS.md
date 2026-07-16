# CHƯƠNG 3: RECOMMENDER SYSTEMS (HỆ THỐNG KHUYẾN NGHỊ)

> 🎯 **Mục tiêu**: Gợi ý sản phẩm phù hợp tới người dùng  
> ⭐ Chương này rất quan trọng — vừa ra trắc nghiệm vừa ra tự luận (ứng dụng)

---

## 1. TỔNG QUAN

### Tại sao cần Recommender Systems?
- Giúp user tìm sản phẩm trong "long tail" (sản phẩm ít phổ biến nhưng giá trị)
- Ví dụ: Cuốn "Touching the Void" tăng doanh số nhờ Amazon recommend cùng "Into Thin Air"

### 3 loại Recommendations

| Loại | Ví dụ | Mô tả |
|------|-------|-------|
| Editorial/Hand curated | "Staff picks", danh mục thiết yếu | Con người tự chọn |
| Simple aggregates | Top 10, Most popular | Thống kê đơn giản |
| **Tailored to individual** | Amazon, Netflix | **Cá nhân hóa** — quan trọng nhất |

---

## 2. UTILITY MATRIX (MA TRẬN TIỆN ÍCH)

### ⭐ Định nghĩa
Ma trận `m × n`: hàng = users, cột = items, giá trị = rating

```
           HP1  HP2  HP3  TW  SW1  SW2
Alice       4         5    1
Bob              5         3    3
Carol       2    3         4
```

### Key Problems
1. **Rất thưa (sparse)** — hầu hết ô trống
2. **Cold Start**: User mới hoặc Item mới → không có rating
3. **Gathering ratings khó** — phải incentivize hoặc học từ hành vi

### Extrapolating Utilities
> Bài toán cốt lõi: **Dự đoán rating cho các ô trống**

3 hướng tiếp cận:
1. **Content-Based**: Dựa trên thuộc tính sản phẩm
2. **Collaborative Filtering**: Dựa trên users tương tự
3. **Latent Factor**: Phân tích ma trận

---

## 3. CONTENT-BASED FILTERING

### ⭐ Ý tưởng chính
> Gợi ý sản phẩm **tương tự** với sản phẩm mà user đã **đánh giá cao** trước đó

### Quy trình chi tiết

```
1. TẠO ITEM PROFILE:
   → Mỗi item = vector đặc trưng (features)
   → Cho text: dùng TF-IDF

2. TẠO USER PROFILE:
   → Trung bình CÓ TRỌNG SỐ các item profiles đã rated
   → User Profile = Σ(rating_i × item_profile_i) / Σ(rating_i)

3. DỰ ĐOÁN:
   → Tính Cosine Similarity giữa User Profile và Item Profile mới
   → Recommend items có similarity cao nhất
```

### ⭐ Công thức Cosine Similarity

$$\cos(A, B) = \frac{A \cdot B}{\|A\| \times \|B\|} = \frac{\sum A_i B_i}{\sqrt{\sum A_i^2} \times \sqrt{\sum B_i^2}}$$

### 📝 BÀI TẬP MẪU (từ slide BK)

**Đề**: Cho bảng features máy tính:

| Feature | A | B | C | D | E |
|---------|---|---|---|---|---|
| Processor speed | 3 | 2.5 | 2.8 | 2 | 2.9 |
| Disk size | 500 | 320 | 640 | 350 | 580 |
| Main-memory size | 6 | 4 | 6 | 4 | 6 |
| Rating of user x | 4 | 2 | 5 | ? | ? |

**Câu a**: Tính User Profile

**Giải**:
```
User Profile = Σ(ratingᵢ × item_profileᵢ) / Σ(ratingᵢ)

Tổng rating = 4 + 2 + 5 = 11

Processor: (4×3 + 2×2.5 + 5×2.8) / 11 = (12+5+14)/11 = 31/11 ≈ 2.818
Disk:      (4×500 + 2×320 + 5×640) / 11 = (2000+640+3200)/11 = 5840/11 ≈ 530.91
Memory:    (4×6 + 2×4 + 5×6) / 11 = (24+8+30)/11 = 62/11 ≈ 5.636

User Profile = (2.818, 530.91, 5.636)
```

**Câu b**: User x có thích D và E không? (Cosine similarity)

**Giải cho D = (2, 350, 4)**:
```
A = User Profile = (2.818, 530.91, 5.636)
B = D = (2, 350, 4)

A · B = 2.818×2 + 530.91×350 + 5.636×4
      = 5.636 + 185818.5 + 22.544
      = 185846.68

||A|| = √(2.818² + 530.91² + 5.636²) = √(7.94 + 281865.5 + 31.76) ≈ 530.93
||B|| = √(2² + 350² + 4²) = √(4 + 122500 + 16) = √122520 ≈ 350.03

cos(A, D) = 185846.68 / (530.93 × 350.03) ≈ 0.9999...
```

**Giải cho E = (2.9, 580, 6)**: (tương tự)
```
cos(A, E) = (2.818×2.9 + 530.91×580 + 5.636×6) / (||A|| × ||E||)
→ cos(A, E) cũng rất gần 1
```

⚠️ **Lưu ý**: Cosine similarity giữa User Profile và Items thường rất cao vì disk size chiếm dominant → trong thực tế cần **normalize features** trước!

### Ưu/nhược điểm Content-Based

| ✅ Ưu điểm | ❌ Nhược điểm |
|-----------|-------------|
| Không cần dữ liệu user khác | Cần feature engineering |
| Giải thích được | Overspecialization (chỉ gợi ý giống cái đã thích) |
| Xử lý được new items | Không khám phá được sở thích mới |
| Không Cold Start cho items | Cold Start cho users mới |

---

## 4. COLLABORATIVE FILTERING

### ⭐ Ý tưởng chính
> Dựa trên hành vi của **những user GIỐNG NHAU** hoặc **những item GIỐNG NHAU**

### 4.1 User-User CF

**Bước 1**: Tìm users tương tự → **3 cách xử lý missing ratings**

| Cách | Mô tả | Vấn đề |
|------|-------|--------|
| Cách 1 | Bỏ qua items chưa rate | Thiếu dữ liệu, bỏ qua thông tin |
| Cách 2 | Coi missing = 0 (dislike) | Bias — chưa rate ≠ không thích |
| **Cách 3** ⭐ | **Pearson Correlation** | **TỐT NHẤT** — normalize mức đánh giá |

**Bước 2**: Dự đoán rating

### ⭐ Công thức Pearson Correlation

$$sim(u, v) = \frac{\sum_{i \in I_{uv}} (r_{ui} - \bar{r}_u)(r_{vi} - \bar{r}_v)}{\sqrt{\sum_{i \in I_{uv}} (r_{ui} - \bar{r}_u)^2} \times \sqrt{\sum_{i \in I_{uv}} (r_{vi} - \bar{r}_v)^2}}$$

Trong đó:
- I_uv = tập items mà CẢ u và v đều đã rate
- r̄_u = rating trung bình của user u

### 📝 Ví dụ Pearson Correlation

**Đề**: Tính similarity giữa Alice và Bob

| | HP1 | HP2 | HP3 | TW |
|--|-----|-----|-----|----|
| Alice | 5 | 3 | 4 | 2 |
| Bob | 4 | — | 5 | 1 |

**Giải**: Chỉ dùng items CẢ HAI đều rate: {HP1, HP3, TW}

```
r̄_Alice = (5+4+2)/3 = 11/3 ≈ 3.67
r̄_Bob = (4+5+1)/3 = 10/3 ≈ 3.33

Tử số = (5-3.67)(4-3.33) + (4-3.67)(5-3.33) + (2-3.67)(1-3.33)
       = (1.33)(0.67) + (0.33)(1.67) + (-1.67)(-2.33)
       = 0.891 + 0.551 + 3.891
       = 5.333

Mẫu số = √[(1.33² + 0.33² + 1.67²)] × √[(0.67² + 1.67² + 2.33²)]
        = √(1.769 + 0.109 + 2.789) × √(0.449 + 2.789 + 5.429)
        = √4.667 × √8.667
        = 2.160 × 2.944
        = 6.360

sim(Alice, Bob) = 5.333 / 6.360 ≈ 0.839
```

→ Pearson = 0.839 → Alice và Bob **khá giống nhau**

### ⭐ Công thức dự đoán Rating

$$\hat{r}(u, i) = \bar{r}_u + \frac{\sum_{v \in N} sim(u,v) \times (r_{vi} - \bar{r}_v)}{\sum_{v \in N} |sim(u,v)|}$$

### 📝 Ví dụ dự đoán

```
Dự đoán rating của Alice cho HP2:
- r̄_Alice = 3.67
- Neighbors: Bob (sim=0.839, rBob_HP2 không có), Carol (sim=0.5, rCarol_HP2=3, r̄Carol=3)

r̂(Alice, HP2) = 3.67 + [0.5 × (3 - 3)] / |0.5|
              = 3.67 + 0 / 0.5
              = 3.67
```

### 4.2 Item-Item CF

Tương tự nhưng tìm **items giống nhau** thay vì users:
- Tính similarity giữa các items dựa trên rating patterns
- Dự đoán rating user u cho item i = trung bình có trọng số ratings user u cho các items tương tự i

> 💡 Item-Item thường **ổn định hơn** User-User vì items ít thay đổi hơn users

---

## 5. LATENT FACTOR MODEL (MÔ HÌNH NHÂN TỐ TIỀM ẨN)

### ⭐ UV Decomposition / Matrix Factorization

> Phân tích ma trận R ≈ P × Q^T

```
R (m×n)  ≈  P (m×d)  ×  Q^T (d×n)

m: số users
n: số items  
d: số latent factors (ẩn)
```

| Ma trận | Ý nghĩa |
|---------|---------|
| R | Ma trận rating gốc (thưa) |
| P | User preferences cho d latent features |
| Q | Item properties trên d latent features |

### ⭐ Dự đoán rating

$$\hat{R}_{ui} = \sum_{k=1}^{d} P_{uk} \times Q_{ki}$$

### ⭐ Hàm mục tiêu (RMSE + Regularization)

$$J = \sum_{(u,i) \in \text{known}} (R_{ui} - P_u \cdot Q_i^T)^2 + \lambda(\|P_u\|^2 + \|Q_i\|^2)$$

### SGD (Stochastic Gradient Descent) Update Rules

```
Error:    e_ui = R_ui - P_u · Q_i^T

Update P: P_uk ← P_uk + γ × (e_ui × Q_ki - λ × P_uk)
Update Q: Q_ki ← Q_ki + γ × (e_ui × P_uk - λ × Q_ki)

γ = learning rate
λ = regularization parameter
```

### Ví dụ Netflix Prize
- Không có giải pháp đơn lẻ nào chiến thắng
- Team chiến thắng kết hợp **nhiều mô hình** (ensemble)
- Giải thưởng $1M cho 10% cải thiện RMSE

---

## 6. COLD START PROBLEM

### ⭐ Hai loại Cold Start

| Loại | Vấn đề | Giải pháp |
|------|--------|-----------|
| **New User** | Chưa có rating → không biết sở thích | Hỏi rating ban đầu, dùng demographics |
| **New Item** | Chưa ai rate → không thể CF | Dùng Content-Based, thêm metadata |

### ⭐ Giải pháp: Hybrid Approach
Kết hợp Content-Based + Collaborative Filtering:
- CF khi có đủ data
- Content-Based cho new items/users
- Netflix, Amazon đều dùng Hybrid

---

## 7. COMPLEXITY & LIÊN KẾT VỚI CÁC CHƯƠNG KHÁC

> Tìm k users tương tự: O(|X|) → quá chậm cho runtime

### Giải pháp:
| Kỹ thuật | Áp dụng |
|----------|---------|
| **LSH** (Chương 1) | Near-neighbor search nhanh |
| **Clustering** (Chương 2) | Nhóm users tương tự |
| **Dim Reduction** (Chương 5) | Giảm chiều features |

---

## ⚠️ TÓM TẮT — GHI NHỚ NHANH

```
┌──────────────────────────────────────────────────────┐
│  3 PHƯƠNG PHÁP:                                      │
│                                                       │
│  1. CONTENT-BASED:                                    │
│     Item Profile → User Profile → Cosine Similarity   │
│     Ưu: xử lý new items                              │
│     Nhược: overspecialization                          │
│                                                       │
│  2. COLLABORATIVE FILTERING:                          │
│     User-User hoặc Item-Item                          │
│     Pearson Correlation → TỐT NHẤT cho user sim       │
│     r̂(u,i) = r̄_u + Σ sim×(r-r̄) / Σ|sim|           │
│                                                       │
│  3. LATENT FACTOR (Matrix Factorization):             │
│     R ≈ P × Q^T                                      │
│     SGD update: P += γ(e×Q - λ×P)                    │
│                                                       │
│  COLD START → Hybrid (Content + CF)                   │
│  COMPLEXITY → LSH, Clustering, Dim Reduction          │
└──────────────────────────────────────────────────────┘
```
