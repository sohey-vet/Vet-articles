import re
import os
import glob
import urllib.parse
import sys

def main():
    repo_dir = r"C:\Users\souhe\Desktop\論文まとめ"
    index_path = os.path.join(repo_dir, "index.html")

    with open(index_path, "r", encoding="utf-8") as f:
        index_html = f.read()

    # Get all actual generated HTML files
    actual_html_files = [os.path.relpath(p, repo_dir).replace('\\', '/') for p in glob.glob(os.path.join(repo_dir, "topics", "**", "*.html"), recursive=True)]
    actual_titles = [os.path.splitext(os.path.basename(p))[0] for p in actual_html_files]
    
    # Debug: Print actual titles
    print(f"Total actual HTML files: {len(actual_html_files)}")
    
    # Find all cards in index.html
    card_pattern = re.compile(r'<a class="article-card"[^>]*href="([^"]+)"', re.IGNORECASE)
    cards = card_pattern.findall(index_html)
    
    print(f"Total cards in index.html: {len(cards)}")
    
    broken_links = []
    
    # Check which links are broken
    for i, href in enumerate(cards):
        # unquote exactly
        decoded_href = urllib.parse.unquote(href)
        if decoded_href not in actual_html_files:
            broken_links.append((href, decoded_href))
            
    print(f"Broken links found: {len(broken_links)}")
    
    # Attempt to fix broken links by fuzzy matching the title part
    fixed_count = 0
    for href, decoded_href in broken_links:
        # Attempt to find best match in actual_html_files
        old_basename = os.path.splitext(os.path.basename(decoded_href))[0]
        
        # Find if any actual_html_file shares keywords with old_basename
        best_match = None
        best_score = 0
        
        old_keywords = set(old_basename.split('_'))
        if len(old_keywords) == 1 and not '_' in old_basename:
            # Just take first few chars
            old_keywords = {old_basename[:4]}
        
        for actual_file in actual_html_files:
            actual_base = os.path.splitext(os.path.basename(actual_file))[0]
            # Simple keyword overlap
            score = sum(1 for k in old_keywords if k in actual_base)
            if score > best_score:
                best_score = score
                best_match = actual_file
                
        if best_match:
            print(f"Auto-fixing: {decoded_href}  =>  {best_match}")
            # Replace in index.html
            index_html = index_html.replace(f'href="{href}"', f'href="{urllib.parse.quote(best_match)}"')
            fixed_count += 1
            
            # Now we should also fix the tags for this fixed card if we can!
            # To do this robustly, we'll just run sync_index_tags.py later.
        else:
            print(f"Could not auto-fix: {decoded_href}")
            
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_html)
        
    print(f"\nFixed {fixed_count} broken links dynamically.")

if __name__ == "__main__":
    main()
