#!/usr/bin/env python3
"""AINet-DB 典拠台帳(Wikidata / GeoNames)の共通処理。標準ライブラリのみで動く。

このファイルは次の3つから使われる:
  - update_authority.py : 使用中URIの抽出 → Wikidata/GeoNames 取得 → 台帳・要照合表の書き出し
  - lookup.py           : 台帳のローカル検索
  - precheck_aind_v12.py: --authority 指定時の自動検査(不存在・リダイレクト・種別・近現代人物・没年差)

台帳の中身(取得したラベル・P31 等)は「照合の材料」であって「確認済み」ではない。
確認済みかどうかは verified.tsv(人が書く)だけが決める。
"""
import collections
import csv
import datetime
import glob
import importlib.util
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))

F_USED = os.path.join(HERE, "used_uris.tsv")
F_WD = os.path.join(HERE, "wd_entities.tsv")
F_GN = os.path.join(HERE, "gn_entities.tsv")
F_CLASS_LABELS = os.path.join(HERE, "wd_class_labels.tsv")
F_VERIFIED = os.path.join(HERE, "verified.tsv")
F_REVIEW = os.path.join(HERE, "review_queue.tsv")
CACHE = os.path.join(HERE, "cache")

WD_TOKEN = re.compile(r"^#?wd:(Q\d+)$")
GN_TOKEN = re.compile(r"^#?gn:(\d+)$")

# ID-Master の Category → 期待種別
CAT_KIND = {"Person": "P", "Location": "L", "Institution": "I", "Office": "O",
            "Text": "T", "Nisbah": "N", "Subject": "S"}

KIND_JA = {"P": "人物", "L": "地名", "LI": "地名/施設", "I": "施設・組織", "O": "職・称号",
           "T": "著作", "N": "ニスバ", "S": "分野・主題"}

# 期待種別ごとに「合っている」とみなす Wikidata 上位クラス(anchor 名は WD_ANCHORS のキー)
KIND_OK_CLASSES = {
    "P": {"human"},
    "L": {"place", "structure"},
    "LI": {"place", "structure", "org"},
    "I": {"structure", "org", "place"},
    "T": {"work"},
    "O": {"position", "group", "org"},
    "S": {"discipline", "belief", "work"},
    "N": None,  # ニスバは地名・集団・学派・人物由来など幅が広いので種別検査しない
}

# 近現代人物の閾値(マムルーク朝期の人物に付く wd としては明らかにおかしい)
MODERN_DEATH_YEAR = 1700
MODERN_BIRTH_YEAR = 1650
DEATH_YEAR_TOLERANCE = 5  # XML の没年(西暦)と P570 の差の許容幅

TSV_KW = dict(delimiter="\t", quoting=csv.QUOTE_MINIMAL, lineterminator="\n")


# ------------------------------------------------------------------ 文字列正規化
_AR_TR = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ى": "ي", "ة": "ه",
                        "ؤ": "و", "ئ": "ي", "ـ": ""})
_AR_DIA = re.compile(r"[ً-ٰٟ]")
_AR_STOP = {"ابن", "بن", "ابو", "ابي", "ابا", "ام", "بنت", "عبد", "الدين", "و", "في", "من"}


def norm_ar(s):
    if not s:
        return ""
    s = str(s).strip().translate(_AR_TR)
    s = _AR_DIA.sub("", s)
    return re.sub(r"\s+", " ", s)


def ar_tokens(s):
    out = set()
    for t in re.split(r"[\s\|\(\)\[\]،,؛:/\-]+", norm_ar(s)):
        if not t:
            continue
        if t.startswith("ال") and len(t) > 3:
            t = t[2:]
        if t in _AR_STOP or len(t) < 2:
            continue
        out.add(t)
    return out


def is_arabic(s):
    return bool(re.search(r"[؀-ۿ]", s or ""))


# ------------------------------------------------------------------ TSV 入出力
def read_tsv(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def write_tsv(path, rows, fields):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", **TSV_KW)
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in fields})
    os.replace(tmp, path)


def qnum(uri):
    m = re.search(r"(\d+)$", uri)
    return int(m.group(1)) if m else 0


def sort_uris(uris):
    return sorted(uris, key=lambda u: (0 if u.startswith("wd:") else 1, qnum(u)))


