import re
from pathlib import Path

base_dir = Path(r'c:\Users\souhe\Desktop\論文まとめ\topics')
files = list(base_dir.rglob('*.html'))
changed_files = 0

def fix_mermaid_block(block):
    lines = block.split('\n')
    new_lines = []
    
    for line in lines:
        # Avoid breaking HTML tags like <br/> by specifically targeting math operators
        # and surrounding text
        new_line = line
        
        # 1. Look for unescaped < or > inside nodes [ ] or ( ) or { }
        def node_replacer(match):
            bracket_open = match.group(1)
            content = match.group(2)
            bracket_close = match.group(3)
            
            # Replace mathematical/logical operators if they aren't part of an HTML tag
            content = re.sub(r'<(\d)', r'&lt;\1', content)
            content = re.sub(r'>(\d)', r'&gt;\1', content)
            content = re.sub(r'<=', r'&lt;=', content)
            content = re.sub(r'>=', r'&gt;=', content)
            content = re.sub(r'<([A-Za-z\s])', r'&lt;\1', content) 
            content = re.sub(r'>([A-Za-z\s])', r'&gt;\1', content)
            
            # Make sure we don't break <br/> ! We undo &lt;br/&gt; if it happened
            content = content.replace('&lt;br/&gt;', '<br/>').replace('&lt;br&gt;', '<br>').replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')
            
            return f"{bracket_open}{content}{bracket_close}"
            
        new_line = re.sub(r'([\[\(\{])(.*?)([\]\)\}])', node_replacer, new_line)
        
        # 2. Look for edge labels | |
        def edge_replacer(match):
            content = match.group(1)
            content = re.sub(r'<(\d)', r'&lt;\1', content)
            content = re.sub(r'>(\d)', r'&gt;\1', content)
            content = re.sub(r'<=', r'&lt;=', content)
            content = re.sub(r'>=', r'&gt;=', content)
            content = re.sub(r'<([A-Za-z\s])', r'&lt;\1', content) 
            content = re.sub(r'>([A-Za-z\s])', r'&gt;\1', content)
            
            content = content.replace('&lt;br/&gt;', '<br/>').replace('&lt;br&gt;', '<br>').replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')
            return f"|{content}|"
            
        new_line = re.sub(r'\|(.*?)\|', edge_replacer, new_line)
        
        # 3. Ensure arrows are not accidentally HTML entity encoded (Mermaid expects --> or -.->)
        new_line = new_line.replace('--&gt;', '-->').replace('==&gt;', '==>').replace('-.&gt;', '-.>')
        
        new_lines.append(new_line)
        
    return '\n'.join(new_lines)

for f in files:
    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()
        
    new_content = re.sub(r'(<pre class=\"mermaid\">)(.*?)(</pre>)', 
                         lambda m: m.group(1) + fix_mermaid_block(m.group(2)) + m.group(3), 
                         content, 
                         flags=re.DOTALL)
                         
    if new_content != content:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(new_content)
        changed_files += 1
        print(f'Fixed Mermaid syntax in: {f.name}')

print(f'Total fixed files: {changed_files}')
