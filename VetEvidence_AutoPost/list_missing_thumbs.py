import os
import re
from collections import defaultdict

def load_master_mapping():
    md_path = r"C:\Users\souhe\.gemini\antigravity\brain\1e185a7b-d16c-4c06-b71c-236033518d81\artifacts\article_tag_verification.md"
    mapping = {}
    if os.path.exists(md_path):
        with open(md_path, "r", encoding="utf-8") as f:
            for line in f:
                if "|" in line and ".html" in line:
                    cols = [col.strip() for col in line.split("|")]
                    if len(cols) >= 6:
                        raw_tag = cols[3]
                        tag = raw_tag.replace("`", "").strip()
                        if "消化器" in tag: tag = "消化器"
                        fname = cols[5].replace(".html", "").replace(".md", "").strip()
                        mapping[fname] = tag
    mapping["犬の急性下痢_最新エビデンス"] = "消化器"
    mapping["急性膵炎_犬猫の違いと管理"] = "消化器"
    mapping["犬慢性腸症_CE診断カスケード"] = "消化器"
    return mapping

base_dir = r"C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts"
master_mapping = load_master_mapping()
folders_by_category = defaultdict(list)

for folder in os.listdir(base_dir):
    folder_path = os.path.join(base_dir, folder)
    if not os.path.isdir(folder_path) or "_" not in folder: continue
    parts = folder.split("_")
    if len(parts) >= 3:
        sns_md = os.path.join(folder_path, "sns_all_drafts.md")
        main_tag = "その他"
        if os.path.exists(sns_md):
            with open(sns_md, "r", encoding="utf-8", errors="ignore") as f:
                c = f.read()
                m_html = re.search(r"元ファイル:\s*([^\r\n]+)", c)
                if m_html:
                    hf = os.path.basename(m_html.group(1).strip()).replace(".html", "").replace(".md", "").strip()
                    if hf in master_mapping: main_tag = master_mapping[hf]
        folders_by_category[main_tag].append(folder)

print("【腎泌尿器】(全10件):")
for i, f in enumerate(folders_by_category["腎泌尿器"]):
    print(f" {i+1}. 📁 {f}")
    
print("\n【その他】(全13件):")
for i, f in enumerate(folders_by_category["その他"]):
    print(f" {i+1}. 📁 {f}")
