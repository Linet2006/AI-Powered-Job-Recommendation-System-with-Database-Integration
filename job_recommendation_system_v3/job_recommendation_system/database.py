"""
database.py — Database Layer
==============================
Handles all SQLite operations: schema creation, CRUD for users,
jobs, and recommendations.

WHY SQLite?
  → Zero-config, file-based, perfect for prototyping
  → Built into Python (no install needed)
  → Easy to inspect with tools like DB Browser for SQLite
  → Can swap to PostgreSQL with minimal code change
"""

import sqlite3
import os
from datetime import datetime

# ─── Configuration ────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")


def get_connection():
    """
    Returns a new SQLite connection with row_factory set to Row.
    
    WHY row_factory = sqlite3.Row?
      → Lets us access columns by name (row["name"]) instead of index (row[0])
      → Makes code more readable and maintainable
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    conn.execute("PRAGMA foreign_keys = ON")  # Enforce FK constraints
    return conn


# ─── Schema Initialization ────────────────────────────────────────────────────

def init_db():
    """
    Creates all tables if they don't already exist.
    Called once at application startup.
    
    Schema Design Notes:
      Users     → Stores profile: name, email, skills, experience
      Jobs      → Job listings with required skills + description
      Recommendations → Many-to-many between Users and Jobs with a similarity score
    """
    conn = get_connection()
    cursor = conn.cursor()

    # ── Users Table ──────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT    NOT NULL,
            email      TEXT    NOT NULL UNIQUE,
            skills     TEXT    NOT NULL,
            experience TEXT    NOT NULL DEFAULT 'fresher',
            created_at TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # ── Jobs Table ────────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title       TEXT    NOT NULL,
            skills_required TEXT    NOT NULL,
            description     TEXT    NOT NULL
        )
    """)

    # ── Recommendations Table ─────────────────────────────────────────────────
    # Stores results each time a user runs the recommendation engine
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            job_id     INTEGER NOT NULL,
            score      REAL    NOT NULL,
            created_at TEXT    NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (job_id)  REFERENCES jobs(id)  ON DELETE CASCADE
        )
    """)

    # ── Auth / Accounts Table ──────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            name         TEXT    NOT NULL,
            email        TEXT    NOT NULL UNIQUE,
            password     TEXT    NOT NULL,
            role         TEXT    NOT NULL DEFAULT 'seeker',
            company      TEXT,
            avatar       TEXT,
            is_verified  INTEGER NOT NULL DEFAULT 0,
            created_at   TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # ── Job Postings (Employer-created) ────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_postings (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            employer_id     INTEGER NOT NULL,
            job_title       TEXT    NOT NULL,
            company         TEXT    NOT NULL,
            location        TEXT    NOT NULL DEFAULT 'Remote',
            job_type        TEXT    NOT NULL DEFAULT 'Full-time',
            salary_min      INTEGER,
            salary_max      INTEGER,
            skills_required TEXT    NOT NULL,
            description     TEXT    NOT NULL,
            is_active       INTEGER NOT NULL DEFAULT 1,
            created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (employer_id) REFERENCES accounts(id) ON DELETE CASCADE
        )
    """)

    # ── Job Applications ───────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            job_id       INTEGER NOT NULL,
            status       TEXT    NOT NULL DEFAULT 'applied',
            cover_note   TEXT,
            applied_at   TEXT    NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES accounts(id) ON DELETE CASCADE,
            UNIQUE(user_id, job_id)
        )
    """)

    # ── Job Alerts ──────────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_alerts (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            keywords   TEXT    NOT NULL,
            location   TEXT,
            created_at TEXT    NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES accounts(id) ON DELETE CASCADE
        )
    """)

    # ── Notifications ───────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            message    TEXT    NOT NULL,
            type       TEXT    NOT NULL DEFAULT 'info',
            is_read    INTEGER NOT NULL DEFAULT 0,
            created_at TEXT    NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES accounts(id) ON DELETE CASCADE
        )
    """)

    # ── Company Reviews ─────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS company_reviews (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            company_name TEXT    NOT NULL,
            rating       INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
            review_text  TEXT    NOT NULL,
            pros         TEXT,
            cons         TEXT,
            created_at   TEXT    NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES accounts(id) ON DELETE CASCADE
        )
    """)

    # ── Salary Data ─────────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS salary_data (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title  TEXT    NOT NULL,
            min_salary INTEGER NOT NULL,
            avg_salary INTEGER NOT NULL,
            max_salary INTEGER NOT NULL,
            currency   TEXT    NOT NULL DEFAULT 'INR',
            location   TEXT    NOT NULL DEFAULT 'India',
            updated_at TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()
    print("[DB] Tables initialized successfully.")


