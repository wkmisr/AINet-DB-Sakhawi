# Follow-up after the independent review of PR #128 (WK ruling 2026-11-28).
# Line numbers are those of the corpus at commit 2a252cd.
# 1. headings for the 43 unnumbered cross-reference / short entries that used to start with a star
# 2. AIND-D08578: "بن علي محمد" -> "بن علي بن محمد" (the print has the two words transposed: بن بن على محمد)
# 3. "| " on every non-empty line of the two colophons (AIND-D07319, AIND-D09490)
import re,json,random,csv,sys
C='0__DawForAIND_renumbered_B54_split20260905.txt'
raw=open(C,encoding='utf-8',newline='').read(); L=raw.split('\n')
sites=json.load(open(sys.argv[1]))   # [[site, line, n_lines, text], ...] (43 rows)
assert len(sites)==43
used=set(re.findall(r'\b\d{12}\b',raw)); random.seed(2026112802)
rows=[]
NOT_XREF={'s058','s064','s067','s099','s106','s109','s160','s185','s215'}
for sid,ln,n,_ in sites:
    s=L[ln-1]; assert L[ln-2].strip()=='' and not s.startswith(('###','|')),(sid,ln)
    while True:
        pid=''.join(random.choice('0123456789') for _ in range(12))
        if pid not in used and pid[0]!='0': used.add(pid); break
    L[ln-1]='###$%s$# $$$ %s'%(pid,s)
    rows.append((sid,ln,pid,'short entry or bare name (not a cross-reference); entry type left as $$$, to be ruled' if sid in NOT_XREF else 'cross-reference',s.strip()))
# 2
i=94376; old='38 محمد بن علي محمد بن أبي بكر بن إسماعيل بن'; assert L[i].endswith(old),L[i]
L[i]=L[i].replace('محمد بن علي محمد بن أبي بكر','محمد بن علي بن محمد بن أبي بكر')
# 3
def bar(a,b):
    assert L[a-1].startswith('| ') and L[b].strip()=='' and L[b+1].startswith('###$'),(a,b)
    for k in range(a,b):
        if L[k].strip() and not L[k].startswith('|'): L[k]='| '+L[k]
bar(80244,80269); bar(107162,107192)
open(C,'w',encoding='utf-8',newline='').write('\n'.join(L))
w=csv.writer(open(sys.argv[2],'w',encoding='utf-8',newline=''),delimiter='\t',lineterminator='\n')
w.writerow(['site','corpus_line','source_no','kind','text']); w.writerows(rows)
