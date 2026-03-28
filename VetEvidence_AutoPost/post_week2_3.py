import subprocess
import sys

dates = [
    "2026-04-06", # ②月_救急_犬猫の中毒_よくある原因物質と初期対応
    "2026-04-08", # ②水_抗菌薬_抗菌薬選択の基本原則
    "2026-04-10", # ②金_免疫_IMHA_診断と初期治療
    "2026-04-13", # ③月_救急_ショック管理_最新プロトコル
    "2026-04-15", # ③水_循環器_猫のHCM_早期発見と管理
    "2026-04-17"  # ③金_神経_椎間板ヘルニア_頚部胸腰部統合版
]

for date in dates:
    print(f"\n======================================")
    print(f"🚀 開始: {date} のNote下書きアップロード")
    print(f"======================================")
    try:
        subprocess.run(["python", "auto_post_note.py", "--date", date, "--draft"], check=True)
        print(f"✅ {date} 完了")
    except subprocess.CalledProcessError as e:
        print(f"❌ {date} エラー発生: {e}")
        sys.exit(1)
