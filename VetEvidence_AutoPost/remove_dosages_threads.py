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

# Regex to find specific drug dosages (mg/kg, μg/kg, ml/kg, etc.)
dosage_pattern = re.compile(r'(\d+(\.\d+)?(-|〜|~)?\d*(\.\d+)?\s?(mg|μg|mcg|mL|g)/kg(/?(hr|min|day))?)', re.IGNORECASE)

REWRITE_PROMPT = """
あなたは獣医療の専門的な文章をチェックし、安全にSNS(Threads)へ投稿できる状態に修正するアシスタントです。
以下のThreads用投稿文には、自動フィルター（不適切な医療情報の拡散防止）に抵触する恐れのある具体的な薬剤の用量（mg/kg, μg/kg, mL/kgなど）が含まれています。
文章の専門的なトーンや文脈は維持したまま、具体的な数値による用量指定部分だけを削除し、「適切な用量で」「〜の投与を検討」「環境に応じて調整」などのより一般的で自然な表現に置き換えてください。
文章の最後（ハッシュタグの前）には必ず「具体的な薬剤用量や詳細な治療アルゴリズムは文字数の関係でNoteにて解説します。」というニュアンスの一文（または似た表現）を含めてください。
※すでにNoteへの誘導がある場合は、上記の内容を追記・自然に合体させてください。元のハッシュタグなどはそのまま残してください。

必ず以下のJSON形式に従って出力してください:
{
  "new_thread_text": "具体的な用量を削除・修正した新しい投稿文"
}

【元のテキスト】:
"""

def process_file(md_file):
    folder_name = os.path.basename(os.path.dirname(md_file))
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Threads用（長文・専門的）セクションを探す
    threads_match = re.search(r"(## 🧵 Threads用（長文・専門的）.*?\n```text\n)(.*?)(```)", content, re.DOTALL)
    if not threads_match:
        return False, f"[{folder_name}] No Threads section found."

    original_threads_text = threads_match.group(2).strip()

    # 用量表記があるかチェック
    if not dosage_pattern.search(original_threads_text):
        return False, f"[{folder_name}] No dosage matched. Skipping."

    print(f"[{folder_name}] Modifying...")
    
    # APIリトライロジック
    for retry in range(3):
        try:
            response = model.generate_content(REWRITE_PROMPT + original_threads_text)
            data = json.loads(response.text)
            if "new_thread_text" in data:
                new_text = data["new_thread_text"].strip()
                break
        except Exception as e:
            time.sleep(2)
    else:
        return False, f"[{folder_name}] API failed."

    # 置換して保存
    new_content = content.replace(original_threads_text, new_text)
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return True, f"[{folder_name}] Successfully updated."

def main():
    md_files = glob.glob(os.path.join(DRAFTS_DIR, "**", "sns_all_drafts.md"), recursive=True)
    print(f"Total drafts found: {len(md_files)}")
    
    success_count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(process_file, md_files))
        
    for is_success, msg in results:
        if is_success:
            print(msg)
            success_count += 1

    print(f"\nCompleted! Modified {success_count} files.")

if __name__ == "__main__":
    main()
