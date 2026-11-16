"""独立校閲（Fable、2026-11-16）の指摘の反映"""
import glob, re, os, sys
ROOT = sys.argv[1]; DATE, WHO = '2026-11-16', 'claude-opus-5-5-relation-unify'
def path(a): return glob.glob(os.path.join(ROOT, f'Individuals/*/AIND-{a}_*.xml'))[0]
def add_resp(t, note, resp='修正（独立校閲の指摘の反映・2026-11-16）'):
    r = ('    <respStmt>\n' f'        <resp xml:lang="ja">{resp}</resp>\n' f'        <note xml:lang="ja">{note}</note>\n'
         f'        <persName>{WHO}</persName>\n' f'        <date when="{DATE}"/>\n' '    </respStmt>\n')
    i = t.rfind('</person>'); ls = t.rfind('\n', 0, i) + 1
    return t[:ls] + r + t[ls:]
def append_note(t, tag_pat, note):
    m = re.search(r'(<relation [^>]*' + tag_pat + r'[^>]*>)(.*?)(</relation>)', t, re.S)
    assert m, tag_pat
    body = m.group(2)
    ins = (f'<note xml:lang="ja">{note}</note>')
    if '\n' in body:
        new = m.group(1) + body.rstrip(' ') + '    ' + ins + '\n        ' + m.group(3)
    else:
        new = m.group(1) + body + ins + m.group(3)
    return t[:m.start()] + new + t[m.end():]

# A-1 D02097: 「ممن يتردد له الصلاح الطرابلسي ليقرئه」＝الصلاح が師
p = path('D02097'); t = open(p, encoding='utf-8').read()
old = 'subtype="teacher" n="1" active="#AIND-D02097" passive="#AIND-D09344"'
assert t.count(old) == 1
t = t.replace(old, 'subtype="teacher" n="1" active="#AIND-D09344" passive="#AIND-D02097"')
t = append_note(t, r'active="#AIND-D09344" passive="#AIND-D02097"',
    '2026-11-16 是正（独立校閲）: 「ممن يتردد له الصلاح الطرابلسي ليقرئه」は ليقرئه の主語が يتردد と同じ الصلاح で、ـه が本項主。الصلاح الطرابلسي が本項主に通って教えた＝الصلاح が師（active）、本項主が学生（passive）。上の英文注記の読み（本項主が師）は誤り。')
t = add_resp(t, '師弟 relation の向きを是正（الصلاح الطرابلسي #AIND-D09344 が師＝active、本項主が学生）。原文「ممن يتردد له الصلاح الطرابلسي ليقرئه」。')
open(p, 'w', encoding='utf-8').write(t)

# 疑義4: relation 内の旧注記と新しい向きの矛盾を、追記で明示する
KIN = {  # aind: (relation を特定する属性の断片, 新しい subtype)
 'D02152': ('active="#TMP-P-000747"', 'son'), 'D02158': ('active="#TMP-P-000748"', 'son'),
 'D03010': ('active="#AIND-D07114"', 'siblings_child'), 'D03448': ('active="#AIND-D03439"', 'client'),
 'D03853': ('active="#AIND-D07813"', 'son-in-law'), 'D04097': ('active="#TMP-P-000744"', 'son'),
 'D04159': ('active="#TMP-P-000746"', 'siblings_child'), 'D04336': ('active="wd:Q4120128"', 'siblings_child'),
 'D05109': ('active="#AIND-D02571"', 'son'), 'D05229': ('active="#AIND-D05228"', 'grandson'),
 'D06255': ('active="#AIND-D03047"', 'client'), 'D09103a': ('active="#TMP-P-000948"', 'daughter'),
}
for a, (pat, st) in KIN.items():
    p = path(a); t = open(p, encoding='utf-8').read()
    t = append_note(t, re.escape(pat),
        f'2026-11-16 の統一規則（親族・社会関係は active=相手・passive=本項主、subtype＝active が passive の何にあたるか）で、active=相手・subtype={st} に改めた。上の注記の「方向」「active」は改訂前の符号化についての記述。')
    t = add_resp(t, 'relation 内の旧注記（方向・active）が 2026-11-16 の向きの統一と矛盾しないよう、改訂の旨を relation に追記。')
    open(p, 'w', encoding='utf-8').write(t)
TEA = {'D01276': 'passive="#AIND-D09211"', 'D01418': 'passive="#AIND-D08670"', 'D02852': 'passive="#AIND-D03874"',
       'D04428': 'passive="#AIND-D05979"', 'D10040': 'passive="wd:Q4120128"'}
for a, pat in TEA.items():
    p = path(a); t = open(p, encoding='utf-8').read()
    t = append_note(t, re.escape(pat),
        '2026-11-16 の統一規則で師弟は常に subtype="teacher"（active=師）とした（向きは不変）。上の注記の「subtype=student」の慣行は改訂前のもの。')
    t = add_resp(t, 'relation 内の旧注記（subtype=student の慣行）が 2026-11-16 の統一と矛盾しないよう、改訂の旨を relation に追記。')
    open(p, 'w', encoding='utf-8').write(t)
p = path('D06317'); t = open(p, encoding='utf-8').read()
t = append_note(t, r'subtype="educator"', '2026-11-16 Waka 裁定で subtype を社会関係の educator（active=養育者）に改めた（上の注記の educator_of は旧称）。')
t = add_resp(t, 'relation 内の旧称 educator_of について改訂の旨を追記。'); open(p, 'w', encoding='utf-8').write(t)

# 疑義7: D02015 の移行で落ちた一文を戻す
p = path('D02015'); t = open(p, encoding='utf-8').read()
old = 'Editorial cross-reference, not a personal tie.</note>'
assert t.count(old) == 1
t = t.replace(old, 'Editorial cross-reference, not a personal tie. Replaces contaminated TMP-P-000066.</note>')
open(p, 'w', encoding='utf-8').write(t)
print('ok')
