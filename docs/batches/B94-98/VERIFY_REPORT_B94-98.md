# VERIFY_REPORT B94-98（独立検証パス・集約、2026-10-03）

対象: `docs/_work/B94-98_incoming/B94-98/` 100件（B94〜B98 各20件、`AIND-D04738`〜`D04953`、実項 96・REF 4）。
**パイプライン v3**（`docs/精度検証/精度指標_定義書_20260926.md` §7）: チャンク校閲 claude-fable-5-1 ×5 → 内容検証 claude-opus-5 ×2（A＝B94・B95・B97、B＝B96・B98）＋機械検査 claude-opus-5（21項目、`docs/_work/B94-98_incoming/verify/`）→ 集約・自己裁定 claude-fable-5-1（`裁定反映_20261003.md`）。
出典: `VERIFY_REPORT_content_A.md`／`VERIFY_REPORT_content_B.md`／`VERIFY_REPORT_mech.md`（再実行 `VERIFY_REPORT_mech_after.md`）、`FINDINGS_content_A.tsv`（31行）・`FINDINGS_content_B.tsv`（46行）・`FINDINGS_mech.tsv`（17行）。集約後の resolution を付けた統合版 `FINDINGS_all_resolved.tsv`（94行、fixed 79／rejected 15）。

## 1. 検証の分母（定義書 §5）
| 列 | 値 | 出典 |
|---|---|---|
| batch_id / review_date / pipeline_version / n_entries | B94-98 / 2026-10-03 / v3 / 100 |  |
| draft_model / verify_model / aggregator_model | claude-fable-5-1 / content=claude-opus-5;mech=claude-opus-5 / claude-fable-5-1 |  |
| n_assertions_checked（内容検証） | **約 1,325**（A 約745＝relation 116・event 52・state 34・affiliation 12・birth 11・death 39・日付属性 58・placeName 71・persName 232・訳文 120、別途 ID 参照 509／B 約580＝relation 112・event 52・state 31・affiliation 12・placeName 54・persName 167・birth/death 32・日付属性 44・訳文 80） | content A §1、content B §0 |
| n_assertions_checked（機械検査） | 約 7,178（ID参照 1006・relation 228・日付属性 298・placeName 167・persName 197・type語彙 1234・TMP_NEW 62行・FIXLOG 479行ほか。項目間で重複計上） | mech 総括 |
| 校閲者が付けた AIND 同定の裏取り | A 延べ64（実数約56）、B 60端点。誤同定 **A 0／B 4**（D04848×2・D04925・D04862） | A §6、B §1 |
| 新規仮 TMP の逆引き | A 29行中 本伝・既登録あり 0／B 33行中 **6**（D04871×5・D04848） | A §5、B §0 |
| 検出（内容） | 77（A 31／B 46） |  |
| 検出（機械） | 17 |  |
| 集約後 | **適用 79／不適用 15**（不適用＝B98 の @when 精度 12・D04791 cert・D04754 shuhrah・D04914 任意連結） | 裁定反映 §A |
| n_assertions_correct（内容、集約後） | 約 1,263（1,325 − 適用62） |  |
| n_assertions_FP / FN / substitution（集約後・内容＋機械、適用分） | **6 / 43 / 30** | 下表 |
| Record-level exact-match（指摘ゼロの record） | 検出ベース 49/100（指摘のあった record 51）、適用ベース **54/100**（適用のあった record 46） |  |

## 2. 検出内訳（94件。括弧内は集約後に適用した件数）
### 2-1. error_category × severity
| | H | M | L | 計 |
|---|---|---|---|---|
| FP | 0 (0) | 2 (2) | 4 (4) | 6 (6) |
| FN | 6 (6) | 21 (21) | 17 (16) | 44 (43) |
| substitution | 11 (11) | 16 (4) | 17 (15) | 44 (30) |
| 計 | 17 (17) | 39 (27) | 38 (35) | 94 (79) |

### 2-2. origin_stage × caught_stage
| origin \ caught | verify_content | verify_mech | 計 |
|---|---|---|---|
| gemini_draft（初版の誤りが校閲後も残存） | 29 | 1 | 30 (適用 28) |
| claude_review（校閲者の作り込み・見落とし） | 48 | 16 | 64 (適用 51) |

### 2-3. error_category × origin_stage
| | gemini_draft | claude_review |
|---|---|---|
| FP | 3 | 3 |
| FN | 23 | 21 |
| substitution | 4 | 40 |

### 2-4. assertion_type
relation 27／id_assignment 27／other 19（訳文・note・FIXLOG）／date 14／persName 4／affiliation 2／placeName 1。

