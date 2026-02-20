import os
import re

files = [
    r"c:\Users\souhe\Desktop\論文まとめ\topics\救急\子癇_産後低Ca血症_救急対応.html",
    r"c:\Users\souhe\Desktop\論文まとめ\topics\循環器\犬のDCM_犬種別アプローチ.html",
    r"c:\Users\souhe\Desktop\論文まとめ\topics\腫瘍\肥満細胞腫_グレード別の治療判断.html",
    r"c:\Users\souhe\Desktop\論文まとめ\topics\眼科\緑内障の緊急対応_視覚を守る72時間.html",
    r"c:\Users\souhe\Desktop\論文まとめ\topics\救急\外傷の初期安定化_トリアージ.html",
    r"c:\Users\souhe\Desktop\論文まとめ\topics\歯科\猫の口内炎_全臼歯抜歯とステロイド以外の選択肢.html",
    r"c:\Users\souhe\Desktop\論文まとめ\topics\内分泌\犬猫の糖尿病_インスリン管理の実際.html",
    r"c:\Users\souhe\Desktop\論文まとめ\topics\麻酔\局所麻酔_神経ブロック_一般病院でできるテクニック.html"
]

output_file = r"c:\Users\souhe\Desktop\論文まとめ\review_bundle_8articles.md"

with open(output_file, 'w', encoding='utf-8') as outfile:
    outfile.write("# 記事校閲用バンドル（全8本）\n\n")
    outfile.write("AI（Google AI ウルトラ等）による一括校閲・推敲用のファイルです。\n")
    outfile.write("以下の8記事について、医学的な正確性、誤字脱字、表現の適切さ、トーン＆マナーの統一感を校閲してください。\n\n")
    outfile.write("---\n\n")

    for file in files:
        if os.path.exists(file):
            filename = os.path.basename(file)
            title = filename.replace('.html', '')
            outfile.write(f"## 記事: {title}\n\n")
            outfile.write("```html\n")
            with open(file, 'r', encoding='utf-8') as infile:
                content = infile.read()
                # body要素の中身だけを抽出（ヘッダー不要のため）
                body_match = re.search(r'<body.*?>(.*?)</body>', content, re.DOTALL | re.IGNORECASE)
                if body_match:
                    outfile.write(body_match.group(1).strip() + "\n")
                else:
                    outfile.write(content + "\n")
            outfile.write("```\n\n---\n\n")

print(f"Successfully created {output_file}")
