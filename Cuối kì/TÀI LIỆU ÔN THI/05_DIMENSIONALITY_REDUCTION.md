# CHƯƠNG 5: DIMENSIONALITY REDUCTION (GIẢM CHIỀU)

> **Môn học:** Big Data (CO5135) — HCMUT  
> **Mục tiêu:** Nắm vững lý thuyết SVD, PCA, CUR và biết áp dụng tính toán trong bài thi  
> **Mức độ quan trọng:** ⭐⭐⭐⭐⭐ — Chương trọng tâm, tần suất ra đề rất cao

---

## 1. TẠI SAO CẦN GIẢM CHIỀU? (Why Dimensionality Reduction?)

### 1.1. Lời nguyền chiều cao (Curse of Dimensionality)

⭐ **Định nghĩa:** Khi số chiều (features) tăng lên, dữ liệu trở nên **thưa thớt** (sparse) trong không gian cao chiều, gây ra nhiều vấn đề nghiêm trọng.

| Vấn đề | Mô tả |
|---------|--------|
| **Dữ liệu thưa** | Khoảng cách giữa các điểm trở nên gần như bằng nhau → các thuật toán dựa trên khoảng cách (k-NN, clustering) mất hiệu quả |
| **Overfitting** | Quá nhiều feature so với số mẫu → mô hình "học thuộc" noise thay vì pattern |
| **Chi phí tính toán** | Thời gian & bộ nhớ tăng theo cấp số nhân với số chiều |
| **Khó trực quan hóa** | Không thể vẽ đồ thị khi d > 3 |

💡 **Quy tắc ngón tay cái:** Cần ít nhất **5–10 mẫu** cho mỗi chiều để tránh curse of dimensionality.

### 1.2. Các lợi ích của giảm chiều

```
┌─────────────────────────────────────────────────────────┐
│                  LỢI ÍCH GIẢM CHIỀU                     │
├──────────────────┬──────────────────┬───────────────────┤
│  🔇 Loại noise   │  📊 Trực quan    │  📦 Nén dữ liệu   │
│  Loại bỏ feature │  Giảm về 2D/3D  │  Giảm dung lượng  │
│  không quan trọng│  để visualize    │  lưu trữ & truyền │
├──────────────────┼──────────────────┼───────────────────┤
│  ⚡ Tăng tốc      │  🎯 Feature      │  🧠 Tránh          │
│  Giảm thời gian  │  extraction      │  overfitting      │
│  huấn luyện      │  Tạo feature mới │  Mô hình tổng quát│
│  & dự đoán       │  có ý nghĩa hơn  │  hóa tốt hơn     │
└──────────────────┴──────────────────┴───────────────────┘
```

### 1.3. Hai hướng tiếp cận chính

| Hướng tiếp cận | Mô tả | Ví dụ |
|-----------------|--------|-------|
| **Feature Selection** | Chọn một tập con các feature gốc | Filter, Wrapper, Embedded methods |
| **Feature Extraction** | Tạo ra các feature MỚI từ tổ hợp tuyến tính các feature gốc | **SVD, PCA**, CUR, t-SNE |

⚠️ **Lưu ý thi:** Chương này tập trung vào **Feature Extraction**, đặc biệt là SVD và PCA.

---

## 2. SVD — SINGULAR VALUE DECOMPOSITION (Phân rã giá trị suy biến)

### 2.1. Công thức chính

⭐⭐⭐ **Công thức SVD — BẮT BUỘC NHỚ:**

$$\boxed{A = U \times \Sigma \times V^T}$$

Trong đó ma trận **A** có kích thước **m × n**:

| Thành phần | Kích thước | Ý nghĩa | Tính chất |
|------------|-----------|----------|-----------|
| **U** | m × m | Ma trận **left singular vectors** (vector suy biến trái) | Trực giao: U^T U = I. Các cột là **eigenvector của AA^T** |
| **Σ** (Sigma) | m × n | Ma trận đường chéo chứa **singular values** σ₁ ≥ σ₂ ≥ ... ≥ 0 | Giá trị giảm dần trên đường chéo, σᵢ = √λᵢ |
| **V^T** | n × n | Ma trận **right singular vectors** (vector suy biến phải) | Trực giao: V^T V = I. Các cột của V là **eigenvector của A^TA** |

💡 **Cách nhớ thứ tự:** **"U Σ V^T"** → "**U**ốn **S**inh **V**iên **T**hi" (Uốn Sinh Viên Thi)

### 2.2. Tính chất quan trọng

⭐ **Các tính chất cần nhớ:**

1. **AA^T** = U Σ Σ^T U^T → eigenvector của AA^T là các cột của **U**
2. **A^TA** = V Σ^T Σ V^T → eigenvector của A^TA là các cột của **V**
3. **Singular values** σᵢ = √λᵢ (λᵢ là eigenvalue của A^TA hoặc AA^T)
4. **Rank(A)** = số singular values khác 0
5. U và V đều là ma trận **trực giao** (orthogonal): U^T = U⁻¹, V^T = V⁻¹

