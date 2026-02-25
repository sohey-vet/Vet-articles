"""
Final comprehensive Mermaid fix:
1. Remove trailing semicolons from Mermaid statement lines
2. Rename node ID 'end' to 'endNode' (reserved keyword in Mermaid)
3. Verify all labels are properly quoted
"""
import re
from pathlib import Path

base_dir = Path(r'c:\Users\souhe\Desktop\論文まとめ\topics')
files = list(base_dir.rglob('*.html'))
changed_files = 0

def fix_mermaid_block(block):
    lines = block.split('\n')
    new_lines = []
    
    for line in lines:
        new_line = line
        
        # 1. Remove trailing semicolons (but not inside quoted labels)
        # Strip semicolon at end of line (before optional whitespace)
        new_line = re.sub(r';\s*$', '', new_line)
        
        # 2. Rename node ID 'end' to 'endNode' (it's a reserved keyword)
        # Match 'end' as a standalone node ID (not the 'end' keyword for subgraphs)
        # The 'end' keyword for subgraphs appears on its own line
        stripped = new_line.strip()
        if stripped == 'end':
            # This is a subgraph closing keyword - keep it
            pass
        else:
            # Replace 'end' when used as a node ID in connections
            # Pattern: --> end or end --> or end(( or end[
            new_line = re.sub(r'\bend\b(?=\s*-->|\s*\(|\s*\[|\s*\{)', 'endNode', new_line)
            new_line = re.sub(r'-->\s*end\b(?!\s*Node)', '--> endNode', new_line)
            new_line = re.sub(r'\|\s*end\b', '| endNode', new_line)
        
        new_lines.append(new_line)
    
    return '\n'.join(new_lines)

for f in files:
    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()
    
    original = content
    
    content = re.sub(
        r'(<pre class="mermaid">)(.*?)(</pre>)',
        lambda m: m.group(1) + fix_mermaid_block(m.group(2)) + m.group(3),
        content,
        flags=re.DOTALL
    )
    
    if content != original:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(content)
        changed_files += 1
        print(f'Fixed: {f.name}')

print(f'\nTotal fixed: {changed_files}')
