import csv,re,os,sys,json,collections
csv.field_size_limit(10**9)
W='/home/claude/work/audit/'; R='/home/claude/ainet-db-sakhawi/'
PL=list(csv.reader(open(W+'personlist.csv',encoding='utf-8')))[1:]
IM=list(csv.reader(open(W+'idmaster.csv',encoding='utf-8')))[1:]
F=[]  # findings: (area, code, severity, key, detail)
def add(area,code,sev,key,detail): F.append((area,code,sev,key,detail))
def norm(s):
    s=re.sub(r'[ً-ْٰـ★()]','',s or ''); s=re.sub('[إأآٱ]','ا',s)
    s=s.replace('ى','ي').replace('ة','ه'); s=re.sub(r'^\s*\d+\s*','',s)
    return ' '.join(re.findall(r'[ء-ي]+',s))
# ---------- corpus
H=re.compile(r'^###\$(?:(AIND-D\w+) \| )?(\d{12})\$# (\$+) ?(.*)')
corp={}; corp_noid=[]; corder=[]
for ln,l in enumerate(open(R+'0__DawForAIND_renumbered_B54_split20260905.txt',encoding='utf-8').read().split('\n'),1):
    m=H.match(l)
    if not m: continue
    d=dict(id=m[1],n=m[2],k=m[3],head=m[4],line=ln)
    if m[1]:
        if m[1] in corp: add('corpus','C-DUP-ID','高',m[1],f'行{corp[m[1]]["line"]}と行{ln}')
        corp[m[1]]=d; corder.append(m[1])
    else: corp_noid.append(d)
n12=collections.Counter(d['n'] for d in list(corp.values())+corp_noid)
for n,c in n12.items():
    if c>1: add('corpus','C-DUP-12','高',n,f'{c}回')
# ---------- PersonList
IDRE=re.compile(r'^AIND-D\d{5}[a-z]?$')
pl={}; 
for i,r in enumerate(PL,2):
    r=(r+['']*11)[:11]; tok,who,aid,n,full,short,b,d,mad,note=r[:10]
    aid=aid.strip()
    if not aid: add('人物一覧','P-NO-ID','高',f'行{i}','AIND-D IDが空'); continue
    if not IDRE.match(aid): add('人物一覧','P-ID-FORMAT','高',aid,f'行{i} 書式が不正')
    if aid in pl: add('人物一覧','P-DUP-ID','高',aid,f'行{pl[aid]["row"]}と行{i}')
    pl[aid]=dict(row=i,tok=tok.strip(),who=who.strip(),n=n.strip(),full=full.strip(),short=short.strip(),b=b.strip(),d=d.strip(),mad=mad.strip(),note=note.strip())
c12=collections.defaultdict(list)
for a,p in pl.items():
    if p['n']:
        c12[p['n']].append(a)
        if not re.match(r'^\d{12}$',p['n']): add('人物一覧','P-12-FORMAT','高',a,f'行{p["row"]} 12桁ID「{p["n"]}」')
for n,a in c12.items():
    if len(a)>1: add('人物一覧','P-DUP-12','高',n,' / '.join(a))
# blank-status rows
for a,p in pl.items():
    blank=not p['n'] and not p['full']
    p['blank']=blank
    k=corp.get(a,{}).get('k')
    if blank and not p['note']: add('人物一覧','P-BLANK-NO-NOTE','中',a,f'行{p["row"]} 名前・12桁IDが空で注記もない（corpus種別 {k or "なし"}）')
    if blank and k in('$','$$'): add('人物一覧×corpus','PC-BLANK-BUT-MAIN','中',a,f'行{p["row"]} 人物一覧は空欄（転送・統合の扱い）だがcorpusは本伝（{k}）。注記: {p["note"][:60]}')
    if not blank and k=='$$$': add('人物一覧×corpus','PC-FILLED-BUT-REF','低',a,f'行{p["row"]} corpusは転送項（$$$）だが人物一覧に名前等が入っている')
    if (not p['n'])!=(not p['full']): add('人物一覧','P-HALF-BLANK','中',a,f'行{p["row"]} 12桁IDと名前の片方だけ空')
# duplicate content (D00385-type)
sig=collections.defaultdict(list)
for a,p in pl.items():
    if len(norm(p['full']).split())>=3 and (p['b'] or p['d']): sig[(norm(p['full']),p['b'],p['d'])].append(a)
