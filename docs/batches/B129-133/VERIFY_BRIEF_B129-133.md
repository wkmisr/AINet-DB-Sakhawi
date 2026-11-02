# 独立検証パス・ブリーフ（B129-133、2026-10-25）

あなたは al-Sakhāwī『al-Ḍawʾ al-Lāmiʿ』の TEI-XML プロソポグラフィDB（AINet-DB）の**校閲結果を検証する独立検証者**です。校閲者（別のエージェント5名、チャンク B129〜B133 各20件）が作った修正版 XML 100件（実項80＋REF化20）に、校閲者自身が作り込んだ誤り・取りこぼしがないかを、原文と突合して洗い出してください。**XML・corpus・ID-Master・Individuals は一切修正しないでください**（読み取りのみ。報告ファイルだけを書く）。git 操作も禁止です。

## 作業環境
- すべて `mcp__remote-devices__device_bash`（Mac 上）で行う。毎回 `cd "$HOME/mnt/AINet-DB-Sakhawi" && ...`。呼び出しごとに新しいシェル。ファイルの読み書きは python3 / cat / sed で（クラウド側の Read/Edit/Write/Bash はこのマシンのファイルに届かない）。
- **検証対象（校閲後 XML）**: `docs/_work/B129-133_incoming/B129-133/` の100件（`REF_` 接頭辞付き20件は転送見出し）。受領チャンクとの対応は `docs/_work/B129-133_incoming/origin_folders.tsv`（ファイル名<TAB>チャンク）。
- **校閲前（Gemini 初版）**: `docs/_work/B129-133_incoming/orig/`（比較用。校閲で消えた情報のうち、消すべきでなかったものがないか）。
- **原文**: `docs/_work/B129-133_incoming/corpus_B129-133.json`（100件の本文、キー `D06244` 形式）。corpus 全体: `docs/_work/B129-133_incoming/vc/corpus_index.json`（AIND-ID → {text, dollars, line…}）。`python3 -c "import json;d=json.load(open('docs/_work/B129-133_incoming/vc/corpus_index.json'));print(d['AIND-D06270']['text'])"` で任意の項を読める。**校閲者が付けた同定（#AIND-Dxxxxx）は、必ずこの辞書で相手側の原文を読んで裏取りすること。**
- 検索ツール（cwd=リポジトリルート）: `python3 docs/_work/B129-133_incoming/vc/hw.py "<語1>" "<語2>"`（corpus 見出し先頭260字の AND 検索）／`vc/idsearch.py "<文字列>" [件数]`（ID-Master のアラビア語・ラテン語・Note 検索）／`vc/idm.py TMP-P-000010`（ID 行表示）／`vc/rgrep.py "<文字列>" [件数]`（repo の Individuals 全文検索。サブフォルダ再帰）／`python3 docs/_work/B129-133_incoming/vc/h2g.py 886-9 874-3-15 850`（ヒジュラ→西暦。**グレゴリオ暦（proleptic）を正とする**。`--selftest` あり）。
- ID-Master: `docs/_work/idmaster_ext_20261021.tsv`（2026-10-21 に gviz 照合済みのシート実物 8,438 行。列=[登録者,Category,Arabic,Latin,ID,Note,修正]）。新規 TMP は仮番号（`TMP-x-NEW129-nn`〜`NEW133-nn`）のまま XML にある。
- 校閲者の記録: `docs/records/records_B129-133/` の `REVIEW_NOTES_B1xx.md`・`ISSUES_B1xx.md`・`TMP_NEW_B1xx.tsv`・`FIXLOG_B1xx.tsv`（B129〜B133）、precheck: `precheck_B129-133_before.md`、規約全文: `CHUNK_BRIEF_B129-133.md`（**まずこれを読む**。統一規則1〜48・頻出確定ID・汚染番号を含む）。

