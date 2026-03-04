import glob

files = [
    r'c:\Users\souhe\Desktop\論文まとめ\topics\救急\高カリウム血症_致死的不整脈の回避と治療.html',
    r'c:\Users\souhe\Desktop\論文まとめ\topics\救急\難産と帝王切開_救急対応フロー.html',
    r'c:\Users\souhe\Desktop\論文まとめ\topics\救急\高ナトリウム血症_原因と水脱水アプローチ.html',
]

for path in files:
    with open(path, encoding='utf-8') as fp:
        content = fp.read()
    checks = {
        'title': '<title>' in content,
        'h1': '<h1' in content,
        'conclusion': 'id="conclusion"' in content,
        'accordion': 'accordion' in content,
        'owner-tips': 'owner-tips' in content,
        'refs': 'id="refs"' in content,
        'nav': 'slide-menu' in content,
    }
    name = path.split('\\')[-1]
    size = len(content)
    print(f'{name} ({size:,} bytes)')
    for k, v in checks.items():
        status = 'OK' if v else 'MISSING'
        print(f'  {k}: {status}')
    print()
