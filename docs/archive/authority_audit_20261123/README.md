# 2026-11-23 の点検の作業一式

- `audit.py`：人物一覧・ID-Master・corpus・XML の突き合わせ（結果は `findings.tsv`）。
- `xcheck.py`：レコードの語と典拠表の表記の突き合わせ（結果は `label_mismatch.tsv`）。
- `mkxlsx.py`・`view_xlsx.py`：結果と典拠表を Excel にする。

スクリプト中のパスは作業時の環境のもの（`/home/claude/...`）。入力の二つのシートは Drive から CSV で取得した。
