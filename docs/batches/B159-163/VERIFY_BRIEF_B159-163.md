# 独立検証パス・ブリーフ（B159-163、2026-11-08）

あなたは al-Sakhāwī『al-Ḍawʾ al-Lāmiʿ』の TEI-XML プロソポグラフィDB（AINet-DB）の**校閲結果を検証する独立検証者**です。校閲者（別のエージェント5名、チャンク B159〜B163 各20件）が作った修正版 XML 100件（実項86＋REF化14）に、校閲者自身が作り込んだ誤り・取りこぼしがないかを、原文と突合して洗い出してください。**XML・corpus・ID-Master・Individuals は一切修正しないでください**（読み取りのみ。報告ファイルだけを書く）。git 操作も禁止です。

## 作業環境
- **作業場所はクラウドの clone `/home/claude/ainet-db-sakhawi`**。`Bash`・`Read`・`Edit`・`Write` を直接使う（Mac の device_bash は使わない）。コマンドは `cd /home/claude/ainet-db-sakhawi && ...` で始める。**git 操作・ファイル削除は禁止**。**XML は編集しない（読み取り専用）**。書くのは自分の報告ファイルだけ。
- **検証対象（校閲後 XML）**: `docs/_work/B159-163_incoming/B159-163/` の100件（フラット配置。`REF_` 接頭辞付き14件は転送見出し）。チャンクとの対応は `docs/_work/B159-163_incoming/origin_folders_final.tsv`（現在のファイル名<TAB>チャンク）。
- **校閲前（Gemini 初版）**: `docs/_work/B159-163_incoming/orig/`（100件、元のファイル名）。
- **原文**: `docs/_work/B159-163_incoming/corpus_B159-163.json`（キー `D06400` 形式）。corpus 全体: `docs/_work/B159-163_incoming/vc/corpus_index.json`。任意の項: `python3 -c "import json;d=json.load(open('docs/_work/B159-163_incoming/vc/corpus_index.json'));print(d['AIND-D08224']['text'])"`。
- 検索ツール: `python3 docs/_work/B159-163_incoming/vc/hw.py "<語1>" "<語2>"`／`vc/hwm.py`／`vc/idsearch.py "<文字列>" [件数]`／`vc/idm.py TMP-P-000010`／`vc/rgrep.py "<文字列>" [件数]`／日付 `vc/h2g.py`。
- ID-Master: `docs/_work/idmaster_ext_20261106.tsv`（2026-11-06 取得、8,719 行）。新規 TMP は仮番号（`TMP-x-NEW159-nn`〜`NEW163-nn`）のまま XML にある。典拠台帳: `python3 docs/authority/lookup.py Q…`。
- 校閲者の記録: `docs/batches/B159-163/` の `REVIEW_NOTES_B1xx.md`・`ISSUES_B1xx.md`・`TMP_NEW_B1xx.tsv`・`FIXLOG_B1xx.tsv`（B159〜B163）、precheck `precheck_B159-163_before.md`、規約全文 `CHUNK_BRIEF_B159-163.md`（**まずこれを読む**。統一規則1〜62）。

## 規約の要点（CHUNK_BRIEF が正）
第三者言及は Pattern A（event cultural/mention + persName ref）／relation 向き: 師弟は active=師・passive=学生、親族・社会関係は active=相手・passive=本項主／TMP-P 発行ルールと父は必ず relation（本伝→AIND、祖父名復元→TMP-P、裸名→#NEEDID の father relation を必ず立てる＝規則3 改訂）／@when は西暦（グレゴリオ）のみ・精度は when-custom に合わせる、ヒジュラは when-custom／原文にない属性・地名を補わない（規則22）／規則25 原文どおり読む／規則26 同定は確実な場合のみ（通称・推定では AIND に同定せず TMP、ただし ابن فهد 振り分け規則は例外）／規則27 連結レコード／規則28「رأيته فيمن عرض عليه」「كتب بالشهادة」型は本項主＝行為者／規則29「خلف أخاه/والده」は predecessor／規則30 頻出確定IDは年代確認／規則31 relation desc は相手名のみ／規則37 本項主の見出しナサブで特定できる父祖は AIND で relation／規則38 本伝探索はナサブ1段ずらし・女性部・repo 既存使用まで／relation の @n は規約A（親族には付けない、非親族のみ1起点連番）／初版 respStmt は非改変、校閲 respStmt は `claude-b159〜b163-review`・2026-11-06／en 訳は英語／転送見出しは REF 方式X／汚染番号 TMP-P-000529・000530・000064・000664 等は別人流用禁止／毒 wd Q160851→Q228986、Q191314→Q233387／wd・gn は記憶から書かない。

