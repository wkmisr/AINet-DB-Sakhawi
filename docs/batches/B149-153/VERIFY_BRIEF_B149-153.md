# 独立検証パス・ブリーフ（B149-153、2026-11-03）

あなたは al-Sakhāwī『al-Ḍawʾ al-Lāmiʿ』の TEI-XML プロソポグラフィDB（AINet-DB）の**校閲結果を検証する独立検証者**です。校閲者（別のエージェント5名、チャンク B149〜B153 各20件）が作った修正版 XML 100件（実項94＋REF化6）に、校閲者自身が作り込んだ誤り・取りこぼしがないかを、原文と突合して洗い出してください。**XML・corpus・ID-Master・Individuals は一切修正しないでください**（読み取りのみ。報告ファイルだけを書く）。git 操作も禁止です。

## 作業環境
- すべて `mcp__remote-devices__device_bash`（Mac 上）で行う。毎回 `cd "$HOME/mnt/AINet-DB-Sakhawi" && ...`。呼び出しごとに新しいシェル。ファイルの読み書きは python3 / cat / sed で（クラウド側の Read/Edit/Write/Bash はこのマシンのファイルに届かない）。
- **検証対象（校閲後 XML）**: `docs/_work/B149-153_incoming/B149-153/` の100件（`REF_` 接頭辞付き6件は転送見出し）。受領チャンクとの対応は `docs/_work/B149-153_incoming/origin_folders.tsv`（ファイル名<TAB>チャンク）。
- **校閲前（Gemini 初版）**: `docs/_work/B149-153_incoming/orig/`（比較用。校閲で消えた情報のうち、消すべきでなかったものがないか）。
- **原文**: `docs/_work/B149-153_incoming/corpus_B149-153.json`（100件の本文、キー `D07996` 形式）。corpus 全体: `docs/_work/B149-153_incoming/vc/corpus_index.json`（AIND-ID → {text, dollars, line…}）。`python3 -c "import json;d=json.load(open('docs/_work/B149-153_incoming/vc/corpus_index.json'));print(d['AIND-D08128']['text'])"` で任意の項を読める。**校閲者が付けた同定（#AIND-Dxxxxx）は、必ずこの辞書で相手側の原文を読んで裏取りすること。**
- 検索ツール（cwd=リポジトリルート）: `python3 docs/_work/B149-153_incoming/vc/hw.py "<語1>" "<語2>"`（corpus 見出し先頭260字の AND 検索）／`vc/idsearch.py "<文字列>" [件数]`（ID-Master のアラビア語・ラテン語・Note 検索）／`vc/idm.py TMP-P-000010`（ID 行表示）／`vc/rgrep.py "<文字列>" [件数]`（repo の Individuals 全文検索。サブフォルダ再帰）／`python3 docs/_work/B149-153_incoming/vc/h2g.py 886-9 874-3-15 850`（ヒジュラ→西暦。**グレゴリオ暦（proleptic）を正とする**。`--selftest` あり）。
- ID-Master: `docs/_work/idmaster_ext_20261103.tsv`（2026-11-03 に Drive から再取得したシート実物 8,625 行（ヘッダ込み）。列=[登録者,Category,Arabic,Latin,ID,Note,修正]）。新規 TMP は仮番号（`TMP-x-NEW149-nn`〜`NEW153-nn`）のまま XML にある。典拠台帳: `python3 docs/authority/lookup.py Q…`（wd/gn の中身、ネット不要）。
- 校閲者の記録: `docs/batches/B149-153/` の `REVIEW_NOTES_B1xx.md`・`ISSUES_B1xx.md`・`TMP_NEW_B1xx.tsv`・`FIXLOG_B1xx.tsv`（B149〜B153）、precheck: `precheck_B149-153_before.md`、規約全文: `CHUNK_BRIEF_B149-153.md`（**まずこれを読む**。統一規則1〜59・頻出確定ID・汚染番号を含む）。

