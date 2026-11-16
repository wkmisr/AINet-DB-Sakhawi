"""段階1-3 の裁定（★1〜★5、Waka 2026-11-16）を Individuals に反映する"""
import glob, re, os, json, csv, collections, sys
ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
WHO = 'claude-office-followup'; DATE = '2026-11-16'
def fmt(ref): return ref if ref.startswith('wd:') else '#' + ref
# ID ごとの一括付け替え: 旧 → (新, 論点, 理由)
BY_ID = {
 'TMP-O-00003': ('TMP-O-00096', '★1', 'نائب القاضي＝نائب الحكم（2026-07-11 の裁定どおり 00096 に一本化）'),
 'TMP-O-00036': ('wd:Q352842', '★2', 'مدرس＝تدريس'),
 'TMP-O-00170': ('TMP-O-00077', '★3', 'شيخ الصوفية（施設に属さない長）を 00077 に統合'),
 'TMP-O-00136': ('TMP-O-00016', '★4', 'أمير أربعين＝أمير طبلخاناه'),
 'TMP-O-00176': ('TMP-O-00124', '★4', 'أمر المكس＝متولي المكس'),
 'TMP-O-00001': ('TMP-O-00229', '★4', 'الوقيد＝الوقاد'),
 'TMP-O-00043': ('TMP-O-00058', '★5', 'كاتب التوقيع＝موقع'),
}
# 記録ごとの付け替え（BY_ID より優先）: (aind, 旧) → (新, 論点, 理由)
BY_REC = {
 ('D00438', 'TMP-O-00077'): ('wd:Q7492880', '★3', '施設のマシュヤハ＝汎用 مشيخة＋orgName'),
 ('D00443', 'TMP-O-00077'): ('wd:Q7492880', '★3', '施設のマシュヤハ＝汎用 مشيخة＋orgName'),
 ('D03528', 'TMP-O-00077'): ('wd:Q7492880', '★3', '施設のマシュヤハ＝汎用 مشيخة＋orgName'),
 ('D02853', 'TMP-O-00077'): ('wd:Q7492880', '★3', 'ハーンカーのマシュヤハ＝汎用 مشيخة＋orgName（سرياقوس と同じ扱い）'),
 ('D02991', 'TMP-O-00170'): ('wd:Q7492880', '★3', '施設のマシュヤハ＝汎用 مشيخة＋場所'),
 ('D00449', 'TMP-O-00043'): ('TMP-O-00078', '★5', '「كتب التوقيع بباب ابن خطيب الناصرية」＝法廷の書記'),
 ('D07777', 'TMP-O-00043'): ('TMP-O-00078', '★5', '「عمل التوقيع ببابه」（البلقيني）＝法廷の書記'),
 ('D03128', 'TMP-O-00058'): ('TMP-O-00078', '★5', '「كان موقعا ببابه」（القاضي سعد الدين）＝法廷の書記'),
 ('D04490', 'TMP-O-00058'): ('TMP-O-00078', '★5', '「من قدماء موقعيها」（الصالحية）＝法廷の書記'),
}
log = []; files = 0; used = set()
for p in sorted(glob.glob(os.path.join(ROOT, 'Individuals/*/AIND-D*.xml'))):
    aind = re.search(r'AIND-(D\w+?)_', p).group(1)
    t = open(p, encoding='utf-8').read(); notes = []
    def sub(m):
        attrs, body = m.group(1), m.group(2)
        r = re.search(r'ref="#?(TMP-O-\d{5})"', attrs)
        if not r or 'type="office"' not in attrs: return m.group(0)
        old = r.group(1)
        hit = BY_REC.get((aind, old)) or BY_ID.get(old)
        if not hit: return m.group(0)
        if (aind, old) in BY_REC: used.add((aind, old))
        new, k, why = hit
        lab = (re.findall(r'<label xml:lang="ar">([^<]*)</label>', body) or [''])[0]
        notes.append(f'state「{lab}」の ref {old} → {new}（{k}: {why}）')
        log.append(['AIND-' + aind, lab, old, new, k, why])
        return '<state' + attrs.replace(r.group(0), f'ref="{fmt(new)}"', 1) + '>' + body + '</state>'
    t2 = re.sub(r'<state\b([^>]*)>(.*?)</state>', sub, t, flags=re.S)
    if t2 == t: continue
    resp = ('    <respStmt>\n'
            '        <resp xml:lang="ja">修正（官職 ID の統合し漏れ・2026-11-16 Waka 裁定）</resp>\n'
            f'        <note xml:lang="ja">{"／".join(notes)}</note>\n'
            f'        <persName>{WHO}</persName>\n'
            f'        <date when="{DATE}"/>\n'
            '    </respStmt>\n')
    i = t2.rfind('</person>'); ls = t2.rfind('\n', 0, i) + 1
    t2 = t2[:ls] + resp + t2[ls:]
    open(p, 'w', encoding='utf-8').write(t2); files += 1
assert used == set(BY_REC), set(BY_REC) - used
with open(os.path.join(ROOT, 'docs/accuracy/office_audit_20261116/stage1_changes_applied.tsv'), 'w', encoding='utf-8', newline='') as fh:
    w = csv.writer(fh, delimiter='\t'); w.writerow(['aind', 'label', 'old_ref', 'new_ref', 'item', 'reason']); w.writerows(log)
print('files', files, 'changes', len(log), collections.Counter(x[4] for x in log))
