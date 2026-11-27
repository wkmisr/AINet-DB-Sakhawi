"""Convert the current lossless YAML (records.json, = XML) plus the tagged text (dau.json)
into the aind-yaml/0.1 layout:  meta/<id>.yml (assertions) + text/<id>.md (mARkdown with item ids).

Principles (see the schema note):
- authority names live in ID-Master only; records keep `ref` and the verbatim `quote` from the text
- every assertion gets a stable item id (r1, s1, e1, n1, a1, b, d); mARkdown tags carry that id after '|'
- CE dates are derived from AH and not stored; edit history lives in git and in the frozen TEI (tag tei-final)
- everything else in the TEI is carried (Waka 2026-11-27); the conversion ends with audit_tei_vs_yaml.py and
  fails when a TEI value is missing from the YAML and not on its dropped-on-purpose list
"""
import json, re, sys, os, collections, unicodedata, yaml

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

# OpenITI normalize_ara_light (openiti.helper.ara, MIT licence), reproduced so the build needs no extra package
_LIGHT = [("أ", "ا"), ("ٱ", "ا"), ("آ", "ا"), ("إ", "ا"), ("ى", "ي"),
          ("يء", "ء"), ("ىء", "ء"), ("ؤ", "ء"), ("ئ", "ء"), ("ک", "ك"), ("ی", "ي"), ("ۀ", "ه")]


def normalize_ara_light(t):
    t = unicodedata.normalize('NFKC', t)
    for a_, b_ in _LIGHT: t = re.sub(a_, b_, t)
    return t


def norm_ar(q, p=0):
    """Standardized form of a quoted span (Romanov's advice, Waka 2026-11-23):
    (1) drop the proclitic (p letters, as counted by the mARkdown tag);
    (2) unify the case form of a name element that opens the span (أبي/أبا → أبو, أخي → أخو, ذي → ذو, بني → بنو),
        only when it heads a construct; forms inside a longer phrase (ابن أبي اليمن) are left as written;
    (3) OpenITI's light orthographic normalization (alifs, alif maqsura → ya, hamza carriers)."""
    q = q[p:] if p else q
    w = q.split()
    if len(w) > 1 and w[0] in FIVE: w[0] = FIVE[w[0]]
    return normalize_ara_light(' '.join(w))


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


def flat_text(n):
    """the whole text of a note: its own text, inline <span>s (with the text after them) and <p>s"""
    parts = [n.get('text') or '']
    for sp in n.get('span') or []: parts += [sp.get('text') or '', sp.get('_tail') or '']
    for p_ in n.get('p') or []: parts.append(flat_text(p_))
    return ''.join(parts).strip()


def notes_of(x, key='notes'):
    """notes as {lang: text}; when a note has a type, a target or a cert, a list of
    {lang, type, target, cert, text} instead (nothing of the TEI note is lost)"""
    ns = [n for n in x.get(key) or [] if flat_text(n)]
    if not ns: return None
    if any(n.get(a) for n in ns for a in ('type', 'target', 'cert')):
        out = []
        for n in ns:
            o = {}
            for a in ('lang', 'type', 'target', 'cert'):
                if n.get(a): o[a] = norm_id(n[a]) if a == 'target' else n[a]
            o['text'] = flat_text(n)
            out.append(o)
        return out
    out = {}
    for n in ns:
        k = n.get('lang') or 'und'
        out[k] = (out[k] + ' / ' if k in out else '') + flat_text(n)
    return out


def by_lang(descs):
    out = {}
    for d in descs:
        k = d.get('lang') or 'und'
        out[k] = (out[k] + ' / ' if k in out else '') + d['text']
    return out


def desc_parts(it, descs, text, skip=None):
    """distribute TEI <desc>s over an item, so that none is lost:
    method / field -> methods[] / fields[] (an ID, or {label} when there is none);
    relationship_type -> relationship_type {lang: text}; another typed desc -> desc_notes;
    an Arabic desc found verbatim in the text -> phrase; any other -> summary {lang: text}."""
    meth, fld, rt, phr, sm, other = [], [], [], [], [], []
    for d in descs or []:
        t = d.get('text')
        ty = d.get('type')
        if (not t and not (ty in ('method', 'field') and d.get('ref'))) or (t and t == skip): continue
        if ty in ('method', 'field'):
            r_ = norm_id(d.get('ref'))
            v = r_ if r_ and r_ != 'NEEDID' else {'label': t, **({'lang': d['lang']} if d.get('lang') not in (None, 'ar') else {})}
            lst = meth if ty == 'method' else fld
            if v not in lst: lst.append(v)
        elif ty == 'relationship_type': rt.append(d)
        elif ty: other.append({'type': ty, **({'lang': d['lang']} if d.get('lang') else {}), 'text': t})
        elif d.get('lang', 'ar') == 'ar' and text and re.sub(r'\s+', ' ', t).strip() in text: phr.append(re.sub(r'\s+', ' ', t).strip())
        else: sm.append(d)
        for nm in d.get('names') or []:                       # a person named inside a desc
            if norm_id(nm.get('ref')) not in UNK: it.setdefault('desc_persons', []).append({'ref': norm_id(nm['ref'])})
        if d.get('ref') and ty not in ('method', 'field'): it.setdefault('desc_refs', []).append(norm_id(d['ref']))
    if meth: it['methods'] = meth
    if fld: it['fields'] = fld
    if rt: it['relationship_type'] = by_lang(rt)
    if phr: it['_phrase'] = phr
    if sm: it['summary'] = by_lang(sm)
    if other: it['desc_notes'] = other


