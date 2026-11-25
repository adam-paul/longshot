#!/usr/bin/env python3
"""Count SBDB objects with fitted non-grav parameters; cross-match with NHATS."""
import json
import sys
from collections import Counter

sbdb_path, nhats_path = sys.argv[1], sys.argv[2]
sb = json.load(open(sbdb_path))
nh = json.load(open(nhats_path))

F = sb["fields"]
rows = [dict(zip(F, r)) for r in sb["data"]]
print("SBDB signature:", sb.get("signature"))
print("total objects with any of A1/A2/A3:", len(rows), "count field:", sb.get("count"))

kinds = Counter(r["kind"] for r in rows)
print("by kind (all):", dict(kinds))


def is_ast(r):
    return r["kind"].startswith("a")


def is_com(r):
    return r["kind"].startswith("c")


for scope_name, scope in (("ALL", rows), ("NEO", [r for r in rows if r["neo"] == "Y"])):
    print(f"\n=== scope {scope_name}: n={len(scope)} ===")
    print(" asteroids:", sum(is_ast(r) for r in scope), " comets:", sum(is_com(r) for r in scope))
    for p in ("A1", "A2", "A3", "DT"):
        have = [r for r in scope if r[p] is not None]
        print(f" {p}: total={len(have)} asteroids={sum(is_ast(r) for r in have)} comets={sum(is_com(r) for r in have)}")
    # combos for asteroids
    c = Counter()
    for r in scope:
        if is_ast(r):
            key = "+".join(p for p in ("A1", "A2", "A3") if r[p] is not None)
            c[key] += 1
    print(" asteroid param combos:", dict(c))

neo_ast = [r for r in rows if r["neo"] == "Y" and is_ast(r)]
print("\nNEO asteroid classes:", dict(Counter(r["class"] for r in neo_ast)))

# significance of A2 for NEO asteroids
def snr(r, p):
    try:
        v = float(r[p]); s = float(r[p + "_sigma"])
        return abs(v) / s if s > 0 else None
    except (TypeError, ValueError):
        return None

a2 = [r for r in neo_ast if r["A2"] is not None]
snrs = [snr(r, "A2") for r in a2]
print("NEO asteroids with A2:", len(a2))
for thr in (1, 2, 3, 5, 10):
    print(f"  A2 SNR>={thr}:", sum(1 for s in snrs if s is not None and s >= thr))
print("  A2 with no sigma:", sum(1 for s in snrs if s is None))
print("  with diameter:", sum(1 for r in a2 if r["diameter"] is not None))
print("  with albedo:", sum(1 for r in a2 if r["albedo"] is not None))
print("  with spec_B or spec_T:", sum(1 for r in a2 if r["spec_B"] or r["spec_T"]))
print("  with rot_per:", sum(1 for r in a2 if r["rot_per"] is not None))
print("  with diameter AND rot_per:", sum(1 for r in a2 if r["rot_per"] is not None and r["diameter"] is not None))
# H distribution
hs = [float(r["H"]) for r in a2 if r["H"] is not None]
bins = [(0, 16), (16, 18), (18, 20), (20, 22), (22, 24), (24, 26), (26, 28), (28, 40)]
print("  H histogram:", {f"{lo}-{hi}": sum(1 for h in hs if lo <= h < hi) for lo, hi in bins})
print("  A2 sign: negative", sum(1 for r in a2 if float(r["A2"]) < 0), "positive", sum(1 for r in a2 if float(r["A2"]) > 0))
sig = [r for r in a2 if (snr(r, "A2") or 0) >= 3]
print("  A2 sign (SNR>=3): negative", sum(1 for r in sig if float(r["A2"]) < 0), "positive", sum(1 for r in sig if float(r["A2"]) > 0))

# A1 asteroid list
print("\n--- NEO asteroids with A1 ---")
for r in sorted([r for r in neo_ast if r["A1"] is not None], key=lambda r: float(r["H"] or 0)):
    print(f" {r['full_name'].strip():38s} H={r['H']} D={r['diameter']} A1={r['A1']}+-{r['A1_sigma']} (snr {snr(r,'A1') and round(snr(r,'A1'),1)}) A2={r['A2']}+-{r['A2_sigma']} A3={r['A3']}+-{r['A3_sigma']} arc={r['data_arc']}d nobs={r['n_obs_used']} U={r['condition_code']} cls={r['class']}")
print("\n--- NEO asteroids with A3 ---")
for r in sorted([r for r in neo_ast if r["A3"] is not None], key=lambda r: float(r["H"] or 0)):
    print(f" {r['full_name'].strip():38s} H={r['H']} D={r['diameter']} A1={r['A1']}+-{r['A1_sigma']} A2={r['A2']}+-{r['A2_sigma']} A3={r['A3']}+-{r['A3_sigma']} (snr {snr(r,'A3') and round(snr(r,'A3'),1)}) arc={r['data_arc']}d nobs={r['n_obs_used']} cls={r['class']}")

print("\n--- non-NEO asteroids with any NG param ---")
for r in [r for r in rows if r["neo"] != "Y" and is_ast(r)]:
    print(f" {r['full_name'].strip():38s} kind={r['kind']} cls={r['class']} H={r['H']} A1={r['A1']} A2={r['A2']} A3={r['A3']}")

# NHATS cross-match
nh_des = {d["des"]: d for d in nh["data"]}
print("\nNHATS count:", nh.get("count"), len(nh_des))
by_pdes = {r["pdes"]: r for r in rows}
hits = [(d, by_pdes[k]) for k, d in nh_des.items() if k in by_pdes]
print("NHATS objects with any NG param in SBDB:", len(hits))
for p in ("A1", "A2", "A3"):
    print(f"  NHATS with {p}:", sum(1 for d, r in hits if r[p] is not None))
print("  kinds:", dict(Counter(r["kind"] for d, r in hits)))
print("\n--- NHATS objects with fitted NG params (sorted by min dv) ---")
print("des | H | NHATS size range (m) | SBDB D (km) | min dv km/s (dur d) | A1+-sig | A2+-sig | A3+-sig | arc d | nobs | U | class")
for d, r in sorted(hits, key=lambda x: float(x[0]["min_dv"]["dv"])):
    def fmt(p):
        if r[p] is None:
            return "-"
        s = snr(r, p)
        return f"{r[p]}+-{r[p+'_sigma']} ({s:.1f}s)" if s else f"{r[p]}"
    print(f"{d['des']} | {d['h']} | {d['min_size']}-{d['max_size']} | {r['diameter']} | {d['min_dv']['dv']} ({d['min_dv']['dur']}) | {fmt('A1')} | {fmt('A2')} | {fmt('A3')} | {r['data_arc']} | {r['n_obs_used']} | {r['condition_code']} | {r['class']}")

# NHATS dv bins
dvs = [float(d["min_dv"]["dv"]) for d in nh_des.values()]
for thr in (4, 5, 6, 8, 12):
    print(f"NHATS min_dv<{thr}:", sum(1 for v in dvs if v < thr), " with NG:", sum(1 for d, r in hits if float(d["min_dv"]["dv"]) < thr))