### 2.3. ⭐ Quy trình tính SVD từng bước (TRỌNG TÂM THI)

📝 **Ví dụ mẫu:** Tính SVD của ma trận:

$$A = \begin{pmatrix} 1 & 1 \\ 1 & 0 \\ 0 & 1 \end{pmatrix}_{3 \times 2}$$

---

#### **Bước 1: Tính A^T A**

$$A^T A = \begin{pmatrix} 1 & 1 & 0 \\ 1 & 0 & 1 \end{pmatrix} \times \begin{pmatrix} 1 & 1 \\ 1 & 0 \\ 0 & 1 \end{pmatrix} = \begin{pmatrix} 2 & 1 \\ 1 & 2 \end{pmatrix}_{2 \times 2}$$

💡 **Mẹo:** A^TA luôn là ma trận **vuông** kích thước n × n, **đối xứng**, **nửa xác định dương** (eigenvalue ≥ 0)

---

#### **Bước 2: Tìm eigenvalue — giải det(A^TA − λI) = 0**

$$\det\begin{pmatrix} 2-\lambda & 1 \\ 1 & 2-\lambda \end{pmatrix} = 0$$

$$(2-\lambda)^2 - 1 = 0$$

$$4 - 4\lambda + \lambda^2 - 1 = 0$$

$$\lambda^2 - 4\lambda + 3 = 0$$

$$(\lambda - 3)(\lambda - 1) = 0$$

$$\boxed{\lambda_1 = 3, \quad \lambda_2 = 1}$$

---

#### **Bước 3: Tính singular values**

$$\sigma_i = \sqrt{\lambda_i}$$

$$\boxed{\sigma_1 = \sqrt{3}, \quad \sigma_2 = \sqrt{1} = 1}$$

Ma trận Σ (3 × 2):

$$\Sigma = \begin{pmatrix} \sqrt{3} & 0 \\ 0 & 1 \\ 0 & 0 \end{pmatrix}$$

⚠️ **Chú ý:** Σ có cùng kích thước với A (m × n). Phần dư (nếu m > n) được lấp đầy bằng 0.

---

#### **Bước 4: Tìm eigenvector → Ma trận V**

**Với λ₁ = 3:**

$$(A^TA - 3I)\mathbf{v} = 0 \Rightarrow \begin{pmatrix} -1 & 1 \\ 1 & -1 \end{pmatrix}\mathbf{v} = 0$$

$$-v_1 + v_2 = 0 \Rightarrow v_1 = v_2$$

Chuẩn hóa: $\mathbf{v_1} = \frac{1}{\sqrt{2}}\begin{pmatrix} 1 \\ 1 \end{pmatrix}$

**Với λ₂ = 1:**

$$(A^TA - 1 \cdot I)\mathbf{v} = 0 \Rightarrow \begin{pmatrix} 1 & 1 \\ 1 & 1 \end{pmatrix}\mathbf{v} = 0$$

$$v_1 + v_2 = 0 \Rightarrow v_2 = -v_1$$

Chuẩn hóa: $\mathbf{v_2} = \frac{1}{\sqrt{2}}\begin{pmatrix} 1 \\ -1 \end{pmatrix}$

$$\boxed{V = \begin{pmatrix} \frac{1}{\sqrt{2}} & \frac{1}{\sqrt{2}} \\ \frac{1}{\sqrt{2}} & -\frac{1}{\sqrt{2}} \end{pmatrix}}$$

💡 **Mẹo kiểm tra:** Các cột của V phải **trực giao** với nhau: v₁ · v₂ = 0 ✓

---

#### **Bước 5: Tính U từ công thức u_i = (1/σ_i) × A × v_i**

⭐ **Công thức quan trọng:**

$$\mathbf{u_i} = \frac{1}{\sigma_i} A \mathbf{v_i}$$

**Tính u₁:**

$$\mathbf{u_1} = \frac{1}{\sqrt{3}} \begin{pmatrix} 1 & 1 \\ 1 & 0 \\ 0 & 1 \end{pmatrix} \begin{pmatrix} \frac{1}{\sqrt{2}} \\ \frac{1}{\sqrt{2}} \end{pmatrix} = \frac{1}{\sqrt{3}} \begin{pmatrix} \frac{2}{\sqrt{2}} \\ \frac{1}{\sqrt{2}} \\ \frac{1}{\sqrt{2}} \end{pmatrix} = \begin{pmatrix} \frac{2}{\sqrt{6}} \\ \frac{1}{\sqrt{6}} \\ \frac{1}{\sqrt{6}} \end{pmatrix}$$

**Tính u₂:**

