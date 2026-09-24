# REVIEW_NOTES_B88a — チャンク B88a（AIND-D04508〜D04536、20件）

- 校閲者: claude-b88a-review（2026-09-24）
- 対象: `docs/_work/B88_incoming/B88/` の AIND-D0450*／D0451*／D0452*／D0453* 20ファイル（in-place 編集、git 操作なし）
- 参照: `CHUNK_BRIEF_B88.md`、`precheck_B88_before.md`、corpus 原本 `0__DawForAIND_renumbered_B54_split20260905.txt`（転送先・本伝探索）、`corpus_B88.json`（本文）、`docs/_work/idmaster_ext_20260924.tsv`（新規TMP発行前に全件 grep）
- 共通処理（全20件）: 原文全文を `<note type="source" xml:lang="ar">` として translation の直前に挿入（刊本の立項番号は除去、corpus_B88.json と正規化照合で全件一致）／relation @n を規約A（親族 @n 無し・非親族通し番号）に統一／第三者言及（ذكره／أرخه／قاله／ذكرهما）を Pattern A の mention event に統一／西暦は `h2g.py`（proleptic Gregorian、selftest PASS）で全件再計算し月精度に是正／ニスバ由来の residence・placeName を除去（規則22-1）／「ممن سمع مني」型は relation 内 event に一本化し field を除去（規則2）／ja 訳の「ビン」→「ブン」（規則17）・「ハジュリー暦」→「ヒジュラ暦」／校閲 respStmt を追加（初版 respStmt は無改変）／well-formed 確認 OK（20/20）。
- 集計: 実項 19・REF 1（D04515 → #AIND-D04505、cert medium）。新規仮TMP 14件（P×10、L×1、O×2、T×1）。ISSUES 11項。

## 実項/REF 判定
| ID | 判定 | 根拠 |
|---|---|---|
| D04515 | **REF** | 「فيمن جده عبد القادر بن علي قريبا」＝自項に転送指示。転送先 #AIND-D04505（祖父名の食い違いあり → cert medium、ISSUES §Da-1）。ファイル名を REF_ に変更 |
| 他19件 | 実項 | 転送指示なし |

## 汚染番号・幻番号・カテゴリ不一致の処置
| 番号 | 出現 | 処置 |
|---|---|---|
| TMP-P-000664（ティムールの息子 عمر） | D04518・D04533 | D04518 → #AIND-D05815（ナサブ8代一致）／D04533 → #NEEDID（裸名） |
| TMP-P-000204（حسن） | D04519 | → #AIND-D02608（حسن بن عمر بن الزين عبد العزيز … ابن زين الدين） |
| TMP-P-000529（محمد・汚染常習） | D04526 | → #AIND-D08356（محمد بن عمر بن محمد بن علي بن محمد بن إدريس … الشيبي、相互言及で閉合） |
| TMP-P-000352（幻番号） | D04527 | → #AIND-D06936（الجمال الكازروني المدني。マッカの D08619 ではない） |
| TMP-N-00096（ニスバ番号の person 流用） | D04520 | → #AIND-D07528（الشمس البرماوي、corpus 本伝） |
| TMP-P-000360／000735（ID-Master 登録あり） | D04534 | corpus 本伝 #AIND-D00540／#AIND-D05974 を直接充当（名寄せ候補 ISSUES §Da-4） |
| TMP-I-00000（零番号） | D04524 | → #TMP-L-00222（مقابر الناشريين） |
| precheck [名前不一致]（L-00041 Zabīd／L-00094 al-Takrūr／L-00036 Jidda） | D04518・D04520・D04531 | 見かけ上＝修正不要 |

