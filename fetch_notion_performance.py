import os
import requests
import csv
from dotenv import load_dotenv
from pathlib import Path

# Load env
env_path = Path("/Users/ishikawasuguru/Threads_piste/90_System/.env")
load_dotenv(env_path)

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = "2efc991b527b8090a546c89a11a5455d"

def fetch_notion_data():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # Filter for 1/26 to 1/31
    payload = {
        "filter": {
            "and": [
                {
                    "property": "投稿日",
                    "date": {
                        "on_or_after": "2026-01-26"
                    }
                },
                {
                    "property": "投稿日",
                    "date": {
                        "on_or_before": "2026-01-31"
                    }
                }
            ]
        }
    }
    
    print(f"Querying Notion with payload: {payload}")
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return []
    
    results = response.json().get("results", [])
    print(f"Found {len(results)} results in date range.")
    data = []
    
    for page in results:
        props = page.get("properties", {})
        # ... (rest of the processing logic)


def save_to_csv(data):
    fields = ["日付", "本文", "いいね", "インプレッション"] + [f"コメント欄{i}" for i in range(1, 8)]
    with open("/Users/ishikawasuguru/Threads_piste/threads_data_dump.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in data:
            # fill missing keys
            for field in fields:
                if field not in row:
                    row[field] = ""
            writer.writerow(row)

if __name__ == "__main__":
    print("Fetching data from Notion...")
    data = fetch_notion_data()
    print(f"Fetched {len(data)} items.")
    if data:
        save_to_csv(data)
        print("Saved to threads_data_dump.csv")
    else:
        print("No data found or error occurred.")
