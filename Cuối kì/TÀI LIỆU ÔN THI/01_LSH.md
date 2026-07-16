# CHƯƠNG 1: LSH — LOCALITY SENSITIVE HASHING

> 🎯 **Mục tiêu**: Tìm các documents/items tương tự trong tập dữ liệu khổng lồ  
> ❌ Nếu so sánh tất cả cặp: O(n²) → KHÔNG KHẢ THI cho Big Data  
> ✅ LSH giảm xuống gần O(n) bằng cách chỉ so sánh "candidate pairs"

---

## 1. PIPELINE 3 BƯỚC

```
Document → [SHINGLING] → Set of k-shingles
                            ↓
                      [MINHASHING] → Signature (vector ngắn)
                            ↓
                      [LSH BANDING] → Candidate Pairs
                            ↓
                      So sánh thực tế chỉ trên candidate pairs
```

---

## 2. BƯỚC 1: SHINGLING

### ⭐ Định nghĩa
**k-shingle (k-gram)**: Chuỗi con gồm k ký tự liên tiếp trong document.

### 📝 Ví dụ
```
Document = "abcab", k = 2
→ 2-shingles = {ab, bc, ca}     (lấy set, loại trùng)

Document = "hello", k = 3
→ 3-shingles = {hel, ell, llo}
```

### ⭐ Jaccard Similarity

$$J(A, B) = \frac{|A \cap B|}{|A \cup B|}$$

### 📝 Ví dụ tính Jaccard
```
A = {ab, bc, ca}
B = {ab, bc, cd}

A ∩ B = {ab, bc}          → |A ∩ B| = 2
A ∪ B = {ab, bc, ca, cd}  → |A ∪ B| = 4

J(A,B) = 2/4 = 0.5
```

### 💡 Chọn k bao nhiêu?
- **k = 5**: Cho email, tài liệu ngắn
- **k = 9-10**: Cho tài liệu dài, web pages
- k nhỏ → nhiều shingle trùng → similarity cao giả
- k lớn → ít shingle trùng → chính xác hơn

---

## 3. BƯỚC 2: MINHASHING

### ⭐ Mục đích
Nén (compress) các tập shingles thành **signature vectors** ngắn gọn, sao cho:

> **P(MinHash(A) = MinHash(B)) = J(A, B)**  
> Xác suất 2 tập có cùng MinHash = đúng bằng Jaccard Similarity

### ⭐ Thuật toán MinHash

**Bước 1**: Tạo Characteristic Matrix
- Hàng = tất cả shingles có thể
- Cột = documents
- Giá trị = 1 nếu document chứa shingle, 0 nếu không

**Bước 2**: Dùng hoán vị ngẫu nhiên (hoặc hàm hash)
- MinHash(S) = hàng đầu tiên (theo thứ tự hoán vị) mà cột S có giá trị 1

**Bước 3**: Lặp N lần với N hoán vị khác nhau → Signature vector có N thành phần

### 📝 Ví dụ đầy đủ

**Characteristic Matrix**:

| Shingle | S₁ | S₂ | S₃ |
|---------|----|----|-----|
| a       | 1  | 0  | 1   |
| b       | 0  | 1  | 0   |
| c       | 1  | 1  | 0   |
| d       | 0  | 0  | 1   |
| e       | 1  | 1  | 1   |

**Hoán vị π₁**: (e, a, d, c, b) → thứ tự hàng: e=1, a=2, d=3, c=4, b=5
- MinHash(S₁): Hàng đầu tiên có S₁=1 theo thứ tự π₁ → e (vị trí 1) ✓ → h₁(S₁) = 1
- MinHash(S₂): e (vị trí 1) → S₂=1 ✓ → h₁(S₂) = 1
- MinHash(S₃): e (vị trí 1) → S₃=1 ✓ → h₁(S₃) = 1

**Hoán vị π₂**: (b, d, a, e, c) → thứ tự: b=1, d=2, a=3, e=4, c=5
- h₂(S₁): b→S₁=0, d→S₁=0, a→S₁=1 ✓ → h₂(S₁) = 3
- h₂(S₂): b→S₂=1 ✓ → h₂(S₂) = 1
- h₂(S₃): b→S₃=0, d→S₃=1 ✓ → h₂(S₃) = 2

**Signature Matrix** (sau 2 hoán vị):

| Hash | S₁ | S₂ | S₃ |
|------|----|----|-----|
| h₁   | 1  | 1  | 1   |
| h₂   | 3  | 1  | 2   |

### ⭐ Dùng hàm hash thay cho hoán vị

Hoán vị toàn bộ rất tốn → Thay bằng hàm hash:

$$h(x) = (ax + b) \bmod c$$

Với c là số nguyên tố ≥ tổng số shingles

### 📝 Ví dụ hàm hash

```
Giả sử có 5 hàng (shingles 0-4), chọn c = 5

h₁(x) = (x + 1) mod 5    → [1, 2, 3, 4, 0]
h₂(x) = (3x + 1) mod 5   → [1, 4, 2, 0, 3]
```

**Cách tính MinHash với hàm hash**:

Cho mỗi cột (document), với mỗi hàm hash hᵢ:
```
MinHash_hᵢ(S) = min{ hᵢ(row) : row mà S có giá trị 1 }
```

---

## 4. BƯỚC 3: LSH — BANDING TECHNIQUE

### ⭐ Ý tưởng
Chia Signature Matrix thành **b bands**, mỗi band có **r rows** (n = b × r)

