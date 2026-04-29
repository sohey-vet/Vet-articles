import os
import re
from collections import Counter

# 各疾患のフラットで専門的な要約（AI臭、定型句、小芝居を完全排除）
HUMAN_SUMMARIES = {
    "救急": "初期対応のスピードが生死を分けるため、急を要する基準と対応をまとめました。",
    "腎泌尿器": "病気（ステージ）の進行度に合わせた適切な管理と、長期ケアの落としどころについて。",
    "循環器": "早期発見がカギになる心疾患について、現在推奨されている治療の選択肢を解説しています。",
    "皮膚": "単なる対症療法で終わらせないための「根本原因」へのアプローチとスキンケアの原則。",
    "腫瘍": "腫瘍の振る舞いを正しく理解し、価値観に合わせた「最適な治療方針」を決定するプロセス。",
    "猫": "猫特有のデリケートな病態と、ストレスを最小限に抑える環境づくりの重要性について。",
    "神経": "発作などの緊急時にもパニックにならず、ご自宅でできる備えと正しい鑑別のステップ。",
    "栄養": "各種病態のステージに合わせた「食事療法」という最大の薬の使い方を解説しました。",
    "内分泌": "生涯にわたる治療管理が必要になるホルモン疾患の、診断の難しさと治療の基本について。",
    "輸液": "脱水への適切な輸液方法と、逆に命の危険を伴う「過剰投与」をいかに防ぐかというロジック。",
    "麻酔": "ハイリスクな症例において、麻酔の危険性をどう正確に評価し、安全性を高めていくかの工夫。",
    "免疫": "免疫抑制薬のメリット・デメリットを正しく天秤にかけ、うまく付き合っていくための知識。",
    "歯科": "放置されがちな口腔内トラブルの適正な重症度評価と、痛みを和らげるための根本処置について。",
    "眼科": "視覚を守るための「タイムリミット」と、眼科救急において絶対に知っておくべき初期対応。",
    "整形外科": "跛行（歩き方の異常）の原因を見極め、外科と内科治療のどちらを選ぶべきかの比較。",
    "血液ガス": "血液の数値を正しく読み解き、緊急時にどう補正して命を繋ぐかの実践的な内容。",
    "血液": "貧血や電解質異常といった表面的な数値に惑わされず、大元の原因をどう探るかというアプローチ。",
    "消化器": "長引く消化器症状に対する正しい診断のステップと、最新の内科治療を中心としたアップデート。",
    "抗菌薬": "耐性菌を生み出さないために、「本当に抗生剤が必要なケース」をどう判断するかの基準。",
    "その他": "日常の健康診断や予防医療など、身近だからこそ絶対に見落とせない分野の情報です。",
    "下痢": "とりあえずの「絶食」よりも「早期給餌」が推奨されつつある現在のトレンドと、食事管理のポイント。",
    "肝臓": "複雑になりやすい肝・胆道系の病態把握と、予後を改善するための積極的な内科・栄養サポート。"
}

# 記事のテーマを分析して最適なフォーマット（4, 5, 6）を決定するためのカテゴリ分類
P4_RATIONALE = ["腫瘍", "皮膚", "栄養", "内分泌", "免疫", "抗菌薬", "下痢"]
P5_OVERVIEW = ["消化器", "腎泌尿器", "歯科", "整形外科", "猫", "その他", "肝臓"]
P6_TRIAGE = ["救急", "循環器", "輸液", "血液ガス", "麻酔", "血液", "神経", "眼科"]

CIRCLE_NUMBERS = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳㉑㉒㉓㉔㉕㉖㉗㉘㉙㉚㉛㉜㉝㉞㉟㊱"
week_map = {char: int(i+1) for i, char in enumerate(CIRCLE_NUMBERS)}

def get_summary(category):
    for key, val in HUMAN_SUMMARIES.items():
        if key in category:
            return val
    return "該当疾患の医学的エビデンスと、臨床現場での実践的なアプローチについて解説しています。"

