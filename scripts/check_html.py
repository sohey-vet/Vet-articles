import glob
import re
import sys
from collections import Counter

if len(sys.argv) > 1:
    files = sys.argv[1:]
else:
    files = sorted(glob.glob(r'c:\Users\souhe\Desktop\PawMedical\VetEvidence_Website\topics\**\*.html', recursive=True))

ng_count = 0
for path in files:
    with open(path, encoding='utf-8') as fp:
        content = fp.read()
    name = path.split('\\')[-1]

    checks = {
        'title': '<title>' in content,
        'h1': '<h1' in content,
        'conclusion': 'id="conclusion"' in content,
        'accordion': 'accordion' in content,
        'owner-tips': 'owner-tips' in content,
        'refs': 'id="refs"' in content,
        'nav': 'slide-menu' in content,
        'body-mode-free': '<body class="mode-free">' in content,
        'premium-lock': 'premium-lock' in content,
    }
    failed = [f'missing:{k}' for k, v in checks.items() if not v]

    # refs件数の整合性: 見出し「参照論文（N本）」の数字と実際の<li>数を照合
    refs_pos = content.find('id="refs"')
    if refs_pos != -1:
        ol_match = re.search(r'<ol[^>]*>(.*?)</ol>', content[refs_pos:], re.DOTALL)
        li_count = len(re.findall(r'<li[ >]', ol_match.group(1))) if ol_match else 0
        label_match = re.search(r'参照論文（(\d+)本）', content)
        if label_match is not None and int(label_match.group(1)) != li_count:
            failed.append(f'refs-count-mismatch(label={label_match.group(1)},li={li_count})')

    # 用量表記: レンジは全角〜のみ許容（半角ハイフンは禁止）
    bad_dosage = re.findall(r'\d+(?:\.\d+)?-\d+(?:\.\d+)?\s*(?:mg|mL|µg|g)/kg', content)
    if bad_dosage:
        failed.append(f'dosage-halfwidth-hyphen({len(bad_dosage)}件)')

    if failed:
        ng_count += 1
        print(f'NG {name}: {", ".join(failed)}')

    # エビデンス強度表現の一覧（NG判定はしない・目視確認の補助）
    evidence_phrases = re.findall(r'(推奨される|有効とされる|を検討する|記載なし|すべきである)', content)
    if evidence_phrases:
        tally = Counter(evidence_phrases)
        summary = ', '.join(f'{k}x{v}' for k, v in tally.items())
        print(f'INFO {name}: evidence-tier phrases - {summary}')

print(f'checked {len(files)} files / NG: {ng_count}')
