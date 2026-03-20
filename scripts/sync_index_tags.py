import re
import os
import glob
import urllib.parse

def main():
    repo_dir = r"C:\Users\souhe\Desktop\論文まとめ"
    topics_dir = os.path.join(repo_dir, "topics")
    index_path = os.path.join(repo_dir, "index.html")

    with open(index_path, "r", encoding="utf-8") as f:
        index_html = f.read()

    html_files = glob.glob(os.path.join(topics_dir, "**", "*.html"), recursive=True)
    updated_cards = 0

    for html_file in html_files:
        rel_path = os.path.relpath(html_file, repo_dir).replace('\\', '/')
        
        with open(html_file, "r", encoding="utf-8") as f:
            article_html = f.read()
            
        tags = []
        tag_matches = re.finditer(r'<a class="tag ([^"]+)"[^>]*>([^<]+)</a>', article_html)
        for m in tag_matches:
            tags.append({'name': m.group(2), 'class': m.group(1)})

        if not tags:
            continue
            
        # Search index.html for href="..." exactly matching rel_path OR URL-encoded rel_path
        # Just use string searching
        
        url_encoded_path = urllib.parse.quote(rel_path)
        
        start_idx = index_html.find(f'href="{rel_path}"')
        if start_idx == -1:
            start_idx = index_html.find(f'href="{url_encoded_path}"')
            
        if start_idx != -1:
            # backtrack to <a class="article-card"
            card_start = index_html.rfind('<a class="article-card"', 0, start_idx)
            if card_start != -1:
                # forward to </a>
                card_end = index_html.find('</a>', start_idx)
                if card_end != -1:
                    full_card = index_html[card_start:card_end+4]
                    
                    tag_names = ",".join([t['name'] for t in tags])
                    new_card = re.sub(r'data-tags="[^"]*"', f'data-tags="{tag_names}"', full_card)
                    if 'data-tags="' not in new_card:
                        new_card = new_card.replace('<a class="article-card"', f'<a class="article-card" data-tags="{tag_names}"')
                        
                    footer_start = new_card.find('<div class="card-footer">')
                    if footer_start != -1:
                        # Extract papers
                        papers_match = re.search(r'(<span class="card-papers">.*?</span>)', full_card, re.DOTALL)
                        papers_html = papers_match.group(1) if papers_match else ""
                        
                        footer_tags_html = "".join([f'<span class="tag {t["class"]}">{t["name"]}</span>\n' for t in tags])
                        
                        new_footer = f'<div class="card-footer">\n{footer_tags_html}{papers_html}\n</div>'
                        # replace the old footer
                        old_footer_inner_start = footer_start + len('<div class="card-footer">')
                        old_footer_end = new_card.find('</div>', old_footer_inner_start)
                        
                        old_footer = new_card[footer_start:old_footer_end+6]
                        new_card = new_card.replace(old_footer, new_footer)
                    
                    index_html = index_html.replace(full_card, new_card)
                    updated_cards += 1

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_html)
        
    print(f"Successfully synchronized tags for {updated_cards} article cards in index.html.")

if __name__ == "__main__":
    main()
