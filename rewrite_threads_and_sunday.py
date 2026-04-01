import os
import glob
import re
import json
import time
import random
from dotenv import load_dotenv
import google.generativeai as genai
from collections import defaultdict
import concurrent.futures

# --- Configuration ---
ENV_PATH = r"C:\Users\souhe\Desktop\論文まとめ\.env"
DRAFTS_DIR = r"C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts"

load_dotenv(ENV_PATH)
if "GEMINI_API_KEY" not in os.environ:
    print("Error: GEMINI_API_KEY not found in .env")
    exit(1)

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})

# --- Prompts ---
REWRITE_PROMPT = """
あなたは情報を分かりやすく伝える獣医師インフルエンサーです。
提供された既存の「Threads用（専門的な長文）」のテキストを読み、内容に応じて以下の【プラン①】か【プラン③】を自動判定し、月・水・金の専門的な解説の翌日（火・木・土）に投稿するための、新しいトーンのThreads投稿文を作成してください。全体の比率としてプラン①が約70%、プラン③が約30%になるよう、命に関わる重篤な疾患や決断が必要な疾患に限りプラン③を選んでください。

【絶対的な禁止ルール】
・あなたの一人称は必ず「わたし」（ひらがな）を使用してください。絶対に「僕」や「俺」などは使用しないでください。

【判定基準とトーンの指示】
■ プラン①（対象：約70%。慢性疾患、軽い疾患、過剰治療が横行しがちな分野）
トーン：「エビデンス vs 現場のリアル」。飼い主の不安や古い常識に寄り添いつつ、「わたしはこうしてます（葛藤と決断）」というプロの姿勢を示す。翌日の投稿として「昨日の〇〇についてのマニアックな記事の補足ですが…」のような入りが効果的です。

■ プラン③（対象：約30%。致死率の高い急患、FIP、癌、外科手術の要否など）
トーン：「究極の当事者目線」。もし自分の愛犬・愛猫がこの病気になったら、迷わずこの治療を選択・または拒否するという強い決断を示す。

【出力要件】
絵文字を適度に使い、Threads特有の親しみやすい（しかし専門家としての権威は失わない）文章にしてください。文字数は200〜400文字程度。
最後に必ず、「詳細なエビデンスと実践法はプロフのNoteで解説しています🔗」という誘導を入れてください。
ハッシュタグは1〜2個程度、文末に追加してください。

必ず以下のJSONスキーマに従って出力してください:
{
  "plan": "1" または "3",
  "reason": "なぜそのプランを選んだのか（20文字程度）",
  "new_thread_text": "生成された新しいThreads用テキスト（一人称『わたし』厳守）"
}

【元のテキスト】:
"""

def generate_rewrite(original_text, retry=3):
    for i in range(retry):
        try:
            response = model.generate_content(REWRITE_PROMPT + original_text)
            data = json.loads(response.text)
            if "new_thread_text" in data and "plan" in data:
                # Basic sanity check
                if "僕" in data["new_thread_text"]:
                    data["new_thread_text"] = data["new_thread_text"].replace("僕", "わたし")
                return data
        except Exception as e:
            time.sleep(2)
    return None

def process_file(md_file):
    folder_name = os.path.basename(os.path.dirname(md_file))
    week_char = folder_name[0]
    day_char = folder_name[1]
    
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    title_match = re.search(r'# 📝 (.*?)\s*-', content)
    title = title_match.group(1).strip() if title_match else folder_name[3:]
    
    art_info = {
        "day": day_char,
        "title": title,
        "folder": folder_name,
        "week_char": week_char
    }
    
    # We look for the main Threads block and check if "火木土" is already there.
    if "火木土：" in content:
        # Already processed
        plan_match = re.search(r"## 🧵 Threads用（火木土：プラン(\d)）", content)
        plan_used = plan_match.group(1) if plan_match else "1"
        return plan_used, art_info

    # Find the original threads block to read its content
    threads_match = re.search(r"(## 🧵 Threads用（長文・専門的）.*?\n```text\n)(.*?)(```)", content, re.DOTALL)
    
    plan_used = None
    
    if threads_match:
        original_threads_text = threads_match.group(2).strip()
        full_original_block = threads_match.group(0) # everything from ## to ```
        
        print(f"[{folder_name}] AI Generating...")
        result = generate_rewrite(original_threads_text)
        if result:
            plan = str(result["plan"])
            plan_used = plan
            new_text = result["new_thread_text"].strip()
            
            # The appended section
            appended_section = f"\n\n---\n\n## 🧵 Threads用（火木土：プラン{plan}）\n\n```text\n{new_text}\n```"
            
            # Insert right after the original threads block ends
            insertion_point = threads_match.end(0)
            new_content = content[:insertion_point] + appended_section + content[insertion_point:]
            
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
        else:
            print(f"[{folder_name}] Failed to generate.")
    else:
        print(f"[{folder_name}] Could not find original Threads block.")
        
    return plan_used, art_info

