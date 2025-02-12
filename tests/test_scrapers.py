from scrapers.ifyoucould import fetch_ifyoucould_jobs
from scrapers.unjobs import fetch_unjobs
from scrapers.workable import fetch_workable_jobs
from fetch_store.store_jobs import store_jobs

def test_all_scrapers():
    all_jobs = []

    print("\n🟢 Testing If You Could Scraper...")
    ifyoucould_jobs = fetch_ifyoucould_jobs()
    print(f"✅ {len(ifyoucould_jobs)} jobs found.")
    all_jobs.extend(ifyoucould_jobs)

    print("\n🟢 Testing UN Jobs Scraper...")
    unjobs_jobs = fetch_unjobs()
    print(f"✅ {len(unjobs_jobs)} jobs found.")
    all_jobs.extend(unjobs_jobs)

    print("\n🟢 Testing Workable Scraper...")
    workable_jobs = fetch_workable_jobs()
    print(f"✅ {len(workable_jobs)} jobs found.")
    all_jobs.extend(workable_jobs)

    # Store jobs in Firestore
    if all_jobs:
        print(f"\n💾 Storing {len(all_jobs)} total jobs in Firestore...")
        store_jobs(all_jobs)
    else:
        print("\n❌ No jobs found across all sources.")

# Run the test
if __name__ == "__main__":
    test_all_scrapers()