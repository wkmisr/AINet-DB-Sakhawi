import sys,json,csv,re
from norm import norm
q=norm(sys.argv[1]); mode=sys.argv[2] if len(sys.argv)>2 else 'both'; lim=int(sys.argv[3]) if len(sys.argv)>3 else 10
if mode in('id','both'):
    n=0
    for row in csv.reader(open('idmaster_0908.tsv',encoding='utf-8'),delimiter='\t'):
        if len(row)<5: continue
        if q in norm(row[2]) or q in norm(row[5] if len(row)>5 else ''):
            print('ID |',' | '.join(row[1:6])); n+=1
            if n>=lim: break
if mode in('corpus','both'):
    d=json.load(open('corpus_index.json')); n=0
    for k,v in d.items():
        t=norm(v['text'])
        if q in t:
            i=t.find(q); s=v['text']
            print('C |',k,v['dollars'],'|',s[:200].replace('\n',' ') if i<200 else '…'+s[max(0,i-80):i+120].replace('\n',' ')); n+=1
            if n>=lim: break
