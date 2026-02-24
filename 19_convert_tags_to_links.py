import os
import urllib.parse
from pathlib import Path
from bs4 import BeautifulSoup

base_dir = Path(r'c:\Users\souhe\Desktop\論文まとめ')
html_files = list(base_dir.rglob('topics/**/*.html')) + [base_dir / 'templates' / 'article_template.html']

def convert_tags(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as fh:
            soup = BeautifulSoup(fh, 'html.parser')
    except Exception as e:
        print(f"Failed to read {filepath}: {e}")
        return False
        
    tags = soup.find_all('span', class_='tag')
    changed = False
    
    for t in tags:
        text = t.get_text(strip=True)
        if not text:
            continue
            
        # Already an anchor inside? Or is the span inside an anchor?
        if t.parent and t.parent.name == 'a':
            continue
            
        rel_path = os.path.relpath(base_dir / 'index.html', filepath.parent)
        rel_path = rel_path.replace('\\', '/')
        
        encoded_text = urllib.parse.quote(text)
        target_href = f"{rel_path}?tag={encoded_text}"
        
        # Create new <a> tag
        new_tag = soup.new_tag('a', href=target_href)
        new_tag.attrs['class'] = t.attrs.get('class', [])
        new_tag.string = text
        
        t.replace_with(new_tag)
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
            if convert_tags(f):
                count += 1
                print(f"Converted tags in: {f.name}")
    print(f"Total files updated: {count}")
