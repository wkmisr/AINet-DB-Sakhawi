"""段階2（機械的に直せるもの、2026-11-17）。نائب مكة は Waka 了承 2026-11-17。"""
import glob, re, os, csv, sys
ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
WHO = 'claude-office-followup'; DATE = '2026-11-17'
def path(a): return glob.glob(os.path.join(ROOT, f'Individuals/*/AIND-{a}_*.xml'))[0]
def fmt(r): return r if r.startswith(('wd:', 'gn:')) else '#' + r
log = []; T = {}
def get(a):
    if a not in T: T[a] = open(path(a), encoding='utf-8').read()
    return T[a]
def states(t):
    return list(re.finditer(r'([ \t]*)<state\b([^>]*)>(.*?)</state>', t, re.S))
def edit(a, n, new_ref=None, deputy=False, add_note=None, org=None, why=''):
    """state n="n" を書き換える。org=(旧 ref または None, 新 ref) で orgName の ref を直す。"""
    t = get(a)
    for m in states(t):
        if f'n="{n}"' not in m.group(2) or 'type="office"' not in m.group(2): continue
        attrs, body = m.group(2), m.group(3)
        old = (re.search(r'ref="#?([^"]*)"', attrs) or [None, ''])[1]
        a2 = attrs
        if new_ref:
            if 'ref=' in a2: a2 = re.sub(r'ref="[^"]*"', f'ref="{fmt(new_ref)}"', a2, 1)
            else: a2 = a2 + f' ref="{fmt(new_ref)}"'
        if deputy and 'subtype=' not in a2: a2 = a2.replace('type="office"', 'type="office" subtype="deputy"', 1)
        b2 = body
        if org:
            o_old, o_new = org
            b2 = re.sub(r'<orgName( ref="[^"]*")?( xml:lang="ar")?>', f'<orgName ref="{fmt(o_new)}">', b2, 1)
        if add_note:
            ind = m.group(1) + '    '
            if '<note xml:lang="ja">' in b2:
                b2 = re.sub(r'(<note xml:lang="ja">)(.*?)(</note>)', lambda x: x.group(1) + x.group(2) + add_note + x.group(3), b2, 1, flags=re.S)
            else:
                b2 = b2.rstrip() + f'\n{ind}<note xml:lang="ja">{add_note}</note>\n{m.group(1)}'
        lab = (re.findall(r'<label xml:lang="ar">([^<]*)</label>', body) or [''])[0]
        T[a] = t[:m.start()] + f'{m.group(1)}<state{a2}>{b2}</state>' + t[m.end():]
        log.append([a, lab, old or '(なし)', new_ref or old or '(なし)', 'deputy' if deputy else '', f'orgName→{org[1]}' if org else '', why])
        return
    raise SystemExit(f'state n={n} not found in {a}')
def add_state(a, after_n, xml, lab, ref, why, deputy=False):
    t = get(a); ms = states(t)
    nmax = max([int(x) for x in re.findall(r'<state n="(\d+)"', t)] or [0])
    xml = xml.replace('N__', str(nmax + 1))
    if ms:
        m = ms[-1] if after_n is None else [x for x in ms if f'n="{after_n}"' in x.group(2)][0]
        T[a] = t[:m.end()] + '\n' + xml + t[m.end():]
    else:
        i = t.find('    <event'); i = i if i >= 0 else t.find('    <note type="source"')
        T[a] = t[:i] + xml + '\n' + t[i:]
    log.append([a, lab, '(新規 state)', ref, 'deputy' if deputy else '', '', why])
