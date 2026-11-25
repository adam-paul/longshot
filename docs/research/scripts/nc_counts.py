#!/usr/bin/env python3
"""Independent recount of NHATS x SBDB non-grav parameters and of the candidate pools.

Usage: nc_counts.py <fresh sbdb_ng json> <nhats.json> <sbdb_neo.json (all NEOs, with data_arc)> [old sbdb_ng json]
Run with python3 -I.
"""
import json
import sys
from collections import Counter

ng_path, nhats_path, neo_path = sys.argv[1:4]
old_path = sys.argv[4] if len(sys.argv) > 4 else None


def load(p):
    d = json.load(open(p))
    return [dict(zip(d["fields"], r)) for r in d["data"]], d


def fl(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


ng, ngraw = load(ng_path)
nh = json.load(open(nhats_path))
neo, _ = load(neo_path)
nhd = {d["des"]: d for d in nh["data"]}
print("NHATS count field:", nh["count"], "unique des:", len(nhd))
print("fresh SBDB NG list count:", ngraw["count"], "rows:", len(ng))

# --- designation matching sanity: every NHATS des should be a pdes in the all-NEO snapshot
neo_by = {r["pdes"]: r for r in neo}
missing = [k for k in nhd if k not in neo_by]
print("NHATS des not found as pdes in all-NEO snapshot:", len(missing), missing[:10])

ng_by = {r["pdes"]: r for r in ng}
kinds = Counter(r["kind"] for r in ng)
print("kinds in fresh NG list:", dict(kinds))
neo_ast = [r for r in ng if r["neo"] == "Y" and r["kind"].startswith("a")]
print("NEO asteroids with any NG:", len(neo_ast),
      "| A1:", sum(r["A1"] is not None for r in neo_ast),
      "| A2:", sum(r["A2"] is not None for r in neo_ast),
      "| A3:", sum(r["A3"] is not None for r in neo_ast))


def snr(r, p):
    v, s = fl(r[p]), fl(r[p + "_sigma"])
    if v is None or not s:
        return None
    return abs(v) / s


a2 = [r for r in neo_ast if r["A2"] is not None]
print("NEO asteroid A2 S/N>=3:", sum(1 for r in a2 if (snr(r, "A2") or 0) >= 3),
      ">=5:", sum(1 for r in a2 if (snr(r, "A2") or 0) >= 5),
      ">=10:", sum(1 for r in a2 if (snr(r, "A2") or 0) >= 10),
      "no sigma:", sum(1 for r in a2 if snr(r, "A2") is None))

# --- claim 1
hits = {k: ng_by[k] for k in nhd if k in ng_by}
print("\n== CLAIM 1 ==")
print("NHATS objects with any fitted A1/A2/A3 in SBDB:", len(hits), "(claimed 174)")
for p, c in (("A1", 18), ("A2", 169), ("A3", 7)):
    print(f"  with {p}: {sum(1 for r in hits.values() if r[p] is not None)} (claimed {c})")
print("  kinds of the hits:", dict(Counter(r["kind"] for r in hits.values())))
for thr in (4, 5, 6, 8, 12.0001):
    tot = sum(1 for d in nhd.values() if float(d["min_dv"]["dv"]) < thr)
    w = sum(1 for k in hits if float(nhd[k]["min_dv"]["dv"]) < thr)
    print(f"  NHATS min dv < {thr:g}: {tot} objects, {w} with NG parameter")
lt5 = sorted((float(nhd[k]["min_dv"]["dv"]), k) for k in hits if float(nhd[k]["min_dv"]["dv"]) < 5)
print("  the dv<5 objects with NG:", [(k, dv, "+".join(p for p in ("A1", "A2", "A3") if hits[k][p] is not None)) for dv, k in lt5])
nh_a2 = [r for r in hits.values() if r["A2"] is not None]
s3 = [r for r in nh_a2 if (snr(r, "A2") or 0) >= 3]
print("  NHATS A2 with S/N >= 3:", len(s3), "(claimed 154);  S/N strictly > 3:", sum(1 for r in nh_a2 if (snr(r, 'A2') or 0) > 3))
edge = sorted((snr(r, "A2"), r["pdes"], r["A2"], r["A2_sigma"]) for r in nh_a2 if 2.5 <= (snr(r, "A2") or 0) <= 3.5)
print("  NHATS A2 objects with 2.5 <= S/N <= 3.5 (rounded catalogue values):")
for e in edge:
    print("     S/N=%.3f %s A2=%s sig=%s" % e)
nh_a1 = [r for r in hits.values() if r["A1"] is not None]
print("  NHATS A1 objects:", sorted(r["pdes"] for r in nh_a1))
print("  NHATS A1 with S/N>=3:", sum(1 for r in nh_a1 if (snr(r, 'A1') or 0) >= 3), [(r["pdes"], round(snr(r, "A1"), 2)) for r in nh_a1])
print("  NHATS A3 objects:", sorted(r["pdes"] for r in hits.values() if r["A3"] is not None))
print("  numbered/unnumbered among hits:", sum(1 for k in hits if k.isdigit()), sum(1 for k in hits if not k.isdigit()))

# --- consistency of the all-NEO snapshot with the NG list (A2 presence)
a2_all = {r["pdes"] for r in neo if r["A2"] is not None and r["kind"].startswith("a")}
a1_all = {r["pdes"] for r in neo if r["A1"] is not None and r["kind"].startswith("a")}
print("\nall-NEO snapshot: asteroids with A2:", len(a2_all), " with A1:", len(a1_all),
      "| fresh list NEO asteroids with A2:", len({r['pdes'] for r in a2}),
      "| symmetric difference:", sorted(a2_all ^ {r['pdes'] for r in a2})[:10])

# --- claim 5 pools
print("\n== CLAIM 5 ==")
nrows = [neo_by[k] for k in nhd if k in neo_by]
arc = lambda r: fl(r["data_arc"])
p1 = [r for r in nrows if arc(r) is not None and arc(r) > 1000]
print("NHATS with arc > 1000 d:", len(p1), "(claimed 814); without JPL A2:", sum(1 for r in p1 if r["A2"] is None), "(claimed 651)")
print("   arc >= 1000 d:", sum(1 for r in nrows if arc(r) is not None and arc(r) >= 1000))
print("   NHATS with no data_arc value:", sum(1 for r in nrows if arc(r) is None))
p2900 = [r for r in nrows if arc(r) is not None and arc(r) > 2900]
print("   arc > 2900 d:", len(p2900), "without A2:", sum(1 for r in p2900 if r["A2"] is None), "(claimed 549 / 399)")
p2 = [r for r in nrows if fl(r["H"]) is not None and fl(r["H"]) >= 27 and arc(r) is not None and arc(r) >= 60]
print("NHATS with H >= 27 and arc >= 60 d:", len(p2), "(claimed 74); without JPL A1:", sum(1 for r in p2 if r["A1"] is None), "(claimed 63)")
# same using the NHATS list's own H (1 decimal) instead of SBDB H
p2b = [r for r in nrows if fl(nhd[r["pdes"]]["h"]) is not None and fl(nhd[r["pdes"]]["h"]) >= 27 and arc(r) is not None and arc(r) >= 60]
print("   same with NHATS-list H:", len(p2b), "without A1:", sum(1 for r in p2b if r["A1"] is None))
lt5all = [r for r in nrows if float(nhd[r["pdes"]]["min_dv"]["dv"]) < 5]
p3 = [r for r in lt5all if fl(r["H"]) is not None and fl(r["H"]) >= 27 and arc(r) is not None and arc(r) >= 60]
print("NHATS dv<5:", len(lt5all), "; of these H>=27 & arc>=60 d:", len(p3), "(claimed 38 of 286); without JPL A1:", sum(1 for r in p3 if r["A1"] is None))
print("   dv<5 with arc>1000 d:", sum(1 for r in lt5all if arc(r) is not None and arc(r) > 1000), "(claimed 19)")
for hmin in (26, 27, 28):
    row = []
    pool = [r for r in nrows if fl(r["H"]) is not None and fl(r["H"]) >= hmin]
    for a in (30, 60, 100, 365):
        row.append(sum(1 for r in pool if arc(r) is not None and arc(r) >= a))
    a1n = sum(1 for r in pool if arc(r) is not None and arc(r) >= 100 and r["A1"] is not None)
    print(f"   H>={hmin}: n={len(pool)} arc>=30/60/100/365: {row}; of >=100 d with A1: {a1n}")
h27 = [r for r in nrows if fl(r["H"]) is not None and fl(r["H"]) >= 27]
print("   H>=27 with arc < 60 d: %d of %d = %.1f%%" % (sum(1 for r in h27 if arc(r) is None or arc(r) < 60), len(h27), 100 * sum(1 for r in h27 if arc(r) is None or arc(r) < 60) / len(h27)))
arcs = sorted(arc(r) for r in nrows if arc(r) is not None)
hs = sorted(fl(d["h"]) for d in nhd.values() if fl(d["h"]) is not None)
print("   NHATS median arc:", arcs[len(arcs) // 2], " median H (NHATS list):", hs[len(hs) // 2])

if old_path:
    old, _ = load(old_path)
    old_by = {r["pdes"]: r for r in old}
    print("\n== fresh vs earlier researcher's snapshot ==")
    print("only in fresh:", sorted(set(ng_by) - set(old_by))[:20], " only in old:", sorted(set(old_by) - set(ng_by))[:20])
    diff = [(k, p, old_by[k][p], ng_by[k][p]) for k in ng_by if k in old_by for p in ("A1", "A1_sigma", "A2", "A2_sigma", "A3", "A3_sigma") if old_by[k][p] != ng_by[k][p]]
    print("value differences:", len(diff), diff[:10])
