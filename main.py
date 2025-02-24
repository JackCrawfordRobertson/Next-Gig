import time
from fetch.run_scrapers import run_scrapers  # ✅ Correct Import
from store.store_jobs import store_jobs  # ✅ Corrected Import

def job_cycle():
    """Fetch new jobs, store them in Firestore, and send email if new jobs exist."""
    print("\n🔄 Fetching new jobs...")
    jobs = run_scrapers()  # ✅ Now fetches jobs only, does NOT store them

    if any(jobs.values()):  # ✅ Ensure jobs exist before storing
        total_jobs = sum(len(v) for v in jobs.values())
        print(f"💾 Storing {total_jobs} jobs in Firestore...")
        store_jobs(jobs)  # ✅ Storing happens here only!
    else:
        print("❌ No new jobs found. Skipping email.")

    print("✅ Job check complete.")

if __name__ == "__main__":
    start_time = time.time()

    print("\n🚀 Running scraper test...")
    job_cycle()

    elapsed_time = time.time() - start_time
    print(f"\n🕒 Total time taken: {elapsed_time:.2f} seconds.")