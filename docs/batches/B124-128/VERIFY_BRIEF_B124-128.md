# 独立検証パス・ブリーフ（B124-128、2026-10-19）

あなたは al-Sakhāwī『al-Ḍawʾ al-Lāmiʿ』の TEI-XML プロソポグラフィDB（AINet-DB）の**校閲結果を検証する独立検証者**です。校閲者（別のエージェント5名、チャンク B124〜B128 各20件）が作った修正版 XML 100件（実項94＋REF化6）に、校閲者自身が作り込んだ誤り・取りこぼしがないかを、原文と突合して洗い出してください。**XML・corpus・ID-Master・Individuals は一切修正しないでください**（読み取りのみ。報告ファイルだけを書く）。git 操作も禁止です。

## 作業環境
- すべて `mcp__remote-devices__device_bash`（Mac 上）で行う。毎回 `cd "$HOME/mnt/AINet-DB-Sakhawi" && ...`。呼び出しごとに新しいシェル。ファイルの読み書きは python3 / cat / sed で（クラウド側の Read/Edit/Write/Bash はこのマシンのファイルに届かない）。
- **検証対象（校閲後 XML）**: `docs/_work/B124-128_incoming/B124-128/` の100件（`REF_` 接頭辞付き6件は転送見出し）。受領チャンクとの対応は `docs/_work/B124-128_incoming/origin_folders.tsv`（ファイル名<TAB>チャンク）。
- **校閲前（Gemini 初版）**: `docs/_work/B124-128_incoming/orig/`（比較用。校閲で消えた情報のうち、消すべきでなかったものがないか）。
- **原文**: `docs/_work/B124-128_incoming/corpus_B124-128.json`（100件の本文、キー `D05412` 形式）。corpus 全体: `docs/_work/B124-128_incoming/vc/corpus_index.json`（AIND-ID → {text, dollars, line…}）。`python3 -c "import json;d=json.load(open('docs/_work/B124-128_incoming/vc/corpus_index.json'));print(d['AIND-D04991']['text'])"` で任意の項を読める。**校閲者が付けた同定（#AIND-Dxxxxx）は、必ずこの辞書で相手側の原文を読んで裏取りすること。**
- 検索ツール（cwd=リポジトリルート）: `python3 docs/_work/B124-128_incoming/vc/hw.py "<語1>" "<語2>"`（corpus 見出し先頭260字の AND 検索）／`vc/idsearch.py "<文字列>" [件数]`（ID-Master のアラビア語・ラテン語・Note 検索）／`vc/idm.py TMP-P-000010`（ID 行表示）／`vc/rgrep.py "<文字列>" [件数]`（repo の Individuals 全文検索。サブフォルダ再帰）／`python3 docs/_work/B124-128_incoming/vc/h2g.py 886-9 874-3-15 850`（ヒジュラ→西暦。**グレゴリオ暦（proleptic）を正とする**。`--selftest` あり）。
- ID-Master: `docs/_work/idmaster_ext_20261019d.tsv`（2026-10-19 に gviz で取得したシート実物 8,386 行。列=[登録者,Category,Arabic,Latin,ID,Note,修正]。B119-123 の102行・名寄せ7行を含む）。新規 TMP は仮番号（`TMP-x-NEW124-nn`〜`NEW128-nn`）のまま XML にある。
- 校閲者の記録: `docs/records/records_B124-128/` の `REVIEW_NOTES_B1xx.md`・`ISSUES_B1xx.md`・`TMP_NEW_B1xx.tsv`・`FIXLOG_B1xx.tsv`（B124〜B128）、precheck: `precheck_B124-128_before.md`、規約全文: `CHUNK_BRIEF_B124-128.md`（**まずこれを読む**。統一規則1〜46・頻出確定ID・汚染番号を含む）。

