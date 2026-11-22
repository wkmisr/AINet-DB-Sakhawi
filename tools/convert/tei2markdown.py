#!/usr/bin/env python3
"""AINet-DB: TEI-XML person record -> OpenITI mARkdown entry with inline tags.

The Arabic text is the record's <note type="source">. Tags are derived from
the verified XML:
  @YB### / @YD### / @YY###  year of birth / death / other year (AH),
                             placed before the word سنة of the matching phrase
  @T##                       toponym  (first digit = prefix letters, second = words)
  @P##                       person named in the text (not the subject's own nasab)
Manual-style tags (@T, @P) are used because the data were human-verified.
Identifiers are not written inline (mARkdown has no slot for them); the tag
order is listed in the YAML (`markdown_tags`) so each tag can be resolved.

Usage:  tei2markdown.py in.xml out.md        # one record
        tei2markdown.py --stats <dir>        # coverage over a directory
"""
import re, sys, glob
from lxml import etree

XL = "{http://www.w3.org/XML/1998/namespace}lang"

# ---------- Arabic year words -> number
UNITS = {"واحد": 1, "احدى": 1, "إحدى": 1, "اثنتين": 2, "اثنين": 2, "ثنتين": 2, "اثنتي": 2, "اثني": 2, "إثنتين": 2,
         "ثلاث": 3, "ثلاثة": 3, "أربع": 4, "اربع": 4, "أربعة": 4, "خمس": 5, "خمسة": 5,
         "ست": 6, "ستة": 6, "سبع": 7, "سبعة": 7, "ثمان": 8, "ثماني": 8, "ثمانية": 8,
         "تسع": 9, "تسعة": 9}
TENS = {"عشر": 10, "عشرة": 10, "عشرين": 20, "ثلاثين": 30, "أربعين": 40, "اربعين": 40,
        "خمسين": 50, "ستين": 60, "سبعين": 70, "ثمانين": 80, "تسعين": 90}
HUND = {"مائة": 100, "مئة": 100, "مائتين": 200, "ثلاثمائة": 300, "أربعمائة": 400,
        "اربعمائة": 400, "خمسمائة": 500, "ستمائة": 600, "سبعمائة": 700,
        "ثمانمائة": 800, "ثمانمئة": 800, "تسعمائة": 900}
NUMWORD = set(UNITS) | set(TENS) | set(HUND)


def parse_year(words):
    """words after سنة -> (value, n_words_used, has_hundreds)"""
    total, used, hund = 0, 0, False
    pending_wa = 0
    for w in words:
        w = w.rstrip(".،,؛;:")
        if w == "و" and used:            # "ست و تسعين": a detached و
            pending_wa += 1
            continue
        w0 = w[1:] if w.startswith("و") and w[1:] in NUMWORD else w
        if w0 in UNITS: total += UNITS[w0]
        elif w0 in TENS: total += TENS[w0]
        elif w0 in HUND: total += HUND[w0]; hund = True
        else: break
        used += 1 + pending_wa
        pending_wa = 0
    return (total, used, hund) if used else (None, 0, False)


