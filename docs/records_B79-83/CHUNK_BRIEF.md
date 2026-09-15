# B79–83 校閲ブリーフ（チャンク担当者用）

あなたは al-Sakhāwī『al-Ḍawʾ al-Lāmiʿ』（9世紀ヒジュラ暦の人物録）の TEI-XML プロソポグラフィDB（AINet-DB）の**校閲者**です。Gemini が生成した初版 XML（20件）を、原文（corpus）と ID-Master に突合して修正し、`out/<チャンク>/` に修正版を書き出してください。校閲成果は GitHub 公開DBにコミットされ引用されます。**速度より精度。「たぶん」で番号を振らない・訳を通さない。**

## 材料（すべて `/home/claude/b79/work/` 配下。cwd をここにして作業）
- `in/<チャンク>/*.xml` … 初版（読み取り専用。修正版は `out/<チャンク>/` に同名で保存。REF化した項は `REF_` を前置したファイル名で保存し、元名のファイルは out に置かない）
- `corpus_100.md` … 今回100件の原文。`corpus_index.json` … AIND-ID → {src, dollars, text, line}（corpus 全13,968項）。`python3 -c "import json;d=json.load(open('corpus_index.json'));print(d['AIND-D05068']['text'])"` で任意の項を読める。**同定した相手側（#AIND-Dxxxxx）は必ずこの辞書で原文を読んで裏取りする。**
- `idmaster_ext.tsv` … ID-Master（2026-09-09 Drive 実測 7575行。列: 登録者/Category/Arabic/Latin/ID/Note/修正。ヘッダなし）。
- `repo/Individuals/*.xml` … 既収録 2,143件（REF 134 含む）。同じ人物・機関・役職が過去にどう扱われたかの前例。`python3 rgrep.py "<文字列>" [件数]` で全文検索。
- ツール: `python3 search.py "<文字列>" both 8`（ID-Master と corpus を同時に正規化検索。第2引数 id/corpus/both）／`python3 idm.py TMP-P-000010`（ID 行表示）／`python3 hw.py "<語1>" "<語2>"`（corpus 見出し先頭260字の AND 検索＝**逆引き用**）／`python3 h2g.py 886-9 874-3-15 850`（ヒジュラ→西暦、ユリウス暦・曜日。年のみ→年初〜年末、月のみ→月初〜月末）／`python3 norm.py` は正規化関数。
- `ref/` … 前バッチの完成例 `AIND-D04393_*.xml`（実項）・`REF_AIND-D04342_*.xml`（REF 方式X）、前バッチの notes・要判断・VERIFY_REPORT（書き方の参考）。

## 出力（必須）
1. `out/<チャンク>/` に修正版 XML 20件（well-formed を `xmllint --noout` で確認）。
2. `notes_<チャンク>.md` … 1項1〜3行の校閲メモ（判断根拠：同定の決め手、原文引用、日付換算、REF転送先の根拠）。ref/notes_chunk01.md の体裁。
3. `tmp_new_<チャンク>.tsv` … 新規発行 TMP の一覧（7列 TSV: `熊倉<TAB>Category<TAB>Arabic<TAB>Latin<TAB>ID<TAB>Note<TAB>`）。**ID は仮番号** `TMP-P-NEW<チャンク番号>-01` 形式（例 `TMP-P-NEW80-03`、`TMP-L-NEW82-01`）。XML 内でも同じ仮番号を `#TMP-P-NEW80-03` の形で使う（統合担当が最後に本番号へ一括置換する）。Note には「出現: Dxxxxx(役割「原文句」)」と根拠を書く。
4. `pending_<チャンク>.md` … 要判断（Waka 裁定が要るもの）・名寄せ提案（ID-Master 登録済み TMP が既存 AIND 本伝を持つ等）・欠番ウォッチ（「الآتي/الماضي」なのに corpus 見出しが見つからない）・ID-Master 別名追記提案。
5. 最後に短い報告（実項/REF 件数、新規TMP件数、主な誤り型、要判断件数）。

