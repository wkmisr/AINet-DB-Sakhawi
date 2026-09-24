# REVIEW_NOTES_B87c — チャンク B87c（AIND-D07342〜D07381、19件）校閲記録

- 校閲者: claude-b87c-review（2026-09-18）
- 対象: `docs/_work/B87_incoming/B87/` の担当19ファイル（in-place で確定版に修正）
- 参照: `CHUNK_BRIEF_B87.md`／`precheck_B87_before.md`／corpus 原本 `0__DawForAIND_renumbered_B54_split20260905.txt`／`docs/_work/idmaster_working_20260918.tsv`／`docs/records_B79-83/tools/h2g.py`（selftest PASS）
- 結果: 実項 18／REF 1（D07344）。新規仮TMP 16件（P×10・N×1・I×1・T×1・O×3）。ISSUES 11項目。全19ファイル well-formed 確認済み（xml.etree）。

## 全ファイル共通の処置
1. `<note type="source" xml:lang="ar">` を corpus 原本から挿入（刊本連番を除去、`|` 行なし、`<note type="translation">` 直前）。
2. 初版の `<respStmt>` は改変せず、校閲 respStmt（persName=claude-b87c-review、2026-09-18）を追加し修正内容を note に記録。
3. `relation/@n` を規約A（親族は @n なし、非親族のみ通し番号）に統一。
4. 西暦を h2g.py（proleptic Gregorian）で再計算（年のみ→年、月のみ→YYYY-MM、日→YYYY-MM-DD）。
5. ja 訳の語中「ビン」→「ブン」、翻字・立項番号・推測句の混入を除去、en 訳は英語で全面照合。
6. 規則16: ニスバ／施設／職に由来する placeName（residence event・state・death）を除去し、必要な根拠は note に記述（詳細は ISSUES §Dc-10）。
7. 規則8: affiliation と state／event の二重符号化を解消（D07345・D07357・D07367・D07377）。
8. 第三者言及（ذكره／أرخه／قال／وصفه／حكى／تبعه）は relation から Pattern A の `event type="cultural" subtype="mention"` に変更。

## ファイル別

