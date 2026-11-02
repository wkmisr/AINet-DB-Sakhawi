# 独立検証パス・ブリーフ（B134-138、2026-10-26）

あなたは al-Sakhāwī『al-Ḍawʾ al-Lāmiʿ』の TEI-XML プロソポグラフィDB（AINet-DB）の**校閲結果を検証する独立検証者**です。校閲者（別のエージェント5名、チャンク B134〜B138 各20件）が作った修正版 XML 100件（実項88＋REF化12）に、校閲者自身が作り込んだ誤り・取りこぼしがないかを、原文と突合して洗い出してください。**XML・corpus・ID-Master・Individuals は一切修正しないでください**（読み取りのみ。報告ファイルだけを書く）。git 操作も禁止です。

## 作業環境
- すべて `mcp__remote-devices__device_bash`（Mac 上）で行う。毎回 `cd "$HOME/mnt/AINet-DB-Sakhawi" && ...`。呼び出しごとに新しいシェル。ファイルの読み書きは python3 / cat / sed で（クラウド側の Read/Edit/Write/Bash はこのマシンのファイルに届かない）。
- **検証対象（校閲後 XML）**: `docs/_work/B134-138_incoming/B134-138/` の100件（`REF_` 接頭辞付き12件は転送見出し）。受領チャンクとの対応は `docs/_work/B134-138_incoming/origin_folders.tsv`（ファイル名<TAB>チャンク）。
- **校閲前（Gemini 初版）**: `docs/_work/B134-138_incoming/orig/`（比較用。校閲で消えた情報のうち、消すべきでなかったものがないか）。
- **原文**: `docs/_work/B134-138_incoming/corpus_B134-138.json`（100件の本文、キー `D08022` 形式）。corpus 全体: `docs/_work/B134-138_incoming/vc/corpus_index.json`（AIND-ID → {text, dollars, line…}）。`python3 -c "import json;d=json.load(open('docs/_work/B134-138_incoming/vc/corpus_index.json'));print(d['AIND-D06323']['text'])"` で任意の項を読める。**校閲者が付けた同定（#AIND-Dxxxxx）は、必ずこの辞書で相手側の原文を読んで裏取りすること。**
- 検索ツール（cwd=リポジトリルート）: `python3 docs/_work/B134-138_incoming/vc/hw.py "<語1>" "<語2>"`（corpus 見出し先頭260字の AND 検索）／`vc/idsearch.py "<文字列>" [件数]`（ID-Master のアラビア語・ラテン語・Note 検索）／`vc/idm.py TMP-P-000010`（ID 行表示）／`vc/rgrep.py "<文字列>" [件数]`（repo の Individuals 全文検索。サブフォルダ再帰）／`python3 docs/_work/B134-138_incoming/vc/h2g.py 886-9 874-3-15 850`（ヒジュラ→西暦。**グレゴリオ暦（proleptic）を正とする**。`--selftest` あり）。
- ID-Master: `docs/_work/idmaster_ext_20261026b.tsv`（2026-10-26 に Drive から再取得したシート実物 8,480 行（ヘッダ込み）。列=[登録者,Category,Arabic,Latin,ID,Note,修正]）。新規 TMP は仮番号（`TMP-x-NEW134-nn`〜`NEW138-nn`）のまま XML にある。典拠台帳: `python3 docs/authority/lookup.py Q…`（wd/gn の中身、ネット不要）。
- 校閲者の記録: `docs/records/records_B134-138/` の `REVIEW_NOTES_B1xx.md`・`ISSUES_B1xx.md`・`TMP_NEW_B1xx.tsv`・`FIXLOG_B1xx.tsv`（B134〜B138）、precheck: `precheck_B134-138_before.md`、規約全文: `CHUNK_BRIEF_B134-138.md`（**まずこれを読む**。統一規則1〜52・頻出確定ID・汚染番号を含む）。

