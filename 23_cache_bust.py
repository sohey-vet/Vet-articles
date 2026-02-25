import re
from pathlib import Path

base_dir = Path(r'c:\Users\souhe\Desktop\論文まとめ')
timestamp = '20250225v3'

# Process all HTML files in topics/ and index.html
html_files = list(base_dir.joinpath('topics').rglob('*.html'))
index = base_dir / 'index.html'
if index.exists():
    html_files.append(index)

changed = 0
for f in html_files:
    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()
    
    original = content
    
    # Add/update cache bust on style.css references
    # Match: href="../../assets/style.css" or href="assets/style.css" with optional existing ?v=xxx
    content = re.sub(
        r'(href="[^"]*?style\.css)(\?v=[^"]*)?(")',
        rf'\1?v={timestamp}\3',
        content
    )
    
    # Add/update cache bust on script.js references
    content = re.sub(
        r'(src="[^"]*?script\.js)(\?v=[^"]*)?(")',
        rf'\1?v={timestamp}\3',
        content
    )
    
    if content != original:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(content)
        changed += 1

print(f'Updated cache-busting in {changed} files')
