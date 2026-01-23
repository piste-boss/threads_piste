
import os
import sys
import requests
import json
from dotenv import load_dotenv
from pathlib import Path

# Load env from corrected path
env_path = Path("/Users/ishikawasuguru/Threads_piste/90_System/.env")
load_dotenv(env_path)

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID_HYPHEN = "2efc991b-527b-8090-a546-c89a11a5455d"

url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID_HYPHEN}/query"
headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

resp = requests.post(url, headers=headers, json={
    "page_size": 50,
     "sorts": [
        {
            "timestamp": "created_time",
            "direction": "descending"
        }
    ]
})
if resp.status_code != 200:
    print(f"Error: {resp.text}")
    sys.exit(1)

data = resp.json()
for page in data.get("results", []):
    props = page.get("properties", {})
    # Print all property keys to debug
    print(f"Prop Keys: {list(props.keys())}")
    
    # Check title

    title_prop = props.get("タイトル", {}).get("title", [])
    title_text = "".join([t["plain_text"] for t in title_prop])
    
    # Check date
    date_prop = props.get("投稿日", {}).get("date", {})
    start_date = date_prop.get("start") if date_prop else "None"
    
    print(f"Title: {title_text}, Date (ISO): {start_date}")
