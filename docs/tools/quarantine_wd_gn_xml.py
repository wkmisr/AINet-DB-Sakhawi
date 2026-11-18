#!/usr/bin/env python3
"""quarantine_wd_gn_xml.py — 生成済み TEI-XML 下書きに v20.12 の wd/gn 検疫を後掛けする。

背景(2026-11-18): app.py v20.12(2026-10-26)以降、生成モデルが記憶から書いた
Wikidata Q-ID / GeoNames ID は生成時に検疫されて #NEEDID に戻る。しかし
XML_Barzakh には v20.10〜v20.11.1 で生成した下書きが残っており、校閲に回る
下書きには今も無関係な ID(例: ハナフィー派 = Q160851 Lomske)が出てくる。
本スクリプトは app.py の検疫ロジックと定数をそのまま読み込み(コピーしない)、
既存の XML に同じ判定をかける。作り直し(Gemini 再実行)は不要。

判定(app.py verify_and_quarantine_wd_gn_ids と同順):
  1   WD_GN_DENYLIST の Q-ID                     → #NEEDID
  1.5 docs/authority/verified.tsv で 毒/付替     → #NEEDID
  1.6 WD_TO_AIND_REDIRECT                         → #AIND-… ＋ corresp="wd:Q…"
  2   GN_PAIR_DENY(地名語×誤指し gn)            → #NEEDID
  3   ID-Master 登録済み                          → 維持(登録名と表記が違えば check として報告。
                                                    XML の名前は語形がずれやすいので差し戻さない)
  4   WD_ALLOWLIST / GN_ALLOWLIST / verified OK   → 維持
  4.5 校閲済み Individuals/ で使用済みの wd/gn    → 維持(repo 先例)
  5   それ以外(生成モデルの記憶由来)            → #NEEDID
  0   校閲ブリーフの「既知の毒wd」(KNOWN)は正しい ID に置き換え、本伝のある人物の wd は
      AIND＋corresp に(AIND_FIRST)。いずれも app.py 未収載分
  + 学派 affiliation は MADHHAB_DATA の正しい Q-ID に揃える(旧版の Q160851/Q191314 対策)

使い方:
  python3 docs/tools/quarantine_wd_gn_xml.py DIR_OR_FILES... [--idmaster ID-Master.csv] [--write] [--report out.tsv]
  既定は dry-run(報告のみ)。--write でファイルを書き換える(元ファイルは *.bak に退避)。
  --idmaster を省略すると app.py の ID_MASTER_URL から CSV を取得する。
"""
import argparse, ast, csv, io, os, re, sys, glob, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
APP = os.path.join(REPO, "app.py")

NAMES = {"WD_GN_DENYLIST", "WD_ALLOWLIST", "GN_ALLOWLIST", "GN_PAIR_DENY", "WD_TO_AIND_REDIRECT",
         "WD_GN_SUGGESTIONS", "_WD_ID_FORM_RE", "_GN_ID_FORM_RE", "_ARABIC_NORMALIZE_TR",
         "_ARABIC_DIACRITICS", "RETIRED_STATUSES", "MADHHAB_DATA", "ID_MASTER_URL"}
FUNCS = {"normalize_arabic", "is_retired_id_row", "_build_id_to_master_row", "_load_verified_authority"}


def load_app_logic():
    """app.py から必要な定数と関数だけを取り出して実行する(streamlit は読み込まない)。"""
    src = open(APP, encoding="utf-8").read()
    tree = ast.parse(src)
    keep = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in NAMES for t in node.targets):
            keep.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name in FUNCS:
            keep.append(node)
    ns = {"re": re, "_os": os, "_APP_DIR": REPO}
    exec(compile(ast.Module(body=keep, type_ignores=[]), APP, "exec"), ns)
    missing = (NAMES | FUNCS) - set(ns)
    if missing:
        sys.exit(f"app.py から読めなかった定義: {sorted(missing)}")
    return ns


def load_id_master(path, url):
    if path:
        text = open(path, encoding="utf-8").read()
    else:
        import urllib.request
        text = urllib.request.urlopen(url, timeout=30).read().decode("utf-8")
    rows = list(csv.reader(io.StringIO(text)))
    head = [h.strip() for h in rows[0]]
    return [dict(zip(head, (v.strip() for v in r))) for r in rows[1:] if any(v.strip() for v in r)]


