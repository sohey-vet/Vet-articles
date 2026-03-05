---
description: プロジェクト構造マップ — ディレクトリ・ファイルの役割を定義。新しい会話でプロジェクトを理解するために参照。
---

# 📁 プロジェクト構造マップ

> **このドキュメントはVetEvidenceプロジェクトの全体構造を定義します。ファイルの場所や役割がわからない場合はここを参照。**

## ディレクトリ構造

```
c:\Users\souhe\Desktop\論文まとめ\
├── index.html              ← トップページ（記事一覧・検索・フィルタ）
├── CONTENT_PLAN.md          ← 記事公開スケジュール（週3回: 月水金）
├── X_NOTE_運用戦略.md        ← X集客 + Note有料化の戦略書
├── NOTE_投稿ガイド.md        ← Note投稿の手順書
├── MEMO_Note有料化構想.md    ← Note有料化の検討メモ
├── note_post_log.json       ← Note自動投稿の実行ログ
│
├── assets/
│   ├── style.css            ← 全記事共通のCSS（バージョン管理必須）
│   └── script.js            ← 全記事共通のJS（アコーディオン等）
│
├── topics/                  ← 本番HTML記事（GitHub Pages公開用）
│   ├── 免疫/                ← カテゴリ別にHTMLファイルを格納
│   ├── 循環器/
│   ├── 救急/
│   ├── ...（全20ジャンル）
│   └── 各カテゴリに .md と .html が存在
│
├── topics_note/             ← Note投稿用に変換された記事
│   └── カテゴリ/ → Note用に整形されたMD/HTMLファイル
│
├── scripts/
│   ├── md_to_site_html.py     ← MD→HTML変換スクリプト（メイン）
│   ├── standardize_articles.py ← 全記事の一括標準化
│   ├── format_articles_for_note.py ← Note用記事のフォーマット
│   ├── note_auto_post.py      ← Note自動投稿（Playwright）
│   ├── setup_task_scheduler.py ← Windowsタスクスケジューラ設定
│   ├── check_html.py          ← HTML構造チェック
│   ├── check_weird_kanji.py   ← 異体字・旧字チェック
│   ├── fix_typos.py           ← 誤字修正スクリプト
│   └── enhance_note_articles.py ← Note記事の強化
│
├── templates/
│   ├── article_template.html  ← HTML記事の雛形
│   └── note_article_template.md ← Note記事の雛形
│
├── .agent/
│   ├── workflows/            ← Skillsファイル（このファイル含む）
│   ├── artifacts/            ← AI生成の中間成果物
│   └── proofreading/         ← 校正関連ファイル
│
└── .git/                     ← Gitリポジトリ（GitHub連携済み）
```

## 重要な数字

| 項目 | 数値 | 備考 |
|------|------|------|
| HTML記事数 | 94 | topics/ 配下 |
| MD記事数 | 34 | topics/ 配下 |
| カテゴリ数 | 約20 | 救急、循環器、免疫 等 |
| CSSバージョン | 20260304v5 | 全記事統一済み |

## ファイルの関係性

```
[MDファイル] → md_to_site_html.py → [HTMLファイル]
                                        ↓
                              standardize_articles.py
                                        ↓
                              [標準化されたHTML]
                                        ↓
                              format_articles_for_note.py
                                        ↓
                              [Note用記事] → note_auto_post.py → [Note公開]
```
