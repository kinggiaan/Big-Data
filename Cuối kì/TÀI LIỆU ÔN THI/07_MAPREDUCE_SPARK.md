# CHƯƠNG 7: MAPREDUCE & SPARK

> **Mục tiêu**: Hiểu mô hình lập trình MapReduce, các ứng dụng điển hình, và framework Apache Spark.
> Đây là chương **trọng tâm** của môn Big Data — chiếm tỷ trọng lớn trong đề thi.

---

## 1. Mô hình MapReduce

### 1.1. Tổng quan

⭐ **MapReduce** là mô hình lập trình song song để xử lý dữ liệu lớn trên cụm máy tính phân tán (cluster), được Google giới thiệu năm 2004.

**Ý tưởng cốt lõi**: Chia bài toán lớn thành nhiều bài toán nhỏ → xử lý song song → tổng hợp kết quả.

### 1.2. Ba giai đoạn chính

```
Input → [MAP] → Shuffle & Sort → [REDUCE] → Output
```

| Giai đoạn | Input | Output | Mô tả |
|-----------|-------|--------|-------|
| **Map** | `(k1, v1)` | `list of (k2, v2)` | Biến đổi từng cặp input thành danh sách các cặp trung gian |
| **Shuffle & Sort** | `list of (k2, v2)` | `(k2, list(v2))` | Nhóm tất cả value có cùng key lại với nhau |
| **Reduce** | `(k2, list(v2))` | `(k3, v3)` | Tổng hợp các value cùng key thành kết quả cuối |

⭐ **Ghi nhớ quan trọng**:
- **Map**: Phát ra (emit) các cặp key-value trung gian
- **Shuffle & Sort**: Hệ thống tự động làm (programmer KHÔNG viết)
- **Reduce**: Nhận tất cả value cùng key, tổng hợp lại

### 1.3. Word Count — Ví dụ kinh điển

📝 **Ví dụ**: Đếm số lần xuất hiện của mỗi từ trong tập văn bản.

**Input**: 2 dòng văn bản
```
Dòng 1: "hello world hello"
Dòng 2: "world big data"
```

**Luồng dữ liệu đầy đủ**:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        GIAI ĐOẠN MAP                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Mapper 1: "hello world hello"                                      │
│     → (hello, 1), (world, 1), (hello, 1)                           │
│                                                                     │
│  Mapper 2: "world big data"                                         │
│     → (world, 1), (big, 1), (data, 1)                              │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                     GIAI ĐOẠN SHUFFLE & SORT                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  (big,   [1])                                                       │
│  (data,  [1])                                                       │
│  (hello, [1, 1])                                                    │
│  (world, [1, 1])                                                    │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                       GIAI ĐOẠN REDUCE                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Reducer: (big,   [1])    → (big,   1)                              │
│  Reducer: (data,  [1])    → (data,  1)                              │
│  Reducer: (hello, [1, 1]) → (hello, 2)                              │
│  Reducer: (world, [1, 1]) → (world, 2)                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Output cuối cùng**: `(big, 1), (data, 1), (hello, 2), (world, 2)`

### 1.4. Combiner — Tối ưu cục bộ

⭐ **Combiner** = "Mini-Reducer" chạy **ngay tại node Map** trước khi gửi dữ liệu qua mạng.

**Mục đích**: Giảm lượng dữ liệu truyền qua mạng (network I/O).

```
Map → [COMBINER] → Shuffle & Sort → Reduce
```

📝 **Ví dụ với Word Count**:

```
Mapper 1 output: (hello, 1), (world, 1), (hello, 1)
                              ↓ Combiner
Sau Combiner:    (hello, 2), (world, 1)     ← Giảm từ 3 cặp còn 2 cặp!
```

⭐ **Khi nào ĐƯỢC dùng Combiner?**

| Điều kiện | Giải thích | Ví dụ |
|-----------|-----------|-------|
| Phép toán **kết hợp** (associative) | `(a ⊕ b) ⊕ c = a ⊕ (b ⊕ c)` | SUM, COUNT, MAX, MIN |
| Phép toán **giao hoán** (commutative) | `a ⊕ b = b ⊕ a` | SUM, COUNT, MAX, MIN |

⚠️ **Khi nào KHÔNG ĐƯỢC dùng Combiner?**

| Trường hợp | Lý do |
|-------------|-------|
| **Tính AVERAGE (trung bình)** | Trung bình cục bộ ≠ Trung bình toàn cục |
| **Tính MEDIAN** | Median cục bộ ≠ Median toàn cục |
| **Phép toán KHÔNG kết hợp** | Kết quả sai khi combine một phần |

📝 **Ví dụ tại sao Average KHÔNG dùng Combiner được**:

```
Node 1: (temp, [10, 20])     → Combiner avg = 15
Node 2: (temp, [30])         → Combiner avg = 30

Reduce nhận: (temp, [15, 30]) → avg = 22.5   ← SAI ❌
Kết quả đúng: (10 + 20 + 30) / 3 = 20       ← ĐÚNG ✅
```

💡 **Mẹo thi**: Nếu đề hỏi "có thể dùng Combiner không?", kiểm tra tính **kết hợp + giao hoán**. Nếu cả hai đều thỏa → ĐƯỢC. Ngược lại → KHÔNG.

💡 **Workaround cho Average**: Emit `(key, (sum, count))` rồi Combiner cộng sum và count riêng → Reduce tính `sum/count`.

### 1.5. Partitioner — Phân phối dữ liệu cho Reducer

**Partitioner** quyết định key nào đi đến Reducer nào.

| Loại | Công thức | Đặc điểm |
|------|-----------|-----------|
| **HashPartitioner** (mặc định) | `hash(key) mod R` | R = số Reducer, phân phối đều |
| **Custom Partitioner** | Do lập trình viên định nghĩa | Khi cần kiểm soát phân phối |

📝 **Ví dụ HashPartitioner** (R = 3 Reducers):

```
hash("hello") mod 3 = 0  → Reducer 0
hash("world") mod 3 = 1  → Reducer 1
hash("big")   mod 3 = 2  → Reducer 2
hash("data")  mod 3 = 0  → Reducer 0
```

⚠️ **Data Skew**: Nếu key phân bố không đều → một Reducer quá tải → cần Custom Partitioner.

### 1.6. Communication Cost (Chi phí truyền thông)

⭐ **Công thức**:

$$\text{Communication Cost} = r \times |I|$$

Trong đó:
- `r` = **số lần replication** (mỗi bản sao input cần cho bao nhiêu task)
- `|I|` = **kích thước input**

💡 **Ý nghĩa**: Đo lượng dữ liệu cần truyền qua mạng giữa Map và Reduce.

📝 **Ví dụ**:
- Word Count: `r = 1` (mỗi chunk input chỉ cần cho 1 Mapper) → Cost = `|I|`
- Natural Join: `r` có thể > 1 nếu cùng dữ liệu gửi cho nhiều Reducer

---

## 2. Ứng dụng MapReduce

### 2.1. Word Count — Pseudocode đầy đủ

⭐ **Đây là ví dụ kinh điển nhất — HỌC THUỘC!**

```python
# ==================== MAP ====================
def map(key, value):
    # key: document_id (bỏ qua)
    # value: nội dung dòng văn bản
    for word in value.split():
        emit(word, 1)

# ==================== COMBINER (tùy chọn) ====================
def combine(key, values):
    # key: word
    # values: list of counts [1, 1, 1, ...]
    emit(key, sum(values))

# ==================== REDUCE ====================
def reduce(key, values):
    # key: word
    # values: list of counts [1, 1, 1, ...]
    total = 0
    for count in values:
        total += count
    emit(key, total)
```

### 2.2. Natural Join — R(A,B) ⋈ S(B,C)

⭐ **Đây là dạng bài thường gặp trong đề thi!**

**Bài toán**: Join hai bảng R(A,B) và S(B,C) trên cột B.

**Chiến lược**: Dùng B làm key, gắn tag để phân biệt nguồn.

```python
# ==================== MAP ====================
def map(key, value):
    if value from R:
        # Tuple R(a, b)
        emit(b, ("R", a))      # key = join_key, value = (tag, data)
    elif value from S:
        # Tuple S(b, c)
        emit(b, ("S", c))      # key = join_key, value = (tag, data)

# ==================== REDUCE ====================
def reduce(key, values):
    # key = b (join key)
    # values = list of ("R", a) and ("S", c)
    R_list = [a for (tag, a) in values if tag == "R"]
    S_list = [c for (tag, c) in values if tag == "S"]

    # Cross product: mỗi a ghép với mỗi c
    for a in R_list:
        for c in S_list:
            emit((a, key, c), None)   # Output: (a, b, c)
```

📝 **Ví dụ cụ thể**:

```
R(A, B):                    S(B, C):
┌─────┬─────┐              ┌─────┬─────┐
│  A  │  B  │              │  B  │  C  │
├─────┼─────┤              ├─────┼─────┤
│ a1  │ b1  │              │ b1  │ c1  │
│ a2  │ b1  │              │ b1  │ c2  │
│ a3  │ b2  │              │ b2  │ c3  │
└─────┴─────┘              └─────┴─────┘
```

**Giai đoạn Map**:
```
Từ R: (b1, ("R", a1)), (b1, ("R", a2)), (b2, ("R", a3))
Từ S: (b1, ("S", c1)), (b1, ("S", c2)), (b2, ("S", c3))
```

