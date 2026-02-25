"""
DEFINITIVE Mermaid 10 compatibility fix.
Mermaid 10.9.5 is extremely strict about special characters in node labels.

Approach:
1. Decode ALL HTML entities (&lt; &gt; &amp;) to raw characters inside Mermaid blocks
2. Then ensure ALL node labels [...], (...), {...} are QUOTED with double quotes
   e.g. A[text] -> A["text"]
3. Ensure ALL edge labels |text| are QUOTED: |"text"|
4. Ensure ALL subgraph names are QUOTED if they contain special chars
5. Keep arrows --> as-is
"""
import re, html
from pathlib import Path

base_dir = Path(r'c:\Users\souhe\Desktop\論文まとめ\topics')
files = list(base_dir.rglob('*.html'))
changed_files = 0

def fix_mermaid_block(block):
    # Step 1: Decode HTML entities
    # &lt; -> <, &gt; -> >, &amp; -> &
    block = block.replace('&lt;', '<')
    block = block.replace('&gt;', '>')
    block = block.replace('&amp;', '&')
    
    # Step 2: Fix arrows that might have been broken by entity decoding
    # The only place > appears legitimately outside quotes is in arrows: --> ==> -.->
    # These should already be fine since we decoded &gt; to >
    
    # Step 3: Quote ALL node labels that aren't already quoted
    # Patterns: NodeID[label], NodeID(label), NodeID{label}, NodeID((label)), NodeID>label]
    # Also: NodeID(["label"]), NodeID[("label")]
    
    lines = block.split('\n')
    new_lines = []
    
    for line in lines:
        new_line = line
        
        # Quote content inside square brackets: A[text] -> A["text"]
        # But skip if already quoted: A["text"] stays
        def quote_bracket(match):
            prefix = match.group(1)  # The bracket type [ or ( or {
            content = match.group(2)
            suffix = match.group(3)   # The closing bracket ] or ) or }
            
            # Skip if already quoted
            if content.startswith('"') and content.endswith('"'):
                return f'{prefix}{content}{suffix}'
            
            # Skip empty content
            if not content.strip():
                return f'{prefix}{content}{suffix}'
            
            # Quote it
            # Escape any existing double quotes inside
            content = content.replace('"', "'")
            return f'{prefix}"{content}"{suffix}'
        
        # Match [...], (...), {...} but NOT -->  or subgraph or end
        # Skip lines that are just keywords
        stripped = new_line.strip()
        if stripped.startswith('graph ') or stripped.startswith('subgraph') or stripped == 'end' or stripped.startswith('%%') or stripped.startswith('classDef') or stripped.startswith('style ') or stripped.startswith('linkStyle') or stripped.startswith('direction'):
            # For subgraph lines, quote the name if it has special chars
            if stripped.startswith('subgraph '):
                name = stripped[9:].strip()
                if name and not name.startswith('"') and any(c in name for c in '()[]{}≥≤<>＜＞'):
                    new_line = new_line.replace(f'subgraph {name}', f'subgraph "{name}"')
            new_lines.append(new_line)
            continue
        
        # Quote content in square brackets [...]
        def quote_sq(match):
            content = match.group(1)
            if content.startswith('"') and content.endswith('"'):
                return f'[{content}]'
            if not content.strip():
                return f'[{content}]'
            content = content.replace('"', "'")
            return f'["{content}"]'
        
        new_line = re.sub(r'\[([^\]]+)\]', quote_sq, new_line)
        
        # Quote content in round brackets (...) for node definitions
        def quote_rnd(match):
            content = match.group(1)
            if content.startswith('"') and content.endswith('"'):
                return f'({content})'
            if not content.strip():
                return f'({content})'
            content = content.replace('"', "'")
            return f'("{content}")'
        
        new_line = re.sub(r'(?<=[A-Za-z_0-9])\(([^)]+)\)', quote_rnd, new_line)
        
        # Quote content in curly brackets {...} for decision nodes
        def quote_curly(match):
            content = match.group(1)
            if content.startswith('"') and content.endswith('"'):
                return f'{{{content}}}'
            if not content.strip():
                return f'{{{content}}}'
            content = content.replace('"', "'")
            return f'{{"{content}"}}'
        
        new_line = re.sub(r'(?<=[A-Za-z_0-9])\{([^}]+)\}', quote_curly, new_line)
        
        # Quote content in double parens ((text)) for circles
        new_line = re.sub(r'\(\(([^)]+)\)\)', lambda m: f'(("{m.group(1).replace(chr(34), chr(39))}"))', new_line)
        
        # Quote edge labels: |text| -> |"text"|
        def quote_edge(match):
            content = match.group(1)
            if content.startswith('"') and content.endswith('"'):
                return f'|{content}|'
            content = content.replace('"', "'")
            return f'|"{content}"|'
        
        new_line = re.sub(r'\|([^|]+)\|', quote_edge, new_line)
        
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
