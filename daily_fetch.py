from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from datetime import datetime
import psycopg2

# Load environment variables
load_dotenv()

# Authenticate
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope="user-read-recently-played"
))

# Fetch recent tracks
recent_tracks = sp.current_user_recently_played(limit=50)

# Format into DataFrame
track_data = []
for item in recent_tracks['items']:
    track = item['track']
    track_data.append({
        'track_id': track['id'],
        'name': track['name'],
        'artist': track['artists'][0]['name'],
        'played_at': item['played_at']
    })

df = pd.DataFrame(track_data)
df['played_at'] = pd.to_datetime(df['played_at'])
df.drop_duplicates(subset='played_at', inplace=True)  # prevent duplicates

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="neuroloop_db",
    user="your_username",
    password="your_password",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Insert only new records
for _, row in df.iterrows():
    cur.execute("""
        INSERT INTO spotify_tracks (track_id, name, artist, played_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (played_at) DO NOTHING;
    """, (row['track_id'], row['name'], row['artist'], row['played_at']))

conn.commit()
cur.close()
conn.close()
print("✅ Daily tracks inserted (if new)")
