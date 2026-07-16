import json
import sys
from elasticsearch import Elasticsearch

from src.config import INDEX_TEXT, ES_URL

# Fix lỗi in tiếng Việt trên Windows
sys.stdout.reconfigure(encoding='utf-8')

# Khởi tạo kết nối tới Elasticsearch
es = Elasticsearch(ES_URL)


def keyword_search(query_text, year_filter=None, size=5):
    """
    Thực hiện tìm kiếm từ khóa (BM25) trên các trường title và abstract.
    Có hỗ trợ lọc theo năm.
    """
    print(f"\n--- TÌM KIẾM TỪ KHÓA: '{query_text}' ---")

    # Xây dựng câu truy vấn (Query DSL)
    query_body = {
        "bool": {
            "must": [
                {
                    "multi_match": {
                        "query": query_text,
                        "fields": ["title^2", "abstract"],  # Ưu tiên title (nhân đôi điểm)
                        "type": "best_fields"
                    }
                }
            ]
        }
    }

    # Thêm filter nếu có
    if year_filter:
        print(f"(Filter: Năm {year_filter})")
        query_body["bool"]["filter"] = [
            {"term": {"year": str(year_filter)}}
        ]

    # Gửi request tới Elasticsearch
    response = es.search(
        index=INDEX_TEXT,
        query=query_body,
        size=size,
        _source=["title", "year", "authors"]  # Chỉ lấy các trường cần thiết để in ra
    )

    # Xử lý và in kết quả
    hits = response["hits"]["hits"]
    total_hits = response["hits"]["total"]["value"]

    print(f"Tìm thấy tổng cộng {total_hits} kết quả. Hiển thị top {size}:")

    for i, hit in enumerate(hits, 1):
        score = hit["_score"]
        source = hit["_source"]
        title = source.get("title", "N/A")
        year = source.get("year", "N/A")
        authors = source.get("authors", "N/A")

        print(f"\n[{i}] Score: {score:.4f} | Năm: {year}")
        print(f"Tiêu đề: {title}")
        print(f"Tác giả: {authors[:100]}..." if len(authors) > 100 else f"Tác giả: {authors}")


if __name__ == "__main__":
    if not es.ping():
        print("LỖI: Không thể kết nối tới Elasticsearch!")
        exit(1)

    # Test các câu truy vấn khác nhau
    keyword_search("machine learning for healthcare")
    keyword_search("deep learning transformer", year_filter=2023)
    keyword_search("graph neural networks node classification")
