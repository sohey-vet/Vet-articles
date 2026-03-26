import os
import re

files_to_fix = [
    r"C:\Users\souhe\Desktop\論文まとめ\topics\腎泌尿器\猫のCKD_IRISステージ別管理.md",
    r"C:\Users\souhe\Desktop\論文まとめ\topics\免疫\IMHA_診断と初期治療.md",
    r"C:\Users\souhe\Desktop\論文まとめ\topics\循環器\心原性肺水腫_一般病院での救命Tips.md",
    r"C:\Users\souhe\Desktop\論文まとめ\topics\抗菌薬\抗菌薬選択の基本原則.md",
    r"C:\Users\souhe\Desktop\論文まとめ\topics\神経\椎間板ヘルニア_頚部胸腰部統合版.md",
    r"C:\Users\souhe\Desktop\論文まとめ\topics\救急\中毒_初期対応と活性炭.md",
]

for file_path in files_to_fix:
    if not os.path.exists(file_path):
        print(f"Skipping {file_path}, does not exist.")
        continue
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract owner tips HTML
    owner_match = re.search(r'<div id="owner-tips">.*?</button>.*?<div class="accordion-content">.*?<div class="accordion-body premium-content">(.*?)</div>.*?<div class="premium-lock">.*?</div>', content, re.DOTALL)
    
    if owner_match:
        inner_html = owner_match.group(1)
        
        # Parse inner HTML owner tips to Markdown
        tips = re.findall(r'<h4>(.*?)</h4>.*?<div class="speech-bubble">(.*?)</div>', inner_html, re.DOTALL)
        markdown_tips = "## 🗣️ 飼い主への説明ガイド\n\n"
        for q, a in tips:
            markdown_tips += f"**{q.strip()}**\n{a.strip()}\n\n"
            
        content = re.sub(r'<div id="owner-tips">.*?</div>\n*  </div>\n*</div>', markdown_tips.strip(), content, flags=re.DOTALL)

    # Extract refs HTML
    refs_match = re.search(r'<div id="refs">.*?</button>.*?<div class="accordion-content">.*?<div class="accordion-body">(.*?)</div>.*?</div>', content, re.DOTALL)
    if refs_match:
        inner_html = refs_match.group(1)
        # Parse list elements
        li_items = re.findall(r'<li>(.*?)</li>', inner_html, re.DOTALL)
        markdown_refs = "## 📚 参照論文\n\n"
        for item in li_items:
            # Handle <em> inside refs
            item = re.sub(r'<em>(.*?)</em>', r'*\1*', item)
            markdown_refs += f"- {item.strip()}\n"
            
        content = re.sub(r'<div id="refs">.*?</div>\n*  </div>\n*</div>', markdown_refs.strip(), content, flags=re.DOTALL)

    # Note: Sometimes the end tags formatting varies, so robust generic replacement:
    content = re.sub(r'<div id="owner-tips">.*?(?=---)', markdown_tips.strip() + '\n\n', content, flags=re.DOTALL) if owner_match else content
    content = re.sub(r'<div id="refs">.*?(?=---)', markdown_refs.strip() + '\n\n', content, flags=re.DOTALL) if refs_match else content

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Fixed {os.path.basename(file_path)}")

