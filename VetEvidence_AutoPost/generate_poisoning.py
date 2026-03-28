import html_to_note_md_engine as r
import sys

html_file = r'c:\Users\souhe\Desktop\論文まとめ\topics\救急\中毒_初期対応と活性炭.html'
md_file = r'c:\Users\souhe\Desktop\論文まとめ\topics\救急\中毒_初期対応と活性炭.md'

try:
    md_content = r.parse_html_to_markdown(html_file)
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print('✅ Poisoning MD file successfully regenerated using Perfect Logic!')
except Exception as e:
    print('Failed:', e)
    sys.exit(1)
