import os
import re
import urllib.parse
from bs4 import BeautifulSoup

def count_md_references(md_content):
    refs_start = md_content.find('<div id="refs">')
    if refs_start != -1:
        refs_chunk = md_content[refs_start:]
        md_soup = BeautifulSoup(refs_chunk, "html.parser")
        refs_div = md_soup.find("div", id="refs")
        if refs_div:
            li_count = len(refs_div.find_all("li"))
            if li_count > 0:
                return li_count

    lines = md_content.split('\n')
    in_refs = False
    count = 0
    list_pattern = re.compile(r'^\s*(?:\d+\.|-|\*)\s+')
    
    for line in lines:
        if line.startswith('## '):
            if '参照' in line or '参考' in line or 'Reference' in line or 'reference' in line:
                in_refs = True
            else:
                if in_refs: break 
        elif in_refs:
            if line.startswith('---'): break 
            if list_pattern.match(line): count += 1
                
    return count

def main():
    repo_dir = r"C:\Users\souhe\Desktop\論文まとめ"
    index_path = os.path.join(repo_dir, "index.html")
    
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.find_all("a", class_="article-card")
    
    mismatches = []
    
    for card in cards:
        title_tag = card.find("h3")
        title = title_tag.text.strip() if title_tag else "Unknown Title"
        
        papers_span = card.find("span", class_="card-papers")
        displayed_count = 0
        if papers_span:
            text = papers_span.text.strip()
            match = re.search(r'(\d+)\s*本', text)
            if match:
                displayed_count = int(match.group(1))
        
        href = card.get("href", "")
        if not href: continue
        
        href_decoded = urllib.parse.unquote(href)
        md_rel_path = href_decoded.replace(".html", ".md")
        md_file_path = os.path.join(repo_dir, md_rel_path)
        
        actual_count = 0
        if os.path.exists(md_file_path):
            with open(md_file_path, "r", encoding="utf-8") as f:
                md_content = f.read()
            actual_count = count_md_references(md_content)
        else:
            continue
            
        if displayed_count != actual_count:
            mismatches.append({
                "title": title,
                "displayed": displayed_count,
                "actual": actual_count,
                "file": md_rel_path
            })
            
    with open(r"C:\Users\souhe\.gemini\antigravity\brain\846085b5-dc3f-4c6c-af54-0389adfffbb5\reference_mismatches.md", "w", encoding="utf-8") as out:
        out.write("# 参照論文数 ミスマッチレポート\n\n")
        out.write("全108記事のうち、実際の参照論文数と `index.html` 上の表示に差異がある記事は **" + str(len(mismatches)) + "件** でした。\n\n")
        out.write("大きく分けて以下の2パターンが存在します。\n")
        out.write("1. **数字が異なる** (例: ブラウザ表示は7だが実際は4)\n")
        out.write("2. **ブラウザ側の表示が欠落している** (ブラウザ表示が「0」（枠がない表示）だが実際には論文がある)\n")
        out.write("3. **ファイル側の論文リストが一時的に0** (ブラウザには表示されているが、MDファイル側に参照論文のリストがない)\n\n")
        
        out.write("## 📝 詳細リスト\n\n")
        out.write("| 記事タイトル | index.html上表示 | MDファイル上の実数 |\n")
        out.write("|---|---|---|\n")
        
        for m in mismatches:
            disp_str = f"{m['displayed']}本" if m['displayed'] > 0 else "表示なし"
            act_str = f"{m['actual']}本" if m['actual'] > 0 else "0本 (未記載)"
            out.write(f"| {m['title']} | {disp_str} | {act_str} |\n")

if __name__ == "__main__":
    main()
