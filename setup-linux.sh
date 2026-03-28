#!/usr/bin/env bash
# Tạo venv và cài dependency trên Linux/macOS (POSIX).
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Cần cài Python 3 (ví dụ: sudo apt install python3 python3-venv python3-pip)"
  exit 1
fi

python3 -m venv venv
# shellcheck source=/dev/null
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Xong. Kích hoạt môi trường:"
echo "  source venv/bin/activate"
echo "Sau đó: docker compose up -d  và chạy các bước trong README (Linux)."
