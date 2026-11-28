"""転送の項の後始末（Waka 裁定 2026-11-28、裁定表シート1・3 とも推奨どおり）。
usage: python3 apply_20261128.py REPO rulings_20261128.json

シート1（s1）：XML があり、本文が転送だけの項を REF 方式X にする。
  - person に type="reference" subtype="LIMBO"、ファイル名に REF_
  - 残す：コメント、persName full、sex、note source、note translation、既存の respStmt
  - 外す：それ以外の子要素（name_only・nisbah・relation・state など）
  - note source がなければ corpus から入れる。note reference（target）を足す
  - corpus の記号を $$$、persons_registry を transfer＋転送先
シート3（s3）：XML のない転送の項。corpus の記号を $$$、persons_registry を transfer（転送先は空）。
ほかのレコードから s1 の項を指す参照は、転送先に付け替える（RETARGET）。
"""
import sys, json, glob, re, os, subprocess, collections
import xml.parsers.expat, xml.etree.ElementTree as ET
REPO, RUL = sys.argv[1], sys.argv[2]
D = json.load(open(RUL, encoding='utf-8'))
DATE = '2026-11-28'
CORPUS = f'{REPO}/0__DawForAIND_renumbered_B54_split20260905.txt'
corp = open(CORPUS, encoding='utf-8').read()

def corpus_text(d):
    m = re.search(r'(?m)^###\$AIND-' + d + r' \| \d+\$# \$+ (.*?)(?=^###\$|\Z)', corp, re.S)
    return m.group(1).rstrip('\n')
def mark(d):
    global corp
    pat = re.compile(r'(?m)^(###\$AIND-' + d + r' \| \d+\$# )\$ ')
    assert len(pat.findall(corp)) == 1, d
    corp = pat.sub(lambda m: m.group(1) + '$$$ ', corp)

def chunks(raw):
    """top-level children (elements and comments) with their byte slices"""
    out = []; depth = [0]; cur = [None]
    p = xml.parsers.expat.ParserCreate()
    def start(name, attrs):
        depth[0] += 1
        if depth[0] == 2: cur[0] = (name, attrs, p.CurrentByteIndex)
    def end(name):
        if depth[0] == 2:
            i = p.CurrentByteIndex
            if raw[i:i+2] == b'</': j = raw.index(b'>', i) + 1
            else: j = raw.index(b'/>', cur[0][2]) + 2   # self-closing
            out.append((cur[0][0], cur[0][1], raw[cur[0][2]:j].decode('utf-8')))
        depth[0] -= 1
    def comment(data):
        if depth[0] == 1:
            i = p.CurrentByteIndex; j = raw.index(b'-->', i) + 3
            out.append(('#comment', {}, raw[i:j].decode('utf-8')))
    p.StartElementHandler = start; p.EndElementHandler = end; p.CommentHandler = comment
    p.Parse(raw, True)
    return out

