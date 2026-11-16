"""本項主が active の親族・社会 relation の是正（2026-11-16）
統一規則: subtype は「active が passive の何にあたるか」、親族・社会関係は active=相手・passive=本項主。
 - 'swap'        : 向きの符号化が逆（subtype は相手の役割を表していた）→ active/passive を入れ替える
 - 'inv:<st>'    : 符号化自体は統一規則で正しい（本項主が相手の <旧subtype>）→ active=相手 にし subtype を逆関係に
 - 'keep'        : 逆関係の語が統制語彙にないため、統一規則で正しい形のまま残す
対称な関係は 'swap'（subtype 不変）。統制外 subtype は対象外。
"""
import glob, re, sys, os, csv

ROOT, LOG = sys.argv[1], sys.argv[2]
SYM = {'brother', 'sister', 'cousin', 'spouse', 'colleague', 'friend', 'companion', 'rival', 'relative',
       'possible_identity', 'brother-in-law', 'met', 'other', 'neighbor'}
SKIP = {'praise', 'see_also', 'master', 'educator_of', 'correspondent', 'teacher'}
# 本文照合で決めた処置（kin_active_review の非対称 39 件、出現順）
ACTION = {
 1: 'swap', 2: 'swap', 3: 'swap', 4: 'swap', 5: 'relative', 6: 'inv:son', 7: 'inv:predecessor', 8: 'swap',
 9: 'swap', 10: 'inv:son-in-law', 11: 'inv:predecessor', 12: 'inv:son', 13: 'inv:siblings_child',
 14: 'inv:siblings_child', 15: 'inv:siblings_child', 16: 'inv:siblings_child', 17: 'inv:client',
 18: 'inv:son-in-law', 19: 'inv:grandson', 20: 'swap', 21: 'inv:siblings_child', 22: 'inv:siblings_child',
 23: 'keep', 24: 'inv:siblings_child', 25: 'swap', 26: 'swap', 27: 'swap', 28: 'swap', 29: 'swap',
 30: 'swap', 31: 'swap', 32: 'swap', 33: 'inv:siblings_child', 34: 'inv:grandson', 35: 'inv:grandson',
 36: 'inv:client', 37: 'inv:client', 38: 'inv:daughter', 39: 'inv:son-in-law',
}
DATE, WHO = '2026-11-16', 'claude-opus-5-5-relation-unify'
log = []; k = 0; files = 0
for f in sorted(glob.glob(os.path.join(ROOT, 'Individuals/*/AIND-D*.xml'))):
    me = re.search(r'(AIND-D\w+?)_', os.path.basename(f)).group(1)
    t = open(f, encoding='utf-8').read()
    notes = []

    def fix(m):
        global k
        tag = m.group(0)
        st = re.search(r'subtype="([^"]+)"', tag).group(1)
        if st in SKIP:
            return tag
        ac = re.search(r'\sactive="([^"]+)"', tag).group(1)
        pa = re.search(r'\spassive="([^"]+)"', tag).group(1)
        if ac != '#' + me:
            return tag
        if st in SYM:
            act = 'swap'
        else:
            k += 1
            act = ACTION[k]
        if act == 'keep':
            log.append([me, k, st, pa, act, tag, tag]); return tag
        new = re.sub(r'\sactive="[^"]+"', f' active="{pa}"', tag, count=1)
        new = re.sub(r'\spassive="[^"]+"', f' passive="#{me}"', new, count=1)
        if act.startswith('inv:'):
            new = new.replace(f'subtype="{st}"', f'subtype="{act[4:]}"', 1)
            notes.append(f'{pa}: 「本項主が相手の {st}」→ active=相手・subtype={act[4:]}')
        elif act == 'relative':
            new = new.replace(f'subtype="{st}"', 'subtype="relative"', 1)
            notes.append(f'{pa}: 「صهر」で向きが決まらないため {st} → relative（規則52）・active=相手')
        else:
            notes.append(f'{pa}: 逆向きの符号化を是正（{st}、active=相手）')
        log.append([me, k if st not in SYM else '', st, pa, act, tag, new])
        return new

    t2 = re.sub(r'<relation\b[^>]*>', fix, t)
    if t2 != t:
        note = '親族・社会 relation の向きを統一規則（active=相手・passive=本項主、subtype＝active が passive の何にあたるか）に合わせた。' + '／'.join(notes) + '。'
        resp = ('    <respStmt>\n'
                '        <resp xml:lang="ja">修正（relation の向きの統一・2026-11-16 Waka 依頼）</resp>\n'
                f'        <note xml:lang="ja">{note}</note>\n'
                f'        <persName>{WHO}</persName>\n'
                f'        <date when="{DATE}"/>\n'
                '    </respStmt>\n')
        idx = t2.rfind('</person>'); ls = t2.rfind('\n', 0, idx) + 1
        t2 = t2[:ls] + resp + t2[ls:]
        open(f, 'w', encoding='utf-8').write(t2); files += 1
assert k == 39, k
with open(LOG, 'w', encoding='utf-8', newline='') as fh:
    w = csv.writer(fh, delimiter='\t'); w.writerow(['aind', 'k', 'old_subtype', 'partner', 'action', 'old_tag', 'new_tag']); w.writerows(log)
from collections import Counter
print('files', files, Counter(r[4].split(':')[0] for r in log))
