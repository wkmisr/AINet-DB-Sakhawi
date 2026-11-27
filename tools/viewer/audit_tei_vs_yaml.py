"""Check that the aind-yaml files carry every value of the TEI (records_tei.json, lossless dicts).

usage: python3 audit_tei_vs_yaml.py <records_tei.json> <v01 out dir> [report.tsv]
       (also run at the end of to_v01.py; the conversion fails when something is missing)

Every leaf value of a TEI record must be found in the YAML of the same record, unless it falls under DROPPED
(the explicit list of what is left out on purpose, with the reason). Ruling (Waka 2026-11-27): everything in the
XML except the edit history goes into the YAML; the history is kept in git, CHANGELOG.md and the frozen TEI.

How a value is looked for:
- attribute-like values (ids, cert, type, role, AH years …) are counted: the YAML must hold at least as many
  scalars equal to the value as the TEI holds;
- texts are looked for as substrings of the record's YAML scalars (whitespace and quotes normalised).
Entries of one list that differ only in their text/lang (an Arabic and a Latin label of the same ref) count once.
"""
import json, re, os, sys, collections, yaml

# what is left out on purpose -------------------------------------------------------------------------------
DROPPED = [
    ('resp',             'edit history (respStmt): kept in git, CHANGELOG.md and the frozen TEI (Waka 2026-11-27)'),
    ('generator',        'creation record of the app; summarised in provenance (app, version, time, model)'),
    ('n',                '@n = running number inside the generating app\'s groups; the order is kept by the item ids'),
    ('lang',             'language attribute; kept as the key of the text it belongs to'),
    ('ce_date',          'CE dates (@when, @notBefore, @notAfter): computed from the AH dates'),
    ('text_of_id',       'name or label of an item that has an ID: ID-Master holds it'),
    ('needid',           '#NEEDID = workflow marker; the person becomes a local person (<record>#pN)'),
    ('rel_type_personal','relation @type="personal" (the TEI default); YAML type is derived from the subtype'),
    ('markup',           'whitespace between elements, @dir of a <span>'),
]
DROP_REASON = dict(DROPPED)

ATTR = {'ref', 'active', 'passive', 'target', 'corresp', 'cert', 'type', 'subtype', 'role', 'sex', 'source_id', 'id',
        'when_ah', 'notBefore_ah', 'notAfter_ah'}
REAL_ID = lambda v: bool(v) and 'NEEDID' not in v


def norm_atom(v):
    v = str(v).strip().lstrip('#')
    return re.sub(r'^0+(?=\d)', '', v)            # AH '0867-11' (TEI) = '867-11' / 867 (YAML)


# a TEI value that the YAML holds as a key or a section rather than as a scalar
# (YAML key -> the TEI values it stands for, counted once per entry)
KEYMAP = {'full': ['full'], 'name_only': ['name_only'], 'full_alt': ['full'], 'name_only_alt': ['name_only'], 'methods': ['method'], 'fields': ['field'],
          'relationship_type': ['relationship_type'], 'sources': ['cultural', 'mention'], 'assessments': ['status']}
MARKUP = re.compile(r'^[\s>]*$')


def norm_text(x):
    return re.sub(r"[\"'\\]", '', re.sub(r'\s+', ' ', str(x)).strip())


