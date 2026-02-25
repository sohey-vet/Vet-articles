import os
import re
from pathlib import Path
import bs4
from bs4 import BeautifulSoup

def update_index():
    base_dir = Path(r"c:\Users\souhe\Desktop\論文まとめ")
    index_path = base_dir / "index.html"
    topics_dir = base_dir / "topics"

    with open(index_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Find the articles grid
    articles_grid = soup.find('div', id='articles-grid')
    if not articles_grid:
        print("Error: Could not find articles-grid")
        return

    # Get all existing links to avoid duplicates
    existing_links = [a['href'] for a in articles_grid.find_all('a', class_='article-card')]

    new_cards_added = 0

    # Scrape all topic HTML files
    for html_file in topics_dir.rglob('*.html'):
        rel_path = html_file.relative_to(base_dir).as_posix()
        if rel_path in existing_links:
            continue

        print(f"Adding {rel_path} to index...")
        
        with open(html_file, 'r', encoding='utf-8') as f:
            article_soup = BeautifulSoup(f, 'html.parser')
            
        header = article_soup.find('header', class_='page-header')
        if not header: continue
            
        h1 = header.find('h1')
        title_text = h1.text.strip() if h1 else html_file.stem
        # Extract emoji if present
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
        tags = []
        if tags_div:
            for span in tags_div.find_all('span', class_=re.compile(r'^tag')):
                tag_class = " ".join(span.get('class', []))
                tag_text = span.get_text(separator="", strip=True) # remove small tags inner html if any, or just get text
                # clean up text
                tag_text = span.contents[0].strip() if span.contents else span.text.strip()
                tags.append({'class': tag_class, 'text': tag_text})

        # Find category - use the folder name as the primary category
        category = html_file.parent.name
        
        papers = "📄 5論文" # Default
        meta_bar = header.find('div', class_='meta-bar')
        if meta_bar:
            for item in meta_bar.find_all('div', class_='meta-item'):
                if '論文' in item.text:
                    papers = item.text.strip()

        # Create new card HTML
        new_card = soup.new_tag('a', href=rel_path, **{'class': 'article-card', 'data-category': category})
        
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
        for t in tags[:2]: # only first two tags to keep it clean
            t_span = soup.new_tag('span', **{'class': t['class']})
            t_span.string = t['text']
            footer_div.append(t_span)
            
        papers_span = soup.new_tag('span', **{'class': 'card-papers'})
        papers_span.string = papers
        footer_div.append(papers_span)
        
        new_card.append(footer_div)

        # Try to insert after the category comment, else append
        # E.g. <!-- ===== 救急 ===== -->
        target_comment = f" ===== {category} ===== "
        inserted = False
        for element in articles_grid.children:
            if isinstance(element, bs4.Comment) and target_comment in element:
                # Find the last article in this category or just insert after comment
                element.insert_after(new_card)
                # We need a newline
                new_card.insert_before('\n                    ')
                inserted = True
                break
        
        if not inserted:
            # Maybe category doesn't exist, just append
            articles_grid.append('\n                    ')
            articles_grid.append(new_card)

        new_cards_added += 1

    # Update counts
    print(f"Added {new_cards_added} new cards. Updating counts...")
    
    # Update sidebar counts
    all_cards = articles_grid.find_all('a', class_='article-card')
    total_count = len(all_cards)
    
    # Update "すべて"
    count_all = soup.find('span', id='count-all')
    if count_all: count_all.string = str(total_count)
    
    visible_count = soup.find('span', id='visible-count')
    if visible_count: visible_count.string = f"{total_count}件"
    
    # Update individual genres
    genres = {}
    for card in all_cards:
        cat = card.get('data-category', '')
        genres[cat] = genres.get(cat, 0) + 1
        
    for btn in soup.find_all('button', class_='genre-btn'):
        genre = btn.get('data-genre')
        if genre and genre != 'all':
            count_span = btn.find('span', class_='genre-count')
            if count_span:
                count_span.string = str(genres.get(genre, 0))

    # Calculate total papers
    papers_total = 0
    for card in all_cards:
        papers_span = card.find('span', class_='card-papers')
        if papers_span:
            m = re.search(r'\d+', papers_span.text)
            if m: papers_total += int(m.group())
            
    # Update hero header
    stat_values = soup.find_all('div', class_='stat-value')
    for stat in stat_values:
        if '論文' in stat.find_next_sibling('div', class_='stat-label').text:
            stat.string = f"{papers_total}+"
        elif 'テーマ' in stat.find_next_sibling('div', class_='stat-label').text:
            stat.string = str(total_count)

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))
        
    print("Done updating index.html!")

if __name__ == "__main__":
    update_index()
