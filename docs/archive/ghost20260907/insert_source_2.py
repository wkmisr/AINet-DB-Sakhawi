import glob,sys,os
D=sys.argv[1]
S={'D00782':'أحمد بن صبح أحد الظلمة بدمشق . مات بقلعتها في\nسنة ثلاث وتسعين .','D01628':'أحمد بن محمد الشكيلي المدني . فيمن جده إبراهيم .'}
for k,t in S.items():
    p=glob.glob(os.path.join(D,'AIND-%s_*.xml'%k))[0]; s=open(p,encoding='utf-8').read()
    assert 'type="source"' not in s
    i=s.index('    <note type="translation"'); s=s[:i]+'    <note type="source" xml:lang="ar">%s</note>\n'%t+s[i:]
    open(p,'w',encoding='utf-8').write(s); print(k,'ok')
