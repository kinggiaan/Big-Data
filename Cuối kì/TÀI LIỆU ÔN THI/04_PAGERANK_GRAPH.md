# CHƯƠNG 4: PAGERANK & GRAPH ALGORITHMS

> **Môn:** Big Data (CO5135) — HCMUT  
> **Trọng tâm thi:** Tính PageRank bằng tay (Power Iteration), xử lý Dead Ends/Spider Traps, thuật toán HITS  
> **Mức độ quan trọng:** ⭐⭐⭐⭐⭐ (Rất hay ra thi — phần tính toán nhiều)

---

## 1. PageRank Algorithm

### 1.1. Mô hình Random Surfer (Người lướt web ngẫu nhiên)

💡 **Ý tưởng cốt lõi:** Tưởng tượng một người lướt web ngẫu nhiên:
- Tại mỗi trang web, người đó **chọn ngẫu nhiên** một link trên trang để click
- Mỗi link có **xác suất bằng nhau** được chọn
- **PageRank** của một trang = xác suất mà người lướt web đang ở trang đó tại thời điểm bất kỳ (trạng thái dừng - steady state)

```
Trang có nhiều link trỏ đến → Xác suất được ghé thăm cao → PageRank cao
Trang được link từ trang "quan trọng" → PageRank càng cao
```

### 1.2. Công thức cơ bản

⭐ **Công thức PageRank cơ bản:**

```
r_j = Σ(i→j) r_i / d_i
```

Trong đó:
| Ký hiệu | Ý nghĩa |
|----------|---------|
| r_j | PageRank của trang j |
| r_i | PageRank của trang i (trang trỏ đến j) |
| d_i | **Out-degree** của trang i (số link đi ra từ i) |
| i → j | Trang i có link trỏ đến trang j |

💡 **Cách hiểu:** Trang j nhận "phiếu bầu" từ mỗi trang i trỏ đến nó. Mỗi phiếu bầu có giá trị = PageRank của i chia đều cho tất cả link đi ra của i.

### 1.3. Dạng ma trận (Matrix Form)

⭐ **Stochastic Adjacency Matrix (Ma trận chuyển tiếp) M:**

```
M_ji = 1/d_i   nếu i → j
M_ji = 0        nếu không có link từ i → j
```

⭐ **Phương trình PageRank dạng ma trận:**

```
r = M × r
```

Trong đó:
- **r** là vector PageRank (cột), mỗi phần tử là PageRank của một trang
- **M** là **column-stochastic matrix** (tổng mỗi cột = 1)
- **r** chính là **eigenvector** ứng với eigenvalue = 1 của ma trận M

⚠️ **Lưu ý quan trọng:**  
- Mỗi **cột** của M đại diện cho **trang nguồn** (trang có link đi ra)  
- Mỗi **hàng** của M đại diện cho **trang đích** (trang nhận link)  
- Tổng mỗi **cột** = 1 (vì xác suất chuyển từ trang nguồn ra các trang khác = 1)

### 1.4. Xây dựng Transition Matrix — Ví dụ chi tiết

📝 **Ví dụ 1: Xây dựng ma trận chuyển tiếp**

Cho đồ thị web gồm 4 trang: **A, B, C, D** với các link:

```
A → B, C
B → C
C → A
D → A, B, C
```

**Đồ thị minh họa:**
```
A --1/2--> B
A --1/2--> C
B --1---> C
C --1---> A
D --1/3--> A
D --1/3--> B
D --1/3--> C
```

**Bước 1: Xác định out-degree**

| Trang | Link đi ra | Out-degree d_i |
|-------|-----------|----------------|
| A | B, C | 2 |
| B | C | 1 |
| C | A | 1 |
| D | A, B, C | 3 |

**Bước 2: Xây dựng ma trận M (cột = nguồn, hàng = đích)**

Mỗi cột i: chia đều 1/d_i cho các trang mà i trỏ đến

```
         A     B     C     D
    ┌                           ┐
A:  │  0      0     1     1/3   │
B:  │  1/2    0     0     1/3   │
C:  │  1/2    1     0     1/3   │
D:  │  0      0     0     0     │
    └                           ┘
```

**Giải thích từng cột:**
- **Cột A** (A trỏ đến B, C): d_A = 2 → M_BA = 1/2, M_CA = 1/2
- **Cột B** (B trỏ đến C): d_B = 1 → M_CB = 1
- **Cột C** (C trỏ đến A): d_C = 1 → M_AC = 1
- **Cột D** (D trỏ đến A, B, C): d_D = 3 → M_AD = M_BD = M_CD = 1/3

⚠️ **Kiểm tra:** Tổng mỗi cột phải = 1 (trừ cột dead-end)
- Cột A: 0 + 1/2 + 1/2 + 0 = 1 ✓
- Cột B: 0 + 0 + 1 + 0 = 1 ✓
- Cột C: 1 + 0 + 0 + 0 = 1 ✓
- Cột D: 1/3 + 1/3 + 1/3 + 0 = 1 ✓

