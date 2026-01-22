import re
import csv
import json
import sys

def parse_markdown(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return

    # Normalize newlines
    content = content.replace('\r\n', '\n')
    
    # Split by separator
    chunks = content.split('---')
    
    posts = []
    
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
            
        # Extract fields
        # Title: ## 投稿案X: Title
        title_match = re.search(r'## (.*)', chunk)
        
        # Date: **投稿予定日時**: YYYY-MM-DD HH:MM
        date_match = re.search(r'\*\*投稿予定日時\*\*: (.*)', chunk)
        
        # Body: Between **本文** and **コメント欄**
        # We use re.DOTALL to match newlines
        body_match = re.search(r'\*\*本文\*\*\n(.*?)\n\*\*コメント欄\*\*', chunk, re.DOTALL)
        
        # Comment: After **コメント欄**
        comment_match = re.search(r'\*\*コメント欄\*\*\n(.*)', chunk, re.DOTALL)
        
        if title_match and date_match:
            title = title_match.group(1).strip()
            date_str = date_match.group(1).strip()
            
            # Format date to ISO 8601 with Timezone (JST)
            # Input: 2026-01-22 06:00
            # Output: 2026-01-22T06:00:00+09:00
            if re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}', date_str):
                iso_date = date_str.replace(' ', 'T') + ':00+09:00'
            else:
                iso_date = date_str # Fallback
            
            body = body_match.group(1).strip() if body_match else ""
            comment = comment_match.group(1).strip() if comment_match else ""
            
            posts.append({
                "title": title,
                "date": iso_date,
                "body": body,
                "comment": comment,
                "status": "未着手"
            })
            
    output_file = '/Users/ishikawasuguru/.gemini/antigravity/brain/11186f2b-f661-49e1-a3e4-366c28efb007/posts.csv'
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        # Header
        writer.writerow(['Date', 'Title', 'Body', 'Comment', 'Status'])
        # Rows
        for post in posts:
            writer.writerow([
                post['date'],
                post['title'],
                post['body'],
                post['comment'],
                post['status']
            ])
    print(f"Successfully saved {len(posts)} posts to {output_file}")

if __name__ == "__main__":
    parse_markdown('/Users/ishikawasuguru/Threads_piste/Piste_threads_post.md')