# ─── Users CRUD ───────────────────────────────────────────────────────────────

def insert_user(name: str, email: str, skills: str, experience: str) -> int:
    """
    Inserts a new user. Returns the new user's ID.
    Raises ValueError if email already exists.
    """
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO users (name, email, skills, experience) VALUES (?, ?, ?, ?)",
            (name.strip(), email.strip().lower(), skills.strip(), experience.strip())
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError(f"A user with email '{email}' already exists.")
    finally:
        conn.close()


def get_user_by_id(user_id: int) -> dict | None:
    """Fetches a single user by ID. Returns dict or None."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_email(email: str) -> dict | None:
    """Fetches a user by email address."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE email = ?", (email.strip().lower(),)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_users() -> list[dict]:
    """Returns all users as a list of dicts."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Jobs CRUD ────────────────────────────────────────────────────────────────

def insert_job(job_title: str, skills_required: str, description: str) -> int:
    """Inserts a job listing. Returns the new job's ID."""
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO jobs (job_title, skills_required, description) VALUES (?, ?, ?)",
        (job_title.strip(), skills_required.strip(), description.strip())
    )
    conn.commit()
    conn.close()
    return cursor.lastrowid


def get_all_jobs() -> list[dict]:
    """Returns all jobs as a list of dicts."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM jobs ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_job_by_id(job_id: int) -> dict | None:
    """Fetches a single job by ID."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def jobs_are_seeded() -> bool:
    """Check if jobs table already has data (to avoid duplicate seeding)."""
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    conn.close()
    return count > 0


# ─── Recommendations CRUD ─────────────────────────────────────────────────────

def save_recommendations(user_id: int, recommendations: list[dict]) -> None:
    """
    Saves a batch of recommendations for a user.
    Each recommendation = {"job_id": int, "score": float}
    """
    conn = get_connection()
    # Clear previous recommendations for this user (fresh run)
    conn.execute("DELETE FROM recommendations WHERE user_id = ?", (user_id,))
    # Insert new recommendations
    conn.executemany(
        "INSERT INTO recommendations (user_id, job_id, score) VALUES (?, ?, ?)",
        [(user_id, r["job_id"], round(r["score"], 4)) for r in recommendations]
    )
    conn.commit()
    conn.close()


def get_recommendation_history(user_id: int) -> list[dict]:
    """
    Fetches all historical recommendations for a user,
    joined with job details for display.
    """
    conn = get_connection()
    rows = conn.execute("""
        SELECT 
            r.id,
            r.score,
            r.created_at,
            j.job_title,
            j.skills_required,
            j.description,
            j.id AS job_id
        FROM recommendations r
        JOIN jobs j ON r.job_id = j.id
        WHERE r.user_id = ?
        ORDER BY r.score DESC
    """, (user_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_db_stats() -> dict:
    """Returns high-level stats about the database contents."""
    conn = get_connection()
    stats = {
        "total_users":           conn.execute("SELECT COUNT(*) FROM users").fetchone()[0],
        "total_jobs":            conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0],
        "total_recommendations": conn.execute("SELECT COUNT(*) FROM recommendations").fetchone()[0],
    }
    conn.close()
    return stats


# ─── Auth / Account CRUD ──────────────────────────────────────────────────────

def register_account(name, email, password, role="seeker", company="", skills="", experience="fresher"):
    """Register a new account. Returns account id."""
    from werkzeug.security import generate_password_hash
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO accounts (name, email, password, role, company) VALUES (?,?,?,?,?)",
            (name.strip(), email.strip().lower(),
             generate_password_hash(password), role, company.strip())
        )
        uid = cursor.lastrowid
        # Also insert into users table for ML compatibility
        if role == "seeker":
            try:
                conn.execute(
                    "INSERT INTO users (name, email, skills, experience) VALUES (?,?,?,?)",
                    (name.strip(), email.strip().lower(), skills.strip(), experience)
                )
            except Exception:
                pass
        conn.commit()
        return uid
    except sqlite3.IntegrityError:
        raise ValueError(f"Email '{email}' already registered.")
    finally:
        conn.close()


