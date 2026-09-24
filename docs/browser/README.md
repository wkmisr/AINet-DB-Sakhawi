# AINet Browser — 再ビルド手順

Artifact URL（固定・republish で更新）: https://claude.ai/code/artifact/364e6aac-07cc-46b0-9d5f-7e92190056f4
（favicon 📜、タイトル「AINet Browser」。v14 = 2026-09-08 XML_Limbo 70件収録後、2,143 件）

XML 2,143 件を JSON にまとめ、単一 HTML（約 7.3 MB）として Artifact に公開する静的ブラウザ。
チャットを変えても、この 4 ファイルと下の手順があれば同じ URL に再公開できる。

## 入力
- `Individuals/`（repo）
- `idmaster.tsv` — ID-Master（Google Sheet「2. ID-Master」）の TSV エクスポート（Drive の download_file_content → base64 デコード）。列: B=Category, C=Arabic, D=Latin, E=ID, F=Note
- corpus txt（repo 直下 `0__DawForAIND_renumbered_B54_split20260905.txt`）

## 手順（cloud 側の作業ディレクトリで）
```
python3 make_corpus_index.py <corpus.txt> corpus_index.json      # AIND -> 本文（見出し照合用）
python3 build.py <Individuals dir> idmaster.tsv corpus_index.json  # -> data.json（統計を表示）
python3 assemble.py data.json                                      # app_template.html の __DATA__ に埋め込み -> ainet_browser.html
```
その後 Artifact ツールで `ainet_browser.html` を上記 URL に `url` 指定で republish する
（別チャットからは先に `action: read` で最新版を読み込んでから publish。favicon は省略）。

## 期待値（2026-09-25 v17、2,595 件）— B88（159件）＋規則22-1 遡及点検＋Waka 裁定反映後
self_hit 2574 / person_hit 3907 / place_hit 1651 / org_hit 263 / office_hit 637 / text_hit 496
（self_miss 21 / person_miss 580 / place_miss 209 / org_miss 652 / office_miss 740 / text_miss 226。place_miss が 336→209 に減ったのは規則22-1 で原文に根拠のない placeName を除去したため。
idmaster.tsv＝シート実物 9/24（7,682行）＋B87 51件＋B88 105件＋Waka 照合の wd 3件 = 7,841行）

## 期待値（2026-09-21 v16、2,436 件）— B87（77件）収録後
self_hit 2419 / person_hit 3519 / place_hit 1541 / org_hit 242 / office_hit 613 / text_hit 455
（self_miss 17 / person_miss 504 / place_miss 336 / org_miss 605 / office_miss 699 / text_miss 207。data.json 8,447,787 bytes / ainet_browser.html 8,487,073 bytes）
（idmaster は `docs/_work/browser_build/idmaster.tsv`＝シート実物 `docs/_work/idmaster_working_20260918.tsv`（7,681行）に `docs/records_B87/TMP登録_B87.tsv` の51件（取り下げ1行を除く）を結合した 7,732 行。B87 分は Waka 未貼付のため結合が必要）

## 期待値（2026-09-18 v15b、2,359 件）— entity alignment 精度修正後
self_hit 2343 / person_hit 3404 / place_hit 1460 / org_hit 237 / office_hit 596 / text_hit 430
（build.py の三点修正: (1) 候補文字列のクリーニング（ويعرف بـ 等の「〜として知られる」節の分割・丸括弧/ダッシュ注記の分離）と STOP 語彙による句マッチ抑止、
(2) selftoks / 除外ゾーンを full[0] だけでなく本人の全 persName 形（nisbah/laqab/shuhrah/kunyah）＋本人の office/affiliation から構築、
(3) マッチ窓の左方向拡張（'بن مفلح' → 'الشرف بن مفلح'）。person +15 / office +24 / org +8、失われた非 person span は 1 件のみ）

## 期待値（2026-09-18 v15、2,359 件）
self_hit 2343 / person_hit 3389 / place_hit 1460 / org_hit 229 / office_hit 572 / text_hit 430
（B56-58・B84-85 反映後 ＋ affiliation/state 二重記録 67 件（61 ファイル）削除後 ＋ 原文 note 欠落55件補填後 ＋ B86 の20件収録後。idmaster は `docs/_work/idmaster_ext_20260918.tsv`＝9/16版に未貼付TMP 2本を結合したもの を使用）
（参考・B86 収録前の中間ビルド 2,339 件: self_hit 2268 / person_hit 3271 / place_hit 1407 / org_hit 222 / office_hit 550 / text_hit 416）

## 期待値（2026-09-08 v14、2,143 件）
self_hit 2127 / person_hit 3049 / place_hit 1332 / org_hit 210 / office_hit 532 / text_hit 397
（v13・2,073 件: self 2057、他は同じ）
（v12・1,983 件: self 1967 / person 2880 / place 1273 / org 206 / office 515 / text 374）

## 備考
- ビルドは device 側（`docs/_work/browser_build/`、git 管理外）でも実行できる: idmaster.tsv を置き、`cp ../../browser/*.py ../../browser/app_template.html .` してから上記 3 コマンド。生成した ainet_browser.html を cloud に stage して Artifact に republish（2026-09-08 実績）。
- 原文は XML の `<note type="source" xml:lang="ar">` から取る。corpus_index は本人見出し（selfspan）照合にのみ使用。
- `app_template.html` を編集すれば UI を変えられる（`__DATA__` を残すこと）。
- 原文中の `%~%` は詩の半句区切り → 詩形で表示。