S = '    '
# ---- نائب مكة（シャリーフ配下の常設のナーイブ＝00053＋مكة。Waka 了承 2026-11-17）
edit('D00744', 1, add_note='「نائب مكة للسيد بركات ثم لولده」＝マッカのアミール（シャリーフ بركات、のちその子）の下で町を預かるナーイブ。常設の職として 00053＋مكة（D07962「ناب في إمرة مكة」＝アミール職の代行とは別。2026-11-17 Waka 了承）。', why='誰のナーイブかを注記')
edit('D07433', 2, add_note=' 「نائب مكة عن السيد بركات」＝シャリーフ بركات の下のナーイブ（常設の職、00053＋مكة。2026-11-17 Waka 了承）。', why='誰のナーイブかを注記')
edit('D06050', 1, deputy=True, add_note=' 兄 مسعود が持つナーイブ職の代理なので subtype="deputy"（2026-11-17 Waka 了承）。', why='「ناب عن أخيه في نيابة مكة」＝兄のナーイブ職の代理')
add_state('D06371', 1, f'{S}<state n="N__" type="office" ref="#TMP-O-00053">\n{S}    <label xml:lang="ar">نائب مكة</label>\n{S}    <label xml:lang="ar-Latn">nāʾib Makka</label>\n{S}    <placeName ref="gn:104515">مكة</placeName>\n{S}    <note xml:lang="ja">見出し「مولى السيد حسن بن عجلان نائب مكة」＝シャリーフ حسن بن عجلان の下のナーイブ（常設の職、00053＋مكة。2026-11-17 Waka 了承）。記録が抜けていたので追加。</note>\n{S}</state>', 'نائب مكة', 'TMP-O-00053', '見出しの「نائب مكة」の記録が抜けていた')
# ---- 既存の欠落
add_state('D00524', 1, f'{S}<state n="N__" type="office" ref="#TMP-O-00096">\n{S}    <label xml:lang="ar">نائب الحكم</label>\n{S}    <label xml:lang="ar-Latn">nāʾib al-ḥukm</label>\n{S}    <note xml:lang="ja">「ثم استنابه العز الكناني في العقود والفسوخ ثم في القضاء」＝カーディー العز الكناني の代理（はじめ契約・解消の取り扱い、のち裁判全般）。نائب الحكم は固有 ID（規則65 (f) の例外）。記録が抜けていたので追加。</note>\n{S}</state>', 'نائب الحكم', 'TMP-O-00096', '「استنابه العز الكناني … في القضاء」の記録が抜けていた')
add_state('D06298', None, f'{S}<state n="N__" type="office" subtype="deputy" ref="#TMP-O-00063">\n{S}    <label xml:lang="ar">الدوادارية الثانية (نيابة عن أخيه جانم)</label>\n{S}    <label xml:lang="ar-Latn">al-dawādāriyya al-thāniya</label>\n{S}    <note xml:lang="ja">「ممن ناب عن أخيه جانم في الدوادارية الثانية حين عينت له وهو بحلب」＝兄 جانم に任じられた第二ダワーダール職を、兄がアレッポにいる間代理した。本職 دوادار（00063）＋deputy（規則65 (f)）。官職の記録がなかったので追加。</note>\n{S}</state>', 'الدوادارية الثانية', 'TMP-O-00063', '官職の記録がなかった', deputy=True)
# ---- ref のない office state
W = '（ref がなかった state に既存 ID を付けた）'
edit('D00592', 1, 'TMP-O-00236', why='الخباز＝00236 الفران | الخباز' + W)
edit('D00599', 3, 'TMP-O-00211', why='أمانة الحكم＝00211' + W)
edit('D00809', 1, 'TMP-O-00409', why='「البدر النسابة」＝系譜学者。新規 TMP-O-00409（規則65 (a) の学識の称と同じ扱い）')
edit('D01013', 1, 'TMP-O-00077', why='「الرفاعي … شيخ طائفته」＝施設に属さないスーフィー教団の長（00077、先例 D08924a）')
edit('D01186', 1, 'TMP-O-00408', why='「ملقن الأموات بها」（マディーナ）＝葬送時のタルキーン役。新規 TMP-O-00408')
edit('D01338', 1, 'TMP-O-00163', why='صاحب بجاية＝00163 صاحب البلد＋placeName' + W)
edit('D01524', 2, 'TMP-O-00171', why='قراءة الجوق＝00171 قارئ الجوق' + W)
edit('D01819', 1, 'TMP-O-00091', why='جابي＝00091' + W)
edit('D08929b', 2, 'TMP-O-00108', why='「استقر في نوبة بالبيمارستان」＝病院の当番医。00108 طبيب＋orgName' + W)
edit('D08929b', 3, 'TMP-O-00108', why='「… وتربة برقوق」＝バルクーク廟の当番医。00108 طبيب＋orgName' + W)
W2 = '（#NEEDID だったものを規則65 の汎用 ID に）'
edit('D03400', 1, 'TMP-O-00163', why='صاحب صنعاء＝00163＋placeName' + W2)
edit('D03463', 1, 'TMP-O-00177', why='「ملك اليمن بعد أبيه」＝00177 ملك＋placeName' + W2)
edit('D03463', 2, 'TMP-O-00032', why='「اشتغل بالنظر في مدارس وغيرها」＝00032 ناظر' + W2)
edit('D03437', 1, 'TMP-O-00032', why='「ولي نظر المسجد الحرام المكي」＝00032 ناظر＋orgName' + W2)
# ---- 汎用化を保留していた複合職のうち、規則65 (b) どおりに決まるもの
edit('D03890', 1, 'TMP-O-00082', why='استيفاء البيمارستان＝00082 مستوفي＋orgName（00025 は retired）')
edit('D04661', 4, 'TMP-O-00032', why='نظر القلعة（حلب）＝00032 ناظر＋orgName（00290 は retired）')
edit('D05973', 1, 'TMP-O-00032', why='نظر قلعة دمشق＝00032 ناظر＋場所（00290 は retired）')
# ---- 誤った orgName の ref
edit('D00464', 1, org=('TMP-I-00050', 'TMP-I-00290'), why='ضريح الليث の ref が TMP-I-00050（ديوان السلطان）だった。新規 TMP-I-00290')
edit('D01670', 1, org=('TMP-I-00054', 'TMP-I-00068'), why='الجوق の ref が TMP-I-00054（الفاضلية）だった。既存 TMP-I-00068 الجوق')
edit('D01999', 1, org=('TMP-I-00010', 'TMP-I-00061'), why='جامع المقسي の ref が TMP-I-00010（المسجد المعروف بابن طلحة）だった。既存 TMP-I-00061')
edit('D01999', 3, org=('TMP-I-00054', 'TMP-I-00291'), why='حانوت الدكة の ref が TMP-I-00054（الفاضلية）だった。新規 TMP-I-00291')

