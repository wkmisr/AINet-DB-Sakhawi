#!/usr/bin/env python3
"""Rebuild name_ar in authority/persons_registry.tsv where the value inherited from the PersonList is unusable.

The PersonList (frozen 2026-11-23) carried, for 1,511 entries, a Python list of the first tokens of the
heading ("['$', 'إبراهيم', 'بن', ...]") instead of a name, and the registry copied it. This script rebuilds
those values from the corpus and cleans the rows that still carry collation marks. WK ruling 2026-11-28.

Rule for a broken row (function name_from_corpus):
  the entry's first paragraph (heading line + the lines that follow, up to a blank line, the next heading,
  or a line starting with "|"), without the print's entry number and without ★ / ±±±, whitespace collapsed,
  cut before the first full stop written as a separate token (" . "). No full stop: the whole paragraph.
Rows not in the corpus (retired numbers): the tokens left in the broken value, joined.
Rows that are not broken but carry ±±± or a working memo (and AIND-D08578, whose words were corrected): the marks are removed; if the result then differs
  from the corpus (words corrected in PR #128), the same number of words is taken from the corpus.

Only name_ar and history change. Rows with a record (XML) are never touched.

to_review.tsv lists the rebuilt rows a person should look at again, with the reason (function reasons):
  more than 30 words / no full stop / not in the corpus / the name breaks off (a gap in the print: the value
  ends in بن, ابن, و or هو before the full stop) / a full stop attached to a word, so the rule did not cut there.
  The last two were added after the review of PR #130 (WK ruling 2026-11-28); their values are not changed.

  fix_name_ar.py report <dir>   write the tables to <dir>, change nothing
  fix_name_ar.py apply <dir>    write the tables and update the registry
  fix_name_ar.py review <dir>   rewrite <dir>/to_review.tsv from <dir>/rebuilt.tsv, change nothing else

After apply the registry has no broken rows left, so report and apply would write empty tables: both refuse
to run then. Use review to rebuild to_review.tsv from the rebuilt.tsv written at apply time.
"""
import ast, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_authority as B

DATE = '2026-11-28'
STOP = re.compile(r'\s\.(?=\s|$)')
MEMO = re.compile(r'\[[^\]]*order false[^\]]*\]')            # the working memo left in AIND-D08570
EXTRA = {'AIND-D08578'}                                      # no mark, but the words were corrected in PR #128
INDEX = ('AIND-D11191', 'AIND-D12845')                          # the index part of vol. 11
OPEN_END = {'بن', 'ابن', 'و', 'هو'}                          # a name that ends in one of these breaks off (gap in the print)
UNCUT = {'AIND-D08832', 'AIND-D08978'}                       # full stop attached to the last word of the name (no space in the corpus)
REVIEW_COLS = ['id', 'section', 'cut', 'words', 'new', 'reason']

def reasons(x):
    """Why a rebuilt row goes to to_review.tsv ('' = it does not). x: id, cut, words, new."""
    out = []
    if x['cut'] == 'tokens':
        out.append('corpus にない')
    if x['cut'] == 'none':
        out.append('句点なし')
    if int(x['words']) > 30:
        out.append('30語超')
    if x['cut'] == 'period' and x['new'].split()[-1] in OPEN_END:
        out.append('欠字で名前が途中')
    if x['id'] in UNCUT:
        out.append('句点に空白がなく切れていない')
    return '／'.join(out)

def review_rows(rebuilt):
    return [dict(x, reason=reasons(x)) for x in rebuilt if reasons(x)]

def norm(s):
    return re.sub(r'\s+', ' ', s.replace('★', '').replace('±±±', '')).strip()

