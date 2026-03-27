import html_to_note_md_engine as r
import sys

html_file = r'c:\Users\souhe\Desktop\論文まとめ\topics\循環器\心原性肺水腫_一般病院での救命Tips.html'
md_file = r'c:\Users\souhe\Desktop\論文まとめ\topics\循環器\心原性肺水腫_一般病院での救命Tips.md'

try:
    md_content = r.parse_html_to_markdown(html_file)
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print('✅ Pulmonary Edema MD file successfully regenerated using Perfect Logic!')
except Exception as e:
    print('Failed:', e)
    sys.exit(1)
