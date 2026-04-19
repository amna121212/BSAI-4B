"""
preprocess_and_embed.py
Pipeline Step 1 & 2: Load, preprocess QnA data and embed using HuggingFace MiniLM
"""

import json
import re
import numpy as np
import faiss
import pickle
import os
from sentence_transformers import SentenceTransformer

# ─────────────────────────────────────────────
# STEP 1: LOAD & PREPROCESS DATA
# ─────────────────────────────────────────────

def load_data(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"[✓] Loaded {len(data)} QnA pairs from {filepath}")
    return data

def preprocess_text(text):
    """Clean and normalize text."""
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)           # collapse whitespace
    text = re.sub(r'[^\w\s.,!?\'"-]', '', text) # remove special chars
    text = text.lower()
    return text

def preprocess_dataset(data):
    """Preprocess all questions and answers."""
    processed = []
    for item in data:
        processed.append({
            "question": preprocess_text(item["question"]),
            "answer": item["answer"],             # keep answers readable (not lowercased)
            "original_question": item["question"] # preserve original for display
        })
    print(f"[✓] Preprocessed {len(processed)} entries")
    return processed

# ─────────────────────────────────────────────
# STEP 2: EMBED USING HuggingFace MiniLM
# ─────────────────────────────────────────────

def embed_questions(processed_data, model_name="sentence-transformers/all-MiniLM-L6-v2"):
    """Generate embeddings for all questions using MiniLM."""
    print(f"[~] Loading model: {model_name}")
    model = SentenceTransformer(model_name)
    
    questions = [item["question"] for item in processed_data]
    print(f"[~] Embedding {len(questions)} questions...")
    embeddings = model.encode(questions, show_progress_bar=True, convert_to_numpy=True)
    print(f"[✓] Embeddings shape: {embeddings.shape}")
    return model, embeddings

# ─────────────────────────────────────────────
# STEP 3: STORE VECTORS USING FAISS
# ─────────────────────────────────────────────

def build_faiss_index(embeddings):
    """Build a FAISS index from embeddings using cosine similarity (via L2 on normalized vectors)."""
    dimension = embeddings.shape[1]
    
    # Normalize embeddings for cosine similarity
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    normalized = embeddings / norms
    
    # Use flat (exact) L2 index on normalized vectors = cosine similarity
    index = faiss.IndexFlatL2(dimension)
    index.add(normalized.astype(np.float32))
    
    print(f"[✓] FAISS index built with {index.ntotal} vectors (dim={dimension})")
    return index, normalized

# ─────────────────────────────────────────────
# SAVE EVERYTHING
# ─────────────────────────────────────────────

def save_pipeline(index, processed_data, normalized_embeddings, output_dir="model"):
    os.makedirs(output_dir, exist_ok=True)
    
    faiss.write_index(index, os.path.join(output_dir, "qna.index"))
    
    with open(os.path.join(output_dir, "qna_data.pkl"), "wb") as f:
        pickle.dump(processed_data, f)
    
    np.save(os.path.join(output_dir, "embeddings.npy"), normalized_embeddings)
    
    print(f"[✓] Pipeline saved to '{output_dir}/'")

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    raw_data = load_data(os.path.join(BASE_DIR, "data", "restaurant_qna.json"))
    processed_data = preprocess_dataset(raw_data)
    model, embeddings = embed_questions(processed_data)
    index, normalized = build_faiss_index(embeddings)
    save_pipeline(index, processed_data, normalized, output_dir=os.path.join(BASE_DIR, "model"))
    
    print("\n[✓] Pipeline complete! Run app.py to start the Flask server.")
