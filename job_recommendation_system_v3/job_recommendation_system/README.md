# 🤖 AI-Powered Job Recommendation System

> **NLP-based job matching engine** — built with TF-IDF, Cosine Similarity, Flask, and SQLite.  
> Internship Project · LearnDepth Academy · March 2026

---

## 📸 Features at a Glance

| Feature | Description |
|---|---|
| 🎯 Smart Recommendations | TF-IDF + Cosine Similarity ranks 42 job roles by skill match |
| 🔍 Skill Gap Analysis | See exactly which skills you're missing for any role |
| 📄 Resume Parser | Paste resume text → auto-extracts 80+ recognizable tech skills |
| 🕓 History Tracking | Every recommendation run saved to DB per user |
| 📊 Visual Match % | Color-coded progress bars (green ≥70%, amber ≥40%, red <40%) |
| 🏷️ Quick Skill Tags | One-click skill adding in the UI |
| 🌐 REST API | 8 clean endpoints, JSON in/out, CORS-enabled |

---

## 🗂️ Project Structure

```
job_recommendation_system/
│
├── app.py              ← Flask app — routes, startup, request handling
├── model.py            ← ML core: TF-IDF vectorizer, cosine similarity,
│                          skill gap analysis, resume skill extraction
├── database.py         ← SQLite layer: schema init, CRUD for all 3 tables
├── dataset.py          ← 42 diverse job roles across 10 domains
├── seed_data.py        ← One-command DB setup + seeding
│
├── templates/
│   └── index.html      ← Single-page frontend (vanilla JS, no frameworks)
├── static/
│   └── style.css       ← Dark-theme design system with CSS variables
│
├── uploads/            ← Resume file uploads (auto-created)
├── database.db         ← SQLite DB (auto-created on first run)
│
├── requirements.txt    ← 6 dependencies
├── .env.example        ← Environment variable template
├── test_system.py      ← Full test suite (no Flask server needed)
└── README.md
```

---

## ⚙️ Quick Start

### 1. Clone / Download the project
```bash
cd job_recommendation_system
```

### 2. (Recommended) Create a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
python app.py
```

On first run, this will automatically:
- ✅ Create `database.db` with all 3 tables
- ✅ Seed 42 job records
- ✅ Fit the TF-IDF model
- ✅ Start Flask on `http://localhost:5000`

### 5. Open the UI
```
http://localhost:5000
```

---

## 🔌 API Reference

### `POST /api/users` — Register User
```json
Request:  { "name": "Alice", "email": "alice@test.com",
            "skills": "Python, ML, SQL", "experience": "2 years" }
Response: { "success": true, "user_id": 1, "message": "..." }
```

### `GET /api/users/<id>` — Get User Profile
```json
Response: { "success": true, "user": { "id": 1, "name": "Alice", ... } }
```

### `GET /api/jobs` — List All Jobs
```
Query params: ?search=python  ?limit=10
```

### `POST /api/recommend` — Get Recommendations ⭐
```json
Request:  { "skills": "Python, Machine Learning, SQL",
            "top_n": 8, "save": true, "user_id": 1 }
Response: { "success": true, "recommendations": [
              { "job_title": "Data Scientist",
                "match_percent": 78.3,
                "score": 0.783, ... }
            ]}
```

### `POST /api/recommend/gap` — Skill Gap Analysis ⭐
```json
Request:  { "user_skills": "Python, SQL", "job_id": 1 }
Response: { "gap_analysis": {
              "matched_skills": ["Python", "Sql"],
              "missing_skills": ["Machine Learning", "TensorFlow", ...],
              "coverage_percent": 22.2 } }
```

### `POST /api/resume/extract` — Extract Skills from Resume
```json
Request:  { "text": "I work with Python, Docker, AWS..." }
Response: { "extracted_skills": "Aws, Docker, Python", "skill_count": 3 }
```

### `GET /api/history/<user_id>` — Recommendation History
```json
Response: { "user": {...}, "history": [{...}, ...], "count": 5 }
```

### `GET /api/stats` — Database Stats
```json
Response: { "stats": { "total_users": 3, "total_jobs": 42,
                        "total_recommendations": 15 } }
```

---

## 🧠 How the ML Works

```
User Skills String
        │
        ▼
  preprocess_skills()
  • lowercase
  • expand abbreviations (ml → machine learning)
  • remove punctuation
        │
        ▼
  TfidfVectorizer.transform()
  • Converts skill text into a weighted numeric vector
  • Rare/specific skills get higher IDF weight
  • ngram_range=(1,2) captures "machine learning" as a phrase
        │
        ▼
  cosine_similarity(user_vector, job_matrix)
  • Computes similarity score for every job at once (vectorized)
  • Returns values 0.0 → 1.0
        │
        ▼
  Sort by score → Top N results
```

### Why these choices?

| Choice | Reason |
|---|---|
| TF-IDF over Bag-of-Words | Weights rare skills higher (more discriminative) |
| Cosine over Euclidean | Ignores vector length, fairer for short skill lists |
| ngram_range=(1,2) | "Machine Learning" treated as one concept, not two |
| sublinear_tf=True | Prevents extremely common skills from dominating |
| Fit once at startup | ~10ms inference per request vs ~200ms if re-fitting every time |

---

## 🔧 Configuration

Copy `.env.example` to `.env` and adjust:
```env
FLASK_DEBUG=true
FLASK_PORT=5000
DB_PATH=database.db
MAX_RECOMMENDATIONS=20
```

---

## 🚀 Deployment (Production)

```bash
# Use Gunicorn instead of Flask dev server
gunicorn --workers 2 --bind 0.0.0.0:8000 app:app
```

For cloud deployment: Railway, Render, or Heroku all support this setup with zero config changes.

---

## 📈 Possible Improvements

1. **PDF Resume Parsing** — Use `pdfplumber` to extract text from PDF uploads
2. **BERT-based Skills NER** — Fine-tuned model for better skill extraction accuracy
3. **Collaborative Filtering** — "Users like you also matched..." recommendations
4. **User Authentication** — JWT tokens with Flask-JWT-Extended
5. **PostgreSQL** — Swap SQLite for production-scale database
6. **Redis Caching** — Cache top recommendations for frequent users
7. **Evaluation Metrics** — Track NDCG@K, Precision@K for model quality

---

## 📦 Dependencies

```
flask==3.0.3           Web framework
flask-cors==4.0.1      CORS headers for API
scikit-learn==1.5.1    TF-IDF + cosine similarity
numpy==1.26.4          Numerical operations
pandas==2.2.2          Data handling utilities
python-dotenv==1.0.1   Environment variable loading
```

---

*Built for LearnDepth Academy ML Internship · March 2026*
