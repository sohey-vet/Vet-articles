import re
import json

with open("c:/Users/souhe/Desktop/VetEvidence_SNS_Drafts/all_sunday_digests.md", "r", encoding="utf-8") as f:
    content = f.read()

blocks = re.split(r'---+\s+##', content)[1:]
weeks = []

for block in blocks:
    articles = re.findall(r'[■・①]\s*(?:月曜：|水曜：|金曜：)?([^\n\r]+)', block)
    articles = [a.strip() for a in articles if not a.startswith("神経ブロック")]
    if len(articles) >= 3:
        weeks.append(articles[:3])

with open("c:/Users/souhe/Desktop/VetEvidence_SNS_Drafts/VetEvidence_AutoPost/extracted_weeks.json", "w", encoding="utf-8") as f:
    json.dump(weeks, f, ensure_ascii=False, indent=2)
