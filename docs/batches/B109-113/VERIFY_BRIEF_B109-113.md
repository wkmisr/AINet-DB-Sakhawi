# 独立検証パス・ブリーフ（B109-113、2026-10-10）

あなたは al-Sakhāwī『al-Ḍawʾ al-Lāmiʿ』の TEI-XML プロソポグラフィDB（AINet-DB）の**校閲結果を検証する独立検証者**です。校閲者（別のエージェント5名、チャンク B109〜B113 各20件）が作った修正版 XML 100件（実項84＋REF化16）に、校閲者自身が作り込んだ誤り・取りこぼしがないかを、原文と突合して洗い出してください。**XML・corpus・ID-Master・Individuals は一切修正しないでください**（読み取りのみ。報告ファイルだけを書く）。git 操作も禁止です。

## 作業環境
- すべて `mcp__remote-devices__device_bash`（Mac 上）で行う。毎回 `cd "$HOME/mnt/AINet-DB-Sakhawi" && ...`。呼び出しごとに新しいシェル。ファイルの読み書きは python3 / cat / sed で（クラウド側の Read/Edit/Write/Bash はこのマシンのファイルに届かない）。
- **検証対象（校閲後 XML）**: `docs/_work/B109-113_incoming/B109-113/` の100件（`REF_` 接頭辞付き11件は転送見出し）。受領チャンクとの対応は `docs/_work/B109-113_incoming/origin_folders.tsv`。
- **校閲前（Gemini 初版）**: `docs/_work/B109-113_incoming/orig/`（比較用。校閲で消えた情報のうち、消すべきでなかったものがないか）。
- **原文**: `docs/_work/B109-113_incoming/corpus_B109-113.json`（100件の本文、キー `D05956` 形式）。corpus 全体: `docs/_work/B109-113_incoming/vc/corpus_index.json`（AIND-ID → {src, dollars, text, line}）。`python3 -c "import json;d=json.load(open('docs/_work/B109-113_incoming/vc/corpus_index.json'));print(d['AIND-D05999']['text'])"` で任意の項を読める。**校閲者が付けた同定（#AIND-Dxxxxx）は、必ずこの辞書で相手側の原文を読んで裏取りすること。**
- 検索ツール（cwd=リポジトリルート）: `python3 docs/_work/B109-113_incoming/vc/hw.py "<語1>" "<語2>"`（corpus 見出し先頭260字の AND 検索）／`vc/idsearch.py "<文字列>" [件数]`（ID-Master のアラビア語・ラテン語・Note 検索）／`vc/idm.py TMP-P-000010`（ID 行表示）／`vc/rgrep.py "<文字列>" [件数]`（repo の Individuals 全文検索。サブフォルダ再帰）／`python3 docs/records/records_B79-83/tools/h2g.py 886-9 874-3-15 850`（ヒジュラ→西暦。**グレゴリオ暦（proleptic）を正とする**。`--selftest` あり）。
- ID-Master: `docs/_work/idmaster_ext_20261010.tsv`（2026-10-10 13:14 のシート実物 8,181 行。列=[登録者,Category,Arabic,Latin,ID,Note,修正]。B104-108 の78行・太田氏の追加（〜P-001427）・2026-10-10 の名寄せを含む）。新規 TMP は仮番号（`TMP-x-NEW109-nn`〜`NEW113-nn`）のまま XML にある。
- 校閲者の記録: `docs/records/records_B109-113/` の `REVIEW_NOTES_B1xx.md`・`ISSUES_B1xx.md`・`TMP_NEW_B1xx.tsv`・`FIXLOG_B1xx.tsv`、precheck: `precheck_B109-113_before.md`、規約全文: `CHUNK_BRIEF_B109-113.md`（**まずこれを読む**。統一規則1〜36・頻出確定ID・汚染番号を含む）。

