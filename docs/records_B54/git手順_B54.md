# B54 コミット手順（ターミナル）

現在の状態: ブランチ **`B49`** / リモート `https://github.com/wkmisr/AINet-DB-Sakhawi.git`
直近コミット `4d7846d B49-53: 校閲完了（実項98/REF化1/重複投入1）`

---

## ⚠ 先に確認: コミットしてはいけないファイルが混ざっています

`git status` の未追跡 **170件**の内訳は次のとおりです。

| 種別 | 件数 | 扱い |
|---|---|---|
| `AIND-*.xml` / `REF_AIND-*.xml` | **100** | ✅ B54本体。コミットする |
| **`.fuse_hidden0000…`** | **69** | ❌ **コミット厳禁**。マウントの残骸（**日付は6月24日**＝今回の作業とは無関係の古い残骸） |
| `.DS_Store` | 1 | ❌ コミットしない |

**`git add .` や `git add -A` は使わないでください。** 69件のゴミが一緒に入ります。

---

## 手順

```bash
cd ~/Desktop/AINet-DB-Sakhawi
```

### 1. ゴミの掃除と .gitignore の作成

```bash
# FUSE残骸と .DS_Store を削除
find . -name '.fuse_hidden*' -delete
find . -name '.DS_Store' -delete

# 一時退避フォルダを削除
rm -rf _to_delete

# 今後のために .gitignore を作成（現在ありません）
cat > .gitignore <<'EOF'
.DS_Store
.fuse_hidden*
_to_delete/
EOF
```

### 2. 状態確認（ここで100件+文書類だけになっているはず）

```bash
git status --short | awk '{print $1}' | sort | uniq -c
```

**期待値: `M` が 33、`??` が 5前後**（`.gitignore` / corpus txt / CHANGELOG / docs / records_B54）。
`??` に `.fuse_hidden` が残っていたら手順1をやり直してください。

### 3. B54ブランチを作成

```bash
git checkout -b B54
```

### 4. ステージング（明示的に指定）

```bash
git add Individuals/
git add 0__DawForAIND_renumbered_B54.txt
git add CHANGELOG/CHANGELOG_B54_append.md
git add docs/HANDOVER_20260821_v13_20.md
git add docs/records_B54/
git add .gitignore
```

### 5. 内容の最終確認

```bash
git status --short
git diff --cached --stat | tail -5
```

**期待値: 133ファイル前後**（新規100 + 修正33 + 文書類）。

### 6. コミット

```bash
git commit -m "B54: 校閲完了（実項97/REF化3/重複投入0）

- 新規TMP 119件（P42/N14/L16/I10/O22/T10/S5）
- corpus: 0__DawForAIND_renumbered_B54.txt（\$\$\$ 1421）
- REF化3件: D03054→D07104 / D05619→D05422 / D05702→D05686
- 毒wd 2件是正: Q1065604→#AIND-D06305+wd:Q557847 / Q286307→wd:Q441410
- 裁定適用（§D-1〜§D-12・§A-4・§I）: 裁定記録_B54.md
  - ابن فهد 三者を corpus 本文で確定し没年で振り分け（既存repo 4件も遡及是正）
  - TMP-O-00044 → TMP-O-00050 統合（既存repo 17件付替え）
  - cert運用 3段階案を確立（زعم=low / قال أنه・بلغني=medium / يحرر=low+possible_identity）
- 破損XML 13件を修復 → repo全1584ファイルが well-formed に
- HANDOVER v13.20"
```

### 7. push

```bash
git push -u origin B54
```

### 8. PR作成（B44=PR#53 と同じ流れ）

```bash
gh pr create --base main --head B54 \
  --title "B54: 校閲完了（実項97/REF化3）+ 既存repo是正33件" \
  --body "詳細は docs/records_B54/ を参照。

## 本バッチ
- 実項97 / REF化3 / 重複投入0、新規TMP 119件
- 基準corpus を 0__DawForAIND_renumbered_B54.txt に更新（\$\$\$ 1421）

## 既存repoへの是正（33件）
- ابن فهد の年代矛盾 4件（D00449/D01689/D01977/D02535）
- TMP-O-00044→TMP-O-00050 統合 16件
- 破損XML修復 13件 → **repo全1584ファイルが well-formed に**

## Waka側に残る作業
- ID-Master への裁定書き戻し（docs/records_B54/ID-Master修正指示_B54.md）
- prompt_analyze.txt / app.py / precheck の cert 対応（同 cert運用_実装仕様_B54.md）"
```

`gh` が未設定なら、push 後にブラウザで作成してください。

---

## 補足: ブランチについて

現在 **`B49` ブランチ上**にいます。B49-53の成果（`4d7846d`）がこのブランチの先端です。
`git checkout -b B54` は **B49の先端から分岐**するので、B49-53の内容を含んだ状態でB54が乗ります。

B49-53が既に main にマージ済みなら、先に main を取り込んでから分岐するほうが綺麗です。

```bash
git fetch origin
git log --oneline origin/main -1     # main の先端を確認
```

`4d7846d` が `origin/main` に入っていれば:

```bash
git checkout main && git pull && git checkout -b B54
```

としてから手順4に進んでください。**入っていなければ現状のまま（B49から分岐）で問題ありません。**