$$\mathbf{u_2} = \frac{1}{1} \begin{pmatrix} 1 & 1 \\ 1 & 0 \\ 0 & 1 \end{pmatrix} \begin{pmatrix} \frac{1}{\sqrt{2}} \\ -\frac{1}{\sqrt{2}} \end{pmatrix} = \begin{pmatrix} 0 \\ \frac{1}{\sqrt{2}} \\ -\frac{1}{\sqrt{2}} \end{pmatrix}$$

**Tính u₃:** (cần thêm vì U phải là 3×3)

u₃ được tìm bằng cách lấy vector trực giao với cả u₁ và u₂ (tích có hướng — cross product):

$$\mathbf{u_3} = \mathbf{u_1} \times \mathbf{u_2} = \begin{pmatrix} \frac{1}{\sqrt{3}} \\ -\frac{1}{\sqrt{3}} \\ \frac{1}{\sqrt{3}} \end{pmatrix}$$

$$\boxed{U = \begin{pmatrix} \frac{2}{\sqrt{6}} & 0 & \frac{1}{\sqrt{3}} \\ \frac{1}{\sqrt{6}} & \frac{1}{\sqrt{2}} & -\frac{1}{\sqrt{3}} \\ \frac{1}{\sqrt{6}} & -\frac{1}{\sqrt{2}} & \frac{1}{\sqrt{3}} \end{pmatrix}}$$

---

#### **Bước 6: Kết quả — Kiểm tra A = UΣV^T**

$$A = \begin{pmatrix} \frac{2}{\sqrt{6}} & 0 & \frac{1}{\sqrt{3}} \\ \frac{1}{\sqrt{6}} & \frac{1}{\sqrt{2}} & -\frac{1}{\sqrt{3}} \\ \frac{1}{\sqrt{6}} & -\frac{1}{\sqrt{2}} & \frac{1}{\sqrt{3}} \end{pmatrix} \begin{pmatrix} \sqrt{3} & 0 \\ 0 & 1 \\ 0 & 0 \end{pmatrix} \begin{pmatrix} \frac{1}{\sqrt{2}} & \frac{1}{\sqrt{2}} \\ \frac{1}{\sqrt{2}} & -\frac{1}{\sqrt{2}} \end{pmatrix}$$

💡 **Kiểm tra nhanh:** Nhân ngược lại UΣV^T phải ra đúng A ban đầu.

---

### 2.4. Xấp xỉ hạng thấp (Low-Rank Approximation)

⭐⭐ **Ý tưởng cốt lõi:** Giữ lại **k** singular values lớn nhất, bỏ phần còn lại → xấp xỉ A bằng ma trận hạng k.

$$\boxed{A_k = U_k \times \Sigma_k \times V_k^T}$$

Trong đó:
- **U_k**: m × k (k cột đầu tiên của U)
- **Σ_k**: k × k (k singular values lớn nhất)
- **V_k^T**: k × n (k hàng đầu tiên của V^T)

```
Ví dụ: A (1000×500) với rank = 500

SVD đầy đủ:     U(1000×1000) × Σ(1000×500) × V^T(500×500)
                 = lưu trữ 1,000,000 + 500,000 + 250,000 = 1,750,000 phần tử

Xấp xỉ k=10:    U_k(1000×10) × Σ_k(10×10) × V_k^T(10×500)
                 = lưu trữ 10,000 + 100 + 5,000 = 15,100 phần tử
                 → Tiết kiệm ~99% bộ nhớ!
```

### 2.5. ⭐ Năng lượng giữ lại (Energy Retained)

Công thức đánh giá chất lượng xấp xỉ:

$$\boxed{\text{Energy Retained} = \frac{\sum_{i=1}^{k} \sigma_i^2}{\sum_{j=1}^{r} \sigma_j^2} \times 100\%}$$

Trong đó:
- k = số singular values giữ lại
- r = rank(A) = tổng số singular values khác 0

📝 **Ví dụ tính năng lượng:**

Cho singular values: σ₁ = 5, σ₂ = 3, σ₃ = 1, σ₄ = 0.5

| Giữ k | Tính toán | Energy |
|-------|-----------|--------|
| k = 1 | 25 / 35.25 | **70.9%** |
| k = 2 | (25 + 9) / 35.25 | **96.5%** |
| k = 3 | (25 + 9 + 1) / 35.25 | **99.3%** |
| k = 4 | (25 + 9 + 1 + 0.25) / 35.25 | **100%** |

Tổng: 5² + 3² + 1² + 0.5² = 25 + 9 + 1 + 0.25 = **35.25**

💡 **Thường chọn k sao cho energy ≥ 90%** (trong ví dụ trên: k = 2 đã đủ 96.5%)

### 2.6. Sai số xấp xỉ (Frobenius Norm Error)

$$\|A - A_k\|_F^2 = \sum_{i=k+1}^{r} \sigma_i^2$$

⭐ **Ý nghĩa:** Sai số bằng tổng bình phương các singular values bị bỏ đi.

