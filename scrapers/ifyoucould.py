import sys
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # Go up one level
import config  # Import the config file

BASE_URL = "https://www.ifyoucouldjobs.com/jobs"
MAX_PAGES = 2  # Only scrape 2 pages

def fetch_ifyoucould_jobs():
    """Scrapes job listings from If You Could Jobs using Selenium with strict keyword filtering"""
    print("🔍 Starting If You Could Jobs Scraper...")

    # Set up Chrome options
    options = Options()
    # REMOVE HEADLESS MODE FOR DEBUGGING
    options.add_argument("--headless")  # Run in background
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    print("🚀 Launching Chrome Browser...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    jobs = []

    for page in range(1, MAX_PAGES + 1):
        url = f"{BASE_URL}?page={page}"
        print(f"🌍 Navigating to {url} (Page {page})")
        driver.get(url)
        time.sleep(5)  # Wait for page to load

        # ✅ Handle Cookie Popup Only Once
        if page == 1:
            try:
                print("🍪 Checking for cookie popup...")
                cookie_button = driver.find_element(By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
                cookie_button.click()
                print("✅ Cookie popup dismissed!")
                time.sleep(2)  # Wait after clicking
            except Exception:
                print("⚠️ No cookie popup found or already dismissed.")

        print("🔍 Searching for job elements...")
        job_elements = driver.find_elements(By.CSS_SELECTOR, "article.bg-warm-grey, article.bg-light-peach")
        print(f"📌 Found {len(job_elements)} job elements on Page {page}.")

        for job in job_elements:
            try:
                # ✅ Check if title exists, otherwise skip
                title_element = job.find_elements(By.CSS_SELECTOR, "h2.type-style-3")
                if title_element:
                    title = title_element[0].text.strip()
                else:
                    print("⚠️ Skipping job due to missing title")
                    continue

                company_element = job.find_elements(By.CSS_SELECTOR, "h3.type-style-4")
                company = company_element[0].text.strip() if company_element else "Unknown"

                location_element = job.find_elements(By.XPATH, ".//dt[contains(text(), 'Location')]/following-sibling::dd")
                location = location_element[0].text.strip() if location_element else "Unknown"

                salary_element = job.find_elements(By.XPATH, ".//dt[contains(text(), 'Salary')]/following-sibling::dd")
                salary = salary_element[0].text.strip() if salary_element else "Not listed"

                # ✅ Fix: Get Full Job Link
                link_element = job.find_element(By.CSS_SELECTOR, "a.link-reset")
                relative_link = link_element.get_attribute("href")
                full_link = f"https://www.ifyoucouldjobs.com{relative_link}" if relative_link.startswith("/") else relative_link

                # ✅ Strict Filtering: Only include jobs with an **exact match** in JOB_KEYWORDS
                if any(keyword.lower() == title.lower() for keyword in config.JOB_KEYWORDS):
                    print(f"🆕 Job Matched: {title} at {company} ({location}) - {salary}")
                    print(f"🔗 Job Link: {full_link}")

                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": location,
                        "salary": salary,
                        "url": full_link  # ✅ Stores the full job URL
                    })
                else:
                    print(f"❌ Job Skipped: {title} (Does not match exact keywords)")

            except Exception as e:
                print(f"⚠️ Skipping a job due to error: {e}")
                continue  # Skip if any element is missing

    # input("🔍 Press Enter to close the browser...")  # Keeps browser open for debugging
    driver.quit()
    print(f"✅ Finished scraping. Total jobs found: {len(jobs)}")
    return jobs

# Run Scraper for Debugging
fetch_ifyoucould_jobs()