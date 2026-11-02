# 機械検査レポート（B104-108 独立検証・機械パス、2026-10-05）

- 対象: `docs/_work/B104-108_incoming/B104-108/` 100件（実項89＋REF 11）／校閲前 `orig/`／`corpus_B104-108.json`・`vc/corpus_index.json`／ID-Master `docs/_work/idmaster_ext_20261005b.tsv`（8,082 行）／`TMP_NEW_B104〜B108.tsv`・`FIXLOG_B104〜B108.tsv`・`ISSUES_B104〜B108.md`・`REVIEW_NOTES_B104〜B108.md`。repo `Individuals/**`（AIND 番号別 2869件）を語彙・先例・相手側ファイルの参照に使用。
- スクリプト（再実行可・読み取り専用）: `docs/_work/B104-108_incoming/verify/` の `mech_lib.py`（共通ロード）・`mech_check.py`（本体。`mech_items_a.py`=項目1〜4、`_b`=5〜11、`_c`=12〜16、`_c2`=17〜18、`_d`=19〜21、`_e`=22 を exec）。B99-103 の同名スクリプトを流用し、パス・日付・チャンク名・ID-Master・batch_id・仮番号の書式（NEW104〜108）を更新。項目3 の連結レコード検出を一般ロジック（原文末尾の独立した転送文の正規表現。「له ذكر في」は除外）に置き換え、項目11 の汚染・幻番号リストに CHUNK_BRIEF_B104-108 の番号を追加（000416・000347 は「条件付き汚染」＝M）、項目15 の並行追加行の範囲を ID-Master 行 8007〜8082 に変更。`mech_report.py` は本レポートと TSV を生成。中間結果 `mech_results.json`。
- 実行: `cd <repo root> && python3 docs/_work/B104-108_incoming/verify/mech_check.py && python3 docs/_work/B104-108_incoming/verify/mech_report.py`
- XML・corpus・ID-Master・Individuals は一切変更していない。git 操作なし。

## 総括

| 区分 | 件数 |
|---|---|
| 点検 assertion 概数（ID参照 1054・relation 223・日付属性 347・placeName 140・persName 192・type語彙 1311・TMP_NEW 77行・FIXLOG 489行 ほか） | 約 7,501（項目間で重複計上あり） |
| 検出（違反）合計 | **61** |
| 確信度 H / M / L | 6 / 2 / 53 |
| FP / FN / substitution | 7 / 12 / 42 |
| origin: claude_review / gemini_draft（初版の誤りが校閲後も残存） | 60 / 1 |

### 最重要（H）

- [9] **AIND-D05837**（AIND-D05837_260483068522.xml）仮番号 #TMP-P-NEW104-03 が TMP_NEW_B10x.tsv に未登録 → TSV に登録するか既存 ID に
- [9] **AIND-D05856**（AIND-D05856_384831599246.xml）仮番号 #TMP-P-NEW105-08 が TMP_NEW_B10x.tsv に未登録 → TSV に登録するか既存 ID に
- [9] **AIND-D05905**（AIND-D05905_835253711586.xml）仮番号 #TMP-L-NEW107-05 が TMP_NEW_B10x.tsv に未登録 → TSV に登録するか既存 ID に
- [9] **AIND-D05908**（AIND-D05908_681649910511.xml）仮番号 #TMP-P-NEW107-13 が TMP_NEW_B10x.tsv に未登録 → TSV に登録するか既存 ID に
- [9] **AIND-D05939**（AIND-D05939_387926995743.xml）仮番号 #TMP-P-NEW108-11 が TMP_NEW_B10x.tsv に未登録 → TSV に登録するか既存 ID に
- [15] **TMP-P-NEW108-07**（TMP-P-NEW108-07）チャンク間で同一実体の仮 TMP が二重発行の疑い: TMP-P-NEW106-04「الشيخ طلحة العنبري البعلي」（B106）⇔ TMP-P-NEW108-07「طلحة العنبري」（B108）、共通語 ['العنبري', 'طلحه']。発行側 Note に「同番号を使用願う」の申し送りがあるのに別番号が切られている → 一方に統合（TMP-P-NEW106-04 を残し TMP-P-NEW108-07 の XML 参照を差し替え、TSV 行を取り下げ）

## 項目別「点検N件中違反M件」

| # | 項目 | 分母の単位 | 点検N | 違反M | 参考所見 |
|---|---|---|---|---|---|
| 1 | well-formed | XMLファイル | 100 | 0 | 0 |
| 2 | REF 方式X の形 | REF ファイル | 11 | 0 | 14 |
| 3 | 原文 source note と corpus の一致・連結レコード（原文末尾の独立した転送文）の検出と訳文/実伝要素への混入・★校閲印 | ファイル | 100 | 0 | 0 |
| 4 | 日付属性（when-custom⇔when、h2g 再計算、ヒジュラ混入、書式、notBefore/notAfter） | 日付属性 | 347 | 0 | 18 |
| 5 | persName name_only ≤3世代／full の居住句・職名句 | persName(full/name_only) | 192 | 3 | 1 |
| 6 | respStmt（初版非改変・校閲 respStmt） | ファイル | 100 | 37 | 37 |
| 7 | ID 書式（#・wd:・gn:・桁数・自IDの桁） | ID 参照属性 | 1054 | 0 | 0 |
| 8 | 幻 AIND | AIND 参照 | 369 | 0 | 0 |
| 9 | 幻 TMP（ID-Master 未登録／仮番号の TSV 未登録） | TMP 参照 | 451 | 6 | 0 |
| 10 | 毒 wd・未登録 wd/gn | wd/gn 参照 | 217 | 0 | 22 |
| 11 | 汚染 TMP・カテゴリ位置適合 | ID 参照 | 1054 | 0 | 3 |
| 12 | 規約A（relation/@n） | relation | 223 | 0 | 0 |
| 13 | affiliation と state の二重符号化 | ファイル(affiliation) | 105 | 0 | 0 |
| 14 | 統制外 type/subtype（repo 既存値と照合） | type/subtype 付き要素 | 1311 | 1 | 3 |
| 15 | 仮 TMP の重複・ID-Master 既登録・corpus 本伝・TSV⇔XML 片側漏れ | TMP_NEW 行 | 77 | 6 | 94 |
| 16 | 汎用名 TMP-P の「⚠汎用名」明記 | TMP_NEW Person 行 | 39 | 7 | 11 |
| 17 | xml:lang・en 訳の英語性・ja 訳の混入物・placeName ref 位置 | 点検箇所 | 775 | 0 | 0 |
| 18 | 規則22（原文にない placeName・空 residence） | placeName＋residence | 140 | 0 | 5 |
| 19 | relation 整合（本項主・self・向き・相互矛盾・possible_identity 双方向・「ممن سمع مني」型の向き） | relation＋سمع مني型 | 238 | 0 | 28 |
| 20 | 校閲前 orig との要素数比較 | ファイル | 100 | 0 | 16 |
| 21 | 規則24 FIXLOG の書式・語彙・件数 | FIXLOG 行 | 489 | 0 | 1 |
| 22 | 「أرخه ابن فهد」振り分け（没年⇔D09211/D05979/D03985・cert） | 「ابن فهد」記録者の項 | 9 | 1 | 4 |

