from store.store_jobs import store_jobs, fetch_stored_jobs

def test_firestore():
    print("💾 Storing a test job in Firestore...")

    # ✅ Define a test job entry
    test_job = [
        {
            "title": "Test Engineer",
            "company": "TestCorp",
            "location": "Remote",
            "url": "https://test.example.com/job1"
        }
    ]

    # ✅ Store the test job under 'test_source'
    store_jobs({"test_source": test_job})

    print("📝 Retrieving stored test jobs from Firestore...")
    stored_jobs = fetch_stored_jobs("test_source")  # Fetch only from 'test_source'

    if stored_jobs:
        print(f"✅ {len(stored_jobs)} test job(s) found in Firestore!")
        for job in stored_jobs:
            print(f"- {job['title']} at {job['company']} ({job['location']})\n  {job['url']}")
    else:
        print("❌ No test jobs found in Firestore! Check Firestore connection and permissions.")

# ✅ Run the test
test_firestore()