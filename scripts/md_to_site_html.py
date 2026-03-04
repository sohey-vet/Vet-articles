"""
md_to_site_html.py
─────────────────────────────
Markdown 記事 → サイト（VetEvidence）HTML 変換スクリプト

使い方:
  python scripts/md_to_site_html.py --file topics/救急/高カリウム血症_致死的不整脈の回避と治療.md
  python scripts/md_to_site_html.py --all-new   (Markdownが新規でHTMLが未作成のものを全変換)
"""

import os
import re
import sys
import html as htmllib
from pathlib import Path

PROJECT_ROOT = Path(r"c:\Users\souhe\Desktop\論文まとめ")
STYLE_VERSION = "20260304v2"


def extract_tags_from_meta(md_text: str, title: str) -> list[dict]:
    """メタデータからタグを生成。ジャンルを使う。"""
    genre_match = re.search(r'ジャンル:\s*(.+)', md_text)
    tags = []
    if genre_match:
        genres = [g.strip() for g in genre_match.group(1).split('・')]
        for g in genres:
            css_class = "tag--primary"
            if g in ["皮膚", "外科", "整形"]:
                css_class = "tag--warning"
            elif g in ["猫", "犬"]:
                css_class = "tag--success"
            tags.append({"label": g, "class": css_class, "query": g})
    if not tags:
        tags = [{"label": "救急", "class": "tag--primary", "query": "救急"}]
    return tags


def md_to_html_body(md_text: str) -> str:
    """MarkdownのbodyをHTMLに変換（簡易版）"""
    lines = md_text.splitlines()
    result = []
    list_type = None  # None, 'ul', or 'ol'
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Skip metadata section
        if stripped.startswith('## メタデータ'):
            break
        
        # Skip HTML tags that we'll handle separately (owner-tips, refs)
        if stripped.startswith('<div id="owner-tips"') or stripped.startswith('<div id="refs"'):
            # consume until matching close
            depth = 0
            while i < len(lines):
                l = lines[i]
                depth += l.count('<div')
                depth -= l.count('</div>')
                i += 1
                if depth <= 0:
                    break
            continue

        is_bullet = stripped.startswith('- ') or stripped.startswith('✅ ') or stripped.startswith('* ')
        is_number = re.match(r'^\d+\. ', stripped)

        # Close open list if list type changes or list ends
        if list_type:
            if stripped == '' or stripped.startswith('#') or stripped.startswith('> '):
                # Empty line or new block closes the list
                pass # We will handle empty line closing later to allow multi-paragraph list items if needed, but for simplicity, let's just close on non-list items.
            
            if not is_bullet and not is_number and stripped != '':
                 result.append(f'</{list_type}>')
                 list_type = None
            elif list_type == 'ul' and is_number:
                 result.append('</ul>')
                 list_type = None
            elif list_type == 'ol' and is_bullet:
                 result.append('</ol>')
                 list_type = None

        # Heading 2
        if stripped.startswith('## '):
            heading = stripped[3:].strip()
            result.append(f'<h4>{htmllib.escape(heading)}</h4>')
        # Heading 3
        elif stripped.startswith('### '):
            heading = stripped[4:].strip()
            result.append(f'<h4>{htmllib.escape(heading)}</h4>')
        # Heading 4
        elif stripped.startswith('#### '):
            heading = stripped[5:].strip()
            result.append(f'<h4>{htmllib.escape(heading)}</h4>')
        # List item (Bullet)
        elif is_bullet:
            if list_type != 'ul':
                result.append('<ul>')
                list_type = 'ul'
            item = re.sub(r'^[-✅*]\s+', '', stripped)
            item = format_inline(item)
            result.append(f'<li>{item}</li>')
        # Numbered list
        elif is_number:
            if list_type != 'ol':
                result.append('<ol>')
                list_type = 'ol'
            item = re.sub(r'^\d+\.\s+', '', stripped)
            item = format_inline(item)
            result.append(f'<li>{item}</li>')
        # Blockquote (clinical tip)
        elif stripped.startswith('> '):
            content = stripped[2:].strip()
            content = format_inline(content)
            result.append(f'<div class="clinical-tip"><p>{content}</p></div>')
        # Horizontal rule
        elif stripped == '---':
            pass  # skip
        # Empty line
        elif stripped == '':
            if list_type:
                result.append(f'</{list_type}>')
                list_type = None
        # Normal paragraph
        else:
            content = format_inline(stripped)
            if content:
                result.append(f'<p>{content}</p>')

        i += 1

    if list_type:
        result.append(f'</{list_type}>')

    return '\n'.join(result)


