import os, re

# 1. Update index.html
idx_path = r'C:\Users\souhe\Desktop\論文まとめ\index.html'
if os.path.exists(idx_path):
    text = open(idx_path, 'r', encoding='utf-8').read()
    if '消化器・肝臓' in text:
        text = text.replace('消化器・肝臓', '消化器')
        
    hp1 = '犬の急性下痢_最新エビデンス.html'
    hp2 = '急性膵炎_犬猫の違いと管理.html'
    hp3 = '犬慢性腸症_CE診断カスケード.html'
    
    for base_h in [hp1, hp2, hp3]:
        pattern = r'(<a\s+class="article-card"\s+data-tags=")[^"]*("\s+href="[^"]*' + re.escape(base_h) + r'")'
        def r_func(m):
            return m.group(1) + '消化器' + m.group(2)
        text = re.sub(pattern, r_func, text)

    open(idx_path, 'w', encoding='utf-8').write(text)
    print('index.html fully updated')

# 2. Update .md files
from glob import glob
md_paths = glob(r'C:\Users\souhe\Desktop\論文まとめ\topics\**\犬の急性下痢_最新エビデンス.md', recursive=True) + \
           glob(r'C:\Users\souhe\Desktop\論文まとめ\topics\**\急性膵炎_犬猫の違いと管理.md', recursive=True) + \
           glob(r'C:\Users\souhe\Desktop\論文まとめ\topics\**\犬慢性腸症_CE診断カスケード.md', recursive=True)

for p in md_paths:
    text = open(p, 'r', encoding='utf-8').read()
    text = re.sub(r'tags:\s*\[.*?\]', 'tags: [消化器]', text)
    open(p, 'w', encoding='utf-8').write(text)
    print('Updated MD:', os.path.basename(p))

# 3. Update .html files
html_paths = glob(r'C:\Users\souhe\Desktop\論文まとめ\topics\**\犬の急性下痢_最新エビデンス.html', recursive=True) + \
             glob(r'C:\Users\souhe\Desktop\論文まとめ\topics\**\急性膵炎_犬猫の違いと管理.html', recursive=True) + \
             glob(r'C:\Users\souhe\Desktop\論文まとめ\topics\**\犬慢性腸症_CE診断カスケード.html', recursive=True)

for p in html_paths:
    text = open(p, 'r', encoding='utf-8').read()
    # match <div class=\"article-tags\">\n followed by any number of standard 	ag spans up to </div>
    m = re.search(r'(<div\s+class="article-tags">\s*)(.*?)(</div>)', text, flags=re.DOTALL)
    if m:
        new_tags = '<span class="tag tag--primary">消化器</span>\n    '
        text = text[:m.start(2)] + new_tags + text[m.end(2):]
        open(p, 'w', encoding='utf-8').write(text)
        print('Updated HTML:', os.path.basename(p))

# 4. Update md_to_site_html.py mapping
md2_path = r'C:\Users\souhe\Desktop\論文まとめ\scripts\md_to_site_html.py'
if os.path.exists(md2_path):
    text = open(md2_path, 'r', encoding='utf-8').read()
    if "'消化器・肝臓':" in text:
        text = text.replace("'消化器・肝臓': '🍽️ 消化器・肝臓'", "'消化器': '🍽️ 消化器'")
        text = text.replace("'消化器・肝臓',", "'消化器',")
        open(md2_path, 'w', encoding='utf-8').write(text)
        print('Updated md_to_site_html.py')

print('All python tasks completed!')
