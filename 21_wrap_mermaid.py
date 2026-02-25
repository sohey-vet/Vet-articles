import os
from bs4 import BeautifulSoup
from pathlib import Path

base_dir = Path(r'c:\Users\souhe\Desktop\論文まとめ\topics')
files = list(base_dir.rglob('*.html'))

def wrap_mermaid(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as fh:
            soup = BeautifulSoup(fh, 'html.parser')
    except Exception as e:
        print(f"Failed to read {filepath}: {e}")
        return False

    changed = False
    
    # We only want to wrap <pre class="mermaid"> if it's NOT already in a wrapper
    mermaid_blocks = soup.find_all('pre', class_='mermaid')
    for block in mermaid_blocks:
        parent = block.parent
        if parent and parent.name == 'div' and 'mermaid-wrapper' in parent.get('class', []):
            continue # already wrapped
            
        # Create a wrapper div
        wrapper = soup.new_tag('div', **{'class': 'mermaid-wrapper'})
        # Replace the block with the wrapper, then insert the block inside the wrapper
        block.wrap(wrapper)
        changed = True

    if changed:
        with open(filepath, 'w', encoding='utf-8') as fh:
            fh.write(str(soup))
        return True
    return False

if __name__ == '__main__':
    count = 0
    for f in files:
        if wrap_mermaid(f):
            count += 1
            print(f"Wrapped Mermaid in: {f.name}")
    print(f"Total files updated: {count}")
