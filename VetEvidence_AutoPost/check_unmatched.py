import re
import os
import glob
import urllib.parse

repo_dir = r'C:\Users\souhe\Desktop\論文まとめ'
topics_dir = os.path.join(repo_dir, 'topics')
index_path = os.path.join(repo_dir, 'index.html')

with open(index_path, 'r', encoding='utf-8') as f:
    index_html = f.read()

html_files = glob.glob(os.path.join(topics_dir, '**', '*.html'), recursive=True)

unmatched = []
for html_file in html_files:
    rel_path = os.path.relpath(html_file, repo_dir).replace('\\', '/')
    url_encoded_path = urllib.parse.quote(rel_path)
    
    start_idx = index_html.find(f'href="{rel_path}"')
    if start_idx == -1:
        start_idx = index_html.find(f'href="{url_encoded_path}"')
        
    if start_idx == -1:
        unmatched.append(rel_path)

print('Unmatched files:', len(unmatched))
for u in unmatched:
    print(u)
