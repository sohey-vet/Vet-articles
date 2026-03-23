import os, csv

d = r'C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts\VetEvidence_AutoPost\Canva_CSVs'
out_file = r'C:\Users\souhe\.gemini\antigravity\brain\1e185a7b-d16c-4c06-b71c-236033518d81\artifacts\Category_Mapping_List.md'
os.makedirs(os.path.dirname(out_file), exist_ok=True)

files = [f for f in os.listdir(d) if f.endswith('.csv')]
lines = ["# 16カテゴリ別 記事分類リスト\n", "Canvaの各カテゴリ（ひな形）に、どの記事が流し込まれるかの一覧です。\n", "109記事がタグ解析により**合計164箇所**に重複配分されています。\n"]

for f in sorted(files):
    cat_name = f.replace('.csv', '')
    path = os.path.join(d, f)
    with open(path, 'r', encoding='utf-8-sig') as csvfile:
        reader = list(csv.reader(csvfile))
        if len(reader) <= 1:
            continue
        articles = [row[0] for row in reader[1:]]
        lines.append(f"## {cat_name} ({len(articles)}件)\n")
        for a in articles:
            lines.append(f"- {a}")
        lines.append("\n")

with open(out_file, 'w', encoding='utf-8') as outfile:
    outfile.write('\n'.join(lines))
