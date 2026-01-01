import tweepy
import pandas as pd
from datetime import datetime, timedelta
import os
import pytz
import time

# --- LOAD SECRETS ---
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
# Bearer token removed to prevent 403 Read-Only errors

CSV_FILE = 'posts.csv'

# --- AUTHENTICATION (User Context Only) ---
client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET
)

def post_tweet(content):
    try:
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

    try:
        df = pd.read_csv(CSV_FILE)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
    
    # Convert Server Time (UTC) to IST
    utc_now = datetime.utcnow()
    ist_now = utc_now + timedelta(hours=5, minutes=30)
    
    print(f"🕒 Current Server Time (IST): {ist_now.strftime('%Y-%m-%d %H:%M')}")
    
    updated = False
    posts_made = 0

    for index, row in df.iterrows():
        if str(row['is_posted']) == 'True':
            continue
            
        try:
            scheduled_str = f"{row['date']} {row['time']}"
            scheduled_dt = datetime.strptime(scheduled_str, "%Y-%m-%d %H:%M")
        except ValueError:
            continue

        # Check if due
        if scheduled_dt <= ist_now:
            print(f"🚀 Due Now: {row['time']} | Content: {row['content'][:30]}...")
            
            if post_tweet(row['content']):
                df.at[index, 'is_posted'] = True
                updated = True
                posts_made += 1
                time.sleep(2) # Prevent spamming

    if updated:
        df.to_csv(CSV_FILE, index=False)
        print(f"💾 Database updated. {posts_made} tweets posted.")
    else:
        print("💤 No tweets due right now.")

if __name__ == "__main__":
    check_schedule()
