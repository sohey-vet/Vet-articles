import os
import re
import urllib.parse
from bs4 import BeautifulSoup

def count_md_references(md_content):
    refs_start = md_content.find('<div id="refs">')
    if refs_start != -1:
        refs_chunk = md_content[refs_start:]
        md_soup = BeautifulSoup(refs_chunk, "html.parser")
        refs_div = md_soup.find("div", id="refs")
        if refs_div:
            li_count = len(refs_div.find_all("li"))
            if li_count > 0:
                return li_count

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
        remainder = p[len(card_inner)+4:]
        
        href_match = re.search(r'href="([^"]+)"', full_card)
        if not href_match:
            new_parts.append(full_card[len('<a class="article-card"'):] + remainder)
            continue
            
        href = href_match.group(1)
        href_decoded = urllib.parse.unquote(href)
        md_rel_path = href_decoded.replace(".html", ".md")
        md_file_path = os.path.join(repo_dir, md_rel_path)
        
        if not os.path.exists(md_file_path):
            new_parts.append(full_card[len('<a class="article-card"'):] + remainder)
            continue
            
        with open(md_file_path, "r", encoding="utf-8") as f:
            md_content = f.read()
            
        actual_count = count_md_references(md_content)
        
        # Check current HTML count
        displayed_count = 0
        papers_span = re.search(r'<span class="card-papers">📄 参照論文(\d+)本</span>', full_card)
        if papers_span:
            displayed_count = int(papers_span.group(1))
            
        if displayed_count > 0 and displayed_count != actual_count:
            # Fix HTML
            new_card = full_card.replace(
                f'<span class="card-papers">📄 参照論文{displayed_count}本</span>',
                f'<span class="card-papers">📄 参照論文{actual_count}本</span>'
            )
            full_card = new_card
            
            # Fix MD Metadata
            new_md_content = re.sub(
                r'> 📄 \*\*参照論文\*\*: \d+本',
                f'> 📄 **参照論文**: {actual_count}本',
                md_content
            )
            if new_md_content != md_content:
                with open(md_file_path, "w", encoding="utf-8") as f:
                    f.write(new_md_content)
                print(f"Updated MD metadata for {md_rel_path} to {actual_count}本")
            else:
                # Add if missing?
                pass
                
            fixed_count += 1
            print(f"Updated HTML badge for {md_rel_path} ({displayed_count} -> {actual_count})")
            
        p_mod = full_card[len('<a class="article-card"'):] + remainder
        new_parts.append(p_mod)
        
    new_grid_content = '<a class="article-card"'.join(new_parts)
    new_html = html[:start_idx] + new_grid_content + html[grid_end_idx:]
    
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(new_html)
        
    print(f"\nSuccessfully synced {fixed_count} mismatched reference counts!")

if __name__ == "__main__":
    main()
