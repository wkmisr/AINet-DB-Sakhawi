# 校閲記録 B88b（2026-09-24 / claude-b88b-review）

- 対象: `docs/_work/B88_incoming/B88/` のうちチャンク B88b（`AIND-D07431`〜`AIND-D07475`、20件、in-place 確定）
- 参照: corpus `0__DawForAIND_renumbered_B54_split20260905.txt`（転送先・関係者探索は原本に対して実施）/ `docs/_work/B88_incoming/corpus_B88.json` / ID-Master `docs/_work/idmaster_ext_20260924.tsv` / `precheck_B88_before.md` / `docs/records_B79-83/tools/h2g.py`（グレゴリオ暦、`--selftest` PASS）
- 内訳: **実項 20件 / REF（転送見出し）0件**。転送指示（مضى／يأتي／في ابن…／فيمن جده… 等）を持つ項は本チャンクになし。`D07458`「محمد بن سليمان الحكري .」は名のみだが転送指示がなく実項（規則13）。
- 新規仮TMP **20件**（P×11・I×3・O×2・S×2・T×2、`TMP_NEW_B88b.tsv`）、要裁定 **§Db-1〜§Db-12（12件）**
- 全20件 `xmllint --noout` 通過。全20件に corpus 原文の `<note type="source" xml:lang="ar">` を `<note type="translation">` の直前に挿入（初版はいずれも未挿入。刊本立項番号は除去、改行は原本どおり）。
- 全20件に `resp`=「校閲」（＋「翻訳校正」）、`persName`=`claude-b88b-review`、`date when="2026-09-24"` の respStmt を追加。初版作成者（Assistant 4）の respStmt は不改変。
- 西暦は全件 `h2g.py` で独立再計算（proleptic Gregorian）。初版の西暦誤り 6件（D07445 没年ズレ・二択未表現、D07448 日精度欠落、D07463・D07467・D07470 月精度欠落、D07475 年ズレ）とヒジュラ年の `@when` 混入 1件（D07457 event）を是正。
- relation の `@n` は規約A（親族なし・非親族のみ通し番号）に全件統一。初版はほぼ全件が旧規約（親族にも n、student/teacher を別系列で採番）。
- 第三者言及（ذكره/أرخه/قال فيه）は全件 Pattern A の mention event に置換（D07459・D07463・D07466・D07467・D07470・D07475）。初版は統制外 subtype（mentioned_by／chronicler／other／validator）の relation。
- 規則22-1 により、ニスバ・施設所在地・職の勤務地に由来する placeName／residence event を除去（D07444・D07445・D07448・D07459・D07461・D07463・D07472・D07473・D07475）。照応代名詞（بها）による地名は保持（D07445・D07452）。規則20により `جاور` の placeName を除去（D07448・D07472）。
- precheck 指摘: D07472 の TMP-N-00128（ニスバ番号の person 流用）→ #AIND-D07896、D07473 の TMP-N-00808 → 新規 TMP-P-NEW88b-11。名前不一致（D07445・D07461・D07466・D07470）はいずれもラテン翻字の見かけ上の不一致で実体一致、修正不要。毒wd・立項連番混入・`[要照合wd]` は本チャンクになし。
- 訳文は全件で原文と逐語照合し、「ビン」→「ブン」（規則17）、en から日本語括弧・換算値・推測句・立項番号を除去。
- 仮番号は `TMP-X-NEW88b-nn` 形式。

---

## AIND-D07431（محمد بن سعيد、父 الشمس الوراق）— 実項
1. 「الشمس الوراق أبوه」を父の呼称と読み、本項主の laqab「الشمس」を除去（ISSUES §Db-1）。父 #NEEDID（裸のラカブ＋職名、規則3）。「أظنه نسب لجده」により سعيد を祖父 cert medium（初版は active/desc 空欄）。
2. 没月 `when="1483"` → `1483-07`（888-06）。visit event・state تاجر（wd:Q215536）に原文 desc。

## AIND-D07444（محمد بن سلمان الشنباري）— 実項
1. 「قرأ القراءات」の空 teacher relation（active=""）を除去し learning event に（規則14）。
2. الديمي：TMP-P-000215（汎称）→ #AIND-D04876（cert medium、§Db-8）。bibl صحيح البخاري #NEEDID → wd:Q1023470。「وكذا قرأ علي فيه」＝サハーウィーへの朗読。
3. 「صحبة ابنة العلم البلقيني」→ 新規 TMP-P-NEW88b-01（§Db-2）、subtype companion。ハッジ when-custom 0884（سنة السلطان）cert medium。
4. 「وكان منزلا في سبعها」を status state に新設（初版は誤訳のうえ未符号化）。「ربما أقرأ الأبناء」→ state TMP-O-00029 cert medium、placeName القاهرة・residence event を除去（規則22-1）。

