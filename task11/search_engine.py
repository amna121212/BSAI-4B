"""
search_engine.py
Pipeline Step 4: Semantic search using FAISS + MiniLM embeddings
"""

import os
import re
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# ─────────────────────────────────────────────
# Load pipeline artifacts
# ─────────────────────────────────────────────

def load_pipeline(model_dir="model"):
    base = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.path.join(base, model_dir)

    index = faiss.read_index(os.path.join(model_dir, "qna.index"))

    with open(os.path.join(model_dir, "qna_data.pkl"), "rb") as f:
        qna_data = pickle.load(f)

    model = SentenceTransformer(MODEL_NAME)
    print(f"[✓] Pipeline loaded: {index.ntotal} vectors, {len(qna_data)} QnA pairs")
    return index, qna_data, model


# ─────────────────────────────────────────────
# Preprocess query (mirror training preprocessing)
# ─────────────────────────────────────────────

def preprocess_query(text):
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,!?\'"-]', '', text)
    text = text.lower()
    return text


# ─────────────────────────────────────────────
# Semantic search
# ─────────────────────────────────────────────

def search(query, index, qna_data, model, top_k=3, threshold=0.75):
    """
    Search for the best matching QnA pair.
    Returns list of (original_question, answer, similarity_score).
    threshold: cosine similarity cut-off (distance < 2*(1-threshold) for normalized vectors)
    """
    cleaned = preprocess_query(query)
    query_embedding = model.encode([cleaned], convert_to_numpy=True)
    
    # Normalize for cosine similarity
    norm = np.linalg.norm(query_embedding, axis=1, keepdims=True)
    query_normalized = (query_embedding / norm).astype(np.float32)
    
    distances, indices = index.search(query_normalized, top_k)
    
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx == -1:
            continue
        # Convert L2 distance on normalized vectors → cosine similarity
        cosine_similarity = 1 - (dist / 2)
        if cosine_similarity >= threshold:
            results.append({
                "question": qna_data[idx]["original_question"],
                "answer": qna_data[idx]["answer"],
                "score": round(float(cosine_similarity) * 100, 1)
            })
    
    return results


# ─────────────────────────────────────────────
# Quick CLI test
# ─────────────────────────────────────────────

if __name__ == "__main__":
    index, qna_data, model = load_pipeline()
    
    test_queries = [
        "When do you open?",
        "Can I book a table?",
        "Do you have food for vegetarians?",
        "Is there free wifi?",
        "What is your most famous dish?",
    ]
    
    for q in test_queries:
        print(f"\nQuery: {q}")
        results = search(q, index, qna_data, model)
        if results:
            top = results[0]
            print(f"  Match ({top['score']}%): {top['question']}")
            print(f"  Answer: {top['answer'][:80]}...")
        else:
            print("  No confident match found.")
