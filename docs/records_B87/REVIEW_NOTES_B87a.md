# REVIEW_NOTES_B87a — チャンク B87a（AIND-D04468〜D04507、20件）

- 校閲者: claude-b87a-review（2026-09-18）
- 対象: `docs/_work/B87_incoming/B87/` の AIND-D044*／AIND-D0450* 20ファイル（in-place 編集、git 操作なし）
- 参照: `CHUNK_BRIEF_B87.md`、`precheck_B87_before.md`、corpus 原本 `0__DawForAIND_renumbered_B54_split20260905.txt`（転送先探索）、`corpus_B87.json`（本文）、`idmaster_working_20260918.tsv`
- 共通処理（全20件）: 原文全文を `<note type="source" xml:lang="ar">` として translation の直前に挿入（刊本の立項番号は除去）／relation @n を規約A（親族 @n 無し・非親族通し番号）に統一／西暦は `h2g.py`（proleptic Gregorian）で再計算／ja 訳の「ビン」→「ブン」／校閲 respStmt を追加（初版 respStmt は無改変）／well-formed 確認 OK。
- 集計: 実項 18・REF 2（D04470→#AIND-D04465、D04503→#AIND-D04514）。新規仮TMP 12件（P×8、L×1、I×1、T×1、O×1）。ISSUES 12項。

## 実項/REF 判定
| ID | 判定 | 根拠 |
|---|---|---|
| D04470 | **REF** | 「فيمن جده محمد بن يوسف قريبا」＝自項に転送指示。転送先 #AIND-D04465（ナサブ・ニスバ一致、5項前） |
| D04503 | **REF** | 「يأتي فيمن جده يوسف بن علي قريبا」＝自項に転送指示。転送先 #AIND-D04514（本文に「يقال عبد الله بن علي بن أيوب」と明記） |
| D04489 | 実項 | 「أظنه الماضي قريبا」は推測コメント（規則13・D07686 と同型）→ possible_identity（#AIND-D04486、cert medium） |
| 他17件 | 実項 | 転送指示なし |

