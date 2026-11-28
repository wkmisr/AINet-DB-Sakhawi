import re,json,sys
C='/home/claude/ainet-db-sakhawi/0__DawForAIND_renumbered_B54_split20260905.txt'
O='/home/claude/openiti/0925ah/data/0902Sakhawi/0902Sakhawi.DawLamic/0902Sakhawi.DawLamic.JK003608-ara1.mARkdownSimple'
def norm(w):
    w=re.sub(r'[ً-ْٰـ]','',w)
    w=re.sub('[إأآٱ]','ا',w); w=w.replace('ى','ي').replace('ة','ه').replace('ؤ','و').replace('ئ','ي')
    if w in('ابنه','ابنت'): w='بنت'
    return w
AR=re.compile(r'[ء-يً-ْٰ]+|PageV\d+P\d+')
toks=[];pg=[];cur=(1,1)  # page of token = page whose end-marker follows
raw=open(O,encoding='utf-8').read()
start=raw.index('#META#Header#End#') if '#META#Header#End#' in raw else 0
pending=[]
for m in AR.finditer(raw,start):
    t=m.group()
    if t.startswith('PageV'):
        v,p=int(t[5:7]),int(t[8:])
        for i in pending: pg[i]=(v,p)
        pending=[]
    else:
        toks.append(norm(t)); pg.append(None); pending.append(len(toks)-1)
last=None
for i in range(len(pg)):
    if pg[i] is None: pg[i]=last
    else: last=pg[i]
idx={}
for i in range(len(toks)-2):
    idx.setdefault((toks[i],toks[i+1],toks[i+2]),[]).append(i)
H=re.compile(r'^###\$(?:(AIND-D\w+) \| )?(\d{12})\$# (\$+) ?(.*)')
ents=[];cw=0;cur=None
W=re.compile(r'[\u0621-\u064A]+')
for ln,l in enumerate(open(C,encoding='utf-8').read().split('\n'),1):
    m=H.match(l)
    if m:
        cur=dict(id=m[1] or '',n=m[2],k=m[3],head=m[4],line=ln,cw=cw); ents.append(cur)
    cw+=len(W.findall(l))
import bisect
pos=0;lastcw=0;ok=0
for e in ents:
    ws=[norm(w) for w in re.findall(r'[\u0621-\u064A\u064B-\u0652\u0670]+',e['head'].replace('★',''))]
    num=re.match(r'\s*(\d+)',e['head']); e['num']=int(num[1]) if num else None
    e['tok']=None
    exp=pos+(e['cw']-lastcw); tol=400+0.25*(e['cw']-lastcw)
    for off in (0,1,2):
        key=tuple(ws[off:off+3])
        if len(key)<3: break
        c=idx.get(key)
        if c:
            j=bisect.bisect_left(c,exp); best=None
            for q in (j-1,j):
                if 0<=q<len(c) and abs(c[q]-off-exp)<=tol and c[q]-off>pos-5:
                    if best is None or abs(c[q]-off-exp)<abs(best-exp): best=c[q]-off
            if best is not None: e['tok']=best; break
    if e['tok'] is not None: pos=e['tok']; lastcw=e['cw']; e['vp']=pg[min(pos,len(pg)-1)]; ok+=1
    else: e['vp']=None
print(len(ents),'matched',ok)
# monotonic check
bad=sum(1 for a,b in zip(ents,ents[1:]) if a['vp'] and b['vp'] and b['vp']<a['vp'])
print('non-monotonic',bad)
json.dump(ents,open('/home/claude/work/boundary/aligned.json','w'),ensure_ascii=False)
