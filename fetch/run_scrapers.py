import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ✅ Import job keywords & location from config
from config import JOB_KEYWORDS, LOCATION  

# ✅ Import scrapers
from fetch import ifyoucould, unjobs, workable, linkedin
# from fetch.glassdoor import fetch_glassdoor_jobs  # ✅ Uncomment to enable Glassdoor

def fetch_jobs():
    """Fetch job listings dynamically from all sources using job keywords and location."""
    print("\n⏳ Running job scrapers...")

    jobs = {
        "linkedin": linkedin.fetch_all_linkedin_jobs(),
        "ifyoucould": ifyoucould.fetch_ifyoucould_jobs(),
        "unjobs": unjobs.fetch_unjobs(),
        "workable": workable.fetch_workable_jobs(),
    }

    # ✅ Add Glassdoor back but keep it commented out
    # print("\n🔍 Fetching Glassdoor jobs...")
    # jobs["glassdoor"] = fetch_glassdoor_jobs(JOB_KEYWORDS, LOCATION)  # ✅ Calls the correct function

    return jobs  # ✅ Now only returning jobs, not storing them

def run_scrapers():
    """Run all scrapers and return job data."""
    return fetch_jobs()  # ✅ Now just returning jobs

if __name__ == "__main__":
    run_scrapers()