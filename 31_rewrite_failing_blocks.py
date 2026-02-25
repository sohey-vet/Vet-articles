"""
Manually rewrite ALL 8 failing Mermaid blocks with clean, tested syntax.
Each block is rewritten from scratch based on the medical content.
"""
import re
from pathlib import Path

def replace_mermaid(filepath, new_blocks):
    """Replace all mermaid blocks in a file with the provided new blocks."""
    with open(filepath, 'r', encoding='utf-8') as fh:
        content = fh.read()
    
    # Find all mermaid blocks
    pattern = r'<pre class="mermaid">.*?</pre>'
    existing = re.findall(pattern, content, re.DOTALL)
    
    if len(new_blocks) != len(existing):
        # If mismatch, replace all with new blocks joined
        # Remove all existing blocks first
        for i, block in enumerate(existing):
            if i < len(new_blocks):
                content = content.replace(block, f'<pre class="mermaid">\n{new_blocks[i]}\n</pre>', 1)
            else:
                content = content.replace(block, '', 1)
    else:
        for i, block in enumerate(existing):
            content = content.replace(block, f'<pre class="mermaid">\n{new_blocks[i]}\n</pre>', 1)
    
    with open(filepath, 'w', encoding='utf-8') as fh:
        fh.write(content)
    print(f'Rewrote: {Path(filepath).stem}')


# 1. クッシング症候群 - Cushing's diagnostic algorithm
cushing_block = '''graph TD
    A["臨床症状あり? (多飲多尿, 腹部膨満, 脱毛, 皮膚菲薄化, パンティング, ALP著増など)"] --> B{"複数の典型症状が合致？"}
    B -->|"No"| C["HAC検査は時期尚早。他の疾患を検討"]
    B -->|"Yes"| D{"併発疾患の急性期や重度ストレスはないか?"}
    D -->|"Yes"| E["偽陽性リスク高。安定化後に再検査"]
    D -->|"No"| F["スクリーニング検査実施"]
    F --> G["LDDST 実施"]
    F --> H["UCCR 実施"]
    G --> I{"LDDST結果"}
    I -->|"コルチゾール抑制"| J["HACは否定的"]
    I -->|"コルチゾール非抑制"| K["HACの疑い強い"]
    H --> L{"UCCR結果"}
    L -->|"正常"| J
    L -->|"上昇"| K
    K --> M["鑑別検査: HDDST or 内因性ACTH"]
    M --> N{"HDDST: 4h/8hで抑制あり? or ACTH高値?"}
    N -->|"Yes"| O["PDH: 下垂体性"]
    N -->|"No"| P["AT: 副腎腫瘍"]
    O --> Q["治療: トリロスタン (PDH第一選択)"]
    P --> R["腹部エコー: 副腎サイズ評価"]
    R --> S["AT 4cm超: 血管浸潤評価必須"]
    S --> T["治療: 副腎摘出術 or トリロスタン"]'''

replace_mermaid(
    r'c:\Users\souhe\Desktop\論文まとめ\topics\内分泌\クッシング症候群_診断の落とし穴.html',
    [cushing_block]
)


# 2. 不整脈の救急対応 - Arrhythmia emergency
arrhythmia_block = '''graph TD
    A["心電図所見から不整脈を鑑別"] --> B{"心拍数は？"}
    B -->|"頻脈 (犬>160 / 猫>220 bpm)"| C{"QRS幅は？"}
    C -->|"幅広い (>0.06秒)"| D{"リズムは？"}
    D -->|"規則的"| E["心室頻拍 (VT)"]
    E --> F["初期治療: リドカイン 2mg/kg IV"]
    C -->|"狭い (<0.06秒)"| G{"リズムは？"}
    G -->|"規則的"| H["上室性頻拍 (SVT)"]
    H --> I["初期治療: 迷走神経刺激"]
    G -->|"不規則"| J["心房細動 (AF)"]
    J --> K["初期治療: ジルチアゼム"]
    B -->|"徐脈 (犬<60 / 猫<120 bpm)"| L{"P波とQRSの関係は？"}
    L -->|"P-QRS解離"| M["3度房室ブロック"]
    M --> N["アトロピン反応試験"]
    L -->|"PR延長"| O["1度/2度房室ブロック"]
    B -->|"正常心拍"| P{"不規則なリズム？"}
    P -->|"散発性幅広QRS"| Q["心室期外収縮 (VPC)"]
    F --> R["治療効果評価と基礎疾患検索"]
    I --> R
    K --> R
    N --> R
    Q --> R'''

