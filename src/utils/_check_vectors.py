import sys, json
sys.stdout.reconfigure(encoding='utf-8')

with open('data/arxiv_cs_100k_with_vectors.jsonl', 'r', encoding='utf-8') as f:
    first = json.loads(f.readline())

print('Keys:', list(first.keys()))
if 'embedding' in first:
    emb = first['embedding']
    print(f'Embedding dim: {len(emb)}')
    print(f'First 5 values: {emb[:5]}')
    title = first.get('title', '')
    print(f'Title: {title[:80]}...')
else:
    print('WARNING: No embedding field found!')