for k,a in sig.items():
    if len(a)>1: add('人物一覧','P-DUP-CONTENT','中',' / '.join(a),f'名前・生没年が同一: {k[0][:50]} | {k[1]} | {k[2]}')
# dates
DOK=re.compile(r'^\d{3,4}(-\d{2}(-\d{2})?)?$')
bad=collections.Counter()
for a,p in pl.items():
    for fld in('b','d'):
        v=p[fld]
        if v and not DOK.match(v):
            add('人物一覧','P-DATE-ARABIC' if re.search(r'[\u0621-\u064A]',v) and not re.search(r'\d',v) else 'P-DATE-QUALIFIED','低',a,f'行{p["row"]} {"生年" if fld=="b" else "没年"}「{v[:40]}」')
        elif v:
            y=int(v[:4] if len(v.split("-")[0])==4 else v.split('-')[0])
            if not 600<=y<=910: add('人物一覧','P-DATE-RANGE','中',a,f'行{p["row"]} {"生年" if fld=="b" else "没年"} {v}')
    if p['b'] and p['d'] and DOK.match(p['b']) and DOK.match(p['d']):
        yb,yd=int(p['b'].split('-')[0]),int(p['d'].split('-')[0])
        if yd<yb or yd-yb>110: add('人物一覧','P-DATE-ORDER','高',a,f'行{p["row"]} 生年{p["b"]} 没年{p["d"]}')
mads=collections.Counter(p['mad'] for p in pl.values() if p['mad'])
MAD={'الشافعي':'Shafi','الحنفي':'Hanafi','المالكي':'Maliki','الحنبلي':'Hanbali'}
for a,p in pl.items():
    if p['mad'] and p['full']:
        inname=[v for k,v in MAD.items() if re.search(k+r'(\s|$)',p['full'])]
        madn=p['mad']
        for k,v in MAD.items(): madn=madn.replace(k,v)
        if inname and not any(v.lower() in madn.lower() for v in inname):
            add('人物一覧','P-MADHHAB-NAME','中',a,f'行{p["row"]} 名前に{"/".join(inname)}、学派欄は「{p["mad"]}」')
# ---------- PL x corpus
for a in corp:
    if a not in pl: add('人物一覧×corpus','PC-MISSING-IN-PL','高',a,f'corpus行{corp[a]["line"]}（{corp[a]["k"]}）が人物一覧にない: {corp[a]["head"][:50]}')
for a,p in pl.items():
    if a not in corp:
        add('人物一覧×corpus','PC-NOT-IN-CORPUS','中' if p['note'] else '高',a,f'行{p["row"]} corpusにない。注記: {p["note"][:70] or "（なし）"}')
        continue
    c=corp[a]
    if p['n'] and p['n']!=c['n']: add('人物一覧×corpus','PC-12-MISMATCH','高',a,f'行{p["row"]} 人物一覧 {p["n"]} / corpus {c["n"]}')
    if p['full']:
        x=norm(p['full']).split(); y=norm(c['head']).split()
        k=min(len(x),len(y),4)
        if k>=2 and x[:k]!=y[:k] and ' '.join(x[:2]) not in ' '.join(y[:14]):
            add('人物一覧×corpus','PC-NAME-MISMATCH','低',a,f'行{p["row"]} 人物一覧「{" ".join(x[:6])}」/ corpus「{" ".join(y[:6])}」')
# order
rows=[(p['row'],a) for a,p in pl.items() if a in corp]; rows.sort()
pos={a:i for i,a in enumerate(corder)}
# ---------- XML
xml={}; refs=collections.defaultdict(set); 
REF=re.compile(r'(?:ref|active|passive|corresp|sameAs)="([^"]*)"')
for d,_,fs in os.walk(R+'Individuals'):
    for f in fs:
        if not f.endswith('.xml'): continue
        isref=f.startswith('REF_'); m=re.match(r'(?:REF_)?(AIND-D\w+?)_(\d{12})\.xml$',f)
        t=open(os.path.join(d,f),encoding='utf-8').read()
        if not m: add('XML','X-FILENAME','高',f,'ファイル名の書式が不正'); continue
        a,n=m[1],m[2]
        xid=re.search(r'<person[^>]*xml:id="([^"]*)"(?:[^>]*source="([^"]*)")?',t)
        b=re.search(r'<birth[^>]*when-custom="([^"]*)"',t); de=re.search(r'<death[^>]*when-custom="([^"]*)"',t)
        full=re.search(r'<persName type="full"[^>]*>([^<]*)',t)
        aff=re.search(r'<affiliation[^>]*type="madhhab"[^>]*>',t) or re.search(r'type="madhhab"[^>]*ref="([^"]*)"',t)
        xml[a]=dict(ref=isref,n=n,xid=xid[1] if xid else None,src=xid[2] if xid else None,b=b[1] if b else '',d=de[1] if de else '',full=full[1] if full else '',file=f)
        if a in xml and xml[a]['file']!=f: add('XML','X-DUP-FILE','高',a,f)
        if not isref and (not xid or xid[1]!=a): add('XML','X-ID-MISMATCH','高',a,f'ファイル名と xml:id「{xid[1] if xid else None}」が違う')
        if xid and xid[2] and xid[2]!=n: add('XML','X-SOURCE-MISMATCH','高',a,f'ファイル名 {n} / source {xid[2]}')
        for mm in REF.finditer(t):
            for v in mm[1].split():
                refs[v].add(a)
