import re,json,glob,csv,random,sys
C='0__DawForAIND_renumbered_B54_split20260905.txt'
raw=open(C,encoding='utf-8',newline='').read()
nl='\r\n' if '\r\n' in raw else '\n'
L=raw.split(nl)
rows=json.load(open('/mnt/user-data/uploads/AINet-DB-Sakhawi/docs/_work/collation_marks_20261128/rows2.json'))
line={r[0]:r[1] for r in rows}
E={ # sid: [(old,new)]
's004':[('دريا±±±','دربا')],'s021':[('بمندة±±±','بسنده')],'s031':[('وتنكن±±±','وتنكد')],'s032':[('قلعة±±±','قطعة')],
's048':[('محالس من±±±','مجالس من')],'s074':[('التماية±±±','النسابة')],'s084':[('★و?★　','')],
's090':[('حب البلاد ★ووأدخل?★','حب البلادر وأدخل')],'s091':[('★الديراسطياري?★','الديراسطياري')],
's101':[('★علي بن قردم العلائي المذكور وأبوه في المائة قبلها★','علي بن قردم العلائي المذكور أبوه في المائة قبلها')],
's102':[('★على★_أحمد؟_ علي','على علي')],'s115':[('بحرأ عزير±±±','بحرا عزيز')],'s119':[('وبالناني±±±','وبالثاني')],
's121':[('الثنائي±±±','التتائي')],'s133':[('يذيح±±±','يذبح')],'s138':[('والضوا بطفأ±±± حضر','والضوابط فأحضر')],
's140':[('★وتآليف ?★','وتأليف')],'s157':[('بلدية±±±','بلديه')],'s162':[('بذله±±±','وبذله')],'s176':[('قياله±±±','فياله')],
's206':[('شرفى±±±','شرقي')],'s013':[('أملية±±±','أماليه')],'s025':[('انتمائه±±±','ائتمانه')],'s114':[('السنبكية±±±','السنبيكة')],
's203':[('الذكرى±±±','الدكري')],'s035':[('رثاه±±±','أباه')],'s036':[('قالته±±±','فاتته')],'s049':[('فقد±±±','حقد')],
's130':[('السل±±± هو','السلطان وهو')],'s135':[('اللآلا±±±','اللآلي')],'s136':[('المبان±±±','اللبان')],'s137':[('بخراسان±±±','بحراز')],
's173':[('قمة±±±','قبة')],'s209':[('الا±±±','الإنشاء')],'s149':[('ال±±±','ال ...')],
's152':[('★محمد بن علي★ [ُorder false_from here to no. 66] ','محمد بن علي')],'s153':[('محمد ★بن★ بن علي','محمد بن علي')],
's155':[('الحجار±±± （الحجاز؟）','الحجار')],'s156':[('وأجاز±±± （أجازت؟）','وأجاز')],'s200':[('إلى ★إلى★ أن','إلى أن')],
's233':[('بن ★بن ... أبي بكر','بن ... بن أبي بكر')],'s236':[('★ أخت ابن الزيادي ★','أخت ابني الزيادي')],
's237':[('★?1066 number★ ','')],
}
log=[]
for sid,ops in E.items():
    n=line[sid]; s=L[n-1]
    for old,new in ops:
        assert s.count(old)==1,(sid,n,old,s)
        s=s.replace(old,new)
    log.append((sid,n,L[n-1],s)); L[n-1]=s
# extra typo
assert 'ولعهلها' in L[137714]; L[137714]=L[137714].replace('ولعهلها','ولعلها')
# generic removal
star=[i for i,s in enumerate(L) if '★' in s or '±±±' in s]
special={80243,80268,107157,107187,101572}  # 0-based: handled below
for i in star:
    if i in special: continue
    s=L[i]; had=('★' in s)
    t=s.replace('±±±','').replace('★','')
    if had:
        m=re.match(r'(###\$.*?\$# \$+ (?:\d+ )?)?(.*)$',t,flags=re.S); head,body=m.group(1) or '',m.group(2)
        body=re.sub('[ 　]{2,}',' ',body).lstrip(' 　'); t=head+body
    if not any(l[1]==i+1 for l in log): log.append(('gen',i+1,s,t))
    else:
        for k,l in enumerate(log):
            if l[1]==i+1: log[k]=(l[0],l[1],l[2],t)
    L[i]=t
# --- structural 1: D07319 colophon (lines 80242-80269, 1-based)
assert L[80241].endswith('بعد أن وقف ما يملكه') and L[80243].startswith('?insert ★') and L[80268].endswith('★ من عقار على الخانقاه رحمه الله .')
body1=L[80241]+' من عقار على الخانقاه رحمه الله .'
col=L[80243:80269]; col[0]='| '+col[0].replace('?insert ★','',1); col[-1]=col[-1].replace(' ★ من عقار على الخانقاه رحمه الله .','')
assert not any('★' in x for x in col)
new1=[body1,'']+col
# --- structural 2: D09490 colophon (107155..107191)
assert L[107154].rstrip()=='الغفار بن حفاظ الدمشقي المزي .' and L[107157].startswith('insert? ★ ') and L[107187].endswith('★ المنيحي الخطيب . كتب')
h2='الغفار بن حفاظ الدمشقي المزي المنيحي الخطيب . كتب'
col2=L[107157:107188]; col2[0]='| '+col2[0].replace('insert? ★ ','',1); col2[-1]=col2[-1].replace(' ★ المنيحي الخطيب . كتب','')
col2=[x.replace('±±±','') for x in col2]; assert not any('★' in x for x in col2)
new2=[h2]+L[107188:107191]+['']+col2
assert L[107191]==''
# --- structural 3: D09086b
s=L[101572]; a,b=s.split(' 532　★محمد★ النجم'); assert a.endswith('بمكة .')
digits=set(re.findall(r'\b\d{12}\b',raw)); random.seed(20261128)
while True:
    pid=''.join(random.choice('0123456789') for _ in range(12))
    if pid not in digits and pid[0]!='0': break
new3=[a,'','###$AIND-D09086b | %s$# $ 532 محمد النجم%s'%(pid,b)]
# apply bottom-up
L[107154:107191]=new2
L[101572:101573]=new3
L[80241:80269]=new1
out=nl.join(L); assert '★' not in out and '±±±' not in out
open(C,'w',encoding='utf-8',newline='').write(out)
json.dump({'log':log,'pid':pid},open('/home/claude/work/applylog.json','w'),ensure_ascii=False)
print(len(log),pid,len(star))
