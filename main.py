import schedule
import time
from fetch_store.fetch_jobs import run_scrapers  
from fetch_store.store_jobs import store_jobs  
from email_service.send_email import send_email  

def job_cycle():
    """Fetch new jobs & store them in Firestore."""
    print("\n🔄 Fetching new jobs...")
    jobs = run_scrapers()  # ✅ Fetch all jobs
    if jobs:
        print(f"💾 Storing {sum(len(j) for j in jobs.values())} jobs in Firestore...")
        store_jobs(jobs)  # ✅ Save jobs
    else:
        print("❌ No new jobs found.")

    print("✅ Job check complete.")

# ✅ Schedule tasks
schedule.every(3).hours.do(job_cycle)  # Fetch jobs every 3 hours
schedule.every(6).hours.do(send_email)  # Send job alert emails every 6 hours

print("\n🚀 Job Finder Bot is running... (Press CTRL+C to stop)")
while True:
    schedule.run_pending()
    time.sleep(60)  # ✅ Check every minute for pending jobs