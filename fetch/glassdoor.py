import os
import json
import re
import requests
import random
import time
from datetime import datetime, timedelta

# ✅ Random User-Agents to Avoid Detection
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
]

HEADERS = {
    "authority": "www.glassdoor.com",
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "apollographql-client-name": "job-search-next",
    "apollographql-client-version": "4.65.5",
    "content-type": "application/json",
    "origin": "https://www.glassdoor.com",
    "referer": "https://www.glassdoor.com/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": random.choice(USER_AGENTS),  # ✅ Random user-agent
}

QUERY_TEMPLATE = """
query JobSearchResultsQuery(
    $keyword: String,
    $locationId: Int,
    $numJobsToShow: Int!,
    $pageNumber: Int
) {
    jobListings(
        contextHolder: {
            searchParams: {
                keyword: $keyword,
                locationId: $locationId,
                numPerPage: $numJobsToShow,
                pageNumber: $pageNumber
            }
        }
    ) {
        jobview {
            job {
                jobTitleText
                listingId
            }
            header {
                employerNameFromSearch
                locationName
                ageInDays
            }
        }
    }
}
"""

# ✅ Fallback CSRF Token (Used If Real Token Cannot Be Retrieved)
FALLBACK_TOKEN = "Ft6oHEWlRZrxDww95Cpazw:0pGUrkb2y3TyOpAIqF2vbPmUXoXVkD3oEGDVkvfeCerceQ5-n8mBg3BovySUIjmCPHCaW0H2nQVdqzbtsYqf4Q:wcqRqeegRUa9MVLJGyujVXB7vWFPjdaS1CtrrzJq-ok"

def create_session():
    """Create a session without a proxy"""
    session = requests.Session()
    session.headers.update(HEADERS)  # ✅ Apply headers globally
    return session  # 🚀 Uses your local IP

def get_csrf_token(session, retries=3):
    """Attempts to fetch CSRF token from multiple pages."""
    urls = [
        "https://www.glassdoor.com/Job/computer-science-jobs.htm",
        "https://www.glassdoor.com/Job/data-journalist-jobs.htm",
        "https://www.glassdoor.com/",
    ]
    
    for attempt in range(retries):
        for url in urls:
            try:
                time.sleep(random.uniform(3, 7))  # ✅ Random delay to avoid detection
                res = session.get(url, headers=HEADERS)
                print(f"🔍 CSRF Response Code from {url}: {res.status_code}")
                
                if res.status_code == 200:
                    match = re.search(r'"token":\s*"([^"]+)"', res.text)
                    if match:
                        token = match.group(1)
                        print(f"✅ CSRF Token Retrieved: {token[:10]}...")
                        return token
                else:
                    print(f"⚠️ Retrying CSRF Token Request ({attempt+1}/{retries})...")

            except Exception as e:
                print(f"❌ Failed to fetch CSRF token from {url} (Error: {e})")

    print("❌ No CSRF Token Found! Using fallback token.")
    return FALLBACK_TOKEN

# ✅ Step 3: Fetch a Single Job from Glassdoor
def fetch_one_job(query, session, location_id="11047"):
    """Query Glassdoor API for a single job listing."""
    api_url = "https://www.glassdoor.com/graph"
    csrf_token = get_csrf_token(session)

    if not csrf_token:
        print(f"❌ CSRF token missing, skipping {query}")
        return []

    HEADERS["gd-csrf-token"] = csrf_token  # ✅ Apply CSRF token

    payload = json.dumps([{
        "operationName": "JobSearchResultsQuery",
        "variables": {
            "keyword": query,
            "locationId": location_id,
            "numJobsToShow": 1,  # ✅ Request only 1 job for debugging
            "pageNumber": 1
        },
        "query": QUERY_TEMPLATE
    }])

    try:
        time.sleep(random.uniform(3, 7))  # ✅ Add delay before API call
        response = session.post(api_url, headers=HEADERS, data=payload)
        print(f"🔍 API Response Code: {response.status_code}")

        response.raise_for_status()  # ✅ Ensure successful API call
    except requests.RequestException as e:
        print(f"❌ API request failed for {query} (Error: {e})")
        return []

    try:
        data = response.json()[0]
        jobs_data = data.get("data", {}).get("jobListings", {}).get("jobview", [])
    except (json.JSONDecodeError, IndexError) as e:
        print(f"❌ JSON parsing failed for {query} (Error: {e})")
        return []

    # ✅ Process Job Listing
    jobs = []
    for job in jobs_data:
        job_id = job["job"]["listingId"]
        title = job["job"]["jobTitleText"]
        company = job["header"]["employerNameFromSearch"]
        location = job["header"]["locationName"]
        age_in_days = job["header"].get("ageInDays", 0)
        date_posted = (datetime.utcnow() - timedelta(days=age_in_days)).strftime("%Y-%m-%d")

        jobs.append({
            "id": job_id,
            "title": title,
            "company": company,
            "location": location,
            "date_posted": date_posted,
            "url": f"https://www.glassdoor.com/job-listing/j?jl={job_id}",
            "has_applied": False
        })

    return jobs

# ✅ Step 4: Run the Test for One Job
if __name__ == "__main__":
    print("🔍 Starting Glassdoor Jobs Scraper...")
    session = create_session()

    test_job = "Data Journalist"  # ✅ Test with only one job
    print(f"\n🌍 Searching for '{test_job}' job in London...")
    jobs = fetch_one_job(test_job, session)

    print(f"📌 Total jobs found: {len(jobs)}")
    print(jobs)  # ✅ Print for debugging