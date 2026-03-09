import os
import json
from sns_pipeline.core import extract_article_info, call_gemini

def generate_ig_slides_post(md_filepath):
    """
    Instagram向けカルーセル画像（最大10枚）用のテキスト台本とキャプションをGemini APIを用いて生成する
    """
    info = extract_article_info(md_filepath)
    title = info['title']
    content = info['content']
    target_animal = info['target_animal']
    
    animal_hashtag = f"#{target_animal}" if target_animal in ["犬", "猫"] else "#犬 #猫"

    prompt = f"""
以下の獣医学記事（Markdown形式）の内容をもとに、Instagramのカルーセル投稿用（画像10枚分）の【文字入れ用スライド台本】と【キャプション（投稿文）】を作成してください。
ターゲットは「臨床経験2〜3年目以上の獣医師」です。学術的正確性を保ちながら、スマホで読みやすい情報量（各スライドが長すぎないこと）に圧縮してください。

【記事本文】
{content[:5000]}... (省略)

【⚠️ 日本語表現の厳格なルール】
・「IV」「SC」「IM」「CRI」「PO」「BID」「SID」などの投与経路や頻度の略語は、臨床現場で広く使われているため**そのまま使用して構いません**（例: 0.5 mL/kg IV slow）。
・ただし「D50」「Dextrose」「Saline」「LRS」など、日本の現場で直感的に伝わりにくい英語略語や直訳語は避け、「50%ブドウ糖」「生理食塩水」「乳酸リンゲル液」などと**日本語に開いてください**。
・「Prednisolone」などの英語の薬剤名は使用せず、「プレドニゾロン」「グルカゴン」のように**必ずカタカナ表記**にしてください。
・「Take Home Message」や「CTA」などのマーケティング用語・横文字は完成テキストに含めず、「まとめ」「要点」など自然な日本語にしてください。

【スライド構成ルール】
画像を最大10枚想定し、各スライドのテキスト（Canva等のデザインツールで画像にそのまま貼り付ける文字）を作成してください。

[スライド構成の目安]
1枚目（表紙）: プロの目を引く学術的な問い・課題（例: 犬の急性下痢、メトロニダゾール出しすぎていませんか？）
2枚目（結論/フロー）: すぐに使える診断や治療の結論。
3〜8枚目（解説・データ）: 論文のデータ、推奨用量、禁忌などを箇条書きや表形式で。文字が多めになっても「プロなら拡大して読む・保存する」内容にする。
9枚目（まとめ）: 本記事の要点（まとめ）3点。
10枚目（読者へのアクション・誘導）: 「詳細なエビデンスと論文リンクはプロフのNoteにて。診察ですぐ見返せるよう【保存】を推奨します。」

【出力形式】
以下のような構造化されたフォーマット（プレーンテキスト）で出力してください。

=== Instagram スライド台本 ===
[1枚目: 表紙]
（キャッチコピー等のテキスト）

[2枚目: 結論]
（結論テキスト）

... 

[10枚目: 読者へのアクション・誘導]
（保存とNoteへの誘導）

=== キャプション（投稿文） ===
（投稿本文。ハッシュタグは 5〜8個程度で適切に付与）
【必須ハッシュタグ】: #獣医、#動物救急 を優先して入れること。
【禁止ハッシュタグ】: #獣医師、#救急医療、#獣医学生、#犬の病気、#猫の病気、#犬猫の病気 は絶対に使わないこと。
"""

    generated_text = call_gemini(prompt)
    if "エラー" in generated_text:
        return f"[エラー] Instagram用テキスト生成に失敗しました: {generated_text}"
    
    return generated_text

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(generate_ig_slides_post(sys.argv[1]))
    else:
        print("Usage: python generate_ig_slides.py <markdown_file_path>")
