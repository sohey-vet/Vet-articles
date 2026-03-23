import os
import glob
import re
import urllib.parse
import difflib

# omitting the lengthy string parsing for brevity, I'll rewrite the whole file
USER_INPUT = """
メチシリン耐性菌（MRSA/MRSP）─ 対策と治療	その他　　感染症
健康診断の最適化 ─ 推奨項目	その他	予防医療　
手作り食・生食のリスクとエビデンス	その他	栄養
犬猫の膀胱炎 ─ 本当に抗菌薬が必要か？	腎泌尿器　　抗菌薬
肥満管理 ─ 減量プログラムの実際	その他　　栄養
犬猫の中毒 ─ 初期対応と活性炭の限界		救急　　中毒
犬のITP ─ 診断と治療	血液　　免疫　　救急
免疫介在性溶血性貧血（IMHA）─ 診断と初期治療　　血液　　免疫　　救急
犬猫の糖尿病 ─ インスリン管理の実際	内分泌	猫　糖尿病
猫の喘息 ─ 犬との違いと吸入療法	呼吸器	猫　救急
不整脈の救急対応 ─ 心電図の読み方	循環器	救急　心電図
心嚢水・心タンポナーデ ─ 心嚢穿刺の実際		救急　　循環器　　心エコー
犬種別スクリーニング	　その他
猫の動脈血栓塞栓症（ATE）─ 救急対応	救急　　循環器	猫　　心エコー
心原性肺水腫 ─ 一般病院での救命Tips	　　救急　　循環器　　心エコー
FIP（猫伝染性腹膜炎）─ 抗ウイルス薬時代の治療	　　救急　　感染症	猫
周術期の抗菌薬 ─ 予防投与のタイミング	　　その他　　抗菌薬　　感染症　　外科
DIC ─ 診断と治療	　救急	血液
GDV ─ 安定化と手術判断	救急　　外科　　輸液
急性腎障害（AKI）の初期対応	救急　　腎泌尿器　　輸液
敗血症の早期認識と初期蘇生 ─ 「1時間以内」が生死を分ける	　救急　　輸液　　感染症　　抗菌薬
溺水・煙吸入 ─ 肺損傷の管理	　救急	呼吸器
熱中症 ─ エビデンスベースの冷却法	救急
犬の慢性腸症（CE）─ 2025年最新「診断カスケード」の実践	救急　　消化器・肝臓
犬猫の中毒 ─ よくある原因物質と初期対応の限界	救急　　中毒
猫のDKA ─ 糖尿病性ケトアシドーシス緊急管理	　救急	内分泌　猫　輸液　電解質
緑内障の緊急対応 ─ 視覚を守る72時間	　　眼科　　救急
難産と帝王切開 ─ 救急対応と新生子蘇生フロー	救急　　外科
電解質異常の緊急対応 ─ K・Ca	血液　　救急　電解質　輸液
高カリウム血症 ─ 致死的不整脈の回避と段階的アプローチ	　血液　　救急	輸液　　電解質
高ナトリウム血症 ─ 原因の究明と「水脱水」への安全なアプローチ	　血液　　救急	輸液　　電解質
低血糖の緊急管理 ─ インスリノーマ含む	救急	　内分泌
輸血のベストプラクティス ─ 一般病院で安全に実施するために	血液　　救急
猫の三臓器炎 ─ 胆管炎・膵炎・IBD	　猫　	消化器・肝臓
猫の肥大型心筋症（HCM）─ 早期発見と管理	猫	　循環器　　心エコー
猫の胸水 ─ 原因鑑別と胸腔穿刺	　猫	　　救急　　
猫の多頭飼育ストレス ─ 環境エンリッチメントのエビデンス	猫
FLUTD ─ 閉塞vs非閉塞の対応：救急から長期管理まで	　救急　　腎泌尿器　　猫
猫の行動学 ─ 不適切排泄・攻撃性の医学的原因	　猫
アポキルvsサイトポイントvsステロイド ─ 犬のアトピー性皮膚炎の痒み管理	皮膚
マラセチア皮膚炎 ─ 再発防止戦略	　皮膚
食物アレルギーの除去食試験 ─ 正しいやり方	　皮膚	免疫
犬のアトピー性皮膚炎 ─ 最新治療薬比較	　　皮膚　　免疫
てんかんの長期管理 ─ 抗てんかん薬の選択	神経
発作の初期対応 ─ 頭蓋内疾患を疑うとき	　　救急　　神経
脊髄軟化症・変形性関節症・DM	神経
猫の脂肪肝 ─ 強制給餌と栄養管理	　　猫	栄養
尿石症 ─ 種類別の治療・食事療法	　　腎泌尿器　　栄養
尿管結石・尿管閉塞 ─ 診断と治療の実際	腎泌尿器
急性腎障害 vs 慢性腎臓病 ─ 鑑別と初期対応	腎泌尿全器	　　救急　　輸液
犬猫の膀胱炎 ─ ISCAIDガイドライン準拠	腎泌尿器	抗菌薬
猫の特発性膀胱炎（FIC）─ ストレス管理を含む最新治療	　　腎泌尿器　　猫
蛋白尿の評価と治療介入のタイミング	腎泌尿器
腎臓病の食事療法 ─ リン制限とカリウム管理	腎泌尿器	　　栄養
猫の慢性腎臓病（CKD）─ IRISステージ別管理	腎泌尿器
リンパ腫 ─ 犬と猫の違い・治療プロトコル	腫瘍　　血液
肥満細胞腫 ─ グレード別の治療判断	腫瘍
血管肉腫 ─ 脾臓・心臓型の管理と予後	腫瘍	救急
扁平上皮癌と移行上皮癌 ─ 診断・治療セット	腫瘍
血液ガス分析の基本 ─ 3ステップ判読法	　血液
ショック時の輸液戦略 ─ ボーラス投与の実際	救急　　輸液
周術期の輸液管理 ─ 術中・術後の最適化	麻酔　　輸液
短頭種症候群（BOAS）─ 周術期管理の実際	　　麻酔	　外科
鎮静プロトコルの比較 ─ 処置別の最適な組み合わせ	麻酔
"""

