import re
import urllib.parse
from pathlib import Path
from bs4 import BeautifulSoup

base_dir = Path(r'c:\Users\souhe\Desktop\論文まとめ')
html_files = list(base_dir.rglob('topics/**/*.html')) + [base_dir / 'index.html']

def extract_number(text):
    # Find all digits in the text
    match = re.search(r'\d+', text)
    if match:
        return match.group()
    # Handle full-width numbers just in case
    text = text.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
    match = re.search(r'\d+', text)
    if match:
        return match.group()
    return None

def standardize_papers(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as fh:
            soup = BeautifulSoup(fh, 'html.parser')
    except Exception as e:
        print(f"Failed to read {filepath}: {e}")
        return False
        
    changed = False
    
    if filepath.name == 'index.html':
        # Target: <span class="card-papers">📄論文6本</span>
        paper_spans = soup.find_all('span', class_='card-papers')
        for span in paper_spans:
            text = span.get_text()
            if '📄' in text:
                num = extract_number(text)
                if num:
                    new_text = f"📄 参照論文{num}本"
                    if text != new_text:
                        span.string = new_text
                        changed = True
    else:
        # Target: <div class="meta-item"><span class="icon">📄</span><span>参照論文 6本</span></div>
        meta_items = soup.find_all('div', class_='meta-item')
        for item in meta_items:
            icon_span = item.find('span', class_='icon')
            if icon_span and '📄' in icon_span.get_text():
                text_span = icon_span.find_next_sibling('span')
                if text_span:
                    text = text_span.get_text()
                    num = extract_number(text)
                    if num:
                        new_text = f"参照論文{num}本"
                        if text != new_text:
                            text_span.string = new_text
                            changed = True
                            
    if changed:
        with open(filepath, 'w', encoding='utf-8') as fh:
            fh.write(str(soup))
        return True
    return False

if __name__ == '__main__':
    count = 0
    for f in html_files:
        if f.exists() and f.is_file():
            if standardize_papers(f):
                count += 1
                print(f"Standardized papers in: {f.name}")
    print(f"Total files updated: {count}")
