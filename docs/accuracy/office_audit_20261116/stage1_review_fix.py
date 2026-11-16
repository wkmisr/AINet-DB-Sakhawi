"""PR #110 の独立校閲（claude-fable-5-2、2026-11-16）の指摘を反映"""
import glob, re, os, csv, sys
ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
WHO = 'claude-office-followup'; DATE = '2026-11-16'
def path(a): return glob.glob(os.path.join(ROOT, f'Individuals/*/AIND-{a}_*.xml'))[0]
log = []
def edit(aind, old_ref, label, new_ref=None, deputy=None, why='', extra_after=None):
    """aind の office state（old_ref かつ label 一致）を書き換える。"""
    p = path(aind); t = open(p, encoding='utf-8').read()
    pat = re.compile(r'([ \t]*)<state\b([^>]*)>(.*?)</state>', re.S)
    for m in pat.finditer(t):
        attrs, body = m.group(2), m.group(3)
        r = re.search(r'ref="#?([^"]+)"', attrs)
        lab = (re.findall(r'<label xml:lang="ar">([^<]*)</label>', body) or [''])[0]
        if not (r and r.group(1) == old_ref and lab == label and 'type="office"' in attrs): continue
        a2 = attrs
        if new_ref: a2 = a2.replace(r.group(0), 'ref="%s"' % (new_ref if new_ref.startswith('wd:') else '#' + new_ref), 1)
        if deputy and 'subtype=' not in a2: a2 = a2.replace('type="office"', 'type="office" subtype="deputy"', 1)
        new = f'{m.group(1)}<state{a2}>{body}</state>'
        if extra_after: new += '\n' + extra_after
        t = t[:m.start()] + new + t[m.end():]
        open(p, 'w', encoding='utf-8').write(t)
        log.append([aind, label, old_ref, new_ref or old_ref, 'deputy' if deputy else '', why])
        return
    raise SystemExit(f'not found: {aind} {old_ref} {label}')

# 1. 裁判代理官が 00053（総督の نائب）のままだったもの → 00096
for a, why in [('D01035', '「أحد النواب」＝裁判代理官'), ('D01394', '「ناب في الحكم」'), ('D01450', '「كان من موقعي الحكم بل ناب أيضا」'),
               ('D01658', '「أحد النواب」＝裁判代理官'), ('D01742', '「ممن استنابه المالكي」'), ('D01901', '「ناب عن ثانيهما في الأحكام」'),
               ('D07777', '「أحد النواب」＝裁判代理官'), ('D08027', '「أحد النواب」＝裁判代理官'), ('D01604', '「وناب في الحكم … بدمشق」')]:
    edit(a, 'TMP-O-00053', 'نائب', 'TMP-O-00096', why=why + '。00053（総督）ではなく نائب الحكم（規則65 (f)）')
# 2. 00318 を改名せず 00093 مشيخة الخدام の代理に
edit('D06034', 'TMP-O-00318', 'نائب شيخ الخدام بالحرم المدني', 'TMP-O-00093', why='本職 مشيخة الخدام（00093）＋代理（00318 は retired）')
edit('D02841', 'TMP-O-00053', 'نائب المشيخة بالمدينة النبوية', 'TMP-O-00093', deputy=True,
     why='マディーナのマシュヤハ＝宦官長（مشيخة الخدام、00093）の代理。本項主 خشكلدي は宦官名')
# 3. 代理なのに 00053／subtype 抜け
edit('D04268', 'TMP-O-00053', 'أحد من ناب عن ناظر الخاص', 'TMP-O-00085', deputy=True, why='ناظر الخاص（00085）の代理')
edit('D00801', 'TMP-O-00214', 'كتابة العلامة', deputy=True, why='「ناب عن والده في كتابة العلامة」')
edit('D02127', 'TMP-O-00053', 'نائب', 'TMP-O-00338', why='「نائب قلعة حلب」＝城塞司令（00338）。総督ではない')
# 5・6. 代理 → 本任、臨時の代行
ind = '    '
edit('D10305', 'wd:Q125482', 'الإمامة', deputy=True, why='「وأم نيابة عن أبيه ثم استقلالا」の前段（代理）。後段の本任を別 state に分けた',
     extra_after=f'{ind}<state type="office" ref="wd:Q125482">\n{ind}    <label xml:lang="ar">الإمامة</label>\n{ind}    <label xml:lang="ar-Latn">al-imāma</label>\n{ind}    <orgName ref="wd:Q312342">الأزهر</orgName>\n{ind}    <note xml:lang="ja">「ثم استقلالا」＝父の代理のあと本任（規則65 (f)、代理と本任は state を分ける）。</note>\n{ind}</state>')
edit('D08912a', 'wd:Q125482', 'الإمامة بمقام المالكية', deputy=True, why='「ناب في … الإمامة بمقام المالكية عن أبيه」の代理部分。「ثم استقل بنصف الإمامة」以降を別 state に分けた',
     extra_after=f'{ind}<state type="office" ref="wd:Q125482">\n{ind}    <label xml:lang="ar">الإمامة بمقام المالكية</label>\n{ind}    <label xml:lang="ar-Latn">al-imāma bi-maqām al-Mālikiyya</label>\n{ind}    <placeName ref="gn:104515">مكة</placeName>\n{ind}    <note xml:lang="ja">「ثم استقل بنصف الإمامة」以降の本任（半分の独立取得→罷免→復職）。代理部分は前の state（subtype="deputy"）。</note>\n{ind}</state>')
edit('D05724', 'wd:Q932945', 'خطيب', deputy=True, why='「خطب في جامع الأزهر مرات نيابة عني」＝サハーウィーの代行（見出しの「الخطيب」は通称）')

for a in sorted({x[0] for x in log}):
    items = [x for x in log if x[0] == a]
    note = '／'.join(f'state「{x[1]}」' + (f'の ref {x[2]} → {x[3]}' if x[2] != x[3] else '') + ('、subtype="deputy"' if x[4] else '') + f'（{x[5]}）' for x in items)
    p = path(a); t = open(p, encoding='utf-8').read()
    resp = ('    <respStmt>\n        <resp xml:lang="ja">修正（官職 ID 整理 PR #110 の独立校閲の反映・2026-11-16）</resp>\n'
            f'        <note xml:lang="ja">{note}</note>\n        <persName>{WHO}</persName>\n        <date when="{DATE}"/>\n    </respStmt>\n')
    i = t.rfind('</person>'); ls = t.rfind('\n', 0, i) + 1
    open(p, 'w', encoding='utf-8').write(t[:ls] + resp + t[ls:])
with open(os.path.join(ROOT, 'docs/accuracy/office_audit_20261116/stage1_review_fixes.tsv'), 'w', encoding='utf-8', newline='') as fh:
    w = csv.writer(fh, delimiter='\t'); w.writerow(['aind', 'label', 'old_ref', 'new_ref', 'deputy', 'reason']); w.writerows(log)
print(len(log), 'edits in', len({x[0] for x in log}), 'files')
