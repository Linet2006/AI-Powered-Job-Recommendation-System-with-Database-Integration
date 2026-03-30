"""
seed_data.py — Database Seeder
================================
Seeds the Jobs table with the custom dataset on first run.
Safe to run multiple times (checks if data already exists).

Run manually: python seed_data.py
Also called automatically at app startup.
"""

from database import init_db, insert_job, jobs_are_seeded
from dataset import JOBS_DATA


def seed_jobs():
    """
    Seeds the jobs table if it's empty.
    Skips seeding if data already exists (idempotent).
    """
    if jobs_are_seeded():
        print("[Seed] Jobs already in DB. Skipping seed.")
        return

    print(f"[Seed] Inserting {len(JOBS_DATA)} job records...")
    for job in JOBS_DATA:
        insert_job(
            job_title=job["job_title"],
            skills_required=job["skills_required"],
            description=job["description"],
        )
    print(f"[Seed] ✓ Successfully seeded {len(JOBS_DATA)} jobs.")


def setup():
    """Full setup: initialize DB tables and seed job data."""
    init_db()
    seed_jobs()


if __name__ == "__main__":
    setup()
    print("[Seed] Database setup complete!")
