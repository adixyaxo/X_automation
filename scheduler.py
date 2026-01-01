import tweepy
import pandas as pd
from datetime import datetime, timedelta
import os
import pytz
import time
import random

# --- CONFIGURATION ---
# The bot will wait between 1 minute and 20 minutes before checking the schedule
MIN_DELAY = 60    
MAX_DELAY = 600

# --- LOAD SECRETS ---
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")

CSV_FILE = 'posts.csv'

# --- AUTHENTICATION ---
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
        # Check if the error is specifically about "Duplicate Content"
        if "duplicate" in str(e).lower():
            print(f"⚠️ Skipped duplicate: {content[:30]}...")
            return True  # We return True so the bot marks it as 'done' and moves to the next one
        
        print(f"❌ Error posting: {e}")
        return False


def check_schedule():
    # --- RANDOM DELAY START ---
    delay_seconds = random.randint(MIN_DELAY, MAX_DELAY)
    delay_minutes = delay_seconds // 60
    print(f"🎲 Randomizing execution... Waiting {delay_minutes} minutes before checking schedule.")
    
    # Pause the script here to mimic human irregularity
    time.sleep(delay_seconds)
    print("⏰ Waking up now...")
    # --------------------------

    if not os.path.exists(CSV_FILE):
        print("Error: posts.csv not found.")
        return

    try:
        df = pd.read_csv(CSV_FILE)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
    
    # Server Time (UTC) to IST
    utc_now = datetime.utcnow()
    ist_now = utc_now + timedelta(hours=5, minutes=30)
    print(f"🕒 Current Time (IST): {ist_now.strftime('%Y-%m-%d %H:%M')}")
    
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

        if scheduled_dt <= ist_now:
            print(f"🚀 Due Now: {row['time']}")
            
            if post_tweet(row['content']):
                df.at[index, 'is_posted'] = True
                updated = True
                posts_made += 1
                
                # Small safety sleep between multiple posts
                time.sleep(2)

    if updated:
        df.to_csv(CSV_FILE, index=False)
        print(f"💾 Database updated. {posts_made} tweets posted.")
    else:
        print("💤 No tweets due right now.")

if __name__ == "__main__":
    check_schedule()
