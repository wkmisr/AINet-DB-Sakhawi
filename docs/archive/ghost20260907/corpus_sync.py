# corpus同期チェック（2026-09-07）: Individuals の (AIND, 12桁) と corpus txt ヘッダの同期
# usage: python3 corpus_sync.py <corpus.txt> <Individuals dir> [--apply]
#   --apply: XMLに存在する 12桁 のうち txt ヘッダに AIND が無い行へ「AIND-Dxxxxx | 」を補う（本文は変更しない）
import re, glob, os, sys, json
F, D = sys.argv[1], sys.argv[2]; APPLY = '--apply' in sys.argv
lines = open(F, encoding='utf-8').read().split('\n')
xml = {}
for f in glob.glob(os.path.join(D, '*.xml')):
    m = re.search(r'(AIND-D\d+[a-z]?)_(\d{12})', os.path.basename(f)); xml[m.group(2)] = (m.group(1), os.path.basename(f))
withid, noid, bad = {}, {}, []
for i, l in enumerate(lines):
    if not l.startswith('###$'): continue
    m = re.match(r'###\$(AIND-D\d+[a-z]?)\s*\|\s*(\d{12})\$#', l)
    if m: withid[m.group(2)] = (m.group(1), i); continue
    m2 = re.match(r'###\$(\d{12})\$#', l)
    if m2: noid[m2.group(1)] = i; continue
    bad.append((i + 1, l[:90]))
rep = {'txt_headers_with_aind': len(withid), 'txt_headers_without_aind': len(noid), 'malformed': bad, 'xml': len(xml),
       'ok': 0, 'aind_mismatch': [], 'xml_only': [], 'fixable': []}
for src, (a, fn) in sorted(xml.items(), key=lambda x: x[1][0]):
    if src in withid:
        if withid[src][0] == a: rep['ok'] += 1
        else: rep['aind_mismatch'].append((fn, withid[src][0], withid[src][1] + 1))
    elif src in noid:
        rep['fixable'].append((fn, a, src, noid[src] + 1))
    else:
        rep['xml_only'].append((fn, a, src))
rep['txt_only_without_aind'] = len(noid) - len(rep['fixable'])
print(json.dumps({k: (v if not isinstance(v, list) else len(v)) for k, v in rep.items()}, ensure_ascii=False))
for k in ('malformed', 'aind_mismatch', 'xml_only', 'fixable'):
    print('--', k); [print('  ', x) for x in rep[k]]
# 元テキスト（02_Daw_checked）から落ちた 2 項の復元（本文は原文どおり、ms#### 記号は除去）
RESTORE = [
 ('590436370061', 'AIND-D00782', '870594905740', '$', ['أحمد بن صبح أحد الظلمة بدمشق . مات بقلعتها في', 'سنة ثلاث وتسعين .']),
 ('822322662826', 'AIND-D01628', '243479350695', '$$$', ['أحمد بن محمد الشكيلي المدني . فيمن جده إبراهيم .']),
]
if APPLY:
    n = 0
    for fn, a, src, ln in rep['fixable']:          # 1) ヘッダに AIND を補う（行番号は不変）
        i = ln - 1; assert lines[i].startswith('###$%s$#' % src)
        lines[i] = lines[i].replace('###$%s$#' % src, '###$%s | %s$#' % (a, src), 1); n += 1
    for src, a, after, dol, body in RESTORE:       # 2) 欠落項を直前項の末尾に挿入
        if any(l.startswith('###$%s | %s$#' % (a, src)) for l in lines): continue
        idx = next(i for i, l in enumerate(lines) if l.startswith('###$') and after + '$#' in l)
        j = idx + 1
        while j < len(lines) and not lines[j].startswith('###$'): j += 1
        while lines[j-1].strip() == '': j -= 1
        lines[j:j] = ['', '###$%s | %s$# %s %s' % (a, src, dol, body[0])] + body[1:]; print('restored', a, 'at line', j + 2)
    open(F, 'w', encoding='utf-8').write('\n'.join(lines)); print('applied', n)
