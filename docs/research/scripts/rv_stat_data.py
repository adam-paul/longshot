"""Statistician review: data-based checks (effective sample size of a size-weighted sealed set,
per-object spread of log-score differences in the pilot, sieve counts with unknown != fail).
Usage: python3 -I rv_stat_data.py <catalog_dir> <out_prior_null_dir>
Reads only; stdlib only.
"""
import csv
import json
import math
import random
import statistics as st
import sys

cat, pn = sys.argv[1], sys.argv[2]


def fl(x):
    try:
        return float(x)
    except Exception:
        return None


nh = json.load(open(cat + "/nhats.json"))["data"]
sb = json.load(open(cat + "/sbdb_neo.json"))
F = {f: i for i, f in enumerate(sb["fields"])}
SB = {r[F["pdes"]]: r for r in sb["data"]}

rows = []
for o in nh:
    r = SB.get(o["des"])
    rows.append(dict(des=o["des"], h=fl(o["h"]), dv=fl(o["min_dv"]["dv"]), occ=fl(o["occ"]),
                     rot=fl(r[F["rot_per"]]) if r else None,
                     arc=fl(r[F["data_arc"]]) if r else None,
                     obs_start=o.get("obs_start"), obs_mag=fl(o.get("obs_mag"))))
print("NHATS", len(rows), "median H", st.median([x["h"] for x in rows if x["h"] is not None]))

# ---------------------------------------------------------------- labelled set
lab = list(csv.DictReader(open(pn + "/labels.csv")))
for r in lab:
    r["Hf"] = fl(r["H"])
    r["af"] = fl(r["a"])
print("labelled rows", len(lab))

EDGES = [-99, 18, 20, 22, 23, 24, 25, 26, 27, 28, 99]


def hbin(h):
    for i in range(len(EDGES) - 1):
        if EDGES[i] <= h < EDGES[i + 1]:
            return i
    return None


def ess_report(name, subset, target):
    tb = [0] * (len(EDGES) - 1)
    for x in target:
        if x["h"] is not None:
            tb[hbin(x["h"])] += 1
    lb = [0] * (len(EDGES) - 1)
    for r in subset:
        if r["Hf"] is not None:
            lb[hbin(r["Hf"])] += 1
    nt, nl = sum(tb), sum(lb)
    print(f"\n-- {name}: labelled n={nl}; target n={nt}")
    print("   H bin        target share   labelled n   weight per object")
    w = []
    uncovered = 0.0
    for i in range(len(tb)):
        lo, hi = EDGES[i], EDGES[i + 1]
        if lb[i] == 0:
            uncovered += tb[i] / nt
            print(f"   [{lo:>4},{hi:>3})   {tb[i] / nt:10.3f}   {lb[i]:8d}   (no labelled objects)")
            continue
        wi = (tb[i] / nt) / (lb[i] / nl)
        w += [wi] * lb[i]
        print(f"   [{lo:>4},{hi:>3})   {tb[i] / nt:10.3f}   {lb[i]:8d}   {wi:8.2f}")
    ess = sum(w) ** 2 / sum(v * v for v in w)
    print(f"   Kish effective n of the WHOLE labelled set = {ess:.0f}  (target share with no labelled object: {uncovered:.3f})")
    for share in (0.2, 0.33, 0.5):
        print(f"     sealed share {share:.2f} -> effective n about {ess * share:.0f}")
    # capped weights
    for cap in (5, 10):
        wc = [min(v, cap) for v in w]
        print(f"     weights capped at {cap}: effective n {sum(wc) ** 2 / sum(v * v for v in wc):.0f} (whole set)")
    return ess


