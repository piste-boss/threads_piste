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

# Query all pages in the range
data = {
    "filter": {
        "and": [
            {"property": "投稿日", "date": {"on_or_after": "2026-02-03"}},
            {"property": "投稿日", "date": {"on_or_before": "2026-02-10"}}
        ]
    }
}

resp = requests.post(url, headers=headers, json=data)
print(f"Status Code: {resp.status_code}")
if resp.status_code == 200:
    results = resp.json().get("results", [])
    print(f"Total results found: {len(results)}")
    seen_dates = {} # date_str -> list of page_ids
    
    for page in results:
        props = page.get("properties", {})
        date_val = props.get("投稿日", {}).get("date", {}).get("start")
        if date_val:
            if date_val not in seen_dates:
                seen_dates[date_val] = []
            seen_dates[date_val].append(page["id"])
            
    # Delete duplicates
    for date_str, page_ids in seen_dates.items():
        if len(page_ids) > 1:
            print(f"Found {len(page_ids)} pages for {date_str}. Keeping the first one, deleting others.")
            # Keep index 0, delete others
            for page_id in page_ids[1:]:
                del_url = f"https://api.notion.com/v1/blocks/{page_id}"
                del_resp = requests.delete(del_url, headers=headers)
                if del_resp.status_code == 200:
                    print(f"  ✓ Deleted duplicate {page_id}")
                else:
                    print(f"  ✗ Failed to delete {page_id}: {del_resp.text}")
else:
    print(f"Error querying Notion: {resp.text}")
