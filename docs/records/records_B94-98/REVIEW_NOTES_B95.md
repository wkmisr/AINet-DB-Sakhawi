# REVIEW_NOTES_B95 — AIND-D04784〜AIND-D04827（20件、2026-10-03、claude-b95-review）

対象: `docs/_work/B94-98_incoming/B94-98/` のうち origin_folders.tsv で B95 と記された20件（عبد الوهاب 部後半〜عبيد）。原文は corpus_B94-98.json と corpus 原本（`0__DawForAIND_renumbered_B54_split20260905.txt`）で逐語照合。ID は `idmaster_ext_20261003.tsv` で照合。日付は h2g.py（--selftest PASS）で独立再計算（グレゴリオ暦）。全 20 件 well-formed 確認済み（ElementTree）。

## 総括
- 実項 20 件／REF 0 件。REF 候補 D04827 は転送定型の無い訂正注記と判断し実項（二重立項型、#AIND-D04773 へ possible_identity cert medium）→ ISSUES §D95-1。
- 新規仮TMP 5 件（P×2・L×3）→ `TMP_NEW_B95.tsv`。
- ISSUES 8 件 → `ISSUES_B95.md`。
- FIXLOG 71 件 → `FIXLOG_B95.tsv`（H 9／M 28／L 34。FP 15／FN 23／substitution 33）。
- 共通処理: 全件に `<note type="source" xml:lang="ar">` を corpus から付与（★連結 2 件 D04807・D04814 は実伝部分のみ＋editorial note）、「أرخه ابن فهد／وصفه／قاله لي」型を Pattern A（cultural/mention）へ、統制外 subtype（employer／chronicler／chronological grouping／jāwara）を是正、relation/@n を規約A、月・日精度の @when を精密化、校閲 respStmt（claude-b95-review、2026-10-03）を追加。初版 respStmt は不変。立項連番の訳文混入は本チャンクでは無し。

## ファイル別

### AIND-D04784（عبد الوهاب بن عمر بن محمد التاج الزرعي ثم القاهري الحنفي）
- 毒wd Q160851 → Q228986。ニスバ由来 residence（القاهرة）削除。
- ابن الأشقر → **#AIND-D07940**（المحب بن الأشقر كاتب السر、cert medium →§D95-3）。「employer」→ patron（イブン・ハジャル）。ジャクマク patron。規約A（brother に n なし、非親族 1〜3）。
- نقيب شيخنا → state office #TMP-O-00067＋persName wd:Q471116。没年「قريب الخمسين أو بعدها بقليل」＝when-custom 850・cert low・@when 1446。兄弟 إبراهيم は本伝未検出で #NEEDID。

### AIND-D04785（عبد الوهاب بن محمد بن إبراهيم بن أبي بكر تاج الدين الخليلي الموقت）
- 息子 عبد العزيز: 流用 #TMP-P-000813（الكازروني の息子＝別人）→ **#AIND-D03977**（ナサブ5代・ابن الموقت 一致）。「فيما قاله لي ولده」を Pattern A。874＝1469 検証。

### AIND-D04791（عبد الوهاب بن المحب محمد بن النور علي بن يوسف التاج الزرندي المدني الشافعي）
- 汚染番号 #TMP-P-000664 → **#AIND-D05962**（عمر … أخو عبد الوهاب ومحمد）、#TMP-P-000529 → **#AIND-D08970**（محمد … البهاء أبو البقاء … أخو عمر الماضي）。
- 父 المحب محمد → TMP-P-NEW95-01（→§D95-2）。規則23で子4名（D03925・D04744・D07920・D09949）を son cert medium。ニスバ由来 residence 削除。訳の「ハディースを」除去。

### AIND-D04804（عبد الوهاب تاج الدين الدمشقي ثم القاهري خليفة المقام الأحمدي بطنتدا）
- 息子 سالم → **#AIND-D03061**（相手側で父＝D04804 と同定済み）。ニスバ由来 residence ×2 と勤務地由来 residence（طنتدا）削除。state と重複する affiliation 削除（規則8）。866-06 → @when 1462-03。「بها／هناك」は照応で保持。

### AIND-D04805（عبد الوهاب اليمني الزبيدي ويعرف بالحربي）
- chronicler → Pattern A（D09211 cert low）。shuhrah のみ（重複 nisbah 除去）。854-01 → 1450-02。綴り説明の訳を修正。

### AIND-D04806（عبد الوهاب فخر الدين رأس الرافضة）
- 865 → @when **1460**（初版 1461 誤り）。「رأس الرافضة」を status state。

### AIND-D04807（عبدون بن عبد الوهاب بن أحمد الزين الطهويهي الأزهري）★連結1本
- 規則2型。editorial note（『عبيد الله بن بايزيد . يأتي في التحتانية من الآباء …』＝転送先 D04813）。affiliation الأزهر は repo 先例（D04308・D04373）に従い保持。