（「参考所見」は違反としない機械所見の件数。要点は「違反としなかった機械所見」の節、全件は verify/mech_results.json の info。）

## 違反の詳細（項目別）

### 1. well-formed — 点検 100 件中 違反 0 件

違反なし。

### 2. REF 方式X の形 — 点検 11 件中 違反 0 件

違反なし。

### 3. 原文 source note と corpus の一致・連結レコード（原文末尾の独立した転送文）の検出と訳文/実伝要素への混入・★校閲印 — 点検 100 件中 違反 0 件

違反なし。

### 4. 日付属性（when-custom⇔when、h2g 再計算、ヒジュラ混入、書式、notBefore/notAfter） — 点検 347 件中 違反 0 件

違反なし。

### 5. persName name_only ≤3世代／full の居住句・職名句 — 点検 192 件中 違反 3 件

| entry | ファイル | 箇所 | 内容（根拠） | 修正案 | 確信度 | type | category | origin |
|---|---|---|---|---|---|---|---|---|
| AIND-D05921 | AIND-D05921_837036290817.xml | <persName type="full"> | full に居住句・職名句・関係句の疑い ['الأمير']（repo full 2871件中の出現数 {'الأمير': 11}）「عمر بن قاسم بن جمعة الأمير زين الدين القساسي الحلبي」 | 居住句・職名句・父や兄弟の述語を除く（規則5） | L | persName | FP | gemini_draft |
| AIND-D05922 | AIND-D05922_178912244489.xml | <persName type="full"> | full に居住句・職名句・関係句の疑い ['المقرئ']（repo full 2871件中の出現数 {'المقرئ': 9}）「عمر بن قاسم الأنصاري المصري الشافعي المقرئ」 | 居住句・職名句・父や兄弟の述語を除く（規則5） | L | persName | FP | claude_review |
| AIND-D05923 | AIND-D05923_741389382410.xml | <persName type="full"> | full に居住句・職名句・関係句の疑い ['القاضي']（repo full 2871件中の出現数 {'القاضي': 19}）「عمر بن أبي القسم بن معيبد القاضي تقي الدين اليمني التعزي」 | 居住句・職名句・父や兄弟の述語を除く（規則5） | L | persName | FP | claude_review |

### 6. respStmt（初版非改変・校閲 respStmt） — 点検 100 件中 違反 37 件

| entry | ファイル | 箇所 | 内容（根拠） | 修正案 | 確信度 | type | category | origin |
|---|---|---|---|---|---|---|---|---|
| AIND-D05822 | AIND-D05822_300454785611.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05832 | AIND-D05832_201792172631.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05836 | AIND-D05836_402749665889.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05837 | AIND-D05837_260483068522.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05839 | AIND-D05839_512690762346.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05852 | AIND-D05852_398073016963.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05854 | AIND-D05854_270125773445.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05856 | AIND-D05856_384831599246.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05859 | AIND-D05859_979122533009.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05868 | AIND-D05868_582953743006.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05871 | AIND-D05871_931773035172.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05872 | AIND-D05872_753045353126.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05874 | AIND-D05874_663190778534.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05883 | AIND-D05883_451219042998.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05884 | AIND-D05884_475579560634.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05899 | AIND-D05899_833223668435.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05902 | AIND-D05902_115817329370.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05903 | AIND-D05903_538708030172.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05905 | AIND-D05905_835253711586.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05908 | AIND-D05908_681649910511.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05911 | AIND-D05911_989633458929.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05912 | AIND-D05912_535071568627.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05920 | AIND-D05920_883253326596.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05922 | AIND-D05922_178912244489.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05923 | AIND-D05923_741389382410.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05929 | AIND-D05929_989549572876.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05932 | AIND-D05932_615308604181.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05933 | AIND-D05933_739204150038.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05938 | AIND-D05938_978308838174.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05939 | AIND-D05939_387926995743.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05940 | AIND-D05940_761786282785.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05941 | AIND-D05941_777091298084.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05944 | AIND-D05944_513819030317.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05946 | AIND-D05946_986055717683.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05947 | AIND-D05947_640134689588.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05950 | AIND-D05950_635038610234.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |
| AIND-D05951 | AIND-D05951_752638505787.xml | <respStmt> | orig にも校閲にも該当しない respStmt 1 個 | 確認 | L | other | substitution | claude_review |

### 7. ID 書式（#・wd:・gn:・桁数・自IDの桁） — 点検 1054 件中 違反 0 件

違反なし。

### 8. 幻 AIND — 点検 369 件中 違反 0 件

違反なし。

### 9. 幻 TMP（ID-Master 未登録／仮番号の TSV 未登録） — 点検 451 件中 違反 6 件

| entry | ファイル | 箇所 | 内容（根拠） | 修正案 | 確信度 | type | category | origin |
|---|---|---|---|---|---|---|---|---|
| AIND-D05837 | AIND-D05837_260483068522.xml | <relation type="personal" subtype="patron" n="2" active="#TMP-P-NEW104-03" passive="#AIND-D05837"> | 仮番号 #TMP-P-NEW104-03 が TMP_NEW_B10x.tsv に未登録 | TSV に登録するか既存 ID に | H | id_assignment | FN | claude_review |
| AIND-D05856 | AIND-D05856_384831599246.xml | <relation type="personal" subtype="father" active="#TMP-P-NEW105-08" passive="#AIND-D05856"> | 仮番号 #TMP-P-NEW105-08 が TMP_NEW_B10x.tsv に未登録 | TSV に登録するか既存 ID に | H | id_assignment | FN | claude_review |
| AIND-D05905 | AIND-D05905_835253711586.xml | <placeName ref="#TMP-L-NEW107-05"> | 仮番号 #TMP-L-NEW107-05 が TMP_NEW_B10x.tsv に未登録 | TSV に登録するか既存 ID に | H | id_assignment | FN | claude_review |
| AIND-D05908 | AIND-D05908_681649910511.xml | <relation type="personal" subtype="father" active="#TMP-P-NEW107-13" passive="#AIND-D05908"> | 仮番号 #TMP-P-NEW107-13 が TMP_NEW_B10x.tsv に未登録 | TSV に登録するか既存 ID に | H | id_assignment | FN | claude_review |
| AIND-D05939 | AIND-D05939_387926995743.xml | <relation type="personal" subtype="father" active="#TMP-P-NEW108-11" passive="#AIND-D05939"> | 仮番号 #TMP-P-NEW108-11 が TMP_NEW_B10x.tsv に未登録 | TSV に登録するか既存 ID に | H | id_assignment | FN | claude_review |
| AIND-D05951 | AIND-D05951_752638505787.xml | <relation type="personal" subtype="teacher" n="1" active="#TMP-P-NEW106-04" passive="#AIND-D05951"> | #TMP-P-NEW106-04 は他チャンク発行の仮番号（本ファイルのチャンク=B108） | 自チャンクの仮番号にするか、共有なら TSV Note に出現ファイルを明記 | L | id_assignment | substitution | claude_review |