**Sau Shuffle & Sort**:
```
b1 → [("R", a1), ("R", a2), ("S", c1), ("S", c2)]
b2 → [("R", a3), ("S", c3)]
```

**Giai đoạn Reduce** (cross product):
```
b1: a1×c1, a1×c2, a2×c1, a2×c2 → (a1,b1,c1), (a1,b1,c2), (a2,b1,c1), (a2,b1,c2)
b2: a3×c3                       → (a3,b2,c3)
```

⚠️ **Chú ý**: Reduce thực hiện **tích chéo (cross product)** giữa R_list và S_list, KHÔNG phải phép cộng!

### 2.3. Matrix Multiplication — M(m×n) × N(n×p)

⭐ **Kết quả**: P = M × N, trong đó `P[i][j] = Σ(k=1→n) M[i][k] × N[k][j]`

**Chiến lược**: Key = (i, j) vị trí trong ma trận kết quả.

```python
# ==================== MAP ====================
def map(key, value):
    if value from M:
        # M[i][k] = m_ik
        for j in range(p):             # p = số cột ma trận N
            emit((i, j), ("M", k, m_ik))
    elif value from N:
        # N[k][j] = n_kj
        for i in range(m):             # m = số hàng ma trận M
            emit((i, j), ("N", k, n_kj))

# ==================== REDUCE ====================
def reduce(key, values):
    # key = (i, j)
    # values = list of ("M", k, m_ik) and ("N", k, n_kj)
    M_dict = {}
    N_dict = {}

    for (tag, k, val) in values:
        if tag == "M":
            M_dict[k] = val    # M[i][k]
        else:
            N_dict[k] = val    # N[k][j]

    result = 0
    for k in M_dict:
        if k in N_dict:
            result += M_dict[k] * N_dict[k]

    emit(key, result)          # P[i][j]
```

📝 **Ví dụ**:

```
M (2×3):            N (3×2):
┌───┬───┬───┐       ┌───┬───┐
│ 1 │ 2 │ 3 │       │ 7 │ 8 │
│ 4 │ 5 │ 6 │       │ 9 │10 │
└───┴───┴───┘       │11 │12 │
                    └───┴───┘

P[0][0] = 1×7 + 2×9 + 3×11 = 7 + 18 + 33 = 58
```

**Communication Cost**: Mỗi phần tử M[i][k] gửi p lần (cho mỗi j), mỗi phần tử N[k][j] gửi m lần (cho mỗi i).

$$\text{Cost} = m \cdot n \cdot p + n \cdot p \cdot m = 2 \cdot m \cdot n \cdot p$$

### 2.4. DISTINCT

```python
# ==================== MAP ====================
def map(key, value):
    emit(value, None)          # Dùng value làm key

# ==================== REDUCE ====================
def reduce(key, values):
    emit(key, None)            # Chỉ emit 1 lần cho mỗi key
```

💡 **Nguyên lý**: Shuffle & Sort tự động nhóm các giá trị giống nhau → Reduce chỉ cần emit 1 lần.

### 2.5. GROUP BY với Aggregation

📝 **Ví dụ**: `SELECT department, SUM(salary) FROM employees GROUP BY department`

```python
# ==================== MAP ====================
def map(key, value):
    # value = employee record
    dept = value.department
    salary = value.salary
    emit(dept, salary)

# ==================== REDUCE ====================
def reduce(key, values):
    # key = department
    # values = list of salaries
    emit(key, sum(values))
```

💡 **Combiner**: CÓ THỂ dùng cho SUM, COUNT, MAX, MIN. KHÔNG dùng cho AVG.

### 2.6. Bảng tóm tắt các ứng dụng

| Ứng dụng | Map emit | Reduce xử lý | Combiner? |
|-----------|----------|---------------|-----------|
| **Word Count** | `(word, 1)` | `sum(counts)` | ✅ Có |
| **Natural Join** | `(join_key, (tag, data))` | Cross product | ❌ Không |
| **Matrix Multiply** | `((i,j), (tag, k, val))` | Dot product | ❌ Không |
| **DISTINCT** | `(value, null)` | Emit 1 lần | ✅ Có |
| **GROUP BY SUM** | `(group_key, value)` | `sum(values)` | ✅ Có |
| **GROUP BY AVG** | `(group_key, value)` | `sum/count` | ⚠️ Phải emit (sum, count) |

---

## 3. Apache Spark

### 3.1. Tổng quan

⭐ **Apache Spark** là framework xử lý dữ liệu lớn **in-memory**, nhanh hơn MapReduce gấp **10-100 lần**.

**Kiến trúc Spark**:

```
┌──────────────────────────────────────┐
│           Spark Application          │
├──────────────────────────────────────┤
│    Spark SQL │ MLlib │ GraphX │ ...  │
├──────────────────────────────────────┤
│           Spark Core (RDD)           │
├──────────────────────────────────────┤
│  YARN / Mesos / Standalone / K8s    │
├──────────────────────────────────────┤
│   HDFS / S3 / Cassandra / HBase     │
└──────────────────────────────────────┘
```

### 3.2. RDD — Resilient Distributed Dataset

⭐ **RDD** là cấu trúc dữ liệu nền tảng của Spark.

**Ba đặc tính quan trọng** (nhớ chữ **RDD**!):

| Đặc tính | Giải thích |
|----------|-----------|
| **R**esilient (Bền bỉ) | Khôi phục được khi lỗi nhờ **lineage** (đồ thị phụ thuộc) |
| **D**istributed (Phân tán) | Dữ liệu chia thành nhiều partition trên cluster |
| **D**ataset (Tập dữ liệu) | Tập hợp các phần tử có thể thao tác song song |

**Đặc điểm bổ sung**:
- **Immutable** (bất biến): Không thể thay đổi sau khi tạo, chỉ tạo RDD mới qua transformation
- **Lazy evaluation**: Chỉ thực thi khi gặp Action
- **Type-safe**: Biết kiểu dữ liệu tại compile time

**Fault Tolerance qua Lineage**:

```
textFile ──map──→ words ──flatMap──→ pairs ──reduceByKey──→ counts
   │                │                  │                      │
   └────────────────┴──────────────────┴──────────────────────┘
              Lineage Graph (DAG) — lưu lại cách tạo RDD
              Nếu partition bị mất → tính lại từ lineage
```

⚠️ **Lineage vs Replication**: MapReduce dùng replication (ghi 3 bản sao lên HDFS), Spark dùng lineage (ghi nhớ cách tính lại) → nhẹ hơn nhiều!

### 3.3. Transformations vs Actions

⭐⭐ **ĐÂY LÀ BẢNG CỰC KỲ QUAN TRỌNG — HỌC THUỘC!**

| Transformations (Lazy — KHÔNG thực thi ngay) | Actions (Eager — KÍCH HOẠT thực thi) |
|----------------------------------------------|---------------------------------------|
| `map(func)` — áp hàm lên từng phần tử | `collect()` — trả tất cả về driver |
| `filter(func)` — lọc theo điều kiện | `count()` — đếm số phần tử |
| `flatMap(func)` — map rồi flatten | `first()` — lấy phần tử đầu |
| `mapValues(func)` — map chỉ trên value | `take(n)` — lấy n phần tử đầu |
| `reduceByKey(func)` — reduce theo key | `reduce(func)` — tổng hợp tất cả |
| `groupByKey()` — nhóm theo key | `saveAsTextFile(path)` — ghi ra file |
| `sortByKey()` — sắp xếp theo key | `foreach(func)` — áp hàm lên từng phần tử |
| `join(rdd)` — join hai RDD | `countByKey()` — đếm theo key |
| `union(rdd)` — hợp hai RDD | `takeSample()` — lấy mẫu ngẫu nhiên |
| `distinct()` — loại bỏ trùng lặp | `takeOrdered(n)` — lấy n phần tử đã sắp xếp |
| `intersection(rdd)` — giao hai RDD | `top(n)` — lấy n phần tử lớn nhất |
| `coalesce(n)` — giảm partition | |
| `repartition(n)` — thay đổi partition | |

💡 **Cách nhớ**:
- **Transformation** = "biến đổi" → tạo RDD mới, CHƯA chạy (lazy)
- **Action** = "hành động" → KÍCH HOẠT chạy cả chuỗi transformation, trả kết quả

⚠️ **Câu hỏi thường gặp**: "Cho đoạn code Spark, bao nhiêu job được tạo?" → Đếm số **Action**!

```python
rdd = sc.textFile("data.txt")        # Không chạy
words = rdd.flatMap(lambda x: x.split())  # Không chạy (transformation)
pairs = words.map(lambda x: (x, 1))       # Không chạy (transformation)
counts = pairs.reduceByKey(lambda a,b: a+b) # Không chạy (transformation)
result = counts.collect()                   # CHẠY! (action) → 1 job
counts.saveAsTextFile("output")            # CHẠY! (action) → 1 job nữa
# Tổng cộng: 2 jobs
```

### 3.4. Narrow vs Wide Transformations

⭐ **Phân biệt rất quan trọng cho hiểu performance!**

