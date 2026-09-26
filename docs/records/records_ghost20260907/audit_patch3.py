# 監査_20260907 第2ラウンド: 空 active/passive relation 131件の紐付け
# usage: python3 audit_patch3.py <Individuals dir> [--dry]
import sys, glob, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from empty_decisions import DEC
D = sys.argv[1]; DRY = '--dry' in sys.argv
START = 966
REL = re.compile(r'<relation\b[^>]*>.*?</relation>|<relation\b[^>]*/>', re.S)
newtmp = []   # (id, name, latin, note)
alloc = {}    # (pid, NEWspec) -> id
log = []
def attr(s, a):
    m = re.search(r'\b%s="([^"]*)"' % a, s); return m.group(1) if m else None
files = sorted(glob.glob(os.path.join(D, 'AIND-*.xml')))
seen_keys = set()
for f in files:
    s = open(f, encoding='utf-8').read()
    pid = re.search(r'xml:id="([^"]+)"', s).group(1)
    if not re.search(r'\b(active|passive)=""', s): continue
    son_ct = 0; out = s; last_new = None
    for m in list(REL.finditer(s)):
        el = m.group(0)
        if 'active=""' not in el and 'passive=""' not in el: continue
        sub = attr(el, 'subtype'); n = attr(el, 'n')
        dm = re.search(r'<desc xml:lang="ar">([^<]*)</desc>', el); desc = (dm.group(1) if dm else '').strip()
        cands = [(pid, sub, desc)]
        if n: cands.append((pid, sub, 'n=%s' % n))
        cands.append((pid, sub, ''))
        if pid == 'AIND-D00813' and sub == 'son':
            son_ct += 1; cands = [(pid, sub, 'n=%s' % 'ab'[son_ct-1])]
        if pid == 'AIND-D01663': cands = [(pid, sub, 'n=x')]
        key = next((c for c in cands if c in DEC), None)
        if key is None:
            print('NO DECISION', pid, sub, n, desc[:40]); continue
        seen_keys.add(key); dec = DEC[key]
        if dec == 'DEL':
            new = ''; log.append((pid, sub, desc, 'DEL'))
        else:
            if dec.startswith('NEW:'):
                name, latin, note = dec[4:].split('|')
                tid = 'TMP-P-%06d' % (START + len(newtmp)); newtmp.append((tid, name, latin, note)); last_new = tid; ref = '#' + tid
            elif dec == 'SAME':
                ref = '#' + last_new
            else:
                ref = dec
            new = el.replace('active=""', 'active="%s"' % ref) if 'active=""' in el else el.replace('passive=""', 'passive="%s"' % ref)
            if ref == '#NEEDID' and 'xml:lang="ja"' not in new:
                note = '<note xml:lang="ja">監査20260907: 本文から相手を一意に特定できず #NEEDID</note>'
                new = new.replace('</relation>', note + '</relation>') if '</relation>' in new else new[:-2] + '>' + note + '</relation>'
            if key == ('AIND-D01597', 'father', 'محمد شهاب الدين'):
                new = new.replace('<desc xml:lang="ar">محمد شهاب الدين</desc>', '<desc xml:lang="ar">ناصر الدين محمد</desc>')
            log.append((pid, sub, desc, ref))
        out = out.replace(el, new, 1)
    if not DRY:
        open(f, 'w', encoding='utf-8').write(out)
missing = set(DEC) - seen_keys
print('unused decisions:', missing)
print('relations handled:', len(log), ' new TMP:', len(newtmp), ' last:', newtmp[-1][0] if newtmp else None)
json.dump({'log': log, 'newtmp': newtmp}, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audit_patch3_log.json'), 'w'), ensure_ascii=False, indent=0)
