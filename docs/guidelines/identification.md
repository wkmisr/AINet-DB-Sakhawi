# AIND identification guideline

Version 0.1 (2026-11-29, draft for the ten-biography trial). Stage 2 of the pipeline (design v5, sec. 4).

This file is the canonical statement of how a person mentioned in a biography of al-Sakhāwī's
*al-Ḍawʾ al-lāmiʿ* is identified. The prompts in `tools/identify/prompts/` are excerpts of it; when
they disagree, this file is right and the prompt is to be corrected. Rulings by the principal
investigator (WK) are the source of the rules; appendix A maps the sections to the numbered rules
of the review briefs used until November 2026.

Identification is done by a model that reads the context and searches for itself. People rule on
what the models leave open. The guideline is written for both.

---

## 1. The task

**Unit.** One *mention*: a stretch of text in one biography that refers to a person other than the
subject of that biography. Mentions come from stage 1 (extraction) with a number (`m1`, `m2`, …),
the words as printed, the relation or event they take part in, and whether they stand in the
narrator's own text or inside a quotation.

**Question.** Which person is this, in terms of the project's registry of persons
(`authority/persons_registry.tsv`)?

**Answer.** One of six verdicts (sec. 4), with the evidence that a third party needs to check it.

Identification does not change the extraction. It does not create registry IDs, merge IDs, or
correct the text. Where it sees that one of these is needed, it says so in the answer and a person
decides.

## 2. Principles

In order of precedence.

1. **Read the text as printed.** A word that looks like a misprint is still read as it stands.
   Spelling and dotting variants are used to *search*; they are not grounds to read a different
   name into the text. A discrepancy between the mention and the entry it is linked to is recorded
   in the answer, not removed.
2. **Link only when it is certain.** Linking a mention to the wrong person is the worst error;
   leaving it open is not an error. `undetermined` and `not_found` are correct answers whenever
   the evidence stops short. A resemblance of names, a plausible date, or the fame of a candidate
   does not make an identification.
3. **The evidence is in the other entry's text.** A candidate is accepted only after its entry has
   been read, and on points that the entry itself states. A heading that looks right is a reason
   to read the entry, nothing more. This holds for IDs suggested by the pre-search, by the
   conventions file, and by any earlier record.
4. **No hits is not absence.** A person is reported as having no entry only after the searches of
   sec. 6 have been made. Most past errors of this project were entries that existed and were not
   found.
5. **IDs come from the tools.** An ID is never written from memory. Every ID in an answer was
   returned by a tool in the same run or stands in `conventions.md`. No Wikidata or GeoNames
   number is ever produced by the model.
6. **Show the work.** Each answer names the passage that decided it and the strong candidates
   that were set aside, with the reason.

## 3. The source and its entries

### 3.1 Order of the book

The corpus follows the order of the print. An entry's position matters because al-Sakhāwī points
backwards and forwards (sec. 7.3). The ranges below are approximate; go by the headings.

| Part | Entries (about) | Heading begins with |
|---|---|---|
| Men by name, alphabetical (ism, then father's name, then grandfather's) | AIND-D00001 – D10605 | the ism |
| Men by kunya | D10606 – D11135 | «أبو …» |
| Laqabs and by-names | D11136 – about D11390 | a laqab or by-name («أسد الدين», «الأشقر», «صاحب كنباية») |
| Nisbas | about D11400 – D12130 | a nisba («الآثاري جماعة …») |
| «ابن X» names, then unnamed men | D12131 – D12843 | «ابن …»; «رجل …» |
| Women by name | D12844 – D13664 | the ism |
| Women by kunya | D13665 – D13851 | «أم …» |
| Unnamed women | D13852 – D13922 | «ابنة …», «والدة …», «مستولدة …» |

The parts from the laqabs to the «ابن X» names are largely an index to the first two: an entry
there usually gives a by-name and the full name of one or several persons whose biographies stand
under their names.

