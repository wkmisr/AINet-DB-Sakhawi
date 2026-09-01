#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
precheck_corpus_anomalies.py  v1.0  (2026-08-31)

AINet-DB: corpus 側の異常記号を一括で洗い出し、分類し、作業可否を判定する。

目的:
  アルバイトが「記号が入っているので作業しませんでした」と個別報告してくる状況をなくす。
  記号の意味と作業可否をあらかじめ機械判定し、
    ①作業者には記号を除去したクリーン版を渡す
    ②本当に人間の判断が要るものだけを一覧にして熊倉へ回す
  という2系統に分ける。

使い方:
  python3 precheck_corpus_anomalies.py --corpus 0__DawForAIND_renumbered_B54.txt \
      --out-tsv corpus_anomalies.tsv --out-clean corpus_clean_for_workers.txt \
      [--out-md corpus_anomalies_report.md]

判定表 (2026-08-31 時点):
  ┌──────────────┬────────────────────────────────┬──────────┐
  │ 記号          │ 意味                             │ 作業可否 │
  ├──────────────┼────────────────────────────────┼──────────┤
  │ ±±±          │ 語末に付く注記マーカー。            │ ◎ そのまま作業可 │
  │              │ 常に完全な単語の直後・語を分断しない │          │
  │ ★語★        │ 未採番見出しの境界マーカー          │ △ 別項として要採番 │
  │ ★ID_Missing★│ 同上（AIND番号なしの見出し）        │ △ 同上   │
  │ ★語?★       │ 校訂者の読み疑義（人間が入れた）     │ ○ 疑義語以外は作業可 │
  │ ... / …      │ 原文の欠落 (lacuna)              │ ○ 欠落部を空にして作業可 │
  │ =NNN above?  │ 人間の照合メモ                    │ ○ メモを外して作業可 │
  │ 全角スペース   │ 変換ノイズ                       │ ◎ 半角化して作業可 │
  └──────────────┴────────────────────────────────┴──────────┘

  ◎ = 作業者は無視してよい（クリーン版では自動除去）
  ○ = 作業者は記号部分だけ空欄にして作業を続行してよい
  △ = 構造の問題。採番が要るので熊倉へ回す
