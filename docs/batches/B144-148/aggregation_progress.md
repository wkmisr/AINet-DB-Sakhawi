# 集約 進捗ログ B144-148（claude-b144-148-triage, 2026-10-31）

- [x] 退避: XML 100件＋TMP_NEW 5件 → docs/_work/B144-148_incoming/triage/backup_pre_triage/（xml/・tmp/）
- [x] 入力確認: 決定1〜18・CHUNK_BRIEF 規則1〜58・検証3本（A15・B14・M42＝71件）・ISSUES 26節・TMP_NEW 67行・前バッチ（B139-143）の集約の型。tri.py ほかコピー済みスクリプトを確認（make_mech_after.py の件数・取り下げ番号の文言を本バッチ用に修正）。corpus 表示用 ct.py を追加
- [x] ed1: 決定1 D07905 父→D04746／決定2 D07887 兄弟 علي→D05265、أحمد は引き直して本伝なし＝維持／決定3 D07938→D09205／決定4 D07957→D08204／決定5 西暦3件（h2g.py で再計算、note も訂正）
- [x] ed2: 決定6 D07861 target→D07839／決定7 D07891 父→TMP-P-NEW145-07（أحمد السيد、NEW145-06 取り下げ）・full から「حفيد الأهدل」／決定8 D07858 候補 D04662 を note／決定9 D07871 学生→TMP-P-NEW145-08
- [x] ed3: 決定10 D07948→D08141 cert medium（corpus 全文で固定呼称を確認）／決定11 D07962 父→wd:Q29919643、祖父 NEW148-02 維持／決定12 D07851 notAfter 除去／決定13 D07870 laqab 除去・訳／決定15 البلقيني 3項を #AIND-D05849＋corresp wd:Q6798541 に
- [x] ed4: 決定14 name_only 3件・full の職名4件（M21・M24 declined）・D07926 affiliation×3 除去・D07867 state orgName 除去＋TMP-L-NEW144-03・desc「شيخنا」×5・長文 desc・صاحب تونس・القاضي×2・ابن شيخنا（M42 declined）
- [x] ed5: 決定17 D07908 note／A10・A11・B7・B8・B11・B12・B14・M17・M31／declined A9・A15・M16・M19／§D148-3 確認中に二重立項 D07971⇄D09293 を発見し possible_identity cert high
- [x] ed6: TSV 系の処置記録（B13・M27〜M30・M32）、鏡像申し送りを REVIEW_NOTES_B144〜B148 に追記
- [x] TMP: mk_tmp_edits.py → tmp_edits.json → tmp_build.py（TMP_NEW_all.tsv 70行＝維持64・取り下げ6）
- [x] 同型走査: scan.py（desc 続柄句・ابن فهد cert・father 欠落・訳文アラビア語・ビン・teaching＝実残存0。ヒットは الشمني の「مني」・إسمعيل の「سمع」・ビント・「أخو＋本項主」書式の偽陽性）／scan2.py（取り下げ番号の属性参照0・未登録仮番号0・未使用仮番号0・-custom と西暦の不一致0（年精度 notAfter 年末取り含む）・name_only 4世代0・affiliation⇄state 二重0・desc 続柄句0）
- [x] mech after 42→10（すべて決定済み／declined）、precheck after 267（仮番号の書式不正・幻番号 各76、名前不一致106、汚染注意7＝正用、要照合wd2）
- [x] well-formed 100/100、集約 respStmt 37ファイル（末尾に1つ）、初版・校閲 respStmt 不変（backup と比較）
- [x] FINDINGS_all_resolved.tsv（71行: applied 64／declined 7）、集約報告_20261031.md。完了
