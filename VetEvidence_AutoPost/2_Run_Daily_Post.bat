@echo off
cd /d "%~dp0"

echo ==========================================
echo VetEvidence AutoPost - Daily Execution
echo ==========================================
echo.
echo [%date% %time%] 起動しました。
echo.

:: X の投稿処理
echo [X] 投稿処理を開始します...
python auto_post_x.py
if %errorlevel% neq 0 (
    echo [X] 投稿処理でエラーが発生しました。ログを確認してください。
)
echo.

:: Threads の投稿処理
echo [Threads] 投稿処理を開始します...
python auto_post_threads.py
if %errorlevel% neq 0 (
    echo [Threads] 投稿処理でエラーが発生しました。ログを確認してください。
)
echo.

echo ==========================================
echo 全ての処理が完了しました。
echo ==========================================
timeout /t 10
