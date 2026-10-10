# REVIEW_NOTES_B113 — AIND-D06071〜D06102（20件、2026-10-10、claude-b113-review）

対象: `docs/_work/B109-113_incoming/B109-113/` の B113 分 20 ファイル（in-place、عيسى 部）。原文は `corpus_B109-113.json` と corpus 原本で逐語照合。全件に `<note type="source">` を挿入し、校閲 `<respStmt>` を追加。日付は h2g.py で再計算。REF 1件は `REF_` にリネーム。連結レコードは本チャンクに無し（全20件の末尾を点検。D06099 は原文が「وأثنى عليه」で終わり句点なし＝corpus どおり）。

## 実項/REF 内訳
- REF（方式X）1件: **D06076**（يأتي فيمن لم يسم أبوه → `#AIND-D06109`。同項末尾「وسمى أباه سليمان بن عبد الله」で確定）
- 実項: 19件（うち名のみの実項 D06081）

## ファイル別

### AIND-D06071 عيسى بن أحمد الحنديسي البجائي
職由来 residence（بجاية）除去。affiliation employed を state（نائب في الخطابة、wd:Q932945）に統合、施設 جامع بجاية الأعظم → `TMP-I-NEW113-01`。「شيخها وقدوة أهلها」を office → status（890＝1485）。「تصدى للإفتاء والإقراء」teaching event。逆算生年 notAfter 830（cert low）。訳文に文字説明を補完。

### AIND-D06074 عيسى بن سعيد بن عبد الحميد القاضي المالكي
没年 830 の西暦 1427 → 1426。
（検証後訂正 2026-10-10: persName full から職名「القاضي」を除去（規則5、機械[5]）。）

### REF_AIND-D06076 عيسى بن سليمان بن عبد الله الأنصاري
転送先 `#AIND-D06109`。nisbah・name_only 除去。

### AIND-D06077 عيسى بن عباس بن عمر المغربي التلمساني الخالدي
統制外 relation 2件 → mention event（الجمال المرشدي `#AIND-D07216` medium §D113-5、ابن فهد D09211 low）。没月 → 1419-06。人物評を status に。

### AIND-D06078 عيسى بن عبد الله العماد … ابن الهليس
幻番号 TMP-P-000603 → `#AIND-D06757`（Pattern A）、شيخنا في أنبائه も Pattern A。patron → `#AIND-D01950`（الأشرف إسماعيل、medium §D113-3）。أبيات حسين → TMP-L-00225、نظر عدن → TMP-O-00032。没月 → 1400-03。jāwara に placeName مكة（原文明記）。訳文の文字化けを全面是正。
（検証後訂正 2026-10-10: patron #AIND-D01950 の cert medium を除去（802年以前の「الأشرف صاحب اليمن」は同人のみ、§D113-3）。）

### AIND-D06079 عيسى بن عثمان … ابن جوشن
息子3人 → `#AIND-D08408`（الفخر محمد）／`#AIND-D05330`（علي、汚染 TMP-P-000530 を差し替え）／`#AIND-D01149`（أحمد）。ニスバ由来 residence 除去。没年「قريب العشرين أو بعدها」cert low。teaching event・status 追加。

### AIND-D06080 عيسى بن عطيفة … الحلوي
『المنهاج』wd:Q6806081 → TMP-T-00065。field ×2 除去。「كتبت له」→ إجازة relation（medium）。relation 内 event の @when 誤記（0897-12）を when-custom／1492-10 に。生年 1462 → 1461。study event → meeting event（لقيني）。الحلوي＝حلي（TMP-L-00102）を editorial note に。

### AIND-D06081 عيسى بن عطية النعيمي أبو عزارة
名のみの実項。原文 note のみ追加。

### AIND-D06082 عيسى بن علي بن جار الله … ابن زائد
従兄弟 موسى → `#AIND-D10040`（الآتي）、父 → `#AIND-D05100`（ナサブ4代一致、§D113-6）。ابن فهد → mention（D09211 low）。没月 → 1456-11。

