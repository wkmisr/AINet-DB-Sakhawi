# REVIEW_NOTES_B112 — AIND-D06042〜D06070（20件、2026-10-10、claude-b112-review）

対象: `docs/_work/B109-113_incoming/B109-113/` の B112 分 20 ファイル（in-place）。原文は `corpus_B109-113.json` と corpus 原本で逐語照合。全件に `<note type="source">` を挿入し、校閲 `<respStmt>` を追加。日付は h2g.py で再計算。REF 2件は `REF_` にリネーム。連結レコードは本チャンクに無し（全20件の末尾を点検）。

## 実項/REF 内訳
- REF（方式X）2件: **D06043**（القلشاني . في ابن محمد → `#AIND-D05999`、未受領）、**D06046**（النجار المقري في ابن محمد بن محمد بن عبد الله → `#AIND-D05974`、未受領）
- 実項: 18件（うち名のみ D06069）

## ファイル別

### AIND-D06042 عمر القرمي ثم الحلبي
「chronicled by」relation → Ibn Ḥajar mention event（Q471116、T-00034）。没年 801（一の位のみ）cert medium、没地 مصر（「بها … في الطريق」）cert medium（§D112-7）。residence حلب・دمشق、travel مصر に原文 desc と @when。訳文の推測句「（クリミア）」除去。
（検証後訂正 2026-10-10: travel event の @when（没年の転用）を notAfter 801／1399 に（内容B L）。）

### REF_AIND-D06043 عمر القلشاني
転送先 `#AIND-D05999`（عمر بن محمد القلشاني … قاضي الجماعة بتونس、848年没）。
（検証後訂正 2026-10-10: REF に残っていた nisbah persName を除去（内容B L・機械[2]）。）

### AIND-D06044 عمر الكردي ثم المصري الأباريقي
الشرف المناوي #NEEDID → `#AIND-D10313`（871年没、年代整合。D10815 は809年没で不適）、subtype other（信奉、先例 D05812）。المنير → mention event（TMP-P-000342、§D112-4）。没地 القاهرة（原文なし）除去、埋葬地 تربة المناوي → `TMP-I-NEW112-02`。سلخ ذي القعدة 860 → 0860-11-29／1456-11-07（先例どおり29日）。水差し売りを state（`TMP-O-NEW112-05`）。

### AIND-D06045 عمر اللولوي الدمشقي الصالحي الحنبلي
毒 wd Q191314 → Q233387。「يقرئ الأبناء」の state #NEEDID → wd:Q3595924（مقرئ）。
（検証後訂正 2026-10-10: 「يقرئ الأبناء」の state ref を wd:Q3595924 → TMP-O-00245（معلم الأبناء）に（内容B L）。）

### REF_AIND-D06046 عمر النجار المقري
転送先 `#AIND-D05974`（عمر بن محمد بن محمد بن عبد الله … الحموي النجار المقرئ … نزيل مكة ويعرف فيها بالشيخ عمر النجار）。次項 D06047 の عمر النجار（851年没）は別人と note に明記。

### AIND-D06047 عمر النجار（آخر مؤذن بمنارة باب العمرة）
毒 wd Q589 → Q428858。零番号 #TMP-I-00000 ×2 → `TMP-I-NEW112-01`（منارة باب العمرة）／既登録 `#TMP-I-00208`（بيت أم المؤمنين بزقاق الحجر、§D112-5）、#TMP-O-00000 → `TMP-O-NEW112-01`。affiliation 2件（state と二重）・residence مكة・death の مكة を除去。ابن فهد → mention（D09211 low、没851）。

### AIND-D06048 عميد بن عبد الله الخراساني الحنفي قاضي تمرلنك
毒 wd Q160851 → Q228986。Ibn Ḥajar relation → mention event。تمرلنك（wd:Q8462）relation の subtype other → patron（§D112-6）。#TMP-O-00000 → wd:Q217029（汎用 قاض）。没年 805（一の位のみ）cert medium、帰還 travel（الروم TMP-L-00038）に @when。
（検証後訂正 2026-10-10: travel event の @when（没年の転用）を notAfter 805／1403 に（内容B L）。）

### AIND-D06049 عنان بن علي بن عنان بن مغامس … الحسيني
師 wd:Q4120093 → `#AIND-D09163`（ابن الجزري）。『الحصن الحصين』→ `TMP-T-NEW112-01`。learning @when の誤置（0823）→ when-custom 0823／when 1420。没年 830 の西暦 1427 → 1426。ابن فهد → mention（D09211 low）。父 D05327・祖父 D06051 は editorial note のみ（§D112-1）。
（検証後訂正 2026-10-10: 見出しナサブで特定できる父 #AIND-D05327・祖父 #AIND-D06051 の relation を立てた（規則23 の対象外、D06082 と統一。§D112-1 解決、内容B M-1）。）

