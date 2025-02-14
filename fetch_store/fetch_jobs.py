from fetch.ifyoucould import fetch_ifyoucould_jobs
from fetch.unjobs import fetch_unjobs
from fetch.workable import fetch_workable_jobs
from fetch.linkedin import fetch_all_linkedin_jobs  
# from scrapers.ziprecruiter import fetch_all_ziprecruiter_jobs
from fetch_store.store_jobs import store_jobs  

def fetch_jobs():
    """Fetch job listings from all sources and return as a dictionary."""
    print("\n⏳ Running job scrapers...")

    jobs = {
        "ifyoucould": fetch_ifyoucould_jobs(),
        "unjobs": fetch_unjobs(),
        "workable": fetch_workable_jobs(),
        "linkedin": fetch_all_linkedin_jobs(), 
        # "ziprecruiter": fetch_all_ziprecruiter_jobs(),

    }

    return jobs  

def run_scrapers():
    jobs = fetch_jobs()

    # ✅ Send to Firestore via `store_jobs.py`
    if any(jobs.values()):  # ✅ Checks if any list has jobs
        total_jobs = sum(len(v) for v in jobs.values())
        print(f"\n💾 Sending {total_jobs} jobs to Firestore...")
        store_jobs(jobs)  # ✅ Calls `store_jobs.py`
    else:
        print("\n❌ No jobs found across all sources.")

if __name__ == "__main__":
    run_scrapers()