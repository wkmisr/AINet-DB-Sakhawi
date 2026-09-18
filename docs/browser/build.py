import glob, re, json, collections, csv, os, sys
# usage: python3 build.py <Individuals dir> <idmaster.tsv> <corpus_index.json>  -> data.json (in cwd)
IND = sys.argv[1] if len(sys.argv)>1 else 'Individuals'
IDM = sys.argv[2] if len(sys.argv)>2 else 'idmaster.tsv'
CIX = sys.argv[3] if len(sys.argv)>3 else 'corpus_index.json'
from lxml import etree

XML_NS = '{http://www.w3.org/XML/1998/namespace}'
def lang(e): return e.get(XML_NS + 'lang') or ''

def notes_split(el, textfn):
    """Return {'note': <en/neutral>, 'note_ja': <ja>} for an element's <note> children."""
    out = {}
    en = [textfn(n) for n in el.findall('note') if textfn(n) and lang(n) not in ('ja',)]
    ja = [textfn(n) for n in el.findall('note') if textfn(n) and lang(n) == 'ja']
    if en: out['note'] = ' / '.join(en)
    if ja: out['note_ja'] = ' / '.join(ja)
    return out


# ---------- ID-Master (Arabic name per ID) ----------
idm = {}
for row in csv.reader(open(IDM, encoding='utf-8'), delimiter='\t'):
    if len(row) > 4 and row[4]:
        idm.setdefault(row[4].strip(), (row[2].strip(), row[3].strip(), row[1].strip()))

def id_name(ref):
    if not ref: return ''
    r = ref.lstrip('#')
    e = idm.get(r)
    return e[0] if e else ''

CORPUS = json.load(open(CIX, encoding='utf-8'))
def corpus_headword(aid):
    e = CORPUS.get(aid)
    if not e: return ''
    t = re.sub(r'^\d+\s+', '', e['text']).replace('\n', ' ')
    head = t.split(' . ')[0]
    out = [' '.join(head.split()[:25])]
    for m in re.finditer(r'ويعرف (?:قديما |أيضا )?ب(?:ال)?([؀-ۿ]+(?: [؀-ۿ]+){0,2})', t[:600]):
        out.append(m.group(1))
    return out

SPECIAL = {'wd:Q4120128': ['عني', 'مني', 'لازمني', 'لقيني', 'أجازني', 'أجاز لي', 'كتبت عنه', 'رأيته', 'صاحبنا', 'حضر عندي', 'سمعت منه', 'أخذت عنه'],
           'wd:Q471116': ['شيخنا', 'ابن حجر'], '#AIND-D09211': ['ابن فهد', 'التقي بن فهد'], '#AIND-D05979': ['النجم بن فهد', 'ابن فهد'],
           '#AIND-D03985': ['العز بن فهد']}
# ---------- coordinates for geonames refs (hand-coded gazetteer) ----------
GN = {
 '104515': (21.4267, 39.8261), '360630': (30.0444, 31.2357), '170654': (33.5138, 36.2765), '109223': (24.4686, 39.6142),
 '170063': (36.2021, 37.1343), '266826': (34.4367, 35.8497), '352261': (30.0, 31.2), '281184': (31.7683, 35.2137),
 '361058': (31.2001, 29.9187), '293100': (32.9648, 35.4959), '277130': (34.0058, 36.2181), '358048': (31.4165, 31.8133),
 '285066': (31.5326, 35.0998), '170017': (35.1318, 36.7578), '2464470': (36.8065, 10.1815), '282615': (32.2211, 35.2544),
 '2505329': (36.7509, 5.0567), '304922': (38.3552, 38.3095), '325363': (36.9914, 35.3308), '276781': (33.8938, 35.5018),
 '305608': (38.3552, 38.3095), '109600': (23.5, 39.5), '359146': (27.75, 30.8), '2516422': (37.3, -3.13),
 '346030': (30.7143, 31.2444), '105995': (23.78, 38.79), '361546': (31.1313, 33.7984), '415189': (12.7855, 45.0187),
 '268064': (33.5571, 35.3729), '315372': (39.75, 39.5), '321062': (37.0263, 37.9738), '12440535': (30.05, 31.26),
 '2464917': (35.8256, 10.6369), '2485926': (35.6971, -0.6308), '299817': (36.9165, 34.8951), '104889': (21.4133, 39.8933),
 '692713': (45.0, 34.1), '352735': (30.96, 31.24), '2464915': (35.8256, 10.6369), '172041': (34.0058, 36.2181),
 '2472706': (37.2744, 9.8739), '105299': (16.8892, 42.5511), '2210247': (32.8872, 13.1913), '340218': (15.63, 40.1),
 '750269': (40.1885, 29.061), '1273294': (28.6139, 77.209), '170905': (32.625, 36.105), '349715': (30.9617, 31.2433),
 '2507026': (36.7538, 3.0588), '10594248': (21.4225, 39.8262),
}