def generate_sunday_digest(w_idx, week_char, articles):
    # Sort Mon, Wed, Fri
    def day_order(item):
        if item['day'] == '月': return 1
        if item['day'] == '水': return 2
        if item['day'] == '金': return 3
        return 4
    
    arts = sorted(articles, key=day_order)
    # Give them safe defaults in case some days are missing
    t_mon = arts[0]['title'] if len(arts) > 0 else "最新エビデンス"
    t_wed = arts[1]['title'] if len(arts) > 1 else "最新エビデンス"
    t_fri = arts[2]['title'] if len(arts) > 2 else "最新エビデンス"
    
    templates = [
        # Template 1: Action-oriented question
        f"""今週の獣医学エビデンス総まとめ📝\n
今週のNoteでは、診察室で意外と誤解されがちな3つのテーマを取り上げました！\n
✅ {t_mon}
✅ {t_wed}
✅ {t_fri}\n
特に「{t_wed}」のケースでは、「なるほど！」と驚かれた飼い主さんも多かったのではないでしょうか？😊\n
みなさんはどのトピックが一番気になりましたか？ぜひリプライで教えてください💬\n
詳しい解説と最新エビデンスは、すべてプロフのNoteリンクから読めます👇
#獣医 #獣医療アップデート #獣医学""",

        # Template 2: Insider/Behind-the-scenes feel
        f"""【週間ダイジェスト】今週の獣医学アップデート🐾\n
今週も濃い内容をお届けしました。獣医師が普段どんなことを考えて治療方針を決めているか、少しでも伝われば嬉しいです！\n
📌 今週のラインナップ
・月曜：{t_mon}
・水曜：{t_wed}
・金曜：{t_fri}\n
個人的に一番思い入れがあったのは「{t_fri}」の記事です。現場でも本当に悩むことが多いテーマなんですよ🏥\n
もし似たような経験をした方がいれば、感想教えてくださいね！解説用Noteへのリンクはプロフに貼ってあります👇
#一次診療 #動物病院 #現場のリアル""",

        # Template 3: Urgent / Important reminder 
        f"""日曜日のエビデンス振り返りタイム⏰\n
今週解説した3つのテーマ、本当に知っておいて損はない内容ばかりです！動物業界の方も、飼い主さんも必見👀\n
👉 {t_mon}
👉 {t_wed}
👉 {t_fri}\n
「{t_mon}」なんかは、昔と今で常識がかなり変わってきている分野です。知識のアップデート、できていますか？✨\n
気になるテーマがあれば、プロフのNoteリンクから詳細を確認してみてくださいね👇
#獣医 #エビデンスに基づく獣医療 #アップデート""",

        # Template 4: Friendly/Casual summary
        f"""今週のNote記事まとめ📝 みなさん、追いつけていますか？笑\n
ちょっとマニアックな話も多かった今週の投稿、振り返りリストはこちらです👇\n
✅ {t_mon}
✅ {t_wed}
✅ {t_fri}\n
「{t_mon}」や「{t_fri}」について、診察室ではなかなか時間がなくてここまで語れません💦 こうしてSNSで情報共有できるのが嬉しいです！\n
どれか一つでも参考になったら「いいね」で教えてもらえると励みになります😊 記事はプロフのリンクからどうぞ🔗
#獣医学 #獣医療の裏側""",

        # Template 5: Focus on the "why"
        f"""【今週の獣医学エビデンスまとめ】\n
「なぜその治療をするのか？」その"根拠"を知ると、動物医療はもっと見え方が変わります💡\n
今週の3大トピックはこちら：
① {t_mon}
② {t_wed}
③ {t_fri}\n
「なるほど、だからあの時先生はこう言ったのか！」という発見があれば、ぜひコメントで教えてください✨
すべての専門的な解説と根拠は、プロフのNoteリンクから深掘りできます👇
#獣医療エビデンス #一次診療 #動物病院"""
    ]
    
    # We deterministically pick a template based on the week index to ensure variety
    selected_template = templates[w_idx % len(templates)]
    
    out = f"## 第{w_idx+1}週目 ({week_char}週)\n\n```text\n{selected_template}\n```\n\n---\n\n"
    return out

def main():
    md_files = glob.glob(os.path.join(DRAFTS_DIR, "**", "sns_all_drafts.md"), recursive=True)
    plan_counts = {"1": 0, "3": 0}
    week_groups = defaultdict(list)
    
    print(f"Total files to process: {len(md_files)}")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(process_file, md_files))
        
    for plan, art_info in results:
        if plan:
            plan_counts[plan] = plan_counts.get(plan, 0) + 1
        week_groups[art_info["week_char"]].append(art_info)
            
    print(f"Rewrite completed. Plan 1: {plan_counts.get('1', 0)}, Plan 3: {plan_counts.get('3', 0)}")
    
    print("Generating Sunday Digests...")
    digest_output = os.path.join(DRAFTS_DIR, "all_sunday_digests.md")
    
    all_week_chars = list(week_groups.keys())
    
    def map_circle_num(c):
        if '\u2460' <= c <= '\u2473': return ord(c) - 0x2460 + 1 # ①-⑳
        if '\u3251' <= c <= '\u325f': return ord(c) - 0x3251 + 21 # ㉑-㉟
        if c == '㊱': return 36
        return 999
        
    sorted_weeks = sorted(all_week_chars, key=map_circle_num)
    
    with open(digest_output, 'w', encoding='utf-8') as f:
        f.write("# 🗓️ 日曜ダイジェスト 投稿用台本（全36週分）\n\n")
        f.write("これらのテキストは日曜日の昼などにNoteやX、Threadsの「まとめ投稿」としてお使いください。\n\n---\n\n")
        
        for w_idx, week_char in enumerate(sorted_weeks):
            articles = week_groups[week_char]
            f.write(generate_sunday_digest(w_idx, week_char, articles))
            
    print(f"Sunday Digests saved to {digest_output}")

if __name__ == "__main__":
    main()