### 1.5. Power Iteration — Ví dụ tính toán chi tiết

⭐ **Phương pháp Power Iteration (Lặp lũy thừa):**

```
1. Khởi tạo: r⁽⁰⁾ = [1/n, 1/n, ..., 1/n]ᵀ   (chia đều)
2. Lặp:      r⁽ᵗ⁺¹⁾ = M × r⁽ᵗ⁾
3. Dừng khi:  |r⁽ᵗ⁺¹⁾ - r⁽ᵗ⁾| < ε  (hội tụ)
```

📝 **Ví dụ 2: Power Iteration — Đồ thị 3 node**

Cho đồ thị web: **A → B → C → A** (chu trình đơn giản)

```
A --1--> B --1--> C --1--> A  (vòng tròn)
```

**Ma trận chuyển tiếp M:**

```
         A   B   C
    ┌               ┐
A:  │  0   0   1    │
B:  │  1   0   0    │
C:  │  0   1   0    │
    └               ┘
```

**Khởi tạo:** n = 3

```
r⁽⁰⁾ = [1/3, 1/3, 1/3]ᵀ
```

**Iteration 1:** r⁽¹⁾ = M × r⁽⁰⁾

```
r_A = 0×(1/3) + 0×(1/3) + 1×(1/3) = 1/3
r_B = 1×(1/3) + 0×(1/3) + 0×(1/3) = 1/3
r_C = 0×(1/3) + 1×(1/3) + 0×(1/3) = 1/3

r⁽¹⁾ = [1/3, 1/3, 1/3]ᵀ
```

→ Đã hội tụ ngay! (Vì đồ thị đối xứng hoàn toàn → mọi trang đều bằng nhau)

---

📝 **Ví dụ 3: Power Iteration — Đồ thị 4 node (phức tạp hơn) ⭐⭐⭐**

Cho đồ thị:

```
A → B, C
B → C
C → A
D → A, B, C
```

Ma trận M (đã xây dựng ở Ví dụ 1):

```
         A     B     C     D
    ┌                           ┐
A:  │  0      0     1     1/3   │
B:  │  1/2    0     0     1/3   │
C:  │  1/2    1     0     1/3   │
D:  │  0      0     0     0     │
    └                           ┘
```

**Khởi tạo:**

```
r⁽⁰⁾ = [1/4, 1/4, 1/4, 1/4]ᵀ = [0.25, 0.25, 0.25, 0.25]ᵀ
```

⚠️ **Chú ý:** Không ai trỏ đến D (hàng D toàn 0 trừ phần tử D,D cũng = 0) → PageRank của D sẽ dần về 0.

---

**Iteration 1:** r⁽¹⁾ = M × r⁽⁰⁾

```
r_A = 0×0.25 + 0×0.25 + 1×0.25 + (1/3)×0.25
    = 0 + 0 + 0.25 + 0.0833 = 0.3333

r_B = (1/2)×0.25 + 0×0.25 + 0×0.25 + (1/3)×0.25
    = 0.125 + 0 + 0 + 0.0833 = 0.2083

r_C = (1/2)×0.25 + 1×0.25 + 0×0.25 + (1/3)×0.25
    = 0.125 + 0.25 + 0 + 0.0833 = 0.4583

r_D = 0×0.25 + 0×0.25 + 0×0.25 + 0×0.25
    = 0

r⁽¹⁾ = [0.3333, 0.2083, 0.4583, 0]ᵀ
```

⚠️ **Kiểm tra tổng:** 0.3333 + 0.2083 + 0.4583 + 0 = 1.0 ✓

---

**Iteration 2:** r⁽²⁾ = M × r⁽¹⁾

```
r_A = 0×0.3333 + 0×0.2083 + 1×0.4583 + (1/3)×0
    = 0.4583

r_B = (1/2)×0.3333 + 0×0.2083 + 0×0.4583 + (1/3)×0
    = 0.1667

r_C = (1/2)×0.3333 + 1×0.2083 + 0×0.4583 + (1/3)×0
    = 0.1667 + 0.2083 = 0.375

r_D = 0

r⁽²⁾ = [0.4583, 0.1667, 0.375, 0]ᵀ
```

---

**Iteration 3:** r⁽³⁾ = M × r⁽²⁾

```
r_A = 1×0.375 = 0.375

r_B = (1/2)×0.4583 = 0.2292

r_C = (1/2)×0.4583 + 1×0.1667 = 0.2292 + 0.1667 = 0.3958

r_D = 0

r⁽³⁾ = [0.375, 0.2292, 0.3958, 0]ᵀ
```

---

**Bảng tổng hợp quá trình hội tụ:**

| Iteration | r_A | r_B | r_C | r_D | Tổng |
|-----------|-------|-------|-------|-------|------|
| 0 | 0.2500 | 0.2500 | 0.2500 | 0.2500 | 1.0 |
| 1 | 0.3333 | 0.2083 | 0.4583 | 0.0000 | 1.0 |
| 2 | 0.4583 | 0.1667 | 0.3750 | 0.0000 | 1.0 |
| 3 | 0.3750 | 0.2292 | 0.3958 | 0.0000 | 1.0 |

