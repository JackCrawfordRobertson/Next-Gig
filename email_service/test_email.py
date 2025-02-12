import smtplib
from email.mime.text import MIMEText
import config

def send_test_email():
    subject = "Test Email from Job Finder Bot"
    body = "Hello! This is a test email to check if the job bot email system is working."

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = config.EMAIL_ADDRESS
    msg["To"] = config.RECIPIENT_EMAIL

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.starttls()  # Upgrade to secure connection
        server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
        server.sendmail(config.EMAIL_ADDRESS, config.RECIPIENT_EMAIL, msg.as_string())
        server.quit()

        print("✅ Test email sent successfully!")

    except Exception as e:
        print("❌ Error sending test email:", e)

# Run the test
send_test_email()