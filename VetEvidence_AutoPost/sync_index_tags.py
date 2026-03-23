import re
import os
import glob
import urllib.parse
from collections import defaultdict

def main():
    repo_dir = r"C:\Users\souhe\Desktop\論文まとめ"
    topics_dir = os.path.join(repo_dir, "topics")
    index_path = os.path.join(repo_dir, "index.html")

    with open(index_path, "r", encoding="utf-8") as f:
        index_html = f.read()

    html_files = glob.glob(os.path.join(topics_dir, "**", "*.html"), recursive=True)
    updated_cards = 0
    
    # Track the exact tags for each processed card
    # To determine how many cards fall into each genre
    genre_counts = defaultdict(int)
    total_valid_cards = 0

    for html_file in html_files:
        rel_path = os.path.relpath(html_file, repo_dir).replace('\\', '/')
        
        with open(html_file, "r", encoding="utf-8") as f:
            article_html = f.read()
            
        tags = []
        tag_matches = re.finditer(r'<a class="tag ([^"]+)"[^>]*>([^<]+)</a>', article_html)
        for m in tag_matches:
            tags.append({'name': m.group(2).strip(), 'class': m.group(1)})

        if not tags:
            continue
            
        tag_names_list = [t['name'] for t in tags]

        # Search index.html for href="..." exactly matching rel_path OR URL-encoded rel_path
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
                    
                    tag_names = ",".join(tag_names_list)
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
                    total_valid_cards += 1
                    
                    # Compute categories matching this card
                    # Sidebar categories we care about
                    sidebar_genres = [
                        "救急", "循環器", "輸液", "腎泌尿器", "猫", "皮膚", "免疫", "血液", 
                        "消化器・肝臓", "腫瘍", "神経", "内分泌", "麻酔", "眼科", "歯科", "その他"
                    ]
                    
                    # If any tag on the card matches or partially matches the genre, tally it
                    # Note: "消化器・肝臓" might be matched by "消化器" or "肝臓"
                    matched_genres = set()
                    for tag in tag_names_list:
                        for g in sidebar_genres:
                            if g == "消化器・肝臓":
                                if "消化器" in tag or "肝臓" in tag:
                                    matched_genres.add(g)
                            else:
                                if g in tag:
                                    matched_genres.add(g)
                    
                    for mg in matched_genres:
                        genre_counts[mg] += 1
                        
    # Now, replace the counts in the sidebar!
    # Format is:
    # <button class="genre-btn" data-genre="救急">
    #     <span class="genre-icon">🚑</span>
    #     <span>救急</span>
    #     <span class="genre-count">20</span>
    # </button>
    
    # 1. Update the "all" count
    index_html = re.sub(
        r'(<span class="genre-count" id="count-all">)\d+(</span>)',
        rf'\g<1>{total_valid_cards}\g<2>',
        index_html
    )
    
    # 2. Update each specific genre
    for genre, count in genre_counts.items():
        pattern = rf'(<button class="genre-btn"[^>]*data-genre="{re.escape(genre)}"[^>]*>[\s\S]*?<span class="genre-count">)\d+(</span>)'
        index_html = re.sub(
            pattern,
            rf'\g<1>{count}\g<2>',
            index_html
        )
        
    # Also handle genres that might have 0 counts (if they exist in the HTML but weren't in genre_counts)
    sidebar_genres_full = [
        "救急", "循環器", "輸液", "腎泌尿器", "猫", "皮膚", "免疫", "血液", 
        "消化器・肝臓", "腫瘍", "神経", "内分泌", "麻酔", "眼科", "歯科", "その他"
    ]
    for genre in sidebar_genres_full:
        if genre not in genre_counts:
            pattern = rf'(<button class="genre-btn"[^>]*data-genre="{re.escape(genre)}"[^>]*>[\s\S]*?<span class="genre-count">)\d+(</span>)'
            index_html = re.sub(
                pattern,
                rf'\g<1>0\g<2>',
                index_html
            )

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_html)
        
    print(f"Successfully synchronized tags for {updated_cards} article cards in index.html.")
    print("Sidebar genres updated:")
    for g in sidebar_genres_full:
        print(f"  {g}: {genre_counts.get(g, 0)}")
    print(f"  All: {total_valid_cards}")

if __name__ == "__main__":
    main()
