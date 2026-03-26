---
description: The definitive structural blueprint and recovery guide for all 108 articles (Golden State 2026.03.26 11:00 Ver).
---

# 🚨 VetEvidence HTML Gold Standard (2026.03.26 11:00 Ver)

このワークフローファイルは、2026年3月26日 11:00時点で完成した「最も美しく、エラーがなく、機能的に完璧な全108記事のHTML構造」を永久保存するための**AI用絶対ルールブック（MEMORY/SKILL）**です。
今後、万が一スクリプトの暴走や誤操作で記事が崩壊した場合、AIはこのドキュメントを参照して「あるべき姿（Golden State）」へ復元しなければなりません。

## 📍 復元用Gitタグ（最重要）
現在の完璧な状態は、GitHub上に **タグ名：`v2026.03.26_1100_Golden`** として永久保存（スナップショット）されています。
もしリポジトリ全体が大規模に崩壊した場合は、以下のコマンドでこの時点に一瞬でロールバック（復元）できます。
`git -C "c:\Users\souhe\Desktop\論文まとめ" reset --hard v2026.03.26_1100_Golden`

## 🏗️ 完璧なHTML構造の定義（DOM Structure）

VetEvidenceのすべてのHTMLファイルは、以下の厳密な階層とクラス名を持っていなければなりません。
自動化スクリプト等でこれらを1ミリでも書き換えることは**禁止**されています。

### 1. メタデータ＆表示切り替えスイッチ
- `<head>` には常に最新のCSSキャッシュバスター（例：`style.css?v=20260326v5`）を含める。
- 本文上部には必ず `<div class="content-mode-bar">` を配置し、プレミアム表示のトグルスイッチを含める。

### 2. 無料公開ゾーン（Free Content）
- `<div class="free-content">` で囲う。
- 結論 `<div class="bottom-line">` や表組み `<div class="card">` をここに配置。

### 3. アコーディオン構造（Premium Zone）
各トピックごとに必ず以下の厳密な入れ子構造を維持すること。
```html
<div class="accordion">
    <button class="accordion-trigger">
        <span class="trigger-left"><span class="trigger-icon">アイコン</span><span>タイトル</span></span><span class="chevron">▼</span>
    </button>
    <div class="accordion-content">
        <div class="accordion-body premium-content">
            <!-- プレミアム本文 -->
        </div>
        <div class="premium-lock"><span class="lock-icon">🔒</span>詳細は有料会員限定です</div>
    </div>
</div>
```

### 4. 飼い主への説明ガイド（Owner Tips）
必ず個別の `div#owner-tips` アンカーを持ち、内部に `speech-bubble` クラスを持つこと。
```html
<div id="owner-tips">
    <!-- アコーディオン構造の内部に以下を配置 -->
    <div class="owner-tip">
        <h4>質問</h4>
        <div class="speech-bubble">回答</div>
    </div>
</div>
```

### 5. 参照論文（References）
必ず `div#refs` を持ち、アコーディオンで開閉可能で、内部は `<ol>` で始まる番号付きリストでなければならない。

---

## 🎨 Pro Mermaid フローチャート規格 (12px / 8px)

フローチャートを描画するMermaidブロックは、スマホでの縦スクロールでの視認性を最高レベルに引き上げた**Proテンプレート**に準拠すること。
全図形に12pxの線と8pxの枠（CSSからグローバル強制適用）が適用されるため、コード自体はクリーンであるべきです。

### 絶対ルール：
1. **コンテナ:** 必ず `<div class="mermaid-wrapper"><pre class="mermaid">` で囲む。
2. **方向:** 常に `graph TD` （上から下）。
3. **ノード:** `A["アクション(四角)"]` または `B{"判断(ひし形)"}` 以外使わない（丸み帯びは廃止）。
4. **矢印（超重要）:** `A -- テキスト --> B` のような書き方はSyntax Error（＝爆弾マーク）の原因になるため**完全禁止**。
   - ⭕ 正解： `A -->|"はい"| B`
5. **装飾:** `subgraph`（大きな囲み）や `style`、`classDef` 等のハードコード装飾はスマホ画面を圧迫するため原則使用しない。

---

## 🚫 開発AIへの禁止事項
1. `md_to_site_html.py` コンパイラを安易に全ファイルに対して回さないこと。このスクリプトには「飼い主ガイド消滅バグ」「フッタータグ混入バグ」等の既知の欠陥（Known Bugs）が含まれており、不用意に回すとこの108記事のGolden Stateが再び破壊されます。
2. もし修正が必要な場合は、**対象のHTMLファイルの当該DOMのみを直接外科手術（Surgical Edit）でピンポイントに置換するアプローチ**を最優先すること。
