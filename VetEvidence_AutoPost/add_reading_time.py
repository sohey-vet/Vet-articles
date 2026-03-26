import glob
import os
import re
import math

count = 0
for md_path in glob.glob(r"C:\Users\souhe\Desktop\論文まとめ\topics\*\*.md"):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if "読了時間" not in content:
        char_count = len(re.sub(r'\s+', '', content))
        mins = max(1, math.ceil(char_count / 500))
        
        # Format the time nicely. If it's a huge article, cap it reasonably, usually they are 3-10 minutes.
        
        lines = content.split('\n')
        new_lines = []
        inserted = False
        for line in lines:
            new_lines.append(line)
            if line.startswith('# ') and not inserted:
                new_lines.append("")
                new_lines.append(f"> ⏱️ **読了時間**: 約{mins}分")
                new_lines.append("")
                inserted = True
                
        if inserted:
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            count += 1
            print(f"✅ 追加完了 ({mins}分): {os.path.basename(md_path)}")

print(f"\n🎉 全 {count} 件のマークダウンファイルに読了時間を復元・追記しました！")
