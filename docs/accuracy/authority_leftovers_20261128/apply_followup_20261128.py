"""典拠表の残り：独立校閲（R2）後の修正（WK 裁定 2026-11-28）。
usage: python3 apply_followup_20261128.py REPO   （apply_20261128.py を当てた後に1回だけ）

1. السمهودي：corpus に本伝 AIND-D05247 がある（本文に同じ論争）。D03437 の rival を #AIND-D05247 に、
   wd:Q12188541 は D05247 の same_as に、TMP-P-001088 は D05247 に統合。
2. gn:692713（ドネツィク州の同名の集落）→ gn:692714（クリミアの Staryi Krym）。D01839。
3. gn:315372（エルズィンジャン県）→ gn:315373（市）。D02734。
4. D08030 の note の旧番号、TMP-L-00407 の note。
5. この PR が書いた「Waka 裁定」を「WK 裁定」に（以後の表記。過去の分は変えない）。
"""
import sys, csv, glob, io, re, os
import xml.etree.ElementTree as ET
csv.field_size_limit(10**9)
REPO = sys.argv[1]; DATE = '2026-11-28'
HEAD = '典拠表の残りの整理（WK 裁定 2026-11-28）。'
def one(d):
    fp, = glob.glob(f'{REPO}/Individuals/*/*AIND-{d}_*.xml'); return fp
def edit(d, subs, msg):
    fp = one(d); t = open(fp, encoding='utf-8').read()
    for old, new in subs:
        assert t.count(old) >= 1, (d, old[:50]); t = t.replace(old, new)
    rs = '    <respStmt><resp xml:lang="ja">修正・追記</resp><note xml:lang="ja">' + HEAD + msg + '</note><persName>Kumakura</persName><date when="' + DATE + '"/></respStmt>\n'
    i = t.rindex('</person>'); t = t[:i] + rs + t[i:]; ET.fromstring(t); open(fp, 'w', encoding='utf-8').write(t)

# 5. この PR が足した respStmt の表記（先に行う）
n = 0
for fp in glob.glob(f'{REPO}/Individuals/*/*.xml'):
    t = open(fp, encoding='utf-8').read(); k = t.count('典拠表の残りの整理（Waka 裁定 2026-11-28）。')
    if k: open(fp, 'w', encoding='utf-8').write(t.replace('典拠表の残りの整理（Waka 裁定 2026-11-28）。', HEAD)); n += k
print('respStmt WK', n)

# 1. السمهودي：先の付け替えの respStmt を外し、新しい記載に替える
fp = one('D03437'); t = open(fp, encoding='utf-8').read()
old = re.search(r'    <respStmt><resp xml:lang="ja">修正・追記</resp><note xml:lang="ja">典拠表の残りの整理（WK 裁定 2026-11-28）。rival の相手 wd:Q12188541 を #TMP-P-001088[^\n]*\n', t)
assert old; open(fp, 'w', encoding='utf-8').write(t.replace(old.group(0), ''))
edit('D03437', [('active="#TMP-P-001088"', 'active="#AIND-D05247"')],
     'rival の相手（السيد السمهودي）を本伝 #AIND-D05247 に付け替えた（もとは wd:Q12188541。2026-09-16 の裁定 §D-6 による）。'
     'D05247「… الحسني السمهودي … ويعرف بالشريف السمهودي」の本文に同じ論争（「وصنف في مسئلة فرش البسط المنقوشة ردا على من نازعه」）がある。'
     'wd:Q12188541 は典拠表の D05247 の same_as 欄に置いた。')
edit('D01839', [('ref="gn:692713"', 'ref="gn:692714"')],
     '「قرم」の gn:692713 を gn:692714 に直した。692713 はドネツィク州マリウポリ近郊の同名の集落で、クリミアの Staryi Krym（旧 Solkhat）は 692714'
     '（独立校閲が Wikidata Q576937 の GeoNames ID で確認。GeoNames の実物は未照合）。')
edit('D02734', [('ref="gn:315372"', 'ref="gn:315373"')],
     '「أرزنجان」の gn:315372 を gn:315373 に直した（2か所）。315372 はエルズィンジャン県の番号で、市は 315373'
     '（独立校閲が Wikidata Q136217 の GeoNames ID で確認。GeoNames の実物は未照合）。')
