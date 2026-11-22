"""Apply the 2026-11-22 rulings to Individuals/:
  (1) out-of-vocabulary relation subtypes (151 relations, groups A-H)
  (2) event fixes ★1-★11 from docs/accuracy/yaml_patterns_20261122/rulings_draft.md
Every changed file gets one respStmt that lists what changed. Run from the repo root."""
import glob, re, sys, collections
from lxml import etree

TODAY = '2026-11-22'
WHO = 'claude-opus-5-5-vocab-20261122'
FILES = {}
for f in glob.glob('Individuals/**/*.xml', recursive=True):
    m = re.match(r'(AIND-D\w+?)_\d+\.xml$', f.split('/')[-1])
    if m: FILES[m.group(1)] = f
LOG = collections.defaultdict(list)
DOCS = {}


def doc(pid):
    if pid not in DOCS:
        DOCS[pid] = etree.parse(FILES[pid], etree.XMLParser(remove_blank_text=False))
    return DOCS[pid].getroot()


def rels(p, subtype=None, active=None):
    out = []
    for r in p.iter('relation'):
        if subtype is not None and r.get('subtype') != subtype: continue
        if active is not None and r.get('active') != active: continue
        out.append(r)
    return out


def top_events(p):
    return [e for e in p if e.tag == 'event']


def el(tag, text=None, **att):
    e = etree.Element(tag)
    for k, v in att.items():
        if v is None: continue
        e.set('{http://www.w3.org/XML/1998/namespace}lang' if k == 'lang' else k, v)
    if text: e.text = text
    return e


def append_child(parent, child, indent):
    """append child keeping the file's one-element-per-line indentation"""
    kids = list(parent)
    if kids:
        last = kids[-1]
        child.tail = last.tail
        last.tail = '\n' + indent
    else:
        parent.text = (parent.text or '') + '\n' + indent
        child.tail = '\n' + indent[:-4]
    parent.append(child)


def rel_text(r):
    d = r.find('desc')
    return (d.text or '').strip() if d is not None else ''


def rel_notes(r):
    return [n for n in r.findall('note')]


def add_event(p, etype, subtype=None, persons=(), desc_en=None, notes=(), **att):
    ev = el('event', type=etype, subtype=subtype)
    ns = [int(e.get('n')) for e in top_events(p) if (e.get('n') or '').isdigit()]
    ev.set('n', str(max(ns) + 1 if ns else 1))
    for k, v in att.items():
        if v: ev.set(k.replace('_', '-'), v)
    if desc_en:
        ev.append(el('desc', desc_en, lang='en'))
    for ref, role, txt in persons:
        ev.append(el('persName', txt, ref=ref, role=role))
    for n in notes:
        ev.append(n)
    evs = top_events(p)
    anchor = evs[-1] if evs else None
    if anchor is None:
        for c in p:
            if c.tag in ('state', 'note', 'respStmt'): anchor = c.getprevious(); break
    idx = list(p).index(anchor) + 1 if anchor is not None else len(p)
    ev.tail = '\n    '
    if anchor is not None:
        ev.tail = anchor.tail; anchor.tail = '\n    '
    p.insert(idx, ev)
    return ev


def drop(r):
    lr = r.getparent()
    prev = r.getprevious()
    if prev is not None: prev.tail = r.tail if r.tail is not None else prev.tail
    else: lr.text = r.tail if r.tail is not None else lr.text
    lr.remove(r)
    if lr.tag == 'listRelation' and len(lr) == 0:
        pp = lr.getparent(); pr = lr.getprevious()
        if pr is not None: pr.tail = lr.tail
        pp.remove(lr)


