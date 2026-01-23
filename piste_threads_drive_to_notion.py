#!/usr/bin/env python3
"""
Sync Google Drive Image Links to Notion

1. List files in Google Drive Folder (from piste_threads_image_uplorder.py)
2. Extract Date from filename (e.g. 2026-01-30-6:00)
3. Find Notion Page with same Date
4. Update 'URL' property with Drive Link
"""

import os
import sys
import re
import pickle
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dotenv import load_dotenv
from notion_client import Client
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Load env
env_path = Path(__file__).parent / "90_System" / ".env"
load_dotenv(env_path)

# Drive Config
DRIVE_FOLDER_ID = "1C1wxMNuIL0zDoqVIKFTeYi2agMn47vhk"
TOKEN_FILE = Path(__file__).parent / "image_upload" / "token.pickle"

# Notion Config
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID_HYPHEN = "2efc991b-527b-8090-a546-c89a11a5455d" # Hyphenated from previous script

JST = timezone(timedelta(hours=9))

def get_drive_service():
    creds = None
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("Error: Valid Drive token not found. Please run image uploader first to auth.")
            return None
            
    return build('drive', 'v3', credentials=creds)

def list_drive_files(service):
    print("Listing Drive files...")
    files = []
    page_token = None
    while True:
        results = service.files().list(
            q=f"'{DRIVE_FOLDER_ID}' in parents and trashed=false",
            fields="nextPageToken, files(id, name, webViewLink)",
            pageToken=page_token
        ).execute()
        files.extend(results.get('files', []))
        page_token = results.get('nextPageToken')
        if not page_token:
            break
    return files

def get_notion_client():
    if not NOTION_API_KEY:
        print("Error: NOTION_API_KEY not found.")
        return None
    return Client(auth=NOTION_API_KEY)


def find_page_by_date(notion, date_obj):
    # Use direct requests to avoid library version issues
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID_HYPHEN}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # Search for date match (exact match on ISO string might be tricky with timezone variations)
    # The Notion 'date' property usually stores ISO with offset.
    # Our target_dt is JST.
    # We will query for "Date" property equals target_iso.
    # Note: Property name is "投稿日" based on previous script.
    
    target_iso = date_obj.isoformat()
    
    data = {
        "filter": {
            "property": "投稿日",
            "date": {
                "equals": target_iso
            }
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            print(f"Error querying Notion: {response.text}")
            return []
            
        return response.json().get("results", [])
    except Exception as e:
        print(f"Error querying Notion: {e}")
        return []

def update_page_url(notion, page_id, url_link):
    # Use direct requests
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # We need to find the URL property name. 
    # Assume "URL" or "url". If "URL" doesn't exist, it might fail?
    # Actually, we can check the page properties first, but let's try "URL" since user specified it.
    # If the user renamed it, it might be different.
    # But usually creating a URL property defaults to "URL".
    
    data = {
        "properties": {
            "URL": { 
                "url": url_link
            }
        }
    }
    
    try:
        response = requests.patch(url, headers=headers, json=data)
        if response.status_code == 200:
             print(f"  ✓ Updated Notion Page {page_id}")
             return True
        else:
             print(f"  ✗ Failed to update page {page_id}: {response.text}")
             return False
    except Exception as e:
        print(f"  ✗ Failed to update page {page_id}: {e}")
        return False

def main():
    service = get_drive_service()
    if not service:
        sys.exit(1)
        
    drive_files = list_drive_files(service)
    print(f"Found {len(drive_files)} files in Drive.")
    
    notion = get_notion_client()
    if not notion:
        sys.exit(1)
    
    for f in drive_files:
        name = f['name']
        link = f['webViewLink']
        
        # Parse filename: 2026-01-30-6:00 piste_threads.png
        # Regex to capture date parts
        match = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})-(\d{1,2}):(\d{2})', name)
        if match:
            year, month, day, hour, minute = map(int, match.groups())
            target_dt = datetime(year, month, day, hour, minute, tzinfo=JST)
            
            print(f"Processing {name} -> {target_dt}")
            
            pages = find_page_by_date(notion, target_dt)
            if pages:
                for page in pages:
                    update_page_url(notion, page['id'], link)
            else:
                print(f"  No matching Notion page found for {target_dt}")
        else:
            # print(f"Skipping non-matching file: {name}")
            pass

if __name__ == "__main__":
    main()
