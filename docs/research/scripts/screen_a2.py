#!/usr/bin/env python3
"""Apply the Yarkovsky density upper bound to every SBDB NEO asteroid with A2 (SNR>=3).

rho_max = K * (1-A) / (D * |A2|), K = 3.1282e-8 (linear theory, sphere, F=0.2071, |cos gamma| = 1)
'generous' bound multiplies by 0.2455/0.2071 (finite-size max) * 1.3 (roughness/beaming allowance) and uses |A2| - 2 sigma.
Usage: screen_a2.py sbdb_ng_all.json nhats.json
"""
import json
import sys

K = 3.1282e-08
GEN = (0.2455 / 0.2071) * 1.3

sb = json.load(open(sys.argv[1]))
nh = json.load(open(sys.argv[2]))
nh_des = {d["des"]: d for d in nh["data"]}
F = sb["fields"]
rows = [dict(zip(F, r)) for r in sb["data"]]
rows = [r for r in rows if r["neo"] == "Y" and r["kind"].startswith("a") and r["A2"] is not None]


def dH(H, pv):
    return 1329e3 * 10 ** (-H / 5.0) / pv ** 0.5


res = []
for r in rows:
    a2 = abs(float(r["A2"])); s = float(r["A2_sigma"])
    if a2 / s < 3:
        continue
    H = float(r["H"])
    rec = dict(pdes=r["pdes"], name=r["full_name"].strip(), H=H, a2=float(r["A2"]), snr=a2 / s, nhats=r["pdes"] in nh_des,
               dv=float(nh_des[r["pdes"]]["min_dv"]["dv"]) if r["pdes"] in nh_des else None,
               a1=r["A1"], a3=r["A3"])
    a2lo = max(a2 - 2 * s, 1e-30)
    if r["diameter"] is not None:
        D = float(r["diameter"]) * 1000
        pv = float(r["albedo"]) if r["albedo"] is not None else 0.15
        rec["D_known"] = D
        rec["rmax_known"] = K * (1 - 0.39 * pv) / (D * a2)
        rec["rmax_known_gen"] = GEN * K * (1 - 0.39 * pv) / (D * a2lo)
    for pv in (0.05, 0.15, 0.30, 0.60):
        D = dH(H, pv)
        rec[f"rmax_{pv}"] = K * (1 - 0.39 * pv) / (D * a2)
        rec[f"rmaxgen_{pv}"] = GEN * K * (1 - 0.39 * pv) / (D * a2lo)
    res.append(rec)

print("NEO asteroids with A2 SNR>=3:", len(res), " of which NHATS:", sum(r["nhats"] for r in res))


def best(r):
    """most generous plausible bound: known D if available, else pV=0.60 (smallest D)"""
    return r.get("rmax_known_gen", r["rmaxgen_0.6"])


for thr in (300, 500, 1000, 2000, 3500, 5000):
    n = sum(1 for r in res if best(r) < thr)
    nn = sum(1 for r in res if best(r) < thr and r["nhats"])
    print(f"  generous rho_max < {thr}: {n} objects ({nn} NHATS)")
print("\n--- anomalous: generous rho_max < 1000 kg/m3 even at pV=0.6 or known D (cannot be Yarkovsky for plausible density) ---")
for r in sorted(res, key=best):
    if best(r) < 1000:
        print(f"  {r['name']:30s} H={r['H']:5.2f} A2={r['a2']:.2e} snr={r['snr']:6.1f} D_known={r.get('D_known')} rho_max_gen={best(r):7.0f} nominal(pV=.15)={r['rmax_0.15']:7.0f} NHATS={r['nhats']} dv={r['dv']} A1={r['a1']} A3={r['a3']}")

# metal exclusion statistics: nominal bound at plausible metal albedo 0.10-0.30
print("\n--- metal test: rho_max (nominal linear) at pV=0.15 / generous at pV=0.30 ---")
for lab, key in (("nominal pV=0.15", "rmax_0.15"), ("nominal pV=0.30", "rmax_0.3"), ("generous(2sig,+57%) pV=0.30", "rmaxgen_0.3")):
    n_all = sum(1 for r in res if r[key] < 4000)
    n_nh = sum(1 for r in res if r[key] < 4000 and r["nhats"])
    n_all2 = sum(1 for r in res if r[key] < 2500)
    n_nh2 = sum(1 for r in res if r[key] < 2500 and r["nhats"])
    print(f"  {lab}: rho_max<4000: {n_all} of {len(res)} ({n_nh} of {sum(r['nhats'] for r in res)} NHATS);  rho_max<2500: {n_all2} ({n_nh2} NHATS)")

print("\n--- NHATS objects with A2 SNR>=3, dv<7: bounds ---")
print("name | H | dv | A2 | snr | rho_max nominal at pV=0.05/0.15/0.30/0.60 | generous at pV=0.30")
for r in sorted([r for r in res if r["nhats"] and r["dv"] < 7.0], key=lambda r: r["dv"]):
    print(f"  {r['name']:28s} {r['H']:5.2f} {r['dv']:.2f} {r['a2']:.2e} {r['snr']:6.1f} | {r['rmax_0.05']:6.0f} {r['rmax_0.15']:6.0f} {r['rmax_0.3']:6.0f} {r['rmax_0.6']:6.0f} | {r['rmaxgen_0.3']:6.0f}")

import statistics
vals = [r["rmax_0.15"] for r in res]
print("\nmedian nominal rho_max at pV=0.15 over all detections:", round(statistics.median(vals)), " quartiles:", [round(x) for x in statistics.quantiles(vals, n=4)])
vals = [r["rmax_known"] for r in res if "rmax_known" in r]
print("with SBDB diameter (n=%d): median rho_max %d, quartiles %s" % (len(vals), statistics.median(vals), [round(x) for x in statistics.quantiles(vals, n=4)]))
