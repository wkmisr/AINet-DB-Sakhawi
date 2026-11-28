#!/usr/bin/env python3
"""固有の情報を持つ REF を実項に戻す（WK 裁定 2026-11-28）。repo の根で一度だけ走らせる。
REF 5件を実項のレコードに書き直し（ファイル名から REF_ を外す）、corpus の記号 $$$ → $、
persons_registry の status transfer → active。あわせて REF_AIND-D02425 の日本語訳を直す。"""
import glob, os, re, subprocess, sys
sys.path.insert(0, 'tools/authority')
import build_authority as B

TODAY = '2026-11-28'
CORPUS = glob.glob('0__DawForAIND_renumbered_*.txt')[0]
corpus_text = open(CORPUS, encoding='utf-8').read()
flat = re.sub(r'\s+', ' ', corpus_text)

def resp(note):
    return ('    <respStmt><resp xml:lang="ja">修正・追記</resp><note xml:lang="ja">' + note +
            '</note><persName>Kumakura</persName><date when="%s"/></respStmt>\n' % TODAY)

RULING1 = '実項復帰（WK 裁定 2026-11-28：転送の句があっても、その項にしかない情報を持つ項は実項にする）。'
RULING2 = '実項復帰（WK 裁定 2026-11-28：転送の形をしていても、本人の項がほかにない人物は実項のままにする）。'
COMMON = 'type="reference" subtype="LIMBO" と REF_ を外し、note reference・note editorial の内容を relation・event の note に移した。corpus の記号 $$$ → $、典拠表 transfer → active。'

