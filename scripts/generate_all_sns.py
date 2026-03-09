#!/usr/bin/env python3
import os
import sys
import datetime
import subprocess

# sns_pipelineモジュールをインポートするためにパスを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sns_pipeline.generate_x import generate_x_post
from sns_pipeline.generate_threads import generate_threads_post
from sns_pipeline.generate_ig_slides import generate_ig_slides_post

# ── 丸数字マッピング (1〜35) ──
CIRCLED_NUMBERS = {
    1: "①", 2: "②", 3: "③", 4: "④", 5: "⑤",
    6: "⑥", 7: "⑦", 8: "⑧", 9: "⑨", 10: "⑩",
    11: "⑪", 12: "⑫", 13: "⑬", 14: "⑭", 15: "⑮",
    16: "⑯", 17: "⑰", 18: "⑱", 19: "⑲", 20: "⑳",
    21: "㉑", 22: "㉒", 23: "㉓", 24: "㉔", 25: "㉕",
    26: "㉖", 27: "㉗", 28: "㉘", 29: "㉙", 30: "㉚",
    31: "㉛", 32: "㉜", 33: "㉝", 34: "㉞", 35: "㉟",
}

# ── NEW_CONTENT_PLAN_DRAFT.md に基づくスケジュールマッピング ──
# key = 記事ファイル名のベース（拡張子なし）の一部, value = (週番号, 曜日)
SCHEDULE_MAP = {
    "犬の急性下痢": (1, "月"), "猫のCKD": (1, "水"), "心原性肺水腫": (1, "金"),
    "中毒": (2, "月"), "抗菌薬選択の基本原則": (2, "水"), "IMHA": (2, "金"),
    "ショック管理": (3, "月"), "猫のHCM": (3, "水"), "椎間板ヘルニア": (3, "金"),
    "FIP": (4, "月"), "輸液の基本": (4, "水"), "リンパ腫": (4, "金"),
    "CPR": (5, "月"), "猫の胸水": (5, "水"), "僧帽弁閉鎖不全症": (5, "金"),
    "急性膵炎": (6, "月"), "免疫介在性血小板減少症": (6, "水"), "敗血症": (6, "金"),
    "FLUTD": (7, "月"), "尿石症": (7, "水"), "療法食の選び方": (7, "金"),
    "外耳炎": (8, "月"), "クッシング症候群": (8, "水"), "麻酔モニタリング": (8, "金"),
    "血液ガス分析": (9, "月"), "膀胱炎": (9, "水"), "アトピー性皮膚炎": (9, "金"),
    "ショック時の輸液戦略": (10, "月"), "GDV": (10, "水"), "ピモベンダン": (10, "金"),
    "尿道閉塞": (11, "月"), "維持輸液": (11, "水"), "不整脈": (11, "金"),
    "蛋白尿": (12, "月"), "脂肪肝": (12, "水"), "ハイリスク患者の麻酔": (12, "金"),
    "DIC_診断": (13, "月"), "発作の初期対応": (13, "水"), "心臓病と麻酔": (13, "金"),
    "マラセチア": (14, "月"), "急性腎障害": (14, "水"), "三臓器炎": (14, "金"),
    "血管肉腫": (15, "月"), "周術期の輸液": (15, "水"), "多発性関節炎": (15, "金"),
    "腎臓病と高血圧": (16, "月"), "気道緊急": (16, "水"), "鎮静プロトコル": (16, "金"),
    "動脈血栓塞栓症": (17, "月"), "周術期の抗菌薬": (17, "水"), "猫の喘息": (17, "金"),
    "食物アレルギー": (18, "月"), "低血糖の緊急管理": (18, "水"), "急性腎障害vs慢性腎臓病": (18, "金"),
    "てんかん": (19, "月"), "手作り食": (19, "水"), "免疫抑制薬": (19, "金"),
    "猫の輸液": (20, "月"), "子癇": (20, "水"), "DCM": (20, "金"),
    "肥満細胞腫": (21, "月"), "緑内障": (21, "水"), "外傷の初期安定化": (21, "金"),
    "猫の口内炎": (22, "月"), "糖尿病": (22, "水"), "局所麻酔": (22, "金"),
    "特発性膀胱炎": (23, "月"), "前十字靭帯": (23, "水"), "熱中症": (23, "金"),
    "歯周病": (24, "月"), "心嚢水": (24, "水"), "メチシリン耐性菌": (24, "金"),
    "猫の行動学": (25, "月"), "脱水の評価と補正": (25, "水"), "短頭種症候群": (25, "金"),
    "天疱瘡": (26, "月"), "溺水": (26, "水"), "尿管結石": (26, "金"),
    "肺高血圧症": (27, "月"), "角膜潰瘍": (27, "水"), "前庭疾患": (27, "金"),
    "アポキル": (28, "月"), "輸血": (28, "水"), "歯の破折": (28, "金"),
    "多頭飼育": (29, "月"), "麻酔中の低血圧": (29, "水"), "甲状腺機能亢進症": (29, "金"),
    "肥満管理": (30, "月"), "扁平上皮癌": (30, "水"), "腎臓病の食事療法": (30, "金"),
    "DICの管理": (31, "月"), "犬種別スクリーニング": (31, "水"), "心臓病のリハビリ": (31, "金"),
    "膝蓋骨脱臼": (32, "月"), "脊髄軟化症": (32, "水"), "薬疹": (32, "金"),
    "先天性心疾患": (33, "月"), "赤い目の鑑別": (33, "水"), "無麻酔歯石除去": (33, "金"),
    "骨折の初期安定化": (34, "月"), "フィラリア": (34, "水"), "電解質異常": (34, "金"),
    "健康診断": (35, "月"), "ワクチン": (35, "水"),
}