def mention_or_merge(p, r, etype='cultural', subtype='mention', role=None, why=''):
    ref = r.get('active'); txt = rel_text(r)
    for ev in top_events(p):
        if ev.get('type') == etype and ev.get('subtype') == subtype and any(pn.get('ref') == ref for pn in ev.findall('persName')):
            for n in rel_notes(r): append_child(ev, n, '        ')
            drop(r); return f'relation「{r.get("subtype")}」({ref}) を除去し、既存の {etype}/{subtype} event に注記を移した。{why}'
    long = len(txt.split()) > 4
    ev = add_event(p, etype, subtype, [(ref, role, None if long else txt)], notes=rel_notes(r))
    if long:
        d = el('desc', txt, lang='ar'); ev.insert(0, d)
    if r.get('cert'): ev.set('cert', r.get('cert'))
    drop(r)
    return f'relation「{r.get("subtype")}」({ref}) を {etype}{"/" + subtype if subtype else ""} event の persName{"（role=" + role + "）" if role else ""} に移した。{why}'


def to_xref(p, r):
    tgt = r.get('active'); txt = rel_text(r)
    n = el('note', txt or None, type='cross-reference', target=None if tgt == '#NEEDID' else tgt)
    for nn in rel_notes(r):
        if nn.text: n.text = ((n.text + ' — ') if n.text else '') + nn.text
    idx = list(p).index(p.find('listRelation'))
    n.tail = '\n    '
    p.insert(idx + 1, n)
    old = r.get('subtype'); drop(r)
    return f'relation「{old}」は編者の参照指示（له ذكر في 型）なので除去し、note type="cross-reference" に移した（先例 D02012・D02015）。'


def to_death_person(p, r, role, why):
    d = p.find('death')
    if d is None:
        return mention_or_merge(p, r, 'religious', 'funeral', role, why)
    pn = el('persName', rel_text(r) or None, ref=r.get('active'), role=role, cert=r.get('cert'))
    append_child(d, pn, '        ')
    for n in rel_notes(r): append_child(d, n, '        ')
    old = r.get('subtype'); drop(r)
    return f'relation「{old}」は葬儀・埋葬の記述なので除去し、<death> の persName（role={role}）に移した（葬儀は bio_event にしない規則）。{why}'


def resub(r, new, why='', swap=False, note=None):
    old = r.get('subtype'); r.set('subtype', new)
    if swap:
        a, b = r.get('active'), r.get('passive'); r.set('active', b); r.set('passive', a)
    if note:
        r.append(el('note', note, lang='ja'))
    return f'relation subtype「{old}」→「{new}」{"（active/passive を入替え）" if swap else ""}。{why}'


# ---------- (1) out-of-vocabulary relations ----------
A_MENTION = ['mentioned by', 'praised by', 'informant/source', 'author/compiler', 'mention', 'mentioned_by', 'biographer',
             'praiser', 'chronicler', "mentioned in his Mu'jam"]
XREF = ['mentioned_in', 'mentioned in connection with', 'mentioned in biography', 'cross-reference']
COMP = ['companion of', 'travel companion', 'companionship', 'associate']
MEET = ['met', 'met_or_known_by', 'acquaintance']
PATRON = ['servant/master', 'employer', 'employed under', 'servant', 'employer/superior', 'master-slave/mamluk relation',
          'military_superior', 'intimate companion', 'nisbah origin']
KIN = {'nephew': 'siblings_child', 'child': 'son', 'paternal_grandfather': 'grandfather', 'relative_by_marriage': 'relative',
       'co-father-in-law': 'relative', 'father of daughter-in-law': 'relative', 'daughter-in-law': 'relative',
       'marriage alliance': 'relative', 'granduncle': 'relative'}
KIN_NOTE = {'granduncle': '大叔父（祖父母の兄弟）。統制語彙に該当語がないため relative（2026-11-22 裁定）。',
            'co-father-in-law': '子どうしの婚姻による姻戚（規則52、向きの決まらない姻戚は relative）。',
            'father of daughter-in-law': '息子の妻の父（規則52）。', 'daughter-in-law': '息子の妻（規則52）。',
            'marriage alliance': '「صاهر」型の姻戚（規則52）。'}
