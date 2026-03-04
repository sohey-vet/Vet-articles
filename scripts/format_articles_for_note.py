"""
format_articles_for_note.py
─────────────────────────────
Markdown 記事 → Note 投稿用テキスト変換スクリプト

Note のスクロール閲覧に最適化:
  - テーブルは簡潔な箇条書きに変換
  - 見出しと本文の余白を最小化
  - プロフェッショナルで読みやすいレイアウト

使い方:
  python scripts/format_articles_for_note.py
  python scripts/format_articles_for_note.py --file topics/救急/CPR.md
"""

import os
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(r"c:\Users\souhe\Desktop\論文まとめ")
TOPICS_DIR = PROJECT_ROOT / "topics"
OUTPUT_DIR = PROJECT_ROOT / "topics_note"


# ──────────────────────────────────────────────
#  テーブル → テキスト変換（Note最適化）
# ──────────────────────────────────────────────

def parse_markdown_table(table_md: str) -> dict:
    lines = [l.strip() for l in table_md.strip().split("\n") if l.strip()]
    if len(lines) < 3:
        return {"headers": [], "rows": []}

    def split_cells(line):
        cells = line.strip().strip("|").split("|")
        return [c.strip() for c in cells]

    headers = split_cells(lines[0])
    rows = [split_cells(l) for l in lines[2:]]
    return {"headers": headers, "rows": rows}


def clean_cell(text):
    """セルテキストをクリーンアップ"""
    # 取消線 → 【廃止】
    text = re.sub(r'~~(.*?)~~', r'【廃止】\1', text)
    text = re.sub(r'</?em>', '', text)
    # ** を除去（変換側で改めて適用する）
    text = text.replace("**", "")
    # ⛔ を除去（意味不明と指摘あり）
    text = text.replace("⛔ ", "").replace("⛔", "")
    return text.strip()


def shorten_label(label: str) -> str:
    """冗長なカラムヘッダーを短縮する"""
    mapping = {
        "2024年の変更点・強調ポイント": "変更点",
        "現場での具体的アクション": "アクション",
        "タイミング・備考": "備考",
    }
    for long, short in mapping.items():
        if long in label:
            return short
    return label


def table_to_text(table_md: str) -> str:
    """
    Markdown テーブルを Note 向けの簡潔な箇条書きに変換。
    """
    data = parse_markdown_table(table_md)
    headers = data["headers"]
    rows = data["rows"]

    if not headers or not rows:
        return table_md

    num_cols = len(headers)
    out = []

    h_lower = " ".join(h.lower() for h in headers)

    # --- 2列テーブル ---
    if num_cols == 2:
        is_comparison = any(kw in h_lower for kw in [
            "旧", "昔", "❌", "常識", "従来", "vs", "新", "最新"
        ])

        if is_comparison:
            for row in rows:
                if len(row) >= 2:
                    old = clean_cell(row[0])
                    new = clean_cell(row[1])
                    out.append(f"・旧）{old}")
                    out.append(f"・新）{new}")
                    out.append("")
        else:
            for row in rows:
                if len(row) >= 2:
                    key = clean_cell(row[0])
                    val = clean_cell(row[1])
                    out.append(f"・**{key}** → {val}")
                    out.append("")

    # --- 3列テーブル ---
    elif num_cols == 3:
        h1_short = shorten_label(clean_cell(headers[1]))
        h2_short = shorten_label(clean_cell(headers[2]))

        for row in rows:
            if len(row) < 3:
                continue
            c0 = clean_cell(row[0])
            c1 = clean_cell(row[1])
            c2 = clean_cell(row[2])

            out.append(f"**{c0}**")
            if c1:
                out.append(f"・{h1_short}: {c1}")
            if c2:
                out.append(f"・{h2_short}: {c2}")
            out.append("")

    # --- 4列以上 ---
    else:
        for row in rows:
            if len(row) < num_cols:
                continue
            c0 = clean_cell(row[0])
            out.append(f"**{c0}**")
            for j in range(1, num_cols):
                hdr = shorten_label(clean_cell(headers[j])) if j < len(headers) else ""
                val = clean_cell(row[j])
                if val:
                    out.append(f"・{hdr}: {val}" if hdr else f"・{val}")
            out.append("")

    return "\n".join(out).strip()


# ──────────────────────────────────────────────
#  導入文の自動生成
# ──────────────────────────────────────────────

