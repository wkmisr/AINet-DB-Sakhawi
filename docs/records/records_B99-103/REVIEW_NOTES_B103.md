# REVIEW_NOTES_B103 — AIND-D05764〜D05800（20件、2026-10-04、claude-b103-review）

対象: `docs/_work/B99-103_incoming/B99-103/` の B103 分 20 ファイル（in-place）。原文は `corpus_B99-103.json` と corpus 原本で逐語照合。全件に `<note type="source">` を挿入し、校閲 `<respStmt>` を追加。日付は h2g.py で再計算。REF 2件は `REF_` にリネーム。

## 実項/REF 内訳
- REF（方式X）: **D05764**（في ابن آدم → `#AIND-D04925`）、**D05769**（مضى في علي خروعة → `#AIND-D05749`）
- 実項: 18件

## ファイル別

### REF_AIND-D05764 علي الكناني الحبيبي
転送先 `#AIND-D04925`（علي بن آدم بن حبيب … الكناني الحبيني البوصيري）。nisbah・relation 2本を除去。綴り揺れ الحبيبي/الحبيني は note（§D103-9）。

### AIND-D05765 علي الكيلاني الشافعي
「عرض عليه」は三人称のまま読み師 `#NEEDID`（§D103-1）。「أظنه ملا علي … أبوه نور الله」→ `#AIND-D05673` possible_identity（cert medium）。初版の父 relation（推定相手の父）と honorific ملا を除去。895 → 1489。

### AIND-D05767 علي المحلي ثم المكي العطار
没 882-11 → 1478-02（初版 1477）。ニスバ由来 residence 2件除去、「الساكن برباط العباس」→ residence event（TMP-I-NEW103-01）。ابن فهد → `#AIND-D05979` cert medium（没年 882）。

### AIND-D05768 علي المغربي العطار
職の勤務地由来の residence（مكة）除去。没年不詳・ムハッラム月のみを note。

### REF_AIND-D05769 علي اليمني
転送先 `#AIND-D05749`（علي الشهير بخروعة、B102）。

### AIND-D05770 عمار بن خمليش
residence فاس 除去。職 → TMP-O-NEW103-01（شيخ أولاد حسين）。父 `#NEEDID` relation 追加。

### AIND-D05771 عمار بن عبد الرحيم بن حسن الغرياني
汚染番号 TMP-P-000204（祖父位置）→ `#NEEDID`、父 → TMP-P-NEW103-02。method حمل عن（TMP-S-00008）、field 除去。الصليبة → TMP-L-NEW103-02。state 内 orgName（二重符号化）除去。訳文を逐語化。

### AIND-D05772 عمار الحوفي
規則2（field 除去）。صرد → TMP-L-NEW103-01。重複 visit 除去。

### AIND-D05775 عمرو بن أحمد … بن أمير تونس
没年 بضع وعشرين → notBefore 823/1420・notAfter 829/1426（初版 when="701"）。異名 عمر を cert low の name_only に。父は TMP 未発行（§D103-2）。

### AIND-D05776 عمرو بن عثمان الديمي
父 → `#AIND-D04876`（الفخر الديمي）。没 864 → 1459。ニスバ由来 affiliation（الأزهر）除去。field 除去。異母弟 D07954 は relation 化せず note。

### AIND-D05783 عمر بن إبراهيم بن القواس
没 801-11 → 1399-07 cert medium。Pattern A（شيخنا في أنبائه）。推定 affiliation（الجامع الأموي）・ニスバ由来 residence 除去（§D103-7）。

### AIND-D05784 عمر بن إبراهيم الأخطابي
「سمع علي」＝ عليّ。قريب التسعين → when-custom 890 / when 1485 / cert low（規則4）。

### AIND-D05785 عمر بن أحمد بن مطير
兄・後継 → `#AIND-D11059`。父 → `#AIND-D00452` cert medium（§D103-3）。甥 `#AIND-D01162` への師 relation（規則23）。الأهدل → `#AIND-D02702` Pattern A。state「الوظيفة」→ note、فقيه state（TMP-O-00185）。

### AIND-D05786 عمر بن أحمد بن أحمد الحلبي الدمياطي
先例 D07526 と同じ充当: 師 `#AIND-D08850`（ابن الكويك）、同学 `#AIND-D07363`（أبو الطيب بن البدراني）、الزين رضوان `#AIND-D03005` Pattern A（§D103-4）。

