"""
Clean up the quoting mess created by the previous script.
Fix doubly-quoted patterns and ensure clean Mermaid 10 syntax.
"""
import re
from pathlib import Path

base_dir = Path(r'c:\Users\souhe\Desktop\論文まとめ\topics')
files = list(base_dir.rglob('*.html'))
changed_files = 0

def clean_mermaid_block(block):
    original = block
    
    # Fix corrupted double-paren patterns like (("'text'")) -> (("text"))
    block = re.sub(r'\(\("\'([^\']+)\'\"\)\)', r'(("\1"))', block)
    block = re.sub(r'\(\"?\(\'([^\']+)\'\"\)?\)', r'(("\1"))', block)
    
    # Fix any remaining ('text') inside ((...)) 
    block = re.sub(r"\(\(\"'([^']+)'\"\)\)", r'(("\1"))', block)
    
    # Fix all patterns where we have ["'text'"] -> ["text"]  
    block = re.sub(r"\[\"'([^']+)'\"\]", r'["\1"]', block)
    
    # Fix all patterns where we have ("'text'") -> ("text")
    block = re.sub(r"\(\"'([^']+)'\"\)", r'("\1")', block)
    
    # Fix all patterns where we have {"'text'"} -> {"text"}
    block = re.sub(r"\{\"'([^']+)'\"\}", r'{"\1"}', block)
    
    # Fix edge labels |"'text'"| -> |"text"|
    block = re.sub(r"\|\"'([^']+)'\"\|", r'|"\1"|', block)
    
    return block

for f in files:
    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()
    
    original = content
    content = re.sub(
        r'(<pre class="mermaid">)(.*?)(</pre>)',
        lambda m: m.group(1) + clean_mermaid_block(m.group(2)) + m.group(3),
        content,
        flags=re.DOTALL
    )
    
    if content != original:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(content)
        changed_files += 1
        print(f'Cleaned: {f.name}')

print(f'\nTotal cleaned: {changed_files}')

# Verify GDV specifically
f = base_dir / '救急' / 'GDV_安定化と手術判断.html'
with open(f, 'r', encoding='utf-8') as fh:
    content = fh.read()
blocks = re.findall(r'<pre class="mermaid">(.*?)</pre>', content, re.DOTALL)
for block in blocks:
    for line in block.split('\n')[:5]:
        print(repr(line.strip()))
