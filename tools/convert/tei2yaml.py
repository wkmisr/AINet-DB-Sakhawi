#!/usr/bin/env python3
"""AINet-DB: TEI-XML person record <-> YAML (lossless round trip).

Usage:
  tei2yaml.py to-yaml  in.xml  out.yml
  tei2yaml.py to-xml   in.yml  out.xml
  tei2yaml.py check    <dir-of-xml>      # round-trip every file, report diffs

Design
- Top level of a record gets readable keys (id, sex, names, birth, death,
  relations, events, states, affiliations, source_text, translation, notes, resp).
- Below that, every element becomes a mapping: attributes as keys, text as
  `text`, children grouped by tag (`placeName` -> `places`, ...).
- `#AIND-...`, `#TMP-...`, `#NEEDID` lose the '#' (restored on the way back).
- `when-custom` etc. (AH) become `when_ah` etc.; `xml:lang` becomes `lang`.
- Order of siblings with different tags is not kept (it carries no meaning
  in this schema); order among same-tag siblings is kept.
"""
import re, sys, glob
from lxml import etree
import yaml

XML_NS = "{http://www.w3.org/XML/1998/namespace}"

ATTR_OUT = {f"{XML_NS}lang": "lang", f"{XML_NS}id": "id",
            "when-custom": "when_ah", "notBefore-custom": "notBefore_ah",
            "notAfter-custom": "notAfter_ah"}
ATTR_IN = {v: k for k, v in ATTR_OUT.items()}
REF_ATTRS = {"ref", "active", "passive", "target", "corresp"}
LOCAL_ID = re.compile(r"^#((?:AIND|TMP)-[A-Z]-?\w+|NEEDID\w*)$")

CHILD_OUT = {"persName": "names", "placeName": "places", "orgName": "orgs",
             "desc": "descs", "note": "notes", "bibl": "bibls",
             "event": "events", "relation": "relations", "state": "states",
             "affiliation": "affiliations", "respStmt": "resp",
             "label": "labels", "date": "dates", "resp": "resp_label",
             "listRelation": "listRelation", "p": "p", "span": "span"}
CHILD_IN = {v: k for k, v in CHILD_OUT.items()}
SINGLE = {"birth", "death", "sex"}


def ref_out(v):
    return " ".join(LOCAL_ID.sub(r"\1", t) for t in v.split(" "))


def ref_in(v):
    return " ".join(("#" + t) if re.match(r"^((AIND|TMP)-|NEEDID)", t) else t
                    for t in v.split(" "))


def el2d(e):
    d = {}
    for k, v in e.attrib.items():
        key = ATTR_OUT.get(k, k)
        if k in REF_ATTRS:
            v = ref_out(v)
        elif key.endswith("_ah") and re.fullmatch(r"\d{4}", v):
            v = int(v)                      # 0820 -> 820 (re-padded on output)
        elif re.fullmatch(r"[1-9]\d*", v):
            v = int(v)
        d[key] = v
    if e.text and e.text.strip():
        d["text"] = e.text
    for c in e:
        if isinstance(c, etree._Comment):
            d.setdefault("comments", []).append(c.text)
            continue
        if c.tail and c.tail.strip():           # mixed content: keep tail
            pass
        tag = etree.QName(c).localname
        cd = el2d(c)
        if c.tail and c.tail.strip():
            cd["_tail"] = c.tail
        if tag in SINGLE:
            d[tag] = cd
        else:
            d.setdefault(CHILD_OUT.get(tag, tag), []).append(cd)
    return d


def person2d(root):
    d = el2d(root)
    out = {}
    out["id"] = d.pop("id")
    out["source_id"] = d.pop("source")
    for k in ("type", "subtype", "corresp"):
        if k in d:
            out[k] = d.pop(k)
    if "comments" in d:
        out["generator"] = [c.strip() for c in d.pop("comments")]
    if "sex" in d:
        out["sex"] = d.pop("sex")["value"]
    for k in ("names", "birth", "death"):
        if k in d:
            out[k] = d.pop(k)
    # flatten listRelation (normally exactly one, holding relations)
    lr = d.pop("listRelation", [])
    if lr:
        out["listRelation"] = lr
    for k in ("relations", "events", "states", "affiliations"):
        if k in d:
            out[k] = d.pop(k)
    notes = d.pop("notes", [])
    rest = []
    for n in notes:
        if n.get("type") == "source" and set(n) <= {"type", "lang", "text"} \
                and "source_text" not in out:
            out["source_text"] = n["text"]
        elif n.get("type") == "translation" and set(n) <= {"type", "lang", "text"} \
                and n.get("lang") not in out.get("translation", {}):
            out.setdefault("translation", {})[n["lang"]] = n["text"]
        else:
            rest.append(n)
    if rest:
        out["notes"] = rest
    if "resp" in d:
        out["resp"] = d.pop("resp")
    if "text" in d:
        out["_text"] = d.pop("text")
    out.update(d)   # anything unforeseen is kept verbatim
    return out


