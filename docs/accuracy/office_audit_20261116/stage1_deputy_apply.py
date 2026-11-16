"""段階1-4 ★6（Waka 2026-11-16 (b)）: 代理職は本職 ID＋<state subtype="deputy">"""
import glob, re, os, csv, sys
ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
WHO = 'claude-office-followup'; DATE = '2026-11-16'
def fmt(ref): return ref if ref.startswith('wd:') or ref == '#NEEDID' else '#' + ref
# 代理専用 ID → 本職 ID（ID ごと）
BY_ID = {'TMP-O-00207': 'TMP-O-00055', 'TMP-O-00285': 'wd:Q125482', 'TMP-O-00125': 'TMP-O-00100'}
KEEP_ID = {'TMP-O-00318'}  # 00318 は本職「شيخ الخدام بالحرم المدني」に改名し、代理は subtype で表す
# 本職 ID のまま「نائب／نيابة」のラベルを持つ記録（ref はそのまま、subtype を付ける）
BY_REC = {('D10087', 'wd:Q125482'), ('D02659', 'wd:Q125482'), ('D03724', 'wd:Q125482'),
          ('D02706', 'TMP-O-00032'), ('D07647', 'TMP-O-00032'), ('D05973', 'TMP-O-00045'),
          ('D05985', 'TMP-O-00067'), ('D06071', 'wd:Q932945'), ('D07144', 'wd:Q7492880'),
          ('D07863', 'wd:Q239718'), ('D07962', 'TMP-O-00163'), ('D07095', 'NEEDID')}
DEP = re.compile(r'نائب|نيابة|ناب|نواب|ينوب')
log = []; files = 0; used = set()
for p in sorted(glob.glob(os.path.join(ROOT, 'Individuals/*/AIND-D*.xml'))):
    aind = re.search(r'AIND-(D\w+?)_', p).group(1)
    t = open(p, encoding='utf-8').read(); notes = []
    def sub(m):
        attrs, body = m.group(1), m.group(2)
        if 'type="office"' not in attrs or 'subtype=' in attrs: return m.group(0)
        r = re.search(r'ref="#?([^"]+)"', attrs)
        if not r: return m.group(0)
        old = r.group(1)
        lab = (re.findall(r'<label xml:lang="ar">([^<]*)</label>', body) or [''])[0]
        if old in BY_ID: new = BY_ID[old]
        elif old in KEEP_ID: new = old
        elif (aind, old) in BY_REC and DEP.search(lab): new = old; used.add((aind, old))
        else: return m.group(0)
        a2 = attrs.replace(r.group(0), f'ref="{fmt(new)}"', 1).replace('type="office"', 'type="office" subtype="deputy"', 1)
        notes.append(f'state「{lab}」を代理職として subtype="deputy" を付けた' + (f'（ref {old} → {new}）' if new != old else ''))
        log.append(['AIND-' + aind, lab, old, new])
        return '<state' + a2 + '>' + body + '</state>'
    t2 = re.sub(r'<state\b([^>]*)>(.*?)</state>', sub, t, flags=re.S)
    if t2 == t: continue
    resp = ('    <respStmt>\n'
            '        <resp xml:lang="ja">修正（代理職の書き方・2026-11-16 Waka 裁定 ★6 (b)）</resp>\n'
            f'        <note xml:lang="ja">{"／".join(notes)}</note>\n'
            f'        <persName>{WHO}</persName>\n'
            f'        <date when="{DATE}"/>\n'
            '    </respStmt>\n')
    i = t2.rfind('</person>'); ls = t2.rfind('\n', 0, i) + 1
    t2 = t2[:ls] + resp + t2[ls:]
    open(p, 'w', encoding='utf-8').write(t2); files += 1
assert used == BY_REC, BY_REC - used
with open(os.path.join(ROOT, 'docs/accuracy/office_audit_20261116/stage1_deputy_applied.tsv'), 'w', encoding='utf-8', newline='') as fh:
    w = csv.writer(fh, delimiter='\t'); w.writerow(['aind', 'label', 'old_ref', 'new_ref']); w.writerows(log)
print('files', files, 'changes', len(log))
