---
description: MD→HTML変換パイプライン — 変換スクリプトの使い方と変換後の検証手順を定義。
---

# 🔄 MD→HTML変換パイプライン

> **Markdownから本番HTMLへの変換手順。ミスを防ぐために必ずこの手順に従う。**

## 1. 変換スクリプト

### 個別ファイル変換
```bash
python scripts/md_to_site_html.py --file topics/カテゴリ/記事名.md
```

### 新規ファイル一括変換
```bash
python scripts/md_to_site_html.py --all-new
```

## 2. 変換後の必須手順

```
① 変換実行
② standardize_articles.py を実行（CSS/JS統一、owner-tips形式確認）
③ ブラウザで表示確認
④ 問題なければ git commit
```

### 具体的なコマンド
```bash
# Step 1: 変換
python scripts/md_to_site_html.py --file topics/カテゴリ/記事名.md

# Step 2: 標準化
python scripts/standardize_articles.py

# Step 3: ブラウザ確認（手動）
# - 結論セクションが表示されるか
# - アコーディオンが正常に動くか
# - 飼い主説明が紫ボーダーか
# - 参照論文が番号付きリストか

# Step 4: コミット
git add -A && git commit -m "feat: Add [記事名] article"
```

## 3. index.htmlへの登録

新記事を追加した場合、`index.html` に記事カードを追加する必要がある。
→ `/index-management` ワークフローを参照。

## 4. 変換スクリプト（md_to_site_html.py）の修正ルール

> ⚠️ `md_to_site_html.py` を変更する場合は、以下を必ず守る:

1. 変更前にGitコミット
2. 変更内容をユーザーに説明
3. テスト変換を1ファイルで実行して確認
4. 問題なければ全記事に適用

## 5. トラブルシューティング

| 問題 | 原因 | 対処 |
|------|------|------|
| 結論が空 | MDの「## 結論」セクションがない | MDファイルを確認 |
| アコーディオンが閉じない | script.js のバージョン不一致 | standardize_articles.py 実行 |
| 飼い主説明が紫でない | owner-tip クラス未使用 | /html-structure 参照 |
| Mermaid図解エラー | 全角スペース or 記号 | /html-structure セクション8を参照 |
