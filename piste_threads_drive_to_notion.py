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
    
    # Not exact ISO match can be flaky.
    # Query for the specific DATE (YYYY-MM-DD) which matches any time on that day (usually)
    # OR query for a range.
    # Let's try querying for the date string "YYYY-MM-DD".
    target_date_str = date_obj.strftime("%Y-%m-%d")
    
    data = {
        "filter": {
            "property": "投稿日",
            "date": {
                "equals": target_date_str
            }
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            print(f"Error querying Notion: {response.text}")
            return []
            
        results = response.json().get("results", [])
        
        # Filter strictly by time in Python
        matched_pages = []
        target_iso_prefix = date_obj.strftime("%Y-%m-%dT%H:%M") # Match up to minute
        
        for page in results:
            props = page.get("properties", {})
            date_prop = props.get("投稿日", {})
            date_val = date_prop.get("date", {})
            if not date_val:
                continue
                
            start_date = date_val.get("start", "") # ISO string
            # Check if start_date starts with our target (ignoring seconds/timezone string diffs if minute matches)
            # Notion ISO: 2026-01-30T06:00:00.000+09:00
            # Target: 2026-01-30T06:00
            
            # Simple substring match for "YYYY-MM-DDTHH:MM"
            if target_iso_prefix in start_date:
                matched_pages.append(page)
        
        return matched_pages

    except Exception as e:
        print(f"Error querying Notion: {e}")
        return []

def update_page_url(notion, page_id, url_link, property_name="URL"):
    # Use direct requests
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    data = {
        "properties": {
            property_name: { 
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
        
        # Parse filename: 
        # Format 1: 2026-01-30-6:00 piste_threads.png
        # Format 2: jan30_12_00_salad_chicken.png (Year 2026 implicitly)
        
        target_dt = None
        
        # Try Format 1
        match1 = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})-(\d{1,2}):(\d{2})', name)
        if match1:
            year, month, day, hour, minute = map(int, match1.groups())
            target_dt = datetime(year, month, day, hour, minute, tzinfo=JST)
            
        # Try Format 2
        if not target_dt:
            # Matches jan30_12_00_... => month=jan(1), day=30, hour=12, minute=00
            match2 = re.match(r'jan(\d{1,2})_(\d{1,2})_(\d{2})_', name.lower())
            if match2:
                day, hour, minute = map(int, match2.groups())
                year = 2026 # Hardcoded for this context
                month = 1   # Jan
                target_dt = datetime(year, month, day, hour, minute, tzinfo=JST)
        
        if target_dt:
            print(f"Processing {name} -> {target_dt}")
            
            pages = find_page_by_date(notion, target_dt)
            if pages:
                for page in pages:
                    # Try to update 'URL' or '画像URL'
                    if not update_page_url(notion, page['id'], link, "URL"):
                        print("  Retrying with property '画像URL'...")
                        update_page_url(notion, page['id'], link, "画像URL")
            else:
                print(f"  No matching Notion page found for {target_dt}")
        else:
            # print(f"Skipping non-matching file: {name}")
            pass

if __name__ == "__main__":
    main()
