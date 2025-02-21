import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from Levenshtein import ratio  
import sys
import os
from urllib.parse import quote


# ✅ Ensure Python finds config.py in the root directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import config  # ✅ Now config.py will always be found

BASE_URL = "https://www.glassdoor.co.uk/Job/london-england-{query}-jobs-SRCH_IL.0,14_IC2671300_KO{start},{end}.htm?fromAge=7"


def handle_cookie_banner(driver):
    """Handles both 'Accept Cookies' and 'Reject Cookies' options."""
    try:
        print("🍪 Checking for cookie banner...")
        WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        ).click()
        print("✅ Accepted cookies.")
    except Exception:
        try:
            WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler"))
            ).click()
            print("✅ Rejected cookies.")
        except Exception:
            print("⚠️ No cookie banner found or already dismissed.")


def close_popup(driver):
    """Closes the sign-in popup if it appears."""
    try:
        print("🔓 Checking for Sign-in popup...")
        WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.CloseButton"))
        ).click()
        print("✅ Sign-in popup dismissed!")
    except Exception:
        print("⚠️ No Sign-in popup found or already dismissed.")


def load_more_jobs(driver, max_clicks=2):
    """Clicks the 'Show more jobs' button up to `max_clicks` times and closes the login popup if needed."""
    for _ in range(max_clicks):
        try:
            print("🔄 Clicking 'Show more jobs' button...")
            load_more_button = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-test='load-more']"))
            )
            driver.execute_script("arguments[0].click();", load_more_button)  # ✅ Avoids interception issues
            time.sleep(2)  # ✅ Allow time for new jobs to load

            # ✅ Handle login popup again if it appears
            close_popup(driver)

        except Exception:
            print("⚠️ 'Show more jobs' button not found or no more jobs to load.")
            break


def fetch_glassdoor_jobs():
    """Scrapes job listings from Glassdoor using Selenium with strict job title matching."""
    print("\n🔍 Starting Glassdoor Jobs Scraper...")

    # ✅ Chrome options for headless  browsing
    options = Options()
    options.add_argument("--headless")  
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")  # ✅ Large window for better rendering
    options.add_argument("--blink-settings=imagesEnabled=false")  # ✅ Disables image loading for speed
    options.add_argument("--disable-blink-features=CSSPaintAPI")  # ✅ Disables CSS styles for pure HTML loading

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    jobs = []

    for keyword in config.JOB_KEYWORDS:
        query = quote(keyword.replace(" ", "-"))  # ✅ Convert spaces to hyphens
        start = 15  # ✅ Glassdoor always starts the job title at position 15
        end = start + len(keyword)  # ✅ Dynamically calculate end position
        query_url = BASE_URL.format(query=query, start=start, end=end)

        print(f"\n🌍 Navigating to {query_url} (Query: {keyword})")
        driver.get(query_url)

        # ✅ Handle cookie banner
        handle_cookie_banner(driver)

        # ✅ Manually enter the query in the search box (ensures correct search execution)
        try:
            search_box = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
            )
            search_box.clear()
            search_box.send_keys(keyword)
            search_box.send_keys(Keys.RETURN)
            time.sleep(1.5)  # ✅ Reduced wait time
        except Exception:
            print("⚠️ Could not find the search box to manually trigger search.")

        # ✅ Close any popups
        close_popup(driver)

        # ✅ Load more jobs by clicking the button up to 2 times
        load_more_jobs(driver)

        try:
            job_cards = WebDriverWait(driver, 3).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.jobCard.JobCard_jobCardContent__JQ5Rq"))
            )
        except Exception:
            print("❌ No job listings found. Moving to next keyword.")
            continue

        print(f"📌 Found {len(job_cards)} jobs for '{keyword}'.")

        for job_card in job_cards[:10]:  # ✅ Limit results per keyword
            try:
                # Extract Job Title & URL
                title_element = job_card.find_element(By.CSS_SELECTOR, "a.JobCard_jobTitle__GLyJ1")
                title = title_element.text.strip()
                job_url = title_element.get_attribute("href")

                # ✅ Use Levenshtein distance for fuzzy matching (Threshold: 80%)
                similarity = ratio(keyword.lower(), title.lower())
                if similarity < 0.8:
                    print(f"❌ Skipping '{title}' (Similarity: {similarity:.2f}) - Not a close match to '{keyword}'.")
                    continue  # Skip this job if the title is not similar enough

                # Extract Company Name
                company_element = job_card.find_element(By.CSS_SELECTOR, "span.EmployerProfile_compactEmployerName__9MGcV")
                company = company_element.text.strip()

                # Extract Job Location
                location_element = job_card.find_element(By.CSS_SELECTOR, "div.JobCard_location__Ds1fM")
                location = location_element.text.strip()

                jobs.append({
                    "title": title,
                    "company": company,
                    "location": location,
                    "url": job_url,
                    "date_added": datetime.utcnow().strftime("%Y-%m-%d"),
                    "has_applied": False
                })

                print(f"✅ {title} at {company} ({location}) - Similarity: {similarity:.2f}")
                print(f"🔗 {job_url}")

            except Exception as e:
                print(f"⚠️ Skipping job due to error: {e}")

    driver.quit()
    print(f"✅ Finished scraping Glassdoor. Total jobs found: {len(jobs)}")
    return jobs


# ✅ Test Run
if __name__ == "__main__":
    fetch_glassdoor_jobs()