## 規約の要点（CHUNK_BRIEF が正）
第三者言及は Pattern A（event cultural/mention + persName ref）／relation 向き: 師弟は active=師・passive=学生、親族・社会関係は active=相手・passive=本項主／TMP-P 発行ルールと父は必ず relation（本伝→AIND、祖父名復元→TMP-P、裸名→#NEEDID の father relation を必ず立てる＝規則3 改訂）／@when は西暦（グレゴリオ）のみ・精度は when-custom に合わせる、ヒジュラは when-custom／原文にない属性・地名を補わない（規則22）／規則25 原文どおり読む／規則26 同定は確実な場合のみ（通称・推定では AIND に同定せず TMP、ただし ابن فهد 振り分け規則は例外）／規則27 連結レコード／規則28「رأيته فيمن عرض عليه」「كتب بالشهادة」型は本項主＝行為者／規則29「خلف أخاه/والده」は predecessor／規則30 頻出確定IDは年代確認／規則31 relation desc は相手名のみ／規則37 本項主の見出しナサブで特定できる父祖は AIND で relation／規則38 本伝探索はナサブ1段ずらし・女性部・repo 既存使用まで／relation の @n は規約A（親族には付けない、非親族のみ1起点連番）／初版 respStmt は非改変、校閲 respStmt は `claude-b1xx-review`・2026-11-03／en 訳は英語／転送見出しは REF 方式X／汚染番号 TMP-P-000529・000530・000064・000664 等は別人流用禁止／毒 wd Q160851→Q228986、Q191314→Q233387／wd・gn は記憶から書かない。

## 本バッチの REF（転送先の原文を必ず読み、転送先として正しいか確認）
B150: D08121→D08574（「ويأتي فيمن جده محمد بن عمر بن عيسى」、ابن القطان。合同索引 D12646 は不使用）／**D08127→D08128（第2候補 D08129 を editorial note、§D150-1。両者とも「محمد بن علي بن عبيد」で決め手なし）**／D08130→D08132（「يأتي بعد واحد」、معجم の見出し形で一致）。B151: D08140→D10927（「في الكنى」）。B152: D08177→D08171（「مضى فيمن جده محمد بن محمد بن مسلم」、見出しに البالسي なし＝本文で裏取り）。B153: D10041→D10048（D10047 は別人）。
**実項として扱われたもの**: D08139「… السكري أبوه . كذلك」（「كذلك」＝直前と同じく سمع مني）／D08094（「ينظر」型、D08601 と possible_identity low）／D10013⇄D10022（「يحرر」型、possible_identity low）／兄弟型 D08114（←D08113）・D08165（←D08164）・D08169（←D08168）・D10020（المؤيد أحمد の異母兄弟、父 D02110）／D10002・D10003（ملج×2）・D10004・D10005（ممجق×2）。

