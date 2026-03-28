import json
import os

schedule_file = r'c:\Users\souhe\Desktop\VetEvidence_SNS_Drafts\VetEvidence_AutoPost\sns_schedule.json'
out_file = r'C:\Users\souhe\.gemini\antigravity\brain\e4b66c2d-e5db-4e1b-89f6-34d1b39a6b4c\sns_schedule_table.md'

with open(schedule_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

from collections import defaultdict
by_date = defaultdict(list)
for item in data:
    by_date[item['date']].append(item)

dates = sorted(by_date.keys())

md_lines = ['# 📅 SNS予約投稿スケジュール一覧', '', '| 日付 | X (Pattern 1) | X (Pattern 2) | Threads |', '| :--- | :--- | :--- | :--- |']

for d in dates:
    p1, p2, th = '', '', ''
    for item in by_date[d]:
        if item['platform'] == 'X' and item['type'] == 'Pattern 1': p1 = item['source']
        if item['platform'] == 'X' and item['type'] == 'Pattern 2': p2 = item['source']
        if item['platform'] == 'Threads': th = item['source']
    md_lines.append(f'| {d} | {p1} | {p2} | {th} |')

with open(out_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(md_lines))

print('Done')
