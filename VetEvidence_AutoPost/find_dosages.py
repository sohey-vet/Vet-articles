import json
import re

json_path = r'c:\Users\souhe\Desktop\VetEvidence_SNS_Drafts\VetEvidence_AutoPost\sns_schedule.json'
output_path = r'c:\Users\souhe\Desktop\VetEvidence_SNS_Drafts\VetEvidence_AutoPost\dosages_list.txt'

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

dosage_pattern = re.compile(r'(\d+(\.\d+)?(-|〜|~)?\d*(\.\d+)?\s?(mg|μg|mcg|mL|g)/kg(/?(hr|min|day))?)', re.IGNORECASE)

results = []
for item in data:
    if item['platform'] == 'Threads' and item['type'] == 'Threads Long':
        content = item['content']
        matches = dosage_pattern.findall(content)
        if matches:
            results.append({
                'date': item['date'],
                'source': item['source'],
                'matches': [m[0] for m in matches]
            })

with open(output_path, 'w', encoding='utf-8') as f:
    for r in results:
        f.write(f"Date: {r['date']}, Source: {r['source']}\n")
        f.write(f"Matches: {r['matches']}\n\n")

print(f"Total found: {len(results)}")
