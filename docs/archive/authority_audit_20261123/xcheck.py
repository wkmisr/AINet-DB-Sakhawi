import csv,os,re,collections,sys
csv.field_size_limit(10**9)
R='/home/claude/ainet-db-sakhawi/'
def norm(s):
    s=re.sub(r'[ً-ْٰـ]','',s); s=re.sub('[إأآٱ]','ا',s).replace('ى','ي').replace('ة','ه')
    return ' '.join(re.findall(r'[ء-ي]+',s))
def bare(s):
    return ' '.join(re.sub(r'^(وال|بال|كال|فال|لل|ال|و|ب|ل)(?=..)','',w) for w in s.split())
E_=list(csv.DictReader(open(R+'authority/entities_registry.tsv',encoding='utf-8',newline=''),delimiter='\t'))
EN={e['id']:e for e in E_}
labels={k:{norm(x) for x in [e['label_ar']]+e['variants'].split('|') if norm(x)} for k,e in EN.items()}
bylab=collections.defaultdict(set)
for k,ls in labels.items():
    for l in ls: bylab[(EN[k]['category'],l)].add(k); bylab[(EN[k]['category'],'~'+bare(l))].add(k)
A=re.compile(r'<(\w+)\b([^>]*\bref="#?([^"]+)"[^>]*)>([^<]*)(?:\s*<(\w+)[^>]*xml:lang="ar"[^>]*>([^<]*))?')
out=collections.defaultdict(lambda: dict(n=0,recs=set()))
tot=collections.Counter()
for d,_,fs in os.walk(R+'Individuals'):
    for f in fs:
        if not f.endswith('.xml') or f.startswith('REF_'): continue
        rec=f.split('_')[0]; t=open(os.path.join(d,f),encoding='utf-8').read()
        for m in A.finditer(t):
            tag,attrs,ref,direct,ctag,ctext=m.groups()
            if ref not in EN: continue
            text=direct.strip() if ('xml:lang="ar"' in attrs and direct.strip()) else (ctext or '').strip()
            if not text: continue
            cat=EN[ref]['category']; tot[cat]+=1
            parts={norm(x) for x in text.split('|') if norm(x)}
            if parts & labels[ref]: continue
            if {bare(p) for p in parts} & {bare(l) for l in labels[ref]}: kind='冠詞・前置詞の違いだけ'
            else:
                cand=set()
                for p in parts: cand|=bylab.get((cat,p),set())|bylab.get((cat,'~'+bare(p)),set())
                cand.discard(ref)
                kind='別のIDの表記と一致（IDの付け違いの疑い）' if cand else '表記が典拠表にない'
            key=(cat,ref,text,kind,' '.join(sorted(cand)) if kind.startswith('別') else '')
            out[key]['n']+=1; out[key]['recs'].add(rec)
rows=[(c,ref,EN[ref]['label_ar']+((' | '+EN[ref]['variants']) if EN[ref]['variants'] else ''),text,kind,sug,v['n'],' '.join(sorted(v['recs'])[:6])) for (c,ref,text,kind,sug),v in out.items()]
rows.sort(key=lambda r:(r[4],r[0],r[1]))
with open('/home/claude/work/xcheck/label_mismatch.tsv','w',encoding='utf-8',newline='') as f:
    w=csv.writer(f,delimiter='\t'); w.writerow(['分類','レコードが付けたID','そのIDの典拠表の表記','レコードの語','種類','一致する別のID','箇所数','レコード（例）']); w.writerows(rows)
print('checked',dict(tot))
c=collections.Counter((r[4],r[0]) for r in rows); n=collections.Counter()
for r in rows: n[(r[4],r[0])]+=r[6]
for k in sorted(c): print(k,'種類',c[k],'箇所',n[k])
import random; random.seed(4)
for kind in sorted({r[4] for r in rows}):
    print('==',kind)
    S=[r for r in rows if r[4]==kind]
    for r in random.sample(S,min(8,len(S))): print('  ',r[0],r[1],'|',r[2][:40],'|',r[3][:40],'|',r[5][:40],'|',r[6])