def format_inline(text: str) -> str:
    """インラインマークダウン（太字、イタリック等）をHTMLへ"""
    # Bold+Italic
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Inline code
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    # Special arrow
    text = text.replace('→', '→')
    return text


def extract_html_block(text: str, start_marker: str) -> str:
    """ネストされたHTMLのdivタグを深さカウントで正確に抽出する関数"""
    start_idx = text.find(start_marker)
    if start_idx == -1:
        return ""
    
    sub_text = text[start_idx:]
    depth = 0
    i = 0
    while i < len(sub_text):
        # <div を見つける
        if sub_text.startswith('<div', i):
            depth += 1
            i += 4
        # </div を見つける
        elif sub_text.startswith('</div', i):
            depth -= 1
            if depth == 0:
                # タグの終わり（>）まで含める
                end_idx = sub_text.find('>', i) + 1
                return sub_text[:end_idx]
            i += 5
        else:
            i += 1
    return sub_text

def extract_owner_tips_html(md_text: str) -> str:
    """飼い主説明のhtmlブロックを抽出"""
    return extract_html_block(md_text, '<div id="owner-tips">')

def extract_refs_html(md_text: str) -> str:
    """参照論文ブロックをそのまま抽出"""
    return extract_html_block(md_text, '<div id="refs">')


def generate_nav_links(sections: list[tuple[str, str]]) -> str:
    """サイドバーナビリンクを生成"""
    links = ['<a href="../../index.html">🏠 トップ</a>']
    for anchor, label in sections:
        links.append(f'<a href="#{anchor}">{label}</a>')
    links.append('<h4>情報ソース</h4>')
    links.append('<a href="https://pubmed.ncbi.nlm.nih.gov/" target="_blank">🔍 PubMed</a>')
    return '\n'.join(links)


