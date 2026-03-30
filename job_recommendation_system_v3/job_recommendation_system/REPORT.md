# AI-Powered Job Recommendation System
## Project Report — LearnDepth Academy Internship

---

## 1. Project Overview

This project implements a complete end-to-end **AI-Powered Job Recommendation System** using:
- NLP-based Machine Learning (TF-IDF + Cosine Similarity)
- SQLite database with relational design
- Flask REST API backend
- Modern responsive frontend UI
- Advanced features: skill gap analysis, resume extraction, recommendation history

---

## 2. System Architecture

```
User (Browser)
    │
    ▼
Frontend (HTML/CSS/JS)
    │  REST API calls (fetch)
    ▼
Flask Backend (app.py)
    ├── /api/users          → User management
    ├── /api/jobs           → Job listings
    ├── /api/recommend      → ML recommendations
    ├── /api/recommend/gap  → Skill gap analysis
    ├── /api/resume/extract → NLP skill extraction
    └── /api/history/<id>   → Recommendation history
    │
    ├── database.py  → SQLite CRUD operations
    └── model.py     → TF-IDF + Cosine Similarity
```

---

## 3. Machine Learning Explanation

### Why TF-IDF?

TF-IDF (Term Frequency–Inverse Document Frequency) converts text into numerical vectors:

- **TF** = How often a skill appears in the text
- **IDF** = How rare that skill is across all job listings

This means:
- A skill like "Python" that appears in many jobs gets **lower weight** (less discriminative)
- A skill like "Reinforcement Learning" that appears rarely gets **higher weight** (more specific)

### Why Cosine Similarity?

Cosine similarity measures the **angle** between two vectors:
- Score = 1.0 → Perfect match
- Score = 0.0 → No overlap

It ignores vector length (a user with 3 skills vs a job needing 15 is still fairly compared).

### Configuration Choices

```python
TfidfVectorizer(
    ngram_range=(1, 2),   # Captures "machine learning" as a phrase, not just words
    min_df=1,             # Include rare skills (important for niche roles)
    sublinear_tf=True,    # Log-dampens very frequent terms
)
```

---

## 4. Database Schema

```sql
-- Users: stores job seeker profiles
CREATE TABLE users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL,
    email      TEXT    NOT NULL UNIQUE,
    skills     TEXT    NOT NULL,
    experience TEXT    NOT NULL DEFAULT 'fresher',
    created_at TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Jobs: the recommendation corpus (40 roles seeded from dataset.py)
CREATE TABLE jobs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    job_title       TEXT    NOT NULL,
    skills_required TEXT    NOT NULL,
    description     TEXT    NOT NULL
);

-- Recommendations: stores ML output per user per session
CREATE TABLE recommendations (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL REFERENCES users(id),
    job_id     INTEGER NOT NULL REFERENCES jobs(id),
    score      REAL    NOT NULL,
    created_at TEXT    NOT NULL DEFAULT (datetime('now'))
);
```

---

## 5. API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/users` | Register a new user |
| `GET`  | `/api/users/<id>` | Fetch user profile |
| `GET`  | `/api/jobs` | List all jobs (supports `?search=`, `?limit=`) |
| `POST` | `/api/recommend` | Get ML job recommendations |
| `POST` | `/api/recommend/gap` | Skill gap analysis for a specific job |
| `POST` | `/api/resume/extract` | Extract skills from resume text |
| `GET`  | `/api/history/<user_id>` | Fetch recommendation history |
| `GET`  | `/api/stats` | Database statistics |

---

## 6. Advanced Features Implemented

| Feature | Implementation |
|---------|----------------|
| ✅ Skill Gap Analysis | Set operations: matched/missing/extra skills |
| ✅ Resume Skill Extraction | Keyword NLP with 80+ tech skills vocabulary |
| ✅ Recommendation History | Saved to DB per user, queryable by user_id |
| ✅ Match % with Progress Bar | Visual score bars color-coded by fit |
| ✅ Top N Filtering | Configurable `top_n` parameter |
| ✅ Quick Skill Tags | One-click skill adding in the UI |

---

## 7. Project Structure

```
job_recommendation_system/
├── app.py          ← Flask routes + startup
├── model.py        ← TF-IDF recommender + skill gap + resume NLP
├── database.py     ← SQLite schema + CRUD operations
├── dataset.py      ← 40+ job roles custom dataset
├── seed_data.py    ← DB initializer + seeder
├── requirements.txt
├── database.db     ← Generated on first run
├── templates/
│   └── index.html  ← Full frontend SPA
├── static/
│   └── style.css   ← Design system
└── uploads/        ← Resume file uploads
```

---

## 8. How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application (DB + model init happens automatically)
python app.py

# 3. Open browser
# http://localhost:5000
```

---

## 9. Sample API Usage (curl)

```bash
# Add a user
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","email":"alice@test.com","skills":"Python, ML, SQL","experience":"2 years"}'

# Get recommendations
curl -X POST http://localhost:5000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"skills":"Python, Machine Learning, SQL, Pandas","top_n":5}'

# Skill gap analysis
curl -X POST http://localhost:5000/api/recommend/gap \
  -H "Content-Type: application/json" \
  -d '{"user_skills":"Python, SQL","job_id":1}'
```

---

## 10. Possible Improvements

1. **Better NLP**: Replace keyword extraction with a fine-tuned BERT model for skill recognition
2. **Collaborative Filtering**: Add user-user or item-item collaborative filtering alongside content-based
3. **PDF Resume Parsing**: Use `pdfplumber` or `PyMuPDF` to extract text from PDF resumes
4. **Authentication**: Add JWT-based auth with Flask-JWT-Extended
5. **PostgreSQL**: Swap SQLite for PostgreSQL for production scale
6. **Caching**: Add Redis caching for frequently requested recommendations
7. **Evaluation Metrics**: Track NDCG, Precision@K for model performance monitoring

---

*Submitted by: [Your Name]*  
*Internship Program: LearnDepth Academy — Machine Learning Track*  
*Date: March 2026*
