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
