"""office_label_map.tsv（官職ラベル → ID の対応表）を作り直す（2026-11-17）。
機械学習チーム向け。官職は「ID＋場所・施設＋deputy」の組で照合する前提。
分類は idmaster_office_actions.tsv（2026-11-16）＋その後の新規 ID。"""
import glob, re, os, csv, sys, collections
ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
D = os.path.join(ROOT, 'docs/accuracy/office_audit_20261116')
CLS = {r['ID'].replace('wd:', ''): r['分類（新設列）'] for r in csv.DictReader(open(os.path.join(D, 'idmaster_office_actions.tsv'), encoding='utf-8'), delimiter='\t')}
CLS.update({'Q3020184': '司法', 'TMP-O-00408': '宗教・学術職', 'TMP-O-00409': '学識・宗教的身分'})
def norm(s):
    s = re.sub('[ً-ْـ]', '', s or '')
    s = s.translate(str.maketrans({'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ٱ': 'ا', 'ى': 'ي', 'ة': 'ه', 'ؤ': 'و', 'ئ': 'ي'}))
    return re.sub(r'\s+', ' ', s).strip()
cnt = collections.Counter(); dep = collections.Counter(); qual = collections.Counter(); ids_by_label = collections.defaultdict(set)
for p in glob.glob(os.path.join(ROOT, 'Individuals/*/AIND-D*.xml')):
    t = open(p, encoding='utf-8').read()
    for m in re.finditer(r'<state\b([^>]*)>(.*?)</state>', t, re.S):
        if 'type="office"' not in m.group(1): continue
        r = re.search(r'ref="#?([^"]*)"', m.group(1)); ref = r.group(1) if r else ''
        if not ref or 'NEEDID' in ref: continue
        ref = ref.replace('wd:', '')
        lab = norm((re.findall(r'<label xml:lang="ar">([^<]*)</label>', m.group(2)) or [''])[0])
        if not lab: continue
        k = (lab, ref); cnt[k] += 1; ids_by_label[lab].add(ref)
        if 'subtype="deputy"' in m.group(1): dep[k] += 1
        if re.search(r'<(placeName|orgName)\b', m.group(2)): qual[k] += 1
with open(os.path.join(D, 'office_label_map.tsv'), 'w', encoding='utf-8', newline='') as fh:
    w = csv.writer(fh, delimiter='\t')
    w.writerow(['label_normalized', 'id', 'category', 'count', 'with_place_or_inst', 'deputy', 'ambiguous'])
    for (lab, ref), n in sorted(cnt.items()):
        w.writerow([lab, ('wd:' + ref) if ref.startswith('Q') else ref, CLS.get(ref, ''), n, qual[(lab, ref)], dep[(lab, ref)], 'yes' if len(ids_by_label[lab]) > 1 else ''])
print(len(cnt), 'pairs;', sum(1 for l in ids_by_label if len(ids_by_label[l]) > 1), 'ambiguous labels;', sum(1 for (l, r) in cnt if not CLS.get(r)), 'without category')
print([r for (l, r) in cnt if not CLS.get(r)])
