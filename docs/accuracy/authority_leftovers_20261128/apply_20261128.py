"""典拠表の残りの整理（WK 裁定 2026-11-28）。裁定表は rulings_20261128.json（45行）。
usage: python3 apply_20261128.py REPO
A 法学派：分類 Madhhab を新設（4行）。B 本伝のある人物の wd は persons_registry の same_as。
C 本伝のない人物の wd を登録、السمهودي は TMP-P-001088 のまま。D 既存 TMP と同じ gn・wd は TMP に付け替え、same_as に記録。
E gn・wd を登録。F 同表記の重複の統合・退役・表記の直し。G 書式の崩れ、転送項への参照、分類 Other。
"""
import sys, glob, re, csv, collections
REPO = sys.argv[1]; DATE = '2026-11-28'; TAG = f'{DATE} WK 裁定（典拠表の残り）: '
csv.field_size_limit(10**9)
def read(p):
    rows = list(csv.reader(open(p, encoding='utf-8', newline=''), delimiter='\t'))
    return rows[0], rows[1:]
def write(p, hdr, rows):
    w = csv.writer(open(p, 'w', encoding='utf-8', newline=''), delimiter='\t', lineterminator='\n'); w.writerow(hdr); w.writerows(rows)
EP, PP = f'{REPO}/authority/entities_registry.tsv', f'{REPO}/authority/persons_registry.tsv'
raw_e, raw_p = open(EP, encoding='utf-8', newline='').read(), open(PP, encoding='utf-8', newline='').read()
eh, er = read(EP); ph, pr = read(PP)
# the files must round-trip through the csv module unchanged before we touch them
import io
def dump(h, rows):
    s = io.StringIO(); w = csv.writer(s, delimiter='\t', lineterminator='\n'); w.writerow(h); w.writerows(rows); return s.getvalue()
assert dump(ph, pr) == raw_p, 'persons registry does not round-trip'
# entities: one row (TMP-N-05512) had text appended after a closing quote on 2026-11-27; rewriting the file quotes it properly
_bad = [a.split('\t')[0] for a, b in zip(raw_e.split('\n'), dump(eh, er).split('\n')) if a != b]
assert _bad in ([], ['TMP-N-05512']), _bad
E = {r[0]: r for r in er}; P = {r[0]: r for r in pr}
ei = {k: i for i, k in enumerate(eh)}; pi = {k: i for i, k in enumerate(ph)}
def hist(row, idx, s): row[idx['history']] = (row[idx['history']] + ' ' if row[idx['history']] else '') + TAG + s
def eset(i, s, **kw):
    r = E[i]
    for k, v in kw.items(): r[ei[k]] = v
    hist(r, ei, s)
def eadd(after, i, cat, ar, latn='', variants='', note='', cls=''):
    assert i not in E and i not in P
    row = [''] * len(eh)
    for k, v in dict(id=i, category=cat, status='active', label_ar=ar, label_latn=latn, variants=variants, note=note).items(): row[ei[k]] = v
    row[ei['class']] = cls; hist(row, ei, '登録')
    er.insert(er.index(E[after]) + 1, row); E[i] = row
def padd(after, i, name, note):
    assert i not in P and i not in E
    row = [''] * len(ph)
    for k, v in dict(id=i, status='active', name_ar=name, note=note).items(): row[pi[k]] = v
    hist(row, pi, '登録'); pr.insert(pr.index(P[after]) + 1, row); P[i] = row
def same_as(reg, idx, i, ext):
    r = reg[i]; assert not r[idx['same_as']], i
    r[idx['same_as']] = ext; hist(r, idx, f'same_as に {ext}')
def merge(i, tgt, why):
    r = E[i]; assert r[ei['status']] == 'active' and E[tgt][ei['status']] == 'active'
    r[ei['status']] = 'merged'; r[ei['target']] = tgt; hist(r, ei, f'{why}{tgt} に統合。番号は再利用しない')

# --- records
notes = collections.defaultdict(list); texts = {}
def path(d):
    f, = glob.glob(f'{REPO}/Individuals/*/*AIND-{d}_*.xml'); return f
def sub(d, old, new, n, what):
    f = path(d); t = texts.setdefault(f, open(f, encoding='utf-8').read())
    assert t.count(old) == n, (d, old, t.count(old))
    texts[f] = t.replace(old, new); notes[f].append(what)
