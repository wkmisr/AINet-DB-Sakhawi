# REVIEW_NOTES_B91 — チャンク B91（AIND-D04628〜D04653、20件）

- 校閲者: claude-b91-review（2026-09-25）
- 対象: `docs/_work/B89-93_incoming/B89-93/` のソート順41〜60件目（D04628・D04629・D04630・D04631・D04632・D04633・D04636・D04637・D04640・D04641・D04642・D04643・D04644・D04645・D04646・D04647・D04648・D04649・D04650・D04653）。in-place 編集、git 操作なし。
- 参照: `CHUNK_BRIEF_B89-93.md`、`precheck_B89-93_before.md`、`corpus_B89-93.json`（本文）、corpus 原本 `0__DawForAIND_renumbered_B54_split20260905.txt`（転送先・相手側本伝の探索）、`docs/_work/idmaster_ext_20260925.tsv`（新規TMP発行前に全件 grep）。
- 共通処理（全20件）: 原文全文を `<note type="source" xml:lang="ar">` として translation の直前に挿入（刊本の立項番号は除去、corpus_B89-93.json から機械抽出）／relation @n を規約A（親族 @n 無し・非親族通し番号）に統一／第三者言及（ذكره／قاله／ترجمه／قال شيخنا في الإنباء／ذكر المقريزي／ذكره الخزرجي／للعز الموصلي فيه نظم）を Pattern A の mention event に統一／西暦は `h2g.py`（selftest PASS）で全件再計算し月精度に是正（初版の年誤り: D04637 1403→1404-03、D04640 1428→1427、D04643 1398→1399-08）／ニスバ・施設所在地・在職地由来の residence／placeName を除去（規則22-1）／affiliation と state の二重符号化を解消（規則8: D04628・D04636・D04641・D04643・D04649・D04653）／「ممن سمع مني」型は relation 内 event に一本化し field を除去（規則2: D04641・D04645）／裸名の父に #NEEDID の father relation を付与（規則3・12）／ja 訳の「ビン」→「ブン」（規則17）、推測句・翻字・内部IDを訳文から除去／校閲 respStmt を追加（初版 respStmt は無改変）／well-formed 確認 OK（20/20）。
- 集計: 実項 18・REF 2（D04642 → #AIND-D04584、D04644 → #AIND-D04575）。新規仮TMP 18件（P×9、L×3、I×3、O×2、N×1）。ISSUES 9項。
- 作業用の一時ファイル `docs/_work/B89-93_incoming/_b91tmp/`（src.json・w.py）は削除権限がないため残置（統合時に破棄可）。

## 実項/REF 判定
| ID | 判定 | 根拠 |
|---|---|---|
| D04642 | **REF** | 「فيمن جده عبد الله بن حسن بن يوسف」＝自項に転送指示。転送先 **#AIND-D04584**（刊本200項 عبد الله بن محمد بن عبد الله بن حسن بن يوسف … البدر بن القطب البهنسي القاهري、755年生。B90 担当分）。ファイル名を REF_ に変更 |
| D04644 | **REF** | 「فيمن جده طيمان」＝自項に転送指示。転送先 **#AIND-D04575**（刊本191項 عبد الله بن محمد بن طيمان … الجمال الطيماني ثم الدمشقي الشافعي。B90 担当分）。ファイル名を REF_ に変更 |
| 他18件 | 実項 | 転送指示なし |

