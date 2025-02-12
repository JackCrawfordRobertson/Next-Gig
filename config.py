import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials

# Load environment variables from the .env file
load_dotenv()

# Get the file path of the Firebase service account JSON
firebase_credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
if not firebase_credentials_path:
    raise ValueError("❌ FIREBASE_CREDENTIALS_PATH is missing! Please set it in your .env file.")

cred = credentials.Certificate(firebase_credentials_path)
firebase_admin.initialize_app(cred)


EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
    raise ValueError("❌ EMAIL_ADDRESS or EMAIL_PASSWORD is missing! Check your .env file.")

# SMTP details
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Hardcoded Job Keywords
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

# Load Location (default to London)
LOCATION = os.getenv("LOCATION", "London")

# Load the Recipient Email
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
if not RECIPIENT_EMAIL:
    raise ValueError("❌ RECIPIENT_EMAIL is missing! Make sure it's set in your .env file.")