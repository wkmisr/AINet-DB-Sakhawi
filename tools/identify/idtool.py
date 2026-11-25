"""Command-line front end to the identification tools (design v5, sec. 4.2).

  python3 tools/identify/idtool.py search "الشرف بن مفلح" [--record AIND-D01906] [--kind father] [-k 20]
  python3 tools/identify/idtool.py genealogy AIND-D01906 father
  python3 tools/identify/idtool.py neighbours AIND-D10588 [-n 2]
  python3 tools/identify/idtool.py read AIND-D10588
  python3 tools/identify/idtool.py reverse AIND-D04627
  python3 tools/identify/idtool.py authority "ابن الجزري"
  python3 tools/identify/idtool.py features AIND-D01906

With --record, `search` runs the full pre-search (name + genealogy shift + "الذي قبله"), excluding
the record itself. Output is JSON lines so that a model harness can read it.
"""
import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(__file__))
import aind_names as A


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd')
    ap.add_argument('args', nargs='*')
    ap.add_argument('--record'); ap.add_argument('--kind'); ap.add_argument('-k', type=int, default=20)
    ap.add_argument('-n', type=int, default=1)
    a = ap.parse_args()
    ix = A.Index()
    head = lambda p: {'id': p, 'heading': ix.persons[ix.pos[p]]['name']}
    out = []
    if a.cmd == 'search':
        q = ' '.join(a.args)
        if a.record:
            res, kind = ix.presearch(a.record, q, kind=a.kind, k=a.k)
        else:
            res, _ = ix.search(q, k=a.k)
        out = [dict(head(p), score=s, why=w) for p, s, w in res]
    elif a.cmd == 'genealogy':
        out = [head(p) for p in ix.genealogy(a.args[0], a.args[1])[:a.k]]
    elif a.cmd == 'neighbours':
        out = [head(p) for p in ix.neighbours(a.args[0], a.n)]
    elif a.cmd == 'read':
        out = [dict(head(a.args[0]), text=ix.read(a.args[0]))]
    elif a.cmd == 'reverse':
        r = ix.reverse(a.args[0])
        out = [{'xml_refs': r['xml'], 'text_hits': r['text'], 'text_patterns': r['text_patterns']}]
    elif a.cmd == 'authority':
        out = [{'id': i, 'score': s, 'name': n, 'aliases': al} for i, s, n, al in ix.authority_search(' '.join(a.args), k=a.k)]
    elif a.cmd == 'features':
        f = ix.feat[a.args[0]]
        out = [{k: sorted(v) for k, v in f.items()} | {'nasab': A.nasab_list(ix.persons[ix.pos[a.args[0]]]['name'])}]
    else:
        ap.error('unknown command')
    for o in out:
        print(json.dumps(o, ensure_ascii=False))


if __name__ == '__main__':
    main()
