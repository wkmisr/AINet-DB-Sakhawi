#!/usr/bin/env python3
"""AINet-DB で使っている Wikidata / GeoNames の URI を全件抽出し、両サイトから情報を取って
手元の台帳(TSV)に保存する。標準ライブラリのみ。Mac のターミナルで実行する。

    cd ~/Desktop/AINet-DB-Sakhawi
    python3 docs/authority/update_authority.py

主なオプション:
    --extract-only        ネットに出ず、使用中URIの一覧(used_uris.tsv)と要照合表だけ作り直す
    --extra-xml DIR       校閲前バッチなど Individuals 以外の XML も対象に含める(複数可)
    --idmaster TSV        ID-Master の TSV(省略時は docs/_work/idmaster_ext_*.tsv の最新)
    --max-age 30          取得から N 日以内のものは再取得しない(既定 30)
    --refresh-all         全件取り直す
    --gn-user NAME        GeoNames の無料アカウント名(あれば公式 API を使う。なくても動く)

出力(docs/authority/):
    used_uris.tsv         使用中URIと、XML・ID-Master での使われ方
    wd_entities.tsv       Wikidata の取得結果(ラベル ar/en/ja・別名・説明・P31・種別・生没年・座標・GeoNames ID)
    gn_entities.tsv       GeoNames の取得結果(名称・アラビア語名・地物種別・国・座標・対応 wd)
    wd_class_labels.tsv   P31 等に出てくるクラスの名前
    review_queue.tsv      照合用の一覧(自動フラグの重い順)。Numbers / Excel で開く
    cache/                取得した生データ(git 管理外)
"""
import argparse
import datetime
import json
import os
import shutil
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import authority_lib as A  # noqa: E402

UA = ("AINet-DB-authority/1.0 (https://github.com/wkmisr/AINet-DB-Sakhawi; "
      "academic prosopography of al-Sakhawi's al-Daw' al-Lami') python-urllib")
WD_API = "https://www.wikidata.org/w/api.php"
WD_SPARQL = "https://query.wikidata.org/sparql"
LANGS = ["ar", "en", "ja", "fr", "de"]

# 種別判定の上位クラス。(QID, 英語ラベルに含まれるはずの語)。
# 起動時に実ラベルと突き合わせ、合わないものは使わずに警告する(番号の記憶違い対策)。
WD_ANCHORS = {
    "human": [("Q5", "human")],
    "place": [("Q2221906", "geographic location"), ("Q17334923", "location"),
              ("Q486972", "human settlement"), ("Q618123", "geographical feature"),
              ("Q82794", "region"), ("Q56061", "administrative territorial entity")],
    "structure": [("Q811979", "structure"), ("Q41176", "building")],
    "org": [("Q43229", "organization")],
    "work": [("Q47461344", "written work"), ("Q7725634", "literary work"), ("Q17537576", "creative work")],
    "position": [("Q4164871", "position"), ("Q12737077", "occupation"), ("Q28640", "profession"),
                 ("Q216353", "title"), ("Q355567", "noble title")],
    "group": [("Q16334295", "group of humans"), ("Q41710", "ethnic group"), ("Q133311", "tribe")],
    "belief": [("Q9174", "religion"), ("Q13414953", "religious denomination")],
    "discipline": [("Q11862829", "academic discipline")],
    "taxon": [("Q16521", "taxon")],
    "event": [("Q1190554", "occurrence")],
}

WD_FIELDS = ["qid", "status", "redirect_to", "label_ar", "label_en", "label_ja", "aliases_ar", "aliases_en",
             "desc_en", "desc_ar", "desc_ja", "p31", "classes", "birth", "death", "coord", "gn",
             "country", "located_in", "arwiki", "enwiki", "fetched"]
GN_FIELDS = ["gnid", "status", "name", "name_ar", "name_ja", "alt_en", "feature", "country", "lat", "lon",
             "wd", "via", "fetched"]

_USE_CURL = False


# ------------------------------------------------------------------ HTTP
def _curl(url, body, accept):
    cmd = ["curl", "-sS", "--fail", "--max-time", "120", "-A", UA]
    if accept:
        cmd += ["-H", f"Accept: {accept}"]
    if body is not None:
        cmd += ["-H", "Content-Type: application/x-www-form-urlencoded", "--data-binary", "@-"]
    cmd.append(url)
    p = subprocess.run(cmd, input=body, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"curl 失敗({p.returncode}): {p.stderr.decode('utf-8', 'replace')[:200]}")
    return p.stdout.decode("utf-8")


