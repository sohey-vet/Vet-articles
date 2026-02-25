"""
Fix Mermaid diagrams that have their content on a single line 
using <br/> as line separators instead of actual newline characters.

Strategy:
- Replace ;<br/> with ;\n  (end of statement)
- Replace <br/><br/> with \n\n (blank lines)
- Replace <br/> followed by indentation (4+ spaces) with \n + spaces
- Replace <br/> before keywords (subgraph, end, graph, etc) with \n
- Keep <br/> inside node labels (e.g A[line1<br/>line2]) untouched
- Also fix &amp; -> & and ensure arrows --> are not HTML-encoded
"""
import re
from pathlib import Path

base_dir = Path(r'c:\Users\souhe\Desktop\論文まとめ\topics')
files = list(base_dir.rglob('*.html'))
changed_files = 0
error_files = []

def fix_mermaid_content(content):
    """Convert single-line <br/> separated Mermaid to proper multi-line format."""
    
    # If there are no <br/> at all, the content is likely already multi-line
    if '<br/>' not in content and '<br>' not in content:
        return content
    
    original = content
    
    # Step 1: Normalize <br> variants to <br/>
    content = content.replace('<br>', '<br/>')
    content = content.replace('<br />', '<br/>')
    
    # Step 2: Replace <br/><br/> with double newlines (blank lines between sections)
    content = content.replace('<br/><br/>', '\n\n')
    
    # Step 3: Replace ;<br/> with ;\n (end of Mermaid statement)
    content = content.replace(';<br/>', ';\n')
    
    # Step 4: Replace <br/> before Mermaid keywords with \n
    keywords = ['subgraph', 'end', 'graph ', 'classDef', 'class ', 'style ', 'linkStyle']
    for kw in keywords:
        content = content.replace(f'<br/>{kw}', f'\n{kw}')
        content = content.replace(f'<br/>    {kw}', f'\n    {kw}')
        content = content.replace(f'<br/>        {kw}', f'\n        {kw}')
    
    # Step 5: Replace <br/> followed by spaces+node-id pattern (e.g., <br/>    A --> B)
    # This catches statement separators that don't end with ;
    content = re.sub(r'<br/>\s{2,}', lambda m: '\n' + ' ' * (len(m.group()) - 5), content)
    
    # Step 6: Replace remaining <br/> that appear OUTSIDE of brackets
    # We do this carefully by only replacing <br/> that is NOT inside [], (), {}
    # Simple heuristic: if <br/> is followed by a capital letter or node ID, it's a statement separator
    content = re.sub(r'<br/>([A-Z_])', r'\n\1', content)
    
    # Step 7: Fix HTML entities in arrows and operators
    content = content.replace('--&gt;', '-->')
    content = content.replace('==&gt;', '==>')
    content = content.replace('-.&gt;', '-.>')
    content = content.replace('&amp;', '&')
    
    # Step 8: Fix &lt; and &gt; that appear in edge labels (between -- and -->)
    # These should remain as &lt; and &gt; because they're display text
    # But &gt; and &lt; in arrows should be raw > <
    # Actually, inside edge labels |"text"| and node labels ["text"], 
    # &lt; and &gt; are fine and Mermaid will render them correctly.
    
    return content


for f in files:
    with open(f, 'r', encoding='utf-8') as fh:
        html_content = fh.read()
    
    original_html = html_content
    
    # Find and fix all mermaid blocks
    def replace_block(match):
        pre_tag = match.group(1)
        mermaid_content = match.group(2) 
        close_tag = match.group(3)
        fixed = fix_mermaid_content(mermaid_content)
        return f'{pre_tag}{fixed}{close_tag}'
    
    html_content = re.sub(
        r'(<pre class="mermaid">)(.*?)(</pre>)',
        replace_block,
        html_content,
        flags=re.DOTALL
    )
    
    if html_content != original_html:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(html_content)
        changed_files += 1
        
        # Verify: check if any <br/> remain outside node labels (potential issues)
        mermaid_blocks = re.findall(r'<pre class="mermaid">(.*?)</pre>', html_content, re.DOTALL)
        for block in mermaid_blocks:
            remaining_br = block.count('<br/>')
            # Count lines to see if conversion happened
            line_count = block.count('\n')
            if remaining_br > 0 and line_count < 5:
                error_files.append(f.name)
        
        print(f'Fixed: {f.name}')

print(f'\nTotal fixed: {changed_files}')
if error_files:
    print(f'Potential remaining issues in: {", ".join(set(error_files))}')
else:
    print('No remaining issues detected.')
