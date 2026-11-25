"""Statistician review: how many newly found H>25 NEAs are NHATS members (size of the survey forecast stream),
and exact binomial bands for proposed size/spin coverage bars. Read-only, stdlib only.
Usage: python3 -I rv_stat_stream.py <catalog_dir>
"""
import json, sys, math
from math import comb
cat = sys.argv[1]
nh = {o['des'] for o in json.load(open(cat + '/nhats.json'))['data']}
sb = json.load(open(cat + '/sbdb_neo.json'))
F = {f: i for i, f in enumerate(sb['fields'])}
def fl(x):
    try: return float(x)
    except Exception: return None
for yr in ('2024', '2025', '2026'):
    tot = inn = 0
    for r in sb['data']:
        if r[F['kind']] and r[F['kind']].startswith('c'):
            continue
        h = fl(r[F['H']]); fo = r[F['first_obs']]
        if h is None or fo is None or not fo.startswith(yr) or h <= 25:
            continue
        tot += 1
        inn += r[F['pdes']] in nh
    print(f"first observed {yr}, H>25: {tot} NEAs, {inn} in NHATS ({100*inn/max(tot,1):.0f}%)")
def cdf(k, n, p):
    return sum(comb(n, i) * p**i * (1-p)**(n-i) for i in range(0, k+1))
def band(n, p):
    lo = next(k for k in range(n+1) if cdf(k, n, p) > 0.025)
    hi = next(k for k in range(n+1) if cdf(k, n, p) >= 0.975)
    return lo, hi
for n in (197, 88, 20):
    print(f"n={n}: 68% interval should cover {band(n, 0.68)} of {n}; 95% interval should cover {band(n, 0.95)} of {n}")
# power of a coverage check: stated 95% interval that truly covers 80% / 70%
for n in (88, 20):
    lo, _ = band(n, 0.95)
    print(f"n={n}: P(flagged) if a stated 95% range truly covers 85/80/70%: " + ", ".join(f"{cdf(lo-1, n, q):.2f}" for q in (0.85, 0.80, 0.70)))
# two rival class priors on a new sample
for n in (50, 100, 200, 300):
    se = math.sqrt(0.5*0.5/n)
    print(f"n={n}: SE of an observed S/Q fraction = {se:.3f}; 35% vs 57% differ by {0.22/se:.1f} SE")
# bits <-> odds translation
def Hb(p): return -p*math.log2(p)-(1-p)*math.log2(1-p)
for p in (0.56, 0.60, 0.63, 0.68, 0.75):
    print(f"turning 50:50 into {int(p*100)}:{int(100-p*100)} on average = {1-Hb(p):.3f} bits")
