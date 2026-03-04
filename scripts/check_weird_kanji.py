import glob
import re

md_files = glob.glob(r'c:\Users\souhe\Desktop\論文まとめ\topics\**\*.md', recursive=True)
anomalies = []

weird_chars = ['體', '狀', '發', '現', '選', '變', '嚴', '點', '觀', '醫', '獸', '腦', '藥', '靜', '脫', '檢', '氣', '惡', '從', '應', '拔', '醉', '擴', '懷', '采', '訤', '攻']
# '現' -> depends on the word, '現状' is normal. Better filter individually, but since we just want a quick test, let's look for explicit anomalies

for filepath in md_files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            for ch in weird_chars:
                if ch in content:
                    anomalies.append(f'{filepath}: contains {ch}')
    except Exception:
        pass

if not anomalies:
    print('No weird characters found.')
else:
    for a in anomalies:
        print(a)