## 本バッチ固有の検証点
- **校閲者が付けた AIND 同定を相手側原文で裏取り**（全件は REVIEW_NOTES_B149〜B153。主要なもの）: B149: D07996 孫 D04275 medium（父「الماضي أبوه」は corpus に見出しなし＝TMP-P、§D149-1）／D08061 العيني D09832・البساطي D06729／D08062 子 D10083／D08064 兄 D01014・子 D11088・孫 D08478／D08071 親族 D07832 medium／D08074 学生 D08670／D08081 子 D05478・兄弟 D02951／D08082 父 D05161・母 D13639・兄弟 D01020／D08085 父 D05170・子 D06132／D08086 父 D05172・أم هانئ D13827・ابن الفوي D08590／D08090 従兄弟 D05788・D08796／D08091 従兄弟 D03752。B150: D08094 父 D05185・D08601 low／D08096 يشبك الفقيه D10358／D08099 父 D05200／D08102 兄 D03692・学生 D07563／D08106 師 D09468・جعفر D02414 medium／D08114 兄 D08113・父 D05240・الفرسيسي D07360／D08124 子 D01416／D08131 子 D08932／D08133 父 D05285。B151: D08150 父 D05330・叔父 D08408・祖父 D06079／D08151 D07009（brother-in-law）・異父姉妹 D13072・D13063・継父 D00254・D07940／D08152 父 D05335・D07144 medium／D08155 子 D08935・D05960／D08156 祖父 D06650（父候補 D05367、§D151-2）／D08159 父 D05527・兄 D00195・D03922／D08165 父 D05545・母 D13747 medium／D08166 父 D05546・祖父 D08766・兄弟 D01065・D10765・**子 D08953・D08952（「وجدهم مع ولدي هذا المحمدين」の読み、§D151-4）**／D08167 حذيفة D06743・ابن زغدان D06861（patron）・サハーウィーの息子 D01348（§D151-5）／D08168・D08169 父 D05550・祖父 D08912／D08172 子 D08956・TMP-L-00344 medium／D08160⇄D05971（§D151-3）。B152: D08181 父 D05614・子 D08957／D10002 أزبك＝D01869 son-in-law low（§D152-1、矛盾あり）／D10003 後任 D03257 medium／D10005 تغرى برمش D02275・D06312 possible_identity／D10006 母方祖父 D03180／D10008 兄弟 D04060・D04316／D10011 父 D04913／D10012 D05226・D04873／D10017 patron D02560／**D10019 父 D10359（ブリーフの「別人」は誤り）・母 D13854 medium**／D10020 父 D02110・兄弟 D00563。B153: D10022 D04266 medium／D10027 父 D02471／D10029 父 D06194／D10035 父 D07156・祖父 D02180・兄 D10184／D10036 D03481／D10037 兄弟 D10639／D10039 子 D09459・D03816・patron D03484／D10040 父 D00636・子 D09461・従兄弟 D06082・師8名／D10042 子 D01660・D04362・D03455・D05983。**規則23・26・37・57 に照らして cert の付け方を点検**。
- **新規 TMP（TMP_NEW_B149〜153.tsv、計43件）の本伝・既登録の見落とし**（14バッチ連続で検証パスが最多捕捉）。とくに TMP-P: D07996 父・D08062 父・D08086 兄弟 عبد القادر・D08090 父・D08091 父（B149）／D08102 父（طحان）・D08106 父・師 النجار・D08114 母・المحالبي・D08134 祖父 الصاحب شهاب الدين（B150）／D08139 父 السكري・D08155 父・叔父 عمر・D08172 父（B151）／D10000 父 راجح・عبيد الكبير الحضرمي・ناجي بن بسر（B152）／D10037 父ほか（B153）。**名の1語＋ニスバ・「ويعرف بـX」・ニスバ索引（D11xxx〜D12xxx）・クンヤ部・ラカブ部・女性部・点の揺れ・ラカブを除いた名の連なりで引き直す**。TMP-L・TMP-I・TMP-O・TMP-T（شرح الشواهد・شرح البخاري・المجالسة・السيرة النبوية للدمياطي ほか）は ID-Master の既登録（表記違い）を grep。**チャンク間で同一対象の重複発行がないか**。
- **名寄せ・同定提案（ISSUES）の下限（規則57）**: §D151-3（D08160⇄D05971）・§D151-5（TMP-P-000549→D01348）・§D153-5（TMP-P-000329→D01660）・§D152-1 ほか。
- **父 relation（規則3）**: 全実項に father relation があるか。汚染番号 TMP-P-000530・000529・000664・000416・000489・000063 が残っていないか。
- **「ممن سمع مني」型・قرأ علي・حضر إلي・من حفظي**: 向き（active=wd:Q4120128）、場所、年。D10040「أجاز لي」（本項主が師）。D10006「سمع بقراءتي」（サハーウィーとの relation を立てていないか）。D08167「كتبت عنه … مناما」。D08076・D08086「تردد لي／حضر عندي」の扱いのチャンク間の揃い。
- **「أرخه ابن فهد」振り分け（規則43・58、cert は event 側）**: D08063・D08082・D08085・D08131・D10016・D10017・D10018（「أرخهم ثلاثتهم」）・D10023・D10028・D10030、学生としての D08091・D10038・D10031。
- **「仕えた」型 patron（規則56）と主人でない君主（規則53）**: D08119・D08061・D10016・D10017・D10028・D10039・主人ニスバ（D10003・D10004・D10005・D10025）／D10005「عمله الظاهر جقمق」・D10012。
- **日付**: D08061・D10032 の تقريبا／حدود、D08074・D08093 の بعيد、D08145・D08151 の بضع、D08079・D10022・D08156（没年を作っていないか）、D10005 両説、D10019・D10035・D10042 の曜日、D10031「في عشر السبعين」と生年の矛盾、D08168・D08169 嬰児、D08181・D10038・D10039 の欠字。**全日付を h2g.py で独立に再計算**（年精度 notAfter は year end）。校閲者は初版の誤り（D08145・D08165・D08166）を直したと報告している＝直った値も検算。
- **規則22**: placeName の除去しすぎ・残しすぎ。D08108「بالثغر」→アレクサンドリア gn:361058 cert medium（§D150-2：番号が ID-Master／repo にあるか）。D08129「مات بها」。ニスバの由来説明（D08124）。
- **既存 repo ファイルの不具合（校閲者報告、統合時に是正予定）**: D01024 brother relation の active に # 欠落、D01014 の placeName が TMP-L-00010（登録=إب）。他にもあれば列挙。
- **規則31（desc に続柄句・職名を残さない）と規則54（初版 respStmt 非改変）**を全件で。
- **ISSUES（B149 12／B150 8／B151 9／B152 9／B153 5）のうち、統一規則・repo 先例・corpus 証拠で解決できるもの**に解決案を添える。
- **ID-Master 未登録 wd/gn の新規使用**がないか（校閲者は記憶から書かない方針）。


