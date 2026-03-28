import regenerate_md_from_html_perfect as r
import sys

html_file = r'c:\Users\souhe\Desktop\論文まとめ\topics\下痢\犬の急性下痢_最新エビデンス.html'
md_file = r'c:\Users\souhe\Desktop\論文まとめ\topics\下痢\犬の急性下痢_最新エビデンス.md'

try:
    md_content = r.parse_html_to_markdown(html_file)
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print('✅ MD file successfully regenerated using Perfect Logic!')
except Exception as e:
    print('Failed:', e)
    sys.exit(1)
