import os
import glob
import re
import urllib.parse

def main():
    repo_dir = r"C:\Users\souhe\Desktop\論文まとめ"
    html_files = glob.glob(os.path.join(repo_dir, "topics", "**", "*.html"), recursive=True)
    
    # 免疫介在性溶血性貧血（IMHA）─ 診断と初期治療    血液　　免疫　　救急
    imha_tags = ["血液", "免疫", "救急"]
    imha_file = [hf for hf in html_files if "IMHA_診断と初期" in hf][0]
    
    # FIP（猫伝染性腹膜炎）─ 抗ウイルス薬時代の治療    救急　　感染症    猫
    fip_tags = ["救急", "感染症", "猫"]
    fip_file = [hf for hf in html_files if "FIP_抗ウイルス薬" in hf][0]
    
    def update_tags_in_html(html_file, tags):
        with open(html_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        tags_section_match = re.search(r'(<div class="tags"[^>]*>)(.*?)(</div>)', content, re.DOTALL)
        if tags_section_match:
            new_tags_html = ""
            for g in tags:
                if not g: continue
                css_class = "tag--secondary" if g == "その他" else "tag--primary"
                if g in ["皮膚", "皮膚科", "外科", "整形外科"]: css_class = "tag--warning"
                elif g in ["猫", "猫専門", "犬"]: css_class = "tag--success"
                encoded_q = urllib.parse.quote(g)
                new_tags_html += f'<a class="tag {css_class}" href="../../index.html?tag={encoded_q}">{g}</a>'
                
            content = content[:tags_section_match.start(2)] + "\n" + new_tags_html + "\n" + content[tags_section_match.end(2):]
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(content)
                
    def update_tags_in_markdown(md_file, new_tags):
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        if re.search(r'tags:\s*\[.*?\]', content):
            tag_str = ", ".join(new_tags)
            content = re.sub(r'tags:\s*\[.*?\]', f'tags: [{tag_str}]', content)
        elif re.search(r'TAGS\n.*?\n', content):
            tag_str = " ".join(new_tags)
            content = re.sub(r'TAGS\n.*?\n', f'TAGS\n{tag_str}\n', content)
        else:
            content += f"\n\n---\ntags: [{', '.join(new_tags)}]\n"
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(content)

    update_tags_in_html(imha_file, imha_tags)
    update_tags_in_html(fip_file, fip_tags)
    
    md_imha = imha_file.replace('.html', '.md')
    if os.path.exists(md_imha): update_tags_in_markdown(md_imha, imha_tags)
    
    md_fip = fip_file.replace('.html', '.md')
    if os.path.exists(md_fip): update_tags_in_markdown(md_fip, fip_tags)

    print("Patched IMHA and FIP tags.")
    
if __name__ == "__main__":
    main()