📝 **Ví dụ:** Với σ₁ = 5, σ₂ = 3, σ₃ = 1, σ₄ = 0.5 và k = 2:

$$\|A - A_2\|_F^2 = \sigma_3^2 + \sigma_4^2 = 1 + 0.25 = 1.25$$

### 2.7. 📝 Ví dụ tính toán hoàn chỉnh: Ma trận 2×2

**Đề bài:** Tính SVD của $A = \begin{pmatrix} 3 & 0 \\ 4 & 5 \end{pmatrix}$

**Bước 1:** $A^TA = \begin{pmatrix} 3 & 4 \\ 0 & 5 \end{pmatrix}\begin{pmatrix} 3 & 0 \\ 4 & 5 \end{pmatrix} = \begin{pmatrix} 25 & 20 \\ 20 & 25 \end{pmatrix}$

**Bước 2:** det(A^TA - λI) = (25-λ)² - 400 = λ² - 50λ + 225 = 0

$$\lambda = \frac{50 \pm \sqrt{2500 - 900}}{2} = \frac{50 \pm 40}{2}$$

$$\lambda_1 = 45, \quad \lambda_2 = 5$$

**Bước 3:** $\sigma_1 = \sqrt{45} = 3\sqrt{5}, \quad \sigma_2 = \sqrt{5}$

$$\Sigma = \begin{pmatrix} 3\sqrt{5} & 0 \\ 0 & \sqrt{5} \end{pmatrix}$$

**Bước 4:** Eigenvectors của A^TA:

Với λ₁ = 45: $(A^TA - 45I)\mathbf{v} = 0$

$$\begin{pmatrix} -20 & 20 \\ 20 & -20 \end{pmatrix}\mathbf{v} = 0 \Rightarrow v_1 = v_2 \Rightarrow \mathbf{v_1} = \frac{1}{\sqrt{2}}\begin{pmatrix} 1 \\ 1 \end{pmatrix}$$

Với λ₂ = 5: $(A^TA - 5I)\mathbf{v} = 0$

$$\begin{pmatrix} 20 & 20 \\ 20 & 20 \end{pmatrix}\mathbf{v} = 0 \Rightarrow v_1 = -v_2 \Rightarrow \mathbf{v_2} = \frac{1}{\sqrt{2}}\begin{pmatrix} 1 \\ -1 \end{pmatrix}$$

**Bước 5:** Tính U:

$$\mathbf{u_1} = \frac{1}{3\sqrt{5}} \begin{pmatrix} 3 & 0 \\ 4 & 5 \end{pmatrix}\begin{pmatrix} \frac{1}{\sqrt{2}} \\ \frac{1}{\sqrt{2}} \end{pmatrix} = \frac{1}{3\sqrt{5}} \begin{pmatrix} \frac{3}{\sqrt{2}} \\ \frac{9}{\sqrt{2}} \end{pmatrix} = \begin{pmatrix} \frac{1}{\sqrt{10}} \\ \frac{3}{\sqrt{10}} \end{pmatrix}$$

$$\mathbf{u_2} = \frac{1}{\sqrt{5}} \begin{pmatrix} 3 & 0 \\ 4 & 5 \end{pmatrix}\begin{pmatrix} \frac{1}{\sqrt{2}} \\ -\frac{1}{\sqrt{2}} \end{pmatrix} = \frac{1}{\sqrt{5}} \begin{pmatrix} \frac{3}{\sqrt{2}} \\ -\frac{1}{\sqrt{2}} \end{pmatrix} = \begin{pmatrix} \frac{3}{\sqrt{10}} \\ -\frac{1}{\sqrt{10}} \end{pmatrix}$$

**Kết quả:**

$$A = \begin{pmatrix} \frac{1}{\sqrt{10}} & \frac{3}{\sqrt{10}} \\ \frac{3}{\sqrt{10}} & -\frac{1}{\sqrt{10}} \end{pmatrix} \begin{pmatrix} 3\sqrt{5} & 0 \\ 0 & \sqrt{5} \end{pmatrix} \begin{pmatrix} \frac{1}{\sqrt{2}} & \frac{1}{\sqrt{2}} \\ \frac{1}{\sqrt{2}} & -\frac{1}{\sqrt{2}} \end{pmatrix}$$

---

## 3. PCA — PRINCIPAL COMPONENT ANALYSIS (Phân tích thành phần chính)

### 3.1. Ý tưởng cốt lõi

⭐ **PCA tìm các hướng (principal components) mà dữ liệu có phương sai lớn nhất**, sau đó chiếu dữ liệu lên các hướng đó.

```
        ↑ PC2 (ít phương sai)
        |    ·  ·
        |  · · ·· ·
  ------·--··--··--··---→ PC1 (nhiều phương sai nhất)
        | · · ·· ·
        |   ·  ·
        ↓

→ Giữ PC1, bỏ PC2 → giảm từ 2D xuống 1D
```

