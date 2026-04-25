# 🍽️ Restaurant QnA Bot — Lab 10

A semantic question-answering chatbot for a restaurant, built using:
- **HuggingFace MiniLM** for sentence embeddings
- **FAISS** for fast vector similarity search
- **Flask + HTML/CSS/JS** for the web UI

---

## 📁 Project Structure

```
restaurant_qna_bot/
│
├── data/
│   └── restaurant_qna.json        # 30 curated QnA pairs
│
├── templates/
│   └── index.html                 # Flask HTML UI (Bella chatbot)
│
├── preprocess_and_embed.py        # Step 1–3: Preprocess, embed, build FAISS index
├── search_engine.py               # Step 4: Semantic search logic
├── app.py                         # Step 5: Flask app server
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Build the pipeline (run ONCE to generate the FAISS index)
```bash
python preprocess_and_embed.py
```
This will:
- Load and preprocess the 30 restaurant QnA pairs
- Embed all questions using `all-MiniLM-L6-v2`
- Build and save a FAISS index to `model/`

### 3. Start the Flask server
```bash
python app.py
```

### 4. Open the chatbot
Visit: **http://localhost:5000**

---

## 🔍 Pipeline Explanation

| Step | File | Description |
|------|------|-------------|
| 1 | `preprocess_and_embed.py` | Load JSON, clean text (lowercase, strip special chars) |
| 2 | `preprocess_and_embed.py` | Embed questions using `sentence-transformers/all-MiniLM-L6-v2` |
| 3 | `preprocess_and_embed.py` | Build FAISS IndexFlatL2 on normalized vectors = cosine similarity |
| 4 | `search_engine.py` | Preprocess query → embed → search FAISS → return top-k matches |
| 5 | `app.py` + `templates/index.html` | Flask backend + styled chat UI (Bella) |

---

## 💬 Sample Questions to Try

- "What are your opening hours?"
- "Do you have vegetarian food?"
- "Can I make a reservation?"
- "Do you deliver to my area?"
- "Is there wifi?"
- "What's your most popular dish?"
- "Do you allow dogs?"
- "Tell me about happy hour"

---

## 🧠 Model Info

- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Embedding size**: 384 dimensions
- **Similarity**: Cosine similarity via normalized L2 FAISS index
- **Threshold**: 55% confidence (adjustable in `search_engine.py`)
