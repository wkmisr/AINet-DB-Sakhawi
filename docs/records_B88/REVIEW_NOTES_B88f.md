# REVIEW_NOTES_B88f

- 担当: チャンク B88f（`AIND-D07618`〜`AIND-D07658`、20件）／校閲者 claude-b88f-review／2026-09-24
- 実項 17 件・REF 3 件（D07625・D07633・D07652）。全20件 in-place 編集・well-formed 確認済み。新規仮TMP 16 件（`TMP_NEW_B88f.tsv`）、ISSUES 8 件（`ISSUES_B88f.md`）。
- 共通処理: 原文全文 `<note type="source" xml:lang="ar">` を translation の直前に挿入／校閲 `<respStmt>` を追加（初版 respStmt は不改変）／原文に明示のない field（الحديث）除去（規則2）／relation/@n を規約A（非親族のみ通し番号）に／ニスバ由来の placeName・residence 除去（規則22）／月精度の西暦は h2g.py で再計算し `YYYY-MM`（repo 慣行）／訳文の「ビン」→「ブン」、翻字・立項連番・訳者補足の除去。

## AIND-D07618（実項）
- 兄「الذي قبله」空 relation → #AIND-D07617。父 #AIND-D03821 を規則23（兄弟項・D02184 からの一意同定）で cert medium 追加。
- #AIND-D02184（بركات بن التقي عبد الرحمن العساسي السمنودي）と同一人物とみられるが転送指示なし → 実項維持＋possible_identity（cert high）。逆方向は §Df-1。
- 訳文の「マハンマド」「ハディースを」（補い）を是正。

## AIND-D07621（実項）
- مصافحة 連鎖の teacher relation 4件（#NEEDID×3・wd:Q9458＝預言者）を除去し cert low の cultural event に統合（話者は父。§Df-2）。biographer（المقريزي）→ Pattern A mention event（wd:Q293604、bibl عقوده=TMP-T-00122）。
- 空 father → 新規 #TMP-P-NEW88f-01。student relation の event に when-custom 0817／1414。death に原文 note。
- 訳文から立項連番「43」と誤読（「180歳まで生きたハッターブ」等）を除去し、連鎖の話者＝父の読みに修正。

## AIND-D07623（実項）
- 継父 الشمس الأمشاطي → #AIND-D06643（teacher حضر ＋ other「継父」）、義兄 المظفر محمود الأمشاطي → #AIND-D09828（brother-in-law）。無名の母・姉妹の空 relation を除去。
- 埋葬地 تربتهم → 新規 #TMP-I-NEW88f-01、『النقاية』→ 新規 #TMP-T-NEW88f-02（cert medium＝يقال）。
- state: シャーヒド（O-00050、orgName「مجلس…」除去）、ناب في القضاء → نائب الحكم（O-00096、ID-Master 正規語）。placeName القاهرة 除去。hajj に原文 desc。
- 没月 876-01 → 1471-06。訳文冒頭「マフムード」（誤名）等を是正。

## REF_AIND-D07625（REF）
- 「مضى فيمن جده محمد بن أبي بكر」→ 転送先 #AIND-D07579（الجمال بن الوجيه الأنصاري المكي、860年没）。方式X で REF 化・リネーム。

## AIND-D07626（実項）
- サハーウィーからの聴聞2件を1 relation に統合（bibl القول البديع T-00090・المسلسل T-00019 併記）。「علي」＝عليّ。
- 父「وجيه الدين」→ 新規 #TMP-P-NEW88f-02（⚠汎用名、§Df-7）。書写を cultural event、「سافر قبل التسعين」を travel event（notAfter 889＝1485）。

## AIND-D07631（実項）
- 師 الميدومي の person 位置流用 TMP-N-00163 → #TMP-P-000173（الصدر الميدومي）。学生 التقي أبو بكر القلقشندي=#AIND-D10816 維持。TMP-T-00020 の名前不一致は見かけ上（修正不要）。
- 没日 802-01-25 → 1399-10-05。

## AIND-D07632（実項）
- student event の不正値 when="after 830" → notBefore-custom 0830／1426。師 الصلاح بن أبي عمر=TMP-P-000031 維持。
- 「قيم مصارع معالج」は #NEEDID 維持（§Df-3）、「واسم جده」の欠落を textual note に。

## REF_AIND-D07633（REF）
- 「مضى فيمن جده محمد بن أبي بكر」→ 転送先 #AIND-D07581（الشمس الصبيبي المدني）。方式X。

## AIND-D07636（実項）
- teacher/father → wd:Q4664581（الزين العراقي）、brother → #AIND-D00844（الولي أبو زرعة）。「mentioned by」→ Pattern A（wd:Q471116、bibl إنبائه T-00034）。
- residence القاهرة（ニスバ）除去、マッカ行を travel event（801-07 推定・cert medium）。没月 802-02 → 1399-10。full に「الأصل」復元。英訳の父名誤り（ʿAbd al-Raḥmān）を是正。

