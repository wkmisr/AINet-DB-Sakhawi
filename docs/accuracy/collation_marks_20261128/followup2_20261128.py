#!/usr/bin/env python3
"""Second follow-up to PR #128 (2026-11-28), after collation with the print.

WK rulings 2026-11-28:
  - entries that are not cross-references get an AIND number (suffix on the number of the preceding entry)
  - '...' after a bare name is replaced by '.', as in the print
  - s198 / s187 are corrected to the print
  - the 7 heading-less cross-references that never carried a star get a $$$ heading
Line numbers are those of the corpus at commit 319bed1. Run once from the repo root.
"""
import re, random, csv, io
C='0__DawForAIND_renumbered_B54_split20260905.txt'
REG='authority/persons_registry.tsv'
D='docs/accuracy/collation_marks_20261128/'
L=open(C,encoding='utf-8',newline='').read().split('\n')
n0=len(L)
used=set(re.findall(r'(\d{12})\$#',"\n".join(L)))

# 1. '...' -> '.'  (bare names; the print has the name and a full stop)
for ln in (50048,56791,95796,110496):
    s=L[ln-1]; assert s.rstrip().endswith('...'),ln
    L[ln-1]=s.rstrip()[:-3].rstrip()+' .'
# 2. s187: drop the working memo '=850'
assert L[112441-1]=='الروياني . سبق قريبا =850 .'
L[112441-1]='الروياني . سبق قريبا .'
# 3. s198: 'بن محمد' restored, full stop after المدينة as in the print (vol. 10, PDF p. 259)
old='التلمساني المغربي المالكي نزيل المدينة مضى في يحيى بن عبد الرحمن قريبا.'
assert L[114571-1]==old
L[114571-1]='التلمساني المغربي المالكي نزيل المدينة . مضى في يحيى بن محمد بن عبد الرحمن قريبا .'

# 4. AIND numbers for the 9 entries that are not cross-references
NEW=[('s058',50048,'AIND-D04559b','عبد الله بن محمد بن أحمد البخانقي','vol. 5, PDF p. 47'),
     ('s064',51115,'AIND-D04670b','عبد الله الحامي المغربي','vol. 5, PDF p. 75'),
     ('s067',51124,'AIND-D04676b','عبد الله العجلوني','vol. 5, PDF p. 76'),
     ('s099',56791,'AIND-D05173b','علي بن أبي سويد بن أبي دعيج بن أبي نمى','vol. 5, PDF p. 230'),
     ('s106',58804,'AIND-D05397b','علي بن محمد بن أحمد الطبناوي','vol. 5, PDF p. 289'),
     ('s109',59493,'AIND-D05446b','علي بن محمد بن عبد العزيز بن الرفا','vol. 5, PDF p. 308'),
     ('s160',95796,'AIND-D08690b','محمد بن محمد بن أحمد العدوي','vol. 9, PDF p. 52'),
     ('s185',110496,'AIND-D09888b','مختص الطواشي','vol. 10, PDF p. 150'),
     ('s215',124050,'AIND-D11136c','سابق الدين','vol. 11, PDF p. 158')]
issued=[]
HL={r.split('\t')[0]:int(r.split('\t')[1]) for r in open(D+'headings_added.tsv',encoding='utf-8').read().split('\n')[1:] if r}
for site,_ln,aid,name,pos in NEW:
    ln=HL[site]
    m=re.match(r'^###\$(\d{12})\$# \$\$\$ (.*)$',L[ln-1]); assert m,(site,L[ln-1])
    assert name.split()[0]==m.group(2).replace('　',' ').split()[0],site
    # the preceding AIND heading must be the base number
    j=ln-2
    while not re.match(r'^###\$AIND-',L[j]): j-=1
    base=re.match(r'^###\$(AIND-D\d+[a-z]?)',L[j]).group(1)
    assert base[:11]==aid[:11],(site,base,aid)
    L[ln-1]='###$%s | %s$# $ %s'%(aid,m.group(1),m.group(2))
    issued.append((site,ln,aid,m.group(1),name,pos))

# 5. $$$ headings for 7 heading-less cross-references that never carried a star
random.seed(2026112802)
ADD=[(15750,'vol. 2, PDF p. 95'),(19462,'vol. 2, PDF p. 201'),(19951,'vol. 2, PDF p. 214'),(20703,'vol. 2, PDF p. 233'),
     (21784,'vol. 2, PDF p. 261'),(41000,'vol. 4, PDF p. 135'),(42285,'vol. 4, PDF p. 171')]
added=[]
for ln,pos in ADD:
    s=L[ln-1]; assert L[ln-2].strip()=='' and s.strip() and not s.startswith('#'),ln
    while True:
        pid=str(random.randint(1,9))+''.join(str(random.randint(0,9)) for _ in range(11))
        if pid not in used: used.add(pid); break
    L[ln-1]='###$%s$# $$$ %s'%(pid,s)
    added.append((ln,pid,pos,s))
assert len(L)==n0
open(C,'w',encoding='utf-8',newline='').write('\n'.join(L))

# 6. registry: 9 rows, each after the last row of its base number
R=open(REG,encoding='utf-8',newline='').read()
nl='\r\n' if '\r\n' in R else '\n'
rows=R.split(nl)
ids=[r.split('\t')[0] for r in rows]
for site,ln,aid,pid,name,pos in issued:
    assert aid not in ids
    base=aid[:11]
    k=max(i for i,x in enumerate(ids) if x[:11]==base)
    hist='Added 2026-11-28 (unnumbered entry of the print, %s; it had no heading in the corpus and was given one in PR #128; AIND number issued by WK ruling 2026-11-28)'%pos
    row='\t'.join([aid,'active','',name,'','','',hist])
    rows.insert(k+1,row); ids.insert(k+1,aid)
open(REG,'w',encoding='utf-8',newline='').write(nl.join(rows))

# 7. headings_added.tsv
H=open(D+'headings_added.tsv',encoding='utf-8',newline='').read().rstrip('\n').split('\n')
by={x[0]:x for x in issued}
out=[H[0]+'\taind']
for r in H[1:]:
    f=r.split('\t')
    if f[0] in by:
        f[3]='short entry or bare name (not a cross-reference); AIND number issued (WK ruling 2026-11-28), entry type $'
        f[4]=L[int(f[1])-1].split('$# $ ',1)[1]
        f.append(by[f[0]][2])
    else:
        f[4]=L[int(f[1])-1].split('$$$ ',1)[1]
        f.append('')
    out.append('\t'.join(f))
for i,(ln,pid,pos,s) in enumerate(added,1):
    out.append('\t'.join(['n%02d'%i,str(ln),pid,'cross-reference (no star in the corpus; found in the review of 2026-11-28; print: %s)'%pos,s,'']))
open(D+'headings_added.tsv','w',encoding='utf-8',newline='').write('\n'.join(out)+'\n')
for x in issued: print(*x[:4])
for x in added: print(*x[:3])
