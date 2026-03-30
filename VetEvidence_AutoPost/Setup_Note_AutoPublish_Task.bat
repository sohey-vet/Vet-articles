@echo off
setlocal
cd /d "%~dp0"

echo -------------------------------------------------------------
echo タスクスケジューラ登録スクリプトを管理者権限で実行します
echo -------------------------------------------------------------
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process powershell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \""%~dp0Setup_Note_AutoPublish_Task.ps1\""' -Verb RunAs"

echo 登録プロセスを起動しました。
timeout /t 3
endlocal
