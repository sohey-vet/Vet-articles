import os
import re
from bs4 import BeautifulSoup

html_files = [
    r"c:\Users\souhe\Desktop\論文まとめ\topics\救急\犬猫の中毒_原因物質と対処法.html",
    r"c:\Users\souhe\Desktop\論文まとめ\topics\抗菌薬\抗菌薬選択の基本原則.html",
    r"c:\Users\souhe\Desktop\論文まとめ\topics\免疫\IMHA_診断と初期治療.html",
    r"c:\Users\souhe\Desktop\論文まとめ\topics\循環器\猫のHCM_早期発見と管理.html",
    r"c:\Users\souhe\Desktop\論文まとめ\topics\神経\椎間板ヘルニア_頚部胸腰部統合版.html"
]

def parse_html_to_markdown(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    # 1. タイトル
    h1 = soup.find("h1")
    title = h1.get_text(strip=True) if h1 else "No Title"

    title_icons = ""
    # Usually the icon is in span class icon, let's keep it if exists or just put 🐕 
    
    # 2. タグ
    tags = []
    meta_tags = soup.find_all("span", class_="meta-tag")
    for t in meta_tags:
        tags.append("#" + t.get_text(strip=True))
    tags_str = " ".join(tags)

    # 3. 結論 (bottom-line)
    bottom_line_div = soup.find("div", class_="bottom-line")
    bottom_line_text = ""
    if bottom_line_div:
        p = bottom_line_div.find("p", class_="summary-text")
        if p:
            bottom_line_text = p.get_text(strip=True)
        else:
            bottom_line_text = bottom_line_div.get_text(strip=True).replace("結論:", "").strip()

    # 4. 見出しごとのコンテンツ (accordion)
    accordions = soup.find_all("div", class_="accordion")
    content_md = []
    for acc in accordions:
        # Check if it's owner-tips or refs (they might be inside accordions or have IDs)
        if acc.parent and acc.parent.get("id") in ["owner-tips", "refs"]:
            continue # process later

        # Title
        trigger = acc.find("button", class_="accordion-trigger")
        trigger_text = ""
        if trigger:
            span = trigger.find("span", class_="trigger-left")
            if span:
                trigger_text = span.get_text(strip=True)
            else:
                trigger_text = trigger.get_text(strip=True).replace("▼", "")

        content_md.append(f"## 🗺️ {trigger_text}")
        
        # Body
        body = acc.find("div", class_="premium-content") or acc.find("div", class_="accordion-body")
        if not body: continue

        for child in body.children:
            if child.name == "h3":
                content_md.append(f"### ▼ {child.get_text(strip=True)}")
            elif child.name == "p":
                # handle bold text
                text = child.get_text(strip=False) # Keep text 
                # Very basic replace for strong
                for s in child.find_all("strong"):
                    if "臨床アクション" in s.get_text():
                        s.replace_with(f"**💡 臨床アクション**")
                    else:
                        s.replace_with(f"**{s.get_text()}**")
                
                content_md.append(child.get_text("\n", strip=True))
                content_md.append("")
            elif child.name == "ul":
                for li in child.find_all("li"):
                    content_md.append(f"- {li.get_text(strip=True)}")
                content_md.append("")
            elif child.name == "table":
                # Convert table to markdown
                headers = [th.get_text(strip=True) for th in child.find_all("th")]
                if headers:
                    content_md.append("| " + " | ".join(headers) + " |")
                    content_md.append("|" + "|".join(["---"] * len(headers)) + "|")
                for tr in child.find_all("tr"):
                    tds = [td.get_text(strip=True) for td in tr.find_all("td")]
                    if tds:
                        content_md.append("| " + " | ".join(tds) + " |")
                content_md.append("")

    # 5. 飼い主への説明
    owner_section = soup.find("div", id="owner-tips")
    owner_md = ["## 🗣️ 飼い主への説明ガイド"]
    if owner_section:
        tips = owner_section.find_all("div", class_="owner-tip")
        for tip in tips:
            q = tip.find("h4")
            a = tip.find("div", class_="speech-bubble")
            if q: owner_md.append(f"**Q. {q.get_text(strip=True)}**")
            if a: owner_md.append(a.get_text(strip=True))
            owner_md.append("")

    # 6. 参照論文
    ref_section = soup.find("div", id="refs")
    ref_md = ["## 📚 参照論文"]
    if ref_section:
        lis = ref_section.find_all("li")
        for li in lis:
            ref_md.append(f"- {li.get_text(strip=True)}")
        if not lis:
            ref_md.append("（記載なし）")
    
    # 結合してMarkdownを生成
    full_md = []
    full_md.append(f"# {title}\n{tags_str}\n\n## 🎯 結論\n{bottom_line_text}\n")
    full_md.append("\n".join(content_md))
    full_md.append("\n".join(owner_md))
    full_md.append("\n".join(ref_md))
    
    return "\n".join(full_md)

for html_file in html_files:
    if os.path.exists(html_file):
        md_content = parse_html_to_markdown(html_file)
        md_file = html_file.replace(".html", ".md")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"Restored: {md_file}")
