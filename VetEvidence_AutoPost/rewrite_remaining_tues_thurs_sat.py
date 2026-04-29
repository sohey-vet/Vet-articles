import os
import glob
import re
import time
import json
import sys
import concurrent.futures
from dotenv import load_dotenv
import google.generativeai as genai

# --- Configuration ---
ENV_PATH = r"C:\Users\souhe\Desktop\論文まとめ\.env"
DRAFTS_DIR = r"C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts"
SCHEDULE_FILE = os.path.join(DRAFTS_DIR, "VetEvidence_AutoPost", "sns_schedule.json")
START_DATE = "2026-04-21"

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

load_dotenv(ENV_PATH)
if "GEMINI_API_KEY" not in os.environ:
    print("Error: GEMINI_API_KEY not found in .env")
    exit(1)

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

# --- 🎯 Dr. Sohey Tone & Manner Prompts ---
BASE_PROMPT = """
あなたは臨床経験20年のプロフェッショナルな救急専任獣医師です。以下の【元のテキスト】（SNS用ドラフト一式）を全て読み込み、Threads用の引用投稿文（300文字〜400文字程度）を新規に作成してください。

【厳守すべきライティングルール】
1. **ペルソナとトーン**: 「臨床歴20年のベテラン獣医師が、現場で後輩獣医師（代診医）に対して、具体的なエビデンスや手技のコツを教え、甘い判断を正している」というトーンで書いてください。
2. **生きた言葉（口語化）**: 「〜と言えるでしょう」「〜に直結します」といったAI的な硬い表現は避け、「〜ですね」「〜がセオリーです」「〜に注意してください」など、現場で話しかけているような自然な言葉遣いにしてください。
3. **内容の正確性と深み**: 元のテキスト（特にInstagram用の詳細スライド部分）から「なぜそうするのか（病態的理由）」「具体的な基準値」「現場で陥りやすいミス」を正確に抽出し、実践的に役立つレベルの深みを持たせてください。
4. **CTAの完全廃止**: 投稿の最後や途中に「詳細はプロフィールのリンクへ」「Noteにてご確認いただけます」といった誘導文（CTA）は**絶対に**含めないでください。純粋な医学的つぶやきとして完結させてください。
5. **不要なカッコ書きの排除**: 略語の説明などで余計な「()」や「（）」を使わないでください。ただし、「胸水の性状検査（TG、ブドウ糖、乳酸など）」のように、列挙して具体例を示すためのカッコは使用して構いません。
6. **不要な語り・ポエムの排除**: 「寄り添います」「最善を尽くします」といった感情的な表現は一切不要です。
7. **「私見」「当院」の禁止**: エビデンスに基づかない独自の推測や、「当院では」といった特定の病院を連想させる表現は含めないでください。

※出力は、マークダウンや引用符などを含めず、変換されたプレーンテキストのみを出力してください。挨拶や余分な解説は一切不要です。
-----------------------------------
【元のテキスト（ドラフト全体）】:
"""

def generate_rewrite(original_text, folder_name, retry=3):
    prompt = BASE_PROMPT + original_text

    for i in range(retry):
        try:
            response = model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Remove any unwanted markdown formatting if the model still outputs it
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
        
    threads_match = re.search(r"(## 🧵 Threads用（火木土：.*?）.*?\n```text\n)(.*?)(```)", content, re.DOTALL)
    
    if threads_match:
        print(f"[{folder_name}] AI Generating...")
        
        # NOTE: Pass entire 'content' to AI
        new_text = generate_rewrite(content, folder_name)
        
        if new_text:
            insertion_point_start = threads_match.end(1)
            insertion_point_end = threads_match.start(3)
            
            new_content = content[:insertion_point_start] + new_text + "\n" + content[insertion_point_end:]
            
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"[{folder_name}] Successfully updated.")
            return True
        else:
            print(f"[{folder_name}] Failed to generate.")
            return False
    else:
        print(f"[{folder_name}] Could not find original Threads (火木土) block.")
        return False

def main():
    print("Starting Batch Rewrite for unposted Threads Short (from {})...".format(START_DATE))
    
    # 1. ターゲットとなるフォルダ（source）のリストを抽出
    if not os.path.exists(SCHEDULE_FILE):
        print(f"Error: {SCHEDULE_FILE} not found.")
        return
        
    with open(SCHEDULE_FILE, 'r', encoding='utf-8') as f:
        schedule = json.load(f)
        
    target_folders = set()
    for item in schedule:
        if item.get("platform") == "Threads" and item.get("type") == "Threads Short":
            if item.get("date", "") >= START_DATE:
                target_folders.add(item.get("source"))
                
    print(f"Found {len(target_folders)} target articles to rewrite.")
    
    if not target_folders:
        return
        
    # 2. 該当フォルダの md ファイルパスを作成
    md_files = []
    for base_folder in target_folders:
        # source might be folder name
        path = os.path.join(DRAFTS_DIR, base_folder, "sns_all_drafts.md")
        if os.path.exists(path):
            md_files.append(path)
            
    print(f"Found {len(md_files)} md files to process.")
    
    # 3. 並列処理で一気にリライト
    success_count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(process_file, md_files))
        success_count = sum(1 for r in results if r)
            
    print(f"Rewrite completed! Successfully generated: {success_count} / {len(md_files)}")

if __name__ == "__main__":
    main()
