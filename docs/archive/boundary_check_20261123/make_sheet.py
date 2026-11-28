import json,random,re,sys
from openpyxl import Workbook
from openpyxl.styles import Font,Alignment,PatternFill,Border,Side
from openpyxl.worksheet.datavalidation import DataValidation
ents=json.load(open('pages.json')); vols=json.load(open('vols.json'))['pages_per_vol']
# interpolate
prev=None
for e in ents:
    if e['vp']: prev=tuple(e['vp']); e['lo']=e['hi']=prev; e['est']=False
    else: e['lo']=prev; e['est']=True
nxt=None
for e in reversed(ents):
    if not e['est']: nxt=e['lo']
    else: e['hi']=nxt or e['lo']; e['lo']=e['lo'] or e['hi']
for e in ents:
    m=re.match(r'\s*(\d+)\s',e['head']); e['num']=int(m[1]) if m else None
    e['short']=' '.join(re.sub(r'^\s*\d+\s*','',e['head'].replace('★','')).split()[:9])
random.seed(20261123)
blocks=[]
def clean(v,s):
    for e in ents:
        if tuple(e['lo'])!=tuple(e['hi']) and tuple(e['lo'])<=(v,s+4) and tuple(e['hi'])>=(v,s): return False
    return True
for v in range(1,13):
    for _try in range(500):
        s=random.randint(5,vols[str(v)]-10)
        if clean(v,s): break
    blocks.append((v,s,s+4))
F=Font(name='Arial',size=11); B=Font(name='Arial',size=11,bold=True); AF=Font(name='Arial',size=13)
yel=PatternFill('solid',fgColor='FFF2CC'); gry=PatternFill('solid',fgColor='E7E6E6'); alt=PatternFill('solid',fgColor='F7F7F7'); warn=PatternFill('solid',fgColor='FCE4D6')
thin=Side(style='thin',color='999999'); bd=Border(left=thin,right=thin,top=thin,bottom=thin)
wb=Workbook(); ws=wb.active; ws.title='説明'
txt=[
('見出しの境界の検査（第1回：各巻から連続5頁、計60頁）',B),
('目的：コーパスの見出し（項の区切り）が刊本と合っているかを確かめる。見るのは「項がどこで始まるか」だけで、本文の語句の違いは対象外。',F),
('',F),
('手順',B),
('1. シート「頁ごと」を上から順に進める。刊本のその頁を開き、その頁で始まる項（本伝）の数を数えて、黄色の「刊本で始まる本伝の数」に入れる。',F),
('2. 右の「判定」が「一致」になれば、その頁は終わり。次の頁へ進む。',F),
('3. 「要確認」になった頁だけ、シート「見出しごと」でその頁の行を一つずつ刊本と見比べ、黄色の「判定」を選ぶ。',F),
('4. 刊本にあるのにコーパスにない項を見つけたら、シート「刊本にだけある項」に書く。',F),
('5. 1頁ごとに、かかった分数を「頁ごと」の「所要（分）」に入れる（全体を検査するかどうかの見積もりに使う）。',F),
('',F),
('数え方',B),
('・「本伝」は、刊本で番号が付いている項、または名前から始まる独立した項。「فلان . مضى في …」のような他の項へ送るだけの行（転送）は本伝に数えない。',F),
('・頁をまたぐ項は、始まった頁で数える。',F),
('・コーパス側の頁は、OpenITIの本文にある頁の記号から機械で求めた。各巻の最初の頁だけは、数を入れる前にシート「見出しごと」でその頁の最初の見出しを刊本と見比べ、頁付けが合っているかを確かめる。ずれていたら作業を止めて知らせてほしい。',F),
('・コーパス側の数は隠してある（先に見ると数え方が引きずられるため）。列を再表示しないこと。',F),
('・「頁」の欄が「推定」となっている見出しは、頁を前後の見出しから推し量ったもの（後から分割・追加した項）。',F),
('・オレンジ色の行は、立項番号が前の見出しから飛んでいる箇所。項が抜けているか、番号の読み違いの可能性があるので、特に注意して見る。',F),
('',F),
('記入するのは黄色の欄だけ。それ以外の欄は書き換えない。',B),
]
for i,(t,f) in enumerate(txt,1):
    c=ws.cell(i,1,t); c.font=f; c.alignment=Alignment(wrap_text=True,vertical='top')
