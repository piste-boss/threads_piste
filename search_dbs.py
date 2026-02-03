import os
import requests
import json
from dotenv import load_dotenv
from pathlib import Path

# Load env
env_path = Path("/Users/ishikawasuguru/Threads_piste/90_System/.env")
load_dotenv(env_path)

NOTION_API_KEY = os.getenv("NOTION_API_KEY")

def search_notion():
    url = "https://api.notion.com/v1/search"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    payload = {
        "filter": {
            "value": "database",
            "property": "object"
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

if __name__ == "__main__":
    results = search_notion()
    for db in results.get("results", []):
        title = "".join([t.get("plain_text", "") for t in db.get("title", [])])
        print(f"Database: {title}, ID: {db['id']}")