# ---------- Arabic normalisation ----------
DIAC = re.compile(r'[ً-ْٰـۖ-ۭ]')
def norm(s):
    s = DIAC.sub('', s)
    s = re.sub('[أإآٱ]', 'ا', s)
    s = s.replace('ة', 'ه').replace('ى', 'ي').replace('ؤ', 'و').replace('ئ', 'ي').replace('ء', '')
    return s
def ntoks(s):
    """normalised tokens (drop punctuation); 'ابن' -> 'بن'"""
    out = []
    for w in re.findall(r'[؀-ۿ]+', s):
        w = norm(w)
        if w == 'ابن': w = 'بن'
        if w: out.append(w)
    return out

PREFIXES = ['', 'و', 'ف', 'ب', 'ل', 'ك', 'وب', 'فب', 'ول', 'فل', 'ال', 'وال', 'بال', 'فال', 'لل', 'ولل']
GIVEN = set(ntoks('محمد أحمد علي عبد الله الرحمن إبراهيم عمر عثمان أبو أبي بن بنت الدين حسن حسين يوسف إسماعيل خليل بكر قاسم عبد يحيى موسى إسحاق داود سليمان ابن أم والد أخو جد ابنة الآتي الماضي'))
COMMON = set(ntoks('محمد أحمد علي عبد الله الرحمن إبراهيم عمر عثمان أبو أبي بن بنت الدين حسن حسين يوسف إسماعيل خليل بكر قاسم عبد يحيى موسى إسحاق داود سليمان الشيخ القاضي الشمس التقي الجمال البدر الزين الشهاب النور الكمال العز الفخر البرهان السراج التاج الولي المحب الجلال المجد الصلاح الشرف الصدر البهاء المكي القاهري الشافعي الحنفي المالكي الحنبلي الدمشقي المصري ابن أم والد أخو جد ابنة الآتي الماضي'))

FIRSTP_VERBS = set(ntoks('سمع وسمع قرأ وقرأ عرض عرضها عرضه عرضهما وعرض أخذ وأخذ اشتغل واشتغل حضر وحضر لازم ولازم كتب وكتب أجاز قرأه فسمع فقرأ فعرض'))

# tokens that are never a name element: "known as" markers, bare kinship descriptors and a few
# narrative verbs.  Derived empirically from the mis-highlighted person spans of the 2,359-record
# build (see e.g. AIND-D00420 'ويعرف' and 'وأسند وصيته إليه'), not guessed.
# A candidate window containing any of these is refused; SPECIAL candidates are exempt, because the
# al-Sakhawi heuristics deliberately match first-person verb phrases.
STOP = set(ntoks('ويعرف يعرف وتعرف تعرف ويدعى يدعى ويدعي يدعي '
                 'أسند وأسند وصيته إليه إليها '
                 'شقيق شقيقه شقيقة نزيل ربيب الأصل بالنسبة الجماعة الزعيم'))