### 3.2 Kinds of entry

| Kind | What it is | Use as the answer? |
|---|---|---|
| Biography | The person's own entry, however short (a bare name is still an entry) | Yes |
| Transfer heading | A heading that only sends the reader elsewhere («مضى في …», «يأتي في الكنى», «هو X»). Registry status `transfer`, with `target` | No. Follow it to the target and answer with the target |
| Index entry for one person | A by-name with one full name («الوسيمي … محمد بن أحمد بن أبي بكر … الكاتب») | Only if that person has no biography elsewhere (search for one under the full name). If there is one, answer with the biography. Either way set the flag `index_entry` |
| Index entry for several persons | «ابن عزم … عمر بن محمد بن أحمد وابنه محمد وابنه محمد»; «X اثنان : …»; «الفلاني جماعة منهم …» | Never. Use it to learn who bears the name, then find each person's biography |
| Double entry | Two biographies that appear to be of one person, neither pointing to the other | Answer with the entry whose text matches the mention; name the other in `other_entries` |

A transfer heading whose target is not recorded, or seems wrong, is reported with the flag
`transfer_unresolved`; do not guess the target. The registry marks transfer headings in the parts
by name and by kunya. In the index parts (laqabs, nisbas, «ابن X») it does not yet tell an index
entry from a biography: read the entry.

### 3.3 IDs

- `AIND-D` + five digits, sometimes a letter (`AIND-D00544a`): a heading of the book. The only kind
  of ID an `identified` verdict may carry.
- `TMP-P-` + six digits: a person who has no entry in the book but was met in earlier work.
- `wd:Q…`: a person entered in the registry under a Wikidata number.
- Registry status: `active`; `transfer` (see above); `merged` and `retired` (not to be used; a
  merged row names its successor in `target`).

**A person who has a biography is always answered with the AIND number of that biography**, also
when the registry holds a Wikidata row for the same person. This includes Ibn Ḥajar and
al-Sakhāwī himself, both of whom have entries.

## 4. Verdicts

