# 独立検証パス・ブリーフ（B94-98、2026-10-03）

あなたは al-Sakhāwī『al-Ḍawʾ al-Lāmiʿ』の TEI-XML プロソポグラフィDB（AINet-DB）の**校閲結果を検証する独立検証者**です。校閲者（別のエージェント5名、チャンク B94〜B98 各20件）が作った修正版 XML 100件（実項96＋REF化4）に、校閲者自身が作り込んだ誤り・取りこぼしがないかを、原文と突合して洗い出してください。**XML・corpus・ID-Master・Individuals は一切修正しないでください**（読み取りのみ。報告ファイルだけを書く）。git 操作も禁止です。

## 作業環境
- すべて `mcp__remote-devices__device_bash`（Mac 上）で行う。毎回 `cd "$HOME/mnt/AINet-DB-Sakhawi" && ...`。呼び出しごとに新しいシェル。ファイルの読み書きは python3 / cat / sed で。
- **検証対象（校閲後 XML）**: `docs/_work/B94-98_incoming/B94-98/` の100件（`REF_` 接頭辞付き4件は転送見出し）。受領チャンクとの対応は `docs/_work/B94-98_incoming/origin_folders.tsv`。
- **校閲前（Gemini 初版）**: `docs/_work/B94-98_incoming/orig/B94/B9x/`（比較用。校閲で消えた情報のうち、消すべきでなかったものがないか）。
- **原文**: `docs/_work/B94-98_incoming/corpus_B94-98.json`（100件の本文）。corpus 全体: `docs/_work/B94-98_incoming/vc/corpus_index.json`（AIND-ID → {src, dollars, text, line}）。`python3 -c "import json;d=json.load(open('docs/_work/B94-98_incoming/vc/corpus_index.json'));print(d['AIND-D05087']['text'])"` で任意の項を読める。**校閲者が付けた同定（#AIND-Dxxxxx）は、必ずこの辞書で相手側の原文を読んで裏取りすること。**
- 検索ツール（cwd=リポジトリルート）: `python3 docs/_work/B94-98_incoming/vc/hw.py "<語1>" "<語2>"`（corpus 見出し先頭260字の AND 検索）／`vc/idsearch.py "<文字列>" [件数]`（ID-Master のアラビア語・ラテン語・Note 検索）／`vc/idm.py TMP-P-000010`（ID 行表示）／`vc/rgrep.py "<文字列>" [件数]`（repo の Individuals 全文検索。サブフォルダ再帰）／`python3 docs/records/records_B79-83/tools/h2g.py 886-9 874-3-15 850`（ヒジュラ→西暦。**グレゴリオ暦（proleptic）を正とする**。`--selftest` あり）。
- ID-Master: `docs/_work/idmaster_ext_20261003.tsv`（2026-10-03 のシート実物。列=[登録者,Category,Arabic,Latin,ID,Note,修正]）。新規 TMP は仮番号（`TMP-x-NEW9n-mm`）のまま XML にある。
- 校閲者の記録: `docs/records/records_B94-98/` の `REVIEW_NOTES_B9x.md`・`ISSUES_B9x.md`・`TMP_NEW_B9x.tsv`・`FIXLOG_B9x.tsv`、precheck: `precheck_B94-98_before.md`、規約全文: `CHUNK_BRIEF_B94-98.md`（**まずこれを読む**。統一規則1〜24・頻出確定ID・汚染番号を含む）。

## 規約の要点（CHUNK_BRIEF が正）
第三者言及は Pattern A（event cultural/mention + persName ref）／relation 向き: 師弟は active=師・passive=学生、親族・社会関係は active=相手・passive=本項主／TMP-P 発行ルールと父の3段階（祖父名復元→TMP-P、本伝→AIND、裸名→#NEEDID）／@when は西暦（グレゴリオ）のみ、ヒジュラは when-custom／原文にない属性・地名を補わない（規則22）／relation の @n は規約A（親族には付けない、非親族のみ1起点連番）／初版 respStmt は非改変、校閲 respStmt は `claude-b9x-review`・2026-10-03／en 訳は英語／転送見出しは REF 方式X／汚染番号 TMP-P-000529・000530・000490・000064・000664 等は別人流用禁止／毒 wd Q160851→Q228986、Q191314→Q233387／wd・gn は記憶から書かない。

