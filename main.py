# main.py
import time
from fetch import run_scrapers
from store import store_jobs  # store_jobs now references store/store_jobs.py properly

def job_cycle():
    """Fetch new jobs, store them in Firestore, and optionally send email."""
    print("\n🔄 Fetching new jobs...")
    jobs = run_scrapers()  # This function returns a dictionary of lists

    if jobs:
        total_jobs = sum(len(v) for v in jobs.values())
        print(f"💾 Storing {total_jobs} jobs in Firestore...")
        store_jobs.store_jobs(jobs)  # Must match the function name in store_jobs.py
    else:
        print("❌ No new jobs found. Skipping email.")

    print("✅ Job check complete.")

if __name__ == "__main__":
    start_time = time.time()

    print("\n🚀 Running scraper test...")
    job_cycle()

    elapsed_time = time.time() - start_time
    print(f"\n🕒 Total time taken: {elapsed_time:.2f} seconds.")