def convert_md_to_html(md_path: Path) -> Path:
    md_text = md_path.read_text(encoding='utf-8')
    lines = md_text.splitlines()

    # Title
    title = ""
    for line in lines:
        if line.startswith('# '):
            title = line[2:].strip()
            break

    # Description from 結論 section
    desc_match = re.search(r'## 結論\n(.*?)(?=\n## |\Z)', md_text, re.DOTALL)
    description = ""
    if desc_match:
        raw = desc_match.group(1).strip()
        # First bullet
        first_bullet = re.search(r'[・\-\*]\s*(.+)', raw)
        if first_bullet:
            description = re.sub(r'\*\*(.+?)\*\*', r'\1', first_bullet.group(1))[:80]

    # Tags from metadata
    tags = extract_tags_from_meta(md_text, title)

    # Update date
    date_match = re.search(r'更新日:\s*(\S+)', md_text)
    update_date = date_match.group(1) if date_match else "2026年3月更新"
    # Format: 2026-03-04 → 2026年3月更新
    if re.match(r'\d{4}-\d{2}-\d{2}', update_date):
        y, m, _ = update_date.split('-')
        update_date = f"{y}年{int(m)}月更新"

    # Ref count
    refs_count = len(re.findall(r'<li>', md_text))

    # Find sections for nav  
    section_map = []
    for line in lines:
        if line.startswith('## ') and not line.startswith('## メタデータ') and not line.startswith('## 結論'):
            sec_text = line[3:].strip()
            anchor = re.sub(r'[^\w\u3000-\u9fff]', '', sec_text)[:20]
            section_map.append((anchor, sec_text))

    section_map_extra = [
        ("owner-tips", "🗣️ 飼い主説明"),
        ("refs", "📚 参照論文"),
    ]

    nav_links = generate_nav_links(section_map_extra)

    # Build tag HTML
    tags_html = ''
    for tag in tags:
        encoded = tag['query'].encode('utf-8').hex()
        # Use JS-friendly URL encoding
        import urllib.parse
        encoded_q = urllib.parse.quote(tag['query'])
        tags_html += f'<a class="tag {tag["class"]}" href="../../index.html?tag={encoded_q}">{tag["label"]}</a>'

    # Conclusion section
    conclusion_html = ""
    if desc_match:
        raw_conclusion = desc_match.group(1).strip()
        conclusion_items = []
        for line in raw_conclusion.splitlines():
            stripped = line.strip()
            if stripped.startswith('- ') or stripped.startswith('・') or stripped.startswith('-'):
                item = re.sub(r'^[-・]\s*', '', stripped)
                item = format_inline(item)
                conclusion_items.append(f'<li>{item}</li>')
        if conclusion_items:
            conclusion_html = '<ul>' + ''.join(conclusion_items) + '</ul>'
        else:
            conclusion_html = f'<p>{format_inline(raw_conclusion)}</p>'

    # Owner tips & refs raw HTML from MD
    owner_tips_raw = extract_owner_tips_html(md_text)
    refs_raw = extract_refs_html(md_text)

    # Prepare markdown text for section generation
    clean_md_text = md_text
    if owner_tips_raw:
        clean_md_text = clean_md_text.replace(owner_tips_raw, '')
    if refs_raw:
        clean_md_text = clean_md_text.replace(refs_raw, '')

    # Normalize heading levels if content is wrapped in "## 本文"
    clean_md_text = re.sub(r'^##\s*本文\s*\n', '\n', clean_md_text, flags=re.MULTILINE)
    clean_md_text = re.sub(r'^###\s+', '## ', clean_md_text, flags=re.MULTILINE)

    # Body sections - split by ## headers
    section_blocks = re.split(r'\n(?=## )', clean_md_text)
    accordion_sections = []

    icon_map = {
        '臨床症状': '⚡',
        '原因': '🔍',
        '治療': '💊',
        '介入': '💊',
        '画像診断': '🩺',
        '難産': '🩺',
        '外科': '🔪',
        '新生子': '👶',
        '輸液': '💧',
        'ステップ': '🗺️',
        'モニタリング': '📊',
        '緊急': '🚨',
        '病態': '🧬',
    }

    for block in section_blocks:
        if not block.strip().startswith('## '):
            continue
        block_lines = block.strip().splitlines()
        heading = block_lines[0][3:].strip()

        if heading in ['結論', 'メタデータ']:
            continue

        # Determine icon
        icon = '📋'
        for kw, ic in icon_map.items():
            if kw in heading:
                icon = ic
                break

        anchor = re.sub(r'[^\w\u3040-\u9fff]', '', heading)[:20]
        section_content = '\n'.join(block_lines[1:])

        body_html = md_to_html_body(section_content)
        accordion_sections.append({
            'anchor': anchor,
            'icon': icon,
            'heading': heading,
            'body': body_html,
        })

    # Build accordion HTML
    accordions_html = ''
    for sec in accordion_sections:
        accordions_html += f'''
<div id="{sec['anchor']}">
<div class="accordion">
<button class="accordion-trigger">
<span class="trigger-left"><span class="trigger-icon">{sec['icon']}</span><span>{htmllib.escape(sec['heading'])}</span></span>
<span class="chevron">▼</span>
</button>
<div class="accordion-content">
<div class="accordion-body premium-content">
{sec['body']}
</div>
<div class="premium-lock"><span class="lock-icon">🔒</span>{htmllib.escape(sec['heading'])}の詳細は有料会員限定です</div>
</div>
</div>
</div>'''

    # Full HTML
    html_out = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<meta content="{htmllib.escape(description)}" name="description"/>
