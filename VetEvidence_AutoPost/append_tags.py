import os
import glob

def main():
    repo_dir = r"C:\Users\souhe\Desktop\論文まとめ\topics"
    md_files = glob.glob(os.path.join(repo_dir, "**", "*.md"), recursive=True)

    target_titles = [
        "メチシリン耐性菌",
        "犬猫の膀胱炎",
        "前十字靭帯断裂",
        "療法食の選び方",
        "肥満管理"
    ]

    for md_file in md_files:
        basename = os.path.basename(md_file)
        if any(target in basename for target in target_titles):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            if "tags:" not in content and "TAGS" not in content:
                # Append modern tags
                with open(md_file, 'a', encoding='utf-8') as f:
                    f.write("\n\n---\ntags: [その他]\n")
                print(f"Appended tags to {basename}")

if __name__ == "__main__":
    main()
