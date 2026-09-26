# REVIEW_NOTES_B88e — チャンク B88e（AIND-D07551〜D07616、20件・محمد بن عبد الرحمن）

- 校閲者: claude-b88e-review（2026-09-24）
- 対象: `docs/_work/B88_incoming/B88/` の指定20ファイル（`ls *.xml | sed -n '81,100p'`）。in-place 編集、git 操作なし。
- 参照: `CHUNK_BRIEF_B88.md`、`precheck_B88_before.md`、corpus 原本 `0__DawForAIND_renumbered_B54_split20260905.txt`（転送先・親族本伝の探索）、`corpus_B88.json`（本文）、`docs/_work/idmaster_ext_20260924.tsv`（B86 の TMP-*-NEW86* 行は無視）、`docs/records_B79-83/tools/h2g.py`（西暦）。
- 共通処理（全20件）: 原文全文を `<note type="source" xml:lang="ar">` として translation の直前に挿入（刊本の立項番号は除去。corpus_B88.json と機械照合 20/20 一致）／relation @n を規約A（親族 @n 無し・非親族のみ1起点連番）に統一／西暦は h2g.py（proleptic Gregorian）で再計算／ja 訳の「ビン」→「ブン」・ラカブ「〜・アッ＝ディーン」→「〜ッディーン」、補い・転写・立項連番の混入を除去／校閲 respStmt を追加（初版 respStmt は無改変）／well-formed 確認 20/20 OK／全 ref を ID-Master・corpus AIND 一覧と機械照合（NEW88e 以外は登録済み、#NEEDID 残存 0）。
- 集計: **実項 16・REF 4**（D07551→#AIND-D07571／D07567→#AIND-D07547／D07572→#AIND-D07555／D07612→#AIND-D07629）。新規仮TMP **11件**（P×7、I×1、L×2、O×1）。ISSUES **12項**。

## 実項/REF 判定
| ID | 判定 | 根拠 |
|---|---|---|
| D07551 | **REF** | 「فيمن جده عيسى بن سلطان」＝自項に転送指示。→ #AIND-D07571（ابن سلطان、corpus 行83229） |
| D07567 | **REF** | 「فيمن جده الخضر قريبا」。→ #AIND-D07547（ابن بريطع／ابن العماد、行82907） |
| D07572 | **REF** | 「مضى فيمن جده عبد العزيز بن محمد بن أحمد قريبا」。→ #AIND-D07555（行82989） |
| D07612 | **REF** | 「يأتي فيمن لم يسم جده」。→ #AIND-D07629（「واسم جده محمد」、行84760） |
| 他16件 | 実項 | 転送指示なし（「الماضي أبوه」「أخو الذي قبله」型は本人の本伝） |

