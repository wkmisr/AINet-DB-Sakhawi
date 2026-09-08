# AINet Browser — 再ビルド手順

Artifact URL（固定・republish で更新）: https://claude.ai/code/artifact/364e6aac-07cc-46b0-9d5f-7e92190056f4
（favicon 📜、タイトル「AINet Browser」。v12 = 2026-09-08 corpus 同期後）

XML 1,983 件を JSON にまとめ、単一 HTML（約 6.8 MB）として Artifact に公開する静的ブラウザ。
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

## 期待値（2026-09-08、1,983 件）
self_hit 1967 / person_hit 2880 / place_hit 1273 / org_hit 206 / office_hit 515 / text_hit 374

## 備考
- 原文は XML の `<note type="source" xml:lang="ar">` から取る。corpus_index は本人見出し（selfspan）照合にのみ使用。
- `app_template.html` を編集すれば UI を変えられる（`__DATA__` を残すこと）。
- 原文中の `%~%` は詩の半句区切り → 詩形で表示。