## 出力と記録（規則24）
指定された報告ファイルに、**誤りと思われるものだけ**を、ファイルID・箇所・根拠（原文引用）・提案修正の4点で列挙し、各項に確信度 H/M/L、`assertion_type`（persName/date/relation/placeName/affiliation/event/state/bibl/id_assignment/wd_ref/gn_ref/translation/ref_target/other）と `error_category`（FP=作り込み／FN=取りこぼし／substitution=値誤り）を付けること。**「違反ゼロ」の点検項目も分母つきで必ず書く**。冒頭に「点検した assertion の概数・検出数（H/M/L、FP/FN/substitution 別）」を表で。さらに機械可読の指摘一覧を `FINDINGS_<名前>.tsv`（ヘッダなし、列=`batch_id, entry_id, assertion_type, error_category, severity, origin_stage, caught_stage, resolution, description`。`batch_id`=B149-153、`origin_stage`=claude_review（校閲者が作り込んだ・見落とした誤りの場合）または gemini_draft（初版の誤りが校閲後も残っていた場合）、`caught_stage`=verify_content または verify_mech、`resolution`=open）で出す。

---
（以下、役割別の節。自分に割り当てられた節に従う）

## あなたの役割: 内容検証（corpus 逆引き） — 担当 （チャンク指定はプロンプト参照）

担当範囲のすべてのファイルについて、校閲後 XML と corpus 原文を並べて読み、次を点検する:
- (a) 校閲者が付けた全ての `#AIND-D…` 同定が正しいか（相手側原文で裏取り。ナサブ・没年・「الماضي/الآتي」の整合・綴り揺れ・同名異人）。REF は**転送先の原文を必ず読み**、転送先として正しいか確認。
- (b) 校閲者が「本伝なし」として新規 TMP を発行した件（`TMP_NEW_B1xx.tsv`）のうち、corpus に本伝がある／ID-Master に既登録のものがないか。**父・祖父の名＋ニスバで corpus 見出しを逆引き**（変綴り・逆転ナサブ・索引項（ニスバ／ابن-部、D11xxx〜D13xxx 帯）・كنى 部・女性部から探す）。
- (c) Pattern A の欠落・relation 化の残存、relation の向き、subtype の妥当性、#NEEDID 維持の妥当性（登録済み ID の放置がないか）、規則23・26・37 の適用が過不足ないか、チャンクをまたぐ相互参照が双方向に閉合しているか（D08168⇄D08169 兄弟、D10020 は D10019 の兄弟ではなく المؤيد أحمد D00563 の兄弟（D10019 の母方の叔父）、D08094⇄D08601、D10013⇄D10022、D08127→D08128／D08129）。
- (d) 日付（when-custom と when の整合、精度の一致、notBefore/notAfter、ヒジュラ年の @when 混入、グレゴリオ換算）。**すべての日付を h2g.py で独立に再計算**。
- (e) 訳文（ja/en）の誤り（主語・数字・脱落・人名転写・hedge の脱落・内部ID・生アラビア語・立項連番・推測句の混入）。**ja 訳の語中 بن は「ブン」**。en が英語であること。欠字・途切れ（D08181「مات .」・D10038「مات في ...」・D10039「وكان ... مات ...」）を訳で補っていないか。
- (f) 幻番号・統合済み番号・汚染番号・毒 wd・空属性・ID 書式。
- (g) 校閲者メモ（REVIEW_NOTES）と XML の不一致。
- (h) 初版にあって校閲版で消えた情報のうち、消すべきでなかったもの（原文にある師・弟子・役職・出来事）。
- (i) 原文にない属性・地名（ニスバ由来 residence、学派、生年、cert="high" の捏造）が残っていないか。規則22 の 1〜6。
- (j) 連結レコード（校閲者報告上は該当なし）が実際に無いか、担当範囲の原文末尾を点検し、あれば訳文・event への混入を見る。
- (k) 校閲者が出した ISSUES のうち、統一規則・repo 先例・corpus 証拠で解決できるものがないか（解決案を添える）。

