import json,re,sys
from openpyxl import Workbook
from openpyxl.styles import Font,Alignment,PatternFill,Border,Side
from openpyxl.worksheet.datavalidation import DataValidation
sel=json.load(open('/home/claude/work/gold10.json'))
txt=open('0__DawForAIND_renumbered_B54_split20260905.txt',encoding='utf-8').read().split('\n')
def body(line):
    out=[re.sub(r'^###\S+ \| \d+\$# \$+ ?','',txt[line-1])]
    i=line
    while i<len(txt) and not txt[i].startswith('###'):
        out.append(txt[i]); i+=1
    t=' '.join(out)
    t=re.sub(r'PageV\d+P\d+',' ',t); t=re.sub(r'ms\d+',' ',t)
    t=re.sub(r'[#~%]+',' ',t); return re.sub(r'\s+',' ',t).strip()
def chunks(t,n=700):
    out=[];cur=''
    for w in t.split(' '):
        if len(cur)+len(w)>n: out.append(cur); cur=w
        else: cur=(cur+' '+w).strip()
    if cur: out.append(cur)
    return out
F=Font(name='Arial',size=11); B=Font(name='Arial',size=11,bold=True); AF=Font(name='Arial',size=14)
yel=PatternFill('solid',fgColor='FFF2CC'); gry=PatternFill('solid',fgColor='E7E6E6')
thin=Side(style='thin',color='999999'); bd=Border(left=thin,right=thin,top=thin,bottom=thin)
wb=Workbook(); ws=wb.active; ws.title='説明'
rows=[
('原文からの正解づくり（試行用・10伝）',B),
('目的：新しいパイプラインの採点に使う正解を、モデルの出力や過去の裁定を見ずに原文から作る。',F),
('',F),
('守っていただきたいこと',B),
('1. この10伝について、アプリの出力、既存のXML、ビューアー、AIの回答を見ない。AIに本文を読ませない。',F),
('2. もう一人の担当者と相談しない（二人の結果を比べて、判断基準の曖昧な箇所を見つけるため）。',F),
('3. 人物の同定には、人物一覧（PersonList）とID-Masterの検索、および『ダウ』の本文そのものを使ってよい。',F),
('4. 史料から決められない場合は、無理に決めず「保留」と書く。保留は正しい答えの一つとして扱う。',F),
('5. 各伝の作業開始と終了の時刻を記入する（所要時間から、今後作れる件数を見積もる）。',F),
('',F),
('記入する場所：各シートの黄色の欄。1行に1項目。行が足りなければ下に足す。',B),
('種類：人物（被伝者以外で本文に出る人物すべて。匿名・「شيخنا」・「والده」なども含む）／関係／出来事／官職・身分／地名／年／著作。',F),
('本文の語句：本文からそのままコピーする。同じ語句が二度出る場合は、備考に「2回目」などと書く。',F),
('人物の同定：AIND-D番号またはTMP-P番号。該当がなければ「新規」、決められなければ「保留」、名前のない人物は「匿名」。',F),
('関係・出来事の種類：父、師、弟子、配偶者、聴講、イジャーザ、任官、巡礼、死去など。日本語で自由に書いてよい。',F),
('相手：関係や出来事にかかわる人物を、同じシートの行番号で示す（例：3）。被伝者は「本人」。',F),
('肯定／否定：サハーウィーがその記述を退けている場合は「否定」。地の文でない場合（引用・伝聞・自称）は、備考に誰の発言かを書く。',F),
('シート「記入例」は書き方の見本で、実在の伝記ではない（本文もIDも架空）。',F),
('対象の10伝はシート「一覧」を参照。本文は校合済みコーパスから、頁の記号などを除いて載せている。',F),
]
for i,(t,f) in enumerate(rows,1):
    c=ws.cell(i,1,t); c.font=f; c.alignment=Alignment(wrap_text=True,vertical='top')
