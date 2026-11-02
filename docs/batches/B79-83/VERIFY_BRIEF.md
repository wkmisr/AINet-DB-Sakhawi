# 独立検証パス・ブリーフ（B79-83）

あなたは al-Sakhāwī『al-Ḍawʾ al-Lāmiʿ』の TEI-XML プロソポグラフィDB（AINet-DB）の**校閲結果を検証する独立検証者**です。校閲者（別のエージェント5名、チャンク B79〜B83 各20件）が作った修正版 XML 100件（実項90＋REF化10）に、校閲者自身が作り込んだ誤り・取りこぼしがないかを、原文と突合して洗い出してください。**修正はしないで、誤りの一覧だけを返してください。**

## 材料（すべて /home/claude/b79/work/ 配下。cwd をここに）
- `out/B79/`〜`out/B83/` … 校閲後 XML（検証対象）。`REF_AIND-*.xml` 10件は転送見出しの REF 化（`<note type="reference" target=…>` の転送先が正しいかを必ず相手側原文で確認）。
- `in/B79/`〜`in/B83/` … 校閲前の Gemini 初版（比較用。校閲で消えた情報のうち消すべきでなかったものがないか）。
- `corpus_100.md` … 100件の原文（AIND-ID 順）。
- `corpus_index.json` … AIND-ID → {src, dollars, text, line}（corpus 全13,968項）。`python3 -c "import json;d=json.load(open('corpus_index.json'));print(d['AIND-D05087']['text'])"` で任意の項を読める。**校閲者が付けた同定（#AIND-Dxxxxx）は、必ずこの辞書で相手側の原文を読んで裏取りすること。**
- `idmaster_ext.tsv` … ID-Master（2026-09-09 Drive 実測 7575行）＋今回新規 TMP 31行（仮番号 `TMP-x-NEWnn-mm`）を結合したもの（列: 登録者/Category/Arabic/Latin/ID/Note/修正）。`python3 search.py "<文字列>" both 8` で ID-Master と corpus を同時検索（第2引数 id / corpus / both、正規化検索）。`python3 idm.py TMP-P-000010` で ID 行を表示。`python3 hw.py "<語1>" "<語2>"` で corpus 見出し（先頭260字）の AND 検索。`python3 rgrep.py "<文字列>" [件数]` で repo 既収録 2,143件（`repo/Individuals/`）の全文検索。
- `h2g.py 886-9 874-3-15 850` … ヒジュラ→西暦（tabular Islamic、ユリウス暦）。日付付きなら曜日も出る。年のみ→年初〜年末、月のみ→月初〜月末。
- `notes_B79.md`〜`notes_B83.md` … 校閲者のメモ（判断根拠）。`pending_B79.md`〜`pending_B83.md` … 校閲者の要判断・名寄せ提案・欠番ウォッチ。
- `tmp_new_all.tsv` … 今回新規発行の TMP 31件（仮番号）。**新規発行の前に既存 AIND / ID-Master に同一実体がないかも検証対象。**
- `precheck_after.md` … 機械検疫（仮番号の書式警告と名前不一致は既知・良性）。
- `ref/` … 前バッチの完成例（AIND-D04393 実項・REF_AIND-D04342）と前回の VERIFY_REPORT.md（出力形式の参考）。
- `CHUNK_BRIEF.md` … 校閲者に渡した規約全文（頻出人物・確定ID・汚染番号・日付規約を含む）。**まずこれを読む。**