### AIND-D06085 عيسى بن علي الأخنائي
規則28。空参照 relation と observer relation を除去し event（895＝1489）に。

### AIND-D06087 عيسى بن علال المصمودي
affiliation を state に統合、جامع القرويين → wd:Q12204282。القضاء → wd:Q217029。没年「قريبا من سنة عشرين」medium。『مختصر ابن عرفة』→ `TMP-T-NEW113-05`。情報提供者（بعض أصحابنا المغاربة）は note のみ。

### AIND-D06088 عيسى بن عيسى بن محمد العرابي … المغربل أبوه
父 → `TMP-P-NEW113-01`、師 رسلان الذهبي → `TMP-P-NEW113-02`、書 → `TMP-T-NEW113-03`（جزء الموافقات جمع الضياء）／`TMP-T-NEW113-04`（جزء البيتوتة）、職 نقيب الوالي → `TMP-O-NEW113-01`、الصالحية → TMP-L-00003。偽人物 TMP-P-000183（الفضلاء）への relation を除去し teaching event に。職由来 residence 除去。
（検証後訂正 2026-10-10: TMP-P-NEW113-02 の TSV を「البهاء رسلان بن أحمد الذهبي」に補い、corpus 20か所が同一人物＝汎用名ではない旨を Note に（内容B L・機械[16]）。）

### AIND-D06090 عيسى بن قرمان
兄弟 إبراهيم → `#AIND-D00287`（カラマン侯、medium §D113-4）。شيخنا → Pattern A。重複 political event を death desc に統合。

### AIND-D06094 عيسى بن محمد بن قاسم … الراحبي
息子 علي（汚染 TMP-P-000530）→ `#AIND-D05331`（الماضي。同項は「الراجبي」綴り）。重複 study event 除去。

### AIND-D06095 عيسى بن محمد … القطب بن العفيف الحسيني الأيجي
full に「القطب」補完。師 السيد صفي الدين → `#AIND-D03763`、甥（学生）عبيد الله → `#AIND-D04811`（同項で裏取り）、兄 العلاء محمد → `#AIND-D09126`、息子 مرشد الدين محمد → `#AIND-D08413`。student relation を1件に統合、field النحو 除去、書 → `TMP-T-NEW113-01`／`-02`。没地 أيج → `TMP-L-NEW113-01`、没年 1455 → 1454。逆算生年 810–816（low）。
（検証後訂正 2026-10-10: 師 السيد صفي الدين（#AIND-D03763）に親族 relation uncle（cert medium）を追加（内容B L）。TMP-P-000702 → #AIND-D09126 は名寄せ提案へ。）

### AIND-D06096 عيسى بن محمد بن محمد أبو الروح الحجاجي
生年 @when を日精度 1327-05-14 に。没年「سنة خمس」＝805 medium。relation「other」→ Pattern A。

### AIND-D06097 عيسى بن محمد الشرف التجاني
父の汚染 TMP-P-000529 → #NEEDID。誤読の disputant relation（البساطي）除去、D01384 との関係を editorial note に（§D113-2）。الزين رضوان → Pattern A（D03005）。possible_identity → `#AIND-D06116`（medium、鏡像は未収録側）。القدس → gn:281184。
（検証後訂正 2026-10-10: editorial note の「本項の父名」は誤記で、「本項が挙げる المغراوي の父祖名」に訂正（内容B L）。）

### AIND-D06099 عيسى بن الشيخ محمود … الصيرامي
毒wd Q160851 → Q228986。甥（学生）→ `#AIND-D03822`、兄弟 النظام يحيى → `#AIND-D10337`（ナサブ矛盾のため medium、§D113-1）。student の向きを規則15に、method「جود | القراءة」。「أثنى عليه」→ mention（D03822）。ニスバ由来 residence 除去。

### AIND-D06100 عيسى بن موسى بن صبح الرمثاوي
relation「mentioned by」→ Pattern A。職由来 residence（دمشق）除去。逆算生年 732–741（low）。

