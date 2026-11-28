"""Apply the 2026-11-22 rulings (date values, event types) and the standing rules that had not been
applied to Individuals/ yet. Run from the repo root:  python3 docs/accuracy/triple_prep_20261122/apply.py
Every changed file gets one respStmt that lists what changed. Details: README.md in this folder."""
import glob, json, re, sys, os, collections
sys.path.insert(0, os.path.dirname(__file__))
from lib import ce, pad, set_date, path, Log, finish, esc

LOG = Log()
STAT = collections.Counter()
V01 = os.environ.get('V01', '/tmp/v01n/meta')        # data_v01/meta (for the rule-placed event triggers)


def load(d):
    f = path(d); return f, open(f, encoding='utf-8').read()


def save(f, s): open(f, 'w', encoding='utf-8').write(s)


def one(s, old, new, d):
    assert s.count(old) == 1, (d, old, s.count(old))
    return s.replace(old, new)


def add_note(s, start, text, lang='ja'):
    """Insert <note> inside the element whose start tag begins at index `start`."""
    m = re.match(r'<([\w:]+)', s[start:]); tag = m.group(1)
    st_end = s.index('>', start)
    if s[st_end - 1] == '/':                                   # self-closing: open it
        s = s[:st_end - 1].rstrip() + '>' + '</%s>' % tag + s[st_end + 1:]
        st_end = s.index('>', start)
    depth, i = 0, start
    pat = re.compile(r'<(/?)%s\b[^>]*?(/?)>' % re.escape(tag))
    for mm in pat.finditer(s, start):
        if mm.group(1): depth -= 1
        elif not mm.group(2): depth += 1
        if depth == 0: close = mm.start(); break
    note = '<note xml:lang="%s">%s</note>' % (lang, esc(text))
    ls = s.rfind('\n', 0, start) + 1; ind = s[ls:start]
    if '\n' not in s[start:close]:                             # element on one line: inline
        return s[:close] + note + s[close:]
    cls = s.rfind('\n', 0, close) + 1
    return s[:cls] + ind + '    ' + note + '\n' + s[cls:]


def redate(d, f, s, start_tag_re, msg, note=None, all_=False, **kw):
    ms = list(re.finditer(start_tag_re, s)); assert ms, (d, start_tag_re)
    for m in reversed(ms if all_ else ms[:1]):
        pos = m.start(); new = set_date(m.group(0), **kw)
        s = s[:pos] + new + s[m.end():]
        if note:
            # a <date/> inside a <state>: the note goes into the state
            s = add_note(s, s.rfind('<state', 0, pos) if new.startswith('<date') else pos, note)
        LOG.add(f, msg); STAT['date'] += 1
    return s


RULING = 'Waka 裁定 2026-11-22'