def repoint(old, new, expect_files, what):
    """every attribute value "old" -> "new" in all records"""
    fs = []
    for f in sorted(glob.glob(f'{REPO}/Individuals/*/*.xml')):
        t = texts.get(f) or open(f, encoding='utf-8').read()
        k = t.count(f'"{old}"')
        if k:
            texts[f] = t.replace(f'"{old}"', f'"{new}"'); notes[f].append(f'{what}（{old} → {new}、{k}か所）'); fs.append(f)
    assert len(fs) == expect_files, (old, len(fs))

# A
eset('wd:Q228986', '分類を Nisbah から Madhhab に', category='Madhhab')
eadd('wd:Q228986', 'wd:Q82245', 'Madhhab', 'الشافعي', 'al-Shāfiʿī', note='Shafiʿism（Wikidata の項目名 شافعية）。レコードの affiliation/madhhab が参照する')
eadd('wd:Q82245', 'wd:Q48221', 'Madhhab', 'المالكي', 'al-Mālikī', note='Malikism（Wikidata の項目名 مالكية）')
eadd('wd:Q48221', 'wd:Q233387', 'Madhhab', 'الحنبلي', 'al-Ḥanbalī', note='Hanbalism（Wikidata の項目名 حنبلية）')
# B
for d, q in [('AIND-D09832', 'wd:Q257745'), ('AIND-D05895', 'wd:Q6534585'), ('AIND-D06305', 'wd:Q557847'), ('AIND-D02110', 'wd:Q286532'),
             ('AIND-D01845', 'wd:Q559146'), ('AIND-D00401', 'wd:Q2637299'), ('AIND-D02400', 'wd:Q561219'), ('AIND-D03517', 'wd:Q307564'),
             ('AIND-D00207', 'wd:Q12198099')]:
    same_as(P, pi, d, q)
for d in ('D00101', 'D01332'):
    sub(d, 'ref="wd:Q12198099"', 'ref="#AIND-D00207" corresp="wd:Q12198099"', 1, 'البقاعي の人物参照を #AIND-D00207 に直し、wd:Q12198099 は corresp に移した（2026-10-05 の裁定の当て漏れ）')
# C
padd('wd:Q471116', 'wd:Q39048909', 'علي بن عجلان', 'ʿAlī b. ʿAjlān（マッカのアミール、797年没）。本伝なし。D02463・D02481 の relation の相手')
padd('wd:Q39048909', 'wd:Q764947', 'سعد الدين التفتازاني', 'al-Taftāzānī（792年没）。本伝なし。ニスバは TMP-N-00230')
sub('D03437', '"wd:Q12188541"', '"#TMP-P-001088"', 1, 'rival の相手 wd:Q12188541 を #TMP-P-001088（السيد السمهودي）に付け替えた（同定が確実でないので TMP で保持、規則26）')
P['TMP-P-001088'][pi['note']] += f' 【{DATE}】候補: wd:Q12188541（نور الدين السمهودي）。確証がないので TMP のまま保持（WK 裁定）'
hist(P['TMP-P-001088'], pi, 'D03437 の参照を wd:Q12188541 から付け替え')
# D
for old, new, nf in [('gn:346030', 'TMP-L-00407', 1), ('gn:415189', 'TMP-L-00049', 1), ('gn:349715', 'TMP-L-00226', 1),
                     ('wd:Q756957', 'TMP-L-00173', 1), ('wd:Q486080', 'TMP-I-00120', 2), ('wd:Q428', 'TMP-T-00095', 1)]:
    repoint(old, '#' + new, nf, '典拠表に登録済みの ID に付け替えた'); same_as(E, ei, new, old)
# E
last_loc = [r for r in er if r[ei['category']] == 'Location'][-1][0]
for i, ar, latn, var, note in [('gn:2464915', 'سوسة', 'Sūsa', '', 'Sousse（チュニジア）'), ('gn:361546', 'العريش', 'al-ʿArīsh', '', 'Al ʿArīsh（エジプト）'),
        ('gn:315372', 'أرزنجان', 'Arzinjān', '', 'Erzincan（トルコ）'), ('gn:692713', 'قرم', 'Qirim', '', 'Staryy Krym（クリミア）'),
        ('gn:2472706', 'بنزرت', 'Banzart', 'بني زرت', 'Bizerte（チュニジア）。本文の表記は「بني زرت」（D01837）'),
        ('gn:2210247', 'طرابلس الغرب', 'Ṭarābulus al-Gharb', 'طرابلس', 'Tripoli（リビア）。シャームの طرابلس は gn:266826'),
        ('gn:2485926', 'وهران', 'Wahrān', '', 'Oran（アルジェリア）')]:
    eadd(last_loc, i, 'Location', ar, latn, var, note); last_loc = i