def set_note(it, x):
    nt = notes_of(x)
    if nt: it['note'] = nt


def ah_date(x):
    d = {}
    for k in ('when_ah', 'notBefore_ah', 'notAfter_ah'):
        if x.get(k):
            v = str(x[k]).lstrip('0') or '0'
            d[k.replace('_ah', '').replace('when', 'ah')] = int(v) if v.isdigit() else v
    if d and x.get('cert'):
        d['cert'] = x['cert']
    if d and x.get('type'):
        d['type'] = x['type']                  # dates of a state: appointment / retirement
    return d or None


def refs(lst, kind):
    """references to persons, places, institutions, works. An Arabic and a Latin entry of the same ID are one
    reference; the same ID with another role or cert stays a separate reference."""
    out = []; seen = set()
    for p in lst or []:
        r = norm_id(p.get('ref'))
        if r == 'NEEDID': r = None
        o = {'ref': r} if r else {}
        if p.get('role'): o['role'] = p['role']
        elif p.get('type') in ('burial', 'funeral'): o['role'] = p['type']     # place of burial / funeral prayer
        elif p.get('type'): o['type'] = p['type']
        if p.get('cert'): o['cert'] = p['cert']
        if p.get('corresp'): o['corresp'] = norm_id(p['corresp'])      # wd beside an AIND id
        if p.get('text') and not r: o['label'] = p['text']   # no ID: keep the given name as a label
        if r:
            key = json.dumps(o, sort_keys=True, ensure_ascii=False)
            if key in seen: continue
            seen.add(key)
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
    plain = ' '.join(t for t in toks if not t.startswith('@'))       # the text without tags, for verbatim phrases
    meta = {'schema': 'aind-yaml/0.1', 'id': k}
    if r.get('type') or r.get('subtype'):                            # cross-reference heading (REF, LIMBO)
        meta['entry'] = {kk: r[kk] for kk in ('type', 'subtype') if r.get(kk)}
    if r.get('corresp'): meta['corresp'] = norm_id(r['corresp'])
    if r.get('source_id'): meta['source'] = {'uid': str(r['source_id'])}
    if r.get('sex'): meta['sex'] = r['sex']

    # ---- items with ids -------------------------------------------------
    by_ref = collections.defaultdict(list)          # ref -> [(kind, item_id)]
    names = []
    ni = 0
    for n in r.get('names', []):
        if n.get('type') in ('full', 'name_only'): continue
        ni += 1; it = {'id': f'n{ni}', 'type': n.get('type')}
        if norm_id(n.get('ref')) not in UNK: it['ref'] = norm_id(n['ref'])
        it['quote'] = None; it['_label'] = n.get('text')
        if n.get('cert'): it['cert'] = n['cert']
        names.append(it)
    meta['name'] = {}
    for ty_ in ('full', 'name_only'):                                # name_only = the name without nisbas and titles
        ns_ = [n for n in r.get('names', []) if n.get('type') == ty_ and n.get('text')]
        if not ns_: continue
        meta['name'][ty_] = ns_[0]['text']
        if ns_[0].get('cert'): meta['name'][ty_ + '_cert'] = ns_[0]['cert']
        if len(ns_) > 1:                                             # another reading of the heading (D02743, D05775)
            meta['name'][ty_ + '_alt'] = [{'text': n['text'], **({'cert': n['cert']} if n.get('cert') else {})} for n in ns_[1:]]
    if names: meta['name']['elements'] = names

    persons = []                                    # people the text names (or implies) but no ID identifies
    def local_person(label, why):
        pid = f'p{len(persons) + 1}'
        o = {'id': pid}
        if label: o['label'] = label
        o['for'] = why
        persons.append(o)
        return f'{k}#{pid}'

    def person_refs(lst, why, stat):
        ps = refs(lst, 'person')
        for pp in ps or []:
            if not pp.get('ref'): pp['ref'] = local_person(pp.pop('label', None), why); STAT[stat] += 1
        return ps

    for kind in ('birth', 'death'):
        x = r.get(kind)
        if not x: continue
        it = {'id': kind[0]}
        d = ah_date(x)
        if d: it['date'] = d
        elif x.get('cert'): it['cert'] = x['cert']
        pl = refs(x.get('places'), 'place') or []
        pl += refs(x.get('orgs'), 'org') or []
        if pl: it['places'] = pl
        ps = person_refs(x.get('names'), kind[0], 'local_person_bd')     # funeral prayer, buried near (role)
        if ps: it['persons'] = ps
        desc_parts(it, x.get('descs'), plain)
        set_note(it, x)
        meta[kind] = it

    rels = []
    rel_src = [rel for lr in r.get('listRelation') or [] for rel in lr.get('relations') or []] + list(r.get('relations') or [])
    for rel in rel_src:
        rid_ = f'r{len(rels) + 1}'
        it = {'id': rid_, 'type': REL_TYPE(rel.get('subtype')), 'subtype': rel.get('subtype'),
              'active': norm_id(rel.get('active')), 'passive': norm_id(rel.get('passive'))}
        if rel.get('type') and rel['type'] != 'personal': it['tei_type'] = rel['type']   # 'professional' (2)
        if rel.get('corresp'): it['corresp'] = norm_id(rel['corresp'])
        lab = next((d.get('text') for d in rel.get('descs') or []
                    if not d.get('type') and d.get('text') and d.get('lang', 'ar') == 'ar'), None)
        orig = (it['active'], it['passive'])
        used_lab = None
        for side in ('active', 'passive'):
            if it[side] in UNK:
                it[side] = local_person(lab, rid_); used_lab = lab; STAT['local_person_rel'] += 1
        desc_parts(it, rel.get('descs'), plain, skip=used_lab)      # the label went to the local person
        if rel.get('cert'): it['cert'] = rel['cert']
        ctx = []
        for ev in rel.get('events') or []:
            c = {}
            if ev.get('type'): c['type'] = ev['type']                  # learning / teaching …
            d = ah_date(ev)
            if d: c['date'] = d
            elif ev.get('cert'): c['cert'] = ev['cert']
            if d and ev.get('cert'): c['cert'] = ev['cert']
            pl = refs(ev.get('places'), 'place')
            if pl: c['places'] = pl
            og = refs(ev.get('orgs'), 'org')
            if og: c['orgs'] = og
            ps = person_refs(ev.get('names'), rid_, 'local_person_rel')
            if ps: c['persons'] = ps
            desc_parts(c, ev.get('descs'), plain)
            if c.get('_phrase'): c['phrase'] = ' / '.join(c.pop('_phrase'))
            set_note(c, ev)
            if c: ctx.append(c)
        if ctx: it['context'] = ctx
        bb = refs(rel.get('bibls'), 'work')
        if bb: it['works'] = bb
        it['quote'] = None
        set_note(it, rel)
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
            lat = [d['text'] for d in st.get('labels') or [] if d.get('lang') == 'ar-Latn' and d.get('text')]
            if lat: it['label_latn'] = ' / '.join(lat)
            oth = [d for d in st.get('labels') or [] if d.get('lang') not in ('ar', 'ar-Latn', None) and d.get('text')]
            if oth: it['label_other'] = by_lang(oth)
        for f, kk in (('places', 'places'), ('orgs', 'orgs'), ('bibls', 'works')):
            v = refs(st.get(f), f)
            if v: it[kk] = v
        ps = person_refs(st.get('names'), it['id'], 'local_person_st')
        if ps: it['persons'] = ps
        d0 = ah_date(st)                                                # a date on the state itself
        ds = ([d0] if d0 else []) + [ah_date(d) for d in st.get('dates') or []]
        if any(ds): it['dates'] = [d for d in ds if d]
        if st.get('cert'): it['cert'] = st['cert']
        desc_parts(it, st.get('descs'), plain)
        it['quote'] = None
        set_note(it, st)
        states.append(it)
    if states: meta['states'] = states

    affs = []
    for a in r.get('affiliations') or []:
        it = {'id': f'a{len(affs) + 1}', 'type': a.get('type')}
        if norm_id(a.get('ref')) not in UNK: it['ref'] = norm_id(a['ref'])
        elif a.get('text'): it['label'] = a['text']
        for f, kk in (('places', 'places'), ('orgs', 'orgs')):
            v = refs(a.get(f), f)
            if v: it[kk] = v
        if a.get('cert'): it['cert'] = a['cert']
        desc_parts(it, a.get('descs'), plain)
        set_note(it, a)
        affs.append(it)
    if affs: meta['affiliations'] = affs

    evs = []
    ev_src = list(r.get('events') or []) + [ev for lr in r.get('listRelation') or [] for ev in lr.get('events') or []]
    for ev in ev_src:
        it = {'id': f'e{len(evs) + 1}', 'type': ev.get('type')}
        if ev.get('subtype'): it['subtype'] = ev['subtype']
        if norm_id(ev.get('ref')) not in UNK: it['ref'] = norm_id(ev['ref'])     # an office sought (D01766)
        lb = [d for d in ev.get('labels') or [] if d.get('text')]
        if lb: it['title'] = by_lang(lb)          # a heading the TEI gave the event (not a name in place of an ID)
        d = ah_date(ev)
        if d: it['date'] = d
        for f, kk in (('names', 'persons'), ('places', 'places'), ('orgs', 'orgs'), ('bibls', 'works')):
            v = person_refs(ev.get(f), it['id'], 'local_person_ev') if kk == 'persons' else refs(ev.get(f), f)
            if v: it[kk] = v
        desc_parts(it, ev.get('descs'), plain)
        phr = it.pop('_phrase', [])
        it['quote'] = phr[0] if phr else None             # an Arabic desc that is verbatim in the text
        if len(phr) > 1: it['_phrase'] = phr
        if ev.get('cert'): it['cert'] = ev['cert']
        set_note(it, ev)
        evs.append(it)
    if evs: meta['events'] = evs

    gnotes = []
    for n in r.get('notes') or []:
        t = flat_text(n)
        if not t: continue
        g = {'text': t}
        for a in ('lang', 'type', 'cert'):
            if n.get(a): g[a] = n[a]
        if n.get('target'): g['target'] = norm_id(n['target'])          # the heading a cross-reference points to
        gnotes.append(g)
    for lr in r.get('listRelation') or []:
        for n in lr.get('notes') or []:
            t = flat_text(n)
            if t: gnotes.append({'text': t, **{a: n[a] for a in ('lang', 'type') if n.get(a)}, 'scope': 'relations'})
        for c_ in lr.get('comments') or []:
            if c_ and c_.strip(): gnotes.append({'text': c_.strip(), 'type': 'xml_comment', 'scope': 'relations'})
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
                if evs[j].get('quote') and evs[j]['quote'] != q:        # the verbatim phrase stays as phrase
                    evs[j].setdefault('_phrase', []).insert(0, evs[j]['quote'])
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
            if not (code == 'P' and it['id'][0] == 'e'):     # relation / office / name element: the item's quote
                if it.get('quote') is None: it['quote'] = Q(q, p)
            else:                                            # a person tag on an event: the quote of that person
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

    for lst in (rels, states, affs, evs, [meta.get('birth') or {}, meta.get('death') or {}]):
        for it in lst:
            ph = [p_ for p_ in dict.fromkeys(it.pop('_phrase', [])) if p_ != it.get('quote')]
            if ph: it['phrase'] = ' / '.join(ph)
    for lst in (names, rels, states, evs):
        for it in lst:
            it.pop('_partner', None); lab = it.pop('_label', None)
            if it.get('quote') is None:
                it['quote'] = None; STAT['noquote_' + it['id'][0]] += 1
                if lab and not it.get('ref'): it['label'] = lab
            elif lab and not it.get('ref') and lab != it.get('quote'):
                it['label'] = lab                         # the name element as written in the TEI (no ID)

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

    # assessments (Waka 2026-11-26): the biographer's characterisation of the person («وهو من الصلحاء», «كان خيرا دينا»).
    # Not an office, a status or an event: they get their own section (ids v1, v2 …, tags @V).
    # (1) evaluative entries are moved out of states[] (state ids are kept, gaps allowed);
    # (2) the stock formulas are picked up from the text by rule (by: rule) for confirmation in the viewer.
    covered = set()
    for i_, t_ in enumerate(toks):
        m_ = ENT.match(t_) or YR.match(t_)
        n_ = None
        if m_: n_ = int(m_.group(3)) if ENT.match(t_) else (int(m_.group(4)) if m_.group(4) else 1)
        else:
            m2 = re.match(r'^@L(\d+)X\d\dL$', t_)
            if m2: n_ = int(m2.group(1))
            elif t_.startswith('@'): n_ = 0
        if n_ is not None: covered.update(range(i_, i_ + n_ + 1))
    def vterm(w):
        """(term, prefix) of an evaluative word, or None"""
        w0 = normalize_ara_light(w)
        for pfx in (0, 1):
            x = w0[pfx:] if pfx and w0[:1] == 'و' and len(w0) > 3 else (w0 if not pfx else None)
            if x and x in VFORM: return VFORM[x], pfx
        return None
    assess, inserts, vretag, vlabels, vat = [], [], {}, [], []
    def add_v(it):
        it['id'] = f'v{len(assess) + 1}'; assess.append(it); STAT['assessment'] += 1; return it['id']
    keep_s = []
    for st in meta.get('states') or []:
        lab = st.get('quote') or st.get('label') or ''
        terms = []
        for w_ in lab.split():
            vt = vterm(w_)
            if vt and vt[0] not in terms: terms.append(vt[0])
        if st['type'] == 'status' and not st.get('ref') and (terms or re.match(VREP, normalize_ara_light(lab))):
            it = {'id': None}
            if st.get('quote'): it['quote'] = st['quote']
            if st.get('norm'): it['norm'] = st['norm']
            if st.get('label') and st['label'] != st.get('quote'):     # the TEI wording of the reputation: a phrase, not a name
                it['phrase'] = st['label'] if not st.get('phrase') else st['label'] + ' / ' + st['phrase']
            it['terms'] = terms
            for kk, vv in st.items():                  # everything else the state carried
                if kk not in ('id', 'type', 'quote', 'norm', 'label') and kk not in it: it[kk] = vv
            vid = add_v(it); vretag[st['id']] = vid; STAT['assessment_from_status'] += 1
            if st.get('label'): vlabels.append(st['label'])
        else:
            keep_s.append(st)
    if vretag:
        if keep_s: meta['states'] = keep_s
        else: del meta['states']
        for i_, t_ in enumerate(new):
            m_ = re.match(r'^@O(\d+)\[[^|\]]*\|(s\d+)\]$', t_)
            if m_ and m_.group(2) in vretag:
                new[i_] = f'@V{m_.group(1)}[assessment|{vretag[m_.group(2)]}]'; vat.append([i_, f'@V{m_.group(1)}[assessment:{vretag[m_.group(2)]}]'])
    used_v = set()
    for it in assess:                                 # moved entries without a place: look for their word in the text
        if it.get('quote'): continue
        for i_, t_ in enumerate(toks):
            if i_ in covered or i_ in used_v: continue
            vt = vterm(t_)
            if vt and vt[0] in it['terms']:
                it['quote'] = t_; nm = norm_ar(t_, vt[1])
                if nm != t_: it['norm'] = nm
                it['by'] = 'rule'
                inserts.append((i_, vt[1], it['id'])); used_v.add(i_); break
    have = {t for it in assess for t in it['terms']}
    i_ = 0
    while i_ < len(toks) - 1:                         # stock formulas: كان / وهو (+ من [أهل]) + evaluative word(s)
        if normalize_ara_light(toks[i_]) in VTRIG and i_ not in covered:
            j_ = i_ + 1; plural_ok = False
            if j_ < len(toks) and toks[j_] == 'من': j_ += 1; plural_ok = True
            if plural_ok and j_ < len(toks) and toks[j_] == 'أهل': j_ += 1
            while j_ < len(toks) and j_ not in covered and j_ not in used_v:
                vt = vterm(toks[j_])
                if not vt: break
                w0 = normalize_ara_light(toks[j_])[vt[1]:]
                if (w0 in VPLUR) != plural_ok: break
                if vt[0] == 'ساكن' and j_ + 1 < len(toks) and re.match(r'^(ب|في|@T)', toks[j_ + 1]): break   # «ساكنا بـ…» = residing
                if vt[0] not in have:
                    it = {'id': None, 'quote': toks[j_]}
                    nm = norm_ar(toks[j_], vt[1])
                    if nm != toks[j_]: it['norm'] = nm
                    it['terms'] = [vt[0]]; it['by'] = 'rule'
                    inserts.append((j_, vt[1], add_v(it))); have.add(vt[0]); STAT['assessment_rule'] += 1
                used_v.add(j_); j_ += 1
            i_ = j_
        else:
            i_ += 1
    if assess:
        out = {}
        for kk, vv in meta.items():
            out[kk] = vv
            if kk == ('states' if 'states' in meta else 'relations' if 'relations' in meta else 'name'): out['assessments'] = assess
        meta.clear(); meta.update(out)
        VMAP[k] = {'retag': vretag, 'insert': [[i__, f'@V{p__}1[assessment:{v__}]'] for i__, p__, v__ in inserts], 'labels': vlabels, 'retag_at': vat}
        for i__, p__, v__ in sorted(inserts, reverse=True):
            new.insert(i__, f'@V{p__}1[assessment|{v__}]')

    # source citations (Waka 2026-11-26): «ذكره / أرخه / قال فلان» is a statement about the sources, not an event
    # in the person's life. They move from events[] to sources[] (ids c1, c2 …); event ids are kept (gaps allowed).
    if meta.get('events'):
        srcs, keep, cmap = [], [], {}
        for ev in meta['events']:
            if ev.get('type') == 'cultural' and ev.get('subtype') == 'mention':
                c = {'id': f'c{len(srcs) + 1}'}
                for kk, vv in ev.items():                 # everything the event carried (type/subtype = the section)
                    if kk not in ('id', 'type', 'subtype'): c[kk] = vv
                cmap[ev['id']] = c['id']; srcs.append(c); STAT['source_citation'] += 1
            else:
                keep.append(ev)
        if srcs:
            if keep: meta['events'] = keep
            else: del meta['events']
            out = {}
            for kk, vv in meta.items():
                out[kk] = vv
                if kk == ('events' if keep else 'affiliations' if 'affiliations' in meta else 'states'): out['sources'] = srcs
            if 'sources' not in out: out['sources'] = srcs
            meta.clear(); meta.update(out)
            for i_, t_ in enumerate(new):
                m_ = re.match(r'^@E(\d+)\[([^|\]]*)\|(e\d+)\]$', t_)
                if m_ and m_.group(3) in cmap: new[i_] = f'@C{m_.group(1)}[mention|{cmap[m_.group(3)]}]'
            CMAP[k] = cmap

    if MENTIONS: to_mentions(k, meta, new); refine_spans(k, meta, new)
    tr = TR.get(k)
    if tr: meta['translation'] = tr
    meta['provenance'] = provenance(r.get('generator'))

    header = f"### $ {k}" if k.startswith('AIND') else f"### $ #{k}"
    md = header + '\n' + ' '.join(new) + '\n'
    return meta, md