# 校閲ブリーフ「既知の毒wd」と頻出確定 ID(D-3: 本伝のある人物は AIND＋corresp)から。
# app.py にはまだ入っていない分。値: (置き換え先, corresp を残すか)。
# None は文脈で正が変わるもの → #NEEDID ＋候補を報告。
KNOWN = {
    "Q160851": ("wd:Q228986", False),   # Lomske → Hanafi
    "Q191314": ("wd:Q233387", False),   # → Hanbali
    "Q35160": ("wd:Q428858", False), "Q589": ("wd:Q428858", False),  # المسجد الحرام
    "Q3824443": ("#AIND-D02830", False), "Q327129": ("#AIND-D02830", False),  # خشقدم
    "Q12247942": ("wd:Q108806953", False),  # التنبيه
    "Q381208": ("#AIND-D02168", False), "Q378194": ("#AIND-D02168", False),  # برسباي
    "Q375664": ("#AIND-D02178", False),  # برقوق
    "Q359300": ("#AIND-D06160", False), "Q374466": ("#AIND-D06160", False),  # الناصر فرج
    "Q4120093": ("#AIND-D09163", False),  # ابن الجزري(人物参照には使わない)
    "Q1164991": (None, "جامع القرويين なら wd:Q12204282"),
    "Q1283": (None, "بحر الهند なら wd:Q1239"),
    "Q3306083": (None, "الأشرفية قايتباي なら wd:Q138136028"),
}
# 本伝のある人物は AIND を ref にし、wd は corresp に回す(D-3 裁定・ブリーフ頻出確定 ID)
AIND_FIRST = {"Q257745": "#AIND-D09832", "Q6534585": "#AIND-D05895", "Q6798541": "#AIND-D05849",
              "Q12198099": "#AIND-D00207"}

ATTR_RE = re.compile(r'\b(ref|active|passive)="([^"]*)"')
TAG_RE = re.compile(r'<(placeName|orgName|persName|affiliation|relation|state|bibl|title|event|name|settlement|country|region)\b[^>]*>')


def arabic_name(xml, tag, start, end):
    """要素の名前(アラビア語)を推定する。relation/state は内側の desc/label(ar)。"""
    if tag in ("relation", "state", "event"):
        close = xml.find(f"</{tag}>", end)
        inner = xml[end:close if close != -1 else end]
        m = re.search(r'<(?:desc|label)\b(?![^>]*type=)[^>]*xml:lang="ar"[^>]*>([^<]*)<', inner) or \
            re.search(r'<(?:desc|label)\b[^>]*xml:lang="ar"[^>]*>([^<]*)<', inner)
        return m.group(1).strip() if m else ""
    m = re.match(r'([^<]*)<', xml[end:])
    return m.group(1).strip() if m else ""