## AIND-D07445（محمد بن سليمان بن أحمد … ابن الفقيه سليمان）— 実項
1. 没日を二択 notBefore/notAfter（842-11-26／843-11-26＝1439-05-19／1440-05-08）に。生年 770「تقريبا」cert medium。
2. 父 #NEEDID → 新規 TMP-P-NEW88b-02（ナサブから復元、通称 الفقيه سليمان／السنباطي）。name_only を3世代に（規則5）。
3. ابن الميلق への2 relation を1本に統合（bibl 2点）。「بحث على قاضي بلده التاج عتيق」→ 新規 TMP-P-NEW88b-03・方法 TMP-S-NEW88b-01（§Db-3）。
4. 「لقيه ابن فهد والبقاعي … وكتبا عنه」→ student relation（كتب、event 838・دمياط）。ابن فهد＝D09211 cert low（§Db-3）、البقاعي＝#AIND-D00207（初版 wd:Q12198099）。空 field（TMP-S-00040）除去。
5. 英語 desc の event を原文 desc に置換（規則7）。原文に明示のない placeName（learning event の دمياط・作詩の دمياط）・residence event を除去、「بها」照応の دمياط は保持。詩3行を訳し直し。

## AIND-D07448（محمد بن سليمان بن حماد السكندري）— 実項
1. 師 4 relation（#NEEDID）→ #AIND-D08403（الشمس جنيبات：الفرائض＋الحساب）・#AIND-D03317（息子 شعبان بن جنيبات：الميقات＋الشروط）の2本に統合。分野 الشروط に新規 TMP-S-NEW88b-02。
2. 父 → 新規 TMP-P-NEW88b-04（⚠汎用名）。祖父 حماد #NEEDID。
3. جامع صفوان のプレースホルダ #TMP-I-00000 → 新規 TMP-I-NEW88b-01（affiliation employed ＋ cultural event「يقرأ فيه البخاري」）。
4. 没地 الاسكندرية（ニスバ由来）・travel event・جاور の placeName を除去（規則20・22-1、§Db-12）。没日 `1470` → `1470-12-04`。「بارع في الفرائض والحساب」を status state に。

## AIND-D07452（محمد بن سليمان بن داود الطائفي الغمري）— 実項
1. 「سمع على أشياء」＝「سمع عليّ」（B87 §D-18）→ teacher wd:Q4120128（初版 #NEEDID・訳文「彼から聴聞」を是正）。
2. أبو العباس＝#AIND-D01456（أبو العباس الغمري、cert medium、subtype servant、§Db-10）。
3. 父 → 新規 TMP-P-NEW88b-05（⚠汎用名）。residence event に orgName جامع الغمري（TMP-I-00072）と「بها」照応の desc。

## AIND-D07453（محمد بن سليمان بن داود اللاري المؤذن）— 実項
1. 「ممن سمع مني بمكة」型：field 除去・relation 内 event のみ（規則2）、重複 study event 除去。
2. state المؤذن #NEEDID → wd:Q239718。父 → 新規 TMP-P-NEW88b-06（⚠汎用名）。

## AIND-D07457（محمد بن سليمان بن وهبان المدني）— 実項
1. 甥 سليمان #NEEDID → #AIND-D03159（سليمان بن علي بن سليمان بن وهبان المدني）。父 → 新規 TMP-P-NEW88b-07。
2. الزين المراغي＝#AIND-D10690 を確認、event `@when="0815"` → when-custom/when（1412）。

## AIND-D07458（محمد بن سليمان الحكري）— 実項（名のみ）
1. 転送指示なし→実項（規則13）。corpus に同名の二重立項なし。father relation（#NEEDID）追加、原文 note 挿入。

## AIND-D07459（محمد بن سليمان الفيومي بواب الزمامية）— 実項
1. 「ذكره ابن فهد مجردا」→ mention event（D09211 cert low）。
2. الزمامية → 新規 TMP-I-NEW88b-02（state بواب の orgName）。重複 affiliation（規則8）・residence event（規則22-1）を除去。placeName مكة は「بمكة」明示のため state に保持。

## AIND-D07461（محمد بن سنقر أبو السعود الجمالي）— 実項
1. 4 relation を伝授形態別3本に整理（سماع 2書／إجازة／قراءة）、field・learning event（مكة×4）除去。bibl حديث زهير العشاري → 新規 TMP-T-NEW88b-01。
2. state شاد عمارة السلطان #NEEDID → TMP-O-00241、両 state の placeName مكة 除去（§Db-11）。父 سنقر #NEEDID（サハーウィーからの聴聞・イジャーザを note に）。