### 3.2. ⭐ Quy trình PCA từng bước (Step-by-step)

📝 **Ví dụ mẫu:** Cho 4 điểm dữ liệu 2D:

| Điểm | x₁ | x₂ |
|------|-----|-----|
| A | 1 | 2 |
| B | 3 | 4 |
| C | 5 | 6 |
| D | 7 | 8 |

---

#### **Bước 1: Tính trung bình (Mean) và Chuẩn hóa (Center)**

$$\bar{x_1} = \frac{1+3+5+7}{4} = 4, \quad \bar{x_2} = \frac{2+4+6+8}{4} = 5$$

Trừ trung bình để tâm hóa dữ liệu:

| Điểm | x₁ - x̄₁ | x₂ - x̄₂ |
|------|-----------|-----------|
| A | -3 | -3 |
| B | -1 | -1 |
| C | 1 | 1 |
| D | 3 | 3 |

⚠️ **QUAN TRỌNG:** Bước tâm hóa (centering) là **BẮT BUỘC** trong PCA. Không center → kết quả SAI!

---

#### **Bước 2: Tính ma trận hiệp phương sai (Covariance Matrix)**

$$\boxed{C = \frac{1}{n-1} X^T X}$$

Trong đó X là ma trận dữ liệu đã tâm hóa (mỗi hàng = 1 mẫu).

$$X = \begin{pmatrix} -3 & -3 \\ -1 & -1 \\ 1 & 1 \\ 3 & 3 \end{pmatrix}$$

$$X^TX = \begin{pmatrix} 20 & 20 \\ 20 & 20 \end{pmatrix}$$

$$C = \frac{1}{3}\begin{pmatrix} 20 & 20 \\ 20 & 20 \end{pmatrix} = \begin{pmatrix} \frac{20}{3} & \frac{20}{3} \\ \frac{20}{3} & \frac{20}{3} \end{pmatrix}$$

💡 **Ý nghĩa ma trận hiệp phương sai:**
- **Phần tử đường chéo** C(i,i) = phương sai (variance) của feature i
- **Phần tử ngoài đường chéo** C(i,j) = hiệp phương sai (covariance) giữa feature i và j

---

#### **Bước 3: Phân rã trị riêng (Eigendecomposition)**

Giải det(C - λI) = 0:

$$\det\begin{pmatrix} \frac{20}{3}-\lambda & \frac{20}{3} \\ \frac{20}{3} & \frac{20}{3}-\lambda \end{pmatrix} = 0$$

$$\left(\frac{20}{3}-\lambda\right)^2 - \left(\frac{20}{3}\right)^2 = 0$$

$$\left(\frac{20}{3}-\lambda\right)^2 = \left(\frac{20}{3}\right)^2$$

$$\frac{20}{3}-\lambda = \pm\frac{20}{3}$$

$$\boxed{\lambda_1 = \frac{40}{3} \approx 13.33, \quad \lambda_2 = 0}$$

Eigenvectors:

- Với λ₁ = 40/3: $\mathbf{e_1} = \frac{1}{\sqrt{2}}\begin{pmatrix} 1 \\ 1 \end{pmatrix}$ → **PC1** (thành phần chính thứ nhất)
- Với λ₂ = 0: $\mathbf{e_2} = \frac{1}{\sqrt{2}}\begin{pmatrix} 1 \\ -1 \end{pmatrix}$ → **PC2**

💡 **Nhận xét:** λ₂ = 0 nghĩa là dữ liệu **hoàn toàn nằm trên 1 đường thẳng** → chỉ cần 1 PC là đủ!

---

#### **Bước 4: Chọn k thành phần & Chiếu dữ liệu**

**Tỷ lệ phương sai giải thích (Variance Explained Ratio):**

$$\text{Ratio}_i = \frac{\lambda_i}{\sum_{j=1}^{d} \lambda_j}$$

| PC | Eigenvalue | Tỷ lệ | Tỷ lệ tích lũy |
|----|-----------|--------|-----------------|
| PC1 | 40/3 | **100%** | 100% |
| PC2 | 0 | 0% | 100% |

→ Chọn **k = 1** (PC1 đã giải thích 100% phương sai)

**Chiếu dữ liệu:**

$$Y = X \times W_k$$

Với W_k = [e₁] (ma trận chứa k eigenvectors đầu tiên):

$$Y = \begin{pmatrix} -3 & -3 \\ -1 & -1 \\ 1 & 1 \\ 3 & 3 \end{pmatrix} \times \begin{pmatrix} \frac{1}{\sqrt{2}} \\ \frac{1}{\sqrt{2}} \end{pmatrix} = \begin{pmatrix} -3\sqrt{2} \\ -\sqrt{2} \\ \sqrt{2} \\ 3\sqrt{2} \end{pmatrix}$$