ws.column_dimensions['A'].width=125
# sheets
pg=wb.create_sheet('頁ごと'); hd=wb.create_sheet('見出しごと'); ex=wb.create_sheet('刊本にだけある項')
ph=['巻','頁','コーパスの本伝の数','コーパスの転送の数','刊本で始まる本伝の数','判定','所要（分）','備考']
for j,h in enumerate(ph,1):
    c=pg.cell(1,j,h); c.font=B; c.fill=gry; c.border=bd; c.alignment=Alignment(wrap_text=True,vertical='center')
hh=['巻','頁','コーパスの行','ID','種別','立項番号','見出しの冒頭','判定','刊本の頁（違う場合）','備考']
for j,h in enumerate(hh,1):
    c=hd.cell(1,j,h); c.font=B; c.fill=gry; c.border=bd; c.alignment=Alignment(wrap_text=True,vertical='center')
kind={'$':'男性','$$':'女性','$$$':'転送'}
pr=2; hr=2; stats=[]
for bi,(v,s,t) in enumerate(blocks):
    for p in range(s,t+1):
        on=[e for e in ents if tuple(e['lo'])<=(v,p)<=tuple(e['hi'])]
        exact=[e for e in on if tuple(e['lo'])==tuple(e['hi'])]
        main=[e for e in exact if e['k']!='$$$']; ref=[e for e in exact if e['k']=='$$$']
        vals=[v,p,len(main),len(ref)]
        for j,x in enumerate(vals,1):
            c=pg.cell(pr,j,x); c.font=F; c.border=bd
            if bi%2: c.fill=alt
        pg.cell(pr,5).fill=yel; pg.cell(pr,5).border=bd
        c=pg.cell(pr,6,f'=IF(E{pr}="","",IF(E{pr}=C{pr},"一致","要確認"))'); c.font=F; c.border=bd
        for j in(7,8): pg.cell(pr,j).fill=yel; pg.cell(pr,j).border=bd; pg.cell(pr,j).font=F
        pr+=1
        lastnum=None
        for e in on:
            est=tuple(e['lo'])!=tuple(e['hi'])
            gap=e['num'] is not None and lastnum is not None and e['num']!=lastnum+1
            row=[v,f'{p}（推定）' if (est or e['est']) else p,e['line'],e['id'] or '（IDなし）',kind[e['k']],e['num'],e['short']]
            for j,x in enumerate(row,1):
                c=hd.cell(hr,j,x); c.font=AF if j==7 else F; c.border=bd
                if j==7: c.alignment=Alignment(horizontal='right',readingOrder=2)
                if gap: c.fill=warn
                elif p%2: c.fill=alt
            for j in(8,9,10): hd.cell(hr,j).fill=yel; hd.cell(hr,j).border=bd; hd.cell(hr,j).font=F
            if e['num'] is not None: lastnum=e['num']
            hr+=1
        stats.append((v,p,len(main),len(ref)))
dv=DataValidation(type='list',formula1='"一致,刊本に見出しなし（前の項の続き）,刊本では別の頁,刊本と名前が違う,その他"',allow_blank=True); hd.add_data_validation(dv); dv.add(f'H2:H{hr-1}')
for col,w in zip('ABCDEFGH',[6,8,12,12,16,12,10,50]): pg.column_dimensions[col].width=w
pg.column_dimensions['C'].hidden=True; pg.column_dimensions['D'].hidden=True
for col,w in zip('ABCDEFGHIJ',[6,12,10,16,8,10,60,28,14,40]): hd.column_dimensions[col].width=w
pg.freeze_panes='A2'; hd.freeze_panes='A2'; hd.auto_filter.ref=f'A1:J{hr-1}'
eh=['巻','頁','刊本の立項番号','項の冒頭の語句（刊本どおり）','直前のコーパスのID','直後のコーパスのID','備考']
for j,h in enumerate(eh,1):
    c=ex.cell(1,j,h); c.font=B; c.fill=gry; c.border=bd
for r in range(2,42):
    for j in range(1,8):
        c=ex.cell(r,j); c.fill=yel; c.border=bd; c.font=AF if j==4 else F
        if j==4: c.alignment=Alignment(horizontal='right',readingOrder=2)
for col,w in zip('ABCDEFG',[6,8,14,50,18,18,40]): ex.column_dimensions[col].width=w
wb.save(sys.argv[1])
print(blocks); print('pages',pr-2,'heading rows',hr-2,'main',sum(s[2] for s in stats),'ref',sum(s[3] for s in stats))