| Verdict | Meaning | Must be given |
|---|---|---|
| `identified` | The person has a biography in the book, and it is this one | `id` (AIND), `certainty`, `basis`, `evidence` |
| `same_as_mention` | The same person as an earlier mention in this biography | `same_as` (the earlier mention's number). The earliest mention of the person carries the real verdict |
| `undetermined` | There are candidates, and the text does not decide between them, or does not confirm the only one | `candidates` (at most five), each with what speaks for and against |
| `not_found` | A person of the book's period who could have an entry; searched as required; none is theirs | `checks`; `registry_id` if the person is already in the registry |
| `out_of_scope` | A person for whom no entry is to be expected | `ground`; `registry_id` if in the registry |
| `extraction_error` | The mention is not a usable mention of another person | `ground` |

### 4.1 `identified`

The standard of evidence is in sec. 5. `certainty` is `high` or `medium`; `low` only where a
convention in `conventions.md` prescribes it. If neither `high` nor `medium` is justified, the
verdict is `undetermined`, not `identified` with a low certainty.

### 4.2 `same_as_mention`

Use it for a second reference to someone already mentioned in the same biography: a repeated name,
a shorter form («الشمس» after «الشمس الفلاني»), «المذكور», a kin term that the context ties to a
named person. Do not use it across a quotation boundary unless the two speakers plainly mean the
same person. If it is not clear that two mentions are one person, treat them separately.

### 4.3 `undetermined`

Typical cases: a by-name shared by a father and a son or by several members of one family; a bare
laqab and nisba that two contemporaries bear; a name that fits one entry, where the entry confirms
only one point. State what would decide («the year of the ijāza», «whether he was in Mecca»).

### 4.4 `not_found`

The person belongs to the period of the book (died in 801 AH or later, or was alive in the ninth
century), so an entry would be normal, and the required searches found none.

If the registry already has this person as `TMP-P` or `wd:`, give that ID in `registry_id`. The
standard is the same as for an identification: the registry row must fit this mention on its own
evidence (name as used at this place, period, context), not merely carry a similar label. Many
`TMP-P` rows are bare common names registered for one relation; a row whose note warns against
reuse is not to be reused.

If the person is not in the registry and the text gives something to know them by (a laqab, a
kunya, an office, an uncommon name, a father's and grandfather's name), set `propose_registry` to
true. A bare common name («علي», «محمد») or an unnamed person gets `propose_registry: false`.

### 4.5 `out_of_scope`

No entry is to be expected for: prophets and figures of sacred history; Companions and Successors;
the founders of the schools and the authors of the classical books, when they appear as authors or
as links in a chain of transmission; any person whose death in or before 800 AH is stated in the
text or is beyond doubt. `ground` is one of `list` (the person is on the out-of-scope list),
`death_before_801` (give the year and where it comes from), `early_figure`, `author_of_classic`.

Only `list` may be given without searching. For the others the name and registry searches are
still made, because a man taken for an early figure has more than once turned out to have an entry.
A teacher of someone born in the 770s may have died before or after 800: without a date, that is
`not_found`, with a note, and not `out_of_scope`.

A person who died in or before 800 is a candidate for Ibn Ḥajar's *al-Durar al-kāmina*. Set the
flag `durar_candidate` when the death falls in 701–800.

### 4.6 `extraction_error`

`ground` is one of: `not_a_person` (a place, a book, an institution, God); `group` (a family, a
tribe, «جماعة», «أهل مكة»); `subject` (the mention is the subject of the biography); `span` (the
words cover two persons, or cut a name in half; say what the span should be). The mention goes
back to stage 1.

## 5. Evidence

### 5.1 What counts

A *point* is a fact about the person that the mention's context and the candidate's entry both
state. The points:

| Point (`basis`) | Example |
|---|---|
| `pointer` | The author's own reference, «الماضي», «الآتي», «الذي قبله», with a name that fits the entry it points to |
| `nasab` | Ism with father's name, better with grandfather's |
| `laqab`, `kunya`, `nisba`, `shuhra` | «الشمس»; «أبو الفضل»; «البطيني»; «ويعرف بابن القطان» |
| `office` | An office or trade, with its place: «قاضي حلب», «شيخ الشيوخ بحلب» |
| `place` | Where the person lived or taught, as stated on both sides |
| `madhhab` | The school of law, as stated on both sides |
| `date` | A dated event that fits both: the year of an ijāza, a death |
| `kin` | A family tie stated on both sides, or a heading that names the subject («والد X», «أخو Y») |
| `teacher_student` | The candidate's entry lists the subject among teachers or students, or the reverse |
| `work` | A book that both sides connect with the person |
| `mutual` | The candidate's entry mentions the subject of this biography |
| `fixed_epithet` | A way of naming that al-Sakhāwī keeps for one person (sec. 5.4) |
| `convention` | A ruling recorded in `conventions.md` |

Two forms of one name are one point, not two: «الشمس» in the mention and «شمس الدين» in the entry
confirm the laqab once.

The school of law and the nisba of a great city («القاهري», «المكي», «الدمشقي») are weak points,
since thousands share them. They support an identification and can exclude one; one of them
together with a single name does not make the two points of sec. 5.2.

### 5.2 `high`

Either of:

- **A pointer with a fitting name.** «أخو الذي قبله» in the heading of AIND-D06501, read with the
  entry before it. «الماضي أبوه» with a father whose entry stands earlier under the name that the
  subject's nasab gives. The name must fit; the pointer alone does not choose among several.
- **Two or more independent points, confirmed in the text of the candidate's entry, and nothing
  against** that is not explained. For someone named only by laqab and nisba, the two parts of the
  name are not enough if another person of the period bears both; a third point is needed.

For a father or a forefather, the subject's own heading can supply the points: the nasab minus its
first name, and the chain of laqabs («الشمس بن البرهان» for a father whose laqab is البرهان). If one
entry fits both, and no second entry does, that is `high`. For a brother, a sister or a child, a
shared nasab is not enough, since cousins and namesakes share it too: the other entry must name
the subject, or the author must point («أخو الذي قبله», «الماضي أخوه»).

### 5.3 `medium`

- The author himself hedges: «أظنه», «وكأنه», «فيما أحسب».
- Two points agree, and one small discrepancy remains unexplained: one link of the nasab missing
  or different, a dotting variant in a rare name. Record the discrepancy in `note`.
- A fixed epithet (sec. 5.4).
- A convention prescribes it.

### 5.4 Fixed epithets

Al-Sakhāwī uses some designations for one person throughout («الفقيه السعودي» for AIND-D06787,
whose entry has «ويعرف بالسعودي»). Such a link is `medium`, and only if (a) the designation is
found in several entries, each time fitting the same person, and (b) no relative or contemporary
of that person bears the same designation. Where a father and a son, or a grandfather and a
grandson, are both called by it, the verdict is `undetermined` with both as candidates.

### 5.5 What does not count

- The mention's name is contained in the candidate's heading. This is what the search returns; it
  is where the work starts.
- The candidate is the best known bearer of the name.
- The registry's label for an ID. Judge by how the text names the person at this place: «ابن
  المنير» and a bare «المنير» are different designations, because «ابن» is not normally dropped.
- Outside knowledge that the entry does not state. It may guide the search; it is not evidence.
- An ID used for the same words in another record. The context there may have been different.
- Position in the book, or likeness of meaning, on their own.

### 5.6 Chronology is always checked

Before linking, compare the dates of the two entries.

- A teacher must be alive, and the student of an age to learn, at the time of the teaching.
  Hearing ḥadīth («سمع», «أحضر») may happen in infancy. An ijāza may be given to an infant or
  obtained by a third party's request, so it only requires that the grantor be alive.
- Al-Sakhāwī was born in 831. Someone «ممن سمع مني», or whom he met, was alive after about 845.
  (AIND-D06591, «الكردي ثم المكي . ممن سمع مني بمكة», is therefore not the Kurdī of AIND-D06513,
  born 747.)
- Laqab and nisba shared by an eighth-century man and his ninth-century namesake are frequent in
  the great families. Check the generation.

A conflict of dates defeats an identification unless the text explains it.

### 5.7 Discrepancies that do not defeat

- A nasab that skips a generation, or names a person after a grandfather («نسبة لجده»).
- Dotting variants of a rare name (sec. 6.3), when everything else fits.
- A nisba present on one side only: persons bear several.

Each is recorded in `note`.

## 6. Searching

### 6.1 Before any search

Read the whole biography. Settle what kind of mention it is: a name; a kin term («والده», «أخيه»,
«ابن عمه»); a designation without a name («شيخنا», «السلطان», «صاحب مكة»); a first person. Settle
who is speaking (sec. 7.2). Note the dates in the biography: they bound everyone in it.

### 6.2 The tools

| Tool | What it does |
|---|---|
| `search_names` | Searches the headings (name, laqab in both forms, kunya, nisba, «ويعرف بـ») for a phrase. With the record and a kin term it also shifts the subject's nasab and looks at the neighbouring entries |
| `genealogy` | Headings that stand to the subject as father, son, brother, grandfather, uncle, cousin, and so on, by nasab |
| `neighbours` | The headings before and after an entry |
| `read` | The full text of an entry, with its registry status and transfer target |
| `search_text` | Entries whose full text contains all the given words or phrases |
| `reverse` | Entries that refer to a given person |
| `authority` | Registry rows by name or alias: persons without an entry, the out-of-scope list, aliases of persons with entries |

The pre-search (name search, nasab shift, neighbours) is run for every mention before the model
starts, and its result is in the input. It is a first list. In a test on reviewed records, where
the mention was a name, the right entry was among its first twenty for about four mentions in
five; it is of little use for designations without a name.

### 6.3 Search steps

`checks` in the answer lists the steps that were made.

| Step | What | When it is required |
|---|---|---|
| `read` | Read the candidate's entry in full | Always before `identified`; for each of the `candidates` of `undetermined` |
| `names` | Search again with the name reduced or rearranged: without the laqab; laqab and nisba only; ism and father only; with and without «ابن»; with the kunya | Before `not_found`; before `out_of_scope` unless the ground is `list` |
| `variants` | Search again with dotting and spelling variants: ب ت ث ن ي; ج ح خ; د ذ; ر ز; س ش; ص ض; ط ظ; ع غ; ف ق; Turkic names written as one word and as two; a form the author himself offers («صوابه», «ويقال», «فكأنه») | Before `not_found` |
| `text` | Full-text search for the by-name or for name and nisba. A by-name is often given only in the body («ويعرف بـ…» after the first sentence) | Before `not_found`; before `out_of_scope` unless `list` |
| `sections` | Look in the part of the book that fits the form of the mention: kunyas for «أبو X»; laqabs and nisbas for a by-name; «ابن X» names; the women's part for a mother, wife, sister or daughter | Before `not_found`, when the form applies |
| `kin` | `genealogy` and `neighbours` for a kin term; relatives stand near each other when they share a name and father | Before `not_found`, for a kin mention |
| `authority` | Registry search | Before `not_found` and `out_of_scope` |
| `mutual` | Look in the candidate's entry for the subject of this biography | Whenever a candidate is read |

A named master, predecessor, successor or in-law is searched by the single name first and narrowed
by nisba and office.

A search often returns the entry of a relative whose heading names the person looked for («أخو
الزين طاهر الماضي»). That is a lead to the person's own entry, with a pointer to follow; it is not
the entry.

### 6.4 Limits

The number of tool calls per mention beyond the pre-search is capped (the cap is set by the
harness; 8 in the trial). When the cap is reached with required steps still open, answer
`undetermined` or `not_found` as the evidence stands and set the flag `budget_exhausted`.

## 7. Reading al-Sakhāwī

### 7.1 «شيخنا»

In the narrator's own text, «شيخنا» alone is Ibn Ḥajar al-ʿAsqalānī. If a name follows («شيخنا
الرشيدي»), it is that person. Inside a quotation, «شيخنا» is the shaykh of the author quoted.
«صاحبنا» and «رفيقنا» mark someone of al-Sakhāwī's own generation; «ابن صاحبنا» the son of such a
one. They help to check the generation.

