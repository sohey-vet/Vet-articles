"""
standardize_articles.py
─────────────────────────────
全HTML記事をITP記事のゴールドスタンダードに統一するスクリプト

修正内容:
1. CSS/JSバージョンを最新 (20260304v5) に統一
2. 飼い主説明を owner-tip + speech-bubble 形式に統一
3. 参照論文のフォーマット整備
"""

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(r"c:\Users\souhe\Desktop\論文まとめ")
LATEST_VERSION = "20260304v5"


def update_css_js_version(html: str) -> str:
    """CSS/JSバージョンを最新に統一"""
    # style.css
    html = re.sub(
        r'style\.css\?v=[^"]+',
        f'style.css?v={LATEST_VERSION}',
        html
    )
    # script.js
    html = re.sub(
        r'script\.js\?v=[^"]+',
        f'script.js?v={LATEST_VERSION}',
        html
    )
    return html


def fix_owner_tips_format(html: str) -> str:
    """飼い主説明を owner-tip + speech-bubble 形式に変換
    
    変換対象パターン:
    パターン1: <p><strong>Q. "質問"</strong></p><p>回答</p>
    パターン2: <p><strong>"質問"</strong></p><p>回答</p>
    パターン3: <h4>質問</h4><p>回答</p> (already h4 but no owner-tip class)
    """
    # Find owner-tips accordion body
    owner_tips_match = re.search(
        r'(<div\s+id="owner-tips">\s*<div\s+class="accordion">.*?<div\s+class="accordion-body[^"]*">)(.*?)(</div>\s*(?:<div\s+class="premium-lock">.*?</div>\s*)?</div>\s*</div>\s*</div>)',
        html, re.DOTALL
    )
    
    if not owner_tips_match:
        return html
    
    before = owner_tips_match.group(1)
    body = owner_tips_match.group(2)
    after = owner_tips_match.group(3)
    
    # Check if already has owner-tip class
    if 'owner-tip' in body and 'speech-bubble' in body:
        return html
    
    # Extract Q&A pairs
    qa_pairs = []
    
    # Pattern 1: <p><strong>Q. "..."</strong></p> followed by <p>answer</p>
    # Pattern 2: <p><strong>"..."</strong></p> followed by <p>answer</p>
    qa_pattern = re.findall(
        r'<p>\s*<strong>\s*(Q\.?\s*)?[「「]?(.+?)[」」]?\s*</strong>\s*</p>\s*<p>(.*?)</p>',
        body, re.DOTALL
    )
    
    if qa_pattern:
        for _, question, answer in qa_pattern:
            question = question.strip().strip('「」')
            answer = answer.strip()
            qa_pairs.append((question, answer))
    else:
        # Pattern 3: <h4>question</h4> followed by content (already h4 but wrong format)
        h4_pattern = re.findall(
            r'<h4>(.*?)</h4>\s*(?:<div[^>]*>)?(.*?)(?:</div>|(?=<h4>)|(?=</div>))',
            body, re.DOTALL
        )
        if h4_pattern:
            for question, answer in h4_pattern:
                question = question.strip()
                answer = answer.strip()
                # Clean tags from answer
                if answer:
                    qa_pairs.append((question, answer))
    
    if not qa_pairs:
        return html
    
    # Build new owner-tips body
    new_body = '\n'
    for i, (question, answer) in enumerate(qa_pairs):
        style = ' style="margin-top:0;"' if i == 0 else ''
        new_body += f'''            <div class="owner-tip"{style}>
                <h4>{question}</h4>
                <div class="speech-bubble">{answer}</div>
            </div>
'''
    
    # Also ensure the accordion trigger uses 🗣️ icon
    full_match = owner_tips_match.group(0)
    full_new = before + new_body + '        ' + after
    
    # Fix trigger icon if it uses 💬 instead of 🗣️
    full_new = full_new.replace(
        '<span class="trigger-icon">💬</span><span>飼い主への説明ガイド</span>',
        '<span class="trigger-icon">🗣️</span><span>飼い主への説明ガイド</span>'
    )
    
    html = html.replace(full_match, full_new)
    return html


def fix_owner_tips_premium(html: str) -> str:
    """飼い主説明にpremium-content と premium-lock を追加"""
    # Check if owner-tips exists but lacks premium-content
    if 'id="owner-tips"' not in html:
        return html
    
    # Fix accordion-body to include premium-content class
    html = re.sub(
        r'(<div\s+id="owner-tips">.*?<div\s+class="accordion-body)(">)',
        r'\1 premium-content\2',
        html, count=1, flags=re.DOTALL
    )
    
    # Add premium-lock if missing in owner-tips section
    if 'owner-tips' in html:
        # Find the owner-tips section and check for premium-lock
        ot_match = re.search(
            r'(<div\s+id="owner-tips">.*?<div\s+class="accordion-body[^"]*">.*?</div>)\s*((?:<div\s+class="premium-lock">.*?</div>)?)\s*(</div>\s*</div>\s*</div>)',
            html, re.DOTALL
        )
        if ot_match and 'premium-lock' not in ot_match.group(2):
            replacement = ot_match.group(1) + '\n        <div class="premium-lock"><span class="lock-icon">🔒</span>飼い主説明ガイドは有料会員限定です</div>\n    ' + ot_match.group(3)
            html = html.replace(ot_match.group(0), replacement)
    
    return html


