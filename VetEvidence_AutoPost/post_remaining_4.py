import subprocess
import sys

dates = [
    "2026-04-06", # 中毒
    "2026-04-10", # IMHA
    "2026-04-15", # HCM
    "2026-04-17"  # 椎間板ヘルニア
]

for date in dates:
    print(f"\n🚀 {date} のNote下書きアップロード開始")
    try:
        subprocess.run(["python", "auto_post_note.py", "--date", date, "--draft"], check=True)
        print(f"✅ {date} 完了")
    except subprocess.CalledProcessError as e:
        print(f"❌ {date} エラー発生: {e}")