### 7.2 Who is speaking

The first person in the narrator's text is al-Sakhāwī («سمع مني», «لقيته», «أجاز لي»). Inside a
quotation it is the author quoted: in «قال الطاووسي : أجاز لي», the ijāza was given to al-Ṭāwūsī;
in «قال شيخنا … ابني», the son is Ibn Ḥajar's. In nested reports («حكى عنه … في ترجمة أبيه»,
«قاله لي X»), a pronoun is first tried on the person named last before it. If the speaker cannot
be settled and the identification depends on it, the verdict is `undetermined`.

### 7.3 Pointers

- «الماضي»: the entry stands earlier in the book. «الآتي»: later. «قريبا»: near by.
- «الذي قبله», «اللذين قبله», «الذي بعده»: the neighbouring entries.
- «يأتي في الكنى», «في الألقاب», «في النساء»: in that part.
- «الماضي أبوه», «الآتي ولده», «أخو X الماضي»: the relative named has an entry in that direction.
- «في ابن X», in a transfer heading, sends to the subject's own entry under «… بن X»; it does not
  mean the entry of a son.
- «فيمن جده X»: the subject's own entry, among those whose grandfather is X.

A pointer raises a candidate that lies in the stated direction and marks for review one that does
not. It does not rule a candidate out: the kunya part and the women's part have their own order,
and some announced entries were never written. Report the pointer and whether the order agrees
(`pointer.consistent`). A pointer with no entry to match gets the flag `announced_entry_missing`.

