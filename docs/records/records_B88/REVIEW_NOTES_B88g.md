# REVIEW_NOTES_B88g — チャンク B88g（AIND-D07659〜D07750、20件）

- 校閲者: claude-b88g-review（2026-09-24）
- 対象: `docs/_work/B88_incoming/B88/` の AIND-D07659／07661／07663／07666／07733／07735〜07740／07742〜07750 の20ファイル（in-place 編集、git 操作なし）
- 参照: `CHUNK_BRIEF_B88.md`、`precheck_B88_before.md`、corpus 原本 `0__DawForAIND_renumbered_B54_split20260905.txt`（全文索引を作成して本伝・転送先を探索）、`corpus_B88.json`、`idmaster_ext_20260924.tsv`
- 共通処理（全20件）: 原文全文を `<note type="source" xml:lang="ar">` として translation の直前に挿入（立項番号は除去）／relation @n を規約A（親族 @n 無し・非親族通し）に統一／西暦は `h2g.py`（proleptic Gregorian）で再計算／各 relation・event に原文句を `desc xml:lang="ar"` として補填／ニスバ・施設由来の placeName・residence を規則22-1で除去／ja 訳「ビン」→「ブン」、「ハジュラ暦」→「ヒジュラ暦」／校閲 respStmt を追加（初版 respStmt は無改変）／well-formed 確認 OK（20/20）。
- 集計: **実項 20・REF 0**。新規仮TMP 15件（P×9、L×3、T×1、O×2）。ISSUES 11項。

## 実項/REF 判定
| ID | 判定 | 根拠 |
|---|---|---|
| D07737 | 実項 | 「أظنه جد الذي قبله」は推測コメント（規則13）→ possible relation（grandson、cert medium） |
| D07747／D07749 | 実項 | 末尾「وسيأتي في الكنى」は実伝を伴う項の相互参照。B74-78 §D-1 先例（D02182）により REF 化せず、クンヤ部 #AIND-D10629／#AIND-D11109 との possible_identity（cert high）。**ISSUES §Dg-2** |
| D07659 | 実項 | クンヤ部 #AIND-D11049 との二重立項（転送指示なし）→ possible_identity cert high（§Dg-1） |
| 他16件 | 実項 | 転送指示なし |