### 10. 毒 wd・未登録 wd/gn — 点検 217 件中 違反 0 件

違反なし。

### 11. 汚染 TMP・カテゴリ位置適合 — 点検 1054 件中 違反 0 件

違反なし。

### 12. 規約A（relation/@n） — 点検 223 件中 違反 0 件

違反なし。

### 13. affiliation と state の二重符号化 — 点検 105 件中 違反 0 件

違反なし。

### 14. 統制外 type/subtype（repo 既存値と照合） — 点検 1311 件中 違反 1 件

| entry | ファイル | 箇所 | 内容（根拠） | 修正案 | 確信度 | type | category | origin |
|---|---|---|---|---|---|---|---|---|
| AIND-D05932 | AIND-D05932_615308604181.xml | <relation type="personal" subtype="maternal_aunt" active="#AIND-D13497" passive="#AIND-D05932"> | 統制外の type/subtype ('relation', 'personal', 'maternal_aunt')（repo Individuals に先例なし） | repo 既存値に（同 type の既存 subtype: ['personal/acquaintance', 'personal/advisor/tutor', 'personal/ancestor', 'personal/appointer', 'personal/associate', 'personal/author of studied treatise', 'personal/author/compiler', 'personal/believer/admirer', 'personal/biographer', 'personal/brother', 'personal/brother-in-law', 'personal/captor']）。ISSUES/REVIEW_NOTES に新設の記載あり＝裁定待ち | L | other | substitution | claude_review |

### 15. 仮 TMP の重複・ID-Master 既登録・corpus 本伝・TSV⇔XML 片側漏れ — 点検 77 件中 違反 6 件

| entry | ファイル | 箇所 | 内容（根拠） | 修正案 | 確信度 | type | category | origin |
|---|---|---|---|---|---|---|---|---|
| AIND-D05912 | TMP-P-NEW107-01 | TMP_NEW_B107.tsv:1 | TSV 登録の TMP-P-NEW107-01（النور أبو الحسن علي بن الكمال أبي البركات محمد بن الجمال أبي السعود محمد بن حسين بن علي بن أحمد بن عطية بن ظهيرة القرشي المكي）がどの XML の ref 属性でも未使用（note 本文でのみ言及: ['AIND-D05912']） | XML の placeName 等で ref として使うか（規則22-2: 原文に明記された施設名は placeName に）、TSV 行を取り下げる | L | id_assignment | FP | claude_review |
| AIND-D05950 | TMP-P-NEW108-06 | TMP_NEW_B108.tsv:6 | TSV 登録の TMP-P-NEW108-06（محمد بن الشيخ حسين بن حسن الفتحي المكي）がどの XML の ref 属性でも未使用（note 本文でのみ言及: ['AIND-D05950']） | XML の placeName 等で ref として使うか（規則22-2: 原文に明記された施設名は placeName に）、TSV 行を取り下げる | L | id_assignment | FP | claude_review |
| AIND-D05883,AIND-D05951 | TMP-P-NEW108-07 | TMP_NEW_B108.tsv:7 | TSV 登録の TMP-P-NEW108-07（طلحة العنبري）がどの XML の ref 属性でも未使用（note 本文でのみ言及: ['AIND-D05883', 'AIND-D05951']） | XML の placeName 等で ref として使うか（規則22-2: 原文に明記された施設名は placeName に）、TSV 行を取り下げる | L | id_assignment | FP | claude_review |
| AIND-D05951 | TMP-P-NEW108-09 | TMP_NEW_B108.tsv:9 | TSV 登録の TMP-P-NEW108-09（التقي إبراهيم بن محمد بن مفلح الحنبلي）がどの XML の ref 属性でも未使用（note 本文でのみ言及: ['AIND-D05951']） | XML の placeName 等で ref として使うか（規則22-2: 原文に明記された施設名は placeName に）、TSV 行を取り下げる | L | id_assignment | FP | claude_review |
| AIND-D05848 | TMP-P-NEW105-04 | TMP_NEW_B104.tsv:2 ⇔ TMP_NEW_B105.tsv:4 | チャンク間で同一実体の仮 TMP が二重発行の疑い: TMP-P-NEW104-02「دولات باي (أيام الظاهر جقمق، كان له حسن اعتقاد في عمر البطايني)」（B104）⇔ TMP-P-NEW105-04「دولات باي المؤيدي (والد عمر)」（B105）、共通語 ['باي', 'دولات'] | 一方に統合（TMP-P-NEW104-02 を残し TMP-P-NEW105-04 の XML 参照を差し替え、TSV 行を取り下げ） | M | id_assignment | substitution | claude_review |
| TMP-P-NEW108-07 | TMP-P-NEW108-07 | TMP_NEW_B106.tsv:4 ⇔ TMP_NEW_B108.tsv:7 | チャンク間で同一実体の仮 TMP が二重発行の疑い: TMP-P-NEW106-04「الشيخ طلحة العنبري البعلي」（B106）⇔ TMP-P-NEW108-07「طلحة العنبري」（B108）、共通語 ['العنبري', 'طلحه']。発行側 Note に「同番号を使用願う」の申し送りがあるのに別番号が切られている | 一方に統合（TMP-P-NEW106-04 を残し TMP-P-NEW108-07 の XML 参照を差し替え、TSV 行を取り下げ） | H | id_assignment | substitution | claude_review |

### 16. 汎用名 TMP-P の「⚠汎用名」明記 — 点検 39 件中 違反 7 件

