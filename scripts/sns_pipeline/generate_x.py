import os
import random
from sns_pipeline.core import extract_article_info, call_gemini

def generate_x_post(md_filepath, pattern=None):
    """
    X向け投稿テキストをGemini APIを用いて生成する
    pattern: 1(昔vs今), 2(結論ファースト), 3(数字で驚かせる)。Noneの場合はランダム
    """
    info = extract_article_info(md_filepath)
    title = info['title']
    content = info['content']
    target_animal = info['target_animal']
    
    if pattern is None:
        pattern = random.choice([1, 2, 3])
        
    animal_hashtag = f"#{target_animal}" if target_animal in ["犬", "猫"] else "#犬 #猫"

    prompt = f"""
以下の獣医学記事（Markdown形式）の内容をもとに、X（旧Twitter）向けの**臨床獣医師向け**の投稿テキストを作成してください。

【記事本文】
{content[:3000]}... (省略)

【投稿の型とルール】
あなたは指定されたパターン {pattern} に従ってテキストを作成します。文字数は最大でも140字〜200字程度（Xで読みやすい長さ）に収めてください。

・ターゲットは「臨床経験2〜3年目以上の獣医師」です。「〜すべき」といった断定は避け、「〜が推奨されている」「〜を考慮する」といった学術的でフラットなトーンにしてください。
・ハッシュタグは本文の最後に追加してください。最大2〜3個まで。
【ハッシュタグの厳格なルール】
・「#獣医」「#動物救急」を優先的に使用してください。
・「#獣医師」「#救急医療」「#獣医学生」「#犬の病気」「#猫の病気」「#犬猫の病気」などのタグは絶対に使用しないでください。
・最も関連する疾患名（例: #急性下痢）を追加で1つ付与するのは構いません。

【⚠️ 日本語表現の厳格なルール】
・「IV」「SC」「IM」「CRI」「PO」「BID」「SID」などの投与経路や頻度の略語は、臨床現場で広く使われているため**そのまま使用して構いません**（例: 0.5 mL/kg IV slow）。
・ただし「D50」「Dextrose」「Saline」「LRS」など、日本の現場で直感的に伝わりにくい英語略語や直訳語は避け、「50%ブドウ糖」「生理食塩水」「乳酸リンゲル液」などと**日本語に開いてください**。
・「Prednisolone」などの英語の薬剤名は使用せず、「プレドニゾロン」「グルカゴン」のように**必ずカタカナ表記**にしてください。
・「Take Home Message」や「CTA」などの横文字/マーケティング用語は使わず、「まとめ」「要点」など自然な日本語にしてください。

【パターン別テンプレート】
"""
    
    if pattern == 1:
        prompt += f"""
パターン1：「昔の常識 vs 今」型
※1行目は必ず「疾患名・病態名」を含むフックにすること。

[1行目: 疾患名を含むフック。例: 犬の急性下痢 ─ メトロニダゾールの再考]

❌ 昔: [記事から読み取れる旧来の常識や一般的な誤解を簡潔に]
✅ 今: [記事が主張する最新のエビデンスや推奨事項を簡潔に]

📄 根拠: [記事内に特定の論文があれば著者名と年、なければ最新ガイドライン等の出典を記載]
"""
    elif pattern == 2:
        prompt += f"""
パターン2：「結論ファースト」型
※1行目は必ず「疾患名・病態名」を含むフックにすること。

[1行目: 疾患名を含むフック。例: 猫のCKD ─ IRISステージ別管理の要点]

[記事の最も重要な結論や、臨床で即役立つガイドラインの推奨事項を1〜2文で]

詳しくは Note で（プロフにリンク）
"""
    elif pattern == 3:
        prompt += f"""
パターン3：「数字で驚かせる」型
※1行目は固定。2行目にインパクトのある数字。

📊 知ってましたか？

[記事の中から、獣医師にとって意外性やインパクトのある「数字・パーセンテージ・期間・生存率・用量」等のデータを1つ提示]

[その数字に関する補足説明や臨床的意義を1〜2文で]

※もし記事内に強調すべき具体的な「数字」や「統計データ」が含まれていない場合は、無理に生成せず、「※この記事にはパターン3（数字）に該当する強力なデータがありません」と1文だけ出力してください。
"""

    prompt += "\n\n上記の指示に従い、テンプレートの[ ]部分を記事内容から抽出・要約して埋め、そのまま投稿できるテキストのみを出力してください。"

    generated_text = call_gemini(prompt)
    if "エラー" in generated_text:
        return f"[エラー] X用テキスト生成に失敗しました: {generated_text}"
    
    return generated_text

if __name__ == "__main__":
    # テスト実行用
    import sys
    if len(sys.argv) > 1:
        print(generate_x_post(sys.argv[1]))
    else:
        print("Usage: python generate_x.py <markdown_file_path>")
