# upload_to_db.py
import pandas as pd
from sqlalchemy import create_engine

df = pd.read_csv("recent_tracks_behavior_only.csv")
engine = create_engine("postgresql://postgres:Jjj391bp.@localhost:5432/neuroloop_db")
df.to_sql("track_history", engine, if_exists="append", index=False)

print("✅ Uploaded CSV to PostgreSQL.")
