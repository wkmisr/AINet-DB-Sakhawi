import sys,glob,re,os
from norm import norm
q=norm(sys.argv[1]); lim=int(sys.argv[2]) if len(sys.argv)>2 else 15; n=0
for f in sorted(glob.glob('repo/Individuals/*.xml')):
    s=open(f,encoding='utf-8').read()
    if q in norm(s) or q in s:
        for line in s.split('\n'):
            if q in norm(line) or q in line:
                print(os.path.basename(f)[:20],'|',line.strip()[:220]); n+=1; break
    if n>=lim: break
