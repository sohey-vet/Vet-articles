import os
import glob
import re

def update_markdown_tags(md_file_path, add_tag):
    with open(md_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Try modern tags: [A, B] format
    match = re.search(r'tags:\s*\[(.*?)\]', content)
    if match:
        current_tags_str = match.group(1)
        current_tags_list = [t.strip() for t in current_tags_str.split(',') if t.strip()]

        if add_tag not in current_tags_list:
            new_tags_list = [add_tag] + current_tags_list
            new_tags_str = ", ".join(new_tags_list)
            new_content = content.replace(f"tags: [{current_tags_str}]", f"tags: [{new_tags_str}]")
            
            with open(md_file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated [modern] {os.path.basename(md_file_path)}: tags: [{new_tags_str}]")
            return True
        return False

    # 2. Try legacy TAGS\n... format
    match_legacy = re.search(r'TAGS\n(.*?)\n', content)
    if match_legacy:
        current_tags_str = match_legacy.group(1)
        if add_tag not in current_tags_str:
            new_tags_str = f"{add_tag}{current_tags_str}"
            new_content = content.replace(f"TAGS\n{current_tags_str}", f"TAGS\n{new_tags_str}")
            with open(md_file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated [legacy] {os.path.basename(md_file_path)}: TAGS\n{new_tags_str}")
            return True
        return False

    print(f"No tag list found in {md_file_path}")
    return False

def main():
    repo_dir = r"C:\Users\souhe\Desktop\論文まとめ\topics"
    md_files = glob.glob(os.path.join(repo_dir, "**", "*.md"), recursive=True)

    target_titles = [
        "抗菌薬選択の基本原則",
        "療法食の選び方",
        "周術期の抗菌薬",
        "手作り食",
        "前十字靭帯断裂",
        "メチシリン耐性菌",
        "肥満管理",
        "膝蓋骨脱臼",
        "犬猫の膀胱炎"
    ]

    updated_count = 0
    for md_file in md_files:
        basename = os.path.basename(md_file)
        if any(target in basename for target in target_titles):
            if update_markdown_tags(md_file, "その他"):
                updated_count += 1
                
    print(f"Total updated: {updated_count} files.")

if __name__ == "__main__":
    main()
