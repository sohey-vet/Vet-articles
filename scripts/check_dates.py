import re
import os
import urllib.parse
import json

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
        html = f.read()
        
    start_tag = '<div class="articles-grid" id="articles-grid">'
    start_idx = html.find(start_tag) + len(start_tag)
    end_idx = html.find('</main>', start_idx)
    grid_end_idx = html.rfind('</div>', start_idx, end_idx)
    grid_content = html[start_idx:grid_end_idx]

    parts = grid_content.split('<a class="article-card"')
    
    print(f"Total parts: {len(parts)-1}")
    
    for i, p in enumerate(parts[1:11]):
        card_inner = p.split('</a>')[0]
        full_card = f'<a class="article-card"{card_inner}</a>'
        
        href_match = re.search(r'href="([^"]+)"', full_card)
        if href_match:
            href = href_match.group(1)
            href_decoded = urllib.parse.unquote(href)
            basename = os.path.basename(href_decoded).replace('.html', '')
            
            mapped_date = "9999-99-99"
            if basename in date_map:
                mapped_date = date_map[basename]
            else:
                for mapped_name, mapped_d in date_map.items():
                    if basename in mapped_name or mapped_name in basename:
                        mapped_date = mapped_d
                        break
                        
            print(f"[{i+1}] {basename[:30]}... -> {mapped_date}")

if __name__ == "__main__":
    main()