<title>{htmllib.escape(title)} | VetEvidence</title>
<link href="../../assets/style.css?v={STYLE_VERSION}" rel="stylesheet"/>
</head>
<body class="mode-premium">
<nav class="mobile-nav">
<span class="nav-brand">🩺 VetEvidence</span>
<button aria-label="メニュー" class="hamburger-btn">
<span></span><span></span><span></span>
</button>
</nav>
<div class="slide-menu-overlay"></div>
<aside class="slide-menu">
<h4>ナビゲーション</h4>
{nav_links}
</aside>
<div class="page-container">
<header class="page-header" style="padding: var(--space-lg) 0 var(--space-md); margin-bottom: var(--space-md);">
<div class="tags" style="margin-bottom: 8px;">
{tags_html}
</div>
<h1 style="font-size: 1.3rem;">{htmllib.escape(title)}</h1>
<p class="subtitle" style="font-size: 0.85rem; margin-top: 4px;">
{htmllib.escape(description)}
</p>
<div class="meta-bar" style="padding: 8px 0 0; margin: 0; gap: 12px;">
<div class="meta-item"><span class="icon">📄</span><span>参照論文{refs_count}本</span></div>
<div class="meta-item"><span class="icon">🔄</span><span>{htmllib.escape(update_date)}</span></div>
</div>
</header>
<div class="content-mode-bar">
<span>📋</span>
<label class="toggle-switch">
<input checked="" id="content-mode-toggle" type="checkbox"/>
<span class="toggle-slider"></span>
</label>
<span class="mode-label">👑 すべて表示</span>
</div>
<!-- FREE ZONE -->
<div class="free-content" id="conclusion">
<div class="bottom-line" style="margin-top:0;padding:var(--space-md) var(--space-lg);">
<h3 style="font-size:0.95rem;">🎯 結論</h3>
<div style="font-size:0.88rem;">
{conclusion_html}
</div>
</div>
</div>
<!-- PREMIUM ZONE -->
<hr class="section-divider"/>
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 8px;">
<h3 style="font-size: 0.95rem; color: var(--color-text-secondary);">📖 詳細解説</h3>
<div>
<button onclick="toggleAllAccordions(true)" style="background:transparent;border:1px solid var(--color-border);color:var(--color-text-secondary);padding:4px 10px;border-radius:50px;cursor:pointer;font-size:0.72rem;font-family:var(--font-sans);">全展開</button>
<button onclick="toggleAllAccordions(false)" style="background:transparent;border:1px solid var(--color-border);color:var(--color-text-secondary);padding:4px 10px;border-radius:50px;cursor:pointer;font-size:0.72rem;font-family:var(--font-sans);margin-left:4px;">全折り</button>
</div>
</div>
{accordions_html}
{owner_tips_raw}
{refs_raw}
<footer class="page-footer" style="margin-top: var(--space-xl);">
<p><a href="../../index.html">← トップに戻る</a> | VetEvidence 🩺</p>
<p style="margin-top:4px;font-size:0.68rem;color:var(--color-text-muted);">
※本まとめは臨床判断の参考資料です。個々の症例の治療方針は担当獣医師の判断に委ねられます。</p>
</footer>
</div>
<script src="../../assets/script.js?v={STYLE_VERSION}"></script>
</body>
</html>'''

    # Output path
    out_path = md_path.with_suffix('.html')
    out_path.write_text(html_out, encoding='utf-8')
    print(f'✅ {out_path.name}')
    return out_path


def main():
    if '--file' in sys.argv:
        idx = sys.argv.index('--file')
        if idx + 1 < len(sys.argv):
            target = Path(sys.argv[idx + 1])
            if target.exists():
                convert_md_to_html(target)
            else:
                print(f'File not found: {target}')
    elif '--all-new' in sys.argv:
        md_files = list(Path(PROJECT_ROOT / 'topics').rglob('*.md'))
        for md in md_files:
            html_path = md.with_suffix('.html')
            if not html_path.exists():
                try:
                    convert_md_to_html(md)
                except Exception as e:
                    print(f'❌ {md.name}: {e}')
    else:
        # Convert the 3 new rescue articles
        targets = [
            PROJECT_ROOT / 'topics' / '救急' / '高カリウム血症_致死的不整脈の回避と治療.md',
            PROJECT_ROOT / 'topics' / '救急' / '難産と帝王切開_救急対応フロー.md',
            PROJECT_ROOT / 'topics' / '救急' / '高ナトリウム血症_原因と水脱水アプローチ.md',
        ]
        for t in targets:
            if t.exists():
                try:
                    convert_md_to_html(t)
                except Exception as e:
                    print(f'❌ {t.name}: {e}')
            else:
                print(f'⚠️ Not found: {t}')


if __name__ == '__main__':
    main()