→ Dữ liệu 2D đã được giảm xuống **1D**!

### 3.3. ⭐ Mối quan hệ PCA và SVD

⭐⭐ **Đây là kiến thức thường gặp trong bài thi:**

| PCA | SVD | Mối liên hệ |
|-----|-----|-------------|
| Ma trận hiệp phương sai C | A^TA / (n-1) | C = A^TA / (n-1) khi A đã center |
| Eigenvalue λᵢ của C | Singular value σᵢ | **λᵢ = σᵢ² / (n-1)** |
| Eigenvector của C | Cột của V (right singular vectors) | **Giống nhau!** |
| Principal components | U_k × Σ_k | PC = X × V_k = U_k × Σ_k |

⭐ **Công thức cầu nối:**

$$\boxed{\lambda_i^{PCA} = \frac{\sigma_i^2}{n - 1}}$$

💡 **Ý nghĩa thực tiễn:** Thay vì tính PCA trực tiếp (cần eigendecomposition của C), ta có thể dùng **SVD trên X** (ma trận dữ liệu đã center) rồi suy ra PCA!

### 3.4. Cách chọn số thành phần k

| Phương pháp | Tiêu chí | Ngưỡng thường dùng |
|-------------|----------|---------------------|
| **Tỷ lệ phương sai tích lũy** | Giữ k sao cho tổng phương sai ≥ threshold | **≥ 85%** hoặc **≥ 90%** |
| **Elbow method** | Đồ thị eigenvalue → tìm "khuỷu tay" (nơi eigenvalue giảm đột ngột) | Chọn k tại điểm bẻ |
| **Kaiser criterion** | Giữ các PC có eigenvalue > 1 (trên dữ liệu chuẩn hóa) | λ > 1 |

📝 **Ví dụ Elbow Method:**

```
λ
10 │ ●
 8 │    ●
 6 │
 4 │       ●
 2 │          ● ← Elbow ở đây (k=3)
 1 │             ●  ●  ●  ●
   └─────────────────────────→ k
     1   2   3   4  5  6  7  8
```

### 3.5. Reconstruction từ PCA

Sau khi giảm chiều, có thể **tái tạo** (xấp xỉ) dữ liệu gốc:

$$\hat{X} = Y \times W_k^T + \bar{X}$$

Trong đó:
- Y: dữ liệu đã chiếu (n × k)
- W_k^T: ma trận eigenvector (k × d)
- X̄: trung bình gốc (cộng lại vì đã trừ ở bước center)

⚠️ **Lưu ý:** Nếu k < d thì tái tạo chỉ là **xấp xỉ**, mất thông tin trên các PC bị bỏ.

---

## 4. CUR DECOMPOSITION (Phân rã CUR)

### 4.1. Ý tưởng

⭐ **CUR là phương pháp thay thế SVD, giữ nguyên các cột và hàng gốc** thay vì tạo ra các vector trừu tượng.

$$\boxed{A \approx C \times U \times R}$$

| Thành phần | Ý nghĩa | Kích thước |
|------------|----------|-----------|
| **C** | Tập con các **cột** (columns) được chọn từ A | m × c |
| **U** | Ma trận kết nối (connecting matrix) | c × r |
| **R** | Tập con các **hàng** (rows) được chọn từ A | r × n |

### 4.2. Cách chọn cột và hàng

⭐ **Leverage Scores (Điểm đòn bẩy):**

Xác suất chọn cột j:

$$\boxed{p_j = \frac{1}{k} \sum_{i=1}^{k} v_{ji}^2}$$

Trong đó:
- v_ji = phần tử (j, i) của ma trận V (right singular vectors)
- k = số singular values giữ lại

💡 **Giải thích:** Cột nào có "đóng góp" nhiều nhất vào các top-k right singular vectors → có xác suất được chọn cao nhất.

Tương tự cho hàng: dùng ma trận U (left singular vectors).

### 4.3. Tính ma trận U trong CUR

Sau khi chọn C (c cột) và R (r hàng):

1. Tạo **W** = giao điểm (intersection) của các cột và hàng đã chọn (kích thước r × c)
2. Tính **SVD** của W: W = X_W × Σ_W × Y_W^T
3. Tính **pseudo-inverse** (giả nghịch đảo): W⁺ = Y_W × Σ_W⁺ × X_W^T
4. **U = W⁺** (pseudo-inverse của W)

Trong đó Σ_W⁺ = đảo nghịch các phần tử khác 0 trên đường chéo:

$$\Sigma_W^+ = \text{diag}\left(\frac{1}{\sigma_1}, \frac{1}{\sigma_2}, \ldots\right)$$

### 4.4. 📝 Ví dụ CUR đơn giản

Cho ma trận:

$$A = \begin{pmatrix} 1 & 1 & 1 \\ 0 & 2 & 1 \\ 2 & 1 & 0 \end{pmatrix}$$

