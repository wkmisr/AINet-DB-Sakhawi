# audit_20261127 — what the TEI-to-YAML conversion dropped, and the cross-reference worklist

- `tei_vs_yaml_losses.tsv`: first audit (2026-11-27) of TEI values the conversion did not carry. Fixed in `tools/viewer/to_v01.py`; the check is now `tools/viewer/audit_tei_vs_yaml.py`, run at the end of every conversion.
- `crossref_marked_as_biography.tsv`: headings marked `$` (biography) whose text is a cross-reference (180 without content, 60 with content).
- `crossref_worklist.tsv`: the worklist for sorting out cross-references (転送の整理), one row per heading or report:
  - `A_marked_as_biography` (240): the rows of `crossref_marked_as_biography.tsv`.
  - `B_unnumbered_crossref_heading` (1,325): `$$$` headings in the corpus with no AIND number. `anchor` = the numbered heading before it, `corpus_line` = line in `0__DawForAIND_renumbered_B54_split20260905.txt` (main 99300d1), `reported` = the part-timers' report on Discord (#アルバイト・相談) that names this anchor, if any.
  - `C_report_not_matching_corpus` (27): reports whose count differs from the corpus (already given a suffix id such as D00744a; a heading buried in the previous text as `★name★`; or nothing in the corpus at all, possibly missing from the corpus — to check against the printed edition).
- `discord_unregistered_reports.tsv`: the 45 Discord reports of 「未登録の伝記」 (2026-06-10 to 11-22), one row per anchor and report: 434 anchors, 548 persons. 407 anchors match the unnumbered `$$$` headings in the corpus exactly.

## Candidate targets (2026-11-27)

`resolve_targets.py` reads the pointer in each cross-reference heading («في ابن …», «فيمن جده …», «فيمن اسم أبيه …», «هو ابن …», «صوابه …», «قريبا», an explicit «[= AIND-D…]») and searches the numbered headings for the name it points to, then the nisbas and titles of the heading. `crossref_worklist.tsv` now has `tier` and `candidates` (up to 5, with score and what matched).

- Tested on the 363 REF records whose target is known (note `target`): a single best candidate is right in 226 of 249 cases (91%); tied candidates include the right one in 23 more; 61 get no candidate.
- Worklist: A (240) unique 116, tied 62, none 62. B (1,325) explicit 1, unique 540, tied 337, none 447.
- These are candidates, not decisions: every target is to be confirmed in the text (unique ones can be checked quickly, tied and none need reading).
