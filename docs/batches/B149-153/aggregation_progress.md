# 集約 進捗ログ B149-153（claude-b149-153-triage, 2026-11-03）

- [x] 退避: XML 100件＋TMP_NEW 5件 → docs/_work/B149-153_incoming/triage/backup_pre_triage/（平置き 105 ファイル）
- [x] 入力確認: 決定1〜22・CHUNK_BRIEF 規則1〜59・検証3本（A12・B17・M46＝75件）・ISSUES 43節・TMP_NEW 43行・前バッチ集約の型。tri.py の respStmt 名・日付を本バッチ用に置換。前バッチの ed1〜ed6.py は triage/prev_B144-148/ に移動（再実行しない）
- [x] ed1: 決定1 D08061 father #NEEDID（同型 father 欠落の全件走査で残存0）／決定2 D10042 師→D06630（D06630・D03455・D06629 原文、repo D05819・D00790 確認）／決定3 D10016・D10017 ابن فهد→D05979 medium（D09211 の没日 871-03-07 を corpus で確認）
- [x] ed2: 決定4 D10040（المجد اللغوي→D09543 medium＝corpus 53＋4 行／ابن حاتم→000540＝D12978・D05365・D13018／المليجي→新規 TMP-P-NEW153-04）／決定5 D10022 詩の両読み（D04266 原文確認）／決定6 D10019 nisbah 除去／決定12 D10022 possible_identity 双方向
- [x] ed3: 決定7 D08139（D01034・D12401 原文、note のみ）／決定8 D08129 العربي（索引 D11844）／決定9 D08151 継父 relation 除去／決定10 D08071→TMP-P-NEW149-06、D08142→TMP-P-NEW151-05／決定11 D08091 父 #NEEDID
- [x] ed4: 決定13 D08173（D05566・D05544 原文）／14 D08094／15 D10025／16 D10035（h2g 893-04＝1488-03-24〜）／17 placeName 4件／18 訳文5件／19 D08150 desc（M14〜M28 declined）
- [x] ed5: 自己裁定 A7（D08082 cert 除去）・M4〜M9（full 職名、M8 declined）・M33・M34（父候補を原文で確認し別人）・M29・M37・M43〜M45 declined・B17
- [x] 走査: scan.py（desc 続柄句・ابن فهد cert・father 欠落・訳文アラビア語・ビン＝実残存0。ヒットは「والد X」書式の #NEEDID 父・「ビント」の偽陽性）／scan2.py（取り下げ番号の参照0・未登録仮番号0・未使用仮番号0・-custom と西暦の不一致0・name_only 4世代0・二重符号化0）。追加走査（desc に句）で D10040 student desc「أجاز لي」を発見→「السخاوي」
- [x] TMP: mk_tmp_edits.py → tmp_edits.json → tmp_build.py（TMP_NEW_all.tsv 46行＝維持45・取り下げ1。新規 TMP-P-NEW149-06・NEW151-05・NEW153-04）
- [x] mech after 46→27（すべて決定済み／declined）、well-formed 100/100。集約 respStmt 33ファイル（末尾に1つ）、初版・校閲 respStmt 不変（backup と比較）
- [x] FINDINGS_all_resolved.tsv（75行: applied 52／declined 23）、aggregation_report_20261103.md。完了
