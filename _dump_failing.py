import re
from pathlib import Path

failing_files = [
    Path(r'c:\Users\souhe\Desktop\論文まとめ\topics\内分泌\クッシング症候群_診断の落とし穴.html'),
    Path(r'c:\Users\souhe\Desktop\論文まとめ\topics\循環器\不整脈の救急対応_心電図の読み方.html'),
    Path(r'c:\Users\souhe\Desktop\論文まとめ\topics\猫\FIP_抗ウイルス薬時代の治療.html'),
    Path(r'c:\Users\souhe\Desktop\論文まとめ\topics\猫\猫の輸液_犬との違いと注意点.html'),
    Path(r'c:\Users\souhe\Desktop\論文まとめ\topics\神経\椎間板ヘルニア_頚部胸腰部統合版.html'),
    Path(r'c:\Users\souhe\Desktop\論文まとめ\topics\神経\発作の初期対応_頭蓋内疾患を疑うとき.html'),
    Path(r'c:\Users\souhe\Desktop\論文まとめ\topics\血液ガス\血液ガス分析の基本.html'),
]

for f in failing_files:
    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()
    blocks = re.findall(r'<pre class="mermaid">(.*?)</pre>', content, re.DOTALL)
    print(f'===FILE: {f.stem}===')
    for i, block in enumerate(blocks):
        print(f'---BLOCK {i+1}---')
        print(block)
        print('---END---')
    print()
