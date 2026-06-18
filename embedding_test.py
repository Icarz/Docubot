from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")

texts = [
    "What is the refund window?",
    "How long do I have to return an item?",
    "What color is your logo?"
]

embeddings = [model.encode(t) for t in texts]

# Compare text 0 vs text 1 (should be high)
sim_01 = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
print(f"Text 0 vs Text 1: {sim_01:.2f}")

# Compare text 0 vs text 2 (should be low)
sim_02 = cosine_similarity([embeddings[0]], [embeddings[2]])[0][0]
print(f"Text 0 vs Text 2: {sim_02:.2f}")