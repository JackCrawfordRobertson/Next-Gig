import os
import hashlib
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ✅ Get Firebase credentials path
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH")

if not FIREBASE_CREDENTIALS_PATH:
    raise ValueError("❌ Missing FIREBASE_CREDENTIALS_PATH in environment variables. Please set it in the .env file.")

# ✅ Prevent multiple Firebase initializations
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)

# ✅ Initialize Firestore
db = firestore.client()

def generate_document_id(url):
    """Generate a Firestore-safe document ID from a job URL using MD5 hashing."""
    return hashlib.md5(url.encode()).hexdigest()

def fetch_existing_job_ids():
    """Fetches all stored job document IDs from the 'jobs_compiled' collection to skip duplicates."""
    jobs_collection = db.collection("jobs_compiled").stream()
    return {job.id for job in jobs_collection}  # Store existing job IDs in a set

def store_jobs(jobs_input):
    """Stores job listings in Firestore while avoiding duplicates."""
    # ✅ Ensure jobs are stored in a dictionary format
    jobs_dict = {"combined": jobs_input} if isinstance(jobs_input, list) else jobs_input

    # ✅ Fetch existing jobs (so we can skip duplicates)
    existing_job_ids = fetch_existing_job_ids()

    stored_count = 0
    all_jobs = []  # Collect jobs for 'jobs_compiled' collection

    for scraper_name, jobs in jobs_dict.items():
        print(f"🔍 Storing {len(jobs)} jobs from '{scraper_name}'...")

        for job in jobs:
            doc_id = generate_document_id(job["url"])

            if doc_id in existing_job_ids:
                print(f"⚠️ Job already exists: {job.get('title', 'Unknown Title')} (Scraper: {scraper_name})")
                continue  # Skip duplicate

            # ✅ Store in individual scraper collection
            db.collection(f"jobs_{scraper_name}").document(doc_id).set(job, merge=True)

            # ✅ Also store in 'jobs_compiled'
            all_jobs.append(job)
            stored_count += 1

    # ✅ Now store everything in 'jobs_compiled'
    for job in all_jobs:
        doc_id = generate_document_id(job["url"])
        db.collection("jobs_compiled").document(doc_id).set(job, merge=True)

    print(f"✅ {stored_count} new jobs stored in Firestore!")