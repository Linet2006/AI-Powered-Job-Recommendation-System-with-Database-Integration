"""
test_system.py — Standalone Test Suite
========================================
Tests ALL components without needing the Flask server running.
Covers: DB operations, ML model, skill gap, resume extraction.

Run:  python test_system.py
"""

import os
import sys
import sqlite3
import tempfile

# ── Test Framework (no pytest needed) ────────────────────────────────────────
PASS = "✅ PASS"
FAIL = "❌ FAIL"
_results = []

def test(name, fn):
    """Run a test function and record the result."""
    try:
        fn()
        _results.append((PASS, name))
        print(f"  {PASS}  {name}")
    except AssertionError as e:
        _results.append((FAIL, name))
        print(f"  {FAIL}  {name}")
        print(f"         → {e}")
    except Exception as e:
        _results.append((FAIL, name))
        print(f"  {FAIL}  {name}")
        print(f"         → {type(e).__name__}: {e}")

def assert_eq(a, b, msg=""):
    assert a == b, f"Expected {b!r}, got {a!r}. {msg}"

def assert_true(val, msg=""):
    assert val, msg or f"Expected truthy, got {val!r}"

def assert_in(val, container, msg=""):
    assert val in container, f"{val!r} not in {container!r}. {msg}"

def assert_gt(a, b, msg=""):
    assert a > b, f"Expected {a!r} > {b!r}. {msg}"


# ════════════════════════════════════════════════════════════════════════════
# SECTION 1: Dataset Tests
# ════════════════════════════════════════════════════════════════════════════
print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print(" SECTION 1: Dataset")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

from dataset import JOBS_DATA

def test_dataset_size():
    assert_gt(len(JOBS_DATA), 20, "Dataset should have > 20 jobs")

def test_dataset_fields():
    for job in JOBS_DATA:
        assert_in("job_title",       job, "Missing job_title")
        assert_in("skills_required", job, "Missing skills_required")
        assert_in("description",     job, "Missing description")

def test_dataset_no_empty():
    for job in JOBS_DATA:
        assert_true(job["job_title"].strip(),       "Empty job_title found")
        assert_true(job["skills_required"].strip(), "Empty skills_required found")
        assert_true(job["description"].strip(),     "Empty description found")

def test_dataset_diversity():
    titles = [j["job_title"] for j in JOBS_DATA]
    # Should cover multiple domains
    assert_true(any("Data" in t for t in titles),     "No Data roles found")
    assert_true(any("ML" in t or "Machine" in t or "AI" in t for t in titles), "No ML/AI roles found")
    assert_true(any("Developer" in t or "Engineer" in t for t in titles), "No Dev/Eng roles found")

test("Dataset has 20+ job roles",            test_dataset_size)
test("All jobs have required fields",        test_dataset_fields)
test("No empty fields in dataset",           test_dataset_no_empty)
test("Dataset covers multiple domains",      test_dataset_diversity)


# ════════════════════════════════════════════════════════════════════════════
# SECTION 2: Database Tests
# ════════════════════════════════════════════════════════════════════════════
print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print(" SECTION 2: Database (isolated temp DB)")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

# Use a temp DB so tests don't pollute the real database
import database as db_module
_ORIGINAL_DB_PATH = db_module.DB_PATH
_TEMP_DB = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_TEMP_DB.close()
db_module.DB_PATH = _TEMP_DB.name  # Redirect module to temp DB

import database as db

def test_init_db():
    db.init_db()
    conn = sqlite3.connect(_TEMP_DB.name)
    tables = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}
    conn.close()
    assert_in("users",           tables)
    assert_in("jobs",            tables)
    assert_in("recommendations", tables)

def test_insert_and_get_user():
    uid = db.insert_user("Bob", "bob@test.com", "Python, SQL", "1-2 years")
    assert_true(uid > 0, "User ID should be positive")
    user = db.get_user_by_id(uid)
    assert_eq(user["name"],  "Bob")
    assert_eq(user["email"], "bob@test.com")
    assert_eq(user["skills"], "Python, SQL")

