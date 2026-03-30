"""
model.py — Machine Learning Recommendation Engine
====================================================
Implements TF-IDF + Cosine Similarity for job matching.
Also includes skill gap analysis and resume text extraction.

─── WHY TF-IDF? ──────────────────────────────────────────────────────────────
  TF-IDF = Term Frequency × Inverse Document Frequency
  
  - TF  : How often a skill appears in the user's skill list
  - IDF : How rare that skill is across ALL job listings
  
  Skills that are RARE but PRESENT get higher weight.
  Skills that appear EVERYWHERE (like "Python") get balanced weight.
  
  Result: a numeric vector per job/user that captures skill importance.

─── WHY COSINE SIMILARITY? ───────────────────────────────────────────────────
  Measures the ANGLE between two vectors (not magnitude/length).
  
  Score = 1.0 → Vectors point the same direction → Perfect match
  Score = 0.0 → Vectors are orthogonal → No overlap at all
  
  It's ideal for text similarity because it ignores document length.
  A user with 3 skills vs a job needing 15 skills is still fairly compared.
"""

import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ─── Text Preprocessing ───────────────────────────────────────────────────────

def preprocess_skills(skills_text: str) -> str:
    """
    Normalizes a skill string for consistent vectorization.
    
    Steps:
      1. Lowercase everything  (Python == python)
      2. Remove punctuation
      3. Remove extra whitespace
      4. Expand common abbreviations
    
    Example:
      "Python, ML, SQL" → "python ml sql"
    """
    if not skills_text:
        return ""

    text = skills_text.lower()

    # Expand common abbreviations so they match correctly
    abbreviations = {
        r"\bml\b":    "machine learning",
        r"\bai\b":    "artificial intelligence",
        r"\bdl\b":    "deep learning",
        r"\bnlp\b":   "natural language processing",
        r"\bjs\b":    "javascript",
        r"\bts\b":    "typescript",
        r"\bk8s\b":   "kubernetes",
        r"\bdb\b":    "database",
        r"\bci/cd\b": "continuous integration continuous deployment",
        r"\bui/ux\b": "user interface user experience",
        r"\boop\b":   "object oriented programming",
        r"\bapi\b":   "application programming interface",
    }
    for pattern, replacement in abbreviations.items():
        text = re.sub(pattern, replacement, text)

    # Replace commas, slashes, dots with spaces
    text = re.sub(r"[,./\\|;:+]", " ", text)

    # Remove any remaining non-alphanumeric except spaces
    text = re.sub(r"[^a-z0-9\s]", "", text)

    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


# ─── Core Recommendation Engine ───────────────────────────────────────────────

class JobRecommender:
    """
    TF-IDF based job recommender.
    
    Flow:
      1. Fit TF-IDF on all job skill texts (learns vocabulary + IDF weights)
      2. Transform jobs into TF-IDF vectors
      3. For a query (user skills), transform to TF-IDF vector
      4. Compute cosine similarity between user vector and each job vector
      5. Rank jobs by similarity score
    """

    def __init__(self):
        """
        TfidfVectorizer config:
          - ngram_range=(1,2)  : Captures both single words AND pairs like "machine learning"
          - min_df=1           : Include skill even if it appears in only 1 job
          - sublinear_tf=True  : Apply log normalization to TF (reduces dominance of repeated terms)
          - analyzer='word'    : Tokenize at word level
        """
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=1,
            sublinear_tf=True,
            analyzer="word",
            token_pattern=r"[a-z][a-z0-9]*",
        )
        self.job_vectors = None   # Matrix of shape (n_jobs, n_features)
        self.jobs = []            # List of job dicts (from DB)
        self.is_fitted = False

    def fit(self, jobs: list[dict]) -> None:
        """
        Trains the TF-IDF model on the job corpus.
        
        Args:
            jobs: List of dicts with keys: id, job_title, skills_required, description
        
        WHY combine skills + title?
          → Adds semantic context. "Data Scientist" in the title reinforces
            the meaning of skills like Python, Statistics.
        """
        if not jobs:
            raise ValueError("Cannot fit model: job list is empty.")

        self.jobs = jobs

        # Build the text corpus: combine title + skills for each job
        # This gives the model both context AND skill keywords
        corpus = [
            preprocess_skills(f"{job['job_title']} {job['skills_required']}")
            for job in jobs
        ]

        # Fit and transform: learns IDF weights, produces sparse matrix
        self.job_vectors = self.vectorizer.fit_transform(corpus)
        self.is_fitted = True
        print(f"[Model] Fitted on {len(jobs)} jobs. Vocabulary size: {len(self.vectorizer.vocabulary_)}")

    def recommend(self, user_skills: str, top_n: int = 10) -> list[dict]:
        """
        Returns top-N job recommendations for the given user skills.
        
        Args:
            user_skills: Comma-separated or space-separated skills string
            top_n:       Number of top jobs to return
        
        Returns:
            List of dicts sorted by score (highest first):
              {job_id, job_title, skills_required, description, score, match_percent}
        
        WHY cosine_similarity on a single vector?
          → We compute similarity between 1 user vector and N job vectors
          → Returns a (1 × N) matrix; we take row 0 for the scores array
        """
        if not self.is_fitted:
            raise RuntimeError("Model not fitted. Call fit() first.")

        # Transform user skills into the same TF-IDF feature space
        processed = preprocess_skills(user_skills)
        user_vector = self.vectorizer.transform([processed])

        # Compute cosine similarity: shape (1, n_jobs)
        scores = cosine_similarity(user_vector, self.job_vectors)[0]

        # Create (index, score) pairs and sort descending
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)

        results = []
        for idx, score in ranked[:top_n]:
            if score < 0.01:  # Skip near-zero matches (irrelevant jobs)
                continue
            job = self.jobs[idx]
            results.append({
                "job_id":          job["id"],
                "job_title":       job["job_title"],
                "skills_required": job["skills_required"],
                "description":     job["description"],
                "score":           round(float(score), 4),
                "match_percent":   round(float(score) * 100, 1),
            })

        # If no match above threshold, return top-3 anyway
        if not results:
            for idx, score in ranked[:3]:
                job = self.jobs[idx]
                results.append({
                    "job_id":          job["id"],
                    "job_title":       job["job_title"],
                    "skills_required": job["skills_required"],
                    "description":     job["description"],
                    "score":           round(float(score), 4),
                    "match_percent":   round(float(score) * 100, 1),
                })

        return results