Giả sử chọn:
- C = cột 1, 3 → $C = \begin{pmatrix} 1 & 1 \\ 0 & 1 \\ 2 & 0 \end{pmatrix}$
- R = hàng 1, 3 → $R = \begin{pmatrix} 1 & 1 & 1 \\ 2 & 1 & 0 \end{pmatrix}$

**Bước 1:** Xác định W (giao của cột 1,3 và hàng 1,3):

$$W = \begin{pmatrix} A_{1,1} & A_{1,3} \\ A_{3,1} & A_{3,3} \end{pmatrix} = \begin{pmatrix} 1 & 1 \\ 2 & 0 \end{pmatrix}$$

**Bước 2:** Tính W⁺ (pseudo-inverse):

$$W^{-1} = \frac{1}{(1)(0)-(1)(2)}\begin{pmatrix} 0 & -1 \\ -2 & 1 \end{pmatrix} = \frac{1}{-2}\begin{pmatrix} 0 & -1 \\ -2 & 1 \end{pmatrix} = \begin{pmatrix} 0 & \frac{1}{2} \\ 1 & -\frac{1}{2} \end{pmatrix}$$

(Vì W là vuông và khả nghịch, W⁺ = W⁻¹)

**Bước 3:** U = W⁺:

$$U = \begin{pmatrix} 0 & \frac{1}{2} \\ 1 & -\frac{1}{2} \end{pmatrix}$$

**Bước 4:** Kiểm tra A ≈ CUR:

$$CUR = \begin{pmatrix} 1 & 1 \\ 0 & 1 \\ 2 & 0 \end{pmatrix} \begin{pmatrix} 0 & \frac{1}{2} \\ 1 & -\frac{1}{2} \end{pmatrix} \begin{pmatrix} 1 & 1 & 1 \\ 2 & 1 & 0 \end{pmatrix}$$

$$= \begin{pmatrix} 1 & 0 \\ 1 & -\frac{1}{2} \\ 0 & 1 \end{pmatrix} \begin{pmatrix} 1 & 1 & 1 \\ 2 & 1 & 0 \end{pmatrix} = \begin{pmatrix} 1 & 1 & 1 \\ 0 & \frac{1}{2} & 1 \\ 2 & 1 & 0 \end{pmatrix}$$

⚠️ **Kết quả xấp xỉ** (phần tử A₂₂ = 2 nhưng CUR cho 0.5). Chọn nhiều cột/hàng hơn sẽ chính xác hơn.

### 4.5. ⭐⭐ So sánh SVD vs CUR (HAY RA THI)

| Tiêu chí | SVD | CUR |
|----------|-----|-----|
| **Thành phần** | U, Σ, V^T (các vector trừu tượng) | C, U, R (cột & hàng gốc) |
| **Tính thưa (Sparsity)** | ❌ U, V thường dense (dày đặc) | ✅ C, R giữ nguyên sparsity của A |
| **Khả năng diễn giải** | ❌ Khó giải thích ý nghĩa | ✅ Dễ hiểu (là cột/hàng thực) |
| **Chính xác** | ✅ Tối ưu (best rank-k approx.) | ⚠️ Gần tối ưu (near-optimal) |
| **Chi phí tính toán** | ❌ O(mn · min(m,n)) — đắt | ✅ Nhanh hơn, đặc biệt cho ma trận thưa |
| **Cập nhật** | ❌ Phải tính lại toàn bộ | ✅ Chỉ cần cập nhật C hoặc R |
| **Lưu trữ** | Cần lưu toàn bộ U, Σ, V | Chỉ cần lưu c cột + r hàng + U nhỏ |
| **Ứng dụng phù hợp** | Dữ liệu dense, cần chính xác | Dữ liệu thưa lớn (recommendation, NLP) |

💡 **Khi nào dùng cái nào?**
- **SVD:** Khi cần xấp xỉ **chính xác nhất** có thể, dữ liệu nhỏ-trung bình
- **CUR:** Khi dữ liệu **lớn, thưa**, cần **diễn giải được**, hoặc cần cập nhật thường xuyên

### 4.6. Đảm bảo chất lượng CUR

⭐ Theo **Drineas et al. (2006)**:

$$\|A - CUR\|_F \leq (1 + \epsilon) \cdot \|A - A_k\|_F$$

Nghĩa là: Sai số CUR chỉ lớn hơn sai số tối ưu (SVD) **một lượng nhỏ tỷ lệ ε**, với điều kiện chọn đủ nhiều cột/hàng.

---

## 5. CÁC DẠNG BÀI THI THƯỜNG GẶP

### Dạng 1: Tính SVD cho ma trận nhỏ

💡 **Chiến lược:**
1. Tính A^TA (luôn lấy cái nhỏ hơn: nếu m < n thì tính AA^T trước)
2. Giải eigenvalue → singular values
3. Tìm eigenvectors → V (hoặc U)
4. Dùng u_i = (1/σ_i)Av_i để tìm nốt

