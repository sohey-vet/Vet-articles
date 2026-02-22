import os
import sys
import re
import json
import glob
import textwrap

# Windows環境での文字化け・エンコードエラー防止
sys.stdout.reconfigure(encoding='utf-8')

# pip install google-generativeai
try:
    import google.generativeai as genai
except ImportError:
    print("google-generativeai パッケージがインストールされていません。")
    print("実行前に: pip install google-generativeai を実行してください。")
    exit(1)

# APIキーの設定
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("環境変数 GEMINI_API_KEY が設定されていません。")
    print("実行前に: set GEMINI_API_KEY=あなたのAPIキー を実行してください。")
    exit(1)

genai.configure(api_key=API_KEY)

# JSON出力が可能な比較的新しい有能モデルを使用
model = genai.GenerativeModel("gemini-2.5-flash", generation_config={"response_mime_type": "application/json"})

def generate_diagram(article_html: str) -> dict:
    """記事のHTML文字列を受け取り、図表の要否・挿入箇所・コードを辞書で返す"""
    prompt = f"""
    あなたは「日本の夜間救急・一次診療の最前線で働くベテラン獣医師」であり、同時に優秀な「メディカルエディター」です。
    以下の【HTML形式の獣医学論文まとめ記事】を読み込んでください。

    【指示内容】
    1. この記事を読者がより深く・直感的に理解するために、文章や既存の表だけでは伝わりにくい情報を整理した「オリジナルの図解（フローチャート等）」があった方が良いと思われる箇所を探してください。
       （例：複雑な診断アルゴリズム、治療のステップ、病態生理のフロー図など）
    2. 図解が不要、またはすでに十分分かりやすく必要がない場合は {{"needs_diagram": false}} としてください。
    3. 有益でありどうしても「図解」を含めるべきであると判断した場合、元の論文の表現のコピー（スクショ等）ではなく、完全にゼロから再構築・再デザインしたオリジナルの図解を作成してください。
       - 原則として、フローチャートやアルゴリズム、関係図等の視覚的表現のため Mermaid 記法 (`<pre class="mermaid">...</pre>`) を用いて生成してください。単純な表（Markdownテーブル）よりも視覚的な図解を優先してください。
       - **【重要】Mermaidの文法エラーを絶対に避けること。ノード内のテキストに括弧や記号（例えば `<` や `>` や `&` や `%` など）やHTMLタグ（`<br>`など）は絶対に使用しないでください。**
       - **【重要】ノードのテキストは極力シンプルに短くし、複雑な記号を用いないでください（例: `A[PLT under 20000]` のように記号を避ける）。**
       - **【重要】Mermaidのコードブロック内に、全角スペースや不要なタブ文字を絶対に入れないでください。Syntax Errorのよくある原因になります。**
       - **【重要】出力する `diagram_code` の値には、Markdownのコードブロックのバッククォート（```mermaid や ```）を絶対に入れないでください。純粋なHTMLタグ（<pre class="mermaid">...</pre>）のみを出力してください。**
    4. その図解を挿入すべき位置の直前にある、原文内の「特徴的な1文または見出し（そのまま検索可能な連続した文字列）」を `insert_after_text` として指定してください（不要な場合は空文字不可）。
       - **【重要】図解はアコーディオンの中（`<div class="accordion-content">`の中）には絶対に入れないでください。必ず「結論」や「トップレベルの見出し（h3など）」の直下など、最初から開いていて見やすい場所（例：「🎯 結論」などのテキスト）を `insert_after_text` に指定してください。**

    {article_html}

    【出力JSONフォーマット】必ず以下のJSONスキーマの形式で出力してください。
    {{
        "needs_diagram": true または false,
        "insert_after_text": "挿入位置の直前のHTMLテキスト",
        "diagram_code": "ここに作成したMarkdownの表、または <pre class='mermaid'>...</pre> を記述"
    }}
    """
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        print(f"  [Error] API呼び出しまたはJSONパースに失敗: {e}")
        return {"needs_diagram": False}

def main():
    # 既存の60記事が保存されているディレクトリ（現状の場所に合わせて設定）
    topics_dir = r"c:\Users\souhe\Desktop\論文まとめ\topics"
    
    if not os.path.exists(topics_dir):
        print(f"ディレクトリが見つかりません: {topics_dir}")
        return

    html_files = glob.glob(os.path.join(topics_dir, "**", "*.html"), recursive=True)
    if not html_files:
        print("HTMLファイルが見つかりませんでした。")
        return

    # 特定の未処理エラーファイルのみを対象とする（テスト用、現在は無効化）
    # html_files = [f for f in html_files if "産褥テタニー" in f or "ハイリスク患者の麻酔" in f]

    print(f"総計 {len(html_files)} 件の記事をチェックします...\n")

    for file_path in html_files:
        filename = os.path.basename(file_path)
        print(f"処理中: {filename} ... ", end="")
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 既にMermaid図解が挿入されているかチェック
        if 'class="mermaid"' in content:
            print("スキップ（既にMermaid図解が含まれています）")
            continue

        # 既存の図表コメント部分を削除（クリーンアップ）
        # content = re.sub(r'<!-- 個別生成図表 -->\n.*?</pre>\n\n', '', content, flags=re.DOTALL)

        # AIに判定・生成させる
        result = generate_diagram(content)

        if not result.get("needs_diagram"):
            print("図表追加は不要と判定")
            continue

        insert_text = result.get("insert_after_text", "")
        diagram_code = result.get("diagram_code", "")

        if not insert_text or not diagram_code:
            print("判定エラー: データが不完全です")
            continue
            
        # 安全対策: もしAIが余計なMarkdownブロック(```mermaid)をつけてしまった場合は除去する
        diagram_code = diagram_code.replace("```mermaid", "").replace("```html", "").replace("```", "").strip()

        # 挿入処理
        new_content = ""
        if insert_text in content:
            new_content = content.replace(insert_text, f"{insert_text}\n\n<!-- 個別生成図表 -->\n{diagram_code}\n\n")
        else:
            print(f"⚠️ 指定されたテキストが見つかりませんでした。フォールバック位置を使用します。")
            fallback_target = "<!-- ===== PREMIUM ZONE ===== -->"
            if fallback_target in content:
                new_content = content.replace(fallback_target, f"\n\n<!-- 個別生成図表 -->\n{diagram_code}\n\n" + fallback_target)
            else:
                fallback_target2 = "</header>"
                if fallback_target2 in content:
                    new_content = content.replace(fallback_target2, fallback_target2 + f"\n\n<!-- 個別生成図表 -->\n{diagram_code}\n\n")
                else:
                    print(f"❌ フォールバック位置も見つからなかったためスキップします。")
                    continue
            
        # HTMLプレビュー環境でMermaidを表示させるためのスクリプト読み込みを追加
        if "class=\"mermaid\"" in diagram_code and "<script type=\"module\"" not in new_content:
            mermaid_script = '\n<script type="module">import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs"; mermaid.initialize({ startOnLoad: true, securityLevel: "loose", theme: "default" });</script>\n'
            if '</body>' in new_content:
                new_content = new_content.replace('</body>', mermaid_script + '</body>')
            else:
                new_content += mermaid_script

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("✨ 図表を生成・挿入しました（完了）！")
            
if __name__ == "__main__":
    main()