tax_all = [r for r in lab if r["tax4"]]
tax_a2 = [r for r in tax_all if r["af"] is not None and r["af"] < 2.0]
tax_spec_a2 = [r for r in tax_a2 if r["tax4_spec"] == "1"]
alb_a2 = [r for r in lab if r["alb"] and r["af"] is not None and r["af"] < 2.0]
print("\ntax4 labelled: all", len(tax_all), " a<2:", len(tax_a2), " spectral a<2:", len(tax_spec_a2), " albedo a<2:", len(alb_a2))
for nm, sub in (("four-class, all NEAs", tax_all), ("four-class, a<2 au", tax_a2), ("four-class spectra only, a<2 au", tax_spec_a2),
                ("albedo, a<2 au", alb_a2)):
    print(f"   {nm}: H>=22: {sum(1 for r in sub if r['Hf'] is not None and r['Hf'] >= 22)}, "
          f"H>=25: {sum(1 for r in sub if r['Hf'] is not None and r['Hf'] >= 25)}, "
          f"H>=26.2: {sum(1 for r in sub if r['Hf'] is not None and r['Hf'] >= 26.2)}, "
          f"H>=27: {sum(1 for r in sub if r['Hf'] is not None and r['Hf'] >= 27)}")

dv6 = [x for x in rows if x["dv"] < 6]
ess_report("four-class labels (all NEAs) weighted to ALL NHATS", tax_all, rows)
ess_report("four-class labels (a<2 au) weighted to ALL NHATS", tax_a2, rows)
ess_report("four-class labels (a<2 au) weighted to NHATS delta-v < 6", tax_a2, dv6)
ess_report("albedo labels (a<2 au) weighted to ALL NHATS", alb_a2, rows)

# ---------------------------------------------------------------- per-object spread of log-score differences
print("\n== per-object SD of (baseline - model) log loss in the pilot (bits) ==")
for fn, cols in (("dark.all.clear", ("ll_lr_orbH", "ll_gbt_orbH", "ll_lr_orb")),
                 ("dark.all.main", ("ll_lr_orbH", "ll_gbt_orb")),
                 ("dark.a2.main", ("ll_lr_orb", "ll_lr_H")),
                 ("tax4.all.main", ("ll_lr_orbH",)),
                 ("tax4.a2.main", ("ll_lr_H",))):
    try:
        L = list(csv.DictReader(open(f"{pn}/cv/{fn}.losses.csv")))
    except Exception as e:
        print(fn, "missing", e)
        continue
    for c in cols:
        for base in ("ll_freq", "ll_Hbin"):
            d = [float(r[base]) - float(r[c]) for r in L]
            m, s = st.mean(d), st.pstdev(d)
            print(f"   {fn:16s} {base:8s} - {c:12s}: n={len(d)} mean gain {m:+.3f}  per-object SD {s:.3f}  SE {s / math.sqrt(len(d)):.4f}")

# ---------------------------------------------------------------- where does the all-NEA skill come from
print("\n== all-NEA dark/bright skill split by semimajor axis (pilot per-object losses) ==")
A = {r["pdes"]: r["af"] for r in lab}
for fn in ("dark.all.clear", "dark.all.main"):
    L = list(csv.DictReader(open(f"{pn}/cv/{fn}.losses.csv")))
    for c, base in (("ll_lr_orbH", "ll_Hbin"), ("ll_lr_orb", "ll_freq"), ("ll_gbt_orb", "ll_freq")):
        ins = [float(r[base]) - float(r[c]) for r in L if A.get(r["pdes"]) is not None and A[r["pdes"]] < 2]
        out = [float(r[base]) - float(r[c]) for r in L if A.get(r["pdes"]) is not None and A[r["pdes"]] >= 2]
        print(f"   {fn} {base}-{c}: all {st.mean(ins + out):+.3f} (n={len(ins) + len(out)}); a<2 au {st.mean(ins):+.3f} (n={len(ins)}); a>=2 au {st.mean(out):+.3f} (n={len(out)})")

