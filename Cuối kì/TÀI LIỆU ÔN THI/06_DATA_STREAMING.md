# CHƯƠNG 6: DATA STREAMING

> 🎯 **Chương RẤT QUAN TRỌNG** — hay ra thi cả trắc nghiệm lẫn bài tập tính toán  
> Đặc trưng: Dữ liệu đến liên tục, KHÔNG lưu hết, chỉ đi qua 1 lần (single-pass)

---

## 1. MÔ HÌNH STREAM PROCESSING

### Thách thức
- Dữ liệu **vô hạn**, đến liên tục với tốc độ cao
- **Không thể lưu toàn bộ** stream → phải xử lý ngay khi data đến
- Chỉ được đi qua **1 lần** (single-pass) → cần thuật toán xấp xỉ
- Bộ nhớ **có giới hạn**

### Window Models (Mô hình cửa sổ)

| Loại | Mô tả | Ví dụ |
|------|-------|-------|
| **Sliding Window** | Cửa sổ kích thước cố định, di chuyển theo thời gian | "Trung bình 1 giờ gần nhất" |
| **Landmark Window** | Từ 1 mốc cố định đến hiện tại (lớn dần) | "Tổng từ khi hệ thống khởi động" |
| **Tilted Time** | Chi tiết cho data gần, thô cho data cũ | "Phút → giờ → ngày → tháng" |

---

## 2. SAMPLING: RESERVOIR SAMPLING

### ⭐ Bài toán
Chọn **k mẫu ngẫu nhiên** từ stream có chiều dài **chưa biết trước** n.

### ⭐ Thuật toán

```
1. Lưu k phần tử ĐẦU TIÊN vào reservoir (bể chứa)
2. Với phần tử thứ i (i > k):
   a. Sinh số ngẫu nhiên j ∈ [1, i]
   b. Nếu j ≤ k → THAY THẾ phần tử thứ j trong reservoir bằng phần tử mới
   c. Nếu j > k → BỎ QUA phần tử mới
```

### ⭐ Tính chất
Mỗi phần tử có xác suất **k/n** được chọn (đồng đều)

### 📝 Ví dụ: k=3, stream = [a, b, c, d, e, f, g]

| Bước | Phần tử | i | P(thêm) = k/i | Kết quả reservoir |
|------|---------|---|---------------|-------------------|
| 1 | a | 1 | - | {a} |
| 2 | b | 2 | - | {a, b} |
| 3 | c | 3 | - | {a, b, c} |
| 4 | d | 4 | 3/4 = 0.75 | Giả sử j=2 (≤3): thay b → {a, **d**, c} |
| 5 | e | 5 | 3/5 = 0.60 | Giả sử j=5 (>3): bỏ qua → {a, d, c} |
| 6 | f | 6 | 3/6 = 0.50 | Giả sử j=1 (≤3): thay a → {**f**, d, c} |
| 7 | g | 7 | 3/7 = 0.43 | Giả sử j=6 (>3): bỏ qua → {f, d, c} |

**Bộ nhớ**: O(k) — chỉ cần lưu k phần tử

---

## 3. FILTERING: BLOOM FILTER

### ⭐ Mục đích
Kiểm tra **1 phần tử có thuộc tập S hay không** — tiết kiệm bộ nhớ, chấp nhận sai số nhỏ.

### ⭐ Cấu trúc
- **Bit array** kích thước **m** bits (ban đầu tất cả = 0)
- **k hàm hash** h₁, h₂, ..., hₖ (mỗi hàm cho output ∈ {0, 1, ..., m-1})

### ⭐⭐ Hai thao tác

**INSERT(x)** — Thêm phần tử x vào filter:
```
Với mỗi hàm hash hᵢ (i = 1..k):
  Tính pos = hᵢ(x)
  Set bit[pos] = 1
```

**QUERY(x)** — Kiểm tra x có trong tập không:
```
Với mỗi hàm hash hᵢ (i = 1..k):
  Tính pos = hᵢ(x)
  Nếu BẤT KỲ bit[pos] = 0 → ❌ CHẮC CHẮN KHÔNG CÓ (Definite No)
Nếu TẤT CẢ bit[pos] = 1 → ⚠️ CÓ THỂ CÓ (Probably Yes)
```