## 規約の要点（CHUNK_BRIEF が正）
第三者言及は Pattern A（event cultural/mention + persName ref）／relation 向き: 師弟は active=師・passive=学生、親族・社会関係は active=相手・passive=本項主／TMP-P 発行ルールと父は必ず relation（本伝→AIND、祖父名復元→TMP-P、裸名→#NEEDID の father relation を必ず立てる＝規則3 改訂）／@when は西暦（グレゴリオ）のみ・精度は when-custom に合わせる、ヒジュラは when-custom／原文にない属性・地名を補わない（規則22）／規則25 原文どおり読む／規則26 同定は確実な場合のみ（通称・推定では AIND に同定せず TMP、ただし ابن فهد 振り分け規則は例外）／規則27 連結レコード／規則28「رأيته فيمن عرض عليه」「كتب بالشهادة」型は本項主＝行為者／規則29「خلف أخاه/والده」は predecessor／規則30 頻出確定IDは年代確認／規則31 relation desc は相手名のみ／規則37 本項主の見出しナサブで特定できる父祖は AIND で relation／規則38 本伝探索はナサブ1段ずらし・女性部・repo 既存使用まで／relation の @n は規約A（親族には付けない、非親族のみ1起点連番）／初版 respStmt は非改変、校閲 respStmt は `claude-b1xx-review`・2026-10-26／en 訳は英語／転送見出しは REF 方式X／汚染番号 TMP-P-000529・000530・000064・000664 等は別人流用禁止／毒 wd Q160851→Q228986、Q191314→Q233387／wd・gn は記憶から書かない。

## 本バッチの REF（転送先の原文を必ず読み、転送先として正しいか確認）
B134: D08022→**D07993**（محمد ولي الدين … المالكي أخو الذي قبله、「فيمن جده أحمد بن عبد العزيز بن القسم」のナサブで閉合するか）／D08035→D07982（أبو الفتح بن إسمعيل … ابن الريس）／D08047→**D08579**（الجمال أبو المحاسن الشيبي）／D08050→D08038（الشمس البكري）。B137: D06327→D06323（قراجا … ويعرف بالطويل、「تقدم قريبا」）／D06331→D03204（سودون … ويعرف بقراقاش）／D06333→D04868（「هو X」型を REF とした判断も点検）／D06347→D06348（「قشتام」の見出し原文）。
**綴り相互参照型（repo 初出、暫定方式＝REF・`target="#NEEDID"`・見出し群を editorial note に列挙）**: B135 D02818（خاير بك → 見出し群「خير بك」D02928〜D02937）／B137 D06354（قطلبك → 「قطلو بك」D06361・D06362・D06363）／B138 D06368（قنباك → قانباك）・D06369（قنباي → قانباي）。**4件で方式・note の書式が揃っているか、列挙された見出し群が corpus で漏れなく正しいか**を確認。
**実項として扱われたもの**: D08024（possible_identity low → D08883、索引 D11473）／D08025（له ذكر فيه、兄弟 D03313）／D02800（兄弟 D00012・حيدر）／D06317（له ذكر في ابنه、子 D05925）／D06376（前任 D06375）／D06304（D06295 の転送先）／D02822（「أظنه المذكور في نابت بن نعير」§D135-6）。