# ---------------------------------------------------------------- A. dates
def dates():
    # A1: the 13 values ruled on 2026-11-22
    A1 = [
        ('D00737', r'<birth when-custom="820s"[^>]*>', dict(lo=815, hi=825),
         '生年「820s」→ 815〜825', '「وهو في سنة تسعين حي ويكون تقريبا في حدود السبعين」＝890年にほぼ70歳 → 生年 815〜825（%s）' % RULING),
        ('D00610', r'<event type="learning" when="880s">', dict(lo=881),
         '学習の年「880s」（@when に AH）→ 881以後', '「المجاورة الثالثة بعد الثمانين」→ 881年以後（%s）' % RULING),
        ('D00610', r'<event type="residence" subtype="jāwara" n="2" when-custom="880s"[^>]*>', dict(lo=881),
         'ジワールの年「880s」→ 881以後', '「المجاورة الثالثة بعد الثمانين」→ 881年以後（%s）' % RULING),
        ('D00452', r'<event type="cultural" n="1" when-custom="0019"[^>]*>', dict(when=819),
         'イジャーザの年「19」→ 819', '「أجاز لهم في سنة تسع عشرة」→ 819（百の位は人物の世代から、%s）' % RULING),
        ('D01321', r'<death when-custom="0005-07-11"[^>]*>', dict(when='0805-07-11'),
         '没年「5-07-11」→ 805-07-11（西暦も再計算）', '「مات في يوم الأحد حادي عشر رجب سنة خمس」→ 805-07-11。805年なら日曜で本文と合う（905年は火曜）（%s）' % RULING),
        ('D02051', r'<date type="appointment" when-custom="أيام المؤيد"/>', dict(lo=815, hi=824),
         '任官「أيام المؤيد」→ 815〜824', '「في أيام المؤيد」＝シャイフの治世 815〜824（%s）' % RULING),
        ('D02051', r'<date type="appointment" when-custom="أيام الأشرف"/>', dict(lo=825, hi=841),
         '任官「أيام الأشرف」→ 825〜841', '「في أيام الأشرف」＝経歴の順（المؤيد の後）からバルスバーイの治世 825〜841（%s）' % RULING),
        ('D00311', r'<event type="residence" n="2" when-custom="0897-898"[^>]*>', dict(lo=897, hi=898, drop_cert=True),
         'マッカ滞在「897-898」→ 897〜898', '「لقيني بمكة في سنة سبع وتسعين… في أول التي تليها」→ 897〜898（%s）' % RULING),
        ('D02327', r'<death when-custom="850\+"[^>]*>', dict(lo=851),
         '没年「850+」→ 851以後', '「مات بعد الخمسين」→ 851年以後（%s）' % RULING),
        ('D00799', r'<event type="other" n="1" when-custom="0001"[^>]*>', dict(when=801),
         '証人の年「1」→ 801', '「شهد على بعض الحنفية سنة إحدى」→ 801（百の位は人物の世代から、%s）' % RULING),
        ('D00774', r'<date type="appointment" when-custom="Shaʿbān"/>', dict(hi=813),
         '任官「Shaʿbān」→ 813年以前（月 شعبان は note）', '「في شعبان」：年は本文になし。イブン・ハジャル『インバー』813年の記事なので 813年以前（%s）' % RULING),
        ('D00031', r'<death when-custom="after 893"[^>]*>', dict(lo=894, drop_cert=True),
         '没年「after 893」→ 894以後', '「وكان حيا بعد ثلاث وتسعين」＝893年より後に生存 → 没年は 894以後（%s）' % RULING),
    ]
    for d, rx, kw, msg, note in A1:
        f, s = load(d); s = redate(d, f, s, rx, msg, note, **kw); save(f, s)
    # removed: no year in the text
    for d, rx, msg, note in [
        ('D01712', r'\n\s*<date type="retirement" when-custom="Once after[^"]*"/>', '退任の日付欄（英文）を除去し note へ',
         '在任は2回：「مرة بعد أخيه ومرة بعد ولد أخيه」（兄の後と甥の後）。年は本文になし（%s）' % RULING),
        ('D00708', r'\n\s*<date type="appointment" when-custom="أول أمره"/>', '職（織工）の日付欄「أول أمره」を除去し note へ',
         '「كان في أول أمره حائكا」＝若い頃。年は付けない（%s）' % RULING)]:
        f, s = load(d); m = re.search(rx, s); assert m, d
        st = s.rfind('<state', 0, m.start()); s = s[:m.start()] + s[m.end():]
        s = add_note(s, st, note); LOG.add(f, msg); STAT['date'] += 1; save(f, s)

    # A2: بضع = 1–9 (ruling 2026-11-22). Ranges written as X3–X9 become X1–X9 (century as already in the TEI);
    # four deaths written as one year with cert low become a range.
    for f in sorted(glob.glob('Individuals/**/*.xml', recursive=True)):
        s = open(f, encoding='utf-8').read()
        src = re.search(r'<note type="source"[^>]*>(.*?)</note>', s, re.S)
        if not src or 'بضع' not in src.group(1): continue
        o = s
        for m in reversed(list(re.finditer(r'<(\w+)\b[^<>]*notBefore-custom="0(\d\d)3"[^<>]*notAfter-custom="0(\d\d)9"[^<>]*>', s))):
            if m.group(2) != m.group(3): continue
            dec = int(m.group(2)) * 10
            new_ = set_date(m.group(0), lo=dec + 1, hi=dec + 9)
            s = s[:m.start()] + new_ + s[m.end():]
            s = add_note(s, s.rfind('<state', 0, m.start()) if m.group(1) == 'date' else m.start(),
                         '「بضع」は1〜9として幅で記録（%s。旧値 %d〜%d）' % (RULING, dec + 3, dec + 9))
            LOG.add(f, '%s「بضع」%d〜%d → %d〜%d' % ({'birth': '生年', 'death': '没年'}.get(m.group(1), m.group(1) + ' の年'), dec + 3, dec + 9, dec + 1, dec + 9))
            STAT['bid'] += 1
        if s != o: save(f, s)
    for d, y in [('D00003', 820), ('D01780', 860), ('D05686', 850), ('D10176b', 865)]:
        f, s = load(d); dec = y // 10 * 10
        s = redate(d, f, s, r'<death when-custom="0%d"[^>]*>' % y, '没年「%d」（単一の年）→ %d〜%d（بضع）' % (y, dec + 1, dec + 9),
                   '「بضع」は1〜9として幅で記録（%s。旧値 %d・単一の年）' % (RULING, y), lo=dec + 1, hi=dec + 9, drop_cert=True)
        STAT['bid'] += 1; save(f, s)

    # A4: AH year written into the CE attribute @when (app bug, fixed in app.py 2026-11-02; old data not migrated)
    for f in glob.glob('Individuals/**/*.xml', recursive=True):
        s = open(f, encoding='utf-8').read(); o = s
        def fix(m):
            tag = m.group(0)
            if 'when-custom=' in tag: return tag
            v = re.search(r'\swhen="(0\d{3}(?:-\d\d){0,2})"', tag).group(1)
            STAT['when_ah'] += 1
            return tag.replace(' when="%s"' % v, ' when-custom="%s" when="%s"' % (v, ce(v)))
        s = re.sub(r'<(?:event|date|state)\b[^<>]*\swhen="0\d{3}(?:-\d\d){0,2}"[^<>]*>', fix, s)
        if s != o:
            n = len(re.findall(r'<(?:event|date|state)\b[^<>]*\swhen="0\d{3}', o))
            LOG.add(f, '@when にあったヒジュラ暦の年 %d 件を when-custom に移し、西暦を計算して @when に（app.py 2026-11-02 改修前のデータ）' % n)
            save(f, s)
    f, s = load('D00551')
    s = one(s, '<event type="learning" when="during the third sojourn (mujāwara)">', '<event type="learning">', 'D00551')
    s = add_note(s, s.index('<event type="learning">'), '時期は「3回目のジワールのとき」（@when にあった英文を note に）')
    LOG.add(f, '学習の @when にあった英文を note に'); save(f, s)