def http(url, params=None, post=None, accept=None, tries=6):
    global _USE_CURL
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    body = urllib.parse.urlencode(post).encode() if post else None
    last = None
    for i in range(tries):
        try:
            if _USE_CURL:
                return _curl(url, body, accept)
            headers = {"User-Agent": UA}
            if accept:
                headers["Accept"] = accept
            req = urllib.request.Request(url, data=body, headers=headers)
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            last = e
            if e.code == 404:
                raise
            if e.code in (429, 500, 502, 503, 504):
                wait = int(e.headers.get("Retry-After") or 0) or 5 * (2 ** i)
                print(f"  … {e.code}、{wait} 秒待って再試行", flush=True)
                time.sleep(min(wait, 120))
                continue
            raise
        except urllib.error.URLError as e:
            last = e
            if isinstance(e.reason, ssl.SSLError) or "CERTIFICATE" in str(e).upper():
                if shutil.which("curl"):
                    print("  (Python の証明書設定が使えないため curl で取得します)", flush=True)
                    _USE_CURL = True
                    continue
            print(f"  … 接続エラー({e.reason})、{5 * (2 ** i)} 秒待って再試行", flush=True)
            time.sleep(5 * (2 ** i))
        except RuntimeError as e:  # curl
            last = e
            print(f"  … {e}、再試行", flush=True)
            time.sleep(5 * (2 ** i))
    raise RuntimeError(f"取得失敗: {url[:120]} — {last}")


def sparql(query):
    txt = http(WD_SPARQL, post={"query": query}, accept="application/sparql-results+json")
    return json.loads(txt)["results"]["bindings"]


def chunks(seq, n):
    seq = list(seq)
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


# ------------------------------------------------------------------ Wikidata
def _best_claims(ent, prop):
    cl = ent.get("claims", {}).get(prop, [])
    cl = [c for c in cl if c.get("rank") != "deprecated"]
    pref = [c for c in cl if c.get("rank") == "preferred"]
    return pref or cl


def _vals(ent, prop):
    out = []
    for c in _best_claims(ent, prop):
        sn = c.get("mainsnak", {})
        if sn.get("snaktype") != "value":
            continue
        out.append(sn.get("datavalue", {}).get("value"))
    return out


def _time(v):
    if not isinstance(v, dict) or "time" not in v:
        return ""
    t, prec = v["time"], v.get("precision", 9)
    sign = "-" if t.startswith("-") else ""
    y, m, d = t.lstrip("+-").split("T")[0].split("-")
    if prec >= 11:
        s = f"{sign}{y}-{m}-{d}"
    elif prec == 10:
        s = f"{sign}{y}-{m}"
    elif prec == 9:
        s = f"{sign}{y}"
    elif prec == 8:
        s = f"{sign}{y}(10年精度)"
    elif prec == 7:
        s = f"{sign}{y}(世紀精度)"
    else:
        s = f"{sign}{y}(粗)"
    if v.get("calendarmodel", "").endswith("Q1985786"):
        s += "J"  # ユリウス暦で記録
    return s.lstrip("0") if not sign else s


def _ids(ent, prop):
    return [v["id"] for v in _vals(ent, prop) if isinstance(v, dict) and "id" in v]


def parse_wd_entity(ent):
    lab = lambda k, l: (ent.get(k, {}).get(l) or {}).get("value", "")
    als = lambda l: " | ".join(a["value"] for a in ent.get("aliases", {}).get(l, []))
    coord = ""
    for v in _vals(ent, "P625"):
        if isinstance(v, dict) and "latitude" in v:
            coord = f"{v['latitude']:.5f},{v['longitude']:.5f}"
            break
    sl = ent.get("sitelinks", {})
    return {
        "qid": ent["id"], "status": "ok", "redirect_to": "",
        "label_ar": lab("labels", "ar"), "label_en": lab("labels", "en"), "label_ja": lab("labels", "ja"),
        "aliases_ar": als("ar"), "aliases_en": als("en"),
        "desc_en": lab("descriptions", "en"), "desc_ar": lab("descriptions", "ar"),
        "desc_ja": lab("descriptions", "ja"),
        "_p31": _ids(ent, "P31"), "_p279": _ids(ent, "P279"),
        "_country": _ids(ent, "P17"), "_located": _ids(ent, "P131"),
        "birth": next((_time(v) for v in _vals(ent, "P569") if _time(v)), ""),
        "death": next((_time(v) for v in _vals(ent, "P570") if _time(v)), ""),
        "coord": coord,
        "gn": " ".join(str(v) for v in _vals(ent, "P1566") if isinstance(v, str)),
        "arwiki": (sl.get("arwiki") or {}).get("title", ""),
        "enwiki": (sl.get("enwiki") or {}).get("title", ""),
    }


