import os
import re
import shutil
from collections import defaultdict

def load_master_mapping():
    md_path = r'C:\Users\souhe\.gemini\antigravity\brain\1e185a7b-d16c-4c06-b71c-236033518d81\artifacts\article_tag_verification.md'
    mapping = {}
    if os.path.exists(md_path):
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
                        
    mapping['犬の急性下痢_最新エビデンス'] = '消化器'
    mapping['急性膵炎_犬猫の違いと管理'] = '消化器'
    mapping['犬慢性腸症_CE診断カスケード'] = '消化器'
    return mapping

def main():
    base_dir = r'C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts'
    thumbs_dir = r'C:\Users\souhe\Desktop\Note_Thumbs'
    
    if not os.path.exists(thumbs_dir):
        print("Note_Thumbs フォルダが見つかりません。")
        return

    master_mapping = load_master_mapping()
    
    # EXACT loop to get the same order as export_csv_for_canva_strict.py
    folders_by_category = defaultdict(list)
    folder_names = os.listdir(base_dir) # Must match the exact os.listdir order
    
    for folder in folder_names:
        folder_path = os.path.join(base_dir, folder)
        if not os.path.isdir(folder_path) or '_' not in folder:
            continue
            
        parts = folder.split('_')
        if len(parts) >= 3:
            sns_md = os.path.join(folder_path, 'sns_all_drafts.md')
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
                            
            folders_by_category[main_tag].append(folder_path)

    # Now distribute the images
    total_distributed = 0
    skipped_categories = []
    
    for category, dest_folders in folders_by_category.items():
        cat_src_dir = None
        for cand in os.listdir(thumbs_dir):
            if category in cand and os.path.isdir(os.path.join(thumbs_dir, cand)):
                cat_src_dir = os.path.join(thumbs_dir, cand)
                break
                
        if not cat_src_dir:
            print(f"Warning: Category '{category}' images folder not found.")
            continue
            
        png_files = [f for f in os.listdir(cat_src_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        def sort_key(f):
            m = re.search(r'(\d+)', f)
            return int(m.group(1)) if m else 999
            
        png_files = sorted(png_files, key=sort_key)
        
        # SAFETY CHECK: If counts do not exactly match, skip this entire category!
        if len(png_files) != len(dest_folders):
            print(f"⚠️ [スキップ] '{category}' はCSVの記事数({len(dest_folders)})と画像数({len(png_files)})が一致しないため、安全のために自動振り分けをスキップします。")
            skipped_categories.append(category)
            continue
            
        for i, dest_folder in enumerate(dest_folders):
            src_img = os.path.join(cat_src_dir, png_files[i])
            dest_img = os.path.join(dest_folder, 'note_thumbnail.png')
            shutil.copy2(src_img, dest_img)
            total_distributed += 1
                
    print(f"\n✅ 完了！ {total_distributed}枚の画像を安全に各記事のフォルダへコピーしました。")
    if skipped_categories:
        print("\n⚠️ 以下のカテゴリはCanvaからダウンロードした画像枚数と記事数が合わなかったため、途中で画像がズレるのを防ぐため自動移動を中止しました。お手数ですが、画像を見て手動で移動させてください:")
        for sc in skipped_categories:
            print(f"  - {sc}")

if __name__ == '__main__':
    main()