def generate_intro(title: str, body_text: str) -> str:
    """タイトルと本文から動的な導入文を生成"""
    parts = re.split(r'[─—―]', title, 1)
    main_topic = parts[0].strip()

    # 本文から「結論」や最初の重要な一文を抽出する
    # 結論セクションがあれば、そこの最初のテキスト行を取得
    intro_sentence = ""
    lines = body_text.splitlines()
    
    in_conclusion = False
    for line in lines:
        stripped = line.strip()
        if "## 🎯 結論" in stripped:
            in_conclusion = True
            continue
        
        if in_conclusion:
            if stripped.startswith("## ") or stripped.startswith("### "):
                break # 次のセクションに入った
            
            # リスト記号や太字マーカーなどを除去して純粋なテキストを取得
            clean_line = re.sub(r'^[・\-*0-9①-⑨\.]+\s*', '', stripped)
            clean_line = clean_line.replace('**', '')
            
            if len(clean_line) > 15: # 短すぎる行はスキップ
                intro_sentence = clean_line
                break

    # 結論から取れなかった場合は、本文の最初の長めの文を取得
    if not intro_sentence:
        for line in lines:
            stripped = line.strip()
            if not stripped.startswith("#") and not stripped.startswith("|") and len(stripped) > 20:
                clean_line = re.sub(r'^[・\-*0-9①-⑨\.]+\s*', '', stripped)
                intro_sentence = clean_line.replace('**', '')
                break

    # 抽出した文末が句点で終わっていなければ補う
    if intro_sentence and not intro_sentence.endswith(("。", "！", "？")):
        intro_sentence += "。"

    if intro_sentence:
        return f"今回のテーマは **{main_topic}**。\n{intro_sentence}\n\n明日からの診療にすぐ活かせる実践的なポイントを整理しました。"
    else:
        return f"この記事では **{main_topic}** について、最新のエビデンスと臨床現場で役立つポイントをまとめました。"


# ──────────────────────────────────────────────
#  HTML ブロックの抽出・除去
# ──────────────────────────────────────────────

def process_owner_tips_block(block_html: str) -> str:
    qas = re.findall(
        r'<h4>(.*?)</h4>\s*<div class="speech-bubble">(.*?)</div>',
        block_html, flags=re.DOTALL
    )
    if not qas:
        return ""
    result = "\n## 🗣️ 飼い主への説明ガイド\n"
    for q, a in qas:
        q = q.strip()
        a = a.strip()
        result += f"**{q}**\n{a}\n\n"
    return result


def process_refs_block(block_html: str) -> str:
    items = re.findall(r'<li>(.*?)</li>', block_html, flags=re.DOTALL)
    if not items:
        return ""
    result = "\n## 📚 参照論文\n"
    for item in items:
        clean = re.sub(r'<[^>]+>', '', item).strip()
        result += f"・{clean}\n"
    return result + "\n"


def clean_html_blocks(text: str) -> str:
    owner_tips = re.findall(
        r'<div id="owner-tips">.*?</div>\s*</div>\s*</div>',
        text, flags=re.DOTALL
    )
    for block in owner_tips:
        replacement = process_owner_tips_block(block)
        text = text.replace(block, replacement)

    refs = re.findall(
        r'<div id="refs">.*?</div>\s*</div>\s*</div>',
        text, flags=re.DOTALL
    )
    for block in refs:
        replacement = process_refs_block(block)
        text = text.replace(block, replacement)

    text = re.sub(r'<(?![\s\d])/?[a-zA-Z][^>]*>', '', text)
    return text


def clean_body(text: str) -> str:
    """本文を Note 向けに整形"""

    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    text = clean_html_blocks(text)
    text = re.sub(r'🔒.*?有料会員限定です', '', text)
    text = re.sub(r'## ✏️ 編集情報.*', '', text, flags=re.DOTALL)
    text = re.sub(r'```\s*ジャンル:.*?```', '', text, flags=re.DOTALL)
    text = re.sub(
        r'>\s*📋\s*\*\*この記事の対象\*\*.*?\n'
        r'>\s*⏱️\s*\*\*読了時間\*\*.*?\n'
        r'(>\s*📄\s*\*\*参照ガイドライン\*\*.*?\n)?',
        '', text
    )

    # 水平線 (---) を除去
    text = re.sub(r'^---\s*$', '', text, flags=re.MULTILINE)

    # 行頭の空白のみの行をクリーンアップ
    text = re.sub(r'^[ \t]+$', '', text, flags=re.MULTILINE)

    # 連続空行を最大 1 行に
    text = re.sub(r'\n{3,}', '\n\n', text)

    # 「（30秒で読める）」等の補足を除去
    text = re.sub(r'（[^）]*秒で読める）', '', text)

    # H1 → H2
    text = re.sub(r'^# ', '## ', text, flags=re.MULTILINE)

    # H3 → H2（Note では H3 が小さすぎてセクション見出しに見えない）
    text = re.sub(r'^### ', '## ', text, flags=re.MULTILINE)

    # H2 直後の空行を除去（Note の H2 は元々マージンがあるため余白が二重になる）
    text = re.sub(r'(^##[^\n]+)\n\n', r'\1\n', text, flags=re.MULTILINE)

    # リスト記号 - を ・ に変換
    text = re.sub(r'^- \*\*', '・**', text, flags=re.MULTILINE)
    text = re.sub(r'^- ([^*])', r'・\1', text, flags=re.MULTILINE)

    # ⛔ を除去
    text = text.replace("⛔ ", "").replace("⛔", "")

    return text.strip()