def test_duplicate_email_raises():
    db.insert_user("Carol", "carol@test.com", "Java", "fresher")
    raised = False
    try:
        db.insert_user("Carol2", "carol@test.com", "Go", "fresher")
    except ValueError:
        raised = True
    assert_true(raised, "Duplicate email should raise ValueError")

def test_get_user_by_email():
    uid = db.insert_user("Dave", "dave@test.com", "React", "fresher")
    user = db.get_user_by_email("dave@test.com")
    assert_eq(user["id"], uid)

def test_insert_and_get_jobs():
    jid = db.insert_job("Test Engineer", "Python Pytest Selenium", "Test software systems.")
    assert_true(jid > 0)
    job = db.get_job_by_id(jid)
    assert_eq(job["job_title"], "Test Engineer")

def test_get_all_jobs():
    db.insert_job("Job A", "Skill X", "Desc A")
    db.insert_job("Job B", "Skill Y", "Desc B")
    jobs = db.get_all_jobs()
    assert_gt(len(jobs), 0)

def test_save_and_get_recommendations():
    uid = db.insert_user("Eve", "eve@test.com", "Python", "fresher")
    jid1 = db.insert_job("Role 1", "Python", "Desc 1")
    jid2 = db.insert_job("Role 2", "Java",   "Desc 2")
    db.save_recommendations(uid, [
        {"job_id": jid1, "score": 0.92},
        {"job_id": jid2, "score": 0.75},
    ])
    history = db.get_recommendation_history(uid)
    assert_eq(len(history), 2)
    # Should be sorted by score descending
    assert_gt(history[0]["score"], history[1]["score"])

def test_db_stats():
    stats = db.get_db_stats()
    assert_in("total_users",           stats)
    assert_in("total_jobs",            stats)
    assert_in("total_recommendations", stats)
    assert_true(stats["total_users"] > 0)

test("init_db creates all 3 tables",              test_init_db)
test("Insert user and retrieve by ID",            test_insert_and_get_user)
test("Duplicate email raises ValueError",         test_duplicate_email_raises)
test("Get user by email",                         test_get_user_by_email)
test("Insert job and retrieve by ID",             test_insert_and_get_jobs)
test("Get all jobs returns list",                 test_get_all_jobs)
test("Save + retrieve recommendations",           test_save_and_get_recommendations)
test("DB stats returns correct keys",             test_db_stats)

# Restore original DB path
db_module.DB_PATH = _ORIGINAL_DB_PATH
os.unlink(_TEMP_DB.name)


# ════════════════════════════════════════════════════════════════════════════
# SECTION 3: ML Model Tests
# ════════════════════════════════════════════════════════════════════════════
print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print(" SECTION 3: ML Model")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

from model import JobRecommender, analyze_skill_gap, extract_skills_from_text, preprocess_skills

# Build a small synthetic corpus for testing
MOCK_JOBS = [
    {"id": 1, "job_title": "Data Scientist",
     "skills_required": "Python Machine Learning Statistics Pandas NumPy SQL TensorFlow",
     "description": "Analyze data, build models."},
    {"id": 2, "job_title": "Frontend Developer",
     "skills_required": "HTML CSS JavaScript React TypeScript Responsive Design Git",
     "description": "Build web interfaces."},
    {"id": 3, "job_title": "DevOps Engineer",
     "skills_required": "Docker Kubernetes CI/CD AWS Linux Terraform Jenkins Monitoring",
     "description": "Manage infrastructure."},
    {"id": 4, "job_title": "NLP Engineer",
     "skills_required": "Python NLP BERT Transformers Hugging Face Text Classification SpaCy",
     "description": "Build NLP systems."},
    {"id": 5, "job_title": "Android Developer",
     "skills_required": "Java Kotlin Android Studio Firebase SQLite REST API Git",
     "description": "Build Android apps."},
]

