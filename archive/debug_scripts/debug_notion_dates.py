
import os
import sys
from notion_client import Client
from dotenv import load_dotenv
from pathlib import Path

# Load env from corrected path
env_path = Path("/Users/ishikawasuguru/Threads_piste/90_System/.env")
load_dotenv(env_path)

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = "2efc991b-527b-8090-a546-c89a11a5455d"

if not NOTION_API_KEY:
    print("No API KEY")
    sys.exit(1)

notion = Client(auth=NOTION_API_KEY)

print(f"Querying DB {NOTION_DATABASE_ID} for recent pages...")
resp = notion.databases.query(database_id=NOTION_DATABASE_ID, page_size=20)

for page in resp.get("results", []):
    props = page.get("properties", {})
    # Check title
    title_prop = props.get("タイトル", {}).get("title", [])
    title_text = "".join([t["plain_text"] for t in title_prop])
    
    # Check date
    date_prop = props.get("投稿日", {}).get("date", {})
    start_date = date_prop.get("start") if date_prop else "None"
    
    print(f"Title: {title_text}, Date (ISO): {start_date}")
