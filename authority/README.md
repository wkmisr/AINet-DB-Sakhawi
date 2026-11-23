# authority/ — 人物の典拠表（2026-11-23 草案）

同じデータを複数の場所に持たない、という原則で作っている。

| ファイル | 性格 | 中身 |
|---|---|---|
| `persons_registry.tsv` | **正本**（人の裁定を記録する） | ほかのどこにも書かれていない事実だけ：状態（active／transfer／merged／retired／needs-ruling）、統合先・転送先、別名、Wikidata、注記 |
| `headings_index.tsv` | 派生（手で編集しない） | corpus の全見出し（12桁ID、AIND番号、種別、行、立項番号、見出しの語句） |
| `persons_view.tsv` | 派生（手で編集しない） | AIND番号ごとに1行。検索・候補引き用。見出しは corpus から、生没年・学派は処理済みレコード（XML）から、状態は registry から取る |

- 見出しの語句・12桁ID・種別の正本は corpus。生没年・学派の正本は処理済みレコード。registry には写さない。
- 派生ファイルは `python3 tools/authority/build_authority.py view` で作り直す。`check` は、派生ファイルが古い場合と registry に矛盾がある場合に失敗する。
- registry は旧・人物一覧（Google シート「1. Sakhawi_PersonList」、2026-11-23 取得）から一度だけ作った（`init`）。担当者・Token の列は移していない（シートに残る）。
- 生没年・学派は registry に持たない。処理済みの項はレコードから出す。未処理の項は、本文から機械で拾った値を派生の表に出す予定（未実装）。旧・人物一覧の値は移していない。
