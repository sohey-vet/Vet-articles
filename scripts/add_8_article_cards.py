import os
import re

index_path = r'c:\Users\souhe\Desktop\論文まとめ\index.html'

with open(index_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 誤配置の輸血カードを削除（「参照論文プ本」のバグも含む）
bad_card = '''                    <a class="article-card" data-tags="救急,血液,輸血" href="topics/救急/輸血のベストプラクティス.html"><span
                            class="card-icon">🚨</span>
                        <h3>輸血のベストプラクティス ― 一般病院で安全に実施するために</h3>
                        <p>PCV 15%の犬が携送された。輸血トリガーの判断から投与量計算、副反応モニタリング、猫の注意点まで。エビデンスに基づく輸血プロトコル。</p>
                        <div class="card-footer"><span class="tag tag--primary">救急</span><span class="tag tag--primary">血液</span><span class="tag tag--warning">輸血</span><span
                                class="card-papers">📄 参照論文プ本</span></div>
                    </a>'''

content = content.replace(bad_card, '')

# 2. 各セクションに正しいカードを挿入

cards_to_insert = {
    '<!-- ===== 救急 ===== -->': '''                    <a class="article-card" data-tags="救急,血液,輸血" href="topics/救急/輸血のベストプラクティス.html"><span
                            class="card-icon">🚨</span>
                        <h3>輸血のベストプラクティス ─ 一般病院で安全に実施するために</h3>
                        <p>PCV 15%の犬が搬送された。輸血トリガーの判断から投与量計算、副反応モニタリング、猫の注意点まで。エビデンスに基づく輸血プロトコル。</p>
                        <div class="card-footer"><span class="tag tag--primary">救急</span><span class="tag tag--primary">血液</span><span class="tag tag--warning">輸血</span><span
                                class="card-papers">📄 参照論文5本</span></div>
                    </a>
                    <a class="article-card" data-tags="麻酔,救急" href="topics/麻酔/麻酔中の低血圧_徐脈_トラブルシューティング.html"><span
                            class="card-icon">😴</span>
                        <h3>麻酔中の低血圧・徐脈 ─ トラブルシューティング</h3>
                        <p>術中MAPが45 mmHgまで低下。術中低血圧と徐脈の体系的な原因検索と、エビデンスに基づく薬剤選択・用量を解説。</p>
                        <div class="card-footer"><span class="tag tag--primary">麻酔</span><span class="tag tag--primary">救急</span><span
                                class="card-papers">📄 参照論文5本</span></div>
                    </a>''',
    '<!-- ===== 歯科 ===== -->': '''                    <a class="article-card" data-tags="歯科" href="topics/歯科/歯の破折_抜歯vs保存の判断.html"><span
                            class="card-icon">🦷</span>
                        <h3>歯の破折 ─ 抜歯vs保存の判断</h3>
                        <p>露髄か非露髄か？抜歯か根管治療か？放置すれば100%歯髄壊死に至る破折歯の、エビデンスに基づく診断・治療フロー。</p>
                        <div class="card-footer"><span class="tag tag--primary">歯科</span><span
                                class="card-papers">📄 参照論文5本</span></div>
                    </a>''',
    '<!-- ===== 猫 ===== -->': '''                    <a class="article-card" data-tags="猫,行動" href="topics/猫/猫の多頭飼育ストレス_環境エンリッチメントのエビデンス.html"><span
                            class="card-icon">🐱</span>
                        <h3>猫の多頭飼育ストレス ─ 環境エンリッチメントのエビデンス</h3>
                        <p>N+1ルール、3D空間の確保、フェロモン療法まで。多頭飼育猫のストレスを科学的に管理するための環境最適化ガイド。</p>
                        <div class="card-footer"><span class="tag tag--primary">猫</span><span class="tag tag--warning">行動</span><span
                                class="card-papers">📄 参照論文5本</span></div>
                    </a>''',
    '<!-- ===== 栄養 ===== -->': '''                    <a class="article-card" data-tags="その他" href="topics/栄養/肥満管理_減量プログラムの実際.html"><span
                            class="card-icon">🍽️</span>
                        <h3>肥満管理 ─ 減量プログラムの実際</h3>
                        <p>RER計算による科学的な減量計画から、猫の肝リピドーシスリスク、飼い主コンプライアンス維持戦略まで。</p>
                        <div class="card-footer"><span class="tag tag--primary">その他</span><span
                                class="card-papers">📄 参照論文5本</span></div>
                    </a>'''
}

for marker, card_html in cards_to_insert.items():
    if marker in content:
        content = content.replace(marker, marker + '\n' + card_html, 1)
        print(f'Inserted card after: {marker[:30]}...')
    else:
        print(f'Marker not found: {marker[:30]}...')

# 3. 内分泌・腫瘍・腎泌尿器セクションを探して追加
inner_inserts = [
    ('<!-- ===== 内分泌 ===== -->', '''                    <a class="article-card" data-tags="内分泌,猫" href="topics/内分泌/猫の甲状腺機能亢進症_治療オプション比較.html"><span
                            class="card-icon">⚖️</span>
                        <h3>猫の甲状腺機能亢進症 ─ 治療オプション比較</h3>
                        <p>チアマゾールの用量設定から、I-131の治癒率95%まで。3治療オプションのエビデンス比較と、治療後のCKD顕在化への対応。</p>
                        <div class="card-footer"><span class="tag tag--primary">内分泌</span><span class="tag tag--primary">猫</span><span
                                class="card-papers">📄 参照論文5本</span></div>
                    </a>'''),
    ('<!-- ===== 腫瘍 ===== -->', '''                    <a class="article-card" data-tags="腫瘍,歯科,腎泌尿器" href="topics/腫瘍/扁平上皮癌と移行上皮癌_診断治療セット.html"><span
                            class="card-icon">🔬</span>
                        <h3>扁平上皮癌と移行上皮癌 ─ 診断・治療セット</h3>
                        <p>猫の口腔SCC（70%以上）とBRAF変異検出で診断補助できるUCC/TCC。COX-2阻害薬と化学療法の実践プロトコル。</p>
                        <div class="card-footer"><span class="tag tag--primary">腫瘍</span><span class="tag tag--warning">歯科</span><span class="tag tag--warning">腎泌尿器</span><span
                                class="card-papers">📄 参照論文5本</span></div>
                    </a>'''),
    ('<!-- ===== 泌尿器 ===== -->', '''                    <a class="article-card" data-tags="腎泌尿器,猫" href="topics/腎泌尿器/腎臓病の食事療法_リン制限とカリウム管理.html"><span
                            class="card-icon">🫘</span>
                        <h3>腎臓病の食事療法 ─ リン制限とカリウム管理</h3>
                        <p>IRISステージ別リン目標値、リン吸着剤プロトコル、低K補正。腎臓食導入で生存期間2倍超のエビデンスと実践的な食事管理。</p>
                        <div class="card-footer"><span class="tag tag--primary">腎泌尿器</span><span class="tag tag--primary">猫</span><span
                                class="card-papers">📄 参照論文5本</span></div>
                    </a>'''),
]

for marker, card_html in inner_inserts:
    if marker in content:
        content = content.replace(marker, marker + '\n' + card_html, 1)
        print(f'Inserted card after: {marker[:30]}...')
    else:
        print(f'Marker not found: {marker[:30]}...')

# 4. サイドバーのカウントと総記事数を更新 (+8記事)
content = content.replace('<div class="stat-value" id="stat-theme-count">78</div>', '<div class="stat-value" id="stat-theme-count">86</div>')
content = content.replace('<span class="genre-count" id="count-all">79</span>', '<span class="genre-count" id="count-all">87</span>')
content = content.replace('<span class="count-badge" id="visible-count">79件</span>', '<span class="count-badge" id="visible-count">87件</span>')

with open(index_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Done! index.html updated.')
