import glob,os,re,sys
for o in glob.glob('out/*.xml'):
    b=os.path.basename(o).replace('REF_','')
    i=os.path.join('in',b)
    if not os.path.exists(i): print('NO IN',b); continue
    si=open(i,encoding='utf-8').read(); so=open(o,encoding='utf-8').read()
    ci=re.search(r'^\s*<!-- generated.*?-->\s*$',si,re.M).group(0).strip()
    ri=re.search(r'<respStmt>.*?</respStmt>',si,re.S).group(0)
    so2=re.sub(r'^\s*<!-- generated.*?-->\s*$','    '+ci,so,count=1,flags=re.M)
    so2=re.sub(r'<respStmt>.*?</respStmt>',lambda m:ri,so2,count=1,flags=re.S)
    if so2!=so: open(o,'w',encoding='utf-8').write(so2); print('fixed',b)
