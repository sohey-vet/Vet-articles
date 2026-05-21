import os
import re
import subprocess
import json
import datetime

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
    desktop_file = r"C:\Users\souhe\Desktop\今週のThreads修正用.md"
    base_dir = r"C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts"
    auto_post_dir = os.path.join(base_dir, "VetEvidence_AutoPost")
    
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