## 本バッチ固有の検証点
- **校閲者が付けた AIND 同定を相手側原文で裏取り**（全件は REVIEW_NOTES_B134〜B138 にある。主要なもの）: B134: D08023 弟子 خير الدين بن القصبي D08670／D08030 أبو العباس بن الغمري D01456／D08031 子 D08919／D08040 النجم بن فهد＝**D05979**（D05979 は「صاحبنا ابن فهد」の番号。النجم عمر بن فهد と同一か要確認）／D08054 父 D05100／**D08041＝ID-Master TMP-P-001238 と同一（§D134-3、D04601 の父）**。B135: D02805 従兄弟 D06729・الجمال الحنبلي D04509（固定呼称 cert medium＝規則26例外2の要件を満たすか）・الزين رضوان／D02807 弟 D03639／D02815 الولوي بن قاسم D08447／D02819 الشيخ اينال D02117・孫 D10593／D02822 حيدرة D02796／D02825 قانباي الحمزاوي D06265／D02827 يحيى الأستادار D10263／D02828 主人 D03200・後任 D06329。B136: D02833 前任 D10122／D02834 الفتحي D02697（TMP-P-000584 名寄せ §D136-1）／D06301 前任 قجماس D06314（medium）・TMP-P-000671 ⇄ D06301（§D136-3）／D06313 父 D06339・叔父 D02266・大叔父 D02972・الجمالي يوسف D10460／D06317 子 D05925。B137: D06345 父 D03045・祖父 D03175・前任 D03401（在任年 883/887 是正）／D06349 فارس D06143・المظفر أحمد D00775／D06324 主人 D02369（TMP-P-000783 名寄せ §D137-1）／D06328 D10491／D06353 العزيز يوسف D10456／D06336 祖父 D10146（medium）／D06323 妻 D12903（medium）。B138: D06357 تنم D02315／D06359 子 D06236／D06371 D09921・D06050・D02560／D06374 D01909・D02450／D06375 前任 D09966（没年 897 是正）／D06378 D02326・D10147・D03036／D06381 D13655。**規則23・26（例外2 を含む）・37 に照らして cert の付け方を点検**。
- **新規 TMP（TMP_NEW_B134〜138.tsv、計40件）の本伝・既登録の見落とし**（11バッチ連続で検証パスが最多捕捉）。とくに TMP-P: **الظاهر بلباي（D06353 舅、B137 NEW137-03）＝スルターン。corpus 見出しは点の揺れ「يلباي」（ي 部）の可能性が高い＝hw.py「يلباي」「الظاهر」で必ず引く**／سودون الشيخوني（D06359）／منجك اليوسفي（D06362）／البدر بن مكتوم（D06372）／ابنة تنم الحسني（D06357 妻＝女性部 D13xxx を「تنم」で引く）／عبد الرحمن بن قطلو بك（D06361、「الماضي」＝見出しナサブをずらして引く）／عرر بن نعير・أشعار（B137）／أوزار（B136）／أحمد بن إبراهيم العجمي・حمزة بن الأسل・سليمان بن داود المنهلي・دوغان بن جعفر・مجاد بن ثابت・الوزير اللباني・كافور مولى الولوي・أرنبغا نائب قلعة صفد（B135）／B134 の TMP-P 4件。**名の1語＋ニスバ・本文中「ويعرف بـX」・ニスバ索引・点の揺れ（ب/ي/ن/ت）・分かち書き（قطلو بك／قطلوبك）で引き直す**。職の TMP-O（شاد الطور・شاد الزردخاناه・مقدم الطباق・تصدير・لالا ほか）は語根で Office を grep（規則41）。TMP-L الرملة（カイロ市中、§D135-5）・تروحة（§D137-3）・قلعة النجا、TMP-I زاوية خجا بردي・تربة خوند هاجر、TMP-T تاريخ المدينة。**チャンク間で同一対象の重複発行がないか**。
- **العيني の参照形**: 全件 `#AIND-D09832`＋`corresp="wd:Q257745"` か（wd 単独が残っていないか）。ابن الملقن が出ればD05895＋corresp。
- **チャンク間の整合**: マムルーク単名項の父 #NEEDID・主人 patron（主人がアミールの場合の立て方、§D135-3・§D138-1）・職（state office、TMP-O-00107 の範囲）。「صهر／حمو／زوجا لابنة」の向きと subtype（D06353・D06355・D06357・D06361・D06365・D06372）が5チャンクで揃っているか（repo 先例 `father-in-law`・`son_in_law` と照合）。「في أيام／في دولة X」を relation にしていないか（B136 は state note に統一）。他人の職（D06357・D06362「نائب الشام」、D02825）を state にしていないか。
- **父 relation（規則3、単名項も #NEEDID）**: 全実項に father relation があるか。
- **「ممن سمع مني」型と شيخنا 師型**: 向き、場所、年。D08060「سمع على قريب التسعين」（عليّ）／D08023（本項主が試問者）／D02834（読み手 الفتحي）／D02805「شيخنا الزين رضوان」（イブン・ハジャルではない）。
- **「أرخه ابن فهد」振り分け（規則43、cert は event 側）**: D08041・D08054・D02814・D02824・D06316・D06346・D06371・D02820・D06361。没年と ID・cert の対応を全件点検。ابن عزم は D08351（D02832）。
- **日付**: 一の位のみ 80X（D06309・D06315・D06317・D06318・D06319・D06356・D06362・D06372・D06377）／D06311 نيف وثلاثين／D02839 حدود الخمسين／D08040 生 قبل 770・没 قريب الأربعين أو قبلها／D06313（校閲者が 1438-04 に是正）／D06345・D06375（世紀誤りの是正）／逆算生年各種／D02841「أصيب في الحريق」。**全日付を h2g.py で独立に再計算**。D06324・D06361「مات .」で death を作っていないか（規則45）。
- **規則47・48**: D06321「عين لإمرة الحج فمات قبل أن يخرج」を state にしていないか。
- **規則22**: placeName の除去しすぎ・残しすぎ（B135 は補完 placeName 16件を除去＝除去しすぎがないか、施設名「رواق ابن معمر」「المؤيدية」「مضارب الخام من الرملة」「المؤمني」が残っているか）。
- **ISSUES（B134 4／B135 6／B136 5／B137 7／B138 6）のうち、統一規則・repo 先例・corpus 証拠で解決できるもの**に解決案を添える。
- **ID-Master 未登録 wd/gn の新規使用**: ISSUES に「未確認」として残っているか（D06320 علي دولات wd:Q4895760 は ID-Master 登録済と校閲者、D08041 زمزم wd:Q146038 は ID-Master 既登録と校閲者＝それぞれ ID-Master と典拠台帳 `python3 docs/authority/lookup.py Q4895760` で確認）。


