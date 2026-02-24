import os
from bs4 import BeautifulSoup
from pathlib import Path

base_dir = Path(r'c:\Users\souhe\Desktop\論文まとめ\topics')
files = list(base_dir.rglob('*.html'))

issues = []

for f in files:
    with open(f, 'r', encoding='utf-8') as fh:
        soup = BeautifulSoup(fh, 'html.parser')
        
    file_issues = []
    if not soup.find('div', id='owner-tips'):
        file_issues.append('Missing id=owner-tips section')
    if not soup.find('div', id='refs'):
        file_issues.append('Missing id=refs section')
        
    if file_issues:
        issues.append((f, file_issues))

print(f'\nFound {len(issues)} files with formatting issues.')

def insert_section_before_footer(soup, html_snippet):
    footer = soup.find('footer', class_='page-footer')
    if footer:
        snippet_soup = BeautifulSoup(html_snippet, 'html.parser')
        footer.insert_before(snippet_soup)

generic_owner_tips = """
<div id="owner-tips">
    <div class="accordion">
        <button class="accordion-trigger">
            <span class="trigger-left"><span class="trigger-icon">🗣️</span><span>飼い主への説明ガイド</span></span>
            <span class="chevron">▼</span>
        </button>
        <div class="accordion-content">
            <div class="accordion-body premium-content">
                <div class="owner-tip" style="margin-top:0;">
                    <h4>このテーマについて</h4>
                    <div class="speech-bubble">
                        本記事は専門的な病態・手技に関する内容（ガイドライン・手技比較・薬理等）であるため、飼い主向けの個別ガイドは省略しています。
                    </div>
                </div>
            </div>
            <div class="premium-lock"><span class="lock-icon">🔒</span>飼い主説明ガイドは有料会員限定です</div>
        </div>
    </div>
</div>
"""

generic_refs = """
<div id="refs">
    <div class="accordion">
        <button class="accordion-trigger">
            <span class="trigger-left"><span class="trigger-icon">📚</span><span>参照論文・資料</span></span>
            <span class="chevron">▼</span>
        </button>
        <div class="accordion-content">
            <div class="accordion-body">
                <ol style="padding-left:20px;font-size:0.82rem;color:var(--color-text-secondary);">
                    <li>本まとめは、関連する獣医学成書や各種国際ガイドラインの一般原則に基づいて作成されています。個別具体的な最新論文については別記事をご参照ください。</li>
                </ol>
            </div>
        </div>
    </div>
</div>
"""

fixed_count = 0
for path, errs in issues:
    with open(path, 'r', encoding='utf-8') as fh:
        soup = BeautifulSoup(fh, 'html.parser')
    
    if 'Missing id=owner-tips section' in errs:
        insert_section_before_footer(soup, generic_owner_tips)
    if 'Missing id=refs section' in errs:
        insert_section_before_footer(soup, generic_refs)
        
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(str(soup))
    print(f'Fixed {path.name}')
    fixed_count += 1

print(f'\nSuccessfully repaired {fixed_count} files.')
