import re,sys,glob,os
from desc_fix import FIX
from lxml import etree
root=sys.argv[1]
by={}
for k,v in FIX.items(): by.setdefault(k[0],{})[k[1]]=v
tot=0
for rid,m in by.items():
    fs=glob.glob(os.path.join(root,rid+'_*.xml')); assert len(fs)==1,rid
    f=fs[0]; s=open(f,encoding='utf-8').read()
    # split on relation elements in order
    rels=list(re.finditer(r'<relation\b.*?</relation>',s,re.S))
    out=s; delta=0
    for idx,new in sorted(m.items()):
        mo=rels[idx]; block=mo.group(0)
        dm=re.search(r'<desc xml:lang="ar">(.*?)</desc>',block,re.S)
        assert dm, (rid,idx)
        old=dm.group(1)
        # indentation of the desc line
        ind=re.search(r'\n([ \t]*)<desc xml:lang="ar">',block)
        pad=ind.group(1) if ind else ''
        note=f'<note xml:lang="ar">{old.strip()}</note>'
        nb=block[:dm.start()]+f'<desc xml:lang="ar">{new}</desc>'+block[dm.end():]
        # insert evidence note right after desc
        nb=nb.replace(f'<desc xml:lang="ar">{new}</desc>',f'<desc xml:lang="ar">{new}</desc>'+('\n'+pad if pad else '')+note,1)
        a,b=mo.start()+delta,mo.end()+delta
        out=out[:a]+nb+out[b:]; delta+=len(nb)-len(block); tot+=1
    etree.fromstring(out.encode('utf-8'))
    open(f,'w',encoding='utf-8',newline='').write(out)
print('fixed',tot,'in',len(by),'files')
