# 集約 進捗ログ — B114-118（triage、2026-10-14）

作業スクリプト置き場: `docs/_work/B114-118_incoming/triage/`。XML は `docs/_work/B114-118_incoming/B114-118/` を直接編集。

- [x] 0. 資料読了（CHUNK_BRIEF・VERIFY_BRIEF・VERIFY_REPORT A/B/mech・FINDINGS 60行・ISSUES 28節・TMP_NEW 56行）。ID-Master max 再確認: P 001439／N 05520／L 00332／I 00221／O 00324／T 00225／S 00075（8,230行）＝起点 P-001440／N-05521／L-00333／I-00222／O-00325／T-00226／S-00076 で変わらず。
- [x] 1. 検証指摘の適用（XML 編集）: B114〜B118 の指摘を順に適用中。補助記録 `triage/triage_notes.json`（ファイル別の集約メモ→最後に respStmt「集約・自己裁定」を挿入）・`triage/tmp_edits.json`（仮TMP の改名・新規・取り下げ）。適用済み: D07005(note)・D07006・D07009・D07019・D07022・D07021・D07023・D07024・D07043・D06109・D07037・D07053・D07127・D07088・D07086・D07067・D07027・D07130・D07050・D07072・D07076・D07079・D07095・D07099・D07103・D07106・D07107・D07100(desc)・D07124・D07059・D07122・D07065・D07052・D07066。
  - 1 完了: `FINDINGS_all_resolved.tsv`（60行: applied 56／declined 2（D07100 jāwara＝repo 既存語彙、D07107 paternal_uncle＝規則35）／issue 2（D07005 ★1、TMP-P-000814 名寄せ ★3））。同型残存の機械走査で relation desc（規則31）6件を追加修正（D06105・D07001・D07009・D07018・D07048・D07059）。
- [~] 2. ISSUES 28節の自己裁定: XML 反映済み＝§D114-2（القلانسي→TMP-P-NEW114-07）・§D115-1・§D115-2・§D116-1（D12197）・§D116-2（note 訂正）・§D116-3（D05407 note）・§D117-1（D07066 note）・§D117-4（الزين طاهر の cert 除去）・§D118-1（D07095 父で確定）・§D118-2（TMP 維持）。残り＝要判断ファイルの作成。
- [x] 3. 仮TMP の実番号採番: 58行（56＋集約新規2: P-NEW114-07 أبو الحرم القلانسي・P-NEW115-04 الشهاب الزاهد）、取り下げ4（P-NEW117-01・P-NEW118-13・O-NEW116-02・L-NEW116-03）、採番54＝P-001440〜001467（28）／N-05521〜05522（2）／L-00333〜00338（6）／I-00222〜00229（8）／O-00325〜00329（5）／T-00226〜00230（5）／S なし。`tmp_map.json`・`tmp_map.tsv`・`TMP登録_B114-118.tsv`（54行）・`TMP_NEW_all.tsv`（58行）作成。XML 36ファイル・162箇所を置換（取り下げ番号は「取り下げた仮番号 B117-P01」形式の文に）。置換前の XML を `triage/backup_pre_number/` に保存。`grep -r NEW11 B114-118/` = 0。スクリプト `triage/tmp_build.py`・`tmp_number.py`。
- [x] 4. 最終確認: 全100件 well-formed。集約 respStmt（claude-b114-118-triage、resp=集約・自己裁定）を38ファイルに付与。`verify/mech_check_after.py`・`mech_report_after.py`（`mech_items_b_after.py` を B114-118 用に新規作成。旧 B109-113 版は `mech_items_b_after_B109-113_stale.py` に mv）で再実行 → 違反1（D07107 paternal_uncle＝規則35 により不適用）。`idmaster_ext_20261014b.tsv`（8,284行＝8,230＋54、末尾改行なし）を作成し precheck_aind_v12 → 118件（名前不一致116＝表記・冠詞・代名詞・翻字差、カテゴリ不一致1＝D07054 shuhrah の N 番号（repo 慣行16件・P は0件）、汚染注意1＝D07100 TMP-O-00108 الطبيب（実体一致））。
- [x] 2. ISSUES 28節の自己裁定 → `docs/要判断/要判断_B114-118.md`（★1〜★4）。
- [x] 5. 記録: `docs/ID-Master要対応_B114-118.md`（§1〜§5）、`統合ファイル一覧_B114-118.tsv`（100行）、`集約報告_20261014.md`。
- 完了（2026-10-14）。
