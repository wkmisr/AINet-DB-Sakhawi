# -*- coding: utf-8 -*-
# B79-83 裁定反映（2026-09-15）: 名寄せ9件の repo 付替え＋D05035 父補填＋D00134 المناوي 是正
import re,glob,os,sys
REPO=os.path.expanduser('~/mnt/AINet-DB-Sakhawi/Individuals')
DATE='2026-09-15'
def stamp(s,note,resp='統合'):
    st=f'    <respStmt><resp xml:lang="ja">{resp}</resp><note xml:lang="ja">{note}</note><persName>claude-fable-5-1</persName><date when="{DATE}"/></respStmt>\n</person>'
    assert s.rstrip().endswith('</person>'),'no </person>'
    i=s.rstrip().rfind('</person>')
    return s[:i]+st+s[s.rstrip().rfind('</person>')+len('</person>'):]
def f(id_): 
    g=glob.glob(f'{REPO}/AIND-{id_}_*.xml'); assert len(g)==1,id_; return g[0]
def sub_attr(s,old,new):
    n=0
    for a in ('active','passive','ref','target'):
        s,k=re.subn(f'{a}="#{old}"',f'{a}="#{new}"',s); n+=k
    return s,n
MERGES={ # old TMP -> (AIND, label, files)
 'TMP-P-000354':('AIND-D08929','الغماري（الشمس محمد بن محمد بن علي بن عبد الرزاق الغماري المالكي النحوي、720–802）',['D00621']),
 'TMP-P-000631':('AIND-D08929','「علي الغماري」＝「سمع على الغماري」の綴り揺れ、人物としては الغماري 本人（TMP-P-000631 は取消）',['D02209','D02212']),
 'TMP-P-000077':('AIND-D01126','الشهاب الجوهري（أحمد بن عمر بن علي بن عبد الصمد البغدادي ثم القاهري「ويعرف بالجوهري」、725–809）',['D00134']),
 'TMP-P-000279':('AIND-D08290','محمد الغمري（الشمس محمد بن عمر بن أحمد الغمري ثم المحلي「ويعرف بالغمري」、786頃–849）',['D00104','D01114','D02327']),
 'TMP-P-000707':('AIND-D01456','أبو العباس الغمري（الشهاب أحمد بن محمد بن عمر الغمري الأصل المحلي「ويعرف بأبي العباس الغمري」）',['D02578']),
 'TMP-P-000694':('AIND-D04864','العفيف الناشري（عثمان بن عمر بن أبي بكر … العفيف الناشري المقري、804/5–848、『البستان الزاهر』著者）',['D03383','D04285']),
 'TMP-P-000603':('AIND-D06757','التقي الفاسي（محمد بن أحمد بن علي … التقي الفاسي المكي المالكي、没832）',['D00446','D01711','D02260','D02412','D02463','D02481','D02685','D02691','D02774','D03015','D03027','D03029','D03779','D03965','D05690']),
 'TMP-P-000614':('AIND-D07488','الشيخ محمد ابن صلح＝محمد بن صالح النمراوي ثم القاهري「ويعرف بابن صالح」（索引 D12453「ابن صالح محمد المعتقد」）',['D01559']),
 'TMP-P-000985':('AIND-D05438','الخطيب علي بن عبد الحق＝علي بن محمد بن عبد الحق نور الدين الغمري ثم القاهري الخطيب التاجر（جامع الغمري のハティーブ）',['D00666']),
}
log=[]
for old,(new,label,files) in MERGES.items():
    for id_ in files:
        p=f(id_); s=open(p,encoding='utf-8').read()
        s2,n=sub_attr(s,old,new); assert n>0,(old,id_)
        s2=stamp(s2,f'名寄せ（B79-83 §A-2、Waka 裁定 2026-09-15）: 暫定 {old} を corpus 本伝 #{new}（{label}）へ統合、属性 {n} 箇所を付替え。')
        open(p,'w',encoding='utf-8').write(s2); log.append((id_,old,new,n))
# D00134: المناوي D10313 -> D10815 (born 772, mujīz list = 8th-c generation)
p=f('D00134'); s=open(p,encoding='utf-8').read()
old_rel='<relation type="personal" subtype="teacher" n="48" active="#AIND-D10313" passive="#AIND-D00134">\n            <desc xml:lang="ar">المناوي</desc>'
assert old_rel in s
s=s.replace(old_rel,'<relation type="personal" subtype="teacher" n="48" active="#AIND-D10815" passive="#AIND-D00134">\n            <desc xml:lang="ar">المناوي</desc><note xml:lang="ja">المناوي ＝ #AIND-D10815（أبو بكر بن محمد بن إسحق … الشرف بن التاج السلمي المناوي الشافعي、760年以前生・没809）。伝主は772年生で、同列の授与者（التنوخي・ابن أبي المجد・الصردي 等）は8世紀後半の世代 → 798年生の الشرف يحيى المناوي（#AIND-D10313）ではない（B79-83 §D-10 の見直し、Waka 裁定 2026-09-15）。</note>')
s=stamp(s,'B79-83 §D-10 見直し（Waka 裁定 2026-09-15）: teacher n=48「المناوي」の #AIND-D10313 → #AIND-D10815（世代不整合＝D10313 は798年生）。','校閲')
open(p,'w',encoding='utf-8').write(s); log.append(('D00134','AIND-D10313','AIND-D10815',1))
# D05035: father -> D01414 (§D-9 ②)
p=f('D05035'); s=open(p,encoding='utf-8').read()
anchor='    </listRelation>'
assert s.count(anchor)==1
s=s.replace(anchor,'        <relation type="personal" subtype="father" n="3" active="#AIND-D01414" passive="#AIND-D05035"><desc xml:lang="ar">أحمد بن محمد بن علي بن درباس</desc><note xml:lang="ja">父 ＝ #AIND-D01414「أحمد بن محمد بن علي بن درباس شهاب الدين بن علاء الدين المصري . ذكره البقاعي في شيوخه」。見出しナサブ「علي بن أحمد بن محمد بن علي … بن درباس」と完全一致（原文に関係記述はなく見出しナサブによる補填＝規約5 ②、Waka 裁定 2026-09-15 §D-9）。兄弟 الفخر أحمد（#AIND-D00500）とも整合。</note></relation>\n'+anchor)
s=stamp(s,'B79-83 §D-9 裁定（2026-09-15）: 見出しナサブが corpus 本伝 #AIND-D01414 と一致する父の relation を補填（規約5 ②）。','校閲')
open(p,'w',encoding='utf-8').write(s); log.append(('D05035','-','AIND-D01414',1))
for l in log: print(*l)
print(len(log),'files')
