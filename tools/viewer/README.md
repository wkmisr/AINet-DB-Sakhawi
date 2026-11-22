# Ḍawʾ mARkdown Viewer — data build (trial)

Trial tools for moving AIND from TEI-XML to **aind-yaml 0.1 + mARkdown** (see `docs/schema/aind-yaml-0.1.md`).
The TEI in `Individuals/` stays the master until the migration is decided; everything here is regenerated from it.

## Steps
Run in a work directory (`AIND_WORK`, default: current directory). `idmaster.tsv` = ID-Master exported as TSV.

1. `python3 tools/viewer/make_records.py <repo> $AIND_WORK` → `records_tei.json` (lossless dicts of the TEI)
2. `AIND_WORK=... python3 tools/viewer/build_data.py` → `dau.json` (tagged mARkdown text per heading), `tr.json`, `labels.json`, `idm.json`, `offices.json`
   - rule-based tagging (years, months, name elements, madhhab, relations, offices, event triggers, بضع ranges = 1–9)
   - `manual_placements.json`: relation placements decided by hand
   - deterministic: the script re-runs itself with `PYTHONHASHSEED=0`
3. `AIND_WORK=... python3 tools/viewer/to_v01.py <out_dir>` → `<out_dir>/meta/*.yml` + `<out_dir>/text/*.md` (= `data_v01/`)
4. `python3 tools/viewer/make_viewer_records.py <out_dir> records.json` → the viewer's YAML data

The viewer (`index.html`) is published as a claude.ai artifact together with `dau.json`, `tr.json`, `labels.json`, `idm.json`, `offices.json`, `records.json`, `js-yaml.min.js`.
Checks made in the viewer (CHECKED, moved tags, merges, "not in text", re-classification) are kept in the artifact's shared database, not in this repo.

`tools/convert/`: `tei2yaml.py` (TEI ⇄ YAML, lossless), `tei2markdown.py` (TEI → OpenITI mARkdown, first trial).
