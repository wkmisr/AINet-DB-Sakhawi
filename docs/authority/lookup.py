#!/usr/bin/env python3
"""典拠台帳のローカル検索(ネット不要)。

    python3 docs/authority/lookup.py Q1283            # QID の中身と、こちらでの使われ方
    python3 docs/authority/lookup.py gn:360630
    python3 docs/authority/lookup.py القاهرة          # ar/en/ja ラベル・別名・XML 記載名から検索
    python3 docs/authority/lookup.py Cairo
    python3 docs/authority/lookup.py --flags          # 自動フラグ(毒・毒疑い・要修正)のある未判定分
    python3 docs/authority/lookup.py --flags --all    # 「要確認」「参考」も含める
"""
import argparse
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import authority_lib as A  # noqa: E402


def show(auth, uri):
    print(f"■ {uri}   {auth.label(uri)}")
    v = auth.verified.get(uri)
    if v:
        print(f"  判定: {v.get('verdict')}({v.get('checked_by', '')} {v.get('date', '')}) {v.get('note', '')}")
    else:
        print("  判定: 未判定(verified.tsv に行なし)")
    e = auth.wd.get(uri[3:]) if uri.startswith("wd:") else auth.gn.get(uri[3:])
    if e:
        keys = (["status", "redirect_to", "label_ar", "label_en", "label_ja", "aliases_ar", "aliases_en",
                 "desc_en", "desc_ar", "desc_ja", "p31", "classes", "birth", "death", "coord", "gn", "country",
                 "located_in", "arwiki", "enwiki", "fetched"] if uri.startswith("wd:") else
                ["status", "name", "name_ar", "name_ja", "alt_en", "feature", "country", "lat", "lon", "wd", "fetched"])
        for k in keys:
            if e.get(k):
                print(f"  {k:12s} {e[k]}")
    u = auth.used.get(uri)
    if u:
        print("  -- こちらでの使用 --")
        for k in ("xml_refs", "xml_files", "expected_kinds", "names_in_xml", "positions", "idmaster",
                  "idmaster_note_mentions", "precheck", "sample_files"):
            if u.get(k) and u.get(k) != "0":
                print(f"  {k:12s} {u[k]}")
    else:
        print("  (repo・ID-Master では未使用)")
    for sev, msg in auth.assess(uri):
        print(f"  [{sev}] {msg}")
    print()


def search(auth, q):
    nq = A.norm_ar(q).lower()
    hits = []
    for qid, e in auth.wd.items():
        hay = " ".join(e.get(k, "") for k in ("label_ar", "label_en", "label_ja", "aliases_ar", "aliases_en",
                                               "desc_en", "arwiki", "enwiki"))
        hay += " " + auth.used.get("wd:" + qid, {}).get("names_in_xml", "")
        if nq in A.norm_ar(hay).lower():
            hits.append("wd:" + qid)
    for gid, e in auth.gn.items():
        hay = " ".join(e.get(k, "") for k in ("name", "name_ar", "name_ja", "alt_en"))
        hay += " " + auth.used.get("gn:" + gid, {}).get("names_in_xml", "")
        if nq in A.norm_ar(hay).lower():
            hits.append("gn:" + gid)
    for uri, u in auth.used.items():
        if uri not in hits and nq in A.norm_ar(u.get("names_in_xml", "") + " " + u.get("idmaster", "")).lower():
            hits.append(uri)
    return A.sort_uris(set(hits))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query", nargs="*")
    ap.add_argument("--flags", action="store_true")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    auth = A.Authority()
    if not auth.loaded():
        print("台帳が空です。先に update_authority.py を実行してください。")
    if args.flags:
        keep = {"毒", "毒疑い", "要修正"} | ({"要確認", "参考"} if args.all else set())
        n = 0
        for uri in A.sort_uris(set(auth.used) | {"wd:" + q for q in auth.wd} | {"gn:" + g for g in auth.gn}):
            if auth.verdict(uri):
                continue
            fl = [(s, m) for s, m in auth.assess(uri) if s in keep]
            if fl:
                n += 1
                refs = auth.used.get(uri, {}).get("xml_refs", "0")
                print(f"{uri:12s} 参照{refs:>4s}  {auth.label(uri)}")
                for s, m in fl:
                    print(f"             [{s}] {m}")
        print(f"\n{n} 件")
        return
    for q in args.query:
        m = re.fullmatch(r"(?:wd:)?(Q\d+)", q)
        g = re.fullmatch(r"gn:(\d+)", q)
        if m:
            show(auth, "wd:" + m.group(1))
        elif g:
            show(auth, q)
        else:
            hits = search(auth, q)
            print(f"「{q}」: {len(hits)} 件")
            for h in hits[:40]:
                print(f"  {h:12s} {auth.label(h)}   [XML記載名: {auth.used.get(h, {}).get('names_in_xml', '')[:60]}]")
            print()


if __name__ == "__main__":
    main()
