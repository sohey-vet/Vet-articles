import html_to_note_md_engine as r
import sys

html_file = r'c:\Users\souhe\Desktop\論文まとめ\topics\抗菌薬\抗菌薬選択の基本原則.html'
md_file = r'c:\Users\souhe\Desktop\論文まとめ\topics\抗菌薬\抗菌薬選択の基本原則.md'

try:
    md_content = r.parse_html_to_markdown(html_file)
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print('✅ Antibiotics MD file successfully regenerated using Perfect Logic!')
except Exception as e:
    print('Failed:', e)
    sys.exit(1)
