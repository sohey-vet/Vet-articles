import json
import os
import urllib.parse
import re

def main():
    repo_dir = r"C:\Users\souhe\Desktop\論文まとめ"
    index_path = os.path.join(repo_dir, "index.html")
    schedule_path = r"C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts\VetEvidence_AutoPost\sns_schedule.json"

    with open(schedule_path, "r", encoding="utf-8") as f:
        schedule_data = json.load(f)

    date_map = {}
    for item in schedule_data:
        date_str = item.get("date")
        source = item.get("source", "")
        parts = source.split("_")
        if len(parts) >= 3:
            basename = "_".join(parts[2:]) 
        else:
            basename = source
        if basename not in date_map or date_str < date_map[basename]:
            date_map[basename] = date_str

    with open(index_path, "r", encoding="utf-8") as f:
        index_html = f.read()

    start_tag = '<div class="articles-grid" id="articles-grid">'
    start_idx = index_html.find(start_tag)
    if start_idx == -1:
        print("Could not find articles-grid")
        return
    
    start_idx += len(start_tag)
    end_idx = index_html.find('</main>', start_idx)
    grid_end_idx = index_html.rfind('</div>', start_idx, end_idx)
    
    grid_content = index_html[start_idx:grid_end_idx]

    # Split by <a class="article-card"
    parts = grid_content.split('<a class="article-card"')
    cards = []
    
    for p in parts[1:]:
        # The card contents are up to the first </a>
        card_inner = p.split('</a>')[0]
        full_card = f'<a class="article-card"{card_inner}</a>'
        cards.append(full_card)

    print(f"Properly parsed {len(cards)} article cards.")

    def get_date_for_card(card):
        href_match = re.search(r'href="([^"]+)"', card)
        if href_match:
            href = href_match.group(1)
            href_decoded = urllib.parse.unquote(href)
            basename = os.path.basename(href_decoded).replace('.html', '')
            if basename in date_map:
                return date_map[basename]
            for mapped_name, mapped_date in date_map.items():
                if basename in mapped_name or mapped_name in basename:
                    return mapped_date
        return "9999-99-99"

    cards.sort(key=get_date_for_card)

    # Reconstruct the grid HTML softly formatting
    new_grid_content = "\n"
    for card in cards:
        new_grid_content += "                " + card + "\n"
    new_grid_content += "            "

    new_index_html = index_html[:start_idx] + new_grid_content + index_html[grid_end_idx:]

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(new_index_html)

    print("index.html rewritten successfully!")

if __name__ == "__main__":
    main()