## 規約の要点（CHUNK_BRIEF が正）
第三者言及は Pattern A（event cultural/mention + persName ref）／relation 向き: 師弟は active=師・passive=学生、親族・社会関係は active=相手・passive=本項主／TMP-P 発行ルールと父は必ず relation（本伝→AIND、祖父名復元→TMP-P、裸名→#NEEDID の father relation を必ず立てる＝規則3 改訂）／@when は西暦（グレゴリオ）のみ・精度は when-custom に合わせる、ヒジュラは when-custom／原文にない属性・地名を補わない（規則22）／規則25 原文どおり読む／規則26 同定は確実な場合のみ（通称・推定では AIND に同定せず TMP、ただし ابن فهد 振り分け規則は例外）／規則27 連結レコード／規則28「رأيته فيمن عرض عليه」「كتب بالشهادة」型は本項主＝行為者／規則29「خلف أخاه/والده」は predecessor／規則30 頻出確定IDは年代確認／規則31 relation desc は相手名のみ／規則37 本項主の見出しナサブで特定できる父祖は AIND で relation／規則38 本伝探索はナサブ1段ずらし・女性部・repo 既存使用まで／relation の @n は規約A（親族には付けない、非親族のみ1起点連番）／初版 respStmt は非改変、校閲 respStmt は `claude-b1xx-review`・2026-10-19／en 訳は英語／転送見出しは REF 方式X／汚染番号 TMP-P-000529・000530・000064・000664 等は別人流用禁止／毒 wd Q160851→Q228986、Q191314→Q233387／wd・gn は記憶から書かない。

## 本バッチの REF（転送先の原文を必ず読み、転送先として正しいか確認）
B124: D05416→**D05725**（D05725 本文「قلت : وهو ابن محمد بن ثامر القرشي الأموي」で裏取り、候補 D05726 は別人）／D05475→D04991。B126: D06147→**D03964**（عبد العزيز … ويلقب فائزا、ブリーフでは未発見）。B127: D06175→D06166（本バッチ B126、الجراعي⇄الجرائحي）／D06189→**D07969**（「محمد أبو سعد … ويلقب فهدا」、ブリーフ候補 D07968 は別人）／D06192→D07885。B125 は REF なし。**転送指示なしの実項**: D06116（D06097 と possible_identity medium）・D06215（له ذكر في أخيه）・D06173（كما ذكر في ابنته）・D06166（أرخهما）。**二重立項**: D06184 فضل الله التاج بن الرملي ⇄ D04803 عبد الوهاب التاج بن الرملي（校閲者は cert high とした＝妥当か、§D127-2）。

