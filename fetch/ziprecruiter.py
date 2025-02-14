import time
import random
import requests
import config  # ✅ Import job keywords & location
from bs4 import BeautifulSoup

# ✅ ZipRecruiter Request Headers (Mimics a browser)
HEADERS = {
    "Host": "www.ziprecruiter.com",
    "accept": "*/*",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "accept-language": "en-US,en;q=0.9",
}

# ❌ Excluded job categories (e.g., video-related roles)
EXCLUDED_KEYWORDS = ["video", "social media"]

# ✅ Fetch all ZipRecruiter jobs (cycles through all job keywords)
def fetch_all_ziprecruiter_jobs(max_jobs=50):
    """
    Fetches ZipRecruiter job listings for all keywords in config.py.
    """
    all_jobs = []

    for keyword in config.JOB_KEYWORDS:
        print(f"\n🔍 Searching for: {keyword.strip()} in {config.LOCATION}")

        jobs = fetch_ziprecruiter_jobs(search_term=keyword.strip(), location=config.LOCATION, max_jobs=max_jobs)

        if jobs:
            print(f"✅ Found {len(jobs)} jobs for {keyword.strip()}!")
            all_jobs.extend(jobs)
        else:
            print(f"❌ No jobs found for {keyword.strip()}.")

    print(f"\n✅ Scraped {len(all_jobs)} total jobs from ZipRecruiter.")
    return all_jobs

# ✅ Fetch ZipRecruiter jobs (single keyword search)
def fetch_ziprecruiter_jobs(search_term, location, max_jobs=50):
    """
    Fetches job listings from ZipRecruiter for a specific job title.
    Filters out jobs containing unwanted keywords.
    """
    jobs = []
    start = 0  # Pagination offset
    seen_job_ids = set()

    # ✅ Correct ZipRecruiter Search URL
    url = (
        f"https://www.ziprecruiter.com/candidate/search?"
        f"search={search_term.replace(' ', '+')}&location={location.replace(' ', '+')}"
    )

    print(f"🔗 Fetching URL: {url}")  # ✅ Debugging step

    response = requests.get(url, headers=HEADERS, timeout=10)
    if response.status_code != 200:
        print(f"❌ ZipRecruiter request failed with status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    job_cards = soup.find_all("article", class_="job_result")

    if not job_cards:
        print(f"❌ No job listings found for {search_term}.")
        return []

    for job_card in job_cards:
        # ✅ Extract Job Title
        title_tag = job_card.find("a", class_="job_title")
        title = title_tag.get_text(strip=True) if title_tag else "N/A"
        job_url = title_tag["href"] if title_tag else "#"

        # ✅ Extract Company Name
        company_tag = job_card.find("div", class_="company_name")
        company_name = company_tag.get_text(strip=True) if company_tag else "N/A"

        # ✅ Extract Location
        location_tag = job_card.find("div", class_="location")
        job_location = location_tag.get_text(strip=True) if location_tag else "N/A"

        # ✅ Extract Salary (if available)
        salary_tag = job_card.find("div", class_="salary")
        salary = salary_tag.get_text(strip=True) if salary_tag else "Not Provided"

        # ✅ Generate a unique job ID
        job_id = job_url.split("/")[-1]
        if job_id in seen_job_ids:
            continue
        seen_job_ids.add(job_id)

        # ✅ FILTER OUT JOBS WITH UNWANTED KEYWORDS
        if any(word.lower() in title.lower() or word.lower() in company_name.lower() for word in EXCLUDED_KEYWORDS):
            print(f"⚠️ Skipping job: {title} at {company_name} (Filtered Out)")
            continue  # 🚨 Skip this job

        jobs.append({
            "title": title,
            "company": company_name,
            "location": job_location,
            "url": job_url,
            "salary": salary,
        })

        # ✅ Stop if max_jobs reached
        if len(jobs) >= max_jobs:
            break

    return jobs