### AIND-D05787 عمر بن أحمد بن زيد الجراعي
毒wd Q191314 → Q233387。叔父 → `#AIND-D10697`、第2師 → `#AIND-D05979`、البخاري → wd:Q1023470、父 → TMP-P-NEW103-01。جاور 由来 placeName 除去（§D103-8）。

### AIND-D05789 عمر بن أحمد بن عبد الرحمن الريمي
父 `#AIND-D00827`・祖父 `#AIND-D03687`・弟 `#AIND-D06687`（汚染番号 TMP-P-000529 を差し替え）。サハーウィーの「المجاورة الثالثة」を本項主の jāwara としていた event を除去。

### AIND-D05790 عمر بن أحمد بن عبد الرحمن بن الجمال المصري
TMP-N-00215（person 位置）→ TMP-P-001331（§D103-5）。active="" の暗記 relation → learning event。父 `#AIND-D00833`・祖父 `#AIND-D03742`・兄 `#AIND-D04977`／`#AIND-D06688`（cert medium）を追加。

### AIND-D05791 عمر بن أحمد بن عبد الواحد التقي الزبيدي
Pattern A（إنبائه）。職の勤務地由来 residence 除去。

### AIND-D05797 عمر بن أحمد بن عمر المنقش
空 relation → 息子 `#AIND-D01110`（「والد عمر الآتي」）。没「سنة ثلاث」803 cert medium（息子の年代と整合）。

### AIND-D05800 عمر بن أحمد … بن رضوان السلاوي
父 → `#AIND-D01215`（ナサブ1代差は note、§D103-6）。曽祖父 → TMP-P-NEW103-03（ancestor）。ابن مزهر → `#AIND-D10854` cert medium。البقاعي → `#AIND-D00207` Pattern A。residence القاهرة notAfter 840/1437。

## corpus で特定した相手側本伝（父子・兄弟の相互参照）
| 本項 | 関係 | 相手 |
|---|---|---|
| D05776 | 父 | #AIND-D04876 الفخر الديمي |
| D05785 | 兄／父／甥 | #AIND-D11059／#AIND-D00452（medium）／#AIND-D01162 |
| D05787 | 叔父／師 | #AIND-D10697／#AIND-D05979 |
| D05789 | 父／祖父／弟 | #AIND-D00827／#AIND-D03687／#AIND-D06687 |
| D05790 | 父／祖父／兄 | #AIND-D00833／#AIND-D03742／#AIND-D04977・#AIND-D06688 |
| D05797 | 息子 | #AIND-D01110 |
| D05800 | 父 | #AIND-D01215 |
| D05765 | possible_identity | #AIND-D05673 |
| D05786 | 師／同学 | #AIND-D08850／#AIND-D07363 |

## 新規仮TMP（7件、TMP_NEW_B103.tsv）
TMP-P-NEW103-01〜03、TMP-L-NEW103-01〜02、TMP-I-NEW103-01、TMP-O-NEW103-01。

## 自己点検（分母つき）
- well-formed: 20件中 20件 OK
- 毒wd（Q160851/Q191314/Q35160/Q3824443/Q12247942/Q381208/Q1164991）: 20件中 違反 0件（D05787 の Q191314 を修正済）
- 幻番号・汚染番号（TMP-P-000529/000204/000236/000199/000321/000360/000034）の残存: 20件中 0件
- ニスバ番号の person 位置流用: 20件中 0件（D05790 TMP-N-00215 を修正済）
- active="" / #NEEDED 等の空参照: 20件中 0件
- relation/@n 規約A（親族に n なし・非親族 1 起点連番）: 20件中 違反 0件
- event/@n 連番: 20件中 違反 0件
- 原文 note（corpus の text と完全一致）: 20件中 20件
- en 訳が英語: 20件中 20件／ja 訳冒頭の立項連番: 0件
- `xml:lang="lat"`: 0件／desc の xml:lang 欠落: 0件
- cert high 以外の箇所: D05765（possible_identity medium・#NEEDID 師）、D05775（name_only low）、D05783（death medium）、D05784（event low）、D05785（father medium・successor medium・teacher medium）、D05767（mention medium）、D05790（brother medium ×2）、D05797（death medium）、D05800（patron medium・residence medium）
- FIXLOG: 74 行（うち resolution=issue 2 行）