## 規約（要点。CHUNK_BRIEF.md が正）
1. 第三者言及（ذكره/أرخه/قال فيه/ترجمه/وصفه/أثنى عليه/أفادنيه/بيض له/جرده 等）は relation ではなく `<event type="cultural" subtype="mention">` + `<persName ref=言及者>`（Pattern A、一方向）。欠落も誤り。
2. relation の向き: `teacher` は active=師 / passive=伝主。`student` は active=伝主 / passive=弟子。一人称主体 = al-Sakhāwī = `wd:Q4120128`。「شيخنا」= Ibn Ḥajar = `wd:Q471116`。father/grandfather/uncle/patron は「その人物」が active、伝主が passive（伝主が叔父側なら伝主が active）。「والد X」＝伝主 active・子 passive で subtype son/daughter。
3. ابن فهد の振り分け: 「في معجمه」→ #AIND-D09211 / 没年>885 → D03985 / 871<没年≤885 → D05979 cert=medium / 没年≤871（または不明）→ D09211 cert=low。原文が النجم/التقي/العز を明示すれば優先。ابن اللبودي = #AIND-D00710、الفاسي = #AIND-D06757、ابن عزم = #AIND-D12540、الأهدل = #AIND-D02702、الطاووسي = #AIND-D00900、الولي العراقي = TMP-P-000011。
4. TMP-P 発行ルール: 名前に識別要素（ナサブ・ニスバ・ラカブ・クンヤ・職名）があれば corpus に立項がなくても TMP-P。裸名でも本項主の見出しから祖父名まで復元できる近親は復元形で TMP-P。祖父名まで復元できない父・名不詳・裸の汎用名・既存項間の曖昧は #NEEDID 維持。**登録済み ID の #NEEDID 放置は誤り**。集合汎称は person 化しない。
5. @when は西暦のみ（ヒジュラは when-custom）。年のみは年初の西暦年、月のみは月初の月、日付付きは曜日で検算。notAfter（年精度）＝年末日の西暦年。「بعد/قبل/بضع/قريب」は notBefore/notAfter 方式。「أوائل/منتصف/أواخر」は日を作らない。位脱落・曜日1日差は cert medium。
6. 原文にない属性（没地・居住地・学派・生年）を付けない。ニスバからの residence 不可。他人の職を伝主の state にしない。persName full に居住句・職名句を入れない。
7. 初版 respStmt・generated コメントは非改変。校閲スタンプ persName=claude-fable-5-1、date=2026-09-09。
8. ja/en 訳は原文と逐語で一致（主語の取り違え・数字・人名転写・内部ID・生アラビア語・立項連番・推測句の混入）。
9. 汚染番号（流用禁止）: TMP-P-000529（汎用 محمد）・000530（علي）・000490（عبد الله）・000064（أبو بكر）・000095・000374・000204（حسن）・000664（عمر）・000502/000503・000340（عبد الله البصري 汎用）・000066/087/127/632/633。ニスバ番号 TMP-N は persName type="nisbah" 専用（例外: TMP-N-05501 ابن البهلوان は shuhrah 位置の repo 前例あり）。毒 wd: Q160851（Hanafi）→ Q228986、Q191314（Hanbali）→ Q233387。校閲者が新たに wd/gn を記憶から書いていないか（ID-Master 未登録の wd/gn が属性にあれば誤り）。
10. 転送見出し（「فيمن جده …」「يأتي …」「مضى في …」「فيمن اسم أبيه …」で終わる1行見出し）は REF 方式X（type="reference" subtype="LIMBO"、実伝由来要素なし、Pattern A event なし、target 有）。転送指示のない項は名のみでも実項（二重立項なら possible_identity）。「له ذكر في …」型は実項。
11. 統制内 subtype: teacher/student/father/mother/son/daughter/brother/sister/grandfather/maternal_grandfather/uncle/siblings_child/cousin/spouse/father-in-law/son-in-law/brother-in-law/relative/patron/client/colleague/friend/rival/successor/predecessor/possible_identity/killer/other。