| entry | ファイル | 箇所 | 内容（根拠） | 修正案 | 確信度 | type | category | origin |
|---|---|---|---|---|---|---|---|---|
| AIND-D05839 | TMP-P-NEW105-02 | TMP_NEW_B105.tsv:2 | 汎用名（ナサブ連結1・ニスバ等1、識別称号なし）「الحسين بن بوبان الغزي」の Note に「⚠汎用名。同名別人への流用禁止」がない | Note に明記（規則3） | L | id_assignment | FN | claude_review |
| AIND-D05883,AIND-D05951 | TMP-P-NEW106-04 | TMP_NEW_B106.tsv:4 | 汎用名（ナサブ連結0・ニスバ等2、識別称号なし）「الشيخ طلحة العنبري البعلي ｜ الفقيه طلحة」の Note に「⚠汎用名。同名別人への流用禁止」がない | Note に明記（規則3） | L | id_assignment | FN | claude_review |
| AIND-D05922 | TMP-P-NEW107-04 | TMP_NEW_B107.tsv:4 | 汎用名（ナサブ連結0・ニスバ等1、識別称号なし）「الديروطي المقرئ (شيخ عمر بن قاسم النشار في القراءات)」の Note に「⚠汎用名。同名別人への流用禁止」がない | Note に明記（規則3） | L | id_assignment | FN | claude_review |
| AIND-D05922 | TMP-P-NEW107-05 | TMP_NEW_B107.tsv:5 | 汎用名（ナサブ連結1・ニスバ等1、識別称号なし）「ابن عمران المقرئ (شيخ عمر بن قاسم النشار)」の Note に「⚠汎用名。同名別人への流用禁止」がない | Note に明記（規則3） | L | id_assignment | FN | claude_review |
| AIND-D05923 | TMP-P-NEW107-07 | TMP_NEW_B107.tsv:7 | 汎用名（ナサブ連結1・ニスバ等1、識別称号なし）「أبو القسم بن معيبد (اليمني التعزي)」の Note に「⚠汎用名。同名別人への流用禁止」がない | Note に明記（規則3） | L | id_assignment | FN | claude_review |
| AIND-D05932 | TMP-P-NEW108-02 | TMP_NEW_B108.tsv:2 | 汎用名（ナサブ連結1・ニスバ等1、識別称号なし）「أحمد بن علي الجزري」の Note に「⚠汎用名。同名別人への流用禁止」がない | Note に明記（規則3） | L | id_assignment | FN | claude_review |
| TMP-P-NEW108-07 | TMP-P-NEW108-07 | TMP_NEW_B108.tsv:7 | 汎用名（ナサブ連結0・ニスバ等1、識別称号なし）「طلحة العنبري」の Note に「⚠汎用名。同名別人への流用禁止」がない | Note に明記（規則3） | L | id_assignment | FN | claude_review |

### 17. xml:lang・en 訳の英語性・ja 訳の混入物・placeName ref 位置 — 点検 775 件中 違反 0 件

違反なし。

### 18. 規則22（原文にない placeName・空 residence） — 点検 140 件中 違反 0 件

違反なし。

### 19. relation 整合（本項主・self・向き・相互矛盾・possible_identity 双方向・「ممن سمع مني」型の向き） — 点検 238 件中 違反 0 件

違反なし。

### 20. 校閲前 orig との要素数比較 — 点検 100 件中 違反 0 件

違反なし。

### 21. 規則24 FIXLOG の書式・語彙・件数 — 点検 489 件中 違反 0 件

違反なし。

### 22. 「أرخه ابن فهد」振り分け（没年⇔D09211/D05979/D03985・cert） — 点検 9 件中 違反 1 件

| entry | ファイル | 箇所 | 内容（根拠） | 修正案 | 確信度 | type | category | origin |
|---|---|---|---|---|---|---|---|---|
| AIND-D05822 | AIND-D05822_300454785611.xml | event mention persName | ابن فهد 振り分け不一致: 没年 when-custom=0865-11 に対し cert=None（期待 low） | ref="#AIND-D09211" cert="low" | M | id_assignment | substitution | claude_review |

## 違反としなかった機械所見（要点）と、違反の補足（B104-108）

