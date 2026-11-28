"""転送の項の後始末・校閲後の追加分（Waka 裁定 2026-11-28、校閲結果の要裁定 1〜8）。
usage: python3 apply_followup_20261128.py REPO rulings_20261128.json
apply_20261128.py を当てた後の状態（b722268）に、1回だけ当てる。

A  REF 方式X を2件追加（D00744a・D01387）。処理は apply_20261128.py の s1 と同じ。
B  記号だけ直す項を7件追加（XML なし）。処理は s3 と同じ。
D  個別の修正：D01984 の転送先、典拠表 D01382 の連鎖、REF_D03522 の corresp、D05623 の corpus の入力誤り。
E  rulings に A・B と、実項のまま／今回は触らない項を足す。
"""
import sys, json, glob, re, os, subprocess, collections
import xml.parsers.expat, xml.etree.ElementTree as ET
REPO, RUL = sys.argv[1], sys.argv[2]
DATE = '2026-11-28'
CORPUS = f'{REPO}/0__DawForAIND_renumbered_B54_split20260905.txt'
corp = open(CORPUS, encoding='utf-8').read()
HERE = os.path.dirname(os.path.abspath(__file__))

def corpus_text(d):
    m = re.search(r'(?m)^###\$AIND-' + d + r' \| \d+\$# \$+ (.*?)(?=^###\$|\Z)', corp, re.S)
    return m.group(1).rstrip('\n')
def flat(d): return ' '.join(corpus_text(d).split())
def mark(d):
    global corp
    pat = re.compile(r'(?m)^(###\$AIND-' + d + r' \| \d+\$# )\$ ')
    assert len(pat.findall(corp)) == 1, d
    corp = pat.sub(lambda m: m.group(1) + '$$$ ', corp)
def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
def resp(msg):
    return ('<respStmt><resp xml:lang="ja">修正・追記</resp><note xml:lang="ja">' + msg +
            '</note><persName>Kumakura</persName><date when="' + DATE + '"/></respStmt>')
def one(d):
    fp, = glob.glob(f'{REPO}/Individuals/*/*AIND-{d}_*.xml'); return fp
def edit(d, subs, msg):
    """subs: [(old, new)]; each old must occur exactly once. Appends a respStmt."""
    fp = one(d); t = open(fp, encoding='utf-8').read()
    for old, new in subs:
        assert t.count(old) == 1, (d, old[:60], t.count(old))
        t = t.replace(old, new)
    i = t.rindex('</person>'); t = t[:i] + '    ' + resp(msg) + '\n' + t[i:]
    ET.fromstring(t); open(fp, 'w', encoding='utf-8').write(t)

def chunks(raw):
    out = []; depth = [0]; cur = [None]
    p = xml.parsers.expat.ParserCreate()
    def start(name, attrs):
        depth[0] += 1
        if depth[0] == 2: cur[0] = (name, attrs, p.CurrentByteIndex)
    def end(name):
        if depth[0] == 2:
            i = p.CurrentByteIndex
            if raw[i:i+2] == b'</': j = raw.index(b'>', i) + 1
            else: j = raw.index(b'/>', cur[0][2]) + 2
            out.append((cur[0][0], cur[0][1], raw[cur[0][2]:j].decode('utf-8')))
        depth[0] -= 1
    def comment(data):
        if depth[0] == 1:
            i = p.CurrentByteIndex; j = raw.index(b'-->', i) + 3
            out.append(('#comment', {}, raw[i:j].decode('utf-8')))
    p.StartElementHandler = start; p.EndElementHandler = end; p.CommentHandler = comment
    p.Parse(raw, True)
    return out

# ---- A：REF 方式X（2件）
A = [('D00744a', '#AIND-D02140', '16 بدلاي المسمى شهاب الدين أحمد بن سعد الدين أبي البركات بن أحمد ابن علي الجبرتي',
      '校閲での拾い漏れ（「في ＋人名」型）。転送先の見出しに本項の名（أحمد بن سعد الدين）がそのままある'),
     ('D01387', '#AIND-D01288', '306 أحمد بن المحب محمد بن بلكا القادري',
      '校閲での拾い漏れ（「في ＋人名」型）。「أحمد بن محمد بن بلكا」の見出しは D01288 だけ')]