def get_schedule_prefix(base_name):
    """記事名からスケジュールのプレフィックス（例: ②水_）を返す。該当なしならNone。"""
    for keyword, (week, day) in SCHEDULE_MAP.items():
        if keyword in base_name:
            return f"{CIRCLED_NUMBERS.get(week, str(week))}{day}_"
    return None

def ensure_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def generate_all_sns(md_filepath):
    """
    指定されたMarkdownまたはHTMLファイルから、Note/X/Threads/Instagram全SNS向けコンテンツを生成する
    """
    if not os.path.exists(md_filepath):
        print(f"[エラー] ファイルが見つかりません: {md_filepath}")
        return

    # 拡張子を除いたベース名を取得
    ext = os.path.splitext(md_filepath)[1]
    base_name = os.path.basename(md_filepath).replace(ext, '')
    
    # 出力先ディレクトリの設定
    category = "etc"
    parts = md_filepath.split(os.sep)
    if 'topics' in parts:
        try:
            category_idx = parts.index('topics') + 1
            if category_idx < len(parts):
                category = parts[category_idx]
        except ValueError:
            pass

    # フォルダ名にスケジュールプレフィックスを付与
    folder_name = f"{category}_{base_name}"
    prefix = get_schedule_prefix(base_name)
    if prefix:
        folder_name = prefix + folder_name

    # デスクトップ上にSNS専用出力フォルダを作成
    desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
    out_dir = os.path.join(desktop_dir, "VetEvidence_SNS_Drafts", folder_name)
    ensure_dir(out_dir)
    
    output_summary_file = os.path.join(out_dir, "sns_all_drafts.md")

    print(f"[{base_name}] のSNS一括生成を開始します...")

    # 1. Note用（既存フォーマットスクリプトの呼び出し）
    note_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "format_articles_for_note.py")
    if os.path.exists(note_script):
        print(" -> Note用Markdownの生成中...")
        try:
            # Note変換は既存スクリプトにお任せ（HTMLを想定して作られている場合は適宜調整）
            # ここでは呼び出しをスキップするか、必要に応じてsubprocessで実行
            pass
        except Exception as e:
            print(f"Note変換でエラー: {e}")

    # 2. X用の生成（3パターンのうちどれかランダム、または複数出力しても良い）
    print(" -> X（旧Twitter）用テキストの生成中...")
    x_draft_1 = generate_x_post(md_filepath, pattern=1)
    x_draft_2 = generate_x_post(md_filepath, pattern=2)
    x_draft_3 = generate_x_post(md_filepath, pattern=3)

    # 3. Threads用の生成
    print(" -> Threads用テキストの生成中...")
    threads_draft = generate_threads_post(md_filepath)

    # 4. Instagram用の生成
    print(" -> Instagramカローセル用台本の生成中...")
    ig_draft = generate_ig_slides_post(md_filepath)
    
    # 5. 結果を一つのファイルにまとめる
    content = f"# 📝 {base_name} - SNS連携投稿ドラフト一式\n\n"
    content += f"生成日時: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    content += f"元ファイル: {md_filepath}\n\n"
    
    content += "---\n\n## 🐦 X（旧Twitter）用\n\n"
    content += "### パターン1: 昔の常識 vs 今\n```text\n" + x_draft_1 + "\n```\n\n"
    content += "### パターン2: 結論ファースト\n```text\n" + x_draft_2 + "\n```\n\n"
    content += "### パターン3: 数字で驚かせる\n```text\n" + x_draft_3 + "\n```\n\n"
    
    content += "---\n\n## 🧵 Threads用（長文・専門的）\n\n"
    content += "```text\n" + threads_draft + "\n```\n\n"
    
    content += "---\n\n## 🟣 Instagram用（カルーセルスライド台本10枚分）\n\n"
    content += "```text\n" + ig_draft + "\n```\n\n"
    
    with open(output_summary_file, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"✨ 全SNS用のドラフト生成が完了しました！\n確認用ファイル: {output_summary_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用法: python generate_all_sns.py <MarkdownまたはHTMLファイルのパス>")
        sys.exit(1)
        
    md_file = sys.argv[1]
    generate_all_sns(md_file)