# ---------------------------------------------------------------- B. event types
METHOD = [('سمع', 'TMP-S-00003', 'سمع | السماع'), ('قرأ', 'TMP-S-00025', 'قرأ | القراءة'), ('قرا', 'TMP-S-00025', 'قرأ | القراءة'),
          ('قراءة', 'TMP-S-00025', 'قرأ | القراءة'), ('أخذ', 'TMP-S-00008', 'أخذ | الأخذ'), ('اشتغل', 'TMP-S-00077', 'اشتغل | الاشتغال'),
          ('حفظ', 'TMP-S-00027', 'حفظ | الحفظ'), ('أجاز', 'TMP-S-00004', 'أجاز | إجازة'), ('حضر', 'TMP-S-00028', 'حضر | الحضور'),
          ('تفقه', 'TMP-S-00032', 'تفقه | التفقه'), ('لازم', 'TMP-S-00014', 'لازم'), ('عرض', 'TMP-S-00006', 'عرض'), ('تلا', 'TMP-S-00010', 'تلا')]


def method_of(q):
    if not q: return None
    w = q.split()[0]
    if w[:1] in 'وف' and len(w) > 3: w = w[1:]
    if w.startswith('قرائن'): return None
    for stem, sid, lab in METHOD:
        if w == stem or (w.startswith(stem) and len(w) - len(stem) <= 2):
            return sid, lab
    return None


