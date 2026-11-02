import re, sys, os, glob, json, html
REPO = os.path.expanduser('~/mnt/AINet-DB-Sakhawi')
CORPUS = os.path.join(REPO, '0__DawForAIND_renumbered_B54_split20260905.txt')
APPLY = '--apply' in sys.argv

# ---- build index from corpus
lines = open(CORPUS, encoding='utf-8').read().split('\n')
hdr = re.compile(r'^###\$(?:(AIND-D\d+[a-z]?) \| )?(\d+)\$# (\$+)\s*(.*)$')
idx = {}; bysrc = {}; cur = None; buf = []
def flush():
    global cur, buf
    if cur is not None:
        rec = {'src': cur['src'], 'dollars': cur['dollars'], 'raw': '\n'.join(buf)}
        if cur['id']: idx[cur['id']] = rec
        else: bysrc[cur['src']] = rec
    cur = None; buf = []
for l in lines:
    m = hdr.match(l)
    if m:
        flush(); cur = {'id': m.group(1), 'src': m.group(2), 'dollars': m.group(3)}; buf = [m.group(4)]
    elif cur is not None:
        if l.startswith('#') and not l.startswith('###$'):
            continue
        buf.append(l)
flush()

stats = {'files': 0, 'inserted': 0, 'skipped_has_source': 0, 'missing_in_corpus': [], 'src_mismatch': [],
         'anchor_translation': 0, 'anchor_reference': 0, 'anchor_respStmt': 0, 'no_anchor': [],
         'stripped_serial': 0, 'dropped_bar_lines': 0, 'multi_heading_in_body': []}

def clean(raw):
    t = raw.strip('\n')
    # drop chapter/letter marker lines ("| حرف ...") and trailing blanks
    out = []
    for l in t.split('\n'):
        if l.lstrip().startswith('|'):
            stats['dropped_bar_lines'] += 1; continue
        out.append(l.rstrip())
    t = '\n'.join(out).strip('\n')
    t = re.sub(r'\n{3,}', '\n\n', t)
    m = re.match(r'^\d+\s+', t)
    if m:
        t = t[m.end():]; stats['stripped_serial'] += 1
    return t

files = sorted(glob.glob(os.path.join(REPO, 'Individuals', '*.xml')))
for f in files:
    s = open(f, encoding='utf-8').read()
    stats['files'] += 1
    if '<note type="source"' in s:
        stats['skipped_has_source'] += 1; continue
    m = re.search(r'<person\b[^>]*\bxml:id="([^"]+)"[^>]*\bsource="([^"]+)"', s)
    pid, src = m.group(1), m.group(2)
    e = idx.get(pid)
    if e is None and src in bysrc:
        e = bysrc[src]; stats['matched_by_src'] = stats.get('matched_by_src', 0) + 1
    if e is None:
        stats['missing_in_corpus'].append(os.path.basename(f)); continue
    if e['src'] != src:
        stats['src_mismatch'].append((os.path.basename(f), src, e['src']))
    text = clean(e['raw'])
    if re.search(r'\n\d+ ', text):
        stats['multi_heading_in_body'].append(pid)
    esc = html.escape(text, quote=False)
    # anchor
    am = re.search(r'^([ \t]*)<note type="translation"', s, re.M)
    if am: stats['anchor_translation'] += 1
    else:
        am = re.search(r'^([ \t]*)<note type="reference"', s, re.M)
        if am: stats['anchor_reference'] += 1
        else:
            am = re.search(r'^([ \t]*)<respStmt>', s, re.M)
            if am: stats['anchor_respStmt'] += 1
            else:
                stats['no_anchor'].append(os.path.basename(f)); continue
    ind = am.group(1)
    ins = f'{ind}<note type="source" xml:lang="ar">{esc}</note>\n'
    new = s[:am.start()] + ins + s[am.start():]
    if APPLY:
        open(f, 'w', encoding='utf-8', newline='').write(new)
    stats['inserted'] += 1
print(json.dumps({k: (v if not isinstance(v, list) else (len(v), v[:20])) for k, v in stats.items()}, ensure_ascii=False, indent=1))