# "... ويعرف بابن الزهري" / "... المعروف بالكلوتاتي": the clause marker, with the attached bi-/ka-.
KNOWN_AS = re.compile(r'(?<![؀-ۿ])\s*(?:و?يعرف|و?تعرف|و?يدعى|و?يدعي|المعروفة?)'
                      r'\s+(?:قديما\s+|أيضا\s+|كأبيه\s+|كسلفه\s+|كجده\s+)?[بك]')
SPLIT_RE = re.compile(r'\s*[—–]\s*|\s+-\s+|[|｜]')
PAREN_RE = re.compile(r'[（(][^）)]*[）)]')
PAREN_IN = re.compile(r'[（(]([^）)]*)[）)]')

def clean_cands(s):
    """Split one stored name/desc string into name-shaped candidate strings, best first.

    Handles the three shapes that produce phrase-matches: a parenthetical gloss, an
    explanatory tail after an em dash, and a "known as" clause.  The shuhrah after
    'ويعرف ب' is kept as its own candidate (it is a real name for that person) but can
    no longer be reached through the marker token."""
    if not s: return []
    parens = [x.strip() for x in PAREN_IN.findall(s)]
    s = PAREN_RE.sub(' ', s)
    parts = []
    for seg in SPLIT_RE.split(s):
        seg = (seg or '').strip()
        if not seg: continue
        m = KNOWN_AS.search(seg)
        if m:
            head, tail = seg[:m.start()].strip(), seg[m.end():].strip()
            if head: parts.append(head)
            if tail: parts.append(tail)
        else:
            parts.append(seg)
    parts += [x for x in parens if x]
    out = []
    for x in parts:
        tk = ntoks(x)
        if not tk or all(t in STOP for t in tk): continue   # evidently a phrase, not a name
        if x not in out: out.append(x)
    return out

def tokenize_src(text):
    """tokens of source text with char offsets"""
    toks = []
    for m in re.finditer(r'[؀-ۿ]+', text):
        w = m.group(0); n = norm(w)
        if n == 'ابن': n = 'بن'
        toks.append((n, m.start(), m.end()))
    return toks

def find_seq(stoks, seq, start=0, allow_prefix=True):
    """find token sequence in source tokens; first token may carry a clitic prefix. returns (i,j) token idx or None"""
    L = len(seq)
    for i in range(start, len(stoks) - L + 1):
        t0 = stoks[i][0]
        ok = t0 == seq[0]
        if not ok and allow_prefix:
            for p in PREFIXES[1:]:
                if t0 == p + seq[0] or (seq[0] == 'بن' and t0 == p + 'ابن'): ok = True; break
        if not ok: continue
        if all(stoks[i + k][0] == seq[k] for k in range(1, L)):
            return i, i + L - 1
    return None

def strip_clitic(t, vocab):
    """token as it appears in the source, reduced to a member of `vocab` if a clitic explains it"""
    if t in vocab: return t
    for p in PREFIXES[1:]:
        if t.startswith(p) and t[len(p):] in vocab: return t[len(p):]
        if t == p + 'ابن' and 'بن' in vocab: return 'بن'
    return None

# normalisation folds ى into ي, so the preposition على looks like the name علي: never extend over
# one of these in its raw spelling.
NOEXT_RAW = set('على عن في من إلى الى مع عند ثم قد بل أو او ما لا ان أن'.split())

def extend_left(stoks, i, vocab, taken, src, maxsteps=2):
    """Grow a matched window leftwards over tokens that belong to the same name but were not
    contiguous in the stored form: the text cites 'الشرف بن مفلح' while the register holds
    'الشرف عبد الله بن مفلح', so the longest contiguous window is only 'بن مفلح'.
    Never crosses an already-taken span or a sentence break."""
    k = i
    for _ in range(maxsteps):
        if k == 0: break
        pt, ps, pe = stoks[k - 1]
        base = strip_clitic(pt, vocab)
        if base is None or base in ('بن',) or base in STOP: break
        if src and src[ps:pe] in NOEXT_RAW: break
        if any(ps < te and pe > ts for ts, te in taken): break
        gap = src[pe:stoks[k][1]] if src else ''
        if '.' in gap or '%' in gap: break
        k -= 1
    return k

