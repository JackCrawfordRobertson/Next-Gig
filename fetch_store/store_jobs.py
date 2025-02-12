import firebase_admin
from firebase_admin import credentials, firestore
import hashlib
import config

# ✅ Initialize Firestore
cred = credentials.Certificate(config.FIREBASE_CREDENTIALS)
firebase_admin.initialize_app(cred)
db = firestore.client()

# ✅ Helper Function: Generate Firestore Document ID
def generate_document_id(url):
    """Generate a Firestore-safe document ID from a job URL using hashing."""
    return hashlib.md5(url.encode()).hexdigest()

# ✅ Fetch Existing Job IDs from Firestore
def fetch_existing_job_ids():
    """Fetch all stored job IDs to prevent duplicates."""
    jobs_collection = db.collection("jobs_compiled").stream()
    return {job.id for job in jobs_collection}  # ✅ Store existing job IDs in a set (faster lookups)

# ✅ Store Jobs in Firestore (Per Scraper & All Jobs Index)
def store_jobs(jobs_dict):
    """
    Stores job listings in Firestore, grouped by scraper source.
    - `jobs_dict` should be a dictionary with scraper names as keys and job lists as values.
    - Example: {'unjobs': [job1, job2], 'workable': [job3, job4], ...}
    """
    existing_job_ids = fetch_existing_job_ids()  # ✅ Fetch stored jobs before inserting
    stored_count = 0
    all_jobs = []  # ✅ Global list for compiled index

    for scraper_name, jobs in jobs_dict.items():
        print(f"🔍 Storing {len(jobs)} jobs from {scraper_name}...")

        for job in jobs:
            doc_id = generate_document_id(job["url"])

            if doc_id in existing_job_ids:  # ✅ Prevent duplicates
                print(f"⚠️ Job already exists: {job['title']} ({scraper_name})")
                continue  

            # ✅ Store in individual scraper collection
            job_ref = db.collection(f"jobs_{scraper_name}").document(doc_id)
            job_ref.set(job, merge=True)

            # ✅ Store in compiled index
            all_jobs.append(job)
            stored_count += 1

    # ✅ Store compiled index
    for job in all_jobs:
        doc_id = generate_document_id(job["url"])
        compiled_ref = db.collection("jobs_compiled").document(doc_id)
        compiled_ref.set(job, merge=True)

    print(f"✅ {stored_count} new jobs stored in Firestore!")

# ✅ Fetch Stored Jobs (Per Scraper or All)
def fetch_stored_jobs(scraper_name=None):
    """
    Fetch stored jobs from Firestore.
    - If `scraper_name` is provided, fetch jobs only for that scraper.
    - If `scraper_name` is None, fetch all stored jobs.
    """
    if scraper_name:
        jobs_collection = db.collection(f"jobs_{scraper_name}").stream()
    else:
        jobs_collection = db.collection("jobs_compiled").stream()  # Fetch all

    return [job.to_dict() for job in jobs_collection]

if __name__ == "__main__":
    print("🔍 Fetching stored jobs from Firestore...")
    stored_jobs = fetch_stored_jobs()
    print(f"✅ Found {len(stored_jobs)} stored jobs.")