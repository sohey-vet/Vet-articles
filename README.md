# 🐾 獣医論文まとめプロジェクト

## 概要
動物救急に関する最新のエビデンスをまとめ、臨床現場で役立つ情報を整理するプロジェクト。

## 用途
1. **自分の勉強用メモ**
2. **同僚への共有**（単品論文レポート / テーマ別まとめ）
3. **SNS・Note発信**（Xサブ垢、Note有料記事でのマネタイズ）

## フォルダ構成
```
論文まとめ/
├── README.md                    # このファイル
├── index.html                   # メインページ（論文一覧・ナビゲーション）
├── assets/                      # CSS・JS・画像など共有リソース
│   ├── style.css
│   └── script.js
├── templates/                   # テンプレートファイル
│   ├── single_paper.html        # 単品論文レポート用テンプレート
│   └── topic_review.html        # テーマ別まとめ用テンプレート
├── papers/                      # 個別論文まとめ
│   └── YYYY-MM-DD_タイトル.html
├── topics/                      # テーマ別まとめ
│   ├── 下痢/
│   ├── 抗生剤/
│   └── ...
└── resources/                   # 論文PDF・参考資料の保管
    └── ...
```

## 論文の情報源
| 情報源 | URL | コスト | 特徴 |
|--------|-----|--------|------|
| VetLit.org | https://vetlit.org | 無料 | 60+ジャーナルの新着論文を分野別にまとめ |
| PubMed | https://pubmed.ncbi.nlm.nih.gov/ | 無料 | 世界最大の医学文献DB |
| Google Scholar | https://scholar.google.com/ | 無料 | 無料PDF探しに最適 |
| Frontiers in Vet Science | https://www.frontiersin.org/journals/veterinary-science | 無料 | 完全オープンアクセス |
| JVECC | Wiley Online Library | 有料 | 救急集中治療の最重要ジャーナル |

## テーマ候補
- [ ] 犬猫の下痢（新エビデンス vs 旧来の治療法）
- [ ] 抗生剤の最適使用（病態別・臓器別）
- [ ] 心肺蘇生（RECOVER guidelines）
- [ ] 中毒
- [ ] 外傷
- [ ] ショック管理
- [ ] 輸液療法
