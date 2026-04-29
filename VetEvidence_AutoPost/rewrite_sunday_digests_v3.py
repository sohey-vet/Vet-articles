import os
import re

# カテゴリ別の具体的な1行ハイライト（Dr. Sohey スタイル）
CATEGORY_SUMMARIES = {
    "救急": "救急時の判断基準と、命を救うための迅速な初期対応について解説しています。",
    "腎泌尿器": "腎・泌尿器疾患における適切な病期分類（ステージング）と管理方法をまとめています。",
    "循環器": "心疾患の早期発見のポイントと、エビデンスに基づく最新の治療選択肢について。",
    "皮膚": "再発しやすい皮膚疾患の根本原因と、ご家庭でできる正しいケア管理のアプローチ。",
    "腫瘍": "各悪性腫瘍の振る舞いと、ご家族と決定していく最適な治療方針の考え方。",
    "猫": "猫特有の病態メカニズムと、見逃しがちなサイン、ストレスに配慮した対応策。",
    "神経": "神経症状の正しい鑑別と、発作などの緊急時におけるご自宅での備えについて。",
    "栄養": "各疾患のステージや状態に合わせた、最新エビデンスに基づく食事・栄養管理の原則。",
    "内分泌": "複雑なホルモン疾患の診断の落とし穴と、生涯にわたる治療管理の基本。",
    "輸液": "脱水やショック状態に対する適切な輸液選択と、過剰投与のリスク管理について。",
    "麻酔": "ハイリスク症例における麻酔のリスク評価と、より安全な周術期管理の工夫。",
    "免疫": "免疫介在性疾患の診断プロセスと、免疫抑制薬のベネフィットとリスク。",
    "歯科": "放置されがちな歯科疾患の重症度評価と、痛みを伴う口腔内トラブルの適切な処置。",
    "眼科": "視覚喪失を防ぐためのタイムリミットと、眼科救急における初期治療の鉄則。",
    "整形外科": "跛行（歩行異常）の原因となる疾患の鑑別と、外科・内科的アプローチの比較。",
    "血液ガス": "命に関わる血液異常・酸塩基平衡の評価と、緊急時における補正の考え方。",
    "血液": "貧血や電解質異常の正しい評価と、疾患に合わせた原因追及のアプローチ。",
    "消化器": "慢性的な消化器症状に対する診断ステップと、食事・内科治療のアップデート。",
    "抗菌薬": "耐性菌を防ぐための適正使用と、本当に抗菌薬が必要なケースの判断基準。",
    "その他": "日常の予防医療や健康診断など、身近でありながら重要な分野のアップデート。",
    "下痢": "消化管トラブルにおける最新の治療トレンドと、ご家庭での食事管理のポイント。",
    "肝臓": "肝・胆道系疾患の複雑な病態と、内科管理および栄養サポートの重要性について。"
}

CIRCLE_NUMBERS = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳㉑㉒㉓㉔㉕㉖㉗㉘㉙㉚㉛㉜㉝㉞㉟㊱"
week_map = {char: int(i+1) for i, char in enumerate(CIRCLE_NUMBERS)}

def get_summary(category):
    for key, val in CATEGORY_SUMMARIES.items():
        if key in category:
            return val
    return "該当疾患の最新のエビデンスと、臨床現場での実践的なアプローチについて解説しています。"

base_dir = r"c:\Users\souhe\Desktop\VetEvidence_SNS_Drafts"
folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]

weeks_data = {i: {} for i in range(1, 37)}

for f in folders:
    # フォルダ形式例: ①月_下痢_犬の急性下痢_最新エビデンス
    match = re.match(r"^([①-㊱])([月水金])_([^_]+)_(.+)$", f)
    if match:
        week_char, day, cat, title = match.groups()
        week_num = week_map[week_char]
        title_clean = title.replace(".md", "")
        summary = get_summary(cat)
        
        weeks_data[week_num][day] = {
            "title": title_clean,
            "summary": summary
        }

# マージして all_sunday_digests.md を再編
new_blocks = []
header = """# 🗓️ 日曜ダイジェスト 投稿用台本（全36週分）

これらのテキストは日曜日の昼などにNoteやX、Threadsの「まとめ投稿」としてお使いください。"""

for w in range(1, 37):
    day_order = ["月", "水", "金"]
    
    articles_text = ""
    for d in day_order:
        if d in weeks_data[w]:
            obj = weeks_data[w][d]
            articles_text += f"■ {obj['title']}\n　→ {obj['summary']}\n"
    
    # 300-400文字に収めるDr. Sohey スタイルのフォーマット
    # 変なテンプレート化を避け、すべて一貫したプロフェッショナルな表現に統一
    week_text = f"""【今週の獣医療エビデンスまとめ】
今週は、日々の診療において重要な以下の3つのテーマについて解説記事を公開しました。

{articles_text}
これらの知識は、動物病院から提案される検査や治療の意図を理解し、より良い選択をするための大きな助けとなります。
各疾患のメカニズムや推奨される対応の詳細については、プロフィールのNoteよりご確認ください。
#獣医 #獣医療アップデート #一次診療 #動物病院"""

    block = f"## 第{w}週目 ({CIRCLE_NUMBERS[w-1]}週)\n\n```text\n{week_text.strip()}\n```\n"
    new_blocks.append(block)

final_content = header + "\n\n---\n\n" + "\n---\n\n".join(new_blocks)

out_path = os.path.join(base_dir, "all_sunday_digests.md")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(final_content)

print("Successfully generated full semantic summaries for all 36 weeks.")
