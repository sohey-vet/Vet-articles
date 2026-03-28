@echo off
setlocal
cd /d "%~dp0"

echo =========================================================
echo VetEvidence X 追尾自動リプライ タスクスケジューラ登録ツール
echo =========================================================
echo.
echo 新仕様：
echo Xの公式予約機能で「1枚目」をあらかじめ12:00に予約しておき、
echo その直後（12:01）にこのPCからボットが起動して、
echo 「2枚目（NoteURL＋写真削除）」を自動でリプライします。
echo （※PCがスリープ状態の場合でも、自動でスリープを解除する設定を含みます）
echo.
echo ---------------------------------------------------------

REM 管理者権限チェック
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [エラー] 権限が不足しています！
    echo ---------------------------------------------------------
    echo このファイルを【右クリック】し、
    echo 【管理者として実行】をクリックして開き直してください。
    echo ---------------------------------------------------------
    pause
    exit /b
)

set TASK_NAME="VetEvidence_X_ReplyBot"
set PYTHON_EXE=python
set SCRIPT_PATH=%~dp0reply_note_link.py

:: 毎週 月,火,水,木,金,土 の 12:01 にボットを起動する
schtasks /Create /F /TN %TASK_NAME% /TR "%PYTHON_EXE% \"%SCRIPT_PATH%\"" /SC WEEKLY /D MON,TUE,WED,THU,FRI,SAT /ST 12:01 /RL HIGHEST /IT

if %errorLevel% equ 0 (
    :: Powershell を使って「タスクを実行するためにスリープを解除する」にチェックを入れる
    powershell -Command "$task = Get-ScheduledTask -TaskName 'VetEvidence_X_ReplyBot'; $task.Settings.WakeToRun = $true; Set-ScheduledTask -InputObject $task"
    
    echo.
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    echo [OK] 登録が完了しました！！
    echo 今後、月～土曜日の【12:01】になると自動で追尾ボットが作動し、
    echo 先ほど投稿されたばかりの1枚目の記事を見つけ出し、
    echo 2枚目（Note誘導）を自動でリプライします。
    echo.
    echo ※スリープ解除(WakeToRun)設定がONになりましたので、
    echo   PCがスリープしていても12:01に自動復帰して実行されます！
    echo   (ロック画面のままでも動作するようプログラムは改良されています)
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
) else (
    echo.
    echo [NG] 登録に失敗しました。
)
pause