💡 **Nhận xét:** D không ai trỏ đến → PageRank = 0 sau iteration 1. Các trang A, B, C dần hội tụ.

---

## 2. Vấn đề: Dead Ends & Spider Traps

### 2.1. Dead Ends (Nút cụt)

⭐ **Định nghĩa:** Trang **không có link đi ra** (out-degree = 0)

**Hậu quả:** PageRank **rò rỉ (leak)** → tổng PageRank dần về 0!

📝 **Ví dụ 4: Dead End**

```
A --1--> B --1--> C (DEAD END — không có link đi ra!)
```

**Ma trận M:**

```
         A   B   C
    ┌               ┐
A:  │  0   0   0    │   ← Cột C toàn 0!
B:  │  1   0   0    │
C:  │  0   1   0    │
    └               ┘
```

⚠️ **Cột C toàn 0** (tổng cột C = 0 ≠ 1) → Ma trận **không phải column-stochastic!**

**Power Iteration:**

| Iter | r_A | r_B | r_C | Tổng |
|------|-------|-------|-------|------|
| 0 | 1/3 | 1/3 | 1/3 | 1.0 |
| 1 | 0 | 1/3 | 1/3 | 2/3 |
| 2 | 0 | 0 | 1/3 | 1/3 |
| 3 | 0 | 0 | 0 | **0** ❌ |

→ **Tổng PageRank giảm dần về 0!** Random Surfer bị "kẹt" ở C, không đi đâu được.

**Giải pháp → Teleportation** (xem mục 3)

---

### 2.2. Spider Traps (Bẫy nhện)

⭐ **Định nghĩa:** Nhóm trang tạo thành **vòng kín**, chỉ có link vào nhưng **link ra chỉ quay lại bên trong nhóm**

**Hậu quả:** Spider trap **hút hết PageRank** → các trang ngoài nhóm → 0

📝 **Ví dụ 5: Spider Trap**

```
A --1--> B --1--> C --1--> C  (C tự trỏ đến chính nó — spider trap!)
                   ↺
```

**Ma trận M:**

```
         A   B   C
    ┌               ┐
A:  │  0   0   0    │
B:  │  1   0   0    │
C:  │  0   1   1    │   ← C tự trỏ đến C!
    └               ┘
```

**Power Iteration:**

| Iter | r_A | r_B | r_C | Tổng |
|------|-------|-------|-------|------|
| 0 | 1/3 | 1/3 | 1/3 | 1.0 |
| 1 | 0 | 1/3 | 2/3 | 1.0 |
| 2 | 0 | 0 | **1.0** | 1.0 |
| 3 | 0 | 0 | **1.0** | 1.0 |

→ **C hút hết 100% PageRank!** Tổng vẫn = 1 (khác dead end), nhưng phân bố không hợp lý.

**Giải pháp → Damping factor β** (xem mục 3)

---

### 2.3. So sánh Dead End vs Spider Trap

| Đặc điểm | Dead End | Spider Trap |
|-----------|----------|-------------|
| **Vấn đề** | Rò rỉ PageRank (leak) | Hút hết PageRank (absorb) |
| **Tổng PR** | Giảm về 0 | Giữ nguyên = 1 |
| **Ma trận** | Cột toàn 0 (not stochastic) | Cột hợp lệ nhưng "kẹt" |
| **Random Surfer** | Bị kẹt, không đi đâu | Bị kẹt trong vòng lặp |
| **Giải pháp** | Teleportation | Damping factor β |

💡 **Mẹo nhớ:**
- **Dead End** = ngõ cụt → PageRank "chảy mất" (như nước rò rỉ)
- **Spider Trap** = bẫy nhện → PageRank "bị hút vào" (như hố đen)

---

## 3. Taxation / Teleportation Solution

### 3.1. Ý tưởng Teleportation

💡 **Ý tưởng:** Tại mỗi bước, Random Surfer có 2 lựa chọn:
- **Với xác suất β:** Đi theo link ngẫu nhiên trên trang hiện tại (như bình thường)
- **Với xác suất (1-β):** **Nhảy ngẫu nhiên** đến bất kỳ trang nào trong web (teleport!)

Điều này giải quyết **cả hai vấn đề**:
- Dead End: Surfer có thể teleport ra khỏi nút cụt
- Spider Trap: Surfer có thể teleport ra khỏi bẫy

### 3.2. Công thức PageRank với Damping Factor

⭐⭐⭐ **Công thức Google PageRank (CỰC KỲ QUAN TRỌNG):**

```
r' = β × M × r  +  (1 - β) / n × e
```

Trong đó:
| Ký hiệu | Ý nghĩa |
|----------|---------|
| β | **Damping factor** (hệ số giảm chấn), thường β = 0.8 hoặc 0.85 |
| M | Ma trận chuyển tiếp (stochastic adjacency matrix) |
| r | Vector PageRank hiện tại |
| n | Tổng số trang web |
| e | Vector toàn 1: e = (1, 1, ..., 1)ᵀ |
| (1-β)/n | Xác suất teleport đến mỗi trang |

