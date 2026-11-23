"""Convert the current lossless YAML (records.json, = XML) plus the tagged text (dau.json)
into the aind-yaml/0.1 layout:  meta/<id>.yml (assertions) + text/<id>.md (mARkdown with item ids).

Principles (see the schema note):
- authority names live in ID-Master only; records keep `ref` and the verbatim `quote` from the text
- every assertion gets a stable item id (r1, s1, e1, n1, a1, b, d); mARkdown tags carry that id after '|'
- CE dates are derived from AH and not stored; edit history lives in git and in the frozen TEI (tag tei-final)
"""
import json, re, sys, os, collections, yaml

WORK = os.environ.get('AIND_WORK', '.')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(WORK, 'v01')
R = json.load(open(os.path.join(WORK, 'records_tei.json')))
E = {e['k']: e for e in json.load(open(os.path.join(WORK, 'dau.json')))}
TR = json.load(open(os.path.join(WORK, 'tr.json')))

ENT = re.compile(r'^@(P|T|S|O|E)(\d)(\d+)\[([^\]]*)\]$')
YR = re.compile(r'^@(Y[BDYA])(\d+)(?:-(\d+))?(?:\[(\d+)\])?$')
LM = re.compile(r'^@L(\d+)X(\d+)L$')
STAT = collections.Counter()


FIVE = {'أبي': 'أبو', 'أبا': 'أبو', 'أخي': 'أخو', 'أخا': 'أخو', 'ذي': 'ذو', 'ذا': 'ذو', 'بني': 'بنو'}


def norm_ar(q, p=0):
    """Standardized form of a quoted span: drop the proclitic (p letters, as counted by the mARkdown tag)
    and unify the case forms of أبو / أخو / ذو / بنو when they head a construct (followed by another word)."""
    q = q[p:] if p else q
    w = q.split()
    for i in range(len(w) - 1):
        if w[i] in FIVE: w[i] = FIVE[w[i]]
    return ' '.join(w)


def norm_id(x):
    x = (x or '').lstrip('#')
    return x or None


UNK = (None, 'NEEDID')          # '#NEEDID' in the TEI = not identified (workflow marker)

# relation type is derived from the subtype (the TEI @type is 'personal' almost everywhere)
KIN = {'father', 'mother', 'son', 'daughter', 'brother', 'sister', 'grandfather', 'grandmother', 'grandson',
       'granddaughter', 'maternal_grandfather', 'uncle', 'paternal_uncle', 'maternal_uncle', 'maternal_aunt',
       'paternal_aunt', 'aunt', 'cousin', 'siblings_child', 'spouse', 'father-in-law', 'son-in-law',
       'brother-in-law', 'daughter-in-law', 'mother-in-law', 'relative', 'ancestor', 'descendant'}
REL_TYPE = lambda st: ('kin' if st in KIN else 'scholarly' if st == 'teacher'
                       else 'identity' if st == 'possible_identity' else 'social')


def ar_texts(lst):
    return [d.get('text') for d in (lst or []) if d.get('text') and d.get('lang', 'ar') == 'ar']


def notes_of(x):
    out = {}
    for n in x.get('notes') or []:
        if n.get('text'):
            k = n.get('lang') or 'und'
            out[k] = (out[k] + ' / ' if k in out else '') + n['text']
    return out or None


def ah_date(x):
    d = {}
    for k in ('when_ah', 'notBefore_ah', 'notAfter_ah'):
        if x.get(k):
            v = str(x[k]).lstrip('0') or '0'
            d[k.replace('_ah', '').replace('when', 'ah')] = int(v) if v.isdigit() else v
    if d and x.get('cert'):
        d['cert'] = x['cert']
    return d or None


def refs(lst, kind):
    out = []; seen = set()
    for p in lst or []:
        r = norm_id(p.get('ref'))
        if r == 'NEEDID': r = None
        if r and r in seen: continue
        if r: seen.add(r)
        o = {'ref': r} if r else {}
        if p.get('role'): o['role'] = p['role']
        elif p.get('type') in ('burial', 'funeral'): o['role'] = p['type']     # place of burial / funeral prayer
        if p.get('cert'): o['cert'] = p['cert']
        if p.get('text') and not r: o['label'] = p['text']   # no ID: keep the given name as a label
        out.append(o)
    return out or None


