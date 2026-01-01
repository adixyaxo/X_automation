import pandas as pd
import random
from datetime import datetime, timedelta
import os

# --- CONFIGURATION ---
SOURCE_CSV = "tweets.csv"       
OUTPUT_CSV = "posts.csv"        
START_DATE = datetime(2026, 1, 2)   # ✅ Fixed to 2026
END_DATE = datetime(2026, 1, 31)    # ✅ Fixed to 2026

# --- TIME SETTINGS (14 HOUR WINDOW) ---
START_HOUR = 10                 # 10:00 AM
END_HOUR = 24                   # 24:00 (Midnight). Range will be 10:00 to 23:59.

# --- 1. READ TWEETS ---
if not os.path.exists(SOURCE_CSV):
    print(f"❌ Error: '{SOURCE_CSV}' not found. Make sure it is in the same folder.")
    exit()

try:
    # Read the CSV. We assume tweets are in the first column.
    df_source = pd.read_csv(SOURCE_CSV, header=0)
    tweets = df_source.iloc[:, 0].dropna().tolist()
    print(f"✅ Loaded {len(tweets)} tweets from {SOURCE_CSV}.")
except Exception as e:
    print(f"❌ Error reading CSV: {e}")
    exit()

# --- 2. CALCULATE SCHEDULE ---
days_diff = (END_DATE - START_DATE).days + 1
schedule_data = []

total_tweets = len(tweets)
tweets_per_day = total_tweets // days_diff
remainder = total_tweets % days_diff

print(f"📅 Scheduling over {days_diff} days (Jan 2 - Jan 31, 2026).")
print(f"⌚ Time Range: 10:00 AM to Midnight (14 Hours).")

tweet_index = 0

for day in range(days_diff):
    current_date = START_DATE + timedelta(days=day)
    date_str = current_date.strftime("%Y-%m-%d")
    
    # Add extra tweets to earlier days if there is a remainder
    daily_count = tweets_per_day + (1 if day < remainder else 0)
    
    for _ in range(daily_count):
        if tweet_index < len(tweets):
            # Generate random hour between 10 and 23
            # randint is inclusive, so we want (10, 23)
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
# Sort to make the CSV readable
df_output = df_output.sort_values(by=['date', 'time'])
df_output.to_csv(OUTPUT_CSV, index=False)

print(f"\n✅ Success! Generated '{OUTPUT_CSV}' with {len(df_output)} scheduled posts.")
print(f"👉 Now upload '{OUTPUT_CSV}' to your GitHub repository.")