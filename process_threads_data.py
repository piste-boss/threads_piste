import csv
import datetime
import os
import re

DATA_FILE = '/Users/ishikawasuguru/Threads_piste/Piste_threads_data.md'
REPORT_FILE = '/Users/ishikawasuguru/Threads_piste/Piste_threads_report.md'
CSV_FILE = '/Users/ishikawasuguru/Threads_piste/threads_data_dump.csv'

def parse_markdown_table_line(line):
    parts = line.strip().split('|')
    if len(parts) < 6:
        return None
    date_str = parts[1].strip()
    return date_str

def read_existing_dates():
    existing_dates = set()
    if not os.path.exists(DATA_FILE):
        return existing_dates
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip().startswith('|') and '日付' not in line and ':---' not in line:
                date_str = parse_markdown_table_line(line)
                if date_str:
                    existing_dates.add(date_str)
    return existing_dates

def process_csv_row(row):
    # Parse date: 2026-01-10T21:52:13+0000 -> 2026-01-10 21:52:13
    raw_date = row['日付']
    try:
        dt = datetime.datetime.strptime(raw_date, '%Y-%m-%dT%H:%M:%S%z')
        # Convert to naive string for comparison/storage (assuming existing md is effectively JST or naive, keeping simple)
        # Actually spreadsheet is +0000 UTC. The existing markdown has dates like 2026-01-10 21:52:13.
        # User is in JST (UTC+9). The spreadsheet +0000 needs to be converted to JST?
        # Let's check existing file contents. 
        # Line 5: | 2026-01-10 21:52:13 | ...
        # CSV Line: 2026-01-10T21:52:13+0000
        # If the spreadsheet says 21:52 UTC, that is 06:52 JST next day.
        # WAIT. Line 5 in MD matches CSV Line 1 in date string exactly: 2026-01-10 21:52:13.
        # So the MD file effectively stores UTC time but labeled as just date/time?
        # OR the spreadsheet is actually storing local time with a fake +0000?
        # Let's assume we just want to match the string representation "YYYY-MM-DD HH:MM:SS" ignoring timezone for matching purposes,
        # but for the "JST" report, we might need to be careful.
        # However, looking at the report example: "2025-12-21 07:00".
        # If I look at the csv dump, I see "2026-01-10T21:52:13+0000".
        # If I convert this to JST (+9), it becomes 2026-01-11 06:52:13.
        # The existing MD has "2026-01-10 21:52:13".
        # It seems the existing MD just took the UTC string without conversion?
        # Or maybe the spreadsheet export is giving me UTC but the user sees JST in the browser?
        # Let's look at a known post.
        # MD Line 12: 2026-01-05 23:16:58
        # If that was JST, it's late night.
        # If that was UTC, it's 08:16 JST next day.
        # The report says: "2026-01-05 08:02" for a post with 26915 impressions.
        # MD Line 13: 2026-01-04 23:02:05 | ... | 48 | 26915.
        # Report says: "2026-01-05 08:02" (Wait, 23:02 UTC + 9h = 08:02).
        # SO, the MD file stores UTC times (or whatever the raw string is).
        # The Report converts to JST.
        # I should simply store the UTC time in the MD file to be consistent with existing data.
        formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        formatted_date = raw_date # Fallback

    body = row['本文'].replace('\n', '<br>')
    # Truncate body if too long for table? Existing file has "..." but also short text.
    # I'll just keep it full but replace newlines.
    
    likes = row['いいね']
    impressions = row['インプレッション']
    
    comments = []
    for i in range(1, 8):
        key = f'コメント欄{i}'
        if row.get(key):
            comments.append(row[key])
    comment_text = " ".join(comments).replace('\n', '<br>')
    
    return f"| {formatted_date} | {body} | {likes} | {impressions} | {comment_text} |"

