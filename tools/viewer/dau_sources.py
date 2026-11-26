"""Viewer text for source citations and assessments: writes <dau_view.json> from <dau.json> (left untouched), using
<v01>/source_ids.json written by to_v01.py.
  @E01[mention:eK] -> @C01[mention:cN];  @O..[status…] moved to assessments -> @V..[assessment:vN];
  rule-placed assessments are inserted as @V01[assessment:vN]; moved entries leave the office list.
usage: python3 dau_sources.py <v01 dir> <dau.json> <dau_view.json>"""
import json, re, sys
M = json.load(open(sys.argv[1] + '/source_ids.json')); D = json.load(open(sys.argv[2])); n = C_ = 0
for e in D:
    k = e['k']; t = e.get('t')
    if not t: continue
    v = M['assessments'].get(k)
    if v:
        toks = t.split(' ')
        labs = list(v['labels'])
        if v['retag']:                               # the n-th ID-less status tag belongs to the n-th ID-less status entry
            keep = []
            for o in e.get('o') or []:
                if o.get('typ') == 'status' and not o.get('id') and o.get('lab') in labs: labs.remove(o['lab'])
                else: keep.append(o)
            if 'o' in e: e['o'] = keep
        for i, tag in v.get('retag_at') or []:
            assert toks[i].startswith('@O'), (k, toks[i]); toks[i] = tag
        for i, tag in sorted(v['insert'], reverse=True): toks.insert(i, tag); n += 1
        t = ' '.join(toks)
    m = M['sources'].get(k)
    if m:
        def f(x):
            global C_
            if x.group(3) in m: C_ += 1; return f'@C{x.group(1)}[mention:{m[x.group(3)]}]'
            return x.group(0)
        t = re.sub(r'@E(\d+)\[([^:\]]*):(e\d+)\]', f, t)
    e['t'] = t
json.dump(D, open(sys.argv[3], 'w'), ensure_ascii=False, separators=(',', ':')); print('citations', C_, 'assessment tags inserted', n)