replace_mermaid(
    r'c:\Users\souhe\Desktop\論文まとめ\topics\循環器\不整脈の救急対応_心電図の読み方.html',
    [arrhythmia_block]
)


# 3. FIP - Treatment algorithm (two identical blocks, replace both)
fip_block = '''graph TD
    A["FIP診断確定 GS-441524治療開始"] --> B{"病型分類"}
    B -->|"滲出型/非滲出型 (眼・神経症状なし)"| C1["経口用量: 15mg/kg PO SID"]
    B -->|"眼型"| C2["経口用量: 15-20mg/kg PO SID"]
    B -->|"神経型"| C3["経口用量: 20mg/kg/日 (10mg/kg q12h分割推奨)"]
    C1 --> D{"経口投与可能か？"}
    C2 --> D
    C3 --> D
    D -->|"Yes"| E["経口投与継続 (在宅管理が主)"]
    D -->|"No (嘔吐,重度口内炎等)"| F["SC注射で開始"]
    F --> G{"経口投与に切替可能？"}
    G -->|"Yes"| E
    G -->|"No"| F
    E --> H["治療開始後モニタリング"]
    H -->|"毎週"| I["体重測定 用量再計算"]
    H -->|"1-2週で確認"| J["食欲改善, 活動性回復"]
    H -->|"1-2週で確認"| K["腹水/胸水減少"]
    H -->|"4週ごと検査"| L["CBC, 生化学, SAA"]
    H -->|"4週ごと検査"| M["A/G比 (血清/滲出液)"]
    L --> N{"SAA正常化, グロブリン低下, リンパ球上昇？"}
    M --> O{"A/G比 0.6以上に正常化？"}
    N -->|"Yes"| P{"総合評価 治療期間判断"}
    O -->|"Yes"| P
    N -->|"No"| Q["治療継続 or 用量増加 (再評価)"]
    O -->|"No"| Q
    Q --> H
    P -->|"滲出型で良好な反応"| R1["治療完了: 42日間"]
    P -->|"その他/神経型は84日以上推奨"| R2["治療完了: 84日間"]
    R1 --> T["治療完了後3ヶ月間モニタリング"]
    R2 --> T
    T -->|"再発兆候なし"| U["寛解と判断"]
    T -->|"再発兆候あり (発熱,グロブリン/SAA再上昇)"| V["再治療 (同用量or増量)"]'''

replace_mermaid(
    r'c:\Users\souhe\Desktop\論文まとめ\topics\猫\FIP_抗ウイルス薬時代の治療.html',
    [fip_block, fip_block]
)


# 4. 猫の輸液 - Cat fluid therapy monitoring
cat_fluid_block = '''graph TD
    A["輸液中の猫をモニタリング"] --> B{"過剰輸液のサインを検出？"}
    B -->|"YES (RR上昇, 結膜浮腫, 体重急増)"| C["輸液速度を直ちに減量/一時中断"]
    C --> D["酸素吸入の準備/開始"]
    D --> E["利尿剤（例: Furosemide）の投与検討"]
    E --> F{"心疾患の既往・徴候は？"}
    F -->|"YES"| G["心エコー等による心臓評価を推奨"]
    F -->|"NO"| H["循環動態・呼吸状態の頻回モニタリング"]
    G --> H
    H --> I["獣医師による治療方針再検討"]
    B -->|"NO"| J["現在の輸液速度を継続"]
    J --> K["定期的なモニタリング継続"]
    K --> A'''

replace_mermaid(
    r'c:\Users\souhe\Desktop\論文まとめ\topics\猫\猫の輸液_犬との違いと注意点.html',
    [cat_fluid_block]
)


# 5. 椎間板ヘルニア - IVDD grading and treatment
ivdd_block = '''graph TD
    A["犬の胸腰部IVDD診断"] --> B{"修正Frankelスケール評価"}
    B -->|"Grade 1-3 (疼痛のみ～起立困難)"| D["保存療法 (厳格な安静 4-6週, 鎮痛)"]
    B -->|"Grade 4 (対麻痺, DPP残存)"| F["手術推奨 (回復率: 86-96%)"]
    B -->|"Grade 5 (対麻痺, DPP消失)"| G{"DPP消失から48時間以内か?"}
    G -->|"YES"| I["緊急手術"]
    I --> J["回復率: 50-58%"]
    I --> K["PMMリスクについて飼い主へ説明"]
    G -->|"NO"| L["非緊急手術"]
    L --> M["回復率: 50%以下"]
    L --> K
    D --> N{"症状悪化?"}
    N -->|"YES"| F
    N -->|"NO"| O["経過観察"]
    F --> P["術後リハビリテーション"]
    J --> P
    M --> P'''

