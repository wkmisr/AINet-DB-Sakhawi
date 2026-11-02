import re, json, glob, os, sys
from lxml import etree
os.chdir(os.path.dirname(os.path.abspath(__file__))+'/../../..')
XML='{http://www.w3.org/XML/1998/namespace}lang'
DIA=re.compile('[ً-ْـٰ]')
def norm(s):
    s=DIA.sub('',s)
    s=re.sub('[أإآٱ]','ا',s); s=s.replace('ى','ي').replace('ة','ه')
    s=re.sub(r'\s+',' ',s).strip()
    return s
AR='ء-ي'
def token_re(pn):
    core=pn
    if core.startswith('ال'): core=core[2:]
    words=[re.escape(w) for w in core.split(' ')]
    body=r'\s+'.join(words)
    return re.compile(r'(?<![%s])[وفبلك]{0,2}(?:ال|ل)?%s(?![%s])'%(AR,body,AR))
out=[]; tot=0; tot_sub=0
for f in sorted(glob.glob('Individuals/*.xml')):
    t=etree.parse(f); r=t.getroot()
    srcs=[n for n in r.iter('note') if n.get('type')=='source' and n.get(XML)=='ar']
    src=' '.join(''.join(n.itertext()) for n in srcs)
    ns=norm(src)
    for pn in r.iter('placeName'):
        lang=pn.get(XML)
        if lang not in (None,'ar'): continue
        tot+=1
        txt=''.join(pn.itertext()); nt=norm(txt)
        if not nt: continue
        sub = nt in ns or (nt.startswith('ال') and nt[2:] in ns) or ('ال'+nt) in ns
        tok = bool(token_re(nt).search(ns))
        if not tok:
            par=pn.getparent()
            ctx=par.tag+'['+' '.join(f'{k.split("}")[-1]}={v}' for k,v in par.attrib.items())+']'
            out.append(dict(file=os.path.basename(f),id=r.get('{http://www.w3.org/XML/1998/namespace}id'),
              pn=txt,ref=pn.get('ref'),ptype=pn.get('type'),cert=pn.get('cert'),line=pn.sourceline,
              parent=ctx,parent_line=par.sourceline,substr_hit=sub))
print('total ar placeName',tot,'not in source (token)',len(out),'of which substring-hit',sum(o['substr_hit'] for o in out))
json.dump(out,open('docs/records_B88/rule22_audit/miss_latest.json','w'),ensure_ascii=False,indent=0)
