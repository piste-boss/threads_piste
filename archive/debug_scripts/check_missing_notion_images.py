import os
import requests
from dotenv import load_dotenv
from pathlib import Path

env_path = Path("90_System/.env")
load_dotenv(env_path)

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = "2efc991b527b8090a546c89a11a5455d"

url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_prop_val(props, name, sub):
    p = props.get(name, {})
    if not p: return None
    v = p.get(p.get("type", ""), {})
    if not v: return None
    if isinstance(v, list):
        if not v: return None
        return v[0].get("plain_text")
    return v.get(sub)

data = {
    "filter": {
        "and": [
            {"property": "投稿日", "date": {"on_or_after": "2026-02-03"}},
            {"property": "投稿日", "date": {"on_or_before": "2026-02-10"}}
        ]
    }
}

resp = requests.post(url, headers=headers, json=data)
if resp.status_code == 200:
    results = resp.json().get("results", [])
    print(f"Checking {len(results)} pages...")
    missing = []
    for page in results:
        props = page.get("properties", {})
        
        # Date
        date_prop = props.get("投稿日", {}).get("date")
        date_val = date_prop.get("start") if date_prop else "No Date"
        
        # Title
        title_objs = props.get("タイトル", {}).get("title", [])
        title = title_objs[0].get("plain_text", "No Title") if title_objs else "No Title"
        
        # Image URL
        url_val = props.get("URL", {}).get("url")
        img_url_val = props.get("画像URL", {}).get("url")
        
        if not url_val and not img_url_val:
            missing.append(f"{date_val}: {title}")
    
    if missing:
        print(f"Found {len(missing)} pages missing images:")
        for m in sorted(missing):
            print(f"- {m}")
    else:
        print("All fetched pages have image URLs.")
else:
    print(f"Error: {resp.status_code} - {resp.text}")
