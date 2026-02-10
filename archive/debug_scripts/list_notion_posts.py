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

data = {
    "filter": {
        "and": [
            {"property": "投稿日", "date": {"on_or_after": "2026-02-03"}},
            {"property": "投稿日", "date": {"on_or_before": "2026-02-10"}}
        ]
    },
    "sorts": [{"property": "投稿日", "direction": "ascending"}]
}

resp = requests.post(url, headers=headers, json=data)
if resp.status_code == 200:
    results = resp.json().get("results", [])
    print(f"Found {len(results)} pages:")
    for page in results:
        props = page.get("properties", {})
        title = props.get("タイトル", {}).get("title", [{}])[0].get("plain_text", "No Title")
        date_val = props.get("投稿日", {}).get("date", {}).get("start", "No Date")
        print(f"- {date_val}: {title}")
else:
    print(f"Error: {resp.text}")