# ---- mentions (2026-11-27): a tag in the text carries only its kind, its span and a mention id -------------
# @P12[father:AIND-D00280|r1]  ->  @P12[m3]   with  mentions: [{id: m3, kind: person, quote, norm, ref: AIND-D00280}]
# Items point to the mention (`mention: m3`; a relation's partner side becomes m3); the ID and the quoted words
# live on the mention only. Items that no tag places keep `mention: null` (the former `quote: null`).
MENTIONS = os.environ.get('AIND_MENTIONS', '1') != '0'
KIND = {'P': 'person', 'T': 'place', 'S': 'name', 'O': 'office', 'E': 'event', 'C': 'source', 'V': 'assessment',
        'YB': 'year', 'YD': 'year', 'YY': 'year', 'YA': 'age', 'L': 'month'}
TAG2 = re.compile(r'^@(P|T|S|O|E|C|V)(\d)(\d+)\[([^\]]*)\]$')


def to_mentions(k, meta, new):
    items = {}
    for it in (meta.get('name') or {}).get('elements') or []: items[it['id']] = it
    for sec in ('relations', 'states', 'affiliations', 'events', 'sources', 'assessments'):
        for it in meta.get(sec) or []: items[it['id']] = it
    for kk in ('birth', 'death'):
        if meta.get(kk): items[meta[kk]['id']] = meta[kk]
    holders = [meta.get('birth'), meta.get('death'), *(meta.get('states') or []), *(meta.get('events') or []),
               *(meta.get('sources') or []), *(meta.get('affiliations') or []),
               *[c for r_ in meta.get('relations') or [] for c in r_.get('context', [])]]
    places = [pl for h in holders if h for pl in h.get('places') or []]
    ments = []
    def words(i, n):
        out, j = [], i + 1
        while len(out) < n and j < len(new):
            if not new[j].startswith('@'): out.append(new[j])
            j += 1
        return ' '.join(out)
    def move(src, m):                                   # the quoted words go from the item to the mention
        for a in ('quote', 'norm'):
            if src.get(a) is not None and a not in m: m[a] = src[a]
            src.pop(a, None)
    for i, t in enumerate(new):
        m_ = TAG2.match(t); y_ = YR.match(t); l_ = LM.match(t)
        if not (m_ or y_ or l_): continue
        mid = f'm{len(ments) + 1}'
        if m_:
            code, p, n = m_.group(1), int(m_.group(2)), int(m_.group(3))
            body, _, iid = m_.group(4).partition('|')
            sub, rid = parse_br(body)
            if rid == 'NEEDID': rid = None
            m = {'id': mid, 'kind': KIND[code]}
            if iid and iid not in items and iid in CMAP.get(k, {}): iid = CMAP[k][iid]   # event moved to sources
            it = items.get(iid) if iid else None
            if not it and iid: STAT['mention_iid_missing_' + code] += 1
            if code == 'T':
                m['quote'] = words(i, n)
                if rid: m['ref'] = rid
                for pl in places:
                    if pl.get('ref') == rid and 'mention' not in pl:
                        pl['mention'] = mid; pl.pop('ref', None); move(pl, m); STAT['mention_place'] += 1
                m.pop('norm', None); nm = norm_ar(m['quote'], p)
                if nm != m['quote']: m['norm'] = nm
            elif code == 'P' and it is not None and iid[0] == 'r':
                side = ('active' if rid and it.get('active') == rid else 'passive' if rid and it.get('passive') == rid
                        else 'active' if it.get('active') != k else 'passive')
                m['ref'] = it[side]; it[side] = mid; move(it, m); STAT['mention_rel'] += 1
            elif code == 'P' and it is not None:                       # a person on an event / source
                pe = next((pp for pp in it.get('persons') or [] if pp.get('ref') == rid and 'mention' not in pp), None)
                if pe is not None:
                    m['ref'] = pe.pop('ref'); pe['mention'] = mid; move(pe, m); STAT['mention_ev_person'] += 1
                else:
                    if rid: m['ref'] = rid
                    m['quote'] = words(i, n); STAT['mention_unlinked_evperson'] += 1
            elif it is not None:                                     # name element, office, event, source, assessment
                if rid and it.get('ref') == rid: m['ref'] = it.pop('ref')
                elif rid: m['ref'] = rid; STAT['mention_ref_differs' if it.get('ref') else 'mention_ref_tag_only'] += 1
                it['mention'] = mid; move(it, m); STAT['mention_item'] += 1
            else:
                if rid: m['ref'] = rid
                if sub and code in ('P', 'O', 'S'): m['tag_type'] = sub       # the tag's own type when no item takes it
                m['quote'] = words(i, n); STAT['mention_unlinked_' + code] += 1
            if 'quote' not in m: m['quote'] = words(i, n)
            new[i] = f'@{code}{p}{n}[{mid}]'
        elif y_:
            code, n = y_.group(1), int(y_.group(4)) if y_.group(4) else 1
            m = {'id': mid, 'kind': KIND[code], 'value': y_.group(2).lstrip('0') + (('-' + y_.group(3).lstrip('0')) if y_.group(3) else '')}
            it = meta.get('death') if code == 'YD' else meta.get('birth') if code == 'YB' else None
            q = words(i, n)
            if it is not None and it.get('quote') == q and 'mention' not in it:
                it['mention'] = mid; move(it, m)
            m.setdefault('quote', q)
            new[i] = f'@Y0{n}[{mid}]' if code != 'YA' else f'@A0{n}[{mid}]'
        else:
            n = int(l_.group(1))
            m = {'id': mid, 'kind': 'month', 'value': int(l_.group(2)), 'quote': words(i, n)}
            new[i] = f'@L0{n}[{mid}]'
        ments.append(m)
    # items nobody placed: `quote: null` becomes `mention: null`; a verbatim phrase without a place stays as phrase
    for it in items.values():
        if 'mention' in it: continue
        if it['id'][0] == 'r':                         # a relation is placed when a partner side is a mention
            it.pop('quote', None); it.pop('norm', None); continue
        if 'quote' in it:
            q = it.pop('quote'); it.pop('norm', None)
            if q is not None and it is not meta.get('birth') and it is not meta.get('death'):
                it['phrase'] = q if not it.get('phrase') else q + ' / ' + it['phrase']
            elif q is not None:
                it['phrase'] = q
            it['mention'] = None
    for pl in places:                                  # a place quote that no tag claimed (should not happen)
        if 'quote' in pl and 'mention' not in pl: pl['phrase'] = pl.pop('quote'); pl.pop('norm', None)
    if ments:
        out = {}
        for kk, vv in meta.items():
            if kk in ('translation', 'provenance') and 'mentions' not in out: out['mentions'] = ments
            out[kk] = vv
        if 'mentions' not in out: out['mentions'] = ments
        meta.clear(); meta.update(out)


