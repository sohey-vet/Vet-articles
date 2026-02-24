import os
from pathlib import Path
from bs4 import BeautifulSoup
import re

base_dir = Path(r'c:\Users\souhe\Desktop\論文まとめ\topics')
files = list(base_dir.rglob('*.html'))

old_script = '<script type="module">import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs"; mermaid.initialize({ startOnLoad: true });</script>'
new_script = '<script type="module">import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs"; mermaid.initialize({ startOnLoad: true, securityLevel: "loose", theme: "default" });</script>'

def safe_quote(match, wrapper_open, wrapper_close):
    inner = match.group(1)
    if not inner.strip():
        return match.group(0)
    if '"' in inner:
        return match.group(0) # Already contains quotes
    return f'{wrapper_open}"{inner}"{wrapper_close}'

def repair_mermaid(filepath):
    with open(filepath, 'r', encoding='utf-8') as fh:
        html_content = fh.read()
    
    # Update script tag globally
    if old_script in html_content:
        html_content = html_content.replace(old_script, new_script)
        
    soup = BeautifulSoup(html_content, 'html.parser')
    mermaids = soup.find_all('pre', class_='mermaid')
    changed = False
    
    for m in mermaids:
        original = m.string
        if not original:
            continue
        
        text = original
        
        # We process line by line to avoid messing up structural lines
        lines = text.split('\n')
        new_lines = []
        for line in lines:
            if line.strip().startswith('style') or line.strip().startswith('classDef') or line.strip().startswith('class ') or line.strip().startswith('//') or line.strip().startswith('graph') or line.strip().startswith('subgraph') or line.strip().startswith('end'):
                new_lines.append(line)
                continue
            
            # 1. Quote text in rectangular nodes [text]
            # Careful not to match things that look like lists, but in mermaid A[Text] is common.
            line = re.sub(r'\[([^\]]+)\]', lambda m: safe_quote(m, '[', ']'), line)
            
            # 2. Quote text in diamond nodes {text}
            line = re.sub(r'\{([^\}]+)\}', lambda m: safe_quote(m, '{', '}'), line)
            
            # 3. Quote text in circle nodes ((text))
            line = re.sub(r'\(\((.+?)\)\)', lambda m: safe_quote(m, '((', '))'), line)
            
            # # 4. Quote text in normal round nodes (text) -> but this conflicts with ((text)) if not careful
            # # Actually, we can skip `()` as it's rarely used with complex text, but let's do `(text)` avoiding `((`
            # line = re.sub(r'(?<!\()\(([^\(\)]+)\)(?!\))', lambda m: safe_quote(m, '(', ')'), line)
            
            # 5. Quote edge labels |text|
            line = re.sub(r'\|([^\|]+)\|', lambda m: safe_quote(m, '|', '|'), line)

            new_lines.append(line)
            
        new_text = '\n'.join(new_lines)
        if new_text != original:
            m.string.replace_with(new_text)
            changed = True
            
    # We must also write the changed soup if Mermaid was touched, or the string replace if only the script tag was updated.
    # To be safe, just write soup out, but soup might reformat things. Let's compare soup string to html_content.
    
    # Actually, we can just replace the <script> and be done if mermaid didn't change, but if mermaid changed, we use soup.
    # Beautiful soup might change formatting slightly so we only use soup if we modified a PRE tag.
    
    if changed:
        try:
            # We want to use HTML content but with the script replaced.
            soup = BeautifulSoup(html_content, 'html.parser') # re-parse to ensure script is in
            mermaids2 = soup.find_all('pre', class_='mermaid')
            for i, m2 in enumerate(mermaids2):
                orig_m = mermaids[i]
                if orig_m.string:
                    m2.string.replace_with(mermaids[i].string)
            final_html = str(soup)
        except Exception:
            final_html = str(soup)
    else:
        final_html = html_content
        
    # Check if there is a difference to save disk writes
    with open(filepath, 'r', encoding='utf-8') as fh:
        current_disk = fh.read()
        
    if final_html != current_disk:
        with open(filepath, 'w', encoding='utf-8') as fh:
            fh.write(final_html)
        return True
    return False

if __name__ == '__main__':
    count = 0
    for f in files:
        if repair_mermaid(f):
            count += 1
            print(f'Repaired: {f.name}')
    print(f'Total files aggressively quoted/updated: {count}')