OTHER = {'neighbor': '隣人（جار）', 'townsman': '同郷（بلدي）', 'compatriot': '同郷', 'believer/admirer': '「له فيه اعتقاد」型（相手が本項主の聖性を信じた）',
         'spiritual relationship': '本項主が相手の聖性を強く信じた（اعتقاد）', 'sovereign': '本項主の在職がこの君主の治世であったことの記述'}
FUNERAL = {'funeral_attendee': 'funeral_prayer', 'led funeral prayer for': 'funeral_prayer', 'funeral': 'funeral_prayer',
           'neighbor in burial': 'buried_near'}
EVENT_ROLE = {  # subtype -> (event type, event subtype, role)
    'captor': ('political', None, 'captor'), 'jailer': ('political', None, 'imprisoner'),
    'executor of will': ('other', None, 'executor'), 'intended host': ('travel', None, 'intended_host'),
    '仲介者': ('cultural', 'ijaza', 'mediator'), 'mediator': ('cultural', None, 'beneficiary'),
    'facilitator': ('political', None, 'facilitator'), 'diplomatic contact': ('political', None, 'recipient'),
    'event-related': ('political', None, 'participant'), 'reciter': ('cultural', None, 'reader'),
    'reciter in learning session': ('cultural', None, 'reader'), 'witness': ('cultural', 'ijaza', 'witness'),
    'witness_for': ('cultural', 'ijaza', 'grantor'), 'composed for': ('cultural', None, 'dedicatee'),
    'praised_in_poetry': ('cultural', None, 'dedicatee'), 'author of studied treatise': ('cultural', None, 'author'),
}

oov = [l.rstrip('\n').split('\t') for l in open(sys.argv[1], encoding='utf-8')][1:]
grouped = collections.defaultdict(list)
for pid, typ, st, act, pas, desc in oov:
    grouped[(pid, st.replace('&apos;', "'"))].append(act)

for (pid, st), acts in grouped.items():
    p = doc(pid)
    for act in dict.fromkeys(acts):
        cands = [r for r in rels(p, st, act)]
        if not cands and st == 'predecessor':
            cands = [r for r in p.iter('relation') if r.get('subtype') == st and r.get('type') != 'personal' and r.get('active') == act]
        for r in cands:
            if pid == 'AIND-D05637' and st == 'witness_for':
                continue
            if pid == 'AIND-D03182' and st == 'met':
                LOG[pid].append(to_xref(p, r))
            elif st == 'deputy':
                LOG[pid].append(resub(r, 'deputy', 'subtype は「active が passive の何にあたるか」（規則15）により active＝代理（本項主）・passive＝本務者に（2026-11-22 裁定、educator と同じ本項主 active の例外）。', swap=True))
            elif st in COMP:
                LOG[pid].append(resub(r, 'companion', '統制語彙に companion（صحبة・同行）を新設（2026-11-22 裁定）。'))
            elif st == 'companion':
                pass
            elif st in MEET:
                LOG[pid].append(mention_or_merge(p, r, 'cultural', 'meeting', None, '学習を伴わない面会は event（2026-10-27 裁定）。'))
            elif st in A_MENTION:
                LOG[pid].append(mention_or_merge(p, r, 'cultural', 'mention', None, '言及・典拠は人的関係ではないので Pattern A（2026-11-22 裁定）。'))
            elif st in XREF or (st == 'met' and False):
                LOG[pid].append(to_xref(p, r))
            elif st in PATRON:
                LOG[pid].append(resub(r, 'patron', '仕えた・重用された・マムルークの主は patron（規則51、2026-11-22 裁定）。'))
            elif st in KIN:
                LOG[pid].append(resub(r, KIN[st], '親族の表記を統制語彙に統一（2026-11-22 裁定）。', note=KIN_NOTE.get(st)))
            elif st in OTHER:
                LOG[pid].append(resub(r, 'other', '統制語彙外の弱い関係は other＋note（2026-11-22 裁定）。', note=OTHER[st] + '。元の subtype「' + st + '」。'))
            elif st in FUNERAL:
                LOG[pid].append(to_death_person(p, r, FUNERAL[st], ''))
            elif st in EVENT_ROLE:
                et, es, role = EVENT_ROLE[st]
                LOG[pid].append(mention_or_merge(p, r, et, es, role, '出来事にあたる記述は relation でなく event の persName（2026-11-22 裁定）。'))
            elif st == 'predecessor':
                r.set('type', 'personal'); LOG[pid].append('relation type「professional」→「personal」（predecessor は社会関係の統制語彙）。')
            elif st in ('killed together with', 'host', 'chief / head', 'appointer', 'advisor/tutor'):
                pass  # handled individually below
            else:
                print('UNHANDLED', pid, st, act)

