---
description: SNSドラフト作成手順 — 各SNS（X, Note, Threads, IG）向けの投稿ドラフトを一括生成するプロセス。
---

# 📲 SNSドラフト一括生成手順

記事のMarkdownから、Note、X（旧Twitter）、Threads、Instagramの各SNS向けドラフトを一括で自動生成します。新しく記事を作成した際や、SNS投稿の準備をする際にこのワークフロー（`/sns-draft-generation`）に従ってください。

## 1. ドラフト一括生成の実行

`scripts/generate_all_sns.py` を使用して、対象のMarkdown（またはHTML）ファイルから全SNS向けのドラフトを生成します。

```bash
python scripts/generate_all_sns.py "topics/カテゴリ/記事名.md"
```

## 2. 生成されるファイルと保存先

スクリプトを実行すると、以下の場所に各SNS用のドラフトが生成されます。

### ① X, Threads, Instagram 用のドラフト
デスクトップの専用フォルダに、一括してまとめられたMarkdownが生成されます。複数パターンの提案やカルーセル台本が含まれます。
- 保存先: `~/Desktop/VetEvidence_SNS_Drafts/カテゴリ_記事名/sns_all_drafts.md`
- 内容:
  - **X用**: 3パターン（昔vs今型、結論ファースト型、数字で驚かせる型）
  - **Threads用**: 長文・専門的な掘り下げテキスト
  - **Instagram用**: 10枚のカルーセルスライド用台本とキャプション、および**Canva一括作成用データ（`ig_carousel_data.csv`）**

### ② Note 用のドラフト
Note用のフォーマットに変換されたMarkdownがプロジェクト内に生成されます。
- 保存先: `topics_note/カテゴリ/記事名/記事名.md`

## 3. ドラフト生成後のフロー

1. **内容確認**: 生成された `sns_all_drafts.md` および Note用記事に目を通し、専門的観点から微調整を行います。
2. **Xの投稿**: 確認済みのテキストを用いて、`/x-posting` のルールに従い手動または自動で投稿予約を行います。
3. **Noteの投稿**: `topics_note/` の記事を `/note-posting` の手順（`note_auto_post.py`）に従って自動投稿または手動投稿します。
4. **Instagramの作成**: `ig_carousel_data.csv` をCanvaの「一括作成（Bulk Create）」機能に読み込ませ、画像デザインを自動生成します。（事後抽出したい場合は `python scripts/export_ig_csv.py` を実行してください）
5. **Threadsの投稿**: 長手テキストを活用して展開します。

## 💡 留意事項
- Gemini API（`gemini-3.1-pro-preview` 等）を使用してテキストを自動生成します。.env設定が必要です。
- 獣医師向けの専門性を保つため、「D50」などの直訳的な略語は「50%ブドウ糖」などに自動で日本語展開されるプロンプトが組み込まれています。現場の略語（IV, CRIなど）は維持されます。
