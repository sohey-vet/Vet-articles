# Google AI Ultra 校閲リクエスト

以下の8つの獣医学記事原稿について、最終的な校閲（Quality Control）をお願いします。
各記事は「Gemini 3 Proによるファクト抽出」→「Claude Opus 4.6による執筆」→「Gemini 3 Proによるクロスチェック」を経ていますが、念のため、以下の点について**Google AI Ultraの高度な推論能力**で再確認してください。

## チェック項目
1. **医学的妥当性**: 記載されている薬剤用量、治療方針が獣医学的に（特に欧米の最新ガイドラインに照らして）妥当か。
2. **安全性**: 致命的な誤り（例: "ml"と"mg"の間違い、"IV"と"SC"の間違い）がないか。
3. **論理性**: 文脈に矛盾がないか。

---

## 1. 周術期の輸液管理
- **結論**: AAHA 2024ガイドライン準拠。犬5mL/kg/hr、猫3mL/kg/hr。
- **重要数値**:
    - 犬初期速度: 5 mL/kg/hr
    - 猫初期速度: 3 mL/kg/hr
    - ボーラス: 犬5-10 mL/kg、猫3-5 mL/kg

## 2. 多発性関節炎 (IMPA vs Septic)
- **結論**: 鑑別の鍵は関節液分析。
- **重要数値**:
    - IMPA: 非変性好中球、培養陰性。Tx: Prednisolone 1-2 mg/kg/day。
    - Septic: 変性好中球、細胞内細菌。

## 3. アジソン病 (Hypoadrenocorticism)
- **結論**: ACTH刺激試験で診断。
- **重要数値**:
    - ACTH後Cortisol < 2 μg/dLで確定。
    - クリーゼ: DOCP 2.2 mg/kg (実臨床1.1-1.5)、Prednisolone 0.05-0.1 mg/kg。
    - 輸液ボーラス: 15-30 mL/kg。

## 4. 腎臓病と高血圧 (CKD & Hypertension)
- **結論**: IRIS分類 SBP > 160 mmHgで治療。
- **重要数値**:
    - 猫第一選択: Amlodipine 0.625-1.25 mg/cat PO q24h。
    - 犬第一選択: ACE-I/ARB。追加でAmlodipine 0.1-0.2 mg/kg。
    - 標的臓器: 眼、腎、脳、心。

## 5. 気道緊急 (Upper Airway Obstruction)
- **結論**: まず鎮静。
- **重要数値**:
    - 鎮静: Acepromazine 0.005-0.02 mg/kg + Butorphanol 0.2-0.4 mg/kg IV。
    - 冷却目標: 39.5℃で中止。
    - ステロイド: Dex SP 0.1-0.2 mg/kg IV。

## 6. 鎮静プロトコル (Sedation Cheat Sheet)
- **結論**: 処置合わせ。
- **重要数値**:
    - 犬Dex: 3-5 mcg/kg IV。
    - 猫Kitty Magic: Dex 10-20 mcg/kg + Ketamine 3-5 mg/kg + Butorphanol 0.2-0.3 mg/kg IM。
    - 来院前: Gabapentin 50-100 mg/cat PO。

## 7. 猫のATE (Arterial Thromboembolism)
- **結論**: 5Ps診断、鎮痛最優先。
- **重要数値**:
    - 鎮痛: Fentanyl 2-5 mcg/kg IV。
    - 抗血栓(急性): UFH 250-300 IU/kg IV → 150-250 SC。
    - 抗血栓(慢性): Clopidogrel 18.75 mg/cat + Rivaroxaban 2.5 mg/cat。

## 8. 周術期の抗菌薬 (Antibiotic Prophylaxis)
- **結論**: 執刀30-60分前投与、術後24h以内中止。
- **重要数値**:
    - Cefazolin: 20-22 mg/kg IV。
    - 追加投与: 90-120分ごと。
    - Clean手術: 原則不要。
