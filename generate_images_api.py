import os
import sys
import re
import requests
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load env variables
env_path = Path(__file__).parent / "90_System" / ".env"
load_dotenv(env_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY not found in 90_System/.env")
    # We don't exit here immediately to allow other logic if needed, 
    # but for this script it's essential.
    print("Please set your OPENAI_API_KEY for image generation.")
    sys.exit(1)

client = OpenAI(api_key=OPENAI_API_KEY)

IMAGE_DIR = Path("Piste_threads_image")
PROMPT_FILE = Path("Piste_threads_image_prompt.md")

def download_image(url, save_path):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"  ✓ Saved to {save_path.name}")
        return True
    except Exception as e:
        print(f"  ✗ Failed to download image: {e}")
        return False

def generate_from_prompts():
    if not PROMPT_FILE.exists():
        print(f"Prompt file not found: {PROMPT_FILE}")
        return

    # Ensure output directory exists
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Regex to capture date and prompt
    # Format: - **YYYY-MM-DD HH:MM**: [Prompt]
    matches = re.findall(r'- \*\*(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\*\*: (.*)', content)
    
    print(f"Found {len(matches)} prompts in markdown file.")
    
    success_count = 0
    
    for date_str, prompt in matches:
        dt_part, time_part = date_str.split(' ')
        hour, minute = time_part.split(':')
        hour_int = int(hour)
        formatted_date_str = f"{dt_part}-{hour_int}:{minute}" 
        filename = f"{formatted_date_str} piste_threads.png"
        filepath = IMAGE_DIR / filename
        
        if filepath.exists():
            continue
        
        print(f"\nGenerating for {date_str}...")
        
        # Retry loop for API Quota
        max_retries = 1
        for attempt in range(max_retries + 1):
            try:
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size="1024x1792", 
                    quality="standard",
                    n=1,
                )
                
                image_url = response.data[0].url
                if download_image(image_url, filepath):
                    success_count += 1
                break # Success, exit retry loop
                    
            except Exception as api_error:
                error_str = str(api_error)
                print(f"  ✗ API Error (Attempt {attempt+1}): {error_str}")
                
                # Check for rate limit / quota errors (429 or specific text)
                if "429" in error_str or "quota" in error_str.lower():
                    if attempt < max_retries:
                        print("  ⚠ Quota limit reached. Waiting 3 hours before retrying...")
                        import time
                        time.sleep(3 * 60 * 60) # 3 hours wait
                        print("  Resuming generation attempt...")
                        continue
                
                # If not quota error or max retries reached, move to next prompt
                break

    print(f"\nGeneration Complete. New images: {success_count}")

if __name__ == "__main__":
    generate_from_prompts()
