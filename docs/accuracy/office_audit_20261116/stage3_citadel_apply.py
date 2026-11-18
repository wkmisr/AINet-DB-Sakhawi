"""城塞の表し方（Waka 裁定 2026-11-18）: 城塞は場所（placeName）として書き、
場所の欄には都市ではなく城塞そのものを入れる。"""
import glob, re, os, sys
ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
WHO = 'claude-office-followup'; DATE = '2026-11-18'
def path(a): return glob.glob(os.path.join(ROOT, f'Individuals/*/AIND-{a}_*.xml'))[0]
FIX = [  # (aind, state n, 置き換え前の場所要素（正規表現）, 置き換え後, 理由)
 ('D02246', 3, r'<placeName ref="gn:293100">صفد</placeName>', '<placeName ref="#TMP-L-00417">قلعة صفد</placeName>', 'صفد → قلعة صفد（新規 TMP-L-00417）'),
 ('D02246', 6, r'<placeName ref="gn:170654">دمشق</placeName>', '<placeName ref="#TMP-L-00328">قلعة دمشق</placeName>', 'دمشق → قلعة دمشق（TMP-L-00328）'),
 ('D03289', 2, r'<placeName ref="gn:170654">دمشق</placeName>', '<placeName ref="#TMP-L-00328">قلعة دمشق</placeName>', 'دمشق → قلعة دمشق（TMP-L-00328）'),
 ('D05176', 1, r'<placeName ref="gn:170654">دمشق</placeName>', '<placeName ref="#TMP-L-00328">قلعة دمشق</placeName>', 'دمشق → قلعة دمشق（TMP-L-00328）'),
 ('D06214', 1, r'<placeName ref="gn:170063">حلب</placeName>', '<placeName ref="wd:Q206231">قلعة حلب</placeName>', 'حلب → قلعة حلب（wd:Q206231）'),
 ('D06142', 1, r'<placeName ref="gn:170654">دمشق</placeName>\s*<placeName ref="#TMP-L-00328">القلعة</placeName>', '<placeName ref="#TMP-L-00328">قلعة دمشق</placeName>', 'دمشق と القلعة の二つ → قلعة دمشق（TMP-L-00328）一つに'),
 ('D04661', 4, r'<placeName ref="gn:170063">حلب</placeName>\s*<orgName ref="wd:Q206231">قلعة حلب</orgName>', '<placeName ref="wd:Q206231">قلعة حلب</placeName>', 'placeName حلب と orgName قلعة حلب → placeName قلعة حلب（wd:Q206231）一つに'),
]
done = {}
for a, n, pat, rep, why in FIX:
    p = path(a); t = done.get(a) or open(p, encoding='utf-8').read()
    m = [x for x in re.finditer(r'<state\b[^>]*>.*?</state>', t, re.S) if f'n="{n}"' in x.group(0).split('>')[0]][0]
    s2, k = re.subn(pat, rep, m.group(0), count=1); assert k == 1, (a, n)
    done[a] = t[:m.start()] + s2 + t[m.end():]
    done.setdefault('_n_' + a, []).append(f'state n={n} の場所: {why}')
for a in [k for k in done if not k.startswith('_n_')]:
    t = done[a]; note = '／'.join(done['_n_' + a])
    rs = ('    <respStmt>\n        <resp xml:lang="ja">修正（城塞は場所として書く・2026-11-18 Waka 裁定）</resp>\n'
          f'        <note xml:lang="ja">{note}。場所の欄には都市ではなく城塞そのものを入れる（規則65 (i)）。</note>\n'
          f'        <persName>{WHO}</persName>\n        <date when="{DATE}"/>\n    </respStmt>\n')
    i = t.rfind('</person>'); ls = t.rfind('\n', 0, i) + 1
    open(path(a), 'w', encoding='utf-8').write(t[:ls] + rs + t[ls:])
print('ok')