log = []
for d, target, thead, memo in A:
    fp, = glob.glob(f'{REPO}/Individuals/*/AIND-{d}_*.xml')
    raw = open(fp, 'rb').read(); ch = chunks(raw)
    head = raw.decode('utf-8').split('\n', 1)[0]
    assert head.startswith('<person xml:id="AIND-' + d + '"') and 'type=' not in head, head
    head = head[:-1] + ' type="reference" subtype="LIMBO">'
    keep = collections.defaultdict(list); removed = collections.Counter()
    for name, at, s in ch:
        if name == '#comment': keep['comment'].append(s)
        elif name == 'persName' and at.get('type') == 'full': keep['full'].append(s)
        elif name == 'sex': keep['sex'].append(s)
        elif name == 'note' and at.get('type') == 'source': keep['source'].append(s)
        elif name == 'note' and at.get('type') == 'translation': keep['tr_' + at.get('xml:lang', '')].append(s)
        elif name == 'respStmt': keep['resp'].append(s)
        else: removed[name + ('/' + at['type'] if 'type' in at else '')] += 1
    assert len(keep['full']) == 1 and keep['sex'] and keep['source'], d
    ref = (f'<note type="reference" target="{target}">転送見出し（原文「{esc(flat(d))}」による）。転送先は {target}「{esc(thead)}」。{esc(memo)}。</note>')
    rem = '、'.join(f'{k}×{v}' if v > 1 else k for k, v in sorted(removed.items())) or 'なし'
    rs = resp('REF 処理（方式X、Waka 裁定 2026-11-28。独立校閲で見つかった拾い漏れ）: 原文が転送指示だけの項を '
              'type="reference" subtype="LIMBO" にし、ファイル名を REF_ にした。外した要素: ' + rem + f'。転送先 {target} を note reference に記した。')
    body = keep['comment'] + keep['full'] + keep['sex'] + keep['source'] + keep['tr_ja'] + keep['tr_en'] + [ref] + keep['resp'] + [rs]
    new = head + '\n' + ''.join('    ' + s + '\n' for s in body) + '</person>' + ('\n' if raw.endswith(b'\n') else '')
    ET.fromstring(new); open(fp, 'w', encoding='utf-8').write(new)
    nf = os.path.join(os.path.dirname(fp), 'REF_' + os.path.basename(fp))
    subprocess.run(['git', '-C', REPO, 'mv', os.path.relpath(fp, REPO), os.path.relpath(nf, REPO)], check=True)
    mark(d); log.append((d, target, rem, ''))

# ---- B：記号だけ（7件）。3列目は参考の転送先（典拠表には入れない）、4列目はメモ
B = [('D06880', '', '校閲での拾い漏れ（42語で、作成時の「40語以下」の条件から外れた）。転送先は未特定'),
     ('D09948', 'D09828', '校閲での拾い漏れ（「في ＋人名」型）'),
     ('D11047a', 'D00595', '校閲での拾い漏れ（「في ＋人名」型）'),
     ('D08491', 'D08153', '「هو X」型（要裁定 6：転送として扱う）。本人の項 D08153「… ويعرف بابن قرمان」がある'),
     ('D08495', 'D06933', '「هو X」型（要裁定 6）。本人の項 D06933「… ويعرف بابن قماقم」がある'),
     ('D11009a', 'D00725', '「هو X」型（要裁定 6）。本人の項 D00725「أحمد بن دريب … أبو الغواير … صاحب جازان وابن صاحبها」がある'),
     ('D10984a', 'D09084', '「هو X」型（要裁定 6）。本人の項 D09084「محمد الجمال أبو السعود بن ظهيرة أخو اللذين قبله」（الكمال أبو البركات D08764 の子）がある。D09089・D06530 の أبو السعود は父が違う')]
for d, t, memo in B:
    assert not glob.glob(f'{REPO}/Individuals/*/*AIND-{d}_*.xml'), d
    mark(d)

# ---- D：個別の修正
# D01984 → D01987
src1984 = flat('D01984')
edit('D01984', [(
    '<note type="reference" target="#NEEDID">転送見出し（原文「' + src1984 + '」による）。転送先は未定。「إسماعيل بن ميكائيل」の見出しが corpus にない。娘 D13077 の項に名前が出るだけ。</note>',
    '<note type="reference" target="#AIND-D01987">転送見出し（原文「' + src1984 + '」による）。転送先は #AIND-D01987「958 إسماعيل بن محمد المقدسي ثم المكي الصوفي」。'
    '見出しに ميكائيل はないが、本文末尾に「واسم جده ميكائيل」。810年没、妻は أبو العباس بن عبد المعطي の娘で、娘 #AIND-D13077 の項'
    '（「مات أبوها سنة عشر」、母 فاطمة ابنة أبي العباس بن عبد المعطي）と一致。</note>')],
    '転送先を #NEEDID から #AIND-D01987 に直した（独立校閲の指摘、Waka 裁定 2026-11-28）。根拠は note reference に記した。')
