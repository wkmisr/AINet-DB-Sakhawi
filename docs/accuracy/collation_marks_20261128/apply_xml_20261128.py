import re,json,glob
exec(open('/home/claude/work/apply.py').read().split("log=[]")[0].split("rows=json.load",1)[0].replace("raw=open(C,encoding='utf-8',newline='').read()","raw=''").replace("L=raw.split(nl)","")) if False else None
src=open('/home/claude/work/apply.py').read()
E=eval('{'+src.split("E={ # sid: [(old,new)]")[1].split("\n}\n")[0]+'}')
rows=json.load(open('/mnt/user-data/uploads/AINet-DB-Sakhawi/docs/_work/collation_marks_20261128/rows2.json'))
X={f.split('/')[-1].split('_')[0]:f for f in glob.glob('Individuals/*/*.xml')}
by={}
for r in rows:
    if r[2].startswith('AIND') and r[2] in X: by.setdefault(r[2],[]).append(r[0][:4])
changed=[]
for a,sids in sorted(by.items()):
    t=open(X[a],encoding='utf-8',newline='').read()
    m=re.search(r'(<note type="source"[^>]*>)(.*?)(</note>)',t,flags=re.S)
    if not m: print('nosrc',a); continue
    s=m.group(2); s0=s; did=[]
    for sid in sids:
        for old,new in E.get(sid,[]):
            if old in s: s=s.replace(old,new); did.append(f'「{old.replace("±±±","").replace("★","")}」→「{new}」')
            else:
                o2=old.replace('±±±','').replace('★','')
                if o2 and o2 in s and o2!=new and len(o2)>3: s=s.replace(o2,new); did.append(f'「{o2}」→「{new}」')
    marks=('±±±' in s or '★' in s)
    s=s.replace('±±±','').replace('★','')
    if s==s0: continue
    note='校合記号（★・±±±）の後始末（Waka 裁定 2026-11-28）。note source から corpus の作業記号を外した' if marks else '校合記号の後始末（Waka 裁定 2026-11-28）'
    if did: note+='。刊本との照合により '+'、'.join(did)+' に直した'
    note+='。ほかの要素は変更なし。'
    rs=f'    <respStmt><resp xml:lang="ja">修正・追記</resp><note xml:lang="ja">{note}</note><persName>Kumakura</persName><date when="2026-11-28"/></respStmt>\n'
    t2=t[:m.start(2)]+s+t[m.end(2):]
    i=t2.rfind('</person>'); assert i>0
    t2=t2[:i]+rs+t2[i:]
    open(X[a],'w',encoding='utf-8',newline='').write(t2); changed.append((a,did))
    # other elements holding old words?
    body=re.sub(r'<respStmt.*?</respStmt>|<note.*?</note>','',t2,flags=re.S)
    for sid in sids:
        for old,new in E.get(sid,[]):
            o2=old.replace('±±±','').replace('★','')
            if len(o2)>3 and o2 in body: print('OTHER ELEMENT has old word',a,sid,o2)
for a,d in changed: print(a,d)
print(len(changed))
