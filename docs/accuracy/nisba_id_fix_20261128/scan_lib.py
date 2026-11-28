import csv, re, glob, sys, json, collections
import xml.etree.ElementTree as ET
REPO=sys.argv[1] if len(sys.argv)>1 else "."
DIAC=re.compile('[ً-ٰٟـۖ-ۭ]')
def norm(s, strip_al=True):
    s=DIAC.sub('',s or '').strip()
    s=re.sub('[أإآٱ]','ا',s).replace('ى','ي').replace('ة','ه')
    s=re.sub(r'\s+',' ',s)
    # leading و ب ل ف before ال
    s=re.sub(r'^[وبلف](?=ال)','',s)
    if strip_al: s=re.sub(r'^ال','',s)
    s=s.replace(' ','')
    s=re.sub(r'يه$','ي',s)   # feminine
    return s
reg={}
for r in csv.DictReader(open(f'{REPO}/authority/entities_registry.tsv',encoding='utf-8'),delimiter='\t'):
    if r['id'].startswith('TMP-N-'): reg[r['id']]=r
def reg_forms(r):
    forms=[r['label_ar']]+[v for v in re.split(r'[|;،]',r.get('variants') or '') if v.strip()]
    return forms
# index normalized -> ids (active)
idx=collections.defaultdict(set)
for i,r in reg.items():
    for f in reg_forms(r):
        f2=re.sub(r'\s*\(.*?\)\s*','',f)
        idx[norm(f2)].add(i)
occ=[]  # (word, ref, D, fullname)
noref=[]
for fp in glob.glob(f'{REPO}/Individuals/*/*.xml'):
    t=ET.parse(fp).getroot()
    D=t.get('{http://www.w3.org/XML/1998/namespace}id')
    full=''
    # （2026-11-28 校閲で補った。元のファイルはここで切れていた）
    for el in t.iter('persName'):
        if el.get('type')=='full': full=el.text or ''
    for el in t.iter('persName'):
        if el.get('type')!='nisbah': continue
        r=el.get('ref')
        if r: occ.append((el.text or '', r.lstrip('#'), D, full))
        else: noref.append((el.text or '', D, full))
if __name__=='__main__':
    mis=[(w,i,D) for w,i,D,_ in occ if i in reg and norm(w) not in {norm(re.sub(r'\s*\(.*?\)\s*','',f)) for f in reg_forms(reg[i])}]
    w2=collections.defaultdict(set)
    for w,i,D,_ in occ: w2[norm(w)].add(i)
    dead=[(w,i,D) for w,i,D,_ in occ if i not in reg or reg[i]['status']!='active']
    print('nisbah',len(occ)+len(noref),'noref',len(noref),'mismatch',len(mis),
          'split',sum(1 for v in w2.values() if len(v)>1),'non-active or unknown ref',len(dead))
