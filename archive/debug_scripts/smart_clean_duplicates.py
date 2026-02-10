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
    }
}

resp = requests.post(url, headers=headers, json=data)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    results = resp.json().get("results", [])
    print(f"Found {len(results)} pages in total.")
    seen_dates = {}
    
    for page in results:
        props = page.get("properties", {})
        date_val = props.get("投稿日", {}).get("date", {}).get("start")
        title_objs = props.get("タイトル", {}).get("title", [])
        title = title_objs[0].get("plain_text", "") if title_objs else ""
        
        if date_val:
            if date_val not in seen_dates:
                seen_dates[date_val] = []
            seen_dates[date_val].append({"id": page["id"], "title": title})

    for date_val, pages in seen_dates.items():
        if len(pages) > 1:
            print(f"Found {len(pages)} for {date_val}")
            # Preferred: title doesn't contain "（もしあれば）"
            to_keep = pages[0]
            for p in pages:
                if "（もしあれば）" not in p["title"] and p["title"] != "":
                    to_keep = p
                    break
            
            for p in pages:
                if p["id"] != to_keep["id"]:
                    del_url = f"https://api.notion.com/v1/blocks/{p['id']}"
                    requests.delete(del_url, headers=headers)
                    print(f"  ✗ Deleted {p['id']} ({p['title']})")
            print(f"  ✓ Kept {to_keep['id']} ({to_keep['title']})")
else:
    print(f"Error: {resp.text}")
