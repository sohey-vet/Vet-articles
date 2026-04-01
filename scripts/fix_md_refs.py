import os
import re

def fix_references_in_file(filepath):
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
        if line.startswith('## '):
            if '参照' in line or '参考' in line or 'Reference' in line or 'reference' in line:
                in_refs = True
            else:
                in_refs = False
        
        if in_refs:
            # Check if line starts with '・' (possibly with leading whitespace)
            match = re.search(r'^(\s*)・\s*(.*)', line)
            if match:
                indent = match.group(1)
                content = match.group(2)
                line = f"{indent}{ref_count}. {content}\n"
                ref_count += 1
                changed = True
                
        new_lines.append(line)
        
    if changed:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"Fixed {ref_count - 1} references in {os.path.basename(filepath)}")
        return True
    else:
        print(f"No changes needed for {os.path.basename(filepath)}")
        return False

def main():
    repo_dir = r"C:\Users\souhe\Desktop\論文まとめ"
    target_files = [
        r"topics\下痢\犬の急性下痢_最新エビデンス.md",
        r"topics\腎泌尿器\猫のCKD_IRISステージ別管理.md",
        r"topics\循環器\心原性肺水腫_一般病院での救命Tips.md",
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
        if fix_references_in_file(full_path):
            fixed_count += 1
            
    print(f"Total files fixed: {fixed_count}")

if __name__ == "__main__":
    main()