# D01382：note の文を属性に合わせる
edit('D01382', [(
    '転送先は #AIND-D01540（أحمد بن محمد بن محمد بن الناصح . سيأتي قريبا）（転送先も転送見出しのため、実体は D01540 の指示「فيمن لم يسم جد أبيه」の先。要追跡）。',
    '転送先は #AIND-D01549（本伝）。原文の指示が直接指す見出しは #AIND-D01540（أحمد بن محمد بن محمد بن الناصح . سيأتي قريبا）で、これも転送見出し（2026-11-28 に REF 化）。その指示「فيمن لم يسم جد أبيه」の先が D01549。')],
    'note reference の文を target（#AIND-D01549）に合わせて直した（独立校閲の指摘、Waka 裁定 2026-11-28）。')
# D02243：relation の note
edit('D02243', [(
    '母方祖父=#AIND-D02244(直後の項)。「الآتي بعده」で一意閉合。',
    '母方祖父の本伝は #AIND-D08147。「الآتي بعده」が指す直後の項 #AIND-D02244 は転送見出しで、その転送先が D08147。')],
    'maternal_grandfather の relation の note を active（#AIND-D08147）に合わせて直した（独立校閲の指摘、Waka 裁定 2026-11-28）。')
# D03522：corresp を外し、引き継ぎを note reference に
edit('D03522', [
    ('source="522161495722" corresp="wd:Q307564" type="reference"', 'source="522161495722" type="reference"'),
    ('عبد الحق بن أبي سعيد عثمان بن أحمد بن أبي سالم إبراهيم بن أبي الحسن المريني العبد الحقي نسبة لبني عبد الحق」。</note>',
     'عبد الحق بن أبي سعيد عثمان بن أحمد بن أبي سالم إبراهيم بن أبي الحسن المريني العبد الحقي نسبة لبني عبد الحق」。'
     '本項にあった corresp（wd:Q307564）と父の同定（Waka 裁定 2026-08-11、要判断B39-43 §D-9：第2の系譜「ابن عثمان بن أحمد」を cert=low で採る。'
     '父は Abū Saʿīd ʿUthmān III＝wd:Q2688156、仮番号 TMP-P-000729）は、#AIND-D03517 のレコードを作るときに D03517 に付ける。</note>')],
    'ルートの corresp（wd:Q307564）を外した（REF は corresp を持たない。Waka 裁定 2026-11-28）。corresp と、REF 処理で外した父の同定（Waka 裁定 2026-08-11）は、'
    '転送先 #AIND-D03517 のレコードを作るときの引き継ぎとして note reference に記した。')
# D05623：corpus の入力誤り
OLD, NEW = 'علي بن محمد القاضي', 'علي بن محمد بن القاضي'
line = re.compile(r'(?m)^(###\$AIND-D05623 \| \d+\$# \$\$\$ )' + OLD + r' \. فيمن جده \.$')
assert len(line.findall(corp)) == 1
corp = line.sub(lambda m: m.group(1) + NEW + ' . فيمن جده .', corp)
edit('D05623', [
    ('<persName type="full" xml:lang="ar">' + OLD + '</persName>', '<persName type="full" xml:lang="ar">' + NEW + '</persName>'),
    ('<note type="source" xml:lang="ar">' + OLD + ' . فيمن جده .</note>', '<note type="source" xml:lang="ar">' + NEW + ' . فيمن جده .</note>'),
    ('アリー・ブン・ムハンマド・アル＝カーディー。', 'アリー・ブン・ムハンマド・ブン・アル＝カーディー。'),
    ('ʿAlī b. Muḥammad al-Qāḍī.', 'ʿAlī b. Muḥammad b. al-Qāḍī.'),
    ('転送見出し（原文「' + OLD + ' . فيمن جده .」による）。転送先は未定。本文が「فيمن جده」で切れていて転送先を決められない。',
     '転送見出し（原文「' + NEW + ' . فيمن جده .」による）。転送先は未定。刊本（第6巻32頁）でも「فيمن جده .」で祖父名が欠けていて、転送先を決められない。')],
    'corpus の入力誤り（بن の脱落：「بن محمد القاضي」→「بن محمد بن القاضي」）を刊本（第6巻32頁）により訂正し、persName full・note source・訳文の名・note reference の引用を合わせた'
    '（独立校閲の指摘、Waka 裁定 2026-11-28）。転送先は #NEEDID のまま。')
open(CORPUS, 'w', encoding='utf-8').write(corp)

