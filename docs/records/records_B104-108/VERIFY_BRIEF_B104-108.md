# 独立検証パス・ブリーフ（B104-108、2026-10-05）

あなたは al-Sakhāwī『al-Ḍawʾ al-Lāmiʿ』の TEI-XML プロソポグラフィDB（AINet-DB）の**校閲結果を検証する独立検証者**です。校閲者（別のエージェント5名、チャンク B104〜B108 各20件）が作った修正版 XML 100件（実項89＋REF化11）に、校閲者自身が作り込んだ誤り・取りこぼしがないかを、原文と突合して洗い出してください。**XML・corpus・ID-Master・Individuals は一切修正しないでください**（読み取りのみ。報告ファイルだけを書く）。git 操作も禁止です。

## 作業環境
- すべて `mcp__remote-devices__device_bash`（Mac 上）で行う。毎回 `cd "$HOME/mnt/AINet-DB-Sakhawi" && ...`。呼び出しごとに新しいシェル。ファイルの読み書きは python3 / cat / sed で（クラウド側の Read/Edit/Write/Bash はこのマシンのファイルに届かない）。
- **検証対象（校閲後 XML）**: `docs/_work/B104-108_incoming/B104-108/` の100件（`REF_` 接頭辞付き11件は転送見出し）。受領チャンクとの対応は `docs/_work/B104-108_incoming/origin_folders.tsv`。
- **校閲前（Gemini 初版）**: `docs/_work/B104-108_incoming/orig/`（比較用。校閲で消えた情報のうち、消すべきでなかったものがないか）。
- **原文**: `docs/_work/B104-108_incoming/corpus_B104-108.json`（100件の本文、キー `D04957` 形式）。corpus 全体: `docs/_work/B104-108_incoming/vc/corpus_index.json`（AIND-ID → {src, dollars, text, line}）。`python3 -c "import json;d=json.load(open('docs/_work/B104-108_incoming/vc/corpus_index.json'));print(d['AIND-D06040']['text'])"` で任意の項を読める。**校閲者が付けた同定（#AIND-Dxxxxx）は、必ずこの辞書で相手側の原文を読んで裏取りすること。**
- 検索ツール（cwd=リポジトリルート）: `python3 docs/_work/B104-108_incoming/vc/hw.py "<語1>" "<語2>"`（corpus 見出し先頭260字の AND 検索）／`vc/idsearch.py "<文字列>" [件数]`（ID-Master のアラビア語・ラテン語・Note 検索）／`vc/idm.py TMP-P-000010`（ID 行表示）／`vc/rgrep.py "<文字列>" [件数]`（repo の Individuals 全文検索。サブフォルダ再帰）／`python3 docs/records/records_B79-83/tools/h2g.py 886-9 874-3-15 850`（ヒジュラ→西暦。**グレゴリオ暦（proleptic）を正とする**。`--selftest` あり）。
- ID-Master: `docs/_work/idmaster_ext_20261005b.tsv`（2026-10-05 のシート実物 8,082 行。列=[登録者,Category,Arabic,Latin,ID,Note,修正]。太田氏の並行追加 P-001332〜001357 等と B99-103 の新規41行（P-001358〜001373 等）を含む）。新規 TMP は仮番号（`TMP-x-NEW104-nn`〜`NEW108-nn`）のまま XML にある。
- 校閲者の記録: `docs/records/records_B104-108/` の `REVIEW_NOTES_B10x.md`・`ISSUES_B10x.md`・`TMP_NEW_B10x.tsv`・`FIXLOG_B10x.tsv`、precheck: `precheck_B104-108_before.md`、規約全文: `CHUNK_BRIEF_B104-108.md`（**まずこれを読む**。統一規則1〜31・頻出確定ID・汚染番号を含む）。

