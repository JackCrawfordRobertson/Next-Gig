import smtplib
import sqlite3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import config

def get_unsent_jobs():
    """Retrieve unsent jobs from the database"""
    conn = sqlite3.connect("jobs.db")
    c = conn.cursor()
    c.execute("SELECT title, company, location, url FROM jobs WHERE sent = 0")
    jobs = c.fetchall()
    conn.close()
    return jobs

def mark_jobs_as_sent():
    """Mark jobs as sent in the database"""
    conn = sqlite3.connect("jobs.db")
    c = conn.cursor()
    c.execute("UPDATE jobs SET sent = 1 WHERE sent = 0")
    conn.commit()
    conn.close()

def send_email():
    """Send job listings via Gmail SMTP"""
    jobs = get_unsent_jobs()
    if not jobs:
        print("No new jobs to send.")
        return

    # Format email content
    job_list = "\n".join([f"- {title} at {company} ({location}): {url}" for title, company, location, url in jobs])

    subject = "New Job Listings Found"
    body = f"Here are the latest job listings:\n\n{job_list}"

    # Set up email
    msg = MIMEMultipart()
    msg["From"] = config.EMAIL_ADDRESS
    msg["To"] = config.RECIPIENT_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        # Connect to SMTP server
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.starttls()
        server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
        server.sendmail(config.EMAIL_ADDRESS, config.RECIPIENT_EMAIL, msg.as_string())
        server.quit()

        print("Email sent successfully!")
        mark_jobs_as_sent()

    except Exception as e:
        print("Error sending email:", e)