## 出力と記録（規則24）
指定された報告ファイルに、**誤りと思われるものだけ**を、ファイルID・箇所・根拠（原文引用）・提案修正の4点で列挙し、各項に確信度 H/M/L、`assertion_type`（persName/date/relation/placeName/affiliation/event/state/bibl/id_assignment/wd_ref/gn_ref/translation/ref_target/other）と `error_category`（FP=作り込み／FN=取りこぼし／substitution=値誤り）を付けること。**「違反ゼロ」の点検項目も分母つきで必ず書く**。冒頭に「点検した assertion の概数・検出数（H/M/L、FP/FN/substitution 別）」を表で。さらに機械可読の指摘一覧を `FINDINGS_<名前>.tsv`（ヘッダなし、列=`batch_id, entry_id, assertion_type, error_category, severity, origin_stage, caught_stage, resolution, description`。`batch_id`=B134-138、`origin_stage`=claude_review（校閲者が作り込んだ・見落とした誤りの場合）または gemini_draft（初版の誤りが校閲後も残っていた場合）、`caught_stage`=verify_content または verify_mech、`resolution`=open）で出す。

---
（以下、役割別の節。自分に割り当てられた節に従う）

## あなたの役割: 内容検証（corpus 逆引き） — 担当 （チャンク指定はプロンプト参照）

