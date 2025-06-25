from dotenv import load_dotenv
import os
load_dotenv()

import spotipy 
from spotipy.oauth2 import SpotifyOAuth 
import pandas as pd
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt

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


# Example: Plot average rewind score by day
df_summary = df.groupby('day_of_week')['rewind_score'].mean().reindex(
    ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
)

df_summary.plot(kind='bar', title='Average Rewind Score by Day of Week')
plt.ylabel('Rewind Score')
plt.tight_layout()
plt.show()



from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report


# Assume df is your full DataFrame
X = df[['hour', 'day_of_week', 'artist']]
y = df['is_high_replay'].astype(int)

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Preprocessing
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), ['day_of_week', 'artist'])
    ],
    remainder='passthrough'
)

# Model pipeline
clf = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
])

clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)

print(classification_report(y_test, y_pred))


importances = clf.named_steps['classifier'].feature_importances_
feature_names = clf.named_steps['preprocessor'].get_feature_names_out()
feat_df = pd.DataFrame({'Feature': feature_names, 'Importance': importances})
feat_df = feat_df.sort_values(by='Importance', ascending=False)

plt.figure(figsize=(10,6))
sns.barplot(x='Importance', y='Feature', data=feat_df.head(10))
plt.title('Top 10 Features Predicting Replays')
plt.tight_layout()
plt.show()
