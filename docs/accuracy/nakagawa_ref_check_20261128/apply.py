#!/usr/bin/env python3
"""中川さんの転送点検（2026-11-28 返却）の反映。WK 裁定 2026-11-28。
corpus 3行の語と、persons_registry 3行（name_ar・target・note・history）を直す。一度だけ走らせる。"""
import csv, glob, io, sys

CORPUS = glob.glob("0__DawForAIND_renumbered_*.txt")[0]
REG = "authority/persons_registry.tsv"

# (AIND, corpus の旧, corpus の新)
CORPUS_FIXES = [
    ("AIND-D06843", "محمد بن أحمد بن محمد بن أيوب وإلياس .", "محمد بن أحمد بن محمد بن أيوب بن إلياس ."),
    ("AIND-D08688", "محمد بن محمد بن أحمد الملاوي .", "محمد بن محمد بن أحمد السلاوي ."),
    ("AIND-D09971", "بن علي الشيراز ي ويسمى", "بن علي الشيرازي ويسمى"),
]
H = "2026-11-28 WK 裁定（中川さんの転送点検の反映）: "
REG_FIXES = {
    "AIND-D06843": dict(name_ar="محمد بن أحمد بن محمد بن أيوب بن إلياس", target="AIND-D06908", note="",
        history=H + "name_ar・corpus「وإلياس」→「بن إلياس」（入力誤り、刊本 第7巻55頁）。転送先 AIND-D06908。旧 note「曽祖父がAyyūbとĪyāsで分岐しています。」は誤入力から生じた注なので外した"),
    "AIND-D08688": dict(name_ar="محمد بن محمد بن أحمد السلاوي", target="AIND-D08629",
        history=H + "name_ar・corpus「الملاوي」→「السلاوي」（入力誤り、刊本 第9巻52頁）。転送先 AIND-D08629"),
    "AIND-D09971": dict(name_ar="مغيث بن محمود بن علي الشيرازي",
        history=H + "name_ar を名前だけに（本文「ويسمى محمدا أيضا ممن」が入っていた。corpus「الشيراز ي」の空白も詰めた、刊本 第10巻166頁）。実項のまま（本人の項はここだけ）"),
}

lines = open(CORPUS, encoding="utf-8").read().split("\n")
for aid, old, new in CORPUS_FIXES:
    idx = [i for i, l in enumerate(lines) if l.startswith("###$" + aid + " ")]
    assert len(idx) == 1, aid
    i = idx[0]
    assert lines[i].count(old) == 1, (aid, lines[i])
    lines[i] = lines[i].replace(old, new)
open(CORPUS, "w", encoding="utf-8").write("\n".join(lines))

raw = open(REG, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in raw else "\n"
rows = raw.split(nl)
head = rows[0].split("\t")
seen = set()
for n, r in enumerate(rows):
    c = r.split("\t")
    if c[0] in REG_FIXES:
        d = dict(zip(head, c))
        for k, v in REG_FIXES[c[0]].items():
            d[k] = (d[k] + " " + v).strip() if k == "history" else v
        rows[n] = "\t".join(d[h] for h in head)
        seen.add(c[0])
assert seen == set(REG_FIXES), seen
open(REG, "w", encoding="utf-8", newline="").write(nl.join(rows))
print("ok")