### 7.4 Names

- A laqab has two forms: «الشمس» and «شمس الدين». For officials and amirs a third occurs
  («الشمسي», «الزيني»).
- A laqab in the dual or plural belongs to each name that follows: «الزينين عبادة وطاهر» are
  al-Zayn ʿUbāda and al-Zayn Ṭāhir.
- «ابن X» may be a by-name carried for generations; X need not be the father.
- «سبط X»: a daughter's child of X. «حفيد X»: a son's child, or any descendant. «قريبه»: a
  relative, degree unknown.
- «X أبوه», after a nisba or a trade in a heading, says it of the father, not of the subject.
- Sultans are named by regnal title, and the titles repeat («الظاهر», «الأشرف», «الناصر»,
  «المؤيد», «المنصور»). The date of the event decides which is meant; read the sultan's entry for
  his years. A master's nisba on a mamluk («الظاهري برقوق», «الأشرفي برسباي») names the master.
- «السلطان», «صاحب مكة», «القاضي» without a name: `identified` only if the same passage fixes the
  year or the reign, and then with `medium`; otherwise `undetermined`.

### 7.5 Sources named in passing

«ذكره شيخنا في معجمه», «قاله المقريزي في عقوده», «أرخه ابن فهد»: the person named is the author of
a source. He is identified like anyone else. Where a family of authors shares a name, see
`conventions.md`.

