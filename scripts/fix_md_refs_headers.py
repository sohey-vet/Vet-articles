import os
import re

def fix_references_headers_and_lists(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return False
        
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    in_refs = False
    ref_count = 1
    new_lines = []
    changed = False
    
    for line in lines:
        # Check for non-standard markdown headings for references
        if line.lstrip().startswith('#') and ('参照' in line or '参考' in line or 'Reference' in line or 'reference' in line):
            # Standardize heading
            new_heading = "## 📚 参照論文\n"
            if line != new_heading:
                line = new_heading
                changed = True
            in_refs = True
        elif line.lstrip().startswith('#'):
            in_refs = False
            
        if in_refs and not line.startswith('##'):
            # Check if line has any kind of list (1. / - / * / ・) or just leading spaces with numbers
            match = re.search(r'^(\s*)(?:\d+\.|-|\*|・|・)\s+(.*)', line)
            # Or match raw number without dot like "1 Sykes JE..."
            match_raw_num = re.search(r'^(\s*)(\d+)\s+(.*)', line)
            
            if match:
                indent = match.group(1)
                content = match.group(2)
                # Ensure it's using standard "1. " format
                if not line.startswith(f"{indent}{ref_count}. "):
                    line = f"{indent}{ref_count}. {content}\n"
                    changed = True
                ref_count += 1
            elif match_raw_num:
                indent = match_raw_num.group(1)
                content = match_raw_num.group(3)
                line = f"{indent}{ref_count}. {content}\n"
                ref_count += 1
                changed = True
                
        new_lines.append(line)
        
    if changed:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"Fixed formatting in {os.path.basename(filepath)} ({ref_count - 1} references)")
        return True
    else:
        print(f"No changes needed for {os.path.basename(filepath)}")
        return False

def main():
    repo_dir = r"C:\Users\souhe\Desktop\論文まとめ"
    target_files = [
        r"topics\免疫\IMHA_診断と初期治療.md",
        r"topics\循環器\猫のHCM_早期発見と管理.md",
        r"topics\歯科\歯の破折_抜歯vs保存の判断.md",
        r"topics\猫\猫の多頭飼育ストレス_環境エンリッチメントのエビデンス.md",
        r"topics\麻酔\麻酔中の低血圧_徐脈_トラブルシューティング.md",
        r"topics\内分泌\猫の甲状腺機能亢進症_治療オプション比較.md",
        r"topics\栄養\肥満管理_減量プログラムの実際.md",
        r"topics\腎泌尿器\腎臓病の食事療法_リン制限とカリウム管理.md"
    ]
    
    fixed_count = 0
    for rel_path in target_files:
        full_path = os.path.join(repo_dir, rel_path)
        if fix_references_headers_and_lists(full_path):
            fixed_count += 1
            
    print(f"Total files fixed: {fixed_count}")

if __name__ == "__main__":
    main()
