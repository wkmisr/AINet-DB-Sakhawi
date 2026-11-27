import re, json, glob, csv, collections, sys
import os
if os.environ.get('PYTHONHASHSEED')!='0':                  # set iteration order decides some alias placements: keep runs reproducible
    os.environ['PYTHONHASHSEED']='0'; os.execv(sys.executable,[sys.executable]+sys.argv)
HERE=os.path.dirname(os.path.abspath(__file__))
WORK=os.environ.get('AIND_WORK','.')
sys.path.insert(0,os.path.join(HERE,'..','convert'))
from tei2markdown import year_phrases, find_span, norm, TENS, HUND
from lxml import etree
R=os.environ.get('AIND_REPO',os.path.join(HERE,'..','..'))
XL="{http://www.w3.org/XML/1998/namespace}lang"
# ---- authority: rows in the ID-Master column order ('', Category, Arabic, Latin, ID, Note, -, class, Status).
# Read from the registries (authority/, the master since 2026-11-27; AIND_AUTHORITY or <repo>/authority);
# fall back to an ID-Master export ($AIND_WORK/idmaster.tsv) only when no registry is found.
AUTH=os.environ.get('AIND_AUTHORITY',os.path.join(R,'authority'))
def idmaster_rows():
    pe,en=os.path.join(AUTH,'persons_registry.tsv'),os.path.join(AUTH,'entities_registry.tsv')
    if not (os.path.exists(pe) and os.path.exists(en)):
        return list(csv.reader(open(os.path.join(WORK,'idmaster.tsv'),encoding='utf-8'),delimiter='\t'))
    bare=lambda i: i[3:] if i.startswith(('wd:','gn:')) else i
    st=lambda r: 'retired' if r['status']=='retired' else ''
    rows=[]
    ws=lambda x: re.sub(r'\s+',' ',x).strip()
    for r in csv.DictReader(open(en,encoding='utf-8'),delimiter='\t'):
        ar=' | '.join(ws(x) for x in [r['label_ar']]+r['variants'].split('|') if ws(x))
        rows.append(['',r['category'],ar,r['label_latn'],bare(r['id']),r['note'],'',r['class'],st(r)])
    for r in csv.DictReader(open(pe,encoding='utf-8'),delimiter='\t'):
        if r['status']=='merged': continue   # old numbers: their forms are on the surviving row
        al=[ws(v) for v in r['aliases'].split('|') if ws(v)]
        if r['id'].startswith('AIND-'):          # persons with a biography: only the aliases (their names come from the entries)
            if al: rows.append(['','Person',' | '.join(al),'',r['id'],r['note'],'','',st(r)])
            continue
        rows.append(['','Person',' | '.join([ws(r['name_ar'])]+al),'',bare(r['id']),r['note'],'','',st(r)])
    return rows
IDROWS=idmaster_rows()
HDR=re.compile(r'^###\$(AIND-D\d+[a-z]?|\d{12})(?: \| (\d{12}))?\$# ?(\${1,3}|\|)? ?(.*)$')
entries=[];cur=None
for line in open(R+'/0__DawForAIND_renumbered_B54_split20260905.txt',encoding='utf-8'):
    line=line.rstrip('\n')
    m=HDR.match(line)
    if m:
        key,src,kind,txt=m.groups()
        if key.isdigit(): src,key=key,key
        cur={'k':key,'s':src or '','m':{'$':'M','$$':'F','$$$':'R'}.get(kind,'O'),'lines':[txt]}
        entries.append(cur)
    elif cur and not line.startswith('#'):
        cur['lines'].append(line)
for e in entries: e['t']=norm(' '.join(e.pop('lines')))
print('entries',len(entries))

def kun_variants(name):
    w=name.split()
    out={name}
    if w and w[0] in ('أبو','أبي','أبا','ابو','ابي','ابا'):
        for k in ('أبو','أبي','أبا'): out.add(' '.join([k]+w[1:]))
    return out
ALIAS_STOP={'سمع','وسمع','مني','لي','لنا','له','لها','عني','عنه','كتبت','وكتبت','أجاز','وأجاز','أجزت','وأجزت','على','من','وغيره','وغيرهما','وغيرهم','عن','ممن','في','قرأ','وقرأ','حضر','وحضر','أخذ','وأخذ','إجازة','حافلة','قال','ذكره','ترجمه','كان','وهو','هو','وجماعة','وطائفة','وآخرين','وغير'}
GENERIC_KUNYA={'أبو بكر','أبو عبد الله','أبو محمد','أبو العباس','أبو الحسن','أبو الفضل','أبو القاسم','أبو حفص','أبو علي'}
def clean_alias(a):
    w=a.split()
    if w and w[0].startswith('و') and len(w[0])>3 and (w[0][1:].startswith('ال') or w[0][1:] in ('ابن','أبي','أبو','أبا')):
        w[0]=w[0][1:]
    return ' '.join(w)
def trim_desc(n):
    w=n.split()
    while w and (w[0] in ALIAS_STOP or w[0] in ('على','وعلى','من','ومن','عن','وعن','عند','وعند','سبط','شقيق','أخو','وأخو','ابنة','بنت','ابن أخت','زوج','زوجة','صهر','والد','أبو')) and len(w)>2:
        w=w[1:]
    if any(x in ALIAS_STOP for x in w): return ''
    return clean_alias(' '.join(w))
def usable_alias(a,oid=''):
    w=a.split()
    if not w or any(x in ALIAS_STOP for x in w): return False
    if a=='شيخنا': return oid=='wd:Q471116'
    if a in GENERIC_KUNYA: return False
    return len(w)>=2 or (len(w)==1 and w[0].startswith('ال') and len(w[0])>4)
INV={'teacher':'student','educator':'ward'}
def role_of(rel,pid):
    st=(rel.get('subtype') or rel.get('type') or 'rel')
    if rel.get('active')=='#'+pid and rel.get('passive')!='#'+pid:
        st=INV.get(st,'inv-'+st)
    return re.sub(r'[^A-Za-z0-9_\-]+','_',st)