### Dạng 2: Xấp xỉ hạng thấp & tính energy

💡 **Chiến lược:**
1. Tính SVD (hoặc đề cho sẵn singular values)
2. Chọn k theo yêu cầu
3. Áp dụng công thức energy retained
4. Tính A_k = U_k Σ_k V_k^T nếu cần

### Dạng 3: Thực hiện PCA

💡 **Chiến lược:**
1. **LUÔN center** dữ liệu trước (trừ trung bình)
2. Tính covariance matrix
3. Eigendecomposition
4. Chọn k theo variance explained ≥ 90%
5. Chiếu dữ liệu

### Dạng 4: So sánh SVD vs CUR (lý thuyết)

💡 **Chiến lược:** Học bảng so sánh ở mục 4.5, tập trung vào:
- Sparsity preservation
- Interpretability
- Optimality of approximation

---

## 6. BẢNG CÔNG THỨC TỔNG HỢP NHANH

| Công thức | Ý nghĩa |
|-----------|----------|
| A = UΣV^T | Phân rã SVD |
| σᵢ = √λᵢ | Singular value = căn eigenvalue |
| uᵢ = (1/σᵢ)Avᵢ | Tính left singular vector từ right |
| A_k = U_kΣ_kV_k^T | Xấp xỉ hạng k |
| Energy = Σᵢ₌₁ᵏ σᵢ² / Σⱼ₌₁ʳ σⱼ² | Năng lượng giữ lại |
| ‖A - A_k‖²_F = Σᵢ₌ₖ₊₁ʳ σᵢ² | Sai số Frobenius |
| C = X^TX/(n-1) | Ma trận hiệp phương sai (PCA) |
| λᵢ^PCA = σᵢ²/(n-1) | Liên hệ PCA-SVD |
| pⱼ = (1/k)Σᵢ₌₁ᵏ vⱼᵢ² | Leverage score (CUR) |

---

## 7. MẸO LÀM BÀI THI

⚠️ **Những lỗi thường gặp:**

1. ❌ **Quên center dữ liệu** khi làm PCA → kết quả sai hoàn toàn
2. ❌ **Nhầm thứ tự eigenvalue:** phải sắp **giảm dần** (σ₁ ≥ σ₂ ≥ ...)
3. ❌ **Quên chuẩn hóa eigenvector:** eigenvector phải có **độ dài = 1**
4. ❌ **Nhầm kích thước Σ:** Σ có cùng kích thước với A (m × n), không phải vuông
5. ❌ **Nhầm A^TA và AA^T:** 
   - A^TA → eigenvector cho **V** (kích thước n × n)
   - AA^T → eigenvector cho **U** (kích thước m × m)

💡 **Mẹo tiết kiệm thời gian:**

1. **Tính A^TA hay AA^T trước?** → Chọn cái có kích thước **nhỏ hơn**
   - A (m × n): nếu m < n → tính AA^T (m × m) trước
   - Nếu n < m → tính A^TA (n × n) trước
2. **Kiểm tra nhanh:** Tổng eigenvalues = trace(A^TA) = Σ aᵢⱼ²
3. **Eigenvectors trực giao:** Nếu tìm được v₁, v₂ phải vuông góc với v₁

---

> ## 📋 TÓM TẮT CHƯƠNG 5 — DIMENSIONALITY REDUCTION
> 
> | Chủ đề | Điểm chính |
> |--------|-----------|
> | **Curse of Dimensionality** | Dữ liệu thưa thớt trong không gian cao chiều → giảm hiệu quả thuật toán |
> | **SVD** | A = UΣV^T. Tính qua A^TA → eigenvalues → singular values → V → U |
> | **Low-rank Approximation** | A_k = U_kΣ_kV_k^T. Energy = Σσᵢ²(top k) / Σσⱼ²(all) |
> | **PCA** | Center → Covariance → Eigendecomposition → Chiếu. Liên hệ: λ = σ²/(n-1) |
> | **CUR** | A ≈ CUR. Giữ sparsity, dễ giải thích, nhưng kém chính xác hơn SVD |
> | **SVD vs CUR** | SVD: chính xác, dense. CUR: nhanh, sparse, interpretable |
> 
> **⭐ Top 3 công thức PHẢI NHỚ:**
> 1. A = UΣV^T (SVD)
> 2. uᵢ = (1/σᵢ)Avᵢ (tính U từ V)
> 3. Energy Retained = Σσᵢ²(k) / Σσⱼ²(all) (chất lượng xấp xỉ)
> 
> **⭐ Top 3 điều KHÔNG ĐƯỢC QUÊN:**
> 1. PCA: phải CENTER dữ liệu trước
> 2. Singular values sắp GIẢM DẦN
> 3. Eigenvectors phải CHUẨN HÓA (độ dài = 1)
