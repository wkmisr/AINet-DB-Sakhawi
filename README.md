# Arab-Islamic Network DB Project (AINet-DB)

This repository builds a structured, TEI-XML prosopographical database from al-Sakhāwī's (d. 902 H / 1497 CE) biographical dictionary *al-Ḍawʾ al-Lāmiʿ li-Ahl al-Qarn al-Tāsiʿ*, in order to reconstruct the networks of scholars, officials and merchants of the late Mamluk period (9th century AH).

This project is supported by JSPS KAKENHI Grant Number [26K00196](https://kaken.nii.ac.jp/en/grant/KAKENHI-PROJECT-26K00196/) (Grant-in-Aid for Scientific Research (B), FY2026–2030).

## Method

- Each biographical entry is drafted into TEI-XML by a generative AI (Gemini), reviewed by a different AI (Claude), independently re-checked, and every open question is ruled on by a human editor (human-in-the-loop).
- Persons, places, institutions, offices, books and subjects are identified with project IDs kept in the ID-Master (a shared Google Sheet), and linked to Wikidata / GeoNames where a match has been verified.

## Repository layout

| Path | Contents |
|---|---|
| `0__DawForAIND_renumbered_B54_split20260905.txt` | The base text of *al-Ḍawʾ al-Lāmiʿ*, one entry per record, with AIND-D IDs (see format below). All XML is checked against this text. |
| `Individuals/` | The reviewed TEI-XML files, one per entry, in sub-folders by AIND number (`0000-0999/` … `13000-13999/`). Cross-reference entries are prefixed `REF_`. |
| `Dawou_Lami/` | Scans of the printed edition used for checking. |
| `app.py`, `prompt_analyze.txt`, `requirements.txt` | AINet-DB Researcher Pro (Streamlit app used for drafting). User guide (Japanese): `docs/app_guide_ja.md`. |
| `CHANGELOG.md` | Change log of the base text and of manual data corrections. |
| `docs/` | Working documentation — see [`docs/README.md`](docs/README.md). |

## Base text format

```
###$AIND-DXXXXX | NNNNNNNNNNNN$# {marker} text…
```

- `AIND-DXXXXX` — AIND-D ID (5 digits; letter suffix such as `D00544a` for inserted entries). Used as `xml:id`.
- `NNNNNNNNNNNN` — 12-digit source ID. Used as the `source` attribute.
- marker: `$` male entry, `$$` female entry, `$$$` cross-reference to another entry.

XML file names follow `{AIND-D ID}_{12-digit ID}.xml`, e.g. `AIND-D00001_932540579843.xml`.

## Identifiers

| Prefix | Meaning |
|---|---|
| `AIND-D…` | An entry (person) of *al-Ḍawʾ al-Lāmiʿ* |
| `TMP-P-` / `TMP-L-` / `TMP-I-` / `TMP-O-` / `TMP-T-` / `TMP-N-` / `TMP-S-` | Provisional project IDs for persons not entered in the book, locations, institutions, offices, texts, nisbas, and subjects (registered in the ID-Master) |
| `wd:Q…` / `gn:…` | Wikidata / GeoNames, used only after verification |
| `#NEEDID` | A person mentioned without enough information to identify |