## 規約の要点（CHUNK_BRIEF が正）
第三者言及は Pattern A（event cultural/mention + persName ref）／relation 向き: 師弟は active=師・passive=学生、親族・社会関係は active=相手・passive=本項主／TMP-P 発行ルールと父の3段階（祖父名復元→TMP-P、本伝→AIND、裸名→#NEEDID）／@when は西暦（グレゴリオ）のみ・精度は when-custom に合わせる、ヒジュラは when-custom／原文にない属性・地名を補わない（規則22）／規則25 原文どおり読む／規則26 同定は確実な場合のみ（通称・推定では AIND に同定せず TMP、ただし ابن فهد 振り分け規則は例外）／規則27 連結レコードは source note を実伝部分のみ＋editorial note／規則28「رأيته فيمن عرض عليه」型は本項主＝試問者／規則29「خلف أخاه/والده」は predecessor／規則30 頻出確定IDは年代確認／規則31 relation desc は相手名のみ／relation の @n は規約A（親族には付けない、非親族のみ1起点連番）／初版 respStmt は非改変、校閲 respStmt は `claude-b1xx-review`・2026-10-10／en 訳は英語／転送見出しは REF 方式X／汚染番号 TMP-P-000529・000204 等は別人流用禁止／毒 wd Q160851→Q228986、Q191314→Q233387／wd・gn は記憶から書かない。

## 本バッチの REF 16件（転送先の原文を必ず読み、転送先として正しいか確認）
B109: D05956→D05999（未受領）／D05987→D05933。B110: D05988→D05940（ブリーフ案は「ナサブで探す」、校閲者は B108 の D05940 を同定）／D05991→D05945（**父名 محمد⇄عمر の食い違い**、§D110-1）／D06013→D06025（未受領、B106 REF D05888 と同じ転送先）。B111: D06021→D05902／D06023→D05905／D06024→D05989（B110）／D06027→D05897／D06032→D05916／D06035→D05906／D06039→D05992（B110）／D06041→D05983（未受領）。B112: D06043→D05999／D06046→D05974（未受領）。B113: D06076→D06109（未受領）。**「اثنان」型 D06026・D06028 は実項（実伝由来要素なし＋editorial note）、名のみ D06000・D06069・D06081 は実項**＝妥当か確認。