## 規約の要点（CHUNK_BRIEF が正）
第三者言及は Pattern A（event cultural/mention + persName ref）／relation 向き: 師弟は active=師・passive=学生、親族・社会関係は active=相手・passive=本項主／TMP-P 発行ルールと父は必ず relation（本伝→AIND、祖父名復元→TMP-P、裸名→#NEEDID の father relation を必ず立てる＝規則3 改訂）／@when は西暦（グレゴリオ）のみ・精度は when-custom に合わせる、ヒジュラは when-custom／原文にない属性・地名を補わない（規則22）／規則25 原文どおり読む／規則26 同定は確実な場合のみ（通称・推定では AIND に同定せず TMP、ただし ابن فهد 振り分け規則は例外）／規則27 連結レコード／規則28「رأيته فيمن عرض عليه」「كتب بالشهادة」型は本項主＝行為者／規則29「خلف أخاه/والده」は predecessor／規則30 頻出確定IDは年代確認／規則31 relation desc は相手名のみ／規則37 本項主の見出しナサブで特定できる父祖は AIND で relation／規則38 本伝探索はナサブ1段ずらし・女性部・repo 既存使用まで／relation の @n は規約A（親族には付けない、非親族のみ1起点連番）／初版 respStmt は非改変、校閲 respStmt は `claude-b1xx-review`・2026-10-25／en 訳は英語／転送見出しは REF 方式X／汚染番号 TMP-P-000529・000530・000064・000664 等は別人流用禁止／毒 wd Q160851→Q228986、Q191314→Q233387／wd・gn は記憶から書かない。

## 本バッチの REF（転送先の原文を必ず読み、転送先として正しいか確認）
B129: D06249→D06231（قاسم بن علي المعمار）／D06259→D06256（الأبو بكري البهلوان）／D06267→D06272（المحمدي＝قانباي الصغير）／D06271→D06270（「وهو الذي قبله」、D06270 本文のイブン・ハジャル引用で閉合と校閲者）。B130: D06295→**D06304**（「قانم نعبة」⇄ 見出し「نعجة」の点の揺れ、§D130-1）／D06297→D06303（التاجر）／D07229→**D07165**（ابن السراج、ID-Master TMP-P-001485 の Note 経由）。B131: D07232→D07167／D07233→D10930（كنى 部）／D07240→D07242／D07241→D07243／D07259→D07225／D07270→D07221。B132: **D07276→D07236**（ブリーフは別人の可能性を指摘したが校閲者は一致と判断、888年の証人情報は editorial note に保持＝§D132-1）／D07277→D07256。B133: D08001→D07988／D08011→D07984／D08014→D07985／D08018→D08008／D08020→D07995。
**実項として扱われたもの**: D06253（「قاسم الحنفي اثنان」型、参照先 D06236・D06251）／D06260（D06256 と別人と判断＝possible_identity なし。妥当か）／D07280 ⇄ D07271（possible_identity low、ينظر）／**D07293 ⇄ D09267（二重立項型 possible_identity medium、§D132-3）**／D07310〜D07312（父 D02423、兄 D07309）／D08010（ويحرر اسمه）／D08017（أظنه ابن فكيك、D08256 と同一人候補 §D133-5）。

