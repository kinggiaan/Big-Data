"""Quick sanity check for sentence-transformers cosine similarity."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

model = SentenceTransformer('all-MiniLM-L6-v2')
print(f'Model loaded. Device: {model.device}')
print(f'Embedding dim: {model.get_sentence_embedding_dimension()}')
print()

pairs = [
    ('deep learning for image classification', 'using neural networks to categorize pictures'),
    ('reinforcement learning in robotics', 'training robots with reward-based algorithms'),
    ('natural language processing', 'quantum computing algorithms'),
    ('BERT fine-tuning for NLP', 'pre-trained language model adaptation'),
    ('cat sitting on a mat', 'adversarial robustness in deep networks'),
]

print('Cosine Similarity Sanity Check')
print('=' * 70)
for a, b in pairs:
    emb = model.encode([a, b])
    sim = cos_sim(emb[0], emb[1]).item()
    label = 'HIGH' if sim > 0.5 else ('MED' if sim > 0.3 else 'LOW')
    print(f'  [{label:4s}] {sim:.4f}  |  "{a}"  vs  "{b}"')

print()
emb = model.encode(['methods to detect fake images', 'deepfake detection algorithms'])
sim = cos_sim(emb[0], emb[1]).item()
print(f'Key test (should be > 0.7): {sim:.4f}')
print(f'  "methods to detect fake images" vs "deepfake detection algorithms"')
print(f'  Result: {"PASS" if sim > 0.7 else "FAIL"}')

