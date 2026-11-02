#!/usr/bin/env python3
"""TEI-XML (Individuals/*.xml) -> RDF (Turtle) prototype converter.
Vocabulary: CIDOC-CRM for persons / birth / death / events / time-spans / places,
a lightweight project vocabulary (aindv:) for relations, names, offices,
PROV-O for record provenance (human and AI agents).
Usage: python3 xml2ttl.py <Individuals_dir> <out.ttl> [--idm=<ID-Master export .tsv>] [AIND-Dxxxxx ...]
"""
import sys, glob, os, re
from lxml import etree
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD, PROV

BASE = "https://wkmisr.github.io/arab-islamic-networks/"   # provisional; to be replaced by a w3id.org persistent URI once the encoding is complete
AIND = Namespace(BASE + "id/")
REC  = Namespace(BASE + "record/")
AG   = Namespace(BASE + "agent/")
V    = Namespace(BASE + "vocab#")
CRM  = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
WD   = Namespace("http://www.wikidata.org/entity/")
XMLNS = "{http://www.w3.org/XML/1998/namespace}"

def ref2uri(ref):
    if not ref: return None
    ref = ref.strip().split()[0]
    if ref.startswith("#NEEDID"): return None
    if ref.startswith("#"): return AIND[ref[1:]]
    if ref.startswith("wd:"): return WD[ref[3:]]
    if ref.startswith("gn:"): return URIRef("https://sws.geonames.org/%s/" % ref[3:])
    return None

def lit(el, text=None):
    t = (text if text is not None else "".join(el.itertext())).strip()
    t = re.sub(r"\s+", " ", t)
    lang = el.get(XMLNS + "lang")
    return Literal(t, lang=lang) if lang else Literal(t)

def slug(s): return re.sub(r"[^A-Za-z0-9_]+", "_", s).strip("_")

def timespan(g, node, el):
    attrs = {k: el.get(k) for k in ("when", "notBefore", "notAfter", "when-custom")}
    if not any(attrs.values()): return
    ts = URIRef(str(node) + "-ts")
    g.add((ts, RDF.type, CRM["E52_Time-Span"]))
    g.add((node, CRM["P4_has_time-span"], ts))
    if attrs["when"]:      g.add((ts, CRM["P82_at_some_time_within"], Literal(attrs["when"])))
    if attrs["notBefore"]: g.add((ts, CRM["P82a_begin_of_the_begin"], Literal(attrs["notBefore"])))
    if attrs["notAfter"]:  g.add((ts, CRM["P82b_end_of_the_end"], Literal(attrs["notAfter"])))
    if attrs["when-custom"]: g.add((ts, V.hijriDate, Literal(attrs["when-custom"])))

def cert(g, node, el):
    if el.get("cert"): g.add((node, V.certainty, V["cert_" + el.get("cert")]))

def places(g, node, el):
    for pl in el.findall("placeName"):
        u = ref2uri(pl.get("ref"))
        if u:
            g.add((node, CRM.P7_took_place_at, u))
            g.add((u, RDFS.label, lit(pl)))

