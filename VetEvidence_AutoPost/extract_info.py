import os
import re

repo_dir = r'C:\Users\souhe\Desktop\論文まとめ'
files = [
    r'topics\救急\高ナトリウム血症_原因と水脱水アプローチ.html',
    r'topics\眼科\赤い目の鑑別_結膜炎_緑内障.html',
    r'topics\腎泌尿器\犬猫の膀胱炎_ISCAIDガイドライン.html'
]

for f in files:
    path = os.path.join(repo_dir, f)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as h_file:
            html = h_file.read()
            html = re.sub(r'<div class="mermaid">.*?</div>', '', html, flags=re.DOTALL)
            text = ''
            for m in re.finditer(r'<(h2|h3|li|p)[^>]*>(.*?)</\1>', html, re.DOTALL):
                inner = re.sub(r'<[^>]+>', '', m.group(2))
                text += inner.strip() + '\n'
            print('='*50)
            print('FILE:', f)
            print(text[:1500])
