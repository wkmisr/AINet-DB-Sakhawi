# 独立検証パス・ブリーフ（B99-103、2026-10-04）

あなたは al-Sakhāwī『al-Ḍawʾ al-Lāmiʿ』の TEI-XML プロソポグラフィDB（AINet-DB）の**校閲結果を検証する独立検証者**です。校閲者（別のエージェント5名、チャンク B99〜B103 各20件）が作った修正版 XML 100件（実項87＋REF化13）に、校閲者自身が作り込んだ誤り・取りこぼしがないかを、原文と突合して洗い出してください。**XML・corpus・ID-Master・Individuals は一切修正しないでください**（読み取りのみ。報告ファイルだけを書く）。git 操作も禁止です。

## 作業環境
- すべて `mcp__remote-devices__device_bash`（Mac 上）で行う。毎回 `cd "$HOME/mnt/AINet-DB-Sakhawi" && ...`。呼び出しごとに新しいシェル。ファイルの読み書きは python3 / cat / sed で（クラウド側の Read/Edit/Write/Bash はこのマシンのファイルに届かない）。
- **検証対象（校閲後 XML）**: `docs/_work/B99-103_incoming/B99-103/` の100件（`REF_` 接頭辞付き13件は転送見出し）。受領チャンクとの対応は `docs/_work/B99-103_incoming/origin_folders.tsv`。
- **校閲前（Gemini 初版）**: `docs/_work/B99-103_incoming/orig/`（比較用。校閲で消えた情報のうち、消すべきでなかったものがないか）。
- **原文**: `docs/_work/B99-103_incoming/corpus_B99-103.json`（100件の本文、キー `D04957` 形式）。corpus 全体: `docs/_work/B99-103_incoming/vc/corpus_index.json`（AIND-ID → {src, dollars, text, line}）。`python3 -c "import json;d=json.load(open('docs/_work/B99-103_incoming/vc/corpus_index.json'));print(d['AIND-D05026']['text'])"` で任意の項を読める。**校閲者が付けた同定（#AIND-Dxxxxx）は、必ずこの辞書で相手側の原文を読んで裏取りすること。**
- 検索ツール（cwd=リポジトリルート）: `python3 docs/_work/B99-103_incoming/vc/hw.py "<語1>" "<語2>"`（corpus 見出し先頭260字の AND 検索）／`vc/idsearch.py "<文字列>" [件数]`（ID-Master のアラビア語・ラテン語・Note 検索）／`vc/idm.py TMP-P-000010`（ID 行表示）／`vc/rgrep.py "<文字列>" [件数]`（repo の Individuals 全文検索。サブフォルダ再帰）／`python3 docs/records/records_B79-83/tools/h2g.py 886-9 874-3-15 850`（ヒジュラ→西暦。**グレゴリオ暦（proleptic）を正とする**。`--selftest` あり）。
- ID-Master: `docs/_work/idmaster_ext_20261004.tsv`（2026-10-04 のシート実物 8,041 行。列=[登録者,Category,Arabic,Latin,ID,Note,修正]。太田氏の並行追加 P-001332〜001357 等を含む）。新規 TMP は仮番号（`TMP-x-NEW99-nn`〜`NEW103-nn`）のまま XML にある。
- 校閲者の記録: `docs/records/records_B99-103/` の `REVIEW_NOTES_B1xx.md`・`ISSUES_B1xx.md`・`TMP_NEW_B1xx.tsv`・`FIXLOG_B1xx.tsv`、precheck: `precheck_B99-103_before.md`、規約全文: `CHUNK_BRIEF_B99-103.md`（**まずこれを読む**。統一規則1〜26・頻出確定ID・汚染番号を含む）。

## 規約の要点（CHUNK_BRIEF が正）
第三者言及は Pattern A（event cultural/mention + persName ref）／relation 向き: 師弟は active=師・passive=学生、親族・社会関係は active=相手・passive=本項主／TMP-P 発行ルールと父の3段階（祖父名復元→TMP-P、本伝→AIND、裸名→#NEEDID）／@when は西暦（グレゴリオ）のみ・精度は when-custom に合わせる、ヒジュラは when-custom／原文にない属性・地名を補わない（規則22）／規則25 原文どおり読む／規則26 同定は確実な場合のみ（通称・推定では AIND に同定せず TMP、ただし ابن فهد 振り分け規則は例外）／relation の @n は規約A（親族には付けない、非親族のみ1起点連番）／初版 respStmt は非改変、校閲 respStmt は `claude-b1xx-review`・2026-10-04／en 訳は英語／転送見出しは REF 方式X／汚染番号 TMP-P-000529・000204 等は別人流用禁止／毒 wd Q160851→Q228986、Q191314→Q233387／wd・gn は記憶から書かない。