def match_name(stoks, name, taken, min_single_len=4, src='', use_stop=True, extend=True):
    """try to locate a (possibly reconstructed) name in the source text. returns span (s,e) or None"""
    seq = ntoks(name)
    seq = [t for t in seq if t not in ('...',)]
    if not seq: return None
    n = len(seq)
    vocab = set(seq)
    # windows from longest to shortest, starting at any position
    for L in range(min(n, 8), 0, -1):
        for a in range(0, n - L + 1):
            sub = seq[a:a + L]
            if use_stop and any(w in STOP for w in sub): continue
            if L > 1 and sub[-1] == 'بن': continue   # no name ends in 'b.' -- that is a mid-phrase window
            if L == 1:
                w = sub[0]
                if w in COMMON or len(w) < min_single_len: continue
            elif L == 2 and all(w in GIVEN for w in sub):
                continue
            pos = 0
            while True:
                r = find_seq(stoks, sub, pos)
                if r is None: break
                s, e = stoks[r[0]][1], stoks[r[1]][2]
                if not any(s < te and e > ts for ts, te in taken):
                    i0 = extend_left(stoks, r[0], vocab, taken, src) if extend else r[0]
                    return (stoks[i0][1], e, L + (r[0] - i0))
                pos = r[0] + 1
    return None

MONTHS = ['المحرم', 'محرم', 'صفر', 'ربيع الأول', 'ربيع الآخر', 'ربيع الثاني', 'جمادى الأولى', 'جمادى الأخرى', 'جمادى الآخرة', 'جمادى الثانية',
          'رجب', 'شعبان', 'رمضان', 'شوال', 'ذي القعدة', 'ذي الحجة', 'ذو القعدة', 'ذو الحجة']
NUMW = r'(?:ثمانماية|ثمانمائة|تسعمائة|سبعمائة|تسعماية|سبعماية|اثنتين|أربعين|ستمائة|ثمانين|ثلاثين|اربعين|عشرين|تسعين|اثنين|سبعين|خمسين|أربع|احدى|مائة|إحدى|ثمان|ثلاث|اربع|ستين|بضع|نيف|سبع|مئة|أحد|خمس|تسع|عشر|ست)'
DATE_RE = re.compile(r'سنة\s+(?:' + NUMW + r'(?:\s+(?:و|و\s)?' + NUMW + r'){0,5}(?:\s+و\s*(?:سبعمائة|ثمانمائة|تسعمائة|ستمائة|سبعماية|ثمانماية|تسعماية|مائة|مئة))?)')
MONTH_RE = re.compile('|'.join(re.escape(m) for m in sorted(MONTHS, key=len, reverse=True)))

def txt(e):
    return (e.text or '').strip() if e is not None else ''

def year_of(v):
    if not v: return None
    m = re.match(r'-?(\d{3,4})', v)
    return int(m.group(1)) if m else None

records = {}
stats = collections.Counter()
files = sorted(glob.glob(os.path.join(IND, '*.xml')))
# first pass: person names for cross reference
pnames = {}
for f in files:
    t = etree.parse(f).getroot()
    pid = t.get(XML_NS + 'id')
    pnames[pid] = {p.get('type'): txt(p) for p in t.findall('persName') if lang(p) == 'ar'}
    pnames[pid]['_alts'] = [txt(p) for p in t.findall('persName') if lang(p) == 'ar' and p.get('type') in ('shuhrah', 'laqab', 'kunyah')]

