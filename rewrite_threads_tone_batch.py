import os
import glob
import re
import time
import concurrent.futures
from dotenv import load_dotenv
import google.generativeai as genai

# --- Configuration ---
ENV_PATH = r"C:\Users\souhe\Desktop\論文まとめ\.env"
DRAFTS_DIR = r"C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts"

load_dotenv(ENV_PATH)
if "GEMINI_API_KEY" not in os.environ:
    print("Error: GEMINI_API_KEY not found in .env")
    exit(1)

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
# 長文かつ洗練されたトーンの出力のため、プロモデルかフラッシュモデルを利用
# ここでは推敲力が求められるため、gemini-2.5-pro があればベターですが、安定動作のためgemini-2.5-flash または pro を使用
model = genai.GenerativeModel('gemini-2.5-flash')

# --- Prompts ---
BASE_PROMPT = """
あなたは情報を正確かつ分かりやすく伝える獣医師です。
以下の専門的なテキストを元に、SNS（Threads等）向けの長文投稿用テキストに推敲してください。

【絶対的な厳守ルール】
1. 私見や過度な感情表現（「〜ですね」「〜ですよね💦」など）は絶対に入れないでください。客観的な事実のみを伝えます。
2. 「ハンドリングストレス」「イノダイレーター」のような、日本の一般臨床現場で馴染みの薄いカタカナ用語は避け、平易な専門用語（例:「保定などのストレス」「強心薬」）に変換してください。
3. すべて「〜です」「〜ます」で終わらせず、適度に「体言止め」を交えて文章のリズムを洗練させてください。形式的な「体言止め＋です・ます」の機械的な繰り返しは避け、自然でプロフェッショナルな読み味を心がけてください。
4. {length_instruction}
5. 絵文字は不要または最小限（段落の区切り程度のみ）にしてください。

出力は、JSON形式などでなく、変換された文章そのもの（プレーンテキスト）のみを出力してください。余分なMarkdown装飾や会話文（例:「はい、以下が作成した文章です」等）は一切含めないでください。

-----------------------------------
【元のテキスト】:
"""

def generate_rewrite(original_text, folder_name, retry=3):
    # 中毒の記事だけ例外的に長めにする処理
    if "中毒" in folder_name:
        length_instruction = "文字数は原則「600文字程度」に増量して詳しく記述してください。"
    else:
        length_instruction = "文字数は原則「400〜450文字程度」に収めてください。"
        
    prompt = BASE_PROMPT.format(length_instruction=length_instruction) + original_text

    for i in range(retry):
        try:
            response = model.generate_content(prompt)
            result_text = response.text.strip()
            
            # APIの不要なマークダウンやプレフィックスを取り除く
            if result_text.startswith("```"):
                result_text = re.sub(r"^```.*?\n", "", result_text)
                result_text = re.sub(r"\n```$", "", result_text)
                
            return result_text.strip()
        except Exception as e:
            print(f"[{folder_name}] API Error: {e}. Retrying...")
            time.sleep(3)
    return None

def process_file(md_file):
    folder_name = os.path.basename(os.path.dirname(md_file))
    
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Match ## 🧵 Threads用（長文・専門的）.. ```text ... ```
    threads_match = re.search(r"(## 🧵 Threads用（長文.*?）.*?\n```text\n)(.*?)(```)", content, re.DOTALL)
    
    if threads_match:
        original_threads_text = threads_match.group(2).strip()
        
        print(f"[{folder_name}] AI Generating...")
        new_text = generate_rewrite(original_threads_text, folder_name)
        
        if new_text:
            # 抽出したブロック内のテキストだけを入れ替える
            # グループ1が開始タグ、グループ3が終了タグ
            insertion_point_start = threads_match.end(1)
            insertion_point_end = threads_match.start(3)
            
            new_content = content[:insertion_point_start] + new_text + "\n" + content[insertion_point_end:]
            
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        else:
            print(f"[{folder_name}] Failed to generate.")
            return False
    else:
        print(f"[{folder_name}] Could not find original Threads block.")
        return False
        
def main():
    md_files = glob.glob(os.path.join(DRAFTS_DIR, "**", "sns_all_drafts.md"), recursive=True)
    
    print(f"Total files to process: {len(md_files)}")
    
    # 並行処理で一気にリライト
    success_count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(process_file, md_files))
        success_count = sum(1 for r in results if r)
            
    print(f"Rewrite completed. Successfully generated: {success_count} / {len(md_files)}")

if __name__ == "__main__":
    main()