## 本バッチの REF（転送先の原文を必ず読み、転送先として正しいか確認）
B162（6件）: D06484→D06513／D06493→D06512／D06495→D06546（خطاب／حطاب）／D06497→D06473／D06498→D06552（同じ転送先の第2見出し D06565 は本バッチ外）／D08198→D04157（「هو عبد القادر مضى」）。
B163（8件）: D08229→D08069／D08231→D08583／D08237→D08606／D08238→D08157／D08240→D08224（يوسيف）／D08244→D08146／D08245→D08595／D08249→D08065。
**実項として扱われたもの**: D03182・D03195（「له ذكر في」型）、D06430（欠字）、D06443（「لعله ابن مبارك السقطي」）。ブリーフは B162 の REF 候補を7と数えたが校閲者は6と判定（§D162-10）＝どれが該当しなかったかを確かめる。

## 本バッチ固有の検証点
- **オーケストレーターのブリーフ自体の誤り（校閲者が是正）を裏取り**: D08243「شيخنا الرشيدي」はブリーフの D00907 ではなく **#AIND-D07805**（§D163-4）／D00396「ابن الشماع」はブリーフ候補 D06812 ではなく **#AIND-D08910a**（§D159-6）／D03178「والدي」はサハーウィーの父ではなく話者 ابن عبد الحق（D04458）の父 **D03516**（規則59(f)）。逆に、校閲者がブリーフどおりに使った番号も鵜呑みにせず相手側本文で確かめる。
- **校閲者が付けた AIND 同定を相手側原文で裏取り**（全件は REVIEW_NOTES_B159〜B163）。とくに cert medium の同定と、ブリーフにない新しい同定:
  - B159: D00356 父 D10495・兄弟 D09578・弟子 D03680／D00359 主人 D03484・D10491／D00360 父 D11146・母 D13024・前任 D00340（ラカブ不一致、medium）／D00363 D02273／D00393 D09892・D06947（medium）／D03182 D00350／D03185 父 D05102／D03186 父 D05170／D03191 父 D10188・兄弟 D10178／D03195 主人 D05185／D06400 主人 D03345／D06401 主人 D10152・記録者 D00710。
  - B160: D06410 主人 D03448／D06411 D02364／D06416 祖父 D02481／D06420 師 D05506・学生 D05716・D03121／D06422 D00900（向き: 本項主＝師）／D06431 師 D05054／D06433 主人 D02237・後任 D06305・婿 D00846／D06435 前任 D03257／D06439 D02178。
  - B161: D06441 父 D01650・兄弟 D05043・D06991／D06446・D08222・D08225 の عبد الكبير الحضرمي＝D04238／D06447 主人 D09082（medium、規則26 例外2）／D06449 父 D10112a・祖父 D05354・姉妹 D13814（medium）／D06450 主人 D06051／D06458 主人 D06568／D06464 父 D00014・叔父 D03550。
  - B162: D06467 父 D00023・雇い主 D01435（medium）／D06469 父 D00043・師 D04736／D06479 子 D00232・師 D00335・D05452・D00896・D03778・D08929／D06482 父 D00029・兄弟 D04829・D03538・D04049／D06489 甥 D07694／D06492 師 D05452・D05172／D08222 父 D05690／D08225 父 D05688・母 D13667・母方祖父 D03934／D08226 D04657（medium）。
  - B163: D08232 師 D06773（イブン・ハジャル引用中の一人称）／D08233 ⇄ D08133 possible_identity high・父 D05285（medium）／D08243 D07805／D08247 子 D01436・雇い主 D08369／D10095 師 D04999・同学者 D07301／D10101 学生 D04690／D08230 D10050（medium、الجمال／الكمال）。
