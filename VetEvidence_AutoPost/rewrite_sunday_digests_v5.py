import os
import re

# AIのような「硬すぎる・画一的すぎる」表現を排除し、人間の獣医師（Dr. Sohey）が
# 実際にスマホやPCから打ち込んだような、自然で呼吸のある文章。
HUMAN_SUMMARIES = {
    "救急": "初期対応のスピードが生死を分けるため、迷わず病院に向かうべき基準をまとめました。",
    "腎泌尿器": "病気（ステージ）の進行度に合わせた適切な管理と、無理のないケアの落としどころについて。",
    "循環器": "早期発見がカギになる心疾患について、現在推奨されている治療の選択肢を解説しています。",
    "皮膚": "単なる対症療法で終わらせないための「根本原因」へのアプローチと、正しいスキンケアのお話。",
    "腫瘍": "腫瘍の振る舞いを正しく理解し、ご家族の価値観に合わせた「最適な治療方針」をどう決めるか。",
    "猫": "猫特有のデリケートな病態と、ストレスを最小限に抑える環境づくりの重要性について。",
    "神経": "発作などの緊急時にもパニックにならず、ご自宅でできる備えと正しい鑑別のステップです。",
    "栄養": "各種病態のステージに合わせた「食事療法」という最大の薬の使い方を解説しました。",
    "内分泌": "生涯にわたるお付き合いになるホルモン疾患の、診断の難しさと治療管理の基本について。",
    "輸液": "脱水への適切な輸液方法と、逆に命の危険を伴う「過剰投与」をいかに防ぐかというお話です。",
    "麻酔": "ハイリスクな子の麻酔の危険性をどう正確に評価し、安全性を高めていくかの工夫です。",
    "免疫": "免疫抑制薬のメリット・デメリットを正しく天秤にかけ、うまく付き合っていくための知識。",
    "歯科": "放置されがちな口腔内トラブルの適正な重症度評価と、痛みを和らげるための根本処置について。",
    "眼科": "視覚を守るための「タイムリミット」と、眼科救急において絶対に知っておくべき初期対応。",
    "整形外科": "歩き方の異常（跛行）の原因を見極め、外科手術と内科治療のどちらを選ぶべきかの比較です。",
    "血液ガス": "血液の数値を正しく読み解き、緊急時にどう補正して命を繋ぐかの実践的な内容です。",
    "血液": "貧血や電解質異常といった表面的な数値に惑わされず、大元の原因をどう探るかというアプローチ。",
    "消化器": "長引く消化器症状に対する正しい診断のステップと、最新の内科治療を中心としたアップデート。",
    "抗菌薬": "耐性菌を生み出さないために、「本当に抗生剤が必要なケース」をどう判断するかの基準です。",
    "その他": "日常の健康診断や予防医療など、身近だからこそ絶対に見落とせない分野の情報です。",
    "下痢": "とりあえずの「絶食」よりも「早期給餌」が推奨されつつある現在のトレンドと、食事管理のポイント。",
    "肝臓": "複雑になりやすい肝・胆道系の病態把握と、予後を改善するための積極的な内科・栄養サポートについて。"
}

CIRCLE_NUMBERS = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳㉑㉒㉓㉔㉕㉖㉗㉘㉙㉚㉛㉜㉝㉞㉟㊱"
week_map = {char: int(i+1) for i, char in enumerate(CIRCLE_NUMBERS)}

def get_mapping(category):
    for key, val in HUMAN_SUMMARIES.items():
        if key in category:
            return val
    return "対象疾患の最新のエビデンスと、ご家庭でのケアのポイントをまとめました。"

base_dir = r"c:\Users\souhe\Desktop\VetEvidence_SNS_Drafts"
folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]
weeks_data = {i: {} for i in range(1, 37)}

for f in folders:
    match = re.match(r"^([①-㊱])([月水金])_([^_]+)_(.+)$", f)
    if match:
        week_char, day, cat, title = match.groups()
        week_num = week_map[week_char]
        title_clean = title.replace(".md", "")
        weeks_data[week_num][day] = {
            "title": title_clean,
            "summary": get_mapping(cat)
        }

new_blocks = []
header = """# 🗓️ 日曜ダイジェスト 投稿用台本（全36週分）

これらのテキストは日曜日の昼などにNoteやX、Threadsの「まとめ投稿」としてお使いください。"""

for w in range(1, 37):
    day_order = ["月", "水", "金"]
    pattern_type = (w - 1) % 3
    
    if pattern_type == 0:
        # パターン1: 語りかけ・チーム医療志向（自然な導入）
        articles_text = ""
        connectors = ["いざという時に迷いやすい分野です。", "診察室でもご相談の多い領域ですね。", "現場のリアルをお伝えしています。"]
        idx = 0
        for d in day_order:
            if d in weeks_data[w]:
                obj = weeks_data[w][d]
                c = connectors[idx]
                articles_text += f"☑ {obj['title']}\n　{c}\n　→ {obj['summary']}\n\n"
                idx += 1
        
        week_text = f"""【今週の解説記事まとめ】
日々の診療お疲れ様です（ご家庭で毎日ケアをしてくださっている飼い主の皆さま、本当にありがとうございます）。
今週は、以下の3テーマについて解説しました。

{articles_text.strip()}

「少し様子を見てもいいのか、すぐに病院へ行くべきか」。そんな迷いが生じた時の判断材料としてお役立てください。
各エビデンスの詳しい解説は、プロフィールのNoteにまとめています。
#一次診療 #動物病院"""

    elif pattern_type == 1:
        # パターン2: 箇条書き・要点ハイライト志向（人間らしいマーク付き）
        articles_text = ""
        prefixes = ["💡ここがポイント：", "💡知っておきたい：", "💡大切なのは："]
        idx = 0
        for d in day_order:
            if d in weeks_data[w]:
                obj = weeks_data[w][d]
                p = prefixes[idx]
                articles_text += f"・{obj['title']}\n　{p}{obj['summary']}\n\n"
                idx += 1
                
        week_text = f"""【今週のエビデンス・振り返り】
今週は、診察室でご質問をいただくことが多い疾患を中心に深掘りしています。

{articles_text.strip()}

ネット上の不確かな情報ではなく、現在の一次診療で推奨されている基準をもとに解説しました。
ご自身やご家族の知識のアップデートに、よかったらプロフィールのNoteをのぞいてみてください。
#獣医 #獣医療アップデート"""

    else:
        # パターン3: インデックス・情報の整理志向（フラットだが温かい）
        articles_text = ""
        idx = 1
        for d in day_order:
            if d in weeks_data[w]:
                obj = weeks_data[w][d]
                articles_text += f"{idx}. {obj['title']}\n　（{obj['summary']}）\n"
                idx += 1
                
        week_text = f"""【今週公開した記事のまとめ】
今週更新したインデックスです。各リンクはプロフィールのNoteから飛べるようになっています。

{articles_text.strip()}

昔と今で少し治療方針が変わってきている領域も多いため、何となくの治療ではなく「なぜその選択をするのか（＝エビデンス）」を知るきっかけになれば嬉しいです。
該当する疾患でお悩みの方は、ぜひ一度ご一読ください。
#エビデンスに基づく獣医療"""

    block = f"## 第{w}週目 ({CIRCLE_NUMBERS[w-1]}週)\n\n```text\n{week_text.strip()}\n```\n"
    new_blocks.append(block)

final_content = header + "\n\n---\n\n" + "\n---\n\n".join(new_blocks)
out_path = os.path.join(base_dir, "all_sunday_digests.md")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(final_content)

print("Successfully humanized all 36 weeks and removed AI smell.")
