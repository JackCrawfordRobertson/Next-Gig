import sys
import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# ✅ Ensure script finds `config.py`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config  # Import the config file

BASE_URL = "https://jobs.workable.com/search?location=London&query={query}&employment_type=full_time&day_range=30"

def fetch_workable_jobs():
    """Scrapes job listings from Workable Jobs using Selenium"""
    print("🔍 Starting Workable Jobs Scraper...")

    # Set up Chrome options
    options = Options()
    options.add_argument("--headless")  # Run in background
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    print("🚀 Launching Chrome Browser...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    jobs = []

    for keyword in config.JOB_KEYWORDS:
        query = keyword.replace(" ", "+")  # Format search query
        query_url = BASE_URL.format(query=query)  # Insert formatted query into the URL
        print(f"🌍 Navigating to {query_url} (Query: {keyword})")
        driver.get(query_url)
        time.sleep(5)  # Wait for JavaScript to load jobs

        # ✅ Handle Cookie Popup
        try:
            print("🍪 Checking for cookie popup...")
            cookie_button = driver.find_element(By.CSS_SELECTOR, "button[data-ui='cookie-consent-decline']")
            cookie_button.click()
            print("✅ Cookie popup declined!")
            time.sleep(2)  # Wait after clicking
        except Exception:
            print("⚠️ No cookie popup found or already dismissed.")

        # ✅ Click "Show More Jobs" Up to 10 Times
        max_clicks = 10
        click_count = 0

        while click_count < max_clicks:
            try:
                show_more_button = driver.find_element(By.CSS_SELECTOR, "button[data-ui='load-more-button']")
                show_more_button.click()
                click_count += 1
                print(f"🔽 Clicked 'Show More Jobs' button #{click_count}...")
                time.sleep(3)  # Allow time for new jobs to load
            except Exception:
                print("✅ No more 'Show More Jobs' button found or end of jobs reached.")
                break  # Exit loop when no button is found

        print(f"🔍 Searching for job elements after {click_count} load-more clicks...")
        job_elements = driver.find_elements(By.CSS_SELECTOR, ".jobCardDetails__job-breakdown--AnIQr")
        print(f"📌 Found {len(job_elements)} job elements for '{keyword}'.")

        for job in job_elements:
            try:
                # ✅ Extract job title
                title_element = job.find_element(By.CSS_SELECTOR, "h2[data-ui='job-card-title'] a")
                title = title_element.text.strip()

                # ✅ Extract company name
                company_element = job.find_element(By.CSS_SELECTOR, "h3[data-ui='job-card-company-label'] a")
                company = company_element.text.strip()

                # ✅ Extract full job link
                job_link = title_element.get_attribute("href")
                full_job_link = f"https://jobs.workable.com{job_link}" if job_link.startswith("/") else job_link

                # ✅ Strict Title Filtering (Ensures Job Title Matches Keywords)
                if not any(kw.lower() in title.lower() for kw in config.JOB_KEYWORDS):
                    print(f"⚠️ Skipping '{title}' - Does Not Match Exact Keyword '{keyword}'")
                    continue

                print(f"🆕 Job Found: {title} at {company}")
                print(f"🔗 Job Link: {full_job_link}")

                jobs.append({
                    "title": title,
                    "company": company,
                    "location": "London",
                    "url": full_job_link,  # ✅ Stores the full job URL
                    "date_added": datetime.utcnow().strftime("%Y-%m-%d"),  # ✅ New field
                    "has_applied": False,  # ✅ New field
                })

            except Exception as e:
                print(f"⚠️ Skipping a job due to error: {e}")
                continue  # Skip if any element is missing

    driver.quit()
    print(f"✅ Finished scraping Workable. Total jobs found: {len(jobs)}")
    return jobs

# ✅ Test Run
if __name__ == "__main__":
    fetch_workable_jobs()