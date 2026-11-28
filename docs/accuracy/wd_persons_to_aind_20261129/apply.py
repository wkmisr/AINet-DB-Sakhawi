#!/usr/bin/env python3
"""Persons who have a biography but were registered, and pointed at, under a Wikidata number:
the AIND number becomes the only ID, the Wikidata number goes to same_as (WK 裁定 2026-11-29:
正規 ID は AIND 番号、wd は same_as).

  apply.py report   write changes.tsv, change nothing
  apply.py apply    update authority/persons_registry.tsv and the records, write changes.tsv

Registry: the AIND row gets the number in same_as and the name and aliases of the wd row as aliases;
the wd row becomes `merged` with the AIND row as target. Records: ref / active / passive that hold
the Wikidata number are re-pointed to the AIND number, and a respStmt is added.
"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'authority'))
import build_authority as B

DATE = '2026-11-29'
# wd row -> biography. Each pair was checked against the entry's text and the ledger's label (README).
PAIRS = {
    'wd:Q471116': 'AIND-D01068',     # ابن حجر العسقلاني
    'wd:Q4120128': 'AIND-D07578',    # السخاوي
    'wd:Q293604': 'AIND-D01026',     # المقريزي
    'wd:Q4664581': 'AIND-D03861',    # الزين العراقي
    'wd:Q4725309': 'AIND-D05078',    # النور الهيثمي
    'wd:Q57420531': 'AIND-D05432',   # ابن خطيب الناصرية
    'wd:Q8462': 'AIND-D02324',       # تمرلنك
    'wd:Q9294': 'AIND-D03796',       # ابن خلدون
    'wd:Q730299': 'AIND-D06334',     # قرا يوسف
    'wd:Q55672163': 'AIND-D00267',   # البرهان سبط ابن العجمي
    'wd:Q6758211': 'AIND-D06814',    # الجلال المحلي
    'wd:Q107246101': 'AIND-D03090',  # سعد الدين بن الديري
    'wd:Q31003843': 'AIND-D09233',   # العلاء البخاري
    'wd:Q6758203': 'AIND-D03709',    # الجلال البلقيني
}
# same_as was filled on 2026-11-28 (#126, #132); only the wd row was left active
ALREADY = {'wd:Q6798541': 'AIND-D05849', 'wd:Q12219083': 'AIND-D06729',
           'wd:Q6537956': 'AIND-D07808', 'wd:Q85461758': 'AIND-D10669'}
TAG = re.compile(r'<(\w+)\b[^<>]*>')
ATTR = re.compile(r'\b(ref|active|passive)="([^"]*)"')


def hist(r, text):
    r['history'] = (r['history'] + ' | ' if r['history'] else '') + f'{DATE} WK 裁定（正規 ID は AIND 番号）: {text}'


def main(mode):
    reg = B.read_tsv(B.REG); R = {r['id']: r for r in reg}
    for wd, aid in {**PAIRS, **ALREADY}.items():
        w, a = R[wd], R[aid]
        assert w['status'] == 'active' and a['status'] == 'active', (wd, aid)
        if wd in PAIRS:
            assert not a['same_as'], aid
            a['same_as'] = wd
        else:
            assert wd in a['same_as'].split(), (wd, aid)
        al = [x.strip() for x in a['aliases'].split('|') if x.strip()]
        for x in [w['name_ar']] + w['aliases'].split('|'):
            x = x.strip()
            if x and x not in al and x != a['name_ar']:
                al.append(x)
        a['aliases'] = ' | '.join(al)
        hist(a, (f'same_as に {wd}。' if wd in PAIRS else '') + f'{wd} の行の名前と別名を aliases に移した')
        w['status'], w['target'] = 'merged', aid
        hist(w, f'本伝 {aid} に統合（この番号は {aid} の same_as 欄に持つ）')
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
                    new = ['#' + PAIRS[v] if v in PAIRS else v for v in vals]
                    for v, n in zip(vals, new):
                        if v != n:
                            rows.append(dict(record=own, element=m[1], attribute=a[1], old=v, new=n)); done.append((v, n))
                    return f'{a[1]}="{" ".join(new)}"'
                return ATTR.sub(attr, m[0])
            new = TAG.sub(tag, t)
            if done:
                what = '、'.join(f'{v} → {n}' for v, n in sorted(set(done)))
                note = (f'正規 ID を AIND 番号に（WK 裁定 {DATE}）。伝記のある人物への参照を Wikidata 番号から AIND 番号に付け替えた（{len(done)}か所：{what}）。'
                        '人物と Wikidata 番号の対応は典拠表 authority/persons_registry.tsv の same_as 欄に持つ。')
                stmt = (f'    <respStmt><resp xml:lang="ja">修正</resp><note xml:lang="ja">{note}</note>'
                        f'<persName>claude-fable-5-2-wd2aind-20261129</persName><date when="{DATE}"/></respStmt>\n')
                i = new.rindex('</person>')
                edits[p] = new[:i] + stmt + new[i:]
    open(os.path.join(HERE, 'changes.tsv'), 'w', encoding='utf-8', newline='').write(
        B.dump(rows, ['record', 'element', 'attribute', 'old', 'new']))
    print('re-pointed', len(rows), 'records', len(edits))
    if mode == 'apply':
        open(B.REG, 'w', encoding='utf-8', newline='').write(B.dump(reg, B.REG_COLS))
        for p, t in edits.items():
            open(p, 'w', encoding='utf-8', newline='').write(t)


if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] not in ('report', 'apply'):
        sys.exit(__doc__)
    main(sys.argv[1])
