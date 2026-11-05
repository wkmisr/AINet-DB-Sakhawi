# 独立検証パス・ブリーフ（B154-158、2026-11-05）

あなたは al-Sakhāwī『al-Ḍawʾ al-Lāmiʿ』の TEI-XML プロソポグラフィDB（AINet-DB）の**校閲結果を検証する独立検証者**です。校閲者（別のエージェント5名、チャンク B154〜B158 各20件）が作った修正版 XML 100件（実項92＋REF化8）に、校閲者自身が作り込んだ誤り・取りこぼしがないかを、原文と突合して洗い出してください。**XML・corpus・ID-Master・Individuals は一切修正しないでください**（読み取りのみ。報告ファイルだけを書く）。git 操作も禁止です。

## 作業環境（今回から変更）
- **作業場所はクラウドの clone `/home/claude/ainet-db-sakhawi`**。`Bash`・`Read`・`Edit`・`Write` を直接使う（Mac の device_bash は使わない）。コマンドは `cd /home/claude/ainet-db-sakhawi && ...` で始める。**git 操作・ファイル削除は禁止**。**XML は編集しない（読み取り専用）**。書くのは自分の報告ファイルだけ。
- **検証対象（校閲後 XML）**: `docs/_work/B154-158_incoming/B154-158/` の100件（フラット配置。`REF_` 接頭辞付き8件は転送見出し）。チャンクとの対応は `docs/_work/B154-158_incoming/origin_folders_final.tsv`（現在のファイル名<TAB>チャンク）。
- **校閲前（Gemini 初版）**: `docs/_work/B154-158_incoming/orig/`（100件、元のファイル名）。
- **原文**: `docs/_work/B154-158_incoming/corpus_B154-158.json`（キー `D02848` 形式）。corpus 全体: `docs/_work/B154-158_incoming/vc/corpus_index.json`。任意の項: `python3 -c "import json;d=json.load(open('docs/_work/B154-158_incoming/vc/corpus_index.json'));print(d['AIND-D08128']['text'])"`。
- 検索ツール: `python3 docs/_work/B154-158_incoming/vc/hw.py "<語1>" "<語2>"`／`vc/hwm.py`／`vc/idsearch.py "<文字列>" [件数]`／`vc/idm.py TMP-P-000010`／`vc/rgrep.py "<文字列>" [件数]`／日付 `vc/h2g.py`。
- ID-Master: `docs/_work/idmaster_ext_20261105.tsv`（2026-11-05 取得、8,670 行）。新規 TMP は仮番号（`TMP-x-NEW154-nn`〜`NEW158-nn`）のまま XML にある。典拠台帳: `python3 docs/authority/lookup.py Q…`。
- 校閲者の記録: `docs/batches/B154-158/` の `REVIEW_NOTES_B15x.md`・`ISSUES_B15x.md`・`TMP_NEW_B15x.tsv`・`FIXLOG_B15x.tsv`（B154〜B158）、precheck `precheck_B154-158_before.md`、規約全文 `CHUNK_BRIEF_B154-158.md`（**まずこれを読む**。統一規則1〜60）。

## 規約の要点（CHUNK_BRIEF が正）
第三者言及は Pattern A（event cultural/mention + persName ref）／relation 向き: 師弟は active=師・passive=学生、親族・社会関係は active=相手・passive=本項主／TMP-P 発行ルールと父は必ず relation（本伝→AIND、祖父名復元→TMP-P、裸名→#NEEDID の father relation を必ず立てる＝規則3 改訂）／@when は西暦（グレゴリオ）のみ・精度は when-custom に合わせる、ヒジュラは when-custom／原文にない属性・地名を補わない（規則22）／規則25 原文どおり読む／規則26 同定は確実な場合のみ（通称・推定では AIND に同定せず TMP、ただし ابن فهد 振り分け規則は例外）／規則27 連結レコード／規則28「رأيته فيمن عرض عليه」「كتب بالشهادة」型は本項主＝行為者／規則29「خلف أخاه/والده」は predecessor／規則30 頻出確定IDは年代確認／規則31 relation desc は相手名のみ／規則37 本項主の見出しナサブで特定できる父祖は AIND で relation／規則38 本伝探索はナサブ1段ずらし・女性部・repo 既存使用まで／relation の @n は規約A（親族には付けない、非親族のみ1起点連番）／初版 respStmt は非改変、校閲 respStmt は `claude-b15x-review`・2026-11-05／en 訳は英語／転送見出しは REF 方式X／汚染番号 TMP-P-000529・000530・000064・000664 等は別人流用禁止／毒 wd Q160851→Q228986、Q191314→Q233387／wd・gn は記憶から書かない。

