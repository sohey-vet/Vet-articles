@echo off
setlocal
cd /d "%~dp0"

echo =========================================================
echo VetEvidence X 連日自動投稿 タスクスケジューラ一括登録ツール
echo =========================================================
echo.
echo X(Twitter)の公式仕様上、「ツリー（複数枚）の予約投稿」は
echo アプリ側で禁止（予約ボタンが消滅）されています。
echo.
echo そこで、Windowsの時計機能（タスクスケジューラ）を利用し、
echo 『毎日12:00に自動でブラウザを立ち上げて本番投稿する』
echo スイッチをPCに組み込みます。
echo.
echo ---------------------------------------------------------

REM 管理者権限チェック
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [エラー] 権限が不足しています！
    echo ---------------------------------------------------------
    echo このファイル（1週間のX予約登録.bat）を【右クリック】し、
    echo 【管理者として実行】をクリックして開き直してください。
    echo ---------------------------------------------------------
    pause
    exit /b
)

set TASK_NAME="VetEvidence_X_AutoPost_Weekly"
:: 仮想環境のPythonがうまく使われないケースを考慮し、実行可能な python.exe をそのまま呼び出します
set PYTHON_EXE=python
set SCRIPT_PATH=%~dp0auto_post_x.py

:: 毎週 月,火,水,木,金,土 の 12:00 に実行する
schtasks /Create /F /TN %TASK_NAME% /TR "%PYTHON_EXE% \"%SCRIPT_PATH%\"" /SC WEEKLY /D MON,TUE,WED,THU,FRI,SAT /ST 12:00 /RL HIGHEST /IT

if %errorLevel% equ 0 (
    echo.
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    echo [OK] 登録が完了しました！！
    echo 今後、月～土曜日の【12:00】になると自動でスクリプトが作動し、
    echo その日の sns_schedule.json に入っている草案をすべてXに投稿します。
    echo.
    echo ※注意: 当該時刻には、お使いのPCの電源が入り、スリープが
    echo   解除されている必要があります。（画面を開いておいてください）
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
) else (
    echo.
    echo [NG] 登録に失敗しました。
)
pause