def year_phrases(tokens, anchor, known=(), month_ends=()):
    """yield (token_index, AH year); the index is that of سنة/عام, or of the
    first number word when the year follows a month name without سنة.
    Sakhawi often drops the hundreds (سنة خمس عشرة) or even the tens (سنة خمس)
    when the context fixes them. Such a year is completed to the year that
    (1) ends in the same digits and is attested in the XML (`known`), else
    (2) ends in the same digits and does not run backwards from the last year read, else
    (3) takes the century of the anchor year."""
    known = sorted(k for k in set(known) if k)
    last_full = None
    out = []
    month_ends = set(month_ends)
    for i, t in enumerate(tokens):
        if t in ("سنة", "سنه", "عام"):
            val, used, hund = parse_year(tokens[i + 1:i + 6])
        elif i in month_ends:
            val, used, hund = parse_year(tokens[i:i + 5])
        else:
            continue
        if val is None:
            continue
        if not hund:
            mod = 10 if val < 10 else 100
            fits = lambda y: y % mod == val % mod
            hit = [k for k in known if fits(k)]
            if last_full is not None and hit:
                after = [k for k in hit if k >= last_full]
                hit = after or hit
            if hit:
                val = hit[0]
            elif last_full is not None:
                val = next(y for y in range(last_full, last_full + 1000) if fits(y))
            elif anchor:
                val = (anchor // 100) * 100 + val if val >= 10 else (anchor // 10) * 10 + val
            else:
                continue
        last_full = val
        out.append((i, val))
    return out


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def find_span(tokens, name, start=0):
    """locate name (list of words) allowing a 1-2 letter proclitic on word 1.
    returns (index, prefix_len) or None"""
    nw = name.split()
    for i in range(start, len(tokens) - len(nw) + 1):
        if tokens[i + 1:i + len(nw)] != nw[1:]:
            continue
        t, w = tokens[i], nw[0]
        if t == w:
            return i, 0
        for p in ("و", "ف", "ب", "ل", "ك", "وب", "فب", "ول", "بب"):
            if t == p + w:
                return i, len(p)
            if w.startswith("ال") and p.endswith("ل") and t == p + w[1:]:  # لل
                return i, len(p)
    return None


def build(xml_path):
    root = etree.parse(xml_path).getroot()
    pid = root.get(f"{{http://www.w3.org/XML/1998/namespace}}id")
    src = root.find("note[@type='source']")
    if src is None:
        return None
    tokens = norm(src.text).split(" ")
    ins = {}              # token index -> list of tag strings
    tags_meta = []        # for YAML: what each tag points to
    report = {"years": [], "places": [], "persons": []}

    def add(i, tag, ref):
        ins.setdefault(i, []).append(tag)
        tags_meta.append((i, tag, ref))

    # subject's own name ends at the first stand-alone "."
    try:
        body_start = tokens.index(".") + 1
    except ValueError:
        body_start = 0

    # --- years
    def ah(el):
        v = el.get("when-custom") if el is not None else None
        m = re.match(r"(\d{3,4})", v or "")
        return int(m.group(1)) if m else None
    yb, yd = ah(root.find("birth")), ah(root.find("death"))
    other = {ah(e) for e in root.iter("event", "state", "date") if ah(e)}
    anchor = yb or yd or (min(other) if other else None)
    found = set()
    for i, y in year_phrases(tokens, anchor, {yb, yd} | other):
        if y == yb: tag = f"@YB{y}"
        elif y == yd: tag = f"@YD{y}"
        else: tag = f"@YY{y}"
        add(i, tag, None)
        found.add(y)
    for label, y in (("birth", yb), ("death", yd)):
        if y:
            report["years"].append((label, y, y in found))

    # --- places (all placeName with text, anywhere in the record)
    seen = set()
    for pn in root.iter("placeName"):
        name = norm(pn.text or "")
        if not name or name in seen:
            continue
        seen.add(name)
        hit = find_span(tokens, name, body_start)
        report["places"].append((name, pn.get("ref"), bool(hit)))
        if hit:
            i, p = hit
            add(i, f"@T{p}{len(name.split())}", pn.get("ref"))

    # --- persons mentioned in the body (event/state persName, relation desc)
    cands = []
    for pn in root.iter("persName"):
        par = pn.getparent()
        if par is root or par.tag == "respStmt":
            continue
        cands.append((norm(pn.text or ""), pn.get("ref")))
    for rel in root.iter("relation"):
        other_id = rel.get("active") if rel.get("passive") == "#" + pid else rel.get("passive")
        for d in rel.findall("desc"):
            if d.get(XL) == "ar" and d.get("type") in (None, "name"):
                cands.append((norm(d.text or ""), other_id))
    seen = set()
    for name, ref in cands:
        if not name or name in seen:
            continue
        seen.add(name)
        hit = find_span(tokens, name, body_start)
        report["persons"].append((name, ref, bool(hit)))
        if hit:
            i, p = hit
            add(i, f"@P{p}{len(name.split())}", ref)

    out = []
    for i, t in enumerate(tokens):
        out.extend(ins.get(i, []))
        out.append(t)
    sex = root.find("sex")
    head = "### $$$ " if root.get("type") == "reference" else \
           "### $$ " if (sex is not None and sex.get("value") == "F") else "### $ "
    md = (f"#META# 000.AINet.RecordID :: {pid}\n"
          f"#META# 000.AINet.SourceID :: {root.get('source')}\n"
          f"#META# 000.AINet.Data :: {pid}.yml\n\n"
          f"{head}" + " ".join(out) + "\n")
    tags_meta.sort(key=lambda x: x[0])
    return md, [(t, r) for _, t, r in tags_meta], report


if __name__ == "__main__":
    if sys.argv[1] == "--stats":
        tot = {"years": [0, 0], "places": [0, 0], "persons": [0, 0]}
        miss = {"years": [], "places": [], "persons": []}
        n = 0
        for f in glob.glob(sys.argv[2] + "/**/*.xml", recursive=True):
            if "/REF_" in f:
                continue
            r = build(f)
            if not r:
                continue
            n += 1
            for k, items in r[2].items():
                for it in items:
                    tot[k][0] += 1; tot[k][1] += it[-1]
                    if not it[-1]: miss[k].append((f.split("/")[-1][:11],) + it[:-1])
        print(f"records: {n}")
        for k, (a, b) in tot.items():
            print(f"{k:8s} {b}/{a} = {b/a:.1%} tagged automatically")
        import random; random.seed(1)
        for k in miss:
            print(f"-- sample misses: {k}")
            for m in random.sample(miss[k], min(8, len(miss[k]))):
                print("  ", m)
    else:
        md, tags, rep = build(sys.argv[1])
        open(sys.argv[2], "w").write(md)
        print(md)
        for t in tags: print(t)
        print(rep)