def login_account(email, password, role):
    """Verify credentials. Returns account dict or None."""
    from werkzeug.security import check_password_hash
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM accounts WHERE email=? AND role=?",
        (email.strip().lower(), role)
    ).fetchone()
    conn.close()
    if row and check_password_hash(dict(row)["password"], password):
        d = dict(row)
        d.pop("password", None)
        return d
    return None


def get_account_by_email(email):
    conn = get_connection()
    row = conn.execute("SELECT * FROM accounts WHERE email=?", (email.lower(),)).fetchone()
    conn.close()
    if row:
        d = dict(row); d.pop("password", None); return d
    return None


# ─── Job Postings (Employer) ──────────────────────────────────────────────────

def create_job_posting(employer_id, job_title, company, location, job_type,
                        salary_min, salary_max, skills_required, description):
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO job_postings
           (employer_id,job_title,company,location,job_type,salary_min,salary_max,skills_required,description)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (employer_id, job_title, company, location, job_type,
         salary_min, salary_max, skills_required, description)
    )
    conn.commit()
    conn.close()
    return cursor.lastrowid


def get_job_postings(search="", location="", job_type="", min_salary=0):
    conn = get_connection()
    query = "SELECT * FROM job_postings WHERE is_active=1"
    params = []
    if search:
        query += " AND (LOWER(job_title) LIKE ? OR LOWER(skills_required) LIKE ?)"
        params += [f"%{search.lower()}%", f"%{search.lower()}%"]
    if location:
        query += " AND LOWER(location) LIKE ?"
        params.append(f"%{location.lower()}%")
    if job_type:
        query += " AND job_type=?"
        params.append(job_type)
    if min_salary:
        query += " AND salary_max >= ?"
        params.append(min_salary)
    query += " ORDER BY created_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Applications ─────────────────────────────────────────────────────────────

def apply_to_job(user_id, job_id, cover_note=""):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO applications (user_id, job_id, cover_note) VALUES (?,?,?)",
            (user_id, job_id, cover_note)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise ValueError("Already applied to this job.")
    finally:
        conn.close()


