# 集約 進捗ログ B159-163（claude-b159-163-triage, 2026-11-08）

- [x] 退避: XML 100件＋TMP_NEW 5件 → docs/_work/B159-163_incoming/triage/backup_pre_triage/（平置き 105 ファイル）
- [x] 入力確認: 決定1〜19・CHUNK_BRIEF 規則1〜62・検証3本（A15・B15・M32＝62件）・ISSUES 45節・TMP_NEW 27行。前バッチの tri.py・ct.py・scan.py・scan2.py・make_findings_resolved.py・tmp_build.py・mk_tmp_edits.py・make_mech_after.py を triage/ に複写し、respStmt 名・日付・チャンク名を本バッチ用に置換（triage/ にあった 11/6 の部分置換版は上書き）
- [x] ed1: 決定1 D00356（son→nephew #AIND-D10999、訳、D09578 未確定、TMP-P-001060 候補）／決定2 D06414（主人→#AIND-D10349、D10349・D07238 原文）／決定3 D00359（@when 1487）
- [x] ed2: ed1 の note 位置の補正（D00359）／決定4 D03182（met の向き）
- [x] ed3: 決定5 D03191（death 0852 cert low、就任 @when 1451、cert medium 除去、訳。D03365・D02468 原文）
- [x] ed4: 決定6 D08226（#NEEDID＋候補）／決定8 name_only 6件・D06489 full／決定9・12 D06446（الشبيكة・搬送先 مكة・طريق جدة の ref）／決定10 D06411／決定11・13 D06489（葬儀日付・訳・TMP-I-NEW162-02）／決定12 D06476・D03186／決定13 訳文4件／決定14 desc・@n（D06483・D06433・D08233・D10094）
- [x] ed5: L 指摘（D06405・D06439 の event n、D06445 nisbah、D10095 の記録訂正、D06479 note、D06440 son、D06416 候補 note）
- [x] ed6: §D161-6 の候補補足（D06461）／★2 回付 note（D06467、決定7 は保留＝D12723）／★1-17 回付 note（D10096・D06489）／決定19（D06414 gn:321062 を台帳で確認）
- [x] TMP: mk_tmp_edits.py → tmp_edits.json → tmp_build.py。TMP_NEW_all.tsv 28行＝維持27・取り下げ1（NEW160-02）、集約で新規 TMP-I-NEW162-02。各チャンク TSV 最終形（B159 8・B160 4・B161 5・B162 6・B163 4）
- [x] 走査: scan.py（desc 続柄句＝「والد X」書式の #NEEDID 父と名のない人物の呼称のみ。実残存0）／scan2.py（取り下げ番号の参照0・未登録仮番号0・未使用0・日付不一致0・name_only 4世代0・二重符号化0）／wd/gn 30種を典拠台帳で照合（全件あり）
- [x] mech after: 32 → 15（M3・L12、すべて決定済み／declined）、well-formed 100/100、項目6 違反0。集約 respStmt 30ファイル（末尾に1つ）、初版・校閲 respStmt は backup と比較して不変
- [x] FINDINGS_all_resolved.tsv 62行（applied 48・declined 14）
- [x] decisions.md（★1 名寄せ一括 17項目＋候補一覧・★2 ابن المرجوشي・確認依頼13）、idmaster_actions.md（§1 新規27行・取り下げ1／§2 名寄せ17行／§3 Note 追記・訂正10件／§4 wd/gn）、aggregation_report_20261108.md。完了