### 2-5. 傾向
- **本伝・既登録の見落とし**が今回も最大の H 源（B96: القباني 家5件＝ID-Master TMP-P-000809 と本伝 D00075・D00594・D05080・D05813、D04848 の ابن القصاص ＝ D04075、D04953 の父 D00563、D04914 の父 D10188）。B87〜B93 に続き4バッチ連続。父・祖父・叔父の「名＋ニスバ」grep に加え、**ID-Master の Note に書かれた子・親の AIND 対応表**を読む必要がある。
- **同定の取り違え**（الهيثمي → D04081、الأبي → D04932）は、相手側本伝に本項主への言及（「ابن آدم البوصيري」「رفيقا للجمال بن موسى」）があり、逆引きで閉合できた。
- **チャンク間の基準不統一**: 父 relation の付与（B95・B98 で計13件欠落）と @when の精度（B96 のみ日精度）。前者は規則3 の運用、後者は規則18 の文言の曖昧さ（要判断★6）。
- substitution の 40/44 が claude_review 起点だが、うち 12 は @when 精度（不適用）、9 は訳文・note の表記で、同定・日付値の実質的誤りは H 11 件。

## 3. 「違反ゼロ」項目（分母つき）
| 項目 | 内容A | 内容B | 機械（再実行後） |
|---|---|---|---|
| REF 転送先の妥当性 | 2/2 誤り0 | 2/2 誤り0 | 4/4 形式違反0 |
| 毒 wd（Q160851／Q191314／Q35160／Q3824443／Q12247942／Q381208／Q1164991） | 0/509 | 0/352 | 0/206 |
| 汚染・幻・名寄せ済み旧番号の残存 | 0/509 | 0/352 | 0/1052 |
| ID-Master 未登録の非仮 TMP／TSV 未登録の仮番号／幻 AIND | 0/509 | 0/352 | 0/408／0/409 |
| ID 書式（#・桁数） | — | 0/352 | 0/1052 |
| 規約A（relation/@n） | — | 0/112 | 0/252（before 1→after 0） |
| relation の向き・本項主含有・self・possible_identity 双方向 | 0/116 | 0/112 | 0/252 |
| Pattern A の符号化漏れ | 0/14 | 0/12 | — |
| 日付（h2g 再計算） | 0/58（意味上の誤り1＝D04766 適用） | 0/44 | 0/351 |
| 原文にない placeName（規則22） | 0/71（読み替え1＝D04759 適用） | 0/54 | 0/167 |
| 訳文へのアラビア文字・内部ID・立項連番・en の日本語混入 | 0/120 | 0/80 | 0/776 |
| 原文 source note と corpus の一致（★連結4件含む） | 60/60 | — | 100/100 |
| respStmt（初版非改変・校閲 respStmt） | — | — | 100/100（集約 respStmt 53件を許容） |
| name_only ≤3世代・full の居住句 | — | — | 0/197（before 1→after 0） |
| affiliation と state の二重符号化 | — | — | 0/100 |
| 統制外 type/subtype | — | 0/112 | 0/1255 |
| 仮 TMP のチャンク間重複・片側漏れ | — | 0/33 | 0/77（取り下げ6行除外） |
| ⚠汎用名の明記 | 13/13 | — | 56/56（before 7件欠落→after 0） |
| well-formed | — | — | 100/100 |
| 機械検査の残違反 | | | **1**（[15] TMP-P-NEW95-04 に対する候補 D00213＝別人。誤検出） |

## 4. 集約結果
- 実項 96 / REF 4（D04743→D10179／D04858→D04888／D04881→D04840 cert medium／D04930→D04933。転送先は4件とも未収録）。
- 統合すべき最終ファイル一覧: `統合ファイル一覧_B94-98.tsv`（100行＝実項 96・REF 4、すべて `Individuals/4000-4999/` 行き）。
- 新規仮 TMP **77**（P 56 / L 8 / I 6 / O 4 / T 3）: `TMP_NEW_all.tsv`（83行、取り下げ6行）。実番号の採番は統合時。
- ISSUES 45 → 自己裁定 24、要判断 ★7（急ぐ1＝ID-Master 名寄せ）。既存 Individuals への変更提案 7件（未適用）。
- precheck（`precheck_B94-98_after.md`）: 261件＝仮番号の書式・幻番号 168（採番で消える）、名前不一致 87（翻字・表記差）、汚染注意 3（TMP-O-00096／00108／00012、実体一致を確認済み）、カテゴリ不一致 3（shuhrah 位置の TMP-N、repo 先例 D05710 と同型）。実質ゼロ。
- `docs/精度検証/model_accuracy_log.tsv` への1行と `model_accuracy_findings.tsv` への94行の追記は、本レポート §1〜§2 と `FINDINGS_all_resolved.tsv` から統合時に行う（本集約では未追記）。