def partner_names(ref):
    """candidate strings for a referenced person id"""
    out = []
    if not ref: return out
    out += SPECIAL.get(ref, [])
    r = ref.lstrip('#')
    if r.startswith('AIND-') and r not in pnames:
        out += corpus_headword(r)
    if r in pnames:
        pn = pnames[r]
        out += pn['_alts']
        for k in ('full', 'name_only'):
            if pn.get(k): out.append(pn[k])
    nm = id_name(ref)
    if nm:
        for part in nm.split('|'):
            out.append(part.strip())
    cleaned = []
    for x in out:
        for y in (clean_cands(x) if x not in SPECIAL.get(ref, []) else [x]):
            if y not in cleaned: cleaned.append(y)
    return cleaned

for f in files:
    t = etree.parse(f).getroot()
    pid = t.get(XML_NS + 'id'); src12 = t.get('source')
    isref = t.get('type') == 'reference'
    rec = {'id': pid, 'src': src12, 'ref': isref, 'file': os.path.basename(f)}
    names = collections.defaultdict(list)
    for p in t.findall('persName'):
        if lang(p) == 'ar' and txt(p): names[p.get('type') or 'other'].append({'t': txt(p), 'ref': p.get('ref') or ''})
        if lang(p) == 'ar-Latn' and p.get('type') == 'full': rec['latin'] = txt(p)
    rec['names'] = names
    rec['sex'] = (t.find('sex').get('value') if t.find('sex') is not None else '')
    for tag in ('death', 'birth'):
        e = t.find(tag)
        if e is not None:
            d = {'h': e.get('when-custom') or '', 'g': e.get('when') or '', 'cert': e.get('cert') or '',
                 'nb': e.get('notBefore-custom') or '', 'na': e.get('notAfter-custom') or ''}
            d['y'] = year_of(d['h']) or year_of(d['nb']) or year_of(d['na'])
            m = re.match(r'-?\d{3,4}-(\d{2})', d['h'])
            d['m'] = int(m.group(1)) if m else None
            pl = [{'t': txt(p), 'ref': p.get('ref') or ''} for p in e.findall('placeName') if lang(p) != 'ar-Latn' and txt(p)]
            if pl: d['place'] = pl[0]
            d.update(notes_split(e, txt))
            rec[tag] = d
    # relations
    rels = []
    for r in t.findall('.//relation'):
        act, pas = r.get('active') or '', r.get('passive') or ''
        partner = act if pas == '#' + pid else pas
        d = {'subtype': r.get('subtype') or '', 'active': act, 'passive': pas, 'partner': partner,
             'cert': r.get('cert') or '', 'n': r.get('n') or ''}
        for ds in r.findall('desc'):
            if lang(ds) == 'ar-Latn': continue
            ty = ds.get('type')
            if ty == 'method': d['method'] = txt(ds); d['method_ref'] = ds.get('ref') or ''
            elif ty == 'field': d['field'] = txt(ds); d['field_ref'] = ds.get('ref') or ''
            elif ty in (None, 'relationship_type'): d.setdefault('desc', txt(ds))
        d['bibl'] = [{'t': txt(b), 'ref': b.get('ref') or ''} for b in r.findall('bibl') if lang(b) != 'ar-Latn' and txt(b)]
        ev = r.find('event')
        if ev is not None:
            pl = [{'t': txt(p), 'ref': p.get('ref') or ''} for p in ev.findall('placeName') if lang(p) != 'ar-Latn' and txt(p)]
            if pl: d['place'] = pl[0]
            if ev.get('when-custom'): d['when'] = ev.get('when-custom')
        d.update(notes_split(r, txt))
        d['partner_name'] = id_name(partner) or (pnames.get(partner.lstrip('#'), {}).get('full', '') if partner else '')
        rels.append(d)
    rec['relations'] = rels
    # events (top level)
    evs = []
    for e in t.findall('event'):
        d = {'type': e.get('type') or '', 'subtype': e.get('subtype') or '', 'when': e.get('when-custom') or '', 'cert': e.get('cert') or ''}
        d['places'] = [{'t': txt(p), 'ref': p.get('ref') or ''} for p in e.findall('placeName') if lang(p) != 'ar-Latn' and txt(p)]
        d['persons'] = [{'t': txt(p), 'ref': p.get('ref') or ''} for p in e.findall('persName') if lang(p) != 'ar-Latn' and txt(p)]
        d['orgs'] = [{'t': txt(p), 'ref': p.get('ref') or ''} for p in e.findall('orgName') if lang(p) != 'ar-Latn' and txt(p)]
        d['bibl'] = [{'t': txt(b), 'ref': b.get('ref') or ''} for b in e.findall('bibl') if lang(b) != 'ar-Latn' and txt(b)]
        ds = [txt(x) for x in e.findall('desc') if lang(x) != 'ar-Latn' and txt(x)]
        if ds: d['desc'] = ' | '.join(ds)
        d.update(notes_split(e, txt))
        evs.append(d)
    rec['events'] = evs
    # states / offices
    sts = []
    for s in t.findall('.//state'):
        d = {'type': s.get('type') or '', 'ref': s.get('ref') or '', 'when': s.get('when-custom') or ''}
        lab = [txt(l) for l in s.findall('label') if lang(l) == 'ar' and txt(l)]
        labl = [txt(l) for l in s.findall('label') if lang(l) == 'ar-Latn' and txt(l)]
        d['label'] = lab[0] if lab else (txt(s.find('label')) if s.find('label') is not None else '')
        if labl: d['latin'] = labl[0]
        pl = [{'t': txt(p), 'ref': p.get('ref') or ''} for p in s.findall('placeName') if lang(p) != 'ar-Latn' and txt(p)]
        if pl: d['place'] = pl[0]
        og = [{'t': txt(p), 'ref': p.get('ref') or ''} for p in s.findall('orgName') if lang(p) != 'ar-Latn' and txt(p)]
        if og: d['org'] = og[0]
        dt = s.find('date')
        if dt is not None: d['date'] = dt.get('when-custom') or dt.get('when') or txt(dt)
        d.update(notes_split(s, txt))
        sts.append(d)
    rec['states'] = sts
    affs = []
    for a in t.findall('.//affiliation'):
        d = {'type': a.get('type') or '', 'ref': a.get('ref') or ''}
        og = [txt(p) for p in a.findall('orgName') if lang(p) != 'ar-Latn' and txt(p)]
        d['org'] = og[0] if og else txt(a)
        ogl = [txt(p) for p in a.findall('orgName') if lang(p) == 'ar-Latn' and txt(p)]
        if ogl: d['latin'] = ogl[0]
        pl = [{'t': txt(p), 'ref': p.get('ref') or ''} for p in a.findall('placeName') if lang(p) != 'ar-Latn' and txt(p)]
        if pl: d['place'] = pl[0]
        affs.append(d)
    rec['affiliations'] = affs
    # notes
    for n in t.findall('note'):
        ty = n.get('type')
        if ty == 'source': rec['source'] = txt(n)
        elif ty == 'translation':
            rec['ja' if lang(n) == 'ja' else 'en'] = txt(n)
        elif ty == 'reference': rec['reference'] = {'target': n.get('target') or '', 't': txt(n)}
        elif ty == 'personalia':
            lg = lang(n)
            key = 'personalia_ja' if lg == 'ja' else ('personalia_ar' if lg == 'ar' else 'personalia')
            rec[key] = (rec[key] + ' / ' + txt(n)) if rec.get(key) else txt(n)
    resp = []
    for rs in t.findall('respStmt'):
        resp.append({'resp': ' / '.join(txt(x) for x in rs.findall('resp')), 'who': txt(rs.find('persName')),
                     'date': (rs.find('date').get('when') if rs.find('date') is not None else '')})
    rec['resp'] = resp

    # ---------- entity alignment on source text ----------
    spans = []; taken = []
    src = rec.get('source', '')
    if src:
        stoks = tokenize_src(src)
        def add(kind, s, e, label, ref, extra=None):
            spans.append({'k': kind, 's': s, 'e': e, 'l': label, 'r': ref}); taken.append((s, e))
        # headword (self)
        # dates
        for dm in DATE_RE.finditer(src):
            if not any(dm.start() < te and dm.end() > ts for ts, te in taken): add('date', dm.start(), dm.end(), dm.group(0), '')
        for mm in MONTH_RE.finditer(src):
            if not any(mm.start() < te and mm.end() > ts for ts, te in taken): add('date', mm.start(), mm.end(), mm.group(0), '')
        # places: from death/birth/events/states/affiliations/relations
        placeset = {}
        for d in (rec.get('death'), rec.get('birth')):
            if d and d.get('place'): placeset[d['place']['t']] = d['place']['ref']
        for e in evs:
            for p in e['places']: placeset[p['t']] = p['ref']
        for s in sts + affs:
            if s.get('place'): placeset[s['place']['t']] = s['place']['ref']
        for r in rels:
            if r.get('place'): placeset[r['place']['t']] = r['place']['ref']
        for pt, pr in placeset.items():
            seq = ntoks(pt)
            if not seq: continue
            pos = 0; hit = False
            while True:
                rr = find_seq(stoks, seq, pos)
                if rr is None: break
                s, e = stoks[rr[0]][1], stoks[rr[1]][2]
                if not any(s < te and e > ts for ts, te in taken): add('place', s, e, pt, pr); hit = True
                pos = rr[0] + 1
            stats['place_hit' if hit else 'place_miss'] += 1
        # self headword first (soft exclusion for person matching: try outside the headword first)
        hw = names['full'][0]['t'] if names.get('full') else ''
        m = match_name(stoks, hw, [], src=src) if hw else None
        selfspan = {'k': 'self', 's': m[0], 'e': m[1], 'l': hw, 'r': '#' + pid} if m else None
        stats['self_hit' if m else 'self_miss'] += 1
        # The subject's OWN name in every registered form -- not just full[0] -- is protected, so a
        # relative sharing the family nisba can no longer grab the subject's shuhrah (the subject's
        # own 'ويعرف بابن الزهري' was being tagged as the father).  Every occurrence of one of the
        # subject's epithets, and of an office/affiliation registered for the subject, joins the
        # soft exclusion zone that person matching tries to stay out of.
        SELF_KEYS = ('full', 'name_only', 'nisbah', 'laqab', 'shuhrah', 'kunyah')
        selfstrs = [x['t'] for k in SELF_KEYS for x in names.get(k, [])]
        epithets = [x['t'] for k in ('nisbah', 'laqab', 'shuhrah', 'kunyah') for x in names.get(k, [])]
        epithets += [st.get('label') for st in sts if st.get('type') == 'office' and st.get('label')]
        epithets += [af.get('org') for af in affs if af.get('org')]
        selfzones = [(selfspan['s'], selfspan['e'])] if selfspan else []
        for sstr in epithets:
            sq = ntoks(sstr); pos = 0
            while sq:
                rr = find_seq(stoks, sq, pos)
                if rr is None: break
                selfzones.append((stoks[rr[0]][1], stoks[rr[1]][2]))
                pos = rr[0] + 1
        # persons: relations partners, event mentions
        cands = []
        for r in rels:
            c = []
            if r.get('desc'): c += clean_cands(r['desc'])
            c += partner_names(r['partner'])
            cands.append(('rel', r['subtype'], r['partner'], c, r))
        for e in evs:
            for p in e['persons']:
                c = clean_cands(p['t']) + partner_names(p['ref'])
                cands.append(('mention', e['subtype'] or e['type'], p['ref'], c, p))
        selftoks = set()
        for sstr in (selfstrs or ([hw] if hw else [])): selftoks |= set(ntoks(sstr))
        def nasab_frag(a, b):
            # a window made only of the subject's own name tokens (e.g. 'بن عبد الوهاب') is the subject's nasab, not a mention
            w = [t[0] for t in stoks if t[1] >= a and t[2] <= b]
            return len(w) <= 4 and all(x in selftoks for x in w)
        seen_ref = {}
        for kind, sub, ref, c, obj in cands:
            found = None
            if ref and ref in seen_ref:   # same partner referenced twice: reuse the first location
                obj['span'] = seen_ref[ref]; stats['person_hit'] += 1; continue
            taken_self = taken + selfzones
            for nm in c:
                sp = nm in SPECIAL.get(ref, [])
                found = match_name(stoks, nm, taken_self, min_single_len=(2 if sp else 4), src=src, use_stop=not sp)
                if found: break
            if not found:
                for nm in c:
                    sp = nm in SPECIAL.get(ref, [])
                    found = match_name(stoks, nm, taken, min_single_len=(2 if sp else 4), src=src, use_stop=not sp)
                    if found: break
            if not found and ref == 'wd:Q4120128':
                for i in range(1, len(stoks)):
                    if stoks[i][0] == 'علي' and stoks[i-1][0] in FIRSTP_VERBS and not any(stoks[i][1] < te and stoks[i][2] > ts for ts, te in taken):
                        found = (stoks[i][1], stoks[i][2], 1); break
            if found and sub not in ('father', 'grandfather', 'ancestor', 'great-grandfather') and nasab_frag(found[0], found[1]):
                found = None
            if found:
                add('person', found[0], found[1], obj.get('desc') or obj.get('t') or (c[0] if c else ''), ref)
                spans[-1]['sub'] = sub
                obj['span'] = len(spans) - 1
                if ref: seen_ref[ref] = len(spans) - 1
                stats['person_hit'] += 1
            else:
                stats['person_miss'] += 1
        # texts (bibl)
        for e in evs + rels:
            for b in e.get('bibl', []):
                seq = ntoks(b['t'])
                if not seq: continue
                rr = find_seq(stoks, seq, 0)
                if rr:
                    s, e2 = stoks[rr[0]][1], stoks[rr[1]][2]
                    if not any(s < te and e2 > ts for ts, te in taken): add('text', s, e2, b['t'], b['ref']); stats['text_hit'] += 1; continue
                stats['text_miss'] += 1
        # orgs (states/affiliations)
        for s in sts + affs:
            o = s.get('org')
            ot = o['t'] if isinstance(o, dict) else o
            if not ot: continue
            seq = ntoks(ot)
            rr = find_seq(stoks, seq, 0) if seq else None
            if rr:
                a, b2 = stoks[rr[0]][1], stoks[rr[1]][2]
                if not any(a < te and b2 > ts for ts, te in taken): add('org', a, b2, ot, (o.get('ref') if isinstance(o, dict) else s.get('ref')) or ''); stats['org_hit'] += 1; continue
            stats['org_miss'] += 1
        # offices (state labels)
        for s in sts:
            if s['type'] != 'office' or not s.get('label'): continue
            seq = ntoks(s['label'])
            rr = find_seq(stoks, seq, 0) if seq else None
            if rr:
                a, b2 = stoks[rr[0]][1], stoks[rr[1]][2]
                if not any(a < te and b2 > ts for ts, te in taken): add('office', a, b2, s['label'], s['ref']); stats['office_hit'] += 1; continue
            stats['office_miss'] += 1
    if not src: selfspan = None
    rec['spans'] = spans
    rec['selfspan'] = selfspan
    records[pid] = rec

# geonames gazetteer output
json.dump({'records': list(records.values()), 'gn': GN, 'idm': {k: v[0] for k, v in idm.items() if k.startswith(('TMP-', 'Q', 'AIND'))}},
          open('data.json', 'w', encoding='utf-8'), ensure_ascii=False)
print(len(records), dict(stats))
print('size', os.path.getsize('data.json'))
