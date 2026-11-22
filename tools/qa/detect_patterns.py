"""Find recurring error patterns in the converted records (TEI -> records_tei.json, dau.json).
usage: AIND_WORK=<work dir> python3 tools/qa/detect_patterns.py <out_dir>
Writes one TSV per pattern (id, detail, text excerpt) and summary.tsv. No AI is used."""
import os, sys, re, json, csv, collections

W = os.environ.get('AIND_WORK', '.')
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
R = json.load(open(os.path.join(W, 'records_tei.json')))
E = {e['k']: e for e in json.load(open(os.path.join(W, 'dau.json')))}
IDM = json.load(open(os.path.join(W, 'idm.json')))
OFFS = json.load(open(os.path.join(W, 'offices.json')))
HITS = collections.defaultdict(list)
TAG = re.compile(r'^@')


def plain(k):
    return ' '.join(w for w in E.get(k, {}).get('t', '').split(' ') if not TAG.match(w))


def norm(s):
    s = re.sub('[أإآ]', 'ا', s or '').replace('ى', 'ي').replace('ة', 'ه')
    return re.sub('[ً-ْ]', '', s)


def nisba_stated(q, nt):
    # stated without the bare place name:
    #  'القاهري المولد والدار' / 'المكي الأصل'  (the nisba states birth, residence or origin)
    #  'المكي ... مات بها'                      (pronoun back to the nisba's place)
    #  'بمعلاتها'                               (the place name with a suffix)
    base = q.replace('ال', '', 1)
    stem = base[:-1] if base.endswith('ه') else base
    if len(stem) >= 3 and re.search(stem + '(?:ت|ه)(?:ها|ه)', nt): return True
    for nis in {stem + 'ي', base + 'ي'}:
        if re.search(nis + r' (?:\S+ )?(?:ال)?(?:مولد|دار|منشا|اصل|مسكن|وفاه)', nt): return True
        if re.search(nis + r'(?: |$)', nt) and re.search(r'(?:^| )(?:و|ف|ثم )?(?:مات|توفي|دفن|ولد|نشا|قطن|سكن|استوطن|اقام)\S* (?:\S+ )?(?:بها|فيها)', nt): return True
    return False


def en(x):
    return ' | '.join(d.get('text', '') for k in ('descs', 'notes') for d in x.get(k) or [] if d.get('text'))


def ids(lst):
    return [(p.get('ref') or '').lstrip('#') for p in lst or []]


AUTH_OK = set(IDM)
for f in ('docs/authority/wd_entities.tsv', 'docs/authority/gn_entities.tsv'):
    p = os.path.join(os.environ.get('AIND_REPO', '.'), f)
    if os.path.exists(p):
        for row in csv.DictReader(open(p), delimiter='\t'):
            if row.get('status') == 'ok':
                AUTH_OK.add(('wd:' + row['qid']) if 'qid' in row else ('gn:' + row['gnid']))
AUTH_OK |= set(E)

PLACE_EV = {'travel', 'visit', 'study', 'riḥla', 'hajj', 'umrah', 'jāwara', 'residence'}