## ファイル別
### AIND-D04468
- 「ممن سمع مني بمكة」型（規則2）: 独立 event study を除去し relation 内 event に一本化。父 #NEEDID（裸名）。「أفضل」＝بافضل 一族の可能性を note（ISSUES §Da-10）。
### AIND-D04469
- 没地・居住地 شنين → **TMP-L-NEW87a-01**。relation「patron of father」（父の関係）を除去し note 化。residence اليمن（父の記述由来）除去。訳文の転写誤り多数是正（アブドゥッアッラフマーン／マハンマド／シャニィニー／ヤマニー、النسك＝篤信）。ISSUES §Da-7。
### REF_AIND-D04470
- REF 方式X。nisbah・listRelation 除去、target #AIND-D04465。ファイル名を REF_ に変更（mv）。
### AIND-D04471
- 父 #NEEDID → **#AIND-D03881**（corpus 本伝、子3人の列挙一致）。兄 عبد الرحمن → #AIND-D03644。ألف は女性名 → subtype sister・#AIND-D12883。母（空 relation）→ #AIND-D12870（أزدان رومية）。甥 محمد بن عبد الرحمن بن عبد الرحيم → **TMP-P-NEW87a-03**。853→1449。既存 D03644 の TMP-P-001106 は D03881 と同一（ISSUES §Da-2）。
### AIND-D04472
- uncle → maternal_uncle、#NEEDID → #AIND-D04238 cert medium（ISSUES §Da-6）。父 #NEEDID 追加。没年空白のため @when なし。
### AIND-D04475
- 師1 #NEEDID → #TMP-P-000575（اليونيني）。師2・3（P-000576／577）確認。الحجار は師の伝承経路＝note のみ。父 → **TMP-P-NEW87a-04**。生年 تقريبا → cert medium、没年 قريبا من → cert low。student @n=4。precheck [名前不一致]（Q1023470 Latin）は見かけ上。訳文の伝承経路誤読を是正。
### AIND-D04479
- relation「chronicled_by」→ Pattern A mention event（#AIND-D09211 cert low）。nisbah/shuhrah 二重 → shuhrah。847-06 → 1443-10。父 #NEEDID 追加。
### AIND-D04481
- 父の汚染番号 TMP-P-000490 → **#AIND-D04592**（ナサブ5代一致・الآتي أبوه）。「ربما حضر عندي」= teacher（حضر）、field・placeName 除去。residence القاهرة／hajj の مكة（原文なし）除去。事跡を cultural event に整理。
### AIND-D04482
- 毒wd Q160851 → Q228986。師 relation 2件を1件に統合: field الحديث → الفقه（Q484181）、bibl → #TMP-T-00048（مجمع البحرين）、「أذن له في الإقراء」を method desc。@when="0833-04" → when-custom + when 1430-01。الجانبكية（TMP-I-00000／#NEEDID）→ **TMP-I-NEW87a-01**、affiliation study 除去。「وصفه」→ mention event。父 #NEEDID 追加。
### AIND-D04484
- 没年「سنة ست」→ 806 cert low（ISSUES §Da-3）、death placeName 除去。biographer relation → mention event（شيخنا／إنبائه）。state نائب الحكم（O-00096 正用）から placeName 除去。residence المدينة は「أقرأ بها」による（ISSUES §Da-9）。
### AIND-D04485
- 零番号4件を全置換: 被疑者 → #TMP-P-001028／#AIND-D01952（D01952 本文と閉合）、村 → #TMP-L-00234、職 → **TMP-O-NEW87a-01**。subtype「accused murderer」→ killer cert medium（ISSUES §Da-8）。原文にない nisbah الغربي 除去。political event（death と重複）除去。871→1466。ISSUES §Da-4。
### AIND-D04489
- possible_identity #AIND-D04486 cert medium 追加。没年 803 cert medium（ISSUES §Da-5）。「ブン・アビー・アブドゥッラー」。
### AIND-D04490
- [カテゴリ不一致] TMP-N-00485 → 学友 الراعي ＝ #AIND-D09054。イジャーザの授与者は「خلق」→ active #NEEDID（初版は Ibn Ḥajar と誤認）。@when="0836-07-19" → 1433-03-20。「ijaza petitioner」→ other（#AIND-D09211）。@n 1–4 通し。شاهد O-00044（統合済）→ O-00050。الصالحية → wd:Q7404512（先例）。affiliation employed（state と重複）除去。residence القاهرة 除去。父 → **TMP-P-NEW87a-05**。
### AIND-D04493
- 859 の @when 1455 → **1454**（859-01-01＝1454-12-31）。父 #NEEDID 追加。
### AIND-D04496
- relation 内 event @when="0890" → when-custom 0890／when 1485／cert medium（قريب التسعين）。nisbah/shuhrah 二重 → shuhrah。مؤدب الأبناء → #TMP-O-00111。父 → **TMP-P-NEW87a-06**。
### AIND-D04498
- 父 → #AIND-D04913（ナサブ4代一致）追加。chronicler → mention event（D09211 cert low）。residence مكة（ニスバ由来）除去、没地は「بها」により保持。846-05 → 1442-09。
### AIND-D04500
- イジャーザ relation（جماعة → #NEEDID、791→1389）追加。informant → mention event（D09211 cert low）。父 → **TMP-P-NEW87a-02**（النور أبو الحسن علي بن أحمد بن عبد العزيز العقيلي النويري、corpus 言及で実体特定）。residence مكة（自認ニスバ由来）除去。813→1410。
### AIND-D04502
- 「ممن سمع مني بالقاهرة」型: 独立 event study 除去。الخطيب → wd:Q932945。父 → **TMP-P-NEW87a-07**。
### REF_AIND-D04503
- REF 方式X。listRelation 除去、target #AIND-D04514。ファイル名を REF_ に変更（mv）。
### AIND-D04507
- 師 أبو العباس المرداوي → **TMP-P-NEW87a-01**（الشهاب أحمد بن عبد الرحمن المرداوي）。bibl → **TMP-T-NEW87a-01**。student relation の方向（قرأ عليه شيخنا＝本項主が師）を確認し維持。الصالحية → #TMP-L-00003（ダマスクス）。父 → **TMP-P-NEW87a-08**。訳文の方向誤り（「読み聞かせた」）を是正。

## precheck 対応
- D04475 [名前不一致]×3（Q1023470）: 見かけ上＝修正不要。
- D04479 [名前不一致]（TMP-L-00146）: 見かけ上＝修正不要。
- D04481 [汚染注意] TMP-P-000490: → #AIND-D04592。
- D04482 [要照合wd] Q160851: → Q228986（無条件置換）。
- D04484 [汚染注意] TMP-O-00096: 登録実体（نائب الحكم）と一致＝正用のまま。
- D04490 [カテゴリ不一致] TMP-N-00485: → #AIND-D09054。
- 立項連番の訳文混入: 本チャンクには無し（各 ja 訳の冒頭を確認）。