## ファイル別
### AIND-D07659
- 「سمع مني بالمدينة」型（規則2）。父 → **TMP-P-NEW88g-01**（عبد السلام بن أبي الفتح محمد … الكازروني、ابن تقي 家、D07660／D01529／D10861 参照）。クンヤ部 #AIND-D11049 と possible_identity（cert high、§Dg-1）。residence المدينة 除去。
### AIND-D07661
- field الحديث 除去。父 → **TMP-P-NEW88g-02**（⚠汎用）。grandfather → maternal_grandfather（سبط علي البواب、#NEEDID）。residence 除去。訳「大仕事（孫）」→「娘方の孫」。
### AIND-D07663
- 父 #NEEDID 追加。訳の読点整理。
### AIND-D07666
- 師 مسعود المغربي #NEEDID×2 → #AIND-D09916 cert medium（1件に統合、method اشتغل）。サハーウィー لازم relation の空 field 除去。父 → **TMP-P-NEW88g-03**。「الطيب النغمة」を full から除去。857→1453。訳: 「أناسيده الطيبة」（美しい詠唱）の誤読（優れたシャイフたち）を是正。
### AIND-D07733
- [汚染注意] TMP-N-00108 は nisbah 位置＝正用・修正不要（§Dg-11）。空 brother → #AIND-D07731・#AIND-D07732（شقيق اللذين قبله）。父 → #AIND-D04346 cert medium（規則23）。「عرض علي」の field القراءات・bibl 除去。cultural event（حفظ القرآن وغيره）追加。
### AIND-D07735
- [カテゴリ不一致] TMP-N-00312 → #AIND-D03560（الجلال القمصي）。الديمي TMP-P-000215 → #AIND-D04876、الفخر المقسي #NEEDID → #AIND-D04857、父 #NEEDID → #AIND-D04339（ويعرف بالحجازي）。bibl الأذكار → TMP-T-00002。873-09-28 → **1469-04-20**（初版 1468）。没地 القاهرة（原文なし）と重複 event 除去。ニスバ الحجازي → shuhrah ابن الحجازي。§Dg-4。
### AIND-D07736
- 父 #NEEDID → #AIND-D04349（والد الشمس محمد الآتي）、祖父 → #AIND-D07737 cert medium。サハーウィーへの سمع／قرأ を2 relation に、bibl الستة → **TMP-T-NEW88g-01**（§Dg-6）。laqab الشمس 追加。850-12 → **1447-02**（初版 1446）、891 → 1486。residence 除去。§Dg-7。
### AIND-D07737
- subtype other #NEEDID → grandson #AIND-D07736 cert medium。師 #AIND-D06936 確認、event 834 → when-custom/when 1430。父 #NEEDID 追加。
### AIND-D07738
- 父 → #AIND-D04363（ويعرف باليبناوي）。chronicler relation → mention event（#AIND-D09211 cert low）。生年欠落 → @when 無し cert low（§Dg-8）。没年 بضع وثلاثين → notBefore/notAfter（833-12〜839-12＝1430-08〜1436-07）。residence 除去。
### AIND-D07739
- 汚染番号 TMP-P-000530 → #AIND-D05246（أخو محمد الآتي）。父 → **TMP-P-NEW88g-04**。売主 خليل بن الناصر → **TMP-P-NEW88g-05**（other）。المنصور／جقمق への relation・affiliation 除去（note 化）。الرمل／الجزيرة → **TMP-L-NEW88g-01／-02**。881-10 → **1477-01**（初版 1476）。residence・state placeName 除去。訳の構文誤読を是正。§Dg-9。
### AIND-D07740
- 妻 → #AIND-D13076、子 أحمد → #AIND-D01366、子 أبو الفتح → #AIND-D08857、patron → #AIND-D05959（ابن المزلق）。父 → **TMP-P-NEW88g-06**。ابن فهد → mention event（cert low）。842-04 → 1438-09。「مباكا」＝مباركا と解して訳を是正。
### AIND-D07742
- [カテゴリ不一致] TMP-N-00251 → #AIND-D07360（الفرسيسي）。[書式不正] TMP-S-000003 → TMP-S-00003。bibl の TMP-S-00062 → TMP-T-00082（سيرة ابن سيد الناس、兄 D07741 本文で特定）。空 brother → #AIND-D07741。父 → **TMP-P-NEW88g-07** cert medium（D07741 のナサブから復元）。聴聞年 796 を cert medium で付与。
### AIND-D07743
- 「كتب عنه العز بن فهد」→ mention event（#AIND-D03985、D02660 先例）。「praised_by_subject」→ cultural event 内 persName（#AIND-D04835 cert medium）。residence・affiliation الأزهر 除去。父 #NEEDID 追加。
### AIND-D07744
- 汚染番号 TMP-P-000529（子）→ #AIND-D08856（الماضي أبوه）。父 → **TMP-P-NEW88g-08**。state مادح الحرم → **TMP-O-NEW88g-01**＋orgName TMP-I-00120。827 → **1423**（初版 1424）。residence を 829〜830 範囲＋cert medium に。shuhrah「مادح الحرم」除去。※ブリーフ記載の「159番」「TMP-N-00136」「TMP-P-000603」は本ファイルには無く（D07748／D07754）、precheck 自体は本項に指摘なし。
### AIND-D07745
- 師 #NEEDID → #AIND-D07124（ركن الدين الخوافي）cert medium（أو لأخيه）、802 → 1399。父 → #AIND-D04386。兄弟 D07746（高）・D07747〜49（medium）。§Dg-3。
### AIND-D07746
- 空 brother → #AIND-D07745。規則23により父・兄弟3名・الخوافي イジャーザを cert medium で補填。
### AIND-D07747
- 実項＋possible_identity #AIND-D10629（§Dg-2）。師 #NEEDID×2 → #AIND-D05648・#AIND-D07573、TMP-P-000484 → #AIND-D07784、TMP-P-000158 → #AIND-D13339。833 → **1429**（初版 1430）。affiliation buried（二重）除去。兄弟・父・母を補填。
### AIND-D07748
- 立項連番「159番。」「No. 159.」除去。[カテゴリ不一致] TMP-N-00136 → TMP-P-000464（الزين الزركشي）cert medium。#NEEDID → #AIND-D03558（عبد الرحمن بن الأذرعي、cert medium）・#AIND-D13294（ابنة ابن الشرائحي）、الشمس الشاوي は #NEEDID 維持（§Dg-5）。没地 القاهرة（原文なし）除去、848-01 → 1444-04。visit القاهرة の重複統合。兄弟・父・母を補填。
### AIND-D07749
- 実項＋possible_identity #AIND-D11109（§Dg-2）。الزين المراغي → #AIND-D10690（814 → 1411）、أبو شعر #NEEDID×3 → #AIND-D03641 に統合。母 → **TMP-P-NEW88g-09**。父・兄弟4名を補填。833 → **1429**。
### AIND-D07750
- 兄 → #AIND-D00156、父 → #AIND-D04400（العرياني 家）。laqab الشهاب → الشمس。colleague relation → 無名の師 #NEEDID。state ガラス商い → **TMP-O-NEW88g-02**、الوراقين → **TMP-L-NEW88g-03**。state صوفي の placeName・affiliation×2・residence 除去。808 تقريبا → cert medium／1405、879-01 → 1474-05。訳「アッ＝ザッジャージ」是正。

## precheck 対応（本チャンク該当分）
- D07733 [汚染注意] TMP-N-00108／[名前不一致] T-00095: 修正不要（nisbah 正用・Latin 表記）。
- D07735 [カテゴリ不一致] TMP-N-00312: 是正。
- D07739 [汚染注意] TMP-P-000530: 是正（#AIND-D05246）。
- D07742 [カテゴリ不一致] TMP-N-00251／[書式不正・幻番号] TMP-S-000003／[カテゴリ不一致・名前不一致] TMP-S-00062: 是正。
- D07744 [汚染注意] TMP-P-000529: 是正（#AIND-D08856）。
- D07747 [名前不一致] TMP-I-00037: 見かけ上。
- D07748 [名前不一致] TMP-I-00037: 見かけ上／[カテゴリ不一致] TMP-N-00136: 是正／[連番訳混入] 159: 除去。

## 日付検証（h2g.py）
857→1453／873-09-28→1469-04-20（火）／850-12→1447-02／891→1486／834→1430／833-12→1430-08・839-12→1436-07／881-10→1477-01／842-04→1438-09／791→1389・796→1393／827→1423・829→1425・830→1427／802→1399／833→1429／848-01→1444-04／814→1411／808→1405／879-01→1474-05。初版の誤り: D07735（1468）、D07736（1446）、D07739（1476）、D07744（1424）、D07747／D07749（1430）。
