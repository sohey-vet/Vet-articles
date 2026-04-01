import os
import re
import urllib.parse

def count_md_references(md_content):
    from bs4 import BeautifulSoup
    refs_start = md_content.find('<div id="refs">')
    if refs_start != -1:
        refs_chunk = md_content[refs_start:]
        md_soup = BeautifulSoup(refs_chunk, "html.parser")
        refs_div = md_soup.find("div", id="refs")
        if refs_div:
            return len(refs_div.find_all("li"))

    lines = md_content.split('\n')
    in_refs = False
    count = 0
    list_pattern = re.compile(r'^\s*(?:\d+\.|-|\*)\s+')
    
    for line in lines:
        if line.startswith('## '):
            if '参照' in line or '参考' in line or 'Reference' in line or 'reference' in line:
                in_refs = True
            else:
                if in_refs: break 
        elif in_refs:
            if line.startswith('---'): break 
            if list_pattern.match(line): count += 1
                
    return count

def main():
    repo_dir = r"C:\Users\souhe\Desktop\論文まとめ"
    index_path = os.path.join(repo_dir, "index.html")
    
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()
        
    start_tag = '<div class="articles-grid" id="articles-grid">'
    start_idx = html.find(start_tag)
    end_idx = html.find('</main>', start_idx)
    grid_end_idx = html.rfind('</div>', start_idx, end_idx)
    
    grid_content = html[start_idx:grid_end_idx]
    
    parts = grid_content.split('<a class="article-card"')
    new_parts = [parts[0]]
    fixed_count = 0
    
    for p in parts[1:]:
        card_inner = p.split('</a>')[0]
        full_card = f'<a class="article-card"{card_inner}</a>'
        remainder = p[len(card_inner)+4:] # text after </a> if any
        
        # Check if missing
        if '<span class="card-papers">' not in full_card:
            # Extract href
            href_match = re.search(r'href="([^"]+)"', full_card)
            if href_match:
                href = href_match.group(1)
                href_decoded = urllib.parse.unquote(href)
                md_rel_path = href_decoded.replace(".html", ".md")
                md_file_path = os.path.join(repo_dir, md_rel_path)
                
                if os.path.exists(md_file_path):
                    with open(md_file_path, "r", encoding="utf-8") as f:
                        md_content = f.read()
                    actual_count = count_md_references(md_content)
                    
                    # Insert the badge
                    # Find <div class="card-footer">...</div>
                    footer_start = full_card.find('<div class="card-footer">')
                    if footer_start != -1:
                        footer_end = full_card.find('</div>', footer_start)
                        
                        # We will insert just before the closing </div>
                        # We want it on a new line or same line? Usually on a new line.
                        # Let's inspect the spacing.
                        # <div class="card-footer">\n<span class="tag tag--primary">救急</span>\n</div>
                        inner_footer = full_card[footer_start:footer_end]
                        # append <span class="card-papers">📄 参照論文X本</span>\n before </div>
                        # Using exact newline from existing if possible
                        insertion = f'\n<span class="card-papers">📄 参照論文{actual_count}本</span>\n'
                        # To align cleanly, just put it before the last </div>
                        
                        new_card = full_card[:footer_end] + f'<span class="card-papers">📄 参照論文{actual_count}本</span>\n' + full_card[footer_end:]
                        
                        full_card = new_card
                        fixed_count += 1
        
        # reconstruct
        # But wait, full_card starts with <a class="article-card" which we split by
        # so we append to new_parts without the split string
        # Actually our split was `<a class="article-card"`
        # full_card has that at the beginning.
        # So we strip it off so we can just re-join with `<a class="article-card"` later, OR we just join directly.
        
        # Actually it's simpler to just replace p with the modified content.
        # full_card = <a class="article... </a>
        # remainder = everything after </a>
        # The split string `<a class="article-card"` is missing in p. 
        # So `p` was basically ` href="...">...</a>\n   `
        
        # Let's just reconstruct p
        # full_card string starts with <a class="article-card" so we take from len('<a class="article-card"') -> end of full_card
        p_mod = full_card[len('<a class="article-card"'):] + remainder
        new_parts.append(p_mod)
        
    new_grid_content = '<a class="article-card"'.join(new_parts)
    new_html = html[:start_idx] + new_grid_content + html[grid_end_idx:]
    
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(new_html)
        
    print(f"Successfully fixed {fixed_count} missing badges in index.html!")

if __name__ == "__main__":
    main()
