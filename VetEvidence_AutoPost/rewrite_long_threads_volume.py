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

# 専門的・長文スレッド用プロンプト
# ボリュームアップ（400〜450字）、体言止め強化（「〜だ。」禁止）、特定URLの確実な付与
PROMPT_LONG = """
あなたは、現役の獣医師・獣医学生をターゲットにした極めて高度な専門記事を書く執筆者です。
提示された「【参考資料】」の内容を基に、以下の厳格なルールに従って、Threads（月・水・金）用の「最も深く密度の濃い」長文投稿を作成してください。

【文字数とレイアウトの絶対ルール】
1. 文字数は「本文のみ（末尾のURL等含まず）で400文字〜450文字前後」という特大ボリュームにすること。
中身が「ペラペラ」にならないよう、Instagram台本内にある深い医学的なメカニズム、病態生理、各種薬剤名、ガイドライン、診断基準（ただし【用量数値以外】）を限界まで詰め込んでください。結果的に長すぎて自動投稿時にスレッドが2つに分割されても構いません。
2. スマートフォンで読みやすいよう、一文や読点の区切りごとに確実な改行（空白行）を入れ、視覚的にスッキリとした美しいレイアウトにすること。

【語尾と文体の絶対ルール】
3. 全編を通じて「〜だ。」という表現を【完全禁止】とします。「不可欠だ。」「重要だ。」などの表現は絶対に使わないでください。
4. 代わりに、名詞で終わる「体言止め（〜。）」を多用するか、「〜である」「〜と考えられる」「〜を推奨する」「〜される」を用い、文末を非常に美しく洗練された論文調で引き締めてください。
5. 本文において絵文字は【完全禁止】です。
6. 「mg/kg」「μg/kg」「mL/kg」のような【具体的な薬剤の用量数値】はMeta社規定回避のため【絶対禁止】です。（薬剤名自体や投与ルートは記載可）

【必須の結び（完全一致）】
7. 文章の一番最後に、以下の3行を【一言一句変えずに】そのまま付与してください。（ここでは💡と🔗の絵文字を使用して良い）

💡疾患の詳細や最新エビデンスはNoteで詳しく解説！
🔗 https://note.com/pawmedical_jp/
#（参考資料から適切なものを1つ） #（もう1つ）

必ず以下のJSON形式で出力してください:
{
  "new_thread_long": "条件を満たした新しい長文Threads投稿"
}

【参考資料】:
"""

def generate_rewrite(prompt, context, retry=3):
    for i in range(retry):
        try:
            response = model.generate_content(prompt + context)
            data = json.loads(response.text)
            if "new_thread_long" in data:
                return data
        except Exception as e:
            time.sleep(2)
    return None

def process_file(md_file):
    folder_name = os.path.basename(os.path.dirname(md_file))
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Instagram用データを含む全体コンテキストを抽出（タイトル除く本文すべて）
    context_start = content.find("## 🐦 X")
    if context_start == -1:
        context_start = 0
    context = content[context_start:]

    print(f"[{folder_name}] Generating Expanded Long Thread...")
    long_res = generate_rewrite(PROMPT_LONG, context)
    
    if not long_res:
        return False, f"[{folder_name}] API failed."

    new_long = long_res.get("new_thread_long", "").strip()

    # 置換対象のブロックを見つける
    # ## 🧵 Threads用（長文・専門的） から --- まで（または次の## 🧵まで）
    long_match = re.search(r"(## 🧵 Threads用（長文・専門的）\n+\s*```text\n)(.*?)(```)", content, re.DOTALL)
    
    if not long_match:
        return False, f"[{folder_name}] Could not find long thread section."

    orig_block = long_match.group(0)
    new_block = f"## 🧵 Threads用（長文・専門的）\n\n```text\n{new_long}\n```"

    new_content = content.replace(orig_block, new_block)

    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return True, f"[{folder_name}] Successfully generated volume up threads."

def main():
    md_files = glob.glob(os.path.join(DRAFTS_DIR, "**", "sns_all_drafts.md"), recursive=True)
    print(f"Total files: {len(md_files)}")
    
    success_count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(process_file, md_files))
        
    for is_success, msg in results:
        print(msg)
        if is_success:
            success_count += 1

    print(f"\nCompleted! Enhanced {success_count} files.")

if __name__ == "__main__":
    main()
