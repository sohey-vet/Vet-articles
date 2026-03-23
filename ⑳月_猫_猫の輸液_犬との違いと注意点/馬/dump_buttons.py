import bs4

html = open('page_dump.html', encoding='utf-8').read()
soup = bs4.BeautifulSoup(html, 'html.parser')

with open('buttons_dump.txt', 'w', encoding='utf-8') as f:
    # Find all buttons and icons
    elements = soup.find_all(lambda tag: tag.name in ('button', 'div', 'span') and any(c in tag.get('class', []) for c in ['x-button', 'x-icon', 'x-arrow-el', 'x-font-icon']))
    
    for i, el in enumerate(elements):
        # only ones that might be next race (e.g., right side of header, or containing 'down'/'arrow')
        classes = " ".join(el.get('class', []))
        text = el.text.strip().replace('\n', ' ')
        f.write(f"[{i}] tag={el.name} classes='{classes}' text='{text}'\n")