def provenance(gen):
    p = {'converted_from': 'TEI (tag tei-final)'}
    raw = [g for g in (gen or []) if g]
    for g in raw:
        m = re.search(r'Researcher Pro v([\d.]+)', g)
        if m: p['app'] = 'AINet-DB Researcher Pro ' + m.group(1)
        m = re.search(r' at (\d{4}-\d\d-\d\dT[\d:]+Z)', g)
        if m: p['generated_at'] = m.group(1)
        m = re.search(r'gemini-requested=(\S+)', g)
        if m: p['model_requested'] = m.group(1)
        m = re.search(r'gemini-resolved=(\S+)', g)
        if m: p['model_resolved'] = m.group(1)
        m = re.search(r'by (claude-[\w.-]+)', g)
        if m: p['created_by'] = m.group(1)
    if 'model_requested' not in p and 'model_resolved' not in p and 'created_by' not in p:
        if p.get('generated_at'):
            p['model_era'] = 'gemini-2.5-flash 系（推定）' if p['generated_at'] < '2026-07-24' else 'gemini-3.5-flash 系（推定）'
            p['model_era_basis'] = '生成日時と app.py の履歴（2026-07-24 に切替）からの推定'
        else:
            p['model'] = 'unknown'
    if raw and not any(k in p for k in ('app', 'created_by')):
        p['generator_note'] = raw
    return p


def tag_spans(text):
    """yield (token_index, tag, kind, br_or_m, words)"""
    toks = text.split(' ')
    for i, t in enumerate(toks):
        m = ENT.match(t)
        if m:
            n = int(m.group(3)); p = int(m.group(2))
            w = toks[i + 1:i + 1 + n]
            yield i, m, 'ENT', w
            continue
        m = YR.match(t)
        if m:
            n = int(m.group(4)) if m.group(4) else 1
            yield i, m, 'Y', toks[i + 1:i + 1 + n]


def parse_br(br):
    m = re.match(r'^([A-Za-z0-9_+\-/.]+):(.+)$', br)
    if m and not re.match(r'^(wd|gn)$', m.group(1)):
        return m.group(1), m.group(2)
    if re.match(r'^[a-z]+(/deputy)?$', br):
        return br, None
    return None, br