- **[2] REF 11件**: target はすべて corpus_index に実在する実項。転送先が本バッチ内・repo のどちらでも REF になっている例はない。D05827 は最終転送先の D06040 を target にしている（経由先 D05811 は REF）。D05943→D06001 は、ブリーフ案の D05942 を校閲者が採らなかったもの（転送先が妥当かは内容検証で判断）。nisbah persName は残っていない。name_only は揃っておらず、D05878・D05888・D05892 だけが name_only を残している（ほか8件は full のみ）。違反には数えないが、集約時に統一するとよい。
- **[3] 連結レコード**: 一般ロジックで100件の原文末尾を走査した（「. <見出し名> … (مضى|يأتي|في …|فيمن …|هو ابن …)」で終わる独立文。「له ذكر في」は本伝の一部なので除外）。**検出は 0 件**で、校閲者の報告（該当なし）と一致する。末尾が「وله ذكر في ابنه」で終わる D05872 と「وأظنه ابن عم … الآتي」で終わる D05923 は本文の一部であり、連結ではない。source note 100件は corpus と全件一致した（立項連番込み・空白正規化後）。
- **[4] 日付**: 日付属性 310 件を h2g.py で全件換算した。違反は D05923 の1件だけ。死亡 when-custom=0837（年のみ）に対して @when=1434 になっている。原文は「آخر سنة سبع وثلاثين」で、校閲者は年末が 1434 側に落ちることを根拠に、規則18（年のみ→年初＝1433）から意図的に外している。規則の機械的な形とは食い違うので M とし、裁定を求める（年精度のまま @when=1433 にして note で年末を示すか、notBefore/notAfter で年末側を表すか）。notBefore/notAfter が日精度で when-custom が年・月精度という組み合わせが 8 件ある（D05839・D05870・D05871・D05872）。換算値はすべて正しく、規則18 の精度規定は @when が対象で、「notAfter 年精度→年末」の慣行もあるので違反に数えていない。曜日の記述がある4件（D05873 土・D05903 水 は一致、D05926 月/換算日、D05937「ليلة الخميس」/換算水）は、ずれが ±1 日の範囲に収まる（ليلة は前夜）。ヒジュラ年が @when に混入した例は 0 件。
- **[5]** full の「بن القاضي…」「بن الأمير…」（父の称号）と「بن قاضي القضاة」はナサブの一部として除外した（D05840・D05872・D05882・D05926）。残る L 4件（D05921 الأمير／D05922 المقرئ／D05923 القاضي／D05836 المعروف بـ）は本人の称号・職名句・通称句で、見出しをそのまま full にしたもの。M の D05859 name_only 4世代「عمر بن عبد الرحمن بن أبي بكر بن أبي بكر」は初版からの残り（祖父と曽祖父が同名なので、3世代で切ると「… بن أبي بكر」で止まる）。
- **[10]** 毒 wd の属性使用は 0/217 件。学派 wd（Q82245・Q48221・Q233387・Q228986）は ID-Master には無いが repo に既出。wd:Q4165175（الكشاف、D05905）は ID-Master に未登録だが repo に既出で、ISSUES_B107 §D107-3 に「未照合」として記録されている。wd:Q1283（بحر الهند）は XML から除かれて TMP-L-NEW107-01 になっており、§D107-1 に「未確認」として記録がある。wd:Q4120093（ابن الجزري）は ID-Master に「要確認」印つきで登録されており、D05857・D05872（B105）、D05923（B107、§D107-10）、D05933（B108、ISSUES に記載）で使われている。B105 の2件は ISSUES に記載がない（違反ではない。集約時に §D107-10 とまとめて照合すればよい）。
- **[11]** 汚染・幻番号（000530／000204／000490／000529／000064／000664／000416、幻 000352／000003／000762／000573／000707／000360／000034／000035／000277 ほか）の残存は 0 件。TMP-P-000347（زينب ابنة الكمال）は D05932 で師として使われているが、ID-Master の登録名と原文「أحضر على زينب ابنة الكمال」が一致するので適合とした。要注意の Office 番号 TMP-O-00012（D05813 العطار）と TMP-O-00108（D05946 الحكيم＝طبيب）はどちらも Office の位置で使われている（実体が一致するかは内容検証で確認）。カテゴリ位置の不適合と TMP-N の person 位置への流用は 0 件（D05922 の TMP-N-00346 は TMP-P-NEW107-04 に差し替え済み、D05905 の bibl TMP-I-00047・D05951 の bibl TMP-P-000008 も是正済み）。
- **[12]** 規約A 違反は 0/219 件。D05932 の maternal_aunt は親族として扱った（@n なし）。
- **[14]** 統制外の値は D05932 の relation subtype「maternal_aunt」の1件だけ（repo に先例なし）。ISSUES_B108 に新設として記載があるので L。低頻度の値（associate 1件・neighbor 2件・event meeting 1件）は参考所見とした。
- **[15]** 仮 TMP は 77 行（P 39・I 10・L 9・O 7・T 9・N 3）。ID-Master との正規化一致は 0 件。並行追加行（8007〜8082、76 行）との語の重なりは機械が 8 組拾ったが、どれも共通語が一般語（الكمال／المكي／السراج／عمر／بكر 等）だけで、ナサブが食い違うので別実体と判断した。**チャンク間の重複は2組を違反とした**。(1) **H: TMP-P-NEW106-04「الشيخ طلحة العنبري البعلي」（B106、D05883）⇔ TMP-P-NEW108-07「طلحة العنبري」（B108、D05951）**。B106 の TSV Note と ISSUES §D106-5 で「B108 D05951 でも同番号を使用願う」と申し送りがあったのに、B108 が別の番号を切っている。(2) M: TMP-P-NEW104-02「دولات باي」（B104、D05812。ジャクマク期の人物）⇔ TMP-P-NEW105-04「دولات باي المؤيدي」（B105、D05848 の父）。どちらも「⚠汎用名」の明記があるので、同一人物かどうかは内容検証で判断すること（別人なら違反を取り下げてよい）。XML で使われている仮番号はすべて TSV に登録されている。逆に TSV にあって XML の ref で使われていないのは TMP-L-NEW107-03（الكبش、D05922 の note でのみ言及。施設 TMP-I-NEW107-06「مدرسة قانم بالكبش」に地名を含めた形）の1件。TSV は全行7列。
- **[16]** 「名＋父名＋ニスバ1つ以下」または「ニスバ・通称のみ」で、識別に使える称号・職名を欠く TMP-P のうち、Note に「⚠汎用名」がない7件を L とした。称号・職名・複数ニスバで識別できるもの（NEW105-01・NEW106-01・NEW107-03／06／08／11・NEW108-03／08）は対象外とした。
- **[17]** en 訳に日本語・アラビア文字が混入した例、ja 訳の「ビン」・内部ID・立項連番の残存は 0 件（D05889「324」・D05932「365番」は除去済み）。M の2件（D05839 بوبان、D05871 عياذ）は、原文の綴り注記（「بموحدتين أولاهما مضمومة」型）を訳すためにアラビア文字を括弧書きで残したもの。規則上は生アラビア語にあたるが、訳の内容としては妥当なので、カナ＋ローマ字の説明に置き換えるかどうかは裁定に委ねる。
- **[18]** 原文に現れない placeName は5件で、すべて「حج」に付けた مكة（規則20 の例外）なので違反は 0 件。中身が除去 note だけの residence も 0 件。
- **[19]** relation 234 本（سمع مني 型 16 件を含む）で、本項主の欠落・self-relation・親族関係の向きの逆転・相互矛盾はどれも 0 件。repo 側と閉合している親族は10組（D00594・D05080・D03621・D03945・D03969・D04519・D04520・D07677・D04574・D03713）。「ممن سمع مني」型16件はすべて active=wd:Q4120128・passive=本項主の向き（付表）。D05825「سمع علي」（＝私に）、D05837「سمع مني معهم」も同じ形で符号化されている。possible_identity は本バッチでは 0 本。**相手名の desc がない relation が B108 に偏っている**（B104 9/31、B105 6/52、B106 0/34、B107 5/55、B108 21/47）。規則31 は「desc は相手名のみ」と定めるだけで desc の欠落は違反ではないが、TMP 相手の師弟 relation は note だけでは名前が分からないので、集約時に揃えるとよい。D05858 には「teacher（active=本項主・passive=息子 D03945、اشتغل、cert medium）」と「son」が併存している（本項主は息子の師でもあるという読み。当否は内容検証で）。
- **[20]** 実伝要素が大きく減ったのは D05921（7→4、職を「نائب قلعة حلب」1件に統合）の1件で、REVIEW_NOTES_B107 に理由がある。affiliation の減少16件は、学派と施設の二重符号化（規則8）と原文に根拠のないものを除いたもので、death の減少は 0 件。D05853 の birth 1→0 は、10歳未満で死んだ記述から生年を逆算していた初版を除去したもの（REVIEW_NOTES_B105）。
- **[21]** FIXLOG は5チャンク計 489 行で、書式・語彙の違反は 0 件、batch_id は全行 B104-108。FIXLOG に1行もないのに assertion 要素が変わった entry も 0 件。
- **[22]** 「أرخه／ذكره／أفاده ابن فهد」「بيض له ابن فهد」「في معجمه」の9件はすべて規則どおり（付表）。没年>885（D03985）の項はない。D05929 は「أجاز لابن شيخنا وابن فهد وذكره في معجمه」で、Pattern A mention（D09211）に加えて、本項主→D09211 のイジャーザ relation（815年）がある。815年の受給者が التقي بن فهد（787年生）か、ほかの ابن فهد（النجم عمر は812年生）かは内容検証で確認すること。D05946「كتب عنه العز بن فهد」→D03985 と D05859「ذكره التقي بن فهد في معجمه」は名前が明示されているので、振り分け規則の対象外とした。


## 付表: 校閲前 orig と校閲後の要素数（20）

実伝要素 = relation+event+state+death+birth+affiliation。値は orig→校閲後。