## 本バッチの REF（転送先の原文を必ず読み、転送先として正しいか確認）
B155: D03124→D09883（「وسيأتي في الميم」、本文に没年あり）。B156: D03161→D03156／D08186→D08576・D08190→D08576（同一人物への転送見出しが複数。校閲者は D08592 も同じ転送先と報告）／D08193→D08591／D08194→D08175。B157: D08214→D08007／D10054→D10052。
**実項として扱われたもの**: D02875「في أثناء قاسم بن أحمد …」（「له ذكر في」型の実項＋D06205 との friend relation、§D154-5）／D02891・D08196（名だけ）／D02897（D02905 と possible_identity medium、§D155-1）／D08196⇄D11028（possible_identity）／D10046⇄D10091（possible_identity medium、チャンク B157⇄B158 をまたぐ）。

## 本バッチ固有の検証点
- **校閲者が付けた AIND 同定を相手側原文で裏取り**（全件は REVIEW_NOTES_B154〜B158）。とくに cert medium の同定、名寄せ提案（ISSUES）、オーケストレーターのブリーフにない新しい同定（例: D02848 父 D07721、D02853 البلالي D08056、D02856 父 D09945、D02880 母 D12908、D02889 父 D10619、D03102 父 D04615・子 D03637、D03105 母 D13881・兄弟 D10977、D03128 主人 D03090、D03137 兄弟 D03574・D00505、D03159 師 D04793・D01349・叔父 D07457、D03164 父 D06106、D03173 甥 D02984・兄弟 D02957、D03175 子 D03045、D08184、D08208・D10074 父 D05661、D08210 السنباطي D09191、D10044 兄 D02967、D10045 父 D01408・ابن عبد السلام D07655、D10055 従兄弟 D10521、D10057 المحب بن ظهيرة D01373、D10058 父 D02610、D10060 ابن البقري D03500、D10063 前任 D08839、D10070 父 D04576、D10080 子 D10886、D10081 زروق D00517、D10082 父 D07186・子 D05664、D10087 父 D08658・叔父 D04340、D10092 D00602・D10050・D09424）。
- **新規 TMP（TMP_NEW_B154〜158.tsv、計55件）の本伝・既登録の見落とし**（15バッチ連続で検証パスの最多捕捉）。とくに父の TMP-P（B156 の6件、B157 の7件、B158 の6件）。D10046 の父 TMP（NEW157-05）と D10091 側の父の重複。
- **父 relation（規則3）**: 全実項に father relation があるか。汚染番号 TMP-P-000530・000529・000063・000064・000204 が残っていないか。
- **「ممن سمع مني」型**（D03105・D03160・D08200・D08218・D08220・D10056）、D02872「يحضر عندي」、D02880「قرأت عليه」（サハーウィーが学生）、D03173「أخذه عني」、D08187「تردد إلي」、D08210「سمع معي」、D10070「سمع معنا」の向きと relation の要否（規則55・60(g)）。
- **「أرخه ابن فهد」振り分け（規則43・58・60(a)、cert は event 側）**: D03111・D08208（أرخهما）・D10058・D10067・D10074、D03156「التقي بن فهد في معجمه」、D10062「أخذ عنه ابن فهد」。
- **日付**: 一の位だけの年（D02863・D02892・D02894・D10059・D10077・D10086）、D10074（校閲者が 874 に訂正）、D03175、D10055、年跨ぎ（D03119・D03128）、D02880・D08187・D08210 の「تقريبا／ظنا」、D10046（floruit）。**全日付を h2g.py で独立に再計算**。
- **規則22**（placeName の除去しすぎ・残しすぎ）、D03123 の没地（ジッダ／マッカ、§D155-4）、D03131「زيارة النبي」。
- **他人の職を state にしていないか**（D03170・D10045・D10063・D10076（§D158 の甥の職の読み）・D10082・D10087）。
- **規則31（desc）と規則54（初版 respStmt 非改変）**を全件で。
- **ISSUES（B154 9／B155 10／B156 15／B157 11／B158 11）のうち、統一規則・repo 先例・corpus 証拠で解決できるもの**に解決案を添える。
- **ID-Master 未登録 wd/gn の新規使用**がないか。

