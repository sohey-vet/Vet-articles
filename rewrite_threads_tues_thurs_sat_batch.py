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
model = genai.GenerativeModel('gemini-2.5-flash')

# --- Prompts ---
BASE_PROMPT = """
あなたは診療現場で働くプロフェッショナルな獣医師です。
以下の専門的なテキストや既存のテキストを元に、SNS（Threads等）の短・中文投稿用に【新しいトーン】で文章を書き直してください。

【厳守すべき新しいトーンとルール】
1. ベースの口調は丁寧なコラムのような自然な「です・ます」調としてください。口語になりすぎないよう注意してください。
2. 断定的な表現（「〜しなければなりません」等）や極端な感情表現（ひどい負担、〜ですよね等）を避け、専門家としての覚悟や寄り添いを「〜ことが大切です」「〜していくのです」のように柔らかく表現してください。
3. 【絶対禁止】：「あのコ」「そのコ」「わたし（達）」「お薬」という表現は**絶対に使用しない**でください。主語は自然に省略するか、「ご家族」「薬」などに適宜言い換えてください。翻訳調の不自然な日本語にならないよう注意してください。
  ※【名詞の最適化追加】：対象が犬（または猫）限定の記事と明確な場合は「大切な動物」を「大切な愛犬（愛猫）」などへ適宜変更してください。また「動物の個々の反応」を「個々の反応」とするように、文脈上省略しても通じる名詞（動物など）は極力省略し、不要な語を減らした自然な日本語にしてください。
4. 【絶対禁止】：「〜してございます」「〜と存じます」といった過剰な敬語や謙譲語は**絶対に使用しない**でください。「〜です」「〜ます」といった自然でシンプルな表現に留めてください。
5. 【絶対禁止】：「体言止め」の連発、ポエムのようなキザな文章、極端に短い1文ごとの改行は絶対に避けてください。
6. 改行ルール：意味のまとまり（2〜4文程度）ごとに自然な段落を作り、スマートフォンで読みやすい構成にしてください。
7. 出力文字数は「200〜400字程度」に収めてください。
8. 最後に必ず「詳細な実践法はプロフのNoteリンクにて。」等の自然な誘導を一文加えてください。

出力は、JSON形式などでなく、変換された文章そのもの（プレーンテキスト）のみを出力してください。余分なMarkdown装飾や会話文（例:「はい、以下が作成した文章です」等）は一切含めないでください。

-----------------------------------
【元のテキスト】:
"""

def generate_rewrite(original_text, folder_name, retry=3):
    prompt = BASE_PROMPT + original_text

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
        
    # Match ## 🧵 Threads用（火木土：プランX）.. ```text ... ```
    threads_match = re.search(r"(## 🧵 Threads用（火木土：.*?）.*?\n```text\n)(.*?)(```)", content, re.DOTALL)
    
    if threads_match:
        original_threads_text = threads_match.group(2).strip()
        
        print(f"[{folder_name}] AI Generating...")
        new_text = generate_rewrite(original_threads_text, folder_name)
        
        if new_text:
            # 抽出したブロック内のテキストだけを入れ替える
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
        print(f"[{folder_name}] Could not find original Threads (火木土) block.")
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