def events():
    # B1: study -> learning, with the method by rule from the event's trigger word
    for f in sorted(glob.glob('Individuals/**/*.xml', recursive=True)):
        s = open(f, encoding='utf-8').read(); o = s
        k = re.search(r'AIND-D\w+?(?=_)', f).group(0)
        y = os.path.join(V01, k + '.yml'); evs = []
        if os.path.exists(y):
            import yaml
            evs = yaml.safe_load(open(y, encoding='utf-8')).get('events') or []
        tops = list(re.finditer(r'(?m)^    <event type="(\w+)"[^>]*?/?>', s))
        msgs = []
        for idx, m in reversed(list(enumerate(tops))):
            t = m.group(1)
            if t not in ('study', 'learning'): continue
            tag = m.group(0); new = tag.replace('type="study"', 'type="learning"')
            mt = None
            body = '' if tag.endswith('/>') else s[m.end():s.find('</event>', m.end())]
            if idx < len(evs) and evs[idx]['type'] in ('study', 'learning') and 'type="method"' not in body:
                mt = method_of(evs[idx].get('quote'))
            s = s[:m.start()] + new + s[m.end():]
            if mt:
                desc = '<desc type="method" ref="#%s" xml:lang="ar">%s</desc>' % mt
                if new.endswith('/>'):
                    s = s[:m.start()] + new[:-2].rstrip() + '>' + desc + '</event>' + s[m.start() + len(new):]
                else:
                    e = m.start() + len(new); s = s[:e] + desc + s[e:]
                STAT['method'] += 1; msgs.append('学習の方法 %s（中心語「%s」から規則で）' % (mt[1], evs[idx]['quote']))
            if t == 'study': STAT['study'] += 1; msgs.append('event type study → learning')
        if s != o:
            for x in reversed(msgs): LOG.add(f, x)
            save(f, s)

    # B2: D00104 hajj / jāwara / burial written as top-level types
    f, s = load('D00104')
    s = one(s, '<event type="hajj"', '<event type="religious" subtype="hajj"', 'D00104')
    s = one(s, '<event type="jāwara"', '<event type="residence" subtype="jāwara"', 'D00104')
    m = re.search(r'\n\s*<event type="burial"[^>]*>.*?</event>', s, re.S); blk = m.group(0); s = s[:m.start()] + s[m.end():]
    pl = re.search(r'<placeName ref="([^"]+)">([^<]+)</placeName>', blk)
    d0 = s.index('<death'); dn = s.index('</death>', d0)
    ind = '        '
    s = s[:dn].rstrip(' ') + ind + '<placeName xml:lang="ar" type="burial" ref="%s">%s</placeName>\n' % pl.groups() + ind + \
        '<note xml:lang="ja">埋葬（「ودفن」、没日と同日）を event type="burial" から死亡の欄の埋葬地に移した（%s）</note>\n    ' % RULING + s[dn:]
    LOG.add(f, 'event type hajj → religious/hajj、jāwara → residence/jāwara、burial → death の埋葬地'); STAT['d00104'] += 1; save(f, s)

    # B3: funerals -> <death> (funeral prayer is not a bio event: app guide v20.2)
    for f in sorted(glob.glob('Individuals/**/*.xml', recursive=True)):
        s = open(f, encoding='utf-8').read()
        ms = list(re.finditer(r'\n( *)<event type="(?:religious|other|cultural)"[^>]*subtype="funeral"[^>]*>.*?</event>', s, re.S))
        if not ms: continue
        lines = []
        for m in reversed(ms):
            blk = m.group(0); s = s[:m.start()] + s[m.end():]
            body = re.sub(r'^\s*<event[^>]*>|</event>\s*$', '', blk.strip())
            ar = ' '.join(re.findall(r'<desc xml:lang="ar">(.*?)</desc>', body))
            role = 'funeral_attendee' if re.search(r'(^|\s)[وف]?(حضر|شهد)', ar) else 'funeral_prayer'
            out = []
            for el in re.findall(r'<(?:desc|persName|placeName|orgName|note)\b[^>]*>.*?</(?:desc|persName|placeName|orgName|note)>', body, re.S):
                if el.startswith('<desc'):
                    out.append(el.replace('<desc', '<note', 1).replace('</desc>', '</note>'))
                elif el.startswith('<persName'):
                    out.append(re.sub(r'<persName', '<persName role="%s"' % role, el, count=1) if 'role=' not in el else el)
                elif el.startswith('<placeName') or el.startswith('<orgName'):
                    out.append(re.sub(r'<(placeName|orgName)', r'<\1 type="funeral"', el, count=1) if 'type=' not in el.split('>')[0] else el)
                else:
                    out.append(el)
            lines = out + lines
            STAT['funeral'] += 1
        lines.append('<note xml:lang="ja">葬儀（صلاة الجنازة 等）は出来事にしない規則（アプリ v20.2）により、event subtype="funeral" から死亡の欄に移した。場所は type="funeral"、人物は role="funeral_prayer"／"funeral_attendee"（%s）</note>' % RULING)
        d0 = s.index('<death'); dn = s.index('</death>', d0)
        s = s[:dn].rstrip(' ') + ''.join('        ' + x + '\n' for x in lines) + '    ' + s[dn:]
        LOG.add(f, '葬儀の event %d 件を死亡の欄に移した' % len(ms)); save(f, s)

    # B4/B5
    for d, a, b, msg in [('D05963', '<event type="meeting"', '<event type="cultural" subtype="meeting"', 'event type meeting → cultural/meeting'),
                         ('D07958', '<event type="meeting"', '<event type="cultural" subtype="meeting"', 'event type meeting → cultural/meeting'),
                         ('D02938', '<event type="economic"', '<event type="other"', 'event type economic → other')]:
        f, s = load(d); s = one(s, a, b, d); LOG.add(f, msg); STAT['evtype'] += 1; save(f, s)


