import os
import json
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials

# Load environment variables from .env file (for local development)
load_dotenv()

# ✅ Handle Firebase Credentials (from GitHub Secrets OR .env file)
firebase_json = os.getenv("FIREBASE_CREDENTIALS_JSON")

if firebase_json:
    firebase_credentials_path = "/tmp/firebase_credentials.json"
    with open(firebase_credentials_path, "w") as f:
        f.write(firebase_json)
else:
    firebase_credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")

if not firebase_credentials_path:
    raise ValueError("❌ FIREBASE_CREDENTIALS_PATH is missing! Please set it in your .env file or GitHub Secrets.")

# ✅ Initialize Firebase
cred = credentials.Certificate(firebase_credentials_path)
firebase_admin.initialize_app(cred)

# ✅ Load Email Credentials
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
    raise ValueError("❌ EMAIL_ADDRESS or EMAIL_PASSWORD is missing! Check your .env file or GitHub Secrets.")

# ✅ SMTP details
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# ✅ Job Keywords
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

# ✅ Default Location
LOCATION = os.getenv("LOCATION", "London")

# ✅ Recipient Email
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
if not RECIPIENT_EMAIL:
    raise ValueError("❌ RECIPIENT_EMAIL is missing! Make sure it's set in your .env file or GitHub Secrets.")