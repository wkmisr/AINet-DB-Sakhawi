# CHANGELOG — ibn ʿAzm 名寄せ統合（TMP-P-000351 → AIND-D12540）

書式: YYYY-MM-DD | 担当者 | 対象 | 内容

## 2026-07-08
- 2026-07-08 | Kumakura | TMP-P-000351（ابن عزم）の確定IDへの付け替え（名寄せ・一括統合）

  ### 背景
  仮ID TMP-P-000351 で参照していた ابن عزم について、確定 AIND-D12540（corpus: 「ابن عزم بفتحتين ثم ميم عمر بن محمد بن أحمد」）が Waka により同定済み（ID-Master注記 🐻）。ID-Master方針「統合作業はまとめて行う」に従い、repo全XMLの参照を一括で D12540 へ付け替えた。ابن عزم の言及はいずれも Pattern A（`<event type="cultural" subtype="mention">` 直下の `<persName ref=…>`）で、active/passive等の構造使用は無し。

  ### ID-Master の変更（要反映）
  - TMP-P-000351 → **AIND-D12540**（عمر بن محمد بن أحمد ابن عزم）。TMP-P-000351 は廃止・再利用不可。

  ### XML の変更（構造ref是正・11件）
  対象の `<persName ref="#TMP-P-000351">` → `ref="#AIND-D12540"` に是正し、統合スタンプ（resp=統合, Claude Opus 4.8, 2026-07-08）を付与:
  - AIND-D00388 / AIND-D00392（B6・「ذكره ابن عزم」）
  - AIND-D00554 / AIND-D00558 / AIND-D00572（「أرخه ابن عزم」）
  - AIND-D00885 / AIND-D01138 / AIND-D01167 / AIND-D01169 / AIND-D01274 / AIND-D01467（「ذكره/قاله ابن عزم」）

  ### 既統合（今回対象外・確認のみ）
  以下5件は前バッチで既に属性が AIND-D12540 に是正済み（TMP-P-000351 は履歴noteにのみ残存）:
  - AIND-D00940 / AIND-D01221 / AIND-D01652 / AIND-D01662 / AIND-D01690

  ### 検証
  - 変更11件すべて `xmllint --noout` well-formed。
  - repo全体の構造参照 `(ref|active|passive)="#TMP-P-000351"` = **0**（残存は履歴note本文のみ・監査証跡として保持）。

  ### 申し送り
  - 逆relation（AIND-D12540側に「言及された」逆リンク）は Pattern A（言及）であり不要（一方向イベント）。
  - AIND-D12540 本項（ابن عزم عمر بن محمد بن أحمد）は現repo範囲外（未立項）。将来立項時に本人伝XMLを作成。