| entry | chunk | REF | 実伝要素 | relation | event | state | death | birth | affil. | placeName | 全要素 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| AIND-D05803 | B104 |  | 4→4 | 1→1 | 2→2 | 0→0 | 1→1 | 0→0 | 0→0 | 3→2 | 25→33 |
| AIND-D05805 | B104 |  | 3→3 | 1→1 | 2→2 | 0→0 | 0→0 | 0→0 | 0→0 | 2→2 | 18→26 |
| AIND-D05811 | B104 | REF | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 12→16 |
| AIND-D05812 | B104 |  | 5→4 | 3→1 | 1→0 | 0→1 | 0→1 | 0→0 | 1→1 | 1→0 | 26→29 |
| AIND-D05813 | B104 |  | 7→8 | 4→5 | 2→1 | 1→2 | 0→0 | 0→0 | 0→0 | 2→1 | 30→43 |
| AIND-D05816 | B104 |  | 3→2 | 1→1 | 2→1 | 0→0 | 0→0 | 0→0 | 0→0 | 2→1 | 21→25 |
| AIND-D05819 | B104 |  | 4→4 | 3→3 | 1→1 | 0→0 | 0→0 | 0→0 | 0→0 | 1→1 | 22→34 |
| AIND-D05820 | B104 |  | 4→3 | 2→2 | 2→1 | 0→0 | 0→0 | 0→0 | 0→0 | 2→1 | 23→29 |
| AIND-D05822 | B104 |  | 8→10 | 4→5 | 1→2 | 2→2 | 1→1 | 0→0 | 0→0 | 4→4 | 38→63 |
| AIND-D05824 | B104 |  | 3→2 | 1→1 | 2→1 | 0→0 | 0→0 | 0→0 | 0→0 | 2→1 | 19→24 |
| AIND-D05825 | B104 |  | 2→2 | 1→1 | 1→1 | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 17→23 |
| AIND-D05826 | B104 |  | 7→5 | 3→3 | 3→1 | 0→0 | 0→0 | 0→0 | 1→1 | 3→1 | 35→36 |
| AIND-D05827 | B104 | REF | 1→0 | 1→0 | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 14→16 |
| AIND-D05828 | B104 | REF | 1→0 | 1→0 | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 13→16 |
| AIND-D05829 | B104 | REF | 1→0 | 1→0 | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 17→16 |
| AIND-D05830 | B104 |  | 2→2 | 1→1 | 0→0 | 0→0 | 0→0 | 0→0 | 1→1 | 0→0 | 15→23 |
| AIND-D05832 | B104 |  | 6→5 | 2→2 | 2→1 | 0→0 | 1→1 | 1→1 | 0→0 | 3→4 | 27→42 |
| AIND-D05836 | B104 |  | 6→6 | 3→2 | 2→2 | 0→1 | 1→1 | 0→0 | 0→0 | 6→5 | 31→47 |
| AIND-D05837 | B104 |  | 3→3 | 3→2 | 0→0 | 0→1 | 0→0 | 0→0 | 0→0 | 0→0 | 23→34 |
| AIND-D05838 | B104 | REF | 1→0 | 1→0 | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 14→16 |
| AIND-D05839 | B105 |  | 7→7 | 4→4 | 1→0 | 1→1 | 0→0 | 0→1 | 1→1 | 2→1 | 30→45 |
| AIND-D05840 | B105 |  | 8→9 | 4→5 | 2→2 | 0→0 | 1→1 | 0→0 | 1→1 | 2→2 | 32→45 |
| AIND-D05844 | B105 |  | 3→3 | 1→1 | 0→0 | 1→1 | 1→1 | 0→0 | 0→0 | 1→1 | 20→29 |
| AIND-D05847 | B105 |  | 3→2 | 1→1 | 2→1 | 0→0 | 0→0 | 0→0 | 0→0 | 2→1 | 18→23 |
| AIND-D05848 | B105 |  | 1→2 | 0→1 | 0→0 | 0→0 | 1→1 | 0→0 | 0→0 | 0→0 | 13→23 |
| AIND-D05851 | B105 |  | 3→2 | 1→1 | 2→1 | 0→0 | 0→0 | 0→0 | 0→0 | 2→1 | 20→24 |
| AIND-D05852 | B105 |  | 4→4 | 2→1 | 0→1 | 0→0 | 1→1 | 0→0 | 1→1 | 2→2 | 22→36 |
| AIND-D05853 | B105 |  | 4→3 | 1→1 | 0→1 | 0→0 | 1→1 | 1→0 | 1→0 | 2→2 | 22→29 |
| AIND-D05854 | B105 |  | 5→6 | 1→2 | 0→0 | 2→3 | 0→0 | 0→0 | 2→1 | 0→0 | 25→43 |
| AIND-D05855 | B105 |  | 3→2 | 1→1 | 2→1 | 0→0 | 0→0 | 0→0 | 0→0 | 2→1 | 20→24 |
| AIND-D05856 | B105 |  | 3→4 | 1→1 | 0→1 | 1→1 | 1→1 | 0→0 | 0→0 | 3→1 | 22→37 |
| AIND-D05857 | B105 |  | 3→3 | 1→1 | 2→2 | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 20→29 |
| AIND-D05858 | B105 |  | 5→7 | 2→3 | 0→0 | 0→1 | 1→1 | 1→1 | 1→1 | 0→0 | 22→40 |
| AIND-D05859 | B105 |  | 2→2 | 2→1 | 0→1 | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 20→33 |
| AIND-D05860 | B105 |  | 1→1 | 0→0 | 0→0 | 0→0 | 1→1 | 0→0 | 0→0 | 0→0 | 14→20 |
| AIND-D05868 | B105 |  | 9→10 | 6→6 | 2→2 | 0→0 | 0→1 | 0→0 | 1→1 | 1→1 | 32→58 |
| AIND-D05869 | B105 |  | 7→8 | 1→2 | 5→5 | 0→0 | 1→1 | 0→0 | 0→0 | 6→3 | 30→41 |
| AIND-D05870 | B105 |  | 10→9 | 4→5 | 4→2 | 0→0 | 0→0 | 1→1 | 1→1 | 4→1 | 41→48 |
| AIND-D05871 | B105 |  | 8→10 | 3→6 | 3→1 | 0→1 | 1→1 | 0→0 | 1→1 | 1→0 | 28→54 |
| AIND-D05872 | B105 |  | 18→16 | 8→10 | 5→3 | 1→1 | 1→1 | 1→1 | 2→0 | 10→8 | 61→87 |
| AIND-D05873 | B106 |  | 2→2 | 1→0 | 0→1 | 0→0 | 1→1 | 0→0 | 0→0 | 4→4 | 22→28 |
| AIND-D05874 | B106 |  | 6→7 | 2→3 | 2→2 | 0→0 | 1→1 | 1→1 | 0→0 | 0→0 | 24→42 |
| AIND-D05875 | B106 |  | 2→2 | 1→0 | 0→1 | 0→0 | 1→1 | 0→0 | 0→0 | 2→2 | 19→25 |
| AIND-D05876 | B106 |  | 6→5 | 3→3 | 2→1 | 0→0 | 1→1 | 0→0 | 0→0 | 4→3 | 30→37 |
| AIND-D05877 | B106 |  | 1→1 | 0→0 | 0→0 | 0→0 | 1→1 | 0→0 | 0→0 | 0→0 | 15→21 |
| AIND-D05878 | B106 | REF | 1→0 | 1→0 | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 14→17 |
| AIND-D05882 | B106 |  | 4→3 | 0→2 | 3→0 | 0→0 | 1→1 | 0→0 | 0→0 | 5→4 | 28→34 |
| AIND-D05883 | B106 |  | 18→19 | 9→9 | 5→6 | 1→1 | 1→1 | 1→1 | 1→1 | 8→7 | 61→85 |
| AIND-D05884 | B106 |  | 13→12 | 5→5 | 4→2 | 2→3 | 1→1 | 0→0 | 1→1 | 3→1 | 44→60 |
| AIND-D05886 | B106 |  | 5→5 | 2→1 | 1→2 | 0→0 | 1→1 | 1→1 | 0→0 | 3→1 | 28→35 |
| AIND-D05887 | B106 |  | 5→5 | 0→0 | 1→2 | 0→0 | 1→1 | 0→0 | 3→2 | 1→0 | 23→35 |
| AIND-D05888 | B106 | REF | 1→0 | 1→0 | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 14→17 |
| AIND-D05889 | B106 |  | 5→6 | 3→1 | 1→4 | 0→0 | 1→1 | 0→0 | 0→0 | 3→1 | 28→38 |
| AIND-D05891 | B106 |  | 6→6 | 3→3 | 1→0 | 0→0 | 0→1 | 1→1 | 1→1 | 1→0 | 30→39 |
| AIND-D05892 | B106 | REF | 1→0 | 1→0 | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 14→17 |
| AIND-D05894 | B106 |  | 3→2 | 1→1 | 2→1 | 0→0 | 0→0 | 0→0 | 0→0 | 2→1 | 22→27 |
| AIND-D05899 | B106 |  | 4→4 | 0→0 | 1→1 | 1→2 | 1→1 | 0→0 | 1→0 | 4→1 | 27→40 |
| AIND-D05900 | B106 |  | 1→1 | 1→1 | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 14→21 |
| AIND-D05901 | B106 |  | 5→5 | 1→1 | 1→1 | 2→2 | 1→1 | 0→0 | 0→0 | 3→0 | 29→37 |
| AIND-D05902 | B106 |  | 9→9 | 4→4 | 2→2 | 1→1 | 0→0 | 0→0 | 2→2 | 3→3 | 34→55 |
| AIND-D05903 | B107 |  | 9→9 | 1→2 | 0→0 | 1→1 | 1→1 | 1→1 | 5→4 | 0→0 | 36→53 |
| AIND-D05904 | B107 |  | 8→8 | 3→3 | 2→2 | 1→1 | 1→1 | 0→0 | 1→1 | 3→2 | 32→44 |
| AIND-D05905 | B107 |  | 16→10 | 5→3 | 4→2 | 2→3 | 1→1 | 0→0 | 4→1 | 6→1 | 60→62 |
| AIND-D05907 | B107 |  | 3→2 | 1→1 | 2→1 | 0→0 | 0→0 | 0→0 | 0→0 | 2→1 | 18→23 |
| AIND-D05908 | B107 |  | 7→6 | 4→4 | 2→1 | 0→0 | 1→1 | 0→0 | 0→0 | 2→1 | 29→44 |
| AIND-D05911 | B107 |  | 13→10 | 4→4 | 4→4 | 2→1 | 0→0 | 1→1 | 2→0 | 7→5 | 55→61 |
| AIND-D05912 | B107 |  | 5→7 | 3→4 | 0→1 | 0→0 | 1→1 | 1→1 | 0→0 | 2→0 | 25→45 |
| AIND-D05913 | B107 |  | 4→3 | 0→0 | 0→0 | 2→2 | 1→1 | 0→0 | 1→0 | 1→0 | 26→30 |
| AIND-D05914 | B107 |  | 3→3 | 1→0 | 0→1 | 1→1 | 1→1 | 0→0 | 0→0 | 0→0 | 22→30 |
| AIND-D05915 | B107 |  | 1→1 | 0→0 | 0→0 | 0→0 | 1→1 | 0→0 | 0→0 | 0→0 | 14→21 |
| AIND-D05917 | B107 |  | 4→4 | 2→2 | 1→1 | 0→0 | 1→1 | 0→0 | 0→0 | 0→0 | 20→31 |
| AIND-D05920 | B107 |  | 9→9 | 6→4 | 1→1 | 0→1 | 1→1 | 0→1 | 1→1 | 0→0 | 32→55 |
| AIND-D05921 | B107 |  | 7→4 **↓** | 2→2 | 1→0 | 2→1 | 1→1 | 0→0 | 1→0 | 5→2 | 39→35 |
| AIND-D05922 | B107 |  | 17→17 | 9→9 | 4→5 | 2→2 | 0→0 | 0→0 | 2→1 | 6→5 | 67→101 |
| AIND-D05923 | B107 |  | 8→11 | 2→3 | 3→5 | 2→2 | 1→1 | 0→0 | 0→0 | 9→3 | 43→64 |
| AIND-D05924 | B107 | REF | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 11→16 |
| AIND-D05926 | B107 |  | 5→8 | 1→1 | 0→3 | 1→1 | 1→1 | 1→1 | 1→1 | 7→3 | 31→49 |
| AIND-D05928 | B107 |  | 7→8 | 4→3 | 3→4 | 0→0 | 0→1 | 0→0 | 0→0 | 0→0 | 33→45 |
| AIND-D05929 | B107 |  | 11→13 | 8→7 | 3→4 | 0→1 | 0→1 | 0→0 | 0→0 | 0→0 | 48→74 |
| AIND-D05930 | B107 |  | 7→8 | 3→3 | 1→2 | 1→1 | 1→1 | 1→1 | 0→0 | 4→1 | 39→52 |
| AIND-D05931 | B108 |  | 7→8 | 2→3 | 3→3 | 1→1 | 0→0 | 1→1 | 0→0 | 6→6 | 35→49 |
| AIND-D05932 | B108 |  | 9→11 | 5→7 | 1→1 | 0→0 | 1→1 | 1→1 | 1→1 | 2→2 | 36→62 |
| AIND-D05933 | B108 |  | 7→11 | 6→6 | 0→3 | 0→0 | 1→1 | 0→1 | 0→0 | 0→0 | 37→66 |
| AIND-D05937 | B108 |  | 5→5 | 1→1 | 1→1 | 2→2 | 1→1 | 0→0 | 0→0 | 5→2 | 33→40 |
| AIND-D05938 | B108 |  | 2→4 | 0→3 | 1→0 | 1→1 | 0→0 | 0→0 | 0→0 | 1→0 | 17→36 |
| AIND-D05939 | B108 |  | 7→8 | 3→4 | 2→0 | 1→2 | 1→1 | 0→1 | 0→0 | 2→0 | 36→49 |
| AIND-D05940 | B108 |  | 5→5 | 2→1 | 1→2 | 1→1 | 1→1 | 0→0 | 0→0 | 4→2 | 29→44 |
| AIND-D05941 | B108 |  | 6→5 | 4→3 | 2→2 | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 25→38 |
| AIND-D05942 | B108 |  | 5→9 | 0→1 | 4→6 | 0→0 | 1→1 | 0→1 | 0→0 | 7→6 | 34→54 |
| AIND-D05943 | B108 | REF | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 12→16 |
| AIND-D05944 | B108 |  | 11→9 | 4→4 | 1→0 | 2→3 | 1→1 | 0→0 | 3→1 | 3→0 | 46→55 |
| AIND-D05946 | B108 |  | 4→5 | 1→0 | 2→2 | 0→1 | 0→1 | 0→0 | 1→1 | 0→0 | 25→41 |
| AIND-D05947 | B108 |  | 6→5 | 2→2 | 3→1 | 0→1 | 1→1 | 0→0 | 0→0 | 5→0 | 33→39 |
| AIND-D05948 | B108 |  | 2→2 | 1→1 | 1→1 | 0→0 | 0→0 | 0→0 | 0→0 | 1→1 | 18→25 |
| AIND-D05950 | B108 |  | 4→5 | 2→3 | 1→1 | 0→0 | 0→0 | 1→1 | 0→0 | 3→3 | 24→39 |
| AIND-D05951 | B108 |  | 16→15 | 6→7 | 7→4 | 1→2 | 0→0 | 1→1 | 1→1 | 10→6 | 66→79 |
| AIND-D05952 | B108 | REF | 2→0 | 2→0 | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 17→16 |
| AIND-D05953 | B108 |  | 5→5 | 3→4 | 1→0 | 1→1 | 0→0 | 0→0 | 0→0 | 2→0 | 26→32 |
| AIND-D05954 | B108 |  | 1→2 | 0→0 | 0→0 | 0→1 | 1→1 | 0→0 | 0→0 | 2→2 | 17→26 |
| AIND-D05955 | B108 |  | 1→1 | 0→0 | 1→1 | 0→0 | 0→0 | 0→0 | 0→0 | 0→0 | 14→20 |
| **計** | | | 525→523 | 223→223 | 142→131 | 43→59 | 51→57 | 18→22 | 48→31 | 224→130 | 2732→3830 |

