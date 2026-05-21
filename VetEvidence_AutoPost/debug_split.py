import json
import sys
import re

def clean_cta_and_links(t):
    konkyo_marker = "📄 根拠:"
    if konkyo_marker in t:
        t = t[:t.rfind(konkyo_marker)].strip()
        
    blocks = re.split(r'\n\s*\n', t)
    split_index = len(blocks)
    for i in range(len(blocks) - 1, -1, -1):
        block = blocks[i]
        if "http:" in block or "https:" in block or "note.com" in block:
            split_index = i
            while split_index > 0:
                prev_block = blocks[split_index - 1]
                if any(k in prev_block for k in ["詳細", "Note", "プロフ", "リンク", "💡", "🔗", "👇", "こちら"]):
                    split_index -= 1
                else:
                    break
            break
            
    if split_index == len(blocks):
        cta_marker = "詳細・エビデンスはNoteへ"
        if cta_marker in t:
            idx = t.rfind(cta_marker)
            main_t = t[:idx].strip()
        else:
            main_t = t
    else:
        main_t = "\n\n".join(blocks[:split_index]).strip()
    
    if not main_t:
        return ""
        
    if main_t.endswith("👇") or main_t.endswith("💡"):
        main_t = main_t[:-1].strip()
        
    return main_t

def split_text(t, limit=480):
    chunks = []
    while len(t) > limit:
        # 1. 見出し（【）の前での分割を最優先
        split_idx = t.rfind("\n【", 0, limit)
        if split_idx == -1:
            split_idx = t.rfind("\n・", 0, limit)
        # 2. 見出しがない場合は段落の切れ目
        if split_idx == -1:
            split_idx = t.rfind("\n\n", 0, limit)
        # 3. 通常の改行
        if split_idx == -1:
            split_idx = t.rfind("\n", 0, limit)
        # 4. 改行もない場合は句点
        if split_idx == -1:
            split_idx = t.rfind("。", 0, limit)
        
        if split_idx == -1:
            split_idx = limit
        else:
            if t[split_idx] == "。":
                split_idx += 1 # 句点は含める
            
        chunks.append(t[:split_idx].strip())
        t = t[split_idx:].strip()
    if t:
        chunks.append(t)
    return chunks

def normalize_text(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text

with open('sns_schedule.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

t = [p['content'] for p in d if p['date']=='2026-05-15' and p['platform']=='Threads'][0]
t = normalize_text(t)
main_text = clean_cta_and_links(t)
chunks = split_text(main_text, 480)

print(f"Total chunks: {len(chunks)}")
for i, c in enumerate(chunks):
    print(f"--- Chunk {i+1} ({len(c)} chars) ---")
    print(c)
