# authority/ — 典拠表（2026-11-23 草案）

同じデータを複数の場所に持たない、という原則で作っている。

## 正本（人の裁定を記録する。ほかのどこにも書かれていない事実だけを持つ）

| ファイル | 中身 |
|---|---|
| `persons_registry.tsv` | 人物。AIND番号（伝記のある人物）、TMP-P番号（伝記のない人物）、Wikidata番号の人物を一つの表に持つ。列：状態（active／transfer／merged／retired）、統合先・転送先、名前（AIND番号以外のみ。AIND番号の名前は corpus の見出しが正本）、別名、対応する外部ID、注記、発行・修正の履歴 |
| `entities_registry.tsv` | 人物以外（ニスバ、地名、施設、官職、著作、学問・学習方法）。列：分類、状態、統合先、正式な表記、ラテン文字表記、異表記、対応する外部ID、下位分類（官職の区分、学習の方法／分野）、注記、履歴 |

## 派生（スクリプトが作る。手で編集しない）

| ファイル | 中身 |
|---|---|
| `headings_index.tsv` | corpus の全見出し |
| `persons_view.tsv` | 人物ごとに1行の検索用の表。見出しは corpus、生没年・学派は処理済みレコード、状態は registry から取る。`cited_by` はその人物を参照するレコードの数 |
| `entities_view.tsv` | 人物以外の検索用の表。`use_count` は参照するレコードの数 |
| `unresolved_refs.tsv` | レコードの参照のうち、典拠表で有効なIDに行き着かないもの（未登録、統合済み、転送項） |

- `python3 tools/authority/build_authority.py view` で派生ファイルを作り直す。`check` は、派生ファイルが古い場合と registry に矛盾がある場合に失敗する。
- 生没年・学派は registry に持たない。登録者も持たない（今後は git の履歴に残る。過去分は凍結したシートにある）。出現箇所の一覧も持たない（レコードから数える）。
- IDの書き方はレコードの参照と同じにしている（`wd:Q…`、`gn:…`、`TMP-…`、`AIND-D…`）。

## 経緯

- `persons_registry.tsv` は Google シート「1. Sakhawi_PersonList」（2026-11-23 取得）から `init` で一度だけ作った。担当者・Token・生没年・学派の列は移していない。
- `import_idmaster.py` で Google シート「2. ID-Master」（2026-11-23 取得）を取り込んだ。Person 行のうちAIND番号のものは、その人物の別名と注記に移した。注記に「旧TMP-P-…から統合」とあるものは、旧番号を `merged` の行として復元した。
- そのまま取り込めなかった行は `import_idmaster_rulings.tsv` にある（裁定が済んだら消す）。
