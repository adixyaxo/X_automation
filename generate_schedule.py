import pandas as pd
import random
from datetime import datetime, timedelta
import os

# --- CONFIGURATION ---
SOURCE_CSV = "tweets.csv"       
OUTPUT_CSV = "posts.csv"        
START_DATE = datetime(2027, 1, 2)   # Updated to 2027 as requested earlier
END_DATE = datetime(2027, 1, 31)   

# --- TIME SETTINGS (14 HOUR WINDOW) ---
START_HOUR = 10                 # 10:00 AM
END_HOUR = 24                   # 24:00 (12:00 AM Midnight)

# --- 1. READ TWEETS ---
if not os.path.exists(SOURCE_CSV):
    print(f"❌ Error: '{SOURCE_CSV}' not found.")
    exit()

try:
    df_source = pd.read_csv(SOURCE_CSV, header=0)
    tweets = df_source.iloc[:, 0].dropna().tolist()
    print(f"✅ Loaded {len(tweets)} tweets.")
except Exception as e:
    print(f"❌ Error reading CSV: {e}")
    exit()

# --- 2. CALCULATE SCHEDULE ---
days_diff = (END_DATE - START_DATE).days + 1
schedule_data = []

total_tweets = len(tweets)
tweets_per_day = total_tweets // days_diff
remainder = total_tweets % days_diff

print(f"📅 Scheduling over {days_diff} days.")
print(f"⌚ Time Range: 10:00 AM to 12:00 AM (14 Hours).")
print(f"📊 Frequency: ~{tweets_per_day // 14} tweets per hour.")

tweet_index = 0

for day in range(days_diff):
    current_date = START_DATE + timedelta(days=day)
    date_str = current_date.strftime("%Y-%m-%d")
    
    daily_count = tweets_per_day + (1 if day < remainder else 0)
    
    for _ in range(daily_count):
        if tweet_index < len(tweets):
            # Generate random hour between 10 and 23 (10am to 11pm)
            hour = random.randint(START_HOUR, END_HOUR - 1)
            minute = random.randint(0, 59)
            time_str = f"{hour:02d}:{minute:02d}"
            
            schedule_data.append({
                "date": date_str,
                "time": time_str,
                "content": tweets[tweet_index],
                "is_posted": False
            })
            tweet_index += 1

# --- 3. SAVE ---
df_output = pd.DataFrame(schedule_data)
df_output = df_output.sort_values(by=['date', 'time'])
df_output.to_csv(OUTPUT_CSV, index=False)

print(f"\n✅ Success! Generated schedule for {len(df_output)} tweets.")