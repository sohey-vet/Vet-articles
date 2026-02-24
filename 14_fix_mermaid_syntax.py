import os
import re
from pathlib import Path
from bs4 import BeautifulSoup

base_dir = Path(r'c:\Users\souhe\Desktop\論文まとめ\topics')
files = list(base_dir.rglob('*.html'))

def fix_mermaid_in_html(filepath):
    with open(filepath, 'r', encoding='utf-8') as fh:
        soup = BeautifulSoup(fh, 'html.parser')
        
    mermaids = soup.find_all('pre', class_='mermaid')
    if not mermaids:
        return False
        
    changed = False
    for m in mermaids:
        original_text = m.string
        if not original_text:
            continue
            
        new_text = original_text
        
        # 1. Fix edge labels: A -- text (with parens) --> B  >>>  A -->|text (with parens)| B
        # Regex captures Source Node ID, Edge text, Destination Node ID
        # It avoids touching standard A --> B since that has no text in between.
        new_text = re.sub(r'([A-Za-z0-9_]+)\s+--\s+(.+?)\s+-->\s+([A-Za-z0-9_]+)', r'\1 -->|\2| \3', new_text)
        
        # 2. Fix some known trailing garbage causing syntax error: ];疾患検索];;
        new_text = new_text.replace('];疾患検索];;', '];')
        new_text = new_text.replace('];リスク増];', '];')
        new_text = new_text.replace(']; 定期検診};', '];')
        new_text = new_text.replace('];; ', ']; ')
        new_text = new_text.replace('};; ', '}; ')
        new_text = new_text.replace('];討];', '];')
        new_text = new_text.replace('];量];', '];')
        
        # 3. Clean trailing semi-colons with extra semicolons or text
        # Use simple replaces for common typos found in the log
        new_text = new_text.replace('];;', '];')
        new_text = new_text.replace('};;', '};')
        new_text = new_text.replace(');;', ');')
        
        if new_text != original_text:
            m.string.replace_with(new_text)
            changed = True
            
    if changed:
        with open(filepath, 'w', encoding='utf-8') as fh:
            fh.write(str(soup))
        print(f"Fixed Mermaid syntax in: {filepath.name}")
        return True
    return False

if __name__ == '__main__':
    count = 0
    for f in files:
        if fix_mermaid_in_html(f):
            count += 1
    print(f"Total files updated: {count}")
