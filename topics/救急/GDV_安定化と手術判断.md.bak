# 🚨 GDV（胃拡張-捻転症候群）─ 安定化と手術判断

> ⏱️ **読了時間**: 約5分
> 📄 **参照論文**: 7本

---

## 🎯 結論

GDV（Gastric Dilatation-Volvulus:
                    胃拡張-捻転症候群）は 手術以外に根治法がない 外科救急疾患。到着後の優先順位は ①輸液蘇生 ②胃減圧
                        ③手術（捻転整復＋胃固定術） 。安定化なしの手術は死亡率を上昇させる。レントゲンで 「ダブルバブル」サイン と脾臓の変位を確認したら、GDVとして迅速に行動する。全体の生存退院率は 約85% （胃壊死なし）〜 約50〜66% （胃壊死・切除あり）。 予防的胃固定術 （避妊・去勢手術時の同時実施）はハイリスク犬種で推奨される。

---

## 🗺️ GDV到着後の治療フロー

| ステップ | 行動 | ポイント |
|:---|:---|:---|
| **① 即座** | 両側頸静脈に大口径（18G以上）留置針 | 末梢は虚脱で確保困難なことが多い |
| **② 0〜15分** | 等張晶質液ボーラス（犬: 10〜20mL/kg） | 後大静脈圧迫 → 静脈還流↓ → 2ルートで急速投与 |
| **③ 同時進行** | X線（右側臥位）でGDV確認 | ダブルバブルサイン、脾臓変位 |
| **④ 15〜30分** | 胃減圧（経口チューブ or 穿刺） | 減圧で血行動態が劇的に改善することが多い |
| **⑤ 安定化後** | 手術（捻転整復 + 胃固定術 ± 脾摘） | 初期安定化後 **直ちに（遅くとも1〜2時間以内）** 緊急手術へ |
| **⑥ 術後** | 不整脈モニタリング（48〜72時間） | 心室性不整脈が術後12〜36時間にピーク |

```mermaid
graph TD
    start(("来院: GDV疑い")) --> triage{"ショック徴候あり？"}
    triage -->|"Yes"| IV_resuscitation["① 輸液蘇生: 2ルート確保、急速輸液 (LRS 10-20mL/kgボーラス)"]
    triage -->|"No"| IV_resuscitation
    IV_resuscitation --> diagnosis["② 診断: 右側臥位X線 (ダブルバブル, 脾臓変位)"]
    diagnosis --> confirmed_gdv{"GDVと確定診断？"}
    confirmed_gdv -->|"No"| other_dx["他疾患の評価"]
    confirmed_gdv -->|"Yes"| decompression_method["③ 胃減圧: 経口胃チューブ試行"]
    decompression_method --> oral_tube_success{"経口チューブ挿入可？"}
    oral_tube_success -->|"Yes"| gastric_wash["ガス/内容物排出 + 温生食で胃洗浄"]
    oral_tube_success -->|"No"| percutaneous_decompression["経皮的胃穿刺による減圧"]
    percutaneous_decompression --> retry_oral_tube{"減圧後、経口チューブ挿入可？"}
    retry_oral_tube -->|"Yes"| gastric_wash
    retry_oral_tube -->|"No"| proceed_surgery_path

    gastric_wash --> hemodynamic_eval["血行動態評価 (MAP≥65, CRT＜2, 心拍安定化)"]
    hemodynamic_eval --> stabilization_achieved{"初期安定化達成？"}
    stabilization_achieved -->|"No"| IV_resuscitation
    stabilization_achieved -->|"Yes"| surgery_prep["④ 手術準備: 血液検査, 心電図"]
    surgery_prep --> proceed_surgery_path["⑤ 緊急手術 (捻転整復 + 胃固定術)"]

    proceed_surgery_path --> stomach_eval{"術中の胃壁評価: 壊死組織あり？"}
    stomach_eval -->|"Yes"| partial_gastrectomy["胃部分切除"]
    stomach_eval -->|"No"| spleen_eval{"脾臓評価: 巻き込み/損傷あり？"}
    partial_gastrectomy --> spleen_eval
    spleen_eval -->|"Yes"| splenectomy["脾臓摘出"]
    spleen_eval -->|"No"| surgery_complete["手術完了"]
    splenectomy --> surgery_complete

    surgery_complete --> post_op_care["⑥ 術後管理: 心電図モニタリング (48-72h)"]
    post_op_care --> arrhythmia{"術後心室性不整脈あり？"}
    arrhythmia -->|"Yes"| sustained_vt{"持続性心室頻拍 (HR＞180bpm, 灌流低下)？"}
    sustained_vt -->|"Yes"| lidocaine_tx["リドカイン投与 (ボーラス→CRI)"]
    sustained_vt -->|"No"| observe_arrhythmia["経過観察 (散発性VPC)"]
    arrhythmia -->|"No"| discharge_criteria["退院基準満たすまで入院"]
    lidocaine_tx --> discharge_criteria
    observe_arrhythmia --> discharge_criteria

    discharge_criteria --> endNode(("退院 + 飼い主説明"))
```

---

## ⚡ 昔の常識 vs 今のエビデンス

| ❌ 旧来 | ✅ 最新 |
|:---|:---|
| GDVは大型犬だけの病気 | フレンチブルドッグ・ダックスフンド等の中小型犬でも報告あり。日本ではフレブルの症例が増加 |
| 減圧してから安定を待って手術 | 安定化しつつ **直ちに（遅くとも1〜2時間以内に）緊急手術** へ。手術を数時間〜24時間遅らせると胃・脾臓の不可逆的壊死を招き致死率が激増する |
| 術後の不整脈にはリドカインをルーチン投与 | 血行動態に影響のない心室性期外収縮は治療不要。 **持続性心室頻拍** （HR＞180 bpm かつ灌流低下）のみリドカイン適応 |
| 予防的胃固定術のエビデンスは不十分 | ハイリスク犬種に対する **予防的胃固定術** はGDV発症を効果的に予防。腹腔鏡補助下で低侵襲に実施可能 |

---

## 📚 参照論文

1. Brockman DJ et al. Canine gastric dilatation/volvulus syndrome in a veterinary critical                                 care unit: 295 cases (1986-1992) (1995). **J Am Vet Med Assoc** 1995;207(4):460-464.
2. Glickman LT et al. Non-dietary risk factors for gastric dilatation-volvulus in large and                                 giant breed dogs (2000). **J Am Vet Med Assoc** 2000;217(10):1492-1499.
3. Mackenzie G et al. A retrospective study of factors influencing survival following                                 surgery for gastric dilatation-volvulus syndrome in 306 dogs (2010). **J Am Anim Hosp                                     Assoc** 2010;46(2):97-102.
4. Sharp CR, Rozanski EA. Cardiovascular and systemic effects of gastric dilatation and                                 volvulus in dogs (2014). **Top Companion Anim Med** 2014;29(2):39-44.
5. Ward MP et al. Benefits of prophylactic gastropexy for dogs at risk of GDV: a decision                                 analytic model (2003). **Prev Vet Med** 2003;60(4):319-329.
6. Rawlings CA et al. Laparoscopic-assisted gastropexy in 20 dogs (2002). **J Am Anim                                     Hosp Assoc** 2002;38(6):589-599.
7. Beer KAS et al. Use of plasma lactate concentration as a prognostic indicator in dogs                                 with gastric dilatation-volvulus: 102 cases (1997-2003) (2013). **J Am Vet Med                                     Assoc** 2013;242(2):235-240.

---

tags: [救急, 外科, 大型犬, 消化器, ショック]
update: 2026-03-24