for a,x in xml.items():
    if a not in corp: add('XML×corpus','XC-NOT-IN-CORPUS','高',a,f'{x["file"]} のIDがcorpusにない')
    elif corp[a]['n']!=x['n']: add('XML×corpus','XC-12-MISMATCH','高',a,f'XML {x["n"]} / corpus {corp[a]["n"]}')
    elif corp[a]['k']=='$$$' and not x['ref']: add('XML×corpus','XC-XML-FOR-REF','中',a,'corpusでは転送項（$$$）なのに通常のXMLがある')
    elif corp[a]['k']!='$$$' and x['ref']: add('XML×corpus','XC-REFXML-FOR-MAIN','中',a,f'REF_ のXMLがあるがcorpusは本伝（{corp[a]["k"]}）')
    p=pl.get(a)
    if not p: add('XML×人物一覧','XP-NOT-IN-PL','高',a,'XMLがあるのに人物一覧に行がない'); continue
    if x['ref']: continue
    if p['blank']: add('XML×人物一覧','XP-PL-BLANK','中',a,f'XMLがあるのに人物一覧 行{p["row"]} は空欄（転送・統合扱い）。注記: {p["note"][:50]}')
    def yr(v):
        m=re.match(r'0*(\d{3})',v or ''); return int(m[1]) if m else None
    for fld,lab in(('b','生年'),('d','没年')):
        px,xx=yr(p[fld]),yr(x[fld])
        if px and xx and px!=xx: add('XML×人物一覧','XP-DATE-DIFF','中',a,f'{lab}: 人物一覧 {p[fld]} / XML {x[fld]}')
        elif xx and not p[fld]: add('XML×人物一覧','XP-DATE-PL-EMPTY','低',a,f'{lab}: XML {x[fld]}、人物一覧は空')
        elif p[fld] and DOK.match(p[fld]) and not x[fld]: add('XML×人物一覧','XP-DATE-XML-EMPTY','低',a,f'{lab}: 人物一覧 {p[fld]}、XMLにない')
# refs
im={}; 
for i,r in enumerate(IM,2):
    r=(r+['']*9)[:9]; who,cat,ar,la,idv,note,fix,cls,st=r
    idv=idv.strip()
    if not idv:
        if cat or ar: add('ID-Master','M-NO-ID','高',f'行{i}',f'{cat} {ar[:30]}')
        continue
    for one in re.split(r'\s*[|,]\s*',idv):
        if one in im: add('ID-Master','M-DUP-ID','高',one,f'行{im[one]["row"]}と行{i}')
        im[one]=dict(row=i,cat=cat.strip(),ar=ar,note=note,st=st,raw=idv)
FMT={'Nisbah':r'TMP-N-\d{5}','Person':r'(TMP-P-\d{6}|AIND-D\d{5}[a-z]?|Q\d+)','Location':r'(TMP-L-\d{5}|\d{3,9}|Q\d+)','Institution':r'(TMP-I-\d{5}|Q\d+|\d{3,9})','Office':r'(TMP-O-\d{5}|Q\d+)','Text':r'(TMP-T-\d{5}|Q\d+)','Subject':r'(TMP-S-\d{5}|Q\d+)'}
for k,v in im.items():
    f=FMT.get(v['cat'])
    if f is None: add('ID-Master','M-CATEGORY','中',k,f'行{v["row"]} Category「{v["cat"]}」')
    elif not re.fullmatch(f,k): add('ID-Master','M-ID-FORMAT','高',k,f'行{v["row"]} {v["cat"]} のIDとして書式が不正')
    if v['cat']=='Person' and k.startswith('AIND-D'):
        if k not in pl: add('ID-Master×人物一覧','MP-AIND-NOT-IN-PL','高',k,f'ID-Master 行{v["row"]} のAIND番号が人物一覧にない')
        elif pl[k]['blank']: add('ID-Master×人物一覧','MP-AIND-BLANK','中',k,f'ID-Master 行{v["row"]} が指すAIND番号は人物一覧で空欄（転送・統合扱い）')