### AIND-D04812（عبيد الله بن محمود الشاشي）
- 父 محمود: 流用 #TMP-P-000760 → #NEEDID。統制外「chronological grouping」（يعقوب）削除。
- **相手側本伝 #AIND-D05559**（「لزم صحبة القطب عبيد الله بن محمود الشاشي أربع سنين … وكتب إلي بترجمة آخر شيوخه وبكائنة موت السلطان يعقوب」）を発見 → student relation（active=D04812）＋Pattern A（伝記筆者）cert medium（→§D95-5）。没日 notBefore/notAfter 895-03-30／04-01＝1490-03-02／03。文字化け修正。

### AIND-D04813（عبيد الله بن بايزيد بن محمود الجلال السمرقندي）
- chronicler → Pattern A（D09211 cert low、bibl ذيله＝先例 D04278）。祖父 #TMP-P-000760 → #NEEDID。844-06 → 1440-11。

### AIND-D04814（عبيد الله بن يوسف التبريزي نزيل القاهرة）★連結1本
- العز عبد السلام البغدادي → **#AIND-D03922**（先例 D03853）。「وصفه شيخنا بـ…」Pattern A 追加。n 重複是正。editorial note（『عبيد الله الأردبيلي . في ابن عوض .』）。ja 冒頭のアラビア語混入修正。

### AIND-D04815（عبيد الله المنزلي المالكي المولى الأسود）
- 根拠のない teacher relation（イブン・ハジャル）削除 → 「لقيته بمجلس شيخنا」を meeting event。student（أنشد）の placeName と visit event 削除（地名なし）。المولى الأسود → status。生年 813 تقريبا cert medium。詩は表面義で訳し掛詞は editorial note（→§D95-7）。

### AIND-D04816（عبيد بن إبراهيم الزعفراني المقدم）
- 空の mother relation 削除。息子 بركات الحريري → TMP-P-NEW95-02。الكداشين → TMP-L-NEW95-01。المقدم → state office #TMP-O-00083。891-02-27＝1486-03-13（土）。

### AIND-D04819（عبيد بن علي بن عبيد الزين التميمي الحنبلي）
- 毒wd Q191314 → Q233387。規則2型（field 除去・重複 study event 削除）。

### AIND-D04820（عبيد بن عمر بن محمد القرشي）
- 息子 عبد الرحمن → **#AIND-D03677**（相手側「الآتي أبوه وبه يعرف」。父のラカブ الزين・クンヤ أبو عمر は note 留め）。
- الزاهد #NEEDID cert medium／ابن النقاش TMP-P-000765 cert low（→§D95-4）。ニスバ由来 residence 削除し「نسبة للقرشية من الغربية」を other event（TMP-L-NEW95-02）。state واعظ の placeName 除去。逆算生年 ≤767 cert low。867-03 → 1462-12。

### AIND-D04822（عبيد بن يوسف بن حليمة）
- 874-11 → @when **1470-05**（初版 1469 誤り）。父 relation 追加。name_only 3世代。

### AIND-D04823（عبيد بن نجم الدين بن شهاب الدين السمرقندي القاضي）
- 父 relation（#NEEDID）追加。850＝1446 検証。

### AIND-D04824（عبيد الدمياطي زوج البرلسية أحد المدولبين）
- قبور الشهداء → TMP-L-NEW95-03。residence の مكة・jāwara 除去（規則20）。hajj の年除去。المدولبين → #TMP-O-00209。訳の推測句除去（→§D95-6）。

### AIND-D04825（عبيد الفيخراني）
- other relation → Pattern A（D09211 cert low）。「في حدود سنة أربعين」cert medium、840＝1436。

### AIND-D04826（عبيد التفلي）
- 854-07 → 1450-08。「كان مذكورا بالخير」を status state。訳の西暦補足除去。

### AIND-D04827（عبيد ويدعى عبد الغني بن كاتب الجيش الفخر بن الجيعان）
- 実項維持（訂正注記）。possible_identity → **#AIND-D04773**（cert medium）。父 → **#AIND-D04060**（الفخر عبد الغني بن شاكر ابن الجيعان كاتب الجيش、cert medium）。訂正句由来の grandfather relation・shuhrah「عبد الوهاب」削除。「بخط الفخر بن ...」→ Pattern A **#AIND-D00500**（الفخر بن درباس、D04773 の並行記述で補完、cert medium）。bibl → TMP-T-00196（الأمالي القديمة）。「=380 above?」を editorial note で説明（→§D95-1）。

## 自己点検（分母つき）
- 毒wd（Q160851／Q191314／Q35160／Q3824443／Q12247942／Q381208／Q1164991）: 点検 20 件中 違反 0 件（初版の 2 件を修正済み）。
- 幻番号・汚染番号・名寄せ済み旧番号（TMP-P-000529／000664／000760／000813 等）の属性残存: 点検 20 件中 違反 0 件（初版の 5 箇所を修正済み）。
- 規約A（relation/@n）: 点検 20 件中 違反 0 件。
- 統制外 subtype（relation／event）: 点検 20 件中 違反 0 件（初版 5 箇所を是正）。
- 原文 note・校閲 respStmt・ja/en 訳: 20/20 件に存在。空属性（active=""／ref=""）: 0 件。
- 参照 ID の ID-Master 存在確認: TMP-N 20 種・TMP-O 5 種・TMP-S 4 種・TMP-T 1 種・wd 11 種・gn 2 種すべて登録あり。
- well-formed: 20/20 件 PASS。