担当ファイル数が多いので、ファイルごとに系統的に。校閲者の結論を鵜呑みにせず、根拠（原文）から独立に読み直すこと。分母は `python3 docs/_work/B149-153_incoming/verify/count_assertions.py docs/_work/B149-153_incoming/B149-153 D07996-D08172` のように担当範囲を指定して機械計数し、報告冒頭の表に内訳を載せる。

---

## あなたの役割: 機械検査（スクリプトによる全件検査） — 担当 100件すべて

`docs/_work/B149-153_incoming/verify/` に前バッチの機械検査スクリプト（mech_lib.py・mech_items_a〜e.py・mech_check.py・mech_report.py・count_assertions.py。パス・ID-Master・batch_id・チャンク名・校閲日は**オーケストレーターが B149-153／idmaster_ext_20261103 にパス置換済み（日付・respStmt 名・固有ハードコードは未置換）**。項目23〜26 と mech_items_h.py は B129-133 で新設した検査＝前バッチ（B144-148）以前の固有ハードコード（mech_items_a の EXPREF・ORTHO_DEF・REALS、mech_items_d の SM_LIST・DIRCHK・19d・D02805、mech_items_i の DEXP ほか、mech_check の POISON 追記・汚染表、mech_items_g 11b）は本バッチ用に差し替えること。本バッチ用の個別点検は mech_items_l.py を新設してよい（mech_items_k.py は B144-148 固有。汎用部だけ残す））をコピーしてある。日付（2026-11-03）・respStmt 名（claude-b149〜b153-review）・前バッチ固有のハードコード（「اثنان」型 D06253、REF 期待転送先、FORCE_CONCAT、幻番号リスト、毒 wd リスト、汚染番号リスト）を本バッチ用に見直してから実行し、100件すべてに次を機械的に検査する。各項目を「点検N件中違反M件」で報告:
1. well-formed（xml.etree）。
2. REF 方式X の形（type="reference" subtype="LIMBO"・実伝由来要素なし・note 順序 source→translation ja→translation en→reference・target が実在 AIND（corpus_index にある）か #NEEDID・ファイル名 `REF_` 接頭辞と一致）。6件。
3. 原文 `<note type="source" xml:lang="ar">` と corpus_B149-153.json の `text` の一致（改行・空白の正規化後）。不一致はすべて列挙。
4. 日付属性（when-custom ⇔ when の対応、ヒジュラ年値が @when にないか、4桁ゼロ詰め、精度一致、notBefore/notAfter の整合）。h2g.py による再計算で全件検算。
5. persName name_only の世代数（≤3）、full に居住句・職名句がないか。
6. respStmt（初版が orig と同一で残り、校閲 respStmt に persName `claude-b149〜b153-review`（チャンクと一致）・date 2026-11-03、resp=校閲）。
7. ID 書式（`#`・`wd:`・`gn:` 欠落、AIND-D 5桁（英字接尾辞 D00544a は許容）、TMP-P 6桁、他 TMP 5桁、passive/active と xml:id の整合）。
8. 幻 AIND（Individuals にも corpus にもない）。
9. 幻 TMP（ID-Master `idmaster_ext_20261103.tsv` 未登録の非仮番号。仮番号 `TMP-x-NEW149〜153-nn` は TMP_NEW_B1xx.tsv に登録があること、チャンク番号がファイルの属するチャンクと一致すること）。
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
21. 規則24 の記録: FIXLOG_B1xx.tsv の書式（9列・固定語彙・batch_id=B149-153）と件数。
22. 「أرخه ابن فهد」の振り分け: source note に「أرخه ابن فهد」「ذكره (التقي) بن فهد」を含む全件について、death の when-custom と Pattern A の persName ref（D09211/D05979/D03985）・cert の対応を表にして報告。
結果は `mech_results.json`、報告は `VERIFY_REPORT_mech.md`、指摘一覧は `FINDINGS_mech.tsv`（いずれも `docs/batches/B149-153/` に。スクリプトは `verify/` に再実行可能な形で残し、報告に保存場所を記すこと）。さらに `count_assertions.py docs/_work/B149-153_incoming/B149-153` を全件で実行し、assertion 総数と内訳を報告に載せる。

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