# ---------------------------------------------------------------- sieve
print("\n== sieve of plan section 1 (H<24; condition code <= occmax; SBDB rot_per; P>2.2 h) ==")
for occmax in (3, 4, 5):
    print(f" condition code <= {occmax}")
    for dvc in (5, 6, 7):
        A_ = [x for x in rows if x["dv"] < dvc]
        B = [x for x in A_ if x["h"] is not None and x["h"] < 24]
        C = [x for x in B if x["occ"] is not None and x["occ"] <= occmax]
        D = [x for x in C if x["rot"] is not None]
        E = [x for x in D if x["rot"] > 2.2]
        U = [x for x in C if x["rot"] is None]
        hs = sorted(x["h"] for x in U)
        print(f"   dv<{dvc}: all {len(A_)}  H<24 {len(B)}  orbit ok {len(C)}  period known {len(D)}  slow {len(E)}  | period UNKNOWN {len(U)}"
              f" (H range {hs[0] if hs else '-'}..{hs[-1] if hs else '-'})"
              f" -> expected extra slow at P(slow)=0.2..0.5: {0.2 * len(U):.1f}..{0.5 * len(U):.1f};"
              f" expected survivors {len(E) + 0.2 * len(U):.1f}..{len(E) + 0.5 * len(U):.1f}")

print("\n== 'Nothing under 5 km/s is brighter than H 24, so none is likely to exceed about 55 m' ==")


def diam(h, pv):
    return 1329e3 / math.sqrt(pv) * 10 ** (-h / 5)


u5 = [x for x in rows if x["dv"] < 5 and x["h"] is not None]
for lo, hi in ((24.0, 24.25), (24.25, 24.5), (24.5, 25.0), (25.0, 25.5), (25.5, 26.0)):
    n = sum(1 for x in u5 if lo <= x["h"] < hi)
    pvneed = (1329e3 * 10 ** (-((lo + hi) / 2) / 5) / 55.0) ** 2
    print(f"   H [{lo},{hi}): {n} objects under 5 km/s; exceeds 55 m if albedo < {pvneed:.3f} (mid-bin)")
n_24_2441 = sum(1 for x in u5 if x["h"] < 24.42)
print(f"   objects under 5 km/s with H < 24.42 (over 55 m whenever albedo < 0.10): {n_24_2441}")
# expected number over 55 m under a two-part albedo prior at fixed H:
# dark share d with pV log-uniform 0.03-0.10, bright share log-normal median 0.22 sigma 0.4 dex-ish (ln sigma 0.5)
random.seed(1)


def p_over(h, dark_share, thr=55.0, n=4000):
    c = 0
    for _ in range(n):
        if random.random() < dark_share:
            pv = math.exp(random.uniform(math.log(0.03), math.log(0.10)))
        else:
            pv = min(0.6, max(0.10, math.exp(random.gauss(math.log(0.22), 0.45))))
        if diam(h, pv) > thr:
            c += 1
    return c / n


for ds in (0.10, 0.15, 0.31):
    e = sum(p_over(x["h"], ds) for x in u5 if x["h"] < 26.5)
    e6 = sum(p_over(x["h"], ds) for x in rows if 5 <= x["dv"] < 6 and x["h"] is not None and 24 <= x["h"] < 26.5)
    print(f"   dark share {ds:.2f} at fixed H: expected number over 55 m among the 286 under 5 km/s = {e:.1f};"
          f" among H>=24 objects at 5-6 km/s = {e6:.1f}")

print("\n== dependence between gates through albedo: one object, H = 24.5 ==")
for pv, cls in ((0.05, "dark (C-like)"), (0.10, "boundary"), (0.20, "moderate (S-like)"), (0.30, "bright")):
    print(f"   albedo {pv:.2f} {cls:18s}: D = {diam(24.5, pv):.0f} m")
h = 24.5
random.seed(2)
N = 200000
big = stony = both = 0
for _ in range(N):
    dark = random.random() < 0.15
    if dark:
        pv = math.exp(random.uniform(math.log(0.03), math.log(0.10)))
    else:
        pv = min(0.6, max(0.10, math.exp(random.gauss(math.log(0.22), 0.45))))
    d = diam(h, pv)
    is_big = d > 55
    is_stony = (not dark)  # crude: bright = stony-like
    big += is_big
    stony += is_stony
    both += (is_big and is_stony)
print(f"   toy joint at H=24.5 (15% dark): P(D>55 m)={big / N:.3f}  P(bright)={stony / N:.3f}  product={big / N * stony / N:.3f}  joint P(D>55 m AND bright)={both / N:.4f}")
