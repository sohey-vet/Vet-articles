import os
import io

desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
bat_path = os.path.join(desktop, '【1クリック】1週間分のX予約スタート.bat')

content = """@echo off
cd /d "C:\\Users\\souhe\\Desktop\\VetEvidence_SNS_Drafts\\VetEvidence_AutoPost"

echo =========================================================
echo 🐾 VetEvidence 1週間分の一括準備(ボタン1つで完結) 🐾
echo =========================================================
echo.
echo [1] 実行日の「次の月曜日」を起算日として最新スケジュール(JSON)を生成中...
python extract_drafts.py
if %errorlevel% neq 0 (
    echo.
    echo [エラー] スケジュール生成に失敗しました！
    pause
    exit /b
)

echo.
echo [2] 最新のスケジュールをもとに、Xの「1枚目」を1週間分公式予約します...
python schedule_1week_x.py
if %errorlevel% neq 0 (
    echo.
    echo [エラー] Xの予約機能中に問題が発生しました！
    pause
    exit /b
)

echo.
echo =========================================================
echo 🎉 すべての準備が完了しました！
echo このままパソコンの電源を入れたままにしておけば、
echo 毎日【12:01】にタスクスケジューラが追尾ボットを自動で射出し、
echo 予約された1枚目に対して「Noteのリンク」を返信してくれます。
echo =========================================================
echo.
pause
"""

with open(bat_path, 'w', encoding='cp932') as f:
    f.write(content)