## 出力と記録（規則24）
指定された報告ファイルに、**誤りと思われるものだけ**を、ファイルID・箇所・根拠（原文引用）・提案修正の4点で列挙し、各項に確信度 H/M/L、`assertion_type`（persName/date/relation/placeName/affiliation/event/bibl/id_assignment/wd_ref/gn_ref/other）と `error_category`（FP=作り込み／FN=取りこぼし／substitution=値誤り）を付けること。**「違反ゼロ」の点検項目も分母つきで必ず書く**（例「毒wdの残存 0/166」）。冒頭に「点検した assertion の概数・検出数（H/M/L、FP/FN/substitution 別）」を表で。さらに機械可読の指摘一覧を `FINDINGS_<名前>.tsv`（ヘッダなし、列=`batch_id, entry_id, assertion_type, error_category, severity, origin_stage, caught_stage, resolution, description`。`batch_id`=B94-98、`origin_stage`=claude_review（校閲者が作り込んだ・見落とした誤りの場合）または gemini_draft（初版の誤りが校閲後も残っていた場合）、`caught_stage`=verify_content または verify_mech、`resolution`=open）で出す。


---
（以下、役割別の節。自分に割り当てられた節に従う）

## あなたの役割: 内容検証（corpus 逆引き） — 担当 （チャンク指定はプロンプト参照）

担当範囲のすべてのファイルについて、校閲後 XML と corpus 原文を並べて読み、次を点検する:
- (a) 校閲者が付けた全ての `#AIND-D…` 同定が正しいか（相手側原文で裏取り。ナサブ・没年・「الماضي/الآتي」の整合・綴り揺れ・同名異人）。REF 4件（D04743→D10179、D04858→D04888、D04881→D04840、D04930→D04933）は**転送先の原文を必ず読み**、転送先として正しいか確認（とくに D04881 は校閲者が「في ابن أحمد بن عثمان の誤植」と解して D04840 を充てている＝cert 妥当性を厳しく見る）。
- (b) 校閲者が「本伝なし」として新規 TMP を発行した件（`TMP_NEW_B9x.tsv`）のうち、corpus に本伝がある／ID-Master に既登録（篠田氏の並行追加 P-001261〜001271 等を含む）のものがないか。**父・祖父の名＋ニスバで corpus 見出しを逆引き**（変綴り・逆転ナサブ・索引項（ニスバ／ابن-部、D11xxx〜D13xxx 帯）・كنى 部から探す）。B87・B88・B89-93 とも検証パスが「本伝見落とし」を最も多く捕捉した。
- (c) Pattern A の欠落・relation 化の残存、relation の向き、subtype の妥当性、#NEEDID 維持の妥当性（登録済み ID の放置がないか）、規則23（他項にのみある情報は relation のみ cert medium で補完、属性は note 留め）の適用が過不足ないか、チャンクをまたぐ相互参照（B94 の D04744 の父 D04791 は B95、B96 の D04846 の子 D04910 は B98 など）が双方向に閉合しているか。
- (d) 日付（when-custom と when の整合、曜日、notBefore/notAfter、ヒジュラ年の @when 混入、グレゴリオ換算）。**すべての日付を h2g.py で独立に再計算**。
- (e) 訳文（ja/en）の誤り（主語・数字・脱落・人名転写・hedge の脱落・内部ID・生アラビア語・立項連番・推測句の混入）。**ja 訳の語中 بن は「ブン」**。en が英語であること。
- (f) 幻番号・統合済み番号・汚染番号・毒 wd・空属性・ID 書式。
- (g) 校閲者メモ（REVIEW_NOTES）と XML の不一致。
- (h) 初版にあって校閲版で消えた情報のうち、消すべきでなかったもの（原文にある師・弟子・役職・出来事）。
- (i) 原文にない属性・地名（ニスバ由来 residence、学派、生年、cert="high" の捏造）が残っていないか。規則22 の 1〜6。
- (j) ★連結レコード（D04807・D04814・D04886・D04900）の source note が実伝部分のみで、editorial note が付いているか。
- (k) 校閲者が出した ISSUES のうち、統一規則・repo 先例・corpus 証拠で解決できるものがないか（解決案を添える）。

