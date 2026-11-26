"""Retag source citations in the viewer text (dau.json): @E01[mention:eK] -> @C01[mention:cN], using
<v01>/source_ids.json written by to_v01.py.  usage: python3 dau_sources.py <v01 dir> <dau.json>"""
import json, re, sys
cmap = json.load(open(sys.argv[1] + '/source_ids.json')); D = json.load(open(sys.argv[2])); n = 0
for e in D:
    m = cmap.get(e['k'])
    if not m or not e.get('t'): continue
    def f(x):
        global n
        if x.group(3) in m: n += 1; return f'@C{x.group(1)}[mention:{m[x.group(3)]}]'
        return x.group(0)
    e['t'] = re.sub(r'@E(\d+)\[([^:\]]*):(e\d+)\]', f, e['t'])
json.dump(D, open(sys.argv[2], 'w'), ensure_ascii=False, separators=(',', ':')); print('retagged', n)
