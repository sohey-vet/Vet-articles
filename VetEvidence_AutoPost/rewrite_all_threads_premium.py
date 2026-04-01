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

# 専門的・長文スレッド用プロンプト（だ・である調、絵文字なし、高密度）
PROMPT_LONG = """
あなたは、現役の獣医師・獣医学生をターゲットにした極めて高度な専門記事を書く執筆者です。
提示された「【参考資料】」の内容を基に、以下の厳格なルールに従って、Threads（月・水・金）用の専門的な長文投稿（300〜450文字程度）を作成してください。

【厳格なルール】
1. 絵文字（😀、⚠️など）は一切使用しないでください。
2. Meta社の自動判定を回避するため、「mg/kg」「μg/kg」「mL/kg」のような【具体的な用量の数値】は絶対に記載しないでください。（例:「テルミサルタン1.0 mg/kg PO」→「テルミサルタンの導入」など）
3. 文末は「〜だ、〜である、〜とする」のような硬派な論文・学術書スタイルで統一してください（「〜です・ます」は禁止）。
4. 獣医師が読んで感銘を受けるレベルの圧倒的な専門用語（病態生理、分子機序、診断基準の詳細、ガイドライン名など）を高密度で盛り込んでください。「適切な対応」「様子を見る」などのペラペラな表現を避け、深い解釈や機序を含めること。
5. 最後の1行は必ず「詳細なエビデンスはプロフのNoteリンクにて。」としてください。ハッシュタグ（2つ程度）を末尾に添えてください。

必ず以下のJSON形式で出力してください:
{
  "new_thread_long": "新しいThreads用の長文（専門的）"
}

【参考資料（Instagram台本など）】:
"""

# エモい・現場のリアルスレッド用プロンプト（です・ます等の多様な語尾、絵文字なし）
PROMPT_SHORT = """
あなたは、飼い主や同業の獣医師に向けて、一次診療の現場の「生の声・葛藤・決断」を語る獣医師インフルエンサーです。
提示された「【参考資料】」と以下のプラン（{plan}）に従って、Threads用の投稿（250〜350文字程度）を作成してください。

【厳格なルール】
1. あなたの一人称は必ず「わたし」（ひらがな）を使用してください。
2. 絵文字（😀、✨、⚠️など）は絶対に、一切使用しないでください。文字だけで勝負してください。
3. 「〜ます。〜ます。」と小学生のように同じ語尾が連続することは絶対に避けてください。体言止め、倒置法、「〜に他ならない」「〜と実感する」「〜という判断だ」など、語彙力豊かで洗練された知的な大人の文章にしてください。「ペラペラでバカっぽく」見えない知的なトーンを維持すること。
4. 最後の1行は必ず「詳細な実践法はプロフのNoteリンクにて。」としてください。ハッシュタグ（2つ程度）を末尾に添えてください。

【プラン指示】
■ プラン1: 「エビデンス vs 現場のリアル」。飼い主の不安や古い常識に寄り添いつつ、理想（ガイドライン）と現実（費用、副作用、性格）の狭間でのプロの葛藤と決断を示す。
■ プラン3: 「究極の当事者目線」。もし自分の愛犬・愛猫が致死的・重篤な病気になったら、迷わずこの治療を選択・または拒否するという覚悟と強い決断を示す。

必ず以下のJSON形式で出力してください:
{
  "new_thread_short": "新しいThreads用の短文"
}

【参考資料】:
"""

def generate_rewrite(prompt, context, retry=3):
    for i in range(retry):
        try:
            response = model.generate_content(prompt + context)
            data = json.loads(response.text)
            return data
        except Exception as e:
            time.sleep(2)
    return None

def process_file(md_file):
    folder_name = os.path.basename(os.path.dirname(md_file))
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # プラン情報を取得
    plan = "1"
    if "プラン3" in content:
        plan = "3"

    # Instagram用データを含む全体コンテキストを抽出（タイトル除く本文すべて）
    context = content[content.find("## 🐦 X"):]

    print(f"[{folder_name}] Generating Long Thread...")
    long_res = generate_rewrite(PROMPT_LONG, context)
    
    print(f"[{folder_name}] Generating Short Thread (Plan {plan})...")
    short_prompt = PROMPT_SHORT.replace("{plan}", f"プラン{plan}")
    short_res = generate_rewrite(short_prompt, context)

    if not long_res or not short_res:
        return False, f"[{folder_name}] API failed."

    new_long = long_res.get("new_thread_long", "").strip()
    new_short = short_res.get("new_thread_short", "").strip()

    # 置換対象のブロックを見つける
    # ## 🧵 Threads用（長文・専門的） から ## 🟣 Instagram用 の直前まで
    threads_section_regex = re.compile(r"(## 🧵 Threads用（長文・専門的）.*?\n)(## 🟣 Instagram用)", re.DOTALL)
    
    if not threads_section_regex.search(content):
        return False, f"[{folder_name}] Could not find threads section bounds."

    new_threads_section = f"## 🧵 Threads用（長文・専門的）\n\n```text\n{new_long}\n```\n\n---\n\n## 🧵 Threads用（火木土：プラン{plan}）\n\n```text\n{new_short}\n```\n\n---\n\n## 🟣 Instagram用"

    new_content = threads_section_regex.sub(new_threads_section, content)

    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return True, f"[{folder_name}] Successfully generated premium threads."

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

    print(f"\nCompleted! Upgraded {success_count} files.")

if __name__ == "__main__":
    main()
