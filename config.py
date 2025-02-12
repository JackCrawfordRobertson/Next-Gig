import os
import json

# ✅ Load Firebase Credentials from GitHub Secrets
FIREBASE_CREDENTIALS = json.loads(os.getenv("FIREBASE_CREDENTIALS"))

# ✅ Load Email Credentials from GitHub Secrets
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# ✅ Keep Job Keywords Hardcoded
JOB_KEYWORDS = [
    "Data Journalist",
    "Product Designer",
    "Data Visualisation",
    "Creative Strategist",
    "Digital Strategist",
    "Information Designer",
    "Service Designer",
    "Design Consultant",
    "Junior Front End Developer",
    "Junior Developer"
]

# ✅ Load Location from Environment Variable (Default to London)
LOCATION = os.getenv("LOCATION", "London")

# ✅ Recipient Email
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")