# ---- 典拠表
REG = f'{REPO}/authority/persons_registry.tsv'
L = open(REG, encoding='utf-8').read().split('\n'); hdr = L[0].split('\t')
S, T, N, Hh = hdr.index('status'), hdr.index('target'), hdr.index('name_ar'), hdr.index('history')
tr = {'AIND-' + d: t[1:] for d, t, _, _ in A}; tr.update({'AIND-' + d: '' for d, _, _ in B})
done = set()
def hist(c, msg): c[Hh] = (c[Hh] + ' ' if c[Hh] else '') + f'{DATE} ' + msg
for i, l in enumerate(L):
    c = l.split('\t')
    if c[0] in tr:
        assert c[S] == 'active' and c[T] == '', l[:80]
        c[S] = 'transfer'; c[T] = tr[c[0]]
        hist(c, 'Waka 裁定（転送の項の後始末・校閲後の追加）: active → transfer' + (f'、転送先 {tr[c[0]]}' if tr[c[0]] else ''))
    elif c[0] == 'AIND-D01984':
        assert c[S] == 'transfer' and c[T] == ''; c[T] = 'AIND-D01987'; hist(c, '転送先 AIND-D01987（独立校閲の指摘、Waka 裁定）')
    elif c[0] == 'AIND-D01382':
        assert c[T] == 'AIND-D01540'; c[T] = 'AIND-D01549'
        hist(c, 'target AIND-D01540 → AIND-D01549（D01540 が transfer になり連鎖になったため。XML の target と同じ。Waka 裁定）')
    elif c[0] == 'AIND-D05623':
        assert c[N] == OLD; c[N] = NEW; hist(c, 'name_ar「بن」を補う（corpus の入力誤り、刊本 第6巻32頁。Waka 裁定）')
    else: continue
    L[i] = '\t'.join(c); done.add(c[0])
assert len(done) == len(tr) + 3, done
open(REG, 'w', encoding='utf-8').write('\n'.join(L))

# ---- E：rulings と log
R = json.load(open(RUL, encoding='utf-8'))
for r in R['s1']:
    if r[0] == 'D01984':
        r[2], r[3] = '#AIND-D01987', '958 إسماعيل بن محمد المقدسي ثم المكي الصوفي'
        r[4] = '見出しに ميكائيل はないが、本文末尾に「واسم جده ميكائيل」。没年（810年）と妻が娘 D13077 の項と一致（独立校閲の指摘）'
    if r[0] == 'D05623':
        r[1] = NEW + ' . فيمن جده .'; r[4] = '刊本（第6巻32頁）でも「فيمن جده .」で祖父名が欠けている。見出しの「بن القاضي」は刊本により訂正（corpus の入力誤り）'
R['s1'] += [[d, flat(d), t, th, m] for d, t, th, m in A]
R['s3'] += [[d, flat(d)] for d, _, _ in B]
R['s3_followup_memo'] = [[d, ('AIND-' + t if t else ''), m] for d, t, m in B]
R['s2'].append(['D03332', flat('D03332'), '実項のまま',
    '「هو X」型だが、本人の項がほかにない（「محمد بن محمد بن يوسف」の見出し D09342〜D09354 に العقعق はいない。ほかは索引の D11311 と、子 D00306・孫 D04772・妾 D13241 の項だけ）。'
    '原則（Waka 2026-11-28）：転送の形をしていても、本人の項がほかにない人物は実項のままにする'])
for d, t in (('D11165', 'D09028'), ('D11179', 'D01825'), ('D11180', 'D08147')):
    R['s4'].append([d, 'なし', flat(d), '通称の一覧の区画（「هو X」型）',
        f'通称の一覧の区画（D11160 番台〜D11190）にあり、隣に「هو」のない同じ型の項が並ぶ。索引部（D11191〜）と一緒に後で決める。記号は $ のまま。参考の転送先 {t}'])
for d in 'D03860 D04572 D04675 D04676 D05719 D05751 D08709 D10319'.split():
    R['s4'].append([d, 'あり' if glob.glob(f'{REPO}/Individuals/*/*AIND-{d}_*.xml') else 'なし', flat(d), '見出しの境界',
        '1つの項の末尾に別の転送見出しが入っている（独立校閲で追加。★ のあるものとないものがある）。今回は触らない。見出しの境界の検査の対象'])
json.dump(R, open(RUL, 'w', encoding='utf-8'), ensure_ascii=False)
with open(os.path.join(HERE, 'apply_log_20261128.tsv'), 'a', encoding='utf-8') as f:
    for r in log: f.write('\t'.join(r) + '\n')
print('REF +', len(log), 'mark only +', len(B), 'registry', len(done))
