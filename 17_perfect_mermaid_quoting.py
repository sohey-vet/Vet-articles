import os
from pathlib import Path
from bs4 import BeautifulSoup
import re

base_dir = Path(r'c:\Users\souhe\Desktop\論文まとめ\topics')
files = list(base_dir.rglob('*.html'))

old_script = 'mermaid.initialize({ startOnLoad: true });'
new_script = 'mermaid.initialize({ startOnLoad: true, securityLevel: "loose", theme: "default" });'

def safe_quote(inner):
    if not inner.strip():
        return inner
    if '"' in inner:
        return inner
    return f'"{inner}"'

def repair_mermaid(filepath):
    # Read entire file as text
    with open(filepath, 'r', encoding='utf-8') as fh:
        html_content = fh.read()
    
    # 1. Update script tag globally
    changed_script = False
    if old_script in html_content:
        html_content = html_content.replace(old_script, new_script)
        changed_script = True
        
    soup = BeautifulSoup(html_content, 'html.parser')
    mermaids = soup.find_all('pre', class_='mermaid')
    changed_mermaid = False
    
    for m in mermaids:
        original = m.string
        if not original:
            continue
            
        lines = original.split('\n')
        new_lines = []
        for line in lines:
            if line.strip().startswith('style') or line.strip().startswith('classDef') or line.strip().startswith('class ') or line.strip().startswith('//') or line.strip().startswith('graph') or line.strip().startswith('subgraph') or line.strip().startswith('end'):
                new_lines.append(line)
                continue
                
            # Regex to find: Node ID + shape opening + text + shape closing
            # Shape []:   A[text]
            line = re.sub(r'([A-Za-z0-9_]+)\[([^\]]+)\]', lambda m: f'{m.group(1)}[{safe_quote(m.group(2))}]', line)
            
            # Shape {}:   A{text}
            line = re.sub(r'([A-Za-z0-9_]+)\{([^\}]+)\}', lambda m: f'{m.group(1)}{{{safe_quote(m.group(2))}}}', line)
            
            # Shape (()): A((text))
            line = re.sub(r'([A-Za-z0-9_]+)\(\((.+?)\)\)', lambda m: f'{m.group(1)}(({safe_quote(m.group(2))}))', line)
            
            # Shape ():   A(text) - avoid matching (()) by negative lookahead/behind
            line = re.sub(r'(?<!\()([A-Za-z0-9_]+)\(([^\(\)]+)\)(?!\))', lambda m: f'{m.group(1)}({safe_quote(m.group(2))})', line)
            
            # Edges -->|text|
            line = re.sub(r'-->\|([^\|]+)\|', lambda m: f'-->|{safe_quote(m.group(1))}|', line)

            new_lines.append(line)
            
        new_text = '\n'.join(new_lines)
        if new_text != original:
            m.string.replace_with(new_text)
            changed_mermaid = True
            
    if changed_script or changed_mermaid:
        with open(filepath, 'w', encoding='utf-8') as fh:
            fh.write(str(soup))
        return True
    return False

if __name__ == '__main__':
    count = 0
    for f in files:
        if repair_mermaid(f):
            count += 1
            print(f'Repaired: {f.name}')
    print(f'Total files updated: {count}')
