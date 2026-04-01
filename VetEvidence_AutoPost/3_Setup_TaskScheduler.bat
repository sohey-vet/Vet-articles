@echo off
chcp 65001 > nul
echo ----------------------------------------------------
echo ? VetEvidence 自動投稿タスクスケジューラ登録スクリプト
echo ----------------------------------------------------
echo 月〜日の12:00に自動実行するタスクを作成します。

set TASK_NAME=VetEvidence_AutoPost_MonToSat
set SCRIPT_PATH=%~dp02_Run_Daily_Post.bat

echo.
echo 【登録内容】
echo タスク名: %TASK_NAME%
echo 実行スクリプト: %SCRIPT_PATH%
echo.

schtasks /create /tn "%TASK_NAME%" /tr "\"%SCRIPT_PATH%\"" /sc weekly /d MON,TUE,WED,THU,FRI,SAT,SUN /st 12:00 /ru "%USERNAME%" /f

if %ERRORLEVEL% equ 0 (
    echo.
    echo ? タスクの登録に成功しました！
    echo （毎週 月〜日 の 12:00 に背面で自動実行されます）
) else (
    echo.
    echo ? タスクの登録に失敗しました。
    echo 管理者権限でこのバッチファイルを実行してみてください（右クリック -^> 管理者として実行）。
)

echo.
pause
