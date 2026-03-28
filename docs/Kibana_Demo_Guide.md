# Hướng dẫn sử dụng Kibana và Elasticsearch cho Demo Midterm

Tài liệu này hướng dẫn bạn cách thao tác trực tiếp trên giao diện Kibana để chụp ảnh minh chứng cho báo cáo Midterm, cũng như cách demo trực tiếp cho giáo viên xem.

---

## 1. Kiểm tra Elasticsearch (Backend)
Mở trình duyệt và truy cập: **http://localhost:9200**

Bạn sẽ thấy một đoạn mã JSON tương tự như sau. **Hãy chụp màn hình đoạn này lại** để chứng minh Elasticsearch đang chạy thành công trên máy bạn.

```json
{
  "name" : "elasticsearch",
  "cluster_name" : "docker-cluster",
  "cluster_uuid" : "xxxxxx",
  "version" : {
    "number" : "8.12.2",
    "lucene_version" : "9.9.2"
  },
  "tagline" : "You Know, for Search"
}
```

---

## 2. Truy cập Kibana (Giao diện quản lý)
Mở trình duyệt và truy cập: **http://localhost:5601**

Lần đầu tiên vào, Kibana có thể hiện màn hình chào mừng. Bạn hãy làm theo các bước sau:
1. Bấm **"Explore on my own"** (nếu có).
2. Nhìn sang thanh menu bên trái (có biểu tượng 3 dấu gạch ngang `☰`).
3. Kéo xuống dưới cùng, tìm mục **Management** -> Chọn **Dev Tools** (Biểu tượng hình cái cờ lê).

**Dev Tools** là nơi bạn gõ các câu lệnh giao tiếp trực tiếp với Elasticsearch. Nó chia làm 2 nửa:
- **Bên trái:** Nơi bạn gõ câu lệnh (Query).
- **Bên phải:** Nơi hiển thị kết quả trả về từ database.

---

## 3. Các câu lệnh Demo trong Kibana Dev Tools

Bạn hãy copy từng đoạn code dưới đây, dán vào nửa bên trái của Dev Tools, sau đó bấm nút **Play (mũi tên màu xanh lá)** ở góc trên bên phải của dòng lệnh đó để chạy.

### Lệnh 1: Kiểm tra số lượng dữ liệu (Chứng minh đã đẩy đủ 100k bài báo)
```json
GET /arxiv_papers/_count
```
*Kết quả bên phải sẽ hiện `"count": 100000`. **-> Chụp màn hình này lại.***

### Lệnh 2: Xem cấu trúc Index (Mapping)
```json
GET /arxiv_papers/_mapping
```
*Kết quả sẽ show ra cấu trúc dữ liệu bạn đã định nghĩa (title là text, year là keyword,...). **-> Chụp màn hình này lại.***

### Lệnh 3: Demo tìm kiếm từ khóa (BM25) trực tiếp trên Kibana
```json
GET /arxiv_papers/_search
{
  "query": {
    "match": {
      "title": "machine learning"
    }
  },
  "_source": ["title", "year", "authors"],
  "size": 3
}
```
*Kết quả bên phải sẽ trả về 3 bài báo có chứa từ "machine learning" trong tiêu đề, kèm theo điểm số `_score`. **-> Chụp màn hình này lại.***

### Lệnh 4: Demo tìm kiếm kết hợp Filter (Lọc theo năm)
```json
GET /arxiv_papers/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "abstract": "deep learning"
          }
        }
      ],
      "filter": [
        {
          "term": {
            "year": "2023"
          }
        }
      ]
    }
  },
  "_source": ["title", "year"],
  "size": 3
}
```
*Kết quả sẽ trả về các bài báo có chữ "deep learning" trong phần tóm tắt và bắt buộc phải xuất bản năm 2023. **-> Chụp màn hình này lại.***

---

## 4. Tổng hợp những gì bạn đã làm được (Để nói lúc thuyết trình)

Khi thuyết trình, bạn có thể tóm tắt công việc của nhóm trong Midterm như sau:

1. **Về Dữ liệu (Data Engineering):**
   - Nhóm đã tải bộ dữ liệu gốc của arXiv nặng hơn 3GB (chứa 2.7 triệu bài báo).
   - Đã viết script Python (`data_prep.py`) đọc từng dòng để không bị tràn RAM, lọc ra đúng 100,000 bài báo thuộc lĩnh vực Khoa học Máy tính (Computer Science).
   - Đã làm sạch dữ liệu (loại bỏ các bài thiếu Title/Abstract) và xuất ra file JSON chuẩn.

2. **Về Hạ tầng (Infrastructure):**
   - Đã đóng gói và khởi chạy thành công cụm Elasticsearch 8.x và Kibana bằng Docker Compose.
   - Việc dùng Docker giúp hệ thống dễ dàng triển khai trên mọi máy tính mà không lo xung đột môi trường.

3. **Về Tìm kiếm (Search Engine):**
   - Đã thiết kế Index Mapping tối ưu: dùng kiểu `text` cho Title/Abstract để tìm kiếm toàn văn bản, và kiểu `keyword` cho Year/Category để lọc tốc độ cao.
   - Đã dùng Bulk API của Python (`index_data.py`) để đẩy 100,000 bài báo vào database chỉ trong khoảng 1-2 phút.
   - Đã xây dựng thành công thuật toán tìm kiếm cơ sở (Baseline) dùng BM25 (`search.py`), hỗ trợ tìm kiếm có trọng số (ưu tiên Title hơn Abstract) và kết hợp Filter. Tốc độ truy vấn trả về kết quả gần như tức thời (dưới 100ms).

*=> "Đây là nền tảng vững chắc để trong giai đoạn Final, nhóm sẽ tiến hành nhúng (embed) 100k bài báo này thành Vector và triển khai Hybrid Search."*