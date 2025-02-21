import time
from fetch import run_scrapers
from store import store_jobs

def job_cycle():
    """Fetch new jobs, store them in Firestore, and send an email update."""
    print("\n🔄 Fetching new jobs...")
    jobs = run_scrapers()  # Run scrapers (don't trigger send_email here)

    if jobs:
        print(f"💾 Storing {sum(len(j) for j in jobs.values())} jobs in Firestore...")
        store_jobs.store_jobs(jobs)
    else:
        print("❌ No new jobs found. Skipping email.")

    print("✅ Job check complete.")

if __name__ == "__main__":
    # ✅ Record start time
    start_time = time.time()

    print("\n🚀 Running scraper test...")
    job_cycle()  # Run the main scraping job cycle

    # ✅ Calculate elapsed time
    elapsed_time = time.time() - start_time
    print(f"\n🕒 Total time taken: {elapsed_time:.2f} seconds.")  # Print elapsed time in seconds