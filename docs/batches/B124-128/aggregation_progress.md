# 集約 進捗ログ B124-128

- 2026-10-19 開始（claude-b124-128-triage）。入力確認済（FINDINGS 73＝A16・B21・mech36、ISSUES 6+3+2+8+6節）。XML・TMP_NEW の作業前コピーを triage/backup_pre_triage/ に退避（105ファイル）。
- e1_father: 父 #NEEDID 12件追加（D06115 D06127 D06135 D06137 D06138 D06139 D06142 D06143 D06145 D06154 D06171 D06172）、D06120 desc 統一
- e2_persname: full 職名句除去10件（D05412 D05433 D06138 D06167 D06186 D06207 D06226 D06227 D06230 D06235）。不適用: D06127・D06139 الطواشي（身分）、D06170 بن الحاجب（父称構文）
- e3_decisions: D06135→D02207（NEW125-01 取り下げ）・D05471→D05452・D06117→D08351・D06184 cert medium・D06218 祖父→note・日付H3件（D06115 D06212 D06225）
- e4_contentA: D06138 state削除・D05431 cert・D05478/D06116 note換算・D06137 note
- e5_contentB: D06165 D06172 D06149 D06230 D06162 D06197 D06214 D06235 D06190
- e6_misc: D06202 D06207(★4) D06176(O-00091) D06194 killer D06225 D05424 note、TSV NEW124-05/NEW128-06 note・NEW124-02 warn
- e7_scan_fix: 同型残存走査（scan.py: 未収録主張・引用語照合・possible_identity high・cert相当・未就任句・حدود・patron=teacher・الماضي/الآتي أبوه の cert・leprosy・換算）→ D06145 full البناء、D06138 引用訂正。他は偽陽性
- tmp_build: TMP_NEW_all.tsv 53行（取り下げ1）。well-formed 確認
- FINDINGS_all_resolved.tsv 作成（73行）
- mech_after 生成・再実行（違反 6 見込み）
- 集約報告_20261019.md 作成。完了
