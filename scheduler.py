import tweepy
import pandas as pd
from datetime import datetime, timedelta
import os
import pytz
import time
import random

# --- CONFIGURATION ---
# 1. Start Delay: Randomly wait 1-10 mins before starting to avoid patterns
START_MIN_DELAY = 60    
START_MAX_DELAY = 600

# 2. Inter-Tweet Delay: Wait 60-120 seconds between multiple tweets
TWEET_DELAY_MIN = 60
TWEET_DELAY_MAX = 120

# --- LOAD SECRETS ---
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")

CSV_FILE = 'posts.csv'

# --- SAFETY CHECK ---
# This ensures we don't try to connect with empty keys
if not API_KEY or not ACCESS_TOKEN:
    print("❌ Critical Error: Secrets are missing from environment.")
    print("👉 Check GitHub Settings > Secrets > Actions.")
    exit()

# --- AUTHENTICATION ---
# Using strict User Context (OAuth 1.0a) which you verified works in debug.py
client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET
)

def post_tweet(content):
    """
    Returns: 
    - "success": Posted successfully
    - "duplicate": Content was duplicate (safe to skip)
    - "ratelimit": Critical 429 error (must stop)
    - "error": Generic error
    """
    try:
        response = client.create_tweet(text=content)
        print(f"✅ Posted: {content[:40]}... (ID: {response.data['id']})")
        return "success"
    except Exception as e:
        error_msg = str(e).lower()
        
        # Case 1: Duplicate Content
        if "duplicate" in error_msg:
            print(f"⚠️ Skipped duplicate: {content[:30]}...")
            return "duplicate"
        
        # Case 2: Rate Limit (CRITICAL STOP)
        if "429" in error_msg or "too many requests" in error_msg:
            print(f"⛔ RATE LIMIT HIT (429). Stopping script immediately.")
            return "ratelimit"
            
        # Case 3: Forbidden (Auth/Permission)
        if "403" in error_msg:
            print(f"❌ 403 Forbidden: {error_msg}")
            # If this happens now, the keys are still mismatching or the app has a specific block
            return "error"

        print(f"❌ Unknown Error: {e}")
        return "error"

def check_schedule():
    # --- 1. RANDOM START DELAY ---
    delay_seconds = random.randint(START_MIN_DELAY, START_MAX_DELAY)
    print(f"🎲 Randomizing execution... Waiting {delay_seconds//60} minutes.")
    time.sleep(delay_seconds)
    print("⏰ Waking up now...")

    # --- 2. LOAD DATABASE ---
    if not os.path.exists(CSV_FILE):
        print("Error: posts.csv not found.")
        return

    try:
        df = pd.read_csv(CSV_FILE)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
    
    # --- 3. CHECK TIME (IST) ---
    utc_now = datetime.utcnow()
    ist_now = utc_now + timedelta(hours=5, minutes=30)
    print(f"🕒 Current Time (IST): {ist_now.strftime('%Y-%m-%d %H:%M')}")
    
    updated = False
    posts_made = 0

    # --- 4. PROCESS TWEETS ---
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
            
            status = post_tweet(row['content'])
            
            if status == "success":
                df.at[index, 'is_posted'] = True
                updated = True
                posts_made += 1
                
                # Safety delay before the next tweet
                wait_time = random.randint(TWEET_DELAY_MIN, TWEET_DELAY_MAX)
                print(f"⏳ Waiting {wait_time}s before next tweet...")
                time.sleep(wait_time)
            
            elif status == "duplicate":
                df.at[index, 'is_posted'] = True # Mark done so we don't retry forever
                updated = True
                time.sleep(5)
                
            elif status == "ratelimit":
                break # Stop everything
            
            elif status == "error":
                print("⚠️ Skipping this tweet due to error.")
                time.sleep(10)

    # --- 5. SAVE CHANGES ---
    if updated:
        df.to_csv(CSV_FILE, index=False)
        print(f"💾 Database updated. {posts_made} tweets processed.")
    else:
        print("💤 No tweets due right now.")

if __name__ == "__main__":
    check_schedule()