## 本バッチの REF 13件（転送先の原文を必ず読み、転送先として正しいか確認）
D04969→D05026／D04979→D05032／D04994→D05026／D05720→D05506／D05721→D05462（「أشير إليه قريبا」を D05719 末尾に連結した転送見出し「علي العلاء عصفور المكتب」への指示と解した＝厳しく見る）／D05736→D05742（本バッチ内）／D05737→D04937／D05738→D05552（cert medium、「هو ابن مضى」の名脱落。別候補 D05332）／D05744→D05691（صير/صبر の綴り揺れ）／D05760→#NEEDID（「سقطت」のみ）／D05763→D05462／D05764→D04925／D05769→D05749（B102）。

## 本バッチ固有の検証点
- **corpus レコード末尾に別の転送見出しが連結されているもの**: D05719（末尾「علي العلاء عصفور المكتب . في ابن محمد ابن عبد النصير」）・D05751（末尾「علي الرملاوي … مضى في ابن خليل بن رسلان」）。校閲者は source note に corpus どおり全文を残し editorial note を付した（B94-98 の ★連結4件は実伝部分のみを source note にした＝方針の不一致は集約側で統一する。検証者は「訳文・event・death に連結部分が混入していないか」を見る）。ほかに同種の連結がないか、100件の原文末尾を機械的に点検（末尾に「. في …」「مضى في …」「يأتي في …」で終わる独立文があるもの）。
- **二重立項（possible_identity）**: D04957⇄D04954（medium）、D04974⇄D04995（medium、双方向）、D05625⇄D05581（high、D05581 は repo 収録済み）、D05740⇄D05264（high）、D05308⇄D10932（low）。根拠を原文で確認し、cert の妥当性と双方向性（本バッチ内の相手には逆方向があるか、repo 側の相手は統合時に付ける旨が ISSUES にあるか）を見る。
- **「اثنان」型**: D05715（REF 化せず実伝由来要素なしの実項、先例 D00404）、D05732（実項、後半に第2の人物の記述）。妥当性を判断。
- **「أرخه ابن فهد」振り分け**（十数件）: 没年と充てた ID（D09211 low／D05979 medium／D03985）の対応を全件機械的に点検。D05758「أرخ الثلاثة المنير」の読み。
- **「ممن سمع مني／لازمني」型**（D04962・D05294・D05297・D05311・D05312・D05772・D05784）: active=wd:Q4120128、場所 placeName、D05784「سمع علي」＝私に、の処理。
- **父・祖父・子の同定**: B100（D04992→D01013、D04995→D01022、D04997→D01029、D04998 子→D00986、D05293→D05686、D05301→D05849 medium）、B103（D05776→D04876、D05785→D00452 medium、D05787 叔父 D10697、D05789 父 D00827・祖父 D03687・弟 D06687、D05790 父 D00833・祖父 D03742・兄 D04977/D06688、D05797 子 D01110、D05800 父 D01215）、B99（D04959 父 D00634、D04970 子 D05287、D04980 父 D00856・叔父 D07676・師 D05583、D04963 師 D05465/D00623/D07210）、B101（D05728⇄D10929、D05733⇄D10383、D05730 D04181、D05731 D00104、D05733 D08903）、B102（D05748 D00540・D05922、D05750 D09466/D04932/D06758、D05754 D06840、D05757 D01549 medium）。**全件、相手側原文でナサブ・没年・الماضي/الآتي を裏取り**。規則26（確証なき同定は TMP）に照らして cert の付け方を点検。
- **太田氏・篠田氏の並行 TMP との衝突**: 校閲者の新規仮TMP 40件が ID-Master 既登録（とくに行 8007〜8041 の太田氏追加）と重複していないか、アラビア語正規化で照合。