## 汚染番号・幻番号・カテゴリ不一致・毒wd の処置
| 番号 | 出現 | 処置 |
|---|---|---|
| TMP-P-000529（محمد・汚染常習） | D04629（父）／D04637（父）／D04644（父） | D04629 → 新規 TMP-P-NEW91-02（الشمس محمد بن موسى بن محمد بن موسى المنوفي）／D04637 → #NEEDID（裸名）／D04644 → REF 化に伴い除去 |
| TMP-N-00218（الخزرجي、person 位置） | D04630 | → corpus 本伝 **#AIND-D05108**（علي بن الحسن بن أبي بكر … الخزرجي الزبيدي اليمني المؤرخ）、Pattern A 化 |
| TMP-N-00235（الحناوي、person 位置） | D04636 | → corpus 本伝 **#AIND-D01185**（أحمد بن محمد بن إبراهيم الشهاب الحناوي、763年生）、successor relation cert medium |
| TMP-N-00108（الفاسي） | D04628 | persName type="nisbah" の位置での使用のため適正（precheck は person 位置と誤検出）。他称のため cert medium を付与 |
| wd:Q191314 | D04633 | → wd:Q233387（Hanbali） |
| wd:Q160851 | D04649 | → wd:Q228986（Hanafi） |
| wd:Q1164991（[要照合wd]） | D04628 ×2 | affiliation を除去（規則8）、state 内 orgName を ID-Master 既存 **#TMP-I-00133** に置換。wd の実照合は未確認（ISSUES §D91-1） |
| TMP-I-00000／TMP-O-00000（零番号） | D04653 | → #TMP-I-00131（البيمارستان بمكة）／新規 TMP-O-NEW91-02（السقا）／الحرم → wd:Q428858 |
| TMP-P-000183（「الفضلاء」＝不特定集合） | D04632 | student relation を除去し cultural event に（規則14） |
| precheck [名前不一致]（L-00051 Fās／L-00010 Ibb／L-00146 al-Shabīka） | D04628・D04648・D04653 | 見かけ上＝修正不要（D04628 は placeName 自体を除去） |

## corpus で見つけた相手側本伝・同定（検証パス向け）
- D04628 叔父「الشيخ أبو القسم」＝ **#AIND-D11095**（كنى 部 أبو القسم بن موسى بن محمد بن موسى العبدوسي المغربي نزيل تونس المالكي、837年没）。同一人物の別立項 #AIND-D04020（عبد العزيز بن موسى بن محمد أبو القاسم العبدوسي「وينظر الكنى」）。
- D04630 「ذكره الخزرجي」＝ **#AIND-D05108**。
- D04631 ＝ **#AIND-D09732**（محمد حفيد يوسف بن نصر … صاحب غرناطة ويلقب الغالب بالله、844年在位）と possible_identity cert medium（ISSUES §D91-3）。父候補 #AIND-D09497（الأيسر）は別人。
- D04636 「شيخنا ابن خضر」＝ **#AIND-D00112**（Individuals 先例 D01663・D01935 と同定一致）、「شيخنا الحناوي」＝ **#AIND-D01185**（ニスバ索引 #AIND-D11609 も同人）。「من لم يسم」部（corpus L123975〜、$$$ 集合項）に本項主「القرافي النحوي」の記述あり（後任 الحناوي を断定、「أظنه كان إماما بالناصرية فرج」は note 留め）。
- D04629 師「جعفر」＝ #AIND-D02414（الزين جعفر السنهوري、cert medium）。同名の「الجمال عبد الله بن محمد بن موسى المنوفي」が #AIND-D05473 に従兄弟として登場するが年代不整合のため未同定（ISSUES §D91-2）。
- D04642 → #AIND-D04584、D04644 → #AIND-D04575（いずれも B90 担当分。B90 側で二重IDを出さないこと）。

