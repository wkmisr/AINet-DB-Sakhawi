"""Corpus parsing and Arabic name features for the identification tools (design v5, sec. 4.2).

Search-side only: nothing here is written back to records. Normalization follows OpenITI
normalize_ara_light (as in tools/viewer/to_v01.py on trial/yaml-markdown) plus a few
search-only folds (ta marbuta, diacritics, tatweel, the five nouns).
"""
import re, unicodedata, math, collections, os

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CORPUS = os.path.join(REPO, '0__DawForAIND_renumbered_B54_split20260905.txt')

_LIGHT = [("أ", "ا"), ("ٱ", "ا"), ("آ", "ا"), ("إ", "ا"), ("ى", "ي"),
          ("يء", "ء"), ("ىء", "ء"), ("ؤ", "ء"), ("ئ", "ء"), ("ک", "ك"), ("ی", "ي"), ("ۀ", "ه")]
_DIAC = re.compile(r'[ً-ْٰـ]')


def norm(t):
    t = unicodedata.normalize('NFKC', t)
    t = _DIAC.sub('', t)
    for a, b in _LIGHT:
        t = t.replace(a, b)
    t = t.replace('ة', 'ه')
    t = re.sub(r'[^ء-ي0-9 ]+', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()


FIVE = {'ابي': 'ابو', 'ابا': 'ابو', 'اخي': 'اخو', 'اخا': 'اخو', 'ذي': 'ذو', 'ذا': 'ذو'}

# laqab stems: short form "al-X" (or "al-Xi") <-> "X al-din". Search-only list; extend as needed.
LAQAB = ['شمس', 'بدر', 'جلال', 'تقي', 'محب', 'زين', 'ولي', 'سراج', 'علاء', 'نور', 'شهاب', 'كمال', 'عز',
         'محيي', 'فخر', 'صلاح', 'برهان', 'ناصر', 'امين', 'جمال', 'شرف', 'قطب', 'ركن', 'عماد', 'نجم', 'صدر',
         'تاج', 'رضي', 'سيف', 'حسام', 'غرس', 'فتح', 'وجيه', 'اوحد', 'مجد', 'ضياء', 'زكي', 'بهاء', 'موفق',
         'صفي', 'عفيف', 'كريم', 'شجاع', 'سعد', 'عضد', 'بها', 'قوام', 'نظام', 'عماد', 'حميد', 'رشيد',
         'نفيس', 'مظفر', 'ظهير', 'اصيل', 'علم']
LAQAB_SET = set(LAQAB)
# short forms that differ from the stem
SHORT = {'المحيوي': 'محيي', 'المحيي': 'محيي', 'الناصري': 'ناصر', 'الزيني': 'زين', 'الشمسي': 'شمس',
         'البدري': 'بدر', 'الشهابي': 'شهاب', 'التقوي': 'تقي', 'الجمالي': 'جمال', 'العلائي': 'علاء',
         'الشرفي': 'شرف', 'الكمالي': 'كمال', 'السيفي': 'سيف', 'العزي': 'عز', 'الصلاحي': 'صلاح',
         'البرهاني': 'برهان', 'الفخري': 'فخر', 'النوري': 'نور', 'الولوي': 'ولي', 'الجلالي': 'جلال',
         'السراجي': 'سراج', 'النجمي': 'نجم', 'المجدي': 'مجد', 'الزكوي': 'زكي', 'الرضوي': 'رضي',
         'العمادي': 'عماد', 'القطبي': 'قطب', 'الصدري': 'صدر', 'التاجي': 'تاج', 'الامين': 'امين'}

STOP = {'بن', 'ابن', 'ابنه', 'بنت', 'و', 'ثم', 'في', 'عن', 'على', 'من', 'الى', 'عند', 'هو', 'هي', 'الذي',
        'التي', 'قبله', 'بعده', 'الاتي', 'الماضي', 'الاتيه', 'الماضيه', 'الاتيين', 'الماضيين', 'ويعرف',
        'يعرف', 'المعروف', 'المعروفه', 'وتعرف', 'تعرف', 'كسلفه', 'كابيه', 'ابيه', 'ابوه', 'الدين', 'سنه',
        'شيخنا', 'والده', 'والدته', 'اخوه', 'اخيه', 'ابنه', 'جده', 'عمه', 'خاله', 'زوجه', 'زوج', 'صاحبنا',
        'الشيخ', 'القاضي', 'الامير', 'السيد', 'الحافظ', 'الامام', 'العلامه', 'سبط', 'حفيد', 'ولد', 'والد',
        'شقيق', 'اخو', 'اخت', 'ام', 'بنو', 'اولاد', 'اخوته', 'جماعه', 'وغيره', 'وغيرهما', 'وغيرهم', 'ونحوه'}

COMPOUND_HEAD = {'عبد', 'ابو', 'ابي', 'ابا', 'ذو', 'ام', 'سبط'}


def tokens(t):
    w = norm(t).split()
    out = []
    for x in w:
        if x in FIVE:
            x = FIVE[x]
        # proclitics on a definite or known word (wa-, bi-, li-, ka-)
        if len(x) > 3 and x[0] in 'وبلكف' and x[1:3] == 'ال':
            x = x[1:]
        elif x.startswith('لل') and len(x) > 4:
            x = 'ال' + x[2:]
        elif x.startswith('وابن') or x.startswith('وابو') or x.startswith('وعبد'):
            x = x[1:]
        elif x.startswith('بابن'):
            x = x[1:]
        out.append(x)
    return out


def join_compounds(w):
    """'عبد الله' -> 'عبد_الله', 'ابو بكر' -> 'ابو_بكر'."""
    out, i = [], 0
    while i < len(w):
        if w[i] in COMPOUND_HEAD and i + 1 < len(w) and w[i + 1] not in ('بن', 'ابن'):
            out.append(w[i] + '_' + w[i + 1]); i += 2
        else:
            out.append(w[i]); i += 1
    return out


def laqab_of(x, nxt=None):
    """Return the laqab stem if token x (with the next token) is a laqab, else None."""
    if nxt == 'الدين' and x in LAQAB_SET:
        return x
    if x in SHORT:
        return SHORT[x]
    if x.startswith('ال') and x[2:] in LAQAB_SET:
        return x[2:]
    return None


def nisba_of(x):
    if x.startswith('ال') and len(x) > 4 and x.endswith('ي'):
        return x[2:]
    return None


def heading_features(name):
    """Typed features of a heading's name segment.
    I ism, F father, G grandfather, P further ancestors (set), L laqab, K kunya, N nisba, A known-as."""
    w = join_compounds(tokens(name))
    f = collections.defaultdict(set)
    if not w:
        return f
    f['I'].add(w[0])
    i, depth = 1, 0
    while i + 1 < len(w) and w[i] in ('بن', 'ابن', 'ابنه', 'بنت'):
        depth += 1
        f['F' if depth == 1 else 'G' if depth == 2 else 'P'].add(w[i + 1])
        i += 2
    rest = w[i:]
    known = False
    kin_next = False   # token after "bn"/"akhu"/"sibt": belongs to someone else
    for j, x in enumerate(rest):
        nxt = rest[j + 1] if j + 1 < len(rest) else None
        if x in ('بن', 'ابنه', 'بنت') and nxt:
            kin_next = 'FL'; continue
        if x in ('اخو', 'سبط', 'حفيد', 'شقيق', 'والد', 'ابن') and nxt and not known and x != 'ابن':
            kin_next = 'XL'; continue
        if kin_next:
            L = laqab_of(x, nxt)
            if L:
                f[kin_next].add(L)
            if kin_next == 'FL' and not L:
                f['P'].add(x)
            if x.startswith('ابو_') and kin_next == 'FL':
                f['FK'].add(x)
            kin_next = False
            continue
        if x in ('يعرف', 'ويعرف', 'المعروف', 'وتعرف', 'تعرف'):
            known = 1; continue
        if known:
            if x in ('ب', 'كسلفه', 'كابيه', 'ايضا'):
                continue
            y = x[1:] if x.startswith('ب') and len(x) > 3 else x
            known = known + 1 if known < 3 else False   # the "known as" form: at most three words
            if y in ('ابن', 'بابن') and nxt:
                f['A'].add('ابن ' + nxt); continue
            f['A'].add(y)
        L = laqab_of(x, nxt)
        if L:
            f['L'].add(L); continue
        if x.startswith('ابو_'):
            f['K'].add(x); continue
        if x in ('ابن',) and nxt and not known:
            f['A'].add('ابن ' + nxt); continue
        N = nisba_of(x)
        if N:
            f['N'].add(N)
    # laqab stated as part of the nasab ("bn al-Shams") is the father's, not ours: leave it
    return f


def mention_features(phrase):
    """Untyped-ish features of a mention phrase (desc / quote).
    Returns dict of typed guesses plus 'T' (all content tokens)."""
    w = join_compounds(tokens(phrase))
    f = collections.defaultdict(set)
    first_name_seen = False
    i = 0
    while i < len(w):
        x = w[i]; nxt = w[i + 1] if i + 1 < len(w) else None
        if x in ('بن', 'بنت', 'ابنه') and nxt:
            f['F' if 'F' not in f else 'G'].add(nxt); i += 2; continue
        if x == 'ابن' and nxt:
            f['A'].add('ابن ' + nxt)
            if first_name_seen:
                f['F' if 'F' not in f else 'G'].add(nxt)
            f['T'].add(nxt); i += 2; continue
        L = laqab_of(x, nxt)
        if L:
            f['L'].add(L)
            if nxt == 'الدين':
                i += 2; continue
            i += 1; continue
        if x.startswith('ابو_'):
            f['K'].add(x); f['T'].add(x); i += 1; continue
        N = nisba_of(x)
        if N:
            f['N'].add(N); f['T'].add(x); i += 1; continue
        if x not in STOP and not x.startswith('ال') and len(x) > 1:
            if not first_name_seen:
                f['I'].add(x); first_name_seen = True
            f['T'].add(x)
        elif x.startswith('ال') and x not in STOP and len(x) > 3:
            f['T'].add(x)
        i += 1
    return f


HEAD = re.compile(r'^###\$(AIND-D\d{5}[a-z]?) \| (\d+)\$# \$ ?(\d+)? ?(.*)$')
XREF = re.compile(r'^###\$(\d+)\$# \$\$\$ (.*)$')
ANYHEAD = re.compile(r'^###')


def parse_corpus(path=CORPUS):
    """Return list of entries in corpus order: dict(id, src, no, name, text)."""
    entries, cur = [], None
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            line = line.rstrip('\n')
            if ANYHEAD.match(line):
                m = HEAD.match(line)
                if m:
                    cur = {'id': m.group(1), 'src': m.group(2), 'no': m.group(3), 'lines': [m.group(4)]}
                    entries.append(cur)
                else:
                    m2 = XREF.match(line)
                    if m2:
                        cur = {'id': None, 'src': m2.group(1), 'no': None, 'xref': True, 'lines': [m2.group(2)]}
                        entries.append(cur)
                    else:
                        cur = None
                continue
            if cur is not None and not line.startswith('#META'):
                cur['lines'].append(line)
    for e in entries:
        e['text'] = re.sub(r'\s+', ' ', ' '.join(e.pop('lines'))).strip()
        # sub-entries and some headings carry "$ 492" before the name
        e['text'] = re.sub(r'^(?:\$+ ?)?(?:\d+ )?', '', e['text'])
        e['name'] = name_segment(e['text'])
    return entries


_END = re.compile(r' [،,\.] | ، |\. | (?:ولد|ولدت|مات|ماتت|نزيل|قدم|ممن|اشتغل|كان|سمع|حفظ|نشا|ذكره|اخذ)\b')


def name_segment(text):
    m = _END.search(text)
    seg = text[:m.start()] if m else text[:300]
    return seg[:400]


class Index:
    def __init__(self, entries=None):
        self.entries = entries if entries is not None else parse_corpus()
        self.persons = [e for e in self.entries if e['id']]
        self.pos = {e['id']: i for i, e in enumerate(self.persons)}
        self.feat = {}
        df = collections.Counter()
        for e in self.persons:
            f = heading_features(e['name'])
            self.feat[e['id']] = f
            for k, vs in f.items():
                for v in vs:
                    df[(k, v)] += 1
            for v in set(join_compounds(tokens(e['name']))):
                df[('T', v)] += 1
        self.df = df
        self.N = len(self.persons)
        self.inv = collections.defaultdict(set)
        for e in self.persons:
            for k, vs in self.feat[e['id']].items():
                for v in vs:
                    self.inv[(k, v)].add(e['id'])
            for v in set(join_compounds(tokens(e['name']))):
                self.inv[('T', v)].add(e['id'])
            for L in self.feat[e['id']].get('L', ()):
                self.inv[('T', 'L:' + L)].add(e['id'])

    def idf(self, key):
        return math.log((self.N + 1) / (self.df.get(key, 0) + 1)) + 0.5

    # mention type -> heading types it may match, with a weight
    COMPAT = {'I': [('I', 1.0), ('F', 0.25), ('A', 0.5)],
              'F': [('F', 1.0), ('G', 0.3), ('P', 0.4), ('A', 0.8)],
              'G': [('G', 1.0), ('P', 0.5)],
              'L': [('L', 1.0), ('FL', 0.15)],
              'K': [('K', 1.0)],
              'N': [('N', 1.0), ('A', 0.5)],
              'A': [('A', 1.0), ('F', 0.3)]}

    def search(self, phrase, k=20, exclude=None):
        mf = mention_features(phrase)
        scores = collections.defaultdict(float)
        why = collections.defaultdict(list)
        for mt, vals in mf.items():
            if mt == 'T':
                continue
            for v in vals:
                for ht, w in self.COMPAT.get(mt, []):
                    key = (ht, v)
                    if mt == 'A' and ht == 'A':
                        pass
                    for pid in self.inv.get(key, ()):
                        s = w * self.idf(key)
                        scores[pid] += s
                        why[pid].append(f'{mt}->{ht}:{v}')
        # bag-of-tokens fallback (small weight), catches mis-typed tokens
        for v in mf.get('T', ()):
            key = ('T', v)
            for pid in self.inv.get(key, ()):
                scores[pid] += 0.2 * self.idf(key)
        # a stated laqab / ism / kunya that conflicts with the heading's own costs something
        for mt in ('L', 'I', 'K'):
            vals = mf.get(mt)
            if not vals:
                continue
            for pid in list(scores):
                hv = self.feat[pid].get(mt)
                if hv and not (hv & vals):
                    scores[pid] -= 0.5 * max(self.idf((mt, v)) for v in vals)
        if exclude:
            for x in exclude:
                scores.pop(x, None)
        ranked = sorted(scores.items(), key=lambda kv: (-kv[1], self.pos[kv[0]]))
        return [(pid, round(s, 2), why[pid]) for pid, s in ranked[:k]], mf


# ---- genealogy shift (design v5, 4.2 no. 2) --------------------------------------------------

def nasab_list(name):
    """[ism, father, grandfather, ...] as written in the heading, compounds joined."""
    w = join_compounds(tokens(name))
    if not w:
        return []
    out, i = [w[0]], 1
    while i + 1 < len(w) and w[i] in ('بن', 'ابن', 'ابنه', 'بنت'):
        # "bn al-Kamal Abi l-Fadl Muhammad", "bn al-Shams Muhammad": skip laqab/kunya/title to the ism
        j, lq = i + 1, None
        while j < len(w):
            nx = w[j + 1] if j + 1 < len(w) else None
            L = laqab_of(w[j], nx)
            if L:
                lq = lq or L; j += 2 if nx == 'الدين' else 1; continue
            if w[j].startswith('ابو_') or w[j] in TITLES:
                j += 1; continue
            break
        if j < len(w) and w[j] not in ('بن', 'ابن', 'ابنه', 'بنت') and not w[j].startswith('ال'):
            out.append(w[j]); i = j + 1
        elif lq:
            out.append('L:' + lq); i = j       # only a laqab is given for this ancestor
        else:
            out.append(w[i + 1]); i += 2
    return out


TITLES = {'القاضي', 'العلامه', 'السيد', 'الامير', 'الشيخ', 'الحافظ', 'الامام', 'الخواجا', 'الخواجه', 'العلم', 'الشريف'}


KIN_PATTERNS = {
    # relation of the OTHER person to the record: how the other's nasab relates to the record's nasab r
    'father':      lambda o, r: len(r) > 1 and o[:1] == r[1:2] and _pref(o[1:], r[2:]),
    'mother':      lambda o, r: False,
    'grandfather': lambda o, r: len(r) > 2 and o[:1] == r[2:3] and _pref(o[1:], r[3:]),
    'son':         lambda o, r: len(o) > 1 and o[1:2] == r[:1] and _pref(o[2:], r[1:]),
    'daughter':    lambda o, r: len(o) > 1 and o[1:2] == r[:1] and _pref(o[2:], r[1:]),
    'grandson':    lambda o, r: len(o) > 2 and o[2:3] == r[:1] and _pref(o[3:], r[1:]),
    'brother':     lambda o, r: len(o) > 1 and len(r) > 1 and o[1:2] == r[1:2] and _pref(o[2:], r[2:]),
    'sister':      lambda o, r: len(o) > 1 and len(r) > 1 and o[1:2] == r[1:2] and _pref(o[2:], r[2:]),
    'paternal_uncle': lambda o, r: len(o) > 1 and len(r) > 2 and o[1:2] == r[2:3] and o[:1] != r[1:2] and _pref(o[2:], r[3:]),
    'cousin':      lambda o, r: len(o) > 2 and len(r) > 2 and o[2:3] == r[2:3] and o[1:2] != r[1:2] and _pref(o[3:], r[3:]),
    'siblings_child': lambda o, r: len(o) > 2 and len(r) > 1 and o[2:3] == r[1:2] and o[1:2] != r[:1] and _pref(o[3:], r[2:]),
}
KIN_PATTERNS['uncle'] = KIN_PATTERNS['paternal_uncle']
KIN_PATTERNS['ancestor'] = lambda o, r: any(o[:1] == r[k:k + 1] and _pref(o[1:], r[k + 1:]) for k in range(1, len(r)))
KIN_PATTERNS['descendant'] = lambda o, r: any(o[k:k + 1] == r[:1] and _pref(o[k + 1:], r[1:]) for k in range(1, len(o)))


def _pref(a, b):
    """The shorter nasab is consistent with the longer one (both as written)."""
    n = min(len(a), len(b))
    return a[:n] == b[:n]


def _gen_init(self):
    self.nasab = {e['id']: nasab_list(e['name']) for e in self.persons}
    self.by_first = collections.defaultdict(set)
    self.by_second = collections.defaultdict(set)
    self.by_third = collections.defaultdict(set)
    for pid, n in self.nasab.items():
        if n:
            self.by_first[n[0]].add(pid)
        if len(n) > 1:
            self.by_second[n[1]].add(pid)
        if len(n) > 2:
            self.by_third[n[2]].add(pid)


def genealogy(self, rid, kind):
    """Headings standing in relation `kind` (father, son, brother, ...) to record rid by nasab.
    Ranked by how much of the nasab agrees (longer agreement first)."""
    if not hasattr(self, 'nasab'):
        _gen_init(self)
    r = self.nasab.get(rid) or []
    test = KIN_PATTERNS.get(kind)
    if not test or not r:
        return []
    # narrow the pool cheaply
    if kind in ('father',):
        pool = self.by_first.get(r[1], set()) if len(r) > 1 else set()
    elif kind == 'grandfather':
        pool = self.by_first.get(r[2], set()) if len(r) > 2 else set()
    elif kind in ('son', 'daughter'):
        pool = self.by_second.get(r[0], set())
    elif kind in ('brother', 'sister'):
        pool = self.by_second.get(r[1], set()) if len(r) > 1 else set()
    elif kind in ('paternal_uncle', 'uncle'):
        pool = self.by_second.get(r[2], set()) if len(r) > 2 else set()
    elif kind == 'cousin':
        pool = self.by_third.get(r[2], set()) if len(r) > 2 else set()
    elif kind == 'siblings_child':
        pool = self.by_third.get(r[1], set()) if len(r) > 1 else set()
    elif kind == 'grandson':
        pool = self.by_third.get(r[0], set())
    else:
        pool = set(self.nasab)
    out = []
    for pid in pool:
        if pid == rid:
            continue
        o = self.nasab[pid]
        if test(o, r):
            agree = sum(1 for x, y in zip(o, r) if x == y)
            nis = len(self.feat[pid].get('N', set()) & self.feat[rid].get('N', set()))
            out.append((pid, len(o) + agree + 2 * nis))
    out.sort(key=lambda kv: (-kv[1], abs(self.pos[kv[0]] - self.pos[rid])))
    return [pid for pid, _ in out]


Index.genealogy = genealogy


# ---- neighbours and reading (4.2 nos. 4, 5) --------------------------------------------------

def neighbours(self, rid, n=1):
    i = self.pos[rid]
    return [self.persons[j]['id'] for j in range(max(0, i - n), min(len(self.persons), i + n + 1)) if j != i]


def read(self, rid):
    return self.persons[self.pos[rid]]['text']


Index.neighbours = neighbours
Index.read = read


# ---- combined pre-search for one mention (what the script hands to the model) ---------------

KIN_WORDS = {'father': ['والده', 'ابوه', 'ابيه', 'لابيه'], 'son': ['ابنه', 'ولده', 'لولده'],
             'brother': ['اخوه', 'اخيه', 'شقيقه', 'اخو'], 'grandfather': ['جده', 'لجده'],
             'paternal_uncle': ['عمه'], 'sister': ['اخته', 'شقيقته'], 'daughter': ['ابنته', 'بنته']}


def presearch(self, rid, phrase, kind=None, k=20):
    """Name search + genealogy shift (+ neighbour for 'الذي قبله/بعده'), merged.
    kind: relation subtype if known from extraction (father, son, brother ...), else guessed from the phrase."""
    res, mf = self.search(phrase, k=200, exclude={rid})
    score = {p: s for p, s, w in res}
    why = {p: list(w) for p, s, w in res}
    toks = set(tokens(phrase))
    if kind is None:
        for kk, ws in KIN_WORDS.items():
            if toks & set(ws):
                kind = kk; break
    if kind:
        gen = self.genealogy(rid, kind)
        for i, p in enumerate(gen[:50]):
            score[p] = score.get(p, 0) + 12 - min(i, 10) * 0.3
            why.setdefault(p, []).append(f'genealogy:{kind}')
    nt = norm(phrase)
    if 'الذي قبله' in nt or 'التي قبلها' in nt or 'قبله' in toks:
        i = self.pos[rid]
        if i > 0:
            p = self.persons[i - 1]['id']; score[p] = score.get(p, 0) + 15; why.setdefault(p, []).append('neighbour:before')
    if 'الذي بعده' in nt or 'التي بعدها' in nt:
        i = self.pos[rid]
        if i + 1 < len(self.persons):
            p = self.persons[i + 1]['id']; score[p] = score.get(p, 0) + 15; why.setdefault(p, []).append('neighbour:after')
    ranked = sorted(score.items(), key=lambda kv: (-kv[1], self.pos[kv[0]]))[:k]
    return [(p, round(s, 2), why.get(p, [])) for p, s in ranked], kind


Index.presearch = presearch


# ---- reverse lookup (4.2 no. 3) ---------------------------------------------------------------

_REF = re.compile(r'(?:ref|active|passive|corresp|mutual)="([^"]*)"')


def build_refs(repo=REPO):
    """{person id: set of record ids whose XML points to it} from Individuals/ (any ref-like attribute)."""
    import glob
    refs = collections.defaultdict(set)
    for f in glob.glob(os.path.join(repo, 'Individuals', '*', '*.xml')):
        rid = os.path.basename(f).split('_')[0]
        with open(f, encoding='utf-8') as fh:
            for m in _REF.finditer(fh.read()):
                for x in m.group(1).split():
                    x = x.lstrip('#')
                    if x.startswith(('AIND-D', 'TMP-P')) and x != rid:
                        refs[x].add(rid)
    return refs


def reverse(self, pid):
    """Records that refer to pid in their XML, plus entries whose text names pid by its
    'known as' form or by laqab + ism (text hits are suggestions, not identifications)."""
    if not hasattr(self, 'refs'):
        self.refs = build_refs()
    out = {'xml': sorted(self.refs.get(pid, ()))}
    f = self.feat.get(pid, {})
    pats = [a for a in f.get('A', ()) if a.startswith('ابن ') and self.df.get(('A', a), 99) <= 5]
    if not hasattr(self, 'ntext'):
        self.ntext = {e['id']: ' ' + ' '.join(tokens(e['text'])) + ' ' for e in self.persons}
    hits = []
    if pats:
        for e in self.persons:
            if e['id'] != pid and any(' ' + p + ' ' in self.ntext[e['id']] for p in pats):
                hits.append(e['id'])
    out['text'] = hits[:200]
    out['text_patterns'] = pats
    return out


Index.reverse = reverse


# ---- authority search (4.2 no. 6) -------------------------------------------------------------

def load_registry(path=None):
    """persons_registry.tsv (authority/ on the authority-registry branch, PR #120, not yet on main).
    Falls back to `git show` of that branch."""
    import subprocess, csv, io
    path = path or os.path.join(REPO, 'authority', 'persons_registry.tsv')
    if os.path.exists(path):
        txt = open(path, encoding='utf-8').read()
    else:
        txt = subprocess.run(['git', '-C', REPO, 'show', 'origin/authority-registry-20261123:authority/persons_registry.tsv'],
                             capture_output=True, text=True).stdout
    return list(csv.DictReader(io.StringIO(txt), delimiter='\t'))


def authority_search(self, phrase, k=20, include_aind=False):
    """Token search over registry names and aliases (TMP-P and Wikidata persons by default)."""
    if not hasattr(self, 'reg'):
        self.reg = [r for r in load_registry() if r.get('status') in ('active', '')]
        self.reg_tok = []
        dfc = collections.Counter()
        for r in self.reg:
            t = set(tokens(r.get('name_ar', '') + ' ' + (r.get('aliases') or '').replace('|', ' ')))
            self.reg_tok.append(t); dfc.update(t)
        self.reg_df = dfc
    q = set(tokens(phrase)) - STOP
    n = len(self.reg) + 1
    scored = []
    for r, t in zip(self.reg, self.reg_tok):
        if not include_aind and r['id'].startswith('AIND-D'):
            continue
        common = q & t
        if common:
            scored.append((sum(math.log(n / (self.reg_df[x] + 1)) for x in common), r))
    scored.sort(key=lambda kv: -kv[0])
    return [(r['id'], round(s, 2), r.get('name_ar', ''), r.get('aliases', '')) for s, r in scored[:k]]


Index.authority_search = authority_search