### Thuật toán
1. Chia signature thành b bands, mỗi band r rows
2. Mỗi band: hash đoạn signature vào bucket
3. Nếu 2 documents trùng bucket ở **BẤT KỲ** band nào → **candidate pair**
4. Chỉ tính Jaccard thực cho candidate pairs

### ⭐⭐ CÔNG THỨC S-CURVE (HAY THI)

Cho 2 documents có Jaccard Similarity thực = s:

| Bước | Công thức | Giải thích |
|------|-----------|------------|
| Đồng ý trong 1 band | s^r | Cả r hàng phải giống nhau |
| KHÔNG đồng ý trong 1 band | 1 - s^r | |
| KHÔNG đồng ý trong TẤT CẢ b bands | (1 - s^r)^b | |
| **Là candidate pair** | **1 - (1 - s^r)^b** | ⭐ Công thức chính |

### ⭐ Threshold (Ngưỡng)

$$t \approx \left(\frac{1}{b}\right)^{1/r}$$

### 📝 Bài tập mẫu 1: Tính xác suất

**Đề**: Signature có 100 thành phần, chia thành b=20 bands, r=5 rows/band. Hai documents có Jaccard = 0.8. Tính P(là candidate pair)?

**Giải**:
```
s = 0.8, b = 20, r = 5

Bước 1: s^r = 0.8^5 = 0.32768
Bước 2: 1 - s^r = 1 - 0.32768 = 0.67232
Bước 3: (1 - s^r)^b = 0.67232^20 = 0.000355...
Bước 4: P = 1 - 0.000355 ≈ 0.9996

→ Xác suất ≈ 99.96% là candidate pair ✓
```

### 📝 Bài tập mẫu 2: Tính threshold

**Đề**: b = 20, r = 5. Tính ngưỡng threshold?

**Giải**:
```
t ≈ (1/b)^(1/r) = (1/20)^(1/5) = 0.05^0.2 ≈ 0.55

→ Các cặp có Jaccard > 0.55 sẽ có xác suất cao được chọn làm candidate
→ Các cặp có Jaccard < 0.55 sẽ có xác suất thấp
```

### 📝 Bài tập mẫu 3: Tính cho nhiều mức similarity

**Đề**: b = 5, r = 3. Tính P(candidate) cho s = 0.2, 0.4, 0.6, 0.8

**Giải**:

| s | s^r | 1-s^r | (1-s^r)^b | **P = 1-(1-s^r)^b** |
|---|-----|-------|-----------|---------------------|
| 0.2 | 0.008 | 0.992 | 0.961 | **0.039** (3.9%) |
| 0.4 | 0.064 | 0.936 | 0.718 | **0.282** (28.2%) |
| 0.6 | 0.216 | 0.784 | 0.295 | **0.705** (70.5%) |
| 0.8 | 0.512 | 0.488 | 0.028 | **0.972** (97.2%) |

**Threshold**: t ≈ (1/5)^(1/3) ≈ 0.585

→ Khi s > 0.585: hầu hết được chọn. Khi s < 0.585: hầu hết bị loại.

### ⚠️ Trade-offs khi chọn b và r

| Tăng b (nhiều bands) | Tăng r (nhiều rows/band) |
|----------------------|-------------------------|
| Threshold GIẢM | Threshold TĂNG |
| Dễ tìm candidate hơn | Khó tìm candidate hơn |
| ↑ False Positives | ↓ False Positives |
| ↓ False Negatives | ↑ False Negatives |

---

## 5. LSH CHO COSINE SIMILARITY

### Random Hyperplanes

- Tạo vector ngẫu nhiên **r** (hyperplane)
- Hash: `h(v) = sign(v · r)` → nếu > 0 → 1, nếu ≤ 0 → 0

### ⭐ Công thức

$$P(h(u) = h(v)) = 1 - \frac{\theta}{\pi}$$

Với θ = góc giữa u và v

### 💡 Tương tự Jaccard vs Cosine

| | Jaccard | Cosine |
|--|---------|--------|
| **Dùng cho** | Tập hợp (sets) | Vectors |
| **Hash** | MinHash | Random Hyperplanes |
| **P(trùng hash)** | J(A,B) | 1 - θ/π |

---

## 6. LSH CHO EUCLIDEAN DISTANCE

### Random Projection

- Chọn đường thẳng ngẫu nhiên, chiếu các điểm lên
- Chia đường thẳng thành các đoạn (bucket) có chiều rộng a
- Points trong cùng bucket → candidate pair

### ⭐ Tính chất
- Bucket width a nhỏ → ít false positives, nhiều false negatives
- Bucket width a lớn → nhiều false positives, ít false negatives

---

## ⚠️ TÓM TẮT — GHI NHỚ NHANH

```
┌─────────────────────────────────────────────────────┐
│  PIPELINE:  Shingling → MinHash → LSH Banding      │
│                                                      │
│  JACCARD:   J(A,B) = |A∩B| / |A∪B|                 │
│                                                      │
│  MINHASH:   P(h(A)=h(B)) = J(A,B)                  │
│             h(x) = (ax+b) mod c                      │
│                                                      │
│  S-CURVE:   P(candidate) = 1 - (1 - s^r)^b          │
│                                                      │
│  THRESHOLD: t ≈ (1/b)^(1/r)                         │
│                                                      │
│  COSINE:    P(h(u)=h(v)) = 1 - θ/π                  │
└─────────────────────────────────────────────────────┘
```