def process(path, ns, idmap, ver_ok, ver_bad, repo_ids, write):
    xml = open(path, encoding="utf-8").read()
    out, pos, findings = [], 0, []
    madhhab = {k.split(" ")[0].lower().replace("'", ""): v for k, v in ns["MADHHAB_DATA"].items() if v}
    for tm in TAG_RE.finditer(xml):
        tag, tstart, tend = tm.group(1), tm.start(), tm.end()
        opentag = tm.group(0)
        if "wd:" not in opentag and "gn:" not in opentag:
            continue
        name = arabic_name(xml, tag, tstart, tend)
        new_open = opentag
        extra_corresp = None
        for am in ATTR_RE.finditer(opentag):
            attr, val = am.group(1), am.group(2)
            vals = val.split()
            changed = False
            for i, raw in enumerate(vals):
                mq = re.match(r"^wd:(Q\d+)$", raw); mg = re.match(r"^gn:(\d+)$", raw)
                if not mq and not mg:
                    continue
                key = mq.group(1) if mq else mg.group(1)
                verdict, reason, newv = "keep", "", raw
                # 学派 affiliation: ラベルから正しい Q-ID を当てる
                if tag == "affiliation" and 'type="madhhab"' in opentag and mq:
                    lab = re.match(r'([^<]*)<', xml[tend:]).group(1).strip().split(" ")[0].lower().replace("'", "").replace("ʿ", "")
                    good = madhhab.get(lab)
                    if good and good != key:
                        verdict, reason, newv = "fix", f"学派 {lab} の正しい Q-ID", f"wd:{good}"
                    elif good:
                        verdict = "keep"
                    findings.append((path, tag, attr, raw, newv, verdict, reason or "学派", lab))
                    if newv != raw:
                        vals[i] = newv; changed = True
                    continue
                nn = ns["normalize_arabic"](name)
                if mq and key in KNOWN:
                    tgt, extra = KNOWN[key]
                    if tgt:
                        verdict, reason, newv = "fix", "既知の毒wd(校閲ブリーフ)", tgt
                    else:
                        verdict, reason, newv = "quarantine", f"既知の毒wd(候補: {extra})", "#NEEDID"
                elif mq and key in AIND_FIRST and tag == "relation":
                    verdict, reason, newv = "redirect", "本伝のある人物は AIND 優先(D-3)", AIND_FIRST[key]
                    extra_corresp = raw
                elif mq and key in ns["WD_GN_DENYLIST"]:
                    verdict, reason, newv = "quarantine", "確定毒(WD_GN_DENYLIST)", "#NEEDID"
                    sug = ns["WD_GN_SUGGESTIONS"].get(key, "")
                    if sug: reason += f" 候補 {sug}"
                elif key in ver_bad:
                    verdict, reason, newv = "quarantine", f"典拠台帳で毒/付替({ver_bad[key]})", "#NEEDID"
                elif mq and key in ns["WD_TO_AIND_REDIRECT"]:
                    verdict, reason, newv = "redirect", "D-3 裁定(AIND 優先)", "#" + ns["WD_TO_AIND_REDIRECT"][key].lstrip("#")
                    extra_corresp = raw
                elif mg and any(key == bad and w in nn for w, bad in ns["GN_PAIR_DENY"]):
                    verdict, reason, newv = "quarantine", "gn 既知の誤指しペア", "#NEEDID"
                elif key in idmap:
                    row = idmap[key]
                    alts = row.get("ar_norms") or []
                    if row.get("retired"):
                        verdict, reason = "check", "ID-Master で retired(後継 ID を Note で確認)"
                    elif nn and alts and nn not in alts:
                        # XML の名前は語形・前置詞・文脈つきで登録名とずれやすいので、差し戻さず確認だけ求める
                        reason = f"ID-Master 登録(表記差あり: 登録 {row.get('ar_norm','')})"
                    else:
                        reason = "ID-Master 一致" if nn else "ID-Master 登録"
                elif (mq and key in ns["WD_ALLOWLIST"]) or (mg and key in ns["GN_ALLOWLIST"]) or key in ver_ok:
                    reason = "照合済みリスト"
                elif raw in repo_ids:
                    reason = "校閲済みレコード(Individuals/)で使用済み"
                else:
                    verdict, reason, newv = "quarantine", "未照合(生成モデルの記憶由来)", "#NEEDID"
                findings.append((path, tag, attr, raw, newv, verdict, reason, name))
                if newv != raw:
                    vals[i] = newv; changed = True
            if changed:
                new_open = new_open.replace(f'{attr}="{val}"', f'{attr}="{" ".join(vals)}"', 1)
        if extra_corresp and "corresp=" not in new_open:
            new_open = new_open[:-1].rstrip("/") + f' corresp="{extra_corresp}"' + ("/>" if new_open.endswith("/>") else ">")
        if new_open != opentag:
            out.append(xml[pos:tstart]); out.append(new_open); pos = tend
    out.append(xml[pos:])
    new = "".join(out)
    if write and new != xml:
        shutil.copy2(path, path + ".bak")
        open(path, "w", encoding="utf-8").write(new)
    return findings, new != xml


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--idmaster")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--report", default="quarantine_report.tsv")
    ap.add_argument("--all", action="store_true", help="維持した ID も報告に含める")
    a = ap.parse_args()
    ns = load_app_logic()
    records = load_id_master(a.idmaster, ns["ID_MASTER_URL"])
    idmap = ns["_build_id_to_master_row"](records)
    ver_ok, ver_bad = ns["_load_verified_authority"]()
    # 校閲・裁定を経た Individuals/ で使われている wd/gn は「照合済み」とみなす(repo 先例)
    repo_ids = set()
    for f in glob.glob(os.path.join(REPO, "Individuals", "**", "*.xml"), recursive=True):
        for v in re.findall(r'\b(?:ref|active|passive)="([^"]*)"', open(f, encoding="utf-8").read()):
            repo_ids.update(x for x in v.split() if re.match(r"^(?:wd:Q\d+|gn:\d+)$", x))
    repo_ids -= {f"wd:{k}" for k in list(ns["WD_GN_DENYLIST"]) + list(KNOWN)}
    files = []
    for p in a.paths:
        files += sorted(glob.glob(os.path.join(p, "**", "*.xml"), recursive=True)) if os.path.isdir(p) else [p]
    rows, nchanged = [], 0
    for f in files:
        fd, ch = process(f, ns, idmap, ver_ok, ver_bad, repo_ids, a.write)
        rows += fd; nchanged += ch
    with open(a.report, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["file", "element", "attr", "id", "new", "verdict", "reason", "name"])
        for r in rows:
            if a.all or r[5] != "keep":
                w.writerow(r)
    from collections import Counter
    c = Counter(r[5] for r in rows)
    print(f"files {len(files)} / wd・gn {len(rows)} / " + " ".join(f"{k} {v}" for k, v in sorted(c.items())) +
          f" / {'書き換え' if a.write else '書き換え予定'} {nchanged} ファイル / 報告 {a.report}")


if __name__ == "__main__":
    main()
