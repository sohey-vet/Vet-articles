import glob

files = sorted(glob.glob(r'c:\Users\souhe\Desktop\PawMedical\VetEvidence_Website\topics\**\*.html', recursive=True))

ng_count = 0
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
        'body-mode-free': '<body class="mode-free">' in content,
        'premium-lock': 'premium-lock' in content,
    }
    failed = [k for k, v in checks.items() if not v]
    if failed:
        ng_count += 1
        name = path.split('\\')[-1]
        print(f'NG {name}: missing {", ".join(failed)}')

print(f'checked {len(files)} files / NG: {ng_count}')