def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
log = []
for d, text, target, thead, memo in D['s1']:
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
    assert len(keep['full']) == 1, d
    if not keep['sex']: keep['sex'] = ['<sex value="M"/>']
    added_src = not keep['source']
    if added_src: keep['source'] = ['<note type="source" xml:lang="ar">' + esc(corpus_text(d)) + '</note>']
    flat = ' '.join(text.split())
    if target == '#NEEDID':
        ref = f'<note type="reference" target="#NEEDID">転送見出し（原文「{esc(flat)}」による）。転送先は未定。{esc(memo)}。</note>'
    else:
        ref = (f'<note type="reference" target="{target}">転送見出し（原文「{esc(flat)}」による）。転送先は {target}「{esc(thead)}」。'
               + (esc(memo) + '。' if memo else '') + '</note>')
    rem = '、'.join(f'{k}×{v}' if v > 1 else k for k, v in sorted(removed.items())) or 'なし'
    rs = ('<respStmt><resp xml:lang="ja">修正・追記</resp><note xml:lang="ja">REF 処理（方式X、Waka 裁定 2026-11-28）: 原文が転送指示だけの項を '
          'type="reference" subtype="LIMBO" にし、ファイル名を REF_ にした。外した要素: ' + rem + '。'
          + ('原文 note を corpus から入れた。' if added_src else '') + f'転送先 {target} を note reference に記した。</note>'
          '<persName>Kumakura</persName><date when="' + DATE + '"/></respStmt>')
    body = keep['comment'] + keep['full'] + keep['sex'] + keep['source'] + keep['tr_ja'] + keep['tr_en'] + \
           [s for k in sorted(keep) if k.startswith('tr_') and k not in ('tr_ja', 'tr_en') for s in keep[k]] + [ref] + keep['resp'] + [rs]
    new = head + '\n' + ''.join('    ' + s + '\n' for s in body) + '</person>' + ('\n' if raw.endswith(b'\n') else '')
    ET.fromstring(new)
    open(fp, 'w', encoding='utf-8').write(new)
    nf = os.path.join(os.path.dirname(fp), 'REF_' + os.path.basename(fp))
    subprocess.run(['git', '-C', REPO, 'mv', os.path.relpath(fp, REPO), os.path.relpath(nf, REPO)], check=True)
    mark(d); log.append((d, target, rem, 'source added' if added_src else ''))
for d, text in D['s3']:
    assert not glob.glob(f'{REPO}/Individuals/*/*AIND-{d}_*.xml'), d
    mark(d)
open(CORPUS, 'w', encoding='utf-8').write(corp)

# ほかのレコードからの参照を転送先へ
RETARGET = {'D01382': ('AIND-D01540', 'AIND-D01549'), 'D02243': ('AIND-D02244', 'AIND-D08147')}
for d, (old, new) in RETARGET.items():
    fp, = glob.glob(f'{REPO}/Individuals/*/*AIND-{d}_*.xml'); t = open(fp, encoding='utf-8').read()
    n = t.count('"#' + old + '"'); assert n >= 1
    t = t.replace('"#' + old + '"', '"#' + new + '"')
    rs = (f'    <respStmt><resp xml:lang="ja">修正・追記</resp><note xml:lang="ja">参照 #{old}（転送見出し。2026-11-28 に REF 化）を、'
          f'転送先の本伝 #{new} に付け替えた（{n}か所、Waka 裁定 2026-11-28 の REF 処理に伴う）。</note><persName>Kumakura</persName><date when="{DATE}"/></respStmt>\n')
    i = t.rindex('</person>'); open(fp, 'w', encoding='utf-8').write(t[:i] + rs + t[i:])

# persons_registry
REG = f'{REPO}/authority/persons_registry.tsv'
L = open(REG, encoding='utf-8').read().split('\n'); hdr = L[0].split('\t')
S, T, Hh = hdr.index('status'), hdr.index('target'), hdr.index('history')
tg = {'AIND-' + r[0]: (r[2][1:] if r[2] != '#NEEDID' else '') for r in D['s1']}
tg.update({'AIND-' + r[0]: '' for r in D['s3']})
n = 0
for i, l in enumerate(L):
    c = l.split('\t')
    if c[0] in tg:
        assert c[S] == 'active' and c[T] == '', l[:80]
        c[S] = 'transfer'; c[T] = tg[c[0]]
        c[Hh] = (c[Hh] + ' ' if c[Hh] else '') + f'{DATE} Waka 裁定（転送の項の後始末）: active → transfer' + (f'、転送先 {tg[c[0]]}' if tg[c[0]] else '')
        L[i] = '\t'.join(c); n += 1
assert n == len(tg), (n, len(tg))
open(REG, 'w', encoding='utf-8').write('\n'.join(L))
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'apply_log_20261128.tsv'), 'w', encoding='utf-8') as f:
    for r in log: f.write('\t'.join(r) + '\n')
print('REF', len(log), 'mark only', len(D['s3']), 'registry', n)