### AIND-D06050 عنان بن قنيد بن مثقال القائد الحسني
父 → `#AIND-D06371`（قنيد بن مثقال … والد مسعود وعنان）、兄弟 → `#AIND-D09921`（مسعود بن قنيد）。residence مكة 除去。state نائب مكة（O-00053）・والي مكة（O-00069）は汎用番号のまま（precheck の名前不一致は見かけ上）。

### AIND-D06053 عنبر شجاع الدين العزي الطواشي
師 D10690（الزين أبو بكر المراغي、816年没）・TMP-P-000099（العلم سليمان السقا）に desc を補い、field 除去、learning @when 誤置 → 0801／1398（cert medium）。affiliation・residence المدينة 除去。state → `TMP-O-00049`、orgName → `TMP-I-00120`。
（検証後訂正 2026-10-10: 師 العلم سليمان السقا は corpus 本伝 #AIND-D03134（「本伝なし」は誤り）。TMP-P-000099 は名寄せ提案へ（内容B H-2）。）

### AIND-D06054 عنبر فتى زيرك
主人 زيرك → `#AIND-D03047`（patron）。「ممن سمع مني بمكة」規則2。shuhrah「فتى زيرك」・field・visit event 除去、@n 重複を是正。

### AIND-D06056 عودة بن مسعود بن جامع اللحياني
「biographer」relation → mention event `#AIND-D05979`（没883 → النجم بن فهد、medium）。#TMP-O-00000 → `TMP-O-NEW112-02`（شيخ وادي أبي عروة、placeName TMP-L-00154 は登録実体と一致）。「أحد الأجواد」status。没月 → 1478-04。

### AIND-D06057 عوض بن حسب الله بن مهاوش المكي التمار
persName full に「التمار بها」。職 → `TMP-O-NEW112-03`（placeName مكة cert medium、§D112-7）。「ذا ملاءة ثم افتقر」status。field・residence 除去。没月 → 1494-01。
（検証後訂正 2026-10-10: persName full から職名句「التمار بها」を除去（規則5、内容B L）。）

### AIND-D06058 عوض بن عبد الله الزاهد
「mentioned_by」→ mention event。residence の placeName مصر → جامع عمرو（wd:Q683511、先例 D04225）、affiliation reside 除去。「للناس فيه اعتقاد」status。806-09 → 1404-03、cert medium。

### AIND-D06059 عوض بن غنيم بن صلاح
TMP-O-00143（فقيه المالكية）→ `TMP-O-00255`（فقيه الزيدية）。Zaydi affiliation は先例 D05133 どおり ref なし。

### AIND-D06062 عويد بن منصور بن راجح … أحد قواد مكة
「biographer」→ mention（D09211 low）。重複 political event を death desc に統合。埋葬地 جدة（TMP-L-00036「جدة | ساحل جدة」、「بها」照応）。state → `TMP-O-00094`。没月 → 1442-06。

### AIND-D06063 عيسى بن إبراهيم بن عيسى … أبو إبراهيم الناشري
兄弟の汚染番号 TMP-P-000664 → `TMP-P-NEW112-01`、predecessor relation 追加（規則29）。affiliation 2件・death/residence/state の زبيد（補完）除去。مسجد جليجان → `TMP-I-NEW112-03`、صلاحية زبيد → `TMP-I-NEW112-04`（placeName、原文明記）。父 D00216 は note のみ（§D112-3）。訳文冒頭の未訳部分を訳出。
（検証後訂正 2026-10-10: 兄弟・前任者 عمر は corpus 本伝 #AIND-D05918（同じ مسجد خليجان のイマーム、832年没）。TMP-P-NEW112-01 は取り下げ。ナサブ上は叔父に当たるため brother は cert medium、predecessor は cert なし。父 #AIND-D00216 の father relation を追加（§D112-1・§D112-3 解決、内容B H-1・M-2）。）

### AIND-D06064 عيسى بن أحمد بن بدر الهراوي ثم القاهري الشافعي
field・residence القاهرة 除去。ニスバ由来地 هرا → `TMP-L-NEW112-01`（editorial note のみ、§D112-8）。
（検証後訂正 2026-10-10: 要素の ref に使われない TMP-L-NEW112-01（هرا）は取り下げ、地名は editorial note に記録（機械[15]、§D112-8）。）