### 3.3. Google Matrix

⭐ **Google Matrix A:**

```
A = β × M  +  (1 - β) / n × 𝟏
```

Trong đó **𝟏** là ma trận n×n toàn 1.

**Tính chất của Google Matrix:**
- ✅ Column-stochastic (tổng mỗi cột = 1)
- ✅ Không có cột toàn 0 (giải quyết dead end)
- ✅ Tất cả phần tử > 0 (giải quyết spider trap)
- ✅ **Đảm bảo hội tụ** đến nghiệm duy nhất!

### 3.4. Ví dụ tính PageRank với Damping Factor ⭐⭐⭐

📝 **Ví dụ 6: PageRank với β = 0.8 — Tính toán đầy đủ**

Cho đồ thị 3 trang: **A, B, C**

```
A → B, C    (A trỏ đến B và C)
B → C       (B trỏ đến C)
C → A       (C trỏ đến A)
```

**Bước 1: Xây dựng ma trận M**

```
         A     B     C
    ┌                     ┐
A:  │  0      0     1     │
B:  │  1/2    0     0     │
C:  │  1/2    1     0     │
    └                     ┘
```

**Bước 2: Tham số**
- β = 0.8
- n = 3
- (1 - β) / n = 0.2 / 3 = 0.0667

**Bước 3: Khởi tạo**

```
r⁽⁰⁾ = [1/3, 1/3, 1/3]ᵀ = [0.3333, 0.3333, 0.3333]ᵀ
```

---

**Iteration 1:**

Tính M × r⁽⁰⁾:

```
(M × r)_A = 0×0.3333 + 0×0.3333 + 1×0.3333 = 0.3333
(M × r)_B = 0.5×0.3333 + 0×0.3333 + 0×0.3333 = 0.1667
(M × r)_C = 0.5×0.3333 + 1×0.3333 + 0×0.3333 = 0.5000
```

Áp dụng công thức: r⁽¹⁾ = β × M × r⁽⁰⁾ + (1-β)/n × e

```
r_A = 0.8 × 0.3333 + 0.0667 = 0.2667 + 0.0667 = 0.3333
r_B = 0.8 × 0.1667 + 0.0667 = 0.1333 + 0.0667 = 0.2000
r_C = 0.8 × 0.5000 + 0.0667 = 0.4000 + 0.0667 = 0.4667

r⁽¹⁾ = [0.3333, 0.2000, 0.4667]ᵀ
```

✅ Kiểm tra tổng: 0.3333 + 0.2000 + 0.4667 = 1.0 ✓

---

**Iteration 2:**

Tính M × r⁽¹⁾:

```
(M × r)_A = 0×0.3333 + 0×0.2000 + 1×0.4667 = 0.4667
(M × r)_B = 0.5×0.3333 + 0×0.2000 + 0×0.4667 = 0.1667
(M × r)_C = 0.5×0.3333 + 1×0.2000 + 0×0.4667 = 0.3667
```

```
r_A = 0.8 × 0.4667 + 0.0667 = 0.3733 + 0.0667 = 0.4400
r_B = 0.8 × 0.1667 + 0.0667 = 0.1333 + 0.0667 = 0.2000
r_C = 0.8 × 0.3667 + 0.0667 = 0.2933 + 0.0667 = 0.3600

r⁽²⁾ = [0.4400, 0.2000, 0.3600]ᵀ
```

✅ Kiểm tra tổng: 0.4400 + 0.2000 + 0.3600 = 1.0 ✓

---

**Iteration 3:**

Tính M × r⁽²⁾:

```
(M × r)_A = 0 + 0 + 1×0.3600 = 0.3600
(M × r)_B = 0.5×0.4400 + 0 + 0 = 0.2200
(M × r)_C = 0.5×0.4400 + 1×0.2000 + 0 = 0.4200
```

```
r_A = 0.8 × 0.3600 + 0.0667 = 0.2880 + 0.0667 = 0.3547
r_B = 0.8 × 0.2200 + 0.0667 = 0.1760 + 0.0667 = 0.2427
r_C = 0.8 × 0.4200 + 0.0667 = 0.3360 + 0.0667 = 0.4027

r⁽³⁾ = [0.3547, 0.2427, 0.4027]ᵀ
```

✅ Kiểm tra tổng: 0.3547 + 0.2427 + 0.4027 ≈ 1.0 ✓

---

**Bảng tổng hợp quá trình hội tụ (β = 0.8):**

| Iteration | r_A | r_B | r_C | Tổng |
|-----------|-------|-------|-------|------|
| 0 | 0.3333 | 0.3333 | 0.3333 | 1.0 |
| 1 | 0.3333 | 0.2000 | 0.4667 | 1.0 |
| 2 | 0.4400 | 0.2000 | 0.3600 | 1.0 |
| 3 | 0.3547 | 0.2427 | 0.4027 | 1.0 |
| ... | ... | ... | ... | 1.0 |
| **∞ (hội tụ)** | **≈ 0.387** | **≈ 0.222** | **≈ 0.391** | **1.0** |

