from scrapers.ifyoucould import fetch_ifyoucould_jobs
from scrapers.unjobs import fetch_unjobs
from scrapers.workable import fetch_workable_jobs
from fetch_store.store_jobs import store_jobs  

# ✅ Fetch Jobs from Scrapers
def fetch_jobs():
    """Fetch job listings from all sources and return as a dictionary."""
    print("\n⏳ Running job scrapers...")

    jobs = {
        "ifyoucould": fetch_ifyoucould_jobs(),
        "unjobs": fetch_unjobs(),
        "workable": fetch_workable_jobs(),
    }

    return jobs  # ✅ Keeps jobs in separate lists by source

# ✅ Main Function: Run Scrapers Once (Triggered by GitHub Actions)
def run_scrapers():
    jobs = fetch_jobs()

    # ✅ Send to Firestore via `store_jobs.py`
    if any(jobs.values()):  # ✅ Checks if any list has jobs
        total_jobs = sum(len(v) for v in jobs.values())
        print(f"\n💾 Sending {total_jobs} jobs to Firestore...")
        store_jobs(jobs)  # ✅ Calls `store_jobs.py`
    else:
        print("\n❌ No jobs found across all sources.")

# ✅ Run Scrapers (No Loop, GitHub Actions Handles Scheduling)
if __name__ == "__main__":
    run_scrapers()