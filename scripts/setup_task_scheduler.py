"""
setup_task_scheduler.py
─────────────────────────────
Windows タスクスケジューラに Note 自動投稿タスクを登録する

月・水・金の 12:00 に note_auto_post.py を自動実行するタスクを作成します。
管理者権限で実行してください。

使い方:
  python scripts/setup_task_scheduler.py          # タスク登録
  python scripts/setup_task_scheduler.py --remove  # タスク削除
"""

import subprocess
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(r"c:\Users\souhe\Desktop\論文まとめ")
TASK_NAME = "VetEvidence_Note_AutoPost"
PYTHON_PATH = sys.executable
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "note_auto_post.py"

# Scheduled Task XML template
TASK_XML = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>VetEvidence Note 自動投稿 - 月水金 12:00</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2026-03-04T12:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByWeek>
        <DaysOfWeek>
          <Monday />
          <Wednesday />
          <Friday />
        </DaysOfWeek>
        <WeeksInterval>1</WeeksInterval>
      </ScheduleByWeek>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>true</WakeToRun>
    <ExecutionTimeLimit>PT30M</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{PYTHON_PATH}</Command>
      <Arguments>"{SCRIPT_PATH}"</Arguments>
      <WorkingDirectory>{PROJECT_ROOT}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"""


def register_task():
    """タスクスケジューラにタスクを登録"""
    xml_path = PROJECT_ROOT / "scripts" / "_task_scheduler.xml"
    xml_path.write_text(TASK_XML, encoding="utf-16")

    cmd = [
        "schtasks", "/Create",
        "/TN", TASK_NAME,
        "/XML", str(xml_path),
        "/F"  # 既存タスクがあれば上書き
    ]

    print(f"📅 タスク登録中: {TASK_NAME}")
    print(f"   Python: {PYTHON_PATH}")
    print(f"   Script: {SCRIPT_PATH}")
    print(f"   スケジュール: 月・水・金 12:00")
    print()

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ タスクスケジューラへの登録が完了しました！")
        print()
        print("📋 確認方法:")
        print("   1. Win+R → 'taskschd.msc' で タスクスケジューラ を開く")
        print(f"   2. タスクスケジューラ ライブラリ → '{TASK_NAME}' を確認")
        print()
        print("⚠️  注意事項:")
        print("   - PCが起動していて、ログインしている必要があります")
        print("   - StartWhenAvailable=true のため、PC起動時に遅延分が追いつきます")
        print("   - 投稿する記事がない場合は何も起こりません")
    else:
        print(f"❌ エラー: {result.stderr}")
        print("   管理者権限で実行してみてください")

    # XML テンプレートを削除
    if xml_path.exists():
        xml_path.unlink()


def remove_task():
    """タスクスケジューラからタスクを削除"""
    cmd = ["schtasks", "/Delete", "/TN", TASK_NAME, "/F"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ タスク '{TASK_NAME}' を削除しました。")
    else:
        print(f"❌ エラー: {result.stderr}")


if __name__ == "__main__":
    if "--remove" in sys.argv:
        remove_task()
    else:
        register_task()