def strip_id(r): return (r or '').lstrip('#') or 'NEEDID'
labels=collections.defaultdict(collections.Counter)
xmlmap={}
for f in glob.glob(R+'/Individuals/**/*.xml',recursive=True):
    root=etree.parse(f).getroot()
    pid=root.get('{http://www.w3.org/XML/1998/namespace}id')
    xmlmap[pid]=root
    for el in root.iter('placeName','persName','orgName','bibl'):
        r=el.get('ref')
        if r and el.text and (el.getparent() is not root or el.get('type')=='nisbah') and re.search('[؀-ۿ]',el.text):
            labels[strip_id(r)][norm(el.text)]+=1
    for rel in root.iter('relation'):
        o=rel.get('active') if rel.get('passive')=='#'+pid else rel.get('passive')
        for d in rel.findall('desc'):
            if d.get(XL)=='ar' and d.text and d.get('type') in (None,'name'): labels[strip_id(o)][norm(d.text)]+=1


def _n(w): 
    return re.sub('[\u064B-\u065F\u0670\u0640]','',w).translate(str.maketrans('أإآٱىة','اااايه'))
MONTHS=[('محرم',1),('المحرم',1),('صفر',2),('ربيع الاول',3),('ربيع الاخر',4),('ربيع الثاني',4),('ربيع الاخره',4),
 ('جمادي الاولي',5),('جمادي الاول',5),('جمادي الاخره',6),('جمادي الثانيه',6),('جمادي الاخر',6),('جمادي الثاني',6),
 ('رجب',7),('شعبان',8),('رمضان',9),('شوال',10),('ذي القعده',11),('ذو القعده',11),('ذي الحجه',12),('ذو الحجه',12)]
MONTHS.sort(key=lambda m:-len(m[0].split()))
def find_months(tokens,lo):
    out=[]
    nt=[_n(t) for t in tokens]
    i=lo
    while i<len(tokens):
        hit=None
        for name,num in MONTHS:
            w=name.split();n=len(w)
            first=nt[i]
            for p in ('','ب','و','ف','وب','فب'):
                if first==p+w[0] and nt[i+1:i+n]==w[1:]:
                    # guard: single-word months that are also common words need a date context
                    if n==1 and name in ('صفر','رجب','شعبان','شوال','رمضان','محرم'):
                        ctx=nt[max(0,i-2):i]+nt[i+1:i+3]
                        if not any(c in ('في','شهر','من','سنه','سنة','منها','عام','مستهل','اول','اواخر','اوايل','اوائل','سلخ','ليله','يوم','ثامن','عشر','عشري','خامس','ثاني','ثالث','رابع','سادس','سابع','تاسع','عاشر') or c.startswith('سن') for c in ctx) and not (i+1<len(nt) and nt[i+1] in ('سنه','منها','من')):
                            continue
                    hit=(i,n,num);break
            if hit:break
        if hit:
            out.append(hit);i+=hit[1]
        else:i+=1
    return out
APPROX=[0];EVT=[0];OFF=[0];OFFZ=[0];OFFL=[];XUL=[];NAME_HIT=collections.Counter();MON=[0];METH_TAG=[0];MAN_HIT=collections.Counter();MAN_MISS=[];REL_PRON=[0];REL_KIN=[0];REL_ANA=[0];REL_ALIAS=[0];REL_LOG=[];ONO_HIT=collections.Counter();ONO_MISS=collections.Counter()
# ---- ID-Master: official names of TMP/wd/gn IDs, plus short forms used in running text
IDM={}
for row in IDROWS:
    if len(row)<5 or not row[4].strip(): continue
    i=row[4].strip()
    i=('gn:'+i) if i.isdigit() else ('wd:'+i) if re.fullmatch(r'Q\d+',i) else i
    IDM.setdefault(i,[]).extend(norm(x) for x in row[2].split('|') if x.strip())

# ---- offices: morphological matching for state labels whose surface form differs from the text
PROCL=('وب','فب','ول','فل','وك','و','ف','ب','ل','ك')
def ostem(w):
    w=re.sub('[أإآ]','ا',w).replace('ى','ي')
    for p in PROCL:
        if w.startswith(p) and len(w)-len(p)>=3 and (w[len(p):].startswith('ال') or p in ('و','ف') or len(w)-len(p)>=4):
            w=w[len(p):];break
    if w.startswith('لل') and len(w)>4: w='ال'+w[2:]
    if w.startswith('ال') and len(w)>4: w=w[2:]
    m=re.match(r'^(.{3,}?)(ت)(ها|هم|هما|هن|ه|ي|نا|كم)$',w)
    if m: w=m.group(1)+'ة'
    else:
        m=re.match(r'^(.{3,}?)(ها|هما|هم|هن|نا|كم)$',w)
        if m: w=m.group(1)
    return w.replace('ة','ه')
OSTOP={'احد','من','في','على','عن','بعض','غير','ذلك','الي','شيء'}
def fuzzy_office(tokens,body,forms,free):
    for f in forms:
        fw=f.split()
        if not fw: continue
        hs=ostem(fw[0])
        if len(hs)<3 or hs in OSTOP: continue
        for i in range(body,len(tokens)):
            t=tokens[i]
            if t.startswith('@') or ostem(t)!=hs or not free(i,1): continue
            n=1
            while n<len(fw) and i+n<len(tokens) and free(i+n,1) and ostem(tokens[i+n])==ostem(fw[n]): n+=1
            p=0
            core=re.sub('[أإآ]','ا',t)
            for q in PROCL:
                if t.startswith(q) and ostem(t[len(q):])==hs: p=len(q);break
            return i,p,n
    return None