- **新規 TMP（TMP_NEW_B159〜163.tsv、計27件）の本伝・既登録の見落とし**（16バッチ連続で検証パスの最多捕捉）。とくに父の TMP-P（NEW161-01〜03、NEW162-01、NEW163-01・02、NEW159-02 祖父）と人物 TMP（NEW159-01 الشمس الحريري、NEW160-01 صرغتمش يابو、NEW160-02 بخشباي）。
- **名寄せ提案（ISSUES）**: 太田氏登録 TMP-P 11件（001414〜001425、§D159-1・4）、TMP-P-000629→D04238、000601→D02089、000040→D03550（§D161）、TMP-P-000187＝D06467 本人（§D162-1）、TMP-P-001002→D08242（§D163-3）。各提案が規則26・規則62（使用箇所の原文の呼び方）を満たすか。
- **父 relation（規則3）**: 全実項に father relation があるか。汚染番号 TMP-P-000530・000529・000490・000064・000664・000183 が残っていないか。
- **「ممن سمع مني」型ほか一人称**（D06415・D08242・D06464・D10095「سمع مع الجماعة علي」）、引用中の一人称（D08222「شيوخنا」＝الفاسي、D08232・D10094 のイブン・ハジャル、D03178 の ابن عبد الحق）。
- **「أرخه ابن فهد」振り分け（規則43・58・60(a)、cert は event 側）**: D03185・D03186・D06403/D06404（أرخهما）・D06416・D06449・D06451〜D06453（أرخهم、875 で D05979 medium と校閲者は判断）・D08225。
- **日付**: 一の位・十の位だけの年（D03179・D06426・D06454・D08248・D06450）、D06448「سنة تسع」（校閲者は 799 medium、初版 809、§D161）、D06455「ستيمن」、D06402「آخر الدولة الناصرية فرج」（§D160-1）、D10097（death を範囲で新規追加）、D03191 の就任年異説。**全日付を h2g.py で独立に再計算**。
- **規則22**（placeName の除去しすぎ・残しすぎ）: 校閲者は B160 で9件・B161 でニスバ由来の مكة ×4 などを除去。D03186「بالغد」を地名とした読み（§D159-8）、D06416「بين الحرمين」（§D160-5）。
- **他人の職を state にしていないか**（D00359・D00360・D06410・D06420・D06433・D06448）。
- **規則31（desc）と規則54（初版 respStmt 非改変）**を全件で。
- **ISSUES（B159 10／B160 10／B161 7／B162 10／B163 8）のうち、統一規則・repo 先例・corpus 証拠で解決できるもの**に解決案を添える。
- **ID-Master 未登録 wd/gn の新規使用**がないか（例: §D160-3 البيرة gn:321062）。

## 出力と記録（規則24）
指定された報告ファイルに、**誤りと思われるものだけ**を、ファイルID・箇所・根拠（原文引用）・提案修正の4点で列挙し、各項に確信度 H/M/L、`assertion_type`（persName/date/relation/placeName/affiliation/event/state/bibl/id_assignment/wd_ref/gn_ref/translation/ref_target/other）と `error_category`（FP=作り込み／FN=取りこぼし／substitution=値誤り）を付けること。**「違反ゼロ」の点検項目も分母つきで必ず書く**。冒頭に「点検した assertion の概数・検出数（H/M/L、FP/FN/substitution 別）」を表で。さらに機械可読の指摘一覧を `FINDINGS_<名前>.tsv`（ヘッダなし、列=`batch_id, entry_id, assertion_type, error_category, severity, origin_stage, caught_stage, resolution, description`。`batch_id`=B159-163、`origin_stage`=claude_review（校閲者が作り込んだ・見落とした誤りの場合）または gemini_draft（初版の誤りが校閲後も残っていた場合）、`caught_stage`=verify_content または verify_mech、`resolution`=open）で出す。

---
（以下、役割別の節。自分に割り当てられた節に従う）

## あなたの役割: 内容検証（corpus 逆引き） — 担当 （チャンク指定はプロンプト参照）

