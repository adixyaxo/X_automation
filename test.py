import tweepy
import os

# --- LOAD SECRETS ---
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")

print("--- DEBUGGING CONNECTION ---")

# Check if keys are loaded
if not API_KEY or not ACCESS_TOKEN:
    print("❌ ERROR: Secrets are empty. Check GitHub 'Secrets' settings.")
    exit()
else:
    print("✅ Secrets loaded from environment.")

# Attempt 1: Check User Details (Read Test)
try:
    client = tweepy.Client(
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_SECRET
    )
    me = client.get_me()
    print(f"✅ LOGIN SUCCESSFUL! Logged in as: @{me.data.username}")
except Exception as e:
    print(f"❌ LOGIN FAILED: {e}")
    exit()

# Attempt 2: Check Write Permissions (Write Test)
# We will try to create a tweet. If it fails with 403, your keys are Read-Only.
try:
    print("Attempting to post a test tweet...")
    response = client.create_tweet(text="System check: Write permissions active. 🤖")
    print(f"✅ WRITE SUCCESSFUL! Tweet ID: {response.data['id']}")
    # Optional: Delete it immediately so it doesn't clutter your feed
    client.delete_tweet(response.data['id'])
    print("✅ (Test tweet deleted)")
except Exception as e:
    print(f"❌ WRITE FAILED: {e}")
    print("⚠️ DIAGNOSIS: If Login worked but Write failed, your keys are READ-ONLY.")
    print("👉 ACTION: Go to Dev Portal > Settings. Add 'http://127.0.0.1' as Callback URI. Save. REGENERATE Keys.")