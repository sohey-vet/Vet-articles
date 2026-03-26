@echo off
cd /d "%~dp0"
echo ==========================================
echo Threads 自動投稿 初回ログインセットアップ
echo ==========================================
echo.
echo ブラウザが起動しますので、Threads(Instagram)のアカウントでログインしてください。
echo ログインが完了し、ホーム画面が表示されたら、コマンドプロンプト上でEnterを押して終了してください。
echo.
python auto_post_threads.py --setup
pause