💡 **Nhận xét:**
- Trang **C** có PageRank cao nhất vì nhận link từ cả A và B
- Trang **A** cũng khá cao vì nhận link từ C (trang mạnh)
- Trang **B** thấp nhất vì chỉ nhận link từ A (chia cho 2 link)
- **Tổng luôn = 1** nhờ damping factor!

---

### 3.5. Xử lý Dead Ends trong thực tế

💡 **Hai cách xử lý Dead End:**

**Cách 1: Loại bỏ Dead Ends trước (Pruning)**
```
1. Tìm tất cả node dead-end (out-degree = 0)
2. Loại bỏ chúng khỏi đồ thị
3. Lặp lại (vì loại bỏ có thể tạo dead-end mới)
4. Tính PageRank trên đồ thị còn lại
5. Tính ngược PR cho các node đã loại bỏ
```

**Cách 2: Teleportation (Phổ biến hơn)**
```
Với node dead-end, thay cột toàn 0 bằng cột [1/n, 1/n, ..., 1/n]
→ Dead-end sẽ "teleport" đến bất kỳ trang nào với xác suất đều
```

---

## 4. PageRank với MapReduce / Spark

### 4.1. PageRank với MapReduce

⭐ **Ý tưởng:** Mỗi iteration của Power Iteration = **1 MapReduce job**

```
Input: Danh sách (page, current_PR, [outlinks])

MAP Phase:
  Với mỗi page p có PR = r và outlinks = [l₁, l₂, ..., lₖ]:
    - Emit (lᵢ, r/k) cho mỗi outlink lᵢ     ← Chia PR cho outlinks
    - Emit (p, [l₁, l₂, ..., lₖ])              ← Giữ cấu trúc đồ thị

REDUCE Phase:
  Với mỗi page p, nhận tất cả contributions:
    - new_PR(p) = β × Σ(contributions) + (1-β)/n
    - Emit (p, new_PR, [outlinks])
```

📝 **Ví dụ MapReduce cho 1 iteration:**

```
=== INPUT ===
(A, 0.25, [B, C])
(B, 0.25, [C])
(C, 0.25, [A])
(D, 0.25, [A, B, C])

=== MAP OUTPUT ===
(B, 0.125)      ← từ A: 0.25/2
(C, 0.125)      ← từ A: 0.25/2
(A, [B,C])      ← cấu trúc của A

(C, 0.25)       ← từ B: 0.25/1
(B, [C])        ← cấu trúc của B

(A, 0.25)       ← từ C: 0.25/1
(C, [A])        ← cấu trúc của C

(A, 0.0833)     ← từ D: 0.25/3
(B, 0.0833)     ← từ D: 0.25/3
(C, 0.0833)     ← từ D: 0.25/3
(D, [A,B,C])    ← cấu trúc của D

=== REDUCE OUTPUT (β = 0.8, n = 4) ===
A: 0.8 × (0.25 + 0.0833) + 0.2/4 = 0.8 × 0.3333 + 0.05 = 0.3167
B: 0.8 × (0.125 + 0.0833) + 0.05 = 0.8 × 0.2083 + 0.05 = 0.2167
C: 0.8 × (0.125 + 0.25 + 0.0833) + 0.05 = 0.8 × 0.4583 + 0.05 = 0.4167
D: 0.8 × 0 + 0.05 = 0.05
```

**Vấn đề của MapReduce:**

⚠️ Mỗi iteration = 1 MapReduce job → Đọc/ghi HDFS mỗi lần!

```
Iteration 1: Read HDFS → Map → Shuffle → Reduce → Write HDFS
Iteration 2: Read HDFS → Map → Shuffle → Reduce → Write HDFS
Iteration 3: Read HDFS → Map → Shuffle → Reduce → Write HDFS
...
→ Rất CHẬM vì I/O disk lặp đi lặp lại!
```

### 4.2. PageRank với Spark — Tại sao tốt hơn?

⭐ **Spark giải quyết bằng in-memory caching:**

```python
# Spark PageRank (pseudo-code)
links = sc.textFile("links.txt").map(parseLinks).cache()  # Cache đồ thị!
ranks = links.mapValues(lambda _: 1.0 / N)  # Khởi tạo PR

for i in range(num_iterations):
    contribs = links.join(ranks).flatMap(computeContribs)
    ranks = contribs.reduceByKey(add).mapValues(
        lambda r: 0.85 * r + 0.15 / N
    )

ranks.saveAsTextFile("output")
```

**So sánh MapReduce vs Spark cho PageRank:**

| Tiêu chí | MapReduce | Spark |
|-----------|-----------|-------|
| **Lưu đồ thị** | Đọc lại từ HDFS mỗi iter | **Cache trong RAM** |
| **Truyền dữ liệu** | Qua disk (HDFS) | **Trong bộ nhớ** |
| **Tốc độ** | Chậm (I/O bound) | **Nhanh hơn 10-100x** |
| **Sử dụng** | Nhiều job nối tiếp | **1 chương trình, nhiều iter** |
| **Đồ thị (links)** | Đọc lại mỗi iter | **cache() / persist()** |

