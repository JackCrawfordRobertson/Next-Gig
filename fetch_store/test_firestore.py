from fetch_store.fetch_jobs import fetch_jobs
from fetch_store.store_jobs import store_jobs, fetch_stored_jobs

def test_firestore():
    print("🔍 Fetching test jobs...")
    jobs = fetch_jobs()

    if not any(jobs.values()):  # ✅ Check if any scraper found jobs
        print("❌ No jobs found. Check your scrapers.")
        return

    total_jobs = sum(len(v) for v in jobs.values())
    print(f"✅ {total_jobs} jobs fetched!")

    print("💾 Storing jobs in Firestore...")
    store_jobs(jobs)

    print("📝 Retrieving stored jobs from Firestore...")
    stored_jobs = fetch_stored_jobs()

    print(f"✅ {len(stored_jobs)} jobs found in Firestore!")

    for job in stored_jobs[:5]:  # ✅ Display first 5 jobs
        print(f"- {job['title']} at {job['company']} ({job['location']})\n  {job['url']}")

# ✅ Run the test
test_firestore()