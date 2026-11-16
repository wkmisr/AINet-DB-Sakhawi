"""師弟 relation の表記統一（2026-11-16）
規則: subtype は「active が passive の何にあたるか」。師弟は常に subtype="teacher"・active=師・passive=学生。
 1. subtype="student" かつ active=本項主  → subtype だけ teacher に（向きはそのまま）
 2. subtype="student" かつ passive=本項主 → 向きの逆転（本項主が師）: active/passive を入れ替え teacher に
 3. active の欠けた relation → active="#NEEDID" を補う（student で passive=本項主のものは 2 と同じく本項主=師）
各ファイルに respStmt を追記し、変更一覧 TSV を出力する。
"""
import glob, re, sys, csv, os

ROOT = sys.argv[1]
LOG = sys.argv[2]
DATE = '2026-11-16'
WHO = 'claude-opus-5-5-relation-unify'

rel_re = re.compile(r'<relation\b[^>]*>')
log = []
changed_files = 0

for f in sorted(glob.glob(os.path.join(ROOT, 'Individuals/*/AIND-D*.xml'))):
    me = re.search(r'(AIND-D\w+?)_', os.path.basename(f)).group(1)
    t = open(f, encoding='utf-8').read()
    kinds = []

    def fix(m):
        tag = m.group(0)
        st = re.search(r'subtype="([^"]*)"', tag)
        st = st.group(1) if st else ''
        ac = re.search(r'\sactive="([^"]*)"', tag)
        pa = re.search(r'\spassive="([^"]*)"', tag)
        acv = ac.group(1) if ac else None
        pav = pa.group(1) if pa else None
        n = re.search(r'\sn="([^"]*)"', tag)
        n = n.group(1) if n else ''
        new = tag
        kind = None
        if st == 'student':
            if acv == '#' + me:
                new = tag.replace('subtype="student"', 'subtype="teacher"', 1)
                kind = 'relabel'
            elif pav == '#' + me:
                other = acv if acv else '#NEEDID'
                new = tag.replace('subtype="student"', 'subtype="teacher"', 1)
                if ac:
                    new = re.sub(r'\sactive="[^"]*"', f' active="#{me}"', new, 1)
                    new = re.sub(r'\spassive="[^"]*"', f' passive="{other}"', new, 1)
                else:
                    new = re.sub(r'\spassive="[^"]*"', f' active="#{me}" passive="{other}"', new, 1)
                kind = 'reverse'
            else:
                kind = 'UNHANDLED'
        elif ac is None and pav == '#' + me:
            new = re.sub(r'\spassive="', ' active="#NEEDID" passive="', tag, 1)
            kind = 'add_needid'
        if kind:
            kinds.append(kind)
            log.append([me, os.path.relpath(f, ROOT), kind, st, n, tag, new])
        return new

    t2 = rel_re.sub(fix, t)
    if t2 != t:
        c = {k: kinds.count(k) for k in set(kinds)}
        parts = []
        if c.get('relabel'):
            parts.append(f'subtype="student"（active=本項主）{c["relabel"]}件を subtype="teacher" に変更（向きは不変）')
        if c.get('reverse'):
            parts.append(f'向きが逆に符号化されていた弟子 relation {c["reverse"]}件を、本項主=師（active）・相手=学生（passive）の teacher relation に是正')
        if c.get('add_needid'):
            parts.append(f'active の欠けた relation {c["add_needid"]}件に active="#NEEDID" を補った')
        note = ('師弟 relation の表記統一（規則15改訂: subtype は active が passive の何にあたるかを示す。師弟は常に teacher・active=師）。'
                + '／'.join(parts) + '。')
        resp = ('    <respStmt>\n'
                '        <resp xml:lang="ja">修正（師弟 relation の表記統一・2026-11-16 Waka 依頼）</resp>\n'
                f'        <note xml:lang="ja">{note}</note>\n'
                f'        <persName>{WHO}</persName>\n'
                f'        <date when="{DATE}"/>\n'
                '    </respStmt>\n')
        idx = t2.rfind('</person>')
        assert idx > 0, f
        # keep indentation of </person>
        line_start = t2.rfind('\n', 0, idx) + 1
        t2 = t2[:line_start] + resp + t2[line_start:]
        open(f, 'w', encoding='utf-8').write(t2)
        changed_files += 1

with open(LOG, 'w', encoding='utf-8', newline='') as fh:
    w = csv.writer(fh, delimiter='\t')
    w.writerow(['aind', 'file', 'change', 'old_subtype', 'n', 'old_tag', 'new_tag'])
    w.writerows(log)

from collections import Counter
print('files changed', changed_files)
print(Counter(r[2] for r in log))
