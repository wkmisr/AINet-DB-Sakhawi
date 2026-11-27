import csv,sys
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill,Alignment
csv.field_size_limit(10**9)
F=Font(name='Arial',size=11); B=Font(name='Arial',size=11,bold=True); g=PatternFill('solid',fgColor='E7E6E6')
wb=Workbook(); ws=wb.active; ws.title='説明'
for i,t in enumerate(['典拠表（草案、2026-11-23、PR #120）を見るための表。このファイルを直しても典拠表には反映されない。','',
 '「人物」「人物以外」：典拠表が持っている列だけを、そのまま表示している。',
 '「未解決の参照」：レコードの参照のうち、典拠表で有効なIDに行き着かないものの一覧（点検の結果で、典拠表の一部ではない）。',
 '「要裁定」：ID-Masterからそのまま取り込めなかった行（点検の結果で、典拠表の一部ではない）。','',
 '状態（status）の値：active＝有効／transfer＝転送項／merged＝別の番号に統合済み／retired＝廃止',
 'target：統合先または転送先のID。same_as：対応する外部ID。history：発行・修正の履歴。'],1):
    c=ws.cell(i,1,t); c.font=B if i==1 else F; c.alignment=Alignment(wrap_text=True)
ws.column_dimensions['A'].width=130
W={'name':55,'heading':45,'name_ar':40,'label_ar':36,'label_latn':30,'variants':30,'aliases':30,'history':40,'problem':60,'arabic':40,'examples':50,'heading':60,'note':70,'id':14,'n12':15,'target':14,'legacy_source':30,'value_source':24,'madhhab':22,'legacy_madhhab':22,'legacy_birth':16,'legacy_death':16}
for name,path in [('人物','authority/persons_registry.tsv'),('人物以外','authority/entities_registry.tsv'),('未解決の参照','authority/_generated/unresolved_refs.tsv'),('要裁定','authority/import_idmaster_rulings.tsv')]:
    s=wb.create_sheet(name)
    rows=list(csv.reader(open(path,encoding='utf-8',newline=''),delimiter='\t'))
    for i,r in enumerate(rows,1):
        for j,v in enumerate(r,1):
            c=s.cell(i,j,v); c.font=B if i==1 else F
            if i==1: c.fill=g
    for j,h in enumerate(rows[0],1): s.column_dimensions[s.cell(1,j).column_letter].width=W.get(h,12)
    s.freeze_panes='B2'; s.auto_filter.ref=s.dimensions
wb.save(sys.argv[1])