## 付表: 「أرخه ابن فهد」振り分け（22）

規則: 「في معجمه」→D09211／没年>885→D03985／871<没年≤885→D05979（cert medium）／≤871・不明→D09211（cert low）。cert は event か persName の値。

| entry | 原文句 | death when-custom | 付与 ref・cert | 期待 | 判定 |
|---|---|---|---|---|---|
| AIND-D05803 | أرخه ابن فهد | 0863-06 | #AIND-D09211 low | #AIND-D09211 low | OK |
| AIND-D05822 | أرخه ابن فهد | 0865-11 | #AIND-D09211 low; #AIND-D09211 - | #AIND-D09211 low | NG |
| AIND-D05836 | فن بها وفجع به أبوه أرخه ابن فهد | 0868-08 | #AIND-D09211 low | #AIND-D09211 low | OK |
| AIND-D05873 | ذكره ابن فهد | 0841-10-09 | #AIND-D09211 low | #AIND-D09211 low | OK |
| AIND-D05875 | أرخه ابن فهد | 0855-01 | #AIND-D09211 low | #AIND-D09211 low | OK |
| AIND-D05889 | أفاده ابن فهد | 0827 | #AIND-D09211 low | #AIND-D09211 low | OK |
| AIND-D05929 | الأبي وأجاز لابن شيخنا وابن فهد وذكره في معجمه وآخرين في | 0815 | #AIND-D09211 -; #AIND-D09211 - | #AIND-D09211  | OK |
| AIND-D05940 | أرخه ابن فهد | 0861-05 | #AIND-D09211 low | #AIND-D09211 low | OK |
| AIND-D05941 | ست وثلاثين جماعة وبيض له ابن فهد | — | #AIND-D09211 low | #AIND-D09211 low | OK |

