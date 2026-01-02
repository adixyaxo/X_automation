import tweepy
import pandas as pd
from datetime import datetime, timedelta
import os
import pytz
import time
import random

# --- CONFIGURATION ---
# 1. Start Delay: Wait 1-10 mins before starting (Random start time)
START_MIN_DELAY = 60    
START_MAX_DELAY = 600

# 2. Inter-Tweet Delay: Wait 60-120 seconds between tweets if multiple are due
TWEET_DELAY_MIN = 60
TWEET_DELAY_MAX = 120

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
    """
    Returns: 
    - "success": Posted successfully
    - "duplicate": Content was duplicate (safe to mark as done)
    - "ratelimit": Critical 429 error (must stop)
    - "error": Generic error (retry later)
    """
    try:
        response = client.create_tweet(text=content)
        print(f"✅ Posted: {content[:40]}... (ID: {response.data['id']})")
        return "success"
    except Exception as e:
        error_msg = str(e).lower()
        
        # Case 1: Duplicate Content (Twitter blocks identical tweets)
        if "duplicate" in error_msg:
            print(f"⚠️ Skipped duplicate: {content[:30]}...")
            return "duplicate"
        
        # Case 2: Rate Limit (429) - CRITICAL STOP
        if "429" in error_msg or "too many requests" in error_msg:
            print(f"⛔ RATE LIMIT HIT (429). Stopping script immediately.")
            return "ratelimit"
            
        # Case 3: Forbidden (403) - Usually Auth issues or Ban
        if "403" in error_msg:
            print(f"❌ 403 Forbidden (Check keys or permissions): {error_msg}")
            return "error"

        print(f"❌ Unknown Error: {e}")
        return "error"

def check_schedule():
    # --- 1. RANDOM START DELAY ---
    # This prevents the bot from running at exact times like 10:00:00
    delay_seconds = random.randint(START_MIN_DELAY, START_MAX_DELAY)
    delay_minutes = delay_seconds // 60
    print(f"🎲 Randomizing execution... Waiting {delay_minutes} minutes before checking schedule.")
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
        # Skip if already posted
        if str(row['is_posted']) == 'True':
            continue
            
        try:
            scheduled_str = f"{row['date']} {row['time']}"
            scheduled_dt = datetime.strptime(scheduled_str, "%Y-%m-%d %H:%M")
        except ValueError:
            continue

        # Check if "Due" (Scheduled Time <= Current Time)
        if scheduled_dt <= ist_now:
            print(f"🚀 Due Now: {row['time']}")
            
            status = post_tweet(row['content'])
            
            # --- HANDLE RESULTS ---
            if status == "success":
                df.at[index, 'is_posted'] = True
                updated = True
                posts_made += 1
                
                # SAFETY DELAY: Wait 1-2 minutes before posting the NEXT one
                wait_time = random.randint(TWEET_DELAY_MIN, TWEET_DELAY_MAX)
                print(f"⏳ Waiting {wait_time}s before next check to avoid spam flags...")
                time.sleep(wait_time)
            
            elif status == "duplicate":
                # Mark as posted so we don't get stuck in a loop
                df.at[index, 'is_posted'] = True
                updated = True
                time.sleep(5) # Short wait for logic errors
                
            elif status == "ratelimit":
                # Emergency Exit: Save progress and kill script
                print("🛑 Stopping loop to protect account.")
                break
            
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
