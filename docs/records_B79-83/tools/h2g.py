import sys
def jd(y,m,d): return (11*y+3)//30+354*y+30*m-(m-1)//2+d+1948440-385
def g(J):
    c=J+32082; d=(4*c+3)//1461; e=c-1461*d//4; m=(5*e+2)//153
    return (d-4800+m//10, m+3-12*(m//10), e-(153*m+2)//5+1)
W=['月','火','水','木','金','土','日']
for a in sys.argv[1:]:
    p=[int(x) for x in a.split('-')]
    y=p[0]; m=p[1] if len(p)>1 else 1; d=p[2] if len(p)>2 else 1
    J=jd(y,m,d); Y,M,D=g(J)
    s=f"{a} -> {Y:04d}-{M:02d}-{D:02d}"
    if len(p)>2: s+=f" ({W[J%7]}曜)"
    if len(p)==1: Y2,M2,D2=g(jd(y,12,29)); s+=f" .. {Y2:04d}-{M2:02d}-{D2:02d} (year end)"
    if len(p)==2: Y2,M2,D2=g(jd(y,m,29)); s+=f" .. {Y2:04d}-{M2:02d}-{D2:02d}"
    print(s)