def parse_user_input():
    parsed = []
    lines = USER_INPUT.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # Exception handling first
        if "免疫介在性溶血性貧血（IMHA）─ 診断と初期治療" in line:
            title = "免疫介在性溶血性貧血（IMHA）─ 診断と初期治療"
            tags = ["血液", "免疫", "救急"]
        else:
            if '\t' in line:
                parts = [p.strip() for p in line.split('\t') if p.strip()]
            else:
                parts = [p.strip() for p in re.split(r'[ \u3000]+', line) if p.strip()]
            
            if not parts: continue
            
            title = parts[0]
            raw_tags = " ".join(parts[1:]).replace('　', ' ')
            tags = [t.strip() for t in raw_tags.split() if t.strip()]
            
        tags = [t.replace('腎泌尿全器', '腎泌尿器').replace('消化器・肝臓', '消化器') for t in tags]
        
        if tags:
            parsed.append((title, tags[0], tags[1:]))
            
    return parsed

def get_html_paths(repo_dir):
    return glob.glob(os.path.join(repo_dir, "topics", "**", "*.html"), recursive=True)

def update_tags_in_markdown(md_file, new_tags):
    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    if re.search(r'tags:\s*\[.*?\]', content):
        tag_str = ", ".join(new_tags)
        content = re.sub(r'tags:\s*\[.*?\]', f'tags: [{tag_str}]', content)
    elif re.search(r'TAGS\n.*?\n', content):
        tag_str = " ".join(new_tags)
        content = re.sub(r'TAGS\n.*?\n', f'TAGS\n{tag_str}\n', content)
    else:
        content += f"\n\n---\ntags: [{', '.join(new_tags)}]\n"
        
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(content)

def update_tags_in_html(html_file, tags):
    with open(html_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    tags_section_match = re.search(r'(<div class="tags"[^>]*>)(.*?)(</div>)', content, re.DOTALL)
    if tags_section_match:
        new_tags_html = ""
        for g in tags:
            if not g: continue
            css_class = "tag--secondary" if g == "その他" else "tag--primary"
            if g in ["皮膚", "皮膚科", "外科", "整形外科"]: css_class = "tag--warning"
            elif g in ["猫", "猫専門", "犬"]: css_class = "tag--success"
            
            encoded_q = urllib.parse.quote(g)
            new_tags_html += f'<a class="tag {css_class}" href="../../index.html?tag={encoded_q}">{g}</a>'
            
        content = content[:tags_section_match.start(2)] + "\n" + new_tags_html + "\n" + content[tags_section_match.end(2):]
        
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(content)

def main():
    repo_dir = r"C:\Users\souhe\Desktop\論文まとめ"
    parsed_rules = parse_user_input()
    
    html_files = get_html_paths(repo_dir)
    basenames = [os.path.basename(hf).replace('.html', '') for hf in html_files]
    
    found_count = 0
    missing = []
    
    for title, main_tag, sub_tags in parsed_rules:
        all_tags = [main_tag] + sub_tags
        
        clean_title = title.split('─')[0].strip()
        matches = difflib.get_close_matches(clean_title, basenames, n=1, cutoff=0.3)
        
        if matches:
            best_base = matches[0]
            matched_html = [hf for hf in html_files if best_base in hf][0]
            found_count += 1
            print(f"Matched: {title[:15]} => {best_base}")
            
            update_tags_in_html(matched_html, all_tags)
            
            md_file = matched_html.replace('.html', '.md')
            if os.path.exists(md_file):
                update_tags_in_markdown(md_file, all_tags)
        else:
            missing.append(title)
            print(f"FAILED: {title}")

    print(f"\nSynchronized {found_count}/{len(parsed_rules)} articles.")

if __name__ == "__main__":
    main()
