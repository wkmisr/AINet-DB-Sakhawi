import re,random,json
SRC='/home/claude/b68/corpus.txt'
txt=open(SRC,encoding='utf-8').read()
blocks=re.split(r'(?=###\$)',txt)
assert ''.join(blocks)==txt
existing=set(re.findall(r'(\d{12})\$#',txt))
random.seed(20260905)
def newid():
    while True:
        i=''.join(random.choice('0123456789') for _ in range(12))
        if i[0]!='0' and i not in existing: existing.add(i); return i
hdr=re.compile(r"^###\$(?:(AIND-D\d+)?([a-z]?)\s*\|\s*)?(\d{11,13})\$# (\$+) ?(.*)$")
out=[]; log=[]; last_aind=None; used_suffix={}
for b in blocks:
    if not b.startswith('###$'): out.append(b); continue
    lines=b.split('\n')
    m=hdr.match(lines[0]); assert m, lines[0][:80]
    aind,suf,sid,dol,rest=m.groups()
    if aind and not suf:
        last_aind=aind
    if aind and suf: used_suffix.setdefault(aind,[]).append(suf)
    hits=[i for i,l in enumerate(lines) if i>0 and re.match(r'^\s*\d{1,4}\s*★',l)]
    if not hits: out.append(b); continue
    base = aind if aind else last_aind
    # existing suffixes for base
    start_letter = 'a'
    if base in used_suffix: start_letter=chr(ord(max(used_suffix[base]))+1)
    cuts=hits+[len(lines)]
    # base part
    basepart=lines[:hits[0]]
    while basepart and basepart[-1].strip()=='': basepart.pop()
    out.append('\n'.join(basepart)+'\n\n')
    letter=ord(start_letter)
    for j,h in enumerate(hits):
        seg=lines[h:cuts[j+1]]
        while seg and seg[-1].strip()=='': seg.pop()
        head=seg[0]
        mm=re.match(r'^\s*(\d{1,4})\s*(.*)$',head)
        num,text=mm.groups()
        text_clean=text.replace('★','',2)
        assert '★' not in text_clean or text.count('★')>2
        nid=f'{base}{chr(letter)}'; letter+=1
        sid_new=newid()
        newhead=f'###${nid} | {sid_new}$# $ {num} {text_clean}'
        rest=seg[1:]
        # detach trailing unnumbered ★-stubs (transfer headings) as $$$ stubs
        stubs=[]
        k=[i for i,l in enumerate(rest) if l.startswith('★')]
        if k:
            first=k[0]; tail=rest[first:]; rest=rest[:first]
            while rest and rest[-1].strip()=='': rest.pop()
            # tail may contain several stubs separated by blank lines; split on lines starting with ★
            cur=[]
            for l in tail:
                if l.startswith('★') and cur: stubs.append(cur); cur=[]
                cur.append(l)
            if cur: stubs.append(cur)
        body='\n'.join([newhead]+rest)
        out.append(body+'\n\n')
        for st in stubs:
            while st and st[-1].strip()=='': st.pop()
            t0=st[0].replace('★','',2)
            sid_st=newid()
            out.append('\n'.join([f'###${sid_st}$# $$$ {t0}']+st[1:])+'\n\n')
            log.append({'new_id':'($$$ stub)','source':sid_st,'num':'','heading':t0.strip()[:80],'from_record':nid,'from_dollars':'$$$','lines':len(st)})
        used_suffix.setdefault(base,[]).append(chr(letter-1))
        log.append({'new_id':nid,'source':sid_new,'num':num,'heading':text_clean.strip()[:80],'from_record':aind or ('$$$ '+sid),'from_dollars':dol,'lines':len(seg)})
new=''.join(out)
# ensure trailing structure: original ended how?
open('/home/claude/split/0__DawForAIND_renumbered_B54_split20260905.txt','w',encoding='utf-8').write(new)
json.dump(log,open('/home/claude/split/split_log.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print(len(log), len(re.split(r'(?=###\$)',new)))
for r in log: print(r['new_id'],r['source'],r['num'],r['from_record'],'|',r['heading'][:50])