## 規約の要点（CHUNK_BRIEF が正）
第三者言及は Pattern A（event cultural/mention + persName ref）／relation 向き: 師弟は active=師・passive=学生、親族・社会関係は active=相手・passive=本項主／TMP-P 発行ルールと父の3段階（祖父名復元→TMP-P、本伝→AIND、裸名→#NEEDID）／@when は西暦（グレゴリオ）のみ・精度は when-custom に合わせる、ヒジュラは when-custom／原文にない属性・地名を補わない（規則22）／規則25 原文どおり読む／規則26 同定は確実な場合のみ（通称・推定では AIND に同定せず TMP、ただし ابن فهد 振り分け規則は例外）／規則27 連結レコードは source note を実伝部分のみ＋editorial note／規則28「رأيته فيمن عرض عليه」型は本項主＝試問者／規則29「خلف أخاه/والده」は predecessor／規則30 頻出確定IDは年代確認／規則31 relation desc は相手名のみ／relation の @n は規約A（親族には付けない、非親族のみ1起点連番）／初版 respStmt は非改変、校閲 respStmt は `claude-b10x-review`・2026-10-05／en 訳は英語／転送見出しは REF 方式X／汚染番号 TMP-P-000529・000204 等は別人流用禁止／毒 wd Q160851→Q228986、Q191314→Q233387／wd・gn は記憶から書かない。

## 本バッチの REF 11件（転送先の原文を必ず読み、転送先として正しいか確認）
D05811→D06040（عمر العدني المسلي）／D05827→D06040（直接の指示先 D05811 が REF のため最終転送先を target、経由を note）／D05828→D05893（B106）／D05829→D00688（الشهاب بن رسلان。「言及先への転送」型）／D05838→D05895（B106、ابن الملقن）／D05878→D04311（訂正転送「هو عبد اللطيف بن أحمد」）／D05888→D06025（عمر الكمال البلخي。父名 عبد الله の異伝あり＝§D106-1）／D05892→D05871（B105）／D05924→D05926（B107 内）／D05943→D06001（校閲者はブリーフ案 D05942 を否定）／D05952→D05973（ابن الصابوني）。**D05900（الماضي أبوه）・D05938（名のみ）は実項**として処理された＝妥当か確認。

## 本バッチ固有の検証点
- **チャンク間の相互参照**: D05828→D05893、D05838→D05895、D05892→D05871、D05924→D05926、D05837 の後見人＝D05938（B108、medium）、D05941⇄D05942 の兄弟関係（§D108）、D05891/D05951 で共用の طلحة العنبري（TMP-P-NEW106-04、§D106-5 で B108 に申し送り＝B108 側が別の仮番号を切っていないか）。相互 relation・possible_identity の双方向性と仮TMP の重複を点検。
- **父・親族・師の同定（校閲者報告より。全件、相手側原文でナサブ・没年・الماضي/الآتي を裏取り）**: B104: D05803 師 D00418／D05813 兄弟 D00075・D00594・D05080／D05819 父 D10822・母方叔父 D06630／D05820 父 D10826・兄 D07237／D05822 父 D10837・岳父 D06757・妻 D13757・子 D08298・主人 D02180／D05830 師 D08853 medium／D05832 子 D00207／D05836 父 D02635・兄弟 D03621／D05837 後見人 D05938 medium。B105: D05839 師 D09562・前任 D08986／D05840 甥 D05425／D05854 子 D08313／D05858 子 D03945／D05868 父 D03967・母 D13332・母方祖父 D06786・師 D00449・D09072 medium／D05869 兄弟 D07675・父 D03971／D05870 父 D03969・師 D09916 medium／D05871 師 D06936・D07181、子 D02608（規則23 で D04519・D03490）／D05872 父 D03979・子 D04520・弟 D07677。B106: D05874 父 D03985・祖父 D05979・D05593／D05876 父 D04131・兄弟 D07706／D05882 父 D04556／D05883 いとこ D07118・D05064／D05884 父 D04574・صهر D03817・D07454／D05889 D05981・D08366／D05891 D05497／D05902 父 D05280・師 D07166・D10715。B107: D05903 父 D05283／D05904 父 D05317・兄弟 D08144／D05905 D08993・D00143／D05908 D08290・D01456／D05911 D05476・D05310／D05912 D00196・D10764・母 D13747 medium／D05920 D03713・D03976・D08814・D10447／D05921 D06214／D05922 D05748・D07236・D00540・D01296・D05270・D03608／D05923 D04864・D05983 medium／D05928 D04440／D05929 D09466・D04932・D06758／D05930 D08349。B108: D05931 父 D06693／D05932 D13497・D01128 medium／D05933 D06012 medium／D05937 D08351／D05941 D07201・D10819 medium／D05942 D07214／D05944 父 D09946・兄 D01306・D04796／D05947 D07349／D05951 D08083。規則26（確証なき同定は TMP）に照らして cert の付け方を点検。
- **「ممن سمع مني」型16件**（D05805・D05813・D05816・D05820・D05824・D05825・D05837・D05847・D05851・D05855・D05870・D05876・D05894・D05907・D05911・D05948）: active=wd:Q4120128、場所は原文にあるときのみ。D05825「سمع علي في سنة خمس وتسعين」、D05837「سمع مني معهم」の処理。
- **「أرخه ابن فهد」9件**（D05803・D05822・D05836・D05873・D05875・D05889・D05929・D05940・D05941）: 没年と充てた ID・cert の対応を全件点検。
- **第三者言及**: شيخنا في إنبائه（D05852・D05853・D05856・D05886・D05887・D05899・D05933）→ Q471116＋T-00034／المقريزي（D05901・D05926・D05932）／البقاعي（D05832 → D00207）／ابن المنير（D05914 → TMP-P-000342）。
- **「المدعو」型**（D05819 عمر المدعو عبد السلام、D05944 — 校閲者は「父の通称」と読んだ）の読みと符号化。D05853 父 المؤيد شيخ=D03345。D05856 الحاجب الكبير（§D105 で O-00066 との統合可否）。
- **長文項**（D05920・D05922・D05923・D05930・D05883・D05884・D05911・D05905）: 師・著作・職歴・旅行の取りこぼし（FN）と、relation @n・placeName（規則22）・bibl の ID 照合を重点的に。
- **ISSUES で挙がった名寄せ提案**（TMP-P-000698→D10822、000364→D06630、000228→D09562、000289→D05593、000534→D08993、000284→D08814、000350→D04440 ほか）の根拠を独立に確認。
- **太田氏・B99-103 の並行 TMP との衝突**: 校閲者の新規仮TMP 77件（P 41・I 9・L 8・O 7・T 8・N 3 ほど）が ID-Master 既登録（行 8007〜8082）と重複していないか、アラビア語正規化で照合。
- **ID-Master 未登録 wd の新規使用**（§D107: الكشاف wd:Q4165175、ابن الجزري wd:Q4120093、بحر الهند wd:Q1283）: ISSUES に「未確認」として残っているか。

