# Headings and IDs for the 84 `★ID_Missing★` entries (2026-11-23)

The corpus still held 84 entries that began with the placeholder `★ID_Missing★`
instead of a heading line, so they had neither an AIND ID nor a 12-digit source ID
(reported as out of scope in `docs/archive/split20260905/`). Ruling by Kumakura,
2026-11-23: these entries need IDs, and the assignment is done automatically.

## What changed
- Each `★ID_Missing★ <text>` became `###$<AIND> | <12 digits>$# $ <text>`.
- AIND ID: ID of the record that contained the entry + next free suffix (a, b, …),
  the same rule as `split20260905`.
- 12-digit source ID: random (seed 20261123), unique within the corpus.
- 80 entries stood at the start of a line. 4 stood inside a line (2 of them inside a
  heading line); those lines were split at the mark.
- The body text is unchanged: the script asserts that the text before and after is
  identical once the mark, the new heading prefixes and whitespace are removed.
- Headings: 15,294 → 15,378. `★` in the corpus: 339 → 171. No duplicate AIND or 12-digit IDs.

## Not decided here
- All new headings carry `$`. Whether an entry is a cross-reference (`$$$`) is left to the
  normal review, as for the neighbouring entries of the index band (D11000–D12999, 79 of the 84).
- The other marks (`★name★`, `±±±`, `★word?★`, editorial notes) are untouched.
- PersonList (Google Sheet) needs 84 new rows: see `id_missing_assigned_20261123.tsv`.
- `corpus_index.json` and other derived files must be rebuilt from the new corpus.

## Files
- `assign_id_missing.py` — the script (`python3 assign_id_missing.py <in> <out> <log.tsv>`)
- `id_missing_assigned_20261123.tsv` — new AIND, 12-digit ID, source record, position, start of heading