# ---------------------------------------------------------------- C. references
NEW = {  # new TMP issued here (ID-Master rows in TMP_register.tsv)
    'TMP-L-00419': 'خلد', 'TMP-L-00420': 'دلجة', 'TMP-L-00421': 'سجستان', 'TMP-L-00422': 'حارة عبد الباسط',
    'TMP-I-00294': 'تربة بكتمر الحاجب (بباب النصر)', 'TMP-I-00295': 'تربة رامشت (بالمعلاة)', 'TMP-I-00296': 'الإينالية (بالشارع، القاهرة)',
    'TMP-I-00297': 'رباط الموفى (مكة)', 'TMP-I-00298': 'قاعة السلاح المنسوبة للشيخ عبد الرحمن العجمي', 'TMP-I-00299': 'مسجد الجوزة (دمشق)',
    'TMP-I-00300': 'زاوية ابن الأطعاني (حلب)', 'TMP-T-00277': 'مسند المقلين من الصحابة (من حديث أبي الطاهر الذهلي)',
    'TMP-T-00278': 'الأدوار (للصفي عبد المؤمن الأرموي)', 'TMP-T-00279': 'فضائل ليلة نصف شعبان (لأبي القسم بن عساكر)',
    'TMP-T-00280': 'الكافية للزنجاني', 'TMP-N-05529': 'العبد الوادي', 'TMP-N-05530': 'السمي', 'TMP-S-00077': 'اشتغل | الاشتغال'}