# ---- event triggers: one head word per event, chosen by rules (type/subtype + English summary keywords)
TRIG_TYPE={
 'hajj':['حج','الحج','حاجا'],'jāwara':['جاور','مجاورا','المجاوره','وجاور'],
 'mention':['ذكره','ترجمه','ارخه','قال','اثني','وصفه','حكي','افادنيه','بيض','ذكر','ترجم','نقل','كتب'],
 'funeral':['دفن','صلي'],'burial':['دفن'],'witness':['شهد','شاهد'],'meeting':['لقيه','لقيته','اجتمع','رايته','لقي'],
 'ijaza':['اجاز','اجازه','استجاز'],'isnad':['حدث','روي'],
 'travel':['رحل','سافر','ارتحل','توجه','دخل','قدم','رجع','عاد','التنقل','تنقل','يتردد','تردد'],'visit':['زار','دخل','قدم','زياره'],
 'residence':['سكن','قطن','استوطن','نزل','اقام','نزيل','تحول','انتقل'],
 'learning':['اخذ','قرا','سمع','تفقه','اشتغل','لازم','عرض','حفظ','تلا','بحث','تدرب'],'study':['اخذ','قرا','سمع','تفقه','اشتغل','لازم','عرض','حفظ','تلا','بحث'],
 'teaching':['درس','اقرا','حدث','تصدر','افتي','تصدي','اسمع','افاد'],
 'political':['ولي','تامر','استقر','عزل','سجن','قتل','نفي','امسك','اعتقل','قبض','صودر','اخرج','جهز','خرج','تسلطن','حبس'],
 'religious':['حج','جاور','زار','تصوف','تعبد'],
 'legacy':['خلف','ترك','وقف'],'economic':['تكسب','اتجر','تاجر'],
}
TRIG_EN=[('memoriz',['حفظ']),('recit',['قرا','تلا']),('heard',['سمع']),('listened',['سمع']),('read',['قرا']),('studied',['قرا','اشتغل','تفقه','اخذ']),
 ('married',['تزوج','زوج','زوجه']),('pilgrim',['حج']),('hajj',['حج']),('travel',['رحل','سافر']),('settled',['سكن','قطن','استوطن','نزل']),
 ('killed',['قتل']),('imprisoned',['سجن','حبس']),('executed',['قتل','وسط']),('appointed',['ولي','استقر']),('dismissed',['عزل','صرف']),
 ('composed',['صنف','نظم','الف','عمل']),('wrote',['كتب','صنف']),('copied',['كتب','نسخ']),('poem',['نظم','انشد','قال']),('poetry',['نظم','قال']),
 ('mentioned',['ذكره','ذكر']),('recorded',['ارخه','ذكره']),('granted',['اجاز','اعطي','انعم']),('battle',['واقعه','قتال','حارب']),('campaign',['تجريده','سافر','خرج']),
 ('plague',['طاعون','الطاعون']),('commentary',['شرح']),('transmitted',['حدث','روي']),('taught',['درس','اقرا']),('teach',['درس','اقرا']),('engaged',['اشتغل','تعاني']),
 ('excelled',['برع','مهر']),('inherit',['ورث']),('property',['اخذ','صودر']),('seized',['امسك','قبض','اخذ']),('became',['صار','ولي','استقر']),('went',['توجه','سافر','دخل','رجع']),
 ('tailor',['الخياطه','خياطا']),('accountant',['حاسبا']),('trade',['تكسب','اتجر']),('merchant',['تاجر','اتجر']),('built',['انشا','بني','عمر']),('endow',['وقف'])]
def _tn(w):
    w=re.sub('[أإآ]','ا',w).replace('ى','ي').replace('ة','ه')
    return re.sub('[\u064B-\u0652]','',w)
def trig_match(tok,lemma):
    t=_tn(tok)
    for p in ('','و','ف','ثم'):
        if t.startswith(p) and t[len(p):].startswith(lemma) and len(t)-len(p)-len(lemma)<=3: return True
    return False
def event_triggers(tokens,body,events,covered_ok):
    out={};last=body;used=set()
    for j,ev in enumerate(events):
        lem=list(TRIG_TYPE.get(ev.get('subtype') or '',[]))
        en=' '.join(d.get('text','') for d in ev.get('descs') or [] if d.get('lang')=='en').lower()
        for k,v in TRIG_EN:
            if k in en: lem+= [x for x in v if x not in lem]
        lem+= [x for x in TRIG_TYPE.get(ev.get('type') or '',[]) if x not in lem]
        if not lem: continue
        hit=None
        for rng in (range(last,len(tokens)),range(body,last)):
            for lemma in lem:
                for i in rng:
                    if i in used or tokens[i].startswith('@') or not covered_ok(i): continue
                    if trig_match(tokens[i],lemma): hit=i;break
                if hit is not None: break
            if hit is not None: break
        if hit is not None:
            out[j]=hit;used.add(hit);last=hit
    return out
def short_forms(full):
    w=full.split();out={full}
    if 'بن' in w:
        last=len(w)-1-w[::-1].index('بن')
        fam=w[last+1:last+2]
        tail=[x for x in w[last+2:]]
        if fam:
            out.add('ابن '+fam[0])
            for t in tail[:2]:
                if t.startswith('ال'): out.add(t+' بن '+fam[0])
            ism=' '.join(w[:2]) if w[0] in ('عبد','أبو','أبي') else w[0]
            if w[0]!='ابن': out.add(ism+' بن '+fam[0])
        ism=' '.join(w[:2]) if w[0] in ('عبد','أبو','أبي') else w[0]
        lastnis=[x for x in w[1:] if x.startswith('ال') and x not in ('الله','الرحمن','الدين')]
        if lastnis: out.add(ism+' '+lastnis[-1])
    return out
for i,names in IDM.items():
    if not i.startswith(('TMP-P-','AIND','wd:')): continue
    for n in names:
        for f in short_forms(n): labels[i][f]+=0
for e in entries:
    if e['k'].startswith('AIND') and e['m']!='R':
        n0=re.sub(r'@\S+ ','',e['t']); n0=re.sub(r'^\d+ ','',n0).split(' . ')[0]
        n0=' '.join(n0.split()[:14])
        for f in short_forms(norm(n0)): labels[e['k']][f]+=0
for i in list(labels):
    for a in list(labels[i]):
        for f in short_forms(a): labels[i][f]+=0