# ---- spans (2026-11-27) ------------------------------------------------------------------------------------
# year: «سنة» and the number words after it; event: the verbatim phrase from the TEI where there is one, else from
# the head word to the end of the clause (span: rule); no event tag where an office tag lies inside the span (the
# office says it); a short laqab right before a person tag (الشرف إبراهيم) belongs to the person.
NUMW = set(normalize_ara_light(w) for w in ('واحد احدى إحدى اثنتين اثنين ثنتين ثلاث ثلاثة أربع اربع أربعة خمس خمسة ست ستة سبع سبعة '
        'ثمان ثماني ثمانية تسع تسعة عشر عشرة عشرين ثلاثين أربعين اربعين خمسين ستين سبعين ثمانين تسعين مائة مئة مائتين '
        'ثلاثمائة أربعمائة اربعمائة خمسمائة ستمائة سبعمائة ثمانمائة ثمانمئة تسعمائة بضع بضعة الف ألف').split())
LAQAB = set(normalize_ara_light(w) for w in ('الشرف البدر الشمس التقي الزين العلاء الجلال الكمال الجمال الشهاب النور المحب '
        'الولوي السراج العز الصلاح البرهان الفخر المجد الصدر العماد النجم الشرفي البدري الزيني الشمسي التاج الركن الرضي '
        'الامين القطب الحافظ الناصري السيفي العلم الكمالي الجلالي السعد الغرس الخير').split())
