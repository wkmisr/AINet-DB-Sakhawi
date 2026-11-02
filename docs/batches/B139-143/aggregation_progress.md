# 集約 進捗ログ B139-143（claude-b139-143-triage, 2026-10-26）

- [x] 退避: XML 100件＋TMP_NEW 5件 → docs/_work/B139-143_incoming/triage/backup_pre_triage/（xml/・tmp/）
- [x] スクリプト: B134-138 triage から tri.py・make_findings_resolved.py・make_mech_after.py・tmp_build.py をコピーしパス置換。同型走査用 scan.py を新設
- [x] ed1: 決定1 D07421 父→D09065・possible_identity D11025 high／決定2 D07707 師→D06796・A18・M21 declined／決定3 D07439 possible_identity D07243 medium・師→D07784 medium・note/訳訂正／決定4 D07828 叔父→TMP-P-001350・000068 名寄せ候補 note
- [x] ed2: 決定5 patron 統一（D07415 servant→patron、他5本 note）・決定6 desc（D06388・D07702・D07814・D07833・D07834・D07705・D06397）＋走査で D07806「عمه」×2・決定7 ابن فهد cert（D07407・D07419）・決定8 D07829 event 維持（M18 declined）・D07400 full الأمير
- [x] ed3: 決定9（D06397 D02262 閉合不成立・D07397 فاس 除去／rival 削除／بلد العناب・D07720・D07810 O-00096・D07837 الصاحبية）、A10・A13・A16・B1・B5・B6・B7、persName full（M7〜M12・M16 applied、M13〜M15 declined）、M22・M23 declined
- [x] ed4: §D141-2・§D142-2 自己裁定の note、tmp_edits.json → tmp_build.py（TMP_NEW_all.tsv 43行＝維持41・取り下げ2）
- [x] 同型走査（scan.py）: desc 続柄句・ابن فهد cert・father 欠落・訳文アラビア語・ビン・teaching 残存0
- [x] mech after 29→9（全 declined／確定済み）。D11025・D07243 の鏡像申し送りを REVIEW_NOTES_B140・B141 に追記。D07837 の TMP-I を placeName→orgName（precheck カテゴリ不一致の解消）
- [x] precheck after 177（TMP書式45・幻45＝仮番号、名前不一致80＝見かけ、汚染注意6＝正用、カテゴリ不一致1＝shuhrah の既知）
- [x] FINDINGS_all_resolved.tsv（60行: applied 53／declined 7）、集約報告_20261026.md 作成。完了
