import os
import hashlib
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# ✅ Load environment variables from .env file
load_dotenv()

# ✅ Get Firebase credentials path from environment variables
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH")

if not FIREBASE_CREDENTIALS_PATH:
    raise ValueError("❌ Missing FIREBASE_CREDENTIALS_PATH in environment variables. Please set it in the .env file.")

# ✅ Prevent multiple Firebase initializations
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)

# ✅ Initialize Firestore
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
def store_jobs(jobs_input):
    """
    Stores job listings in Firestore. Supports two input formats:
      1) A dictionary with scraper names as keys and job lists as values, e.g.:
         {'unjobs': [job1, job2], 'workable': [job3, job4], ...}
      2) A single list of jobs, e.g.:
         [job1, job2, job3, ...]
         This will be stored under the key "combined".
    """

    # ✅ Wrap single list inputs under 'combined'
    jobs_dict = {"combined": jobs_input} if isinstance(jobs_input, list) else jobs_input

    existing_job_ids = fetch_existing_job_ids()  # ✅ Fetch stored jobs before inserting
    stored_count = 0
    all_jobs = []  # ✅ Global list for compiled index

    for scraper_name, jobs in jobs_dict.items():
        print(f"🔍 Storing {len(jobs)} jobs from {scraper_name}...")

        for job in jobs:
            doc_id = generate_document_id(job["url"])

            if doc_id in existing_job_ids:  # ✅ Prevent duplicates
                print(f"⚠️ Job already exists: {job.get('title', 'Unknown Title')} ({scraper_name})")
                continue  

            # ✅ Store in individual scraper collection
            db.collection(f"jobs_{scraper_name}").document(doc_id).set(job, merge=True)

            # ✅ Store in compiled index
            all_jobs.append(job)
            stored_count += 1

    # ✅ Store compiled index
    for job in all_jobs:
        doc_id = generate_document_id(job["url"])
        db.collection("jobs_compiled").document(doc_id).set(job, merge=True)

    print(f"✅ {stored_count} new jobs stored in Firestore!")

# ✅ Fetch Stored Jobs (Per Scraper or All)
def fetch_stored_jobs(scraper_name=None):
    """
    Fetch stored jobs from Firestore.
    - If `scraper_name` is provided, fetch jobs only for that scraper.
    - If `scraper_name` is None, fetch all stored jobs.
    """
    collection_name = f"jobs_{scraper_name}" if scraper_name else "jobs_compiled"
    jobs_collection = db.collection(collection_name).stream()
    return [job.to_dict() for job in jobs_collection]

if __name__ == "__main__":
    print("🔍 Fetching stored jobs from Firestore...")
    stored_jobs = fetch_stored_jobs()
    print(f"✅ Found {len(stored_jobs)} stored jobs.\n")

    # Example quick test:
    print("💡 Storing a single-list test of 2 dummy jobs under 'combined'...")
    dummy_job_list = [
        {
            "title": "Dummy Engineer",
            "company": "ExampleCorp",
            "location": "Remote",
            "url": "https://dummy.examplecorp.com/job1"
        },
        {
            "title": "Dummy Designer",
            "company": "ExampleCorp",
            "location": "Remote",
            "url": "https://dummy.examplecorp.com/job2"
        }
    ]
    store_jobs(dummy_job_list)