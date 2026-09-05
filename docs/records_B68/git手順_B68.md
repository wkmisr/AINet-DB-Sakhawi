# git 手順 B68（2026-09-04）

## 配置済みファイル（コミットは Waka）
- `Individuals/`: 実項 65件（新規。B68 は repo 未収録だったため上書きなし）＋ `REF_AIND-D0xxxx_*.xml` 17件（新規）。
  - 重複投入 2件（D04069/D04088）は repo 既収録のため配置していない。
- `docs/records_B68/`: HANDOVER_20260904_v13_24.md / 要判断_B68.md / 欠番ウォッチリスト_B68.md / TMP登録_B68.tsv / precheck_B68_before.md / precheck_B68_after.md / notes_chunk01〜07.md / VERIFY_BRIEF.md / VERIFY_REPORT.md / git手順_B68.md
- `docs/HANDOVER_20260904_v13_24.md`（コピー）

## 手順
```bash
cd ~/Desktop/AINet-DB-Sakhawi
rm -f .git/index.lock          # 2026-09-04 時点で stale lock が残存（git status が warning を出す）
git status --short            # 84件（Individuals 82 + docs/records_B68 + HANDOVER）。B64-67 分はコミット済み
git checkout -b B68
git add Individuals docs
git commit -m "B68: 校閲65実項+REF17（転送見出し）、新規TMP45（P897-917/N2/L8/I3/O8/T3）、独立検証パス15件適用、HANDOVER v13.24"
git push -u origin B68
# → PR を作成し main へマージ（B64 ブランチの PR が未マージなら先にそちら）
```

## 注意
- corpus txt（`0__DawForAIND_renumbered_B54.txt`）は変更していない（REF化 17件の $$$ 化は帳簿のみ。帳簿 1436 → **1453**）。
- ID-Master への TMP 45件貼付と §A-2 名寄せ（旧番号の repo 側付替えを先に）は Waka 作業。
- B69-73（100件、うち重複5件）は次バッチ。
