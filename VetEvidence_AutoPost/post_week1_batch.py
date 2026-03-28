import os
import time
import sys

dates = ["2026-03-30", "2026-04-01", "2026-04-03"]
titles = [
    "①月_下痢_犬の急性下痢_最新エビデンス", 
    "①水_腎泌尿器_猫のCKD_IRISステージ別管理", 
    "①金_循環器_心原性肺水腫_一般病院での救命Tips"
]

print("==================================================")
print("📦 投稿プラン1週目（全3記事）のバッチ投稿を開始します")
print("==================================================")

for i, (d, title) in enumerate(zip(dates, titles), 1):
    print(f"\n▶ 処理中 {i}/3: [{d}] {title}")
    ret = os.system(f"python auto_post_note.py --date {d} --draft")
    if ret != 0:
        print(f"❌ エラーが発生したため中断しました: {d}")
        sys.exit(1)
    
    # 連続投稿によるNote側のスパム判定やPlaywrightのプロファイル競合を防ぐための待機
    if i < 3:
        print(f"⏳ 次の記事まで10秒待機します...")
        time.sleep(10)

print("\n🎉 全3記事のNoteへの自動投稿が完了いたしました！")
