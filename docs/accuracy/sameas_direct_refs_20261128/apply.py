#!/usr/bin/env python3
"""Records that point at a person by a Wikidata number although the person has a main entry
and the number is in the registry's same_as column: re-point ref / active / passive to the AIND number.
WK 裁定 2026-11-28 (AIND 番号を正とする。外部 ID は典拠表の same_as 欄にだけ持つ).

  apply.py report   write changes.tsv, change nothing
  apply.py apply    write changes.tsv and update the records
"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'authority'))
import build_authority as B

DATE = '2026-11-28'
TAG = re.compile(r'<(\w+)\b[^<>]*>')
ATTR = re.compile(r'\b(ref|active|passive)="([^"]*)"')

def main(mode):
    same = {}
    for path in (B.REG, B.ENT):
        for r in B.read_tsv(path):
            for tok in (r.get('same_as') or '').split():
                same[tok] = r['id']
    rows, edits = [], {}
    for d, _, fs in sorted(os.walk(os.path.join(ROOT, 'Individuals'))):
        for f in sorted(fs):
            if not f.endswith('.xml'):
                continue
            p = os.path.join(d, f); t = open(p, encoding='utf-8', newline='').read()
            own = re.search(r'<person\b[^>]*xml:id="([^"]+)"', t)[1]
            done = []
            def tag(m):
                def attr(a):
                    vals = a[2].split()
                    new = ['#' + same[v] if v in same else v for v in vals]
                    for v, n in zip(vals, new):
                        if v != n:
                            rows.append(dict(record=own, element=m[1], attribute=a[1], old=v, new=n)); done.append((v, n))
                    return f'{a[1]}="{" ".join(new)}"'
                return ATTR.sub(attr, m[0])
            new = TAG.sub(tag, t)
            if done:
                what = '、'.join(f'{v} → {n}' for v, n in sorted(set(done)))
                note = (f'外部 ID の一本化（WK 裁定 {DATE}）。参照を Wikidata 番号から本伝の AIND 番号に付け替えた（{len(done)}か所：{what}）。'
                        '人物と Wikidata 番号の対応は典拠表 authority/persons_registry.tsv の same_as 欄に持つ。')
                stmt = (f'    <respStmt><resp xml:lang="ja">修正</resp><note xml:lang="ja">{note}</note>'
                        f'<persName>claude-fable-5-2-sameas-20261128</persName><date when="{DATE}"/></respStmt>\n')
                i = new.rindex('</person>')
                edits[p] = new[:i] + stmt + new[i:]
    if rows or mode == 'apply':
        open(os.path.join(HERE, 'changes.tsv'), 'w', encoding='utf-8', newline='').write(
            B.dump(rows, ['record', 'element', 'attribute', 'old', 'new']))
    print('re-pointed', len(rows), 'records', len(edits))
    if mode == 'apply':
        for p, t in edits.items():
            open(p, 'w', encoding='utf-8', newline='').write(t)

if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] not in ('report', 'apply'):
        sys.exit(__doc__)
    main(sys.argv[1])
