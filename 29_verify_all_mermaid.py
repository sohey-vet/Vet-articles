"""
Create a single test HTML file containing ALL Mermaid blocks from ALL articles.
Each block is labeled with its source filename for easy identification.
This allows browser verification of all diagrams at once.
"""
import re
from pathlib import Path

base_dir = Path(r'c:\Users\souhe\Desktop\論文まとめ\topics')
files = sorted(base_dir.rglob('*.html'))

html_parts = ['''<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>All Mermaid Verification</title>
<style>
body { background: #1a1a2e; color: white; padding: 20px; font-family: sans-serif; }
.test-block { margin: 20px 0; padding: 15px; border: 1px solid #333; border-radius: 8px; }
.test-block h3 { color: #38bdf8; margin: 0 0 10px 0; font-size: 0.85rem; }
.pass { border-color: #22c55e; }
.fail { border-color: #ef4444; }
</style>
</head><body>
<h1>Mermaid Rendering Verification - All Articles</h1>
<p id="status">Loading...</p>
''']

block_count = 0
for f in files:
    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()
    
    blocks = re.findall(r'<pre class="mermaid">(.*?)</pre>', content, re.DOTALL)
    for i, block in enumerate(blocks):
        block_id = f'block_{block_count}'
        label = f'{f.parent.name}/{f.stem}'
        if len(blocks) > 1:
            label += f' (block {i+1})'
        
        html_parts.append(f'''
<div class="test-block" id="{block_id}" data-file="{label}">
<h3>{label}</h3>
<pre class="mermaid">
{block}
</pre>
</div>
''')
        block_count += 1

html_parts.append(f'''
<script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script>
<script>
mermaid.initialize({{ startOnLoad: true, theme: 'dark' }});

// After rendering, check which blocks have errors
setTimeout(() => {{
  const blocks = document.querySelectorAll('.test-block');
  let passed = 0, failed = 0;
  const failList = [];
  blocks.forEach(block => {{
    const svg = block.querySelector('svg');
    const hasError = svg && (svg.querySelector('.error-text') || svg.innerHTML.includes('Syntax error'));
    const noSvg = !svg;
    if (hasError || noSvg) {{
      block.classList.add('fail');
      failed++;
      failList.push(block.dataset.file);
    }} else {{
      block.classList.add('pass');
      passed++;
    }}
  }});
  document.getElementById('status').innerHTML = 
    `<span style="color:#22c55e">PASS: ${{passed}}</span> / <span style="color:#ef4444">FAIL: ${{failed}}</span><br>` +
    (failList.length > 0 ? '<b>Failed:</b><br>' + failList.join('<br>') : '<b>All diagrams render correctly!</b>');
}}, 5000);
</script>
</body></html>
''')

output = Path(r'c:\Users\souhe\Desktop\論文まとめ\_verify_all_mermaid.html')
with open(output, 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(html_parts))

print(f'Created verification page with {block_count} Mermaid blocks from {len(files)} files')
