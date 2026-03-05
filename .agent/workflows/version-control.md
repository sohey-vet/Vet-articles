---
description: バージョン管理と資産保護ルール — CSS/JSバージョン、Gitコミット、バックアップの必須手順を定義。
---

# 🔖 バージョン管理と資産保護

> **記事の消失・破損を二度と起こさないためのルールです。**

## 1. CSS/JSバージョン管理

### 現在のバージョン
```
style.css?v=20260304v5
script.js?v=20260304v5
```

### バージョン命名規則
```
YYYYMMDD + v + 連番
例: 20260304v5 = 2026年3月4日の第5版
```

### バージョン変更の手順（必ず守る）
1. **ユーザーに確認を取る**（勝手に変えない）
2. CSSまたはJSの変更を行う
3. 新バージョン番号を決定
4. `standardize_articles.py` のLATEST_VERSIONを更新
5. `python scripts/standardize_articles.py` を実行して全記事を一括更新
6. `python /tmp/audit_articles.py` でCSS VERSIONS: が1種類であることを確認

## 2. Gitコミットルール

### HTMLを変更する前に
```bash
git add -A && git commit -m "checkpoint: before [作業内容]"
```

### 一括変更スクリプト実行前に
```bash
git add -A && git commit -m "checkpoint: before batch update"
```

### 変更完了後に
```bash
git add -A && git commit -m "[変更内容の要約]"
```

## 3. 一括変更時の必須検証

一括変更（スクリプトによる全記事修正）を行った後は、必ず以下を実行:

```bash
# 1. 監査スクリプトで全記事を検査
python /tmp/audit_articles.py   # 結果は /tmp/audit_results.txt

# 2. 確認項目
#    - CRITICAL: 0
#    - FORMAT: 0
#    - CSS VERSIONS: 1種類のみ
#    - JS VERSIONS: 1種類のみ

# 3. ブラウザで最低2記事を目視確認
```

## 4. 禁止事項

- ❌ ユーザー確認なしでCSSバージョンを変更する
- ❌ Gitコミットせずに一括変更スクリプトを実行する
- ❌ HTMLファイルの中身を空にする修正を行う
- ❌ `md_to_site_html.py` のテンプレート構造を無断で変更する
