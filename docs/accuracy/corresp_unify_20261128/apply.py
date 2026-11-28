#!/usr/bin/env python3
"""Move external IDs out of the records' corresp attribute into the registry's same_as column (WK ruling 2026-11-28).

corresp sat on relation / persName / person elements in two forms:
  corresp="wd:Q…"      the Wikidata number of the person the element points to (the "D-3" form)
  corresp="#AIND-D…"   the same AIND number as ref / active on the same element (no meaning)
Identity with an external ID is a statement about the person, made once, in authority/persons_registry.tsv
(same_as). Mentions only say whom they point to (ref / active / passive).

This script removes every corresp attribute from the records, adds a respStmt to each changed record,
and fills same_as for the persons whose number was only in the records. The pairs in PAIRS were checked
against the main entry in the corpus and against docs/authority/wd_entities.tsv.

  apply.py report   write changes.tsv, change nothing
  apply.py apply    write changes.tsv, update the records and the registry
"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'authority'))
import build_authority as B

DATE = '2026-11-28'
PAIRS = {  # Wikidata number -> the person's main entry
    'wd:Q257745': 'AIND-D09832',    # العيني
    'wd:Q6534585': 'AIND-D05895',   # ابن الملقن
    'wd:Q557847': 'AIND-D06305',    # قايتباي
    'wd:Q286532': 'AIND-D02110',    # إينال
    'wd:Q12198099': 'AIND-D00207',
    'wd:Q559146': 'AIND-D01845',
    'wd:Q2637299': 'AIND-D00401',
    'wd:Q561219': 'AIND-D02400',    # جهانشاه
    'wd:Q85461758': 'AIND-D10669',  # ابن قاضي شهبة
    'wd:Q12219083': 'AIND-D06729',  # الشمس البساطي
    'wd:Q6537956': 'AIND-D07808',   # ابن ناصر الدين
    'wd:Q6798541': 'AIND-D05849',   # السراج البلقيني
}
SULTANS = {  # corresp carried the AIND number itself; the Wikidata number comes from the handover notes and the ledger
    'AIND-D02423': 'wd:Q647942',    # جقمق
    'AIND-D02168': 'wd:Q557812',    # برسباي
    'AIND-D03298': 'wd:Q553204',    # شاه رخ
    'AIND-D06160': 'wd:Q698037',    # فرج بن برقوق
}
SULTAN_SOURCE = {  # where the number came from, for the registry's history (it was not in the records)
    'AIND-D02423': '引き継ぎ v13.15 の D-3形式の記録と台帳 wd_entities.tsv から。レコードにはなかった',
    'AIND-D02168': '引き継ぎ v13.18 の記録と台帳 wd_entities.tsv から。レコードにはなかった',
    'AIND-D03298': '引き継ぎ v13.15 の D-3形式の記録と台帳 wd_entities.tsv から。レコードにはなかった',
    'AIND-D06160': '台帳 wd_entities.tsv から。レコードにも引き継ぎにも記録はなかった',
}
TAG = re.compile(r'<(\w+)\b([^<>]*?)\s+corresp="([^"]*)"([^<>]*)>')
NOTE = ('外部 ID の一本化（WK 裁定 {d}）。corresp 属性を外した（{n}か所：{what}）。'
        '人物と Wikidata 番号の対応は典拠表 authority/persons_registry.tsv の same_as 欄に持つ。')

def main(mode):
    reg = B.read_tsv(B.REG); R = {r['id']: r for r in reg}
    rows, edits = [], {}
    for d, _, fs in sorted(os.walk(os.path.join(ROOT, 'Individuals'))):
        for f in sorted(fs):
            if not f.endswith('.xml'):
                continue
            p = os.path.join(d, f); t = open(p, encoding='utf-8').read()
            own = re.search(r'AIND-D\d{5}[a-z]?', f)[0]; vals = []
            def sub(m):
                el, co = m[1], m[3]
                attrs = dict(re.findall(r'([\w:-]+)="([^"]*)"', m[2] + m[4]))
                assert el in ('relation', 'persName', 'person'), (f, el)
                if el == 'person':
                    who = attrs['xml:id']; assert PAIRS[co] == who, (f, co)
                elif co.startswith('wd:'):
                    who = PAIRS[co]
                    assert '#' + who in (attrs.get('ref'), attrs.get('active'), attrs.get('passive')), (f, co)
                else:
                    who = co.lstrip('#')
                    assert co in (attrs.get('ref'), attrs.get('active')), (f, co)
                rows.append(dict(record=own, element=el, person=who, corresp=co,
                                 kind='wd' if co.startswith('wd:') else 'same AIND as ref/active'))
                vals.append(co)
                return f'<{el}{m[2]}{m[4]}>'
            new = TAG.sub(sub, t)
            if vals:
                assert 'corresp="' not in re.sub(r'>[^<]*<', '><', new), f
                note = NOTE.format(d=DATE, n=len(vals), what='、'.join(sorted(set(vals))))
                stmt = (f'    <respStmt><resp xml:lang="ja">修正</resp><note xml:lang="ja">{note}</note>'
                        f'<persName>claude-fable-5-2-corresp-20261128</persName><date when="{DATE}"/></respStmt>\n')
                i = new.rindex('</person>')
                edits[p] = new[:i] + stmt + new[i:]
    add = {}
    for wd, aid in list(PAIRS.items()) + [(w, a) for a, w in SULTANS.items()]:
        cur = R[aid]['same_as']
        assert cur in ('', wd), (aid, cur, wd)
        if not cur:
            add[aid] = wd
    assert {r['person'] for r in rows if r['kind'] != 'wd'} <= set(SULTANS) | set(PAIRS.values())
    open(os.path.join(HERE, 'changes.tsv'), 'w', encoding='utf-8', newline='').write(
        B.dump(rows, ['record', 'element', 'person', 'corresp', 'kind']))
    print('corresp removed', len(rows), 'records', len(edits), 'same_as added', len(add), sorted(add.items()))
    if mode == 'apply':
        for p, t in edits.items():
            open(p, 'w', encoding='utf-8', newline='').write(t)
        for r in reg:
            if r['id'] in add:
                r['same_as'] = add[r['id']]
                r['history'] = (r['history'] + ' | ' if r['history'] else '') + \
                    f'{DATE} WK 裁定（外部 ID の一本化）: same_as に {add[r["id"]]}（{SULTAN_SOURCE.get(r["id"], "レコードの corresp から移した")}）'
        open(B.REG, 'w', encoding='utf-8', newline='').write(B.dump(reg, B.REG_COLS))

if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] not in ('report', 'apply'):
        sys.exit(__doc__)
    main(sys.argv[1])