for k, r in R.items():
    txt = plain(k); nt = norm(txt)
    evs = r.get('events') or []
    # P1: one journey split into several events: same type, same English text, one place each
    groups = collections.defaultdict(list)
    for i, ev in enumerate(evs):
        if ev.get('type') in PLACE_EV and len(ev.get('places') or []) == 1:
            groups[(ev.get('type'), en(ev))].append(i)
    for (t, s), ix in groups.items():
        if len(ix) > 1 and s:
            HITS['P1_split_journey'].append((k, f"{t} e{','.join(str(i+1) for i in ix)}: " + ' / '.join(ids(evs[i]['places'])[0] for i in ix), s[:120]))
    # P1b: "من X إلى Y" in the text while the record has no event holding both places
    for m in re.finditer(r'من (\S+(?: \S+)?) (?:إلى|الى) (\S+)', txt):
        if not any(len(ev.get('places') or []) > 1 for ev in evs) and any(ev.get('type') in PLACE_EV for ev in evs):
            HITS['P1b_from_to_in_text'].append((k, m.group(0), '')); break
    # P2: people named only in an English note of an event (no person on the event)
    for i, ev in enumerate(evs):
        s = en(ev)
        if not ev.get('names') and re.search(r'\b(company of|accompanied|together with|with (?:al-|Ibn|the [Ss]hay)|in the presence of)', s):
            HITS['P2_person_only_in_note'].append((k, f"e{i+1} {ev.get('type')}", s[:140]))
    # P3: residence / birth / death place that the text never states (place not in text, nisba only)
    for i, ev in enumerate(evs):
        if ev.get('type') == 'residence':
            for p in ev.get('places') or []:
                q = norm(p.get('text') or '')
                if q and re.search('[؀-ۿ]', q) and q.replace('ال', '') not in nt.replace('ال', '') and not nisba_stated(q, nt):
                    HITS['P3_place_not_in_text'].append((k, f"e{i+1} residence {p.get('ref','')} {p.get('text','')}", ''))
    for kind in ('birth', 'death'):
        for p in (r.get(kind) or {}).get('places') or []:
            q = norm(p.get('text') or '')
            if q and re.search('[؀-ۿ]', q) and q.replace('ال', '') not in nt.replace('ال', '') and not nisba_stated(q, nt):
                HITS['P3_place_not_in_text'].append((k, f"{kind} {p.get('ref','')} {p.get('text','')}", ''))
    # P4: office label and office ID disagree (the label shares no word stem with any known form of the ID)
    for i, st in enumerate(r.get('states') or []):
        ref = (st.get('ref') or '').lstrip('#')
        lab = next((d['text'] for d in st.get('labels') or [] if d.get('lang') == 'ar' and d.get('text')), '')
        if not ref or not lab or ref not in OFFS: continue
        forms = [OFFS[ref]['ar']] + OFFS[ref].get('f', [])
        stems = lambda s: {w.replace('ال', '')[:3] for w in norm(s).replace('|', ' ').split() if len(w) > 2}
        fs = set().union(*[stems(f) for f in forms])
        if not (stems(lab) & fs):
            HITS['P4_office_label_vs_id'].append((k, f"s{i+1} {ref} [{OFFS[ref]['ar']}]", lab))
    # P5: wd/gn IDs not in ID-Master nor in the checked authority ledger (possible "poison" IDs)
    def walk(x):
        if isinstance(x, dict):
            for kk, v in x.items():
                if kk in ('ref', 'active', 'passive', 'corresp') and isinstance(v, str):
                    for t in v.split():
                        t = t.lstrip('#')
                        if re.match(r'^(wd|gn):', t) and t not in AUTH_OK:
                            yield t
                else:
                    yield from walk(v)
        elif isinstance(x, list):
            for y in x: yield from walk(y)
    for t in sorted(set(walk(r))):
        HITS['P5_unverified_external_id'].append((k, t, ''))
    # P6: duplicate events (same type, same places, same date)
    seen = {}
    for i, ev in enumerate(evs):
        key = (ev.get('type'), ev.get('subtype'), tuple(sorted(ids(ev.get('places')))), ev.get('when_ah'), tuple(sorted(ids(ev.get('names')))))
        if key in seen and (key[2] or key[4]):
            HITS['P6_duplicate_event'].append((k, f"e{seen[key]+1}=e{i+1} {key[0]} {' '.join(key[2])}", en(ev)[:100]))
        seen.setdefault(key, i)
    # P7: events with no anchor at all: no place, person, org, work, date, and no Arabic wording
    for i, ev in enumerate(evs):
        if not any(ev.get(x) for x in ('places', 'names', 'orgs', 'bibls', 'when_ah', 'notBefore_ah', 'notAfter_ah')) \
           and not any(d.get('lang') == 'ar' for d in ev.get('descs') or []):
            HITS['P7_event_without_anchor'].append((k, f"e{i+1} {ev.get('type')}/{ev.get('subtype') or ''}", en(ev)[:120]))

DESC = {
    'P1_split_journey': '一つの移動が場所ごとに別の出来事に分かれている（同じ種類・同じ注記で場所が1つずつ）',
    'P1b_from_to_in_text': '本文に「من X إلى Y」があるのに、出発地と到着地を一つに持つ出来事がない',
    'P2_person_only_in_note': '出来事の関係者が英語の注記にしか書かれていない（人物の参照なし）',
    'P3_place_not_in_text': '居住地・生地・没地が本文に書かれていない（ニスバなどからの推定の可能性）',
    'P4_office_label_vs_id': '官職の語句とIDが食い違う（語句がIDの名前・既知の書き方と語幹を共有しない）',
    'P5_unverified_external_id': 'ID-Master にも照合済み台帳にもない wd/gn 番号（毒IDの疑い）',
    'P6_duplicate_event': '同じ出来事が重複している（種類・場所・年・人物が同じ）',
    'P7_event_without_anchor': '場所・人物・年・アラビア語の文言のどれも持たない出来事（英語の要約だけ）',
}
with open(os.path.join(OUT, 'summary.tsv'), 'w') as f:
    f.write('pattern\tdescription\thits\trecords\n')
    for p in DESC:
        h = HITS.get(p, [])
        f.write(f"{p}\t{DESC[p]}\t{len(h)}\t{len({x[0] for x in h})}\n")
        with open(os.path.join(OUT, p + '.tsv'), 'w') as g:
            g.write('id\tdetail\tnote\n')
            for x in h: g.write('\t'.join(s.replace('\t', ' ').replace('\n', ' ') for s in x) + '\n')
        print(f"{p:28s} {len(h):6d} hits {len({x[0] for x in h}):5d} records")