## AIND-D07462（محمد بن سنقر ناصر الدين الأستادار）— 実項
1. 要素構成は原文と一致。没年 809＝1406 確認。訳文の注記除去。

## AIND-D07463（محمد بن سنقر الشرفي، لغيلغ）— 実項
1. 「أرخه ابن المنير وقال …」→ mention event（TMP-P-000342）。patron relation（父の مولى 関係）除去、父 → 新規 TMP-P-NEW88b-08（§Db-4）。
2. 埋葬地 تربة الصوفية الصغرى → 新規 TMP-I-NEW88b-03。residence event（الحسينية、モスク所在地）除去。没月 `1456` → `1456-05`。

## AIND-D07464（محمد بن سنقر ابن أخت تغري بردى القادري）— 実項
1. 叔父 #NEEDID → #AIND-D02273（maternal_uncle）。ニスバ القادري は叔父のものとして除去、full を「محمد بن سنقر」に。
2. 「ولدي」→ TMP-P-000549（companion）。聴聞の伝授者は #NEEDID 維持（§Db-5）。「ومات」に death 要素（日付なし）を追加。

## AIND-D07465（محمد بن سودون دقماق ناصر الدين）— 実項
1. 父 → #AIND-D03212、母 → #AIND-D13333、同母姉妹 → #AIND-D13419、母方祖父 TMP-P-001100 を追加。D03212 側の誤配置は §Db-6。
2. state مقطع → 新規 TMP-O-NEW88b-01（status）。「وهو الآن حي」を other event に。

## AIND-D07466（محمد بن سويد الشمس المصري）— 実項
1. 兄弟 البدر حسن → #AIND-D02549。「ذكره شيخنا في أنبائه」→ mention event（wd:Q471116・TMP-T-00034）。ja「スワイハ」→「スワイド」。

## AIND-D07467（محمد بن سيف بن محمد بن عمر بن بشارة）— 実項
1. 没月 `1416` → `1417-01`（819-12）。صفد は埋葬地でなく移送先→ burial placeName を除去し other event（placeName صفد）に。
2. 「ذكره شيخنا أيضا」→ mention event（bibl なし）。父 → 新規 TMP-P-NEW88b-09。

## AIND-D07470（محمد بن شاش شرف الدين）— 実項
1. 「ذكره العيني」→ mention event（wd:Q257745）。没月 `1442` → `1443-01`（846-09）。

## AIND-D07472（محمد بن شعبان بن علي بن شعبان الغزي）— 実項
1. 師：TMP-N-00128 → #AIND-D07896（الجوجري）、الشرف بن الجيعان #NEEDID → #AIND-D10249、العبادي TMP-P-000085・أبو السعادات D08815・الزيني زكريا D03042 確認。空 field（TMP-S-00000）5件除去。
2. 「سمع مني」の方向を是正（規則15）。兄弟 أحمد → #AIND-D00770、عبد القادر の誤同定 D04089 → #AIND-D04123。父 → 新規 TMP-P-NEW88b-10。
3. جاور の placeName・state の placeName القاهرة・重複 affiliation الصالحية を除去、orgName に repo 先例 wd:Q7404512（§Db-7）。name_only 3世代・full から居住句除去。

## AIND-D07473（محمد بن شعبان بن محمد البوتيجي）— 実項
1. الولي العراقي：TMP-P-000011 → #AIND-D00844（§Db-8）。حضر（講義）と سمع（أمالي、新規 TMP-T-NEW88b-02）を別 relation に。
2. TMP-N-00808 の person 流用 → 新規 TMP-P-NEW88b-11（المعلى）、validator relation → mention event（§Db-9）。親族 الزين البوتيجي → #AIND-D03717。
3. 没年 قريبا من سنة سبعين ظنا → when-custom 0870 cert low（規則4）。residence event（ニスバ由来）除去。「تنزل في الجهات」status state、「باشر في بعض جهات الجوالي」→ 新規 TMP-O-NEW88b-02。

## AIND-D07475（محمد بن شعبان الشمس محتسب القاهرة）— 実項
1. 没日 `1440` → `1441-03-24`（844-10-21）。生年 780 cert medium。
2. 「قال المقريزي」→ mention event（wd:Q293604）。political event に persName المؤيد（#AIND-D03345）、英語 desc・placeName・cert を原文 desc に置換。residence event（職の所在地）除去。state label「محتسب القاهرة」（placeName は原文明示）。