## 本バッチ固有の検証点
- **校閲者が付けた AIND 同定を相手側原文で裏取り**（全件は REVIEW_NOTES_B129〜B133 にある。主要なもの）: B129: D06244 أبو حامد بن الضياء D06912（teacher cert medium）／D06246 ابن الهمام D07903・بيت ابن أصيل D07945／D06254 後任 D07242／D06255 زيرك D03047（patron active=本項主）・يشبك D10359（medium）／D06274 يونس العلائي D10602。B130: D06287 سيباي D03248／D06293 إينال الأشقر D02114／D06289 妻 D13195・الأتابك D01869（medium）／D06286 السيفي الحنفي D08993（例外2 medium、§D130-7）／D07230 叔父 D11058・弟子 الدوالي D10050／D07228 أبو البقاء بن الضياء D06911（medium）。B131: D07234 父 D10818・師 فاطمة D13487・子 D03515・娘 D13609／D07249 父 D10851・子 D10824／D07254 叔父 D01521／D07255 父 D10856／D07265 甥 D07700／D07266 الفوي D05452（medium）／D07269 父 D10895／D07235 父 D10825（medium、§D131-2）。B132: D07273 師 الأياسي D09562・後任 D09009（medium）／D07292 弟子 راجح D02984／D07294 母 D13540・母方祖父 D04246・جهة شيخنا D12898／D07296 母 D13532／D07300 ابن الهمام D07903／D07297 父 TMP-P-000766。B133: D07302 父 D02406・母 D13259・母方祖父 D06160／D07306 ancestor D05506・子 D10166／D07307 D09466・D04932・بشر TMP-P-001356・رابعة TMP-P-000221／D07308 بديد D02141（patron）／D08010 兄弟 D04332／D08021 主人 D08893・師 D13827。**規則23・26（例外2 を含む）・37 に照らして cert の付け方を点検**。
- **العيني の参照形（オーケストレーター決定）**: B59-63 裁定 §D-12 により **`#AIND-D09832`＋`corresp="wd:Q257745"`** が正（ブリーフの頻出確定ID表の `wd:Q257745` は誤記）。本バッチ（D06269・D06276・D06280・D07274 ほか）で形が割れている＝集約で統一する。検証者は全件を列挙する。
- **頻出確定ID表と既登録の食い違い**: البيبرسية（D07294 は ID-Master 既登録 TMP-L-00352、ブリーフ表は wd:Q6400398）——どちらが正か ID-Master・repo 実勢で判定。
- **チャンク間の整合**: マムルーク単名項（B129・B130）の父 #NEEDID・主人 patron・職（state office、TMP-O-00107 の範囲）の統一。ابن الهمام（B129 D06246・B132 D07300）、فاطمة ابنة أبي اليمن（B131 D07234・D07255）、الفوي（B131）、شيخنا الأبي（B133）。同一人物に別仮番号が出ていないか（TMP_NEW_B129〜133.tsv）。D07294 と D07296 の母方親族（D13540）。
- **新規 TMP（TMP_NEW_B129〜133.tsv、計37件）の本伝・既登録の見落とし**（10バッチ連続で検証パスが最多捕捉）。とくに TMP-P（شاذبك الصارمي・جانم・السجزي・ابن جعمان 父子・التقي أبو بكر بن جمعة・الدماميني・ابن شقير・عبد القادر القابسي・سليمان بن سيد البناء・الحبال الصائغ・أحمد بن بيلبك・تغري برمش・جاجق・الشريف الفخري・جسار الحميضي・الجلال جعفر الجرجاني・عمر بن إبراهيم البعلي・أبو الطاهر الدريبي・العلاء علي المنفلوطي）。**名の1語＋ニスバ・本文中「ويعرف بـX」・ニスバ索引（★ID_Missing★ 行を含む）・点の揺れで引き直す**。既登録 TMP-P（Note 空）にも本伝を探す。職の TMP-O は語根で Office を grep（規則41）。
- **父 relation（規則3、単名項も #NEEDID）**: 全実項に father relation があるか。D07310〜12 は D02423。
- **「ممن سمع مني」型と شيخنا 師型**: 向き、場所は原文にあるときのみ、年（D08005 895）。D07300「سمع بقراءتي على شيخه」（サハーウィーは読み手で師ではない）。D06244・D07307「أجاز في استدعاء」（本項主→イブン・ハジャルの子らへ）。
- **「أرخه ابن فهد」振り分け（規則43、cert は event 側）**: D07235・D07269・D07289・D07293・D07304・D07308、D07228「صاحبنا ابن فهد」、D07280「لقيه ابن فهد」。没年と ID・cert の対応を全件点検。**ابن عزم は本伝 `#AIND-D08351`**（D07261・D07281）。
- **日付**: D07228「سنة ست」（806 cert low と校閲者）／D07284 803／D07246 生「قبل سنة خمسين وسبعمائة」・807 消息不明／D06260 訃報（notAfter）／D06269（808）・D06276（807）の一の位と曜日／D07302 生839頃・没88X／D07310〜12（853 の曜日）／D07292 逆算生年／D07274・D07297（校閲者が年を訂正）。**全日付を h2g.py で独立に再計算**。
- **欠字・途切れ（規則45）**: D07302「سنة ... وثمانين」・D06298「في شوال سنة .」で年を補っていないか。
- **規則47・48**: 内定・派遣（D06298）を state にしていないか、マムルーク位階・職の TMP-O が既登録を使っているか、他人の職（D07291 兄の خازندار、D06298 兄の دوادار）を state にしていないか。
- **ISSUES（B129 3／B130 7／B131 5／B132 7／B133 7）のうち、統一規則・repo 先例・corpus 証拠で解決できるもの**に解決案を添える。とくに §D133-4（D08021 の Hanbali affiliation を除去した判断。原文に学派明記なしだが「أوقاف الحنابلة」「أم هانئ」等の文脈）。
- **ID-Master 未登録 wd/gn の新規使用**: ISSUES に「未確認」として残っているか（§D129-1 ابن الملقن wd:Q6534585 等）。
- **規則22**: placeName／residence の除去しすぎ・残しすぎ。