## 8. The answer

One JSON object per biography; schema in `tools/identify/prompts/output.schema.json`.

```json
{
  "record": "AIND-D06501",
  "guideline": "identification/0.1",
  "results": [
    {
      "mention": "m1",
      "verdict": "identified",
      "id": "AIND-D06500",
      "certainty": "high",
      "basis": ["pointer", "nasab"],
      "evidence": [
        {"entry": "AIND-D06501", "quote": "أخو الذي قبله وذاك الأكبر"},
        {"entry": "AIND-D06500", "quote": "محمد بن إبراهيم بن عبد الرحمن بن حسين بن قاسم الشمس بن البرهان المدني"}
      ],
      "pointer": {"phrase": "الذي قبله", "consistent": true},
      "mutual": "no",
      "checks": ["read", "mutual"],
      "rejected": [],
      "note": ""
    }
  ]
}
```

- `evidence[].quote` is copied from the entry, not paraphrased, and short (up to about 25 words).
  At least one quote comes from the candidate's entry.
- `rejected` lists candidates that a careful reader would have considered, each with one line on
  why not. `candidates` (for `undetermined`) lists those still standing, and `decides` says what
  would settle it.
- `other_entries`: a second biography or an index entry of the same person (sec. 3.2).
- `mutual`: `yes`, `no`, `not_checked`.
- `flags`: `transfer_followed`, `transfer_unresolved`, `index_entry`, `announced_entry_missing`,
  `pointer_inconsistent`, `spelling_differs`, `nasab_differs`, `durar_candidate`,
  `budget_exhausted`, `speaker_unclear`, `registry_row_doubtful`.
- `note` is in English, one or two sentences. Arabic is quoted as printed.
- Every mention in the input gets exactly one result.

The harness records every tool call with its arguments and result. The answer does not repeat
them; `checks` says which steps the model considers done, and the harness compares.

## 9. Verification (stage 3)

A model of another vendor checks the main model's answers. It never sees the main model's verdict
or reasoning.