def wbgetentities(ids, props, languages=LANGS):
    for attempt in range(6):
        txt = http(WD_API, params={"action": "wbgetentities", "ids": "|".join(ids), "props": props,
                                   "languages": "|".join(languages), "format": "json"})
        data = json.loads(txt)
        if "error" in data:
            code = data["error"].get("code")
            if code == "maxlag":  # 読み取りでは maxlag を付けないので通常は来ない
                print(f"  … Wikidata 混雑、{15 * (attempt + 1)} 秒待って再試行", flush=True)
                time.sleep(15 * (attempt + 1))
                continue
            if code == "no-such-entity":
                # 1件でも存在しない ID があると全体が失敗する版がある → 1件ずつに分ける
                if len(ids) == 1:
                    return {ids[0]: {"id": ids[0], "missing": ""}}
                out = {}
                for one in ids:
                    out.update(wbgetentities([one], props, languages))
                return out
            raise RuntimeError(f"Wikidata API エラー: {data['error']}")
        return data.get("entities", {})
    raise RuntimeError("Wikidata API が混雑(maxlag)のため取得できませんでした")


def fetch_wd(qids, cache_dir):
    os.makedirs(cache_dir, exist_ok=True)
    rows = {}
    qids = list(qids)
    for n, batch in enumerate(chunks(qids, 50), 1):
        print(f"  Wikidata 本体 {min(n * 50, len(qids))}/{len(qids)}", flush=True)
        ents = wbgetentities(batch, "info|labels|aliases|descriptions|claims|sitelinks")
        seen = set()
        for key, ent in ents.items():
            if "missing" in ent:
                q = ent.get("id", key)
                rows[q] = {"qid": q, "status": "missing"}
                seen.add(q)
                continue
            red = ent.get("redirects")
            if red:
                rows[red["from"]] = {"qid": red["from"], "status": "redirect", "redirect_to": red["to"]}
                seen.add(red["from"])
            with open(os.path.join(cache_dir, ent["id"] + ".json"), "w", encoding="utf-8") as f:
                json.dump(ent, f, ensure_ascii=False)
            if ent["id"] in batch and ent["id"] not in seen:
                rows[ent["id"]] = parse_wd_entity(ent)
                seen.add(ent["id"])
        for q in batch:
            if q not in seen:
                rows[q] = {"qid": q, "status": "missing"}
        time.sleep(0.5)
    want = set(qids)
    return {k: v for k, v in rows.items() if k in want}


def check_anchors():
    """WD_ANCHORS の番号が意図したクラスかを実ラベルで確認し、合うものだけ返す。"""
    allq = [q for lst in WD_ANCHORS.values() for q, _ in lst]
    ents = wbgetentities(allq, "labels", ["en"])
    ok = {}
    for name, lst in WD_ANCHORS.items():
        for q, expect in lst:
            got = ((ents.get(q, {}).get("labels", {}).get("en")) or {}).get("value", "")
            if expect.lower() in got.lower():
                ok.setdefault(name, []).append(q)
            else:
                print(f"  ! 種別判定の基準 {q} のラベルが「{got}」で想定「{expect}」と違うため使いません", flush=True)
    return ok


