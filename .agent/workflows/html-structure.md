---
description: HTML記事の構造仕様書 — CSSバージョン、必須構造要素、テンプレートを定義。記事作成・修正時に必ず参照。
---

# 🏗️ HTML記事 構造仕様書

> **このSkillはVetEvidenceの全HTML記事に適用される絶対ルールです。例外なく従ってください。**

## 1. CSS/JSバージョン（絶対厳守）

```
style.css?v=20260304v5
script.js?v=20260304v5
```

> ⚠️ **このバージョンを変更してはならない。** 変更が必要な場合は必ずユーザーに確認し、変更後は全94記事を一括更新すること。

## 2. 必須HTML構造（上から順）

```
<!DOCTYPE html>
<html lang="ja">
<head>
  ├── charset, viewport, description, title
  └── style.css（上記バージョン）
<body class="mode-premium">
  ├── nav.mobile-nav（ハンバーガーメニュー）
  ├── aside.slide-menu（サイドナビ）
  ├── div.page-container
  │   ├── header.page-header
  │   │   ├── div.tags（タグバッジ複数）
  │   │   ├── h1（記事タイトル、font-size:1.3rem）
  │   │   ├── p.subtitle（サブタイトル）
  │   │   └── div.meta-bar（参照論文X本 + 更新日）
  │   ├── div.content-mode-bar（切替トグル）
  │   ├── div.free-content#conclusion（🎯 結論）
  │   ├── hr.section-divider
  │   ├── div（📖 詳細解説 + 全展開/全折りボタン）
  │   ├── div.accordion × N本（PREMIUM ZONE）
  │   ├── div#owner-tips（🗣️ 飼い主説明）
  │   ├── div#refs（📚 参照論文）
  │   └── footer.page-footer（トップリンク + 免責）
  └── script.js（上記バージョン）
  └── [Mermaidがある場合のみ] mermaid初期化script
```

## 3. タグバッジのカラールール

| クラス | 用途 | 例 |
|--------|------|----|
| `tag--primary` | メインジャンル | 救急、免疫、循環器 |
| `tag--warning` | 関連ジャンル（注意系） | 血液 |
| `tag--success` | 動物種 | 犬、猫 |
| `tag--danger` | 緊急系 | 緊急 |

## 4. アコーディオン構造（詳細解説）

```html
<div id="セクション名">
<div class="accordion">
    <button class="accordion-trigger">
        <span class="trigger-left">
            <span class="trigger-icon">📋</span>
            <span>セクションタイトル</span>
        </span>
        <span class="chevron">▼</span>
    </button>
    <div class="accordion-content">
        <div class="accordion-body premium-content">
            <!-- コンテンツ -->
        </div>
        <div class="premium-lock">
            <span class="lock-icon">🔒</span>
            セクションタイトルの詳細は有料会員限定です
        </div>
    </div>
</div>
</div>
```

**必須クラス:**
- `accordion-body` に `premium-content` クラスを必ず付与
- `premium-lock` を各アコーディオンに必ず含める

## 5. 飼い主説明（#owner-tips）— 紫ボーダー形式

```html
<div id="owner-tips">
<div class="accordion">
    <button class="accordion-trigger">
        <span class="trigger-left">
            <span class="trigger-icon">🗣️</span>
            <span>飼い主への説明ガイド</span>
        </span>
        <span class="chevron">▼</span>
    </button>
    <div class="accordion-content">
        <div class="accordion-body premium-content">
            <div class="owner-tip" style="margin-top:0;">
                <h4>質問テキスト</h4>
                <div class="speech-bubble">回答テキスト</div>
            </div>
            <div class="owner-tip">
                <h4>質問テキスト2</h4>
                <div class="speech-bubble">回答テキスト2</div>
            </div>
        </div>
        <div class="premium-lock">
            <span class="lock-icon">🔒</span>
            飼い主説明ガイドは有料会員限定です
        </div>
    </div>
</div>
</div>
```

**絶対ルール:**
- アイコンは `🗣️`（💬ではない）
- Q&Aは `owner-tip` クラス + `speech-bubble` クラスの組み合わせ
- 最初の `owner-tip` には `style="margin-top:0;"` を付与
- 2〜3個のQ&Aを含める

## 6. 参照論文（#refs）

```html
<div id="refs">
<div class="accordion">
    <button class="accordion-trigger">
        <span class="trigger-left">
            <span class="trigger-icon">📚</span>
            <span>参照論文（X本）</span>
        </span>
        <span class="chevron">▼</span>
    </button>
    <div class="accordion-content">
        <div class="accordion-body premium-content">
            <ol style="padding-left:20px;font-size:0.82rem;color:var(--color-text-secondary);">
                <li>著者 et al. タイトル. <em>雑誌名</em> 年;巻(号):ページ.</li>
            </ol>
        </div>
    </div>
</div>
</div>
```

**ルール:**
- `<ol>` で番号付きリスト
- 雑誌名は `<em>` でイタリック
- メタバーの「参照論文X本」と`<span>`の「参照論文（X本）」の数を一致させる

## 7. フッター

```html
<footer class="page-footer" style="margin-top: var(--space-xl);">
    <p><a href="../../index.html">← トップに戻る</a> | VetEvidence 🩺</p>
    <p style="margin-top:4px;font-size:0.68rem;color:var(--color-text-muted);">
        ※本まとめは臨床判断の参考資料です。個々の症例の治療方針は担当獣医師の判断に委ねられます。</p>
</footer>
```

## 8. Mermaid図解のルール

- `<pre class="mermaid">...</pre>` で記述（Markdownコードブロック禁止）
- 結論セクションの直後など、常に表示される位置に配置
- 全角スペース・HTMLタグ禁止
- 初期化スクリプトを `</body>` 直前に配置:

```html
<script type="module">
    import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";
    mermaid.initialize({ startOnLoad: true, securityLevel: "loose", theme: "default" });
</script>
```

## 9. 検証

記事作成・修正後は必ず以下を実行:
```
python scripts/standardize_articles.py
```
