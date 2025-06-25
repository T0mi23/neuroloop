from dotenv import load_dotenv
import os
load_dotenv()

import spotipy 
from spotipy.oauth2 import SpotifyOAuth 
import pandas as pd
from datetime import datetime

sp = spotipy.Spotify(auth_manager = SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope="user-read-recently-played"
))

recent_tracks = sp.current_user_recently_played(limit = 50)

track_data= []
for item in recent_tracks['items']:
    track = item['track']
    track_data.append({
        'name': track['name'],
        'artist': track['artists'][0]['name'],
        'played_at': item['played_at']
    })

# 🧠 WHY: Use datetime to help analyze trends (day, hour, etc.)
df = pd.DataFrame(track_data)
df['played_at'] = pd.to_datetime(df['played_at'])
df['date'] = df['played_at'].dt.date
df['hour'] = df['played_at'].dt.hour
df['day_of_week'] = df['played_at'].dt.day_name()

# 🔁 WHY: Rewind Score = how many times same track played on same day
rewind_counts = df.groupby(['name', 'date']).size().reset_index(name='rewind_score')
df = df.merge(rewind_counts, on=['name', 'date'], how='left')

# ✅ WHY: Highlight tracks with 3+ same-day plays as "dopamine hits"
df['is_high_replay'] = df['rewind_score'] >= 3

# 💾 WHY: Save for Power BI, analysis, or visual display
df.to_csv('recent_tracks_behavior_only.csv', index=False)
print("✅ Saved as recent_tracks_behavior_only.csv")
