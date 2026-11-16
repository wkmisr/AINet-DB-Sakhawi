"""段階2 ★7〜★9（Waka 裁定 2026-11-17、すべて推奨 (a)）"""
import glob, re, os, csv, sys
ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
WHO = 'claude-office-followup'; DATE = '2026-11-17'
def path(a): return glob.glob(os.path.join(ROOT, f'Individuals/*/AIND-{a}_*.xml'))[0]
def fmt(r): return r if r.startswith(('wd:', 'gn:')) else '#' + r
log = []; T = {}
def edit(a, old, label=None, new=None, org=None, why=''):
    t = T.get(a) or open(path(a), encoding='utf-8').read(); hit = 0
    for m in list(re.finditer(r'([ \t]*)<state\b([^>]*)>(.*?)</state>', t, re.S)):
        attrs, body = m.group(2), m.group(3)
        r = re.search(r'ref="#?([^"]*)"', attrs)
        lab = (re.findall(r'<label xml:lang="ar">([^<]*)</label>', body) or [''])[0]
        if not r or r.group(1) != old or (label and lab != label): continue
        a2 = attrs.replace(r.group(0), f'ref="{fmt(new)}"', 1); b2 = body
        if org and '<orgName' not in b2:
            ind = m.group(1) + '    '
            b2 = re.sub(r'(<label xml:lang="ar-Latn">[^<]*</label>\n)', lambda x: x.group(1) + f'{ind}<orgName ref="{fmt(org[0])}">{org[1]}</orgName>\n', b2, count=1)
        t = t[:m.start()] + f'{m.group(1)}<state{a2}>{b2}</state>' + t[m.end():]
        log.append([a, lab, old, new, f'orgName {org[1]}' if org else '', why]); hit += 1
        break
    assert hit, (a, old, label)
    T[a] = t
# ★7 「الحجوبية」は原文どおり 00065 حاجب（規則25）
edit('D01619', 'TMP-O-00066', 'الحجوبية', 'TMP-O-00065', why='★7「ولي الحجوبية」＝حاجب（原文どおり、規則25）')
edit('D10379c', 'TMP-O-00066', 'حجوبية طرابلس', 'TMP-O-00065', why='★7「عمل حجوبية طرابلس」＝حاجب')
edit('D10379c', 'TMP-O-00066', 'حجوبية دمشق', 'TMP-O-00065', why='★7「ثم دمشق」＝حاجب')
# ★8 マディーナの خدام → 00353 خادم＋施設・場所
for a in ['D10026', 'D02815', 'D03031', 'D03335', 'D03396', 'D04299', 'D06053', 'D06379']:
    edit(a, 'TMP-O-00049', None, 'TMP-O-00353', why='★8 マディーナの「أحد خدام …」＝汎用 خادم＋施設・場所（規則65 (b)）')
edit('D02981', 'TMP-O-00049', None, 'TMP-O-00353', org=('TMP-I-00120', 'الحجرة النبوية'), why='★8「خدمة بالحجرة النبوية」＝汎用 خادم＋施設（預言者モスク内の預言者廟、TMP-I-00120）')
# ★9 شاد＋対象 → 00131（汎用 شاد）＋場所・施設
edit('D06328', 'TMP-O-00362', None, 'TMP-O-00131', why='★9「شاد الطور」＝汎用 شاد＋placeName الطور')
edit('D02158', 'TMP-O-00157', None, 'TMP-O-00131', org=('wd:Q12241647', 'الأشرفية'), why='★9「شاد أوقاف الاشرفية」＝汎用 شاد＋orgName الأشرفية（バルスバーイのマドラサ。本項主はその従兄弟）')
for a, t in T.items():
    note = '／'.join(f'state「{x[1]}」の ref {x[2]} → {x[3]}' + (f'、{x[4]}' if x[4] else '') + f'（{x[5]}）' for x in log if x[0] == a)
    resp = ('    <respStmt>\n        <resp xml:lang="ja">修正（官職 ID 整理 段階2・2026-11-17 Waka 裁定 ★7〜★9）</resp>\n'
            f'        <note xml:lang="ja">{note}</note>\n        <persName>{WHO}</persName>\n        <date when="{DATE}"/>\n    </respStmt>\n')
    i = t.rfind('</person>'); ls = t.rfind('\n', 0, i) + 1
    open(path(a), 'w', encoding='utf-8').write(t[:ls] + resp + t[ls:])
with open(os.path.join(ROOT, 'docs/accuracy/office_audit_20261116/stage2_rulings_applied.tsv'), 'w', encoding='utf-8', newline='') as fh:
    w = csv.writer(fh, delimiter='\t'); w.writerow(['aind', 'label', 'old_ref', 'new_ref', 'added', 'reason']); w.writerows(log)
print(len(log), 'changes in', len(T), 'files')