# 各レコード: head = persName〜sex（〜affiliation）、body = listRelation・event・note editorial。
# quotes = note に引いた corpus の語句（corpus にあることを実行時に確かめる）。
RECORDS = {
'AIND-D07276': dict(
 head='''    <persName type="full" xml:lang="ar">محمد بن أبي بكر بن الحمصي</persName>
    <persName type="name_only" xml:lang="ar">محمد بن أبي بكر</persName>
    <persName type="shuhrah" xml:lang="ar">ابن الحمصي</persName>
    <sex value="M"/>
''',
 body='''    <listRelation>
        <relation type="personal" subtype="father" active="#NEEDID" passive="#AIND-D07276"><desc xml:lang="ar">أبو بكر</desc><note xml:lang="ja">父 أبو بكر：本項の見出しでは名のみ → #NEEDID。本伝 #AIND-D07236 の見出し（… الشمس أبو الفتح بن الشرف بن ناصر الدين）によれば父のラカブは الشرف。同定は D07236 のレコードを作るときに行い、本項には補わない（規則23）。</note></relation>
        <relation type="personal" subtype="possible_identity" n="1" active="#AIND-D07236" passive="#AIND-D07276" cert="high"><desc xml:lang="ar">وقد مضى فيمن جده محمد بن أبي بكر</desc><note xml:lang="ja">サハーウィー自身の転送の句。本伝は #AIND-D07236（刊本 452番「محمد بن أبي بكر بن محمد بن أبي بكر الشمس أبو الفتح بن الشرف بن ناصر الدين المنوفي السرسي الأصل القاهري الشافعي المقري ويعرف بابن الحمصاني وربما يقول الحمصي نسبة لحرفة جده لأمه」、レコード未作成）。祖父名 محمد بن أبي بكر と通称 ابن الحمصاني／الحمصي が一致する。corpus の「محمد بن أبي بكر بن محمد بن أبي بكر」見出し4件（D07234・D07235・D07236・D07237）のうち الحمصي を名乗るのは D07236 のみ（2026-10-25 校閲の照合）。本項にしかない出来事（888年の証人署名）を持つので、転送の句があっても実項とする（先例 #AIND-D05627）。</note></relation>
    </listRelation>
    <event type="cultural" subtype="witness" n="1" when-custom="0888" when="1483">
        <desc xml:lang="ar">شهد في إجازة على جعفر المقري سنة ثمان وثمانين</desc>
        <persName ref="#AIND-D02414" role="grantor">جعفر المقري</persName>
        <note xml:lang="ja">本項主が証人（規則28、先例 D01491・D07076 の witness 型）。جعفر المقري＝#AIND-D02414（刊本 278番 جعفر بن إبراهيم … الزين أبو الفتح القرشي الدهني السنهوري القاهري الازهري الشافعي المقرئ。#AIND-D05004 も「الزين جعفر المقري」と呼ぶ。2026-10-25 校閲の同定）。受領者は書かれていない。888＝1483-02-18〜1484-02-07（年初 1483、h2g.py）。本伝 D07236 の本文にこの件はない（D07236 が記すのは「ورأيته شهد عليه في إجازة」＝ابن الاسيوطي のイジャーザへの署名）。</note>
    </event>
''',
 quotes=['الشمس أبو الفتح بن الشرف بن ناصر الدين المنوفي السرسي الأصل القاهري الشافعي المقري ويعرف بابن الحمصاني وربما يقول الحمصي نسبة لحرفة جده لأمه',
         'الزين أبو الفتح القرشي الدهني السنهوري القاهري الازهري الشافعي المقرئ', 'ورأيته شهد عليه في إجازة'],
 resp=RULING1 + COMMON + '初版（2026-09-03）の event other（888）を、witness 型の cultural event（授与者 #AIND-D02414、@when 1483）として立て直した。通称「ابن الحمصي」は shuhrah（ref なし）。父は #NEEDID（初版の TMP-P-000064 は汚染番号のため使わない）。本伝 #AIND-D07236 とは possible_identity（cert high）。初版の student relation（#NEEDID）は原文に根拠がないので戻していない。',
 hist='転送の句はあるが、888年の証人署名（جعفر المقري のイジャーザ）がこの項にしかない。本伝 AIND-D07236 とはレコードの possible_identity で結ぶ'),

'AIND-D10054': dict(
 head='''    <persName type="full" xml:lang="ar">موسى بن أحمد الحسني</persName>
    <persName type="name_only" xml:lang="ar">موسى بن أحمد</persName>
    <persName type="nisbah" xml:lang="ar" ref="#TMP-N-00079">الحسني</persName>
    <sex value="M"/>
''',
 body='''    <listRelation>
        <relation type="personal" subtype="father" active="#NEEDID" passive="#AIND-D10054"><desc xml:lang="ar">أحمد</desc><note xml:lang="ja">父 أحمد：名のみ → #NEEDID。同定は本伝 #AIND-D10052 のレコードを作るときに行う。</note></relation>
        <relation type="personal" subtype="possible_identity" n="1" active="#AIND-D10052" passive="#AIND-D10054" cert="high"><desc xml:lang="ar">وقد مضى فيمن جده موسى قريبا</desc><note xml:lang="ja">サハーウィー自身の転送の句。本伝は #AIND-D10052（刊本 758番「موسى بن أحمد بن موسى الشرف الحسني السرسنائي ثم القاهري الشافعي نزيل الناصرية」、871年没、本項の2項前＝「قريبا」、レコード未作成）。名・父名・祖父 موسى・ニスバ الحسني が一致する（2026-11-05 校閲の照合）。本項にしかない出来事（834年の証人署名）を持つので、転送の句があっても実項とする（先例 #AIND-D05627）。</note></relation>
    </listRelation>
    <event type="cultural" subtype="witness" n="1" when-custom="0834" when="1430">
        <desc xml:lang="ar">شهد على عبد الدائم في إجازة سنة أربع وثلاثين</desc>
        <persName ref="#AIND-D03536" role="grantor">عبد الدائم</persName>
        <note xml:lang="ja">本項主が証人（規則28、先例 D01491・D07076 の witness 型）。عبد الدائم＝#AIND-D03536（刊本 132番 عبد الدائم بن علي زين الدين أبو محمد الحديدي ثم القاهري الأزهري الشافعي）。D03536 の本文「فقرأ عليه النور أبو عبد القادر الأزهري الآتي وأجاز له في سنة أربع وثلاثين فكان ممن شهد عليه الزين طاهر」が同じ834年のイジャーザを記すので cert は付けない（先例 D06030）。corpus の عبد الدائم の見出しはほかに D03535・D03537 の2件。同じイジャーザの証人の記述：#AIND-D09379「شهد على عبد الدائم الأزهري في إجازة سنة أربع وثلاثين」、#AIND-D03180「وقد رأيت خطه بالشهادة على الشيخ عبد الدائم في إجازة أبي عبد القادر سنة أربع وثلاثين」。受領者（أبو عبد القادر）は本項に書かれていないので persName を立てない（規則23）。834＝1430-09-28〜1431-09-17（年初 1430、h2g.py）。本伝 D10052 の本文にこの件はない。</note>
    </event>
''',
 quotes=['موسى بن أحمد بن موسى الشرف الحسني السرسنائي ثم القاهري الشافعي نزيل الناصرية',
         'عبد الدائم بن علي زين الدين أبو محمد الحديدي ثم القاهري الأزهري الشافعي',
         'فقرأ عليه النور أبو عبد القادر الأزهري الآتي وأجاز له في سنة أربع وثلاثين فكان ممن شهد عليه الزين طاهر',
         'شهد على عبد الدائم الأزهري في إجازة سنة أربع وثلاثين',
         'وقد رأيت خطه بالشهادة على الشيخ عبد الدائم في إجازة أبي عبد القادر سنة أربع وثلاثين'],
 resp=RULING1 + COMMON + '初版の XML は repo にないので、要素は 2026-11-05 校閲の記録（editorial note）と原文から作り直した：witness 型の cultural event（授与者 #AIND-D03536、@when 1430）、ニスバ الحسني（TMP-N-00079）、父 #NEEDID、本伝 #AIND-D10052 との possible_identity（cert high）。',
 hist='転送の句はあるが、834年の証人署名（عبد الدائم のイジャーザ）がこの項にしかない。本伝 AIND-D10052 とはレコードの possible_identity で結ぶ'),

'AIND-D01310': dict(
 head='''    <persName type="full" xml:lang="ar">أحمد بن محمد بن حذيفة المسيري</persName>
    <persName type="name_only" xml:lang="ar">أحمد بن محمد بن حذيفة</persName>
    <persName type="nisbah" xml:lang="ar" ref="#TMP-N-00407">المسيري</persName>
    <sex value="M"/>
''',
 body='''    <listRelation>
        <relation type="personal" subtype="father" active="#NEEDID" passive="#AIND-D01310"><desc xml:lang="ar">محمد</desc><note xml:lang="ja">父 محمد：名のみ → #NEEDID。本伝 #AIND-D01255 の見出しでは祖父は أحمد で、「ابن حذيفة」は通称（ويعرف بابن حذيفة）。本項の見出しは、サハーウィーが名簿で見た呼び方（منسوبا لذلك）のまま。</note></relation>
        <relation type="personal" subtype="teacher" n="1" active="#AIND-D09211" passive="#AIND-D01310">
            <desc type="method" ref="#TMP-S-00003" xml:lang="ar">سمع | السماع</desc>
            <desc xml:lang="ar">رأيته منسوبا لذلك فيمن سمع على التقي بن فهد بمكة</desc>
            <event type="learning"><placeName ref="gn:104515">مكة</placeName></event>
            <note xml:lang="ja">التقي بن فهد＝#AIND-D09211（刊本 727番 محمد بن محمد بن محمد بن محمد بن عبد الله بن محمد بن عبد الله بن فهد التقي أبو الفضل … الأصفوني ثم المكي الشافعي）。サハーウィーが、マッカで التقي بن فهد から聴講した者の名簿に本項主がこのナサブで載るのを見た、という記述。本伝 #AIND-D01255 の本文に التقي بن فهد からの聴講はない。</note>
        </relation>
        <relation type="personal" subtype="possible_identity" n="2" active="#AIND-D01255" passive="#AIND-D01310" cert="high"><desc xml:lang="ar">مضى فيمن جده أحمد</desc><note xml:lang="ja">サハーウィー自身の転送の句。本伝は #AIND-D01255（刊本 276番「أحمد بن محمد بن أحمد شهاب الدين المسيري ثم القاهري الشافعي ويعرف بابن حذيفة」、875年没、レコード未作成）。本項にしかない情報（التقي بن فهد からの聴講）を持つので、転送の句があっても実項とする（先例 #AIND-D05627）。</note></relation>
    </listRelation>
''',
 quotes=['أحمد بن محمد بن أحمد شهاب الدين المسيري ثم القاهري الشافعي ويعرف بابن حذيفة',
         'محمد بن محمد بن محمد بن محمد بن عبد الله بن محمد بن عبد الله بن فهد التقي أبو الفضل'],
 resp=RULING1 + COMMON + '6月の初版（XML_Limbo に残る形）をもとに、teacher relation（سمع、マッカ）を立て直した：相手は初版の TMP-P-000087 ではなく本伝のある #AIND-D09211（التقي بن فهد）。ニスバ المسيري（TMP-N-00407）、父 #NEEDID、本伝 #AIND-D01255 との possible_identity（cert high）。',
 hist='転送の句はあるが、マッカで التقي بن فهد から聴講したという記述がこの項にしかない。本伝 AIND-D01255 とはレコードの possible_identity で結ぶ。note 欄に入っていた corpus の行の写し（「###$ | 417366805220$# $$$ …」）は外した'),

'AIND-D05829': dict(
 head='''    <persName type="full" xml:lang="ar">عمر بن حاتم العجلوني</persName>
    <persName type="name_only" xml:lang="ar">عمر بن حاتم</persName>
    <persName type="nisbah" xml:lang="ar" ref="#TMP-N-00040">العجلوني</persName>
    <persName type="honorific" xml:lang="ar">الزاهد</persName>
    <persName type="honorific" xml:lang="ar">الولي</persName>
    <sex value="M"/>
''',
 body='''    <listRelation>
        <relation type="personal" subtype="father" active="#NEEDID" passive="#AIND-D05829"><desc xml:lang="ar">حاتم</desc><note xml:lang="ja">父 حاتم：名のみ、corpus に本伝なし → #NEEDID。#AIND-D00688 の本文では「حديم」。</note></relation>
        <relation type="personal" subtype="other" n="1" active="#AIND-D00688" passive="#AIND-D05829"><desc xml:lang="ar">له كلام يدخل في منقبته وجلالته مضى في أحمد بن حسين بن رسلان</desc><note xml:lang="ja">本人の本伝への転送ではなく、本項主の言葉が引かれている項への案内（「له ذكر في …」型の先例 D04364・D00410a と同じ subtype other）。相手＝#AIND-D00688（أحمد بن حسين بن حسن بن علي بن يوسف بن علي بن أرسلان … الشهاب أبو العباس الرملي الشافعي نزيل بيت المقدس、ابن رسلان）。D00688 の本文「وسئل عنه عمر بن حديم العجلوني الزاهد الولي حين قدم القدس أهو من الأولياء فقال」（父名は「حديم」、本見出しは「حاتم」。綴りの揺れとして記録し、読み替えない）。ほかに #AIND-D01543「وقال عمر بن حاتم العجلوني لم أر أحدا」、#AIND-D01684「سئل الشيخ عمر بن حاتم العجلوني عن أمثل من رأت عيناه」にも本項主の言葉が引かれる。本項主の項は corpus にここしかないので実項とする。</note></relation>
    </listRelation>
''',
 quotes=['وسئل عنه عمر بن حديم العجلوني الزاهد الولي حين قدم القدس أهو من الأولياء فقال',
         'وقال عمر بن حاتم العجلوني لم أر أحدا', 'سئل الشيخ عمر بن حاتم العجلوني عن أمثل من رأت عيناه',
         'الشهاب أبو العباس الرملي الشافعي نزيل بيت المقدس'],
 resp=RULING2 + COMMON + '初版（2026-08-23）のニスバ العجلوني（TMP-N-00040）と honorific「الزاهد」「الولي」を戻した。ابن رسلان（#AIND-D00688）との関わりは subtype other の relation（初版の統制外 subtype「biographical cross-reference」・#NEEDID は使わない）。父は #NEEDID。',
 hist='転送先 AIND-D00688 は本人の項ではなく、本人の言葉が引かれている ابن رسلان の項。本人の項は corpus にここしかない。AIND-D00688 との関わりはレコードの relation に記した'),

'AIND-D07119': dict(
 head='''    <persName type="full" xml:lang="ar">محمد بن إسماعيل ابن محمد بن عبد الله الشمس القلهاتي المكي الشافعي</persName>
    <persName type="name_only" xml:lang="ar">محمد بن إسماعيل بن محمد بن عبد الله</persName>
    <persName type="nisbah" xml:lang="ar" ref="#TMP-N-02778">القلهاتي</persName>
    <persName type="nisbah" xml:lang="ar" ref="#TMP-N-00002">المكي</persName>
    <persName type="laqab" xml:lang="ar">الشمس</persName>
    <sex value="M"/>
    <affiliation type="madhhab" ref="wd:Q82245">Shafi'i</affiliation>
''',
 body='''    <listRelation>
        <relation type="personal" subtype="father" active="#NEEDID" passive="#AIND-D07119"><desc xml:lang="ar">إسماعيل بن محمد بن عبد الله</desc><note xml:lang="ja">父 إسماعيل بن محمد بن عبد الله：ナサブのみ、corpus に本伝が見当たらない → #NEEDID。</note></relation>
        <relation type="personal" subtype="son" active="#AIND-D09866" passive="#AIND-D07119"><desc xml:lang="ar">والد محمود زائد . يأتي فيه</desc><note xml:lang="ja">息子＝#AIND-D09866（刊本 578番「محمود بن محمد بن إسماعيل بن محمد بن عبد الله نجم الدين المدعو زائدا لكثرة ما كان لأبويه من الأبناء ابن الشمس القلهاتي」、858年生、レコード未作成）。「يأتي فيه」＝本項主のことは息子の項に書く、の意。</note></relation>
    </listRelation>
    <note type="editorial" xml:lang="ja">本項主の項は corpus にここしかないので実項とする（本人の本伝への転送ではない）。経歴は息子の項 #AIND-D09866 の本文にある：「وكان أبوه صالحا تلاوة وعبادة وورعا ممن اشتغل بالقاهرة وغيرها وقطن مكة وذكر بالفضيلة وحسن الخط ممن يكتب بالأجرة مع تعانيه السفر للتكسب حتى مات بمندوة في مستهل رجب سنة سبع وثمانين وقد زاحم الثمانين」（887年ラジャブ月初めに مندوة で没、80歳近く）。相手側の項の内容なので本項の属性（death・state・event）にはせず、ここに記録する（規則23）。</note>
''',
 quotes=['محمود بن محمد بن إسماعيل بن محمد بن عبد الله نجم الدين المدعو زائدا لكثرة ما كان لأبويه من الأبناء ابن الشمس القلهاتي',
         'وكان أبوه صالحا تلاوة وعبادة وورعا ممن اشتغل بالقاهرة وغيرها وقطن مكة وذكر بالفضيلة وحسن الخط ممن يكتب بالأجرة مع تعانيه السفر للتكسب حتى مات بمندوة في مستهل رجب سنة سبع وثمانين وقد زاحم الثمانين'],
 resp=RULING2 + COMMON + '初版（2026-08-31）のニスバ القلهاتي（TMP-N-02778）・المكي（TMP-N-00002）、ラカブ الشمس、学派（Shafi\'i）を戻した。息子 محمود زائد は #AIND-D09866（初版は #NEEDID）。父は #NEEDID。息子の項にある本項主の経歴は editorial note に記録した（属性にはしていない）。',
 hist='転送先 AIND-D09866 は本人の項ではなく、息子 محمود زائد の項。本人の項は corpus にここしかない。AIND-D09866 との関係はレコードの son relation に記した'),
}