担当範囲のすべてのファイルについて、校閲後 XML と corpus 原文を並べて読み、次を点検する:
- (a) 校閲者が付けた全ての `#AIND-D…` 同定が正しいか（相手側原文で裏取り。ナサブ・没年・「الماضي/الآتي」の整合・綴り揺れ・同名異人）。REF は**転送先の原文を必ず読み**、転送先として正しいか確認。
- (b) 校閲者が「本伝なし」として新規 TMP を発行した件（`TMP_NEW_B1xx.tsv`）のうち、corpus に本伝がある／ID-Master に既登録のものがないか。**父・祖父の名＋ニスバで corpus 見出しを逆引き**（変綴り・逆転ナサブ・索引項（ニスバ／ابن-部、D11xxx〜D13xxx 帯）・كنى 部・女性部から探す）。
- (c) Pattern A の欠落・relation 化の残存、relation の向き、subtype の妥当性、#NEEDID 維持の妥当性（登録済み ID の放置がないか）、規則23・26・37 の適用が過不足ないか、チャンクをまたぐ相互参照が双方向に閉合しているか（D08024⇄D08883、D06375⇄D06376、D06304←D06295、D06327→D06323、D02807⇄D03639、D06317⇄D05925）。
- (d) 日付（when-custom と when の整合、精度の一致、notBefore/notAfter、ヒジュラ年の @when 混入、グレゴリオ換算）。**すべての日付を h2g.py で独立に再計算**。
- (e) 訳文（ja/en）の誤り（主語・数字・脱落・人名転写・hedge の脱落・内部ID・生アラビア語・立項連番・推測句の混入）。**ja 訳の語中 بن は「ブン」**。en が英語であること。欠字・途切れ（D06324・D06361「مات .」）を訳で補っていないか。
- (f) 幻番号・統合済み番号・汚染番号・毒 wd・空属性・ID 書式。
- (g) 校閲者メモ（REVIEW_NOTES）と XML の不一致。
- (h) 初版にあって校閲版で消えた情報のうち、消すべきでなかったもの（原文にある師・弟子・役職・出来事）。
- (i) 原文にない属性・地名（ニスバ由来 residence、学派、生年、cert="high" の捏造）が残っていないか。規則22 の 1〜6。
- (j) 連結レコード（校閲者報告上は該当なし）が実際に無いか、担当範囲の原文末尾を点検し、あれば訳文・event への混入を見る。
- (k) 校閲者が出した ISSUES のうち、統一規則・repo 先例・corpus 証拠で解決できるものがないか（解決案を添える）。

担当ファイル数が多いので、ファイルごとに系統的に。校閲者の結論を鵜呑みにせず、根拠（原文）から独立に読み直すこと。分母は `python3 docs/_work/B134-138_incoming/verify/count_assertions.py docs/_work/B134-138_incoming/B134-138 D02206-D02828` のように担当範囲を指定して機械計数し、報告冒頭の表に内訳を載せる。

---

## あなたの役割: 機械検査（スクリプトによる全件検査） — 担当 100件すべて

