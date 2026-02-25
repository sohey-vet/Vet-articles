"""
Aggressive fix for ALL remaining Mermaid syntax issues.
Handles: <br/> line separators, &amp; entities, unquoted subgraph names, encoded arrows.
"""
import re
from pathlib import Path

base_dir = Path(r'c:\Users\souhe\Desktop\論文まとめ\topics')
files = list(base_dir.rglob('*.html'))
changed_files = 0

def fix_mermaid_block(block):
    """Fix all known syntax issues in a Mermaid block."""
    original = block
    
    # 1. Fix encoded arrows: --&gt; to -->
    block = block.replace('--&gt;', '-->')
    block = block.replace('==&gt;', '==>')
    block = block.replace('-.&gt;', '-.>')
    
    # 2. Fix encoded ampersands: &amp; to & (used in Mermaid for AND: A & B --> C)
    block = block.replace('&amp;', '&')
    
    # 3. Convert <br/> line separators to real newlines
    # Strategy: split on <br/> but be smart about keeping <br/> inside node labels
    
    if '<br/>' in block or '<br>' in block:
        # Normalize
        block = block.replace('<br>', '<br/>')
        block = block.replace('<br />', '<br/>')
        
        # Replace <br/><br/> with double newlines first
        block = block.replace('<br/><br/>', '\n\n')
        
        # Replace ;<br/> with ;\n (end of statement)
        block = block.replace(';<br/>', ';\n')
        
        # Replace <br/> before keywords
        for kw in ['subgraph', 'end', 'graph ', 'classDef', 'class ', 'style ', 'linkStyle', 'direction']:
            block = re.sub(rf'<br/>\s*({kw})', r'\n\1', block)
        
        # Replace <br/> followed by spaces (indentation = new statement)
        block = re.sub(r'<br/>(\s{2,})', r'\n\1', block)
        
        # Replace <br/> followed by a node identifier (capital letter or lowercase start of statement)
        block = re.sub(r'<br/>(\s*[A-Z_])', r'\n\1', block)
        
    # 4. Fix unquoted subgraph names containing special characters
    def quote_subgraph(match):
        name = match.group(1).strip()
        # If name contains ( ) [ ] { } and is not already quoted
        if any(c in name for c in '()[]{}') and not name.startswith('"'):
            return f'subgraph "{name}"'
        return match.group(0)
    
    block = re.sub(r'subgraph\s+(.+?)$', quote_subgraph, block, flags=re.MULTILINE)
    
    return block

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

# Verify no remaining issues
print('\n--- Verification ---')
remaining = 0
for f in files:
    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()
    blocks = re.findall(r'<pre class="mermaid">(.*?)</pre>', content, re.DOTALL)
    for block in blocks:
        issues = []
        if '--&gt;' in block:
            issues.append('encoded arrows')
        if '&amp;' in block:
            issues.append('encoded &')
        # Check for <br/> that look like line separators (outside brackets)
        # Simple heuristic: <br/> followed by a space and capital letter
        if re.search(r'<br/>\s*[A-Z_]', block):
            issues.append('br as line separator')
        if issues:
            print(f'  REMAINING: {f.name}: {issues}')
            remaining += 1

if remaining == 0:
    print('  All Mermaid blocks look clean!')