# individual cases
def one(pid, st, act=None):
    c = rels(doc(pid), st, act)
    assert len(c) == 1, (pid, st, act, len(c))
    return c[0]

p = doc('AIND-D00311'); r = one('AIND-D00311', 'chief / head')
t = [x for x in rels(p, 'teacher', '#AIND-D10558')][0]
for n in rel_notes(r): append_child(t, n, '            ')
drop(r); LOG['AIND-D00311'].append('relation「chief / head」(#AIND-D10558) は同じ相手の teacher relation と重複（「رئيسه الفقيه يوسف المقرى فقرأ عليه」）のため除去し、注記を teacher に移した。')
r = one('AIND-D00524', 'appointer')
LOG['AIND-D00524'].append(resub(r, 'deputy', '「العز الكناني」が本項主を代理（نائب）・カーディーに任じた＝本項主はその代理（2026-11-22 裁定の deputy）。', swap=True))
r = one('AIND-D01702', 'advisor/tutor')
LOG['AIND-D01702'].append(resub(r, 'client', '本項主は「أستاذ الظاهر برقوق」（バルクークの主人）＝バルクークは本項主の client（規則51・規則15）。'))
p = doc('AIND-D01702'); r = one('AIND-D01702', 'killed together with')
ev = [e for e in top_events(p) if e.get('type') == 'political'][0]
ev.append(el('persName', rel_text(r), ref=r.get('active'), role='co-victim'))
drop(r); LOG['AIND-D01702'].append('relation「killed together with」(#AIND-D02089 أيتمش) を除去し、殺害の political event の persName（role=co-victim）に移した（★9）。')
p = doc('AIND-D05637'); ra = one('AIND-D05637', 'witness_for', '#TMP-P-000822'); rb = one('AIND-D05637', 'witness_for', '#TMP-P-000823')
add_event(p, 'cultural', 'ijaza', [('#TMP-P-000822', 'grantor', rel_text(ra)), ('#TMP-P-000823', 'recipient', rel_text(rb))],
          notes=rel_notes(ra) + rel_notes(rb))
drop(ra); drop(rb)
LOG['AIND-D05637'].append('relation「witness_for」2件（イジャーザを与えた父 #TMP-P-000822・受けた息子 #TMP-P-000823）を、本項主が証人となった cultural/ijaza event 1件の persName（role=grantor／recipient）に移した（2026-11-22 裁定）。')
p = doc('AIND-D02364'); r = one('AIND-D02364', 'host')
ev = top_events(p)[2]
ev.append(el('persName', rel_text(r), ref=r.get('active'), role='host'))
drop(r); LOG['AIND-D02364'].append('relation「host」(#TMP-P-000683 ابن دلغادر) を除去し、「ظهر عند ابن دلغادر」の political event の persName（role=host）に移した（★9）。')


# ---------- (2) event fixes ★1-★11 ----------
def pl(ref, txt, **att): return el('placeName', txt, ref=ref, **att)

def ev_n(pid, i): return top_events(doc(pid))[i - 1]

# ★1 D00005
p = doc('AIND-D00005'); e1, e2 = ev_n('AIND-D00005', 1), ev_n('AIND-D00005', 2)
for c in list(e1): e1.remove(c)
e1.text = None
for c in (pl('gn:281184', 'بيت المقدس', role='origin'), pl('gn:104515', 'مكة', role='destination'),
          el('persName', 'الزين عبد القادر النووي المقدسي', ref='#TMP-P-000005', role='companion'),
          el('note', 'يكثر', type='frequency', lang='ar')):
    e1.append(c)