## 本バッチ固有の検証点
- **校閲者が付けた AIND 同定（REVIEW_NOTES に全件。主要なもの）を相手側原文で裏取り**: B109: D05957 父 D07914・祖父 D04775／D05962 兄弟 D04791・D08970／D05964 父 D08286・祖父 D05799／D05965 父 D08298／D05968 父 D08366・祖父 D05981／D05969 師 D01089・D00271・D04440・D05934／D05972 父 D08634・師 D13094／D05973 いとこ D05028・息子 D08362／D05976 師 D07198・D01133・前任者 D02851・D08929b（**b 付き番号の実在確認**）／D05977 父 D09084・母 D13744・兄弟 D09206・D10860・母方叔父 D04166・師 D01072・D06786／D05982 息子 D08367／D05984 息子 D08369／D05985 父 D09469・祖父 D10077・親族 D00300。B110: D05998 後任 D00238・前任 D07166／D06003 弟子 D06755／D05992 息子 D08374・D10786・弟子 D08853（medium）／D06004 兄弟 D10884（brother＋predecessor）／D05989 師 D10463・D04575／D05994 親族候補 D06830（low）・D02423。B111: D06022 息子 D04164／D06029 D08290／D06030 الوانوغي D09463・القاضي عبد القادر D04166（medium、witness event）／D06036 子 D06475（転送見出し D08385 経由、父名矛盾＝§D111-1）。B112: D06050 父 D06371・兄弟 D09921／D06054 主人 D03047／D06044 D10313／D06053 師 D10690／D06070 学生 D01379・العجيسي D10261・البرزلي D11065。B113: D06079 息子 D08408・D05330・D01149／D06082 従兄弟 D10040・父 D05100／D06094 息子 D05331／D06095 師 D03763・甥 D04811・兄 D09126・息子 D08413／D06099 甥 D03822・兄弟 D10337／D06078 D06757・الأشرف D01950（medium）／D06090 兄弟 D00287（medium）／D06077 D07216（medium）。**規則26（確証なき同定は TMP）に照らして cert の付け方を点検**。逆に **D06049（父 D05327・祖父 D06051）・D06063（父 D00216）は「ナサブ一致のみ」として relation を立てず note 留め**にされている（§D112-1/-3）＝規則26「名が一致する場合は確実とみなしてよい」と照らし、立てるべきか意見を。
- **新規 TMP 49件**（P 11／L 6／I 10／O 10／T 10／N 1 程度。`TMP_NEW_B109〜113.tsv`）の本伝・既登録の見落とし（**B87〜B109-113 の6バッチ連続で検証パスが最多捕捉**）。とくに TMP-P（D05978 の父 ابن ظهيرة 家、D06063 の兄 عمر الناشري、D06088 の父 عيسى المغربل、رسلان الذهبي、أبو عبد الله المغربي、محمد النويري قاضي طرابلس）。**ID-Master の Note を本項主の AIND で grep**（`idsearch.py D05978`）。
- **名寄せ提案の根拠確認**: TMP-P-000055→D05028、000337→D00300、001262→D04575、000311→D11065、001073→D10337、000485→D06727、000811≒D06255。
- **「ذكره شيخنا في معجمه」（D05963・D05997）**: B109 はサハーウィー自身の『المعجم』に TMP-T-NEW109-01 を発行、B110 は TMP-T-00104 を充当 ＝ **チャンク間の方針割れ**。原文（主語・書名）を読み、どちらが正しいか（イブン・ハジャル『المجمع المؤسس』か）判定を。
- **「ممن سمع مني」型**（D05965・D06002・D06017・D06034・D06054・D06057・D06064・D06094）、D06010（جاور معي ولازمني في الإملاء）・D06080（قرأ علي … سمع مني المسلسل）: active=wd:Q4120128、場所は原文にあるときのみ。
- **「أرخه／ذكره ابن فهد」**（D05957・D05978・D06031・D06037・D06038・D06047・D06049・D06056・D06062・D06077・D06082・D06102）と D06011（التقي بن فهد في معجمه＝D09211）: 没年と充てた ID・cert の対応を全件点検。
- **第三者言及**: شيخنا في إنبائه（D05984・D05990・D05995・D06015・D06042・D06048・D06058・D06078・D06090・D06096・D06100）→ Q471116＋T-00034／المقريزي（D05963・D05997）／أبو السعادات البلقيني（D05958 → D08815）／المنير（D06044）／البدري（D06019 → D10718）／الزين رضوان（D06097）。
- **規則28**（D06085）・**規則29**（D06063）・**「ابن أخيه … عليه」型**（D06095・D06099、師=本項主）・**D06097 ⇄ D06116 possible_identity**（D06116 未受領）・**D06030 witness event**（先例 D01491 型）・**新 subtype 提案**（D06048 patron、D05994 funeral_attendee（§D110-7））が統制語彙に合うか。
- **長文項**（D05976・D05977・D05985・D05994・D05973・D05969・D05989・D05992・D06095・D06071・D06088）: 師・著作・職歴・旅行の取りこぼし（FN）と、relation @n・placeName（規則22）・bibl の ID 照合を重点的に。
- **ID-Master 未登録 wd/gn の新規使用**（أيج・جامع بجاية الأعظم ほか）: ISSUES に「未確認」として残っているか。記憶由来の wd/gn が付いていないか。

## 出力と記録（規則24）
指定された報告ファイルに、**誤りと思われるものだけ**を、ファイルID・箇所・根拠（原文引用）・提案修正の4点で列挙し、各項に確信度 H/M/L、`assertion_type`（persName/date/relation/placeName/affiliation/event/bibl/id_assignment/wd_ref/gn_ref/other）と `error_category`（FP=作り込み／FN=取りこぼし／substitution=値誤り）を付けること。**「違反ゼロ」の点検項目も分母つきで必ず書く**（例「毒wdの残存 0/166」）。冒頭に「点検した assertion の概数・検出数（H/M/L、FP/FN/substitution 別）」を表で。さらに機械可読の指摘一覧を `FINDINGS_<名前>.tsv`（ヘッダなし、列=`batch_id, entry_id, assertion_type, error_category, severity, origin_stage, caught_stage, resolution, description`。`batch_id`=B109-113、`origin_stage`=claude_review（校閲者が作り込んだ・見落とした誤りの場合）または gemini_draft（初版の誤りが校閲後も残っていた場合）、`caught_stage`=verify_content または verify_mech、`resolution`=open）で出す。

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
- (j) 連結レコード（本バッチでは校閲者報告上は該当なし）が実際に無いか、100件の原文末尾を点検し、あれば訳文・event への混入を見る。
- (k) 校閲者が出した ISSUES のうち、統一規則・repo 先例・corpus 証拠で解決できるものがないか（解決案を添える）。

