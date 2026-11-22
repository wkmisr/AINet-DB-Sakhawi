"""Step 1: TEI (Individuals/**/*.xml) -> records_tei.json (lossless dicts, one per person; see convert/tei2yaml.py).
usage: python3 make_records.py <repo_root> <work_dir>"""
import sys, os, glob, json
from lxml import etree
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'convert'))
from tei2yaml import person2d
repo, work = sys.argv[1], sys.argv[2]
out = {}
for f in sorted(glob.glob(repo + '/Individuals/**/*.xml', recursive=True)):
    d = person2d(etree.parse(f).getroot())
    d.pop('source_text', None)                      # the text lives in the corpus / text/*.md
    if 'source_id' in d: d['source_id'] = str(d['source_id'])
    out[d['id']] = d
json.dump(out, open(os.path.join(work, 'records_tei.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(len(out), 'records')
