# 📋 CHEAT SHEET — TỔNG HỢP CÔNG THỨC & THUẬT TOÁN

> **In ra 2 mặt giấy A4 → Mang đi thi lật nhanh**  
> Sắp xếp theo chương, mỗi chương gói gọn 1 khung

---

## 1️⃣ LSH (Locality Sensitive Hashing)

```
Pipeline: Shingling → MinHash → LSH Banding

Jaccard:  J(A,B) = |A∩B| / |A∪B|

MinHash:  P(h(A)=h(B)) = J(A,B)
          h(x) = (ax + b) mod c

S-curve:  P(candidate) = 1 - (1 - s^r)^b
          n = b × r (tổng hàng signature)

Threshold: t ≈ (1/b)^(1/r)

Cosine LSH: P(h(u)=h(v)) = 1 - θ/π
```

---

## 2️⃣ CLUSTERING

```
K-means: ASSIGN (gần centroid nhất) → UPDATE (mean) → LẶP
  Mặc định: Euclidean distance
  K-means++: chọn centroid theo P ∝ D(x)²

Khoảng cách:
  Euclidean: √(Σ(xᵢ-yᵢ)²)
  Cosine:    1 - (A·B)/(||A||·||B||)
  Jaccard:   1 - |A∩B|/|A∪B|
  Manhattan: Σ|xᵢ-yᵢ|

BFR (Big Data K-means):
  Lưu: (N, SUM, SUMSQ) cho mỗi cluster
  Centroid: μᵢ = SUMᵢ / N
  Variance: σᵢ² = SUMSQᵢ/N - (SUMᵢ/N)²
  Mahalanobis: MD = √(Σ((xᵢ-cᵢ)/σᵢ)²)
  3 sets: DS (gán rồi) | CS (mini-cluster) | RS (outlier)
  Merge: N=N₁+N₂, SUM=SUM₁+SUM₂, SUMSQ=SUMSQ₁+SUMSQ₂

CURE: Nhiều representative points + shrink α về centroid

HAC Linkage: Single(min) | Complete(max) | Average(avg) | Ward
```

---

## 3️⃣ RECOMMENDER SYSTEMS

```
Content-Based:
  User Profile = Σ(ratingᵢ × item_profileᵢ) / Σ(ratingᵢ)
  Cosine Sim = (A·B) / (||A|| × ||B||)

Collaborative Filtering:
  Pearson:  sim(u,v) = Σ(rᵤᵢ-r̄ᵤ)(rᵥᵢ-r̄ᵥ) / √[Σ(rᵤᵢ-r̄ᵤ)² × Σ(rᵥᵢ-r̄ᵥ)²]
  Predict:  r̂(u,i) = r̄ᵤ + Σ[sim(u,v)×(rᵥᵢ-r̄ᵥ)] / Σ|sim(u,v)|

Matrix Factorization: R ≈ P × Q^T
  SGD: eᵤᵢ = Rᵤᵢ - Pᵤ·Qᵢ^T
       Pᵤₖ += γ(eᵤᵢ×Qₖᵢ - λPᵤₖ)
       Qₖᵢ += γ(eᵤᵢ×Pᵤₖ - λQₖᵢ)

Cold Start → Hybrid (Content + CF)
```

---

## 4️⃣ PAGERANK & GRAPH

```
PageRank cơ bản: rⱼ = Σ(i→j) rᵢ/dᵢ

Với damping β (0.8-0.85):
  r' = β × M × r + (1-β)/n × e

Google Matrix: A = β×M + (1-β)×[1/n]

Power Iteration:
  r⁽⁰⁾ = [1/n, ..., 1/n]
  r⁽ᵗ⁺¹⁾ = A × r⁽ᵗ⁾
  Stop khi ||r⁽ᵗ⁺¹⁾ - r⁽ᵗ⁾|| < ε

Dead Ends → teleport (PageRank rò rỉ)
Spider Traps → damping factor β

HITS: a(p) = Σ(q→p) h(q)    (Authority)
      h(p) = Σ(p→q) a(q)    (Hub)
      → Normalize → Lặp
```

---

## 5️⃣ DIMENSIONALITY REDUCTION