## 出力と記録（規則24）
指定された報告ファイルに、**誤りと思われるものだけ**を、ファイルID・箇所・根拠（原文引用）・提案修正の4点で列挙し、各項に確信度 H/M/L、`assertion_type`（persName/date/relation/placeName/affiliation/event/state/bibl/id_assignment/wd_ref/gn_ref/translation/ref_target/other）と `error_category`（FP=作り込み／FN=取りこぼし／substitution=値誤り）を付けること。**「違反ゼロ」の点検項目も分母つきで必ず書く**。冒頭に「点検した assertion の概数・検出数（H/M/L、FP/FN/substitution 別）」を表で。さらに機械可読の指摘一覧を `FINDINGS_<名前>.tsv`（ヘッダなし、列=`batch_id, entry_id, assertion_type, error_category, severity, origin_stage, caught_stage, resolution, description`。`batch_id`=B129-133、`origin_stage`=claude_review（校閲者が作り込んだ・見落とした誤りの場合）または gemini_draft（初版の誤りが校閲後も残っていた場合）、`caught_stage`=verify_content または verify_mech、`resolution`=open）で出す。

---
（以下、役割別の節。自分に割り当てられた節に従う）

## あなたの役割: 内容検証（corpus 逆引き） — 担当 （チャンク指定はプロンプト参照）

担当範囲のすべてのファイルについて、校閲後 XML と corpus 原文を並べて読み、次を点検する:
- (a) 校閲者が付けた全ての `#AIND-D…` 同定が正しいか（相手側原文で裏取り。ナサブ・没年・「الماضي/الآتي」の整合・綴り揺れ・同名異人）。REF は**転送先の原文を必ず読み**、転送先として正しいか確認。
- (b) 校閲者が「本伝なし」として新規 TMP を発行した件（`TMP_NEW_B1xx.tsv`）のうち、corpus に本伝がある／ID-Master に既登録のものがないか。**父・祖父の名＋ニスバで corpus 見出しを逆引き**（変綴り・逆転ナサブ・索引項（ニスバ／ابن-部、D11xxx〜D13xxx 帯）・كنى 部・女性部から探す）。
- (c) Pattern A の欠落・relation 化の残存、relation の向き、subtype の妥当性、#NEEDID 維持の妥当性（登録済み ID の放置がないか）、規則23・26・37 の適用が過不足ないか、チャンクをまたぐ相互参照が双方向に閉合しているか（D06249→D06231、D06271→D06270、D07310〜12→D07309、D07280⇄D07271、D07293⇄D09267）。
- (d) 日付（when-custom と when の整合、精度の一致、notBefore/notAfter、ヒジュラ年の @when 混入、グレゴリオ換算）。**すべての日付を h2g.py で独立に再計算**。
- (e) 訳文（ja/en）の誤り（主語・数字・脱落・人名転写・hedge の脱落・内部ID・生アラビア語・立項連番・推測句の混入）。**ja 訳の語中 بن は「ブン」**。en が英語であること。欠字「...」を訳で補っていないか（D07302・D06298）。
- (f) 幻番号・統合済み番号・汚染番号・毒 wd・空属性・ID 書式。
- (g) 校閲者メモ（REVIEW_NOTES）と XML の不一致。
- (h) 初版にあって校閲版で消えた情報のうち、消すべきでなかったもの（原文にある師・弟子・役職・出来事）。
- (i) 原文にない属性・地名（ニスバ由来 residence、学派、生年、cert="high" の捏造）が残っていないか。規則22 の 1〜6。
- (j) 連結レコード（校閲者報告上は該当なし）が実際に無いか、担当範囲の原文末尾を点検し、あれば訳文・event への混入を見る。
- (k) 校閲者が出した ISSUES のうち、統一規則・repo 先例・corpus 証拠で解決できるものがないか（解決案を添える）。

