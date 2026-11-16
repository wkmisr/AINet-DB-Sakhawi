"""PR #111 の独立校閲（claude-fable-5-2、2026-11-17）の反映"""
import glob, re, os, sys
ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
WHO = 'claude-office-followup'; DATE = '2026-11-17'
def path(a): return glob.glob(os.path.join(ROOT, f'Individuals/*/AIND-{a}_*.xml'))[0]
T = {}; NOTES = {}
def sub(a, old, new, note, count=1):
    t = T.get(a) or open(path(a), encoding='utf-8').read()
    assert t.count(old) >= 1, (a, old[:60]); T[a] = t.replace(old, new, count); NOTES.setdefault(a, []).append(note)
def resub(a, pat, rep, note, flags=re.S):
    t = T.get(a) or open(path(a), encoding='utf-8').read()
    t2, n = re.subn(pat, rep, t, count=1, flags=flags); assert n == 1, (a, pat[:60]); T[a] = t2; NOTES.setdefault(a, []).append(note)
# A1 D00592: パン屋は父、本人は香料商
resub('D00592', r'<state n="1" type="office" ref="#TMP-O-00236">.*?</state>',
      '<state n="1" type="office" ref="#TMP-O-00012">\n        <label xml:lang="ar">العطار</label>\n        <label xml:lang="ar-Latn">al-ʿAṭṭār</label>\n        <note xml:lang="ja">「الخباز أبوه العطار هو」＝パン屋（الخباز）は父、香料商（العطار）が本人（B164-168 決定19 の訳の訂正どおり）。本人の生業は العطار（TMP-O-00012）。</note>\n    </state>',
      'state を「الخباز」（TMP-O-00236、段階2 で付与）から本人の生業「العطار」（TMP-O-00012）に改めた。「الخباز أبوه العطار هو」で الخباز は父')
# A2 D00809: 「البدر النسابة」は本人ではない可能性が高い → state を外し note に
resub('D00809', r'\s*<state n="1" type="office" ref="#TMP-O-00409">.*?</state>',
      '\n    <note type="editorial" xml:lang="ja">【2026-11-17 官職 ID 整理・要 Waka 確認】見出し「… بن عمر الشريف الحسني بن عمر الشريف البدر النسابة」の後半「بن عمر الشريف البدر النسابة」は「ابن عم الشريف البدر النسابة」（系譜学者 البدر حسن بن محمد … الحسني、corpus 本伝 #AIND-D02617「ويعرف بالشريف النسابة」、المشهد الحسيني に住む）の崩れとみられ、系譜学者（النسابة）は本項主ではない可能性が高い。そのため office state（النسابة、TMP-O-00409）を外した。刊本どおりの読みを優先する規則25 に照らし、relation（従兄弟 #AIND-D02617）や laqab「البدر」の扱いは裁定待ち。</note>',
      'office state「النسابة」（TMP-O-00409）を外し editorial note に（「بن عمر الشريف البدر النسابة」＝「ابن عم …」で系譜学者は #AIND-D02617 の可能性が高い。要 Waka 確認）')
# A3 D03463: マドラサの修築は治績で ناظر 職ではない
resub('D03463', r'\s*<state n="2" type="office" ref="#TMP-O-00032">.*?</state>',
      '\n    <event type="other" n="2">\n        <desc xml:lang="ar">واشتغل بالنظر في مدارس وغيرها بعمارتها وتنمية أوقافها</desc>\n        <note xml:lang="ja">王としてマドラサなどの修築とワクフの増殖に心を配った治績。ناظر 職への就任ではないので office state にしない（2026-11-17、段階2 で付けた TMP-O-00032 を取り消し）。</note>\n    </event>',
      'state「النظر في المدارس」（TMP-O-00032）を event（other）に移した。王の治績で ناظر 職ではない')
# B4 D08929b
sub('D08929b', '<orgName>تربة برقوق</orgName>', '<orgName ref="wd:Q56284343">تربة برقوق</orgName>', 'orgName「تربة برقوق」に wd:Q56284343（التربة الظاهرية برقوق）')
T['D08929b'] = T['D08929b'].replace('→ref 未付与', '（2026-11-17 に TMP-O-00108 طبيب を付与）').replace('ID-Master 未登録（TMP-O-00040 شيخ تربة برقوق のみ）→ref 未付与', 'wd:Q56284343（2026-11-17）')
# B5 D06298
sub('D06298', '<label xml:lang="ar">الدوادارية الثانية (نيابة عن أخيه جانم)</label>', '<label xml:lang="ar">الدوادارية الثانية</label>', 'state のラベルから「(نيابة عن أخيه جانم)」を外した（subtype="deputy" と重複）')
t = T['D06298']
t2 = re.sub(r'(本項主自身の在職ではないため state にしない)', r'\1【2026-11-17 改: 規則65 (f) により本職 ID＋subtype="deputy" の state を立てた】', t, count=1)
if t2 != t: T['D06298'] = t2; NOTES['D06298'].append('relation の note の「state にしない」に改めた旨を追記')
# B7 D00744 / C D01450
sub('D00744', '<label xml:lang="ar">نائب</label>', '<label xml:lang="ar">نائب مكة</label>', 'ラベル「نائب」→「نائب مكة」')
sub('D01450', '<label xml:lang="ar">ناب (في الحكم)</label>', '<label xml:lang="ar">ناب</label>', 'ラベルの補い「(في الحكم)」を外した（原文「بل ناب أيضا」）')
sub('D01450', '<label xml:lang="ar-Latn">nāba (fī l-ḥukm)</label>', '<label xml:lang="ar-Latn">nāba</label>', '')
# B8 D00464: affiliation は state と二重符号化（規則8）で ref も誤り
resub('D00464', r'\s*<affiliation n="1" type="employed" ref="#TMP-I-00049">\s*<orgName xml:lang="ar">ضريح الليث</orgName>\s*<orgName xml:lang="ar-Latn">ḍarīḥ al-Layth</orgName>\s*</affiliation>', '',
      'affiliation（employed、ضريح الليث、ref TMP-I-00049 は誤り）を除去（state と二重符号化、規則8）')
