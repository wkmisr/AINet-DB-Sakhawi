# 監査_20260907: ID紐付け是正パッチ（cloud/device 共通）
# usage: python3 audit_patch.py <Individuals dir>
import sys, glob, os, re
D = sys.argv[1]
def f(pid):
    g = glob.glob(os.path.join(D, f'AIND-{pid}_*.xml'))
    assert len(g) == 1, (pid, g); return g[0]

# (pid, old, new, expected count)  — attribute-level exact replacements
P = [
 # --- 汚染TMP（別人IDの流用）
 ('D00256', 'subtype="father" active="#TMP-P-000044"', 'subtype="father" active="#TMP-P-000956"', 1),
 ('D00638a','subtype="father" active="#TMP-P-000044"', 'subtype="father" active="#AIND-D02375"', 1),
 ('D00902', 'subtype="father" active="#TMP-P-000044"', 'subtype="father" active="#TMP-P-000401"', 1),
 ('D00909', 'subtype="brother" active="#TMP-P-000044"', 'subtype="brother" active="#TMP-P-000957"', 1),
 ('D00909', 'subtype="father" active="#TMP-P-000073"', 'subtype="father" active="#AIND-D04548"', 1),
 ('D00911', 'subtype="ancestor" active="#TMP-P-000044"', 'subtype="ancestor" active="#TMP-P-000958"', 1),
 ('D01393', 'subtype="brother" active="#TMP-P-000044"', 'subtype="brother" active="#AIND-D00285"', 1),
 ('D01393', 'subtype="brother" active="#TMP-P-000073"', 'subtype="brother" active="#AIND-D08902a"', 1),
 ('D01393', 'subtype="father" active="#TMP-P-000100"', 'subtype="father" active="#AIND-D07940"', 1),
 ('D01394', 'subtype="son" active="#TMP-P-000044"', 'subtype="son" active="#AIND-D06885"', 1),
 ('D01390', 'active="#TMP-P-000374"', 'active="#AIND-D03092"', 1),
 ('D01390', 'active="#TMP-P-000375"', 'active="#AIND-D03106"', 1),
 ('D01390', 'active="#TMP-P-000376"', 'active="#TMP-P-000959"', 1),
 ('D01390', 'active="#TMP-P-000377"', 'active="#AIND-D08897"', 1),
 ('D00311', 'active="#TMP-P-000361"', 'active="#TMP-P-000960"', 2),
 ('D00318', 'subtype="uncle" active="#TMP-P-000361"', 'subtype="uncle" active="#TMP-P-000006"', 1),
 ('D01363', 'subtype="father" active="#TMP-P-000371"', 'subtype="father" active="#AIND-D07731"', 1),
 ('D00126', 'subtype="father" active="#TMP-P-000291"', 'subtype="father" active="#AIND-D03079"', 1),
 ('D00201', 'active="#TMP-P-000288"', 'active="#TMP-P-000271"', 1),
 ('D00134', 'subtype="other" active="#TMP-P-000275"', 'subtype="other" active="#AIND-D00462"', 1),
 ('D01619', 'active="#TMP-P-000067"', 'active="#AIND-D10439"', 1),
 ('D00750', 'active="#TMP-P-000346"', 'active="#TMP-P-000678"', 1),
 ('D00527', 'active="#AIND-D00104"', 'active="#AIND-D02507"', 2),
 ('D00527', 'active="#TMP-P-000488"', 'active="#AIND-D04089"', 1),
 ('D00527', 'active="#TMP-P-000489"', 'active="#AIND-D04089"', 1),
 ('D00104', 'active="#TMP-P-000280"', 'active="#AIND-D02507"', 1),
 ('D00104', 'active="#TMP-P-000281"', 'active="#AIND-D04089"', 1),
 ('D00406', 'active="#TMP-P-000006"', 'active="#AIND-D05766"', 1),
 ('D00780', 'active="#TMP-P-000006"', 'active="#TMP-P-000961"', 1),
 ('D00435', 'n="5" active="#TMP-P-000006"', 'n="5" active="#TMP-P-000964"', 1),
 ('D00240', 'active="#TMP-P-000073"', 'active="#AIND-D05583"', 1),
 ('D00240', 'subtype="grandfather" active=""', 'subtype="grandfather" active="#TMP-P-000965"', 1),
 ('D01628', 'subtype="grandfather" active=""', 'subtype="grandfather" active="#TMP-P-000962"', 1),
 ('D00512', 'subtype="grandfather" active="#TMP-N-00758"', 'subtype="grandfather" active="#TMP-P-000963"', 1),
 # --- カテゴリ誤用（Nisbah番号を人物/地名に流用）
 ('D00573', 'passive="#TMP-N-00174"', 'passive="#AIND-D10718"', 1),
 ('D00824', '<placeName ref="#TMP-N-00217">', '<placeName ref="#TMP-L-00240">', 1),
 # --- البدري 統一（TMP-P-000719 → AIND-D10718）
 ('D02143', 'ref="#TMP-P-000719"', 'ref="#AIND-D10718"', 1),
 ('D02660', 'ref="#TMP-P-000719"', 'ref="#AIND-D10718"', 1),
 ('D05634', 'ref="#TMP-P-000719"', 'ref="#AIND-D10718"', 1),
 ('D09009a','ref="#TMP-P-000719"', 'ref="#AIND-D10718"', 1),
 # --- 幻番号
 ('D00666', '#TMP-N-05554', '#TMP-N-00554', 1),
 ('D00890', '#TMP-T-00079', '#TMP-T-00065', 2),
 ('D01131', '#TMP-T-00079', '#TMP-T-00065', 8),
 ('D01988', '#TMP-T-00079', '#TMP-T-00065', 2),
 ('D01664', '#TMP-T-00079', '#TMP-T-00164', 2),
 ('D01182', '#TMP-T-00031', '#TMP-T-00144', 2),
 ('D01285', '#TMP-T-00031', '#TMP-T-00165', 4),
 ('D01082', '#TMP-T-00000', '#TMP-T-00018', 1),
 ('D01415', '#TMP-I-00000', '#TMP-I-00148', 1),
 ('D01614', '#TMP-L-00015', '#TMP-I-00091', 2),
 # --- 誤記
 ('D01663', '#AIND-DD00112', '#AIND-D00112', 1),
 ('D00101', 'wd:#Q12217063', 'wd:Q12217063', 1),
 ('D02019', '#AIND-D02710', '#AIND-D02759', 1),
 ('D02655', '#AIND-D02710', '#AIND-D02759', 1),
 # --- 名寄せ（重複TMP統合・AIND確定）
 ('D01728', '#TMP-P-000203', '#AIND-D00101', 1),
 ('D01257', '#TMP-P-000544', '#TMP-P-000388', 1),
 ('D00886', '#TMP-P-000564', '#TMP-P-000561', 1),
 ('D01155', '#TMP-P-000564', '#TMP-P-000561', 2),
 ('D00524', '#TMP-P-000496', '#AIND-D00462', 1),
 ('D01497', '#TMP-P-000609', '#AIND-D00462', 1),
 ('D00875', 'wd:Q1140365', 'wd:Q2175237', 2),
]
# repo-wide wd → AIND（スルタン等、本伝あり）
W = {'wd:Q557847':'#AIND-D06305','wd:Q647942':'#AIND-D02423','wd:Q122501':'#AIND-D02423',
     'wd:Q557812':'#AIND-D02168','wd:Q248996':'#AIND-D02178','wd:Q698037':'#AIND-D06160',
     'wd:Q286532':'#AIND-D02110','wd:Q285627':'#AIND-D02110','wd:Q553204':'#AIND-D03298'}

log=[]
bad=[(pid,old,open(f(pid),encoding='utf-8').read().count(old),n) for pid,old,new,n in P if open(f(pid),encoding='utf-8').read().count(old)!=n]
assert not bad, bad   # dry-run: 全件一致してから書込
for pid,old,new,n in P:
    p=f(pid); s=open(p,encoding='utf-8').read()
    open(p,'w',encoding='utf-8').write(s.replace(old,new)); log.append(f'{pid}\t{old}\t{new}\t{n}')
wc={}
for p in glob.glob(os.path.join(D,'*.xml')):
    s=open(p,encoding='utf-8').read(); t=s
    for k,v in W.items():
        for q in ('"%s"'%k, '"%s '%k, ' %s"'%k):
            if q in t: t=t.replace(q,q.replace(k,v)); wc[k]=wc.get(k,0)+1
    if t!=s: open(p,'w',encoding='utf-8').write(t)
log.append('wd->AIND files: '+str(wc))
print('\n'.join(log)); print('OK', len(P), 'replacements')