replace_mermaid(
    r'c:\Users\souhe\Desktop\論文まとめ\topics\神経\椎間板ヘルニア_頚部胸腰部統合版.html',
    [ivdd_block]
)


# 6. 発作の初期対応 - Status epilepticus
seizure_block = '''graph TD
    A["発作発生/SE疑い"] --> B{"SE定義満たす? (5分超持続 or 意識回復なく2回以上)"}
    B -->|"Yes"| C["ジアゼパム 0.5-1mg/kg IV/直腸内"]
    B -->|"No"| Z["SEではない/経過観察"]
    C -->|"同時並行"| F["血糖チェック iCa/NH3"]
    F -->|"低血糖あり (<60mg/dL)"| G["デキストロース 0.5g/kg IV"]
    G --> D{"発作停止?"}
    F -->|"低血糖なし"| D
    C -->|"同時並行"| E["ABC確認 O2フローバイ"]
    D -->|"Yes"| H["SE停止: 安定化 基礎疾患検索/維持療法"]
    D -->|"No (1回目後)"| I["ジアゼパム 2回目"]
    I --> J{"発作停止?"}
    J -->|"Yes"| H
    J -->|"No (2回目後)"| K["ジアゼパム 3回目"]
    K --> L{"発作停止?"}
    L -->|"Yes"| H
    L -->|"No (3回目後)"| M["レベチラセタム 30-60mg/kg IV over 5min"]
    M --> N{"発作停止?"}
    N -->|"Yes"| H
    N -->|"No (難治性SE)"| O["プロポフォールCRI 0.1-0.6mg/kg/min"]
    O --> P["挿管・人工換気準備"]
    O --> Q["SE停止: 安定化 基礎疾患検索/維持療法"]'''

replace_mermaid(
    r'c:\Users\souhe\Desktop\論文まとめ\topics\神経\発作の初期対応_頭蓋内疾患を疑うとき.html',
    [seizure_block]
)


# 7. 血液ガス分析 - Blood gas analysis
blood_gas_block = '''graph TD
    A["血液ガス分析 開始"] --> S1{"Step 1: pHを評価"}
    S1 -->|"pH < 7.35"| A1["アシドーシス"]
    S1 -->|"pH > 7.45"| A2["アルカローシス"]
    S1 -->|"pH 7.35-7.45"| A3["正常範囲 (混合性も考慮)"]
    A1 --> S2A{"Step 2: 主要な原因を特定"}
    S2A -->|"PCO2 上昇"| RA["呼吸性アシドーシス"]
    S2A -->|"HCO3 低下"| MA["代謝性アシドーシス"]
    A2 --> S2B{"Step 2: 主要な原因を特定"}
    S2B -->|"PCO2 低下"| RK["呼吸性アルカローシス"]
    S2B -->|"HCO3 上昇"| MK["代謝性アルカローシス"]
    RA --> S3RA{"Step 3: 代償を確認: HCO3上昇(同方向)?"}
    S3RA -->|"Yes"| RAC["慢性 (代償あり)"]
    S3RA -->|"No"| RAA["急性 (代償なし)"]
    MA --> S3MA{"Step 3: 代償を確認: PCO2低下(同方向)?"}
    S3MA -->|"Yes"| MAC["慢性 (代償あり)"]
    S3MA -->|"No"| MAA["急性 (代償なし)"]
    RK --> S3RK{"Step 3: 代償を確認: HCO3低下(同方向)?"}
    S3RK -->|"Yes"| RKC["慢性 (代償あり)"]
    S3RK -->|"No"| RKA["急性 (代償なし)"]
    MK --> S3MK{"Step 3: 代償を確認: PCO2上昇(同方向)?"}
    S3MK -->|"Yes"| MKC["慢性 (代償あり)"]
    S3MK -->|"No"| MKA["急性 (代償なし)"]'''

replace_mermaid(
    r'c:\Users\souhe\Desktop\論文まとめ\topics\血液ガス\血液ガス分析の基本.html',
    [blood_gas_block]
)


print('\nAll 7 files rewritten.')
