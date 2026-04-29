import os
import re
import json
from datetime import datetime, timedelta, date
import sys

# ----- 設定 -----
DRAFTS_ROOT = r"C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# 正規表現パターン
PATTERN_1_RE = re.compile(r"### パターン1.*?\n```text\n(.*?)\n```", re.DOTALL)
PATTERN_2_RE = re.compile(r"### パターン2.*?\n```text\n(.*?)\n```", re.DOTALL)
THREADS_LONG_RE = re.compile(r"## 🧵 Threads用（長文.*?）.*?\n```text\n(.*?)\n```", re.DOTALL)
THREADS_SHORT_RE = re.compile(r"## 🧵 Threads用（火木土：プラン.*?）.*?\n```text\n(.*?)\n```", re.DOTALL)

def extract_content(text, pattern):
    match = pattern.search(text)
    if match:
        return match.group(1).strip()
    return ""

def extract_sunday_digests():
    digest_md_path = os.path.join(DRAFTS_ROOT, "all_sunday_digests.md")
    if not os.path.exists(digest_md_path):
        return []
    with open(digest_md_path, "r", encoding="utf-8") as f:
        content = f.read()
    matches = re.findall(r"## 第\d+週目.*?\n```text\n(.*?)\n```", content, re.DOTALL)
    return [m.strip() for m in matches]

def clean_markdown(text):
    if not text: return text
    # Convert markdown bold to Japanese solid brackets
    text = re.sub(r'\*\*(.*?)\*\*', r'【\1】', text)
    return text

def append_cta(text, platform):
    if not text: return text
    
    # 既にNoteのリンクが含まれている場合は重複を避けるために追加しない
    if "note.com/paw" in text.lower() or "Noteで詳しく" in text:
        return text

    if platform == "X":
        cta = "\n\n詳細・エビデンスはNoteへ👇\nhttps://note.com/pawmedical_jp"
    elif platform == "Threads":
        # Threadsはシャドウバン対策の「URL完全排除絶対ルール」に従い、本文にはURLを一切付加しない
        # (プロフ誘導CTAはauto_post_threads.pyのロジックで自動的にリプライツリーに生成・付加されます)
        return text
    else:
        cta = "\n\n🔗 https://note.com/pawmedical_jp"
    return text + cta


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    print("🐾 VetEvidence SNS Draft エクストラクター")
    
    if not os.path.exists(DRAFTS_ROOT):
        print(f"❌ 下書きフォルダが見つかりません: {DRAFTS_ROOT}")
        return

    articles = []
    
    # フォルダ一覧を取得してソート（①, ②, ③... というプレフィックス順）
    folders = []
    for item in os.listdir(DRAFTS_ROOT):
        item_path = os.path.join(DRAFTS_ROOT, item)
        if os.path.isdir(item_path):
            # 例: "①月_下痢_..." から数値を抽出してソートキーにする
            # 汎用的に先頭の丸数字などをパースするのは難しいため、文字列ソートで代用、
            # あるいは更新日順などで対応するか、週(W21)の情報を元に並べる。
            folders.append(item)
            
    # ①, ② などの丸数字を考慮した簡易ソート（文字コード順で概ね並ぶ）
    folders.sort()

    for folder_name in folders:
        # sns_all_drafts.md を探す
        draft_md_path = os.path.join(DRAFTS_ROOT, folder_name, "sns_all_drafts.md")
        if not os.path.exists(draft_md_path):
            continue
            
        with open(draft_md_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        pat1 = extract_content(content, PATTERN_1_RE)
        pat2 = extract_content(content, PATTERN_2_RE)
        threads_long = extract_content(content, THREADS_LONG_RE)
        threads_short = extract_content(content, THREADS_SHORT_RE)
        
        if pat1 or pat2 or threads_long or threads_short:
            articles.append({
                "folder": folder_name,
                "x_pattern1": pat1,
                "x_pattern2": pat2,
                "threads_long": threads_long,
                "threads_short": threads_short
            })
            
    print(f"✅ {len(articles)}件の記事ドラフトを抽出しました。")
    sunday_digests = extract_sunday_digests()
    print(f"✅ {len(sunday_digests)}件の日曜ダイジェストを抽出しました。")
    
    # スケジュール割り当てロジック
    # 常に固定の開始日（2026年3月30日月曜日）を基準としてカレンダーを生成する
    start_monday = date(2026, 3, 30)
    
    schedule = []
    current_date = start_monday
    
    for i, article in enumerate(articles):
        # 1記事につき、月水金のいずれかの日（Day 1）と、その翌日の火木土（Day 2）を使用
        # i=0 -> 月(Day1), 火(Day2)
        # i=1 -> 水(Day1), 木(Day2)
        # i=2 -> 金(Day1), 土(Day2)
        # i=3 -> 翌週の月(Day1), 火(Day2) ...
        
        week_offset = i // 3
        day_index = i % 3  # 0:月, 1:水, 2:金
        
        day1_offset = week_offset * 7 + (day_index * 2) # 月曜からのオフセット: 0, 2, 4
        day1_date = start_monday + timedelta(days=day1_offset)
        day2_date = day1_date + timedelta(days=1)
        
        # Day 1: 月・水・金 -> X(パターン1) と Threads
        schedule.append({
            "date": day1_date.isoformat(),
            "platform": "X",
            "content": append_cta(clean_markdown(article["x_pattern1"]), "X"),
            "source": article["folder"],
            "type": "Pattern 1"
        })
        if article.get("threads_long"):
            schedule.append({
                "date": day1_date.isoformat(),
                "platform": "Threads",
                "content": append_cta(clean_markdown(article["threads_long"]), "Threads"),
                "source": article["folder"],
                "type": "Threads Long"
            })
        
        # Day 2: 火・木・土 -> X(パターン2) と Threads (Short)
        if article.get("x_pattern2"):
            schedule.append({
                "date": day2_date.isoformat(),
                "platform": "X",
                "content": append_cta(clean_markdown(article["x_pattern2"]), "X"),
                "source": article["folder"],
                "type": "Pattern 2"
            })
        if article.get("threads_short"):
            schedule.append({
                "date": day2_date.isoformat(),
                "platform": "Threads",
                "content": append_cta(clean_markdown(article["threads_short"]), "Threads"),
                "source": article["folder"],
                "type": "Threads Short"
            })
            
        # Day 7 (日曜日) -> 1週間の締めくくりにダイジェスト追加
        if day_index == 2 and week_offset < len(sunday_digests):
            sunday_date = start_monday + timedelta(days=week_offset * 7 + 6)
            digest_text = sunday_digests[week_offset]
            schedule.append({
                "date": sunday_date.isoformat(),
                "platform": "X",
                "content": digest_text,
                "source": "all_sunday_digests.md",
                "type": "Sunday Digest"
            })
            schedule.append({
                "date": sunday_date.isoformat(),
                "platform": "Threads",
                "content": digest_text,
                "source": "all_sunday_digests.md",
                "type": "Sunday Digest"
            })
        
    # JSONとして保存
    output_file = os.path.join(OUTPUT_DIR, "sns_schedule.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(schedule, f, ensure_ascii=False, indent=2)
        
    print(f"📅 スケジュール生成完了: {output_file}")
    print(f"最初の投稿予定日: {start_monday.isoformat()}")

if __name__ == "__main__":
    main()