# B9 D10176a / D02257
resub('D10176a', r'(<label xml:lang="ar">شاد الحوش</label>\s*<label xml:lang="ar-Latn">[^<]*</label>\n)', r'\1        <orgName xml:lang="ar">الحوش</orgName>\n', 'state「شاد الحوش」に orgName「الحوش」（スルターンの中庭。ID 未登録で ref なし）を補った（規則65 (h)）')
resub('D02257', r'(<label xml:lang="ar">شاد الشربخاناة</label>\s*<label xml:lang="ar-Latn">[^<]*</label>\n)', r'\1        <orgName ref="#TMP-I-00079">الشربخاناه</orgName>\n', 'state「شاد الشربخاناة」に orgName TMP-I-00079 を補った（規則65 (h)、他の 6 例と同じ）')
# C D06371 / D02158
sub('D06371', '＝シャリーフ حسن بن عجلان の下のナーイブ（常設の職、00053＋مكة。', '＝マッカのナーイブ（シャリーフ配下の常設の職、00053＋مكة。誰の下かは原文になし（حسن بن عجلان は旧主人で、本人の没年 865 よりずっと前に没）。', 'note の「حسن بن عجلان の下」を「誰の下かは原文になし」に改めた')
sub('D02158', '<orgName ref="wd:Q12241647">الأشرفية</orgName>', '<orgName ref="wd:Q12241647" cert="medium">الأشرفية</orgName>', 'orgName الأشرفية に cert="medium"（أوقاف الأشرفية はマドラサ以外を含みうる）')
# B6 古い note の ID 記述（ref と食い違うもの）に現在の ref を追記
STALE = {'D02158': ('TMP-O-00157', 'TMP-O-00131'), 'D06328': ('TMP-O-00362', 'TMP-O-00131'), 'D04661': ('TMP-O-00290', 'TMP-O-00032'),
         'D05973': ('TMP-O-00290', 'TMP-O-00032'), 'D06379': ('TMP-O-00049', 'TMP-O-00353'), 'D06053': ('TMP-O-00049', 'TMP-O-00353'),
         'D04299': ('TMP-O-00049', 'TMP-O-00353'), 'D03031': ('TMP-O-00049', 'TMP-O-00353'), 'D10026': ('TMP-O-00049', 'TMP-O-00353'),
         'D02815': ('TMP-O-00049', 'TMP-O-00353'), 'D07962': ('TMP-O-00295', 'TMP-O-00163'), 'D06034': ('TMP-O-00318', 'TMP-O-00093'),
         'D10087': ('TMP-O-00325', 'wd:Q125482')}
for a, (old, new) in STALE.items():
    t = T.get(a) or open(path(a), encoding='utf-8').read(); n = 0
    def f(m):
        global n
        body = m.group(0)
        if old in body and '（2026-11 の官職 ID 整理で' not in body:
            return body.replace('</note>', f'（2026-11 の官職 ID 整理で ref は {new} に移った）</note>', 1)
        return body
    t2 = re.sub(r'<state\b[^>]*>.*?</state>', lambda m: re.sub(r'<note xml:lang="ja">.*?</note>', f, m.group(0), flags=re.S), t, flags=re.S)
    if t2 != t: T[a] = t2; NOTES.setdefault(a, []).append(f'state の古い note の {old} に現在の ref（{new}）を追記')
for a, t in T.items():
    note = '／'.join(x for x in NOTES[a] if x)
    resp = ('    <respStmt>\n        <resp xml:lang="ja">修正（官職 ID 整理 段階2 の独立校閲の反映・2026-11-17）</resp>\n'
            f'        <note xml:lang="ja">{note}</note>\n        <persName>{WHO}</persName>\n        <date when="{DATE}"/>\n    </respStmt>\n')
    i = t.rfind('</person>'); ls = t.rfind('\n', 0, i) + 1
    open(path(a), 'w', encoding='utf-8').write(t[:ls] + resp + t[ls:])
print(len(T), 'files')
