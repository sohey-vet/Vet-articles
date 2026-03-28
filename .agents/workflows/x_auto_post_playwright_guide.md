---
description: X（Twitter）のPlaywright自動スレッド投稿におけるUI操作の厳格な仕様と回避策
---

# X (Twitter) Playwright 自動スレッド投稿プロトコル

XのWeb UI（React / Draft.js）は非常に複雑かつ動的に変化するため、Playwrightでの自動化には特有の「罠」が存在します。本ドキュメントでは、安定してスレッド投稿とリンクプレビュー削除を行うための必須ルールを定義します。

## 1. ゴーストドラフト（背面テキストボックス）の回避
Xでは、投稿モーダル（ポップアップ画面）が開いている裏側で、通常のタイムライン上の「いまどうしてる？」入力欄が `is_visible()` = True の状態で待機しています。
- **絶対ルール**: テキストボックスを検索する際は、単に `[data-testid^="tweetTextarea_"]` を探すのではなく、必ず **`[role="dialog"]`** をプレフィックスとして付与し、現在アクティブなモーダル内に限定すること。
- **NG例**: `page.locator('[data-testid^="tweetTextarea_"]').all()`
- **OK例**: `page.locator('[role="dialog"] [data-testid^="tweetTextarea_"]').all()`

## 2. 背景誤爆による「ポストを保存しますか？」ポップアップの回避
2枚目以降のツリー投稿入力欄は、モーダル内でスクロール枠外（画面外）に配置されることがあります。
- **絶対ルール**: `click(force=True)` は原則禁止。はみ出た要素に対して強制クリックを行うと、要素の中心座標がモーダル外壁（グレーの背景マスク `div[data-testid="twc-cc-mask"]`）に重なり、背景をクリックしたと判定されます。背景クリックはXの「投稿破棄（保存）ダイアログ」を即座に召喚し、以降の処理を完全にロックさせます。
- **回避策**: クリック前に必ずJSのネイティブAPIで画面中央にスクロールさせ、フォーカスを合わせる。
```python
text_box_2.evaluate("el => el.scrollIntoView({block: 'center'})")
time.sleep(1)
text_box_2.evaluate("el => el.focus()")
time.sleep(1)
text_box_2.click() # force=True は不要
```

## 3. 文字入力パターンの標準化（Draft.js対策）
Playwrightの `insert_text()` や `fill()` は、Xのカスタムテキストエディタ（Draft.js）と相性が悪く、ハッシュタグやURL、絵文字（👉等）のパース時に文字消失バグを引き起こします。
- **絶対ルール**: OSのクリップボードを経由した **`Ctrl+V / Meta+V` （ペースト）** 動作でテキストを流し込むこと。

## 4. OGPリンクプレビュー（カード）の確実な削除
URL入力後に自動生成されるリンクプレビュー（顔写真などのカード）は、出現までにネットワーク遅延（最大10秒以上）が生じます。
- **絶対ルール**: 最大15秒間のポーリングを行い、カードの削除ボタンが現れた瞬間にクリックする仕組みを実装すること。
- **クリティカル注意**: 削除ボタンを検索する際、1枚目に添付した「スライド画像（消化器.pngなど）」の削除ボタンまで誤爆して消さないよう、`data-testid` や `aria-label` に `removephoto` や `メディア` が含まれていないかを厳格に除外判定（continue）すること。
- **回避策**:
```javascript
// JSを用いた安全なポーリング削除の実装例（詳細は auto_post_x.py 参照）
if(testid.includes('removephoto') || testid.includes('removemedia') || label.includes('メディア')) {
    continue; // スライド画像を保護
}
if(label.includes('リンクプレビューを削除') || testid.includes('removelinkpreview') || testid.includes('remove-card')) {
    b.click(); // OGPカードのみを削除
    return true;
}
```

## エラー発生時のデバッグ
処理が失敗した場合は、必ず `logs/x_post_log_*.log` と、同階層に自動保存される `failed_state.png` を同時に確認し、Playwrightのエラー内容（Timeout等）とUIの視覚的状態（ポップアップが出ているか、文字が入力されているか）を照らし合わせること。
