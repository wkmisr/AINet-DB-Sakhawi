import sys,json
from norm import norm
qs=[norm(a) for a in sys.argv[1:]]
d=json.load(open('corpus_index.json'))
for k,v in d.items():
    h=norm(v['text'][:260])
    if all(q in h for q in qs): print(k,v['dollars'],'|',v['text'][:220].replace('\n',' '))
