---
description: index.htmlの管理ルール — 新記事追加時のトップページ更新手順を定義。記事追加後に必ず参照。
---

# 🌐 index.html 管理ルール

> **新記事を追加したら、必ずindex.htmlにも登録すること。**

## 1. 記事カードの追加

新記事を `topics/` に追加したら、`index.html` の対応するカテゴリセクションに記事カードを追加する。

### 記事カードのHTML構造
```html
<a class="article-card" href="topics/カテゴリ/ファイル名.html"
   data-tags="タグ1,タグ2,タグ3">
    <div class="article-card-header">
        <span class="card-icon">🏥</span>
        <h3>記事タイトル</h3>
    </div>
    <p class="article-card-desc">記事の概要（1文）</p>
    <div class="article-card-tags">
        <span class="tag tag--primary">タグ1</span>
        <span class="tag tag--success">タグ2</span>
    </div>
</a>
```

## 2. カテゴリとアイコンの対応表

| カテゴリ | アイコン | data-genre |
|---------|---------|------------|
| 救急 | 🚨 | 救急 |
| 循環器 | ❤️ | 循環器 |
| 免疫 | 🛡️ | 免疫 |
| 内分泌 | ⚖️ | 内分泌 |
| 腎泌尿器 | 🫘 | 腎泌尿器 |
| 神経 | 🧠 | 神経 |
| 皮膚 | 🩺 | 皮膚 |
| 猫 | 🐱 | 猫 |
| 腫瘍 | 🔬 | 腫瘍 |
| 輸液 | 💧 | 輸液 |
| 麻酔 | 😴 | 麻酔 |
| 抗菌薬 | 💊 | 抗菌薬 |
| 栄養 | 🍽️ | 栄養 |
| 整形外科 | 🦴 | 整形外科 |
| 歯科 | 🦷 | 歯科 |
| 眼科 | 👁️ | 眼科 |
| 肝臓 | 🫁 | 肝臓 |
| 消化器 | 🍽️ | 消化器 |
| 血液ガス | 🧪 | 血液ガス |

## 3. タグフィルタとの連携

- `data-tags` 属性に含めるタグ名は、URLエンコードなしの日本語
- フィルタ機能はJavaScriptで `data-tags` を読み取って絞り込む
- 新しいタグを追加する場合は、サイドバーのフィルタリストにも追加

## 4. 記事数の更新

`index.html` のヘッダー部分に全記事数が表示されている場合、新記事追加後に更新する。

## 5. 注意事項

- ❌ index.html のCSS/JSリンクのバージョンも `/version-control` に従う
- ❌ 記事カードの構造を勝手に変えない
- 新記事追加後は必ずブラウザで表示確認
