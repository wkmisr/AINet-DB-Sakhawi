"""官職 ID 整理の適用（Waka 裁定 2026-11-16）"""
import glob, re, json, os, sys, collections
ROOT = sys.argv[1]; W = '/home/claude/work/'
DATE, WHO = '2026-11-16', 'claude-opus-5-5-office-audit'
recs = json.load(open(W + 'office_records.json'))
NEWNUM = {'NEW-1': 'TMP-O-00402', 'NEW-2': 'TMP-O-00403', 'NEW-3': 'TMP-O-00404', 'NEW-4': 'TMP-O-00405',
          'NEW-5': 'TMP-O-00406', 'NEW-6': 'TMP-O-00407'}
# 場所・施設の記録が無い汎用化 15 件に補う要素（原文・旧 ID の表記から）
QUAL = {
 ('AIND-D00991', 'TMP-O-00215'): '<orgName xml:lang="ar">الركب العراقي</orgName>',
 ('AIND-D02779', 'TMP-O-00162'): '<orgName xml:lang="ar">الإسطبل</orgName>',
 ('AIND-D02792', 'TMP-O-00164'): '<orgName xml:lang="ar">مقام الشافعي</orgName>',
 ('AIND-D03398', 'TMP-O-00140'): '<orgName xml:lang="ar">أولاد أبي الليل</orgName>',
 ('AIND-D04971', 'TMP-O-00253'): '<orgName xml:lang="ar">درجة الكعبة</orgName>',
 ('AIND-D05600', 'TMP-O-00237'): '<orgName xml:lang="ar">الركب الشامي</orgName>',
 ('AIND-D05872', 'TMP-O-00306'): '<orgName xml:lang="ar">مقام المالكية</orgName>',
 ('AIND-D06019', 'TMP-O-00316'): '<orgName xml:lang="ar">قضاة الحنابلة</orgName>',
 ('AIND-D06164', 'TMP-O-00340'): '<orgName xml:lang="ar">الدولة</orgName>',
 ('AIND-D06164', 'TMP-O-00341'): '<orgName xml:lang="ar">الديوان المفرد</orgName>',
 ('AIND-D07378', 'TMP-O-00274'): '<orgName xml:lang="ar">زاوية داود الحكمي</orgName>',
 ('AIND-D07473', 'TMP-O-00281'): '<orgName xml:lang="ar">الجوالي</orgName>',
 ('AIND-D07477', 'TMP-O-00282'): '<placeName xml:lang="ar">فارسكور</placeName>',
 ('AIND-D08021', 'TMP-O-00356'): '<orgName xml:lang="ar">أوقاف الحنابلة</orgName>',
 ('AIND-D08061', 'TMP-O-00375'): '<orgName xml:lang="ar">الأحباس</orgName>',
}
def fmt(ref):
    return ref if ref.startswith('wd:') else '#' + ref
by_file = collections.defaultdict(list)
for r in recs: by_file[r['aind']].append(r)
log = []; files = 0
for aind, items in by_file.items():
    p = glob.glob(os.path.join(ROOT, f'Individuals/*/{aind}_*.xml'))[0]
    t = open(p, encoding='utf-8').read()
    notes = []
    for r in items:
        old = r['old']
        pat = re.compile(r'([ \t]*)<state\b([^>]*ref="(?:#|)' + re.escape(old) + r'"[^>]*)>(.*?)</state>\n?', re.S)
        hit = None
        for m in pat.finditer(t):
            lab = (re.findall(r'<label xml:lang="ar">([^<]*)</label>', m.group(3)) or [''])[0]
            if lab == r['label']: hit = m; break
        assert hit, (aind, old, r['label'])
        new = NEWNUM.get(r['new'], r['new'])
        if new == 'DELETE':
            t = t[:hit.start()] + t[hit.end():]
            notes.append(f'state「{r["label"]}」（{old}）を除去: {r["reason"]}')
        else:
            attrs = re.sub(r'ref="(?:#|)' + re.escape(old) + '"', f'ref="{fmt(new)}"', hit.group(2), count=1)
            body = hit.group(3)
            q = QUAL.get((aind, old))
            if q:
                ind = hit.group(1)
                body = body.rstrip() + f'\n{ind}    {q}\n{ind}'
            t = t[:hit.start()] + f'{hit.group(1)}<state{attrs}>{body}</state>\n' + t[hit.end():]
            notes.append(f'state「{r["label"]}」の ref {old} → {new}（{r["kind"]}: {r["reason"]}）' + ('。場所・施設を補った' if q else ''))
        log.append([aind, r['label'], old, new, r['kind'], r['reason']])
    # 削除後に state の n が飛ぶのは許容（n は目印）
    resp = ('    <respStmt>\n'
            '        <resp xml:lang="ja">修正（官職 ID の整理・2026-11-16 Waka 裁定）</resp>\n'
            f'        <note xml:lang="ja">{"／".join(notes)}</note>\n'
            f'        <persName>{WHO}</persName>\n'
            f'        <date when="{DATE}"/>\n'
            '    </respStmt>\n')
    i = t.rfind('</person>'); ls = t.rfind('\n', 0, i) + 1
    t = t[:ls] + resp + t[ls:]
    open(p, 'w', encoding='utf-8').write(t); files += 1
import csv
with open(W + 'office_changes_applied.tsv', 'w', encoding='utf-8', newline='') as fh:
    w = csv.writer(fh, delimiter='\t'); w.writerow(['aind', 'label', 'old_ref', 'new_ref', 'kind', 'reason']); w.writerows(log)
print('files', files, 'changes', len(log))