💡 **Tại sao Spark nhanh hơn nhiều cho PageRank:**
1. **Đồ thị (links) không đổi** qua các iteration → `cache()` trong RAM, đọc 1 lần
2. **Ranks** cũng giữ trong RAM → không cần ghi/đọc HDFS giữa các iteration
3. **Lineage** cho phép tự phục hồi nếu partition bị mất
4. Spark chỉ cần **ghi kết quả cuối cùng** ra HDFS

---

## 5. Thuật toán HITS (Hyperlink-Induced Topic Search)

### 5.1. Khái niệm Hub và Authority

⭐ **Hai loại trang quan trọng:**

| Loại | Ý nghĩa | Ví dụ |
|------|---------|-------|
| **Authority** | Trang có **nội dung chất lượng**, được nhiều trang trỏ đến | Wikipedia, trang chính thức |
| **Hub** | Trang **tổng hợp link** đến nhiều authority tốt | Trang danh mục, Yahoo Directory |

💡 **Quan hệ tương hỗ (Mutual Reinforcement):**
- Trang **Hub tốt** = trỏ đến nhiều **Authority tốt**
- Trang **Authority tốt** = được nhiều **Hub tốt** trỏ đến

```
Hub 1 (h=cao) ──→ Authority 1 (a=cao)
Hub 1 (h=cao) ──→ Authority 2 (a=cao)
Hub 2 (h=cao) ──→ Authority 1 (a=cao)
Hub 2 (h=cao) ──→ Authority 2 (a=cao)
Hub 3 (h=thấp) ─→ Authority 3 (a=thấp)
```

### 5.2. Công thức HITS

⭐ **Authority score update:**

```
a(p) = Σ h(q)    với mọi q trỏ đến p (q → p)
```

> Authority của p = Tổng Hub score của tất cả trang **trỏ đến** p

⭐ **Hub score update:**

```
h(p) = Σ a(q)    với mọi q mà p trỏ đến (p → q)
```

> Hub score của p = Tổng Authority score của tất cả trang mà p **trỏ đến**

### 5.3. Thuật toán HITS — Các bước

```
Bước 1: Khởi tạo h(p) = 1, a(p) = 1 cho mọi trang p
Bước 2: Lặp:
   a) Authority update: a(p) = Σ h(q)  với q → p
   b) Hub update:       h(p) = Σ a(q)  với p → q
   c) Chuẩn hóa (Normalize):
      - Chia a cho max(a) hoặc sqrt(Σa²)
      - Chia h cho max(h) hoặc sqrt(Σh²)
Bước 3: Lặp lại cho đến khi hội tụ
```

⚠️ **Quan trọng:** Phải **chuẩn hóa** sau mỗi iteration, nếu không giá trị sẽ phát tán vô hạn!

**Các cách chuẩn hóa phổ biến:**
- **Scale theo max:** a_i = a_i / max(a), h_i = h_i / max(h)
- **Scale theo norm-2:** a_i = a_i / √(Σ a_j²)
- **Scale theo tổng:** a_i = a_i / Σ a_j

### 5.4. Ví dụ HITS chi tiết ⭐⭐⭐

📝 **Ví dụ 7: Thuật toán HITS**

Cho đồ thị 4 trang:

```
1 → 2, 3
2 → 3
3 → 4
4 → 3
```

```
  1 ──→ 2
  │      │
  ↓      ↓
  3 ←──→ 4
  ↑      │
  └──────┘
```

**Adjacency List (ai trỏ đến ai):**

| Trang | Trỏ đến (out) | Được trỏ từ (in) |
|-------|---------------|-------------------|
| 1 | 2, 3 | — |
| 2 | 3 | 1 |
| 3 | 4 | 1, 2, 4 |
| 4 | 3 | 3 |

---

**Bước 1: Khởi tạo**

| Trang | a | h |
|-------|---|---|
| 1 | 1 | 1 |
| 2 | 1 | 1 |
| 3 | 1 | 1 |
| 4 | 1 | 1 |

---

**Iteration 1:**

**a) Authority update: a(p) = Σ h(q) với q → p**

```
a(1) = 0                           (không ai trỏ đến 1)
a(2) = h(1) = 1                    (chỉ 1 trỏ đến 2)
a(3) = h(1) + h(2) + h(4) = 1+1+1 = 3   (1, 2, 4 trỏ đến 3)
a(4) = h(3) = 1                    (chỉ 3 trỏ đến 4)
```

Authority trước chuẩn hóa: a = (0, 1, 3, 1)

**b) Hub update: h(p) = Σ a(q) với p → q** (dùng authority MỚI)

```
h(1) = a(2) + a(3) = 1 + 3 = 4    (1 trỏ đến 2, 3)
h(2) = a(3) = 3                    (2 trỏ đến 3)
h(3) = a(4) = 1                    (3 trỏ đến 4)
h(4) = a(3) = 3                    (4 trỏ đến 3)
```

