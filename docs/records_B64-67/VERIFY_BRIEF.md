# 独立検証パス・ブリーフ（B64-67）

あなたは al-Sakhāwī『al-Ḍawʾ al-Lāmiʿ』の TEI-XML プロソポグラフィDBの**校閲結果を検証する独立検証者**です。校閲者（別のエージェント）が作った修正版XML 79件に、校閲者自身が作り込んだ誤り・取りこぼしがないかを、原文と突合して洗い出してください。**修正はしないで、誤りの一覧だけを返してください。**

## 材料（すべて /tmp/b64/work/ 配下）
- `out/` … 校閲後XML 79件（検証対象）。`REF_AIND-D04026_*.xml` は転送見出しのREF化。
- `in/` … 校閲前のGemini初版（比較用）
- `corpus_index.json` … AIND-ID → {src, text} の辞書（corpus全13,821項の原文）。`python3 -c "import json;d=json.load(open('corpus_index.json'));print(d['AIND-D03886']['text'])"` で任意の項を読める。**校閲者が付けた同定（#AIND-Dxxxxx）は、必ずこの辞書で相手側の原文を読んで裏取りすること。**
- `idmaster_0902.tsv` … ID-Master（列: 登録者/Category/Arabic/Latin/ID/Note/修正）。`search.py "<文字列>" both 8` で ID-Master と corpus を同時検索できる（第2引数 id / corpus / both）。
- `h2g.py 886-9 874-3-15` … ヒジュラ→西暦（tabular Islamic）。日付付きなら曜日も出る。
- `notes_chunk01.md`〜`notes_chunk07.md` … 校閲者のメモ（判断根拠）。
- `TMP登録_B64-67.tsv` … 今回新規発行のTMP番号22件。

## 規約（要点）
1. 第三者言及（ذكره/أرخه/قال فيه/ترجمه/وصفه 等）は relation ではなく `<event type="cultural" subtype="mention">` + `<persName ref=言及者>`（Pattern A、一方向）。欠落も誤り。
2. relation の向き: `subtype="teacher"` は active=師 / passive=伝主。`subtype="student"` は active=伝主(師) / passive=弟子。「سمع مني/قرأ علي/أخذ عني」の一人称主体 = al-Sakhāwī = `wd:Q4120128`。「شيخنا」= Ibn Ḥajar = `wd:Q471116`。
3. ابن فهد の振り分け: 「في معجمه」→ #AIND-D09211 / 没年>885 → D03985 / 871<没年≤885 → D05979 cert=medium / 没年≤871 → D09211 cert=low。原文が النجم/التقي を明示すれば優先。
4. 汎用名（محمد/علي/أحمد 等）の父・兄弟で立項がないものは TMP を発行せず `#NEEDID`。集合汎称（جماعة）は person 化しない。
5. @when は西暦のみ。ヒジュラ暦は when-custom。西暦換算は tabular Islamic で月初の月。
6. 原文にない属性（没地・居住地・学派 等）を付けない。ニスバからの逆算 residence は不可。
7. 初版の respStmt は非改変。校閲スタンプ persName=claude-fable-5-1、date=2026-09-02。
8. ja/en 訳は原文と逐語で一致すること（主語の取り違え・数字・人名転写・内部IDの混入・生アラビア語の混入がないか）。
9. 統合済み/使用禁止番号: TMP-P-000233→#AIND-D08815、TMP-O-00044→TMP-O-00050、TMP-P-000696/000720→#AIND-D00900、TMP-N-00266/00108 はニスバ専用（person位置禁止）。汚染番号 TMP-P-000529（汎用 محمد）・000530（علي）・000664（ティムールの子 عمر）・000416・000204 は別人登録＝流用禁止。

## やること
79件すべてについて、`out/` のXMLと corpus 原文を並べて読み、次を点検する:
- (a) 校閲者が付けた全ての `#AIND-D…` 同定が正しいか（相手側原文で裏取り。ナサブ・没年・「الماضي/الآتي」の整合）
- (b) Pattern A の欠落・relation化の残存、relation の向き、subtype の妥当性
- (c) 日付（when-custom と when の整合、曜日）
- (d) 訳文の誤り（主語・数字・脱落・人名）
- (e) 幻番号・統合済み番号・空属性・well-formed
- (f) 校閲者メモ（notes）と XML の不一致
- (g) 初版にあって校閲版で消えた情報のうち、消すべきでなかったもの

## 出力形式
`/tmp/b64/work/VERIFY_REPORT.md` に、**誤りと思われるものだけ**を、ファイルID・箇所・根拠（原文引用）・提案修正の4点で列挙してください。確信度を H/M/L で付け、誤りゼロの項目は列挙不要。最後に「点検した件数／検出件数」を書いてください。
