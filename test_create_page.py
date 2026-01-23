
import os
import sys
from notion_client import Client
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

# Load env from corrected path
env_path = Path("/Users/ishikawasuguru/Threads_piste/90_System/.env")
load_dotenv(env_path)

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = "2efc991b-527b-8090-a546-c89a11a5455d"

notion = Client(auth=NOTION_API_KEY)

print("Creating test page...")
props = {
    "タイトル": {
        "title": [{"text": {"content": "Test Page 123"}}]
    },
    "投稿日": {
        "date": {"start": "2026-01-31T10:00:00+09:00"}
    }
}

try:
    resp = notion.pages.create(
        parent={"database_id": NOTION_DATABASE_ID},
        properties=props
    )
    print(f"Created page: {resp['id']}")
    
    # Verify immediately
    print("Verifying...")
    get_resp = notion.pages.retrieve(resp['id'])
    p = get_resp["properties"]
    t = p["タイトル"]["title"][0]["text"]["content"]
    d = p["投稿日"]["date"]["start"]
    print(f"Retrieved: Title={t}, Date={d}")
except Exception as e:
    print(f"Error: {e}")