担当範囲のすべてのファイルについて、校閲後 XML と corpus 原文を並べて読み、次を点検する:
- (a) 校閲者が付けた全ての `#AIND-D…` 同定が正しいか（相手側原文で裏取り。ナサブ・没年・「الماضي/الآتي」の整合・綴り揺れ・同名異人）。REF は**転送先の原文を必ず読み**、転送先として正しいか確認。
- (b) 校閲者が「本伝なし」として新規 TMP を発行した件（`TMP_NEW_B1xx.tsv`）のうち、corpus に本伝がある／ID-Master に既登録のものがないか。**父・祖父の名＋ニスバで corpus 見出しを逆引き**（変綴り・逆転ナサブ・索引項（ニスバ／ابن-部、D11xxx〜D13xxx 帯）・كنى 部・女性部から探す）。
- (c) Pattern A の欠落・relation 化の残存、relation の向き、subtype の妥当性、#NEEDID 維持の妥当性（登録済み ID の放置がないか）、規則23・26・37 の適用が過不足ないか、チャンクをまたぐ相互参照が双方向に閉合しているか（D00356⇄D09578・D10495、D03191⇄D10178、D06464⇄D00014、D06482⇄D04829・D03538・D04049、D08242⇄D01102、D08233⇄D08133、D06451〜D06453 の ابن فهد 振り分けの一貫性、B159 D06461 前任 سنبل⇄B161 §D161-6）。
- (d) 日付（when-custom と when の整合、精度の一致、notBefore/notAfter、ヒジュラ年の @when 混入、グレゴリオ換算）。**すべての日付を h2g.py で独立に再計算**。
- (e) 訳文（ja/en）の誤り（主語・数字・脱落・人名転写・hedge の脱落・内部ID・生アラビア語・立項連番・推測句の混入）。**ja 訳の語中 بن は「ブン」**。en が英語であること。欠字・途切れ（D06430「ماجي بن ...」・D06460「ومات .」）を訳で補っていないか。
- (f) 幻番号・統合済み番号・汚染番号・毒 wd・空属性・ID 書式。
- (g) 校閲者メモ（REVIEW_NOTES）と XML の不一致。
- (h) 初版にあって校閲版で消えた情報のうち、消すべきでなかったもの（原文にある師・弟子・役職・出来事）。
- (i) 原文にない属性・地名（ニスバ由来 residence、学派、生年、cert="high" の捏造）が残っていないか。規則22 の 1〜6。
- (j) 連結レコード（校閲者報告上は該当なし）が実際に無いか、担当範囲の原文末尾を点検し、あれば訳文・event への混入を見る。
- (k) 校閲者が出した ISSUES のうち、統一規則・repo 先例・corpus 証拠で解決できるものがないか（解決案を添える）。

担当ファイル数が多いので、ファイルごとに系統的に。校閲者の結論を鵜呑みにせず、根拠（原文）から独立に読み直すこと。分母は `python3 docs/_work/B159-163_incoming/verify/count_assertions.py docs/_work/B159-163_incoming/B159-163 D00356-D06449` のように担当範囲を指定して機械計数し、報告冒頭の表に内訳を載せる。

---

## あなたの役割: 機械検査（スクリプトによる全件検査） — 担当 100件すべて