## 本バッチ固有の検証点
- **校閲者が付けた AIND 同定（REVIEW_NOTES に全件）を相手側原文で裏取り**。主要なもの: B124: D05433 父 D07433・祖父 D03112／D05435 父 D07494（medium）／D05436 الجلال القمصي D03560／D05468 父 D07962・娘 D13266／D05471 الفخر الدنديلي D04840・姉妹 D13792・الفوي TMP-P-000072（medium）／D05477 兄弟 D01414／D05478 父 D08081（الجزائري⇄الجرائري、medium）。B126: D06146 父 D10662／D06159 叔父 D07238・D05821、المحيوي القرشي→D04141?（§D126-1）／D06164 兄弟 D10264・D02779・D10991／D06172 主人 D08016／D06170 برسباي قرا D02170。B127: D06174 前任 D06358（medium）・後任 D01848／D06186 نوروز D10152（TMP-P-000672 に本伝）／D06197 前任 D02831／D06194 子 D10029／D06173 娘 D13013／D06188 祖父 D08834／D06190 父 D04913／D06206 父 D00634／D06207 師 D00672／D06193 جكم D02428。B128: D06212 父 D02230（medium）・義父 D05546（medium）／D06214 子 D05921／D06215 父 D02957・兄 D02984／D06216 父 D03047（medium）／D06218 母方叔父 D00818・祖父 D02497（medium）／D06225 兄弟・前任 D07908／D06227 師 ابن عياش D03589（medium）／D06228 父 D05451／D06230 子 D08449／D06232 父 D05937・兄弟 D08351（＝ابن عزم 本人？ §D128-5）／D06237 父 D06409。B125: D06122 父 D04893・صاحب الحجاز D07156（medium）／D06127 出所 D05595 التوريزي（النويري⇄التوريزي）・الفقيه السعودي D06787（例外2）／D06132 父 D08085／D06133 父 D10112a・母 D13464・異父弟 D05111・継父 D02560（没年 776→876 に訂正）／D06135 سوار D03198／D06137 تنم D02315（medium）／D06138 主人 D06199・前任 D05410・後任 D10009（medium）／D06139 前任 D08447。**規則23・26（例外2 を含む）・37 に照らして cert の付け方を点検**。
- **ابن عزم の ID**: ブリーフは `#AIND-D12540`（索引）を頻出確定IDとしたが、B128 校閲者は本伝 D08351 を指摘（§D128-5）。D06117「أرخه ابن عزم」と D06232 の扱いの整合を確認し、どちらが正しいかを原文で判定。
- **チャンク間の整合**: D06166（B126）⇄ D06175（B127 REF）⇄ D06165「أرخهما」。D06116（B125）⇄ D06097（既収録）。B124〜B128 で同一人物に別仮番号が出ていないか（TMP_NEW_B124〜128.tsv）。
- **新規 TMP（TMP_NEW_B124〜128.tsv）の本伝・既登録の見落とし**（9バッチ連続で検証パスが最多捕捉）。とくに TMP-P。**見出し語だけでなく本文中「ويعرف بـX」・ニスバ索引（★ID_Missing★ 行を含む）・点の揺れ（ب/د・ش/س・ح/ي・خ/ج・ف/ق・ع/غ）で引き直す**。ラカブ＋ニスバのみの人物はニスバ単独で hw.py。**既登録 TMP-P（Note 空）にも本伝を探す**。**ID-Master の Note を本項主の AIND で grep**。職の TMP-O は語根で Office を grep（規則41）。
- **父 relation（規則3 改訂 (c')）**: 全実項に father relation があるか。識別要素のない「名＋父名＋ニスバ」だけの父に TMP-P を出していないか（→#NEEDID）、逆に珍しい名・ラカブ付きの父を #NEEDID にしていないか。兄弟姉妹 relation は相手側の名指しがあるか、父が #NEEDID の場合のみ cert medium（規則23）。
- **「ممن سمع مني」型と شيخنا 師型**: 向き、場所は原文にあるときのみ、年（D05431 895）。D05420「عرض على العمدة」＝عليّ。D05477「ذكره البقاعي في شيوخه」＝本項主が師。
- **「أرخه／ذكره ابن فهد」振り分け（規則43、cert は event 側）**: D05433・D05467・D05468・D06132・D06133・D06145・D06165/D06166（أرخهما）・D06206・D06211・D06213・D06228。没年と ID・cert の対応を全件点検。
- **第三者言及**: شيخنا في إنبائه（D05444・D05469・D06129・D06186・D06194・D06237）／المقريزي（D06162・D06174・D06184）／العيني（D06143・D06162・D06193・D06220）／ابن اللبودي（D05435）／ابن عزم（D06117）／البقاعي（D05477）／الفاسي（D06190）／الجلال القمصي（D05436、規則44）／الفقيه السعودي（D06127、規則26 例外2）。
- **日付**: 一の位のみの年（D05469「سنة اثنتين」・D06129「آخر سنة ست」・D06174「سنة إحدى」「سنة ثلاث」・D06220「سنة إحدى」）、D05424「تقريبا」、D05444 逆算生年、D05478「بضع وخمسين」、D06191（881/882）、D06200「في حدود الخمسين」、D06190「في عشر الثلاثين ظنا」、D06235（855-12-21 金曜→1452-01-23）、D06228「فقد في البحر」、D06159（899 存命）。**全日付を h2g.py で独立に再計算**。
- **欠字・途切れ（規則45）**: D05448・D05485・D06120・D06124・D06156・D06154・D06157 で名・年・関係を補っていないか、訳で補っていないか。
- **ID-Master 未登録 wd/gn の新規使用**: ISSUES に「未確認」として残っているか。記憶由来の wd/gn が付いていないか。
- **規則22**: placeName／residence の除去しすぎ・残しすぎ。


## 出力と記録（規則24）
指定された報告ファイルに、**誤りと思われるものだけ**を、ファイルID・箇所・根拠（原文引用）・提案修正の4点で列挙し、各項に確信度 H/M/L、`assertion_type`（persName/date/relation/placeName/affiliation/event/state/bibl/id_assignment/wd_ref/gn_ref/translation/ref_target/other）と `error_category`（FP=作り込み／FN=取りこぼし／substitution=値誤り）を付けること。**「違反ゼロ」の点検項目も分母つきで必ず書く**。冒頭に「点検した assertion の概数・検出数（H/M/L、FP/FN/substitution 別）」を表で。さらに機械可読の指摘一覧を `FINDINGS_<名前>.tsv`（ヘッダなし、列=`batch_id, entry_id, assertion_type, error_category, severity, origin_stage, caught_stage, resolution, description`。`batch_id`=B124-128、`origin_stage`=claude_review（校閲者が作り込んだ・見落とした誤りの場合）または gemini_draft（初版の誤りが校閲後も残っていた場合）、`caught_stage`=verify_content または verify_mech、`resolution`=open）で出す。

---
（以下、役割別の節。自分に割り当てられた節に従う）

## あなたの役割: 内容検証（corpus 逆引き） — 担当 （チャンク指定はプロンプト参照）

担当範囲のすべてのファイルについて、校閲後 XML と corpus 原文を並べて読み、次を点検する:
- (a) 校閲者が付けた全ての `#AIND-D…` 同定が正しいか（相手側原文で裏取り。ナサブ・没年・「الماضي/الآتي」の整合・綴り揺れ・同名異人）。REF は**転送先の原文を必ず読み**、転送先として正しいか確認。
- (b) 校閲者が「本伝なし」として新規 TMP を発行した件（`TMP_NEW_B1xx.tsv`）のうち、corpus に本伝がある／ID-Master に既登録のものがないか。**父・祖父の名＋ニスバで corpus 見出しを逆引き**（変綴り・逆転ナサブ・索引項（ニスバ／ابن-部、D11xxx〜D13xxx 帯）・كنى 部・女性部から探す）。
- (c) Pattern A の欠落・relation 化の残存、relation の向き、subtype の妥当性、#NEEDID 維持の妥当性（登録済み ID の放置がないか）、規則23・26・37 の適用が過不足ないか、チャンクをまたぐ相互参照が双方向に閉合しているか（D06165⇄D06166⇄D06175、D06116→D06097）。
- (d) 日付（when-custom と when の整合、精度の一致、notBefore/notAfter、ヒジュラ年の @when 混入、グレゴリオ換算）。**すべての日付を h2g.py で独立に再計算**。
- (e) 訳文（ja/en）の誤り（主語・数字・脱落・人名転写・hedge の脱落・内部ID・生アラビア語・立項連番・推測句の混入）。**ja 訳の語中 بن は「ブン」**。en が英語であること。欠字「...」を訳で補っていないか（D05448・D05485・D06120・D06124・D06156・D06157）。
- (f) 幻番号・統合済み番号・汚染番号・毒 wd・空属性・ID 書式。
- (g) 校閲者メモ（REVIEW_NOTES）と XML の不一致。
- (h) 初版にあって校閲版で消えた情報のうち、消すべきでなかったもの（原文にある師・弟子・役職・出来事）。
- (i) 原文にない属性・地名（ニスバ由来 residence、学派、生年、cert="high" の捏造）が残っていないか。規則22 の 1〜6。
- (j) 連結レコード（校閲者報告上は該当なし）が実際に無いか、担当範囲の原文末尾を点検し、あれば訳文・event への混入を見る。
- (k) 校閲者が出した ISSUES のうち、統一規則・repo 先例・corpus 証拠で解決できるものがないか（解決案を添える）。

担当ファイル数が多いので、ファイルごとに系統的に。校閲者の結論を鵜呑みにせず、根拠（原文）から独立に読み直すこと。分母は `python3 docs/_work/B124-128_incoming/verify/count_assertions.py docs/_work/B124-128_incoming/B124-128 D05412-D06142` のように担当範囲を指定して機械計数し、報告冒頭の表に内訳を載せる。

---

## あなたの役割: 機械検査（スクリプトによる全件検査） — 担当 100件すべて

`docs/_work/B124-128_incoming/verify/` に前バッチの機械検査スクリプト（mech_lib.py・mech_items_a〜e.py・mech_check.py・mech_report.py・count_assertions.py。パス・ID-Master・batch_id・チャンク名は B124-128 用に置換済み）をコピーしてある。日付（2026-10-19）・respStmt 名（claude-b124〜b128-review）・前バッチ固有のハードコード（「اثنان」型 D06026/D06028、FORCE_CONCAT、幻番号リスト、毒 wd リスト、汚染番号リスト）を本バッチ用に見直してから実行し、100件すべてに次を機械的に検査する。各項目を「点検N件中違反M件」で報告:
1. well-formed（xml.etree）。
2. REF 方式X の形（type="reference" subtype="LIMBO"・実伝由来要素なし・note 順序 source→translation ja→translation en→reference・target が実在 AIND（corpus_index にある）か #NEEDID・ファイル名 `REF_` 接頭辞と一致）。6件。
3. 原文 `<note type="source" xml:lang="ar">` と corpus_B124-128.json の `text` の一致（改行・空白の正規化後）。不一致はすべて列挙。
4. 日付属性（when-custom ⇔ when の対応、ヒジュラ年値が @when にないか、4桁ゼロ詰め、精度一致、notBefore/notAfter の整合）。h2g.py による再計算で全件検算。
5. persName name_only の世代数（≤3）、full に居住句・職名句がないか。
6. respStmt（初版が orig と同一で残り、校閲 respStmt に persName `claude-b12x-review`（チャンクと一致）・date 2026-10-19、resp=校閲）。
7. ID 書式（`#`・`wd:`・`gn:` 欠落、AIND-D 5桁（英字接尾辞 D00544a は許容）、TMP-P 6桁、他 TMP 5桁、passive/active と xml:id の整合）。
8. 幻 AIND（Individuals にも corpus にもない）。
9. 幻 TMP（ID-Master `idmaster_ext_20261019d.tsv` 未登録の非仮番号。仮番号 `TMP-x-NEW12x-nn` は TMP_NEW_B1xx.tsv に登録があること、チャンク番号がファイルの属するチャンクと一致すること）。
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
21. 規則24 の記録: FIXLOG_B1xx.tsv の書式（9列・固定語彙・batch_id=B124-128）と件数。
22. 「أرخه ابن فهد」の振り分け: source note に「أرخه ابن فهد」「ذكره (التقي) بن فهد」を含む全件について、death の when-custom と Pattern A の persName ref（D09211/D05979/D03985）・cert の対応を表にして報告。
結果は `mech_results.json`、報告は `VERIFY_REPORT_mech.md`、指摘一覧は `FINDINGS_mech.tsv`（いずれも `docs/records/records_B124-128/` に。スクリプトは `verify/` に再実行可能な形で残し、報告に保存場所を記すこと）。さらに `count_assertions.py docs/_work/B124-128_incoming/B124-128` を全件で実行し、assertion 総数と内訳を報告に載せる。

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
