#!/bin/bash
echo "=== Doc Count ==="
echo -n "arxiv_text:    "
curl -s http://localhost:9200/arxiv_text/_count | python3 -c "import sys,json; print(json.load(sys.stdin)['count'])"
echo -n "arxiv_vectors: "
curl -s http://localhost:9200/arxiv_vectors/_count | python3 -c "import sys,json; print(json.load(sys.stdin)['count'])"

echo ""
echo "=== Sample: Same doc in both indices ==="
# Get first doc ID from arxiv_text
DOC_ID=$(curl -s 'http://localhost:9200/arxiv_text/_search?size=1' | python3 -c "import sys,json; print(json.load(sys.stdin)['hits']['hits'][0]['_id'])")
echo "Doc ID: $DOC_ID"

echo ""
echo "--- From arxiv_text (no embedding): ---"
curl -s "http://localhost:9200/arxiv_text/_doc/$DOC_ID?_source_excludes=abstract" | python3 -m json.tool

echo ""
echo "--- From arxiv_vectors (has embedding): ---"
curl -s "http://localhost:9200/arxiv_vectors/_doc/$DOC_ID?_source=title,year,categories" | python3 -m json.tool
