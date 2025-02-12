import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import firebase_admin
from firebase_admin import credentials, firestore
import hashlib
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) 
import config


# ✅ Initialize Firestore (If Not Already Initialized)
if not firebase_admin._apps:
    cred = credentials.Certificate(config.FIREBASE_CREDENTIALS)
    firebase_admin.initialize_app(cred)
db = firestore.client()

# ✅ Helper Function: Generate Firestore Document ID
def generate_document_id(url):
    """Generate a Firestore-safe document ID from a job URL using hashing."""
    return hashlib.md5(url.encode()).hexdigest()

# ✅ Fetch New Jobs (Unsynced)
def get_unsent_jobs():
    """Retrieve unsent jobs from Firestore."""
    jobs_collection = db.collection("jobs_compiled").stream()
    unsent_jobs = []

    for job in jobs_collection:
        job_data = job.to_dict()
        if not job_data.get("sent", False):  # ✅ Only fetch jobs that haven't been marked as sent
            unsent_jobs.append(job_data)

    return unsent_jobs

# ✅ Mark Jobs as Sent
def mark_jobs_as_sent(jobs):
    """Update Firestore to mark jobs as sent."""
    for job in jobs:
        doc_id = generate_document_id(job["url"])
        job_ref = db.collection("jobs_compiled").document(doc_id)
        job_ref.update({"sent": True})  # ✅ Mark as sent in Firestore

# ✅ Send Email
def send_email():
    """Send job listings via Gmail SMTP with formatted output."""
    jobs = get_unsent_jobs()

    if not jobs:
        print("❌ No new jobs to send.")
        return

    # ✅ Format Email Content
    job_list = "\n".join([
        f"🆕 NEW! {job['title']} at {job['company']} ({job['location']})\n   🔗 {job['url']}\n"
        for job in jobs
    ])

    subject = f"🛠️ {len(jobs)} New Job Listings Found!"
    body = f"Hello,\n\nHere are the latest job listings:\n\n{job_list}\n\nBest,\nJob Scraper Bot"

    # ✅ Set up email
    msg = MIMEMultipart()
    msg["From"] = config.EMAIL_ADDRESS
    msg["To"] = config.RECIPIENT_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        # ✅ Connect to SMTP server
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.starttls()
        server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
        server.sendmail(config.EMAIL_ADDRESS, config.RECIPIENT_EMAIL, msg.as_string())
        server.quit()

        print("✅ Email sent successfully!")
        mark_jobs_as_sent(jobs)  # ✅ Mark jobs as sent after successful email

    except Exception as e:
        print("❌ Error sending email:", e)

# ✅ Run Email Test (Only when running this file directly)
if __name__ == "__main__":
    send_email()