`docs/_work/B134-138_incoming/verify/` に前バッチの機械検査スクリプト（mech_lib.py・mech_items_a〜e.py・mech_check.py・mech_report.py・count_assertions.py。パス・ID-Master・batch_id・チャンク名・校閲日は**オーケストレーターが B134-138／idmaster_ext_20261026b／2026-10-26 に置換済み**。項目23〜26 と mech_items_h.py は B129-133 で新設した検査＝前バッチ固有のハードコード（D06253・D07310〜12・العيني 等）は本バッチ用に差し替えること）をコピーしてある。日付（2026-10-26）・respStmt 名（claude-b134〜b138-review）・前バッチ固有のハードコード（「اثنان」型 D06253、REF 期待転送先、FORCE_CONCAT、幻番号リスト、毒 wd リスト、汚染番号リスト）を本バッチ用に見直してから実行し、100件すべてに次を機械的に検査する。各項目を「点検N件中違反M件」で報告:
1. well-formed（xml.etree）。
2. REF 方式X の形（type="reference" subtype="LIMBO"・実伝由来要素なし・note 順序 source→translation ja→translation en→reference・target が実在 AIND（corpus_index にある）か #NEEDID・ファイル名 `REF_` 接頭辞と一致）。12件。
3. 原文 `<note type="source" xml:lang="ar">` と corpus_B134-138.json の `text` の一致（改行・空白の正規化後）。不一致はすべて列挙。
4. 日付属性（when-custom ⇔ when の対応、ヒジュラ年値が @when にないか、4桁ゼロ詰め、精度一致、notBefore/notAfter の整合）。h2g.py による再計算で全件検算。
5. persName name_only の世代数（≤3）、full に居住句・職名句がないか。
6. respStmt（初版が orig と同一で残り、校閲 respStmt に persName `claude-b134〜b138-review`（チャンクと一致）・date 2026-10-26、resp=校閲）。
7. ID 書式（`#`・`wd:`・`gn:` 欠落、AIND-D 5桁（英字接尾辞 D00544a は許容）、TMP-P 6桁、他 TMP 5桁、passive/active と xml:id の整合）。
8. 幻 AIND（Individuals にも corpus にもない）。
9. 幻 TMP（ID-Master `idmaster_ext_20261026b.tsv` 未登録の非仮番号。仮番号 `TMP-x-NEW134〜138-nn` は TMP_NEW_B1xx.tsv に登録があること、チャンク番号がファイルの属するチャンクと一致すること）。
10. 毒 wd（Q160851／Q191314／Q35160／Q589／Q3824443／Q327129／Q12247942／Q381208／Q1164991／Q1283／Q3306083、人物位置の Q4120093 等）の属性使用、ID-Master にも repo にもない wd/gn が新規に付いていないか（付いていれば「未確認」の記録が ISSUES にあるか）。
11. 汚染 TMP の person 位置使用（TMP-P-000529／000530／000490／000064／000664／000063／000489／000352／000140／000131／000603／000204／000350／000719／000694／000292 など）。TMP-N の person 位置流用。カテゴリ不一致。
12. 規約A（relation/@n）。
13. affiliation と state の同一 ref 二重符号化。
14. 統制外の type/subtype（repo の `Individuals/**/*.xml` に既存の値と照合）。
15. 仮 TMP のチャンク間重複・ID-Master との近似一致、TMP_NEW ⇔ XML の片側漏れ。TSV が7列か。15c 並行追加（今回はゼロ）。
16. 汎用名 TMP-P の TSV Note に「⚠汎用名」があるか。
17. `<desc>` に xml:lang があるか。`xml:lang="lat"` の残存。en 訳が英語か。ja 訳に「ビン」・ラテン文字・内部ID・立項連番が混入していないか。
18. 規則22 機械検査: アラビア語 placeName のうち原文（source note）に現れないもの（照応・حج 由来を除く）をリストし、cert の付け方と合わせて報告。空 residence イベントの有無。
19. relation 整合: passive/active の少なくとも一方が本項主、self-relation なし、相互 relation の矛盾、desc が相手の名前のみ、possible_identity が本バッチ内では双方向か。
20. 校閲前 orig と比べた変更の概要統計（ファイルごとの要素数の増減）を表で。極端な減少があれば列挙。
21. 規則24 の記録: FIXLOG_B1xx.tsv の書式（9列・固定語彙・batch_id=B134-138）と件数。
22. 「أرخه ابن فهد」の振り分け: source note に「أرخه ابن فهد」「ذكره (التقي) بن فهد」を含む全件について、death の when-custom と Pattern A の persName ref（D09211/D05979/D03985）・cert の対応を表にして報告。
結果は `mech_results.json`、報告は `VERIFY_REPORT_mech.md`、指摘一覧は `FINDINGS_mech.tsv`（いずれも `docs/records/records_B134-138/` に。スクリプトは `verify/` に再実行可能な形で残し、報告に保存場所を記すこと）。さらに `count_assertions.py docs/_work/B134-138_incoming/B134-138` を全件で実行し、assertion 総数と内訳を報告に載せる。

## assertion の数え方の定義（分母の固定、2026-10-06）
| assertion_type | 単位（1件＝） |
|---|---|
| persName | 本項主の `<persName>` 要素1つ |
| id_assignment | 人物参照1つ（relation の active/passive、persName/@ref、event 内 persName/@ref。#NEEDID も1件） |
| relation | `<relation>` 要素1つ |
| date | 日付属性1つ |
| placeName | `<placeName>` 要素1つ |
| affiliation／event／state／bibl | 要素1つ |
| wd_ref／gn_ref | 地名・書名・機関の wd/gn 属性1つ |
| translation | translation note 1つ（ja・en 各1件） |
| ref_target | REF の `<note type="reference">/@target` 1つ |
分母は `count_assertions.py` で機械計数する。
