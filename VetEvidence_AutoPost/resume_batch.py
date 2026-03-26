import os
import sys
import json
import time

SCHEDULE_FILE = "sns_schedule.json"

with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

unique_articles = []
seen_sources = set()
for item in data:
    source = item.get("source", "")
    if source and source not in seen_sources:
        seen_sources.add(source)
        unique_articles.append({
            "date": item["date"],
            "source": source
        })

# 1〜7番目はすでに成功しているため、8番目から15番目までを再開する
target_list = unique_articles[7:15]

print("==================================================")
print(f"📦 先ほど中断した8記事目からの下書き生成バッチを再開します（全8記事）")
print("==================================================")

for i, item in enumerate(target_list, 8):
    d = item["date"]
    src = item["source"]
    print(f"\n▶ 処理中 {i}/15: [{d}] {src}")
    
    ret = os.system(f'python auto_post_note.py --date "{d}" --draft')
    if ret != 0:
        print(f"⚠️ エラーが発生したため処理を中断しました: {d}")
        sys.exit(1)
    
    if i < 15:
        print(f"⏳ 次の記事へのアクセス制限を回避するため 7秒待機します...")
        time.sleep(7)

print("\n🎉 全15記事の下書き生成が完全に完了いたしました！")