def classify_wd(qids, anchors):
    """各 QID がどの上位クラス(human / place / work …)に属するかを SPARQL で判定。"""
    a2name = {q: name for name, lst in anchors.items() for q in lst}
    values_a = " ".join("wd:" + q for q in a2name)
    res = {q: set() for q in qids}
    qids = list(qids)
    for n, batch in enumerate(chunks(qids, 25), 1):
        print(f"  種別判定 {min(n * 25, len(qids))}/{len(qids)}", flush=True)
        q = ("SELECT DISTINCT ?item ?anchor WHERE { VALUES ?item { %s } VALUES ?anchor { %s } "
             "?item (wdt:P31|wdt:P279)/wdt:P279* ?anchor . }") % (" ".join("wd:" + x for x in batch), values_a)
        try:
            rows = sparql(q)
        except Exception as e:  # タイムアウト時は1件ずつ
            print(f"    (まとめて判定できず1件ずつに切替: {e})", flush=True)
            rows = []
            for one in batch:
                try:
                    rows += sparql(q.replace(" ".join("wd:" + x for x in batch), "wd:" + one))
                except Exception as e2:
                    print(f"    {one}: 判定失敗 {e2}", flush=True)
        for b in rows:
            item = b["item"]["value"].rsplit("/", 1)[-1]
            anc = b["anchor"]["value"].rsplit("/", 1)[-1]
            if item in res and anc in a2name:
                res[item].add(a2name[anc])
        time.sleep(1)
    return res


def fetch_labels(qids, known):
    need = [q for q in qids if q not in known]
    for batch in chunks(need, 50):
        ents = wbgetentities(batch, "labels", ["en", "ja", "ar"])
        for k, e in ents.items():
            labs = e.get("labels", {})
            known[e.get("id", k)] = {
                "qid": e.get("id", k),
                "label_en": (labs.get("en") or {}).get("value", ""),
                "label_ja": (labs.get("ja") or {}).get("value", ""),
                "label_ar": (labs.get("ar") or {}).get("value", "")}
        time.sleep(0.5)
    return known


# ------------------------------------------------------------------ GeoNames
def _local(tag):
    return tag.rsplit("}", 1)[-1]


def parse_gn_rdf(txt, gnid):
    root = ET.fromstring(txt)
    feat = None
    for el in root.iter():
        if _local(el.tag) == "Feature":
            feat = el
            break
    if feat is None:
        return {"gnid": gnid, "status": "missing"}
    out = {"gnid": gnid, "status": "ok", "via": "rdf"}
    ar, ja, en = [], [], []
    for el in feat:
        t, txtv = _local(el.tag), (el.text or "").strip()
        lang = el.get("{http://www.w3.org/XML/1998/namespace}lang", "")
        res = ""
        for k, v in el.attrib.items():
            if _local(k) == "resource":
                res = v
        if t == "name":
            out["name"] = txtv
        elif t in ("alternateName", "officialName", "shortName"):
            {"ar": ar, "ja": ja, "en": en}.get(lang, []).append(txtv)
        elif t == "featureCode":
            out["feature"] = res.rsplit("#", 1)[-1]
        elif t == "countryCode":
            out["country"] = txtv
        elif t == "lat":
            out["lat"] = txtv
        elif t == "long":
            out["lon"] = txtv
    out["name_ar"] = " | ".join(dict.fromkeys(ar))
    out["name_ja"] = " | ".join(dict.fromkeys(ja))
    out["alt_en"] = " | ".join(dict.fromkeys(en))
    return out


def parse_gn_json(d, gnid):
    if "status" in d and "geonameId" not in d:
        msg = d["status"].get("message", "")
        return {"gnid": gnid, "status": "missing" if "not" in msg.lower() else f"error:{msg[:60]}"}
    alts = d.get("alternateNames", [])
    pick = lambda l: " | ".join(dict.fromkeys(a["name"] for a in alts if a.get("lang") == l))
    return {"gnid": gnid, "status": "ok", "via": "api", "name": d.get("name") or d.get("toponymName", ""),
            "name_ar": pick("ar"), "name_ja": pick("ja"), "alt_en": pick("en"),
            "feature": f"{d.get('fcl', '')}.{d.get('fcode', '')}".strip("."),
            "country": d.get("countryCode", ""), "lat": d.get("lat", ""), "lon": d.get("lng", "")}


