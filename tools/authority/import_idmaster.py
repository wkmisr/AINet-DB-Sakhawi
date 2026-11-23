#!/usr/bin/env python3
"""One-off import of the ID-Master sheet (CSV export) into the authority registries.

  import_idmaster.py <idmaster.csv>

- Person rows with an AIND ID   -> aliases / notes on that person in persons_registry.tsv;
                                   a former TMP-P number named in the note becomes a `merged` row
- Person rows with TMP-P / Wikidata IDs -> new rows in persons_registry.tsv
- every other category          -> entities_registry.tsv
- rows that cannot be imported as they stand -> import_idmaster_rulings.tsv (for a human decision)
"""
import csv, io, os, re, sys, collections
csv.field_size_limit(10**9)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A = os.path.join(ROOT, 'authority')
P_COLS = ['id', 'status', 'target', 'name_ar', 'name_latn', 'aliases', 'same_as', 'note', 'history', 'added_by']
E_COLS = ['id', 'category', 'status', 'target', 'label_ar', 'label_latn', 'variants', 'same_as', 'class', 'note', 'history', 'added_by']
PREFIX = {'TMP-N': 'Nisbah', 'TMP-L': 'Location', 'TMP-I': 'Institution', 'TMP-O': 'Office', 'TMP-T': 'Text', 'TMP-S': 'Subject', 'TMP-P': 'Person'}
FORMER = re.compile(r'(?:旧\s*|Formerly\s+)(TMP-P-\d{6})|(TMP-P-\d{6})\s*(?:から|を)?\s*(?:統合|merged)')

def write(path, rows, cols):
    b = io.StringIO()
    w = csv.DictWriter(b, cols, delimiter='\t', lineterminator='\n', extrasaction='ignore')
    w.writeheader(); w.writerows(rows)
    open(path, 'w', encoding='utf-8', newline='').write(b.getvalue())

def norm_id(raw, cat):
    s = raw.strip()
    if re.fullmatch(r'wd:Q\d+', s): return s
    if re.fullmatch(r'Q\d+', s): return 'wd:' + s
    if re.fullmatch(r'\d{3,9}', s): return 'gn:' + s
    return s

def split(s):
    return [x.strip() for x in s.split('|') if x.strip()]

def join(*xs):
    out = []
    for x in xs:
        for y in (x if isinstance(x, list) else split(x)):
            if y and y not in out: out.append(y)
    return ' | '.join(out)

def main(src):
    persons = list(csv.DictReader(open(os.path.join(A, 'persons_registry.tsv'), encoding='utf-8', newline=''), delimiter='\t'))
    for p in persons:
        p.setdefault('name_ar', ''); p.setdefault('name_latn', ''); p.setdefault('history', ''); p.setdefault('added_by', '')
        p['same_as'] = p.pop('wikidata', '') if 'wikidata' in p else p.get('same_as', '')
    P = {p['id']: p for p in persons}
    E = {}
    rulings = []
    for i, r in enumerate(list(csv.reader(open(src, encoding='utf-8')))[1:], 2):
        who, cat, ar, la, raw, note, hist, cls, st = [(c or '').strip() for c in (r + [''] * 9)[:9]]
        if not (cat or ar or raw): continue
        if not raw:
            rulings.append((i, cat, ar, raw, 'IDが空')); continue
        rid = norm_id(raw, cat)
        kind = next((v for k, v in PREFIX.items() if rid.startswith(k)), 'Person' if rid.startswith('AIND-D') else None)
        if not cat:
            cat = kind or ''
            if not cat: rulings.append((i, cat, ar, raw, 'Categoryが空で、IDからも決まらない')); continue
        if kind and kind != cat:
            rulings.append((i, cat, ar, raw, f'CategoryとIDの種類が合わない（IDは{kind}）。Categoryのとおりに取り込んだ'))
        names = split(ar); latn = la
        if cat == 'Person':
            if rid.startswith('AIND-D'):
                p = P.get(rid)
                if not p:
                    rulings.append((i, cat, ar, raw, 'AIND番号が人物の典拠表にない')); continue
                p['aliases'] = join(p['aliases'], names)
                if note: p['note'] = (p['note'] + ' ' if p['note'] else '') + '[ID-Master] ' + note
                if hist: p['history'] = (p['history'] + ' ' if p['history'] else '') + hist
                for m in FORMER.finditer(note + ' ' + hist):
                    old = m[1] or m[2]
                    if old not in P:
                        P[old] = dict.fromkeys(P_COLS, ''); P[old].update(id=old, status='merged', target=rid, name_ar=names[0] if names else '',
                                                                          note=f'ID-Master 行{i} の注記から復元')
                    elif P[old]['status'] != 'merged':
                        rulings.append((i, cat, ar, raw, f'注記は {old} を統合済みとするが、{old} の行が別に残っている'))
                continue
            if rid in P:
                q = P[rid]
                if q['status'] == 'merged':
                    rulings.append((i, cat, ar, raw, f'{rid} は {q["target"]} に統合済みと別の行の注記にあるが、この行が残っている')); continue
                rulings.append((i, cat, ar, raw, 'IDが重複。別名と注記を一つの行にまとめた'))
                q['aliases'] = join(q['aliases'], names); q['note'] = (q['note'] + ' / ' + note).strip(' /')
                continue
            P[rid] = dict(id=rid, status='retired' if st == 'retired' else 'active', target='', name_ar=names[0] if names else '',
                          name_latn=latn, aliases=join(names[1:]), same_as='', note=note, history=hist, added_by=who)
            continue
        if rid.startswith('AIND-D'):
            rulings.append((i, cat, ar, raw, 'Person以外のCategoryにAIND番号')); continue
        if rid in E:
            rulings.append((i, cat, ar, raw, 'IDが重複。表記と注記を一つの行にまとめた'))
            e = E[rid]; e['variants'] = join(e['variants'], [n for n in names if n != e['label_ar']]); e['note'] = (e['note'] + ' / ' + note).strip(' /')
            continue
        E[rid] = dict(id=rid, category=cat, status='retired' if st == 'retired' else 'active', target='',
                      label_ar=names[0] if names else '', label_latn=latn, variants=join(names[1:]), same_as='',
                      **{'class': cls}, note=note, history=hist, added_by=who)
    def key(x):
        return (0, x) if x.startswith('AIND') else (1, x)
    write(os.path.join(A, 'persons_registry.tsv'), [P[k] for k in sorted(P, key=key)], P_COLS)
    write(os.path.join(A, 'entities_registry.tsv'), [E[k] for k in sorted(E, key=lambda k: (E[k]['category'], k))], E_COLS)
    with open(os.path.join(A, 'import_idmaster_rulings.tsv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n'); w.writerow(['idmaster_row', 'category', 'arabic', 'id', 'problem']); w.writerows(rulings)
    print('persons', len(P), collections.Counter(p['status'] for p in P.values()))
    print('entities', len(E), collections.Counter(e['category'] for e in E.values()))
    print('rulings', len(rulings), collections.Counter(re.sub(r'（.*|TMP\S+|AIND\S+|\{.*', '', x[4])[:22] for x in rulings))

if __name__ == '__main__':
    main(sys.argv[1])