rec = JobRecommender()
rec.fit(MOCK_JOBS)

def test_recommender_fitted():
    assert_true(rec.is_fitted, "Recommender should be fitted after fit()")

def test_recommender_returns_list():
    results = rec.recommend("Python Machine Learning SQL")
    assert_true(isinstance(results, list))
    assert_true(len(results) > 0)

def test_recommender_top_n():
    results = rec.recommend("Python SQL", top_n=2)
    assert_true(len(results) <= 2, "top_n=2 should return at most 2 results")

def test_recommender_correct_ranking_ml():
    """Python + ML skills should rank Data Scientist or NLP Engineer first."""
    results = rec.recommend("Python Machine Learning Statistics Pandas NumPy")
    top_title = results[0]["job_title"]
    assert_true(
        "Data Scientist" in top_title or "NLP" in top_title,
        f"Expected ML role at top, got: {top_title}"
    )

def test_recommender_correct_ranking_frontend():
    """React + HTML skills should rank Frontend Developer first."""
    results = rec.recommend("React JavaScript HTML CSS TypeScript")
    assert_eq(results[0]["job_title"], "Frontend Developer")

def test_recommender_correct_ranking_devops():
    """Docker + Kubernetes should rank DevOps first."""
    results = rec.recommend("Docker Kubernetes AWS CI/CD Terraform")
    assert_eq(results[0]["job_title"], "DevOps Engineer")

def test_recommender_score_between_0_and_1():
    results = rec.recommend("Python SQL")
    for r in results:
        assert_true(0.0 <= r["score"] <= 1.0,
                    f"Score out of range: {r['score']}")

def test_recommender_result_fields():
    results = rec.recommend("Python")
    for r in results:
        for field in ["job_id", "job_title", "skills_required",
                      "description", "score", "match_percent"]:
            assert_in(field, r, f"Missing field: {field}")

def test_recommender_unfitted_raises():
    fresh = JobRecommender()
    raised = False
    try:
        fresh.recommend("Python")
    except RuntimeError:
        raised = True
    assert_true(raised, "Should raise RuntimeError if not fitted")

def test_recommender_empty_corpus_raises():
    fresh = JobRecommender()
    raised = False
    try:
        fresh.fit([])
    except ValueError:
        raised = True
    assert_true(raised, "Should raise ValueError on empty corpus")

def test_preprocess_expands_abbreviations():
    result = preprocess_skills("ml nlp ai")
    assert_in("machine learning", result)
    assert_in("natural language processing", result)
    assert_in("artificial intelligence", result)

def test_preprocess_handles_punctuation():
    result = preprocess_skills("Python, SQL; Docker/Kubernetes")
    assert_true("," not in result and ";" not in result and "/" not in result)

test("Recommender is fitted after fit()",           test_recommender_fitted)
test("Recommender returns list of results",         test_recommender_returns_list)
test("top_n parameter is respected",               test_recommender_top_n)
test("ML skills → Data Scientist ranks first",     test_recommender_correct_ranking_ml)
test("Web skills → Frontend Developer first",      test_recommender_correct_ranking_frontend)
test("DevOps skills → DevOps Engineer first",      test_recommender_correct_ranking_devops)
test("All scores are in [0, 1] range",             test_recommender_score_between_0_and_1)
test("Result dicts have all required fields",      test_recommender_result_fields)
test("Unfitted model raises RuntimeError",         test_recommender_unfitted_raises)
test("Empty corpus raises ValueError",             test_recommender_empty_corpus_raises)
test("Abbreviations expanded in preprocessing",    test_preprocess_expands_abbreviations)
test("Punctuation removed in preprocessing",       test_preprocess_handles_punctuation)


# ════════════════════════════════════════════════════════════════════════════
# SECTION 4: Skill Gap Analysis Tests
# ════════════════════════════════════════════════════════════════════════════
print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print(" SECTION 4: Skill Gap Analysis")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