担当ファイル数が多いので、ファイルごとに系統的に。校閲者の結論を鵜呑みにせず、根拠（原文）から独立に読み直すこと。

---

## あなたの役割: 機械検査（スクリプトによる全件検査） — 担当 100件すべて

python3 のスクリプトを書いて（`docs/_work/B109-113_incoming/verify/` に保存）、100件すべてに次を機械的に検査する。各項目を「点検N件中違反M件」で報告:
1. well-formed（xml.etree）。
2. REF 方式X の形（type="reference" subtype="LIMBO"・実伝由来要素（state/event/birth/death/affiliation/relation/nisbah persName）なし・note 順序 source→translation ja→translation en→reference・target が実在 AIND（corpus_index にある）か #NEEDID・ファイル名 `REF_` 接頭辞と一致）。
3. 原文 `<note type="source" xml:lang="ar">` と corpus_B109-113.json の `text` の一致（改行・空白の正規化後）。不一致はすべて列挙。
4. 日付属性（when-custom ⇔ when の対応、ヒジュラ年値が @when にないか、4桁ゼロ詰め、精度一致（年のみ→YYYY、月のみ→YYYY-MM）、notBefore/notAfter の整合）。h2g.py による再計算で主要な死亡・出生・event の西暦を検算できるものは全件検算。
5. persName name_only の世代数（≤3）、full に居住句・職名句がないか（نزيل／خادم／شيخ ～／قاضي ～ 等）。
6. respStmt（初版が orig と同一で残り、校閲 respStmt に persName `claude-b1xx-review`（チャンクと一致）・date 2026-10-10、resp=校閲）。
7. ID 書式（`#`・`wd:`・`gn:` 欠落、AIND-D 5桁、TMP-P 6桁、他 TMP 5桁、passive/active と xml:id の整合）。
8. 幻 AIND（Individuals にも corpus にもない）。
9. 幻 TMP（ID-Master `docs/_work/idmaster_ext_20261005b.tsv` 未登録の非仮番号。仮番号 `TMP-x-NEW1xx-nn` は TMP_NEW_B1xx.tsv に登録があること、チャンク番号がファイルの属するチャンクと一致すること）。
10. 毒 wd（Q160851／Q191314／Q35160／Q589／Q3824443／Q327129／Q12247942／Q381208／Q1164991／Q1283／Q3306083、人物位置の Q4120093 等）の属性使用、ID-Master にも repo にもない wd/gn が新規に付いていないか（付いていれば「未確認」の記録が ISSUES にあるか）。
11. 汚染 TMP の person 位置使用（TMP-P-000529／000530／000490／000064／000664／000063／000489／000352／000140／000131／000603／000204／000350／000719 など）。TMP-N の person 位置流用。カテゴリ不一致（P/N/L/I/O/T/S の位置適合: relation active/passive と persName ref は P か AIND か wd、placeName は L/gn/wd、affiliation・state は I/O/wd、bibl は T/wd）。
12. 規約A（relation/@n: 親族に @n なし、非親族は1起点の連番）。
13. affiliation と state の同一 ref 二重符号化。
14. 統制外の type/subtype（repo の `Individuals/**/*.xml` に既存の値と照合。relation subtype・event type/subtype・state type・affiliation type・note type）。
15. 仮 TMP のチャンク間重複・ID-Master との近似一致（アラビア語正規化: ا/أ/إ/آ、ة/ه、ى/ي、ال 除去、母音記号除去）、および TMP_NEW ⇔ XML の片側漏れ（XML 未使用の TSV 行／TSV 未登録の仮番号）。TSV が7列か。
16. 汎用名 TMP-P（名＋父名のみ・ニスバのみ）の TSV Note に「⚠汎用名」があるか。
17. `<desc>` に xml:lang があるか。`xml:lang="lat"` の残存がないか（"ar-Latn"）。en 訳が英語か（アラビア文字・日本語が混入していないか）。ja 訳に「ビン」（語中 بن の誤転写）・ラテン文字・内部ID・立項連番が混入していないか。placeName の ref 付与位置。
18. 規則22 機械検査: アラビア語 placeName のうち原文（source note）に現れないもの（照応 بها/فيها/به/منها/إليها/هناك/بلده/حج 由来を除く）をリストし、cert の付け方と合わせて報告。除去 note だけが残る空 residence イベントの有無。
19. relation 整合: passive/active の少なくとも一方が本項主、self-relation なし、相互 relation の矛盾、desc が相手の名前のみ、possible_identity が本バッチ内では双方向か。
20. 校閲前 orig と比べた変更の概要統計（ファイルごとの要素数の増減）を表で。極端な減少（情報の大量脱落）があれば列挙。
21. 規則24 の記録: FIXLOG_B1xx.tsv の書式（9列・語彙が固定語彙・batch_id=B109-113）と件数。
22. 「أرخه ابن فهد」の振り分け: source note に「أرخه ابن فهد」を含む全件について、death の when-custom と Pattern A の persName ref（D09211/D05979/D03985）・cert の対応を表にして報告。
スクリプトは再実行可能な形で残し、報告に保存場所を記すこと。

