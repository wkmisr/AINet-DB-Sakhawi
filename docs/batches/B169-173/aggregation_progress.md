# 集約 進捗ログ B169-173（claude-b169-173-triage, 2026-11-18）

- [x] モデル型番を `docs/_work/B169-173_incoming/model_triage.txt` に記録
- [x] 退避: XML 100件＋TMP_NEW 5件 → docs/_work/B169-173_incoming/triage/backup_pre_triage/（平置き 105 ファイル）
- [x] スクリプトの前バッチ固有のハードコードを修正: tri.py（respStmt 名 claude-b164-168-triage→claude-b169-173-triage、日付 2026-11-10→2026-11-18）、make_mech_after.py（同上・検証指摘の件数・取り下げ番号の説明）、tmp_xcheck.py・tmp_build.py（チャンク名 B164〜B168→B169〜B173）、make_findings_resolved.py（T 行の追加）。mk_tmp_edits.py は本バッチ用に書き直し
- [x] 入力確認: 前バッチの集約成果物・CHUNK_BRIEF 規則1〜66・VERIFY_BRIEF・検証3本（A2・B7・M14＝23件、すべて L）・ISSUES 41節・TMP_NEW 23行・決定1〜23
- [x] 決定の「確かめて決める」: 決定2（repo の見出し職業語 state あり49・なし40＝state に統一、A2 不適用、D06579 に state）／決定11（repo 先例 D05340・D06100＝70代→770〜779）／決定13（repo D07025 に鏡像あり）／決定14（使用箇所の原文を全件読んだ。001336 の向きの誤りを発見）／決定20（tmp_xcheck: 共用・重複なし、NEW173-05・06 は別人）
- [x] 事実確認（corpus 本文）: D06644・D12507・D12415・D03754・D04191・D00721・D12926／D03765・D01303・D04282・D05779・D00150・D01673・D00327・D04492・D06755・D00833・D07109・D00134（使用文脈）／repo D00420・D07748・D01259・D02039・D01427・D01902・D04098・D07559・D02982・D03713・D04837・D00253 の source
- [x] ed1.py（dryrun/x で事前に同じ結果を確認、本番との差0）: 決定1 D06541／決定2 D06596 note・D06579 state（T2）／決定3 D03140／決定4 desc 6件／決定5 D06592・D06646（T1）／決定6 D06614 note／決定7 D06578／決定8 D06579／決定10 D06564／決定11 D06641／決定19 D06624／決定23 D06668・D06682・D06613・D06690・D06624 note。19ファイル
- [x] TMP: mk_tmp_edits.py → tmp_edits.json → tmp_build.py。TMP_NEW_all.tsv 24行＝取り下げ1（TMP-L-NEW171-01）・維持22・集約追加1（TMP-O-NEW171-01）。各チャンク TSV 最終形（B169 5・B170 4・B171 4・B172 2・B173 8＝23）
- [x] wd/gn: XML の39種すべて典拠台帳に status ok（verified: OK 2・保留 1・未判定 36）、新規の wd/gn なし
- [x] 走査: scan.py（D06412 の単名書式 desc のみ、「ビン」は「ビント」）／scan2.py（取り下げ番号の参照0・未登録仮番号0・未使用の維持行0・日付不一致0・name_only 4世代0・二重符号化0）
- [x] mech after: 14 → 7（M2・L5、すべて決定済み／declined）、well-formed 100/100、項目6 違反0。集約 respStmt 19ファイル（末尾に1つ）、初版・校閲 respStmt は backup と比較して不変
- [x] FINDINGS_all_resolved.tsv 25行（検証23: applied 17・declined 6／集約で追加2: applied 2）
- [x] repo 側の追加観察: TMP-L-00010（登録 إب）が repo 6ファイルで別地に流用＝汚染番号（§6(a)・§7）。desc「شيخنا」が repo に21ファイル
- [x] idmaster_actions.md（§1 新規23行・取り下げ1・集約追加1／§2 名寄せ ★1 12項目／§3 Note 訂正／§4 wd/gn）、decisions.md（★1・確認依頼16）、aggregation_report_20261118.md。完了
