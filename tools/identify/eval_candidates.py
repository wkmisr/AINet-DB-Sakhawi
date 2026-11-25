"""Measure the name-search tool against reviewed relations (design v5, 4.2; measurement 11).

Gold = every <relation> in Individuals/ whose one end is the record itself and whose other end
is an AIND-D person other than the record, with an Arabic <desc>. The <desc> is used as the query.
Writes a TSV of every case (rank, or blank if not in top 100) for inspection.
Usage: python3 tools/identify/eval_candidates.py [out.tsv]
"""
import sys, os, re, glob, collections
sys.path.insert(0, os.path.dirname(__file__))
import aind_names as A
import xml.etree.ElementTree as ET

KIN = {'father', 'mother', 'son', 'daughter', 'brother', 'sister', 'grandfather', 'grandmother', 'grandson',
       'granddaughter', 'maternal_grandfather', 'uncle', 'paternal_uncle', 'maternal_uncle', 'maternal_aunt',
       'paternal_aunt', 'aunt', 'cousin', 'siblings_child', 'spouse', 'father-in-law', 'son-in-law',
       'brother-in-law', 'daughter-in-law', 'mother-in-law', 'relative', 'ancestor', 'descendant'}


def gold():
    out = []
    for f in sorted(glob.glob(os.path.join(A.REPO, 'Individuals', '*', '*.xml'))):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        rid = root.get('{http://www.w3.org/XML/1998/namespace}id')
        for r in root.iter('relation'):
            a, p = (r.get('active') or '').lstrip('#'), (r.get('passive') or '').lstrip('#')
            if rid not in (a, p):
                continue
            other = p if a == rid else a
            if not other.startswith('AIND-D') or other == rid:
                continue
            d = r.find('desc')
            if d is None or not (d.text or '').strip():
                continue
            out.append((rid, other, r.get('subtype') or '', d.text.strip()))
    # one case per (record, other, desc)
    seen, uniq = set(), []
    for g in out:
        k = (g[0], g[1], A.norm(g[3]))
        if k not in seen:
            seen.add(k); uniq.append(g)
    return uniq


def main(outpath=None):
    ix = A.Index()
    G = gold()
    ranks = []
    rows = []
    for rid, other, st, desc in G:
        if other not in ix.pos:
            rows.append((rid, other, st, desc, 'not_in_corpus')); continue
        res, mf = ix.search(desc, k=100, exclude={rid})
        ids = [p for p, s, w in res]
        rk = ids.index(other) + 1 if other in ids else None
        res2, _ = ix.presearch(rid, desc, kind=st if st in A.KIN_PATTERNS else None, k=100)
        ids2 = [p for p, s, w in res2]
        rk2 = ids2.index(other) + 1 if other in ids2 else None
        grp = 'kin' if st in KIN else 'other'
        label = '|' in desc or len(A.norm(desc).split()) == 1 and st == 'teacher'
        ranks.append((grp, rk, rk2, label))
        rows.append((rid, other, st, desc, rk or '', rk2 or '', 'label' if label else 'name'))
    def report(sel, label):
        n = len(sel)
        if not n:
            return
        line = [f'{label}: n={n}']
        for c in (1, 5, 20, 100):
            line.append(f'top{c} {100*sum(1 for r in sel if r and r <= c)/n:.1f}%')
        print('  '.join(line))
    print('-- name search only')
    report([r for g, r, r2, l in ranks], 'all')
    report([r for g, r, r2, l in ranks if not l], 'desc is a name phrase')
    report([r for g, r, r2, l in ranks if not l and g == 'kin'], '  kin')
    report([r for g, r, r2, l in ranks if not l and g == 'other'], '  other')
    print('-- presearch (name + genealogy + neighbour)')
    report([r2 for g, r, r2, l in ranks], 'all')
    report([r2 for g, r, r2, l in ranks if not l], 'desc is a name phrase')
    report([r2 for g, r, r2, l in ranks if not l and g == 'kin'], '  kin')
    report([r2 for g, r, r2, l in ranks if not l and g == 'other'], '  other')
    report([r2 for g, r, r2, l in ranks if l], 'desc is a label (e.g. "أخذ | الأخذ")')
    print('records:', len({g[0] for g in G}), 'cases:', len(G), 'not in corpus:', sum(1 for r in rows if r[4] == 'not_in_corpus'))
    if outpath:
        with open(outpath, 'w', encoding='utf-8') as fh:
            fh.write('record\tgold\tsubtype\tdesc\trank_name\trank_presearch\tdesc_kind\n')
            for r in rows:
                fh.write('\t'.join(map(str, r)) + '\n')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else None)
