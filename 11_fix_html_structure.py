import os
from bs4 import BeautifulSoup
from pathlib import Path

base_dir = Path(r'c:\Users\souhe\Desktop\論文まとめ\topics')
files = list(base_dir.rglob('*.html'))

def fix_html_files():
    fixed_count = 0
    
    for f in files:
        changed = False
        with open(f, 'r', encoding='utf-8') as fh:
            soup = BeautifulSoup(fh, 'html.parser')
            
        accordions = soup.find_all('div', class_='accordion')
        for acc in accordions:
            trigger = acc.find('button', class_='accordion-trigger')
            if not trigger:
                continue
                
            text = trigger.get_text(strip=True)
            
            # --- 1. Fix owner-tips wrapper ---
            if '飼い主' in text:
                parent = acc.parent
                if parent.name != 'div' or parent.get('id') != 'owner-tips':
                    wrapper = soup.new_tag('div', id='owner-tips')
                    acc.insert_before(wrapper)
                    wrapper.append(acc)
                    changed = True
                    print(f'{f.name}: fixed owner-tips wrapper')
            
            # --- 2. Fix refs wrapper ---
            if '参照' in text or '論文' in text:
                if '論文' in text and not '参照' in text and not '参考文献' in text:
                    pass # avoid matching unrelated things, but '参照論文' is standard.
                parent = acc.parent
                if parent.name != 'div' or parent.get('id') != 'refs':
                    # Only wrap if it's actually the reference section (usually at the end)
                    if '参照' in text or '参考' in text:
                        wrapper = soup.new_tag('div', id='refs')
                        acc.insert_before(wrapper)
                        wrapper.append(acc)
                        changed = True
                        print(f'{f.name}: fixed refs wrapper')
                        
        if changed:
            with open(f, 'w', encoding='utf-8') as fh:
                fh.write(str(soup))
            fixed_count += 1
            
    print(f'Fixed {fixed_count} files.')

if __name__ == '__main__':
    fix_html_files()