def leaves(r):
    """yield (path, key, value) for every TEI value that must reach the YAML; dropped ones as (path, None, reason)"""
    out = []

    def collapse(lst):
        seen, keep = set(), []
        for d in lst:
            if isinstance(d, dict) and REAL_ID(d.get('ref') or ''):
                key = json.dumps({a: b for a, b in d.items() if a not in ('text', 'lang')}, sort_keys=True, ensure_ascii=False)
                if key in seen: continue
                seen.add(key)
            keep.append(d)
        return keep

    def walk(o, path, parent, inherited=False):
        if isinstance(o, dict):
            has_id = inherited or REAL_ID(str(o.get('ref') or ''))
            for a, v in o.items():
                p = path + '/' + a
                if a == 'resp' and path == '':          out.append((p, None, 'resp')); continue
                if a == 'generator' and path == '':     out.append((p, None, 'generator')); continue
                if a == 'n':                            out.append((p, None, 'n')); continue
                if a == 'lang':                         out.append((p, None, 'lang')); continue
                if a == 'dir':                          out.append((p, None, 'markup')); continue
                if a in ('when', 'notBefore', 'notAfter'): out.append((p, None, 'ce_date')); continue
                if a == 'translation' and path == '':
                    for lg, t in (v or {}).items(): out.append((p + '/' + lg, 'text', t))
                    continue
                if isinstance(v, (dict, list)):
                    walk(collapse(v) if isinstance(v, list) else v, p, o, has_id and a == 'labels')
                    continue
                if v is None or (isinstance(v, str) and MARKUP.match(v)):
                    out.append((p, None, 'markup')); continue
                if a in ('text', '_tail') and has_id:   out.append((p, None, 'text_of_id')); continue
                if a in ATTR and ('NEEDID' in str(v) or not norm_atom(v)):    out.append((p, None, 'needid')); continue
                if a == 'type' and v == 'personal' and '/relations' in path and parent is not None:
                    out.append((p, None, 'rel_type_personal')); continue
                out.append((p, a, v))
        elif isinstance(o, list):
            for x in o: walk(x, path, parent, inherited)
        elif o is not None and not MARKUP.match(str(o)):
            out.append((path, 'text', o))       # bare strings in lists (XML comments)
    walk(r, '', None)
    return out


def scalars(o, acc):
    if isinstance(o, dict):
        for kk, v in o.items():
            for tv in KEYMAP.get(kk, []):
                acc.extend([tv] * (len(v) if isinstance(v, (list, dict)) else 1))
            scalars(v, acc)
    elif isinstance(o, list):
        for v in o: scalars(v, acc)
    elif o is not None:
        acc.append(o)
    return acc


def resolve_mentions(y):
    """what a pointer to a mention stands for: the mention's ref and words, once per pointer"""
    M = {m['id']: m for m in y.get('mentions') or [] if isinstance(m, dict) and m.get('id')}
    extra = []
    def walk(o, key=None):
        if isinstance(o, dict):
            for kk, v in o.items():
                if kk == 'mentions': continue
                walk(v, kk)
        elif isinstance(o, list):
            for v in o: walk(v, key)
        elif isinstance(o, str) and o in M and key in ('mention', 'active', 'passive'):
            extra.extend(v for a, v in M[o].items() if a in ('ref', 'quote', 'norm') and v is not None)
    walk(y)
    return extra


def audit(R, out_dir, report=None):
    C = collections.Counter(); EX = collections.defaultdict(list); DR = collections.Counter()
    for k, r in R.items():
        fn = f'{out_dir}/meta/{k}.yml'
        y = yaml.safe_load(open(fn, encoding='utf-8')) if os.path.exists(fn) else {}
        sc = scalars(y, []) + resolve_mentions(y or {})
        cnt = collections.Counter(norm_atom(s) for s in sc)
        blob = '\u0001'.join(norm_text(s) for s in sc)
        need = collections.Counter(); where = {}
        for path, key, v in leaves(r):
            if key is None: DR[v] += 1; continue
            if key in ATTR:
                need[norm_atom(v)] += 1; where.setdefault(norm_atom(v), path)
            elif norm_text(v) not in blob:
                tag = re.sub(r'/(text|_tail)$', '', path) + ' (text)'
                C[tag] += 1
                if len(EX[tag]) < 3: EX[tag].append((k, norm_text(v)[:90]))
        for v, n in need.items():
            if cnt[v] < n:
                tag = where[v] + ' (value)'
                C[tag] += n - cnt[v]
                if len(EX[tag]) < 3: EX[tag].append((k, v))
    lines = [f'{n}\t{t}\t{EX[t]}' for t, n in sorted(C.items(), key=lambda x: -x[1])]
    if report:
        with open(report, 'w', encoding='utf-8') as f:
            f.write('# missing from YAML (count, TEI path, examples)\n' + '\n'.join(lines) + '\n')
            f.write('# dropped on purpose (count, reason)\n')
            for d, n in sorted(DR.items(), key=lambda x: -x[1]): f.write(f'{n}\t{d}\t{DROP_REASON[d]}\n')
    return C, DR, lines


if __name__ == '__main__':
    R = json.load(open(sys.argv[1]))
    C, DR, lines = audit(R, sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    print('\n'.join(lines) if lines else 'nothing missing')
    print('dropped on purpose:', dict(DR))
    sys.exit(1 if C else 0)
