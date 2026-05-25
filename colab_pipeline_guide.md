# Hướng dẫn chạy Pipeline dữ liệu arXiv trên Google Colab (Sử dụng GPU & Kaggle API)

Để xử lý tập dữ liệu arXiv gốc rất lớn (~3.6 GB dữ liệu thô) và sinh vector nhúng (embedding) cho 100,000 bài báo (hoặc toàn bộ 1.16M bài báo), việc sử dụng **Google Colab với phần cứng GPU miễn phí (như Nvidia T4)** là giải pháp tối ưu nhất.

Dưới đây là quy trình chi tiết và mã nguồn để bạn chạy trực tiếp trên Google Colab.

---

## BƯỚC 1: Tạo Notebook mới trên Google Colab
1. Truy cập [Google Colab](https://colab.research.google.com/).
2. Chọn **New Notebook** (Sổ tay mới).
3. Đổi môi trường chạy sang **GPU**: 
   * Chọn menu **Runtime** (Môi trường chạy) -> **Change runtime type** (Thay đổi loại môi trường chạy).
   * Chọn **T4 GPU** (hoặc GPU bất kỳ có sẵn) và nhấn **Save** (Lưu).

---

## BƯỚC 2: Cài đặt thư viện cần thiết
Tạo một ô mã (Code cell) mới và chạy lệnh sau để cài đặt `sentence-transformers` và `tqdm`:

```python
!pip install sentence-transformers tqdm pandas
```

---

## BƯỚC 3: Kết nối Google Drive (Để lưu kết quả lâu dài)
Chạy ô mã sau để mount Google Drive của bạn. Điều này giúp lưu tệp vector kết quả một cách an toàn mà không sợ bị mất khi Colab ngắt kết nối:

```python
from google.colab import drive
import os

drive.mount('/content/drive')

# Tạo thư mục lưu trữ trong Google Drive
DATA_DIR = "/content/drive/MyDrive/arxiv_data"
os.makedirs(DATA_DIR, exist_ok=True)
print(f"Thư mục lưu trữ: {DATA_DIR}")
```

---

## BƯỚC 4: Tải dataset trực tiếp từ Kaggle về Colab
Để tránh việc phải tải 3.6 GB về máy cá nhân rồi upload lên Colab (rất chậm), bạn hãy tải trực tiếp từ Kaggle bằng Kaggle API:

1. Vào [Kaggle](https://www.kaggle.com/) -> Chọn **Settings** (Cài đặt tài khoản của bạn).
2. Cuộn xuống phần **API** -> Chọn **Create New Token**. Trình duyệt sẽ tải về một file tên là `kaggle.json`.
3. Chạy ô mã dưới đây trên Colab, chọn upload file `kaggle.json` vừa tải về:

```python
from google.colab import files
import json

# Upload file kaggle.json
uploaded = files.upload()

# Cấu hình thư mục chứa Kaggle token
!mkdir -p ~/.kaggle
!mv kaggle.json ~/.kaggle/
!chmod 600 ~/.kaggle/kaggle.json

# Tải bộ dữ liệu arXiv từ Kaggle về Colab (chỉ mất khoảng 1-2 phút)
!kaggle datasets download -d Cornell-University/arxiv -p /content/
!unzip -o /content/arxiv.zip -d /content/
print("Tải dữ liệu hoàn tất!")
```

---

## BƯỚC 5: Trích xuất các bài báo Computer Science (Data Prep)
Chạy đoạn mã sau để lọc các bài báo thuộc lĩnh vực `cs.` (Computer Science). 

*   *Lưu ý*: Bạn có thể điều chỉnh biến `SAMPLE_SIZE = 100000` (đối với Midterm) hoặc đổi tên file đầu ra thành `arxiv_cs_full.jsonl` để lấy toàn bộ dữ liệu Computer Science.

```python
import json
import os
from tqdm import tqdm

INPUT_FILE = "/content/arxiv-metadata-oai-snapshot.json"
# Lưu trực tiếp vào Google Drive để an toàn
OUTPUT_FILE = os.path.join(DATA_DIR, "arxiv_cs_100k_clean.json") 
SAMPLE_SIZE = 100000 # Điều chỉnh kích thước tại đây

print("Đang quét dữ liệu thô và lọc CS papers...")
extracted_records = []

with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    for line in tqdm(f, desc="Scanning"):
        try:
            record = json.loads(line)
            categories = record.get('categories', '')
            if 'cs.' in categories:
                update_date = record.get('update_date', '')
                year = update_date.split('-')[0] if update_date else None

                clean_record = {
                    'id': record.get('id'),
                    'title': record.get('title', '').replace('\n', ' ').strip(),
                    'abstract': record.get('abstract', '').replace('\n', ' ').strip(),
                    'categories': categories,
                    'authors': record.get('authors', ''),
                    'year': year
                }

                if clean_record['title'] and clean_record['abstract']:
                    extracted_records.append(clean_record)
                    if len(extracted_records) >= SAMPLE_SIZE:
                        break
        except json.JSONDecodeError:
            continue

# Lưu file dạng JSON array
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(extracted_records, f, ensure_ascii=False, indent=2)

print(f"\nĐã lưu {len(extracted_records):,} bài báo sạch vào: {OUTPUT_FILE}")
```

---

## BƯỚC 6: Tạo Vector Nhúng (Embedding) sử dụng GPU
Đoạn mã dưới đây sử dụng mô hình `all-MiniLM-L6-v2` để sinh vector nhúng và lưu dưới dạng JSONL. 

*   **Tính năng phục hồi (Resume)**: Đoạn mã tự động kiểm tra xem tệp kết quả trong Google Drive đã có dữ liệu chưa. Nếu Colab bị ngắt kết nối giữa chừng, bạn chỉ cần chạy lại ô này, chương trình sẽ tự động tiếp tục từ vị trí đã dừng mà không phải sinh lại từ đầu.

```python
import json
import os
import time
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

INPUT_FILE = os.path.join(DATA_DIR, "arxiv_cs_100k_clean.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "arxiv_cs_100k_with_vectors.jsonl")
MODEL_NAME = "all-MiniLM-L6-v2"
BATCH_SIZE = 512 # Kích thước lô tối ưu cho GPU T4

# Đếm số lượng dòng đã xử lý để khôi phục (nếu có)
def count_existing(path):
    if not os.path.exists(path):
        return 0
    count = 0
    with open(path, "r", encoding="utf-8") as f:
        for _ in f:
            count += 1
    return count

print("Đang khởi tạo mô hình nhúng...")
model = SentenceTransformer(MODEL_NAME)
device = str(model.device)
print(f"Đang sử dụng phần cứng: {device}")

# Đọc toàn bộ dữ liệu thô đầu vào
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    records = json.load(f)

total_records = len(records)
already_done = count_existing(OUTPUT_FILE)
print(f"Tổng số bài báo: {total_records:,}")
print(f"Đã xử lý trước đó: {already_done:,}")
print(f"Cần xử lý tiếp: {total_records - already_done:,}")

out_file = open(OUTPUT_FILE, "a", encoding="utf-8")
texts_batch = []
records_batch = []
processed = 0

try:
    pbar = tqdm(total=total_records, initial=already_done, desc="Embedding")
    
    for idx, record in enumerate(records):
        if idx < already_done:
            continue
            
        title = record.get("title", "")
        abstract = record.get("abstract", "")
        text = f"{title} [SEP] {abstract}"
        
        texts_batch.append(text)
        records_batch.append(record)
        
        if len(texts_batch) >= BATCH_SIZE:
            embeddings = model.encode(texts_batch, show_progress_bar=False, normalize_embeddings=True)
            for rec, emb in zip(records_batch, embeddings):
                rec["embedding"] = emb.tolist()
                out_file.write(json.dumps(rec, ensure_ascii=False) + "\n")
            processed += len(texts_batch)
            pbar.update(len(texts_batch))
            texts_batch.clear()
            records_batch.clear()
            
            # Ghi đè bộ nhớ đệm lên Google Drive sau mỗi lô
            out_file.flush()
            
    # Xử lý phần dư còn lại
    if texts_batch:
        embeddings = model.encode(texts_batch, show_progress_bar=False, normalize_embeddings=True)
        for rec, emb in zip(records_batch, embeddings):
            rec["embedding"] = emb.tolist()
            out_file.write(json.dumps(rec, ensure_ascii=False) + "\n")
        processed += len(texts_batch)
        pbar.update(len(texts_batch))
        
    pbar.close()
finally:
    out_file.flush()
    out_file.close()

print(f"\nSinh vector hoàn tất! File kết quả nằm trong Google Drive của bạn:")
print(OUTPUT_FILE)
```

---

## BƯỚC 7: Tải file kết quả về máy nội bộ để Index
Sau khi chạy xong trên Colab, file `arxiv_cs_100k_with_vectors.jsonl` sẽ nằm tại thư mục `arxiv_data/` trong Google Drive của bạn.
1. Tải file `arxiv_cs_100k_with_vectors.jsonl` này từ Google Drive về máy tính của bạn.
2. Đặt nó vào thư mục `data/` trong workspace dự án (ghi đè lên tệp 3 bài báo cũ).
3. Tiến hành chạy lệnh Index Elasticsearch cục bộ hoặc di chuyển lên Cloudflare D1/Vectorize như kế hoạch:
   ```bash
   wsl python3 src/pipeline/index_data_v2.py
   ```