MANUAL=collections.defaultdict(list)
for p in json.load(open(os.path.join(HERE,'manual_placements.json'),encoding='utf-8')): MANUAL[p['k']].append(p)
# ---- learning methods: XML desc type=method -> slug, and the verb forms that signal it in the text
METH={'سمع':'samac','حضر':'hudur','قرا':'qiraa','عرض':'ard','اجاز':'ijaza','اخذ':'akhdh','لازم':'mulazama','تفقه':'tafaqquh','جود':'tajwid','تلا':'tilawa','حدث':'tahdith','كتب':'kitaba','لبس':'libs','صحب':'suhba','اشتغل':'ishtighal','درس':'dars','تخرج':'takharruj','بحث':'bahth','روي':'riwaya','استجاز':'ijaza'}
FORMS={'samac':('سمع','وسمع','فسمع','اسمع','واسمع','سماع','بسماع'),'hudur':('حضر','وحضر','فحضر','احضر','واحضر','بحضور'),'qiraa':('قرا','وقرا','فقرا','قراءه','بقراءه','وقراءه'),
 'ard':('عرض','وعرض','فعرض'),'ijaza':('اجاز','واجاز','اجزت','واجزت','استجاز','واستجاز','بالاجازه','اجازه'),'akhdh':('اخذ','واخذ','فاخذ'),'mulazama':('لازم','ولازم','ملازمه'),
 'tafaqquh':('تفقه','وتفقه'),'tajwid':('جود','وجود'),'tilawa':('تلا','وتلا'),'tahdith':('حدث','وحدث','حدثته','وحدثته'),'kitaba':('كتب','وكتب'),'libs':('لبس','ولبس','البس'),
 'suhba':('صحب','وصحب'),'ishtighal':('اشتغل','واشتغل'),'dars':('درس','ودرس'),'takharruj':('تخرج','وتخرج'),'bahth':('بحث','وبحث'),'riwaya':('روي','وروي','روى')}
def meth_slug(desc_text, ref):
    v=_n(desc_text.split('|')[0].strip())
    for k,sl in METH.items():
        if v.startswith(k): return sl
    m=re.search(r'(\d+)$',ref or '')
    return 'm'+(m.group(1).lstrip('0') if m else 'x')
