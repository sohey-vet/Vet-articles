import urllib.parse
text = open(r'c:\Users\souhe\Desktop\論文まとめ\index.html', encoding='utf-8', errors='ignore').read()
decoded = urllib.parse.unquote(text)
lines = decoded.splitlines()

for title in ['犬の急性下痢_最新エビデンス.html', '犬慢性腸症_CE診断カスケード.html']:
    print('--- Checking', title, '---')
    for i, line in enumerate(lines):
        if title in line:
            for j in range(max(0, i-2), min(len(lines), i+12)):
                if '<div class="card-footer">' in lines[j] or 'span' in lines[j] or 'data-tags' in lines[j]:
                    print(lines[j])
            break