### ⭐⭐⭐ Tính chất cực kỳ quan trọng

| | False Positive | False Negative |
|--|---------------|----------------|
| **Có xảy ra?** | ✅ CÓ (nói "có" nhưng thực ra không) | ❌ KHÔNG BAO GIỜ |

> 💡 **Ghi nhớ**: Bloom Filter **KHÔNG BAO GIỜ** có False Negative  
> Nếu nó nói "KHÔNG CÓ" → chắc chắn 100% không có

### ⭐ Công thức False Positive

$$p \approx \left(1 - e^{-kn/m}\right)^k$$

Trong đó:
- m = số bits
- n = số phần tử đã thêm
- k = số hàm hash

### ⭐ Số hàm hash tối ưu

$$k_{opt} = \frac{m}{n} \times \ln 2 \approx 0.693 \times \frac{m}{n}$$

### 📝 Ví dụ đầy đủ

**Đề**: m = 10 bits, k = 2 hàm hash, thêm 3 phần tử: S = {cat, dog, fish}

```
Hàm hash:
h₁(cat) = 1,  h₂(cat) = 5
h₁(dog) = 3,  h₂(dog) = 7
h₁(fish) = 1, h₂(fish) = 9

Bit array ban đầu: [0 0 0 0 0 0 0 0 0 0]
                     0 1 2 3 4 5 6 7 8 9

Insert(cat):  set bit[1]=1, bit[5]=1
              [0 1 0 0 0 1 0 0 0 0]

Insert(dog):  set bit[3]=1, bit[7]=1
              [0 1 0 1 0 1 0 1 0 0]

Insert(fish): set bit[1]=1 (đã=1), bit[9]=1
              [0 1 0 1 0 1 0 1 0 1]
```

**Query("bird")**:
```
h₁(bird) = 3 → bit[3] = 1 ✓
h₂(bird) = 9 → bit[9] = 1 ✓
→ "CÓ THỂ CÓ" ⚠️ (nhưng thực ra KHÔNG — đây là FALSE POSITIVE!)
```

**Query("rat")**:
```
h₁(rat) = 2 → bit[2] = 0 ✗
→ "CHẮC CHẮN KHÔNG CÓ" ✅
(Chỉ cần 1 bit = 0 là kết luận ngay, không cần kiểm tra tiếp)
```

### 📝 Ví dụ tính toán p

**Đề**: m = 1000 bits, n = 100 phần tử. Tính k tối ưu và false positive rate.

```
k_opt = (m/n) × ln2 = (1000/100) × 0.693 = 6.93 → chọn k = 7

p = (1 - e^(-kn/m))^k
  = (1 - e^(-7×100/1000))^7
  = (1 - e^(-0.7))^7
  = (1 - 0.4966)^7
  = (0.5034)^7
  = 0.00819 ≈ 0.82%

→ False positive rate ≈ 0.82% (rất thấp!)
```

---

## 4. ĐẾM PHẦN TỬ PHÂN BIỆT: FLAJOLET-MARTIN

### ⭐ Bài toán
Ước lượng **số phần tử distinct** (khác nhau) trong stream, dùng ít bộ nhớ.

### ⭐ Ý tưởng
- Hash mỗi phần tử thành chuỗi bit
- Đếm số **trailing zeros** (số 0 ở cuối) → gọi là r(x)
- Theo dõi **R = max{r(x)}** cho tất cả x đã gặp

### ⭐⭐ Công thức ước lượng

$$\text{Distinct count} \approx 2^R$$

### 💡 Trực giác
- P(kết thúc bằng 0) = 1/2 → khoảng n/2 phần tử có r ≥ 1
- P(kết thúc bằng 00) = 1/4 → khoảng n/4 phần tử có r ≥ 2
- P(kết thúc bằng 0...0 k lần) = 1/2^k
- Nếu R_max = k thì ước lượng n ≈ 2^k