def test_gap_matched_skills():
    gap = analyze_skill_gap("Python SQL Pandas", "Python SQL Pandas TensorFlow NumPy")
    assert_in("Python", gap["matched_skills"])
    assert_in("Sql",    gap["matched_skills"])
    assert_in("Pandas", gap["matched_skills"])

def test_gap_missing_skills():
    gap = analyze_skill_gap("Python", "Python SQL TensorFlow")
    assert_in("Sql",        gap["missing_skills"])
    assert_in("Tensorflow", gap["missing_skills"])

def test_gap_extra_skills():
    gap = analyze_skill_gap("Python React Docker", "Python SQL")
    assert_in("React",  gap["extra_skills"])
    assert_in("Docker", gap["extra_skills"])

def test_gap_coverage_100_percent():
    gap = analyze_skill_gap("Python SQL Pandas", "Python SQL Pandas")
    assert_eq(gap["coverage_percent"], 100.0)

def test_gap_coverage_0_percent():
    gap = analyze_skill_gap("Java Go Rust", "Python SQL TensorFlow")
    assert_eq(gap["coverage_percent"], 0.0)

def test_gap_coverage_partial():
    gap = analyze_skill_gap("Python SQL", "Python SQL TensorFlow NumPy")
    assert_eq(gap["coverage_percent"], 50.0)

def test_gap_match_count():
    gap = analyze_skill_gap("Python SQL Docker", "Python SQL TensorFlow")
    assert_eq(gap["match_count"], 2)

def test_gap_total_required():
    gap = analyze_skill_gap("Python", "Python SQL TensorFlow Docker")
    assert_eq(gap["total_required"], 4)

def test_gap_empty_user_skills():
    gap = analyze_skill_gap("", "Python SQL")
    assert_eq(gap["match_count"], 0)
    assert_eq(gap["coverage_percent"], 0.0)

test("Matched skills correctly identified",        test_gap_matched_skills)
test("Missing skills correctly identified",        test_gap_missing_skills)
test("Extra skills correctly identified",          test_gap_extra_skills)
test("100% coverage when all skills match",        test_gap_coverage_100_percent)
test("0% coverage when no skills match",           test_gap_coverage_0_percent)
test("Partial coverage calculated correctly",      test_gap_coverage_partial)
test("Match count is accurate",                    test_gap_match_count)
test("Total required count is accurate",           test_gap_total_required)
test("Empty user skills returns 0 matches",        test_gap_empty_user_skills)


# ════════════════════════════════════════════════════════════════════════════
# SECTION 5: Resume Skill Extraction Tests
# ════════════════════════════════════════════════════════════════════════════
print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print(" SECTION 5: Resume Skill Extraction")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

def test_extract_python():
    result = extract_skills_from_text("I have 3 years experience with Python and Django.")
    assert_in("Python", result)

def test_extract_multiple():
    result = extract_skills_from_text(
        "Skilled in Python, TensorFlow, Docker, and AWS cloud infrastructure."
    )
    assert_in("Python",     result)
    assert_in("Tensorflow", result)
    assert_in("Docker",     result)
    assert_in("Aws",        result)

def test_extract_case_insensitive():
    result = extract_skills_from_text("I used PYTHON and REACT and docker")
    assert_in("Python", result)
    assert_in("React",  result)
    assert_in("Docker", result)

def test_extract_multiword_skills():
    result = extract_skills_from_text(
        "Experience with machine learning and deep learning techniques."
    )
    assert_in("Machine Learning", result)
    assert_in("Deep Learning",    result)

def test_extract_empty_returns_empty():
    result = extract_skills_from_text("")
    assert_eq(result, "")

def test_extract_no_tech_skills():
    result = extract_skills_from_text(
        "I love cooking, hiking, and playing the guitar on weekends."
    )
    assert_eq(result, "", "Non-tech text should return empty string")

