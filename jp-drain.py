import pandas as pd
import os
from datetime import datetime, timedelta

csv_url = os.environ.get('CSV_URL')
if not csv_url:
    raise ValueError("CSV_URL environment variable is not set. Please set it in GitHub Secrets.")

df = pd.read_csv(csv_url)
df = df.rename(columns={
    'date': 'datetime', 
    'date time': 'timestamp', 
    'volume in ml': 'volume'
})
df['timestamp'] = pd.to_datetime(df['timestamp'], format='%d/%m/%Y %H:%M:%S')

daily_volumes = {}
daily_colors = {}
daily_smells = {}

for i in range(1, len(df)):
    t1 = df.iloc[i-1]['timestamp']
    t2 = df.iloc[i]['timestamp']
    vol = df.iloc[i]['volume']
    color = df.iloc[i]['color']
    smell = df.iloc[i]['smell']
    
    duration = (t2 - t1).total_seconds() / 3600.0
    rate = vol / duration
    
    current_time = t1
    while current_time < t2:
        next_midnight = (current_time + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_segment = min(t2, next_midnight)
        
        segment_hours = (end_segment - current_time).total_seconds() / 3600.0
        segment_vol = segment_hours * rate
        
        date_str = current_time.strftime('%Y-%m-%d')
        daily_volumes[date_str] = daily_volumes.get(date_str, 0) + segment_vol
        
        if date_str not in daily_colors:
            daily_colors[date_str] = set()
        if date_str not in daily_smells:
            daily_smells[date_str] = set()
        
        daily_colors[date_str].add(color)
        daily_smells[date_str].add(smell)
        
        current_time = end_segment

summary_data = []
for date_str in daily_volumes:
    summary_data.append({
        'Date': date_str,
        'Total Volume (ml)': daily_volumes[date_str],
        'Color': ', '.join(sorted(daily_colors[date_str])),
        'Smell': ', '.join(sorted(daily_smells[date_str]))
    })

summary = pd.DataFrame(summary_data)
summary = summary.sort_values(by='Date')

print("Summary Table:")
print(summary)
summary.to_csv('summary_table.csv', index=False)