# corpus txt -> corpus_index.json  (AIND -> {src, dollars, text, line})
# usage: python3 make_corpus_index.py <corpus.txt> [corpus_index.json]
import re, json, sys
src = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else 'corpus_index.json'
H = re.compile(r'^###\$(?:(AIND-D\w+) \| )?(\d{12,13})\$# (\${1,3}) ?(.*)$')
idx = {}; cur = None
for ln, line in enumerate(open(src, encoding='utf-8'), 1):
    line = line.rstrip('\n')
    m = H.match(line)
    if m:
        aid, num, dol, first = m.groups()
        cur = None
        if aid:
            cur = {'src': num, 'dollars': dol, 'text': first.strip(), 'line': ln}
            idx[aid] = cur
    elif cur is not None:
        if line.startswith('###'): cur = None
        elif line.strip(): cur['text'] += '\n' + line.strip()
json.dump(idx, open(out, 'w', encoding='utf-8'), ensure_ascii=False)
print(len(idx), 'entries ->', out)