## ワークフロー（この順で）
STEP0 立項確認（corpus 原文を読む。src 12桁とファイル名の一致は済）→ STEP1 転送見出しなら REF 方式X → STEP2-A 全番号の突合（TMP/wd/gn を ID-Master・repo と突合、汚染番号流用の解消、#NEEDID の解決、新規発行）→ STEP2-B 翻訳の逐語照合（ja/en）→ STEP2-C 構造是正（Pattern A、relation 向き・subtype、日付、原文にない属性の除去、欠落補填）→ セルフチェック → スタンプ。

## 規約（要点。詳細は ref/HANDOVER_20260724_v13_1.md）
1. **第三者言及は Pattern A**: ذكره/أرخه/قال فيه/ترجمه/وصفه/أثنى عليه/أفادنيه/بيض له/جرده/سماه/قال شيخنا في أنبائه 等は relation ではなく `<person>` 直下の `<event type="cultural" subtype="mention" n="k"><desc xml:lang="ar">原文句</desc><persName ref="言及者ID">名</persName>[<bibl ref="…">書名</bibl>]</event>`。一方向・逆 relation 不要。欠落も誤り。統制外 subtype（chronicler/biographer/source/described by …）は全廃。
2. **relation の向き**: `teacher` は active=師／passive=伝主。`student` は active=伝主／passive=弟子。「سمع مني/قرأ علي/أخذ عني/كتبت له/عرض علي」の一人称主体 = al-Sakhāwī = `wd:Q4120128`（teacher として active）。「شيخنا」= Ibn Ḥajar = `wd:Q471116`（「شيخنا [固有名]」は別人）。father/grandfather/uncle/patron は「その人物」が active、伝主が passive。「خالي」「عمي」は本項主が甥側。「والد X」= 伝主が father(active) で X が passive → subtype は伝主視点で `son`/`daughter`（active=伝主, passive=子）。「أخو X」= brother。`relation` の n は要素種別ごとの通し番号（1,2,3…）。desc は相手の名前のみ（根拠句は note に）。片方向で十分（鏡像不要）。同一師への relation は1本に統合（method/field は複数 desc で）。
3. **統制内 subtype**: teacher/student/father/mother/son/daughter/brother/sister/grandfather/maternal_grandfather/uncle/siblings_child/cousin/spouse/father-in-law/son-in-law/brother-in-law/relative/patron/client/colleague/friend/rival/successor/predecessor/possible_identity/killer/other。「صهر」「قريب」は relative（cert medium）。集合汎称（جماعة/إخوته/الفقراء）は person 化しない。
4. **ID の解決順**: (a) corpus に本伝があれば `#AIND-Dxxxxx`（**全ナサブ・逆転ナサブ・変綴り・ابن-部・ニスバ索引項（D11xxx〜D12xxx 帯）・兄弟項/子項/弟子項からの逆引き・「الآتي/الماضي」の指示**を尽くす。hw.py と search.py corpus）。(b) ID-Master 登録済みなら `#TMP-x-…`／`wd:Q…`／`gn:…`（**ID-Master の Arabic 列を実引きし、登録名と一致を確認**。カテゴリ一致必須＝person 位置に N/L/O 番号は禁止）。(c) どちらにもなければ新規 TMP（仮番号）。**新規発行の前に必ず corpus・ID-Master・repo で既存を確認。**
5. **TMP-P 発行ルール（Waka 2026-09-02/08）**: 名前に識別要素（ナサブ・ニスバ・ラカブ・クンヤ・職名）があれば立項がなくても TMP-P を発行。裸名でも本項主の見出しから相手のナサブが**祖父名まで**復元できる近親（父を同じくする兄弟など）は復元形で TMP-P 発行。祖父名まで復元できない父・一族ニスバのみ継承の復元形（「أحمد الجزيري الرابطي」型）は発行せず `#NEEDID` 維持。`#NEEDID` 維持は名不詳・裸の汎用名・既存項間の曖昧に限る。名不詳者の #NEEDID relation は削除しない。**登録済み ID を #NEEDID のまま放置しない**（ID-Master を必ず検索）。
6. **汚染番号（流用禁止）**: TMP-P-000529（汎用 محمد）・000530（علي）・000490（عبد الله）・000064（أبو بكر）・000095・000374（سيف）・000204（حسن）・000664（عمر＝ティムールの子）・000502/000503（إينال الأمير／その父。ただし D05068 の父 إينال については下記「確定ID」参照）・000066/087/127/632/633。ニスバ番号（TMP-N-…）は persName type="nisbah" 専用。毒 wd: Hanafi は `wd:Q228986`（Q160851 は毒）、Hanbali `wd:Q233387`（Q191314 は毒）、Shafi'i `wd:Q82245`、Maliki `wd:Q48221`。QID・gn を記憶から新規に書かない（校閲環境から Wikidata を参照できない）。ID-Master 未登録の wd/gn が初版にあれば「未確認」として pending に挙げ、ID-Master 登録済みの値か TMP に置き換える。
7. **日付**: `@when` は西暦のみ（ヒジュラは `@when-custom`、4桁ゼロ埋め「0812」「0837-11-19」）。年のみ→年初の西暦年（812→1409）、月のみ→月初の日の月（YYYY-MM）、日付付きは h2g.py で曜日検算。`notAfter`（年精度）＝ヒジュラ年末日の西暦年、`notBefore` は年初。「بعد/قبل/بضع/قريب الN」は notBefore/notAfter（-custom）方式で単一 when にしない。「أوائل/منتصف/أواخر/حدود」は日を作らない。「آخر/سلخ」＝月末日。位脱落（「سنة وتسعين」＝890）は復元年＋cert medium。逆算生年は「頃」cert low＋note 明記で可。death の `<note xml:lang="ar">` に原文句、`<note xml:lang="ja">` に換算（前例参照）。
8. **原文にない属性を付けない**: ニスバからの residence（初版で最多の誤り）、学派、没地、生年、根拠のない retirement/appointment 日、cert="high" の捏造 visit。他人の職を伝主の state にしない。「الدولة X-ية」は placeName にしない。persName full に居住句・職名句・父の述語を入れない（full は見出しの名＋ラカブ＋ニスバまで）。「立項連番」（原文行頭の裸数字）を没年や訳に混入させない。
9. **翻訳（ja/en 各ちょうど1件）**: 原文と逐語で一致させる（主語の取り違え、数字、脱落、人名転写、内部ID・生アラビア語・立項連番・推測句「（イブン・ハジャル）」等の混入排除。ただし شيخنا の（イブン・ハジャル）注記は前例どおり可）。「サハーウィー」一人称は「私（サハーウィー）」。訳を直したら resp に `翻訳校正` を追加。
10. **転送見出し（REF 方式X）**: 「فيمن جده …／مضى في …／يأتي …／صوابه／في ابن …／فيمن اسم أبيه …／يأتي بزيادة …」型の1行見出しは実項化せず、`<person … type="reference" subtype="LIMBO">`、ファイル名 `REF_` 前置、実伝由来要素（relation・event・state・affiliation・nisbah ref）を除去、`<note type="reference" target="#AIND-Dxxxxx">根拠</note>` を置く（転送先は名・父名・祖父名・ニスバの一致で一意に閉合。相手側原文を読んで確認。未受領帯でも target を書く。見つからなければ target="#NEEDID" と pending に）。Pattern A event は置かない。翻訳 ja/en は残す。ref/REF_AIND-D04342 が完成例。**判定基準はその項自身に転送指示があるかのみ**。転送指示がなく二重立項と思われるものは実項のまま双方向 possible_identity（断定=cert high、أظنه=medium）。「له ذكر في …」型は本人の本伝（実項＋subtype other）。
11. **ابن فهد の振り分け**（Pattern A の persName ref と cert）: 原文が「النجم」「التقي」「العز」「في معجم أبيه」等で明示すれば優先。「في معجمه」→ `#AIND-D09211`。没年 > 885 → `#AIND-D03985`（العز）。871 < 没年 ≤ 885 → `#AIND-D05979`（النجم）cert="medium"。没年 ≤ 871 または不明 → `#AIND-D09211`（التقي）cert="low"。**cert は event 属性で書く。**
12. **スタンプ**: 初版 `<respStmt>`（初版作成・Naoki Umetsu／Saeri Kato／Assistant 4 等）と `<!-- generated … -->` コメントは**一切改変しない**。末尾に新規 `<respStmt><resp xml:lang="ja">校閲</resp>[<resp xml:lang="ja">翻訳校正</resp>]<note xml:lang="ja">修正内容の要約</note><persName>claude-fable-5-1</persName><date when="2026-09-09"/></respStmt>` を追加。修正のない項にも `校閲` スタンプ。
13. **`<note type="source">` は入れない**（統合担当が機械挿入する）。
14. 汎用の役職・機関・地名は ID-Master 登録値を優先（例: مشيخة 汎用 = wd:Q7492880、ناظر = TMP-O-00032、نائب = TMP-O-00053、دوادار = TMP-O-00063、حاجب = TMP-O-00065、المقدم = TMP-O-00083、الخاصكية = TMP-O-00015、قائد = TMP-O-00094、خطيب = wd:Q932945、قاضي = wd:Q217029、تاجر = wd:Q215536、كاتب = TMP-O-00010、العطار = TMP-O-00012、طبيب = TMP-O-00108、شاهد = TMP-O-00050、نقيب = TMP-O-00067、وكيل = TMP-O-00060、مؤذن は search.py で確認）。書物: المنهاج = TMP-T-00065（wd:Q6806081 は別書）、القرآن = TMP-T-00095、الأربعين النووية = TMP-T-00044、القول البديع = TMP-T-00090、إنباء الغمر = TMP-T-00034、معجم ابن فهد = TMP-T-00138、صحيح البخاري = wd:Q1023470、صحيح مسلم = wd:Q886659、سنن ابن ماجه = wd:Q1187931、العمدة = TMP-T-00110、نخبة الفكر = TMP-T-00061、الشاطبية・ألفية ابن مالك 等は search.py。地名: مكة = gn:104515、القاهرة = gn:360630、المدينة = gn:109223、دمشق = gn:170654、حلب = gn:170063、المعلاة = wd:Q42004、جدة = TMP-L-00036、مؤذن = wd:Q239718、رئيس المؤذنين = TMP-O-00090、القدس = gn:281184、منى = TMP-L-00201、اليمن = TMP-L-00037、الشام = TMP-L-00002、الروم = TMP-L-00038、الهند = TMP-L-00039、المسجد الحرام = wd:Q428858、المسجد النبوي = TMP-I-00120、البيبرسية = wd:Q6400398、القطبية = TMP-I-00009、البرقوقية = TMP-I-00029、الباسطية(カイロ) = TMP-I-00021、خانقاه سعيد السعداء = TMP-I-00018、خانقاه سرياقوس = TMP-I-00022、جامع الغمري = TMP-I-00072、الشاطبية = TMP-T-00015、المهمندارية = TMP-O-00105。
15. **precheck の名前不一致「al-Muʿallā」等**（ラテン文字の記載名）は良性 → 記載名をアラビア語に直す（placeName/bibl の本文は原文のアラビア語で）。

