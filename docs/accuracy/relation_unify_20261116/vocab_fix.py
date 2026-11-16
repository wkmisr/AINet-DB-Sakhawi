"""統制外 subtype 7件（本項主 active）の処理（Waka 裁定 2026-11-16）"""
import glob, re, sys, os
ROOT = sys.argv[1]
DATE, WHO = '2026-11-16', 'claude-opus-5-5-relation-unify'

def path(aid):
    return glob.glob(os.path.join(ROOT, f'Individuals/*/AIND-{aid}_*.xml'))[0]

def edit(aid, pairs, note):
    p = path(aid); t = open(p, encoding='utf-8').read()
    for old, new in pairs:
        assert t.count(old) == 1, (aid, old[:80], t.count(old))
        t = t.replace(old, new)
    resp = ('    <respStmt>\n'
            '        <resp xml:lang="ja">修正（統制外 subtype の整理・2026-11-16 Waka 裁定）</resp>\n'
            f'        <note xml:lang="ja">{note}</note>\n'
            f'        <persName>{WHO}</persName>\n'
            f'        <date when="{DATE}"/>\n'
            '    </respStmt>\n')
    i = t.rfind('</person>'); ls = t.rfind('\n', 0, i) + 1
    t = t[:ls] + resp + t[ls:]
    open(p, 'w', encoding='utf-8').write(t)

# 1. D02046 master → patron（規則51、active=主人）
edit('D02046', [(
    'subtype="master" n="1" active="#AIND-D02046" passive="#AIND-D02178"',
    'subtype="patron" n="1" active="#AIND-D02178" passive="#AIND-D02046"')],
    '統制外 subtype「master」（active=本項主）を、規則51 に従い patron（active=主人 #AIND-D02178 الظاهر برقوق・passive=本項主）に是正。')

# 2. D02512 correspondent（app の社会関係語彙・対称）→ active=相手 に入替え
edit('D02512', [(
    'subtype="correspondent" n="1" active="#AIND-D02512" passive="wd:Q471116"',
    'subtype="correspondent" n="1" active="wd:Q471116" passive="#AIND-D02512"')],
    'correspondent（書簡相手、対称の社会関係）の向きを統一規則（active=相手・passive=本項主）に合わせた。')

# 3. D01824 praise → relation を除去し、既存の cultural event に人物を付ける
p = path('D01824'); t = open(p, encoding='utf-8').read()
rel = re.search(r'\n\s*<listRelation>\s*<relation [^>]*subtype="praise".*?</listRelation>', t, re.S).group(0)
edit('D01824', [
    (rel, ''),
    ("in praise of Fatḥ al-Dīn al-Muḥarraqī, beginning: 'Ya ṣadr ḥubbuka sāʾir fī sāʾirī / Ḥattā khayāluka fī manāmī zāʾirī'</desc>\n",
     "in praise of Fatḥ al-Dīn al-Muḥarraqī, beginning: 'Ya ṣadr ḥubbuka sāʾir fī sāʾirī / Ḥattā khayāluka fī manāmī zāʾirī'</desc>\n"
     "        <persName ref=\"#TMP-P-000666\">فتح الدين المحرقي</persName>\n")],
    '統制外 subtype「praise」（頌詩を作った相手）は人的関係ではないので relation を除去し、同内容の cultural event に persName（#TMP-P-000666 فتح الدين المحرقي）を付けた（先例 D05997）。')

# 4. D02012 / D02015 see_also → relation を除去し、cross-reference の note（@target）に
p = path('D02012'); t = open(p, encoding='utf-8').read()
rel = re.search(r'    <listRelation>\s*<relation [^>]*subtype="see_also".*?</listRelation>\n', t, re.S).group(0)
edit('D02012', [(rel,
    '    <note type="cross-reference" xml:lang="en" target="#AIND-D02015">Cross-reference (ينظر): the entry on Asanbughā al-ʿAlāʾī (D02015) refers the reader to this Asanbughā al-Nājī. Both died in 803 H and share the name Asanbughā, but they are distinct persons.</note>\n')],
    '統制外 subtype「see_also」は編者の参照指示で人的関係ではないので relation を除去し、note type="cross-reference"（target=#AIND-D02015）に移した。')
p = path('D02015'); t = open(p, encoding='utf-8').read()
rel = re.search(r'\n\s*<relation [^>]*subtype="see_also"[^>]*>.*?</relation>', t, re.S).group(0)
i = t.index('</listRelation>') + len('</listRelation>')
edit('D02015', [
    (rel, ''),
    ('</listRelation>\n', '</listRelation>\n'
     '    <note type="cross-reference" xml:lang="ar" target="#AIND-D02012">وينظر اسنبغا الناجي</note>\n'
     '    <note type="cross-reference" xml:lang="en" target="#AIND-D02012">al-Sakhāwī notes "wa-yunẓar Asanbughā al-Nājī" (compare/verify against Asanbughā al-Nājī) = AIND-D02012 (adjacent entry, al-Ḥājib). Editorial cross-reference, not a personal tie.</note>\n')],
    '統制外 subtype「see_also」は編者の参照指示で人的関係ではないので relation を除去し、note type="cross-reference"（target=#AIND-D02012）に移した。')

# 5-7. educator_of → educator（社会関係の統制語彙に新設、active=養育者。逆の語が無いので本項主 active 可）
p = path('D02463'); t = open(p, encoding='utf-8').read()
edit('D02463', [
    ('subtype="educator_of" n="2"', 'subtype="educator" n="2"'),
    ('subtype="educator_of" n="3"', 'subtype="educator" n="3"')],
    'subtype「educator_of」を、社会関係の統制語彙に新設した educator（active=養育者＝本項主、規則15 の例外）に改めた。')
edit('D06317', [('subtype="educator_of" n="1"', 'subtype="educator" n="1"')],
    'subtype「educator_of」を、社会関係の統制語彙に新設した educator（active=養育者＝本項主、規則15 の例外）に改めた。')
print('done')
