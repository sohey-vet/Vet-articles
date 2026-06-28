import json
import os
import datetime
import re

# 日曜「診察室裏トーク」(ThreadsBot) の設定 -----------------------------------
# 投稿システムは C:\Users\souhe\Documents\ThreadsBot に分離している。
# ローテは日付基準: 2026-07-05(日) を post1 のアンカーとし、以降4週ローテ。
# schedule_today.ps1 の投稿選択ロジックと完全に同じ式にすること（編集＝実投稿の保証）。
THREADSBOT_DIR = r"C:\Users\souhe\Documents\ThreadsBot"
SUNDAY_ANCHOR = datetime.date(2026, 7, 5)  # post1
SUNDAY_NAMES = {
    1: "第1週 日曜カルテ（共感）",
    2: "第2週 あるある翻訳（実用）",
    3: "第3週 先輩の独白（人柄）",
    4: "第4週 季節の注意（保存）",
}

def sunday_talk_index(sunday_date):
    """その日曜にあたる post 番号(1-4)を日付から算出する。"""
    weeks = (sunday_date - SUNDAY_ANCHOR).days // 7  # Pythonの//は負でも床関数
    return (weeks % 4) + 1  # Pythonの%は常に非負

def extract_block(content, header_regex):
    """Finds the header matching header_regex, then extracts the first ```text block after it."""
    # Find header
    header_match = re.search(header_regex, content)
    if not header_match:
        return None
    
    # Search for ```text after header
    start_pos = header_match.end()
    block_start_match = re.search(r'```text\n', content[start_pos:])
    if not block_start_match:
        return None
        
    actual_start = start_pos + block_start_match.end()
    
    # Search for ``` after the text
    block_end_match = re.search(r'```', content[actual_start:])
    if not block_end_match:
        return None
        
    actual_end = actual_start + block_end_match.start()
    
    return content[actual_start:actual_end].strip()