## 出力と記録（規則24）
指定された報告ファイルに、**誤りと思われるものだけ**を、ファイルID・箇所・根拠（原文引用）・提案修正の4点で列挙し、各項に確信度 H/M/L、`assertion_type`（persName/date/relation/placeName/affiliation/event/bibl/id_assignment/wd_ref/gn_ref/other）と `error_category`（FP=作り込み／FN=取りこぼし／substitution=値誤り）を付けること。**「違反ゼロ」の点検項目も分母つきで必ず書く**（例「毒wdの残存 0/166」）。冒頭に「点検した assertion の概数・検出数（H/M/L、FP/FN/substitution 別）」を表で。さらに機械可読の指摘一覧を `FINDINGS_<名前>.tsv`（ヘッダなし、列=`batch_id, entry_id, assertion_type, error_category, severity, origin_stage, caught_stage, resolution, description`。`batch_id`=B104-108、`origin_stage`=claude_review（校閲者が作り込んだ・見落とした誤りの場合）または gemini_draft（初版の誤りが校閲後も残っていた場合）、`caught_stage`=verify_content または verify_mech、`resolution`=open）で出す。

---
（以下、役割別の節。自分に割り当てられた節に従う）

## あなたの役割: 内容検証（corpus 逆引き） — 担当 （チャンク指定はプロンプト参照）

