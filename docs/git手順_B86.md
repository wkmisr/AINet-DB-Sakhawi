# git 手順 B86（2026-09-18）

## 本セッションで実施済み
`origin/main`（1b89d36 = followup-B79-83-A3 の squash マージ）から新ブランチ **`B86-20260918`** を切り、以下を1コミットで載せてあります。**push と PR は Waka の作業**です。

```bash
cd ~/Desktop/AINet-DB-Sakhawi
git --no-optional-locks status -sb          # ブランチが B86-20260918 で clean なことを確認
git --no-optional-locks log -1 --stat       # コミット内容を確認
git push -u origin B86-20260918             # ← ここから Waka
# GitHub で PR を作成 → **Squash and merge**
```

## コミットに含まれるもう一段の注意
- squash マージ後に同じブランチへ追いコミットすると PR が衝突します（B74-78 の #63/#64 の教訓）。次バッチ（B87）も**必ず main から新ブランチ**を切ってください。
- `docs/_work/` は .gitignore 済みのため、B86 の作業用フォルダ・idmaster TSV・browser のビルド成果物はコミットに含まれません（意図どおり）。

## コミット後に Waka 側で必要な作業
1. **ID-Master への貼付（2本）**
   - `docs/records_B56-58_84-85/TMP登録_裁定分_20260916.tsv`（12件、前バッチ分・**未貼付のまま**）
   - `docs/records_B86/TMP登録_B86.tsv`（9件、本バッチ分）
   いずれも7列・ヘッダなし。貼付後は TSV エクスポートで検証してください（セル入力は先頭文字欠落・オートコンプリート置換が起きるため）。
2. **裁定**: `docs/要判断_B86.md`（21項目）。最優先は §D-V1（ユリウス暦の明文化と既存約266件の扱い）。
3. **AINet Browser**: v15（2,359件）を Artifact に republish 済み。URL は変わりません。