```
SVD: A = U × Σ × V^T
  1. Tính A^T×A
  2. Eigenvalues: det(A^TA - λI) = 0
  3. σᵢ = √λᵢ (giảm dần)
  4. Eigenvectors → V
  5. U: uᵢ = (1/σᵢ) × A × vᵢ

Low-rank k: A_k = U_k × Σ_k × V_k^T
Energy: Σ(top k) σᵢ² / Σ(all) σᵢ²

PCA: Center → Covariance (C = X^T×X/(n-1)) → Eigen → Project
  λᵢ(PCA) = σᵢ²/(n-1)

CUR: A ≈ C(columns) × U × R(rows)
  → Giữ sparsity, interpretable hơn SVD
```

---

## 6️⃣ DATA STREAMING

```
Bloom Filter:
  Insert: hash k lần → set bits = 1
  Query: ANY bit = 0 → CHẮC CHẮN KHÔNG. All = 1 → CÓ THỂ CÓ
  False positive: p ≈ (1 - e^(-kn/m))^k
  Optimal k = (m/n) × ln2 ≈ 0.693 × (m/n)
  ⚠️ KHÔNG CÓ false negative

Flajolet-Martin:
  Hash → đếm trailing zeros → R = max
  Distinct ≈ 2^R

DGIM (đếm 1s trong window):
  Bucket: (timestamp, size=2^k)
  1-2 buckets/size, 3 → merge cũ nhất
  Query: tổng + nửa bucket cũ nhất
  Max error: 50%, Memory: O(log²N)

AMS (ước lượng F₂ = Σfᵢ²):
  Chọn vị trí ngẫu nhiên, đếm c (occurrences từ vị trí đó)
  Estimate/biến = n × (2c - 1)
  F₂ ≈ average(all estimates)

Reservoir Sampling (k mẫu từ stream):
  Giữ k đầu. Element thứ i (i>k): thêm P = k/i, thay ngẫu nhiên
```

---

## 7️⃣ MAPREDUCE & SPARK

```
MapReduce: Map(k,v) → list(k',v') → Shuffle → Reduce(k', list(v'))
  Combiner: chỉ khi associative+commutative (sum, max, min)
  ❌ KHÔNG cho: average, median
  Comm Cost = r × |I|

Natural Join R(A,B) ⋈ S(B,C):
  Map: emit ⟨b, (R,a)⟩ và ⟨b, (S,c)⟩
  Reduce: cross product

Spark:
  RDD: Immutable, Distributed, Fault-tolerant (lineage)
  Transformations (LAZY): map, filter, flatMap, reduceByKey
  Actions (TRIGGER): collect, count, save
  Narrow (no shuffle): map, filter
  Wide (shuffle): groupByKey, reduceByKey, join
  cache() → MEMORY_ONLY
  persist() → tùy chọn level

Spark >> MapReduce cho iterative (PageRank): in-memory caching
```

---

## 8️⃣ VISUALIZATION

```
So sánh → Bar | Xu hướng → Line | Quan hệ → Scatter
Mật độ → Heat Map | Kết nối → Network | Đa chiều → Parallel Coord
Phân cấp → Treemap/Sunburst | Địa lý → Choropleth (dùng RATE!)
Text → Word Cloud | Phân phối → Histogram/Box Plot

Lie Factor = visual_change% / data_change% (=1 là trung thực)
```

---

## 🎯 TỰ LUẬN: TEMPLATE 5 PHẦN

```
1. BÀI TOÁN: vấn đề gì?
2. DỮ LIỆU: thu thập từ đâu?
3. KIẾN TRÚC: Sources → Kafka → HDFS → Spark → ML → Dashboard
4. KỸ THUẬT: ít nhất 3-4 kỹ thuật từ MÔN HỌC
5. GIÁ TRỊ: kết quả đem lại

Lĩnh vực → Kỹ thuật chính:
  Nông nghiệp: Streaming + Clustering
  Giao thông: Streaming + PageRank
  Giáo dục: RecSys + Clustering
  Môi trường: Streaming + DGIM
  Khuyến nghị: CF/MF + LSH
```
