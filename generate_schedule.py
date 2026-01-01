import pandas as pd
import random
from datetime import datetime, timedelta
import os

# --- CONFIGURATION ---
SOURCE_CSV = "tweets.csv"       # Your new source file
OUTPUT_CSV = "posts.csv"        # The file the bot actually reads
START_DATE = datetime(2026, 1, 2)  # Change year to 2027 if you strictly meant 2027
END_DATE = datetime(2026, 1, 31)   
START_HOUR = 10                 # 10:00 AM
END_HOUR = 12                   # 12:00 PM (Noon)

# --- 1. READ TWEETS FROM CSV ---
if not os.path.exists(SOURCE_CSV):
    print(f"❌ Error: Could not find '{SOURCE_CSV}'. Make sure it's in the same folder.")
    exit()

print(f"📖 Reading {SOURCE_CSV}...")

try:
    # Read the CSV. We assume the tweets are in the first column.
    # header=0 means the first row is a header ("Tweet Content")
    df_source = pd.read_csv(SOURCE_CSV, header=0)
    
    # Drop empty rows to avoid posting blanks
    tweets = df_source.iloc[:, 0].dropna().tolist()
    
    print(f"✅ Loaded {len(tweets)} tweets.")

except Exception as e:
    print(f"❌ Error reading CSV: {e}")
    exit()

# --- 2. CALCULATE SCHEDULE ---
days_diff = (END_DATE - START_DATE).days + 1
schedule_data = []

# Shuffle tweets so they aren't in strict alphabetical/row order (optional, remove if unwanted)
# random.shuffle(tweets)

total_tweets = len(tweets)
tweets_per_day = total_tweets // days_diff
remainder = total_tweets % days_diff

print(f"📅 Scheduling over {days_diff} days (Jan 2 - Jan 31).")
print(f"📊 Volume: ~{tweets_per_day} tweets per day (Every ~4 minutes).")

tweet_index = 0

for day in range(days_diff):
    current_date = START_DATE + timedelta(days=day)
    date_str = current_date.strftime("%Y-%m-%d")
    
    # Add extra tweets to earlier days if there is a remainder
    daily_count = tweets_per_day + (1 if day < remainder else 0)
    
    for _ in range(daily_count):
        if tweet_index < len(tweets):
            # Generate random time between 10:00 and 11:59
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

# --- 3. SAVE TO POSTS.CSV ---
df_output = pd.DataFrame(schedule_data)
# Sort by Date and Time so the bot executes them in order
df_output = df_output.sort_values(by=['date', 'time'])

df_output.to_csv(OUTPUT_CSV, index=False)

print(f"\n✅ Success! Generated '{OUTPUT_CSV}' with {len(df_output)} scheduled posts.")
print("👉 You can now run 'scheduler.py' (or upload to GitHub).")