def fetch_gn(gnids, cache_dir, user=None):
    os.makedirs(cache_dir, exist_ok=True)
    rows = {}
    gnids = list(gnids)
    for i, g in enumerate(gnids, 1):
        if i % 10 == 0 or i == len(gnids):
            print(f"  GeoNames {i}/{len(gnids)}", flush=True)
        try:
            if user:
                txt = http("https://secure.geonames.org/getJSON",
                           params={"geonameId": g, "username": user, "style": "FULL"})
                with open(os.path.join(cache_dir, g + ".json"), "w", encoding="utf-8") as f:
                    f.write(txt)
                rows[g] = parse_gn_json(json.loads(txt), g)
            else:
                txt = http(f"https://sws.geonames.org/{g}/about.rdf")
                with open(os.path.join(cache_dir, g + ".rdf"), "w", encoding="utf-8") as f:
                    f.write(txt)
                rows[g] = parse_gn_rdf(txt, g)
        except urllib.error.HTTPError as e:
            rows[g] = {"gnid": g, "status": "missing" if e.code == 404 else f"error:{e.code}"}
        except Exception as e:
            rows[g] = {"gnid": g, "status": f"error:{str(e)[:60]}"}
        time.sleep(1.0 if not user else 0.3)
    return rows


def gn_to_wd(gnids):
    out = {}
    for batch in chunks(gnids, 100):
        q = 'SELECT ?gn ?item WHERE { VALUES ?gn { %s } ?item wdt:P1566 ?gn . }' % " ".join(f'"{g}"' for g in batch)
        try:
            for b in sparql(q):
                out.setdefault(b["gn"]["value"], []).append(b["item"]["value"].rsplit("/", 1)[-1])
        except Exception as e:
            print(f"  (GeoNames→Wikidata 対応の取得に失敗: {e})", flush=True)
        time.sleep(1)
    return out


