from flask import Flask, render_template, request, jsonify, session
from groq import Groq
import json
import os

app = Flask(__name__)
app.secret_key = "career_predictor_secret_2024"

with open("data/careers.json", "r", encoding="utf-8") as f:
    CAREER_DATA = json.load(f)

client = Groq(api_key="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")

SYSTEM_PROMPT = """You are an expert AI Career Counselor and Skills Analyst. 
You analyze a user's skills, interests, experience level, and personality traits to:
1. Suggest the TOP 3 most suitable career paths with match percentage
2. Identify skill gaps for each recommended career
3. Create a personalized 4-phase learning roadmap

Always respond in valid JSON format only. No markdown, no extra text.

Response format:
{
  "careers": [
    {
      "title": "Career Title",
      "match_percentage": 85,
      "why_suited": "2-3 sentence explanation",
      "current_strengths": ["skill1", "skill2"],
      "skill_gaps": ["missing_skill1", "missing_skill2", "missing_skill3"]
    }
  ],
  "top_career": "Best matched career title",
  "roadmap": {
    "phase1": {
      "title": "Foundation Building",
      "duration": "1-2 months",
      "tasks": ["task1", "task2", "task3"],
      "resources": ["resource1", "resource2"]
    },
    "phase2": {
      "title": "Core Skill Development",
      "duration": "2-3 months",
      "tasks": ["task1", "task2", "task3"],
      "resources": ["resource1", "resource2"]
    },
    "phase3": {
      "title": "Practical Experience",
      "duration": "2-3 months",
      "tasks": ["task1", "task2", "task3"],
      "resources": ["resource1", "resource2"]
    },
    "phase4": {
      "title": "Job Readiness",
      "duration": "1-2 months",
      "tasks": ["task1", "task2", "task3"],
      "resources": ["resource1", "resource2"]
    }
  },
  "motivational_message": "A personalized encouraging message"
}"""


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/quiz")
def quiz():
    return render_template("quiz.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()

    prompt = f"""You are an expert AI Career Counselor.
Analyze this user profile and respond in valid JSON only. No markdown, no extra text.

User Profile:
- Name: {data.get('name')}
- Education: {data.get('education')}
- Experience: {data.get('experience')}
- Skills: {', '.join(data.get('skills', []))}
- Interests: {', '.join(data.get('interests', []))}
- Work Style: {data.get('work_style')}
- Goal: {data.get('goal')}
- Personality: {', '.join(data.get('personality', []))}

Career options:
{json.dumps(CAREER_DATA['careers'], indent=2)}

Respond ONLY in this JSON format:
{{
  "careers": [
    {{
      "title": "Career Title",
      "match_percentage": 85,
      "why_suited": "explanation",
      "current_strengths": ["skill1", "skill2"],
      "skill_gaps": ["gap1", "gap2"]
    }}
  ],
  "top_career": "Best career title",
  "roadmap": {{
    "phase1": {{"title": "Foundation", "duration": "1-2 months", "tasks": ["t1","t2","t3"], "resources": ["r1","r2"]}},
    "phase2": {{"title": "Core Skills", "duration": "2-3 months", "tasks": ["t1","t2","t3"], "resources": ["r1","r2"]}},
    "phase3": {{"title": "Practice", "duration": "2-3 months", "tasks": ["t1","t2","t3"], "resources": ["r1","r2"]}},
    "phase4": {{"title": "Job Ready", "duration": "1-2 months", "tasks": ["t1","t2","t3"], "resources": ["r1","r2"]}}
  }},
  "motivational_message": "personalized message"
}}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )
        text = response.choices[0].message.content.strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        result = json.loads(text.strip())
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    
@app.route("/results")
def results():
    return render_template("results.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
