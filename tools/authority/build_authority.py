#!/usr/bin/env python3
"""Build the person authority files.

Source of truth (edited by people or by scripts that record a decision):
  authority/persons_registry.tsv, authority/entities_registry.tsv   only facts that live nowhere else
Generated on demand into authority/_generated/ (not committed, never edited):
  persons_view.tsv, entities_view.tsv   lookup tables: registry + names from the corpus + values from the records
  unresolved_refs.tsv                   references in the records that do not reach an active ID
  headings_index.tsv                    every corpus heading

  build_authority.py init <personlist.csv>   create the registry from the frozen PersonList (run once)
  build_authority.py view                    regenerate the derived files from corpus + XML + registry
  build_authority.py check                   exit 1 if the registries are inconsistent with the corpus or with each other
"""
import csv, os, re, sys, io
csv.field_size_limit(10**9)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CORPUS = [f for f in os.listdir(ROOT) if f.startswith('0__DawForAIND') and f.endswith('.txt')][0]
REG = os.path.join(ROOT, 'authority', 'persons_registry.tsv')
OUT = os.path.join(ROOT, 'authority', '_generated')
VIEW = os.path.join(OUT, 'persons_view.tsv')
HEADS = os.path.join(OUT, 'headings_index.tsv')
REG_COLS = ['id', 'status', 'target', 'name_ar', 'aliases', 'same_as', 'note', 'history']
ENT = os.path.join(ROOT, 'authority', 'entities_registry.tsv')
ENT_VIEW = os.path.join(OUT, 'entities_view.tsv')
UNRES = os.path.join(OUT, 'unresolved_refs.tsv')
ENT_COLS = ['id', 'category', 'status', 'target', 'label_ar', 'label_latn', 'variants', 'same_as', 'class', 'note', 'history']
REFRE = re.compile(r'(?:ref|active|passive)="([^"]*)"')
H = re.compile(r'^###\$(?:(AIND-D\w+) \| )?(\d{12})\$# (\$+) ?(.*)')
KIND = {'$': 'male', '$$': 'female', '$$$': 'transfer'}
AID = re.compile(r'AIND-D\d{5}[a-z]?')

def corpus():
    out = []
    with open(os.path.join(ROOT, CORPUS), encoding='utf-8') as f:
        for ln, l in enumerate(f.read().split('\n'), 1):
            m = H.match(l)
            if m:
                num = re.match(r'\s*(\d+)\s', m[4])
                out.append(dict(id=m[1] or '', n12=m[2], kind=KIND[m[3]], line=ln,
                                entry_no=num[1] if num else '',
                                heading=re.sub(r'^\s*\d+\s*', '', m[4]).replace('★', '').strip()))
    return out

def xmls():
    out = {}
    for d, _, fs in os.walk(os.path.join(ROOT, 'Individuals')):
        for f in fs:
            m = re.match(r'(REF_)?(AIND-D\w+?)_(\d{12})\.xml$', f)
            if not m:
                continue
            t = open(os.path.join(d, f), encoding='utf-8').read()
            def date(tag):
                x = re.search(r'<%s\b([^>]*)>' % tag, t)
                if not x:
                    return ''
                a = dict(re.findall(r'([\w-]+)="([^"]*)"', x[1]))
                if a.get('when-custom'):
                    return a['when-custom']
                lo, hi = a.get('notBefore-custom', ''), a.get('notAfter-custom', '')
                return (lo + '/' + hi) if (lo or hi) else ''
            mad = sorted(set(re.findall(r'<affiliation[^>]*type="madhhab"[^>]*ref="([^"]*)"', t)))
            tgt = re.search(r'<note type="reference" target="#(AIND-D\w+)"', t)
            out[m[2]] = dict(refs=set(v.lstrip('#') for mm in REFRE.finditer(t) for v in mm[1].split()), ref=bool(m[1]), birth=date('birth'), death=date('death'),
                             madhhab=' | '.join(mad), target=tgt[1] if tgt else '')
    return out

def read_tsv(p):
    with open(p, encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f, delimiter='\t'))

def dump(rows, cols):
    b = io.StringIO()
    w = csv.DictWriter(b, cols, delimiter='\t', lineterminator='\n', extrasaction='ignore')
    w.writeheader(); w.writerows(rows)
    return b.getvalue()