担当ファイル数が多いので、ファイルごとに系統的に。校閲者の結論を鵜呑みにせず、根拠（原文）から独立に読み直すこと。分母は `python3 docs/_work/B129-133_incoming/verify/count_assertions.py docs/_work/B129-133_incoming/B129-133 D06244-D07230` のように担当範囲を指定して機械計数し、報告冒頭の表に内訳を載せる。

---

## あなたの役割: 機械検査（スクリプトによる全件検査） — 担当 100件すべて

`docs/_work/B129-133_incoming/verify/` に前バッチの機械検査スクリプト（mech_lib.py・mech_items_a〜e.py・mech_check.py・mech_report.py・count_assertions.py。パス・ID-Master・batch_id・チャンク名は**未置換（B124-128 のまま）なので、まず mech_lib.py ほか全スクリプトの B124-128／idmaster_ext_20261019d／20261019c を B129-133／idmaster_ext_20261021 に置換すること**）をコピーしてある。日付（2026-10-25）・respStmt 名（claude-b129〜b133-review）・前バッチ固有のハードコード（「اثنان」型 D06026/D06028、FORCE_CONCAT、幻番号リスト、毒 wd リスト、汚染番号リスト）を本バッチ用に見直してから実行し、100件すべてに次を機械的に検査する。各項目を「点検N件中違反M件」で報告:
1. well-formed（xml.etree）。
2. REF 方式X の形（type="reference" subtype="LIMBO"・実伝由来要素なし・note 順序 source→translation ja→translation en→reference・target が実在 AIND（corpus_index にある）か #NEEDID・ファイル名 `REF_` 接頭辞と一致）。20件。
3. 原文 `<note type="source" xml:lang="ar">` と corpus_B129-133.json の `text` の一致（改行・空白の正規化後）。不一致はすべて列挙。
4. 日付属性（when-custom ⇔ when の対応、ヒジュラ年値が @when にないか、4桁ゼロ詰め、精度一致、notBefore/notAfter の整合）。h2g.py による再計算で全件検算。
5. persName name_only の世代数（≤3）、full に居住句・職名句がないか。
6. respStmt（初版が orig と同一で残り、校閲 respStmt に persName `claude-b129〜b133-review`（チャンクと一致）・date 2026-10-25、resp=校閲）。
7. ID 書式（`#`・`wd:`・`gn:` 欠落、AIND-D 5桁（英字接尾辞 D00544a は許容）、TMP-P 6桁、他 TMP 5桁、passive/active と xml:id の整合）。
8. 幻 AIND（Individuals にも corpus にもない）。
9. 幻 TMP（ID-Master `idmaster_ext_20261021.tsv` 未登録の非仮番号。仮番号 `TMP-x-NEW129〜133-nn` は TMP_NEW_B1xx.tsv に登録があること、チャンク番号がファイルの属するチャンクと一致すること）。
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
21. 規則24 の記録: FIXLOG_B1xx.tsv の書式（9列・固定語彙・batch_id=B129-133）と件数。
22. 「أرخه ابن فهد」の振り分け: source note に「أرخه ابن فهد」「ذكره (التقي) بن فهد」を含む全件について、death の when-custom と Pattern A の persName ref（D09211/D05979/D03985）・cert の対応を表にして報告。
結果は `mech_results.json`、報告は `VERIFY_REPORT_mech.md`、指摘一覧は `FINDINGS_mech.tsv`（いずれも `docs/records/records_B129-133/` に。スクリプトは `verify/` に再実行可能な形で残し、報告に保存場所を記すこと）。さらに `count_assertions.py docs/_work/B129-133_incoming/B129-133` を全件で実行し、assertion 総数と内訳を報告に載せる。

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