## 出力と記録（規則24）
指定された報告ファイルに、**誤りと思われるものだけ**を、ファイルID・箇所・根拠（原文引用）・提案修正の4点で列挙し、各項に確信度 H/M/L、`assertion_type`（persName/date/relation/placeName/affiliation/event/state/bibl/id_assignment/wd_ref/gn_ref/translation/ref_target/other）と `error_category`（FP=作り込み／FN=取りこぼし／substitution=値誤り）を付けること。**「違反ゼロ」の点検項目も分母つきで必ず書く**。冒頭に「点検した assertion の概数・検出数（H/M/L、FP/FN/substitution 別）」を表で。さらに機械可読の指摘一覧を `FINDINGS_<名前>.tsv`（ヘッダなし、列=`batch_id, entry_id, assertion_type, error_category, severity, origin_stage, caught_stage, resolution, description`。`batch_id`=B154-158、`origin_stage`=claude_review（校閲者が作り込んだ・見落とした誤りの場合）または gemini_draft（初版の誤りが校閲後も残っていた場合）、`caught_stage`=verify_content または verify_mech、`resolution`=open）で出す。

---
（以下、役割別の節。自分に割り当てられた節に従う）

## あなたの役割: 内容検証（corpus 逆引き） — 担当 （チャンク指定はプロンプト参照）

担当範囲のすべてのファイルについて、校閲後 XML と corpus 原文を並べて読み、次を点検する:
- (a) 校閲者が付けた全ての `#AIND-D…` 同定が正しいか（相手側原文で裏取り。ナサブ・没年・「الماضي/الآتي」の整合・綴り揺れ・同名異人）。REF は**転送先の原文を必ず読み**、転送先として正しいか確認。
- (b) 校閲者が「本伝なし」として新規 TMP を発行した件（`TMP_NEW_B15x.tsv`）のうち、corpus に本伝がある／ID-Master に既登録のものがないか。**父・祖父の名＋ニスバで corpus 見出しを逆引き**（変綴り・逆転ナサブ・索引項（ニスバ／ابن-部、D11xxx〜D13xxx 帯）・كنى 部・女性部から探す）。
- (c) Pattern A の欠落・relation 化の残存、relation の向き、subtype の妥当性、#NEEDID 維持の妥当性（登録済み ID の放置がないか）、規則23・26・37 の適用が過不足ないか、チャンクをまたぐ相互参照が双方向に閉合しているか（D08168⇄D08169 兄弟、D10020 は D10019 の兄弟ではなく المؤيد أحمد D00563 の兄弟（D10019 の母方の叔父）、D08094⇄D08601、D10013⇄D10022、D08127→D08128／D08129）。
- (d) 日付（when-custom と when の整合、精度の一致、notBefore/notAfter、ヒジュラ年の @when 混入、グレゴリオ換算）。**すべての日付を h2g.py で独立に再計算**。
- (e) 訳文（ja/en）の誤り（主語・数字・脱落・人名転写・hedge の脱落・内部ID・生アラビア語・立項連番・推測句の混入）。**ja 訳の語中 بن は「ブン」**。en が英語であること。欠字・途切れ（D08181「مات .」・D10038「مات في ...」・D10039「وكان ... مات ...」）を訳で補っていないか。
- (f) 幻番号・統合済み番号・汚染番号・毒 wd・空属性・ID 書式。
- (g) 校閲者メモ（REVIEW_NOTES）と XML の不一致。
- (h) 初版にあって校閲版で消えた情報のうち、消すべきでなかったもの（原文にある師・弟子・役職・出来事）。
- (i) 原文にない属性・地名（ニスバ由来 residence、学派、生年、cert="high" の捏造）が残っていないか。規則22 の 1〜6。
- (j) 連結レコード（校閲者報告上は該当なし）が実際に無いか、担当範囲の原文末尾を点検し、あれば訳文・event への混入を見る。
- (k) 校閲者が出した ISSUES のうち、統一規則・repo 先例・corpus 証拠で解決できるものがないか（解決案を添える）。