REFS = [  # (record, old ref, new ref or None=remove attribute, text that must be in the element, message)
    ('D03541', '#NEEDID', '#TMP-T-00183', 'ثلاثيات', 'bibl ثلاثيات البخاري：#NEEDID → 既登録 TMP-T-00183'),
    ('D03541', '#NEEDID', '#TMP-T-00183', 'Thulāthiyyāt', None),
    ('D03417', '#NEEDID', 'wd:Q312342', None, 'affiliation الأزهر：#NEEDID → wd:Q312342'),
    ('D00972', '#NEEDID', '#TMP-L-00289', 'Ṣaḥrāʾ', '埋葬地（ar-Latn 行）：#NEEDID → TMP-L-00289（ar 行は 2026-09-25 裁定で是正済み、Latn 行が漏れていた）'),
    ('D04691', '#NEEDID', '#TMP-L-00036', 'جدة', '埋葬地「قبة لهم بجدة」：#NEEDID → TMP-L-00036 جدة（無名の廟は所在地の ID、2026-09-25 裁定 ★7 と同じ扱い）'),
    ('D04691', '#NEEDID', '#TMP-L-00036', 'Judda', None),
    ('D03644', '#NEEDID', '#TMP-I-00294', 'بكتمر', '埋葬地 تربة بكتمر الحاجب：#NEEDID → 新規 TMP-I-00294'),
    ('D03644', '#NEEDID', '#TMP-I-00294', 'Baqṭumur', None),
    ('D03622', '#NEEDID', '#TMP-I-00295', 'رامشت', '埋葬地 تربة رامشت：#NEEDID → 新規 TMP-I-00295'),
    ('D03622', '#NEEDID', '#TMP-I-00295', 'Rāmasht', None),
    ('D04632', '#NEEDID', '#TMP-T-00277', 'المقلين', 'bibl مسند المقلين：#NEEDID → 新規 TMP-T-00277'),
    ('D04632', '#NEEDID', '#TMP-T-00277', 'Muqillīn', None),
    ('D03414', '#NEEDID', '#TMP-T-00278', 'الأدوار', 'bibl الأدوار：#NEEDID → 新規 TMP-T-00278'),
    ('D03414', '#NEEDID', '#TMP-T-00278', 'Adwār', None),
    ('D04628', '#NEEDID', '#TMP-N-05529', 'العبد الوادي', 'nisbah العبد الوادي：#NEEDID → 新規 TMP-N-05529'),
    ('D06145', '#NEEDID', '#TMP-N-05530', 'السمي', 'nisbah السمي：#NEEDID → 新規 TMP-N-05530'),
    ('D04671', '#NEEDID', None, 'كتب جمة', 'bibl「كتب جمة」は書名でないので ID 欄を外した'),
    ('D04671', '#NEEDID', None, 'kutub jamma', None),
    ('D03405', '#NEEDID', None, 'حكاية', 'bibl「حكاية」は書名でないので ID 欄を外した'),
    ('D03405', '#NEEDID', None, 'Ḥikāya', None),
    ('D03405', '#NEEDID', None, 'حكاية', None),
    ('D03405', '#NEEDID', None, 'Ḥikāya', None),
    ('D04671', '#NEEDID', None, 'كتب جمة', None),
    ('D04671', '#NEEDID', None, 'kutub jamma', None),
    # reused (contaminated) numbers: early TMP numbers given to other entities
    ('D00039', '#TMP-L-00009', '#NEEDID', 'شيكه', '埋葬地「مقبرة شيكه لا لومد」：TMP-L-00009（الصف）の流用 → #NEEDID（刊本の語が読めず同定しない）'),
    ('D00039', '#TMP-L-00009', '#NEEDID', 'Shīka', None),
    ('D00218', '#TMP-L-00009', '#TMP-L-00278', 'قاسيون', 'سفح قاسيون：TMP-L-00009（الصف）の流用 → 既登録 TMP-L-00278'),
    ('D00218', '#TMP-L-00009', '#TMP-L-00278', 'Qāsyūn', None),
    ('D00344', '#TMP-L-00009', '#TMP-I-00023', 'يلبغا', 'تربة يلبغا：TMP-L-00009（الصف）の流用 → 既登録 TMP-I-00023'),
    ('D00430', '#TMP-L-00010', '#TMP-L-00419', 'خلد', 'خلد：TMP-L-00010（إب）の流用 → 新規 TMP-L-00419'),
    ('D00430', '#TMP-L-00010', '#TMP-L-00419', 'Khuld', None),
    ('D00480', '#TMP-L-00010', '#TMP-L-00420', 'دلجة', 'دلجة：TMP-L-00010（إب）・00011（شماخي）・00012（الحسا）の流用 → 新規 TMP-L-00420'),
    ('D00480', '#TMP-L-00011', '#TMP-L-00420', 'دلجة', None),
    ('D00480', '#TMP-L-00012', '#TMP-L-00420', 'دلجة', None),
    ('D00480', '#TMP-L-00012', '#TMP-L-00420', 'Dalja', None),
    ('D00772', '#TMP-L-00010', '#TMP-L-00271', 'لهيا', 'بيت لهيا：TMP-L-00010（إب）の流用 → 既登録 TMP-L-00271'),
    ('D00764', '#TMP-L-00010', '#TMP-L-00214', 'الهدة', 'الهدة：TMP-L-00010（إب）の流用 → 既登録 TMP-L-00214 وادي الهدة'),
    ('D00764', '#TMP-L-00010', '#TMP-L-00214', 'Hadda', None),
    ('D00745', '#TMP-L-00010', '#TMP-L-00305', 'صاروجا', 'سوق صاروجا：TMP-L-00010（إب）の流用 → 既登録 TMP-L-00305'),
    ('D01084', '#TMP-L-00011', '#TMP-L-00421', 'سجستان', 'سجستان：TMP-L-00011（شماخي）・00012（الحسا）の流用 → 新規 TMP-L-00421'),
    ('D01084', '#TMP-L-00012', '#TMP-L-00421', 'سجستان', None),
    ('D01335', '#TMP-L-00011', '#TMP-L-00422', 'عبد الباسط', 'حارة عبد الباسط：TMP-L-00011（شماخي）の流用 → 新規 TMP-L-00422'),
    ('D00642', '#TMP-L-00011', '#TMP-L-00223', 'شديد', 'خيف بني شديد：TMP-L-00011（شماخي）の流用 → 既登録 TMP-L-00223'),
    ('D00642', '#TMP-L-00011', '#TMP-L-00223', 'Shadīd', None),
    ('D00203', '#TMP-I-00049', '#TMP-I-00299', 'الجوزة', 'مسجد الجوزة：TMP-I-00049（تربة خشقدم）の流用 → 新規 TMP-I-00299'),
    ('D00250', '#TMP-I-00049', '#NEEDID', 'زاويته', '「زاويته」（父のザーウィヤ、名なし）：TMP-I-00049 の流用 → #NEEDID'),
    ('D00700', '#TMP-I-00049', '#TMP-I-00300', 'الأطعاني', 'زاوية ابن الأطعاني：TMP-I-00049 の流用 → 新規 TMP-I-00300'),
    ('D00743', '#TMP-I-00049', '#TMP-I-00183', 'ربيع', 'رباط ربيع：TMP-I-00049 の流用 → 既登録 TMP-I-00183'),
    ('D00758', '#TMP-I-00049', '#TMP-I-00296', 'الإينالية', 'الإينالية：TMP-I-00049 の流用 → 新規 TMP-I-00296'),
    ('D00758', '#TMP-I-00049', '#TMP-I-00296', None, None),
    ('D00503', '#TMP-I-00054', '#TMP-I-00298', 'قاعة', 'قاعة السلاح：TMP-I-00054（الفاضلية）の流用 → 新規 TMP-I-00298'),
    ('D00529', '#TMP-I-00054', '#TMP-I-00142', 'المعظمية', 'المعظمية（القدس）：TMP-I-00054 の流用 → 既登録 TMP-I-00142'),
    ('D00902', '#TMP-I-00054', '#TMP-I-00120', 'الحرم', 'الحرم المدني：TMP-I-00054 の流用 → 既登録 TMP-I-00120'),
    ('D01690', '#TMP-I-00054', '#TMP-I-00297', 'الموفى', 'رباط الموفى：TMP-I-00054 の流用 → 新規 TMP-I-00297'),
    ('D00946', '#TMP-N-05476', '#TMP-N-02333', 'العرجاني', 'nisbah العرجاني：TMP-N-05476（القوصي）の流用 → 既登録 TMP-N-02333'),
    ('D01272', '#TMP-N-05476', '#TMP-N-00322', 'البسطامي', 'nisbah البسطامي：TMP-N-05476（القوصي）の流用 → 既登録 TMP-N-00322'),
    ('D01664', '#TMP-T-00080', '#TMP-T-00279', 'شعبان', 'bibl فضائل ليلة نصف شعبان：TMP-T-00080（ألفية ابن مالك）の流用 → 新規 TMP-T-00279'),
    ('D01664', '#TMP-T-00080', '#TMP-T-00279', 'Shaʿbān', None),
    ('D01778', '#TMP-T-00071', '#TMP-T-00280', 'لزنجاني', 'bibl الكافية للزنجاني：TMP-T-00071（كافية ابن الحاجب）の流用 → 新規 TMP-T-00280'),
    ('D01778', '#TMP-T-00071', '#TMP-T-00280', 'Zanjānī', None),
]


