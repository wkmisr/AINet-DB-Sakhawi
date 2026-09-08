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

## 期待値（2026-09-08 v14、2,143 件）
self_hit 2127 / person_hit 3049 / place_hit 1332 / org_hit 210 / office_hit 532 / text_hit 397
（v13・2,073 件: self 2057、他は同じ）
（v12・1,983 件: self 1967 / person 2880 / place 1273 / org 206 / office 515 / text 374）

## 備考
- ビルドは device 側（`docs/_work/browser_build/`、git 管理外）でも実行できる: idmaster.tsv を置き、`cp ../../browser/*.py ../../browser/app_template.html .` してから上記 3 コマンド。生成した ainet_browser.html を cloud に stage して Artifact に republish（2026-09-08 実績）。
- 原文は XML の `<note type="source" xml:lang="ar">` から取る。corpus_index は本人見出し（selfspan）照合にのみ使用。
- `app_template.html` を編集すれば UI を変えられる（`__DATA__` を残すこと）。
- 原文中の `%~%` は詩の半句区切り → 詩形で表示。