`docs/_work/B159-163_incoming/verify/` に前バッチの機械検査スクリプト（mech_lib.py・mech_items_a〜l.py・mech_check.py・mech_report.py・count_assertions.py・mech_sev_override.py）をコピーし、**パス・ID-Master・batch_id（B159-163／idmaster_ext_20261106）と mech_lib.py の CHUNKS（B159〜B163）・REVIEW_DATE（2026-11-06）だけ置換済み**。mech_items_* に残る**前バッチ（B154-158）固有のハードコード**（REF 期待転送先、FORCE_CONCAT、幻番号・毒 wd・汚染番号リスト、ファイル個別の点検）は本ブリーフに合わせて差し替えること（本バッチ用の個別点検は mech_items_m.py を新設してよい）。日付（2026-11-06）・respStmt 名（claude-b159〜b163-review）・前バッチ固有のハードコード（「اثنان」型 D06253、REF 期待転送先、FORCE_CONCAT、幻番号リスト、毒 wd リスト、汚染番号リスト）を本バッチ用に見直してから実行し、100件すべてに次を機械的に検査する。各項目を「点検N件中違反M件」で報告:
1. well-formed（xml.etree）。
2. REF 方式X の形（type="reference" subtype="LIMBO"・実伝由来要素なし・note 順序 source→translation ja→translation en→reference・target が実在 AIND（corpus_index にある）か #NEEDID・ファイル名 `REF_` 接頭辞と一致）。14件。
3. 原文 `<note type="source" xml:lang="ar">` と corpus_B159-163.json の `text` の一致（改行・空白の正規化後）。不一致はすべて列挙。
4. 日付属性（when-custom ⇔ when の対応、ヒジュラ年値が @when にないか、4桁ゼロ詰め、精度一致、notBefore/notAfter の整合）。h2g.py による再計算で全件検算。
5. persName name_only の世代数（≤3）、full に居住句・職名句がないか。
6. respStmt（初版が orig と同一で残り、校閲 respStmt に persName `claude-b159〜b163-review`（チャンクと一致）・date 2026-11-06、resp=校閲）。
7. ID 書式（`#`・`wd:`・`gn:` 欠落、AIND-D 5桁（英字接尾辞 D00544a は許容）、TMP-P 6桁、他 TMP 5桁、passive/active と xml:id の整合）。
8. 幻 AIND（Individuals にも corpus にもない）。
9. 幻 TMP（ID-Master `idmaster_ext_20261106.tsv` 未登録の非仮番号。仮番号 `TMP-x-NEW159〜163-nn` は TMP_NEW_B1xx.tsv に登録があること、チャンク番号がファイルの属するチャンクと一致すること）。
10. 毒 wd（Q160851／Q191314／Q35160／Q589／Q3824443／Q327129／Q12247942／Q381208／Q1164991／Q1283／Q3306083、人物位置の Q4120093 等）の属性使用、ID-Master にも repo にもない wd/gn が新規に付いていないか（付いていれば「未確認」の記録が ISSUES にあるか）。
11. 汚染 TMP の person 位置使用（TMP-P-000529／000530／000490／000064／000664／000183／000063／000489／000352／000140／000131／000603／000204／000350／000719／000694／000292 など）。TMP-N の person 位置流用。カテゴリ不一致。
12. 規約A（relation/@n）。
13. affiliation と state の同一 ref 二重符号化。
14. 統制外の type/subtype（repo の `Individuals/**/*.xml` に既存の値と照合）。
15. 仮 TMP のチャンク間重複・ID-Master との近似一致、TMP_NEW ⇔ XML の片側漏れ。TSV が7列か。15c 並行追加（今回はゼロ）。
16. 汎用名 TMP-P の TSV Note に「⚠汎用名」があるか。
17. `<desc>` に xml:lang があるか。`xml:lang="lat"` の残存。en 訳が英語か。ja 訳に「ビン」・ラテン文字・内部ID・立項連番が混入していないか。
18. 規則22 機械検査: アラビア語 placeName のうち原文（source note）に現れないもの（照応・حج 由来を除く）をリストし、cert の付け方と合わせて報告。空 residence イベントの有無。
19. relation 整合: passive/active の少なくとも一方が本項主、self-relation なし、相互 relation の矛盾、desc が相手の名前のみ、possible_identity が本バッチ内では双方向か。
20. 校閲前 orig と比べた変更の概要統計（ファイルごとの要素数の増減）を表で。極端な減少があれば列挙。
21. 規則24 の記録: FIXLOG_B1xx.tsv の書式（9列・固定語彙・batch_id=B159-163）と件数。
22. 「أرخه ابن فهد」の振り分け: source note に「أرخه ابن فهد」「ذكره (التقي) بن فهد」を含む全件について、death の when-custom と Pattern A の persName ref（D09211/D05979/D03985）・cert の対応を表にして報告。
結果は `mech_results.json`、報告は `VERIFY_REPORT_mech.md`、指摘一覧は `FINDINGS_mech.tsv`（いずれも `docs/batches/B159-163/` に。スクリプトは `verify/` に再実行可能な形で残し、報告に保存場所を記すこと）。さらに `count_assertions.py docs/_work/B159-163_incoming/B159-163` を全件で実行し、assertion 総数と内訳を報告に載せる。

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
