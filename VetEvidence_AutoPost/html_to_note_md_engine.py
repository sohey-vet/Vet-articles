import os
import glob
from bs4 import BeautifulSoup

BASE_DIR = r"c:\Users\souhe\Desktop\論文まとめ\topics"

def extract_cell_text(cell_element, soup):
    """
    表のセルからテキストを抽出し、改行と太字を保持
    """
    for s in cell_element.find_all("strong"):
        bold_text = s.get_text(separator=" ", strip=True)
        if bold_text and not bold_text.startswith("**"):
            s.replace_with(soup.new_string(f"**{bold_text}**"))
            
    for br in cell_element.find_all("br"):
        br.replace_with(soup.new_string("<br/>"))

    return cell_element.get_text(separator=" ", strip=True).replace("\n", "")

def parse_html_to_markdown(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    # 1. タイトル
    h1 = soup.find("h1")
    title = h1.get_text(separator=" ", strip=True) if h1 else "No Title"

    # 2. タグ
    tags = []
    meta_tags = soup.find_all(["span", "a"], class_="tag")
    for t in meta_tags:
        tags.append("#" + t.get_text(separator=" ", strip=True))
    tags_str = " ".join(tags)

    # 3. 結論 (bottom-line)
    bottom_line_div = soup.find("div", class_="bottom-line")
    bottom_line_text = ""
    if bottom_line_div:
        h3 = bottom_line_div.find("h3")
        if h3:
            h3.extract() # 結論見出し自体をツリーから削除して本文への混入を防止
            
        # 結論ブロック内にフローチャート等のノードが混入している場合、予め除外することでテキスト化時の混入を防ぐ
        for mermaid in bottom_line_div.find_all("div", class_="mermaid-wrapper"):
            mermaid.extract()
            
        for s in bottom_line_div.find_all("strong"):
            bold_text = s.get_text(separator=" ", strip=True)
            if bold_text and not bold_text.startswith("**"):
                s.replace_with(soup.new_string(f"**{bold_text}**"))
        
        bottom_line_text = bottom_line_div.get_text(separator=" ", strip=True).replace("\n", "")

    # 4. コンテンツ (accordion / card)
    content_md = []
    # FIX: BS4のclass指定を配列にすることで完全一致とし、過剰マッチによる重複出力バグ（3回出力される不具合）を解消
    accordions_and_cards = soup.find_all("div", class_=["accordion", "card"])
    seen_detail_header = False
    
    for block in accordions_and_cards:
        classes = block.get("class", [])
        parent_id = block.parent.get("id") if block.parent else None
        if parent_id in ["owner-tips", "refs"]:
            continue
            
        if "card" in classes:
            h3 = block.find("h3")
            if h3:
                content_md.append(f"## {h3.get_text(separator=' ', strip=True)}")
        
        elif "accordion" in classes:
            trigger = block.find("button", class_="accordion-trigger")
            if trigger:
                span = trigger.find("span", class_="trigger-left")
                trigger_text = span.get_text(separator=" ", strip=True) if span else trigger.get_text(separator=" ", strip=True).replace("▼", "")
                
                # 詳細解説の大見出しを初回のみ挿入
                if not seen_detail_header:
                    content_md.append("## 📖 詳細解説")
                    seen_detail_header = True
                    
                content_md.append(f"### ▼ {trigger_text}")

        # ボディ部分の処理
        body = block.find("div", class_="premium-content") or block.find("div", class_="accordion-body") or block
        
        def parse_elements(elements):
            for child in elements:
                if child.name is None:
                    continue
                if child.get("id") in ["owner-tips", "refs"]:
                    continue
                if child.name == "div" and "mermaid-wrapper" not in child.get("class", []):
                    # もし内部にブロック要素（p, ul, ol, divなど）が一切ない場合、このdiv自体がpタグの代わり（テキストコンテナ）になっていると判断してテキストを抽出する
                    if not child.find(["p", "ul", "ol", "div", "h3", "h4", "table"]):
                        for s in child.find_all("strong"):
                            text = s.get_text(separator=" ", strip=True)
                            if text and not text.startswith("**"):
                                s.replace_with(soup.new_string(f"**{text}**"))
                        for br in child.find_all("br"):
                            br.replace_with(soup.new_string("<br/>"))
                        
                        div_text = child.get_text(separator=" ", strip=True).replace("\n", "")
                        if div_text:
                            content_md.append(div_text)
                            content_md.append("")
                    else:
                        # ネストされたdivの内部（key-findingsやclinical-tip）を再帰的に探索
                        parse_elements(child.children)
                elif child.name == "h3" and "card" not in classes:
                    content_md.append(f"### ▼ {child.get_text(separator=' ', strip=True)}")
                elif child.name == "h4":
                    for s in child.find_all("strong"):
                        text = s.get_text(separator=" ", strip=True)
                        if text and not text.startswith("**"):
                            s.replace_with(soup.new_string(f"**{text}**"))
                    content_md.append(f"**{child.get_text(separator=' ', strip=True)}**")
                elif child.name == "p":
                    for s in child.find_all("strong"):
                        text = s.get_text(separator=" ", strip=True)
                        if text and not text.startswith("**"):
                            s.replace_with(soup.new_string(f"**{text}**"))
                    for br in child.find_all("br"):
                        br.replace_with(soup.new_string("<br/>"))
                    
                    p_text = child.get_text(separator=" ", strip=True).replace("\n", "")
                    if p_text:
                        content_md.append(p_text)
                        content_md.append("")
                elif child.name in ["ul", "ol"]:
                    list_items = []
                    for i, li in enumerate(child.find_all("li"), 1):
                        for s in li.find_all("strong"):
                            text = s.get_text(separator=" ", strip=True)
                            if text and not text.startswith("**"):
                                s.replace_with(soup.new_string(f"**{text}**"))
                        text_val = li.get_text(separator=" ", strip=True).replace("\n", "").replace("\r", "")
                        if child.name == "ol":
                            list_items.append(f"{i}. {text_val}")
                        else:
                            list_items.append(f"- {text_val}")
                    # 要素間に空行を入れずに結合することで箇条書きの行間を詰める
                    content_md.extend(list_items)
                    content_md.append("") 
                elif child.name == "table":
                    headers = []
                    for th in child.find_all("th"):
                        headers.append(extract_cell_text(th, soup))
                    if headers:
                        content_md.append("| " + " | ".join(headers) + " |")
                        content_md.append("|" + "|".join(["---"] * len(headers)) + "|")
                    for tr in child.find_all("tr"):
                        if tr.find("th"): continue
                        tds = []
                        for td in tr.find_all("td"):
                            tds.append(extract_cell_text(td, soup))
                        if tds:
                            content_md.append("| " + " | ".join(tds) + " |")
                    content_md.append("")

        parse_elements(body.children)

    # 5. 飼い主への説明
    owner_section = soup.find("div", id="owner-tips")
    owner_md = ["## 🗣️ 飼い主への説明ガイド"]
    if owner_section:
        tips = owner_section.find_all("div", class_="owner-tip")
        for tip in tips:
            q = tip.find("h4")
            a = tip.find("div", class_="speech-bubble")
            if q:
                q_text = q.get_text(separator=" ", strip=True)
                if not q_text.startswith("Q.") and not q_text.startswith("Q "):
                    q_text = f"Q. {q_text}"
                owner_md.append(f"**{q_text}**")
            if a: owner_md.append(a.get_text(separator=" ", strip=True).replace("\n", " "))
            owner_md.append("")

    # 6. 参照論文
    ref_section = soup.find("div", id="refs")
    ref_md = ["## 📚 参照論文"]
    if ref_section:
        lis = ref_section.find_all("li")
        for i, li in enumerate(lis, 1):
            text = " ".join(li.get_text(separator=" ", strip=True).replace("\n", " ").replace("\r", " ").split())
            ref_md.append(f"{i}. {text}")
        if not lis:
            ref_md.append("（記載なし）")
    
    full_md = []
    full_md.append(f"# {title}\n")
    full_md.append(f"> ⏱️ **読了時間**: 約5分\n")
    if tags_str:
        full_md.append(f"{tags_str}\n")
    full_md.append(f"## 🎯 結論\n{bottom_line_text}\n")
    full_md.append("\n".join(content_md))
    full_md.append("\n".join(owner_md))
    full_md.append("\n".join(ref_md))
    
    return "\n".join(full_md)

def main():
    print("【MD抽出スクリプト（完全版v4）】のテスト待機中...")

if __name__ == "__main__":
    main()
