"""Referee checks: A1 listing, informative-object share, spin physics, trial counts, 2001 CQ36 bound.
Usage: python3 -I rv_misc.py <dir with nhats.json and sbdb_neo.json>"""
import json, math, sys
from math import erfc, sqrt
base = sys.argv[1]
s = json.load(open(base + "/sbdb_neo.json")); F = s["fields"]; idx = {f: i for i, f in enumerate(F)}
sb = {r[idx["pdes"]]: r for r in s["data"]}
nh = json.load(open(base + "/nhats.json"))["data"]
nhd = {o["des"]: o for o in nh}
def f(x):
    try: return float(x)
    except: return None
print("== asteroids with a JPL A1")
for r in s["data"]:
    a1 = f(r[idx["A1"]]); s1 = f(r[idx["A1_sigma"]])
    if a1 is None or not r[idx["kind"]].startswith("a"): continue
    d = r[idx["pdes"]]
    print("  %-11s H %-6s A1 %+.2e S/N %.1f  NHATS dv %s" % (d, r[idx["H"]], a1, abs(a1)/s1 if s1 else float("nan"), nhd[d]["min_dv"]["dv"] if d in nhd else "-"))
a2 = set(); a1s = set()
for o in nh:
    r = sb[o["des"]]
    A1 = f(r[idx["A1"]]); s1 = f(r[idx["A1_sigma"]]); A2 = f(r[idx["A2"]]); s2 = f(r[idx["A2_sigma"]])
    if A2 is not None and s2 and abs(A2)/s2 >= 3: a2.add(o["des"])
    if A1 is not None and s1 and abs(A1)/s1 >= 3: a1s.add(o["des"])
u = len(a2 | a1s)
print("== NHATS with a >=3 sigma JPL parameter:", u, "; plus ~21 new A1 limits:", u + 21, "= %.1f%% of %d" % (100*(u+21)/len(nh), len(nh)))
rows = [r for r in s["data"] if r[idx["kind"]].startswith("a") and f(r[idx["A2"]]) is not None and f(r[idx["A2_sigma"]])]
sn = lambda r: abs(f(r[idx["A2"]]))/f(r[idx["A2_sigma"]])
print("== NEA A2 >=3 sigma:", sum(1 for r in rows if sn(r) >= 3), "; producer Otto Matic:", sum(1 for r in rows if sn(r) >= 3 and r[idx["producer"]] == "Otto Matic"),
      "; with radar:", sum(1 for r in rows if sn(r) >= 3 and ((r[idx["n_del_obs_used"]] or 0) + (r[idx["n_dop_obs_used"]] or 0)) > 0))
G = 6.674e-11
print("== critical period (strengthless sphere):", {rho: round(math.sqrt(3*math.pi/(G*rho))/3600, 2) for rho in (1190, 2000, 2500, 3000)})
for name, R, Ph in (("R 10 m, P 10 min", 10, 10/60), ("R 30 m, P 21 min", 30, 0.35), ("R 4 m, P 92.5 s", 4, 92.5/3600)):
    w = 2*math.pi/(Ph*3600); rho = 2000
    print("  %s: centrifugal %.1e m/s2, %.0f x self-gravity, rho w^2 R^2 = %.0f Pa" % (name, w*w*R, w*w*R/(4/3*math.pi*G*rho*R), rho*w*w*R*R))
p3 = erfc(3/sqrt(2))
print("== chance 3-sigma results with calibrated errors: 888 objects A2 %.1f + A1 (one-sided) %.1f ; 10,500 objects A2 %.1f" % (888*p3, 888*p3/2, 10500*p3))
print("== 2001 CQ36 nominal density bound (A2 1.5e-13 au/d2):", {D: round(3.128e-8*(1-0.39*0.467*(56/D)**2)/(D*1.5e-13)) for D in (56, 68)})