def fix_refs_format(html: str) -> str:
    """参照論文のフォーマットを整備"""
    # Check if refs uses <p> instead of <ol>/<li>
    refs_match = re.search(
        r'(<div\s+id="refs">.*?<div\s+class="accordion-body[^"]*">)(.*?)(</div>\s*</div>\s*</div>\s*</div>)',
        html, re.DOTALL
    )
    
    if not refs_match:
        return html
    
    body = refs_match.group(2)
    
    # If already uses <ol>, just ensure formatting
    if '<ol' in body:
        return html
    
    # If uses <p>・ or <p>- format, convert to <ol>
    ref_items = re.findall(r'<p>\s*[・\-\d+\.]*\s*(.*?)\s*</p>', body, re.DOTALL)
    if ref_items and len(ref_items) >= 2:
        new_body = '\n            <ol style="padding-left:20px;font-size:0.82rem;color:var(--color-text-secondary);">\n'
        for item in ref_items:
            item = item.strip()
            if item:
                # Italicize journal names (common patterns)
                item = re.sub(r'\b(J Vet Intern Med|JAVMA|Vet Surg|J Vet Emerg Crit Care|J Small Anim Pract|Vet Clin North Am|J Am Vet Med Assoc|Vet Comp Oncol|Front Vet Sci|Vet Radiol Ultrasound|BMC Vet Res|Anim Cogn|J Feline Med Surg|Vet J|Vet Dermatol|Vet Ophthalmol|Vet Anaesth Analg|Vet Pathol|Compend Contin Educ Vet|Top Companion Anim Med)\b', 
                              r'<em>\1</em>', item)
                new_body += f'                <li>{item}</li>\n'
        new_body += '            </ol>\n        '
        
        html = html.replace(refs_match.group(2), new_body)
    
    return html


def ensure_ref_count(html: str) -> str:
    """参照論文数をヘッダーのメタバーに正しく反映"""
    # Count <li> tags in refs section
    refs_match = re.search(r'<div\s+id="refs">.*?</div>\s*</div>\s*</div>\s*</div>', html, re.DOTALL)
    if refs_match:
        count = refs_match.group(0).count('<li>')
        # Update meta-bar count
        html = re.sub(r'参照論文\d+本', f'参照論文{count}本', html)
        # Update refs accordion trigger count
        html = re.sub(r'参照論文（\d+本）', f'参照論文（{count}本）', html)
        # Also update the simpler pattern
        html = re.sub(r'参照論文[・]?資料', f'参照論文（{count}本）', html, count=1)
    return html


def standardize_article(html_path: Path) -> dict:
    """1記事を標準化し、変更内容を返す"""
    html = html_path.read_text(encoding='utf-8')
    original = html
    changes = []
    
    # 1. CSS/JS version
    new_html = update_css_js_version(html)
    if new_html != html:
        changes.append("CSS/JS version updated")
        html = new_html
    
    # 2. Fix owner-tips format
    new_html = fix_owner_tips_format(html)
    if new_html != html:
        changes.append("Owner tips reformatted")
        html = new_html
    
    # 3. Fix owner-tips premium class
    new_html = fix_owner_tips_premium(html)
    if new_html != html:
        changes.append("Owner tips premium class added")
        html = new_html
    
    # 4. Fix refs format
    new_html = fix_refs_format(html)
    if new_html != html:
        changes.append("Refs reformatted to <ol>")
        html = new_html
    
    # 5. Ensure ref count
    new_html = ensure_ref_count(html)
    if new_html != html:
        changes.append("Ref count updated")
        html = new_html
    
    # Write if changed
    if html != original:
        html_path.write_text(html, encoding='utf-8')
    
    return {
        'path': str(html_path.relative_to(PROJECT_ROOT)),
        'changes': changes,
        'modified': html != original
    }


def main():
    topics_dir = PROJECT_ROOT / 'topics'
    html_files = sorted(topics_dir.rglob('*.html'))
    
    print(f"🔧 Standardizing {len(html_files)} articles...")
    print("=" * 60)
    
    modified_count = 0
    for html_file in html_files:
        result = standardize_article(html_file)
        if result['modified']:
            modified_count += 1
            print(f"✅ {result['path']}")
            for c in result['changes']:
                print(f"   → {c}")
        else:
            print(f"⏭️  {result['path']} (no changes)")
    
    print("=" * 60)
    print(f"✅ Modified: {modified_count}/{len(html_files)} articles")


if __name__ == '__main__':
    main()
