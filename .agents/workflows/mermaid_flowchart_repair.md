---
description: How to repair and standardize broken Mermaid flowcharts in HTML articles WITHOUT triggering full re-compilation.
---

# Mermaid Flowchart Surgical Repair Workflow

このワークフローは、記事内の「爆弾マーク（Syntax Error）」になっているMermaidフローチャートを、元の記事本文のデータを1ミリも壊さずに外科手術のように修復・最適化し、全108記事を一貫した「スマホ見やすいPro仕様」に保全するための絶対ルールです。

## 🚨 絶対禁止事項（DO NOT DO THIS）
- `md_to_site_html.py` 等の自動コンパイラツールを実行してMarkdownからHTMLを上書きすることは**絶対厳禁**です。
- HTML内の `<pre class="mermaid">` ブロック「以外」の要素（結論、解説、詳細アコーディオン、owner-tips等）を消去・変更してはいけません。

## 📍 修復ステップ

1. **直接編集（Surgical Edit）:**
   対象の `.html` ファイルを直接開き、`<div class="mermaid-wrapper"><pre class="mermaid">` と `</pre></div>` の間にある Mermaid コードのみを置換します。

2. **Proテンプレート・構文ルール（Mermaid Syntax Rules）:**
   * **レイアウト:** 常に `graph TD` （上から下へのスマホ縦長レイアウト）を使用する。
   * **ノード定義:** 日本語の直接定義はせず、必ず `A["テキスト"]` のように英字IDとダブルクォーテーションで囲む。
   * **条件分岐（ひし形）:** `B{"質問内容？"}`
   * **分岐矢印（絶対エラー回避）:** ❌ `H -- YES --> I` は使用禁止。
     ✅ 必ず `H -->|"はい"| I` または `H -->|"いいえ"| J` の形式に従う。
   * **ノード内改行:** 必要以上の長文は避け、改行は極力使わない（使う場合は `A["テキスト1<br/>テキスト2"]` とし、クォート内に含める）。

3. **デザインと太さ（CSSの適任性）:**
   線の太さ（12px）や枠線の太さ（8px）、フォントサイズはすべて `assets/style.css` 側で既にグローバルに設定されています。
   記事のHTML側で `style="..."` やMermaidの `classDef` などを個別注入する必要は**ありません**。
   `<div class="mermaid-wrapper"><pre class="mermaid">` のクラス構造が保たれていれば自動的にCSSが適用されます。

4. **キャッシュ対策のアプデ（不要な場合は省略）:**
   もしブラウザキャッシュが強すぎて修正が反映されない場合は、HTMLの `<head>` にある `style.css?v=20260326v5` などのクエリパラメータを `v6` や `v7` へスクリプトで一斉に書き換えます（Cache Busting）。

### ✅ 完璧な「Proチャート」のひな形
```html
<div class="mermaid-wrapper"><pre class="mermaid">
graph TD
    A["来院: 呼吸困難の犬"] --> B{"第一優先: ストレス最小化"}
    B --> C["酸素フローバイ即開始"]

    C --> D{"鎮静なしで安全に留置確保は可能か？"}
    D -->|"はい (安全)"| E["フロセミド IV (2-4mg/kg)"]
    D -->|"いいえ (無理せず)"| F["フロセミド IM (2-4mg/kg)"]

    E --> G["留置確保済み"]
    F --> H["鎮静が効いてから留置確保を試みる"]
    H --> G
</pre></div>
```