## ファイル別
### AIND-D04508
- 「ممن سمع مني بمكة」型: 独立 event visit を除去、relation 内 event に原文句 desc、field 除去。name_only を3世代に、full に العطار を補う。父 → **TMP-P-NEW88a-01**（⚠汎用名）。
### AIND-D04510
- 父 #NEEDID → #AIND-D05659（「الآتي أبوه」、D05659 側「خلفه ابنه عبد الله الماضي」）。ザーウィヤ継承を predecessor relation ＋ state office **TMP-O-NEW88a-01**（placeName **TMP-L-NEW88a-01** الحسامية＝الحسانية、ISSUES §Da-2）に符号化し affiliation employed を除去。「ذكره شيخنا … في إنبائه」→ mention event（Q471116／T-00034）。831 → @when 1427（初版 1428 誤り）。
### AIND-D04511
- 「أرخه ابن فهد」→ mention event（D09211 cert low）。ニスバ由来 residence 除去、没地 مكة は「بها」で保持。848-03 → 1444-06。父 → **TMP-P-NEW88a-02**。
### REF_AIND-D04515
- REF 方式X。nisbah・laqab・listRelation 除去、target #AIND-D04505 cert medium。ファイル名を REF_ に変更（mv）。
### AIND-D04516
- state #NEEDID → **TMP-O-NEW88a-02**（خادم البيمارستان）、orgName は所在不明で #NEEDID 維持。「حفظ القرآن … المنهاج」→ cultural event（T-00095／T-00065）。父 #NEEDID 追加。891-03 → 1486-03。訳文の補い（ナワウィー／ターリビーン）除去。
### AIND-D04518
- 父 000664 → #AIND-D05815、兄弟 العفيف عثمان → #AIND-D04864。没地（非 burial）除去、burial زبيد 保持。hajj event に desc 補填、事跡を cultural event に。訳文「ウマル」→「ウスマーン」。
### AIND-D04519
- 父 → #AIND-D05871、兄弟 حسن 000204 → #AIND-D02608、عبد الباسط → #AIND-D03490。field・residence 除去。ニスバ「المطيري」(N-02048) を除去し「مطيري」を laqab に（ISSUES §Da-3）。en 訳の「b. al-Wāḥid」脱落補正。
### AIND-D04520
- 師 البرماوي N-00096 → #AIND-D07528、ابن الجزري Q4120093 維持。父 → #AIND-D05872、母 غزال الحبشية → **TMP-P-NEW88a-03**。没年「قبل سنة ست وثلاثين」→ notBefore 0832／notAfter 0835（1428／1432）。cultural event の placeName مكة 除去、event に desc 補填。訳文「ノイリー」→「ヌワイラ出身」。
### AIND-D04522
- 「المعروفين بالعمرة」の誤訳（ウムラを率いる）を「العمرة＝العمري 一族」に是正。没年 803 cert low・没地除去（ISSUES §Da-5）。state قائد → #TMP-O-00094（placeName 除去）。residence 除去。「قاله الفاسي في مكة」→ mention event（D06757／T-00037）。父 → **TMP-P-NEW88a-04**、息子 #AIND-D07800（規則23、cert medium）。
### AIND-D04524
- 埋葬地 I-00000 → #TMP-L-00222。「قبل العشرين」→ notAfter 0819／1417。affiliation buried 除去。state → #TMP-O-00224（قاضي تعز）。父 → **TMP-P-NEW88a-05**（⚠）、兄弟 #AIND-D03712（規則23、cert medium）。ja 訳の文字化け「ウutmān」是正。
### AIND-D04526
- 兄弟 محمد 000529 → #AIND-D08356。父 → #AIND-D05961（السراج عمر الشيبي شيخ الحجبة）追加。
### AIND-D04527
- 師 000352 → #AIND-D06936、TMP-P-000003 維持、desc 補填。父 → #AIND-D05962。
### AIND-D04528
- 父 → #AIND-D05979（النجم عمر بن فهد）、祖父 grandfather #NEEDID → maternal_grandfather #AIND-D05027（النور بن سلامة、ISSUES §Da-10）。840-04 → 1436-10、840-07 → 1437-01（初版は両方 1436）。full から居住句「ابن صاحبنا النجم」を除く。
### AIND-D04529
- 空 relation（active=""）2件を #AIND-D04528（兄）・#AIND-D05979（父）で補填。「ذكرهما أبوهما」→ mention event（D05979）。863-10 → 1459-08、866-02 → 1461-11（初版 1462 誤り）。
### AIND-D04530
- travel event: #NEEDID → #TMP-L-00037、出発地 مكة を placeName に追加、@when 1451-05、cert 除去。父 → **TMP-P-NEW88a-06**。
### AIND-D04531
- 「أرخه ابن فهد」→ mention event（D09211 cert low）。856-02 → 1452-03。父 → **TMP-P-NEW88a-07**（⚠）。訳文の翻字（ダムルウィー／ヤマニー）是正。
### AIND-D04532
- 師 عبد الله العراقي → **TMP-P-NEW88a-08**（⚠、ISSUES §Da-6）。「نصبه شيخا」→ state status（wd:Q7492880）。「ذكره صاحب صلحاء اليمن」→ mention event（persName #NEEDID、bibl **TMP-T-NEW88a-01**）。الأهدل を shuhrah に。866 → 1461（初版 1462 誤り）。父 #NEEDID 追加。
### AIND-D04533
- 父 000664 → #NEEDID。mention relation ×2 → mention event（Q57420531／Q471116＋T-00034）。没年 807 cert low（ISSUES §Da-7）。event に desc 補填。ニスバ綴り注記の誤訳を是正。
### AIND-D04534
- 師5名: ابن أسد → #AIND-D00540、جعفر → #AIND-D02414、الجلال المرجوشي → #AIND-D07649、عمر النجار → #AIND-D05974、الشهاب القباقبي → **TMP-P-NEW88a-09**（⚠）。父 → **TMP-P-NEW88a-10**（⚠）。「جاز الأربعين」から birth notAfter 0843 cert low（逆算 note）。study event を residence に統合。
### AIND-D04536
- 「ممن سمع علي بمكة」（عليّ＝私、B87 §D-18）: 独立 event study 除去、field 除去。父 → #AIND-D08857（أبو الفتح بن حمام）。

## 出力
- `TMP_NEW_B88a.tsv`（14行・7列）／`ISSUES_B88a.md`（§Da-1〜§Da-11）
