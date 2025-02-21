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
    raise ValueError("❌ Missing FIREBASE_CREDENTIALS_PATH in environment variables. "
                     "Please set it in the .env file.")

# ✅ Prevent multiple Firebase initializations
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)

# ✅ Initialize Firestore
db = firestore.client()

def generate_document_id(url):
    """
    Generates a Firestore-safe document ID from a job URL
    using an MD5 hash. This helps avoid duplicates and
    invalid characters in document IDs.
    """
    return hashlib.md5(url.encode()).hexdigest()

def fetch_existing_job_ids():
    """
    Fetches all stored job document IDs from the 'jobs_compiled' 
    collection so we can skip duplicates.
    """
    jobs_collection = db.collection("jobs_compiled").stream()
    return {job.id for job in jobs_collection}  # Store existing job IDs in a set

def store_jobs(jobs_input):
    """
    Stores job listings in Firestore. This function supports two input formats:
      1) A dictionary with scraper names as keys and job lists as values, e.g.:
         {
           'unjobs': [job1, job2], 
           'workable': [job3, job4], 
           ...
         }
      2) A single list of jobs, e.g.:
         [job1, job2, job3, ...]
         In this case, they will all be stored under the key "combined".

    Logic:
      - We fetch existing job IDs to avoid duplicates.
      - For each scraper (or "combined"), we iterate through each job:
        * Generate a unique doc_id by hashing the job URL.
        * If doc_id is new, store the job in:
          1) "jobs_{scraper_name}" collection
          2) "jobs_compiled" global collection
    """
    # ✅ If a single list of jobs is provided, wrap them under "combined"
    jobs_dict = {"combined": jobs_input} if isinstance(jobs_input, list) else jobs_input

    # ✅ Fetch existing jobs (so we can skip duplicates)
    existing_job_ids = fetch_existing_job_ids()

    stored_count = 0
    all_jobs = []  # We'll also store them in a "jobs_compiled" collection

    for scraper_name, jobs in jobs_dict.items():
        print(f"🔍 Storing {len(jobs)} jobs from '{scraper_name}'...")

        for job in jobs:
            doc_id = generate_document_id(job["url"])

            if doc_id in existing_job_ids:
                print(f"⚠️ Job already exists: {job.get('title', 'Unknown Title')} (Scraper: {scraper_name})")
                continue  # Skip duplicate

            # ✅ Store in individual scraper collection: "jobs_{scraper_name}"
            db.collection(f"jobs_{scraper_name}").document(doc_id).set(job, merge=True)

            # ✅ Also collect for "jobs_compiled"
            all_jobs.append(job)
            stored_count += 1

    # ✅ Now store everything in "jobs_compiled"
    for job in all_jobs:
        doc_id = generate_document_id(job["url"])
        db.collection("jobs_compiled").document(doc_id).set(job, merge=True)

    print(f"✅ {stored_count} new jobs stored in Firestore!")

def fetch_stored_jobs(scraper_name=None):
    """
    Fetch stored jobs from Firestore.
    - If `scraper_name` is provided, fetch jobs only for that scraper 
      (collection name = 'jobs_{scraper_name}').
    - Otherwise, fetch from 'jobs_compiled'.
    """
    collection_name = f"jobs_{scraper_name}" if scraper_name else "jobs_compiled"
    jobs_collection = db.collection(collection_name).stream()
    return [job.to_dict() for job in jobs_collection]

if __name__ == "__main__":
    # ✅ Example local test
    print("🔍 Fetching currently stored jobs from 'jobs_compiled'...")
    stored_jobs = fetch_stored_jobs()
    print(f"✅ Found {len(stored_jobs)} stored jobs.\n")

    # 🏷️ Example: Storing a single-list test of 2 dummy jobs under 'combined'
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

    print("💡 Storing a dummy job list (combined)...")
    store_jobs(dummy_job_list)