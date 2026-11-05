# 集約 進捗ログ B154-158（claude-b154-158-triage, 2026-11-05）

- [x] 退避: XML 100件＋TMP_NEW 5件 → docs/_work/B154-158_incoming/triage/backup_pre_triage/（平置き 105 ファイル）
- [x] 入力確認: 決定1〜19・CHUNK_BRIEF 規則1〜60・検証3本（A20・B15・M17＝52件）・ISSUES 56節・TMP_NEW 55行。前バッチの tri.py・ct.py・scan.py・scan2.py・make_mech_after.py・make_findings_resolved.py・tmp_build.py を triage/ に複写し respStmt 名・日付・チャンク名を本バッチ用に置換（verify/ の *_after.py は B114-118 の古い生成物＝使わない）
- [x] ed1（triage/ed1.py）: 決定1 D10083 子→#AIND-D09473（D09473・D09472・D04013・D12958・D11908 原文、NEW158-04 取り下げ、D02627 は候補 note）／決定2 D03173 teacher relation 除去・書写補助 event に年と persName・訳の向き／決定3 父 TMP-P→#NEEDID（D03131・D03159・D03171・D02897）＋決定10 D08212（祖父＝نور الدين、#NEEDID）／決定5 cert medium 3件
- [x] ed2: 決定4 full 6件（M4・M5・M6・M8 は declined）／決定6 D02871・D08187 の推定 ref 除去／決定7 D10058 父→#NEEDID・D10092 الكرماني ref 除去／決定8 desc 3件／決定9 D10086・D10059 の記憶由来記述／決定11 訳文6件／決定14 D10084・D10089 候補を原文で確認し別人（note）／決定18 D10046（D10289・D01356 を原文で確認）
- [x] ed3: ★1-2（D02874 TMP-P-000342⇄D12770）・★2（D03156 ابن شداد＝子 D01004 も候補）・★3（D10078 العز بن جماعة）の回付 note、B14・B15・M2・M3 の resolution
- [x] TMP: mk_tmp_edits.py → tmp_edits.json → tmp_build.py（field_replace 対応を追加）。TMP_NEW_all.tsv 55行＝維持49・取り下げ6（NEW155-02・NEW155-04・NEW156-01・NEW156-03・NEW157-03・NEW158-04）。各チャンク TSV 最終形（B154 12・B155 5・B156 8・B157 13・B158 11）
- [x] 走査: scan.py（desc 続柄句＝「والد X」書式の #NEEDID 父のみ・「ビント」偽陽性・D10077「الشمني」偽陽性＝実残存0）／scan2.py（取り下げ番号の参照0・未登録仮番号0・未使用0・日付不一致0・name_only 4世代0・二重符号化0。NODESC はサハーウィー相手の師弟（規則60(g)）、FULL D03123「الشيخ المبارك」は見出しの称号＝honorific と同じ、維持）／追加走査: full の伸長（校閲が足した句）＝D03105（クンヤのみ、可）・D03123（称号、可）・「ثم」の復元5件（可）、既登録 TMP-P への cert＝D03156・D03164（規則23 の親子）・★2・★3 のみ
- [x] mech after: 17 → 8（M1・L7、すべて決定済み／declined）、well-formed 100/100、項目6（respStmt）違反0。集約 respStmt 29ファイル（末尾に1つ）、初版・校閲 respStmt は backup と比較して不変
- [x] FINDINGS_all_resolved.tsv 52行
- [x] decisions.md（★1 名寄せ一括 12項目＋候補一覧・★2 ابن شداد・★3 العز بن جماعة・確認依頼12）、idmaster_actions.md（§1 新規49行は仮番号のまま・取り下げ6／§2 名寄せ9行／§3 Note 追記／§4 wd/gn 未照合）、aggregation_report_20261105.md（件数表・ISSUES 処置表（56節＋番号なし1節）・ブリーフ誤り・§6 repo 是正候補＝D04013 father ほか）。完了