### AIND-D06069 عيسى بن أحمد بن نعيمة
名のみ・転送指示なし → 実項のまま（原文 note・editorial note のみ）。

### AIND-D06070 عيسى بن أحمد بن يحيى أبو مهدي الغبريني المالكي قاضي تونس
学生 #NEEDID → `#AIND-D01379`（أحمد بن محمد … القلشاني、本伝「ممن أخذ عن عيسى الغبريني」。القلجاني／القلشاني は D05999 の注記どおり同一ニスバの揺れ）、TMP-N-00449 → `#AIND-D10261`（يحيى بن عبد الرحمن العجيسي、本伝「وبتونس قاضيها وعالمها أبو مهدي عيسى الغبريني … وعنهما أخذ」）。TMP-N-00550 の colleague relation → mention event `#AIND-D11065`（البرزلي）＋ bibl `TMP-T-NEW112-02`（ID-Master TMP-P-000311 は名寄せ要、§D112-2）。@n を規約Aに。residence تونس 除去。state → `TMP-O-NEW112-04`（قاضي تونس）。

## corpus で見つけた相手側本伝（主要）
| 項 | 関係 | 相手 |
|---|---|---|
| D06043（REF） | 転送先 | #AIND-D05999 |
| D06046（REF） | 転送先 | #AIND-D05974 |
| D06044 | 信奉者・埋葬者 | #AIND-D10313 |
| D06049 | 師／（父・祖父は note） | #AIND-D09163／D05327・D06051 |
| D06050 | 父／兄弟 | #AIND-D06371／#AIND-D09921 |
| D06053 | 師 | #AIND-D10690 |
| D06054 | 主人 | #AIND-D03047 |
| D06063 | （父は note） | #AIND-D00216 |
| D06070 | 学生／学生／言及者 | #AIND-D01379／#AIND-D10261／#AIND-D11065 |

## 新規仮TMP（13件、TMP_NEW_B112.tsv）
TMP-P-NEW112-01（عمر بن إبراهيم الناشري）、TMP-I-NEW112-01〜04（منارة باب العمرة／تربة الشرف المناوي／مسجد جليجان／صلاحية زبيد）、TMP-L-NEW112-01（هرا）、TMP-O-NEW112-01〜05（خادم بيت أم المؤمنين／شيخ وادي أبي عروة／التمار／قاضي تونس／بائع الأباريق）、TMP-T-NEW112-01〜02（الحصن الحصين／فتاوى البرزلي）。他チャンク（B111・B113 の TMP_NEW／ISSUES、校閲終盤時点で存在した分）と重複なし。
（検証後訂正 2026-10-10: TMP-P-NEW112-01（兄弟 عمر → #AIND-D05918）と TMP-L-NEW112-01（هرا、要素で未使用）を取り下げ。有効 11件。全体は TMP_NEW_all.tsv。）

## 自己点検（分母つき）
- well-formed: 20件中 20件 OK
- 毒wd（Q160851/Q191314/Q35160/Q589/Q3824443/Q327129/Q12247942/Q381208/Q1164991/Q1283/Q3306083/Q4120093）の属性残存: 20件中 0件（D06045・D06047・D06048・D06049 を修正済）
- 零番号（TMP-O-00000/TMP-I-00000）・汚染番号（TMP-P-000664 ほか precheck 列挙分）の属性残存: 20件中 0件
- ニスバ番号の person 位置流用: 20件中 0件（D06070 を修正済）
- #NEEDID の属性残存: 20件中 0件
- relation/@n 規約A（親族に n なし・非親族 1 起点連番）: 20件中 違反 0件
- event/@n 連番: 20件中 違反 0件
- 規則22 placeName（ニスバ・施設・職からの補完）: 20件中 違反 0件（D06047・D06050・D06053・D06057・D06063・D06064・D06070 で除去）
- 原文 note（corpus の text と完全一致）: 20件中 20件
- en 訳が英語: 20件中 20件／ja 訳冒頭の立項連番: 0件
- `xml:lang="lat"`: 0件／desc の xml:lang 欠落: 0件
- wd/gn は全て ID-Master 登録済み（新規 wd/gn なし）
- REF 2件: 実伝由来要素（nisbah 以外の relation/state/event/death）残存 0件
- cert high 以外の箇所: D06042（death medium・placeName medium・travel medium）、D06047（mention low）、D06048（death medium・travel medium）、D06049（mention low）、D06053（learning medium ×2）、D06056（mention medium）、D06057（placeName medium）、D06058（death medium）、D06062（mention low）
- FIXLOG: 89 行（うち resolution=issue 1 行）
