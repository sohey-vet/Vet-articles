$TaskName = "VetEvidence_Note_AutoPublish"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ActionPath = Join-Path $ScriptDir "Run_Note_Daily_Post.bat"

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "Noteの下書き自動公開（投稿）タスクを登録します..."
Write-Host "登録内容: 毎週 月、水、金 の 12:00 に起動"
Write-Host "（PCがスリープ状態の場合は復帰して実行します）"
Write-Host "=========================================================" -ForegroundColor Cyan

# 古いタスクがあれば削除
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

$Action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$ActionPath`"" -WorkingDirectory $ScriptDir
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Wednesday,Friday -At 12:00
$Settings = New-ScheduledTaskSettingsSet -WakeToRun -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    
$Task = Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "毎週月水金の昼12時にNoteの予約投稿を実行します"

Write-Host ""
Write-Host "✅ タスクの登録を実行しました！" -ForegroundColor Green
Write-Host "[タスク名]: $TaskName"
Write-Host "[実行パス]: $ActionPath"
Write-Host "スリープ状態から復帰して自動的に投稿が行われます。"

Write-Host ""
Write-Host "何かキーを押して閉じてください..."
[void][System.Console]::ReadKey($true)
