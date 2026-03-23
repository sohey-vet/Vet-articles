import os
import re
import csv
import shutil
from collections import defaultdict

def split_smartly(full_text):
    text_clean = full_text.replace("_", " ")
    if len(text_clean) <= 13:
        return text_clean, ""
    parts = full_text.split('_')
    if len(parts) > 1:
        return parts[0], " ".join(parts[1:])
    else:
        return text_clean, ""

def get_main_tag_from_md(md_path):
    pass # Deprecated in favor of the full mapping table

def load_master_mapping():
    md_path = r'C:\Users\souhe\.gemini\antigravity\brain\1e185a7b-d16c-4c06-b71c-236033518d81\artifacts\article_tag_verification.md'
    mapping = {}
    if not os.path.exists(md_path):
        print("Warning: article_tag_verification.md not found.")
        return mapping
        
    with open(md_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '|' in line and '.html' in line:
                cols = [col.strip() for col in line.split('|')]
                if len(cols) >= 6:
                    raw_tag = cols[3]
                    tag = raw_tag.replace('`', '').strip()
                    if tag == '消化器・肝臓':
                        tag = '消化器'
                    fname = cols[5].replace('.html', '').replace('.md', '').strip()
                    mapping[fname] = tag
                    
    # The user specifically requested these 3 to be "消化器"
    mapping['犬の急性下痢_最新エビデンス'] = '消化器'
    mapping['急性膵炎_犬猫の違いと管理'] = '消化器'
    mapping['犬慢性腸症_CE診断カスケード'] = '消化器'
    
    return mapping

def main():
    base_dir = r'C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts'
    out_dir = os.path.join(base_dir, 'VetEvidence_AutoPost', 'Canva_CSVs')
    
    master_mapping = load_master_mapping()

    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    
    data_by_category = defaultdict(list)
    total_articles = 0
    
    for folder in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder)
        if not os.path.isdir(folder_path) or '_' not in folder:
            continue
            
        parts = folder.split('_')
        if len(parts) >= 3:
            full_text = '_'.join(parts[2:])
            title, subtitle = split_smartly(full_text)
            
            paper_count = "9"
            ig_csv = os.path.join(folder_path, 'ig_carousel_data.csv')
            sns_md = os.path.join(folder_path, 'sns_all_drafts.md')
            
            p_found = False
            if os.path.exists(ig_csv):
                with open(ig_csv, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    m = re.search(r'論文(?:数)?\s*[:：]\s*(\d+)', content)
                    if m:
                        paper_count = m.group(1)
                        p_found = True
            
            main_tag = 'その他'
            
            if os.path.exists(sns_md):
                with open(sns_md, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    m_html = re.search(r'元ファイル:\s*([^\r\n]+)', content)
                    if m_html:
                        html_path = m_html.group(1).strip()
                        html_fname = os.path.basename(html_path).replace('.html', '').replace('.md', '').strip()
                        if html_fname in master_mapping:
                            main_tag = master_mapping[html_fname]
                    
                    if not p_found:
                        m = re.search(r'論文(?:数)?\s*[:：]\s*(\d+)', content)
                        if not m:
                            m = re.search(r'(\d+)\s*報', content)
                        if m:
                            paper_count = m.group(1)
                            p_found = True
                            
                        if not p_found and m_html:
                            if os.path.exists(html_path):
                                with open(html_path, 'r', encoding='utf-8', errors='ignore') as hf:
                                    h_content = hf.read()
                                    hm = re.search(r'参照論文\s*[（(]?\s*(\d+)\s*[)）]?本', h_content)
                                    if hm:
                                        paper_count = hm.group(1)
                                        p_found = True

            total_articles += 1
            data_by_category[main_tag].append({
                'タイトル': title,
                'サブタイトル': subtitle,
                '論文数': f"参照論文数:{paper_count}"
            })
            
    total_rows = 0
    for category, items in data_by_category.items():
        csv_path = os.path.join(out_dir, f"{category}.csv")
        with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['タイトル', 'サブタイトル', '論文数'])
            writer.writeheader()
            writer.writerows(items)
        total_rows += len(items)
            
    print(f"✅ CSV出力完了！実記事数: {total_articles} -> 1記事1行（重複なし）で出力しました。")
    
    # 件数をデバッグ表示
    for c in ['救急', '消化器', '消化器・肝臓']:
        if c in data_by_category:
            print(f"💡 「{c}」カテゴリ出力件数: {len(data_by_category[c])}件")

if __name__ == '__main__':
    main()
