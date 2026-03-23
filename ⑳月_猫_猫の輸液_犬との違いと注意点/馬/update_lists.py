import re

with open("smartrc_auto.py", "r", encoding="utf-8") as f:
    text = f.read()

with open("parsed_lists.txt", "r", encoding="utf-8") as f:
    lists_text = f.read()

# LIST_A = { ... } から LIST_C = { ... } までの部分を置換
# 途中かもしれない不要なテキスト(LIST_B等)も全部一括で置換されるようにする
pattern = re.compile(r'LIST_A = \{.*?LIST_C = \{.*?\n\}', re.DOTALL)
new_text = pattern.sub(lists_text.strip(), text)

with open("smartrc_auto.py", "w", encoding="utf-8") as f:
    f.write(new_text)
