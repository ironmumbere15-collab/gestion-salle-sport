from supabase import create_client
from datetime import datetime, timedelta
import os

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase = create_client(url, key)

today = datetime.now().date()
target = today + timedelta(days=3)

data = supabase.table("abonnes").select("*").execute().data

for user in data:
    if str(user["date_fin"]) == str(target):
        print(f"{user['nom']} doit être notifié")
