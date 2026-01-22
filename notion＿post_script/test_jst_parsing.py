import sys
import os
from datetime import timedelta, timezone

# Add the directory to sys.path to import the module
script_dir = "/Users/ishikawasuguru/Threads_piste/notion＿post_script"
sys.path.append(script_dir)

try:
    from piste_threads_notion import parse_markdown_posts
except ImportError:
    # If the filename has full-width underscore or similar issues, handle it
    # The file name in the prompt was `piste_threads_notion.py`
    pass

def test_parse_date_jst():
    markdown_content = """
## 投稿案1: Test
**投稿予定日時**: 2026-01-22 10:00
**本文**
Test Body
**コメント欄**
Test Comment
---
"""
    posts = parse_markdown_posts(markdown_content)
    
    if not posts:
        print("FAIL: No posts extracted")
        return

    post = posts[0]
    scheduled_date = post['scheduled_date']
    
    print(f"Extracted Date: {scheduled_date}")
    print(f"Timezone Info: {scheduled_date.tzinfo}")
    
    # Check if timezone is valid and has +9 offset
    expected_offset = timedelta(hours=9)
    if scheduled_date.tzinfo and scheduled_date.utcoffset() == expected_offset:
        print("SUCCESS: Date has correct JST timezone (+09:00).")
    else:
        print(f"FAIL: Date does not have correct JST timezone. Offset: {scheduled_date.utcoffset()}")

if __name__ == "__main__":
    test_parse_date_jst()