## 付表: possible_identity（19）

| entry | 相手 | cert | 相手ファイル | 同じ相手への他 relation |
|---|---|---|---|---|

## 付表: 「ممن سمع مني／لازمني／سمع علي」型（19b）

| entry | 原文句 | relation（active=wd:Q4120128, passive=本項主） | relation 内 placeName |
|---|---|---|---|
| AIND-D05805 | ممن سمع مني | teacher | مكة |
| AIND-D05813 | ممن سمع مني | teacher | مكة |
| AIND-D05816 | ممن سمع مني | teacher | القاهرة |
| AIND-D05820 | ممن سمع مني | teacher | مكة |
| AIND-D05824 | ممن سمع مني | teacher | مكة |
| AIND-D05825 | سمع علي | teacher | — |
| AIND-D05837 | سمع مني | teacher | — |
| AIND-D05847 | ممن سمع مني | teacher | مكة |
| AIND-D05851 | ممن سمع مني | teacher | مكة |
| AIND-D05855 | ممن سمع مني | teacher | القاهرة |
| AIND-D05870 | لازمني | teacher, teacher | المدينة |
| AIND-D05876 | سمع علي | teacher | مكة |
| AIND-D05894 | ممن سمع مني | teacher | القاهرة |
| AIND-D05907 | ممن سمع مني | teacher | مكة |
| AIND-D05948 | ممن سمع مني | teacher | القاهرة |

## 付表: FIXLOG 件数（21）

| chunk | 行数 | 記録のある entry / 担当 | 記録なし entry | FP/FN/sub | H/M/L | resolution |
|---|---|---|---|---|---|---|
| B104 | 78 | 20/20 | — | 32/26/20 | 19/35/24 | {'fixed': 77, 'issue': 1} |
| B105 | 103 | 20/20 | — | 27/26/50 | 21/45/37 | {'fixed': 103} |
| B106 | 108 | 20/20 | — | 25/16/67 | 29/38/41 | {'fixed': 108} |
| B107 | 99 | 19/20 | AIND-D05915 | 22/37/40 | 26/44/29 | {'fixed': 98, 'issue': 1} |
| B108 | 101 | 19/20 | AIND-D05948 | 29/24/48 | 11/51/39 | {'fixed': 96, 'issue': 5} |
| 計 | 489 | | | | | |
