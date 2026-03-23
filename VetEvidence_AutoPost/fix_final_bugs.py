import os
import glob
import re

def main():
    repo_dir = r"C:\Users\souhe\Desktop\論文まとめ"
    index_path = os.path.join(repo_dir, "index.html")
    
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    print("1. Fixing Asthma in index.html and its source files...")
    # Find asthma block in index.html
    asthma_idx = html.find("猫の喘息 ─ 犬との違いと吸入療法")
    if asthma_idx != -1:
        card_start = html.rfind('<a class="article-card"', 0, asthma_idx)
        card_end = html.find('</a>', asthma_idx)
        if card_start != -1 and card_end != -1:
            card_end += 4
            card_html = html[card_start:card_end]
            
            # replace data-tags
            new_card = re.sub(r'data-tags="[^"]*"', 'data-tags="猫,救急"', card_html)
            
            # replace footer
            footer_start = new_card.find('<div class="card-footer">')
            if footer_start != -1:
                # get papers
                papers_m = re.search(r'(<span class="card-papers">.*?</span>)', new_card)
                papers_str = papers_m.group(1) if papers_m else ""
                
                new_footer = f'<div class="card-footer">\n<span class="tag tag--success">猫</span>\n<span class="tag tag--primary">救急</span>\n{papers_str}\n</div>'
                new_card = new_card[:footer_start] + new_footer + "\n                    " + "</a>"
                # wait, just replacing the footer directly
                footer_end = new_card.find('</div>', footer_start) + 6
                new_card = new_card[:footer_start] + new_footer + new_card[footer_end:]
                
            html = html.replace(card_html, new_card)

    asthma_htmls = glob.glob(os.path.join(repo_dir, 'topics', '**', '猫の喘息*.html'), recursive=True)
    for ah in asthma_htmls:
        with open(ah, "r", encoding="utf-8") as f: c = f.read()
        # Find tags div
        t_start = c.find('<div class="tags" style="margin-bottom:8px;">')
        if t_start != -1:
            t_end = c.find('</div>', t_start) + 6
            new_tags = '<div class="tags" style="margin-bottom:8px;">\n  <a class="tag tag--success" href="../../index.html?tag=%E7%8C%AB">猫</a><a class="tag tag--primary" href="../../index.html?tag=%E6%95%91%E6%80%A5">救急</a>\n  </div>'
            c = c[:t_start] + new_tags + c[t_end:]
            with open(ah, "w", encoding="utf-8") as f: f.write(c)

    asthma_mds = glob.glob(os.path.join(repo_dir, 'topics', '**', '猫の喘息*.md'), recursive=True)
    for am in asthma_mds:
        with open(am, "r", encoding="utf-8") as f: c = f.read()
        c = c.replace("tags:\n  - 呼吸器", "tags:\n  - 猫\n  - 救急")
        c = c.replace("TAGS\n呼吸器", "TAGS\n猫、救急")
        with open(am, "w", encoding="utf-8") as f: f.write(c)

    print("2. Fixing Eye Emoji in index.html and its source files...")
    # Fix in index
    html = html.replace('<span class="card-icon">👁</span>', '<span class="card-icon">👁️</span>')
    html = html.replace('<span class="card-icon">👁\n', '<span class="card-icon">👁️\n')
    
    with open(index_path, "w", encoding="utf-8") as f: f.write(html)

    glaucoma_htmls = glob.glob(os.path.join(repo_dir, 'topics', '**', '緑内障*.html'), recursive=True)
    for gh in glaucoma_htmls:
        with open(gh, "r", encoding="utf-8") as f: c = f.read()
        c = c.replace('<div class="icon">👁</div>', '<div class="icon">👁️</div>')
        with open(gh, "w", encoding="utf-8") as f: f.write(c)

    glaucoma_mds = glob.glob(os.path.join(repo_dir, 'topics', '**', '緑内障*.md'), recursive=True)
    for gm in glaucoma_mds:
        with open(gm, "r", encoding="utf-8") as f: c = f.read()
        c = c.replace('icon: 👁\n', 'icon: 👁️\n')
        c = c.replace('icon: "👁"\n', 'icon: "👁️"\n')
        with open(gm, "w", encoding="utf-8") as f: f.write(c)

    print("Done")

if __name__ == "__main__":
    main()
