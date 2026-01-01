import tweepy
import pandas as pd
from datetime import datetime
import os
import time

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
    
    # Server time (UTC). If you want IST, we need to adjust, 
    # but usually keeping everything in Server Time is easier.
    # If your CSV is generated with "local" times, this simple comparison works
    # provided the server logic is consistent.
    
    now = datetime.now()
    updated = False
    posts_made = 0

    for index, row in df.iterrows():
        # Optimization: Skip rows already posted
        if str(row['is_posted']) == 'True':
            continue
            
        # Parse the scheduled time
        try:
            scheduled_str = f"{row['date']} {row['time']}"
            scheduled_dt = datetime.strptime(scheduled_str, "%Y-%m-%d %H:%M")
        except ValueError:
            continue

        # Logic: If time has passed AND it hasn't been posted yet
        if scheduled_dt <= now:
            
            print(f"🚀 Due Now: {row['time']} | Content: {row['content'][:30]}...")
            
            if post_tweet(row['content']):
                df.at[index, 'is_posted'] = True
                updated = True
                posts_made += 1
                
                # Safety Sleep: Don't spam the API instantly if multiple are due
                time.sleep(2) 

    if updated:
        df.to_csv(CSV_FILE, index=False)
        print(f"💾 Database updated. {posts_made} tweets posted.")
    else:
        print("💤 No tweets due right now.")

if __name__ == "__main__":
    check_schedule()