"""
import re, sys, argparse, json, collections

ENTRY_RE = re.compile(r'^###\$(AIND-D\d+[a-z]?|\d+)?\s*\|?\s*(\d+)?\$#', re.M)

# ---------- 分類 ----------
RULES = [
    # (キー, 正規表現, 意味, 作業可否, 作業者への指示)
    ('PLUSMIN', re.compile(r'±+'),
     '語末に付く注記マーカー（語を分断しない）', '◎',
     '無視してよい。記号を取り除いた語がそのまま正しい読み。'),
    ('STAR_IDMISSING', re.compile(r'★\s*ID_Missing\s*★'),
     'AIND番号を持たない見出しの開始位置', '△',
     '作業しない。別項として採番が必要なので熊倉へ回す。'),
    ('STAR_QUERY', re.compile(r'★[^★]{0,80}[?؟][^★]{0,10}★'),
     '校訂者が読みに疑義を付した語', '○',
     '疑義語は #NEEDID のまま残し、他の部分は通常どおり作業する。'),
    ('STAR_HEADWORD', re.compile(r'★[^★]{1,40}★'),
     '未採番見出しの境界（1ブロックに複数見出しが同居）', '△',
     '作業しない。ブロック内の2件目以降は別項として採番が必要。'),
    ('STAR_ORPHAN', re.compile(r'★'),
     '対になっていない孤立した★（変換ノイズ）', '◎',
     '無視してよい。'),
    ('ELLIPSIS', re.compile(r'\.\.\.|…'),
     '原文の欠落（lacuna）', '○',
     '欠落部は情報なしとして扱い、該当要素を立てずに作業する。'),
    ('XREF_MEMO', re.compile(r'=\s*\d+\s*(?:above|below)\s*\??'),
     '人間が入れた照合メモ', '○',
     'メモは本文ではない。除いて作業し、メモ内容は熊倉へ報告。'),
    ('IDEOSPACE', re.compile(r'　'),
     '全角スペース（変換ノイズ）', '◎', '半角スペースとして扱う。'),
    ('FULLWIDTH_PAREN', re.compile(r'[（）]'),
     '全角括弧（変換ノイズ）', '◎', '半角括弧として扱う。'),
    ('DOLLAR3_STUB', re.compile(r'###\$\d+\$#\s*\$\$\$'),
     '処理済みの転送見出し（$$$）が同じブロックに同居', '◎',
     '処理済みなので作業不要。ブロック先頭の項だけ作業すればよい。'),
]

# クリーン版の変換
#  ◎ … 黙って除去／正規化する（作業者は存在すら意識しなくてよい）
#  ○△ … 除去せず、日本語の自己説明タグに置き換える（見落とし防止）
STRIP = [
    (re.compile(r'±+'), ''),                       # ◎ 除去
    (re.compile(r'　'), ' '),                       # ◎ 半角化
    (re.compile(r'（'), '('), (re.compile(r'）'), ')'),
    (re.compile(r'★\s*ID_Missing\s*★'), '\n【別項・要採番】'),          # △
    (re.compile(r'★([^★]{0,80}[?؟][^★]{0,10})★'), r'【読み疑義:\1】'),   # ○
    (re.compile(r'★([^★]{1,40})★'), r'\n【別項・要採番】\1'),            # △
    (re.compile(r'★'), ''),                        # ◎ 孤立★は除去
    (re.compile(r'=\s*(\d+)\s*(above|below)\s*\??'), r'【照合メモ:\1\2】'),  # ○
    (re.compile(r'\.\.\.|…'), '【原文欠落】'),      # ○
]

def split_entries(text):
    """corpus を {AIND-ID or 疑似ID: 本文} に分割"""
    starts = []
    for m in re.finditer(r'^###\$(AIND-D\d+[a-z]?)\s*\|', text, re.M):
        starts.append((m.start(), m.group(1)))
    out = []
    for i, (pos, aid) in enumerate(starts):
        end = starts[i+1][0] if i+1 < len(starts) else len(text)
        out.append((aid, text[pos:end]))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--corpus', required=True)
    ap.add_argument('--out-tsv', default='corpus_anomalies.tsv')
    ap.add_argument('--out-clean', default=None)
    ap.add_argument('--out-md', default=None)
    a = ap.parse_args()

    text = open(a.corpus, encoding='utf-8').read()
    entries = split_entries(text)

    rows = []
    per_type = collections.Counter()
    per_verdict = collections.Counter()
    hit_entries = set()

    for aid, body in entries:
        # 見出し行の ###$...$# 部分は判定対象外にする
        payload = body.split('$# $', 1)[-1] if '$# $' in body else body
        claimed = set()
        for key, rx, meaning, verdict, instruction in RULES:
            for m in rx.finditer(payload):
                span = (m.start(), m.end())
                # 上位ルールが既に拾った範囲は二重計上しない
                if any(s <= span[0] < e for s, e in claimed):
                    continue
                claimed.add(span)
                s = max(0, m.start()-45); e = min(len(payload), m.end()+45)
                ctx = re.sub(r'\s+', ' ', payload[s:e]).strip()
                rows.append([aid, key, meaning, verdict, m.group(0)[:40], ctx, instruction])
                per_type[key] += 1
                per_verdict[verdict] += 1
                hit_entries.add(aid)

    with open(a.out_tsv, 'w', encoding='utf-8') as f:
        f.write('AIND-ID\t型\t意味\t作業可否\t該当箇所\t前後文脈\t作業者への指示\n')
        for r in rows:
            f.write('\t'.join(x.replace('\t', ' ') for x in r) + '\n')

    if a.out_clean:
        clean = text
        for rx, rep in STRIP:
            clean = rx.sub(rep, clean)
        open(a.out_clean, 'w', encoding='utf-8').write(clean)

    print(f'corpus 総項数        : {len(entries)}')
    print(f'記号を含む項         : {len(hit_entries)}  ({len(hit_entries)*100/len(entries):.1f}%)')
    print(f'検出箇所 合計        : {len(rows)}')
    print()
    print('型別:')
    for k, v in per_type.most_common():
        meaning = next(r[2] for r in RULES if r[0] == k)
        verdict = next(r[3] for r in RULES if r[0] == k)
        print(f'  {verdict} {k:16s} {v:5d}  {meaning}')
    print()
    print('作業可否別（箇所数）:')
    for k in ['◎', '○', '△']:
        print(f'  {k} {per_verdict.get(k,0)}')
    need = sorted({r[0] for r in rows if r[3] == '△'})
    print()
    print(f'★人間の判断が要る項（△）: {len(need)} 項')

    if a.out_md:
        with open(a.out_md, 'w', encoding='utf-8') as f:
            f.write('# corpus 異常記号インベントリ\n\n')
            f.write(f'- 対象: `{a.corpus}`（{len(entries)}項）\n')
            f.write(f'- 記号を含む項: **{len(hit_entries)}**／検出箇所 **{len(rows)}**\n')
            f.write(f'- **人間の判断が要る項（△）: {len(need)}**、残りは作業続行可\n\n')
            f.write('## 型別集計\n\n| 可否 | 型 | 箇所 | 意味 |\n|---|---|---|---|\n')
            for k, v in per_type.most_common():
                meaning = next(r[2] for r in RULES if r[0] == k)
                verdict = next(r[3] for r in RULES if r[0] == k)
                f.write(f'| {verdict} | `{k}` | {v} | {meaning} |\n')
            f.write('\n## 人間の判断が要る項（△）\n\n')
            for aid in need:
                f.write(f'- `{aid}`\n')
    return 0

if __name__ == '__main__':
    sys.exit(main())