ws.column_dimensions['A'].width=120
idx=wb.create_sheet('一覧')
for j,h in enumerate(['シート','層','ID','見出し種別','語数（概数）','コーパスの行'],1):
    c=idx.cell(1,j,h); c.font=B; c.fill=gry; c.border=bd
for i,(s,e) in enumerate(sel,2):
    for j,v in enumerate([f'{i-1:02d}_{e["id"][5:]}',s,e['id'],'女性' if e['k']=='$$' else '男性',e['w'],e['line']],1):
        c=idx.cell(i,j,v); c.font=F; c.border=bd
for col,w in zip('ABCDEF',[16,10,16,12,14,14]): idx.column_dimensions[col].width=w
cols=['行','種類','本文の語句（コピー）','人物の同定','関係・出来事の種類','相手（行番号）','年・地名など','肯定／否定','備考（迷った点、話者、何回目の出現か）']
widths=[6,14,40,18,22,14,18,12,50]
def sheet(name,ident,text,example=None,n=40):
    s=wb.create_sheet(name)
    s['A1']='ID'; s['B1']=ident; s['D1']='担当者'; s['E1'].fill=yel
    s['F1']='開始時刻'; s['G1'].fill=yel; s['H1']='終了時刻'; s['I1'].fill=yel
    for c in ('A1','B1','D1','F1','H1'): s[c].font=B
    r=2
    for ch in chunks(text):
        s.merge_cells(start_row=r,start_column=1,end_row=r,end_column=9); c=s.cell(r,1,ch); c.font=AF
        c.alignment=Alignment(wrap_text=True,vertical='top',horizontal='right',readingOrder=2)
        s.row_dimensions[r].height=max(40,len(ch)/120*22+10); r+=1
    h=r+1
    for j,(hd,w) in enumerate(zip(cols,widths),1):
        c=s.cell(h,j,hd); c.font=B; c.fill=gry; c.border=bd; c.alignment=Alignment(wrap_text=True,vertical='center')
        s.column_dimensions[chr(64+j)].width=w
    for i in range(n):
        rr=h+1+i
        c=s.cell(rr,1,i+1); c.font=F; c.border=bd
        for j in range(2,10):
            c=s.cell(rr,j); c.fill=yel; c.border=bd; c.font=AF if j==3 else F
            c.alignment=Alignment(wrap_text=True,vertical='top',horizontal='right' if j==3 else None,readingOrder=2 if j==3 else 0)
    if example:
        for i,row in enumerate(example):
            for j,v in enumerate(row,2): s.cell(h+1+i,j,v)
    dv=DataValidation(type='list',formula1='"人物,関係,出来事,官職・身分,地名,年,著作"',allow_blank=True); s.add_data_validation(dv); dv.add(f'B{h+1}:B{h+n}')
    dv2=DataValidation(type='list',formula1='"肯定,否定"',allow_blank=True); s.add_data_validation(dv2); dv2.add(f'H{h+1}:H{h+n}')
ex=[('人物','والده','AIND-D00000','','','','','父を指す。見本のIDは架空'),
    ('関係','وأخذ عن والده','','父','1','','肯定',''),
    ('人物','الشمس الفلاني','保留','','','','','同名の候補が二人いて決められない'),
    ('関係','وسمع على الشمس الفلاني','','聴講（師）','3','','肯定','著作名は書かれていない'),
    ('年','سنة بضع وثمانين','','','','بضع وثمانين','','没年。本文の表記のまま'),
    ('出来事','ومات','','死去','本人','行5の年','肯定','')]
sheet('記入例','（見本・架空）','（見本）فلان بن فلان الفلاني ولد بالقاهرة وسمع على الشمس الفلاني وأخذ عن والده ومات سنة بضع وثمانين .',ex,10)
for i,(s,e) in enumerate(sel,1):
    sheet(f'{i:02d}_{e["id"][5:]}',e['id'],body(e['line']),None,40 if e['w']<100 else 80 if e['w']<300 else 150)
wb.save(sys.argv[1])
