import json
import os
from elasticsearch import Elasticsearch, helpers
from tqdm import tqdm

# Khởi tạo kết nối tới Elasticsearch (chạy qua Docker)
es = Elasticsearch("http://localhost:9200")

INDEX_NAME = "arxiv_papers"


def create_index():
    """
    Tạo Index trên Elasticsearch với Mapping phù hợp cho tìm kiếm văn bản và filter.
    """
    # Xóa index cũ nếu đã tồn tại
    if es.indices.exists(index=INDEX_NAME):
        print(f"Index '{INDEX_NAME}' đã tồn tại. Đang xóa...")
        es.indices.delete(index=INDEX_NAME)

    # Định nghĩa cấu trúc dữ liệu (Mapping)
    mapping = {
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "title": {"type": "text"},
                "abstract": {"type": "text"},
                "categories": {"type": "keyword"},
                "authors": {"type": "text"},
                "year": {"type": "keyword"}
            }
        },
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }
    }

    print(f"Đang tạo index mới '{INDEX_NAME}'...")
    es.indices.create(index=INDEX_NAME, body=mapping)
    print("Tạo index thành công!")


def generate_actions(data_list):
    """
    Tạo generator để phục vụ cho Bulk API của Elasticsearch.
    """
    for record in data_list:
        yield {
            "_index": INDEX_NAME,
            "_id": record["id"],
            "_source": {
                "title": record["title"],
                "abstract": record["abstract"],
                "categories": record["categories"].split(" "),  # Tách thành mảng các category
                "authors": record["authors"],
                "year": record["year"]
            }
        }


def bulk_index_data(file_path):
    """
    Đọc file JSON đã làm sạch và đẩy dữ liệu vào Elasticsearch bằng Bulk API.
    """
    print(f"Đang đọc dữ liệu từ {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Bắt đầu index {len(data)} documents vào Elasticsearch...")

    # Sử dụng helpers.bulk để đẩy dữ liệu theo batch (mặc định chunk_size=500)
    success, failed = helpers.bulk(
        es,
        generate_actions(data),
        chunk_size=5000,  # Đẩy 5000 docs mỗi lần để tối ưu tốc độ
        request_timeout=60
    )

    print(f"Hoàn thành! Thành công: {success} documents.")
    if failed:
        print(f"Thất bại: {failed} documents.")


if __name__ == "__main__":
    # Kiểm tra kết nối
    if not es.ping():
        print("LỖI: Không thể kết nối tới Elasticsearch. Hãy chắc chắn Docker đang chạy (localhost:9200)!")
        exit(1)

    print("Đã kết nối tới Elasticsearch thành công.")

    # Đường dẫn file dữ liệu sạch
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    CLEAN_DATA_FILE = os.path.join(BASE_DIR, 'data', 'arxiv_cs_100k_clean.json')

    if not os.path.exists(CLEAN_DATA_FILE):
        print(f"LỖI: Không tìm thấy file {CLEAN_DATA_FILE}!")
        print("Vui lòng chạy script 'src/data_prep.py' trước để tạo dữ liệu.")
        exit(1)

    # Thực thi
    create_index()
    bulk_index_data(CLEAN_DATA_FILE)

