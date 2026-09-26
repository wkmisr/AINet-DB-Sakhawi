# 監査_20260907 第2ラウンド: 自己ID不整合ほか
import sys,glob,os
D=sys.argv[1]
def f(pid):
    g=glob.glob(os.path.join(D,f'AIND-{pid}_*.xml')); assert len(g)==1,(pid,g); return g[0]
P=[
 ('D00124a','passive="#AIND-D00124"','passive="#AIND-D00124a"',2),
 ('D00638a','passive="#AIND-D00638"','passive="#AIND-D00638a"',1),
 ('D00410a','active="#TMP-P-000337" passive="#AIND-D00410"','active="#AIND-D05881" passive="#AIND-D00410a"',1),
 ('D00750','active="#TMP-P-000678" passive="#AIND-D10262"><desc xml:lang="ar">يحيى بن فهد</desc>',
  'active="#NEEDID" passive="#AIND-D00750"><desc xml:lang="ar">يحيى بن فهد</desc><note xml:lang="ja">候補2名で確定不能: المحيوي يحيى بن عبد الرحمن بن فهد (AIND-D10262、旧passive) / العماد يحيى بن محمد بن فهد (TMP-P-000678、旧active)。監査20260907</note>',1),
]
bad=[(pid,old,open(f(pid),encoding='utf-8').read().count(old),n) for pid,old,new,n in P if open(f(pid),encoding='utf-8').read().count(old)!=n]
assert not bad,bad
for pid,old,new,n in P:
    p=f(pid); s=open(p,encoding='utf-8').read(); open(p,'w',encoding='utf-8').write(s.replace(old,new)); print(pid,n)
print('OK')
