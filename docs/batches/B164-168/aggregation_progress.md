# 集約 進捗ログ B164-168（claude-b164-168-triage, 2026-11-10）

- [x] 退避: XML 100件＋TMP_NEW 5件 → docs/_work/B164-168_incoming/triage/backup_pre_triage/（平置き 105 ファイル）
- [x] 前バッチのスクリプト（tri.py・ct.py・scan.py・scan2.py・make_findings_resolved.py・tmp_build.py・make_mech_after.py）を本バッチ用に置換（パス・respStmt 名・日付・チャンク名）。前バッチの編集スクリプト ed1〜6.py・mk_resolutions.py・mk_tmp_edits.py は triage/prev_B159/ に移した（参照用）
- [x] 入力確認: 決定1〜22・CHUNK_BRIEF 規則1〜64・VERIFY_BRIEF・検証3本（A4・B9・M12＝25件）・ISSUES 54節・TMP_NEW 71行・前バッチ集約成果物
- [x] 事実確認（corpus 本文）: D02804・D09652／D13527・D12821・D10072・D06694／D10438・D12855・D10816・D00716・ID-Master 行293・410（Q124745634 は D10816 行にも）／D10296・D00684／D07806／D06453・D07606・D07375・D10118〜D10121／D02883・D02865・D00711・D10115／二重立項の相手 D00963・D12356・D10589・D11162・D13857・D10304・D10315／D01182 ほか「X أبوه Y هو」型・repo D00592／D10250／D09050
- [x] ed1: 決定1 D10483（師→#AIND-D02804）／決定2 D10256（娘 #AIND-D13527）
- [x] ed2: 決定3 D10438（NEW167-02→NEW168-13 cert medium）／決定4 D10296（父→#NEEDID＋候補 D00684。決定の「TMP-P 新規」は規則3 を満たさず）／決定5 D10115・D10122（@when）／決定6 D12859（生年の幅・desc）
- [x] ed3: 決定7 訳文（D10250・D10245・D10269・D10316・D12851・D12859・D12866、同型走査で D10104・D10108）／決定8 full の الأصل／ثم（D10305・D10434・D10435、同型走査で D10277・D10279・D10294）／決定13 D10119〜D10121 cert 除去／決定14 D10115 brother cert 除去／決定16 D10110 note
- [x] ed4: 決定10 D10441（NEW167-05→#NEEDID）／M5・M6・M11 の処置記録
- [x] ed5: scan.py で見つけた possible_identity の desc 2件（D10315・D10481、規則31）／D12856 に ★3 回付 note
- [x] ed6: M7〜M10（TSV の ⚠汎用名）の処置記録
- [x] TMP: tmp_xcheck.py（71行を ID-Master の Arabic・Note・他チャンクと照合。重複は التقي القلقشندي のみ、既登録は TMP-P-000176 のみ）→ mk_tmp_edits.py → tmp_edits.json → tmp_build.py。TMP_NEW_all.tsv 71行＝取り下げ2（NEW167-02・NEW167-05）・維持69。各チャンク TSV 最終形（B164 13・B165 11・B166 11・B167 17・B168 17）
- [x] wd/gn: XML の34種すべて典拠台帳（lookup.py）に status ok で存在、新規の wd/gn なし
- [x] 走査: scan.py（desc の実残存2件→ed5 で是正、他は「والد X」書式・名のない人物の呼称）／scan2.py（取り下げ番号の参照0・未登録仮番号0・未使用の維持行0・日付不一致0・name_only 4世代0・二重符号化0）
- [x] mech after: 12 → 10（M4・L6、すべて決定済み／declined）、well-formed 100/100、項目6 違反0。集約 respStmt 29ファイル（末尾に1つ）、初版・校閲 respStmt は backup と比較して不変
- [x] FINDINGS_all_resolved.tsv 32行（検証25: applied 23・declined 2／集約で追加7: applied 7）
- [x] idmaster_actions.md（§1 新規69行・取り下げ2／§2 名寄せ ★1 12項目／§3 Note 訂正6件／§4 wd/gn）、decisions.md（★1〜★3・確認依頼14）、aggregation_report_20261110.md。追加観察: TMP-L-00140（登録 المهجم）が repo 8ファイルで別地に流用＝汚染番号（§6(a)・§7）。完了