def convert(g, path):
    root = etree.parse(path).getroot()
    pid = root.get(XMLNS + "id")
    p = AIND[pid]; rec = REC[pid]
    g.add((p, RDF.type, CRM.E21_Person))
    if root.get("type"): g.add((p, V.recordType, Literal(root.get("type"))))
    if root.get("corresp"):
        u = ref2uri(root.get("corresp"))
        if u: g.add((p, OWL.sameAs, u))
    # names
    for i, pn in enumerate(root.findall("persName")):
        t = pn.get("type") or "name"
        if t == "full": g.add((p, RDFS.label, lit(pn)))
        ap = URIRef(str(p) + "-name-%d" % (i + 1))
        g.add((ap, RDF.type, CRM.E41_Appellation))
        g.add((ap, CRM.P2_has_type, V["name_" + slug(t)]))
        g.add((ap, RDFS.label, lit(pn)))
        g.add((p, CRM.P1_is_identified_by, ap))
        u = ref2uri(pn.get("ref"))
        if u: g.add((p, V["has_" + slug(t)], u)); g.add((u, RDFS.label, lit(pn)))
    sx = root.find("sex")
    if sx is not None and sx.get("value"): g.add((p, V.sex, Literal(sx.get("value"))))
    for af in root.findall("affiliation"):
        u = ref2uri(af.get("ref"))
        prop = V[slug(af.get("type") or "affiliation")]
        g.add((p, prop, u if u else lit(af)))
    # birth / death
    for tag, cls, prop in (("birth", CRM.E67_Birth, CRM.P98i_was_born),
                           ("death", CRM.E69_Death, CRM.P100i_died_in)):
        for el in root.findall(tag):
            n = URIRef(str(p) + "-" + tag); g.add((n, RDF.type, cls)); g.add((p, prop, n))
            timespan(g, n, el); cert(g, n, el); places(g, n, el)
    # relations: qualified node + direct shortcut triple
    for i, rel in enumerate(root.iter("relation")):
        st = slug(rel.get("subtype") or rel.get("name") or "related")
        a, b = ref2uri(rel.get("active")), ref2uri(rel.get("passive"))
        r = URIRef(str(p) + "-rel-%d" % (i + 1))
        g.add((r, RDF.type, V.Relationship)); g.add((r, V.relType, V[st]))
        if a: g.add((r, V.active, a))
        if b: g.add((r, V.passive, b))
        cert(g, r, rel)
        for d in rel.findall("desc"):
            if d.get("type") in ("method", "field"):
                k = d.get("type")
                g.add((r, V[k + "Text"], lit(d)))
                u = ref2uri(d.get("ref"))
                if u: g.add((r, V[k], u))
            else:
                g.add((r, RDFS.label, lit(d)))
                if a: g.add((a, V.mentionedAs, lit(d)))
        for ev in rel.findall("event"):
            timespan(g, r, ev)
        if a and b: g.add((a, V[st + "Of"], b))
    # events
    for i, ev in enumerate(root.findall("event")):
        e = URIRef(str(p) + "-ev-%d" % (i + 1))
        g.add((e, RDF.type, CRM.E5_Event))
        t = ev.get("type") or "event"; s = ev.get("subtype")
        g.add((e, CRM.P2_has_type, V["event_" + slug(t + ("_" + s if s else ""))]))
        g.add((e, CRM.P11_had_participant, p))
        for pn in ev.findall("persName"):
            u = ref2uri(pn.get("ref"))
            if u: g.add((e, V.mentions if s == "mention" else CRM.P11_had_participant, u))
        for d in ev.findall("desc"): g.add((e, RDFS.label, lit(d)))
        timespan(g, e, ev); cert(g, e, ev); places(g, e, ev)
    # states (offices etc.)
    for i, stt in enumerate(root.findall("state")):
        s = URIRef(str(p) + "-state-%d" % (i + 1))
        g.add((s, RDF.type, V.StateHolding)); g.add((p, V.holds, s))
        g.add((s, V.stateType, V[slug(stt.get("type") or "state")]))
        u = ref2uri(stt.get("ref"))
        if u: g.add((s, V.office, u))
        for lb in stt.findall("label"):
            g.add((s, RDFS.label, lit(lb)))
            if u: g.add((u, RDFS.label, lit(lb)))
        for o in stt.findall("orgName"):
            uo = ref2uri(o.get("ref"))
            if uo: g.add((s, V.institution, uo)); g.add((uo, RDFS.label, lit(o)))
        timespan(g, s, stt); cert(g, s, stt); places(g, s, stt)
    # record + provenance (human and AI agents)
    g.add((rec, RDF.type, PROV.Entity)); g.add((rec, V.describes, p))
    for n in root.findall("note"):
        if n.get("type") == "source": g.add((rec, V.sourceText, lit(n)))
        if n.get("type") == "translation" and n.get(XMLNS + "lang") == "en":
            g.add((rec, V.translation, lit(n)))
    for i, rs in enumerate(root.findall("respStmt")):
        q = URIRef(str(rec) + "-resp-%d" % (i + 1))
        name = (rs.findtext("persName") or "").strip()
        ag = AG[slug(name)]
        g.add((ag, RDF.type, PROV.SoftwareAgent if name.lower().startswith(("claude", "gemini")) else PROV.Person))
        g.add((ag, RDFS.label, Literal(name)))
        g.add((rec, PROV.qualifiedAttribution, q)); g.add((rec, PROV.wasAttributedTo, ag))
        g.add((q, RDF.type, PROV.Attribution)); g.add((q, PROV.agent, ag))
        r = rs.find("resp")
        if r is not None: g.add((q, PROV.hadRole, lit(r)))
        d = rs.find("date")
        if d is not None and d.get("when"): g.add((q, PROV.atTime, Literal(d.get("when"), datatype=XSD.date)))

def idmaster(g, tsv):
    """Labels and categories for every identifier registered in the ID-Master export."""
    import csv
    with open(tsv, encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            u = ref2uri(("#" if re.match(r"(AIND|TMP)-", row.get("ID") or "") else
                         "wd:" if (row.get("ID") or "").startswith("Q") else
                         "gn:" if (row.get("ID") or "").isdigit() else "x") + (row.get("ID") or ""))
            if not u: continue
            for col, lang in (("Arabic", "ar"), ("Latin", "ar-Latn")):
                for v in (row.get(col) or "").split("|"):
                    if v.strip(): g.add((u, RDFS.label, Literal(v.strip(), lang=lang)))
            if row.get("Category"): g.add((u, V.category, V["cat_" + slug(row["Category"])]))

def main():
    src, out = sys.argv[1], sys.argv[2]
    tsv = [a[6:] for a in sys.argv[3:] if a.startswith("--idm=")]
    only = set(a for a in sys.argv[3:] if not a.startswith("--idm="))
    g = Graph()
    for pfx, ns in (("aind", AIND), ("rec", REC), ("agent", AG), ("aindv", V), ("crm", CRM),
                    ("wd", WD), ("prov", PROV), ("owl", OWL), ("rdfs", RDFS)):
        g.bind(pfx, ns)
    g.bind("gn", Namespace("https://sws.geonames.org/"))
    files = sorted(glob.glob(os.path.join(src, "*", "*.xml")))
    n = 0; errs = []
    for f in files:
        if only and not any(os.path.basename(f).startswith(o) for o in only): continue
        try: convert(g, f); n += 1
        except Exception as e: errs.append((f, repr(e)))
    if tsv: idmaster(g, tsv[0])
    g.serialize(out, format="turtle")
    print("records", n, "triples", len(g), "errors", len(errs))
    for e in errs[:10]: print(e)

if __name__ == "__main__": main()