- **Main verdict `identified`:** the verifier gets the biography, the mention, and a shuffled list
  of candidates (the main model's choice, its rejected candidates, and the top of the pre-search),
  with «none of these» always available. It may read entries; it may not search. It chooses, and
  gives evidence in the same form. Prompt: `verify_choice.system.md`.
- **Main verdict `not_found` or `out_of_scope`:** the verifier does the whole task again with the
  same tools and the same prompt as the main model, without the main model's output.
- `same_as_mention`, `undetermined` and `extraction_error` are not verified by a model; they go
  to a person or back to stage 1.

Agreement means the same verdict and, for `identified`, the same `id`. Disagreements go to WK.

## 10. Provenance

Kept with every result: the model and its version, the date, the guideline version, the registry
and corpus commit, the tool calls, and the answer as returned. Reproducibility here means that a
third party can check the grounds, not that the run can be repeated bit for bit.

---

## Appendix A. Where the rules come from

| Section | Source |
|---|---|
| 2.1 | Rule 25, WK 2026-10-04; WK 2026-11-19 (no emendation by conjecture) |
| 2.2, 5.5 | Rule 26, WK 2026-10-04; rule 57, WK 2026-10-27; rule 62, WK 2026-11-05 |
| 2.3 | Rules 60 (h), 63 (f), 66 (a); WK 2026-11-04 |
| 2.4, 6.3 | Rules 10, 32, 38, 61 (a), 63 (c)(d), 66 (b)(c); design v5, external review of 2026-11-24 |
| 2.5 | WK 2026-10-26 (no Wikidata or GeoNames numbers from memory) |
| 3.2 | Rule 11 with WK 2026-09-18 and 2026-10-21; the transfer rulings of 2026-09-08, 2026-11-11, 2026-11-28 |
| 3.3 | WK 2026-11-28 and 2026-11-29 (AIND is the canonical ID; external IDs only in `same_as`) |
| 4 | Design v5, sec. 4.1; `propose_registry` from rules 3 and 12 |
| 5.2 (kin) | Rules 23 and 37 |
| 5.3 | The certainty scale of the briefs (أظنه = medium) |
| 5.4 | Rule 26, exception 2, WK 2026-10-19; rule 61 (c) |
| 5.6 | Rules 30, 34, 61 (b) |
| 7.1, 7.2 | Design v5, sec. 4.3; rules 44 and 59 (f) |
| 7.3 | Design v5, sec. 4.3 |
| 9 | Design v5, sec. 4.4 and 5 |

## Appendix B. Rulings on this guideline and open points

Ruled by WK on 2026-11-29:

1. A person with a biography is answered with the AIND number, which is the canonical ID; a
   Wikidata number belongs in the registry's `same_as` column (sec. 3.3). The records up to now
   use `wd:Q471116` for Ibn Ḥajar and `wd:Q4120128` for al-Sakhāwī; until the registry rows are
   joined and the records re-pointed, scoring treats the two forms as equal.
2. `registry_id` on `not_found` and `out_of_scope`, and `propose_registry` (sec. 4.4, 4.5).
3. `certainty: low` only by convention (sec. 4.1).
4. An unnamed «السلطان» or «صاحب مكة» is identified only if the same passage fixes the year or
   the reign, with `medium`; otherwise `undetermined` (sec. 7.4).
5. Double entries: the entry whose text matches the mention, the other in `other_entries`
   (sec. 3.2).
6. `conventions.md` is given to all three vendors in the trial as it stands, although some of its
   names occur in the ten trial biographies.

Open:

- The cap on tool calls (sec. 6.4) is provisional; to be set from the trial.
- The index parts (about 1,780 headings, AIND-D11136 – D12843) are all `active` in the registry,
  whether they are a person's only entry, a pointer to a biography, or a list of several persons.
  Identification will meet them constantly (sec. 3.2).
- The out-of-scope list (sec. 4.5) does not exist yet.
- The registry's `wd:` rows for persons who have a biography are still to be joined to the AIND
  rows (ruling 1).