def convert(k, r):
    e = E.get(k, {})
    text = e.get('t', '')
    toks = text.split(' ')
    meta = {'schema': 'aind-yaml/0.1', 'id': k}
    if r.get('source_id'): meta['source'] = {'uid': str(r['source_id'])}
    if r.get('sex'): meta['sex'] = r['sex']

    # ---- items with ids -------------------------------------------------
    by_ref = collections.defaultdict(list)          # ref -> [(kind, item_id)]
    names = []
    full = next((n['text'] for n in r.get('names', []) if n.get('type') == 'full'), None)
    ni = 0
    for n in r.get('names', []):
        if n.get('type') in ('full', 'name_only'): continue
        ni += 1; it = {'id': f'n{ni}', 'type': n.get('type')}
        if norm_id(n.get('ref')) not in UNK: it['ref'] = norm_id(n['ref'])
        it['quote'] = None; it['_label'] = n.get('text')
        if n.get('cert'): it['cert'] = n['cert']
        names.append(it)
    meta['name'] = {'full': full} if full else {}
    if names: meta['name']['elements'] = names

    persons = []                                    # people the text names (or implies) but no ID identifies
    def local_person(label, why):
        pid = f'p{len(persons) + 1}'
        o = {'id': pid}
        if label: o['label'] = label
        o['for'] = why
        persons.append(o)
        return f'{k}#{pid}'

    for kind in ('birth', 'death'):
        x = r.get(kind)
        if not x: continue
        it = {'id': kind[0]}
        d = ah_date(x)
        if d: it['date'] = d
        pl = refs(x.get('places'), 'place') or []
        pl += refs(x.get('orgs'), 'org') or []
        if pl: it['places'] = pl
        ps = refs(x.get('names'), 'person')               # funeral prayer, buried near (role)
        for pp in ps or []:
            if not pp.get('ref'): pp['ref'] = local_person(pp.pop('label', None), kind[0]); STAT['local_person_bd'] += 1
        if ps: it['persons'] = ps
        if x.get('descs'): it['summary'] = {d_.get('lang', 'en'): d_['text'] for d_ in x['descs'] if d_.get('text')}
        nt = notes_of(x)
        if nt: it['note'] = nt
        meta[kind] = it

    rels = []
    for lr in r.get('listRelation') or []:
        for rel in lr.get('relations') or []:
            rid_ = f'r{len(rels) + 1}'
            it = {'id': rid_, 'type': REL_TYPE(rel.get('subtype')), 'subtype': rel.get('subtype'),
                  'active': norm_id(rel.get('active')), 'passive': norm_id(rel.get('passive'))}
            lab = next((d.get('text') for d in rel.get('descs') or []
                        if not d.get('type') and d.get('text') and d.get('lang', 'ar') == 'ar'), None)
            orig = (it['active'], it['passive'])
            for side in ('active', 'passive'):
                if it[side] in UNK:
                    it[side] = local_person(lab, rid_); STAT['local_person_rel'] += 1
            meths = [norm_id(d.get('ref')) for d in rel.get('descs') or [] if d.get('type') == 'method']
            if meths: it['methods'] = [m for m in meths if m]
            if rel.get('cert'): it['cert'] = rel['cert']
            ctx = []
            for ev in rel.get('events') or []:
                c = {}
                d = ah_date(ev)
                if d: c['date'] = d
                pl = refs(ev.get('places'), 'place')
                if pl: c['places'] = pl
                og = refs(ev.get('orgs'), 'org')
                if og: c['orgs'] = og
                if ev.get('descs'): c['summary'] = {d_.get('lang', 'en'): d_['text'] for d_ in ev['descs'] if d_.get('text')}
                if c: ctx.append(c)
            if ctx: it['context'] = ctx
            bb = refs(rel.get('bibls'), 'work')
            if bb: it['works'] = bb
            it['quote'] = None
            nt = notes_of(rel)
            if nt: it['note'] = nt
            partner = orig[1] if orig[0] == k else orig[0]          # as written in the TEI / text tags
            it['_partner'] = partner
            rels.append(it)
    if rels: meta['relations'] = rels

    states = []
    for st in r.get('states') or []:
        it = {'id': f's{len(states) + 1}', 'type': st.get('type')}
        if st.get('subtype'): it['subtype'] = st['subtype']
        if norm_id(st.get('ref')) not in UNK: it['ref'] = norm_id(st['ref'])
        else:
            lab = next(iter(ar_texts(st.get('labels'))), None)
            if lab: it['label'] = lab               # no ID: the label is the only value
        for f, kk in (('places', 'places'), ('orgs', 'orgs')):
            v = refs(st.get(f), f)
            if v: it[kk] = v
        ds = [ah_date(d) for d in st.get('dates') or []]
        if any(ds): it['dates'] = [d for d in ds if d]
        if st.get('cert'): it['cert'] = st['cert']
        it['quote'] = None
        nt = notes_of(st)
        if nt: it['note'] = nt
        states.append(it)
    if states: meta['states'] = states

    affs = []
    for a in r.get('affiliations') or []:
        it = {'id': f'a{len(affs) + 1}', 'type': a.get('type')}
        if norm_id(a.get('ref')) not in UNK: it['ref'] = norm_id(a['ref'])
        elif a.get('text'): it['label'] = a['text']
        if a.get('cert'): it['cert'] = a['cert']
        nt = notes_of(a)
        if nt: it['note'] = nt
        affs.append(it)
    if affs: meta['affiliations'] = affs

    evs = []
    for ev in r.get('events') or []:
        it = {'id': f'e{len(evs) + 1}', 'type': ev.get('type')}
        if ev.get('subtype'): it['subtype'] = ev['subtype']
        d = ah_date(ev)
        if d: it['date'] = d
        for f, kk in (('names', 'persons'), ('places', 'places'), ('orgs', 'orgs'), ('bibls', 'works')):
            v = refs(ev.get(f), f)
            if v and kk == 'persons':
                for pp in v:
                    if not pp.get('ref'):
                        pp['ref'] = local_person(pp.pop('label', None), it['id']); STAT['local_person_ev'] += 1
            if v: it[kk] = v
        q = None
        sm = {}
        meths = [norm_id(d_.get('ref')) for d_ in ev.get('descs') or [] if d_.get('type') == 'method' and d_.get('ref')]
        if meths: it['methods'] = meths
        for d_ in ev.get('descs') or []:
            if not d_.get('text') or d_.get('type') in ('method', 'field'): continue
            if d_.get('lang') == 'ar' and d_['text'] in text.replace('  ', ' '):
                q = d_['text']                               # an Arabic desc that is verbatim in the text
            else:
                sm[d_.get('lang', 'en')] = d_['text']
        it['quote'] = q
        if sm: it['summary'] = sm
        if ev.get('cert'): it['cert'] = ev['cert']
        nt = notes_of(ev)
        if nt: it['note'] = nt
        evs.append(it)
    if evs: meta['events'] = evs

    gnotes = []
    for n in r.get('notes') or []:
        if n.get('text') and n.get('type') not in ('source', 'translation'):
            g = {'text': n['text']}
            if n.get('lang'): g['lang'] = n['lang']
            if n.get('type'): g['type'] = n['type']
            gnotes.append(g)
    if gnotes: meta['notes'] = gnotes

    # ---- link text tags to items, fill quotes ---------------------------
    # quote = the words exactly as in the text (proclitics included); norm = standardized form
    # (proclitic removed by the tag's prefix count, case forms of the five nouns unified)
    def Q(q, p):
        return {'_q': q, '_p': p}

    used = set()
    def take(pred, lst):
        for it in lst:
            if it['id'] not in used and pred(it):
                used.add(it['id']); return it
        return None

    new = list(toks)
    for i, m, kind, w in tag_spans(text):
        q = ' '.join(w)
        if kind == 'Y':
            code = m.group(1)
            it = meta.get('death') if code == 'YD' else meta.get('birth') if code == 'YB' else None
            if it is not None and 'quote' not in it:
                it['quote'] = q; STAT['linked_Y'] += 1
            # بضع ranges (1-9, ruling 2026-11-22) are now written in the TEI itself; the TEI date is kept as is
            continue
        code, p = m.group(1), int(m.group(2))
        sub, rid = parse_br(m.group(4))
        if code != 'P' and rid == 'NEEDID': rid = None      # non-person NEEDID: no ID, match by type
        if code == 'E':
            j = int(rid[1:]) - 1 if rid and rid.startswith('e') else -1
            if 0 <= j < len(evs):
                evs[j]['quote'] = q; evs[j]['trigger'] = 'rule'
                new[i] = f'@E{p}{m.group(3)}[{sub}|{rid}]'; STAT['linked_E'] += 1
            continue
        it = None
        if code == 'S':
            it = take(lambda x: x['type'] == sub and (x.get('ref') == rid if rid else True), names)
            if it is None:
                it = {'id': f'n{len(names) + 1}', 'type': sub, 'quote': None, 'by': 'rule'}
                if rid: it['ref'] = rid
                names.append(it); used.add(it['id'])
                meta['name'].setdefault('elements', names)
        elif code == 'P':
            it = take(lambda x: x['_partner'] == rid, rels)
            if it is None:
                for ev in evs:
                    if any(pp.get('ref') == rid for pp in ev.get('persons') or []):
                        it = ev if ev['id'] not in used else None; break
        elif code == 'O':
            it = (take(lambda x: rid and x.get('ref') == rid, states)
                  or take(lambda x: not rid and not x.get('ref') and x['type'] == sub.split('/')[0], states)
                  or take(lambda x: not rid and x['type'] == sub, states))
        elif code == 'T':
            # a place may serve several items; link to none, quote goes onto every place ref with that id
            for holder in [meta.get('birth'), meta.get('death'), *states, *evs, *[c for r_ in rels for c in r_.get('context', [])]]:
                for pl in (holder or {}).get('places') or []:
                    if pl.get('ref') == rid and 'quote' not in pl:
                        pl['quote'] = Q(q, p)
            STAT['T'] += 1
            continue
        if it is not None:
            if it.get('quote') is None and 'persons' not in it:
                it['quote'] = Q(q, p)
            elif 'persons' in it:
                for pp in it['persons']:
                    if pp.get('ref') == rid and 'quote' not in pp: pp['quote'] = Q(q, p)
            new[i] = m.group(0)[:-1] + '|' + it['id'] + ']'
            STAT['linked_' + code] += 1
        else:
            STAT['unlinked_' + code] += 1

    def fixq(o):
        if isinstance(o, dict):
            for k_, v_ in list(o.items()):
                if isinstance(v_, dict) and '_q' in v_:
                    o[k_] = v_['_q']; nm = norm_ar(v_['_q'], v_['_p'])
                    if nm != v_['_q']: o['norm'] = nm
                    STAT['norm_changed' if nm != v_['_q'] else 'norm_same'] += 1
                else: fixq(v_)
        elif isinstance(o, list):
            for x_ in o: fixq(x_)
    fixq(meta)
    for ev in evs:                                   # event trigger: «وحج» -> «حج»
        if ev.get('quote') and 'norm' not in ev:
            nm = norm_ar(ev['quote'], 1 if re.match(r'^[وف]\S{3,}', ev['quote']) else 0)
            if nm != ev['quote']: ev['norm'] = nm; STAT['norm_changed'] += 1

    for lst in (names, rels, states, evs):
        for it in lst:
            it.pop('_partner', None); lab = it.pop('_label', None)
            if it.get('quote') is None:
                it['quote'] = None; STAT['noquote_' + it['id'][0]] += 1
                if lab and not it.get('ref'): it['label'] = lab

    # an unnamed father / grandfather is the 1st / 2nd nasab of the heading (by rule)
    nas = re.findall(r'\[nasab[^\]|]*\|(n\d+)\]', ' '.join(new))
    for st_, pos in (('father', 0), ('grandfather', 1)):
        cand = [rl for rl in rels if rl['subtype'] == st_ and rl['passive'] == k and '#p' in str(rl['active'])]
        if len(cand) == 1 and len(nas) > pos:
            pid = cand[0]['active'].split('#')[1]
            pe = next(x for x in persons if x['id'] == pid)
            pe['name_element'] = nas[pos]; pe['by'] = 'rule'; STAT['local_person_nasab'] += 1
    if persons:
        out = {}
        for kk, vv in meta.items():
            if kk == 'relations': out['persons'] = persons
            out[kk] = vv
        if 'persons' not in out: out['persons'] = persons
        meta.clear(); meta.update(out)

    tr = TR.get(k)
    if tr: meta['translation'] = tr
    meta['provenance'] = provenance(r.get('generator'))

    header = f"### $ {k}" if k.startswith('AIND') else f"### $ #{k}"
    md = header + '\n' + ' '.join(new) + '\n'
    return meta, md


class D(yaml.SafeDumper):
    pass
def _str(d, s):
    return d.represent_scalar('tag:yaml.org,2002:str', s, style='|' if '\n' in s else None)
D.add_representer(str, _str)


if __name__ == '__main__':
    os.makedirs(OUT + '/meta', exist_ok=True); os.makedirs(OUT + '/text', exist_ok=True)
    tot_y = tot_m = 0
    for k, r in R.items():
        meta, md = convert(k, r)
        y = yaml.dump(meta, Dumper=D, allow_unicode=True, sort_keys=False, width=1000)
        open(f'{OUT}/meta/{k}.yml', 'w', encoding='utf-8').write(y)
        open(f'{OUT}/text/{k}.md', 'w', encoding='utf-8').write(md)
        tot_y += len(y.encode()); tot_m += len(md.encode())
    print('files', len(R), 'meta MB', round(tot_y / 1e6, 2), 'text MB', round(tot_m / 1e6, 2))
    print(dict(sorted(STAT.items())))
