"""
app.py — Main Flask Application (v2.0)
"""
import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import database as db
from model import recommender, analyze_skill_gap, extract_skills_from_text
from seed_data import setup

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"]      = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

def startup():
    print("[App] Running startup...")
    setup()
    db.seed_salary_data()
    jobs = db.get_all_jobs()
    recommender.fit(jobs)
    print(f"[App] Ready — {len(jobs)} jobs loaded.")

def ok(data, status=200):  return jsonify({"success": True,  **data}), status
def err(msg, status=400):  return jsonify({"success": False, "error": msg}), status

# ── Pages ─────────────────────────────────────────────────────────────────────
@app.route("/")
def index():       return render_template("index.html")

@app.route("/login")
def login_page():  return render_template("login.html")

@app.route("/logout")
def logout():      return render_template("login.html")

@app.route("/api/auth/check", methods=["POST"])
def auth_check():
    d = request.get_json() or {}
    email = d.get("email","").strip().lower()
    if not email: return err("No session.", 401)
    conn = db.get_connection()
    row = conn.execute("SELECT id,name,email,role,company FROM accounts WHERE email=?", (email,)).fetchone()
    conn.close()
    if not row: return err("Session invalid.", 401)
    return ok({"user": dict(row)})

# ── Auth ──────────────────────────────────────────────────────────────────────
@app.route("/api/auth/register", methods=["POST"])
def auth_register():
    d = request.get_json()
    for f in ["name","email","password"]:
        if not d.get(f,"").strip(): return err(f"'{f}' is required.")
    try:
        uid = db.register_account(
            name=d["name"], email=d["email"], password=d["password"],
            role=d.get("role","seeker"), company=d.get("company",""),
            skills=d.get("skills",""), experience=d.get("experience","fresher")
        )
        db.add_notification(uid, f"Welcome to AIJobMatch, {d['name']}! 🎉", "success")
        return ok({"user_id": uid, "message": f"Welcome, {d['name']}!"}, 201)
    except ValueError as e: return err(str(e))

@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    d = request.get_json()
    if not d.get("email") or not d.get("password"): return err("Email and password required.")
    account = db.login_account(d["email"], d["password"], d.get("role","seeker"))
    if not account: return err("Invalid credentials or wrong role.", 401)
    return ok({"user": account})

# ── Legacy users ──────────────────────────────────────────────────────────────
@app.route("/api/users", methods=["POST"])
def add_user():
    d = request.get_json()
    for f in ["name","email","skills","experience"]:
        if not d.get(f,"").strip(): return err(f"'{f}' required.")
    try:
        uid = db.insert_user(d["name"],d["email"],d["skills"],d["experience"])
        return ok({"user_id":uid,"message":f"User '{d['name']}' registered."},201)
    except ValueError as e: return err(str(e))

@app.route("/api/users/<int:uid>", methods=["GET"])
def get_user(uid):
    u = db.get_user_by_id(uid)
    return ok({"user":u}) if u else err("Not found.",404)

@app.route("/api/users", methods=["GET"])
def get_all_users():
    users = db.get_all_users()
    return ok({"users":users,"count":len(users)})

# ── Jobs ──────────────────────────────────────────────────────────────────────
@app.route("/api/jobs", methods=["GET"])
def get_jobs():
    jobs   = db.get_all_jobs()
    search = request.args.get("search","").lower()
    limit  = request.args.get("limit",type=int)
    if search: jobs = [j for j in jobs if search in j["job_title"].lower() or search in j["skills_required"].lower()]
    if limit:  jobs = jobs[:limit]
    return ok({"jobs":jobs,"count":len(jobs)})

# ── Employer Job Postings ─────────────────────────────────────────────────────
@app.route("/api/postings", methods=["POST"])
def create_posting():
    d = request.get_json()
    for f in ["employer_id","job_title","company","skills_required","description"]:
        if not str(d.get(f,"")).strip(): return err(f"'{f}' required.")
    jid = db.create_job_posting(
        employer_id=d["employer_id"], job_title=d["job_title"],
        company=d["company"], location=d.get("location","Remote"),
        job_type=d.get("job_type","Full-time"),
        salary_min=d.get("salary_min"), salary_max=d.get("salary_max"),
        skills_required=d["skills_required"], description=d["description"]
    )
    return ok({"job_id":jid,"message":"Job posted!"},201)

@app.route("/api/postings", methods=["GET"])
def get_postings():
    jobs = db.get_job_postings(
        search     = request.args.get("search",""),
        location   = request.args.get("location",""),
        job_type   = request.args.get("job_type",""),
        min_salary = request.args.get("min_salary",0,type=int),
    )
    return ok({"postings":jobs,"count":len(jobs)})

@app.route("/api/postings/<int:job_id>/applicants", methods=["GET"])
def get_applicants(job_id):
    return ok({"applicants":db.get_job_applicants(job_id)})

# ── Applications ──────────────────────────────────────────────────────────────
@app.route("/api/apply", methods=["POST"])
def apply():
    d = request.get_json()
    if not d.get("user_id") or not d.get("job_id"): return err("user_id and job_id required.")
    try:
        db.apply_to_job(d["user_id"],d["job_id"],d.get("cover_note",""))
        db.add_notification(d["user_id"],"Your application was submitted! ✅","success")
        return ok({"message":"Applied!"},201)
    except ValueError as e: return err(str(e))

@app.route("/api/applications/<int:user_id>", methods=["GET"])
def get_applications(user_id):
    return ok({"applications":db.get_user_applications(user_id)})

