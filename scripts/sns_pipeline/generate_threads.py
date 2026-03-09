import os
from sns_pipeline.core import extract_article_info, call_gemini

def generate_threads_post(md_filepath):
    """
    Threads向け投稿テキストをGemini APIを用いて生成する
    """
    info = extract_article_info(md_filepath)
    title = info['title']
    content = info['content']
    category = info['category']
    tags = info['tags']
    
    # ジャンル判定: 救急かそれ以外かに応じてトーンを変える
    is_emergency = False
    if category == "救急" or "救急" in tags or "集中治療" in tags or "急変" in tags:
        is_emergency = True

    # スクリプト内でシステムに渡すプロンプト
    prompt = f"""
以下の獣医学記事（Markdown形式）の内容をもとに、Threads向けの**臨床獣医師向け専門的解説テキスト**を作成してください。

【記事本文】
{content[:5000]}... (省略)

【投稿の型とルール】
・ターゲットは「臨床経験2〜3年目以上の獣医師」です。
・専門用語を恐れずに使い、学術論文のディスカッションのような構成にしてください。
・長さは長文（300〜800文字程度）で読み応えを持たせます。
・ハッシュタグは最後に最も関連するものを **1つだけ**（例: #犬の急性下痢）付与してください。

【⚠️ 日本語表現の厳格なルール】
・「IV」「SC」「IM」「CRI」「PO」「BID」「SID」などの投与経路や頻度の略語は、臨床現場で広く使われているため**そのまま使用して構いません**（例: 0.5 mL/kg IV slow）。
・ただし「D50」「Dextrose」「Saline」「LRS」など、日本の現場で直感的に伝わりにくい英語略語や直訳語は避け、「50%ブドウ糖」「生理食塩水」「乳酸リンゲル液」などと**日本語に開いてください**。
・「Prednisolone」などの英語の薬剤名は使用せず、「プレドニゾロン」「グルカゴン」のように**必ずカタカナ表記**にしてください。
・「Take Home Message」などの海外特有の表現やマーケティング用語は使わず、自然な日本語にしてください。
"""

    if is_emergency:
        prompt += """
【救急ジャンル向けトーン（熱量高め・現場Tips重視）】
あなたは高度医療センターなどで働く熱意ある救急医として振る舞います。
以下の構成で書いてください。
1. **フック**: 記事のテーマについて、現場で直面するリアルな課題や最新ガイドラインでの変更点を熱く語る1行目。
2. **本文（解説・Tips）**: エビデンスの要点に加え、「筆者が現場で実際にやっている工夫」「ここで判断が分かれるポイント」「見落としがちなピットフォール（落とし穴）」といった【現場Tips】を意図的に創作・補完して、実践的に解説してください。
3. **締め**: 自然な一言で締めてください（例：「当たり前のことだけど、意外と見落とされがちなポイントだと思います。」など）。読者へのアグレッシブな質問（オープンクエスチョン）は**不要**です。
"""
    else:
        prompt += """
【非救急ジャンル向けトーン（淡白・要点特化）】
あなたは大学病院の専門医のように、冷静かつ淡々とエビデンスを提示するスタイルで書いてください。
以下の構成で書いてください。
1. **フック**: テーマの要点をズバリ提示する1行目。（例：「〇〇の初期治療で押さえるべきポイントを最新エビデンスからまとめました。」）
2. **本文（箇条書きベース）**: ガイドラインの要点、推奨用量、鑑別のポイントなどを箇条書きで分かりやすく整理してください。個人的な見解や熱量は排除し、客観的データのみを提示してください。
3. **締め**: 「詳細なエビデンスと論文リンクはNoteにて。」で誘導して終了。余計な語りや質問は**不要**です。
"""

    prompt += "\n\n上記の指示に従い、そのまま投稿できるテキストのみを出力してください。"

    generated_text = call_gemini(prompt)
    if "エラー" in generated_text:
        return f"[エラー] Threads用テキスト生成に失敗しました: {generated_text}"
    
    return generated_text

if __name__ == "__main__":
    # テスト実行用
    import sys
    if len(sys.argv) > 1:
        print(generate_threads_post(sys.argv[1]))
    else:
        print("Usage: python generate_threads.py <markdown_file_path>")