担当範囲のすべてのファイルについて、校閲後 XML と corpus 原文を並べて読み、次を点検する:
- (a) 校閲者が付けた全ての `#AIND-D…` 同定が正しいか（相手側原文で裏取り。ナサブ・没年・「الماضي/الآتي」の整合・綴り揺れ・同名異人）。REF は**転送先の原文を必ず読み**、転送先として正しいか確認。
- (b) 校閲者が「本伝なし」として新規 TMP を発行した件（`TMP_NEW_B10x.tsv`）のうち、corpus に本伝がある／ID-Master に既登録のものがないか。**父・祖父の名＋ニスバで corpus 見出しを逆引き**（変綴り・逆転ナサブ・索引項（ニスバ／ابن-部、D11xxx〜D13xxx 帯）・كنى 部から探す）。B87〜B94-98 の5バッチ連続で検証パスが「本伝見落とし」を最も多く捕捉した。
- (c) Pattern A の欠落・relation 化の残存、relation の向き、subtype の妥当性、#NEEDID 維持の妥当性（登録済み ID の放置がないか）、規則23（他項にのみある情報は relation のみ cert medium で補完、属性は note 留め）・規則26 の適用が過不足ないか、チャンクをまたぐ相互参照が双方向に閉合しているか。
- (d) 日付（when-custom と when の整合、精度の一致、notBefore/notAfter、ヒジュラ年の @when 混入、グレゴリオ換算）。**すべての日付を h2g.py で独立に再計算**。
- (e) 訳文（ja/en）の誤り（主語・数字・脱落・人名転写・hedge の脱落・内部ID・生アラビア語・立項連番・推測句の混入）。**ja 訳の語中 بن は「ブン」**。en が英語であること。
- (f) 幻番号・統合済み番号・汚染番号・毒 wd・空属性・ID 書式。
- (g) 校閲者メモ（REVIEW_NOTES）と XML の不一致。
- (h) 初版にあって校閲版で消えた情報のうち、消すべきでなかったもの（原文にある師・弟子・役職・出来事）。
- (i) 原文にない属性・地名（ニスバ由来 residence、学派、生年、cert="high" の捏造）が残っていないか。規則22 の 1〜6。
- (j) 連結レコード（本バッチでは校閲者報告上は該当なし）が実際に無いか、100件の原文末尾を点検し、あれば訳文・event への混入を見る。
- (k) 校閲者が出した ISSUES のうち、統一規則・repo 先例・corpus 証拠で解決できるものがないか（解決案を添える）。

担当ファイル数が多いので、ファイルごとに系統的に。校閲者の結論を鵜呑みにせず、根拠（原文）から独立に読み直すこと。

---

## あなたの役割: 機械検査（スクリプトによる全件検査） — 担当 100件すべて

python3 のスクリプトを書いて（`docs/_work/B104-108_incoming/verify/` に保存）、100件すべてに次を機械的に検査する。各項目を「点検N件中違反M件」で報告:
1. well-formed（xml.etree）。
2. REF 方式X の形（type="reference" subtype="LIMBO"・実伝由来要素（state/event/birth/death/affiliation/relation/nisbah persName）なし・note 順序 source→translation ja→translation en→reference・target が実在 AIND（corpus_index にある）か #NEEDID・ファイル名 `REF_` 接頭辞と一致）。
3. 原文 `<note type="source" xml:lang="ar">` と corpus_B104-108.json の `text` の一致（改行・空白の正規化後）。不一致はすべて列挙。
4. 日付属性（when-custom ⇔ when の対応、ヒジュラ年値が @when にないか、4桁ゼロ詰め、精度一致（年のみ→YYYY、月のみ→YYYY-MM）、notBefore/notAfter の整合）。h2g.py による再計算で主要な死亡・出生・event の西暦を検算できるものは全件検算。
5. persName name_only の世代数（≤3）、full に居住句・職名句がないか（نزيل／خادم／شيخ ～／قاضي ～ 等）。
6. respStmt（初版が orig と同一で残り、校閲 respStmt に persName `claude-b10x-review`（チャンクと一致）・date 2026-10-05、resp=校閲）。
7. ID 書式（`#`・`wd:`・`gn:` 欠落、AIND-D 5桁、TMP-P 6桁、他 TMP 5桁、passive/active と xml:id の整合）。
8. 幻 AIND（Individuals にも corpus にもない）。
9. 幻 TMP（ID-Master `docs/_work/idmaster_ext_20261005b.tsv` 未登録の非仮番号。仮番号 `TMP-x-NEW1xx-nn` は TMP_NEW_B10x.tsv に登録があること、チャンク番号がファイルの属するチャンクと一致すること）。
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
21. 規則24 の記録: FIXLOG_B10x.tsv の書式（9列・語彙が固定語彙・batch_id=B104-108）と件数。
22. 「أرخه ابن فهد」の振り分け: source note に「أرخه ابن فهد」を含む全件について、death の when-custom と Pattern A の persName ref（D09211/D05979/D03985）・cert の対応を表にして報告。
スクリプトは再実行可能な形で残し、報告に保存場所を記すこと。
