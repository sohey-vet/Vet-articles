import os
import re
from bs4 import BeautifulSoup
from pathlib import Path

html_files = [
    r"c:\Users\souhe\Desktop\論文まとめ\topics\救急\犬猫の中毒_原因物質と対処法.html",
    r"c:\Users\souhe\Desktop\論文まとめ\topics\免疫\IMHA_診断と初期治療.html",
    r"c:\Users\souhe\Desktop\論文まとめ\topics\循環器\猫のHCM_早期発見と管理.html",
    r"c:\Users\souhe\Desktop\論文まとめ\topics\神経\椎間板ヘルニア_頚部胸腰部統合版.html"
]

def extract_md(node):
    if isinstance(node, str):
        text = node.replace('\r', '').replace('\n', ' ')
        return text

    classes = node.get("class", [])
    # 除外要素
    if any(c in classes for c in ["mermaid-wrapper", "premium-lock", "mobile-nav", "slide-menu", "content-mode-bar", "meta-bar", "page-footer", "tags"]):
        return ""
    if node.name in ["nav", "aside", "footer"]:
        return ""
    if node.name == "button" and "accordion-trigger" not in classes:
        return ""

    text = ""
    if node.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
        level = int(node.name[1])
        inner = "".join([extract_md(c) for c in node.contents]).strip()
        if inner:
            # accordion trigger is often inside button or span, we handle it if it acts as a heading
            if "trigger-left" in classes:
                text += f"\n### ▼ {inner.replace('▼', '').strip()}\n"
            else:
                text += f"\n{'#' * level} {inner}\n"
    elif node.name == "p":
        inner = "".join([extract_md(c) for c in node.contents]).strip()
        if inner: text += f"\n{inner}\n"
    elif node.name in ["strong", "b"]:
        inner = "".join([extract_md(c) for c in node.contents]).strip()
        if inner: text += f"**{inner}**"
    elif node.name in ["em", "i"]:
        inner = "".join([extract_md(c) for c in node.contents]).strip()
        if inner: text += f"*{inner}*"
    elif node.name == "ul":
        for li in node.find_all("li", recursive=False):
            inner = "".join([extract_md(c) for c in li.contents]).strip()
            if inner: text += f"- {inner}\n"
        text += "\n"
    elif node.name == "ol":
        for i, li in enumerate(node.find_all("li", recursive=False), 1):
            inner = "".join([extract_md(c) for c in li.contents]).strip()
            if inner: text += f"{i}. {inner}\n"
        text += "\n"
    elif node.name == "table":
        headers = []
        for th in node.find_all('th'):
            headers.append("".join([extract_md(c) for c in th.contents]).strip().replace('\n', ''))
        if headers:
            text += f"\n| {' | '.join(headers)} |\n|{'|'.join(['---'] * len(headers))}|\n"
        for tr in node.find_all('tr'):
            tds = []
            for td in tr.find_all('td'):
                # handle br
                for br in td.find_all('br'): br.replace_with(" ")
                inner = "".join([extract_md(c) for c in td.contents]).strip().replace('\n', ' ')
                tds.append(inner)
            if tds:
                text += f"| {' | '.join(tds)} |\n"
        text += "\n"
    elif node.name in ["div", "button"]:
        if "accordion-trigger" in classes:
            inner = "".join([extract_md(c) for c in node.contents]).replace('▼', '').strip()
            if inner: text += f"\n### ▼ {inner}\n"
        else:
            for child in node.contents:
                text += extract_md(child)
    else:
        for child in node.contents:
            text += extract_md(child)

    return text

for html_file in html_files:
    if os.path.exists(html_file):
        with open(html_file, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
        
        container = soup.find("div", class_="page-container")
        if not container: continue
            
        md_text = extract_md(container)
        
        # Cleanup extra newlines
        md_text = re.sub(r'\n{3,}', '\n\n', md_text).strip()
        
        md_file = html_file.replace(".html", ".md")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_text)
        print(f"✅ Perfectly restored: {md_file}")
