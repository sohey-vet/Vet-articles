import os
import re
import csv
from collections import defaultdict

VALID_16 = {
    'その他', '免疫', '内分泌', '循環器', '救急', '歯科', '消化器・肝臓', 
    '猫', '皮膚', '眼科', '神経', '腎臓', '腫瘍', '血液', '輸液', '麻酔'
}

CATEGORY_MAP = {
    '下痢': '消化器・肝臓',
    '肝臓': '消化器・肝臓',
    '消化器': '消化器・肝臓',
    '泌尿器': '腎臓',
    '腎泌尿器': '腎臓',
    '整形外科': 'その他',
    '栄養': 'その他',
    '抗菌薬': 'その他',
}

def map_category(raw_tag):
    if raw_tag in CATEGORY_MAP:
        return CATEGORY_MAP[raw_tag]
    if raw_tag in VALID_16:
        return raw_tag
    return 'その他'

def main():
    base_dir = r'C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts'
    out_dir = os.path.join(base_dir, 'VetEvidence_AutoPost', 'Canva_CSVs')
    os.makedirs(out_dir, exist_ok=True)
    
    # category -> list of dicts
    data_by_category = defaultdict(list)
    
    for folder in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder)
        if not os.path.isdir(folder_path) or '_' not in folder:
            continue
            
        parts = folder.split('_')
        if len(parts) >= 4:
            # day = parts[0]
            raw_tag = parts[1]
            title = parts[2]
            subtitle = '_'.join(parts[3:])
            
            category = map_category(raw_tag)
            
            paper_count = "9" # fallback
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
            
            if not p_found and os.path.exists(sns_md):
                with open(sns_md, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    m = re.search(r'論文(?:数)?\s*[:：]\s*(\d+)', content)
                    if not m:
                        m = re.search(r'(\d+)\s*報', content)
                    if m:
                        paper_count = m.group(1)
                        
            data_by_category[category].append({
                'タイトル': title,
                'サブタイトル': subtitle,
                '論文数': f"論文数：{paper_count}"
            })
            
    # Write CSVs
    for category, items in data_by_category.items():
        csv_path = os.path.join(out_dir, f"{category}.csv")
        with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['タイトル', 'サブタイトル', '論文数'])
            writer.writeheader()
            writer.writerows(items)
            
    print(f"✅ {len(data_by_category)} 個の正式カテゴリ別CSVを出力しました：{out_dir}")
    print("生成されたカテゴリ:", list(data_by_category.keys()))

if __name__ == '__main__':
    main()