# same label multiple IDs
lab=collections.defaultdict(set)
for k,v in im.items():
    for part in v['ar'].split('|'):
        s=norm(part)
        if s: lab[(v['cat'],s)].add(k)
for (cat,s),ks in lab.items():
    if len(ks)>1 and cat!='Person': add('ID-Master','M-SAME-LABEL','低',' / '.join(sorted(ks)),f'{cat}「{s}」に複数のID')
# refs resolve
used_im=set()
for v,recs in refs.items():
    ex=sorted(recs)[:3]; n=len(recs)
    if v.startswith('#AIND-D'):
        a=v[1:]
        if a in xml and len(recs)==1 and a in recs: pass
        if a not in corp and a not in pl: add('XMLの参照','R-AIND-UNKNOWN','高',a,f'{n}件のXMLが参照（例 {", ".join(ex)}）。corpusにも人物一覧にもない')
        elif a not in corp: add('XMLの参照','R-AIND-RETIRED','高',a,f'{n}件のXMLが参照（例 {", ".join(ex)}）。corpusにない番号（統合済みか）。注記: {pl[a]["note"][:50]}')
        elif corp[a]['k']=='$$$': add('XMLの参照','R-AIND-TO-REF','中',a,f'{n}件のXMLが転送項（$$$）を参照（例 {", ".join(ex)}）')
        elif a in pl and pl[a]['blank'] and recs!={a}: add('XMLの参照','R-AIND-TO-BLANK','中',a,f'{n}件のXMLが、人物一覧で空欄の番号を参照（例 {", ".join(ex)}）')
    elif v.startswith('#TMP-'):
        k=v[1:]; used_im.add(k)
        if k not in im: add('XMLの参照','R-TMP-UNKNOWN','高',k,f'{n}件のXMLが参照（例 {", ".join(ex)}）。ID-Masterにない')
    elif v.startswith('wd:'):
        k=v[3:]; used_im.add(k)
        if k not in im: add('XMLの参照','R-WD-UNKNOWN','中',v,f'{n}件のXMLが参照（例 {", ".join(ex)}）。ID-Masterにない')
    elif v.startswith('gn:'):
        k=v[3:]; used_im.add(k)
        if k not in im: add('XMLの参照','R-GN-UNKNOWN','中',v,f'{n}件のXMLが参照（例 {", ".join(ex)}）。ID-Masterにない')
    elif v=='#NEEDID': add('XMLの参照','R-NEEDID','低','#NEEDID',f'{n}件のXMLに残っている')
    elif v.startswith('#') or ':' in v:
        add('XMLの参照','R-OTHER-FORM','中',v[:40],f'{n}件のXML（例 {", ".join(ex)}）')
unused=collections.Counter(v['cat'] for k,v in im.items() if k not in used_im and not k.startswith('AIND-D'))
json.dump(dict(noid_kinds=collections.Counter(d['k'] for d in corp_noid),xml_ref=sum(x['ref'] for x in xml.values()),pl=len(pl),corp=len(corp),corp_noid=len(corp_noid),xml=len(xml),im=len(im),mads=mads.most_common(),unused=unused,
  pl_blank=sum(p['blank'] for p in pl.values()),kinds=collections.Counter(c['k'] for c in corp.values()),refkinds=collections.Counter(re.sub(r'[\dA-Za-z]+$','',re.sub(r'\d','',v))[:8] for v in refs)),open(W+'summary.json','w'),ensure_ascii=False,indent=1)
with open(W+'findings.tsv','w',encoding='utf-8',newline='') as f:
    w=csv.writer(f,delimiter='\t'); w.writerow(['対象','コード','重大度','ID・行','内容']); w.writerows(F)
c=collections.Counter((a,b,s) for a,b,s,_,_ in F)
for (a,b,s),n in sorted(c.items()): print(f'{a}\t{b}\t{s}\t{n}')
print(open(W+'summary.json').read()[:1500])
