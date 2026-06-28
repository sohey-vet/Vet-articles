import os
import re
import subprocess
import json
import datetime
import sys

def replace_block(content, header_regex, new_text):
    """Finds the header matching header_regex, then replaces the first ```text block after it with new_text."""
    # Find header
    header_match = re.search(header_regex, content)
    if not header_match:
        return content, False
    
    # Search for ```text after header
    start_pos = header_match.end()
    block_start_match = re.search(r'```text\n', content[start_pos:])
    if not block_start_match:
        return content, False
        
    actual_start = start_pos + block_start_match.end()
    
    # Search for ``` after the text
    block_end_match = re.search(r'\n```', content[actual_start:])
    if not block_end_match:
        return content, None, False
        
    actual_end = actual_start + block_end_match.start()
    
    old_text = content[actual_start:actual_end].strip()
    
    # Replace
    new_content = content[:actual_start] + new_text + content[actual_end:]
    return new_content, old_text, True

def main():
    base_dir = r"C:\Users\souhe\Desktop\PawMedical\VetEvidence_SNS"
    auto_post_dir = os.path.join(base_dir, "VetEvidence_AutoPost")
    desktop_file = os.path.join(auto_post_dir, "今週のThreads修正用.md")
    
    if not os.path.exists(desktop_file):
        print(f"Error: 修正用ファイルが見つかりません。先に抽出を実行してください。 ({desktop_file})")
        input("Press Enter to exit...")
        return
        
    with open(desktop_file, 'r', encoding='utf-8') as f:
        file_content = f.read()
        
    # Split by separator ---
    blocks = file_content.split("---")
    
    success_count = 0
    feedback_entries = []
    
    for block in blocks:
        block = block.strip()
        if not block:
            continue

        # --- 日曜「診察室裏トーク」(ThreadsBot) ブロックの書き戻し ---
        sunday_meta = re.search(r'<!-- SUNDAY_TALK: (.*?) \| FILE: (.*?) -->', block)
        if sunday_meta:
            s_label = sunday_meta.group(1).strip()
            s_file = sunday_meta.group(2).strip()
            s_text_match = re.search(r'```text\n(.*?)\n```', block, re.DOTALL)
            if not s_text_match:
                print(f"Warning: 日曜裏トークの本文ブロックが見つかりません ({s_label})")
                continue
            s_new = s_text_match.group(1).strip()
            s_old = ""
            if os.path.exists(s_file):
                with open(s_file, 'r', encoding='utf-8') as f:
                    s_old = f.read().strip()
            if s_new and s_new != s_old:
                with open(s_file, 'w', encoding='utf-8', newline='') as f:
                    f.write(s_new)
                print(f"Successfully updated (日曜裏トーク): {s_label} -> {s_file}")
                success_count += 1
                feedback_entries.append({
                    "date": datetime.datetime.now().isoformat(),
                    "post_type": f"Sunday Talk ({s_label})",
                    "original_text": s_old,
                    "edited_text": s_new
                })
            else:
                print(f"日曜裏トーク: 変更なし ({s_label})")
            continue

        # Parse metadata
        meta_match = re.search(r'<!-- SOURCE: (.*?) \| TYPE: (.*?) \| HEADER: (.*?) -->', block)
        if not meta_match:
            continue
            
        src = meta_match.group(1).strip()
        post_type = meta_match.group(2).strip()
        header_pattern = meta_match.group(3).strip()
        
        # Parse text content
        text_match = re.search(r'```text\n(.*?)\n```', block, re.DOTALL)
        if not text_match:
            print(f"Warning: Text block not found for {src}")
            continue
            
        new_text = text_match.group(1).strip()
        
        # 500文字制限のチェック (すべてのThreads投稿)
        normalized_text = new_text.replace("\r\n", "\n").replace("\r", "\n")
        text_len = len(normalized_text)
        if text_len > 500:
            print("\n" + "!" * 60)
            print(f"【警告】{src} ({post_type}) の Threads 投稿が 500文字を超えています！ ({text_len}文字)")
            print("このまま反映すると、投稿時にエラーが発生します。")
            print("!" * 60 + "\n")
            ans = input("このまま元のファイルに反映しますか？ (y/N): ").strip().lower()
            if ans != 'y':
                print("反映を中止しました。修正用ファイルを編集してから再度実行してください。")
                import time
                time.sleep(3)
                sys.exit(1)
        
        # Open source file
        md_path = os.path.join(base_dir, src, "sns_all_drafts.md")
        if src == "all_sunday_digests.md":
            md_path = os.path.join(base_dir, src)
            
        if not os.path.exists(md_path):
            print(f"Error: Source file not found: {md_path}")
            continue
            
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Replace block
        new_content, old_text, success = replace_block(content, header_pattern, new_text)
        
        if success:
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Successfully updated: {src} ({post_type})")
            success_count += 1
            
            # Feedback Loop Recording
            if old_text and new_text:
                if old_text != new_text:
                    feedback_entries.append({
                        "date": datetime.datetime.now().isoformat(),
                        "post_type": post_type,
                        "original_text": old_text,
                        "edited_text": new_text
                    })
                else:
                    pass # They are identical
            else:
                print("DEBUG: old_text or new_text is empty")
        else:
            print(f"Failed to find block to replace in {src} for header {header_pattern}")
            
    # Save feedback
    if feedback_entries:
        feedback_file = os.path.join(auto_post_dir, "threads_feedback.json")
        existing_feedback = []
        if os.path.exists(feedback_file):
            try:
                with open(feedback_file, 'r', encoding='utf-8') as f:
                    existing_feedback = json.load(f)
            except:
                pass
        existing_feedback.extend(feedback_entries)
        with open(feedback_file, 'w', encoding='utf-8') as f:
            json.dump(existing_feedback, f, ensure_ascii=False, indent=4)
        print(f"\n{len(feedback_entries)} 件の修正差分を学習データ（threads_feedback.json）に保存しました。")
        
    print(f"\n{success_count} 件の記事を元ファイルに反映しました。")
    print("スケジュールの再構築 (extract_drafts.py) を実行します...")
    
    try:
        subprocess.run(["python", "extract_drafts.py"], cwd=auto_post_dir, check=True)
        print("\n[OK] 全ての処理が完了しました！")
    except Exception as e:
        print(f"\n[Error] extract_drafts.py の実行中にエラーが発生しました: {e}")

    import time
    time.sleep(3)

if __name__ == "__main__":
    main()