| Tiêu chí | Narrow Transformation | Wide Transformation |
|-----------|----------------------|---------------------|
| **Shuffle?** | ❌ KHÔNG | ✅ CÓ (tốn kém!) |
| **Phụ thuộc** | Mỗi partition con phụ thuộc ≤ 1 partition cha | Mỗi partition con phụ thuộc NHIỀU partition cha |
| **Ví dụ** | `map`, `filter`, `flatMap`, `mapValues`, `union`, `coalesce` | `groupByKey`, `reduceByKey`, `join`, `sortByKey`, `distinct`, `repartition` |
| **Stage** | Cùng stage | Tạo stage mới |
| **Tốc độ** | Nhanh (local) | Chậm (network I/O) |

```
Narrow Transformation:          Wide Transformation:
┌───┐     ┌───┐                 ┌───┐     ┌───┐
│ P1│ ──→ │P1'│                 │ P1│ ──╲  │P1'│
└───┘     └───┘                 └───┘   ╲─│   │
                                         ╱─│   │
┌───┐     ┌───┐                 ┌───┐ ──╱  └───┘
│ P2│ ──→ │P2'│                 │ P2│ ──╲  ┌───┐
└───┘     └───┘                 └───┘   ╲─│P2'│
                                         ╱─│   │
┌───┐     ┌───┐                 ┌───┐ ──╱  └───┘
│ P3│ ──→ │P3'│                 │ P3│
└───┘     └───┘                 └───┘
1-to-1 dependency               Many-to-many (shuffle)
```

💡 **Mẹo**: `reduceByKey` tuy là wide transformation nhưng **nhanh hơn** `groupByKey` vì nó kết hợp (combine) dữ liệu **trước khi shuffle** (giống Combiner trong MapReduce).

### 3.5. Lazy Evaluation + DAG

**Lazy Evaluation** (Đánh giá lười biếng):
- Transformation KHÔNG thực thi ngay → chỉ ghi nhận vào **DAG** (Directed Acyclic Graph)
- Chỉ khi gặp **Action** → Spark tối ưu hóa DAG → chia thành **stages** → thực thi

```
                 DAG Execution Plan
                 ==================
textFile ─→ flatMap ─→ map ─→ reduceByKey ─→ collect()
  │            │         │         │              │
  └── Stage 1 (Narrow) ──┘         │              │
                                   └── Stage 2 ───┘
                                   (Wide - shuffle)
```

**Lợi ích của Lazy Evaluation**:
1. ✅ **Tối ưu hóa**: Spark có thể gộp/bỏ qua các bước không cần thiết
2. ✅ **Pipeline**: Nhiều transformation narrow gộp thành 1 stage
3. ✅ **Giảm I/O**: Không ghi kết quả trung gian ra disk (khác MapReduce!)

### 3.6. Persistence / Caching

⭐ **Khi RDD được dùng nhiều lần** → nên cache lại để tránh tính lại.

| Method | Mô tả | Mức lưu trữ mặc định |
|--------|--------|-----------------------|
| `cache()` | Lưu vào bộ nhớ | `MEMORY_ONLY` |
| `persist(level)` | Lưu với mức tùy chọn | Tùy chọn (xem bảng dưới) |
| `unpersist()` | Xóa khỏi cache | — |

**Các mức lưu trữ (StorageLevel)**:

| StorageLevel | Memory | Disk | Serialized | Copies |
|-------------|--------|------|------------|--------|
| `MEMORY_ONLY` | ✅ | ❌ | ❌ | 1 |
| `MEMORY_AND_DISK` | ✅ | ✅ (khi tràn) | ❌ | 1 |
| `MEMORY_ONLY_SER` | ✅ | ❌ | ✅ | 1 |
| `MEMORY_AND_DISK_SER` | ✅ | ✅ (khi tràn) | ✅ | 1 |
| `DISK_ONLY` | ❌ | ✅ | ✅ | 1 |
| `MEMORY_ONLY_2` | ✅ | ❌ | ❌ | 2 |

💡 **Khi nào nên cache?**
- RDD được sử dụng **nhiều lần** (trong vòng lặp, hoặc nhiều action)
- RDD tốn **chi phí tính toán cao** (join, groupBy phức tạp)
- Thuật toán **lặp** (PageRank, K-means)

📝 **Ví dụ**:
```python
# Không cache → tính lại 2 lần
rdd = sc.textFile("data.txt").flatMap(lambda x: x.split()).map(lambda x: (x, 1))
print(rdd.count())          # Tính từ đầu
print(rdd.collect())        # Tính lại từ đầu!

# Có cache → tính 1 lần, dùng 2 lần
rdd = sc.textFile("data.txt").flatMap(lambda x: x.split()).map(lambda x: (x, 1))
rdd.cache()                 # Đánh dấu cache (chưa cache thật)
print(rdd.count())          # Tính + cache
print(rdd.collect())        # Lấy từ cache! Nhanh hơn!
```

### 3.7. Shared Variables — Biến chia sẻ

