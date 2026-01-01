import tweepy
import pandas as pd
from datetime import datetime, timedelta
import os
import pytz
import time
import random  # Import random for the sleep timer

# --- CONFIGURATION ---
MIN_DELAY = 60    # Minimum wait: 60 seconds (1 minute)
MAX_DELAY = 600  # Maximum wait: 600 seconds (10 minutes)

# --- LOAD SECRETS ---
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")

CSV_FILE = 'posts.csv'

# --- AUTHENTICATION ---
# Using User Context (Access Tokens) for Read/Write permission
client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET
)

# API v1.1 for Image Uploads
auth = tweepy.OAuth1UserHandler(
    API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET
)
api = tweepy.API(auth)

def post_tweet(content, image_filename=None):
    try:
        media_id = None
        if image_filename and pd.notna(image_filename):
            if os.path.exists(image_filename):
                print(f"📸 Uploading image: {image_filename}...")
                media_upload = api.media_upload(filename=image_filename)
                media_id = media_upload.media_id
            else:
                print(f"⚠️ Image '{image_filename}' not found. Posting text only.")

        if media_id:
            response = client.create_tweet(text=content, media_ids=[media_id])
        else:
            response = client.create_tweet(text=content)
            
        print(f"✅ Posted: {content[:30]}... (ID: {response.data['id']})")
        return True
    except Exception as e:
        print(f"❌ Error posting: {e}")
        return False

def check_schedule():
    # --- RANDOM DELAY START ---
    # This prevents the bot from always posting at exactly XX:00 or XX:30
    delay_seconds = random.randint(MIN_DELAY, MAX_DELAY)
    delay_minutes = delay_seconds // 60
    print(f"🎲 Randomizing execution... Waiting {delay_minutes} minutes before checking schedule.")
    
    # Pause the script here
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
    
    # Server Time to IST
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
            
            image_file = row['image_file'] if 'image_file' in row else None
            if str(image_file).lower() == 'nan' or str(image_file).strip() == '':
                image_file = None

            if post_tweet(row['content'], image_file):
                df.at[index, 'is_posted'] = True
                updated = True
                posts_made += 1
                time.sleep(2)

    if updated:
        df.to_csv(CSV_FILE, index=False)
        print(f"💾 Database updated. {posts_made} tweets posted.")
    else:
        print("💤 No tweets due right now.")

if __name__ == "__main__":
    check_schedule()