def paragraphs():
    """id -> first paragraph of the entry (heading line included), entry number removed."""
    lines = open(os.path.join(B.ROOT, B.CORPUS), encoding='utf-8').read().split('\n')
    out = {}
    for i, l in enumerate(lines):
        m = B.H.match(l)
        if not m or not m[1]:
            continue
        body, j = [m[4]], i + 1
        while j < len(lines) and lines[j].strip() and not lines[j].startswith('###$') and not lines[j].startswith('|'):
            body.append(lines[j]); j += 1
        out[m[1]] = (norm(re.sub(r'^\s*\d+\s+', '', ' '.join(body))), len(body))
    return out

def name_from_corpus(par):
    m = STOP.search(par)
    return (par[:m.start()].strip(), 'period') if m else (par, 'none')

def plan():
    R = B.read_tsv(B.REG); P = paragraphs(); X = B.xmls()
    rebuilt, cleaned = [], []
    for r in R:
        old, aid = r['name_ar'], r['id']
        if old.startswith('['):
            assert aid not in X, aid
            if aid in P:
                new, cut = name_from_corpus(P[aid][0])
                why = f'{DATE} name_ar を corpus の見出しから作り直した（最初の句点の手前まで。PersonList から来た値はトークンのリストで名前ではなかった。WK 裁定 {DATE}）'
            else:
                new, cut = ' '.join(t for t in ast.literal_eval(old) if not set(t) <= set('$')), 'tokens'
                why = f'{DATE} name_ar を、PersonList から来たトークンのリストに残っていた語をつないだ値にした（corpus にない番号で、ほかに出どころがない。WK 裁定 {DATE}）'
            sec = 'index' if INDEX[0] <= aid <= INDEX[1] else 'main'
            rebuilt.append(dict(id=aid, section=sec, cut=cut, words=len(new.split()), new=new, old=old, why=why))
        elif '±' in old or '★' in old or MEMO.search(old) or aid in EXTRA:
            assert aid not in X and aid in P, aid
            c = norm(MEMO.sub(' ', old))
            pre = ' '.join(P[aid][0].split()[:len(c.split())])
            if pre == old:
                continue
            cleaned.append(dict(id=aid, old=old, new=pre, marks_only=c, differs='yes' if c != pre else '',
                                why=f'{DATE} name_ar から校合の作業記号・作業メモを外した' + ('。語は corpus（PR #128 で刊本に合わせた）と同じにした' if c != pre else '') + f'（WK 裁定 {DATE}）'))
    return R, rebuilt, cleaned

if __name__ == '__main__':
    if len(sys.argv) != 3 or sys.argv[1] not in ('report', 'apply', 'review'):
        sys.exit(__doc__)
    d = sys.argv[2]; os.makedirs(d, exist_ok=True)
    w = lambda n, rows, cols: open(os.path.join(d, n), 'w', encoding='utf-8', newline='').write(B.dump(rows, cols))
    if sys.argv[1] == 'review':
        rev = review_rows(B.read_tsv(os.path.join(d, 'rebuilt.tsv')))
        w('to_review.tsv', rev, REVIEW_COLS)
        print('to_review', len(rev))
        sys.exit()
    R, rebuilt, cleaned = plan()
    if not rebuilt and not cleaned:
        sys.exit('nothing to rebuild or clean (already applied); tables left as they are. To rebuild to_review.tsv, use: review <dir>')
    w('rebuilt.tsv', rebuilt, ['id', 'section', 'cut', 'words', 'new', 'old'])
    w('to_review.tsv', review_rows(rebuilt), REVIEW_COLS)
    w('cleaned.tsv', cleaned, ['id', 'differs', 'old', 'new', 'marks_only'])
    print('rebuilt', len(rebuilt), 'cleaned', len(cleaned), 'to_review', len(review_rows(rebuilt)))
    if sys.argv[1] == 'apply':
        ch = {x['id']: x for x in rebuilt + cleaned}
        for r in R:
            if r['id'] in ch:
                r['name_ar'] = ch[r['id']]['new']
                r['history'] = (r['history'] + ' | ' if r['history'] else '') + ch[r['id']]['why']
        open(B.REG, 'w', encoding='utf-8', newline='').write(B.dump(R, B.REG_COLS))
        print('registry updated', len(ch))