MADH={'الشافعي':'wd:Q82245','الحنفي':'wd:Q228986','المالكي':'wd:Q48221','الحنبلي':'wd:Q233387'}
def tag(root,tokens):
    global RELS
    RELS=[];OFFL.clear();XUL.clear()
    pid=root.get('{http://www.w3.org/XML/1998/namespace}id')
    ins={}
    try: body=tokens.index('.')+1
    except ValueError: body=0
    def ah(el):
        m=re.match(r'(\d{3,4})',(el.get('when-custom') or '') if el is not None else '')
        return int(m.group(1)) if m else None
    yb,yd=ah(root.find('birth')),ah(root.find('death'))
    oth=[ah(e) for e in root.iter('event','state','date') if ah(e)]
    anchor=yb or yd or (min(oth) if oth else None)
    _mends={i+n for i,n,_ in find_months(tokens,0)}
    for i,y in year_phrases(tokens,anchor,{yb,yd,*oth},_mends):
        ins.setdefault(i,[]).append(('@YB' if y==yb else '@YD' if y==yd else '@YY')+str(y))
    covered=set()
    def free(i,n): return not any(k in covered for k in range(i,i+n))
    # approximate years: "سنة بضع وعشرين (وثمانمائة)" -> @YD823-829[n]
    known=[y for y in (yd,yb,*oth) if y]
    for i in range(len(tokens)-2):
        if tokens[i]!='سنة' or tokens[i+1] not in ('بضع','بضعة') or i in ins: continue
        t2=tokens[i+2]; t2=t2[1:] if t2[:1]=='و' and t2[1:] in TENS else t2
        if t2 not in TENS: continue
        tens=TENS[t2]; n=3; cent=None
        if i+3<len(tokens):
            h=tokens[i+3]; h=h[1:] if h[:1]=='و' else h
            if h in HUND: cent=HUND[h]; n=4
        match=[y for y in known if (y%100)//10*10==tens] if tens>=20 else [y for y in known if 10<=y%100<20]
        if cent is None: cent=(match[0]//100*100) if match else ((anchor//100*100) if anchor else 800)
        lo,hi=cent+tens+1,cent+tens+9
        y0=match[0] if match else None
        back=[_n(w) for w in tokens[max(0,i-4):i]]
        kind='@YD' if (y0 and y0==yd) or any(w in ('مات','ومات','توفي','وتوفي','فمات') for w in back) else '@YB' if (y0 and y0==yb) or any(w in ('ولد','وولد','مولده','ومولده') for w in back) else '@YY'
        ins.setdefault(i,[]).append(f'{kind}{lo}-{hi}[{n}]'); APPROX[0]+=1
    def put(name,ref,code,lo=None,hi=None,typ=None):
        if not name: return False
        n=len(name.split())
        h=find_span(tokens,name,body if lo is None else lo)
        while h and not free(h[0],n):
            h=find_span(tokens,name,h[0]+1)
        if not h: return False
        i,p=h
        if hi is not None and i+n>hi: return False
        covered.update(range(i,i+n))
        idv=strip_id(ref) if ref else None
        if typ and code=='S': br=typ+(':'+idv if idv and idv!='NEEDID' else '')
        elif typ and code=='O' and not idv: br=typ
        elif typ: br=typ+':'+(idv or 'NEEDID')
        else: br=idv
        ins.setdefault(i,[]).append(f'@{code}{p}{n}[{br}]')
        return True
    # where does the subject's own name end?  prefer the XML full name; fall back to first ' . '
    start=1 if tokens and tokens[0].isdigit() else 0
    hdr_end=body-1 if body else len(tokens)
    ono=[]
    for pn in root.findall('persName'):
        t=pn.get('type')
        if t in ('nisbah','laqab','kunyah','shuhrah','honorific') and pn.text:
            ono.append((norm(pn.text),pn.get('ref'),t))
    ono.sort(key=lambda x:-len(x[0].split()))   # longest first: shuhrah 'ابن الديري' before nisbah
    for name,ref,t in ono:
        ok_=put(name,ref,'S',start,hdr_end,t)
        if not ok_: ONO_MISS[t]+=1
        else: ONO_HIT[t]+=1
        XUL.append({'k':'S','typ':t,'id':strip_id(ref) if ref else '','lab':name,**({'ok':1} if ok_ else {})})
    for k in range(start,hdr_end):
        w=tokens[k]; base=w[1:] if w.startswith('و') and w[1:] in MADH else w
        if base in MADH and free(k,1):
            covered.add(k); ins.setdefault(k,[]).append(f'@S{len(w)-len(base)}1[madhhab:{MADH[base]}]'); NAME_HIT['madhhab']+=1
    # end of the subject's own name: XML full name if it matches verbatim; otherwise the furthest
    # onomastic element found in the header (or the plain name_only), never the whole entry
    fn=root.find("persName[@type='full']"); no=root.find("persName[@type='name_only']")
    fw=norm(fn.text or '').split() if fn is not None else []
    nw=norm(no.text or '').split() if no is not None else []
    if fw and tokens[start:start+len(fw)]==fw:
        name_end=start+len(fw)
    else:
        ends=[k+1 for k in covered if k<hdr_end]
        name_end=max(ends+[start+(len(nw) if nw and tokens[start:start+len(nw)]==nw else 1)])
    body=name_end
    # ---- ism and nasab chain of the subject's own name (rule-based, as EIS1600 ISM/NAS)
    kin={}
    for rel in root.iter('relation'):
        if rel.get('passive')=='#'+pid and rel.get('subtype') in ('father','grandfather'):
            oid=strip_id(rel.get('active'))
            nm=[norm(x.text) for x in rel.findall('desc') if x.get(XL)=='ar' and x.get('type') in (None,'name') and x.text]
            kin.setdefault(rel.get('subtype'),(oid,nm+list(labels.get(oid,{}))))
    def kin_ok(sub,elem):
        if sub not in kin: return None
        oid,names=kin[sub]
        if not names: return oid if sub=='father' else None
        K=lambda w:{'ابي':'ابو','ابا':'ابو'}.get(_n(w),_n(w))
        STOPK={'الدين','بن','ابن','ابو','عبد','الشيخ','الخواجا','السيد'}
        ew=[K(y) for y in elem]
        key=' '.join(ew[:2]) if ew and ew[0] in STOPK else (ew[0] if ew else '')
        if not key: return None
        for x in names:
            xw=[K(y) for y in x.split()[:6]]
            if ' ' in key:
                if any(' '.join(xw[i:i+2])==key for i in range(len(xw)-1)): return oid
            elif key not in STOPK and key in xw: return oid
        return None
    STOPW={'شقيق','شقيقة','الذي','التي','قبله','قبلها','بعده','زوج','زوجة','أم','قريب','صهر','حفيد','أخي','اخي','أخت','اخت','عم','عمه','خال','أخيه','اخيه','ثم','الأصل','الاصل','المولد','ويعرف','يعرف','المعروف','وهو','ولد','مات','سبط','أخو','اخو','نزيل','الشهير','ابن','أحد','احد','كان','الآتي','الاتي','الماضي','ويقال','ويدعى','والد','ولقبه','لقبه','مولى','عتيق'}
    lim=max(hdr_end,name_end)
    j=start
    if j<len(tokens) and free(j,1) and tokens[j] not in ('بن','ابن','بنت','ابنة') and re.match('^[\u0621-\u064A]+$',tokens[j]):
        # ism: one token, or two for عبد X / أبو X
        n=2 if tokens[j] in ('عبد','أبو','ابو') and j+1<len(tokens) and free(j+1,1) else 1
        covered.update(range(j,j+n)); ins.setdefault(j,[]).append(f'@S0{n}[ism]'); NAME_HIT['ism']+=1
        j+=n
    order=0
    while j<lim:
        if tokens[j] in ('بن','ابن','بنت','ابنة') and free(j,1):
            k=j+1
            while k<lim and k-j-1<4 and free(k,1) and tokens[k] not in ('بن','ابن','بنت','ابنة','.','،',',','؛') and tokens[k] not in STOPW and re.match('^[\u0621-\u064A]+$',tokens[k]):
                k+=1
            n=k-(j+1)
            if n==0: break
            order+=1
            rid=kin_ok('father',tokens[j+1:k]) if order==1 else kin_ok('grandfather',tokens[j+1:k]) if order==2 else None
            br='nasab'+(':'+rid if rid and rid!='NEEDID' else '')
            covered.update(range(j,k)); ins.setdefault(j+1,[]).append(f'@S0{n}[{br}]'); NAME_HIT['nasab']+=1
            if rid: NAME_HIT['nasab_linked']+=1
            j=k
        elif not free(j,1):
            if any('[nisbah' in t or '[madhhab' in t for t in ins.get(j,[])): break   # the nasab ends where the nisbas begin
            j+=1
        else: break
    for i,n,num in find_months(tokens,body):
        if free(i,n):
            covered.update(range(i,i+n)); ins.setdefault(i,[]).append(f'@L{n}X{num:02d}L'); MON[0]+=1
    seen=set()
    for pn in root.iter('placeName'):
        n=norm(pn.text or '')
        if n and n not in seen and re.search('[\u0600-\u06FF]',n):
            seen.add(n); ok_=put(n,pn.get('ref'),'T')
            XUL.append({'k':'T','id':strip_id(pn.get('ref')) if pn.get('ref') else '','lab':n,**({'ok':1} if ok_ else {})})
    for st in root.iter('state'):
        tp=st.get('type') or 'office'; ref=st.get('ref')
        typ=('office/deputy' if st.get('subtype')=='deputy' else 'office') if tp=='office' else tp
        labs=[norm(re.sub(r'\s*\(.*?\)','',lb.text)) for lb in st.findall('label') if lb.get(XL)=='ar' and lb.text]
        labs=[x for x in labs if x]
        idv=strip_id(ref) if ref else None
        rec={'id':idv or '','typ':typ,'lab':labs[0] if labs else ''}
        if any(put(n,ref,'O',typ=typ) for n in labs): OFF[0]+=1; rec['ok']=1
        else:
            forms=labs+[f for f in OFF_FORMS.get(idv,[]) if f not in labs]
            h=fuzzy_office(tokens,body,forms,free)
            if h:
                i,p,n=h; covered.update(range(i,i+n))
                br=typ+(':'+idv if idv else ('' if typ=='status' else ':NEEDID'))
                ins.setdefault(i,[]).append(f'@O{p}{n}[{br}]'); rec['ok']='fz'; OFFZ[0]+=1
        if labs: OFFL.append(rec)
    seen=set()
    for pn in root.iter('persName'):
        par=pn.getparent()
        if par is root or par.tag=='respStmt': continue
        n=norm(pn.text or '')
        ev=next(pn.iterancestors('event'),None)
        role=re.sub(r'[^A-Za-z0-9_\-]+','_',(ev.get('subtype') or ev.get('type'))) if ev is not None else None
        if n not in seen:
            seen.add(n); ok=put(n,pn.get('ref'),'P',typ=role)
            RELS.append({'o':strip_id(pn.get('ref')) if pn.get('ref') else 'NEEDID','role':role or 'person','src':'event','txt':n,'ok':bool(ok)})
    ROLES=collections.defaultdict(list);ROLECOUNT=collections.Counter(role_of(r_,pid) for r_ in root.iter('relation'))
    for rel in root.iter('relation'):
        o=rel.get('active') if rel.get('passive')=='#'+pid else rel.get('passive')
        oid=strip_id(o); r_=role_of(rel,pid)
        if oid!='NEEDID' and r_ not in ROLES[oid]: ROLES[oid].append(r_)
    # manual placements (read by hand) take precedence over every automatic rule
    MANPLACED=set();MANNONE={}
    for p in MANUAL.get(pid,[]):
        rels_=[r_ for r_ in root.iter('relation') if strip_id(r_.get('active') if r_.get('passive')=='#'+pid else r_.get('passive'))==p['o']]
        if not rels_: MAN_MISS.append((pid,p['o'],'no such relation')); continue
        if p.get('none'): MANNONE[p['o']]=p.get('why',''); MAN_HIT['none']+=1; continue
        role='+'.join(ROLES[p['o']]) or role_of(rels_[0],pid); n=len(p['phrase'].split()); k=start; hit=None
        while True:
            h=find_span(tokens,p['phrase'],k)
            if not h: break
            if (not p.get('after') or _n(tokens[h[0]-1]).endswith(_n(p['after']))) and free(h[0],n): hit=h;break
            k=h[0]+1
        if not hit: MAN_MISS.append((pid,p['o'],'phrase not found')); continue
        covered.update(range(hit[0],hit[0]+n)); ins.setdefault(hit[0],[]).append(f"@P{hit[1]}{n}[{role}:{p['o']}]")
        MANPLACED.add(p['o']); MAN_HIT['placed']+=1
    for rel in root.iter('relation'):
        o=rel.get('active') if rel.get('passive')=='#'+pid else rel.get('passive')
        done=False; role=role_of(rel,pid)
        if strip_id(o)!='NEEDID': role='+'.join(ROLES[strip_id(o)])
        if strip_id(o) in MANPLACED:
            RELS.append({'o':strip_id(o),'role':role,'st':rel.get('subtype'),'src':'relation','ok':True,'man':True}); continue
        if strip_id(o) in MANNONE:
            RELS.append({'o':strip_id(o),'role':role,'st':rel.get('subtype'),'src':'relation','ok':False,'nm':True,'why':MANNONE[strip_id(o)]}); continue
        for d in rel.findall('desc'):
            n=trim_desc(norm(d.text or ''))
            if n and d.get(XL)=='ar' and d.get('type') in (None,'name') and n not in seen:
                seen.add(n); done=any(put(v,o,'P',lo=start,typ=role) for v in kun_variants(n)) or done
        oid=strip_id(o)
        meth=[x.text for x in rel.findall('desc') if x.get('type')=='method' and x.text]
        nm=[norm(x.text) for x in rel.findall('desc') if x.get(XL)=='ar' and x.get('type') in (None,'name') and x.text]
        RELS.append({'o':oid,'role':role,'st':rel.get('subtype'),'src':'relation','m':meth[0] if meth else None,'c':rel.get('cert'),'txt':nm[0] if nm else None})
        if not done and oid not in ('NEEDID','wd:Q4120128') and oid!=pid and ('['+oid+']') not in ' '.join(sum(ins.values(),[])):
            for a in sorted({trim_desc(x) for x in labels.get(oid,{})}-{''},key=lambda x:-len(x.split())):
                if not usable_alias(a,oid): continue
                if any(put(v,o,'P',lo=start,typ=role) for v in kun_variants(a)):
                    REL_ALIAS[0]+=1; REL_LOG.append((pid,oid,rel.get('subtype'),a)); done=True; break
        if not done and role.split('+')[0]=='patron':
            for a in labels.get(oid,{}):
                w=a.split()
                if len(w)==2 and w[0].startswith('ال'):
                    stem=_n(w[0])
                    for k in range(1,len(tokens)):
                        if _n(tokens[k])==_n(w[1]) and _n(tokens[k-1]).startswith(stem) and free(k,1):
                            covered.add(k); ins.setdefault(k,[]).append(f'@P01[{role}:{oid}]'); done=True; break
                if done: break
        # first person (al-Sakhawi himself) and anaphoric kin words, only for this relation's role
        if not done and oid=='wd:Q4120128':
            for k in range(body,len(tokens)):
                w=tokens[k]; prev=tokens[k-1] if k else ''
                if (w in ('مني','عني','عندي','بقراءتي','لي','لنا','وعني','ومني','حدثته','وحدثته','حضرني','وحضرني','لازمني','ولازمني','لقيني','ولقيني','بحضرتي') or ((w in ('علي','وعلي') or (w=='على' and k+1<len(tokens) and tokens[k+1] in ('وأنا','وانا'))) and _n(prev) in ('قرا','وقرا','فقرا','عرض','وعرض','فعرض','فعرضها','وعرضها','عرضها','عرضه','وعرضه','سمع','وسمع','فسمع','حضر','وحضر','قراه','وقراه'))) and free(k,1):
                    covered.add(k); ins.setdefault(k,[]).append(f'@P01[{role}:{oid}]'); done=True; REL_PRON[0]+=1; break
        # kin list: "وأخواه محمد وإسماعيل" — a kin word followed by bare isms; match each partner by his ism
        if not done and oid not in ('NEEDID','wd:Q4120128'):
            base=role.split('+')[0]
            KW={'brother':('اخواه','اخوه','اخويه','اخوته','اخوانه','اخوه'),'sister':('اختاه','اخواته','اخته'),
                'son':('اولاده','بنوه','ابناه','ابنيه','ولداه','ولديه','ابنه','ولده'),'daughter':('بناته','ابنتاه','بنتاه','ابنته')}.get(base)
            names=[x for x in nm]+[x for x in labels.get(oid,{})]
            isms=set()
            for x in names:
                w=x.split()
                if not w: continue
                isms.add(' '.join(w[:2]) if w[0] in ('عبد','أبو','ابو') and len(w)>1 else w[0])
            if KW and isms:
                for k in range(body,len(tokens)):
                    t0=_n(tokens[k]); t0=t0[1:] if t0[:1] in ('و','ف') and t0[1:] in KW else t0
                    if t0 not in KW: continue
                    for j in range(k+1,min(k+9,len(tokens))):
                        if tokens[j] in ('.',':'): break
                        for ism in isms:
                            iw=ism.split(); n_=len(iw)
                            seg=tokens[j:j+n_]
                            if len(seg)<n_: continue
                            first=seg[0]; p=0
                            if _n(first)!=_n(iw[0]) and first[:1]=='و' and _n(first[1:])==_n(iw[0]): p=1
                            elif _n(first)!=_n(iw[0]): continue
                            if any(_n(a)!=_n(b) for a,b in zip(seg[1:],iw[1:])): continue
                            if not free(j,n_): continue
                            covered.update(range(j,j+n_)); ins.setdefault(j,[]).append(f'@P{p}{n_}[{role}:{oid}]'); done=True; REL_KIN[0]+=1; break
                        if done: break
                    if done: break
        if not done and oid not in ('NEEDID','wd:Q4120128') and ROLECOUNT[role.split('+')[0]]==1:
            base=role.split('+')[0]
            ANA={'father':('أبوه','أبيه','أباه','والده','أبوهما','أبوهم','أبيهما'),'son':('ابنه','ولده','ابنيه','أولاده','بنيه','ولديه','والد'),'brother':('أخو','أخوه','أخيه','أخا','وأخو','شقيق'),
                 'sister':('أخت','أخته','شقيقة'),'grandfather':('جده','جد'),'mother':('أمه','والدته','أم'),'spouse':('زوجته','زوجها','زوج','زوجة'),'uncle':('عمه','عم'),'paternal_uncle':('عمه','عم'),
                 'maternal_uncle':('خاله','خال'),'daughter':('ابنته','بنته'),'grandson':('حفيد','سبط'),'cousin':('ابن عمه','ابن عم'),'siblings_child':('ابن أخي','ابن أخيه','ابن أخت')}.get(base,())
            for a in (('الذي قبله','التي قبلها','الذي بعده','التي بعدها') if base in ('brother','sister','son','father','daughter','mother') else ())+ANA:
                if put(a,o,'P',typ=role): done=True; REL_ANA[0]+=1; break
        RELS[-1]['ok']=bool(done)
    # ---- method of each teacher-type tag, read from the verb just before it (سمع / حضر / ...)
    pm=collections.defaultdict(list)
    for r_ in root.iter('relation'):
        o_=strip_id(r_.get('active') if r_.get('passive')=='#'+pid else r_.get('passive'))
        for d_ in r_.findall('desc'):
            if d_.get('type')=='method' and d_.text:
                sl=meth_slug(d_.text,d_.get('ref'))
                if sl not in pm[o_]: pm[o_].append(sl)
    pos=collections.defaultdict(list)
    for i_,tl in ins.items():
        for j_,tg in enumerate(tl):
            m_=re.match(r'@P(\d)(\d+)\[([^\]]+)\]$',tg)
            if not m_: continue
            br=m_.group(3); mm_=re.match(r'^([A-Za-z0-9_+\-]+):(.+)$',br)
            if mm_ and mm_.group(1) not in ('wd','gn'): pos[mm_.group(2)].append((i_,j_,mm_.group(1)))
    for o_,sls in pm.items():
        if o_ not in pos: continue
        hits={}
        for (i_,j_,rl) in pos[o_]:
            win=[_n(t_) for t_ in tokens[max(0,i_-5):i_+1]]
            hits[(i_,j_)]=[sl for sl in sls if any(any(w.startswith(f) for f in FORMS.get(sl,())) for w in win)]
        for (i_,j_,rl) in pos[o_]:
            got=hits[(i_,j_)]
            if not got and len(pos[o_])==1: got=sls          # a single mention carries all its methods
            if not got: continue
            tg=ins[i_][j_]
            ins[i_][j_]=tg.replace('['+rl+':','['+rl+'/'+'.'.join(got)+':',1)
            METH_TAG[0]+=1
    EVL=[]
    evs_x=REC_EVENTS.get(pid,[])
    if evs_x:
        tr_=event_triggers(tokens,body,evs_x,lambda i:i not in covered)
        for j,ev in enumerate(evs_x):
            if j in tr_:
                ins.setdefault(tr_[j],[]).append(f"@E01[{re.sub(r'[^A-Za-z0-9_]+','_',(ev.get('subtype') or ev.get('type') or 'event').replace('ā','a'))}:e{j+1}]"); EVT[0]+=1
    for kind,y in (('YD',yd),('YB',yb)):
        if not y: continue
        hit=any(re.match(r'@'+kind+r'(\d+)(?:-(\d+))?',t) and (lambda m:int(m.group(1))<=y<=int(m.group(2) or m.group(1)) or (m.group(2) is not None and int(m.group(1))//10==y//10))(re.match(r'@'+kind+r'(\d+)(?:-(\d+))?',t)) for v in ins.values() for t in v)
        XUL.append({'k':'Y','typ':kind,'id':'','lab':str(y),**({'ok':1} if hit else {})})
    out=[]
    for i,t in enumerate(tokens): out+=ins.get(i,[]); out.append(t)
    return ' '.join(out), sum(len(v) for v in ins.values())

REC_EVENTS={k:v.get('events') or [] for k,v in json.load(open(os.path.join(WORK,'records_tei.json'))).items()}
OFF_FORMS=collections.defaultdict(list)
for _r in xmlmap.values():
    for st in _r.iter('state'):
        r=strip_id(st.get('ref')) if st.get('ref') else None
        if not r: continue
        for lb in st.findall('label'):
            if lb.get(XL)=='ar' and lb.text:
                f=norm(re.sub(r'\s*\(.*?\)','',lb.text))
                if f and f not in OFF_FORMS[r]: OFF_FORMS[r].append(f)
for row in IDROWS:
    if len(row)>4 and row[1]=='Office' and row[4].strip():
        i=row[4].strip(); i=('wd:'+i) if re.fullmatch(r'Q\d+',i) else i
        for f in row[2].split('|'):
            f=norm(re.sub(r'\s*\(.*?\)','',f))
            if f and f not in OFF_FORMS[i]: OFF_FORMS[i].append(f)
ntag=0;nx=0
for e in entries:
    root=xmlmap.get(e['k'])
    e['x']=1 if root is not None else 0
    if root is not None:
        nx+=1
        e['t'],n=tag(root,e['t'].split(' ')); ntag+=n
        if OFFL: e['o']=[dict(x) for x in OFFL]
        if XUL: e['u']=[dict(x) for x in XUL]
        if RELS: e['r']=[{k:v for k,v in r.items() if v not in (None,'')} for r in RELS]
        trs={n.get('{http://www.w3.org/XML/1998/namespace}lang'):norm(n.text or '') for n in root.findall("note[@type='translation']") if n.text}
        if trs: e['tr']=trs
    # display name = text up to first ' . '
    t=re.sub(r'@\S+ ','',e['t'])
    e['n']=re.sub(r'^\d+ ','',t.split(' . ')[0])[:120]
print('events',EVT[0],'offices',OFF[0],'fuzzy',OFFZ[0],'approx',APPROX[0],'name',dict(NAME_HIT),'kin',REL_KIN[0],'pron',REL_PRON[0],'anaphora',REL_ANA[0]);print('with xml',nx,'tags',ntag,'months',MON[0],'relation tags via aliases',REL_ALIAS[0])
for t in ONO_HIT|ONO_MISS: print(' ',t,'hit',ONO_HIT[t],'miss',ONO_MISS[t])

lab={}
for k,c in labels.items(): lab[k]=c.most_common(1)[0][0]
for row in csv.DictReader(open(R+'/docs/authority/wd_entities.tsv'),delimiter='\t'):
    if row['status']=='ok':
        k='wd:'+row['qid']; parts=[lab.get(k),row['label_ar'],row['label_en']]
        lab[k]=' / '.join(dict.fromkeys(x for x in parts if x))
for row in csv.DictReader(open(R+'/docs/authority/gn_entities.tsv'),delimiter='\t'):
    if row['status']=='ok':
        ar=(row['name_ar'] or '').split(' | ')[0]
        k='gn:'+row['gnid']; lab[k]=' / '.join(dict.fromkeys(x for x in (lab.get(k),ar,row['name']) if x))
for e in entries:
    lab.pop(e['k'],None)   # AIND names come from the entries themselves
lab.pop('NEEDID',None)
TR={e['k']:e.pop('tr') for e in entries if 'tr' in e}
json.dump(TR,open('tr.json','w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
with open('dau.json','w',encoding='utf-8') as f:
    f.write('[\n'+',\n'.join(json.dumps(e,ensure_ascii=False,separators=(',',':')) for e in entries)+'\n]\n')
json.dump(lab,open('labels.json','w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
IDMJ={}
for row in IDROWS:
    if len(row)<5 or not row[4].strip() or row[4].strip()=='ID': continue
    i=row[4].strip(); i=('gn:'+i) if i.isdigit() else ('wd:'+i) if re.fullmatch(r'Q\d+',i) else i
    if i in IDMJ: continue
    note=re.sub(r'\s+',' ',row[5] if len(row)>5 else '')
    m=re.search(r'(所在地|役職|人物|内容)[:：]\s*([^。]{0,60})',note)
    IDMJ[i]={'ar':row[2].strip(),'lat':row[3].strip(),'cat':row[1].strip(),'d':(m.group(2) if m else note[:60]).strip(),**({'x':1} if len(row)>8 and row[8].strip()=='retired' else {})}
json.dump(IDMJ,open('idm.json','w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
print('idm.json',len(IDMJ))
print('labels',len(lab),'method-qualified tags',METH_TAG[0]);print('manual',dict(MAN_HIT),MAN_MISS)
json.dump(REL_LOG,open('/tmp/rel_log.json','w'),ensure_ascii=False)

OFFS={}
for row in IDROWS:
    if len(row)<9 or row[1]!='Office' or not row[4].strip(): continue
    i=row[4].strip(); i=('wd:'+i) if re.fullmatch(r'Q\d+',i) else i
    OFFS[i]={'ar':row[2].strip(),'lat':row[3].strip(),'cls':row[7].strip(),'st':row[8].strip(),'note':row[5].strip()[:120]}
FORMS_O=collections.defaultdict(collections.Counter)
for root in xmlmap.values():
    for st in root.iter('state'):
        r=(st.get('ref') or '').lstrip('#')
        if not r: continue
        for lb in st.findall('label'):
            if lb.get(XL)=='ar' and lb.text: FORMS_O[r][norm(re.sub(r'\s*\(.*?\)','',lb.text))]+=1
for i,c in FORMS_O.items():
    if i in OFFS: OFFS[i]['f']=[x for x,_ in c.most_common(8) if x and x!=OFFS[i]['ar']]
json.dump(OFFS,open('offices.json','w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
print('offices.json',len(OFFS))