def refs():
    for d, old, new, must, msg in REFS:
        f, s = load(d)
        pat = re.compile(r'<(\w+)\b([^<>]*?)\s(ref|active)="%s"([^<>]*)>([^<]*)' % re.escape(old))
        hits = [m for m in pat.finditer(s) if must is None or must in m.group(5)]
        if must is None:
            hits = [m for m in pat.finditer(s) if m.group(1) == 'affiliation']
        assert hits, (d, old, must)
        m = hits[0]
        rep = '' if new is None else ' %s="%s"' % (m.group(3), new)
        s = s[:m.start()] + '<%s%s%s%s>%s' % (m.group(1), m.group(2), rep, m.group(4), m.group(5)) + s[m.end():]
        if msg: LOG.add(f, msg)
        STAT['ref'] += 1; save(f, s)
    # D00412: orgName الخاصكية inside the khāṣṣakī state (TMP-O-00015) carried a reused TMP-I-00049
    f, s = load('D00412')
    s = one(s, '\n        <orgName ref="#TMP-I-00049">الخاصكية</orgName>', '', 'D00412')
    LOG.add(f, 'state الخاصكية（TMP-O-00015）の orgName（TMP-I-00049 の流用、الخاصكية は身分で施設ではない）を除去'); save(f, s)
    # D03644: affiliation type="buried" (abolished in app v20.1; burial lives in <death>)
    f, s = load('D03644')
    m = re.search(r'\n\s*<affiliation n="1" type="buried" ref="#NEEDID">.*?</affiliation>', s, re.S); assert m
    s = s[:m.start()] + s[m.end():]
    LOG.add(f, 'affiliation type="buried"（v20.1 で廃止、埋葬地は死亡の欄）を除去'); save(f, s)