@app.route("/api/applications/<int:app_id>/status", methods=["PATCH"])
def update_status(app_id):
    status = request.get_json().get("status","")
    valid  = ["applied","reviewing","shortlisted","rejected","hired"]
    if status not in valid: return err(f"Status must be one of: {', '.join(valid)}")
    db.update_application_status(app_id,status)
    return ok({"message":f"Status → {status}"})

# ── Alerts ────────────────────────────────────────────────────────────────────
@app.route("/api/alerts", methods=["POST"])
def create_alert():
    d = request.get_json()
    if not d.get("user_id") or not d.get("keywords"): return err("user_id and keywords required.")
    aid = db.create_job_alert(d["user_id"],d["keywords"],d.get("location",""))
    db.add_notification(d["user_id"],f"Alert set for: {d['keywords']} 🔔","info")
    return ok({"alert_id":aid,"message":"Alert created!"},201)

@app.route("/api/alerts/<int:user_id>", methods=["GET"])
def get_alerts(user_id):
    return ok({"alerts":db.get_user_alerts(user_id)})

@app.route("/api/alerts/<int:alert_id>", methods=["DELETE"])
def delete_alert(alert_id):
    uid = request.args.get("user_id",type=int)
    db.delete_job_alert(alert_id,uid)
    return ok({"message":"Alert deleted."})

# ── Notifications ─────────────────────────────────────────────────────────────
@app.route("/api/notifications/<int:user_id>", methods=["GET"])
def get_notifications(user_id):
    unread_only = request.args.get("unread","false").lower()=="true"
    notes = db.get_notifications(user_id,unread_only)
    return ok({"notifications":notes,"unread_count":sum(1 for n in notes if not n["is_read"])})

@app.route("/api/notifications/<int:user_id>/read", methods=["POST"])
def mark_read(user_id):
    db.mark_notifications_read(user_id)
    return ok({"message":"Marked read."})

# ── Reviews ───────────────────────────────────────────────────────────────────
@app.route("/api/reviews", methods=["POST"])
def add_review():
    d = request.get_json()
    for f in ["user_id","company_name","rating","review_text"]:
        if not str(d.get(f,"")).strip(): return err(f"'{f}' required.")
    if not (1 <= int(d["rating"]) <= 5): return err("Rating 1–5.")
    rid = db.add_company_review(d["user_id"],d["company_name"],int(d["rating"]),d["review_text"],d.get("pros",""),d.get("cons",""))
    return ok({"review_id":rid,"message":"Review submitted!"},201)

@app.route("/api/reviews/<company_name>", methods=["GET"])
def get_reviews(company_name):
    reviews = db.get_company_reviews(company_name)
    avg = round(sum(r["rating"] for r in reviews)/len(reviews),1) if reviews else 0
    return ok({"reviews":reviews,"average_rating":avg,"count":len(reviews)})

# ── Salary ────────────────────────────────────────────────────────────────────
@app.route("/api/salary/<job_title>", methods=["GET"])
def salary_insights(job_title):
    data = db.get_salary_insights(job_title)
    if not data: return err(f"No salary data for '{job_title}'.",404)
    return ok({"salary_data":data})

# ── ML ────────────────────────────────────────────────────────────────────────
@app.route("/api/recommend", methods=["POST"])
def recommend():
    d = request.get_json()
    skills = d.get("skills","").strip()
    if not skills: return err("'skills' required.")
    top_n   = int(d.get("top_n",10))
    user_id = d.get("user_id")
    results = recommender.recommend(user_skills=skills,top_n=top_n)
    if d.get("save") and user_id:
        db.save_recommendations(user_id,[{"job_id":r["job_id"],"score":r["score"]} for r in results])
        db.add_notification(user_id,f"Found {len(results)} matches for your skills! 🎯","success")
    return ok({"recommendations":results,"count":len(results),"user_skills":skills})

@app.route("/api/recommend/gap", methods=["POST"])
def skill_gap():
    d = request.get_json()
    user_skills = d.get("user_skills","").strip()
    job_id = d.get("job_id")
    if not user_skills: return err("'user_skills' required.")
    if not job_id:      return err("'job_id' required.")
    job = db.get_job_by_id(job_id)
    if not job: return err("Job not found.",404)
    return ok({"job_title":job["job_title"],"gap_analysis":analyze_skill_gap(user_skills,job["skills_required"])})

@app.route("/api/history/<int:user_id>", methods=["GET"])
def history(user_id):
    user = db.get_user_by_id(user_id)
    if not user: return err("User not found.",404)
    return ok({"user":user,"history":db.get_recommendation_history(user_id)})

@app.route("/api/resume/extract", methods=["POST"])
def extract_resume():
    if request.is_json:
        text = request.get_json().get("text","")
    elif "resume" in request.files:
        f = request.files["resume"]
        if not f.filename.lower().endswith(".txt"): return err("Only .txt supported.")
        text = f.read().decode("utf-8",errors="ignore")
    else: return err("Provide text or upload .txt file.")
    if not text.strip(): return err("Empty text.")
    extracted = extract_skills_from_text(text)
    return ok({"extracted_skills":extracted,"skill_count":len(extracted.split(",")) if extracted else 0})

@app.route("/api/stats", methods=["GET"])
def stats():
    return ok({"stats":db.get_db_stats()})

if __name__ == "__main__":
    startup()
    app.run(debug=True, host="0.0.0.0", port=5000)
