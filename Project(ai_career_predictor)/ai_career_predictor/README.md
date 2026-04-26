# 🚀 AI Career Path Predictor
> Built with Flask + Generative AI (Claude API)

## Project Structure
```
ai_career_predictor/
├── app.py                  # Flask backend + API routes
├── requirements.txt        # Dependencies
├── data/
│   └── careers.json        # Career seed data for AI context
└── templates/
    ├── index.html          # Landing page
    ├── quiz.html           # 5-step quiz
    └── results.html        # Results: careers + roadmap
```

## Setup Instructions

### Step 1: Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Set API Key
```bash
# Windows CMD
set ANTHROPIC_API_KEY=your_api_key_here

# Windows PowerShell
$env:ANTHROPIC_API_KEY="your_api_key_here"

# Mac/Linux
export ANTHROPIC_API_KEY=your_api_key_here
```

### Step 4: Run the App
```bash
python app.py
```

Open: http://localhost:5000

---

## Features
- ✅ 5-step interactive quiz (name, skills, interests, personality, goals)
- ✅ GenAI analyzes profile → top 3 career recommendations
- ✅ Match percentage for each career
- ✅ Skill gap detection
- ✅ Personalized 4-phase learning roadmap with resources
- ✅ Beautiful dark UI with animations

## Tech Stack
- **Backend:** Python Flask
- **AI:** Anthropic Claude API (GenAI)
- **Frontend:** HTML, CSS, Vanilla JS
- **Data:** careers.json (seed context for AI)
