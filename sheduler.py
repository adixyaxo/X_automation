import tweepy
import pandas as pd
from datetime import datetime
import os

# --- LOAD SECRETS (From GitHub Actions) ---
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

CSV_FILE = 'posts.csv'

# --- AUTHENTICATION ---
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET
)

def post_tweet(content):
    try:
        # Posting via API v2
        response = client.create_tweet(text=content)
        print(f"✅ Posted: {content[:40]}... (ID: {response.data['id']})")
        return True
    except Exception as e:
        print(f"❌ Error posting: {e}")
        return False

def check_schedule():
    if not os.path.exists(CSV_FILE):
        print("Error: posts.csv not found.")
        return

    df = pd.read_csv(CSV_FILE)
    
    # Get current time (UTC is standard on servers, so we adjust logic or use server time)
    # GitHub servers are UTC. India is UTC+5:30. 
    # To keep it simple, we will assume the dates/times in CSV are meant to be 'Server Time' 
    # OR we just check if "Scheduled Time <= Now".
    
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    
    updated = False

    for index, row in df.iterrows():
        # Combine date and time
        scheduled_str = f"{row['date']} {row['time']}"
        try:
            scheduled_dt = datetime.strptime(scheduled_str, "%Y-%m-%d %H:%M")
        except ValueError:
            continue

        # Logic: If time has passed AND it hasn't been posted yet
        if scheduled_dt <= now and str(row['is_posted']) == 'False':
            
            print(f"🚀 Found due tweet: {row['time']}")
            
            if post_tweet(row['content']):
                df.at[index, 'is_posted'] = True
                updated = True

    if updated:
        df.to_csv(CSV_FILE, index=False)
        print("💾 Database updated.")
    else:
        print("💤 No tweets due.")

if __name__ == "__main__":
    check_schedule()