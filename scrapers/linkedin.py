import time
import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
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

# ✅ Define filtering rules
EXCLUDED_KEYWORDS = ["video", "social media", "director", "senior"]  # 🚨 Now excludes senior roles
REQUIRED_LOCATIONS = ["London", "London Area"]  # 🚨 Only accept jobs in these locations

# ✅ Convert relative date ("1 week ago", "3 weeks ago") to actual date
def parse_relative_date(date_text):
    today = datetime.today()

    if "week ago" in date_text or "weeks ago" in date_text:
        weeks = int(date_text.split()[0])  # Extract number
        return today - timedelta(weeks=weeks)

    if "month ago" in date_text or "months ago" in date_text:
        months = int(date_text.split()[0])  # Extract number
        return today - timedelta(weeks=4 * months)  # Approximate month as 4 weeks

    return today  # Default: If no clear match, assume today

# ✅ Function to fetch all jobs with strict filtering
def fetch_all_linkedin_jobs(max_jobs=5, max_per_title=5):
    """
    Fetches LinkedIn job listings for all keywords in config.py.
    Limits to max_per_title per job role and max_jobs per keyword.
    """
    all_jobs = []

    for keyword in config.JOB_KEYWORDS:
        print(f"\n🔍 Searching for: {keyword.strip()} in {config.LOCATION}")

        jobs = fetch_linkedin_jobs(
            search_term=keyword.strip(),
            location=config.LOCATION,
            max_jobs=max_jobs, 
            max_per_title=max_per_title
        )

        if jobs:
            print(f"✅ Found {len(jobs)} jobs for {keyword.strip()}!")
            all_jobs.extend(jobs)
        else:
            print(f"❌ No jobs found for {keyword.strip()}.")

    print(f"\n✅ Scraped {len(all_jobs)} total jobs from LinkedIn.")
    return all_jobs

# ✅ Function to fetch LinkedIn jobs for a single keyword
def fetch_linkedin_jobs(search_term, location, max_jobs=5, max_per_title=5):
    """
    Fetches job listings from LinkedIn for a specific job title.
    Limits results to a maximum per job title and per keyword.
    Filters out jobs posted more than 14 days ago.
    """
    jobs = []
    start = 0  # LinkedIn paginates results (increments of 25)
    seen_job_ids = set()
    job_title_counts = {}  # ✅ Track count per job title

    # ✅ Get today's date & threshold for 14 days ago
    today = datetime.today()
    date_threshold = today - timedelta(days=14)

    while len(jobs) < max_jobs and start < 1000:
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
            if len(jobs) >= max_jobs:  # ✅ Stop if we already hit the keyword limit
                print(f"🚫 Stopping search for {search_term} (max {max_jobs} jobs found)")
                break

            # ✅ Extract Job URL
            href_tag = job_card.find("a", class_="base-card__full-link")
            if not href_tag or "href" not in href_tag.attrs:
                continue
            job_url = href_tag["href"].split("?")[0]

            # ✅ Extract Job ID
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
            job_location = location_tag.get_text(strip=True) if location_tag else "N/A"

            # ✅ Extract Salary (if available)
            salary_tag = job_card.find("span", class_="job-search-card__salary-info")
            salary = salary_tag.get_text(strip=True) if salary_tag else "Not Provided"

            # ✅ Extract & Validate Job Posting Date
            date_tag = job_card.find("time", class_="job-search-card__listdate")
            job_date = today  # Default to today if no date found

            if date_tag:
                if date_tag.has_attr("datetime"):  # ✅ Use ISO format date if available
                    job_date = datetime.strptime(date_tag["datetime"], "%Y-%m-%d")
                else:  # ✅ Handle "1 week ago" format
                    relative_date_text = date_tag.get_text(strip=True).lower()
                    job_date = parse_relative_date(relative_date_text)

                if job_date < date_threshold:
                    print(f"⏳ Skipping job: {title} at {company_name} (Posted {job_date.date()}, over 14 days old)")
                    continue  # 🚨 Skip old job listings

            # ✅ FILTER OUT JOBS NOT IN LONDON
            if not any(loc in job_location for loc in REQUIRED_LOCATIONS):
                print(f"⏳ Skipping job: {title} at {company_name} (Location: {job_location}, not in London)")
                continue  # 🚨 Skip job if not in London

            # ✅ FILTER OUT SENIOR ROLES (Director, Senior)
            for word in EXCLUDED_KEYWORDS:
                if word.lower() in title.lower():
                    print(f"⚠️ Skipping job: {title} at {company_name} (Filtered Out: Title contains '{word}')")
                    continue  # 🚨 Skip job

            # ✅ **LIMIT JOBS PER TITLE (Max 5 per unique title)**
            if job_title_counts.get(title, 0) >= max_per_title:
                print(f"⚠️ Skipping extra '{title}' jobs (Already found {max_per_title})")
                continue

            # ✅ Add to job list
            jobs.append({
                "title": title,
                "company": company_name,
                "location": job_location,
                "url": job_url,
                "salary": salary,
                "date_posted": job_date.strftime("%Y-%m-%d"),  # ✅ Store formatted date
            })

            # ✅ Update count for this title
            job_title_counts[title] = job_title_counts.get(title, 0) + 1

        start += 25  # ✅ Always paginate in increments of 25
        time.sleep(random.uniform(3, 6))  # ✅ Avoid detection

    return jobs