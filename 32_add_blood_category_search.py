"""
Add '血液' category and search bar to index.html.
Also update individual article tags where needed.
"""
import re
from pathlib import Path
from bs4 import BeautifulSoup

index_path = Path(r'c:\Users\souhe\Desktop\論文まとめ\index.html')
topics_dir = Path(r'c:\Users\souhe\Desktop\論文まとめ\topics')

# Articles that should have the '血液' tag based on content
# I reviewed all 73 articles - these are ones related to blood/hematology:
blood_articles = [
    'IMHA_診断と初期治療',           # 免疫介在性溶血性貧血 - directly blood
    'ITP_診断と治療',                # 免疫介在性血小板減少症 - directly blood
    'DIC_診断と治療',                # 播種性血管内凝固 - blood coagulation
    '血管肉腫_脾臓心臓型の管理と予後', # 血管の腫瘍 + 血液関連
    '血液ガス分析の基本',             # 血液ガス - directly blood
    '輸液の基本_晶質液vs膠質液',      # 血液量管理
    'ショック時の輸液戦略_ボーラス投与の実際',  # ショック=血液循環不全
    'リンパ腫_犬と猫の違い',          # リンパ球=血液系腫瘍
]

# ============================================================
# Step 1: Update index.html
# ============================================================
with open(index_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1a. Add 血液 genre button to sidebar (after 免疫 button)
blood_btn = '''<button class="genre-btn" data-genre="血液">
<span class="genre-icon">🩸</span>
<span>血液</span>
<span class="genre-count">0</span>
</button>'''

# Insert after the 免疫 button (before 消化器・肝臓)
html = html.replace(
    '<button class="genre-btn" data-genre="消化器・肝臓">',
    f'{blood_btn}\n<button class="genre-btn" data-genre="消化器・肝臓">'
)

# 1b. Add 血液 to genreLabels JS
html = html.replace(
    "'免疫': '🛡️ 免疫',",
    "'免疫': '🛡️ 免疫',\n                '血液': '🩸 血液',"
)

# 1c. Add 血液 tag to relevant article cards' data-tags
for article_name in blood_articles:
    # Find the article card and add 血液 to its data-tags if not already present
    pattern = rf'(data-tags="[^"]*?".*?{re.escape(article_name)})'
    match = re.search(pattern, html, re.DOTALL)
    if not match:
        # Try finding just by article name href
        continue
    
    # More targeted: find data-tags attribute for cards linking to this article
    # Pattern: data-tags="..." followed at some point by the article name
    html_lines = html.split('\n')
    for i, line in enumerate(html_lines):
        if article_name in line and 'data-tags=' in line:
            if '血液' not in line:
                # Add 血液 tag
                line = line.replace('data-tags="', 'data-tags="血液,')
                html_lines[i] = line
                print(f'  Added 血液 tag to card: {article_name}')
    html = '\n'.join(html_lines)

# 1d. Add search bar before the articles grid
search_html = '''<div class="search-container" style="margin-bottom: 16px;">
<input type="text" id="article-search" placeholder="🔍 記事を検索..." autocomplete="off"
       style="width: 100%; padding: 12px 16px; border: 1px solid var(--color-border); border-radius: var(--radius-md);
              background: var(--color-bg-secondary); color: var(--color-text-primary); font-size: 0.9rem;
              font-family: var(--font-sans); outline: none; transition: border-color 0.2s;"
       onfocus="this.style.borderColor='var(--color-accent-primary)'"
       onblur="this.style.borderColor='var(--color-border)'" />
</div>'''

html = html.replace(
    '<div class="articles-grid" id="articles-grid">',
    f'{search_html}\n<div class="articles-grid" id="articles-grid">'
)

# 1e. Add search JS before the closing </script>
search_js = '''
            // Search functionality
            const searchInput = document.getElementById('article-search');
            if (searchInput) {
                searchInput.addEventListener('input', (e) => {
                    const query = e.target.value.trim().toLowerCase();
                    
                    if (!query) {
                        // If search is empty, apply current genre filter
                        const activeBtn = sidebar.querySelector('.genre-btn.active');
                        if (activeBtn) {
                            applyFilter(activeBtn.dataset.genre);
                        } else {
                            applyFilter('all');
                        }
                        return;
                    }
                    
                    // Search across title, description, and tags
                    let visibleCount = 0;
                    cards.forEach(card => {
                        const title = card.querySelector('h3')?.textContent?.toLowerCase() || '';
                        const desc = card.querySelector('p')?.textContent?.toLowerCase() || '';
                        const tags = card.dataset.tags?.toLowerCase() || '';
                        
                        if (title.includes(query) || desc.includes(query) || tags.includes(query)) {
                            card.classList.remove('hidden');
                            visibleCount++;
                        } else {
                            card.classList.add('hidden');
                        }
                    });
                    
                    countBadge.textContent = visibleCount + '件';
                    label.querySelector('span:first-child').textContent = `🔍 "${e.target.value}" の検索結果`;
                    
                    // Deactivate genre buttons during search
                    buttons.forEach(b => b.classList.remove('active'));
                });
            }
'''

html = html.replace(
    "            // Check URL parameters on load",
    f"{search_js}\n            // Check URL parameters on load"
)

with open(index_path, 'w', encoding='utf-8') as f:
    f.write(html)

print('Updated index.html: added 血液 category, search bar, and search JS')

# ============================================================
# Step 2: Update individual article HTML files to add 血液 tag
# ============================================================
for article_name in blood_articles:
    # Find the article file
    matches = list(topics_dir.rglob(f'{article_name}.html'))
    if not matches:
        print(f'  WARNING: Could not find file for {article_name}')
        continue
    
    fpath = matches[0]
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if the article already has a 血液 tag in its tag section
    if '血液' in content and 'tag' in content:
        # Check if it's in the visible tag area (not just data attribute)
        soup = BeautifulSoup(content, 'html.parser')
        tags_div = soup.find('div', class_='article-tags') or soup.find('div', class_='tags-container')
        existing_tags = [t.text.strip() for t in soup.find_all('a', class_='tag')] if soup.find_all('a', class_='tag') else []
        
        if '血液' not in existing_tags:
            # Find the tag section and add 血液 tag
            # Look for the pattern: <a class="tag ..." href="...?tag=xxx">xxx</a>
            tag_pattern = r'(<a class="tag[^"]*" href="[^"]*\?tag=[^"]*">[^<]+</a>)\s*(</div>)'
            tag_match = re.search(tag_pattern, content)
            if tag_match:
                blood_tag_html = '\n<a class="tag tag--warning" href="../../index.html?tag=血液">血液</a>'
                content = content[:tag_match.end(1)] + blood_tag_html + content[tag_match.end(1):]
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f'  Added 血液 tag to article: {fpath.stem}')
            else:
                print(f'  Could not find tag insertion point in: {fpath.stem}')
        else:
            print(f'  血液 tag already exists in: {fpath.stem}')
    else:
        # Need to add the tag
        tag_pattern = r'(<a class="tag[^"]*" href="[^"]*\?tag=[^"]*">[^<]+</a>)\s*(</div>)'
        tag_match = re.search(tag_pattern, content)
        if tag_match:
            blood_tag_html = '\n<a class="tag tag--warning" href="../../index.html?tag=血液">血液</a>'
            content = content[:tag_match.end(1)] + blood_tag_html + content[tag_match.end(1):]
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'  Added 血液 tag to article: {fpath.stem}')
        else:
            print(f'  Could not find tag section in: {fpath.stem}')

print('\nDone!')