## AIND-D07639（実項）
- bibl 位置の TMP-S-00038（الإملاء）→ desc type="field" に移設（repo 先例）。『ثلاثيات مسند أحمد』→ 新規 #TMP-T-NEW88f-01。الزين البوتيجي #NEEDID → #AIND-D03717。
- 生年 800 تقريبا → 1397・cert medium、没年 894 → 1488。暗記・イジャーザ・晩年の伝承（بلغني＝medium）を event に。訳文「マホメド」是正。

## AIND-D07642（実項）
- father → #AIND-D03883、grandfather → #AIND-D08673。ラカブ موفق الدين・通称 ابن الأوجاقي を追加。埋葬地 مقام الشافعي → 新規 #TMP-I-NEW88f-02。没月 877-11 → 1473-04。「جاز العشرين」逆算生年 857頃（cert low）。

## AIND-D07643（実項）
- 父（詩句の伝承元）→ 新規 #TMP-P-NEW88f-03（⚠汎用名）。العجلوني の TMP-N-00040 流用・統制外 subtype → #TMP-P-000941 の Pattern A（cert medium、§Df-4）。
- residence دمشق・state placeName・二重 affiliation を除去。詩句・「ويحرر」（cert low）を event に。

## AIND-D07644（実項）
- 師 → #TMP-P-000161（الجمال الحنبلي）。「recorder of name」→ Pattern A（#AIND-D03005 الزين رضوان）。
- 没年の誤符号化（when 850）→ notAfter 849＝1446・cert low。الكتبيين → 新規 #TMP-L-NEW88f-01（residence・medium）、التربة الظاهرية برقوق → 新規 #TMP-I-NEW88f-03（§Df-5）。full から職名句を除外。

## AIND-D07647（実項）
- 弟 → #AIND-D04264、父・祖父・曽祖父 → #AIND-D03903・#AIND-D04268・#AIND-D04080（ابن فخيرة 家）。前任 ابن المحيريق → 新規 #TMP-P-NEW88f-04、كاتب المماليك يوسف بن أبي الفتح → 新規 #TMP-P-NEW88f-05。
- state: شاهد الإدارة → 新規 #TMP-O-NEW88f-01、نيابة النظر → TMP-O-00148、「باسمه مباشرة」→ status（B87 §D-10）。orgName البيمارستان → TMP-I-00034、ديوان المماليك → 新規 #TMP-I-NEW88f-04。二重 affiliation・placeName 除去。

## AIND-D07648（実項）
- 子 يحيى の汚染番号 TMP-P-000596（別人）→ #AIND-D10302。叔父 → #AIND-D10257（العلم يحيى أبوكم）。父 الشمس → 新規 #TMP-P-NEW88f-06。没年 860 تقريبا → 1455・medium。誤訳「不平を…」是正。

## AIND-D07651（実項）
- 兄弟 → #AIND-D07650・#AIND-D04061、父 → #AIND-D03909（規則23・medium）。state ناظر（O-00032、قطيا L-00142、cert medium）。没年不明（兄弟の没年から821年以前と推定、note のみ）。

## REF_AIND-D07652（REF）
- 「في أبي البركات」→ 転送先 #AIND-D10614（أبو البركات بن عبد الرزاق … واسمه إسمعيل ومحمد）。方式X（§Df-8）。

## AIND-D07653（実項）
- 師 الواسطي 裸名 TMP-P-000075 → 本伝 #AIND-D01303。集団番号 TMP-P-000086「بعض الطلبة」→ event。子 → #AIND-D08832。نائب القاضي → نائب الحكم（O-00096）。没月 889-07 → 1484-08。

## AIND-D07657（実項）
- biographer ابن فهد → Pattern A（#AIND-D09211、cert low）。職・機関 → 新規 #TMP-O-NEW88f-02・#TMP-I-NEW88f-05（§Df-6）。没月 867-04 → 1463-01。

## AIND-D07658（実項）
- residence المدينة・state placeName（ニスバ由来）除去。TMP-O-00044（統合済み）→ TMP-O-00050、orgName「الحرم」=TMP-I-00120（cert medium）。learning placeName المدينة は「بها」により保持。

## precheck 対応の要約
- 要照合wd Q9458（D07621）: relation 除去（§Df-2）／連番訳混入 43（D07621）: 除去
- カテゴリ不一致 TMP-N-00163（D07631）→ TMP-P-000173／TMP-N-00040（D07643）→ TMP-P-000941／TMP-S-00038（D07639）→ field に移設
- 汚染注意 TMP-P-000596（D07648）→ #AIND-D10302
- 名前不一致（TMP-T-00090・00019・00020）: 見かけ上の不一致で実体一致、修正不要
