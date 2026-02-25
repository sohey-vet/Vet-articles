import os
import re
from pathlib import Path

def update_tags(directory):
    base_dir = Path(directory)
    updated_files = 0
    cat_pattern = re.compile(r'猫|feline|cat', re.IGNORECASE)
    dog_pattern = re.compile(r'犬|canine|dog', re.IGNORECASE)

    for html_file in base_dir.rglob('*.html'):
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find the title or h1 to infer tags
        title_match = re.search(r'<title>(.*?)</title>', content)
        h1_match = re.search(r'<h1.*?>(.*?)</h1>', content)
        text_to_check = ""
        if title_match: text_to_check += title_match.group(1) + " "
        if h1_match: text_to_check += h1_match.group(1)

        needs_cat = bool(cat_pattern.search(text_to_check))
        needs_dog = bool(dog_pattern.search(text_to_check))

        # Find the tags div
        tags_div_match = re.search(r'(<div class="tags".*?>)(.*?)(</div>)', content, re.DOTALL)
        if not tags_div_match:
            continue
            
        tags_start = tags_div_match.group(1)
        tags_content = tags_div_match.group(2)
        tags_end = tags_div_match.group(3)

        has_cat = '>猫<' in tags_content or '猫</' in tags_content
        has_dog = '>犬<' in tags_content or '犬</' in tags_content

        new_tags = ""
        if needs_cat and not has_cat:
            new_tags += '<span class="tag tag--primary">猫</span>'
        if needs_dog and not has_dog:
            new_tags += '<span class="tag tag--primary">犬</span>'

        if new_tags:
            new_tags_content = tags_content + new_tags
            new_div = f"{tags_start}{new_tags_content}{tags_end}"
            new_content = content[:tags_div_match.start()] + new_div + content[tags_div_match.end():]
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated: {html_file.name} (Added: {new_tags})")
            updated_files += 1

    print(f"Tag update complete. {updated_files} files updated.")

if __name__ == "__main__":
    update_tags(r"c:\Users\souhe\Desktop\論文まとめ\topics")
