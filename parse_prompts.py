import re
import json
import datetime

INPUT_FILE = '/Users/ishikawasuguru/Threads_piste/Piste_threads_image_prompt.md'
YEAR = 2026

def parse_prompts():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Sections start with "## Number. Title (Date)"
    sections = re.split(r'^## ', content, flags=re.MULTILINE)
    parsed_data = []
    
    for section in sections:
        if not section.strip():
            continue
            
        # Parse Header: Title (Month Day, Time)
        # Regex to handle "Title (Jan 24, 18:00)"
        header_match = re.match(r'.*?\((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d+),\s+(\d{1,2}:\d{2})\)', section)
        
        # If not match, maybe start of file or different format
        if not header_match:
            continue
            
        month_str = header_match.group(1)
        day_str = header_match.group(2)
        time_str = header_match.group(3)
        
        # Parse Prompt block
        # Look for "**Prompt**:" or "Prompt:" followed by ">" lines
        prompt_match = re.search(r'Prompt\*\*?:\n(>.*?)(?=\n---|\n##|$)', section, re.DOTALL)

        if prompt_match:
            prompt_text = prompt_match.group(1).strip()
            # Remove "> " and merge lines
            prompt_clean = re.sub(r'^>\s?', '', prompt_text, flags=re.MULTILINE).replace('\n', ' ')
            
            # Create datetime object
            dt_str = f"{YEAR} {month_str} {day_str} {time_str}"
            dt = datetime.datetime.strptime(dt_str, "%Y %b %d %H:%M")
            
            # Format Filename: YYYY-MM-DD-H:MM piste_threads
            # H is non-zero-padded hour if possible to match "6:00"
            filename_date = f"{dt.year}-{dt.month:02d}-{dt.day:02d}"
            filename_time = f"{dt.hour}:{dt.minute:02d}"
            filename = f"{filename_date}-{filename_time} piste_threads"
            
            parsed_data.append({
                'filename': filename,
                'prompt': prompt_clean
            })

    print(json.dumps(parsed_data, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    parse_prompts()
