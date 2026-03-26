import os

target_dirs = [
    r"C:\Users\souhe\Desktop\論文まとめ\topics"
]

count = 0
for d in target_dirs:
    for root, dirs, files in os.walk(d):
        for f in files:
            if f.endswith('.md'):
                path = os.path.join(root, f)
                with open(path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                
                new_lines = [line for line in lines if "この記事の対象" not in line]
                
                if len(lines) != len(new_lines):
                    with open(path, 'w', encoding='utf-8') as file:
                        file.writelines(new_lines)
                    count += 1
                    
print(f"Removed 'この記事の対象' line from {count} files in topics and VetEvidence_SNS_Drafts.")
