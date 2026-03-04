import os
import glob

typo_map = {
    '采血': '採血',
    '黒キャップ': 'EDTA',
    '增加': '増加',
    '訤取': '摂取',
    '痙攻': '痙攣',
    '若球': '眼球',
    '膜脱分娩': '閉塞解除',
    '體重': '体重',
    '狀態': '状態',
    '發生': '発生',
    '發現': '発見',
    '選擇': '選択',
    '變化': '変化',
    '嚴重': '重度',
    '點滴': '点滴',
    '觀察': '観察',
    '醫師': '医師',
    '獸醫': '獣医',
    '腦': '脳',
    '藥': '薬',
    '靜脈': '静脈',
    '脫水': '脱水',
    '檢査': '検査',
    '氣管': '気管',
    '惡心': '悪心',
    '惡化': '悪化',
    '從来': '従来',
    '應答': '応答',
    '氣胸': '気胸',
    '拔系': '抜糸',
    '拔管': '抜管',
    '麻醉': '麻酔',
    '擴張': '拡張',
    '懷妊': '妊娠',
}

md_files = glob.glob(r'c:\Users\souhe\Desktop\論文まとめ\topics\**\*.md', recursive=True)
total_fixes = 0

log = []

for filepath in md_files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        continue
        
    fixes_in_file = 0
    new_content = content
    
    for bad, good in typo_map.items():
        if bad in new_content:
            count = new_content.count(bad)
            new_content = new_content.replace(bad, good)
            log.append(f'- {os.path.basename(filepath)}: {bad} -> {good} ({count}箇所)')
            fixes_in_file += count
            total_fixes += count
            
    if fixes_in_file > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

if total_fixes == 0:
    print('誤字・不自然な表現は見つかりませんでした。')
else:
    print(f'合計 {total_fixes} 箇所の修正を行いました。')
    print('\n'.join(log))