def d2el(tag, d):
    e = etree.Element(tag)
    for k, v in d.items():
        if k in ("text", "_tail", "comments") or isinstance(v, (list, dict)):
            continue
        name = ATTR_IN.get(k, k)
        if k in REF_ATTRS:
            v = ref_in(v)
        elif k.endswith("_ah") and isinstance(v, int):
            v = str(v).zfill(4)
        e.set(name, str(v))
    if "text" in d:
        e.text = d["text"]
    for c in d.get("comments", []):
        e.append(etree.Comment(c))
    for k, v in d.items():
        if k in SINGLE and isinstance(v, dict):
            e.append(d2el(k, v))
        elif isinstance(v, list) and k != "comments":
            ctag = CHILD_IN.get(k, k)
            for item in v:
                ce = d2el(ctag, item)
                if "_tail" in item:
                    ce.tail = item["_tail"]
                e.append(ce)
    return e


def d2person(p):
    d = {"id": p["id"], "source": p["source_id"]}
    for k in ("type", "subtype", "corresp"):
        if k in p:
            d[k] = p[k]
    if "generator" in p:
        d["comments"] = [f" {c} " for c in p["generator"]]
    if "_text" in p:
        d["text"] = p["_text"]
    if "sex" in p:
        d["sex"] = {"value": p["sex"]}
    for k, v in p.items():
        if k in ("id", "source_id", "type", "subtype", "corresp", "generator",
                 "sex", "source_text", "translation", "_text"):
            continue
        d[k] = v
    notes = list(p.get("notes", []))
    if "source_text" in p:
        notes.insert(0, {"type": "source", "lang": "ar", "text": p["source_text"]})
    for lang, t in p.get("translation", {}).items():
        notes.append({"type": "translation", "lang": lang, "text": t})
    if notes:
        d["notes"] = notes
    return d2el("person", d)


# ---------- YAML output: literal blocks for multi-line text, no line wrap
class Dumper(yaml.SafeDumper):
    pass


def _str(dumper, s):
    style = "|" if "\n" in s else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", s, style=style)


Dumper.add_representer(str, _str)


def to_yaml(xml_path):
    root = etree.parse(xml_path).getroot()
    return yaml.dump(person2d(root), Dumper=Dumper, allow_unicode=True,
                     sort_keys=False, width=10**6)


def to_xml(yml_text):
    return d2person(yaml.safe_load(yml_text))


# ---------- canonical comparison
def canon(e, top=True):
    if isinstance(e, etree._Comment):
        return ("#comment", e.text.strip())
    attrs = tuple(sorted(e.attrib.items()))
    text = e.text if (e.text and e.text.strip()) else None
    tail = e.tail if (e.tail and e.tail.strip()) else None
    kids = [canon(c, False) for c in e]
    # stable: same-tag order kept; person-level notes are compared as a set
    kids.sort(key=lambda k: (k[0], k if (k[0] == "note" and top) else ()))
    return (etree.QName(e).localname if not isinstance(e, etree._Comment) else "#c",
            attrs, text, tail, tuple(kids))


def check(paths):
    bad = []
    for f in paths:
        orig = etree.parse(f).getroot()
        orig.tail = None
        back = to_xml(to_yaml(f))
        if canon(orig) != canon(back):
            bad.append(f)
    return bad


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "to-yaml":
        open(sys.argv[3], "w").write(to_yaml(sys.argv[2]))
    elif cmd == "to-xml":
        el = to_xml(open(sys.argv[2]).read())
        etree.indent(el, space="    ")
        open(sys.argv[3], "wb").write(etree.tostring(el, encoding="utf-8"))
    elif cmd == "check":
        fs = sorted(glob.glob(sys.argv[2] + "/**/*.xml", recursive=True))
        bad = check(fs)
        print(f"{len(fs)} files, {len(fs)-len(bad)} lossless, {len(bad)} differ")
        for b in bad[:20]:
            print("  DIFF", b)
