import re
html_path = r'c:\Users\souhe\Desktop\論文まとめ\topics\輸液\輸液の基本_晶質液vs膠質液.html'
with open(html_path, 'r', encoding='utf-8') as f:
    c = f.read()

refs_match = re.search(r'<div id="refs">.*?</div></div>', c, re.DOTALL)
owner_match = re.search(r'<div id="owner-tips">.*?(?=\n<footer class="page-footer")', c, re.DOTALL)

if refs_match and owner_match:
    refs_text = refs_match.group(0)
    owner_text = owner_match.group(0)
    old_full = refs_text + '\n' + owner_text
    new_full = owner_text + '\n' + refs_text
    
    if old_full in c:
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(c.replace(old_full, new_full))
        print('Swapped successfully')
    else:
        print('Combined string not found in content!')
else:
    print('Pattern not found')