eadd([r for r in er if r[ei['category']] == 'Institution'][-1][0], 'wd:Q441410', 'Institution', 'جامع المارداني', 'Jāmiʿ al-Māridānī', note='Mosque of Amir al-Maridani（カイロ）。D05620')
lt = [r for r in er if r[ei['category']] == 'Text'][-1][0]
eadd(lt, 'wd:Q12184919', 'Text', 'الترغيب والترهيب للمنذري', 'al-Targhīb wa-l-tarhīb li-l-Mundhirī', 'الترغيب المنذري', 'D01595')
eadd('wd:Q12184919', 'wd:Q112671686', 'Text', 'السيرة لابن إسحاق', 'al-Sīra li-Ibn Isḥāq', note='D02525')
# F
merge('TMP-I-00193', 'TMP-I-00059', '典拠表の重複（同じ表記、参照なし）。')
merge('TMP-S-00072', 'TMP-S-00006', '典拠表の重複（同じ語、参照なし）。')
repoint('#TMP-S-00068', '#TMP-S-00040', 1, '同じ語（أنشد）の ID を一本化した'); merge('TMP-S-00068', 'TMP-S-00040', '典拠表の重複（同じ語）。')
repoint('#TMP-T-00089', '#TMP-T-00076', 1, '同じ書（جزء ابن الطلاية）の ID を一本化した'); merge('TMP-T-00089', 'TMP-T-00076', '典拠表の重複（同じ書）。')
if not E['TMP-T-00076'][ei['label_latn']]: E['TMP-T-00076'][ei['label_latn']] = E['TMP-T-00089'][ei['label_latn']]; hist(E['TMP-T-00076'], ei, 'ラテン文字表記を TMP-T-00089 から移した')
repoint('#TMP-T-00084', 'wd:Q12217063', 1, '同じ書（السنن للدارقطني）の ID を一本化した'); merge('TMP-T-00084', 'wd:Q12217063', '典拠表の重複（同じ書）。')
E['gn:2505325'][ei['status']] = 'retired'; E['gn:2505325'][ei['note']] = f'【{DATE}】ベジャイア州の番号。レコードは市の番号 gn:2505329 を使う（参照なし）。以後使用しない'; hist(E['gn:2505325'], ei, 'retired')
repoint('#TMP-L-00033', '#TMP-L-00197', 3, 'マッカとマディーナの「الحرمين」の ID を一本化した（本文で文脈を確認）'); merge('TMP-L-00033', 'TMP-L-00197', '典拠表の重複（マッカとマディーナの حرمين。3伝の本文で確認）。')
eset('TMP-L-00197', '表記を「حرمين (مكة والمدينة)」に', label_ar='حرمين (مكة والمدينة)', variants=(E['TMP-L-00197'][ei['variants']] + ' | ' if E['TMP-L-00197'][ei['variants']] else '') + 'الحرمين | حرمين')
eset('TMP-L-00034', '表記を「حرمين (القدس والخليل)」に', label_ar='حرمين (القدس والخليل)', variants=(E['TMP-L-00034'][ei['variants']] + ' | ' if E['TMP-L-00034'][ei['variants']] else '') + 'الحرمين | حرمين')
eset('wd:Q4702696', '表記を付属モスクの名に（2026-11-19 の裁定に合わせる）', label_ar='مسجد الخانقاه الصلاحية (بيت المقدس)', label_latn='Masjid al-Khānqāh al-Ṣalāḥiyya (Bayt al-Maqdis)')
# G
sub('D01074', '"#wd:Q471116"', '"wd:Q471116"', 1, '参照の書式を直した（#wd:Q471116 → wd:Q471116）')
sub('D00459', '"##AIND-D00333"', '"#AIND-D00333"', 1, '参照の書式を直した（##AIND-D00333 → #AIND-D00333）')
sub('D03414', '"#AIND-D04503"', '"#AIND-D04514"', 1, '転送項 #AIND-D04503 への人物参照を、転送先の本伝 #AIND-D04514 に付け替えた')
eset('wd:Q5612976', '分類を Other から Office に', category='Office')

for f, t in texts.items():
    if f not in notes: continue
    rs = ('    <respStmt><resp xml:lang="ja">修正・追記</resp><note xml:lang="ja">典拠表の残りの整理（WK 裁定 2026-11-28）。' + '。'.join(notes[f]) +
          f'。</note><persName>Kumakura</persName><date when="{DATE}"/></respStmt>\n')
    i = t.rindex('</person>'); open(f, 'w', encoding='utf-8').write(t[:i] + rs + t[i:])
write(EP, eh, er); write(PP, ph, pr)
print('records', len(notes), 'entities', len(er), 'persons', len(pr))