Hub trước chuẩn hóa: h = (4, 3, 1, 3)

**c) Chuẩn hóa (Scale theo max):**

Authority: max(a) = 3
```
a = (0/3, 1/3, 3/3, 1/3) = (0, 0.333, 1, 0.333)
```

Hub: max(h) = 4
```
h = (4/4, 3/4, 1/4, 3/4) = (1, 0.75, 0.25, 0.75)
```

---

**Iteration 2:**

**a) Authority update: a(p) = Σ h(q) với q → p**

```
a(1) = 0
a(2) = h(1) = 1
a(3) = h(1) + h(2) + h(4) = 1 + 0.75 + 0.75 = 2.5
a(4) = h(3) = 0.25
```

Authority trước chuẩn hóa: a = (0, 1, 2.5, 0.25)

**b) Hub update: h(p) = Σ a(q) với p → q**

```
h(1) = a(2) + a(3) = 1 + 2.5 = 3.5
h(2) = a(3) = 2.5
h(3) = a(4) = 0.25
h(4) = a(3) = 2.5
```

Hub trước chuẩn hóa: h = (3.5, 2.5, 0.25, 2.5)

**c) Chuẩn hóa (Scale theo max):**

```
a = (0/2.5, 1/2.5, 2.5/2.5, 0.25/2.5) = (0, 0.4, 1, 0.1)
h = (3.5/3.5, 2.5/3.5, 0.25/3.5, 2.5/3.5) = (1, 0.714, 0.071, 0.714)
```

---

**Iteration 3:**

**a) Authority update:**

```
a(1) = 0
a(2) = h(1) = 1
a(3) = h(1) + h(2) + h(4) = 1 + 0.714 + 0.714 = 2.428
a(4) = h(3) = 0.071
```

Chuẩn hóa: a = (0, 1/2.428, 2.428/2.428, 0.071/2.428) = **(0, 0.412, 1, 0.029)**

**b) Hub update:**

```
h(1) = a(2) + a(3) = 0.412 + 1 = 1.412
h(2) = a(3) = 1
h(3) = a(4) = 0.029
h(4) = a(3) = 1
```

Chuẩn hóa: h = (1.412/1.412, 1/1.412, 0.029/1.412, 1/1.412) = **(1, 0.708, 0.021, 0.708)**

---

**Bảng tổng hợp hội tụ:**

| Iter | a₁ | a₂ | a₃ | a₄ | h₁ | h₂ | h₃ | h₄ |
|------|-----|------|------|------|------|------|------|------|
| 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| 1 | 0 | 0.333 | **1** | 0.333 | **1** | 0.750 | 0.250 | 0.750 |
| 2 | 0 | 0.400 | **1** | 0.100 | **1** | 0.714 | 0.071 | 0.714 |
| 3 | 0 | 0.412 | **1** | 0.029 | **1** | 0.708 | 0.021 | 0.708 |

💡 **Nhận xét:**
- **Trang 3** có Authority cao nhất (= 1) vì được nhiều trang trỏ đến nhất (1, 2, 4)
- **Trang 1** có Hub score cao nhất (= 1) vì trỏ đến 2 trang có authority cao (2 và 3)
- **Trang 1** có Authority = 0 vì không ai trỏ đến nó
- **Trang 3** có Hub score gần 0 vì chỉ trỏ đến trang 4 (authority thấp)

### 5.5. Dạng Ma trận của HITS

⭐ **Sử dụng Adjacency Matrix L:**

```
L_ij = 1   nếu trang i trỏ đến trang j
L_ij = 0   ngược lại
```

Với đồ thị ở Ví dụ 7:

```
     1  2  3  4
┌                ┐
│  0  1  1  0    │   ← Trang 1 trỏ đến 2, 3
│  0  0  1  0    │   ← Trang 2 trỏ đến 3
│  0  0  0  1    │   ← Trang 3 trỏ đến 4
│  0  0  1  0    │   ← Trang 4 trỏ đến 3
└                ┘
```

**Công thức ma trận:**

```
a = Lᵀ × h    (Authority update)
h = L  × a    (Hub update)
```

Kết hợp lại:

```
a = Lᵀ L × a    (Authority là eigenvector của LᵀL)
h = L Lᵀ × h    (Hub là eigenvector của LLᵀ)
```

### 5.6. So sánh PageRank vs HITS ⭐⭐

| Tiêu chí | PageRank | HITS |
|-----------|----------|------|
| **Người phát triển** | Larry Page & Sergey Brin (Google) | Jon Kleinberg (Cornell) |
| **Loại điểm** | 1 điểm duy nhất (PageRank) | 2 điểm: Hub + Authority |
| **Thời điểm tính** | **Offline** (tính trước, lưu kết quả) | **Online** (tính khi có query) |
| **Phạm vi** | Toàn bộ web | Chỉ trên **tập kết quả** liên quan đến query |
| **Phụ thuộc query** | ❌ Không (query-independent) | ✅ Có (query-dependent) |
| **Xử lý spam** | Khó bị spam (toàn cục) | Dễ bị spam hơn (cục bộ) |
| **Teleportation** | Có (damping factor β) | Không |
| **Ứng dụng** | Google Search | Nghiên cứu, phân tích mạng |