## ファイル別
### AIND-D04628
- 叔父 #NEEDID → #AIND-D11095。父 → **TMP-P-NEW91-01**。死亡 placeName فاس（原文に没地なし）と residence فاس を除去（規則22-1）。affiliation（جامع القرويين）除去、state الإمامة の orgName → #TMP-I-00133、placeName فاس は原文明記で保持。state الفتيا → #TMP-O-00004、placeName المغرب الأقصى → **TMP-L-NEW91-01**。849 → 1445。訳文の「私は…呼ぶ者を見た」（رأيت من قال فيه）を復元。
### AIND-D04629
- 父 000529 → **TMP-P-NEW91-02**、祖父 → **TMP-P-NEW91-03**。師 جعفر ＝ D02414 cert medium、event に when-custom 0852／@when 1448（初版は @when="0852" の誤記）。イブン・ハジャルの「other」relation → mention event（「شهد شيخنا في إجازته ووصفه…」）。「وشيخ والده وجده」の多義を note・ISSUES §D91-2 に。
### AIND-D04630
- 「ذكره الخزرجي في أبيه」→ mention event（#AIND-D05108）。父 → **TMP-P-NEW91-04**（⚠）。death（أوائل هذا القرن）を notBefore 801／notAfter 810・cert low で追加（ISSUES §D91-7）。state قاض に任地不明 note。
### AIND-D04631
- 「ذكر المقريزي」→ mention event（wd:Q293604、bibl なし）。父 → **TMP-P-NEW91-06**、祖父 → **TMP-P-NEW91-05**。#AIND-D09732 と possible_identity（cert medium）。state → #TMP-O-00163（صاحب (البلد)、先例 D03087）。residence غرناطة 除去。political event に原文 desc・@when 1440-12。訳文の「カイロに」（推定）を除去。
### AIND-D04632
- 「الفضلاء」（TMP-P-000183）への student relation を除去 → cultural event。residence（بيت المقدس・الصالحية・الضيائية）除去、affiliation reside → **TMP-I-NEW91-02**（الضيائية）。death 840 に cert low（حدود…ظنا）。776 → 1374、840 → 1436。
### AIND-D04633
- 毒wd → Q233387。死亡 placeName طرابلس（在職地の継続）除去、815-09 → 1412-12。父 → **TMP-P-NEW91-07**（⚠）、祖父 #NEEDID 維持（ISSUES §D91-4）。state القضاء の推測 date（after 803）を除去し note 化、ref → wd:Q217029。state مدرس（درس بعد أبيه）を追加。
### AIND-D04636
- 師 → **TMP-P-NEW91-08**（ISSUES §D91-5）、弟子 ابن خضر → #AIND-D00112、後任 الحناوي N-00235 → #AIND-D01185（cert medium）。biographer relation → mention event。state مشيخة → wd:Q7492880、orgName → **TMP-I-NEW91-01**、placeName الصحراء → **TMP-L-NEW91-02**、推測の date retirement 除去。affiliation・residence 除去。826-03 → 1423-02。
### AIND-D04637
- 父 000529 → #NEEDID。「قال شيخنا في الإنباء」→ mention event、「للعز الموصلي فيه نظم」→ mention event（**TMP-P-NEW91-09**）。生涯記述を event other に。806-09 → 1404-03、「سنة ست」は 806 cert medium（ISSUES §D91-6）。
### AIND-D04640
- full に الجلاد を補い nisbah **TMP-N-NEW91-01**。831 → 1427（初版 1428）。父 #NEEDID 追加。
### AIND-D04641
- 「ممن سمع مني」型に整理。affiliation 除去、state → #TMP-O-00111（مؤدب الأبناء）、placeName القاهرة 除去。hajj／jāwara に @when 1490、جاور の placeName 除去（規則20）。訳文「ブタイニー」（D00236「بالضم」）。
### REF_AIND-D04642
- REF 方式X。nisbah・listRelation 除去、target #AIND-D04584。mv 済。
### AIND-D04643
- mention event（إنبائه）。affiliation 除去、state の placeName دمشق 除去、ラベル「المؤذن」。801-12 → 1399-08（cert medium、一の位のみ）。birth 722 頃・cert low（قارب الثمانين）。「انتهت إليه الرياسة في فنه」→ cultural event。
### REF_AIND-D04644
- REF 方式X。nisbah・listRelation（父 000529・祖父）除去、target #AIND-D04575。mv 済。
### AIND-D04645
- 「ممن سمع مني بمكة」型に整理（field 除去）。state → **TMP-O-NEW91-01**（دلال الرقيق）、placeName مكة 除去。
### AIND-D04646
- mention event（D09211／T-00138）。placeName القارة → **TMP-L-NEW91-03**（＝قارا、cert medium、ISSUES §D91-8）。
### AIND-D04647
- event に subtype witness・原文 desc・@when 1398、cert high → medium（一の位のみ）。
### AIND-D04648
- honorific「الفقيه الصالح」、placeName を原文語「مدينة أب」（L-00010 維持）。810 → 1407。
### AIND-D04649
- 毒wd → Q228986。affiliation 除去、orgName → **TMP-I-NEW91-03**、residence 除去、state の placeName دمشق は原文明記で保持。mention event（قاله شيخنا في إنبائه）・teaching event 追加。810-05 → 1407-10、birth 740 頃・cert low。
### AIND-D04650
- mention event（D09211／T-00138）。
### AIND-D04653
- 零番号 → #TMP-I-00131／**TMP-O-NEW91-02**／wd:Q428858。affiliation other（施療院）除去 → death placeName に、residence 除去、state の placeName 除去。855-05 → 1451-06。
