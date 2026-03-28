import pandas as pd
import json
import os
from tqdm import tqdm


def prepare_arxiv_data(input_file, output_file, target_category='cs.', sample_size=1000000):
    """
    Đọc file dữ liệu arXiv gốc, lọc các bài báo thuộc lĩnh vực Computer Science,
    làm sạch dữ liệu và lưu ra file JSON mới.
    """
    print(f"Bắt đầu xử lý dữ liệu từ: {input_file}")

    if not os.path.exists(input_file):
        print(f"LỖI: Không tìm thấy file {input_file}!")
        print("Vui lòng tải dataset từ Kaggle: https://www.kaggle.com/datasets/Cornell-University/arxiv")
        print("Giải nén và đặt file 'arxiv-metadata-oai-snapshot.json' vào thư mục 'data/'")
        return

    extracted_records = []

    # Đọc file từng dòng vì file gốc rất lớn (hơn 3GB)
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in tqdm(f, desc="Đang quét dữ liệu"):
            try:
                record = json.loads(line)

                # Lọc theo category (chỉ lấy Computer Science)
                categories = record.get('categories', '')
                if target_category in categories:

                    # Trích xuất năm xuất bản từ update_date (hoặc id)
                    # arXiv ID format: YYMM.number hoặc cũ hơn
                    # Lấy tạm năm từ trường update_date (YYYY-MM-DD)
                    update_date = record.get('update_date', '')
                    year = update_date.split('-')[0] if update_date else None

                    # Chỉ lấy các trường cần thiết để tiết kiệm dung lượng
                    clean_record = {
                        'id': record.get('id'),
                        'title': record.get('title', '').replace('\n', ' ').strip(),
                        'abstract': record.get('abstract', '').replace('\n', ' ').strip(),
                        'categories': categories,
                        'authors': record.get('authors', ''),
                        'year': year
                    }

                    # Loại bỏ các record bị thiếu title hoặc abstract
                    if clean_record['title'] and clean_record['abstract']:
                        extracted_records.append(clean_record)

                        # Dừng lại nếu đã đủ số lượng yêu cầu
                        if len(extracted_records) >= sample_size:
                            break
            except json.JSONDecodeError:
                continue

    print(f"\nĐã trích xuất thành công {len(extracted_records)} bài báo.")

    # Lưu ra file JSON mới
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(extracted_records, f, ensure_ascii=False, indent=2)

    print(f"Đã lưu dữ liệu sạch vào: {output_file}")


if __name__ == "__main__":
    # Đường dẫn thư mục
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, 'data')

    INPUT_FILE = os.path.join(DATA_DIR, 'arxiv-metadata-oai-snapshot.json')
    # Midterm scale: 100k CS papers (tạo file khớp với embed_data.py mặc định)
    OUTPUT_FILE = os.path.join(DATA_DIR, 'arxiv_cs_100k_clean.json')

    # Chạy hàm xử lý
    prepare_arxiv_data(INPUT_FILE, OUTPUT_FILE, target_category='cs.', sample_size=100000)