def init(pl_csv):
    if os.path.exists(REG):
        sys.exit('registry already exists; edit it instead of re-running init')
    C = {c['id']: c for c in corpus() if c['id']}
    X = xmls()
    rows = []
    seen = set()
    for r in list(csv.reader(open(pl_csv, encoding='utf-8')))[1:]:
        r = (r + [''] * 11)[:11]
        aid, n12, full, b, d, mad, note = r[2].strip(), r[3].strip(), r[4].strip(), r[6].strip(), r[7].strip(), r[8].strip(), r[9].strip()
        if not aid:
            continue
        seen.add(aid)
        c, x = C.get(aid), X.get(aid)
        row = dict.fromkeys(REG_COLS, ''); row['id'] = aid; row['note'] = note
        cited = [t for t in AID.findall(note) if t != aid]
        if c is None:
            row['status'] = 'merged' if cited else 'retired'
            row['target'] = cited[0] if cited else ''
        elif c['kind'] == 'transfer':
            row['status'] = 'transfer'
            row['target'] = (x or {}).get('target') or (cited[0] if cited else '')
        elif not n12 and not full and cited:
            row['status'] = 'needs-ruling'   # PersonList treats it as identified with another entry, corpus as a full entry
            row['target'] = cited[0]
        else:
            row['status'] = 'active'
        rows.append(row)
    for aid, c in C.items():
        if aid not in seen:
            row = dict.fromkeys(REG_COLS, ''); row['id'] = aid
            row['status'] = 'transfer' if c['kind'] == 'transfer' else 'active'
            rows.append(row)
    rows.sort(key=lambda r: r['id'])
    open(REG, 'w', encoding='utf-8', newline='').write(dump(rows, REG_COLS))
    print('registry rows', len(rows))

VIEW_COLS = ['id', 'n12', 'kind', 'status', 'target', 'entry_no', 'name', 'heading', 'aliases', 'birth', 'death', 'madhhab',
             'value_source', 'has_record', 'cited_by', 'same_as', 'note']
HEAD_COLS = ['n12', 'id', 'kind', 'line', 'entry_no', 'heading']

def build():
    cs = corpus(); X = xmls(); R = {r['id']: r for r in read_tsv(REG)}
    C = {c['id']: c for c in cs if c['id']}
    problems = []
    for aid in C:
        if aid not in R: problems.append(f'{aid}: in corpus, not in registry')
    for aid, r in R.items():
        if r['status'] in ('active', 'transfer') and not r['name_ar']: problems.append(f'{aid}: no name')
        if not aid.startswith('AIND-D'):
            pass
        elif aid not in C and r['status'] not in ('merged', 'retired'):
            problems.append(f'{aid}: status {r["status"]} but not in corpus')
        if r['status'] in ('merged',) and not r['target']:
            problems.append(f'{aid}: merged without target')
        if r['target'] and r['target'] not in R:
            problems.append(f'{aid}: target {r["target"]} is not a registered ID')
        if aid in C and (C[aid]['kind'] == 'transfer') != (r['status'] == 'transfer'):
            problems.append(f'{aid}: corpus kind {C[aid]["kind"]} vs registry status {r["status"]}')
    EN = {e['id']: e for e in read_tsv(ENT)} if os.path.exists(ENT) else {}
    for k, e in EN.items():
        if k in R: problems.append(f'{k}: in both registries')
        if e['target'] and e['target'] not in EN: problems.append(f'{k}: target {e["target"]} is not a registered ID')
    cited = {}
    for rec, x in X.items():
        for v in x['refs']:
            if v != rec: cited.setdefault(v, set()).add(rec)
    unres = []
    for v in sorted(cited):
        if v in ('NEEDID', ''): continue
        row = R.get(v) or EN.get(v)
        why = 'not registered' if row is None else ('' if row['status'] == 'active' else row['status'] + (' -> ' + row['target'] if row['target'] else ''))
        if why: unres.append(dict(ref=v, problem=why, records=len(cited[v]), examples=' '.join(sorted(cited[v])[:5])))
    ev = [dict(e, use_count=len(cited.get(k, ()))) for k, e in sorted(EN.items(), key=lambda t: (t[1]['category'], t[0]))]
    view = []
    for aid in sorted(R, key=lambda k: (not k.startswith('AIND'), k)):
        r, c, x = R[aid], C.get(aid, {}), X.get(aid)
        v = dict(id=aid, n12=c.get('n12', ''), kind=c.get('kind', ''), status=r['status'], target=r['target'],
                 entry_no=c.get('entry_no', ''), name=r['name_ar'], heading=c.get('heading', ''),
                 aliases=r['aliases'], same_as=r['same_as'], note=r['note'], cited_by=len(cited.get(aid, ())),
                 has_record='yes' if x and not x['ref'] else 'no')
        if x and not x['ref']:
            v.update(birth=x['birth'], death=x['death'], madhhab=x['madhhab'], value_source='record')
        else:
            v.update(birth='', death='', madhhab='', value_source='')
        view.append(v)
    return {VIEW: dump(view, VIEW_COLS), HEADS: dump(cs, HEAD_COLS), ENT_VIEW: dump(ev, ENT_COLS[:9] + ['use_count']), UNRES: dump(unres, ['ref', 'problem', 'records', 'examples'])}, problems

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'init':
        init(sys.argv[2])
    elif cmd in ('view', 'check'):
        files, problems = build()
        if cmd == 'view':
            os.makedirs(OUT, exist_ok=True)
            for path, text in files.items():
                open(path, 'w', encoding='utf-8', newline='').write(text)
                print(os.path.basename(path), len(list(csv.reader(io.StringIO(text), delimiter='\t'))) - 1)
        for p in problems: print('PROBLEM', p)
        sys.exit(1 if problems else 0)
    else:
        sys.exit(__doc__)
