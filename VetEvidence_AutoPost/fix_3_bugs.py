import os
import glob
import re

def main():
    repo_dir = r'C:\Users\souhe\Desktop\論文まとめ'
    
    print("1. Fixing 外耳炎...")
    html_file_otitis = os.path.join(repo_dir, 'topics', '皮膚', '外耳炎の原因別治療アプローチ.html')
    md_file_otitis = os.path.join(repo_dir, 'topics', '皮膚', '外耳炎の原因別治療アプローチ.md')

    if os.path.exists(html_file_otitis):
        with open(html_file_otitis, 'r', encoding='utf-8') as f: content = f.read()
        content = content.replace('皮膚科', '皮膚')
        content = content.replace('%E7%9A%AE%E8%86%9A%E7%A7%91', '%E7%9A%AE%E8%86%9A')
        with open(html_file_otitis, 'w', encoding='utf-8') as f: f.write(content)

    if os.path.exists(md_file_otitis):
        with open(md_file_otitis, 'r', encoding='utf-8') as f: content = f.read()
        content = content.replace('皮膚科', '皮膚')
        with open(md_file_otitis, 'w', encoding='utf-8') as f: f.write(content)

    print("2. Fixing 緑内障 Eye Emoji...")
    glaucoma_files_html = glob.glob(os.path.join(repo_dir, 'topics', '**', '緑内障*.html'), recursive=True)
    glaucoma_files_md = glob.glob(os.path.join(repo_dir, 'topics', '**', '緑内障*.md'), recursive=True)

    for hf in glaucoma_files_html:
        with open(hf, 'r', encoding='utf-8') as f: content = f.read()
        # The plain eye is '👁' (\U0001F441), the emoji eye is '👁️' (\U0001F441\uFE0F)
        # If it's already the emoji eye, replacing '👁' might append double FE0F if we're not careful.
        # But '👁' without FE0F will be caught. Actually just replace any '👁️' to '👁️' just in case.
        content = content.replace('👁️', '👁') # strip first
        content = content.replace('👁', '👁️') # then safely add
        with open(hf, 'w', encoding='utf-8') as f: f.write(content)

    for mf in glaucoma_files_md:
        with open(mf, 'r', encoding='utf-8') as f: content = f.read()
        content = content.replace('👁️', '👁')
        content = content.replace('👁', '👁️')
        with open(mf, 'w', encoding='utf-8') as f: f.write(content)

    index_html_path = os.path.join(repo_dir, 'index.html')
    with open(index_html_path, 'r', encoding='utf-8') as f: index_content = f.read()
    index_content = index_content.replace('👁️', '👁')
    index_content = index_content.replace('👁', '👁️')
    with open(index_html_path, 'w', encoding='utf-8') as f: f.write(index_content)

    print("3. Fixing 猫の喘息...")
    asthma_html = glob.glob(os.path.join(repo_dir, 'topics', '**', '猫の喘息*.html'), recursive=True)
    asthma_md = glob.glob(os.path.join(repo_dir, 'topics', '**', '猫の喘息*.md'), recursive=True)

    new_tags_html = r'''<div class="tags">
            <a class="tag tag--success" href="../../index.html?tag=%E7%8C%AB">猫</a>
<a class="tag tag--primary" href="../../index.html?tag=%E6%95%91%E6%80%A5">救急</a>
        </div>'''
            
    for hf in asthma_html:
        with open(hf, 'r', encoding='utf-8') as f: content = f.read()
        content = re.sub(r'<div class="tags">.*?</div>', new_tags_html, content, flags=re.DOTALL)
        # fix the data-tags in index? Wait, sync_index_tags.py will do that. Let's just fix the HTML text string first.
        # actually, change the document title string if needed? "猫の喘息 ─ 犬との違いと吸入療法 | VetEvidence"
        with open(hf, 'w', encoding='utf-8') as f: f.write(content)

    for mf in asthma_md:
        with open(mf, 'r', encoding='utf-8') as f: content = f.read()
        # Frontmatter tags
        if "tags:\n  - 呼吸器" in content:
            content = content.replace("tags:\n  - 呼吸器", "tags:\n  - 猫\n  - 救急")
        if "TAGS\n呼吸器" in content:
            content = content.replace("TAGS\n呼吸器", "TAGS\n猫、救急")
        with open(mf, 'w', encoding='utf-8') as f: f.write(content)

    print("Done applying fixes.")

if __name__ == "__main__":
    main()