for a in sorted(T):
    items = [x for x in log if x[0] == a]
    note = '／'.join(f'state「{x[1]}」' + (f' ref {x[2]} → {x[3]}' if x[2] != x[3] else '') + (f'、{x[5]}' if x[5] else '') + ('、subtype="deputy"' if x[4] else '') + f'（{x[6]}）' for x in items)
    t = T[a]
    resp = ('    <respStmt>\n        <resp xml:lang="ja">修正（官職 ID 整理 段階2・2026-11-17）</resp>\n'
            f'        <note xml:lang="ja">{note}</note>\n        <persName>{WHO}</persName>\n        <date when="{DATE}"/>\n    </respStmt>\n')
    i = t.rfind('</person>'); ls = t.rfind('\n', 0, i) + 1
    open(path(a), 'w', encoding='utf-8').write(t[:ls] + resp + t[ls:])
with open(os.path.join(ROOT, 'docs/accuracy/office_audit_20261116/stage2_changes_applied.tsv'), 'w', encoding='utf-8', newline='') as fh:
    w = csv.writer(fh, delimiter='\t'); w.writerow(['aind', 'label', 'old_ref', 'new_ref', 'deputy', 'orgName', 'reason']); w.writerows(log)
print(len(log), 'changes in', len(T), 'files')
