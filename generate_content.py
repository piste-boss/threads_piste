import os
import sys
import datetime
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Load env
env_path = Path(__file__).parent / "90_System" / ".env"
load_dotenv(env_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not found in .env")
    print("Please add GEMINI_API_KEY to 90_System/.env")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)

POST_FILE = Path("Piste_threads_post.md")
PROMPT_FILE = Path("Piste_threads_image_prompt.md")
REPORT_FILE = Path("Piste_threads_report.md")

def get_recent_report():
    if REPORT_FILE.exists():
        with open(REPORT_FILE, 'r', encoding='utf-8') as f:
            return f.read()[-3000:] # Last 3000 chars
    return ""

def generate_posts_and_prompts():
    print("Initializing Gemini model...")
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
    report_content = get_recent_report()
    
    # Calculate next week's dates
    today = datetime.date.today()
    next_start = today + datetime.timedelta(days=(7 - today.weekday()) + 1) # Next Tuesday? Or just next week.
    # User said "Weekly Thursday 20:00". So generates for next week?
    # Let's generate for the upcoming Mon-Sun.
    start_date = today + datetime.timedelta(days=1) # Tomorrow
    
    propmt_text = f"""
    あなたはプロのSNSマーケターです。ダイエット・筋トレアカウント「ピステ」のThreads投稿を作成してください。
    
    【コンテキスト】
    直近のレポート:
    {report_content}
    
    【依頼内容】
    明日({start_date})から1週間分（7日分）の投稿案を作成してください。
    各日 06:00, 12:00, 18:00 の3投稿、合計21投稿です。
    
    【フォーマット】
    マークダウン形式で出力してください。
    各投稿には以下の要素を含めてください：
    - ## 投稿案X: [タイトル]
    - **投稿予定日時**: YYYY-MM-DD HH:MM
    - **本文**: (簡潔で有益な情報)
    - **コメント欄**: (詳細な解説、7箇条形式)
    
    また、各投稿に対応する画像生成用のプロンプトも別途作成してください。
    プロンプトは以下の形式で、リストとして出力してください（画像生成スクリプトがこの形式を読み取ります）：
    - **YYYY-MM-DD HH:MM**: (画像生成AI用の具体的で詳細なプロンプト。日本語。アスペクト比 9:16)
    """
    
    print("Generating content...")
    response = model.generate_content(propmt_text)
    
    if response.text:
        # Appending to Post File
        with open(POST_FILE, 'a', encoding='utf-8') as f:
            f.write("\n\n" + response.text + "\n")
        print(f"Appended posts to {POST_FILE}")
        
        # Appending to Prompt File (Image Gen script reads this)
        with open(PROMPT_FILE, 'a', encoding='utf-8') as f:
            f.write("\n\n" + response.text + "\n")
        print(f"Appended prompts to {PROMPT_FILE}")

    else:
        print("Failed to generate content.")

if __name__ == "__main__":
    generate_posts_and_prompts()
