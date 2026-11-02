# h2g.py -- Hijri (tabular Islamic) -> CE conversion for AINet-DB.
#
# ★暦の規約（2026-09-18 Waka 裁定・§D-V4）: 本プロジェクトの西暦は
#   **グレゴリオ暦（proleptic Gregorian＝現在の暦）** で表記する。
#   本ツールは 2026-09-18 以前はユリウス暦を返していたが、同裁定により
#   proleptic Gregorian を返すよう改修した。検証パスが推したユリウス暦は
#   採用しない。ヒジュラ元期 AH 1-01-01 = 622-07-19 グレゴリオ暦
#   （= 622-07-16 ユリウス暦）。
# 併せて §D-V4 の閏年バグを修正: 年末・月末は「次の単位の初日 -1」
#   （jd(y+1,1,1)-1 / jd(y,m+1,1)-1）で求める。旧実装の jd(y,12,29) /
#   jd(y,m,29) は 355日年・30日月で1日早かった。
# 自己検証: python3 h2g.py --selftest
#
# 用法: python3 h2g.py 857-05-20 810 850-01 ...
#   YYYY        -> 年初 .. 年末
#   YYYY-MM     -> 月初 .. 月末
#   YYYY-MM-DD  -> その日（曜日つき）
import sys

def jd(y, m, d):
    """tabular Islamic (civil) -> JDN"""
    return (11*y+3)//30 + 354*y + 30*m - (m-1)//2 + d + 1948440 - 385

def g(J):
    """JDN -> proleptic Gregorian (Y, M, D). Fliegel-Van Flandern."""
    a = J + 32044
    b = (4*a+3)//146097
    c = a - 146097*b//4
    d = (4*c+3)//1461
    e = c - 1461*d//4
    m = (5*e+2)//153
    return (100*b + d - 4800 + m//10, m + 3 - 12*(m//10), e - (153*m+2)//5 + 1)

def year_end(y):
    return jd(y+1, 1, 1) - 1

def month_end(y, m):
    return jd(y+1, 1, 1) - 1 if m == 12 else jd(y, m+1, 1) - 1

W = ['月', '火', '水', '木', '金', '土', '日']

def fmt(J):
    Y, M, D = g(J)
    return f"{Y:04d}-{M:02d}-{D:02d}"

def selftest():
    cases = [
        ("AH 1-01-01",      jd(1, 1, 1),    "0622-07-19"),
        ("AH 857-05-20",    jd(857, 5, 20), "1453-06-07"),
        # 閏年(355日)の年末バグの回帰検査。旧実装 jd(809,12,29) は1日早く
        # 1407-06-15 を返していた。正は 1407-06-16 グレゴリオ暦
        # （= 1407-06-07 ユリウス暦、VERIFY_REPORT_B86 §D-V4 の指摘値）。
        ("AH 809 year end", year_end(809),  "1407-06-16"),
        ("AH 810-01-01",    jd(810, 1, 1),  "1407-06-17"),
        ("AH 850-01-01",    jd(850, 1, 1),  "1446-04-07"),
    ]
    ok = True
    for name, J, want in cases:
        got = fmt(J)
        ok &= (got == want)
        print(f"{'OK ' if got == want else 'NG '} {name:16s} JDN={J}  {got}  (expected {want})  [{W[J%7]}曜]")
    bad = [y for y in range(1, 1100) if year_end(y) + 1 != jd(y+1, 1, 1)]
    print(f"{'OK ' if not bad else 'NG '} year_end == jd(y+1,1,1)-1 for AH 1..1099")
    ok &= not bad
    print("SELFTEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "--selftest":
        sys.exit(selftest())
    for a in args:
        p = [int(x) for x in a.split('-')]
        y = p[0]
        m = p[1] if len(p) > 1 else 1
        d = p[2] if len(p) > 2 else 1
        J = jd(y, m, d)
        s = f"{a} -> {fmt(J)}"
        if len(p) > 2:
            s += f" ({W[J%7]}曜)"
        if len(p) == 1:
            s += f" .. {fmt(year_end(y))} (year end)"
        if len(p) == 2:
            s += f" .. {fmt(month_end(y, m))}"
        print(s)