# 4. D08030：note の旧番号（この PR の respStmt は既にある）
fp = one('D08030'); t = open(fp, encoding='utf-8').read()
o = 'الحرمين（مكة والمدينة）＝TMP-L-00033（repo 4件で使用。ID-Master には同実体の TMP-L-00197 も登録されており重複）。'
assert t.count(o) == 1; t = t.replace(o, 'الحرمين（مكة والمدينة）＝TMP-L-00197（旧 TMP-L-00033 を 2026-11-28 に統合）。')
o2 = '（#TMP-L-00033 → #TMP-L-00197、1か所）。</note>'; assert t.count(o2) == 1
t = t.replace(o2, '（#TMP-L-00033 → #TMP-L-00197、1か所）。jāwara の event の note の番号も合わせた。</note>')
ET.fromstring(t); open(fp, 'w', encoding='utf-8').write(t)

# 典拠表
def read(p): return list(csv.reader(open(p, encoding='utf-8', newline=''), delimiter='\t'))
def write(p, rows):
    w = csv.writer(open(p, 'w', encoding='utf-8', newline=''), delimiter='\t', lineterminator='\n'); w.writerows(rows)
H1 = f'{DATE} Waka 裁定（典拠表の残り）'; H2 = f'{DATE} WK 裁定（典拠表の残り）'
E = f'{REPO}/authority/entities_registry.tsv'; rows = read(E); h = rows[0]; I = {c: h.index(c) for c in h}
k = 0
for r in rows[1:]:
    if H1 in r[I['history']]: r[I['history']] = r[I['history']].replace(H1, H2); k += 1
    if r[0] == 'gn:692713':
        r[0] = 'gn:692714'; r[I['note']] = 'Staryi Krym（クリミア。旧 Solkhat）。Wikidata Q576937。gn:692713 はドネツィク州の同名の集落で別の場所'
        r[I['history']] += '。校閲後に番号を gn:692713 → gn:692714 に直した（GeoNames の実物は未照合、次の台帳更新で確かめる）'
    if r[0] == 'gn:315372':
        r[0] = 'gn:315373'; r[I['note']] = 'Erzincan（トルコ、市）。Wikidata Q136217。gn:315372 は県の番号'
        r[I['history']] += '。校閲後に番号を gn:315372 → gn:315373 に直した（GeoNames の実物は未照合、次の台帳更新で確かめる）'
    if r[0] == 'TMP-L-00407':
        r[I['note']] += ' 【2026-11-28】D04159（الزفتاوي）の「ولد بعيد الثلاثين بزفتا」と同じ町（ガルビーヤの Zifta、gn:346030）。'
write(E, rows); print('entities history WK', k)
P = f'{REPO}/authority/persons_registry.tsv'; rows = read(P); h = rows[0]; I = {c: h.index(c) for c in h}
k = 0
for r in rows[1:]:
    if H1 in r[I['history']]: r[I['history']] = r[I['history']].replace(H1, H2); k += 1
    if r[0] == 'AIND-D05247':
        assert r[I['same_as']] == ''; r[I['same_as']] = 'wd:Q12188541'
        r[I['history']] = (r[I['history']] + ' ' if r[I['history']] else '') + H2 + ': same_as に wd:Q12188541。TMP-P-001088（السيد السمهودي）を統合'
    if r[0] == 'TMP-P-001088':
        o = ' 【2026-11-28】候補: wd:Q12188541（نور الدين السمهودي）。確証がないので TMP のまま保持（Waka 裁定）'
        assert o in r[I['note']]; r[I['note']] = r[I['note']].replace(o, ' 【2026-11-28】本伝 AIND-D05247 に統合（D05247 の本文に同じ論争がある。「独立本伝を発見できず」は誤り）')
        r[I['status']] = 'merged'; r[I['target']] = 'AIND-D05247'
        r[I['history']] = H2 + ': merged → AIND-D05247（独立校閲の指摘。D03437 の参照は #AIND-D05247 に）'
write(P, rows); print('persons history WK', k)