# ─── Skill Gap Analysis ───────────────────────────────────────────────────────

def analyze_skill_gap(user_skills: str, job_skills: str) -> dict:
    """
    Compares user skills to job requirements and identifies gaps.
    
    Returns:
      {
        "matched_skills":  ["Python", "SQL"],       # Skills user has
        "missing_skills":  ["Spark", "Kafka"],       # Skills user lacks
        "extra_skills":    ["Flutter"],              # User has but job doesn't need
        "match_count":     int,
        "total_required":  int,
        "coverage_percent": float
      }
    
    WHY this is valuable:
      → Helps users know exactly what to learn for a specific role
      → Actionable insight beyond just a similarity score
    """
    # Tokenize: split on spaces/commas, lowercase, strip
    def tokenize(text: str) -> set:
        tokens = re.split(r"[,\s]+", text.lower().strip())
        return {t.strip() for t in tokens if len(t) > 1}

    user_set = tokenize(user_skills)
    job_set  = tokenize(job_skills)

    matched = user_set & job_set        # Intersection
    missing = job_set  - user_set       # In job, not in user
    extra   = user_set - job_set        # In user, not in job

    coverage = (len(matched) / len(job_set) * 100) if job_set else 0.0

    # Nicely capitalize for display
    def fmt(skill_set):
        return sorted([s.title() for s in skill_set])

    return {
        "matched_skills":    fmt(matched),
        "missing_skills":    fmt(missing),
        "extra_skills":      fmt(extra),
        "match_count":       len(matched),
        "total_required":    len(job_set),
        "coverage_percent":  round(coverage, 1),
    }


# ─── Resume Skill Extraction ──────────────────────────────────────────────────

# Known tech skills vocabulary for extraction
SKILLS_VOCABULARY = {
    # Languages
    "python", "java", "javascript", "typescript", "c", "c++", "c#", "go",
    "rust", "r", "swift", "kotlin", "php", "ruby", "scala", "matlab",
    "dart", "solidity", "bash", "shell",
    # Web
    "html", "css", "react", "vue", "angular", "node", "express", "django",
    "flask", "fastapi", "nextjs", "nuxt", "jquery", "webpack",
    # Data / ML
    "pandas", "numpy", "scikit-learn", "sklearn", "tensorflow", "pytorch",
    "keras", "xgboost", "lightgbm", "matplotlib", "seaborn", "plotly",
    "tableau", "powerbi", "excel", "spss", "sas",
    # Cloud / DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "k8s", "terraform",
    "ansible", "jenkins", "git", "github", "gitlab", "ci/cd", "linux",
    "nginx", "apache",
    # Databases
    "sql", "mysql", "postgresql", "sqlite", "mongodb", "redis", "cassandra",
    "elasticsearch", "oracle", "firebase", "dynamodb",
    # Other Tech
    "machine learning", "deep learning", "nlp", "computer vision",
    "reinforcement learning", "statistics", "data analysis", "data science",
    "api", "rest", "graphql", "microservices", "agile", "scrum", "jira",
    "blockchain", "ethereum", "smart contracts", "iot", "embedded systems",
    "opencv", "bert", "transformers", "langchain", "openai", "spark",
    "kafka", "airflow", "mlflow", "mlops", "devops", "cybersecurity",
    "penetration testing", "cryptography", "networking",
}


def extract_skills_from_text(text: str) -> str:
    """
    Extracts tech skills from free-form resume text using keyword matching.
    
    Strategy:
      1. Lowercase the text
      2. Check for each known skill (sorted longest first to catch multi-word first)
      3. Return a comma-separated skill string
    
    This is a rule-based NLP approach (keyword extraction).
    For production, you'd use spaCy NER or a fine-tuned BERT model.
    
    Args:
        text: Raw resume or description text
    Returns:
        Comma-separated skills string, e.g. "Python, Machine Learning, SQL"
    """
    text_lower = text.lower()
    found = set()

    # Sort by length descending: match "machine learning" before "machine"
    sorted_vocab = sorted(SKILLS_VOCABULARY, key=len, reverse=True)

    for skill in sorted_vocab:
        # Use word boundary matching for short skills to avoid false positives
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found.add(skill.title())  # Capitalize nicely

    return ", ".join(sorted(found)) if found else ""


# ─── Singleton Model Instance ─────────────────────────────────────────────────
# We create one global recommender instance that gets fitted at app startup.
# WHY? → Fitting TF-IDF every request would be slow. Fit once, reuse everywhere.

recommender = JobRecommender()
