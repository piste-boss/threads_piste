import os
import requests
import json
from dotenv import load_dotenv
from pathlib import Path

# Load env
env_path = Path("/Users/ishikawasuguru/Threads_piste/90_System/.env")
load_dotenv(env_path)

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = "2efc991b527b8090a546c89a11a5455d"

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
    print(json.dumps(info, indent=2, ensure_ascii=False))
