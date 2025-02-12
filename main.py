import schedule
import time
from fetch_store.fetch_jobs import run_scrapers  
from fetch_store.store_jobs import store_jobs  

def job_cycle():
    """Fetch new jobs & store them in Firestore."""
    print("\n🔄 Fetching new jobs...")
    jobs = run_scrapers()  # ✅ Fetch all jobs
    if jobs:
        print(f"💾 Storing {sum(len(j) for j in jobs.values())} jobs in Firestore...")
        store_jobs(jobs)  # ✅ Save jobs
    else:
        print("❌ No new jobs found.")

    print("✅ Job check complete.")

# ✅ TEMPORARY: Run the job immediately for testing
if __name__ == "__main__":
    print("\n🚀 Running scraper test...")
    job_cycle()  # ✅ Runs once to verify scrapers and database storage