prev = e2.getprevious(); prev.tail = e2.tail; p.remove(e2)
LOG['AIND-D00005'].append('★1：出発地・到着地で2件に分かれていた travel を1件に統合（placeName role=origin／destination）、同行者を persName（role=companion、#TMP-P-000005）に、「يكثر」を note type="frequency" に（2026-11-22 裁定）。')

# ★2 D01363, ★3 D01735
for pid, quote in (('AIND-D01363', 'إما بالروم أو حلب'), ('AIND-D01735', 'من علماء دنجية أو دمياط')):
    p = doc(pid); a, b = ev_n(pid, 1), ev_n(pid, 2)
    pb = b.find('placeName'); pa = a.find('placeName')
    for x in (pa, pb): x.set('role', 'alternative'); x.set('cert', 'low')
    pa.addnext(pb)
    for n in a.findall('note'): a.remove(n)
    a.append(el('note', f'本文は「{quote}」の二択。どちらか一方（2026-11-22 裁定）。', lang='ja'))
    prev = b.getprevious(); prev.tail = b.tail; p.remove(b)
    LOG[pid].append(f'★{2 if pid.endswith("1363") else 3}：二択の居所が2件の residence に分かれていたのを1件に統合し、placeName を role="alternative"・cert="low" に（2026-11-22 裁定）。')

# ★4 D02072
p = doc('AIND-D02072'); e1, e2 = ev_n('AIND-D02072', 1), ev_n('AIND-D02072', 2)
for e in (e1, e2):
    prev = e.getprevious(); prev.tail = e.tail; p.remove(e)
add_event(p, 'political', None, [('wd:Q8462', 'appointer', 'أبوه')],
          desc_en='Appointed over Azerbaijan by his father (Tīmūr) in 802, when Tīmūr came from India into Syria.',
          notes=[el('note', '本文「ولاه أبوه أذربيجان في سنة اثنتين وثمانمائة عند قدومه من بلاد الهند إلى البلاد الشامية」。インドからシリアへ来たのは父ティムールで、本項主の移動ではない（2026-11-22 裁定 ★4）。', lang='ja')],
          when_custom='0802').insert(1, pl('wd:Q12836408', 'أذربيجان'))
LOG['AIND-D02072'].append('★4：父ティムールの移動を本項主の travel 2件として立てていたのを削除し、「父によりアゼルバイジャンを任された」political event（802、persName role=appointer wd:Q8462）を立てた（2026-11-22 裁定）。')

# ★5 D04366
e = ev_n('AIND-D04366', 2); e.find('placeName').set('role', 'origin'); e.find('placeName').addnext(pl('gn:104515', 'مكة', role='destination'))
LOG['AIND-D04366'].append('★5：「انتقل من شيراز إلى مكة」の travel に到着地 مكة を加え、placeName に role=origin／destination（2026-11-22 裁定）。')
# ★6 D07533
ev_n('AIND-D07533', 1).find('placeName').set('role', 'origin')
LOG['AIND-D07533'].append('★6：「رجوعه من القاهرة إلى بلده」の القاهرة を role=origin に。「بلده」は地名でないので note のまま（規則25、2026-11-22 裁定）。')
# ★7
for pid, idx in (('AIND-D05733', (1, 2)), ('AIND-D09231a', (1,))):
    for i in idx: ev_n(pid, i).find('placeName').set('role', 'destination')
    LOG[pid].append('★7：「قدم من بلاده إلى …」の到着地の placeName に role=destination（出発地「بلاده」は地名でない、2026-11-22 裁定）。')