担当ファイル数が多いので、ファイルごとに系統的に。校閲者の結論を鵜呑みにせず、根拠（原文）から独立に読み直すこと。

---

## あなたの役割: 機械検査（スクリプトによる全件検査） — 担当 100件すべて

python3 のスクリプトを書いて（`docs/_work/B94-98_incoming/verify/` に保存）、100件すべてに次を機械的に検査する。各項目を「点検N件中違反M件」で報告:
1. well-formed（xml.etree）。
2. REF 方式X の形（type="reference" subtype="LIMBO"・実伝由来要素（state/event/birth/death/affiliation/relation）なし・note 順序 source→translation ja→translation en→reference・target が実在 AIND か #NEEDID・ファイル名 `REF_` 接頭辞と一致）。
3. 原文 `<note type="source" xml:lang="ar">` と corpus_B94-98.json の一致（★連結4件は「最初の ★ の直前まで」で一致し、editorial note が直後にあること）。
4. 日付属性（when-custom ⇔ when の対応、ヒジュラ年値が @when にないか、4桁ゼロ詰め、notBefore/notAfter の整合）。h2g.py による再計算で主要な死亡・出生・event の西暦を検算できるものは検算。
5. persName name_only の世代数（≤3）、full に居住句・職名句がないか。
6. respStmt（初版が非改変で残り、校閲 respStmt に persName `claude-b9x-review`・date 2026-10-03、resp=校閲）。
7. ID 書式（`#`・`wd:`・`gn:` 欠落、AIND-D 5桁、TMP-P 6桁、他 TMP 5桁、passive/active と xml:id の桁数一致）。
8. 幻 AIND（Individuals にも corpus にもない）。
9. 幻 TMP（ID-Master `docs/_work/idmaster_ext_20261003.tsv` 未登録の非仮番号。仮番号 `TMP-x-NEW9n-mm` は TMP_NEW_B9x.tsv に登録があること）。
10. 毒 wd（Q160851／Q191314／Q35160／Q3824443／Q12247942／Q381208／Q1164991 等）の属性使用、ID-Master にも repo にもない wd/gn が新規に付いていないか（付いていれば「未確認」の記録が ISSUES にあるか）。
11. 汚染 TMP の person 位置使用（TMP-P-000529／000530／000490／000064／000664／000063／000489／000352／000140／000131／000603 など）。TMP-N の person 位置流用。カテゴリ不一致（P/N/L/I/O/T/S の位置適合）。
12. 規約A（relation/@n: 親族に @n なし、非親族は1起点の連番）。
13. affiliation と state の同一 ref 二重符号化。
14. 統制外の type/subtype（repo の `Individuals/**/*.xml` に既存の値と照合）。
15. 仮 TMP のチャンク間重複・ID-Master との近似一致（アラビア語正規化）、および TMP_NEW ⇔ XML の片側漏れ（XML 未使用の TSV 行／TSV 未登録の仮番号）。
16. 汎用名 TMP-P（名＋父名のみ・ニスバのみ）の TSV Note に「⚠汎用名。同名別人への流用禁止」があるか。
17. `<desc>` に xml:lang があるか。`xml:lang="lat"` の残存がないか（"ar-Latn"）。en 訳が英語か（アラビア文字・日本語が混入していないか）。placeName の ref 付与位置（child placeName、event 直下でない）。
18. 規則22 機械検査: アラビア語 placeName のうち原文（source note）に現れないもの（照応 بها/فيها/به/منها/إليها/هناك/بلده/حج 由来を除く）をリストし、cert の付け方と合わせて報告。除去 note だけが残る空 residence イベントの有無。
19. relation 整合: passive/active の少なくとも一方が本項主、self-relation なし、相互 relation（双方に father/son など）の矛盾、desc が相手の名前のみ、possible_identity が双方向か。
20. 校閲前 orig と比べた変更の概要統計（ファイルごとの要素数の増減）を表で。極端な減少（情報の大量脱落）があれば列挙。
21. 規則24 の記録: FIXLOG_B9x.tsv の書式（9列・語彙が固定語彙）と件数。
スクリプトは再実行可能な形で残し、報告に保存場所を記すこと。
