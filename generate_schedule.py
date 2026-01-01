import pandas as pd
import random
from datetime import datetime, timedelta

# --- CONFIGURATION ---
# I assumed you meant 2026 since you said "today". Change to 2027 if needed.
START_DATE = datetime(2026, 1, 2)  
END_DATE = datetime(2026, 1, 31)   
START_HOUR = 10                    # 10:00 AM
END_HOUR = 12                      # 12:00 PM

# --- PASTE YOUR 100 TWEETS BELOW ---
tweets = [
    "Most CS students are just copying code from ChatGPT. We are not the same.",
    "If you can't build a project without a tutorial in 2026, you're just a typist.",
    "C++ is the only language that matters.",
    "Building Project Sera: If your routine isn't automated, you're living in the past.",
    "A 6ft frame is wasted if you fill it with junk food. #BatmanArc",
    # ... Add the rest of your 100 strings here ...
]

# --- LOGIC ---
days_diff = (END_DATE - START_DATE).days + 1
schedule_data = []
total_tweets = len(tweets)
tweets_per_day = total_tweets // days_diff
remainder = total_tweets % days_diff

tweet_index = 0

print(f"📅 Generating schedule for {days_diff} days...")

for day in range(days_diff):
    current_date = START_DATE + timedelta(days=day)
    date_str = current_date.strftime("%Y-%m-%d")
    
    # Add extra tweets to earlier days if there is a remainder
    daily_count = tweets_per_day + (1 if day < remainder else 0)
    
    for _ in range(daily_count):
        if tweet_index < len(tweets):
            # Random time between 10:00 and 11:59
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

# Save to CSV
df = pd.DataFrame(schedule_data)
df = df.sort_values(by=['date', 'time'])
df.to_csv("posts.csv", index=False)

print(f"✅ Success! Created 'posts.csv' with {len(df)} tweets.")