# ------------------------------------------------------------------ XML 位置 → 期待種別
def expected_kind(tag, attr, parent_tag, el_type):
    """precheck_aind_v12.expected_kind と同じ基準(+ person/@corresp, orgName)。"""
    if tag == "person" and attr == "corresp":
        return "P"
    if tag == "relation" and attr in ("active", "passive"):
        return "P"
    if tag == "persName":
        return "N" if el_type == "nisbah" else "P"
    if tag == "state":
        return "O"
    if tag == "placeName":
        if el_type == "burial" or parent_tag in ("death", "event"):
            return "LI"
        return "L"
    if tag == "bibl":
        return "T"
    if tag in ("affiliation", "orgName"):
        return "I"
    if tag == "desc":
        return "S"
    return None


def nearest_name(el):
    """参照の近傍にあるアラビア語名(precheck と同じ規則)。"""
    tag = el.tag
    if tag in ("persName", "placeName", "bibl", "orgName"):
        return (el.text or "").strip()
    if tag == "state":
        for lab in el.findall("label"):
            if lab.get("{http://www.w3.org/XML/1998/namespace}lang") == "ar":
                return (lab.text or "").strip()
    if tag == "relation":
        for d in el.findall("desc"):
            if d.get("type") is None:
                return (d.text or "").strip()
    if tag == "affiliation":
        for o in el.findall("orgName"):
            if o.get("{http://www.w3.org/XML/1998/namespace}lang") == "ar":
                return (o.text or "").strip()
    if tag == "person":
        for p in el.findall("persName"):
            if p.get("{http://www.w3.org/XML/1998/namespace}lang") == "ar" or is_arabic(p.text):
                return "".join(p.itertext()).strip()
    return ""


def uri_of(token):
    m = WD_TOKEN.match(token)
    if m:
        return "wd:" + m.group(1)
    m = GN_TOKEN.match(token)
    if m:
        return "gn:" + m.group(1)
    return None


# ------------------------------------------------------------------ 抽出
def _new_rec(uri):
    return {"uri": uri, "refs": 0, "files": set(), "positions": collections.Counter(),
            "kinds": collections.Counter(), "names": collections.Counter(),
            "idmaster": [], "idm_notes": [], "precheck": []}


def latest_idmaster():
    cands = glob.glob(os.path.join(REPO, "docs", "_work", "idmaster_ext_*.tsv"))
    return max(cands, key=os.path.getmtime) if cands else None