## ファイル別
### REF_AIND-D07551
- REF 方式X。name_only・listRelation（grandfather #NEEDID）除去、原文 note 付与、target #AIND-D07571。ファイル名を REF_ に変更（mv）。
### AIND-D07556
- 「صهر …」relation の #NEEDID → #AIND-D04605（ナサブ7代一致）cert medium、重複していた subtype="other" を除去（§De-3）。父 → **TMP-P-NEW88e-01**。
### AIND-D07558
- 息子 عبد الباسط → #AIND-D03494、父 → #AIND-D03683（ナサブ5代一致）。没年「بعيد الثمانين ظنا」を notBefore-custom 0880／notBefore 1475／cert medium に（初版は when-custom 確定扱い）。state الشهادة の placeName القاهرة（ニスバ由来）除去。祖父 النور الأدمي=#AIND-D04954 は note のみ（§De-4）。
### AIND-D07559
- ja 訳「754番。」除去。生年 794 → 1391（初版 1392）。師3件（P-000026／000094／000135）確認、空 field desc 除去。父 → #AIND-D03684 cert medium（§De-2）、母 → **TMP-P-NEW88e-02**。laqab النجم 追加。
### AIND-D07561
- [カテゴリ不一致] TMP-N-00473 → #AIND-D09164（الزين الخوافي）cert medium。父 → #AIND-D03686。独立 event（ヒルカ、relation と重複）除去。889-08 → 1484-09。没地 الخليل（「ببلده」、規則22(3)）cert medium。逆算生年 819頃 cert low（§De-10）。
### AIND-D07564
- 空 brother → #AIND-D07563。父 → #AIND-D03693（兄のナサブ経由、cert medium、§De-6）。affiliation employed／residence دمياط 除去。جامع البدري → **TMP-I-NEW88e-01**。826-07 → 1423-06。
### AIND-D07565
- [カテゴリ不一致] 「praised by」TMP-N-00096 → Pattern A mention event（البرماوي=#AIND-D07528、§De-4）。師3（active 空）除去、師2の field 除去。息子 → #AIND-D08814、父 → **TMP-P-NEW88e-03**。affiliation（state と重複）・residence・state 内 placeName 除去。
### REF_AIND-D07567
- REF 方式X。初版訳の誤読（「祖父アル＝ハディルの項を参照」）を是正。target #AIND-D07547。
### REF_AIND-D07572
- REF 方式X。target #AIND-D07555。
### AIND-D07583
- [汚染注意] grandfather TMP-P-000529 → #AIND-D07346。父 → #AIND-D03746、兄弟 أحمد → **TMP-P-NEW88e-04**。affiliation study 除去、event の placeName #NEEDID → wd:Q23975647 cert medium（B87 §D-26 先例）、bibl 追加。師 relation は立てず（§De-5）。
### AIND-D07587
- 「بن صالح」＝一族通称の誤認を是正（father「صالح」除去、shuhrah ابن صالح 追加、name_only「محمد」）。兄 → #AIND-D07586、甥 → #AIND-D08822、父 → #AIND-D03752 cert medium（§De-6）。師 field 除去。state قاضي → wd:Q217029（任地は note のみ）。没年「إحدى الجماديين 874」を notBefore/notAfter で表現。
### AIND-D07588
- 空 brother ×2 → #AIND-D07586・#AIND-D07587。父 → #AIND-D03752 cert medium。訳文の誤読（「彼の前に記載された二人の兄弟」）を是正。
### AIND-D07589
- 師 #NEEDID → #AIND-D08670（خير الدين بن القصبي）。relation 内 event @when="0898" → when-custom＋when 1492。独立 event study（المدينة）除去。父 → #AIND-D03757。
### AIND-D07590
- precheck [汚染注意] TMP-N-00108 は nisbah 位置＝適正（維持）。息子 → #AIND-D01351、父 → **TMP-P-NEW88e-05**。「أفاده ولده」を mention event に。state كاتب の零番号 orgName（TMP-P-000000）除去、placeName المغرب cert medium（§De-9）。859 → 1454（初版 1455）。residence 2 を notBefore 0830 に。
### AIND-D07592
- 父 → #AIND-D03762（ナサブ8代一致）。没地 الفخة → **TMP-L-NEW88e-01**（§De-7）。「ذكره الناشري」→ mention event（#AIND-D04864 cert medium）。832-10 → 1429-07。
### AIND-D07595
- 父 → #AIND-D03767 cert medium（§De-8）。854-02 → 1450-03。
### AIND-D07608
- 父 → #AIND-D03800（「والد المحب محمد الآتي ونزيل المؤيدية」で閉合、§De-4）、師（أخذ عن أبيه）も同 ID。873-11-09 → **1469-05-30**（初版 1468。日曜一致）。affiliation（state と重複）・residence・state 内 placeName 除去。
### REF_AIND-D07612
- REF 方式X。nisbah・laqab・kunyah・affiliation 除去。target #AIND-D07629。
### AIND-D07615
- ja「37番。」／en「No. 37.」除去。patron → #AIND-D01869（الأتابك أزبك）。父 → **TMP-P-NEW88e-06**。state: موقع الأتابك → TMP-O-00058、توقيع المفرد → **TMP-O-NEW88e-01**、توقيع الدست → TMP-O-00052。placeName القاهرة ×3 除去。
### AIND-D07616
- [汚染注意] 孫 TMP-P-000529（other）→ #AIND-D06547（grandson）。息子 → #AIND-D00274。父 → **TMP-P-NEW88e-07**。[カテゴリ不一致] placeName 位置の TMP-N-00264 → **TMP-L-NEW88e-02**（زواوة）、residence 除去。state قاضي → wd:Q217029。没年 853/852 を notBefore/notAfter cert medium、逆算生年 cert low。

## precheck 対応
- D07559 [連番訳混入]／D07615 [連番訳混入]×2: 除去済み。
- D07561 [カテゴリ不一致] TMP-N-00473／D07565 [カテゴリ不一致] TMP-N-00096: 人物 ID に置換。
- D07583・D07616 [汚染注意] TMP-P-000529: 原文で別人と確認し差し替え。
- D07590 [汚染注意] TMP-N-00108: nisbah 位置での正用＝修正不要。
- D07616 [カテゴリ不一致] TMP-N-00264（placeName）: 地名 TMP-L 新規発行。
- D07565・D07589 [名前不一致]（Q4120006／T-00095 のラテン表記）: 見かけ上。T-00095 は relation 除去に伴い消滅。
