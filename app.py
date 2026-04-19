"""
app.py
Pipeline Step 5: Flask backend serving the Restaurant QnA Bot
"""

from flask import Flask, request, jsonify, render_template
from search_engine import load_pipeline, search

app = Flask(__name__)

# Load pipeline once at startup
print("[~] Loading QnA pipeline...")
index, qna_data, model = load_pipeline()
print("[✓] Server ready.\n")

 
# Routes
 

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    query = data.get("question", "").strip()
    
    if not query:
        return jsonify({"error": "Please enter a question."}), 400
    
    results = search(query, index, qna_data, model, top_k=3, threshold=0.30)
    
    if not results:
        return jsonify({
            "answer": "I'm sorry, I couldn't find a confident answer to your question. "
                      "Please try rephrasing, or call us at (555) 123-4567 for direct assistance!",
            "matched_question": None,
            "score": None,
            "suggestions": []
        })
    
    top = results[0]
    suggestions = [r for r in results[1:] if r["score"] >= 60]
    
    return jsonify({
        "answer": top["answer"],
        "matched_question": top["question"],
        "score": top["score"],
        "suggestions": suggestions
    })


@app.route("/all_questions")
def all_questions():
    """Return all questions for the suggestion dropdown."""
    questions = [item["original_question"] for item in qna_data]
    return jsonify(questions)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
