import html_to_note_md_engine as r
import sys

html_file = r'c:\Users\souhe\Desktop\論文まとめ\topics\救急\ショック管理_最新プロトコル.html'
md_file = r'c:\Users\souhe\Desktop\論文まとめ\topics\救急\ショック管理_最新プロトコル.md'

try:
    md_content = r.parse_html_to_markdown(html_file)
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print('✅ Shock Management MD file successfully regenerated using Perfect Logic!')
except Exception as e:
    print('Failed:', e)
    sys.exit(1)
