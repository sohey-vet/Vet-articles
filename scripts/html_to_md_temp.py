import os
from pathlib import Path
from bs4 import BeautifulSoup

def html_to_md(html_path):
    soup = BeautifulSoup(html_path.read_text(encoding='utf-8'), 'html.parser')
    
    # Extract title
    title_el = soup.find('h1')
    title = title_el.text if title_el else html_path.stem
    tags_el = soup.find(class_='tags')
    tags = tags_el.text.replace('Tags:', '').strip() if tags_el else "獣医, 獣医師, エビデンス"
    
    md_lines = []
    md_lines.append("TITLE")
    md_lines.append(title)
    md_lines.append("\nTAGS")
    md_lines.append(tags)
    md_lines.append("\nBODY")
    
    content_div = soup.find(class_='content')
    if not content_div:
        content_div = soup.find('body')
        
    for el in content_div.children:
        if el.name in ('h2', 'h3'):
            prefix = '## ' if el.name == 'h2' else '### '
            md_lines.append(f"\n{prefix}{el.text.strip()}")
        elif el.name == 'p':
            md_lines.append(f"\n{el.text.strip()}")
        elif el.name == 'ul':
            for li in el.find_all('li'):
                md_lines.append(f"- {li.text.strip()}")
        elif el.name == 'div' and el.get('class'):
            cls = el.get('class')[0]
            if cls in ('conclusion', 'important-point'):
                md_lines.append(f"\n**{el.text.strip()}**")
            elif cls == 'comparison-box':
                md_lines.append(f"\n【比較】\n{el.text.strip()}")
        elif el.name == 'table':
            rows = el.find_all('tr')
            for i, row in enumerate(rows):
                cols = [c.text.strip().replace('\n', ' ') for c in row.find_all(['th', 'td'])]
                md_lines.append("| " + " | ".join(cols) + " |")
                if i == 0:
                    md_lines.append("| " + " | ".join(['---'] * len(cols)) + " |")
                    
    md_content = "\n".join(md_lines)
    
    # Save md
    md_path = html_path.with_suffix('.md')
    md_path.write_text(md_content, encoding='utf-8')
    print(f"Created {md_path.name}")

files_to_convert = [
    r"C:\Users\souhe\Desktop\論文まとめ\topics\免疫\IMHA_診断と初期治療.html",
    r"C:\Users\souhe\Desktop\論文まとめ\topics\循環器\心原性肺水腫_一般病院での救命Tips.html",
    r"C:\Users\souhe\Desktop\論文まとめ\topics\抗菌薬\抗菌薬選択の基本原則.html",
    r"C:\Users\souhe\Desktop\論文まとめ\topics\神経\椎間板ヘルニア_胸腰部の内科vs外科・頚部ベントラルスロット.html",
    r"C:\Users\souhe\Desktop\論文まとめ\topics\腎泌尿器\猫のCKD_IRISステージ別管理.html"
]

for f in files_to_convert:
    html_to_md(Path(f))
