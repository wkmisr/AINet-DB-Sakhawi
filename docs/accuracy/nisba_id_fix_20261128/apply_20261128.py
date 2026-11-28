"""ニスバ ID 付け違いの修正（Waka 裁定 2026-11-28）を repo に当てる。
usage: python3 apply_20261128.py REPO ops_20261128.tsv
"""
import sys, csv, glob, re, collections
REPO, OPS = sys.argv[1], sys.argv[2]
DATE = '2026-11-28'
PRE = 'ニスバ ID の付け違いの修正（Waka 裁定 2026-11-28）。'
ops = list(csv.DictReader(open(OPS, encoding='utf-8'), delimiter='\t'))
byfile = collections.defaultdict(list)
for o in ops:
    fs = glob.glob(f'{REPO}/Individuals/*/AIND-{o["did"]}_*.xml')
    assert len(fs) == 1, (o, fs)
    byfile[fs[0]].append(o)
log = []
def once(t, old, new, o):
    n = t.count(old)
    assert n == 1, f'{o["did"]} {o["op"]} {o["word"]}: {n} matches of {old!r}'
    return t.replace(old, new)
for fp, os_ in byfile.items():
    t = open(fp, encoding='utf-8').read(); t0 = t; notes = []
    for o in os_:
        w = o['word']
        if o['op'] == 'ref':
            t = once(t, f'<persName type="nisbah" xml:lang="ar" ref="#{o["old"]}">{w}</persName>',
                     f'<persName type="nisbah" xml:lang="ar" ref="#{o["new"]}">{w}</persName>', o)
            notes.append(f'nisbah「{w}」の ref を #{o["old"]} から #{o["new"]} に直した（{o["why"]}）')
        elif o['op'] == 'addref':
            t = once(t, f'<persName type="nisbah" xml:lang="ar">{w}</persName>',
                     f'<persName type="nisbah" xml:lang="ar" ref="#{o["new"]}">{w}</persName>', o)
            notes.append(f'ref のない nisbah「{w}」に #{o["new"]} を付けた')
        elif o['op'] in ('drop', 'drop_full'):
            t = once(t, f'    <persName type="nisbah" xml:lang="ar">{w}</persName>\n', '', o)
            if o['op'] == 'drop_full':
                m = re.search(r'(<persName type="full" xml:lang="ar">[^<]*?) ' + w + '</persName>', t)
                assert m, fp
                t = t.replace(m[0], m[1] + '</persName>')
                notes.append(f'nisbah「{w}」のタグを外し、persName full の末尾に足されていた「{w}」も外した（{o["why"]}）')
            else:
                notes.append(f'nisbah「{w}」のタグを外した（{o["why"]}）')
        elif o['op'] == 'dedup_shuhrah':
            line = f'    <persName type="shuhrah" xml:lang="ar">{w}</persName>\n'
            assert t.count(line) == 2, fp
            i = t.index(line) + len(line); t = t[:i] + t[i:].replace(line, '', 1)
            notes.append(f'shuhrah「{w}」が2つあったので1つを消した')
        elif o['op'] == 'addnisbah':
            m = re.search(r'(    <persName type="name_only" xml:lang="ar">[^<]*</persName>\n)', t)
            assert m and 'type="nisbah"' not in t, fp
            t = t.replace(m[1], m[1] + f'    <persName type="nisbah" xml:lang="ar" ref="#{o["new"]}">{w}</persName>\n', 1)
            notes.append(f'見出しの「السمى」に nisbah「{w}」（#{o["new"]}）を足した（D06145 と同じ語）')
        else:
            raise ValueError(o)
    rs = (f'    <respStmt><resp xml:lang="ja">修正・追記</resp><note xml:lang="ja">{PRE}' + '。'.join(notes) +
          f'。</note><persName>Kumakura</persName><date when="{DATE}"/></respStmt>\n')
    assert t.rstrip().endswith('</person>')
    i = t.rindex('</person>'); t = t[:i] + rs + t[i:]
    open(fp, 'w', encoding='utf-8').write(t)
    log.append((fp.split('/')[-1], len(os_), ' / '.join(notes)))
with open('apply_log_20261128.tsv', 'w', encoding='utf-8') as f:
    for r in log: f.write('\t'.join(map(str, r)) + '\n')
print('files', len(log), 'ops', len(ops))

# --- 典拠表 ---
REG = f'{REPO}/authority/entities_registry.tsv'
lines = open(REG, encoding='utf-8').read().split('\n')
hdr = lines[0].split('\t'); assert lines[-1] == ''
rows = [dict(zip(hdr, l.split('\t'))) for l in lines[1:-1]]
R = {r['id']: r for r in rows}
def note(i, s):
    r = R['TMP-N-' + i]; r['note'] = (r['note'] + ' ' if r['note'] else '') + f'【{DATE}】' + s
def merge(i, tgt, why):
    r = R['TMP-N-' + i]; assert r['status'] == 'active', i
    r['status'] = 'merged'; r['target'] = 'TMP-N-' + tgt; note(i, why + f'TMP-N-{tgt} に統合（Waka 裁定）。番号は再利用しない')
for i, tgt, lab in [('01222', '00122', 'تساوي'), ('02644', '00264', 'ارشادي'), ('01666', '00166', 'ولكني'), ('03211', '00321', 'فتقضي'), ('02965', '00265', 'المشتكي'), ('01667', '03167', 'وقوي')]:
    w = R['TMP-N-' + tgt]['label_ar']
    merge(i, tgt, f'表記「{lab}」は名前でない（誤り）。唯一の用例は「{w}」で、')
r = R['TMP-N-05468']; assert r['status'] == 'active'
r['status'] = 'retired'; note('05468', 'ニスバではない（語末が ي・ية でない）。唯一の参照 D01253 は本文が「السفطي」で TMP-N-00193 に付け替えた（Waka 裁定）。以後使用しない')
for i, tgt in [('00024', '00019'), ('05498', '00206'), ('05494', '00231'), ('05495', '00245'), ('00579', '05476'), ('03089', '05483')]:
    a, b = R['TMP-N-' + i], R['TMP-N-' + tgt]
    if a['label_latn'] and not b['label_latn']: b['label_latn'] = a['label_latn']
    merge(i, tgt, '典拠表の重複（同じ表記）。')
import json
new = json.load(open('new.json'))
ids = [int(x['id'][6:]) for x in rows if x['id'].startswith('TMP-N-')]
assert max(ids) == 5530, max(ids)
for k, (d, w, o, lab) in enumerate(new):
    nid = f'TMP-N-{5531 + k:05d}'; assert nid not in R
    row = {h: '' for h in hdr}
    row.update(id=nid, category='Nisbah', status='active', label_ar=lab,
               note=f'Occurs: {d} («{w}»). Issued {DATE} (nisbah ID mismatch fix; previously mis-pointed to TMP-N-{o}).')
    pos = next(j for j, x in enumerate(rows) if x['id'] == (nid[:6] + f'{5530 + k:05d}'))
    rows.insert(pos + 1, row); R[nid] = row
out = '\t'.join(hdr) + '\n' + ''.join('\t'.join(r[h] for h in hdr) + '\n' for r in rows)
open(REG, 'w', encoding='utf-8').write(out)
print('registry rows', len(rows))