## 出力と記録（規則24）
指定された報告ファイルに、**誤りと思われるものだけ**を、ファイルID・箇所・根拠（原文引用）・提案修正の4点で列挙し、各項に確信度 H/M/L、`assertion_type`（persName/date/relation/placeName/affiliation/event/bibl/id_assignment/wd_ref/gn_ref/other）と `error_category`（FP=作り込み／FN=取りこぼし／substitution=値誤り）を付けること。**「違反ゼロ」の点検項目も分母つきで必ず書く**（例「毒wdの残存 0/166」）。冒頭に「点検した assertion の概数・検出数（H/M/L、FP/FN/substitution 別）」を表で。さらに機械可読の指摘一覧を `FINDINGS_<名前>.tsv`（ヘッダなし、列=`batch_id, entry_id, assertion_type, error_category, severity, origin_stage, caught_stage, resolution, description`。`batch_id`=B99-103、`origin_stage`=claude_review（校閲者が作り込んだ・見落とした誤りの場合）または gemini_draft（初版の誤りが校閲後も残っていた場合）、`caught_stage`=verify_content または verify_mech、`resolution`=open）で出す。

---
（以下、役割別の節。自分に割り当てられた節に従う）

## あなたの役割: 内容検証（corpus 逆引き） — 担当 （チャンク指定はプロンプト参照）

担当範囲のすべてのファイルについて、校閲後 XML と corpus 原文を並べて読み、次を点検する:
- (a) 校閲者が付けた全ての `#AIND-D…` 同定が正しいか（相手側原文で裏取り。ナサブ・没年・「الماضي/الآتي」の整合・綴り揺れ・同名異人）。REF は**転送先の原文を必ず読み**、転送先として正しいか確認。
- (b) 校閲者が「本伝なし」として新規 TMP を発行した件（`TMP_NEW_B1xx.tsv`）のうち、corpus に本伝がある／ID-Master に既登録のものがないか。**父・祖父の名＋ニスバで corpus 見出しを逆引き**（変綴り・逆転ナサブ・索引項（ニスバ／ابن-部、D11xxx〜D13xxx 帯）・كنى 部から探す）。B87〜B94-98 の5バッチ連続で検証パスが「本伝見落とし」を最も多く捕捉した。
- (c) Pattern A の欠落・relation 化の残存、relation の向き、subtype の妥当性、#NEEDID 維持の妥当性（登録済み ID の放置がないか）、規則23（他項にのみある情報は relation のみ cert medium で補完、属性は note 留め）・規則26 の適用が過不足ないか、チャンクをまたぐ相互参照が双方向に閉合しているか。
- (d) 日付（when-custom と when の整合、精度の一致、notBefore/notAfter、ヒジュラ年の @when 混入、グレゴリオ換算）。**すべての日付を h2g.py で独立に再計算**。
- (e) 訳文（ja/en）の誤り（主語・数字・脱落・人名転写・hedge の脱落・内部ID・生アラビア語・立項連番・推測句の混入）。**ja 訳の語中 بن は「ブン」**。en が英語であること。
- (f) 幻番号・統合済み番号・汚染番号・毒 wd・空属性・ID 書式。
- (g) 校閲者メモ（REVIEW_NOTES）と XML の不一致。
- (h) 初版にあって校閲版で消えた情報のうち、消すべきでなかったもの（原文にある師・弟子・役職・出来事）。
- (i) 原文にない属性・地名（ニスバ由来 residence、学派、生年、cert="high" の捏造）が残っていないか。規則22 の 1〜6。
- (j) 連結レコード（D05719・D05751）の訳文・event に連結部分が混入していないか。
- (k) 校閲者が出した ISSUES のうち、統一規則・repo 先例・corpus 証拠で解決できるものがないか（解決案を添える）。

担当ファイル数が多いので、ファイルごとに系統的に。校閲者の結論を鵜呑みにせず、根拠（原文）から独立に読み直すこと。

---

## あなたの役割: 機械検査（スクリプトによる全件検査） — 担当 100件すべて

