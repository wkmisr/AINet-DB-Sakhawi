"""Candidate targets for cross-reference headings ($$$): parse the pointer, search the numbered headings."""
import re, json, csv, collections, sys, unicodedata
CORPUS = sys.argv[2] if len(sys.argv) > 2 else '0__DawForAIND_renumbered_B54_split20260905.txt'
L = open(CORPUS, encoding='utf-8').read().split('\n')
DIA = re.compile('[ً-ْٰـ]')
def N(s):
    s = DIA.sub('', unicodedata.normalize('NFKC', s))
    for a, b in (('أ','ا'),('إ','ا'),('آ','ا'),('ٱ','ا'),('ى','ي'),('ة','ه'),('ؤ','ء'),('ئ','ء')): s = s.replace(a, b)
    s = re.sub(r'[★±،,:؛\.\(\)\[\]]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()
H = []          # every heading: (idx, line, id or None, marks, text(heading + continuation))
for i, l in enumerate(L):
    if not l.startswith('###$'): continue
    m = re.match(r'###\$(?:(AIND-D\d+[a-z]?) \| )?(\d+)\$# (\$+) (.*)', l)
    if not m: continue
    cont = []; j = i + 1
    while j < len(L) and L[j].strip() and not L[j].startswith('###'): cont.append(L[j].strip()); j += 1
    H.append({'k': len(H), 'line': i + 1, 'id': m.group(1), 'uid': m.group(2), 'marks': m.group(3),
              'text': (m.group(4) + ' ' + ' '.join(cont)).strip()})
for h in H:
    t = re.sub(r'^\d+\s+', '', h['text'])                # drop the edition's entry number
    h['n'] = N(t); h['words'] = h['n'].split()
STOP = set(N('بن ابن ابي ابو بنت ابنه في من هو هي ثم الاصل نزيل يعرف ويعرف مضى ياتي ياتي الاتي الماضي قريبا فيمن جده ابوه اسم لم يسم اثنان جماعه وابن احدهما').split())
BIO = [h for h in H if h['id'] and h['marks'] in ('$', '$$')]

FIVE = {'ابي': 'ابو', 'ابا': 'ابو', 'اخي': 'اخو', 'ذي': 'ذو'}
def toks(x): return [FIVE.get(w, w) for w in x.split()]
STOPV = r'(?:ياتي|مضي|مضى|الاتي|الماضي|قريبا|ان شاء الله|وسياتي|وقد|ويقال)'
for h in H: h['words'] = toks(h['n'])

def parse(h):
    t = ' '.join(h['words'])
    w = h['words']; ism = w[0] if w else ''
    father = w[2] if len(w) > 2 and w[1] == 'بن' else None
    if father == 'عبد' and len(w) > 3: father = 'عبد ' + w[3]
    exp = re.findall(r'AIND-D\d+[a-z]?', h['text'])                      # an explicit [= AIND-D…]
    prefix = None
    m = re.search(r'فيمن جده ((?:\S+ ?)+?)(?= ' + STOPV + r'| لا |$)', t)
    if m and father: prefix = [ism, 'بن'] + father.split() + ['بن'] + m.group(1).split()
    m = m or None
    if not prefix:
        m = re.search(r'فيمن اسم ابيه (\S+(?: \S+)?)', t)
        if m: prefix = [ism, 'بن'] + m.group(1).split()
    if not prefix:
        m = re.search(r'(?:في|هو|وهو) ابن ((?:\S+ ?)+?)(?= ' + STOPV + r'|$)', t)
        if m: prefix = [ism, 'بن'] + m.group(1).split()
    if not prefix:
        m = re.search(r'(?:في|هو|صوابه) (' + re.escape(ism) + r' بن (?:\S+ ?)+?)(?= ' + STOPV + r'| بدون|$)', t)
        if m: prefix = m.group(1).split()
    if prefix: prefix = [x for x in prefix if x not in ('ايضا',)]
    cut = re.search(r'\b(في|فيمن|هو|وهو|صوابه|مضي|مضى|ياتي|الاتي|الماضي|يذكر|ذكر|اشير)\b', t)
    desc = (t[:cut.start()] if cut else t).split()
    keys = [x for x in desc[1:] if x not in STOP and len(x) > 2]
    near = 'قريبا' in t
    dirn = -1 if re.search(r'مضي|مضى|الماضي|تقدم', t) else 1 if re.search(r'ياتي|الاتي|وسياتي', t) else 0
    return {'ism': ism, 'prefix': prefix, 'keys': keys, 'near': near, 'dir': dirn, 'exp': exp}

def score(h, c, p):
    w = c['words']
    if not w or w[0] != p['ism']: return None
    s, why = 0, []
    if p['prefix']:
        pre = p['prefix']
        if w[:len(pre)] == pre: s += 4; why.append('prefix')
        elif len(pre) > 3 and w[:len(pre) - 1] == pre[:-1]: s += 2; why.append('prefix-1')
        else: return None
    ws = set(w[:40]) | {re.sub(r'^(?:و|ب|وب|ف|ل)', '', x) for x in w[:40]} | {re.sub(r'^(?:و|ب|وب|ف|ل)?ال', '', x) for x in w[:40]}
    hit = [k for k in p['keys'] if k in ws or re.sub(r'^ال', '', k) in ws]
    s += len(hit); why += hit
    d = c['k'] - h['k']
    if p['near']:
        if abs(d) > 80: return None
        s += 1; why.append('near')
    if p['dir'] and d * p['dir'] < 0: s -= 1; why.append('wrong_direction')
    return s, why

POS = {}
def candidates(h):
    p = parse(h)
    if p['exp']: return p, [(99, x, ['explicit']) for x in p['exp']]
    out = []
    for c in BIO:
        if c['id'] == h['id']: continue
        r = score(h, c, p)
        if r and (r[0] >= 2 or p['prefix']): out.append((r[0], c['id'], r[1], abs(c['k'] - h['k'])))
    out.sort(key=lambda x: (-x[0], x[3]))
    return p, [x[:3] for x in out[:5]]

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'eval':          # REF records with a known target (note target)
        R = json.load(open('/home/claude/work118/records_tei.json'))
        gold = {}
        for k, r in R.items():
            if r.get('type') == 'reference':
                t = next((n.get('target') for n in r.get('notes', []) if n.get('target')), None)
                if t: gold[k] = t.lstrip('#')
        byid = {h['id']: h for h in H if h['id']}
        C = collections.Counter(); bad = []
        for k, t in gold.items():
            h = byid.get(k)
            if not h: C['not_in_corpus'] += 1; continue
            p, out = candidates(h)
            top = [x for x in out if x[0] == out[0][0]] if out else []
            if not out: C['none'] += 1; bad.append((k, t, 'none', h['text'][:90]))
            elif len(top) == 1 and top[0][1] == t: C['unique_right'] += 1
            elif len(top) == 1: C['unique_wrong'] += 1; bad.append((k, t, top[0][1], h['text'][:90]))
            elif any(x[1] == t for x in top): C['tied_incl_right'] += 1
            elif any(x[1] == t for x in out): C['right_in_top5'] += 1
            else: C['wrong'] += 1; bad.append((k, t, [x[1] for x in out], h['text'][:90]))
        print(len(gold), dict(C))
        for b in bad[:25]: print(b)

def run_worklist(src, dst):
    byid = {h['id']: h for h in H if h['id']}; byline = {h['line']: h for h in H}
    rows = list(csv.DictReader(open(src), delimiter='\t'))
    C = collections.Counter()
    for r in rows:
        h = byid.get(r['id']) if r['group'].startswith('A') else byline.get(int(r['corpus_line'])) if r['corpus_line'] else None
        if not h: r['tier'] = ''; r['candidates'] = ''; continue
        p, out = candidates(h)
        top = [x for x in out if out and x[0] == out[0][0]]
        tier = ('explicit' if out and out[0][2] == ['explicit'] else 'none' if not out else 'unique' if len(top) == 1 else 'tied')
        r['tier'] = tier; C[r['group'][0] + ':' + tier] += 1
        r['candidates'] = ' ; '.join(f"{x[1]} ({x[0]}: {','.join(x[2])})" for x in out)
    F = list(rows[0].keys())
    with open(dst, 'w', newline='') as f:
        w = csv.DictWriter(f, F, delimiter='\t'); w.writeheader(); w.writerows(rows)
    print(dict(sorted(C.items())))