担当ファイル数が多いので、ファイルごとに系統的に。校閲者の結論を鵜呑みにせず、根拠（原文）から独立に読み直すこと。分母は `python3 docs/_work/B154-158_incoming/verify/count_assertions.py docs/_work/B154-158_incoming/B154-158 D02848-D08196` のように担当範囲を指定して機械計数し、報告冒頭の表に内訳を載せる。

---

## あなたの役割: 機械検査（スクリプトによる全件検査） — 担当 100件すべて

`docs/_work/B154-158_incoming/verify/` に前バッチの機械検査スクリプト（mech_lib.py・mech_items_a〜e.py・mech_check.py・mech_report.py・count_assertions.py。パス・ID-Master・batch_id・チャンク名・校閲日は**オーケストレーターが（mech_lib.py の CHUNKS も B154〜B158 に） B154-158／idmaster_ext_20261105 にパス置換済み（日付・respStmt 名・固有ハードコードは未置換）**。項目23〜26 と mech_items_h.py は B129-133 で新設した検査＝前バッチ（B144-148）以前の固有ハードコード（mech_items_a の EXPREF・ORTHO_DEF・REALS、mech_items_d の SM_LIST・DIRCHK・19d・D02805、mech_items_i の DEXP ほか、mech_check の POISON 追記・汚染表、mech_items_g 11b）は本バッチ用に差し替えること。本バッチ用の個別点検は mech_items_l.py を新設してよい（mech_items_k.py は B144-148 固有。汎用部だけ残す））をコピーしてある。日付（2026-11-05）・respStmt 名（claude-b154〜b158-review）・前バッチ固有のハードコード（「اثنان」型 D06253、REF 期待転送先、FORCE_CONCAT、幻番号リスト、毒 wd リスト、汚染番号リスト）を本バッチ用に見直してから実行し、100件すべてに次を機械的に検査する。各項目を「点検N件中違反M件」で報告:
1. well-formed（xml.etree）。
2. REF 方式X の形（type="reference" subtype="LIMBO"・実伝由来要素なし・note 順序 source→translation ja→translation en→reference・target が実在 AIND（corpus_index にある）か #NEEDID・ファイル名 `REF_` 接頭辞と一致）。8件。
3. 原文 `<note type="source" xml:lang="ar">` と corpus_B154-158.json の `text` の一致（改行・空白の正規化後）。不一致はすべて列挙。
4. 日付属性（when-custom ⇔ when の対応、ヒジュラ年値が @when にないか、4桁ゼロ詰め、精度一致、notBefore/notAfter の整合）。h2g.py による再計算で全件検算。
5. persName name_only の世代数（≤3）、full に居住句・職名句がないか。
6. respStmt（初版が orig と同一で残り、校閲 respStmt に persName `claude-b154〜b158-review`（チャンクと一致）・date 2026-11-05、resp=校閲）。
7. ID 書式（`#`・`wd:`・`gn:` 欠落、AIND-D 5桁（英字接尾辞 D00544a は許容）、TMP-P 6桁、他 TMP 5桁、passive/active と xml:id の整合）。
8. 幻 AIND（Individuals にも corpus にもない）。
9. 幻 TMP（ID-Master `idmaster_ext_20261105.tsv` 未登録の非仮番号。仮番号 `TMP-x-NEW154〜158-nn` は TMP_NEW_B15x.tsv に登録があること、チャンク番号がファイルの属するチャンクと一致すること）。
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
21. 規則24 の記録: FIXLOG_B15x.tsv の書式（9列・固定語彙・batch_id=B154-158）と件数。
22. 「أرخه ابن فهد」の振り分け: source note に「أرخه ابن فهد」「ذكره (التقي) بن فهد」を含む全件について、death の when-custom と Pattern A の persName ref（D09211/D05979/D03985）・cert の対応を表にして報告。
結果は `mech_results.json`、報告は `VERIFY_REPORT_mech.md`、指摘一覧は `FINDINGS_mech.tsv`（いずれも `docs/batches/B154-158/` に。スクリプトは `verify/` に再実行可能な形で残し、報告に保存場所を記すこと）。さらに `count_assertions.py docs/_work/B154-158_incoming/B154-158` を全件で実行し、assertion 総数と内訳を報告に載せる。

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
