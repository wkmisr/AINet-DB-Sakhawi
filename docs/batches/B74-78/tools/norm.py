import re
_D=re.compile(r'[ً-ْٰـ]')
def norm(s):
    s=_D.sub('',s)
    s=re.sub('[إأآا]','ا',s); s=s.replace('ى','ي').replace('ة','ه').replace('ؤ','و').replace('ئ','ي')
    return s