def load_precheck_module(path=None):
    path = path or os.path.join(REPO, "docs", "precheck_aind_v12.py")
    if not os.path.exists(path):
        return None
    # docs/__pycache__ は git 管理下にあるので、読み込みで .pyc を書き換えない
    old = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location("precheck_mod", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = old
    return mod


def extract_used(xml_dirs, idmaster_path, precheck_path=None):
    recs = {}

    def rec(uri):
        if uri not in recs:
            recs[uri] = _new_rec(uri)
        return recs[uri]

    # (1) XML
    nfiles = 0
    for d in xml_dirs:
        for fp in sorted(glob.glob(os.path.join(d, "**", "*.xml"), recursive=True)):
            try:
                root = ET.parse(fp).getroot()
            except ET.ParseError:
                continue
            nfiles += 1
            parent = {c: p for p in root.iter() for c in p}
            fname = os.path.basename(fp)
            for el in root.iter():
                for attr, val in el.attrib.items():
                    for tok in (val or "").split():
                        uri = uri_of(tok)
                        if not uri:
                            continue
                        r = rec(uri)
                        r["refs"] += 1
                        r["files"].add(fname)
                        ptag = parent[el].tag if el in parent else "-"
                        r["positions"][f"{el.tag}/@{attr}<{ptag}"] += 1
                        k = expected_kind(el.tag, attr, ptag, el.get("type"))
                        if k:
                            r["kinds"][k] += 1
                        nm = nearest_name(el)
                        if nm:
                            r["names"][nm] += 1

    # (2) ID-Master(E列=ID、F列=Note)
    if idmaster_path and os.path.exists(idmaster_path):
        with open(idmaster_path, encoding="utf-8") as f:
            for row in csv.reader(f, delimiter="\t"):
                if len(row) < 5:
                    continue
                cat, ar, lat, idv = (row[1] or "").strip(), (row[2] or "").strip(), \
                    (row[3] or "").strip(), (row[4] or "").strip()
                note = (row[5] if len(row) > 5 else "") or ""
                uri = None
                if re.fullmatch(r"Q\d+", idv):
                    uri = "wd:" + idv
                elif re.fullmatch(r"\d+", idv):
                    uri = "gn:" + idv
                elif uri_of(idv):
                    uri = uri_of(idv)
                if uri:
                    r = rec(uri)
                    r["idmaster"].append(f"{cat}|{ar}|{lat}")
                    if cat in CAT_KIND:
                        r["kinds"][CAT_KIND[cat]] += 1
                # Note 中に言及される wd/gn(旧番号・毒番号の記録など)
                for m in re.finditer(r"(?<![A-Za-z0-9])(?:wd:)?(Q\d{2,})(?![0-9])", note):
                    u = "wd:" + m.group(1)
                    if u != uri:
                        rec(u)["idm_notes"].append(f"{idv or '-'} {ar}")
                for m in re.finditer(r"gn[:：\s]?(\d{4,})", note):
                    u = "gn:" + m.group(1)
                    if u != uri:
                        rec(u)["idm_notes"].append(f"{idv or '-'} {ar}")

    # (3) precheck の拒否・許可リスト
    mod = load_precheck_module(precheck_path)
    if mod is not None:
        for name, tag in (("WD_GN_DENYLIST", "deny"), ("WD_PERSON_ONLY_DENY", "deny(人物位置)"),
                          ("WD_REDIRECT", "redirect"), ("WD_ALLOWLIST", "allow")):
            obj = getattr(mod, name, None) or {}
            items = obj.items() if isinstance(obj, dict) else ((k, "") for k in obj)
            for q, msg in items:
                if re.fullmatch(r"Q\d+", str(q)):
                    rec("wd:" + q)["precheck"].append(f"{tag}: {msg}".strip(": "))
        for g in getattr(mod, "GN_ALLOWLIST", set()) or set():
            rec("gn:" + str(g))["precheck"].append("allow")
        for word, g in getattr(mod, "GN_PAIR_DENY", []) or []:
            rec("gn:" + str(g))["precheck"].append(f"deny(「{word}」に対して)")
    return recs, nfiles


USED_FIELDS = ["uri", "xml_refs", "xml_files", "expected_kinds", "names_in_xml", "positions",
               "idmaster", "idmaster_note_mentions", "precheck", "sample_files"]


def used_rows(recs):
    rows = []
    for uri in sort_uris(recs):
        r = recs[uri]
        rows.append({
            "uri": uri,
            "xml_refs": r["refs"],
            "xml_files": len(r["files"]),
            "expected_kinds": " ".join(f"{k}:{n}" for k, n in r["kinds"].most_common()),
            "names_in_xml": " | ".join(n for n, _ in r["names"].most_common(6)),
            "positions": " ".join(f"{p}:{n}" for p, n in r["positions"].most_common(5)),
            "idmaster": " ;; ".join(r["idmaster"][:4]),
            "idmaster_note_mentions": " ;; ".join(r["idm_notes"][:4]),
            "precheck": " ;; ".join(r["precheck"]),
            "sample_files": " ".join(sorted(r["files"])[:5]),
        })
    return rows


# ------------------------------------------------------------------ 台帳の読み込みと評価
def parse_kinds(s):
    out = collections.Counter()
    for part in (s or "").split():
        if ":" in part:
            k, n = part.rsplit(":", 1)
            out[k] += int(n) if n.isdigit() else 1
    return out


def year_of(s):
    """'+1449-02-02' / '-0012' / '1449' / '1440s' などから整数年を取り出す。"""
    m = re.match(r"^([+-]?)(\d{1,4})", (s or "").strip())
    if not m:
        return None
    y = int(m.group(2))
    return -y if m.group(1) == "-" else y


class Authority:
    """台帳(wd_entities / gn_entities / used_uris / verified)をまとめて引く。"""

    def __init__(self, folder=HERE):
        self.folder = folder
        p = lambda n: os.path.join(folder, n)
        self.wd = {r["qid"]: r for r in read_tsv(p("wd_entities.tsv"))}
        self.gn = {r["gnid"]: r for r in read_tsv(p("gn_entities.tsv"))}
        self.used = {r["uri"]: r for r in read_tsv(p("used_uris.tsv"))}
        self.verified = {}
        for r in read_tsv(p("verified.tsv")):
            if r.get("uri"):
                self.verified[r["uri"].strip()] = r  # 後の行が優先(追記で上書きできる)

    def loaded(self):
        return bool(self.wd or self.gn)

    def verdict(self, uri):
        v = self.verified.get(uri)
        return (v.get("verdict") or "").strip() if v else ""

    def label(self, uri):
        if uri.startswith("wd:"):
            e = self.wd.get(uri[3:])
            if not e:
                return "(台帳未取得)"
            if e["status"] == "missing":
                return "(Wikidata に存在しない)"
            if e["status"] == "redirect":
                return f"(→ {e['redirect_to']} にリダイレクト)"
            parts = [e.get("label_ar"), e.get("label_en") or e.get("label_ja")]
            s = " / ".join(x for x in parts if x) or "(ラベルなし)"
            if e.get("desc_en"):
                s += f" — {e['desc_en']}"
            return s
        e = self.gn.get(uri[3:])
        if not e:
            return "(台帳未取得)"
        if e["status"] != "ok":
            return f"(GeoNames: {e['status']})"
        return " / ".join(x for x in (e.get("name_ar", "").split(" | ")[0], e.get("name"))
                          if x) + f" — {e.get('feature', '')} {e.get('country', '')}".rstrip()

    # -------------------------------------------------------------- 自動フラグ
    def assess(self, uri, kinds=None, names=None):
        """(重さ, 文言) のリスト。重さ: 毒 / 毒疑い / 要修正 / 要確認 / 参考"""
        kinds = kinds if kinds is not None else parse_kinds(self.used.get(uri, {}).get("expected_kinds"))
        if names is None:
            names = [n for n in (self.used.get(uri, {}).get("names_in_xml") or "").split(" | ") if n]
        out = []
        if uri.startswith("wd:"):
            e = self.wd.get(uri[3:])
            if not e:
                return [("要確認", "台帳未取得(update_authority.py を実行)")]
            if e["status"] == "missing":
                return [("毒", "Wikidata に存在しない(削除済みか誤番号)")]
            if e["status"] == "redirect":
                out.append(("要修正", f"{e['redirect_to']} へリダイレクト(統合済み)→ 付替え"))
            cls = set((e.get("classes") or "").split())
            if "taxon" in cls:
                out.append(("毒", f"生物分類群(P31: {e.get('p31')})"))
            by = year_of(e.get("birth"))
            dy = year_of(e.get("death"))
            if "human" in cls and ((dy and dy > MODERN_DEATH_YEAR) or (by and by > MODERN_BIRTH_YEAR)):
                out.append(("毒疑い", f"近現代の人物(生 {e.get('birth') or '?'} / 没 {e.get('death') or '?'})"))
            for k in kinds:
                ok = KIND_OK_CLASSES.get(k)
                if ok is None:
                    if k == "N" and "human" in cls:
                        out.append(("要確認", "ニスバ位置に人物の wd"))
                    continue
                if not cls:
                    if k in ("L", "LI", "I") and e.get("coord"):
                        continue
                    out.append(("要確認", f"{KIND_JA.get(k, k)}位置だが種別判定できず(P31: {e.get('p31') or 'なし'})"))
                elif not (cls & ok):
                    sev = "毒疑い" if (k == "P" or "human" in cls or cls & {"work", "taxon", "event"}) else "要確認"
                    out.append((sev, f"{KIND_JA.get(k, k)}位置だが {'/'.join(sorted(cls))}(P31: {e.get('p31')})"))
            if not (e.get("label_ar") or e.get("label_en") or e.get("label_ja")):
                out.append(("要確認", "ar/en/ja いずれのラベルもない"))
            if names and e.get("label_ar"):
                pool = ar_tokens(e.get("label_ar", "") + " " + e.get("aliases_ar", "").replace(" | ", " "))
                if pool and not any(ar_tokens(n) & pool for n in names if is_arabic(n)) \
                        and any(is_arabic(n) for n in names):
                    out.append(("参考", f"アラビア語ラベル「{e['label_ar']}」と記載名「{names[0]}」に共通語なし"))
        else:
            e = self.gn.get(uri[3:])
            if not e:
                return [("要確認", "台帳未取得(update_authority.py を実行)")]
            if e["status"] == "missing":
                return [("毒", "GeoNames に存在しない")]
            if e["status"] != "ok":
                return [("要確認", f"GeoNames 取得失敗: {e['status']}")]
            if names and e.get("name_ar"):
                pool = ar_tokens(e["name_ar"].replace(" | ", " "))
                if pool and not any(ar_tokens(n) & pool for n in names if is_arabic(n)) \
                        and any(is_arabic(n) for n in names):
                    out.append(("参考", f"アラビア語名「{e['name_ar'].split(' | ')[0]}」と記載名「{names[0]}」に共通語なし"))
            if not e.get("name_ar"):
                out.append(("参考", "GeoNames にアラビア語名なし"))
        return out

    def person_death_check(self, qid, xml_death_year):
        e = self.wd.get(qid)
        if not e or not xml_death_year:
            return None
        dy = year_of(e.get("death"))
        if dy is None:
            return None
        if abs(dy - xml_death_year) > DEATH_YEAR_TOLERANCE:
            return f"XML の没年 {xml_death_year} と Wikidata P570 {e.get('death')} が {abs(dy - xml_death_year)} 年ずれる"
        return None


SEV_ORDER = {"毒": 0, "毒疑い": 1, "要修正": 2, "要確認": 3, "参考": 4, "": 5}

REVIEW_FIELDS = ["priority", "uri", "verdict", "auto_flags", "label_ar", "label_en", "label_ja",
                 "description", "type", "life_or_coord", "names_in_xml", "expected_kinds",
                 "idmaster", "idmaster_note_mentions", "precheck", "xml_refs", "sample_files", "url"]


def build_review(auth):
    rows = []
    for uri in sort_uris(set(auth.used) | {"wd:" + q for q in auth.wd} | {"gn:" + g for g in auth.gn}):
        u = auth.used.get(uri, {})
        flags = auth.assess(uri)
        worst = min((SEV_ORDER[s] for s, _ in flags), default=5)
        r = {"uri": uri, "verdict": auth.verdict(uri),
             "auto_flags": " ／ ".join(f"[{s}] {m}" for s, m in flags),
             "names_in_xml": u.get("names_in_xml", ""), "expected_kinds": u.get("expected_kinds", ""),
             "idmaster": u.get("idmaster", ""), "idmaster_note_mentions": u.get("idmaster_note_mentions", ""),
             "precheck": u.get("precheck", ""), "xml_refs": u.get("xml_refs", "0"),
             "sample_files": u.get("sample_files", "")}
        if uri.startswith("wd:"):
            e = auth.wd.get(uri[3:], {})
            r.update(label_ar=e.get("label_ar", ""), label_en=e.get("label_en", ""), label_ja=e.get("label_ja", ""),
                     description=e.get("desc_en") or e.get("desc_ja") or e.get("desc_ar", ""),
                     type=e.get("p31", ""),
                     life_or_coord=(f"{e.get('birth', '')}–{e.get('death', '')}".strip("–")
                                    if (e.get("birth") or e.get("death")) else e.get("coord", "")),
                     url=f"https://www.wikidata.org/wiki/{uri[3:]}")
        else:
            e = auth.gn.get(uri[3:], {})
            r.update(label_ar=e.get("name_ar", ""), label_en=e.get("name", ""), label_ja=e.get("name_ja", ""),
                     description=f"{e.get('feature', '')} {e.get('country', '')}".strip(),
                     type=e.get("feature", ""), life_or_coord=f"{e.get('lat', '')},{e.get('lon', '')}".strip(","),
                     url=f"https://www.geonames.org/{uri[3:]}")
        # 並び: 未判定で重いもの → 未判定の残り → 判定済み
        verdict = r["verdict"]
        r["priority"] = (f"{worst}" if not verdict else "9")
        rows.append(r)
    rows.sort(key=lambda r: (r["priority"], -int(r["xml_refs"] or 0), qnum(r["uri"])))
    labels = {"0": "1 毒", "1": "2 毒疑い", "2": "3 要修正", "3": "4 要確認", "4": "5 参考", "5": "6 フラグなし", "9": "9 判定済み"}
    for r in rows:
        r["priority"] = labels[r["priority"]]
    return rows


def today():
    return datetime.date.today().isoformat()
