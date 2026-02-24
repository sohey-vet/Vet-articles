import os
import re
from pathlib import Path
from bs4 import BeautifulSoup, Comment

def rebuild_index_cards():
    base_dir = Path(r"c:\Users\souhe\Desktop\論文まとめ")
    index_path = base_dir / "index.html"
    topics_dir = base_dir / "topics"

    with open(index_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    articles_grid = soup.find('div', id='articles-grid')
    if not articles_grid:
        print("Error: Could not find articles-grid")
        return

    # Clear grid
    articles_grid.clear()

    # Collect all html files
    html_files = sorted(topics_dir.rglob('*.html'))
    
    # Group by directory name for organizing comments
    groups = {}
    for hf in html_files:
        cat = hf.parent.name
        if cat not in groups:
            groups[cat] = []
        groups[cat].append(hf)
        
    papers_total = 0
    total_count = 0

    for cat, files in groups.items():
        # Add a category comment
        articles_grid.append('\n                    ')
        articles_grid.append(Comment(f" ===== {cat} ===== "))
        
        for html_file in files:
            rel_path = html_file.relative_to(base_dir).as_posix()
            
            with open(html_file, 'r', encoding='utf-8') as f:
                article_soup = BeautifulSoup(f, 'html.parser')
                
            header = article_soup.find('header', class_='page-header')
            if not header: continue
                
            h1 = header.find('h1')
            title_text = h1.text.strip() if h1 else html_file.stem
            emoji_match = re.match(r'^([\U00010000-\U0010ffff\u2600-\u27BF]+)\s*(.*)', title_text)
            if emoji_match:
                icon = emoji_match.group(1)
                title = emoji_match.group(2)
            else:
                icon = "📄"
                title = title_text

            subtitle = header.find('p', class_='subtitle')
            desc = subtitle.text.strip() if subtitle else ""
            
            tags_div = header.find('div', class_='tags')
            tags_list = []
            if tags_div:
                for span in tags_div.find_all('span', class_=re.compile(r'^tag')):
                    tag_class = " ".join(span.get('class', []))
                    tag_text = span.contents[0].strip() if span.contents else span.text.strip()
                    tags_list.append({'class': tag_class, 'text': tag_text})

            # Calculate papers
            papers = "📄 5論文" # Default
            meta_bar = header.find('div', class_='meta-bar')
            if meta_bar:
                for item in meta_bar.find_all('div', class_='meta-item'):
                    if '論文' in item.text:
                        papers = item.text.strip()
            
            m = re.search(r'\d+', papers)
            if m: papers_total += int(m.group())

            all_tag_texts = [t['text'] for t in tags_list]
            
            # create element
            new_card = soup.new_tag('a', href=rel_path, **{'class': 'article-card', 'data-tags': ','.join(all_tag_texts)})
            
            icon_span = soup.new_tag('span', **{'class': 'card-icon'})
            icon_span.string = icon
            new_card.append(icon_span)
            
            title_h3 = soup.new_tag('h3')
            title_h3.string = title
            new_card.append(title_h3)
            
            desc_p = soup.new_tag('p')
            desc_p.string = desc
            new_card.append(desc_p)
            
            footer_div = soup.new_tag('div', **{'class': 'card-footer'})
            priority_tags = ['猫', '犬']
            display_tags = []
            
            # First, add priority tags if they exist
            for t in tags_list:
                if t['text'] in priority_tags:
                    display_tags.append(t)
            
            # Then add other tags until we have 3
            for t in tags_list:
                if t not in display_tags:
                    display_tags.append(t)
                if len(display_tags) >= 3:
                    break
            
            for t in display_tags:
                t_span = soup.new_tag('span', **{'class': t['class']})
                t_span.string = t['text']
                footer_div.append(t_span)
                
            papers_span = soup.new_tag('span', **{'class': 'card-papers'})
            papers_span.string = papers
            footer_div.append(papers_span)
            
            new_card.append(footer_div)
            
            articles_grid.append('\n                    ')
            articles_grid.append(new_card)
            total_count += 1
            
        articles_grid.append('\n                ')

    print(f"Rebuilt {total_count} cards.")
    
    # Update total counts on hero header if needed, but the JS we just wrote will handle the sidebar and visible counts dynamically on load.
    # We still need to update the hero header statically so SEO sees it.
    stat_values = soup.find_all('div', class_='stat-value')
    for stat in stat_values:
        label = stat.find_next_sibling('div', class_='stat-label')
        if label and '論文' in label.text:
            stat.string = f"{papers_total}+"
        elif label and 'テーマ' in label.text:
            stat.string = str(total_count)

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print("Successfully updated index.html with new data-tags structure.")

if __name__ == "__main__":
    rebuild_index_cards()