def main():
    base_dir = r"C:\Users\souhe\Desktop\PawMedical\VetEvidence_SNS"
    auto_post_dir = os.path.join(base_dir, "VetEvidence_AutoPost")
    schedule_file = os.path.join(auto_post_dir, "sns_schedule.json")
    
    if not os.path.exists(schedule_file):
        print(f"Error: Schedule file not found at {schedule_file}")
        return

    today = datetime.date.today()
    # 週末（土・日）に実行した場合は、翌週（月曜始まり）の予定を抽出するように判定
    if today.weekday() >= 5:
        monday = today + datetime.timedelta(days=(7 - today.weekday()))
    else:
        monday = today - datetime.timedelta(days=today.weekday())
    dates_this_week = [(monday + datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    
    with open(schedule_file, 'r', encoding='utf-8') as f:
        schedule = json.load(f)
        
    schedule_this_week = []
    for item in schedule:
        if item.get("platform") == "Threads" and item.get("date") in dates_this_week:
            schedule_this_week.append(item)
            
    # Sort by date
    schedule_this_week = sorted(schedule_this_week, key=lambda x: x['date'])
    
    days_ja = ["月", "火", "水", "木", "金", "土", "日"]
    
    output_lines = [
        f"# 📝 今週のThreads投稿 修正用ファイル ({dates_this_week[0]} 〜 {dates_this_week[-1]})",
        "このファイルを修正して保存し、「2_修正を反映して保存.bat」を実行すると元のファイルが更新されます。",
        "※ `<!-- SOURCE: ... -->` の行はシステムが使用するため変更・削除しないでください。",
        ""
    ]
    
    for item in schedule_this_week:
        dt = datetime.datetime.strptime(item['date'], "%Y-%m-%d")
        day_str = days_ja[dt.weekday()]
        
        post_type = item.get("type", "Unknown")
        src = item.get("source")

        # 日曜は「診察室裏トーク」(ThreadsBot) に一本化済み。古いダイジェスト枠はループ後に専用ブロックで差し込むのでここでは飛ばす。
        if post_type == "Sunday Digest":
            continue

        display_type = "メイン記事" if post_type == "Threads Long" else "引用投稿" if post_type == "Threads Short" else post_type
        
        md_path = os.path.join(base_dir, src, "sns_all_drafts.md")
        if src == "all_sunday_digests.md":
            md_path = os.path.join(base_dir, src)
            
        if not os.path.exists(md_path):
            continue
            
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        extracted_text = ""
        header_pattern = ""
        
        if post_type == "Threads Long":
            header_pattern = r'## 🧵 Threads用（長文・専門的）'
        elif post_type == "Threads Short":
            header_pattern = r'## 🧵 Threads用（火木土.*）'
        elif post_type == "Sunday Digest":
            # Find the index of this digest to find the week number
            # Using the content directly from schedule to match, or matching "第X週目"
            # It's easier to just use the content from schedule since it's already there!
            # But wait, we want to extract from the source md so we can edit it and write it back.
            # However, the user wants to edit it. If we use the schedule text, we still have to write it back.
            # Let's find the week number from the dates. The schedule json has "Sunday Digest" for Threads.
            # Let's just use the content directly from the JSON for Sunday Digest, but how do we sync it back?
            # Sync back requires knowing WHICH week it is in all_sunday_digests.md.
            pass
            
        # For all cases, we can actually just extract it from the file if we know the header, OR we can just use the content in the json!
        # But wait, if we use the content in the json, how do we write it back to sns_all_drafts.md? We must update sns_all_drafts.md!
        
        # Let's refine the Sunday Digest extraction.
        # How to find which week? The schedule script parses all_sunday_digests.md in order.
        # Let's just match the exact text from the JSON inside the md file to find the block!
        
        if post_type == "Sunday Digest":
            # For Sunday digest, we can just find the text block that exactly matches item['content'].
            # But what if there are slight whitespace differences?
            # Let's just search for the exact content string in the file, and its surrounding header.
            # Actually, the header in all_sunday_digests.md is `## 第N週目 (〇週)`.
            json_content = item.get("content", "").strip()
            # Find json_content in content
            idx = content.find(json_content)
            if idx != -1:
                # Find the nearest ## before it
                before = content[:idx]
                h_idx = before.rfind("## ")
                if h_idx != -1:
                    header_line = before[h_idx:].split('\n')[0].strip()
                    header_pattern = re.escape(header_line)
                    
        extracted_text = extract_block(content, header_pattern) if header_pattern else item.get("content", "")
        
        output_lines.append(f"## [{item['date']} {day_str}曜日] {display_type}")
        output_lines.append(f"<!-- SOURCE: {src} | TYPE: {post_type} | HEADER: {header_pattern} -->")
        output_lines.append("```text")
        output_lines.append(extracted_text if extracted_text else item.get("content", ""))
        output_lines.append("```")
        output_lines.append("")
        output_lines.append("---")
        output_lines.append("")

    # --- 週末の日曜「診察室裏トーク」(ThreadsBot) を月〜土の続きに差し込む ---
    sunday_date = datetime.datetime.strptime(dates_this_week[-1], "%Y-%m-%d").date()
    s_idx = sunday_talk_index(sunday_date)
    s_file = os.path.join(THREADSBOT_DIR, f"post{s_idx}.txt")
    if os.path.exists(s_file):
        with open(s_file, 'r', encoding='utf-8') as f:
            s_text = f.read().strip()
        s_name = SUNDAY_NAMES.get(s_idx, f"post{s_idx}")
        output_lines.append(f"## [{dates_this_week[-1]} 日曜日] 診察室裏トーク（{s_name}）")
        output_lines.append(f"<!-- SUNDAY_TALK: post{s_idx} | FILE: {s_file} -->")
        output_lines.append("```text")
        output_lines.append(s_text)
        output_lines.append("```")
        output_lines.append("")
        output_lines.append("---")
        output_lines.append("")
    else:
        print(f"Warning: 日曜裏トークの元ファイルが見つかりません: {s_file}")

    desktop_file = os.path.join(auto_post_dir, "今週のThreads修正用.md")
    with open(desktop_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(output_lines))
        
    print(f"Extraction complete! Created {desktop_file}")
    os.startfile(desktop_file)

if __name__ == "__main__":
    main()
