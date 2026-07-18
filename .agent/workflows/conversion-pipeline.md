---
description: MD→HTML変換パイプライン — 変換スクリプトの使い方と変換後の検証手順を定義。
---

# 🔄 MD→HTML変換パイプライン

> **Markdownから本番HTMLへの変換手順。ミスを防ぐために必ずこの手順に従う。**

> ⚠️ **`md_to_site_html.py` は `scripts/DO_NOT_RUN_md_to_site_html.py` に退避済み・実行/リネーム/復元禁止（2026-07-12）**。
> 現行運用では変換スクリプトを一切使わない。MD→HTML化は **既存記事HTMLの構造を踏襲して手動/AIで生成** し（`/html-structure` 準拠）、生成後に `standardize_articles.py` で標準化・`check_html.py` で検証する。

## 1. MD→HTML生成（手動/AI生成）

変換スクリプトは廃止。新記事のHTMLは、同カテゴリの既存記事HTMLをテンプレートとして構造をそのまま踏襲し、手動またはAIで生成する。

- 構造仕様は `/html-structure` を必ず参照（`#conclusion` → アコーディオン → `#owner-tips` → `#refs` の順、`premium-content`/`premium-lock` 併記など）。
- MDの執筆規約は `/md-writing-rules` を参照。
- 生成後は必ず次項「変換後の必須手順」に進む。

## 2. 生成後の必須手順

```
① 既存HTML構造を踏襲して手動/AIでHTML生成（/html-structure 準拠）
② standardize_articles.py を実行（CSS/JS統一、owner-tips形式確認）
③ check_html.py で構造チェック
④ ブラウザで表示確認
⑤ 問題なければ git commit
```

### 具体的なコマンド
```bash
# Step 1: HTML生成（手動/AI。スクリプトは使わない）

# Step 2: 標準化
python scripts/standardize_articles.py

# Step 3: 構造チェック
python scripts/check_html.py

# Step 4: ブラウザ確認（手動）
# - 結論セクションが表示されるか
# - アコーディオンが正常に動くか
# - 飼い主説明が紫ボーダーか
# - 参照論文が番号付きリストか

# Step 5: コミット
git add -A && git commit -m "feat: Add [記事名] article"
```

## 3. index.htmlへの登録

新記事を追加した場合、`index.html` に記事カードを追加する必要がある。
→ `/index-management` ワークフローを参照。

## 4. 変換スクリプトについて（廃止）

> ⚠️ 旧変換スクリプト `md_to_site_html.py` は `scripts/DO_NOT_RUN_md_to_site_html.py` に退避済み。**実行・リネーム・復元・改変はいずれも禁止**（2026-07-12）。
> テンプレート駆動の自動変換は行わない。HTML生成は既存記事の構造踏襲（手動/AI生成）に一本化されている。標準化・検証は `standardize_articles.py` と `check_html.py` が担う。

## 5. トラブルシューティング

| 問題 | 原因 | 対処 |
|------|------|------|
| 結論が空 | HTMLの `#conclusion` が未生成 | /html-structure 参照・既存記事の構造を踏襲 |
| アコーディオンが閉じない | script.js のバージョン不一致 | standardize_articles.py 実行 |
| 飼い主説明が紫でない | owner-tip クラス未使用 | /html-structure 参照 |
| Mermaid図解エラー | 全角スペース or 記号 | /html-structure セクション8を参照 |
