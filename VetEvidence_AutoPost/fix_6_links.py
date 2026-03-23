import re
import os

def main():
    repo_dir = r"C:\Users\souhe\Desktop\論文まとめ"
    index_path = os.path.join(repo_dir, "index.html")

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    mappings = [
        ("犬の免疫介在性血小板減少症（ITP）", "topics/免疫/ITP_診断と治療.html"),
        ("猫の動脈血栓塞栓症（ATE）", "topics/循環器/猫の動脈血栓塞栓症ATE_救急対応.html"),
        ("DIC ─ 診断と治療", "topics/救急/DIC_診断と治療.html"),
        ("猫の尿道閉塞 ─ 救急対応フロー", "topics/救急/猫の尿道閉塞_救急対応フロー.html"),
        ("産褥テタニー（産後低Ca血症）", "topics/救急/産褥テタニー_産後低Ca血症_救急対応.html"),
        ("犬猫の膀胱炎 ─ ISCAIDガイドライン準拠", "topics/腎泌尿器/犬猫の膀胱炎_ISCAIDガイドライン.html"),
    ]

    for title_hint, correct_href in mappings:
        # find the index of the title
        title_idx = html.find(title_hint)
        if title_idx == -1:
            print(f"Warning: could not find {title_hint} in index.html")
            continue
            
        # backtrack to href="
        href_attr_start = html.rfind('href="', 0, title_idx)
        if href_attr_start == -1:
            continue
            
        href_attr_end = html.find('"', href_attr_start + 6)
        
        old_href = html[href_attr_start+6:href_attr_end]
        
        # replace just for this specific position
        html = html[:href_attr_start+6] + correct_href + html[href_attr_end:]
        print(f"Replaced {old_href} -> {correct_href}")

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)
        
    print("Link fix applied successfully.")

if __name__ == "__main__":
    main()
