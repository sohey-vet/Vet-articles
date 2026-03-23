# VetEvidence SNS 自動投稿システム

このシステムは、月・水・金の週3回開始されるXとThreadsの投稿スケジュールを自動化するためのプログラム群です。

## フォルダ構成
- `extract_drafts.py` : `VetEvidence_SNS_Drafts` 直下のフォルダから原稿（X用パターン1,2、Threads用）を抽出し、日付を割り当てて `sns_schedule.json` を生成します。
- `auto_post_x.py` : JSONスケジュールから「今日」のX用原稿を読み取り、Tweepy（API経由）で即時投稿します。
- `auto_post_threads.py` : JSONスケジュルから「今日」のThreads用原稿を読み取り、Playwright（ブラウザ自動化）経由で即時投稿します。

## 初回セットアップ手順

### 1. X (Twitter) API キーの設定
同じフォルダ内に `.env` という名前のファイルを作成し、以下の内容を記述して保存してください（既存の `Sohey_X_Project` からコピーして内容を貼り付けます）。
```env
X_API_KEY=あなたのAPI_KEY
X_API_SECRET=あなたのAPI_SECRET
X_ACCESS_TOKEN=あなたのACCESS_TOKEN
X_ACCESS_TOKEN_SECRET=あなたのACCESS_TOKEN_SECRET
```

### 2. Threadsのログイン
`0_Setup_Threads_Login.bat` をダブルクリックして実行します。
ブラウザが立ち上がりますので、Threads（Instagram）にログインしてください。
ログインが完了し、タイムラインが表示されたら、コマンドプロンプトの画面上で `Enter` キーを押して終了します（セッション情報が保存されます）。

## 日常の運用手順

### A. スケジュールの作成（週1回 または 原稿追加時）
`1_Extract_Drafts.bat` をダブルクリックで実行します。
ドラフトから投稿予定を一括抽出し、`sns_schedule.json` が更新されます。

### B. 日々の自動投稿
`2_Run_Daily_Post.bat` を実行すると、その日の予定の投稿（XおよびThreads）が自動で「即時投稿」されます。
**💡おすすめの運用方法**
Windowsの「タスク スケジューラ」を開き、以下のように設定することで毎日完全自動で投稿されます。
- トリガー：毎日 11:00 など
- 操作：プログラムの開始
- プログラム/スクリプト：`C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts\VetEvidence_AutoPost\2_Run_Daily_Post.bat`
- 「開始（オプション）」に必ず `C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts\VetEvidence_AutoPost\` を指定してください。
