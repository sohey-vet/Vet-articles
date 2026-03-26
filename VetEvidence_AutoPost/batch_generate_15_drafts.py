import os
import sys
import json
import time

SCHEDULE_FILE = "sns_schedule.json"

with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# 記事の重複を排除し、ユニークなソースを最初から15個抽出する
unique_articles = []
seen_sources = set()
for item in data:
    source = item.get("source", "")
    if source and source not in seen_sources:
        # Noteへの投稿は必ず最初の日付のものを使用するため、最初に出現した日付を記録
        seen_sources.add(source)
        unique_articles.append({
            "date": item["date"],
            "source": source
        })

target_list = unique_articles[:15]

print("==================================================")
print(f"📦 最初の5週間分（全15記事）の下書き量産バッチを開始します")
print("==================================================")

for i, item in enumerate(target_list, 1):
    d = item["date"]
    src = item["source"]
    print(f"\n▶ 処理中 {i}/15: [{d}] {src}")
    
    # すでにNoteへの投稿をテスト済みのWeek 1に関しては、念のためそのまま生成させます。
    # 重複する場合はNoteのUI上で手動削除していただく運用となります。
    
    ret = os.system(f'python auto_post_note.py --date "{d}" --draft')
    if ret != 0:
        print(f"⚠️ エラーが発生したため処理を中断しました: {d}")
        sys.exit(1)
    
    if i < len(target_list):
        print(f"⏳ 次の記事へのアクセス制限を回避するため 7秒待機します...")
        time.sleep(7)

print("\n🎉 全15記事の下書き生成が完了いたしました！")
