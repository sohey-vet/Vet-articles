"""
enhance_note_articles.py
─────────────────────────────
Note 用の整形済テキストに、各テーブル前のセクション導入文を追加するスクリプト。
元の Markdown テーブルの見出しと内容をもとに、読者向けの導入テキストを自動生成する。

使い方:
  python scripts/enhance_note_articles.py
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(r"c:\Users\souhe\Desktop\論文まとめ")
TOPICS_DIR = PROJECT_ROOT / "topics"
OUTPUT_DIR = PROJECT_ROOT / "topics_note"

# ──────────────────────────────────────────────
#  テーブル見出しに基づいたセクション導入文
# ──────────────────────────────────────────────
# 各テーブルのカラムヘッダーパターン → 導入テキストのテンプレート
SECTION_INTROS = {
    # 2列の比較表パターン（旧vs新、昔vs今 等）
    "比較": "以下の表で、従来の考え方と最新のエビデンスに基づく推奨の違いを比較しています。",
    "昔の常識": "現在のエビデンスでは、いくつかの従来の管理法が見直されています。以下の表で旧常識と最新推奨を比較してください。",
    "旧常識": "現在のエビデンスでは、いくつかの従来の管理法が見直されています。以下の表で旧常識と最新推奨を比較してください。",
    # 数値・カットオフ表
    "数値": "臨床で必要になる重要な数値データを以下にまとめました。",
    "カットオフ": "臨床判断に必要な主要なカットオフ値を以下にまとめました。",
    # アクション表・プロトコル
    "アクション": "実際の臨床現場での具体的なアクションポイントを以下に整理しました。",
    "プロトコル": "標準的なプロトコルを以下の表にまとめました。各施設の状況に合わせて適用してください。",
    "ステップ": "段階的な対応手順を以下の表に整理しました。",
    "フロー": "臨床での判断フローを以下にまとめました。",
    "アルゴリズム": "診断・治療のアルゴリズムを以下に整理しました。",
    # 鑑別診断表
    "鑑別": "鑑別診断に必要な要点を以下の表にまとめました。",
    "原因": "主な原因とその特徴を以下の表で確認してください。",
    # 薬剤表
    "薬剤": "使用する薬剤の用量・投与方法を以下にまとめました。",
    "薬物": "薬物療法のプロトコルを以下に整理しました。各薬剤の用量と投与タイミングを確認してください。",
    "用量": "薬剤の具体的な用量と投与方法を以下にまとめました。",
    # 分類表
    "分類": "以下の表で分類と各カテゴリーの特徴を確認してください。",
    "ステージ": "ステージ別の特徴と対応を以下にまとめました。",
    "グレード": "重症度分類と各グレードの特徴を以下に示します。",
    # 生存率・予後
    "生存率": "報告されている生存率データを以下にまとめました。",
    "予後": "予後に関するデータを以下に整理しました。",
    # モニタリング
    "モニタリング": "モニタリングの要点と目標値を以下にまとめました。",
    "管理": "管理のポイントを以下の表に整理しました。",
    # 食事・栄養
    "食事": "食事管理のポイントを以下にまとめました。",
    "フード": "推奨されるフードの選択肢を以下にまとめました。",
    "栄養": "栄養管理のポイントを以下に整理しました。",
}


def get_intro_for_section(heading: str, table_header_line: str) -> str:
    """
    見出しとテーブルヘッダーの内容から適切な導入文を生成。
    """
    combined = (heading + " " + table_header_line).lower()

    # テーブルの列数に基づくヒント
    col_count = table_header_line.count("|") - 1

    # マッチするパターンを探す
    for keyword, intro in SECTION_INTROS.items():
        if keyword.lower() in combined or keyword in heading:
            return intro

    # デフォルトの導入文
    if col_count <= 2:
        return "以下の表に要点をまとめました。"
    elif col_count <= 3:
        return "重要なポイントを以下の表に整理しました。"
    else:
        return "臨床で参照すべき情報を以下の表にまとめました。"


def enhance_formatted_article(formatted_path: Path, md_path: Path) -> bool:
    """
    整形済みテキストの各テーブル画像の前に導入テキストを追加する。
    """
    content = formatted_path.read_text(encoding="utf-8")
    md_content = md_path.read_text(encoding="utf-8")

    # 元 Markdown からテーブルの見出しとヘッダーを抽出
    md_lines = md_content.splitlines()
    table_contexts = []  # (直前の見出し, テーブルヘッダー行) のリスト

    current_heading = ""
    for i, line in enumerate(md_lines):
        stripped = line.strip()
        if stripped.startswith("##"):
            current_heading = stripped.lstrip("#").strip()
        elif stripped.startswith("|") and stripped.endswith("|"):
            # テーブルの最初の行（ヘッダー）
            if i + 1 < len(md_lines):
                next_line = md_lines[i + 1].strip()
                if re.match(r'\|[\s:|-]+\|$', next_line):
                    table_contexts.append((current_heading, stripped))
                    # テーブルの残りの行をスキップするため、フラグは不要
                    # （次のヘッダー行が来るまで同じテーブル）

    # 既にテーブル前に導入テキストがあるかチェック
    lines = content.splitlines()
    new_lines = []
    table_idx = 0

    i = 0
    while i < len(lines):
        line = lines[i]

        if "[IMAGE:" in line and table_idx < len(table_contexts):
            heading, header_line = table_contexts[table_idx]
            intro = get_intro_for_section(heading, header_line)

            # 直前に既に導入テキストがあるかチェック
            prev_text_line = ""
            for j in range(len(new_lines) - 1, -1, -1):
                if new_lines[j].strip():
                    prev_text_line = new_lines[j].strip()
                    break

            # 直前が見出し (##) か空の場合のみ挿入
            if prev_text_line.startswith("##") or prev_text_line.startswith("###") or not prev_text_line:
                new_lines.append(intro)
                new_lines.append("")

            new_lines.append(line)
            table_idx += 1
        else:
            new_lines.append(line)
        i += 1

    new_content = "\n".join(new_lines)

    # リスト記号 - を ・ に変換（Note は - をリストとして扱うため）
    new_content = re.sub(r'^- \*\*', '・**', new_content, flags=re.MULTILINE)
    new_content = re.sub(r'^- ([^*])', r'・\1', new_content, flags=re.MULTILINE)

    formatted_path.write_text(new_content, encoding="utf-8")
    return True


def main():
    formatted_files = sorted(OUTPUT_DIR.glob("*_formatted.txt"))
    # done フォルダ内のファイルも含める
    done_dir = OUTPUT_DIR / "done"
    if done_dir.exists():
        formatted_files.extend(sorted(done_dir.glob("*_formatted.txt")))

    print(f"{'='*60}")
    print(f"  導入テキスト追加: {len(formatted_files)} 記事")
    print(f"{'='*60}")

    # 元 .md ファイルのマッピング
    md_files = {f.stem: f for f in TOPICS_DIR.rglob("*.md")}

    success = 0
    for fmt_file in formatted_files:
        article_name = fmt_file.stem.replace("_formatted", "")
        if article_name in md_files:
            print(f"  📝 {article_name}")
            try:
                enhance_formatted_article(fmt_file, md_files[article_name])
                success += 1
                print(f"     ✅ 完了")
            except Exception as e:
                print(f"     ❌ エラー: {e}")
        else:
            print(f"  ⚠️  {article_name}: 元MarkdownなしSkip")

    print(f"\n合計: {success}/{len(formatted_files)} 完了")


if __name__ == "__main__":
    main()
