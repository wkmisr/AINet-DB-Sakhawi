"""Audit: which values of the TEI (records_tei.json, lossless) are absent from the aind-yaml files.
usage: python3 audit_tei_vs_yaml.py <records_tei.json> <v01 out dir>
Prints one line per kind of loss with a count and two examples. Written 2026-11-27; to be turned into a
failing check at the end of to_v01.py (values absent from YAML must be on an explicit 'dropped on purpose' list).
Dropped on purpose so far: labels/Latin forms of items that carry an ID (ID-Master has them), CE dates,
the source text, relation @n. NOT yet carried (to fix): person type=reference/subtype and note target,
resp (edit history), notes on relation events, the original phrase of events/states, relationship_type descs,
methods/fields without ID, corresp (wd beside an AIND id), events directly under listRelation."""
import json, re, os, sys, collections
R = json.load(open(sys.argv[1])); OUT = sys.argv[2]
Y = {k: (open(f'{OUT}/meta/{k}.yml', encoding='utf-8').read() if os.path.exists(f'{OUT}/meta/{k}.yml') else '') for k in R}
f = lambda x: re.sub(r"[\"'\\]", '', re.sub(r'\s+', ' ', x).strip())
YF = {k: f(v) for k, v in Y.items()}
has = lambda k, s: f(s) in YF[k]
C = collections.Counter(); EX = collections.defaultdict(list)
def miss(tag, k, v):
    C[tag] += 1
    if len(EX[tag]) < 2: EX[tag].append((k, str(v)[:100]))
for k, r in R.items():
    if r.get('type'): miss(f"person type/subtype = {r.get('type')}/{r.get('subtype')}", k, '')
    if r.get('corresp') and not has(k, r['corresp'].lstrip('#')): miss('person corresp', k, r['corresp'])
    C['resp entries (edit history; none carried)'] += len(r.get('resp', []))
    for n in r.get('notes', []):
        if n.get('type') in ('source', 'translation'): continue
        if n.get('text') and not has(k, n['text']): miss(f"person note text [{n.get('type')}]", k, n['text'])
        if n.get('target') and not re.search(r'target', Y[k]): miss('note target as a field', k, n['target'])
    def walk(o, path):
        if isinstance(o, dict):
            for a, v in o.items():
                if a in ('descs', 'notes') and isinstance(v, list):
                    for d in v:
                        if d.get('text') and not has(k, d['text']):
                            miss(f"{path}/{a}[type={d.get('type')},lang={d.get('lang')},ref={'y' if d.get('ref') else 'n'}] text", k, d['text'])
                elif a in ('names', 'places', 'orgs', 'bibls') and isinstance(v, list) and path:
                    for d in v:
                        ref = d.get('ref') or ''
                        if (not ref or 'NEEDID' in ref) and d.get('text') and not has(k, d['text']): miss(f'{path}/{a} without ID: text', k, d['text'])
                        if d.get('corresp') and not has(k, d['corresp'].lstrip('#')): miss(f'{path}/{a} corresp', k, d['corresp'])
                        walk(d, path + '/' + a)
                elif a == 'corresp' and isinstance(v, str):
                    if not has(k, v.lstrip('#')): miss(f'{path} corresp', k, v)
                else: walk(v, path + '/' + a)
        elif isinstance(o, list):
            for x in o: walk(x, path)
    for top in r:
        if top not in ('notes', 'resp', 'translation', 'generator', 'names', 'corresp'): walk(r[top], top)
for t, v in sorted(C.items(), key=lambda x: -x[1]): print(v, t, EX.get(t, ''), sep='\t')
