import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load env
env_path = Path("/Users/ishikawasuguru/Threads_piste/90_System/.env")
load_dotenv(env_path)

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = "2f4c991b527b80ef893ff1e278765e1a"

def get_db_info():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28"
    }
    response = requests.get(url, headers=headers)
    return response.json()

if __name__ == "__main__":
    info = get_db_info()
    props = info.get("properties", {})
    if not props:
        print(f"Error or empty: {info}")
    for name, val in props.items():
        print(f"Property: {name}, Type: {val['type']}")