💡 **Mẹo nhớ:**
- **PageRank** = "Dân chủ": Mỗi trang có 1 phiếu, chia đều cho link → tính cho **toàn bộ web** trước
- **HITS** = "Chuyên gia": Phân loại trang thành Hub/Authority → tính **theo từng query** cụ thể

---

## 6. Các dạng bài thi thường gặp

### Dạng 1: Xây dựng Transition Matrix

> Cho đồ thị web, xây dựng ma trận chuyển tiếp M.

**Cách làm:**
1. Xác định out-degree mỗi node
2. Mỗi cột i: chia 1/d_i cho các hàng tương ứng với trang mà i trỏ đến
3. Kiểm tra tổng mỗi cột = 1

### Dạng 2: Power Iteration (Không damping)

> Cho ma trận M, tính PageRank sau k iterations.

**Cách làm:**
1. Khởi tạo r⁽⁰⁾ = [1/n, ..., 1/n]ᵀ
2. Lặp: r⁽ᵗ⁺¹⁾ = M × r⁽ᵗ⁾
3. Kiểm tra tổng = 1 sau mỗi bước

### Dạng 3: Power Iteration (Có damping β) ⭐⭐⭐

> Cho đồ thị, β, tính PageRank.

**Cách làm:**
1. Xây dựng M
2. Khởi tạo r⁽⁰⁾
3. Lặp: r⁽ᵗ⁺¹⁾ = β × M × r⁽ᵗ⁾ + (1-β)/n × e
4. Kiểm tra tổng = 1

### Dạng 4: Nhận diện Dead End / Spider Trap

> Cho đồ thị, xác định vấn đề và giải thích hậu quả.

### Dạng 5: Tính HITS

> Cho đồ thị, tính Hub và Authority score sau k iterations.

**Cách làm:**
1. Khởi tạo h = a = 1
2. Authority update: a(p) = Σ h(q) với q → p
3. Hub update: h(p) = Σ a(q) với p → q
4. Chuẩn hóa
5. Lặp lại

---

## 📋 TỔNG HỢP CÔNG THỨC & KEY POINTS

```
╔══════════════════════════════════════════════════════════════════════╗
║                    CÔNG THỨC CẦN NHỚ CHO BÀI THI                  ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  1. PageRank cơ bản:     r_j = Σ(i→j) r_i / d_i                    ║
║                                                                      ║
║  2. Dạng ma trận:        r = M × r  (eigenvector, eigenvalue=1)     ║
║                                                                      ║
║  3. ⭐ Với damping:      r' = β·M·r + (1-β)/n · e                  ║
║                                                                      ║
║  4. Google Matrix:       A = β·M + (1-β)/n · 𝟏                     ║
║                                                                      ║
║  5. HITS Authority:      a(p) = Σ h(q)  với q → p                  ║
║                                                                      ║
║  6. HITS Hub:            h(p) = Σ a(q)  với p → q                  ║
║                                                                      ║
║  7. HITS ma trận:        a = Lᵀ·h,  h = L·a                        ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║                      CHECKLIST LÀM BÀI                              ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  ☐ Ma trận M: CỘT = nguồn, HÀNG = đích, tổng cột = 1             ║
║  ☐ Kiểm tra TỔNG PageRank = 1 sau mỗi iteration                   ║
║  ☐ Dead End → cột toàn 0 → tổng PR giảm về 0                      ║
║  ☐ Spider Trap → PR bị hút hết vào trap (tổng vẫn = 1)            ║
║  ☐ HITS: PHẢI chuẩn hóa sau mỗi iteration!                        ║
║  ☐ PageRank = offline, query-independent                            ║
║  ☐ HITS = online, query-dependent                                   ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║                    GIÁ TRỊ THƯỜNG DÙNG                              ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  β (damping)     = 0.8 hoặc 0.85 (Google dùng 0.85)                ║
║  Khởi tạo PR     = 1/n cho mỗi trang                                ║
║  Khởi tạo HITS   = h = a = 1 cho mọi trang                         ║
║  Hội tụ          = |r(t+1) - r(t)| < ε  (ε ≈ 10⁻⁶)               ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

💡 **Mẹo làm bài thi nhanh:**

1. **Vẽ đồ thị** trước khi tính — giúp tránh nhầm link
2. **Ghi rõ out-degree** cạnh mỗi node trên đồ thị
3. **Kiểm tra tổng = 1** sau mỗi iteration (nếu ≠ 1 → sai ở đâu đó!)
4. **Nhân ma trận theo cột**: Mỗi phần tử kết quả = tổng (phần tử hàng × phần tử cột tương ứng)
5. Với HITS: Tính **Authority trước**, rồi dùng Authority mới để tính Hub
6. **Damping factor** chỉ xuất hiện trong PageRank, KHÔNG có trong HITS
