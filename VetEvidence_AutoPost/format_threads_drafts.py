import os
import glob
import re
import json
import time
import concurrent.futures
from dotenv import load_dotenv
import google.generativeai as genai

ENV_PATH = r"C:\Users\souhe\Desktop\論文まとめ\.env"
DRAFTS_DIR = r"C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts"

load_dotenv(ENV_PATH)
if "GEMINI_API_KEY" not in os.environ:
    print("Error: GEMINI_API_KEY not found in .env")
    exit(1)

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})

PROMPT_FORMAT_LONG = """
以下の【元の文章】の【語彙、意味、専門用語、順番、だ・である等のトーン】は【一言一句まったく変更せず】、スマートフォンで読みやすいように視覚的な改行（空白行）だけを追加してください。
長すぎる文は、意味の区切りや読点ごとに改行（空白行）を入れたり、必要に応じて適度な空間を作ってスッキリとしたレイアウトにしてください。元の文章の内容や単語自体は絶対に加筆・修正・削除しないでください。
※末尾のハッシュタグもそのまま残してください。

必ず以下のJSON形式で出力してください:
{
  "formatted_text": "内容を変えずに改行だけを加えた文章"
}

【元の文章】:
"""

PROMPT_FORMAT_SHORT = """
以下の【元の文章】の内容、構成、および真面目で知的なトーン（語尾の「だ・である」または「です・ます」）は【絶対に維持】しつつ、以下の2点だけを【厳重に修正】してください。

① 主語の「わたし」という表現を極力削除（前後の文脈で自然に省略、または「我々」等へ変更）する。（0〜1回に留めること）
② 以下の【参考アカウントのしゃべり口調】のような、読者に直接語りかけるようなポンポンと読める【1〜2フレーズごとの頻繁な改行リズム】を取り入れる。

【絶対的な禁止事項】
・絵文字（😀、✨など）や、不自然な（！）の連発は絶対に、一切使用しないでください。
・元の文章の文体や意味の【大きな変更】は絶対に行わないこと。あくまで「改行による視覚的テンポの改善」と「『わたし』の削除」に特化すること。
※末尾のハッシュタグもそのまま残してください。

【参考アカウントの口調（改行の参考として）】
猫ってヒゲが器に当たるのを
極端に嫌がる子がいるんです！
「最近水飲まないな」と思ったら、
器を疑ってみてください！

必ず以下のJSON形式で出力してください:
{
  "formatted_text": "わたしを削減し、改行リズムを整えた文章"
}

【元の文章】:
"""

def generate_format(prompt, text, retry=3):
    for i in range(retry):
        try:
            response = model.generate_content(prompt + text)
            data = json.loads(response.text)
            if "formatted_text" in data:
                # Remove emojis just in case LLM ignored the instruction
                import emoji
                clean_text = emoji.replace_emoji(data["formatted_text"], replace='')
                return clean_text.strip()
        except Exception as e:
            time.sleep(2)
    return None

def process_file(md_file):
    folder_name = os.path.basename(os.path.dirname(md_file))
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract long and short thread texts
    # They look like:
    # ## 🧵 Threads用（長文・専門的）
    # ```text
    # (long content)
    # ```
    # ---
    # ## 🧵 Threads用（火木土：プランX）
    # ```text
    # (short content)
    # ```
    long_match = re.search(r"## 🧵 Threads用（長文・専門的）\n+\s*```text\n(.*?)\n```", content, re.DOTALL)
    short_match = re.search(r"## 🧵 Threads用（火木土：プラン(\d)）\n+\s*```text\n(.*?)\n```", content, re.DOTALL)

    if not long_match or not short_match:
        return False, f"[{folder_name}] Regex match failed."

    orig_long = long_match.group(1).strip()
    plan_num = short_match.group(1)
    orig_short = short_match.group(2).strip()

    print(f"[{folder_name}] Formatting Long...")
    new_long = generate_format(PROMPT_FORMAT_LONG, orig_long)
    
    print(f"[{folder_name}] Formatting Short...")
    new_short = generate_format(PROMPT_FORMAT_SHORT, orig_short)

    if not new_long or not new_short:
        return False, f"[{folder_name}] API failed."

    # Replace in content safely by replacing the exact blocks matched
    long_block = long_match.group(0)
    new_long_block = f"## 🧵 Threads用（長文・専門的）\n\n```text\n{new_long}\n```"
    
    short_block = short_match.group(0)
    new_short_block = f"## 🧵 Threads用（火木土：プラン{plan_num}）\n\n```text\n{new_short}\n```"

    content = content.replace(long_block, new_long_block)
    content = content.replace(short_block, new_short_block)

    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(content)

    return True, f"[{folder_name}] Successfully formatted."

def main():
    md_files = glob.glob(os.path.join(DRAFTS_DIR, "**", "sns_all_drafts.md"), recursive=True)
    print(f"Found {len(md_files)} files. Starting formatting...")
    
    success_count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(process_file, md_files))
        
    for ok, msg in results:
        print(msg)
        if ok:
            success_count += 1
            
    print(f"Completed! Formatted {success_count} files.")

if __name__ == "__main__":
    main()
