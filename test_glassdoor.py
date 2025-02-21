import time
from fetch.glassdoor import fetch_glassdoor_jobs

def test_glassdoor_scraper():
    """Test function for the Glassdoor job scraper."""
    
    print("\n🔍 Running Glassdoor scraper test...")

    # ✅ Test keyword & location
    test_keyword = "Data Journalist"
    
    print(f"\n🔎 Searching for: '{test_keyword}' jobs in London...\n")
    jobs = fetch_glassdoor_jobs()

    if jobs:
        print(f"\n✅ Test Passed! Found {len(jobs)} jobs.\n")
        for job in jobs[:5]:  # ✅ Print only the first 5 jobs
            print(f"📌 {job['title']} at {job['company']} ({job['location']})")
            print(f"🔗 {job['url']}")
            print(f"💰 Salary: {job['salary']}")
            print(f"📅 Date Posted: {job['date_added']}\n")
            time.sleep(1)  # ✅ Small delay for readability
    else:
        print("\n❌ Test Failed: No jobs found.")

if __name__ == "__main__":
    test_glassdoor_scraper()