def get_user_applications(user_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT a.*, jp.job_title, jp.company, jp.location, jp.job_type,
               jp.salary_min, jp.salary_max
        FROM applications a
        JOIN job_postings jp ON a.job_id = jp.id
        WHERE a.user_id=?
        ORDER BY a.applied_at DESC
    """, (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_job_applicants(job_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT a.*, ac.name, ac.email
        FROM applications a
        JOIN accounts ac ON a.user_id = ac.id
        WHERE a.job_id=?
        ORDER BY a.applied_at DESC
    """, (job_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_application_status(app_id, status):
    conn = get_connection()
    conn.execute("UPDATE applications SET status=? WHERE id=?", (status, app_id))
    conn.commit()
    conn.close()


# ─── Job Alerts ───────────────────────────────────────────────────────────────

def create_job_alert(user_id, keywords, location=""):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO job_alerts (user_id, keywords, location) VALUES (?,?,?)",
        (user_id, keywords, location)
    )
    conn.commit()
    conn.close()
    return cursor.lastrowid


def get_user_alerts(user_id):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM job_alerts WHERE user_id=? ORDER BY created_at DESC", (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_job_alert(alert_id, user_id):
    conn = get_connection()
    conn.execute("DELETE FROM job_alerts WHERE id=? AND user_id=?", (alert_id, user_id))
    conn.commit()
    conn.close()


# ─── Notifications ────────────────────────────────────────────────────────────

def add_notification(user_id, message, type_="info"):
    conn = get_connection()
    conn.execute(
        "INSERT INTO notifications (user_id, message, type) VALUES (?,?,?)",
        (user_id, message, type_)
    )
    conn.commit()
    conn.close()


def get_notifications(user_id, unread_only=False):
    conn = get_connection()
    q = "SELECT * FROM notifications WHERE user_id=?"
    if unread_only:
        q += " AND is_read=0"
    q += " ORDER BY created_at DESC LIMIT 20"
    rows = conn.execute(q, (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_notifications_read(user_id):
    conn = get_connection()
    conn.execute("UPDATE notifications SET is_read=1 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()


# ─── Company Reviews ──────────────────────────────────────────────────────────

def add_company_review(user_id, company_name, rating, review_text, pros="", cons=""):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO company_reviews (user_id,company_name,rating,review_text,pros,cons) VALUES (?,?,?,?,?,?)",
        (user_id, company_name, rating, review_text, pros, cons)
    )
    conn.commit()
    conn.close()
    return cursor.lastrowid


def get_company_reviews(company_name):
    conn = get_connection()
    rows = conn.execute("""
        SELECT cr.*, ac.name as reviewer_name
        FROM company_reviews cr
        JOIN accounts ac ON cr.user_id = ac.id
        WHERE LOWER(cr.company_name) LIKE ?
        ORDER BY cr.created_at DESC
    """, (f"%{company_name.lower()}%",)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Salary Data ──────────────────────────────────────────────────────────────

def get_salary_insights(job_title):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM salary_data WHERE LOWER(job_title) LIKE ?",
        (f"%{job_title.lower()}%",)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def seed_salary_data():
    """Seed realistic Indian tech salary data (LPA = Lakhs Per Annum)."""
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM salary_data").fetchone()[0]
    if count > 0:
        conn.close()
        return
    salary_records = [
        ("Data Scientist",           600000,  1200000, 2500000),
        ("Machine Learning Engineer",700000,  1400000, 3000000),
        ("Software Engineer",        500000,  1000000, 2200000),
        ("Frontend Developer",       400000,   800000, 1800000),
        ("Backend Developer",        450000,   900000, 2000000),
        ("Full Stack Developer",     500000,  1000000, 2200000),
        ("DevOps Engineer",          600000,  1200000, 2500000),
        ("Cloud Engineer",           650000,  1300000, 2800000),
        ("Data Engineer",            600000,  1200000, 2500000),
        ("NLP Engineer",             700000,  1500000, 3200000),
        ("Deep Learning Engineer",   800000,  1600000, 3500000),
        ("AI Research Scientist",    900000,  1800000, 4000000),
        ("Cybersecurity Analyst",    500000,  1000000, 2200000),
        ("Product Manager",          800000,  1600000, 3500000),
        ("Data Analyst",             350000,   700000, 1500000),
        ("Android Developer",        400000,   800000, 1800000),
        ("iOS Developer",            450000,   900000, 2000000),
        ("Flutter Developer",        400000,   800000, 1800000),
        ("MLOps Engineer",           700000,  1400000, 3000000),
        ("Blockchain Developer",     800000,  1600000, 3500000),
        ("QA Engineer",              350000,   700000, 1500000),
        ("Technical Writer",         300000,   600000, 1200000),
    ]
    conn.executemany(
        "INSERT INTO salary_data (job_title,min_salary,avg_salary,max_salary) VALUES (?,?,?,?)",
        salary_records
    )
    conn.commit()
    conn.close()
