import pandas as pd
import requests
import time
from pathlib import Path

Path('data/crime').mkdir(parents=True, exist_ok=True)

base_url = "https://phl.carto.com/api/v2/sql"
years = range(2006, 2025)
frames = []

for year in years:
    url = (
        f"{base_url}?format=csv"
        f"&q=SELECT+*,+ST_Y(the_geom)+AS+lat,+ST_X(the_geom)+AS+lng"
        f"+FROM+incidents_part1_part2"
        f"+WHERE+dispatch_date_time+>=+'{year}-01-01'"
        f"+AND+dispatch_date_time+<+'{year+1}-01-01'"
    )
    print(f"Downloading {year}...", end=" ")
    df = pd.read_csv(url)
    print(f"{len(df):,} rows")
    frames.append(df)
    time.sleep(1)  # be polite to the API

crime_df = pd.concat(frames, ignore_index=True)
print(f"\nTotal: {len(crime_df):,} rows × {crime_df.shape[1]} columns")
crime_df.to_csv('data/crime/philly_crime.csv', index=False)
print("Saved -> data/crime/philly_crime.csv")