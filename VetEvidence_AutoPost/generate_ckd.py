import html_to_note_md_engine as r
import sys

html_file = r'c:\Users\souhe\Desktop\論文まとめ\topics\腎泌尿器\猫のCKD_IRISステージ別管理.html'
md_file = r'c:\Users\souhe\Desktop\論文まとめ\topics\腎泌尿器\猫のCKD_IRISステージ別管理.md'

try:
    md_content = r.parse_html_to_markdown(html_file)
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print('✅ CKD MD file successfully regenerated using Perfect Logic!')
except Exception as e:
    print('Failed:', e)
    sys.exit(1)
