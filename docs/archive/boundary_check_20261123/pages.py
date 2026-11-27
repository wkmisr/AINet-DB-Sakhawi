import re,json
C='/home/claude/ainet-db-sakhawi/0__DawForAIND_renumbered_B54_split20260905.txt'
O='/home/claude/openiti/0925ah/data/0902Sakhawi/0902Sakhawi.DawLamic/0902Sakhawi.DawLamic.JK003608-ara1.mARkdownSimple'
raw=open(O,encoding='utf-8').read()
# page of a position = first page marker at or after it
marks=[(m.start(),int(m[1]),int(m[2])) for m in re.finditer(r'PageV(\d+)P(\d+)',raw)]
import bisect
mp=[m[0] for m in marks]
def page(pos):
    j=bisect.bisect_left(mp,pos)
    return (marks[j][1],marks[j][2]) if j<len(marks) else None
op={}
for m in re.finditer(r'^###\$(\d{12})\$#',raw,re.M): op[m[1]]=page(m.start())
H=re.compile(r'^###\$(?:(AIND-D\w+) \| )?(\d{12})\$# (\$+) ?(.*)')
ents=[]
for ln,l in enumerate(open(C,encoding='utf-8').read().split('\n'),1):
    m=H.match(l)
    if m: ents.append(dict(id=m[1] or '',n=m[2],k=m[3],head=m[4],line=ln,vp=op.get(m[2])))
print(len(ents),'with page',sum(e['vp'] is not None for e in ents),'openiti heads',len(op))
bad=0;last=None
for e in ents:
    if e['vp']:
        if last and tuple(e['vp'])<tuple(last): bad+=1
        last=e['vp']
print('non-monotonic',bad)
cn={e['n'] for e in ents}
print('openiti-only ids',len(set(op)-cn),'corpus-only',sum(e['vp'] is None for e in ents))
json.dump(ents,open('pages.json','w'),ensure_ascii=False)
json.dump({'pages_per_vol':{v:max(p for _,vv,p in marks if vv==v) for v in range(1,13)}},open('vols.json','w'))
print(json.load(open('vols.json')))
