import os
import shutil
import re

repo_dir = r"C:\Users\souhe\Desktop\論文まとめ"
drafts_dir = r"C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts"

tasks = [
    {
        "old": "㉓月_腎泌尿器_猫の特発性膀胱炎FIC_ストレス管理を含む最新治療",
        "new": "㉓月_血液_高ナトリウム血症_原因と水脱水アプローチ",
        "html_path": r"C:\Users\souhe\Desktop\論文まとめ\topics\救急\高ナトリウム血症_原因と水脱水アプローチ.html"
    },
    {
        "old": "㊱月_救急_電解質異常の緊急対応_K_Ca",
        "new": "㊱月_眼科_赤い目の鑑別_結膜炎_緑内障",
        "html_path": r"C:\Users\souhe\Desktop\論文まとめ\topics\眼科\赤い目の鑑別_結膜炎_緑内障.html"
    },
    {
        "old": "㊱金_その他_健康診断の最適化_推奨項目",
        "new": "㊱金_腎泌尿器_犬猫の膀胱炎_ISCAIDガイドライン",
        "html_path": r"C:\Users\souhe\Desktop\論文まとめ\topics\腎泌尿器\犬猫の膀胱炎_ISCAIDガイドライン.html"
    }
]

for t in tasks:
    old_path = os.path.join(drafts_dir, t["old"])
    new_path = os.path.join(drafts_dir, t["new"])
    
    if os.path.exists(old_path) and not os.path.exists(new_path):
        os.rename(old_path, new_path)
    elif not os.path.exists(new_path):
        os.makedirs(new_path)
        
    # Generate draft file
    sns_md = os.path.join(new_path, "sns_all_drafts.md")
    ig_csv = os.path.join(new_path, "ig_carousel_data.csv")
    
    with open(t["html_path"], "r", encoding="utf-8") as f:
        html_content = f.read()
        
    # Extract titles, papers, desc
    title_m = re.search(r'<h1[^>]*>.*?([^<]+)</h1>', html_content)
    title = title_m.group(1).strip() if title_m else t["new"].split("_")[-1]
    
    desc_m = re.search(r'<p class="subtitle"[^>]*>\s*([^\r\n]+)\s*(?:<br>)?\s*([^\r\n]*)', html_content)
    desc = f"{desc_m.group(1).strip()}" if desc_m else "臨床現場でのエビデンスに基づく実践的なアプローチを解説。"
    
    paper_m = re.search(r'参照論文\s*(\d+)\s*本', html_content)
    papers = paper_m.group(1) if paper_m else "5"
    
    html_rel = t["html_path"].replace(repo_dir + "\\", "").replace("\\", "/")
    
    md_content = f"""元ファイル: {html_rel}

## 📱 X (旧Twitter) 用ドラフト
{title}
{desc}
現場で迷わないためのポイントをまとめました。
👇 詳しくはWeb版で（論文{papers}報を参照）
[URLをここに入力]

## 🧵 Threads 用ドラフト
獣医療アップデート🐶🐱
「{title}」
{desc}
日々の診療にすぐ活かせるエビデンスを整理しています。
詳細と海外論文の出典はリンクからどうぞ📚
👇 [URLをここに入力]

## 📸 Instagram 用キャプション
{title}🩺✨
{desc}
.
詳細はプロフィールのリンク（Web版サイト）にて詳しく解説しています。
無料で読める文献もありますので、ぜひご活用ください！
.
#獣医師 #獣医療 #動物病院
"""

    with open(sns_md, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    csv_content = f"""ページ番号,見出し,本文,補足
1,,,{title}
2,,,{desc}
3,,,,,
4,,,,,
5,,,,,
6,,,,,
"""
    with open(ig_csv, "w", encoding="utf-8-sig") as f:
        f.write(csv_content)
        
    print(f"Successfully processed {t['new']}")