# ──────────────────────────────────────────────
#  Markdown テーブルの検出
# ──────────────────────────────────────────────

def find_markdown_tables(text: str) -> list:
    lines = text.split('\n')
    tables = []
    current_table = []
    in_table = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('|') and stripped.endswith('|'):
            current_table.append(line)
            in_table = True
        else:
            if in_table and len(current_table) >= 3:
                sep_line = current_table[1].strip()
                if re.match(r'\|[\s:|-]+\|$', sep_line):
                    tables.append('\n'.join(current_table))
            current_table = []
            in_table = False

    if in_table and len(current_table) >= 3:
        sep_line = current_table[1].strip()
        if re.match(r'\|[\s:|-]+\|$', sep_line):
            tables.append('\n'.join(current_table))

    return tables


# ──────────────────────────────────────────────
#  メイン変換処理
# ──────────────────────────────────────────────

def format_article_for_note(file_path: Path):
    print(f"\n📄 Processing: {file_path.name}")
    content = file_path.read_text(encoding="utf-8")

    # タイトル抽出
    lines = content.splitlines()
    title = ""
    if lines and lines[0].startswith("# "):
        title = lines[0].replace("# ", "", 1).strip()
        lines = lines[1:]
    body_text = "\n".join(lines)

    # タグ抽出
    tags = ["獣医", "獣医師", "動物病院", "エビデンス"]
    tag_match = re.search(r'ハッシュタグ\s*→\s*(.*?)(?:\n|$)', content)
    if tag_match:
        found = re.findall(r'#([^\s#]+)', tag_match.group(1))
        if found:
            tags = found
            
    # ハッシュタグ行を本文から除去
    body_text = re.sub(r'ハッシュタグ\s*→.*?(?:\n|$)', '', body_text)

    # テーブルをテキスト形式に変換
    tables = find_markdown_tables(body_text)
    for table_md in tables:
        text_version = table_to_text(table_md.strip())
        body_text = body_text.replace(table_md, "\n" + text_version + "\n")

    # 本文クリーンアップ
    body_text = clean_body(body_text)

    # 導入文を先頭に挿入
    intro = generate_intro(title, body_text)
    # 結論セクションの直前に導入を入れる
    if "## 🎯 結論" in body_text:
        body_text = body_text.replace(
            "## 🎯 結論",
            f"{intro}\n\n## 🎯 結論"
        )
    else:
        # 結論セクションがない場合は冒頭に
        body_text = intro + "\n\n" + body_text

    # 最終整形: 連続空行を再度圧縮
    body_text = re.sub(r'\n{3,}', '\n\n', body_text)

    # 出力
    article_name = file_path.stem
    output_path = OUTPUT_DIR / f"{article_name}_formatted.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"TITLE\n{title}\n\nTAGS\n{','.join(tags)}\n\nBODY\n{body_text}\n")
    print(f"  ✅ Saved → {output_path.name}")
    return output_path


def process_all():
    md_files = sorted(TOPICS_DIR.rglob("*.md"))
    if not md_files:
        print("No .md files found in topics/")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"{'='*60}")
    print(f"  Note 用フォーマット変換: {len(md_files)} 記事")
    print(f"{'='*60}")

    results = []
    for f in md_files:
        try:
            format_article_for_note(f)
            results.append((f.name, True))
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append((f.name, False))

    print(f"\n{'='*60}")
    print(f"  変換結果サマリー")
    print(f"{'='*60}")
    for name, ok in results:
        print(f"  {'✅' if ok else '❌'} {name}")
    success = sum(1 for _, ok in results if ok)
    print(f"\n合計: {success}/{len(results)} 成功")


if __name__ == "__main__":
    if "--file" in sys.argv:
        idx = sys.argv.index("--file")
        if idx + 1 < len(sys.argv):
            target = Path(sys.argv[idx + 1])
            if target.exists():
                format_article_for_note(target)
            else:
                print(f"File not found: {target}")
    else:
        process_all()