# ---------------------------------------------------------------- D. «شيخنا» as the desc of Ibn Hajar (rule 31)
def shaykhuna():
    for f in sorted(glob.glob('Individuals/**/*.xml', recursive=True)):
        s = open(f, encoding='utf-8').read(); n = 0
        for m in reversed(list(re.finditer(r'<relation [^>]*>', s))):
            if 'wd:Q471116' not in m.group(0): continue
            close = s.index('</relation>', m.end())
            i = s.find('<desc xml:lang="ar">شيخنا</desc>', m.end(), close)
            if i < 0: continue
            s = s[:i] + '<desc xml:lang="ar">ابن حجر</desc><note xml:lang="ja">原文の呼称は「شيخنا」（規則31：desc は相手の名前のみ）</note>' + s[i + len('<desc xml:lang="ar">شيخنا</desc>'):]
            n += 1
        if n:
            LOG.add(f, 'イブン・ハジャルへの relation の desc「شيخنا」→「ابن حجر」、呼称は note（規則31、B169-173 集約 決定4 の repo 版）'); STAT['shaykhuna'] += n; save(f, s)


# ---------------------------------------------------------------- E. TMP-P-000005 = AIND-D04179 (Waka, viewer 2026-11-22)
def merge():
    f, s = load('D00005')
    s, c = re.subn(r'((?:ref|active|passive)=")#TMP-P-000005"', r'\1#AIND-D04179"', s); assert c == 2, c
    LOG.add(f, 'الزين عبد القادر النووي المقدسي：TMP-P-000005 → #AIND-D04179（本伝「عبد القادر بن محمد بن حسن الزين النووي الأصل المقدسي」でラカブ・ニスバ2つが閉合。Waka 2026-11-22 ビューアーで決定）')
    STAT['merge'] += 1; save(f, s)


if __name__ == '__main__':
    dates(); events(); refs(); shaykhuna(); merge()
    finish(LOG, '修正（トリプル書き出しに向けた整備・2026-11-22 Waka 裁定と既定の規則の反映）')
    print(dict(STAT), 'files', len(LOG.d))
    json.dump(LOG.d, open(os.path.join(os.path.dirname(__file__), 'changes.json'), 'w'), ensure_ascii=False, indent=1)
