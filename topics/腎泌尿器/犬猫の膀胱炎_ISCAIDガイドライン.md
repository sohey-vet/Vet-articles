# 🚽 犬猫の膀胱炎 ─ ISCAIDガイドライン準拠

> ⏱️ **読了時間**: 約5分
> 📄 **参照論文**: 6本

---

## 🎯 結論

犬と猫の膀胱炎は まったく異なる疾患概念 で治療アプローチが根本的に違う。
                    犬の下部尿路症状のほとんどは 細菌性UTI （E. coliが最多）。ISCAIDガイドラインでは単純性UTIに対し、 アモキシシリン11〜15mg/kg PO q8〜12h × 3〜5日の短期治療 を推奨。
                    一方、若齢〜中齢の猫の下部尿路症状の 約60〜70%は猫特発性膀胱炎（FIC） で細菌感染は1〜2%のみ → 抗菌薬は不要 。
                    尿培養は 膀胱穿刺尿 で行い、≥10³ CFU/mLを有意とする。

---

## 🗺️ 犬 vs 猫 ─ 下部尿路症状の原因の違いgraph TD
    A["来院: 下部尿路症状"] --> B("問診・身体検査")
    B --> C{"尿道閉塞の有無 (オス猫で特に重要)"}

    C -- あり --> D["!!! 緊急処置 !!!"]

    C -- なし --> E("初期尿検査: 尿比重・pH・沈渣")

    E --> F{"動物種: 犬 or 猫?"}

    F -- 犬 --> G["犬ルート"]
    G --> G1["膀胱穿刺尿培養"]
    G1 --> G2{"尿沈渣で細菌・白血球あり?"}
    G2 -- あり --> G3{"UTIのタイプ?"}
    G3 -- 散発性UTI --> G4["経験的抗菌薬 (Amoxicillin 3-5日)"]
    G4 --> G5{"症状改善?"}
    G5 -- Yes --> G6["治療終了"]
    G5 -- No --> G7["培養結果に基づき抗菌薬調整"]
    G3 -- 再発性/複雑性UTI --> G8["基礎疾患検索 (画像, 血液) + 培養結果に基づき抗菌薬 (7-14日) + 基礎疾患治療"]

    F -- 猫 --> H["猫ルート"]
    H --> H1{"年齢・基礎疾患の有無?"}
    H1 -- 若〜中齢猫基礎疾患なし --> H2["FIC疑い (細菌感染稀)"]
    H2 --> H3["膀胱穿刺尿培養 (細菌除外目的)"]
    H3 --> H4{"培養結果"}
    H4 -- 細菌(-) --> H5["FIC確定: MEMO療法 + 鎮痛"]
    H4 -- 細菌(+) --> H6["細菌性UTI: 培養結果に基づき抗菌薬 + 基礎疾患検索"]
    H1 -- 高齢猫 (>10歳)またはDM/CKDなど基礎疾患あり --> H7["細菌性UTIリスク増"]
    H7 --> H8["膀胱穿刺尿培養"]
    H8 --> H6

    E --> I{"尿路結石/腫瘍の疑い?"}
    I -- あり --> J["画像診断 (X線, エコー)"]

    subgraph 臨床ポイント
    end

| 原因 | 🐕 犬 | 🐱 猫（若〜中齢） | 🐱 猫（高齢 ≥10歳） |
|:---|:---|:---|:---|
| 細菌性UTI | **最多** （メスに多い） | 1〜2% | 増加（CKD・DM合併例） |
| 猫特発性膀胱炎（FIC） | ─ | **60〜70%** | 減少 |
| 尿路結石 | 15〜20% | 10〜20% | 10〜20% |
| 尿道閉塞 | まれ | オス猫で多い <br> （緊急！） | 結石・腫瘍が原因 |
| 腫瘍 | 移行上皮癌（中〜高齢） | まれ | 少数 |

---

## ⚡ 昔の常識 vs 今のエビデンス

| ❌ 旧来 | ✅ 最新 |
|:---|:---|
| UTIの治療は14日間 | 単純性UTI（犬）は **3〜5日の短期治療で十分** （ISCAID 2019） |
| 猫の膀胱炎には抗菌薬 | 若〜中齢猫の膀胱炎の大部分はFIC → **抗菌薬は不要** 。ストレス管理と環境改善が主体 |
| 尿検査で細菌が見えたら治療 | **無症候性細菌尿は治療しない** （臨床的リスクがない限り）。耐性菌増加の原因に |
| 経験的にフルオロキノロン | 単純性UTIの第一選択は **アモキシシリンまたはTMP-SMX** 。フルオロキノロンは腎盂腎炎や耐性菌用に温存 |

---

## 📚 参照論文

1. Weese JS et al. International Society for Companion Animal Infectious Diseases (ISCAID)                                 guidelines for the diagnosis and management of bacterial urinary tract infections in                                 dogs and cats (2019). **Vet J** 2019;247:8-25.
2. Buffington CA. Idiopathic cystitis in domestic cats ─ beyond the lower urinary tract                                 (2011). **J Vet Intern Med** 2011;25(4):784-796.
3. Dorsch R et al. Feline lower urinary tract disease in a German cat population: a                                 retrospective analysis of demographic data, causes, and clinical signs (2014). **Tierärztl Prax Ausg K Kleintiere Heimtiere** 2014;42(4):231-239.
4. Westropp JL et al. Evaluation of the effects of stress in cats with idiopathic cystitis                                 (2006). **Am J Vet Res** 2006;67(4):731-736.
5. Olin SJ, Bartges JW. Urinary tract infections: treatment/comparative therapeutics                                 (2015). **Vet Clin North Am Small Anim Pract** 2015;45(4):721-746.
6. Seguin MA et al. Persistent urinary tract infections and reinfections in 100 dogs                                 (2003). **J Vet Intern Med** 2003;17(5):622-631.

---

tags: [腎泌尿器, 抗菌薬, 猫]
update: 2026-03-24