# ★8
for pid, idx, phrase in (('AIND-D02136', (1, 2), 'يكثر السفر'), ('AIND-D04533', (3, 4), 'يتردد'), ('AIND-D05378', (1, 2), 'تكرر دخوله')):
    for i in idx:
        e = ev_n(pid, i); e.find('placeName').set('role', 'destination')
        e.find('placeName').addnext(el('note', phrase, type='frequency', lang='ar'))
    LOG[pid].append(f'★8：繰り返しの移動（「{phrase}」）。行き先ごとの件数はそのままで、placeName に role=destination、note type="frequency" を付した（2026-11-22 裁定）。')
# ★9 (the rest; D01702・D02364 done above)
def addp(pid, i, ref, role, txt):
    ev_n(pid, i).append(el('persName', txt, ref=ref, role=role))
addp('AIND-D01171', 1, '#AIND-D07156', 'killer', 'الشريف محمد بن بركات'); addp('AIND-D01171', 1, '#AIND-D07152', 'co-victim', 'محمد بن بدير')
addp('AIND-D01893', 1, '#AIND-D06290', 'companion', 'قانصوة الشامي')
addp('AIND-D05353', 1, '#AIND-D04894', 'rival', 'العجل بن عجلان')
addp('AIND-D05644', 2, '#TMP-P-000824', 'companion', 'الشريف إسحق')
addp('AIND-D00129', 2, 'wd:Q4120128', 'teacher', 'عندي')
p = doc('AIND-D02441'); r = one('AIND-D02441', 'colleague', '#AIND-D03018')
addp('AIND-D02441', 1, '#AIND-D03018', 'co-victim', 'السيد رميثة'); drop(r)
for pid in ('AIND-D01171', 'AIND-D01893', 'AIND-D05353', 'AIND-D05644', 'AIND-D00129'):
    LOG[pid].append('★9：出来事の関係者を、既存の relation の相手（同じ ID）で event の persName（@role）に結んだ（2026-11-22 裁定）。')
LOG['AIND-D02441'].append('★9：「قتل مع السيد رميثة」を colleague relation から外し、殺害の political event の persName（role=co-victim、#AIND-D03018）に移した（2026-11-22 裁定）。')
# ★10 D01729
addp('AIND-D01729', 1, '#NEEDID', 'replacement', 'العيزري')
ev_n('AIND-D01729', 1).append(el('note', '「صرف في بعضها بالعيزري」の العيزري は同ニスバの人物が複数（候補 #AIND-D09091 ほか）で特定できない（規則26、2026-11-22 裁定 ★10）。', lang='ja'))
LOG['AIND-D01729'].append('★10：後任者 العيزري を persName #NEEDID（role=replacement）で event に置き、候補を note に（2026-11-22 裁定）。')
# ★11 D02521
p = doc('AIND-D02521'); e1, e3 = ev_n('AIND-D02521', 1), ev_n('AIND-D02521', 3)
e3.append(el('note', '見出しの「نزيل طيبة」も同じ居住（طيبة＝المدينة）。旧 event n=1 を統合（2026-11-22 裁定 ★11）。', lang='ja'))
prev = e1.getprevious(); prev.tail = e1.tail; p.remove(e1)
LOG['AIND-D02521'].append('★11：同じマディーナ居住の residence 2件（طيبة／المدينة النبوية）を1件に統合（2026-11-22 裁定）。')

# ---------- write ----------
for pid, lines in LOG.items():
    p = doc(pid)
    rs = el('respStmt')
    rs.append(el('resp', '修正（統制語彙外 relation の整理・誤りの型 P1/P2/P6 の是正、2026-11-22 Waka 裁定）', lang='ja'))
    rs.append(el('persName', WHO)); rs.append(el('date', when=TODAY))
    rs.append(el('note', ' '.join(lines), lang='ja'))
    for i, c in enumerate(rs): c.tail = '\n        '
    rs.text = '\n        '; list(rs)[-1].tail = '\n    '
    append_child(p, rs, '    ')
    s = etree.tostring(p, encoding='unicode')
    nl = open(FILES[pid], encoding='utf-8').read().endswith('\n')
    open(FILES[pid], 'w', encoding='utf-8').write(s + ('\n' if nl else ''))
print(len(LOG), 'files changed')