python3 のスクリプトを書いて（`docs/_work/B99-103_incoming/verify/` に保存）、100件すべてに次を機械的に検査する。各項目を「点検N件中違反M件」で報告:
1. well-formed（xml.etree）。
2. REF 方式X の形（type="reference" subtype="LIMBO"・実伝由来要素（state/event/birth/death/affiliation/relation/nisbah persName）なし・note 順序 source→translation ja→translation en→reference・target が実在 AIND（corpus_index にある）か #NEEDID・ファイル名 `REF_` 接頭辞と一致）。
3. 原文 `<note type="source" xml:lang="ar">` と corpus_B99-103.json の `text` の一致（改行・空白の正規化後）。不一致はすべて列挙。
4. 日付属性（when-custom ⇔ when の対応、ヒジュラ年値が @when にないか、4桁ゼロ詰め、精度一致（年のみ→YYYY、月のみ→YYYY-MM）、notBefore/notAfter の整合）。h2g.py による再計算で主要な死亡・出生・event の西暦を検算できるものは全件検算。
5. persName name_only の世代数（≤3）、full に居住句・職名句がないか（نزيل／خادم／شيخ ～／قاضي ～ 等）。
6. respStmt（初版が orig と同一で残り、校閲 respStmt に persName `claude-b1xx-review`（チャンクと一致）・date 2026-10-04、resp=校閲）。
7. ID 書式（`#`・`wd:`・`gn:` 欠落、AIND-D 5桁、TMP-P 6桁、他 TMP 5桁、passive/active と xml:id の整合）。
8. 幻 AIND（Individuals にも corpus にもない）。
9. 幻 TMP（ID-Master `docs/_work/idmaster_ext_20261004.tsv` 未登録の非仮番号。仮番号 `TMP-x-NEW1xx-nn` は TMP_NEW_B1xx.tsv に登録があること、チャンク番号がファイルの属するチャンクと一致すること）。
10. 毒 wd（Q160851／Q191314／Q35160／Q3824443／Q12247942／Q381208／Q1164991 等）の属性使用、ID-Master にも repo にもない wd/gn が新規に付いていないか（付いていれば「未確認」の記録が ISSUES にあるか）。
11. 汚染 TMP の person 位置使用（TMP-P-000529／000530／000490／000064／000664／000063／000489／000352／000140／000131／000603／000204 など）。TMP-N の person 位置流用。カテゴリ不一致（P/N/L/I/O/T/S の位置適合: relation active/passive と persName ref は P か AIND か wd、placeName は L/gn/wd、affiliation・state は I/O/wd、bibl は T/wd）。
12. 規約A（relation/@n: 親族に @n なし、非親族は1起点の連番）。
13. affiliation と state の同一 ref 二重符号化。
14. 統制外の type/subtype（repo の `Individuals/**/*.xml` に既存の値と照合。relation subtype・event type/subtype・state type・affiliation type・note type）。
15. 仮 TMP のチャンク間重複・ID-Master との近似一致（アラビア語正規化: ا/أ/إ/آ、ة/ه、ى/ي、ال 除去、母音記号除去）、および TMP_NEW ⇔ XML の片側漏れ（XML 未使用の TSV 行／TSV 未登録の仮番号）。TSV が7列か。
16. 汎用名 TMP-P（名＋父名のみ・ニスバのみ）の TSV Note に「⚠汎用名」があるか。
17. `<desc>` に xml:lang があるか。`xml:lang="lat"` の残存がないか（"ar-Latn"）。en 訳が英語か（アラビア文字・日本語が混入していないか）。ja 訳に「ビン」（語中 بن の誤転写）・ラテン文字・内部ID・立項連番が混入していないか。placeName の ref 付与位置。
18. 規則22 機械検査: アラビア語 placeName のうち原文（source note）に現れないもの（照応 بها/فيها/به/منها/إليها/هناك/بلده/حج 由来を除く）をリストし、cert の付け方と合わせて報告。除去 note だけが残る空 residence イベントの有無。
19. relation 整合: passive/active の少なくとも一方が本項主、self-relation なし、相互 relation の矛盾、desc が相手の名前のみ、possible_identity が本バッチ内では双方向か。
20. 校閲前 orig と比べた変更の概要統計（ファイルごとの要素数の増減）を表で。極端な減少（情報の大量脱落）があれば列挙。
21. 規則24 の記録: FIXLOG_B1xx.tsv の書式（9列・語彙が固定語彙・batch_id=B99-103）と件数。
22. 「أرخه ابن فهد」の振り分け: source note に「أرخه ابن فهد」を含む全件について、death の when-custom と Pattern A の persName ref（D09211/D05979/D03985）・cert の対応を表にして報告。
スクリプトは再実行可能な形で残し、報告に保存場所を記すこと。
