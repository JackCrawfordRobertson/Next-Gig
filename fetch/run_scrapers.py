import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ✅ Correctly import the functions from respective files
# from fetch.glassdoor import fetch_glassdoor_jobs
from fetch import ifyoucould, unjobs, workable, linkedin
from store import store_jobs

def fetch_jobs():
    """Fetch job listings from all sources and return as a dictionary."""
    print("\n⏳ Running job scrapers...")

    jobs = {
        "ifyoucould": ifyoucould.fetch_ifyoucould_jobs(),
        "unjobs": unjobs.fetch_unjobs(),
        "workable": workable.fetch_workable_jobs(),
        "linkedin": linkedin.fetch_all_linkedin_jobs(),
        # "ziprecruiter": ziprecruiter.fetch_all_ziprecruiter_jobs(),  # Uncomment if needed
    }

    # # ✅ Fetch Glassdoor jobs
    # print("\n🔍 Fetching Glassdoor jobs...")
    # jobs["glassdoor"] = fetch_glassdoor_jobs()  # ✅ Calls the correct function

    return jobs  

def run_scrapers():
    """Run all scrapers and store results in Firestore."""
    jobs = fetch_jobs()

    # ✅ Send to Firestore via `store_jobs.py`
    if any(jobs.values()):  # ✅ Checks if any list has jobs
        total_jobs = sum(len(v) for v in jobs.values())
        print(f"\n💾 Sending {total_jobs} jobs to Firestore...")
        store_jobs.store_jobs(jobs)  # ✅ Calls `store_jobs.py`
    else:
        print("\n❌ No jobs found across all sources.")