### AIND-D06102 عيسى بن موسى الشرف الفيومي … العلاف
relation「historian」→ mention（D09211 low）。travel event（البحر #NEEDID）を state（تاجر）に統合。没月 → 1460-12。

## corpus で見つけた相手側本伝（主要）
| 項 | 関係 | 相手 |
|---|---|---|
| D06076 | REF 転送先 | #AIND-D06109 |
| D06077 | 言及者 | #AIND-D07216（medium） |
| D06078 | 主人／言及者 | #AIND-D01950（medium）／#AIND-D06757 |
| D06079 | 息子×3 | #AIND-D08408／D05330／D01149 |
| D06082 | 父／従兄弟 | #AIND-D05100／#AIND-D10040 |
| D06090 | 兄弟 | #AIND-D00287（medium） |
| D06094 | 息子 | #AIND-D05331 |
| D06095 | 師／甥／兄／息子 | #AIND-D03763／D04811／D09126／D08413 |
| D06097 | possible_identity／言及者／逸話の引用先 | #AIND-D06116／#AIND-D03005／（note）#AIND-D01384 |
| D06099 | 甥（学生）／兄弟 | #AIND-D03822／#AIND-D10337（medium） |

## 新規仮TMP（10件、TMP_NEW_B113.tsv）
TMP-P-NEW113-01（عيسى المغربل、D06088 の父）、TMP-P-NEW113-02（رسلان الذهبي）、TMP-T-NEW113-01（الخلاصة للطيبي）、TMP-T-NEW113-02（شرح السيد على الكافية）、TMP-T-NEW113-03（جزء الموافقات جمع الضياء）、TMP-T-NEW113-04（جزء البيتوتة）、TMP-T-NEW113-05（مختصر ابن عرفة）、TMP-L-NEW113-01（أيج）、TMP-I-NEW113-01（جامع بجاية الأعظم）、TMP-O-NEW113-01（نقيب الوالي）。他チャンクの TMP_NEW_B109〜B112 と照合し重複なし。

## 自己点検（分母つき）
- well-formed: 20件中 20件 OK
- 毒wd（Q160851/Q191314/Q35160/Q589/Q3824443/Q327129/Q12247942/Q381208/Q1164991/Q1283/Q3306083/Q4120093）の属性残存: 20件中 違反 0件（D06099 の Q160851 を修正済）
- 幻番号・汚染番号（TMP-P-000529/000530/000603/000183 ほか precheck 列挙分）の属性残存: 20件中 0件（D06078・D06079・D06094・D06097・D06088 を修正済）
- ニスバ番号の person 位置流用: 20件中 0件
- active="" / passive="" の空参照: 20件中 0件（D06085 を修正済）。#NEEDID は裸名の父4件（D06071・D06081・D06087・D06097、規則3）のみ
- relation/@n 規約A（親族に n なし・非親族 1 起点連番）: 20件中 違反 0件
- event/@n 連番: 20件中 違反 0件
- 規則22 placeName（ニスバ・職由来の residence）: 20件中 残存 0件（D06071・D06079・D06088・D06099・D06100 を除去）
- 原文 note（corpus の text と完全一致）: 20件中 20件
- en 訳が英語: 20件中 20件／ja 訳冒頭の立項連番・アラビア語混入: 0件
- `xml:lang="lat"`: 0件／desc の xml:lang 欠落: 0件
- REF 1件: 実伝由来要素（nisbah/relation/state/event）残存 0件
- cert high 以外の箇所: D06071（birth low）、D06077（mention medium・low）、D06078（patron medium）、D06079（death low）、D06080（ijāza medium）、D06082（mention low）、D06087（death medium）、D06090（brother medium）、D06095（birth low）、D06096（death medium）、D06097（possible_identity medium）、D06099（brother medium・siblings_child medium）、D06100（birth low）、D06102（mention low）
- FIXLOG: 86 行（resolution=issue 0 行）
