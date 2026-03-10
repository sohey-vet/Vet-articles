import os
import re

base = r'c:\Users\souhe\Desktop\論文まとめ'

articles_info = [
    ('topics/救急/輸血のベストプラクティス.html', 5, 'PCV 15%の犬が搬送された。輸血トリガーの判断から投与量計算、副反応モニタリング、猫の注意点まで。エビデンスに基づく輸血プロトコル。'),
    ('topics/歯科/歯の破折_抜歯vs保存の判断.html', 5, '露髄か非露髄か？抜歯か根管治療か？放置すれば100%歯髄壊死に至る破折歯の、エビデンスに基づく診断・治療フロー。'),
    ('topics/猫/猫の多頭飼育ストレス_環境エンリッチメントのエビデンス.html', 5, 'N+1ルール、3D空間の確保、フェロモン療法まで。多頭飼育猫のストレスを科学的に管理するための環境最適化ガイド。'),
    ('topics/麻酔/麻酔中の低血圧_徐脈_トラブルシューティング.html', 5, '術中MAPが45 mmHgまで低下。術中低血圧と徐脈の体系的な原因検索と、エビデンスに基づく薬剤選択・用量を解説。'),
    ('topics/内分泌/猫の甲状腺機能亢進症_治療オプション比較.html', 5, 'チアマゾールの用量設定から、I-131の治癒率95%まで。3治療オプションのエビデンス比較と、治療後のCKD顕在化への対応。'),
    ('topics/栄養/肥満管理_減量プログラムの実際.html', 5, 'RER計算による科学的な減量計画から、猫の肝リピドーシスリスク、飼い主コンプライアンス維持戦略まで。'),
    ('topics/腫瘍/扁平上皮癌と移行上皮癌_診断治療セット.html', 5, '猫の口腔SCC（70%以上）とBRAF変異検出で診断補助できるUCC/TCC。COX-2阻害薬と化学療法の実践プロトコル。'),
    ('topics/腎泌尿器/腎臓病の食事療法_リン制限とカリウム管理.html', 5, 'IRISステージ別リン目標値、リン吸着剤プロトコル、低K補正。腎臓食導入で生存期間2倍超のエビデンスと実践的な食事管理。'),
]

for html_path, refs, desc in articles_info:
    full_path = os.path.join(base, html_path.replace('/', os.sep))
    if os.path.exists(full_path):
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = re.sub(r'参照論文\d+本', f'参照論文{refs}本', content)
        content = re.sub(r'参照論文（\d+本）', f'参照論文（{refs}本）', content)
        content = re.sub(r'<meta content="" name="description"', f'<meta content="{desc}" name="description"', content)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Fixed: {os.path.basename(full_path)}')
    else:
        print(f'Not found: {full_path}')