## やること
担当範囲の全件について、`out/` の XML と corpus 原文を並べて読み、次を点検する:
- (a) 校閲者が付けた全ての `#AIND-D…` 同定が正しいか（相手側原文で裏取り。ナサブ・没年・「الماضي/الآتي」の整合・綴り揺れ）。特に注意: D05004（義父 D02414、妻の名を D02414 から復元）／D05009 三師 D00335・D08929・D01126／D05012 弟子 D02873／D05030 父 D01329・D01456／D05031 父 D01341／D05035 兄弟 D00500／D05042 息子 D10745／D04413 الغمري = D08290（cert medium）／D05059／D05065⇄D05686 possible_identity／D05068 父 TMP-P-001047・مراد بن عثمان = D09893／D05080 父 = TMP-P-000809／D05087 父 = **D10815**（D10313 ではない）・兄 D03857・سبط شيخنا = D10471／D05088 兄 D05822／D05089 الناشري = D04864（cert medium）・祖父 TMP 新規／D05096 主人 D04915／D05097 娘 D13199 補填・息子 TMP 新規／D05100 兄 D00636／D05107 父 D02507・祖父 D00104・弟 D00095／D05109 子 D02571／D05118 主人 D07488／D05119 D06796・D08189・D06130／D05124 父 D02714／D05130 السوهائي = D09056（medium）／D05132 D03639／D05134 برقوق نائب الشام = D02179／D05136 D00688・D10928・D06001（medium）／D05145 D05111・D11070／D05150 父 D03027（medium）／D05151 甥 D10734・父 D03021／D05155 父 D03056・رئيس المؤذنين D10946（medium）／D05158 父 D10982／D05177 D03302・D00660／D05179 父 D03328／D05183 D09082／D05189 父 D03443（medium）・主人 D06289／D05194 父 D03519／D05199 D03605・D05196／D05203 兄 D03180／D05205 兄 D04461／D05223 弟 D07656／D05225 師 D05425／D05229 孫 D05228／D05233 父 D04063／D05234 D04189・D07994／D05241 D04272・D05240。REF: D04399→D04387、D05037→D05033、D05046→D04963、D05048→D05026、D05051→D05002、D05164→D05027、D05211→D05213、D05215→D05198、D05219→D05203、D05220→D05208。
- (b) 校閲者が「本伝なし」として新規 TMP を発行した31件（tmp_new_all.tsv）のうち、corpus に本伝がある／ID-Master に既登録のものがないか（逆引き・変綴り・逆転ナサブ・索引項（ニスバ／ابن-部、D11xxx〜D12xxx 帯）・كنى 部から探す）。特に「الآتي／الماضي」なのに見出し未検出とされた TMP-P-NEW79-03（محمد بن أحمد بن محمد بن عبد الحق الغمري）、NEW81-02（محمد بن حسين بن محمد بن نافع الخزاعي）、NEW82-03（بديد بن شكر）、および NEW82-02（أحمد بن عجلان）、NEW83-01〜04、機関 I-NEW81-01（المعينية بدمياط）・I-NEW82-01（المهمندارية マドラサ）・I-NEW82-02（جامع الغمري بالمحلة）、地名 L-NEW82-01・L-NEW83-01〜03、役職 O-NEW81-01/02・O-NEW83-01/02、ニスバ N-NEW83-01。
- (c) Pattern A の欠落・relation 化の残存、relation の向き、subtype の妥当性、#NEEDID 維持の妥当性（登録済み ID の放置がないか）、同一師への relation 分割。
- (d) 日付（when-custom と when の整合、曜日、notBefore/notAfter、ヒジュラ @when 混入）。
- (e) 訳文の誤り（主語・数字・脱落・人名・推測句・生アラビア語・内部 ID）。
- (f) 幻番号・統合済み番号・汚染番号・毒 wd・空属性・well-formed・初版 respStmt 非改変。
- (g) 校閲者メモ（notes）と XML の不一致。
- (h) 初版にあって校閲版で消えた情報のうち、消すべきでなかったもの（例: 原文にある師・弟子・役職・出来事）。
- (i) 原文にない属性（ニスバ由来 residence、学派、生年、cert="high" の捏造）が残っていないか。

## 出力形式
指定されたファイルに、**誤りと思われるものだけ**を、ファイルID・箇所・根拠（原文引用）・提案修正の4点で列挙してください。確信度を H/M/L で付け、誤りゼロの項目は列挙不要。最後に「点検した件数／検出件数（H/M/L）」を書いてください。ref/VERIFY_REPORT.md が前回の形式例。