| Loại | Hướng | Mục đích | Ví dụ |
|------|-------|----------|-------|
| **Broadcast Variable** | Driver → Workers (Read-only) | Gửi dữ liệu lớn chung cho tất cả worker | Lookup table, model parameters |
| **Accumulator** | Workers → Driver (Write-only) | Thu thập thông tin từ workers | Đếm lỗi, thống kê debug |

**Broadcast Variable**:

```python
# Không dùng broadcast → gửi lookup_table trong mỗi task (lãng phí!)
lookup_table = {"VN": "Vietnam", "US": "United States", ...}

# Dùng broadcast → gửi 1 lần cho mỗi worker node
broadcast_lookup = sc.broadcast(lookup_table)

rdd.map(lambda x: broadcast_lookup.value[x])
```

⭐ **Tại sao cần Broadcast?**
- Không broadcast: biến gửi **mỗi task** → N tasks = N bản sao
- Có broadcast: biến gửi **mỗi worker node** → W nodes = W bản sao (W << N)

**Accumulator**:

```python
# Đếm số dòng rỗng
empty_lines = sc.accumulator(0)

def count_empty(line):
    if len(line.strip()) == 0:
        empty_lines.add(1)    # Worker ghi vào accumulator
    return line

rdd = sc.textFile("data.txt")
rdd.foreach(count_empty)

print(f"Số dòng rỗng: {empty_lines.value}")  # Chỉ driver đọc được!
```

⚠️ **Chú ý Accumulator**:
- Worker chỉ **ghi** (add), KHÔNG đọc được giá trị
- Chỉ **driver** mới đọc được `.value`
- Trong transformation (lazy) → accumulator có thể bị đếm **nhiều lần** nếu task retry
- Nên dùng trong **action** (`foreach`) để đảm bảo chính xác

### 3.8. Spark Word Count — PySpark Code

⭐ **Code mẫu chuẩn — HỌC THUỘC!**

```python
from pyspark import SparkContext, SparkConf

# Khởi tạo SparkContext
conf = SparkConf().setAppName("WordCount").setMaster("local[*]")
sc = SparkContext(conf=conf)

# Đọc file → RDD[String]
lines = sc.textFile("hdfs:///input/data.txt")

# Tách từ: flatMap vì 1 dòng → nhiều từ
words = lines.flatMap(lambda line: line.split(" "))

# Tạo cặp (word, 1)
pairs = words.map(lambda word: (word, 1))

# Đếm theo key
counts = pairs.reduceByKey(lambda a, b: a + b)

# Sắp xếp theo count giảm dần (tùy chọn)
sorted_counts = counts.sortBy(lambda x: x[1], ascending=False)

# Lưu kết quả
sorted_counts.saveAsTextFile("hdfs:///output/wordcount")

# Hoặc hiển thị
for (word, count) in sorted_counts.take(10):
    print(f"{word}: {count}")

# Dừng SparkContext
sc.stop()
```

**So sánh với MapReduce Word Count**:

| MapReduce (Java) | Spark (PySpark) |
|-------------------|-----------------|
| ~50-70 dòng code | ~10 dòng code |
| Cần định nghĩa Mapper class, Reducer class, Driver class | Chuỗi transformation gọn |
| Ghi kết quả trung gian ra HDFS | Xử lý in-memory |
| Chạy chậm hơn (disk I/O) | Chạy nhanh hơn 10-100× |

---

## 4. So sánh Spark vs MapReduce

### 4.1. Bảng so sánh đầy đủ

⭐⭐ **BẢNG SO SÁNH QUAN TRỌNG — HAY RA TRONG ĐỀ THI!**

| Tiêu chí | MapReduce | Spark |
|-----------|-----------|-------|
| **Mô hình xử lý** | Batch only | Batch + Real-time + Streaming |
| **Tốc độ** | Chậm (disk I/O sau mỗi stage) | Nhanh 10-100× (in-memory) |
| **Lưu trữ trung gian** | Ghi ra **HDFS** (disk) sau mỗi Map-Reduce | Giữ trong **RAM** (memory) |
| **Fault Tolerance** | **Replication** (ghi 3 bản sao HDFS) | **Lineage** (ghi lại cách tính) |
| **Xử lý lặp (Iterative)** | Rất chậm (đọc/ghi HDFS mỗi vòng lặp) | Rất nhanh (cache RDD trong RAM) |
| **API** | Low-level (Java, viết Mapper/Reducer class) | High-level (Scala, Python, Java, R) |
| **Ease of use** | Phức tạp (~50 dòng cho Word Count) | Đơn giản (~10 dòng cho Word Count) |
| **Real-time processing** | ❌ Không hỗ trợ | ✅ Spark Streaming |
| **Machine Learning** | Cần Mahout (chậm) | MLlib (tích hợp, nhanh) |
| **Graph Processing** | Cần Giraph | GraphX (tích hợp) |
| **SQL** | Cần Hive | Spark SQL (tích hợp) |
| **Cost (phần cứng)** | Cần disk lớn | Cần RAM lớn (đắt hơn) |
| **Khi nào dùng** | ETL đơn giản, batch lớn 1 lần | ML, iterative, interactive, streaming |