def identify_pattern(categories):
    counts = {4: 0, 5: 0, 6: 0}
    for cat in categories:
        matched = False
        for k in P4_RATIONALE:
            if k in cat: counts[4] += 1; matched = True; break
        if matched: continue
        for k in P5_OVERVIEW:
            if k in cat: counts[5] += 1; matched = True; break
        if matched: continue
        for k in P6_TRIAGE:
            if k in cat: counts[6] += 1; matched = True; break
        if not matched: counts[5] += 1 # default to 5
    
    # 多数決で決定。同点の場合は汎用性の高い5を優先
    max_count = max(counts.values())
    candidates = [k for k, v in counts.items() if v == max_count]
    if 5 in candidates: return 5
    if 6 in candidates: return 6
    return 4

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
            "category": cat,
            "summary": get_summary(cat)
        }

new_blocks = []
header = """# 🗓️ 日曜ダイジェスト 投稿用台本（全36週分）

これらのテキストは日曜日の昼などにNoteやX、Threadsの「まとめ投稿」としてお使いください。"""

for w in range(1, 37):
    day_order = ["月", "水", "金"]
    
    # 記事が3つ揃っていない場合はスキップ等（基本的に揃っている）
    articles_cats = [weeks_data[w][d]["category"] for d in day_order if d in weeks_data[w]]
    pattern = identify_pattern(articles_cats)
    
    week_text = ""
    articles_text = ""
    
    if pattern == 4:
        for d in day_order:
            if d in weeks_data[w]:
                obj = weeks_data[w][d]
                articles_text += f"☑ {obj['title']}\n　{obj['summary']}\n"
                
        week_text = f"""【今週の獣医療コラム：治療の根拠を知る】
「なぜその検査や治療が必要なのか」。その背景にある医学的エビデンスを解説しました。

{articles_text.rstrip()}

治療の意図を正確に把握することで、より前向きに治療に参加いただけるはずです。該当疾患の詳しい解説については、プロフィールのリンク先（Note）をお役立てください。
#一次診療 #獣医学"""
                
    elif pattern == 5:
        for d in day_order:
            if d in weeks_data[w]:
                obj = weeks_data[w][d]
                articles_text += f"・{obj['title']}\n　{obj['summary']}\n"
                
        week_text = f"""【今週公開の獣医学解説・インデックス】
今週は、以下の3つの疾患・テーマを取り上げ、病態のメカニズムと対応策をまとめました。

{articles_text.rstrip()}

複雑な病気であっても、原理原則を知ることで見方が変わります。一次診療の現場で基準としているガイドラインやエビデンスの詳細は、プロフィールのNoteをご覧ください。
#エビデンスに基づく獣医療 #獣医"""

    elif pattern == 6:
        for d in day_order:
            if d in weeks_data[w]:
                obj = weeks_data[w][d]
                articles_text += f"■ {obj['title']}\n　{obj['summary']}\n"
                
        week_text = f"""【週間ダイジェスト：症状への正しいアプローチ】
様子を見るべきか、一刻も早く動物病院を受診すべきか。今週はその判断の助けとなる3記事を公開しました。

{articles_text.rstrip()}

誤った自己判断は時に取り返しのつかない結果を招きます。基準となる確かな一次情報については、プロフィールのNoteより各解説記事をご参照ください。
#獣医 #獣医療情報"""

    block = f"## 第{w}週目 ({CIRCLE_NUMBERS[w-1]}週)\n\n```text\n{week_text}\n```\n"
    new_blocks.append(block)

final_content = header + "\n\n---\n\n" + "\n---\n\n".join(new_blocks)
out_path = os.path.join(base_dir, "all_sunday_digests.md")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(final_content)

print("Successfully replaced with pattern 4, 5, and 6 dynamically mapped to content.")