### AIND-D07342（実項）
- 父: 汚染番号 #TMP-P-000204（D0106の息子 حسن）→ **#AIND-D02538**（الحسن بن حسين بن علي بن عبد الدائم بدر الدين الأميوطي … والد المحب محمد الآتي、相互参照）。
- 生年 835-12-13 → **1432-08-20**（初版 1431 は誤り）。
- 居住: 「الحسيني سكنا」により residence を الحسينية(#TMP-L-00007) に。ニスバ由来の القاهرة（学習 event・state placeName）を除去。
- teacher(al-Sakhāwī, لازم) の空 field を「الإملاء」(#TMP-S-00038) で補完。persName full から「سكنا」除去。

### AIND-D07344 → REF_AIND-D07344（REF・方式X）
- 原文末尾「مضى」＝転送指示。`type="reference" subtype="LIMBO"`、`REF_` リネーム、nisbah/kunyah/laqab/relation/event を除去、原文 note と `note type="reference" target="#AIND-D03619"` を付与。
- 転送先 #AIND-D03619 = عبد الرحمن بن حسن بن حمزة بن يوسف المحب أبو الفضل الحلبي الحنفي الكاتب نزيل القاهرة（「ويسمى أيضا محمدا … ليتميز عن أخ له اسمه محمد」）。直前項 D07343（أخو عبد الرحمن الماضي）と整合（ISSUES §Dc-1）。

### AIND-D07345（実項）
- 空の son relation（active=""）→ #NEEDID（息子は「عرض علي كتبا」と描写＝規則14の対象外）。息子の行為を本項主の relation(recipient of book presentation)・event に二重化していたものを除去し son の note に集約。
- ニスバ由来の residence（بلبيس・القاهرة）と affiliation（جامع الأزهر）を除去。ja「マハンマド」→「ムハンマド」。

### AIND-D07347（実項）
- 「السمين」は祖父名（ابن السمين）＝nisbah 要素を除去し name_only「محمد بن حسن بن السمين」（「يحرر اسم جده」により cert low）。
- 伝承連鎖「روى عن خاله … عن العفيف اليافعي إجازة」: イジャーザは叔父↔ヤーフィイー間と読み、本項主の teacher は叔父のみ（#NEEDID teacher×2 を統合）。叔父 أحمد بن إبراهيم العسيلي に **#TMP-P-NEW87c-01**（maternal_uncle relation も同番号）。
- 「ذكره التقي بن فهد في معجمه」→ mention event(#AIND-D09211)。生年 746-06 → **1345-10**。ja 訳の未翻訳アラビア語名・「ベン」を修正。

### AIND-D07348（実項）
- 父 **#AIND-D02549**、弟 **#AIND-D03620**（الوجيه عبد الرحمن）、子 **#AIND-D08744**（الصدر محمد；汚染番号 #TMP-P-000529 を差し替え）、娘 **#AIND-D13336**（عائشة）をいずれも corpus 相互参照で同定。
- 「سبطي الجلال البلقيني」から father-in-law **#AIND-D03709** を復元（初版 other/#NEEDID；ISSUES §Dc-8）。
- 没年「تقريبا」→ cert medium（834 → 1430）。

### AIND-D07350（実項）
- #TMP-P-000275（الحجار）は本項では登録実体そのもの（「بحضوره في الثالثة على الحجار」）のため維持。
- イブン・ハジャルが本項主に読んだ → student relation（active=本項主、passive=wd:Q471116、規則15）、event teaching @ الصالحية(#TMP-L-00003)。書名 أخبار إبراهيم بن أدهم に **#TMP-T-NEW87c-01**、ニスバ الدقاق に **#TMP-N-NEW87c-01**。
- 「قال شيخنا في معجمه」「تبعه المقريزي في عقوده」→ mention event×2（bibl #TMP-T-00104／#TMP-T-00122）。
- 訳の誤り（「彼の前で彼に朗読した」）を是正: 幼時に الحجار のもとで聴講したものをイブン・ハジャルが本項主に読んだ。没地は原文に明示なし。

### AIND-D07353（実項）
- 生年 764 → **1362**（初版 1363）。原文にない出生地 طرابلس を birth から除去。
- 師: الشهاب أحمد بن الحبال → **#TMP-P-NEW87c-02**（cert medium、自称）；ابن البدر → #NEEDID（シュフラのみ）；العز بن جماعة → **#AIND-D07198**（ISSUES §Dc-2）；الجمال الأمشاطي → **#TMP-P-NEW87c-03**（ISSUES §Dc-4）。
- 「لقيه ابن الأسيوطي قريب سنة سبعين وقال إنه كان مستحضرا」→ met relation(#AIND-D03608＝スユーティー, cert medium) ＋ mention event（when-custom=0870／1465、cert medium）。初版の student(#NEEDID, when="0870") を置換。
- teacher の field「الحديث」は原文に明示なしのため除去。residence القاهرة は「قدم القاهرة」により維持。

### AIND-D07355（実項）
- name_only を3世代に。field「الحديث」除去。ニスバ由来の residence（المحلة・القاهرة）除去。

### AIND-D07357（実項）
- 毒wd Q160851 → **Q228986**。
- #TMP-P-000529×2 → 子 **#AIND-D08746**（subtype son）・孫 **#AIND-D09072**（other→grandson）。後任 successor relation（子）を追加。
- affiliation(teach/employed) を除去し state のみ（規則8）。الجردكية に **#TMP-I-NEW87c-01**。ニスバ由来の حلب（residence・state placeName）を除去し note に記述（子 D08746「بالجامع الكبير بحلب」で裏付け）。

### AIND-D07359（実項）
- 父 #TMP-P-000204 → **#TMP-P-NEW87c-04**（حسن بن علي بن عبد الرحمن、أستادار قرقماس الشعباني＝#AIND-D06340）。
- 「أثكل ولدا له」＝規則14 → 空 son relation と other event を除去。
- 「سمع على بعض السيرة … ثم بعض الدلائل」を「سمع عليّ」と読み、teacher(al-Sakhāwī, cert medium)＋cultural event 895/896（1489/1490）（ISSUES §Dc-5）。生年 826 → **1422**（初版 1423）。

### AIND-D07367（実項）
- 父 **#AIND-D02921**（خليل بن يعقوب）・兄弟 **#AIND-D00717**（أحمد）を追加、「صهر أخي」は父の項「صهر أخي أبي بكر」により **#AIND-D10729** の brother-in-law に確定（重複 relation 統合、@n なし；ISSUES §Dc-9）。
- 没月 892-10 → **1487-09**。没地 القاهرة（施設からの推定）を除去。residence placeName を جامع الحاكم(wd:Q775838) に、affiliation(reside) と「المشاهد」visit を除去。state ref → #TMP-O-00080（واعظ）。

### AIND-D07370（実項）
- 「جمال الدين بن شمس وهو معنى خورشيد بالفارسي」＝شمس は父名の訳語で祖父ではない → grandfather relation を除去、name_only「محمد بن خورشيد」。
- 「قرأ على بعض الأربعين النووية وأكمل سماعها」＝「قرأ عليّ」→ teacher(al-Sakhāwī, قرأ＋سمع, bibl #TMP-T-00044) を追加。ja「マホメット」を是正、en の『』除去。

### AIND-D07371（実項）
- 父 #NEEDID → **#TMP-P-NEW87c-05**（「الآتي أبوه」だが corpus に本伝なし＝欠番；合同索引 D11651 は規則11により不使用；ISSUES §Dc-7）。
- ニスバ由来の residence مكة を除去。ja/en 訳冒頭に欠けていた名前を補完。

### AIND-D07374（実項）
- 父 #NEEDID → **#AIND-D02949**（داود بن عثمان بن علي النظام الهاشمي العدني）。兄弟 #TMP-P-000490 → **#TMP-P-NEW87c-06**（عبد الله）。
- 「أرخه ابن فهد」→ mention event(#AIND-D09211, cert low：没863≤871)。没月 863-03 → **1459-01**。
- 職 مباشر → **#TMP-O-NEW87c-01**（placeName جدة は「مباشري جدة」で明示）。職由来の residence جدة を除去。ja 冒頭「マムルーク朝期」等の補足を除去。

### AIND-D07375（実項）
- 父 #NEEDID → **#AIND-D02950**、兄弟 علي #TMP-P-000530 → **#AIND-D05143**、兄弟 سليمان → **#TMP-P-NEW87c-07**。没地 اسكندرية → gn:361058。「أرخهم ابن فهد」→ mention event(#AIND-D09211, cert low)。

### AIND-D07377（実項）
- 生年 797「ظنا」→ cert medium、**1394**（初版 1395）。没日 840-02-19 → **1436-09-11**（tabular で日曜＝「ليلة الأحد」と整合；初版 ja 訳「9月1日」は誤り）。
- 師 عائشة ابنة ابن عبد الهادي → **#AIND-D13339**（ISSUES §Dc-3）。弟子 أبو العباس المقدسي → **#TMP-P-NEW87c-08**（student relation の方向を規則15に是正；ISSUES §Dc-6）。البقاعي wd:Q12198099 → **#AIND-D00207** の mention event。
- affiliation(buried) と death 内 burial の二重化を解消。ニスバ由来の residence を除去。#TMP-I-00091 は実体一致で維持。ja「マクス」→「ムカイス」。

### AIND-D07378（実項）
- 父 #NEEDID → **#AIND-D02958**（داود بن محمد بن أبي القسم التزيلي الحكمي、زاوية 持ち）。ザーウィヤ継承を predecessor relation＋state（**#TMP-O-NEW87c-03**）で符号化。
- 「أخذ عنه الذي بعده بمكة」→ student relation(passive=#AIND-D07379、event teaching مكة)、「حكى لي عنه」→ mention event(#AIND-D07379)。初版の visit event を置換。

### AIND-D07380（実項）
- spouse（「تزوج」のみ）を規則14で除去、daughter の空 active を #NEEDID に、「بيت البارزي」（家系）への relation を除去し note に集約。
- 「يقال إنه جاز الخمسين」（895年）から birth notAfter 845／1442、cert low（逆算を note に明記）。
- 「شيخها في العقليات」は مدرس state の note に統合、年のみの residence n=5 を除去。

### AIND-D07381（実項）
- 子 أحمد #NEEDID → **#TMP-P-NEW87c-09**、子 علي #TMP-P-000530 → **#TMP-P-NEW87c-10**。職 شيخ الناحية → **#TMP-O-NEW87c-02**、منية بدران を orgName→placeName に是正。
- マッカ訪問を 898年巡礼期（when-custom=0898-12／1493-09）で記録。met(al-Sakhāwī) n=1。

## precheck 指摘への対応
| precheck | 対応 |
|---|---|
| D07342 #TMP-P-000204 | → #AIND-D02538 |
| D07348 #TMP-P-000529 | → #AIND-D08744 |
| D07350 #TMP-P-000275 | 登録実体（الحجار）と一致＝維持 |
| D07357 Q160851 ／ #TMP-P-000529×2 | → Q228986 ／ #AIND-D08746・#AIND-D09072 |
| D07359 #TMP-P-000204 | → #TMP-P-NEW87c-04 |
| D07374 #TMP-P-000490 | → #TMP-P-NEW87c-06 |
| D07375 #TMP-P-000530 | → #AIND-D05143 |
| D07377 #TMP-I-00091 名前不一致 | 実体一致＝維持 |
| D07381 #TMP-P-000530 | → #TMP-P-NEW87c-10 |
