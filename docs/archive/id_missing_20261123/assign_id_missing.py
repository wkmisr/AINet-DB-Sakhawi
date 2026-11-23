"""Give a heading line and IDs to every entry marked ★ID_Missing★ in the corpus.
Usage: python3 assign_id_missing.py <corpus.txt> <out_corpus.txt> <log.tsv>
Rules (same as split20260905): AIND = ID of the record that contains the entry + next free suffix;
12-digit source ID = random (seed 20261123), unique in the corpus; body text is not altered."""
import re,random,sys
src,dst,logp=sys.argv[1:4]
txt=open(src,encoding='utf-8').read()
MARK='★ID_Missing★'
existing=set(re.findall(r'(\d{12})\$#',txt))
used={}
for a,s in re.findall(r'^###\$(AIND-D\d+)([a-z]?) ',txt,re.M):
    used.setdefault(a,set())
    if s: used[a].add(s)
random.seed(20261123)
def newsid():
    while True:
        i=''.join(random.choice('0123456789') for _ in range(12))
        if i[0]!='0' and i not in existing: existing.add(i); return i
def nextsuf(base):
    for c in 'abcdefghijklmnopqrstuvwxyz':
        if c not in used[base]: used[base].add(c); return c
    raise SystemExit('no suffix left for '+base)
out=[];log=[];cur=None
for line in txt.split('\n'):
    m=re.match(r'###\$(AIND-D\d+)[a-z]? ',line)
    if m: cur=m.group(1)
    if MARK not in line: out.append(line); continue
    parts=line.split(MARK)
    head=parts[0].rstrip()
    if head:
        out.append(head); out.append('')
    elif out and out[-1].strip(): out.append('')
    for p in parts[1:]:
        text=p.strip(); assert cur and text
        nid=cur+nextsuf(cur); sid=newsid()
        out.append(f'###${nid} | {sid}$# $ {text}')
        log.append((nid,sid,cur,'start of line' if not head else 'inside a line',text[:70]))
        if p is not parts[-1]: out.append('')
new='\n'.join(out)
assert MARK not in new
a=re.sub(r'\s+','',txt.replace(MARK,'')); b=new
for nid,sid,*_ in log: b=b.replace(f'###${nid} | {sid}$# $ ','')
assert a==re.sub(r'\s+','',b), 'text changed'
open(dst,'w',encoding='utf-8').write(new)
with open(logp,'w',encoding='utf-8') as f:
    f.write('new_AIND\tsource_id_12\tfrom_record\tposition\theading_start\n')
    for r in log: f.write('\t'.join(r)+'\n')
print(len(log),'entries;',len(txt.split(chr(10))),'->',len(out),'lines')
