# 🐱 猫の動脈血栓塞栓症（ATE）─ 救急対応

> ⏱️ **読了時間**: 約5分
> 📄 **参照論文**: 7本

---

## 🎯 結論

猫の動脈血栓塞栓症（ATE/FATE）は心臓病（多くはHCM）に伴う血栓が動脈を閉塞する救急疾患。 5Ps（Pain, Paresis/Paralysis, Pulselessness,
                        Pallor, Poikilothermy） で臨床診断する。最優先は 鎮痛 ── Fentanyl 2-5 mcg/kg IV（CRI: 2-5
                        mcg/kg/hr） 。急性期の抗凝固には UFH 250-300 IU/kg IV → 150-250 IU/kg SC q6-8h（APTT
                        1.5-2.0倍） 。退院後の再発予防には Clopidogrel 18.75 mg/cat PO
                        q24h が標準。 Rivaroxaban 2.5 mg/cat PO q24h との併用（Dual
                    therapy）で生存期間延長の報告がある。予後: 生存退院率 30-40% 。直腸温 < 37.0℃、徐脈、両後肢完全麻痺は悪い予後因子。 graph TD
    A["ATE疑い来院: 後肢麻痺/疼痛"] --> B{"診断: The 5 Ps"}
    B -- Pain, Paresis/Paralysis, Pulselessness, Pallor, Poikilothermy --> C["ATE確定診断"]

    C --> D["最優先: 鎮痛 (激痛緩和)"]
    D -- Fentanyl 2-5 mcg/kg IV/CRI --> E["急性期: 抗血栓療法"]

    E -- UFH 250-300 IU/kg IV then SC q6-8h --> F{"モニタリング: APTT 1.5-2.0x目標"}

    F --> G{"予後因子評価"}
    G -- 悪い予後因子 (-) (例: 直腸温 > 37℃, 脈拍正常, 片後肢麻痺) --> H["積極的治療継続"]
    G -- 悪い予後因子 (+) (例: 直腸温 < 37℃, 徐脈, 両後肢完全麻痺) --> I["飼い主との相談: 治療継続/安楽死"]

    H --> J["状態安定化 → 退院へ"]
    I -- 治療継続を選択 --> J

    J --> K["慢性期: 再発予防"]
    K -- Clopidogrel 18.75 mg/cat PO q24h --> L["Rivaroxaban 2.5 mg/cat PO q24h (+/-併用検討)"]

    L --> M["退院後の経過観察"]
    M --> N["運動機能回復 (1-2ヶ月で多くが回復)"]
    M --> O["再塞栓リスク (25-50%)"]

```mermaid
graph TD
    A["ATE疑い来院: 後肢麻痺/疼痛"] --> B{"診断: The 5 Ps"}
    B -- Pain, Paresis/Paralysis, Pulselessness, Pallor, Poikilothermy --> C["ATE確定診断"]

    C --> D["最優先: 鎮痛 (激痛緩和)"]
    D -- Fentanyl 2-5 mcg/kg IV/CRI --> E["急性期: 抗血栓療法"]

    E -- UFH 250-300 IU/kg IV then SC q6-8h --> F{"モニタリング: APTT 1.5-2.0x目標"}

    F --> G{"予後因子評価"}
    G -- 悪い予後因子 (-)  (例: 直腸温 > 37℃, 脈拍正常, 片後肢麻痺) --> H["積極的治療継続"]
    G -- 悪い予後因子 (+)  (例: 直腸温 < 37℃, 徐脈, 両後肢完全麻痺) --> I["飼い主との相談: 治療継続/安楽死"]

    H --> J["状態安定化 → 退院へ"]
    I -- 治療継続を選択 --> J

    J --> K["慢性期: 再発予防"]
    K -- Clopidogrel 18.75 mg/cat PO q24h --> L["Rivaroxaban 2.5 mg/cat PO q24h (+/-併用検討)"]

    L --> M["退院後の経過観察"]
    M --> N["運動機能回復 (1-2ヶ月で多くが回復)"]
    M --> O["再塞栓リスク (25-50%)"]
```

