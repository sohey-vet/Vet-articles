import re
import os

filepath = r"c:\Users\souhe\Desktop\VetEvidence_SNS_Drafts\all_sunday_digests.md"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

new_blocks = []
blocks = re.split(r"---+\s+##", content)
header = blocks[0]

for idx, block in enumerate(blocks[1:]):
    week_match = re.search(r"(第\d+週目 \([^)]+\))", block)
    week_title = week_match.group(1) if week_match else f"第{idx+1}週目"
    
    articles = []
    
    # 既存のフォーマットから記事名を抽出（前のスクリプトで書き換わっているため再対応）
    # ■ または ・ または ①②③ などの行を取り出す
    if "■" in block:
        articles = re.findall(r"■\s*(.+)", block)
    elif "・月曜：" in block:
        m1 = re.search(r"・月曜：(.+)", block)
        m2 = re.search(r"・水曜：(.+)", block)
        m3 = re.search(r"・金曜：(.+)", block)
        if m1 and m2 and m3:
            articles = [m1.group(1), m2.group(1), m3.group(1)]
    elif "・ " in block: # Template C or D
        lines = re.findall(r"・\s([^月水金].+)", block)
        if len(lines) >= 3:
            articles = lines[:3]
    elif "①" in block:
        m1 = re.search(r"①\s*(.+)", block)
        m2 = re.search(r"②\s*(.+)", block)
        m3 = re.search(r"③\s*(.+)", block)
        if m1 and m2 and m3:
            articles = [m1.group(1), m2.group(1), m3.group(1)]
            
    if len(articles) < 3:
        print(f"Error extracting articles for {week_title}. Block:\n{block}")
        continue
        
    a1, a2, a3 = articles[0], articles[1], articles[2]
    
    pattern_idx = idx % 5
    
    if pattern_idx == 0:
        new_text = f"""【今週の獣医学メソッド・まとめ】
今週は、日々の診療でお伝えする機会が多い、以下の3つの疾患・テーマについて解説しました。

■ {a1}
■ {a2}
■ {a3}

特に「{a2}」については、ご家庭での気付きや協力が治療の鍵となる領域でもあります。
各記事の詳しい解説は、プロフィールのNoteから読むことができます。ご自宅での愛犬・愛猫のケアにお役立てください。
#獣医 #獣医療アップデート"""
    elif pattern_idx == 1:
        new_text = f"""【週間ダイジェスト：獣医療のエビデンス】
今週のNoteでは、治療におけるエビデンス（医学的根拠）をテーマに以下の3記事を公開しました。

・月曜：{a1}
・水曜：{a2}
・金曜：{a3}

「{a3}」などのトピックは、実際の診療でもよくご質問をいただく内容です。基礎知識としてご活用いただけるようまとめています。
各記事の詳細は、プロフィールのNoteよりご確認ください。
#一次診療 #動物病院 #獣医学"""
    elif pattern_idx == 2:
        new_text = f"""【今週の解説記事・振り返り】
今週は、以下の3つのテーマについて解説記事を公開しています。

・ {a1}
・ {a2}
・ {a3}

「{a1}」に関しては、治療方針のトレンドが近年変化している分野でもあります。古い情報のままになっていないか、ぜひ一度知識をアップデートしてみてください。
詳細はプロフィールのNoteにて公開しています。
#獣医師 #獣医療情報"""
    elif pattern_idx == 3:
        new_text = f"""【獣医学エビデンス・今週のまとめ】
今週更新した、以下の3テーマに関する記事のまとめです。

・ {a1}
・ {a2}
・ {a3}

「{a1}」や「{a3}」のように、ご自宅での日常的な観察が早期発見に繋がる疾患も少なくありません。
各疾患のメカニズムや推奨される対応については、プロフィールのNoteをご覧ください。少しでもご不安の解消に繋がれば幸いです。
#獣医療エビデンス #動物病院"""
    else:
        new_text = f"""【週間エビデンスピックアップ】
今週解説した主要な獣医療トピックは以下の3つです。

① {a1}
② {a2}
③ {a3}

動物病院で提示される検査や治療の意味を理解することは、動物たちにとっての「最善の選択」に近づく第一歩です。
参考になりそうなトピックがありましたら、プロフィールのNoteからぜひ詳細をお読みください。
#獣医 #獣医療アップデート"""

    block_text = f"## {week_title}\n\n```text\n{new_text}\n```\n"
    new_blocks.append(block_text)

final_content = header.rstrip() + "\n\n---\n\n" + "\n---\n\n".join(new_blocks)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(final_content)

print("Successfully un-cheesified all 36 weeks.")
