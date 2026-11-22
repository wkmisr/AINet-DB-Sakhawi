"""Step 4: v01/meta/*.yml -> records.json (what the viewer's YAML panel and event list read).
usage: python3 make_viewer_records.py <v01_dir> <out_json>"""
import sys, glob, json, yaml
out = {}
for f in glob.glob(sys.argv[1] + '/meta/*.yml'):
    d = yaml.safe_load(open(f, encoding='utf-8')); out[d['id']] = d
json.dump(out, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(len(out), 'records')