def test_extract_returns_string():
    result = extract_skills_from_text("Python developer")
    assert_true(isinstance(result, str))

test("Extracts single skill (Python)",             test_extract_python)
test("Extracts multiple skills",                   test_extract_multiple)
test("Case-insensitive extraction",                test_extract_case_insensitive)
test("Extracts multi-word skills",                 test_extract_multiword_skills)
test("Empty text returns empty string",            test_extract_empty_returns_empty)
test("Non-tech text returns empty",                test_extract_no_tech_skills)
test("Always returns a string",                    test_extract_returns_string)


# ════════════════════════════════════════════════════════════════════════════
# SECTION 6: End-to-End Integration Test
# ════════════════════════════════════════════════════════════════════════════
print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print(" SECTION 6: End-to-End Integration")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

from seed_data import setup

def test_e2e_full_pipeline():
    """
    Simulates the complete user journey:
    1. Init DB & seed jobs
    2. Register a user
    3. Run ML recommendations
    4. Perform skill gap analysis on top job
    5. Save recommendations to DB
    6. Retrieve recommendation history
    """
    # Setup
    setup()
    all_jobs = db.get_all_jobs()
    assert_gt(len(all_jobs), 10, "Should have seeded jobs")

    # Fresh recommender on real dataset
    r = JobRecommender()
    r.fit(all_jobs)

    # Register user (use fresh email for idempotency)
    import random
    uid = db.insert_user(
        f"Test User", f"testuser_{random.randint(10000,99999)}@test.com",
        "Python Machine Learning SQL Pandas TensorFlow", "2 years"
    )
    assert_true(uid > 0)

    # Get recommendations
    results = r.recommend("Python Machine Learning SQL Pandas TensorFlow", top_n=5)
    assert_gt(len(results), 0)

    # Top result should be ML-adjacent
    top = results[0]
    assert_in("match_percent", top)
    assert_true(top["match_percent"] > 0)

    # Skill gap on top job
    gap = analyze_skill_gap(
        "Python Machine Learning SQL Pandas TensorFlow",
        top["skills_required"]
    )
    assert_true(gap["coverage_percent"] >= 0)

    # Save to DB
    db.save_recommendations(uid, [{"job_id": r["job_id"], "score": r["score"]} for r in results])

    # Retrieve history
    history = db.get_recommendation_history(uid)
    assert_eq(len(history), len(results))

def test_e2e_resume_to_recommendation():
    """
    Simulates: paste resume → extract skills → run recommendations
    """
    resume = """
    Senior software engineer with expertise in Python and Flask.
    Deployed machine learning models using TensorFlow and Docker.
    Worked with PostgreSQL and Redis. AWS certified.
    """
    extracted = extract_skills_from_text(resume)
    assert_true(len(extracted) > 0, "Should extract skills from resume")

    # Use extracted skills for recommendations
    all_jobs = db.get_all_jobs()
    r = JobRecommender()
    r.fit(all_jobs)
    results = r.recommend(extracted, top_n=5)
    assert_gt(len(results), 0)
    # Machine learning / backend roles should feature prominently
    titles = [res["job_title"] for res in results]
    assert_true(
        any("Engineer" in t or "Developer" in t or "Scientist" in t for t in titles),
        f"Expected engineering roles in results: {titles}"
    )

test("Full pipeline: register → recommend → save → history", test_e2e_full_pipeline)
test("Resume → extract → recommend pipeline",                test_e2e_resume_to_recommendation)


# ════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ════════════════════════════════════════════════════════════════════════════
total  = len(_results)
passed = sum(1 for r in _results if r[0] == PASS)
failed = total - passed

print("\n" + "═" * 50)
print(f"  RESULTS:  {passed}/{total} passed  |  {failed} failed")
print("═" * 50)

if failed > 0:
    print("\nFailed tests:")
    for status, name in _results:
        if status == FAIL:
            print(f"  {FAIL} {name}")

sys.exit(0 if failed == 0 else 1)