### 4.2. Tại sao Spark tốt hơn cho thuật toán lặp?

⭐ **Ví dụ: PageRank — thuật toán lặp nhiều vòng**

**MapReduce PageRank**:
```
Vòng 1: Đọc HDFS → Map → Reduce → Ghi HDFS     (2 lần disk I/O)
Vòng 2: Đọc HDFS → Map → Reduce → Ghi HDFS     (2 lần disk I/O)
Vòng 3: Đọc HDFS → Map → Reduce → Ghi HDFS     (2 lần disk I/O)
...
Vòng N: Đọc HDFS → Map → Reduce → Ghi HDFS     (2 lần disk I/O)

Tổng disk I/O: 2N lần → RẤT CHẬM!
```

**Spark PageRank**:
```
Đọc HDFS → Cache RDD                             (1 lần disk I/O)
Vòng 1: Tính từ cache (RAM)                      (0 lần disk I/O)
Vòng 2: Tính từ cache (RAM)                      (0 lần disk I/O)
Vòng 3: Tính từ cache (RAM)                      (0 lần disk I/O)
...
Vòng N: Tính từ cache (RAM)                      (0 lần disk I/O)

Tổng disk I/O: 1 lần → RẤT NHANH!
```

```python
# PageRank trong Spark (đơn giản hóa)
links = sc.textFile("graph.txt").map(parse_links).groupByKey().cache()  # Cache!
ranks = links.mapValues(lambda _: 1.0)  # Khởi tạo rank = 1.0

for i in range(num_iterations):
    contribs = links.join(ranks).flatMap(compute_contribs)
    ranks = contribs.reduceByKey(lambda a, b: a + b).mapValues(lambda v: 0.15 + 0.85 * v)

ranks.saveAsTextFile("output")
```

💡 **Điểm mấu chốt**: `links.cache()` — dữ liệu graph **không đổi** qua các vòng lặp → cache 1 lần, dùng N lần!

---

## 5. Data Abstractions — RDD vs DataFrame vs Dataset

### 5.1. Bảng so sánh ba abstraction

⭐ **Đây là kiến thức thường xuất hiện trong câu hỏi lý thuyết!**

| Tiêu chí | RDD | DataFrame | Dataset |
|-----------|-----|-----------|---------|
| **Giới thiệu** | Spark 1.0 (2014) | Spark 1.3 (2015) | Spark 1.6 (2016) |
| **Cấu trúc** | Unstructured/Semi-structured | Structured (có schema, cột) | Structured (có schema + type-safe) |
| **Schema** | ❌ Không | ✅ Có (tự suy luận hoặc định nghĩa) | ✅ Có |
| **Type Safety** | ✅ Compile-time | ❌ Runtime only | ✅ Compile-time |
| **Tối ưu hóa Catalyst** | ❌ Không | ✅ Có (Catalyst Optimizer) | ✅ Có |
| **Tungsten** | ❌ Không | ✅ Có (binary in-memory) | ✅ Có |
| **API** | Functional (map, filter, reduce) | Declarative (select, where, groupBy) | Cả hai |
| **Ngôn ngữ** | Scala, Java, Python | Scala, Java, Python, R | Scala, Java only |
| **Serialization** | Java Serialization (chậm) | Tungsten (nhanh) | Tungsten (nhanh) |
| **GC Overhead** | Cao (tạo nhiều object) | Thấp (off-heap) | Thấp |
| **Khi nào dùng** | Low-level control, unstructured data | Structured data, SQL-like, ML pipeline | Type-safe + tối ưu (Scala/Java) |

### 5.2. Mối quan hệ

```
            Evolution of Spark Data Abstractions
            =====================================

  RDD (2014)          DataFrame (2015)         Dataset (2016)
  ┌──────────┐        ┌──────────────┐         ┌──────────────┐
  │ Low-level│        │ High-level   │         │ Best of both │
  │ Flexible │  ──→   │ Optimized    │   ──→   │ Type-safe +  │
  │ No schema│        │ Has schema   │         │ Optimized    │
  └──────────┘        └──────────────┘         └──────────────┘
                                               
  Ghi chú: Trong PySpark, DataFrame ≈ Dataset[Row]
           Dataset API chỉ có trong Scala/Java
```

### 5.3. Ví dụ code so sánh

