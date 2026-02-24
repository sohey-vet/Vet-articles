import os
from pathlib import Path
from bs4 import BeautifulSoup
import re

base_dir = Path(r'c:\Users\souhe\Desktop\論文まとめ\topics')
files = list(base_dir.rglob('*.html'))

def fix_inequalities(filepath):
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
            
        lines = original_text.split('\n')
        new_lines = []
        for line in lines:
            # We only want to replace < and > if they are part of node text like `MAP < 60` or `PCO2 > 45`
            # We avoid replacing <br> and <br/> or <!-- -->
            if '<br>' in line or '<br/>' in line or '<!--' in line:
                new_lines.append(line)
                continue
                
            # Replacing < and > with full width if they aren't part of an HTML tag
            # Because Mermaid blocks shouldn't have raw < or > anyway unless quoted, which AI struggles with.
            # Also --> should not be replaced!
            
            # Temporary replace --> with a placeholder
            temp_line = line.replace('-->', '@@@')
            
            if '<' in temp_line or '>' in temp_line:
                temp_line = temp_line.replace('<', '＜').replace('>', '＞')
                changed = True
                
            # Restore -->
            new_line = temp_line.replace('@@@', '-->')
            new_lines.append(new_line)
            
        new_text = '\n'.join(new_lines)
        if new_text != original_text:
            m.string.replace_with(new_text)
            changed = True
            
    if changed:
        with open(filepath, 'w', encoding='utf-8') as fh:
            fh.write(str(soup))
        print(f"Sanitized < > in: {filepath.name}")
        return True
    return False

if __name__ == '__main__':
    count = 0
    for f in files:
        if fix_inequalities(f):
            count += 1
    print(f"Total files sanitized: {count}")
