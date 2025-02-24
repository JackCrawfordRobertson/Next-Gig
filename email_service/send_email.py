import os
import hashlib
import smtplib
import firebase_admin
from firebase_admin import credentials, firestore
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from collections import defaultdict

# ✅ Load environment variables
load_dotenv()

# ✅ Get Firebase credentials path
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH")

if not FIREBASE_CREDENTIALS_PATH:
    raise ValueError("❌ Missing FIREBASE_CREDENTIALS_PATH in environment variables. Please set it in the .env file.")

# ✅ Prevent multiple Firebase initializations
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)

# ✅ Initialize Firestore
db = firestore.client()

def generate_document_id(url):
    """Generate a Firestore-safe document ID from a job URL using hashing."""
    return hashlib.md5(url.encode()).hexdigest()

def get_unsent_jobs():
    """Retrieve unsent jobs from Firestore."""
    jobs_collection = db.collection("jobs_compiled").stream()
    unsent_jobs = [job.to_dict() for job in jobs_collection if not job.to_dict().get("sent", False)]
    return unsent_jobs

def mark_jobs_as_sent(jobs):
    """Update Firestore to mark jobs as sent."""
    for job in jobs:
        doc_id = generate_document_id(job["url"])
        db.collection("jobs_compiled").document(doc_id).update({"sent": True})  # ✅ Mark as sent

def get_source_platform(url):
    """Extracts job platform based on the URL."""
    if "linkedin.com" in url:
        return "🔵 LinkedIn"
    elif "workable.com" in url:
        return "🟠 Workable"
    elif "unjobs.org" in url:
        return "🌍 UN Jobs"
    elif "ifyoucouldjobs.com" in url:
        return "🎨 If You Could"
    elif "ziprecruiter.com" in url:
        return "💼 ZipRecruiter"
    else:
        return "🌐 Other"

def send_email():
    """Send job listings via Gmail SMTP with formatted output, grouped by platform and company."""
    jobs = get_unsent_jobs()
    if not jobs:
        print("❌ No new jobs found. Skipping email.")
        return

    jobs_by_platform = defaultdict(lambda: defaultdict(list))
    for job in jobs:
        platform = get_source_platform(job["url"])
        company_name = job.get("company", "Unknown Company")
        jobs_by_platform[platform][company_name].append(job)

    job_list = ""
    for platform, companies in sorted(jobs_by_platform.items()):
        job_list += f"\n# **{platform} Jobs**\n"
        job_list += "=" * (len(platform) + 5) + "\n\n"
        for company, company_jobs in sorted(companies.items()):
            job_list += f"🟢 **{company}**\n"
            job_list += "-" * (len(company) + 8) + "\n"
            for job in company_jobs:
                job_list += f"- **{job['title']}** ({job['location']})\n"
                job_list += f"  📎 <a href='{job['url']}'>Click Here</a>\n\n"

    subject = f"🛠️ {len(jobs)} New Job Listings Found!"
    body = f"""
    <html>
    <body>
    <p>Hello,</p>
    <p>Here are the latest job listings, grouped by platform and company:</p>
    <pre style="font-family:Arial;">{job_list}</pre>
    <p>Best,<br>Your Job Scraper Bot</p>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg["From"] = os.getenv("EMAIL_ADDRESS")
    msg["To"] = os.getenv("RECIPIENT_EMAIL")
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    try:
        server = smtplib.SMTP(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT")))
        server.starttls()
        server.login(os.getenv("EMAIL_ADDRESS"), os.getenv("EMAIL_PASSWORD"))
        server.sendmail(os.getenv("EMAIL_ADDRESS"), os.getenv("RECIPIENT_EMAIL"), msg.as_string())
        server.quit()
        print("✅ Email sent successfully!")
        mark_jobs_as_sent(jobs)
    except Exception as e:
        print(f"❌ Error sending email: {e}")

if __name__ == "__main__":
    send_email()