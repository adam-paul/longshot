#!/usr/bin/env python3
"""Independent recount (claims 1 and 5) from the fresh local snapshots only.

Usage: python3 -I nc_counts2.py <sbdb_neo.json> <nhats.json>
"""
import json
import sys
from collections import Counter

neo_path, nhats_path = sys.argv[1:3]


def fl(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


d = json.load(open(neo_path))
neo = [dict(zip(d["fields"], r)) for r in d["data"]]
nh = json.load(open(nhats_path))
nhd = {x["des"]: x for x in nh["data"]}
print("SBDB NEO rows:", len(neo), "kinds:", dict(Counter(r["kind"] for r in neo)))
print("NHATS count field:", nh["count"], "unique des:", len(nhd))

neo_by = {r["pdes"]: r for r in neo}
assert len(neo_by) == len(neo)
missing = [k for k in nhd if k not in neo_by]
print("NHATS des not found as pdes in SBDB snapshot:", len(missing), missing[:20])


def has(r, p):
    return r[p] is not None


def snr(r, p):
    v, s = fl(r[p]), fl(r[p + "_sigma"])
    if v is None or not s:
        return None
    return abs(v) / s


ng = [r for r in neo if has(r, "A1") or has(r, "A2") or has(r, "A3")]
ast = [r for r in ng if r["kind"].startswith("a")]
com = [r for r in ng if r["kind"].startswith("c")]
print("\n== all NEOs with any A1/A2/A3 ==")
print("  total", len(ng), "asteroids", len(ast), "comets", len(com))
for p in ("A1", "A2", "A3"):
    print(f"  {p}: asteroids {sum(has(r, p) for r in ast)}, comets {sum(has(r, p) for r in com)}")
print("  DT:", sum(r["DT"] is not None for r in ng))
combos = Counter("+".join(p for p in ("A1", "A2", "A3") if has(r, p)) for r in ast)
print("  asteroid combos:", dict(combos))
a2 = [r for r in ast if has(r, "A2")]
nosig = [r["pdes"] for r in a2 if snr(r, "A2") is None]
print("  NEO asteroid A2:", len(a2), "S/N>=3:", sum((snr(r, "A2") or 0) >= 3 for r in a2), ">=5:", sum((snr(r, "A2") or 0) >= 5 for r in a2),
      ">=10:", sum((snr(r, "A2") or 0) >= 10 for r in a2), "| no sigma:", nosig)
print("  sign: negative", sum(fl(r["A2"]) < 0 for r in a2), "positive", sum(fl(r["A2"]) > 0 for r in a2))
a1 = [r for r in ast if has(r, "A1")]
print("  NEO asteroid A1:", len(a1), "S/N>=3:", sum((snr(r, "A1") or 0) >= 3 for r in a1))

print("\n== CLAIM 1: NHATS x non-grav ==")
nrows = [neo_by[k] for k in nhd if k in neo_by]
hits = [r for r in nrows if has(r, "A1") or has(r, "A2") or has(r, "A3")]
print("  NHATS with any NG parameter:", len(hits), "(claimed 174 of 7,226)")
for p, c in (("A1", 18), ("A2", 169), ("A3", 7)):
    print(f"   {p}: {sum(has(r, p) for r in hits)} (claimed {c})")
print("   kinds:", dict(Counter(r["kind"] for r in hits)))
dv = lambda r: float(nhd[r["pdes"]]["min_dv"]["dv"])
for thr in (4, 5, 6, 8, 99):
    print(f"   min dv < {thr}: {sum(dv(r) < thr for r in nrows)} objects, {sum(dv(r) < thr for r in hits)} with NG")
print("   dv<5 with NG:", [(r["pdes"], dv(r), "+".join(p for p in ("A1", "A2", "A3") if has(r, p))) for r in sorted(hits, key=dv) if dv(r) < 5])
nh_a2 = [r for r in hits if has(r, "A2")]
print("   NHATS A2 S/N>=3:", sum((snr(r, "A2") or 0) >= 3 for r in nh_a2), "(claimed 154); S/N>3 strictly:", sum((snr(r, "A2") or 0) > 3 for r in nh_a2),
      "; >=5:", sum((snr(r, "A2") or 0) >= 5 for r in nh_a2))
print("   NHATS A2 with 2.5<=S/N<=3.5:", sorted((round(snr(r, "A2"), 3), r["pdes"], r["A2"], r["A2_sigma"]) for r in nh_a2 if 2.5 <= (snr(r, "A2") or 0) <= 3.5))
print("   NHATS A2 S/N>=3 with dv<6:", sum((snr(r, "A2") or 0) >= 3 and dv(r) < 6 for r in nh_a2), "; with dv<5:", sum((snr(r, "A2") or 0) >= 3 and dv(r) < 5 for r in nh_a2))
nh_a1 = [r for r in hits if has(r, "A1")]
print("   NHATS A1 objects:", [(r["pdes"], round(snr(r, "A1") or 0, 1)) for r in sorted(nh_a1, key=dv)])
print("   NHATS A1 S/N>=3:", sum((snr(r, "A1") or 0) >= 3 for r in nh_a1))
print("   NHATS A3 objects:", [(r["pdes"], round(snr(r, "A3") or 0, 1)) for r in hits if has(r, "A3")])
print("   numbered / unnumbered:", sum(r["pdes"].isdigit() for r in hits), sum(not r["pdes"].isdigit() for r in hits))

print("\n== CLAIM 5: pools ==")
arc = lambda r: fl(r["data_arc"])
print("  NHATS rows matched:", len(nrows), "| no data_arc value:", sum(arc(r) is None for r in nrows))
p1 = [r for r in nrows if arc(r) is not None and arc(r) > 1000]
print("  arc > 1000 d:", len(p1), "(claimed 814); without A2:", sum(not has(r, "A2") for r in p1), "(claimed 651)")
print("    arc >= 1000 d:", sum(arc(r) is not None and arc(r) >= 1000 for r in nrows))
p29 = [r for r in nrows if arc(r) is not None and arc(r) > 2900]
print("    arc > 2900 d:", len(p29), "without A2:", sum(not has(r, "A2") for r in p29), "(claimed 549 / 399)")
print("    arc > 1000 d & dv<6:", sum(dv(r) < 6 for r in p1), "without A2:", sum(dv(r) < 6 and not has(r, "A2") for r in p1), "(claimed 52 / 35)")
H = lambda r: fl(r["H"])
p2 = [r for r in nrows if H(r) is not None and H(r) >= 27 and arc(r) is not None and arc(r) >= 60]
print("  H>=27 & arc>=60 d:", len(p2), "(claimed 74); without A1:", sum(not has(r, "A1") for r in p2), "(claimed 63)")
Hn = lambda r: fl(nhd[r["pdes"]]["h"])
p2b = [r for r in nrows if Hn(r) is not None and Hn(r) >= 27 and arc(r) is not None and arc(r) >= 60]
print("    same with NHATS-list H:", len(p2b), "without A1:", sum(not has(r, "A1") for r in p2b))
lt5 = [r for r in nrows if dv(r) < 5]
p3 = [r for r in lt5 if H(r) is not None and H(r) >= 27 and arc(r) is not None and arc(r) >= 60]
print("  dv<5:", len(lt5), "; H>=27 & arc>=60 d:", len(p3), "(claimed 38 of 286); without A1:", sum(not has(r, "A1") for r in p3))
print("    dv<5 & arc>1000 d:", sum(arc(r) is not None and arc(r) > 1000 for r in lt5), "; without A2:", sum(arc(r) is not None and arc(r) > 1000 and not has(r, "A2") for r in lt5))
print("    dv<6, H>=27, arc>=60:", sum(dv(r) < 6 for r in p2), "(claimed 53)")
print("    H>=26 & arc>=180:", sum(H(r) is not None and H(r) >= 26 and arc(r) is not None and arc(r) >= 180 for r in nrows), "(claimed 135)")
for hmin in (26, 27, 28):
    pool = [r for r in nrows if H(r) is not None and H(r) >= hmin]
    row = [sum(arc(r) is not None and arc(r) >= a for r in pool) for a in (30, 60, 100, 365)]
    a1n = sum(arc(r) is not None and arc(r) >= 100 and has(r, "A1") for r in pool)
    print(f"    H>={hmin}: n={len(pool)} arc>=30/60/100/365: {row}; of >=100 d with A1: {a1n}")
h27 = [r for r in nrows if H(r) is not None and H(r) >= 27]
short = sum(arc(r) is None or arc(r) < 60 for r in h27)
print("    H>=27 with arc<60 d: %d of %d = %.1f%%" % (short, len(h27), 100 * short / len(h27)))
arcs = sorted(arc(r) for r in nrows if arc(r) is not None)
hs = sorted(Hn(r) for r in nrows if Hn(r) is not None)
print("    NHATS median arc:", arcs[len(arcs) // 2], "d; median H:", hs[len(hs) // 2], "; no H in NHATS list:", sum(Hn(r) is None for r in nrows))
for a in (30, 90, 365):
    print(f"    arc <= {a} d: {100*sum(arc(r) is None or arc(r) <= a for r in nrows)/len(nrows):.1f}%")
print("  all NEO asteroids with arc>1000:", sum(r["kind"].startswith("a") and arc(r) is not None and arc(r) > 1000 for r in neo),
      "; arc>2900 without A2:", sum(r["kind"].startswith("a") and arc(r) is not None and arc(r) > 2900 and not has(r, "A2") for r in neo))