## 頻出人物・確定ID
ابن حجر(شيخنا)=wd:Q471116／サハーウィー=wd:Q4120128／الإنباء=TMP-T-00034／ابن فهد=規約11／العز بن فهد=D03985／النجم بن فهد=D05979／التقي بن فهد=D09211／ابن اللبودي=#AIND-D00710／ابن عزم=#AIND-D12540／الطاووسي=#AIND-D00900／الأهدل=#AIND-D02702／الناشري(العفيف)=TMP-P-000694／حمزة الناشري=#AIND-D02778／ابن المنير=TMP-P-000342／التقي الفاسي=#AIND-D06757／العراقي=wd:Q4664581（الولي العراقي = TMP-P-000011）／الهيثمي=wd:Q4725309／المقريزي=wd:Q293604／العيني=wd:Q257745／الأبناسي=#AIND-D00335／الشرف المناوي=#AIND-D10313／الجلال الخجندي=#AIND-D01532／العلم البلقيني=#AIND-D03354／التقي الشمني=#AIND-D01494／ابن عرفة=#AIND-D09141／البقاعي=#AIND-D00207／ابن صديق=#AIND-D00271／الشيخ مدين=#AIND-D09892／الزين المراغي=#AIND-D10690／أبو الفرج المراغي=#AIND-D07182／الكمال بن البارزي=#AIND-D09138／السيد علي المكتب=#AIND-D04942／الزين زكريا=#AIND-D03042／ابن مزهر=#AIND-D10854／عبد الباسط ناظر الجيش=#AIND-D03484。
スルターン・アミール: برقوق=#AIND-D02178／الناصر فرج=#AIND-D06160／المؤيد شيخ=#AIND-D03345／الظاهر ططر=#AIND-D03422／برسباي=#AIND-D02168／جقمق=#AIND-D02423／إينال=#AIND-D02110／خشقدم=#AIND-D02830／قايتباي=#AIND-D06305／الأشرف شعبان=wd:Q286592／قانصوه اليحياوي=#AIND-D06293／جان بلاط=#AIND-D02388／الزيني يحيى الاستادار=#AIND-D10263／تيمور=wd:Q8462／شاه رخ=#AIND-D03298／**الأتابك إينال اليوسفي = TMP-P-001047**（ID-Master 登録済、その子 علي بن إينال = D05068＝今回対象、孫 أحمد = D01001・محمد = D08036）／**مراد بن عثمان（Murad II）**は ID-Master 未登録 → 新規 TMP-P（仮番号）で発行し pending に wd 照合依頼を書く（wd を記憶から書かない）。
メッカの家系: ابن ظهيرة／بنو فهد／بنو عجلان（حسن بن عجلان と子 علي・أبو القاسم・بركات 等は corpus に本伝あり＝hw.py で探す）／القواد（قائد=TMP-O-00094）。非スルターンの任免は relation 化せず state/event 内 note（D02116 方式）。
集合汎称・「أحد الجماعة」「الفقراء」は person 化しない。

## チャンク間の整合
同じ相手（師・言及者・地名・役職）が他チャンクにも出る可能性がある。**ID-Master／repo に既存があればそれを使う**。新規は仮番号で発行し、統合担当が重複を名寄せする（tmp_new の Arabic 列を正確に書くこと）。

## セルフチェック（提出前）
- [ ] 全ファイル well-formed、ja=1/en=1、初版 respStmt 非改変、校閲 respStmt 追加
- [ ] active/passive/ref/target/corresp に汚染番号・ニスバ番号(person位置)・毒wd・未確認wd・「#NEEDED」等の不正値がない
- [ ] #NEEDID が残るのは規約5の3類型のみ（notes に理由）
- [ ] Pattern A 化漏れなし、cert（ابن فهد）付与
- [ ] @when がすべて西暦、h2g.py で検算済み
- [ ] 原文にない residence/madhhab/生年/没地がない
- [ ] REF は方式X（実伝要素なし・target 有）
- [ ] tmp_new の仮番号と XML 内の仮番号が一致