### 📝 Ví dụ đầy đủ

**Đề**: Stream = [a, b, c, a, d, b, c, a]. Hàm hash:

| Phần tử | h(x) (binary) | Trailing zeros r(x) |
|---------|---------------|---------------------|
| a | 101**0** | 1 |
| b | 11**00** | 2 |
| c | 1**0** | 1 (giả sử h(c)=10) |
| d | 1**000** | 3 |

**Chú ý**: a xuất hiện 3 lần nhưng hash giống nhau → chỉ tính 1 lần

```
R = max(1, 2, 1, 3) = 3

Ước lượng distinct ≈ 2^3 = 8
Thực tế: 4 phần tử distinct (a, b, c, d)
```

⚠️ **Sai số khá lớn cho 1 hàm hash** → Cải thiện:

### Cải thiện: Dùng nhiều hàm hash

```
Phương pháp 1: Dùng K hàm hash → K ước lượng → lấy TRUNG BÌNH
  → Vẫn bị lệch bởi giá trị cực đại

Phương pháp 2 (LogLog): 
  Chia K hàm hash thành nhóm → lấy MEDIAN → lấy trung bình
  → Chính xác hơn nhiều

Phương pháp 3 (HyperLogLog): 
  Dùng harmonic mean → chính xác nhất
  → Chỉ cần ~1.5KB bộ nhớ để đếm hàng tỷ phần tử!
```

---

## 5. DGIM ALGORITHM (ĐẾM SỐ 1 TRONG SLIDING WINDOW)

### ⭐ Bài toán
Đếm số bit **1** trong **N bits gần nhất** của binary stream, dùng bộ nhớ O(log²N).

### ⭐ Cấu trúc Bucket
Mỗi bucket có:
- **Timestamp**: Vị trí bit 1 gần nhất (bên phải nhất) trong bucket
- **Size**: Số bit 1 trong bucket = **lũy thừa 2** (1, 2, 4, 8, ...)

### ⭐⭐ 5 Quy tắc DGIM

```
1. Bit bên PHẢI NHẤT của mỗi bucket phải là 1
2. Size = lũy thừa 2 (1, 2, 4, 8, ...)
3. Mỗi size có 1 hoặc 2 buckets (KHÔNG ĐƯỢC 3!)
4. Sizes KHÔNG GIẢM từ phải sang trái (mới → cũ)
5. Buckets KHÔNG overlap (không chồng lấn)
```

### ⭐ Khi bit mới đến

```
Nếu bit MỚI = 0: Không làm gì (chỉ update timestamps)

Nếu bit MỚI = 1:
  1. Tạo bucket mới size = 1 ở vị trí hiện tại
  2. Nếu có 3 buckets size 1 → MERGE 2 bucket CŨ NHẤT thành size 2
  3. Nếu có 3 buckets size 2 → MERGE 2 bucket CŨ NHẤT thành size 4
  4. ... cascade merge cho đến khi mọi size chỉ có 1-2 buckets
```

### 📝 Ví dụ step-by-step

**Stream**: ... 0 1 0 1 1 0 1 1 0 1 0 1 1 0 0 1 (đọc từ trái sang phải, mới nhất ở BÊN PHẢI)

```
Timestamp:    16 15 14 13 12 11 10  9  8  7  6  5  4  3  2  1
Bit:           0  1  0  1  1  0  1  1  0  1  0  1  1  0  0  1

Buckets (từ mới → cũ):
  [1] size=1 (ts=1)      ← 1 bucket size 1
  [1] size=1 (ts=4,5)    ← Hmm, ta xây lại...
```

**Xây dựng lại từ đầu — buckets từ PHẢI (mới) sang TRÁI (cũ)**:

```
Bit 1 (ts=1):  1 → tạo bucket B1(size=1, ts=1)
Buckets: B1[1]

Bit 2 (ts=2):  0 → không làm gì

Bit 3 (ts=3):  0 → không làm gì

Bit 4 (ts=4):  1 → tạo bucket B2(size=1, ts=4)  
Buckets: B2[1], B1[1]  (2 buckets size 1 → OK)

Bit 5 (ts=5):  1 → tạo B3(size=1, ts=5)
→ 3 buckets size 1! → Merge B1+B2 cũ nhất → B12(size=2)
Buckets: B3[1], B12[2]

Bit 6 (ts=6):  0 → không làm gì

Bit 7 (ts=7):  1 → tạo B4(size=1, ts=7)
Buckets: B4[1], B3[1], B12[2]  (2 size-1, 1 size-2 → OK)

Bit 8 (ts=8):  0 → không làm gì

Bit 9 (ts=9):  1 → tạo B5(size=1, ts=9)
→ 3 buckets size 1! → Merge B3+B4 → B34(size=2)
→ 2 buckets size 2! → OK
Buckets: B5[1], B34[2], B12[2]
```

### ⭐⭐ Query: Đếm 1s trong K bits gần nhất

```
1. Tìm tất cả buckets NẰM HOÀN TOÀN trong K bits → cộng size
2. Bucket CŨ NHẤT cắt ngang (partially inside) → cộng NỬA size
3. Tổng = answer

⚠️ SAI SỐ TỐI ĐA: 50% (do ước lượng bucket cũ nhất bằng 1/2)
```

### 📝 Ví dụ Query

```
Giả sử buckets hiện tại (phải → trái):
  B1[size=1, ts=1], B2[size=1, ts=3], B3[size=2, ts=6], B4[size=4, ts=12]

Query: Đếm 1s trong 8 bits gần nhất (ts = 1 đến 8)

B1(ts=1): nằm hoàn toàn trong [1,8] → +1
B2(ts=3): nằm hoàn toàn trong [1,8] → +1
B3(ts=6): nằm hoàn toàn trong [1,8] → +2
B4(ts=12): CẮT NGANG (ts=12 > 8) → +4/2 = +2

Ước lượng = 1 + 1 + 2 + 2 = 6
```

### ⭐ Bộ nhớ DGIM

$$O(\log^2 N)$$

- Có O(log N) sizes khác nhau (1, 2, 4, ..., N)
- Mỗi size có ≤ 2 buckets
- Mỗi bucket cần O(log N) bits cho timestamp
- → Tổng: O(log N × log N) = O(log²N)

---

## 6. AMS ALGORITHM (ESTIMATING FREQUENCY MOMENTS)

### ⭐ Frequency Moments

| Moment | Công thức | Ý nghĩa |
|--------|-----------|---------|
| **F₀** | Số phần tử distinct | Dùng Flajolet-Martin |
| **F₁** | Σfᵢ = n (chiều dài stream) | Trivial — đếm |
| **F₂** | **Σfᵢ²** | "Surprise number" — đo mức LỆCH phân phối |
| **F∞** | max(fᵢ) | Phần tử xuất hiện nhiều nhất |

> 💡 F₂ cao → phân phối lệch (có vài phần tử chiếm đa số)  
> F₂ thấp → phân phối đều

### ⭐⭐ AMS Algorithm cho F₂

```
1. Chọn k vị trí NGẪU NHIÊN trong stream
2. Tại mỗi vị trí, ghi nhận phần tử e và đếm c = 
   số lần e xuất hiện TỪ VỊ TRÍ ĐÓ TRỞ ĐI
3. Estimate cho mỗi biến: X = n × (2c - 1)
4. F₂ ≈ trung bình tất cả estimates
```

### 📝 Ví dụ đầy đủ (HAY THI)

**Đề**: Stream độ dài n = 15:  
`a, b, c, d, a, c, a, b, d, a, c, b, a, d, c`

**Tính F₂ thực**:
```
f(a) = 5, f(b) = 3, f(c) = 4, f(d) = 3
F₂ = 5² + 3² + 4² + 3² = 25 + 9 + 16 + 9 = 59
```

**Ước lượng AMS** — chọn 3 vị trí ngẫu nhiên:

