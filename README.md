Next Gig

🚀 Next Gig is an automated job listing scraper that fetches job postings from multiple sources, stores them in Google Firestore, and sends email alerts for new job postings.

Features

✅ Job listings from:
	•	If You Could
	•	UN Jobs
	•	Workable
	•	LinkedIn

✅ Stores jobs in Google Firestore
✅ Prevents duplicate job entries
✅ Sends email notifications for new jobs
✅ Runs every 8 hours via GitHub Actions

Installation & Setup

1️⃣ Clone the Repository

git clone https://github.com/JackCrawfordRobertson/Next-Gig.git

2️⃣ Set Up Virtual Environment

python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

3️⃣ Install Dependencies

pip install -r requirements.txt

4️⃣ Set Up Environment Variables

Create a .env file and add your Firebase and email credentials:

FIREBASE_CREDENTIALS='your_firebase_json_credentials'
EMAIL_ADDRESS='your_email@gmail.com'
EMAIL_PASSWORD='your_email_app_password'
SMTP_SERVER='smtp.gmail.com'
SMTP_PORT=587
RECIPIENT_EMAIL='your_recipient_email@example.com'

5️⃣ Run the Scraper Manually

python main.py

Deployment with GitHub Actions

The scraper runs every 3 hours using GitHub Actions.
To enable automation:
	1.	Ensure secrets are added in your GitHub repository:
	•	FIREBASE_CREDENTIALS
	•	EMAIL_ADDRESS
	•	EMAIL_PASSWORD
	2.	Push your changes to GitHub
	3.	Monitor logs under Actions in GitHub

Contributing

🛠 Open a pull request if you find improvements!

License

📜 MIT License