TAGX = re.compile(r'^@([A-Z])(\d)(\d+)\[(m\d+)\]$')
STOPCL = {'.', '،', ',', ':', '؛', 'ثم'}


def refine_spans(k, meta, new):
    M = {m['id']: m for m in meta.get('mentions') or []}
    def plain_after(i, n):            # indices of the next n plain words after position i
        out, j = [], i + 1
        while len(out) < n and j < len(new):
            if not new[j].startswith('@'): out.append(j)
            j += 1
        return out
    def set_tag(i, n):
        m_ = TAGX.match(new[i]); new[i] = f'@{m_.group(1)}{m_.group(2)}{n}[{m_.group(4)}]'
    # 1. year spans
    for i, t in enumerate(new):
        m_ = TAGX.match(t)
        if not m_ or m_.group(1) != 'Y': continue
        idx = plain_after(i, 12)
        if not idx: continue
        n = 1
        for j in idx[1:]:
            w = normalize_ara_light(new[j]); w = w[1:] if w[:1] == 'و' and w[1:] in NUMW else w
            if w in NUMW: n += 1
            else: break
        if n > int(m_.group(3)):
            set_tag(i, n); M[m_.group(4)]['quote'] = ' '.join(new[j] for j in idx[:n]); STAT['span_year'] += 1
    # 5. laqab before a person
    for i, t in enumerate(list(new)):
        m_ = TAGX.match(new[i]) if i < len(new) else None
        if not m_ or m_.group(1) != 'P' or i == 0: continue
        prev = new[i - 1]
        if not prev.startswith('@') and normalize_ara_light(prev) in LAQAB:
            n = int(m_.group(3)) + 1
            new[i - 1], new[i] = f'@P{m_.group(2)}{n}[{m_.group(4)}]', prev
            mm = M[m_.group(4)]; mm['quote'] = prev + ' ' + mm['quote']; mm.pop('norm', None)
            nm = norm_ar(mm['quote'], int(m_.group(2)))
            if nm != mm['quote']: mm['norm'] = nm
            STAT['span_laqab'] += 1
    # 2/3. events
    evs = meta.get('events') or []
    def drop_tag(mid):
        for i, t in enumerate(new):
            m_ = TAGX.match(t)
            if m_ and m_.group(4) == mid: del new[i]; return i
        return -1
    plainpos = lambda: [i for i, t in enumerate(new) if not t.startswith('@')]
    for ev in evs:
        ph = ev.get('phrase'); mid = ev.get('mention')
        pos = None
        if ph and ' / ' not in ph:
            pw = ph.split(); pp = plainpos(); words = [new[i] for i in pp]
            for a in range(len(words) - len(pw) + 1):
                if words[a:a + len(pw)] == pw: pos = (pp[a], len(pw)); break
        if pos:
            if mid: drop_tag(mid); pp = plainpos(); words = [new[i] for i in pp]; a = words.index(pw[0]) if False else None
            # recompute the start after a possible deletion
            pp = plainpos(); words = [new[i] for i in pp]
            a = next(x for x in range(len(words) - len(pw) + 1) if words[x:x + len(pw)] == pw)
            start = pp[a]
            if not mid:
                mid = f'm{len(M) + 1}'; M[mid] = {'id': mid, 'kind': 'event'}; meta['mentions'].append(M[mid]); ev['mention'] = mid
            M[mid]['quote'] = ph; M[mid].pop('norm', None); M[mid]['span'] = 'phrase'
            ev.pop('phrase', None); ev.pop('trigger', None)
            while start > 0 and new[start - 1].startswith('@'): start -= 1      # outside the tags that start here
            new.insert(start, f'@E0{len(pw)}[{mid}]'); STAT['span_event_phrase'] += 1
            span_idx = (start, len(pw))
        elif mid:
            i = next((x for x, t in enumerate(new) if TAGX.match(t) and TAGX.match(t).group(4) == mid), None)
            if i is None: continue
            idx = plain_after(i, 40); n = 0
            for j in idx:
                if new[j] in STOPCL or (n >= 1 and re.match(r'^(?:و|ف)(?:كان|ولي|حج|جاور|دخل|سافر|حفظ|سمع|أخذ|اخذ|مات|ولد|ناب|قدم|رجع|عاد|استقر|درس|أقرأ|اقرا|حدث|أفتى|افتى|لازم|تزوج|توجه|انتقل|سكن|نزل|قرأ|قرا|اشتغل|تكسب|تنزل|باشر|ترجمه|ذكره|كتب|صنف|عرض)', new[j])): break
                n += 1
                if n >= 12: break
            if n < 1: n = 1
            set_tag(i, n); M[mid]['quote'] = ' '.join(new[j] for j in idx[:n]); M[mid].pop('norm', None)
            M[mid]['span'] = 'rule'; ev.pop('trigger', None); STAT['span_event_rule'] += 1
            span_idx = (i, n)
        else:
            continue
        # 3. an office tag inside the event span: the office already says it; no event tag
        i0, n0 = span_idx
        inner = []; cnt = 0; j = i0 + 1
        while cnt < n0 and j < len(new):
            if new[j].startswith('@'): inner.append(new[j])
            else: cnt += 1
            j += 1
        offs = [TAGX.match(t).group(4) for t in inner if TAGX.match(t) and TAGX.match(t).group(1) == 'O']
        if offs and ev.get('type') in ('political', 'other', 'cultural', None):
            del new[i0]; ev['mention'] = None; ev['phrase'] = M[mid]['quote']; ev['overlaps'] = offs
            meta['mentions'].remove(M.pop(mid)); STAT['event_tag_dropped_office'] += 1


