@echo off
cd /d "%~dp0.."

echo ==========================================
echo VetEvidence_SNS_Drafts - Git Auto Push
echo ==========================================
echo.
echo [%date% %time%] バックアップ処理を開始します...

:: 変更をステージング
git add .
if %errorlevel% neq 0 (
    echo [エラー] git add に失敗しました。
    pause
    exit /b
)

:: コミット（変更がない場合はスキップされる）
git commit -m "Auto backup: %date% %time%"
if %errorlevel% neq 0 (
    echo [情報] コミット対象の新しい変更はありませんでした。
) else (
    echo [成功] 変更をコミットしました。
)

:: プッシュ
echo.
echo [Push] リモートリポジトリ(Github等)へ送信中...
git push origin sns-drafts
if %errorlevel% neq 0 (
    echo.
    echo [警告] git push に失敗しました。以下の原因が考えられます：
    echo  ・リモートリポジトリ(origin)がまだ設定されていない
    echo  ・ネットワーク接続エラー
    echo.
    echo リモートリポジトリが未設定の場合は、コマンドプロンプトやVSCodeターミナルで
    echo 以下のコマンドを実行してGithub等と連携してください：
    echo   git remote add origin ^<あなたのリポジトリURL^>
    echo   git push -u origin sns-drafts
    echo.
) else (
    echo [成功] 変更内容のプッシュが完了しました！
)

echo ==========================================
pause
