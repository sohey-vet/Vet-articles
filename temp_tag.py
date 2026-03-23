import os
md_path = r'C:\Users\souhe\.gemini\antigravity\brain\1e185a7b-d16c-4c06-b71c-236033518d81\artifacts\article_tag_verification.md'
text = open(md_path, encoding='utf-8').read()
lines = text.splitlines()

targets = ['犬の急性下痢_最新エビデンス', '急性膵炎_犬猫の違いと管理', '犬慢性腸症_CE診断カスケード']

new_lines = []
for line in lines:
    if '|' in line and '.html' in line:
        if any(t in line for t in targets):
            cols = [col.strip() for col in line.split('|')]
            cols[3] = chr(96) + '消化器' + chr(96)
            cols[4] = 'なし'
            line = '| ' + ' | '.join(cols[1:-1]) + ' |'
    new_lines.append(line)

open(md_path, 'w', encoding='utf-8').write('\n'.join(new_lines))
print('Updated article_tag_verification.md successfully')
