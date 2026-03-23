import os
import glob
import re
from collections import defaultdict
import urllib.parse

def main():
    repo_dir = r'C:\Users\souhe\Desktop\論文まとめ'
    drafts_dir = r'C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts'
    
    html_files = glob.glob(os.path.join(repo_dir, 'topics', '**', '*.html'), recursive=True)
    html_basenames = [urllib.parse.unquote(os.path.basename(hf)) for hf in html_files]
    
    drafts_mapping = defaultdict(list)
    
    for folder in os.listdir(drafts_dir):
        folder_path = os.path.join(drafts_dir, folder)
        if not os.path.isdir(folder_path) or '_' not in folder: continue
        
        sns_md = os.path.join(folder_path, 'sns_all_drafts.md')
        if os.path.exists(sns_md):
            with open(sns_md, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                m_html = re.search(r'元ファイル:\s*([^\r\n]+)', content)
                if m_html:
                    html_path = m_html.group(1).strip()
                    html_basename = os.path.basename(html_path).replace('.md', '.html').strip()
                    html_basename = urllib.parse.unquote(html_basename)
                    
                    drafts_mapping[html_basename].append(folder)
                    
    print(f"Total HTML files in topics: {len(html_files)}")
    print(f"Total Draft folders that mapped to an HTML: {sum(len(v) for v in drafts_mapping.values())}\n")
    
    missing = []
    for hf in html_basenames:
        if hf not in drafts_mapping:
            # try finding by without extension or weird spaces
            found = False
            for mapped_name in drafts_mapping.keys():
                if mapped_name.replace('.html', '').replace(' ', '') == hf.replace('.html', '').replace(' ', ''):
                    found = True
                    break
            if not found:
                missing.append(hf)
                
    print("🚨 【SNSドラフトが「全く存在しない」記事（投稿予定なし）】")
    if missing:
        for m in missing:
            print("  ❌ " + m)
    else:
        print("  なし")
        
    print("\n⚠️ 【SNSドラフトが「複数ダブっている」記事】")
    for basename, folders in drafts_mapping.items():
        if len(folders) > 1:
            print(f"  🔁 {basename}")
            for f in folders:
                print(f"      - {f}")

if __name__ == '__main__':
    main()