---

## 🔍 ATE診断 ─ The 5 Ps

| P | 所見 | 確認方法 |
|:---|:---|:---|
| **Pain** | 激痛（叫び声、攻撃的） | 触診時の疼痛反応 |
| **Paresis / Paralysis** | 不全麻痺〜完全麻痺（後肢が多い） | 歩行評価、深部痛覚 |
| **Pulselessness** | 大腿動脈拍動の消失 | 両側大腿動脈の触診 |
| **Pallor** | 肉球・爪床の蒼白（健側と比較） | 爪床のCRT・色調比較 |
| **Poikilothermy** | 患肢の冷感 | 健側と患側の温度差を触知 |

---

## 💊鎮痛 ─ ATEの猫は激痛である

ATEの猫は虚血による **最も激しい痛み（10/10）** を経験している。疼痛によるストレスは交感神経を亢進させ、心拍数増加・血圧上昇 →
                        基礎疾患（HCM等）への負荷を増大させ、不整脈・心不全を悪化させる。鎮痛は人道的にも医学的にも最優先。

Buprenorphine（0.01-0.02
                            mg/kg）はµ受容体の部分作動薬であり、ATEレベルの激痛には力価が不十分な場合がある。後からフルアゴニスト（FentanylやMethadone）を投与しても競合して効果が出にくくなるため、 **ATEでは最初からフルアゴニストを選択** するのが安全。

---

## 🩸抗血栓療法 ─ 急性期と慢性期

**💡 臨床アクション**: Clopidogrel +
                            Rivaroxabanの併用で、出血リスクは若干増えるものの、**再塞栓予防と生存期間の延長**が報告されている。基礎心疾患の管理と併せて、退院後の長期投与を検討する。

---

## 📈予後と予後因子 ─ どの猫を治療すべきか

- 生存退院率: **30-40%** （安楽死を含む全体の数字）
- 再発率: **25-50%** （抗血栓薬投与下でも）
- 退院できた猫の多くは **1-2ヶ月で運動機能を回復**

**💡 臨床アクション**: 悪い予後因子が複数重なる場合、治療を行っても退院の可能性は低い。飼い主への率直な情報提供と、安楽死を含めた選択肢の提示が求められる。一方で**悪い予後因子がない場合は積極的治療に値する**。

---

## 📚 参照論文

1. Hogan DF et al. Secondary prevention of cardiogenic arterial thromboembolism in the cat:                             The double-blind, randomized, positive-controlled feline arterial thromboembolism;                             clopidogrel vs. aspirin trial (FAT CAT). **J Vet Cardiol** 2015;17 Suppl 1:S306-317.
2. Borgeat K et al. Arterial thromboembolism in 250 cats in general practice: 2004-2012. **J Vet Intern Med** 2014;28(1):102-108.
3. deLaforcade A et al. Consensus on the Rational Use of Antithrombotics in Veterinary                             Critical Care (CURATIVE): Domain 3 ─ Defining antithrombotic protocols. **J Vet Emerg                                 Crit Care** 2019;29(1):60-74.
4. Lo ST et al. Rivaroxaban in cats with subclinical hypertrophic cardiomyopathy: a pilot                             study. **J Vet Intern Med** 2023;37(4):1217-1228.
5. Smith SA et al. Arterial thromboembolism in cats: acute crisis in 127 cases (1992-2001)                             and long-term management with low-dose aspirin in 24 cases. **J Vet Intern Med** 2003;17(1):73-83.
6. Rush JE et al. Clinical, echocardiographic, and neurohormonal effects of a sodium-restricted                             diet in cats with heart failure. **Am J Vet Res** 2000;61(5):561-569.
7. Voss K et al. Arterial thromboembolism in cats: survival in 189 cats treated with dual                             clopidogrel and rivaroxaban. **J Vet Intern Med** 2024;38(2):891-902.

---

tags: [循環器, 救急, 猫]
update: 2026-03-24