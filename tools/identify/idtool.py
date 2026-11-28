"""Command-line front end to the identification tools (design v5, sec. 4.2).

  python3 tools/identify/idtool.py search "الشرف المناوي" [--record AIND-D06528] [--kind father] [-k 20]
  python3 tools/identify/idtool.py genealogy AIND-D06528 father
  python3 tools/identify/idtool.py neighbours AIND-D06501 [-n 2]
  python3 tools/identify/idtool.py read AIND-D06501
  python3 tools/identify/idtool.py reverse AIND-D04627
  python3 tools/identify/idtool.py authority "ابن الجزري" [--all]
  python3 tools/identify/idtool.py text "ويعرف بابن حسان" ["second phrase" ...] [--record AIND-D07217]
  python3 tools/identify/idtool.py features AIND-D06528

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
    ap.add_argument('--all', action='store_true', help='authority: include persons with an entry (AIND)')
    a = ap.parse_args()
    ix = A.Index()
    def head(p):
        d = {'id': p, 'heading': ix.persons[ix.pos[p]]['name']}
        r = ix.registry_row(p) or {}
        if r.get('status') and r['status'] != 'active':      # transfer heading, merged or retired ID
            d['status'] = r['status']
            if r.get('target'):
                d['target'] = r['target']
        return d
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
        out = [{'id': i, 'score': s, 'name': n, 'aliases': al, 'note': nt}
               for i, s, n, al, nt in ix.authority_search(' '.join(a.args), k=a.k, include_aind=a.all)]
    elif a.cmd == 'text':
        total, hits = ix.text_search(a.args, k=a.k, exclude={a.record} if a.record else None)
        out = [{'total': total, 'shown': len(hits)}] + [dict(head(p), snippet=sn) for p, sn in hits]
    elif a.cmd == 'features':
        f = ix.feat[a.args[0]]
        out = [{k: sorted(v) for k, v in f.items()} | {'nasab': A.nasab_list(ix.persons[ix.pos[a.args[0]]]['name'])}]
    else:
        ap.error('unknown command')
    for o in out:
        print(json.dumps(o, ensure_ascii=False))


if __name__ == '__main__':
    main()
