import os
import glob
import re
from collections import defaultdict
import urllib.parse

def main():
    repo_dir = r'C:\Users\souhe\Desktop\論文まとめ'
    drafts_dir = r'C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts'
    
    # Get all 108 HTML files
    html_files = glob.glob(os.path.join(repo_dir, 'topics', '**', '*.html'), recursive=True)
    
    # Store mapping: HTML basename -> list of SNS Draft Folders
    html_to_drafts = defaultdict(list)
    
    # Loop over all SNS Draft folders
    for folder in os.listdir(drafts_dir):
        folder_path = os.path.join(drafts_dir, folder)
        if not os.path.isdir(folder_path) or '_' not in folder: continue
        
        sns_md = os.path.join(folder_path, 'sns_all_drafts.md')
        if os.path.exists(sns_md):
            with open(sns_md, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Extract the source HTML file name linked in the draft
                m_html = re.search(r'元ファイル:\s*([^\r\n]+)', content)
                if m_html:
                    html_path = m_html.group(1).strip()
                    html_basename = os.path.basename(html_path).replace('.md', '.html').strip()
                    html_basename = urllib.parse.unquote(html_basename) # Decode just in case
                    html_to_drafts[html_basename].append(folder)
                    
    print(f"Total HTML articles found on disk: {len(html_files)}\n")
    
    # Now check for missing and duplicates
    missing_articles = []
    
    for hf in html_files:
        basename = os.path.basename(hf)
        if basename not in html_to_drafts:
            # Let's try matching without extension just in case
            found = False
            for mapped_name in html_to_drafts.keys():
                if mapped_name.replace('.html', '') == basename.replace('.html', ''):
                    html_to_drafts[basename].extend(html_to_drafts[mapped_name])
                    found = True
                    break
            if not found:
                missing_articles.append(basename)

    print("🚨 【SNSドラフトが「存在しない」記事（サムネも投稿予定もありません）】")
    if not missing_articles:
        print("  なし")
    else:
        for ma in missing_articles:
            print("  ❌ " + ma)
            
    print("\n⚠️ 【SNSドラフトが「複数ダブっている」記事】")
    for basename, folders in html_to_drafts.items():
        if len(folders) > 1:
            print(f"  🔁 {basename}")
            for f in folders:
                print(f"      - {f}")

if __name__ == '__main__':
    main()
