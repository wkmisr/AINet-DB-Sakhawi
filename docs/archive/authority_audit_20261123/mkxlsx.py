import csv,collections,json
from openpyxl import Workbook
from openpyxl.styles import Font,Alignment,PatternFill,Border,Side
r=list(csv.reader(open('findings.tsv',encoding='utf-8'),delimiter='\t'))[1:]
EXP={
'P-DUP-CONTENT':('名前（3語以上）と生没年が別の行と同一','同じ人物の重複項か、書き込み先の誤りかを確認'),
'P-DATE-ORDER':('没年が生年より前、または差が110年超','どちらかの年を訂正'),
'P-DATE-RANGE':('年が600〜910の範囲外','年を訂正'),
'P-DATE-ARABIC':('生没年の欄にアラビア語の文字列（本文の切れ端を含む）','新しい典拠表では数値の幅に直す。機械変換の対象'),
'P-DATE-QUALIFIED':('生没年に ca・after・820s などの修飾や桁の不統一','新しい典拠表では数値の幅に直す'),
'P-HALF-BLANK':('12桁IDと名前の片方だけが空','転送・統合の印か記入漏れかを、状態の列で明示する'),
'P-MADHHAB-NAME':('名前に含まれる学派のニスバと、学派欄の値が違う','改宗・父祖のニスバ・記入誤りのどれかを目視で確認'),
'PC-NOT-IN-CORPUS':('人物一覧にあるがcorpusに見出しがない番号','統合済みなら状態の列に移す。注記のない2件は経緯を確認'),
'PC-BLANK-BUT-MAIN':('人物一覧では空欄（転送・統合の扱い）だが、corpusでは本伝','corpusの種別を $$$ に直すか、人物一覧を埋めるかを決める'),
'PC-FILLED-BUT-REF':('corpusでは転送項（$$$）だが、人物一覧には名前等が入っている','転送項の表し方を統一（状態の列）'),
'PC-NAME-MISMATCH':('人物一覧の名前の冒頭が、corpusの見出しの冒頭14語に現れない','多くは通称・ニスバの見出しで正常。目視で数件を抜き取り確認'),
'XP-DATE-DIFF':('生没年がXMLと人物一覧で違う','本文で確認してどちらかを訂正（100年ずれが多い）'),
'XP-DATE-PL-EMPTY':('XMLに生没年があるが人物一覧は空','YAML/XMLから人物一覧を自動生成すれば解消'),
'XP-DATE-XML-EMPTY':('人物一覧に生没年（数値）があるがXMLにない','本文で確認。XMLの取りこぼしの可能性'),
'XP-PL-BLANK':('通常のXMLがあるのに、人物一覧の行は空欄','どちらの扱いが正しいかを決める'),
'R-AIND-TO-REF':('XMLが転送項（$$$）のAIND番号を参照している','転送先の本伝の番号に付け替える'),
'R-TMP-UNKNOWN':('XMLが参照するTMP番号がID-Masterにない','番号の誤記か登録漏れかを確認'),
'R-WD-UNKNOWN':('XMLが参照するWikidata番号がID-Masterにない','ID-Masterに登録（学派などの定型値を含む）'),
'R-GN-UNKNOWN':('XMLが参照するGeoNames番号がID-Masterにない','ID-Masterに登録'),
'R-OTHER-FORM':('参照の書式が不正（#wd:、##AIND、# だけ、#NEEDED）','XMLを訂正'),
'R-NEEDID':('#NEEDID が残っているXMLの数','未同定として残す箇所。件数の把握のみ'),
'M-DUP-ID':('ID-Masterで同じIDが2行以上にある','行を一つにまとめる'),
'M-ID-FORMAT':('IDの書式が不正、またはCategoryとIDの種類が合わない','IDかCategoryを訂正'),
'M-NO-ID':('IDが空の行','IDを発行するか行を削除'),
'M-CATEGORY':('Categoryが空、または想定外の値','Categoryを記入'),
'M-SAME-LABEL':('同じCategoryで同じアラビア語表記に複数のID','重複登録かどうかを確認（別物なら注記）'),
'MP-AIND-NOT-IN-PL':('ID-MasterのPerson行のAIND番号が人物一覧にない','番号を訂正'),
}
order={'高':0,'中':1,'低':2}
c=collections.Counter((x[0],x[1],x[2]) for x in r)
F=Font(name='Arial',size=11); B=Font(name='Arial',size=11,bold=True)
gry=PatternFill('solid',fgColor='E7E6E6'); thin=Side(style='thin',color='999999'); bd=Border(left=thin,right=thin,top=thin,bottom=thin)
fill={'高':PatternFill('solid',fgColor='F8CBAD'),'中':PatternFill('solid',fgColor='FFE699'),'低':PatternFill('solid',fgColor='FFFFFF')}
wb=Workbook(); ws=wb.active; ws.title='概要'
s=json.load(open('summary.json'))
ws['A1']='典拠ファイルの全数点検（2026-11-23）'; ws['A1'].font=B
info=[('人物一覧（1. Sakhawi_PersonList）の行',s['pl']),('うち名前・12桁IDが空の行',s['pl_blank']),('corpusの見出し（AIND番号あり）',s['corp']),('corpusの見出し（AIND番号なしの転送項 $$$）',s['corp_noid']),('XMLファイル',s['xml']),('うち転送項のXML（REF_）',s['xml_ref']),('ID-MasterのID',s['im']),('検出した食い違いの総数',len(r))]
for i,(k,v) in enumerate(info,2):
    ws.cell(i,1,k).font=F; ws.cell(i,2,v).font=F
ws.cell(11,1,'重大度：高＝データが誤っているか壊れている／中＝人の判断が要る／低＝書式の不統一など、新しい典拠表に移すときに機械で直せるもの').font=F
h=['対象','コード','重大度','件数','何を見つけたか','直し方の案']
for j,x in enumerate(h,1):
    cc=ws.cell(13,j,x); cc.font=B; cc.fill=gry; cc.border=bd
row=14
for (a,code,sev),n in sorted(c.items(),key=lambda t:(order[t[0][2]],t[0][0],t[0][1])):
    e=EXP.get(code,('',''))
    for j,x in enumerate([a,code,sev,n,e[0],e[1]],1):
        cc=ws.cell(row,j,x); cc.font=F; cc.border=bd; cc.fill=fill[sev]; cc.alignment=Alignment(wrap_text=True,vertical='top')
    row+=1
for col,w in zip('ABCDEF',[20,20,8,8,60,60]): ws.column_dimensions[col].width=w
ws.column_dimensions['A'].width=44
al=wb.create_sheet('全件')
for j,x in enumerate(['対象','コード','重大度','ID・行','内容','対応（記入用）'],1):
    cc=al.cell(1,j,x); cc.font=B; cc.fill=gry; cc.border=bd
for i,x in enumerate(sorted(r,key=lambda x:(order[x[2]],x[0],x[1],x[3])),2):
    for j,v in enumerate(x,1):
        cc=al.cell(i,j,v); cc.font=F
        if j==3: cc.fill=fill[x[2]]
for col,w in zip('ABCDEF',[20,20,8,30,110,30]): al.column_dimensions[col].width=w
al.freeze_panes='A2'; al.auto_filter.ref=f'A1:F{len(r)+1}'
wb.save('/home/claude/AIND_authority_audit_20261123.xlsx')
print(len(r),collections.Counter(x[2] for x in r))
