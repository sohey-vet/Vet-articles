from bs4 import BeautifulSoup
import re

with open(r'c:\Users\souhe\Desktop\論文まとめ\topics\下痢\犬の急性下痢_最新エビデンス.html', 'r', encoding='utf-8') as fh:
    html_content = fh.read()

def safe_quote(inner):
    if not inner.strip(): return inner
    if '\"' in inner: return inner
    return f'\"{inner}\"'

soup = BeautifulSoup(html_content, 'html.parser')
mermaids = soup.find_all('pre', class_='mermaid')
m = mermaids[0]
original = m.string
lines = original.split('\n')
new_lines = []
for line in lines:
    if line.strip().startswith('style') or line.strip().startswith('classDef') or line.strip().startswith('class ') or line.strip().startswith('//') or line.strip().startswith('graph') or line.strip().startswith('subgraph') or line.strip().startswith('end'):
        new_lines.append(line)
        continue
    
    # []
    line = re.sub(r'([A-Za-z0-9_]+)\[([^\]]+)\]', lambda m: f'{m.group(1)}[{safe_quote(m.group(2))}]', line)
    
    # {}
    line = re.sub(r'([A-Za-z0-9_]+)\{([^\}]+)\}', lambda m: f'{m.group(1)}{{{safe_quote(m.group(2))}}}', line)
    
    # (())
    line = re.sub(r'([A-Za-z0-9_]+)\(\((.+?)\)\)', lambda m: f'{m.group(1)}(({safe_quote(m.group(2))}))', line)
    
    # Edge ||
    line = re.sub(r'-->\|([^\|]+)\|', lambda m: f'-->|{safe_quote(m.group(1))}|', line)

    new_lines.append(line)

print('\n'.join(new_lines))
