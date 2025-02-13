import time
import random
import requests
from bs4 import BeautifulSoup
import config  # ✅ Import job keywords & location

# ✅ LinkedIn Request Headers (mimics a browser to avoid detection)
HEADERS = {
    "authority": "www.linkedin.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

# ❌ Excluded job categories
EXCLUDED_KEYWORDS = ["video", "social media"]

# ✅ Fetch all LinkedIn jobs (cycles through all job keywords)
def fetch_all_linkedin_jobs(max_jobs=50):
    """
    Fetches LinkedIn job listings for all keywords in config.py.
    """
    all_jobs = []

    for keyword in config.JOB_KEYWORDS:
        print(f"\n🔍 Searching for: {keyword.strip()} in {config.LOCATION}")

        jobs = fetch_linkedin_jobs(search_term=keyword.strip(), location=config.LOCATION, max_jobs=max_jobs)

        if jobs:
            print(f"✅ Found {len(jobs)} jobs for {keyword.strip()}!")
            all_jobs.extend(jobs)
        else:
            print(f"❌ No jobs found for {keyword.strip()}.")

    print(f"\n✅ Scraped {len(all_jobs)} total jobs from LinkedIn.")
    return all_jobs

# ✅ Fetch LinkedIn jobs (single keyword search)
def fetch_linkedin_jobs(search_term, location, max_jobs=15):
    """
    Fetches job listings from LinkedIn for a specific job title.
    Filters out jobs containing unwanted keywords.
    """
    jobs = []
    start = 0  # LinkedIn paginates results (increments of 25)
    seen_job_ids = set()

    while len(jobs) < max_jobs and start < 1000:  # LinkedIn limits results to ~1000
        url = (
            f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?"
            f"keywords={search_term}&location={location}&start={start}"
        )

        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"❌ LinkedIn request failed with status code: {response.status_code}")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        job_cards = soup.find_all("div", class_="base-search-card")

        if not job_cards:
            print(f"❌ No job listings found for {search_term}.")
            break

        for job_card in job_cards:
            # ✅ Extract Job URL
            href_tag = job_card.find("a", class_="base-card__full-link")
            if not href_tag or "href" not in href_tag.attrs:
                continue
            job_url = href_tag["href"].split("?")[0]

            # ✅ Extract Job ID (Unique Identifier)
            job_id = job_url.split("-")[-1]
            if job_id in seen_job_ids:
                continue
            seen_job_ids.add(job_id)

            # ✅ Extract Job Title
            title_tag = job_card.find("span", class_="sr-only")
            title = title_tag.get_text(strip=True) if title_tag else "N/A"

            # ✅ Extract Company Name
            company_tag = job_card.find("h4", class_="base-search-card__subtitle")
            company_name = company_tag.get_text(strip=True) if company_tag else "N/A"

            # ✅ Extract Location
            location_tag = job_card.find("span", class_="job-search-card__location")
            location = location_tag.get_text(strip=True) if location_tag else "N/A"

            # ✅ Extract Salary (if available)
            salary_tag = job_card.find("span", class_="job-search-card__salary-info")
            salary = salary_tag.get_text(strip=True) if salary_tag else "Not Provided"

            # ✅ FILTER OUT JOBS WITH UNWANTED KEYWORDS
            if any(word.lower() in title.lower() or word.lower() in company_name.lower() for word in EXCLUDED_KEYWORDS):
                print(f"⚠️ Skipping job: {title} at {company_name} (Filtered Out)")
                continue  # 🚨 Skip this job

            jobs.append({
                "title": title,
                "company": company_name,
                "location": location,
                "url": job_url,
                "salary": salary,
            })

            # ✅ Stop if max_jobs reached
            if len(jobs) >= max_jobs:
                break

        start += 25  # ✅ FIX: Always paginate in increments of 25
        time.sleep(random.uniform(3, 6))  # ✅ Avoid detection

    return jobs