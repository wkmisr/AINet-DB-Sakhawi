# 検証依頼: corpus 分割新設項 49 件（AIND-Dxxxxx{a,b,…}）

## 対象
- XML: /home/claude/split/work/out/*.xml（49 ファイル、TEI <person>）
- 原文: /home/claude/split/work/dump_all.md（`######## AIND-ID | 12桁 | from …` 見出しの下に各項のアラビア語原文）
- ID-Master: /home/claude/split/work/idmaster_ext.tsv（列: 担当/Category/Arabic/Latin/ID/Note）
- corpus 索引: /home/claude/split/work/corpus_index.json（key=AIND-ID, value.text=原文）。補助: `python3 /home/claude/split/work/hw.py "<語>" ["<語>"...]`（見出し検索）, `python3 /home/claude/split/work/hwr.py "<regex>"`, `python3 /home/claude/split/work/h2g.py 863-11-20`（ヒジュラ→西暦、表計算暦）
- 先行バッチ精査済み XML の参考例: /home/claude/b69/work/out/*.xml

## 規約（要点）
- relation は片方向のみ。active=その subtype に当たる人（father なら父、teacher なら師、student なら弟子、son なら子、patron なら主人）、passive=本項主。
- 日付: @when-custom=ヒジュラ（0863-11-20 形式）、@when=西暦（Gregorian のみ）。年精度→西暦は開始月の年、月精度→開始月。cert は high/medium/low 三段階（明示・確実なら省略）。
- 逆算生年は「頃」と明記・cert="low"・逆算した旨を note に記す（D-12 規約）。
- Pattern A: 言及者は <event type="cultural" subtype="mention"> の persName。
- 暗記書は <event type="cultural"> の <bibl>。未登録テキストは bibl に ref なし。
- 新規発行 TMP: TMP-T-00161 التنبيه / 00162 القدوري / 00163 المنار、TMP-P-000942〜000952（各 note に記載）。これらは「未登録」で正しい（幻番号扱いしない）。
- #NEEDID は無名・未特定用。ref なし（属性省略）は「corpus 本伝なし・ID-Master 未登録」の未付与。

## 検証してほしいこと（各ファイル）
1. 原文との逐語照合: 見出し（persName full/name_only/laqab/kunyah/nisbah/shuhrah）、生没年月日・曜日・場所、関係（人物・向き・subtype）、官職、書名、出来事の抜け・誤り・過剰解釈。
2. ID 照合: relation/@active・persName/@ref・placeName/@ref・orgName/@ref・bibl/@ref・state/@ref が ID-Master の実体と一致するか（corpus 見出しで本伝が存在するのに TMP や未付与になっていないか、別人を指していないか）。特に「Xと推定→cert medium/low」と note にある箇所の妥当性。
3. 訳文（ja/en）の誤訳・脱落。
4. XML 規約違反（属性名、subtype 語彙、n 番号、well-formedness）。

## 出力形式
/home/claude/split/work/VERIFY_REPORT_split.md に、ファイルごとに「指摘（重大/軽微）→根拠（原文引用・ID-Master 行）→修正案」。問題なしのファイルは一行で「問題なし」。最後に総括（重大指摘数・軽微指摘数）。ファイルの直接編集はしないこと。