📝 **Cùng bài toán: Tìm nhân viên lương > 50000 và tính tổng theo phòng ban**

**RDD**:
```python
rdd = sc.textFile("employees.csv")
result = rdd.map(lambda line: line.split(",")) \
             .filter(lambda x: int(x[2]) > 50000) \
             .map(lambda x: (x[1], int(x[2]))) \
             .reduceByKey(lambda a, b: a + b) \
             .collect()
```

**DataFrame**:
```python
df = spark.read.csv("employees.csv", header=True, inferSchema=True)
result = df.filter(df["salary"] > 50000) \
           .groupBy("department") \
           .agg({"salary": "sum"}) \
           .collect()
```

**DataFrame (SQL)**:
```python
df.createOrReplaceTempView("employees")
result = spark.sql("""
    SELECT department, SUM(salary) 
    FROM employees 
    WHERE salary > 50000 
    GROUP BY department
""").collect()
```

💡 **Nhận xét**: DataFrame code ngắn hơn, dễ đọc hơn, VÀ chạy nhanh hơn (nhờ Catalyst Optimizer)!

### 5.4. reduceByKey vs groupByKey

⭐ **Câu hỏi hay gặp trong đề thi!**

| Tiêu chí | `reduceByKey` | `groupByKey` |
|-----------|---------------|--------------|
| **Combine trước shuffle?** | ✅ Có (giống Combiner) | ❌ Không |
| **Dữ liệu qua mạng** | Ít (đã reduce cục bộ) | Nhiều (tất cả values) |
| **Performance** | ⚡ Nhanh | 🐌 Chậm |
| **Khi nào dùng** | Khi reduce function là associative + commutative | Khi cần toàn bộ values |

```
reduceByKey:                          groupByKey:
Node 1: (a,1)(a,1)(b,1)              Node 1: (a,1)(a,1)(b,1)
  ↓ local combine                       ↓ NO combine
  (a,2)(b,1)                            (a,1)(a,1)(b,1)
  ↓ shuffle (2 pairs)                   ↓ shuffle (3 pairs) ← Nhiều hơn!
```

⚠️ **Quy tắc**: Luôn ưu tiên `reduceByKey` hoặc `aggregateByKey` thay vì `groupByKey`!

---

## 📋 TỔNG KẾT CHƯƠNG 7

```
╔══════════════════════════════════════════════════════════════════════╗
║                    TÓM TẮT CHƯƠNG 7                                ║
║                   MAPREDUCE & SPARK                                 ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                     ║
║  1. MAPREDUCE MODEL                                                 ║
║     • Map → Shuffle & Sort → Reduce                                ║
║     • Combiner: chỉ dùng khi associative + commutative             ║
║     • Partitioner: hash(key) mod R                                  ║
║     • Communication Cost = r × |I|                                  ║
║                                                                     ║
║  2. MAPREDUCE APPLICATIONS                                          ║
║     • Word Count: emit (word, 1) → sum                             ║
║     • Join: emit (join_key, (tag, data)) → cross product           ║
║     • Matrix Multiply: emit ((i,j), (tag, k, val)) → dot product  ║
║     • DISTINCT & GROUP BY                                           ║
║                                                                     ║
║  3. APACHE SPARK                                                    ║
║     • RDD: Resilient + Distributed + Dataset                       ║
║     • Transformation (lazy) vs Action (trigger)                     ║
║     • Narrow (no shuffle) vs Wide (shuffle)                         ║
║     • cache() / persist() cho RDD dùng nhiều lần                   ║
║     • Broadcast (read-only) vs Accumulator (write-only)            ║
║                                                                     ║
║  4. SPARK vs MAPREDUCE                                              ║
║     • Spark: in-memory, nhanh 10-100×, API cao cấp                 ║
║     • MapReduce: disk I/O, chậm, low-level                         ║
║     • Spark tốt hơn cho iterative algorithms (PageRank)            ║
║                                                                     ║
║  5. DATA ABSTRACTIONS                                               ║
║     • RDD → DataFrame → Dataset (evolution)                        ║
║     • DataFrame: có schema + Catalyst Optimizer → nhanh nhất       ║
║     • reduceByKey >> groupByKey (performance)                       ║
║                                                                     ║
║  ⭐ MẸO THI:                                                       ║
║     • Combiner KHÔNG dùng cho Average → emit (sum, count)          ║
║     • Đếm job = đếm số Action trong code                           ║
║     • Natural Join Reduce = CROSS PRODUCT (không phải cộng)        ║
║     • Luôn ưu tiên reduceByKey thay vì groupByKey                  ║
║     • Lazy Evaluation: Transformation không chạy ngay!              ║
║                                                                     ║
╚══════════════════════════════════════════════════════════════════════╝
```