def block(t, pat):
    m = re.search(pat, t, re.S)
    assert m, pat
    return m.group(0)

reg = B.read_tsv(B.REG)
assert B.dump(reg, B.REG_COLS) == open(B.REG, encoding='utf-8', newline='').read(), 'registry does not round-trip'
lines = corpus_text.split('\n')

for aid, r in RECORDS.items():
    for q in r['quotes']:
        assert re.sub(r'\s+', ' ', q) in flat, (aid, q)
    old = glob.glob('Individuals/*/REF_%s_*.xml' % aid)
    assert len(old) == 1, aid
    old = old[0]
    t = open(old, encoding='utf-8').read()
    root = block(t, r'<person [^>]*>')
    assert 'type="reference" subtype="LIMBO"' in root
    root = root.replace(' type="reference" subtype="LIMBO"', '')
    comment = block(t, r'    <!-- generated[^\n]*-->\n')
    source = block(t, r'    <note type="source".*?</note>\n')
    trans = ''.join(m.group(0) for m in re.finditer(r'    <note type="translation".*?</note>\n', t, re.S))
    assert trans.count('<note') == 2, aid
    resps = t[t.index('    <respStmt'):t.rindex('</person>')]
    new = root + '\n' + comment + r['head'] + r['body'] + source + trans + resps.rstrip('\n') + '\n' + resp(r['resp']) + '</person>\n'
    path = old.replace('REF_', '')
    subprocess.check_call(['git', 'mv', old, path])
    open(path, 'w', encoding='utf-8').write(new)
    # corpus
    idx = [i for i, l in enumerate(lines) if l.startswith('###$' + aid + ' ')]
    assert len(idx) == 1, aid
    assert '$# $$$ ' in lines[idx[0]], lines[idx[0]]
    lines[idx[0]] = lines[idx[0]].replace('$# $$$ ', '$# $ ')
    # registry
    row = [x for x in reg if x['id'] == aid]
    assert len(row) == 1 and row[0]['status'] == 'transfer', aid
    row = row[0]
    h = '%s WK 裁定（固有の情報を持つ REF の洗い出し）: transfer → active（旧転送先 %s）。%s' % (TODAY, row['target'], r['hist'])
    row['status'], row['target'] = 'active', ''
    if aid == 'AIND-D01310':
        row['note'] = ''
    row['history'] = (row['history'] + ' ' + h).strip()

open(CORPUS, 'w', encoding='utf-8').write('\n'.join(lines))
open(B.REG, 'w', encoding='utf-8', newline='').write(B.dump(reg, B.REG_COLS))

# REF_AIND-D02425 の日本語訳（裁定表 6）
p = glob.glob('Individuals/*/REF_AIND-D02425_*.xml')[0]
t = open(p, encoding='utf-8').read()
OLD, NEW = '私は言う、彼（サハーウィー）は彼以前の人物である。', '私は言う。これは直前の項の人物である。'
assert t.count(OLD) == 1
t = t.replace(OLD, NEW)
t = t[:t.rindex('</person>')] + resp('日本語訳の誤りを直した（WK 裁定 2026-11-28）：「قلت وهو الذي قبله」＝「私は言う。これは直前の項の人物である」（旧訳「彼（サハーウィー）は彼以前の人物である」）。REF のまま。') + '</person>' + t[t.rindex('</person>') + len('</person>'):]
open(p, 'w', encoding='utf-8').write(t)
print('ok')