def append_new_data():
    existing_dates = read_existing_dates()
    new_lines = []
    
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_date = row['日付']
            try:
                dt = datetime.datetime.strptime(raw_date, '%Y-%m-%dT%H:%M:%S%z')
                formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                formatted_date = raw_date
            
            if formatted_date not in existing_dates:
                # Add check to ensure we don't add duplicates from the CSV itself if it has them
                 # (simplest is just building a list and sorting later, but here we append top to bottom?)
                 # The CSV seems reverse chronological or mixed.
                 # Let's just append.
                 new_lines.append(process_csv_row(row))
                 existing_dates.add(formatted_date) # Update set to avoid dupes within CSV

    if new_lines:
        with open(DATA_FILE, 'a', encoding='utf-8') as f:
            for line in new_lines:
                f.write(line + '\n')
        print(f"Appended {len(new_lines)} posts.")
    else:
        print("No new posts to append.")

def generate_report():
    print("Generating report...")
    # Read all data from MD
    posts = []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip().startswith('|') and '日付' not in line and ':---' not in line:
                parts = line.strip().split('|')
                if len(parts) >= 6:
                    date_str = parts[1].strip()
                    body = parts[2].strip()
                    likes = parts[3].strip()
                    impressions = parts[4].strip()
                    comments = parts[5].strip()
                    
                    try:
                        # Parse date as UTC
                        dt_utc = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                        dt_utc = dt_utc.replace(tzinfo=datetime.timezone.utc)
                        # Convert to JST
                        dt_jst = dt_utc.astimezone(datetime.timezone(datetime.timedelta(hours=9)))
                    except:
                        continue
                        
                    try:
                        imp_val = int(impressions)
                    except:
                        imp_val = 0
                    
                    try:
                        likes_val = int(likes)
                    except:
                        likes_val = 0

                    posts.append({
                        'date_jst': dt_jst,
                        'body': body,
                        'likes': likes_val,
                        'impressions': imp_val,
                        'comments': comments
                    })
    
    # Analyze
    posts.sort(key=lambda x: x['impressions'], reverse=True)
    top_5 = posts[:5]
    
    # Calculate stats by hour
    hour_stats = {}
    for p in posts:
        h = p['date_jst'].hour
        if h not in hour_stats:
            hour_stats[h] = []
        hour_stats[h].append(p['impressions'])
        
    avg_hour_stats = []
    for h, imps in hour_stats.items():
        avg = sum(imps) / len(imps)
        avg_hour_stats.append((h, avg, len(imps)))
    
    avg_hour_stats.sort(key=lambda x: x[1], reverse=True)
    
    # Format Report
    today_str = datetime.datetime.now().strftime('%Y-%m-%d')
    report_content = f"\n\n# 週次レポート ({today_str})\n\n"
    
    report_content += "## 1. 概要\n"
    report_content += f"全{len(posts)}件の投稿を分析しました。\n"
    if avg_hour_stats:
        top_hour = avg_hour_stats[0]
        report_content += f"最も反応が良い時間帯は **{top_hour[0]}:00台** (平均 {int(top_hour[1]):,} imp) です。\n"
    
    report_content += "\n## 2. インプレッション上位投稿ランキング (Top 5)\n\n"
    report_content += "| 順位 | インプレッション | いいね | 投稿日時(JST) | 本文(抜粋) |\n"
    report_content += "| :---: | :---: | :---: | :--- | :--- |\n"
    
    for i, p in enumerate(top_5):
        body_short = p['body'].replace('<br>', ' ')[:20] + '...'
        date_fmt = p['date_jst'].strftime('%Y-%m-%d %H:%M')
        report_content += f"| {i+1} | {p['impressions']:,} | {p['likes']:,} | {date_fmt} | {body_short} |\n"
        
    report_content += "\n## 3. 成功要因の分析\n"
    report_content += "\n### 投稿時間帯の傾向 (Top 3)\n"
    for h, avg, count in avg_hour_stats[:3]:
        report_content += f"- **{h}:00台**: 平均 {int(avg):,} インプレッション ({count}件)\n"
        
    with open(REPORT_FILE, 'a', encoding='utf-8') as f:
        f.write(report_content)
    print("Report generated and appended.")

if __name__ == '__main__':
    append_new_data()
    generate_report()