**Biến 1**: Vị trí 3 → phần tử = c
```
Stream từ vị trí 3: c, d, a, c, a, b, d, a, c, b, a, d, c
c xuất hiện: vị trí 3, 6, 11, 15 → từ vị trí 3 trở đi: c = 4 lần
X₁ = 15 × (2×4 - 1) = 15 × 7 = 105
```

**Biến 2**: Vị trí 8 → phần tử = b
```
Stream từ vị trí 8: b, d, a, c, b, a, d, c
b xuất hiện: vị trí 8, 12 → từ vị trí 8 trở đi: c = 2 lần
X₂ = 15 × (2×2 - 1) = 15 × 3 = 45
```

**Biến 3**: Vị trí 13 → phần tử = a
```
Stream từ vị trí 13: a, d, c
a xuất hiện: vị trí 13 → từ vị trí 13 trở đi: c = 1 lần
X₃ = 15 × (2×1 - 1) = 15 × 1 = 15
```

**Ước lượng F₂**:
```
F₂ ≈ (X₁ + X₂ + X₃) / 3 = (105 + 45 + 15) / 3 = 55
Thực tế F₂ = 59

Sai số = |55-59|/59 ≈ 6.8% → khá chính xác!
```

### ⭐ Tổng quát cho Moment bậc k

$$X = n \times (c^k - (c-1)^k)$$

- k = 2: X = n × (c² - (c-1)²) = n × (2c - 1) ← công thức ở trên
- k = 3: X = n × (c³ - (c-1)³) = n × (3c² - 3c + 1)

### Cải thiện độ chính xác

```
1. Dùng NHIỀU biến ngẫu nhiên (k lớn)
2. Chia thành nhóm → median trong nhóm → average giữa các nhóm
   → Giảm variance đáng kể
```

---

## 7. BẢNG SO SÁNH CÁC THUẬT TOÁN STREAMING

| Thuật toán | Bài toán | Bộ nhớ | Sai số | Output |
|-----------|---------|--------|--------|--------|
| **Reservoir Sampling** | Lấy k mẫu ngẫu nhiên | O(k) | Không sai số | k mẫu chính xác |
| **Bloom Filter** | Kiểm tra thuộc tập | O(m) bits | False positive only | Yes/No |
| **Flajolet-Martin** | Đếm distinct | O(log n) | Xấp xỉ (2^R) | Số distinct |
| **DGIM** | Đếm 1s trong window | O(log²N) | ≤ 50% | Số bit 1 |
| **AMS** | Ước lượng F_k | O(k variables) | Xấp xỉ | Frequency moment |

---

## ⚠️ TÓM TẮT — GHI NHỚ NHANH

```
┌───────────────────────────────────────────────────────────┐
│  RESERVOIR SAMPLING:                                       │
│    Giữ k đầu. Element i (i>k): thêm P=k/i, thay ngẫu nhiên│
│                                                             │
│  BLOOM FILTER: ⭐⭐⭐                                       │
│    Insert: hash k lần → set bits = 1                       │
│    Query: ANY bit=0 → CHẮC CHẮN KHÔNG. All=1 → CÓ THỂ CÓ │
│    ❌ KHÔNG CÓ False Negative                               │
│    p ≈ (1 - e^(-kn/m))^k                                   │
│    k_opt = (m/n) × ln2                                      │
│                                                             │
│  FLAJOLET-MARTIN:                                          │
│    Hash → trailing zeros → R = max                          │
│    Distinct ≈ 2^R                                           │
│                                                             │
│  DGIM:                                                      │
│    Buckets: (timestamp, size = 2^k)                         │
│    1-2 buckets/size. 3 → merge 2 cũ nhất                   │
│    Query: tổng + NỬA bucket cũ nhất                         │
│    Max error: 50%. Memory: O(log²N)                         │
│                                                             │
│  AMS (F₂ = Σfᵢ²):                                          │
│    Chọn vị trí random, đếm c từ đó trở đi                  │
│    Estimate = n × (2c - 1)                                  │
│    F₂ ≈ average(all estimates)                              │
└───────────────────────────────────────────────────────────┘
```