CMAP = {}
VMAP = {}
# evaluative vocabulary: written form (after normalize_ara_light) -> controlled term
_V = {'صالح': 'صالحا صالح الصلحاء الصالحين', 'خير': 'خيرا خير الاخيار الخير', 'دين': 'دينا دين', 'فاضل': 'فاضلا فاضل الفضلاء',
      'ثقة': 'ثقة', 'زاهد': 'زاهدا زاهد الزهاد', 'عابد': 'عابدا عابد', 'متعبد': 'متعبدا متعبد', 'ورع': 'ورعا ورع',
      'متواضع': 'متواضعا متواضع', 'معتقد': 'معتقدا معتقد المعتقدين', 'عفيف': 'عفيفا عفيف', 'ساكن': 'ساكنا'}
VFORM = {f: t for t, fs in _V.items() for f in fs.split()}
VPLUR = {'الصلحاء', 'الصالحين', 'الاخيار', 'الخير', 'الفضلاء', 'الزهاد', 'المعتقدين'}
VTRIG = {'كان', 'وكان', 'فكان', 'وهو', 'هو'}
VREP = r'^(?:و|ف)?(?:يذكر|ذكر|يوصف|وصف|موصوف|ينسب)\s*ب'   # «ويذكر بحذق وذكاء …»: a reputation, not a status (2026-11-27)


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
    json.dump({'sources': CMAP, 'assessments': VMAP}, open(f'{OUT}/source_ids.json', 'w'), ensure_ascii=False)   # event id -> source id, per record
    print('files', len(R), 'meta MB', round(tot_y / 1e6, 2), 'text MB', round(tot_m / 1e6, 2))
    print(dict(sorted(STAT.items())))
    # required check (Waka 2026-11-27): every TEI value except the edit history must be in the YAML
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from audit_tei_vs_yaml import audit
    miss, dropped, lines = audit(R, OUT, os.path.join(OUT, 'audit_tei_vs_yaml.tsv'))
    print('dropped on purpose:', dict(dropped))
    if miss:
        print('FAILED: TEI values missing from the YAML (see audit_tei_vs_yaml.tsv):', file=sys.stderr)
        print('\n'.join(lines[:30]), file=sys.stderr)
        sys.exit(1)
    print('audit: every TEI value is in the YAML (or on the dropped-on-purpose list)')
