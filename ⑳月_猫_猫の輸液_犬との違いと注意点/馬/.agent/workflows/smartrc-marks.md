---
description: SmartRcに印を自動で付けるワークフロー
---

## 前提
- Chrome + ChromeDriver がインストール済み
- `c:\Users\souhe\Desktop\馬\robot_chrome_profile` にログイン状態が保存済み
- **スキル `smartrc-marking` を必ず先に読むこと**

## 手順

### 1. スキル参照（必須）
まず `.agent/skills/smartrc-marking/SKILL.md` を読み、印付けルール・データフォーマット・技術的制約を確認する。

### 2. ユーザーからリストA/B/Cを受け取る
テキスト形式でリストA（勝率順）、リストB（単勝パターン）、リストC（追加候補）を受け取る。

### 3. smartrc_auto.py のデータセクションを更新
- `LIST_A`, `LIST_B`, `LIST_C` を受け取ったデータで埋める
- フォーマット: `'会場名+レース番号R': [(馬番, '馬名'), ...]`
- リストCはレースキーに `R` が付かない場合がある（`normalize_race_key` が自動対応）
- **VENUES設定は不要**（v11は会場を自動検出する）

### 4. スクリプト実行
```powershell
cd c:\Users\souhe\Desktop\馬
python smartrc_auto.py
```

> [!CAUTION]
> **絶対に `taskkill /F /IM chrome.exe` を使わないこと！** ユーザーの普段使いのChromeまで全部落ちる。
> スクリプトは専用プロファイル(`robot_chrome_profile`)と専用デバッグポート(9222)で動くので、
> ユーザーのChromeとは干渉しない。もしプロファイルロックエラーが出たら、
> タスクマネージャーで `robot_chrome_profile` を使っているChromeだけを手動で終了する。

### 5. ログイン確認
- スクリプトが「✅ ログイン済み」と表示すれば自動で開始
- 「❌ ログインしていません」の場合: 自動ログインが試行される
- 自動ログイン失敗時: ブラウザでログイン→Enter

### 6. 結果確認
- スクリプト完了後、別ブラウザ/スマホでSmartRcにログインして印を確認

## 重要な教訓（絶対に守ること）
1. **スキル参照**: 印付け前に必ず `smartrc-marking` スキルを読む
2. **ログイン確認**: `Ext.isReady` は使わない。「ログアウト」ボタンの存在で確認する
3. **レース移動**: 会場初回はホーム→場所→R、2回目以降は←戻る→次のR
4. **スクロール**: レース一覧の要素は `scrollIntoView` してからクリック
5. **Chrome競合**: 専用プロファイル＋専用ポートで分離。`taskkill` 禁止
6. **印操作**: UIクリックで操作する（Store APIの直接操作は保存されない）
