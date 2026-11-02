# docs/

Working documentation of the review pipeline. Most files are written in Japanese (the working language of the editors); file and folder names are in English.

| Folder | Contents |
|---|---|
| `handover/` | Hand-over notes between work sessions (`HANDOVER_YYYYMMDD_v13_NN.md`). The latest one describes the current state, the unified encoding rules and the next steps. |
| `batches/<batch>/` | Everything about one review batch (e.g. `B144-148/`): the chunk brief (`CHUNK_BRIEF_*`), reviewers' notes (`REVIEW_NOTES_*`, `ISSUES_*`, `FIXLOG_*`), verification reports (`VERIFY_*`, `FINDINGS_*`), prechecks, the aggregation report, new provisional IDs (`TMP_register_*`, `TMP_NEW_*`), `decisions.md` (questions put to the editor), `rulings_applied_*` (how the rulings were applied), `idmaster_actions.md` (changes to the ID-Master sheet), and `commit_message.txt`. |
| `accuracy/` | Accuracy log of the AI pipeline (`model_accuracy_log.tsv`, `model_accuracy_findings.tsv`) and the metric definitions. |
| `authority/` | Local ledger of the Wikidata / GeoNames IDs used in the project, with lookup and update scripts. |
| `tools/` | Check scripts (`precheck_aind_v12.py` etc.). |
| `browser/` | Build scripts of the AINet Browser (internal viewer, under construction). |
| `lod_prototype/` | TEI-to-RDF conversion prototype. |
| `archive/` | One-off work records (audits, ID merges, symbol mapping, corpus split) and superseded files. |

## Renaming of 2026-11-02

The documentation was reorganized and file names were changed from Japanese to English on 2026-11-02. The full old → new mapping is in [`archive/rename_map_20261102.tsv`](archive/rename_map_20261102.tsv). Paths written inside older documents refer to the old layout (e.g. `docs/records/records_B144-148/` is now `docs/batches/B144-148/`; `docs/要判断/要判断_B144-148.md` is now `docs/batches/B144-148/decisions.md`).