---

## 【2026-10-06 追記・次バッチから必須】assertion の数え方の定義（分母の固定）
バッチ間で Precision／Recall を比較できるよう、内容検証の分母（`点検 assertion 概数`）は**次の単位で機械的に数える**（検証者の裁量で増減させない。冒頭の表はこの内訳で書く）。
| assertion_type | 単位（1件＝） | 数え方 |
|---|---|---|
| persName | `<persName>` 要素1つ（type ごと: full／name_only／laqab／kunyah／shuhrah／nisbah／alias…） | 本項主の persName 要素数。relation/desc 内の相手名は数えない |
| id_assignment | 人物参照 1つ（relation の active/passive、persName/@ref、event 内 persName/@ref） | `#AIND-`／`#TMP-P-`／`wd:` を指す属性の数。#NEEDID も1件 |
| relation | `<relation>` 要素1つ | subtype・向き・cert をまとめて1件 |
| date | 日付属性1つ（birth／death／event／relation 内 event の when-custom・when・notBefore・notAfter 各1） | 属性数 |
| placeName | `<placeName>` 要素1つ | ref の有無を問わず要素数 |
| affiliation | `<affiliation>` 要素1つ | |
| event | `<event>` 要素1つ（relation 内 event も含む） | |
| state | `<state>` 要素1つ | （assertion_type は other でなく **state** を追加して使う） |
| bibl | `<bibl>` 要素1つ | |
| wd_ref／gn_ref | `wd:`／`gn:` を値に持つ属性1つ | id_assignment と重複計上しない（人物の wd は id_assignment、地名・書名・機関の wd/gn はこちら） |
| translation | translation note 1つ（ja・en 各1件） | 訳文の誤りは1 note につき最大1件で数える |
| ref_target | REF の `<note type="reference">/@target` 1つ | |
機械検査は従来どおり別集計（項目間で重複計上するため分母に合算しない）。分母は検証者が **スクリプトで数えて** 報告に内訳を載せる（`docs/_work/B109-113_incoming/verify/count_assertions.py <xml_dir> D05956-D06017` のように担当範囲を指定して実行。両内容検証者が同じスクリプトを使う（2026-10-10 作成））。`model_accuracy_log.tsv` の `n_assertions_checked` はこの合計、`notes` に内訳を書く。


## 前バッチの機械検査スクリプト
`docs/_work/B104-108_incoming/verify/`（mech_lib.py・mech_items_*.py・mech_check.py・mech_report.py）を `docs/_work/B109-113_incoming/verify/` にコピー済み。パス・日付・チャンク名・ID-Master・batch_id を B109-113 用に更新して流用してよい（連結レコード検出は一般ロジック化済み）。