# ------------------------------------------------------------------ main
def stale(row, max_age, refresh_all):
    if refresh_all or not row:
        return True
    if (row.get("status") or "").startswith("error"):
        return True
    try:
        d = datetime.date.fromisoformat(row.get("fetched", "")[:10])
    except ValueError:
        return True
    return (datetime.date.today() - d).days > max_age


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--xml-dir", action="append", default=None,
                    help="対象 XML フォルダ(既定: Individuals)")
    ap.add_argument("--extra-xml", action="append", default=[])
    ap.add_argument("--idmaster", default=None)
    ap.add_argument("--extract-only", action="store_true")
    ap.add_argument("--max-age", type=int, default=30)
    ap.add_argument("--refresh-all", action="store_true")
    ap.add_argument("--gn-user", default=os.environ.get("GEONAMES_USER"))
    ap.add_argument("--only", choices=["wd", "gn"], default=None)
    args = ap.parse_args()

    xml_dirs = (args.xml_dir or [os.path.join(A.REPO, "Individuals")]) + args.extra_xml
    idm = args.idmaster or A.latest_idmaster()
    print(f"[1/4] 使用中URIの抽出: XML={', '.join(os.path.relpath(d, A.REPO) for d in xml_dirs)} / "
          f"ID-Master={os.path.basename(idm) if idm else '(なし)'}", flush=True)
    recs, nfiles = A.extract_used(xml_dirs, idm)
    A.write_tsv(A.F_USED, A.used_rows(recs), A.USED_FIELDS)
    nwd = sum(1 for u in recs if u.startswith("wd:"))
    ngn = len(recs) - nwd
    print(f"      XML {nfiles} ファイル → wd {nwd} 件 / gn {ngn} 件 を used_uris.tsv に書き出し", flush=True)

    wd_rows = {r["qid"]: r for r in A.read_tsv(A.F_WD)}
    gn_rows = {r["gnid"]: r for r in A.read_tsv(A.F_GN)}
    cls_rows = {r["qid"]: r for r in A.read_tsv(A.F_CLASS_LABELS)}

    if not args.extract_only:
        today = A.today()
        if args.only in (None, "wd"):
            want = [u[3:] for u in A.sort_uris(recs) if u.startswith("wd:")]
            todo = [q for q in want if stale(wd_rows.get(q), args.max_age, args.refresh_all)]
            print(f"[2/4] Wikidata: 取得対象 {len(todo)} 件(うち既取得で新しいもの {len(want) - len(todo)} 件は省略)",
                  flush=True)
            # リダイレクト先(付替え先)も台帳に入れて中身を見られるようにする
            todo += sorted({r.get("redirect_to") for r in wd_rows.values() if r.get("redirect_to")}
                           - set(wd_rows) - set(todo))
            if todo:
                got = fetch_wd(todo, os.path.join(A.CACHE, "wd"))
                tgts = sorted({r.get("redirect_to") for r in got.values() if r.get("redirect_to")}
                              - set(got) - set(wd_rows))
                if tgts:
                    print(f"  リダイレクト先 {len(tgts)} 件も取得", flush=True)
                    got.update(fetch_wd(tgts, os.path.join(A.CACHE, "wd")))
                anchors = check_anchors()
                okq = [q for q, r in got.items() if r.get("status") == "ok"]
                classes = classify_wd(okq, anchors) if okq else {}
                ref_q = set()
                for r in got.values():
                    for k in ("_p31", "_country", "_located"):
                        ref_q.update(r.get(k, []))
                fetch_labels(sorted(ref_q), cls_rows)
                name = lambda q: (cls_rows.get(q, {}).get("label_en") or cls_rows.get(q, {}).get("label_ja")
                                  or cls_rows.get(q, {}).get("label_ar") or "")
                for q, r in got.items():
                    r["fetched"] = today
                    if r.get("status") == "ok":
                        r["p31"] = "; ".join(f"{x} {name(x)}".strip() for x in r.get("_p31", []))
                        r["classes"] = " ".join(sorted(classes.get(q, set())))
                        r["country"] = "; ".join(name(x) or x for x in r.get("_country", []))
                        r["located_in"] = "; ".join(f"{x} {name(x)}".strip() for x in r.get("_located", [])[:3])
                    wd_rows[q] = r
                A.write_tsv(A.F_CLASS_LABELS, [cls_rows[k] for k in sorted(cls_rows, key=A.qnum)],
                            ["qid", "label_en", "label_ja", "label_ar"])
        if args.only in (None, "gn"):
            want = [u[3:] for u in A.sort_uris(recs) if u.startswith("gn:")]
            todo = [g for g in want if stale(gn_rows.get(g), args.max_age, args.refresh_all)]
            print(f"[3/4] GeoNames: 取得対象 {len(todo)} 件"
                  f"({'API ' + args.gn_user if args.gn_user else 'アカウントなし=RDF'})", flush=True)
            if todo:
                got = fetch_gn(todo, os.path.join(A.CACHE, "gn"), args.gn_user)
                rev = gn_to_wd(todo)
                for g, r in got.items():
                    r["fetched"] = today
                    r["wd"] = " ".join(rev.get(g, []))
                    gn_rows[g] = r
        A.write_tsv(A.F_WD, [wd_rows[q] for q in sorted(wd_rows, key=A.qnum)], WD_FIELDS)
        A.write_tsv(A.F_GN, [gn_rows[g] for g in sorted(gn_rows, key=A.qnum)], GN_FIELDS)

    print("[4/4] 要照合表(review_queue.tsv)を作成", flush=True)
    auth = A.Authority()
    rows = A.build_review(auth)
    A.write_tsv(A.F_REVIEW, rows, A.REVIEW_FIELDS)
    tally = {}
    for r in rows:
        tally[r["priority"]] = tally.get(r["priority"], 0) + 1
    for k in sorted(tally):
        print(f"      {k}: {tally[k]} 件")
    bad = [r for r in wd_rows.values() if r.get("status") in ("missing", "redirect")]
    if bad:
        print(f"      Wikidata 上で存在しない/統合済み: {len(bad)} 件(review_queue.tsv の先頭)")
    print("完了。docs/authority/review_queue.tsv を開いて確認してください。")


class _Tee:
    """画面表示と同じ内容を update_log.txt にも書く(Claude が結果を読めるように)。"""
    def __init__(self, a, b):
        self.a, self.b = a, b

    def write(self, x):
        self.a.write(x)
        self.b.write(x)
        self.b.flush()

    def flush(self):
        self.a.flush()
        self.b.flush()


if __name__ == "__main__":
    import traceback
    _log = open(os.path.join(A.HERE, "update_log.txt"), "w", encoding="utf-8")
    _log.write(f"# {datetime.datetime.now().isoformat(timespec='seconds')} {' '.join(sys.argv)}\n"
               f"# python {sys.version.split()[0]} / {sys.executable}\n")
    sys.stdout = _Tee(sys.stdout, _log)
    try:
        main()
    except KeyboardInterrupt:
        print("\n中断しました。")
    except Exception:
        print("\n*** エラーで止まりました。以下を Claude に見せてください ***")
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)
