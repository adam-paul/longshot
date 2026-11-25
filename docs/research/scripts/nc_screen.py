#!/usr/bin/env python3
"""Recompute the density-bound screen (claim 2 counts), the dark-comet screen (claim 4d) and
per-object numbers for 2022 OB5 / 2020 GE / 1998 KY26 / 2000 WO107 (claims 3, 4), plus SRP numbers (claim 6).

Usage: nc_screen.py <fresh sbdb_ng json> <nhats.json>      (python3 -I)
"""
import json
import math
import statistics
import sys

K = 3.1282e-8          # au/d2 * m * kg/m3 ; linear large-body maximum, W = 0.2071
K1 = 2.2656e-7         # A1 = K1 * C_R * AMR[m2/kg]
Q = 0.39               # phase integral used to turn geometric into Bond albedo (as in the earlier script)


def fl(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def D_of(H, pv):
    return 1329e3 * 10 ** (-H / 5.0) / math.sqrt(pv)


def rho_max(D, a2, pv, k=K):
    return k * (1 - Q * pv) / (D * a2)


sb = json.load(open(sys.argv[1]))
nh = json.load(open(sys.argv[2]))
rows = [dict(zip(sb["fields"], r)) for r in sb["data"]]
nhd = {d["des"]: d for d in nh["data"]}
by = {r["pdes"]: r for r in rows}
neo_a2 = [r for r in rows if r["neo"] == "Y" and r["kind"].startswith("a") and r["A2"] is not None]
det = [r for r in neo_a2 if abs(fl(r["A2"])) / fl(r["A2_sigma"]) >= 3]
nh_det = [r for r in det if r["pdes"] in nhd]
print("NEO asteroids with A2 S/N>=3:", len(det), "| of which NHATS:", len(nh_det))

print("\n== CLAIM 2 counts: NHATS, A2 S/N >= 3 ==")


def count(rs, thr, pv, factor=1.0, nsig=0.0, use_known_D=False):
    n = 0
    for r in rs:
        a2 = abs(fl(r["A2"])) - nsig * fl(r["A2_sigma"])
        if a2 <= 0:
            continue
        D = D_of(fl(r["H"]), pv)
        p = pv
        if use_known_D and fl(r["diameter"]):
            D = fl(r["diameter"]) * 1000
            p = fl(r["albedo"]) or pv
        if factor * rho_max(D, a2, p) < thr:
            n += 1
    return n


print("  nominal, pV=0.15, rho_max < 4000:", count(nh_det, 4000, 0.15), "of", len(nh_det), "(claimed 118)")
print("  nominal, pV=0.30, rho_max < 4000:", count(nh_det, 4000, 0.30))
print("  nominal, pV=0.05, rho_max < 4000:", count(nh_det, 4000, 0.05))
for fac, lab in ((1.5, "x1.5"), ((0.2455 / 0.2071) * 1.3, "x1.541 (earlier script's GEN)")):
    print(f"  conservative {lab}, |A2|-2sigma, pV=0.30, rho_max < 4000:", count(nh_det, 4000, 0.30, fac, 2.0), "(claimed 11)")
print("  conservative x1.5, |A2|-2sigma, pV=0.30, SBDB diameter where present:", count(nh_det, 4000, 0.30, 1.5, 2.0, True))
print("  stricter: x2.37 (roughness x2 [Rozitis & Green 2012 upper end] x finite-size 1.185), |A2|-2sigma, pV=0.30:", count(nh_det, 4000, 0.30, 2.37, 2.0))
print("  stricter still: x2.37, |A2|-3sigma, pV=0.50:", count(nh_det, 4000, 0.50, 2.37, 3.0))
print("  non-linear smooth sphere (x0.929), nominal pV=0.15:", count(nh_det, 4000, 0.15, 0.929))
print("  all 573 detections: nominal pV=0.15 <4000:", count(det, 4000, 0.15), "| conservative x1.5:", count(det, 4000, 0.30, 1.5, 2.0), "| x1.541:", count(det, 4000, 0.30, 1.541, 2.0))
print("  NHATS: nominal pV=0.15 <2500:", count(nh_det, 2500, 0.15), "| conservative x1.541 <2500:", count(nh_det, 2500, 0.30, 1.541, 2.0))
vals = [rho_max(D_of(fl(r["H"]), 0.15), abs(fl(r["A2"])), 0.15) for r in det]
print("  median nominal rho_max (pV 0.15), all 573:", round(statistics.median(vals)), "quartiles", [round(x) for x in statistics.quantiles(vals, n=4)])
print("  the conservative (x1.5) survivors among NHATS:")
for r in sorted(nh_det, key=lambda r: float(nhd[r["pdes"]]["min_dv"]["dv"])):
    a2 = abs(fl(r["A2"])); s = fl(r["A2_sigma"]); H = fl(r["H"])
    g = 1.5 * rho_max(D_of(H, 0.30), a2 - 2 * s, 0.30)
    if g < 4000:
        g2 = 2.37 * rho_max(D_of(H, 0.30), a2 - 2 * s, 0.30)
        print(f"     {r['full_name'].strip():30s} H={H:5.2f} dv={nhd[r['pdes']]['min_dv']['dv']} A2={fl(r['A2']):+.2e} S/N={a2/s:5.1f} nominal(pV.15)={rho_max(D_of(H,0.15),a2,0.15):6.0f} conservative={g:6.0f} strict(x2.37)={g2:6.0f} A1={r['A1']} A3={r['A3']}")

print("\n== CLAIM 4d: crude dark-comet screen on all 573 (generous bound < 1000 / < 2000 at pV=0.6 or SBDB D) ==")
GEN = (0.2455 / 0.2071) * 1.3
res = []
for r in det:
    a2 = abs(fl(r["A2"])); s = fl(r["A2_sigma"]); H = fl(r["H"])
    a2lo = max(a2 - 2 * s, 1e-30)
    if fl(r["diameter"]):
        D = fl(r["diameter"]) * 1000; pv = fl(r["albedo"]) or 0.15
    else:
        D = D_of(H, 0.60); pv = 0.60
    res.append((GEN * rho_max(D, a2lo, pv), r, D))
for thr in (1000, 2000):
    sel = sorted([x for x in res if x[0] < thr], key=lambda x: x[0])
    print(f"  generous rho_max < {thr}: {len(sel)} objects")
    for g, r, D in sel:
        if thr == 2000 and g < 1000:
            continue
        print(f"     {r['full_name'].strip():30s} H={fl(r['H']):5.2f} D_used={D:8.1f} m A2={fl(r['A2']):+.2e} S/N={abs(fl(r['A2']))/fl(r['A2_sigma']):5.1f} gen_rho_max={g:6.0f} NHATS={'Y' if r['pdes'] in nhd else 'n'} orbit={r.get('orbit_id')} soln={str(r.get('soln_date'))[:10]} nobs={r['n_obs_used']} arc={r['data_arc']}")

print("\n== CLAIM 4a: 2022 OB5 ==")
a2, s = 1.657e-12, 6.493e-14
print("  S/N = %.2f" % (a2 / s))
print("  D[m]   pV(H=28.99)  rho_max nominal   at |A2|-2s   x1.5 & -2s   x2.37 & -2s   | A1 expected if rho=rho_max (C_R=1.2) | A1 if rho=2500 / 5000 / 7500")
for D in (3, 4, 5, 6, 8, 10, 12):
    pv = (1329e3 * 10 ** (-28.99 / 5) / D) ** 2
    rn = rho_max(D, a2, pv)
    r2 = rho_max(D, a2 - 2 * s, pv)
    print(f"  {D:4.0f}   {pv:5.3f}        {rn:7.0f}          {r2:7.0f}      {1.5*r2:7.0f}       {2.37*r2:7.0f}      | {K1*1.2*1.5/(rn*D):.2e}                         | " + " / ".join(f"{K1*1.2*1.5/(rho*D):.2e}" for rho in (2500, 5000, 7500)))
print("  efficiency needed relative to the linear maximum, eta = rho/rho_max (must be <= 1):")
for D in (3, 5, 8, 12):
    pv = (1329e3 * 10 ** (-28.99 / 5) / D) ** 2
    print(f"     D={D:2d} m: " + ", ".join(f"rho={rho}: eta={rho/rho_max(D, a2, pv):.2f}" for rho in (1200, 2500, 3300, 5000, 7500)))
print("  thermal inertia needed with P = 92.5 s at a = 1.026 au (large-body linear W(Theta)):")
Lsun, AU, SIG = 3.828e26, 1.495978707e11, 5.670374419e-8
for pv in (0.05, 0.15, 0.45):
    A = Q * pv
    S = Lsun / (4 * math.pi * (1.026 * AU) ** 2)
    Ts = ((1 - A) * S / (0.9 * SIG)) ** 0.25
    om = 2 * math.pi / 92.5
    row = []
    for G in (10, 15, 25, 50, 100, 200, 400, 1000, 2500):
        th = G * math.sqrt(om) / (0.9 * SIG * Ts ** 3)
        w = 0.5 * th / (1 + th + 0.5 * th * th)
        row.append(f"G={G}: {w/0.2071:.2f}")
    print(f"     pV={pv}: T*={Ts:.0f} K; W/Wmax: " + "; ".join(row))
print("  maximum Gamma that still gives eta (upper branch, Theta > sqrt2):")
for eta in (0.25, 0.35, 0.5, 0.7, 0.9):
    w = eta * 0.2071
    # 0.5 th = w (1 + th + 0.5 th^2) -> 0.5 w th^2 + (w - 0.5) th + w = 0
    a_, b_, c_ = 0.5 * w, w - 0.5, w
    th = (-b_ + math.sqrt(b_ * b_ - 4 * a_ * c_)) / (2 * a_)
    S = Lsun / (4 * math.pi * (1.026 * AU) ** 2)
    Ts = ((1 - 0.06) * S / (0.9 * SIG)) ** 0.25
    G = th * 0.9 * SIG * Ts ** 3 / math.sqrt(2 * math.pi / 92.5)
    print(f"     eta >= {eta}: Theta <= {th:.2f}  ->  Gamma <= {G:.0f} J m-2 K-1 s-1/2")
print("  NEOCC negative AMR -2.37e-4 m2/kg would mean A1 = %.2e au/d2 (sunward push)" % (K1 * -2.37e-4))
print("  spin: omega^2 R / g_self for R=2.5 m, rho=2500: %.0f" % (((2 * math.pi / 92.5) ** 2 * 2.5) / (4 / 3 * math.pi * 6.674e-11 * 2500 * 2.5)))

print("\n== CLAIM 4c: 2020 GE ==")
a1, s1, a2g, s2g, H = 1.7638e-10, 1.258e-11, 1.9398e-12, 2.184e-14, 28.17
print("  A1 S/N %.1f ; A2 S/N %.1f ; |A2|/A1 = %.4f (radiative limit 0.092(1-A)/C_R)" % (a1 / s1, a2g / s2g, a2g / a1))
for cr in (1.0, 1.2, 1.44):
    amr = a1 / (K1 * cr)
    print(f"  C_R={cr}: AMR = {amr:.3e} m2/kg; rho [kg/m3] at pV=0.05/0.15/0.30/0.50/0.70/0.90: " + " ".join(f"{1.5/(amr*D_of(H,pv)):5.0f}" for pv in (0.05, 0.15, 0.30, 0.50, 0.70, 0.90)) + "   (D = " + "/".join(f"{D_of(H,pv):.1f}" for pv in (0.05, 0.15, 0.30, 0.50, 0.70, 0.90)) + " m)")
amr = 8.23e-4
print("  NEOCC AMR 8.23e-4 m2/kg (as published): rho at pV=0.05..0.9: " + " ".join(f"{1.5/(amr*D_of(H,pv)):5.0f}" for pv in (0.05, 0.15, 0.30, 0.50, 0.70, 0.90)))
print("  with A1 - 2 sigma and H + 0.45 (smaller): rho at pV=0.5, C_R=1.2: %.0f" % (1.5 / (((a1 - 2 * s1) / (K1 * 1.2)) * D_of(H + 0.45, 0.5))))
print("  Yarkovsky bound from A2 (nominal): rho_max at pV=0.05/0.15/0.30/0.50: " + " ".join(f"{rho_max(D_of(H,pv), a2g, pv):5.0f}" for pv in (0.05, 0.15, 0.30, 0.50)))
print("  for comparison AMR of known artificial objects: 2020 SO ~ 1e-2 m2/kg; J002E3-type stages 6e-3..1e-2; so 2020 GE (6-8e-4) is ~10x lower")

print("\n== CLAIM 4b: 1998 KY26 ==")
print("  published A3 2.70e-11 +- 0.645e-11 -> S/N %.2f ; current JPL 1.686e-12 +- 1.121e-12 -> S/N %.2f ; ratio of values %.1f ; difference in units of the published sigma: %.1f" % (2.70e-11 / 6.45e-12, 1.686e-12 / 1.121e-12, 2.70e-11 / 1.686e-12, (2.70e-11 - 1.686e-12) / 6.45e-12))
a2k, s2k = 2.196e-13, 4.866e-14
for D, pv in ((11, 0.52), (9, 0.52), (13, 0.52), (30, 0.10)):
    print(f"  A2 bound at D={D} m, pV={pv}: rho_max = {rho_max(D, a2k, pv):.0f}; eta for rho=2800: {2800/rho_max(D, a2k, pv):.2f}")
print("  H=25.91 with pV=0.52 gives D = %.1f m" % D_of(25.91, 0.52))

print("\n== CLAIM 3: 2000 WO107 ==")
a2w, s2w, Dw, sDw, pvw = 1.5643e-14, 3.248e-15, 510.0, 83.0, 0.129
rn = rho_max(Dw, a2w, pvw)
print("  nominal rho_max = %.0f (Bond albedo %.3f); rho/rho_max = %.2f" % (rn, Q * pvw, 4800 / rn))
print("  with |A2| - 1s: %.0f ; - 2s: %.0f ; D - 1s: %.0f ; both -1s: %.0f" % (rho_max(Dw, a2w - s2w, pvw), rho_max(Dw, a2w - 2 * s2w, pvw), rho_max(Dw - sDw, a2w, pvw), rho_max(Dw - sDw, a2w - s2w, pvw)))
fr = math.sqrt((s2w / a2w) ** 2 + (sDw / Dw) ** 2)
print("  fractional error of rho_max from A2 and D: %.2f ; rho_max = %.0f +- %.0f ; density 4800 (+340/-630): excess = %.0f = %.2f sigma (combined with -630)" % (fr, rn, fr * rn, 4800 - rn, (4800 - rn) / math.sqrt((fr * rn) ** 2 + 630 ** 2)))
# volume-equivalent diameter of the Krugly et al. two-ellipsoid shape
v = math.pi / 6 * (0.68 * 0.38 * 0.36 + 0.44 * 0.42 * 0.16) * 1e9
dv = (6 * v / math.pi) ** (1 / 3)
print("  Krugly et al. lobes 0.68x0.38x0.36 km and 0.44x0.42x0.16 km: volume %.3e m3, volume-equivalent D = %.0f m ; mass at 4800 = %.2e kg" % (v, dv, 4800 * v))
print("  bound with volume-equivalent D: rho_max = %.0f ; rho/rho_max = %.2f" % (rho_max(dv, a2w, pvw), 4800 / rho_max(dv, a2w, pvw)))
# area-to-mass comparison: a flattened contact binary seen pole-on-ish vs sphere of same volume
print("  (a non-spherical body has more area per unit mass than the equal-volume sphere, so the sphere bound is not strict for it)")

print("\n== CLAIM 6: radiation pressure ==")
print("  K1 = L/(4 pi c) in au3/d2 per m2/kg = %.4e" % (3.828e26 / (4 * math.pi * 2.99792458e8) * 86400 ** 2 / 1.495978707e11 ** 3))
for cr in (1.0, 1.2):
    print(f"  D = 5 m sphere, C_R = {cr}: " + "; ".join(f"{lab} rho={rho}: AMR={1.5/(rho*5):.2e} m2/kg, A1={K1*cr*1.5/(rho*5):.2e}" for lab, rho in (("rubble", 1200), ("stony", 2500), ("iron", 7500))))
a = {rho: K1 * 1.2 * 1.5 / (rho * 5) for rho in (1200, 2500, 7500)}
print("  differences (C_R=1.2): rubble-stony %.2e ; stony-iron %.2e ; rubble-iron %.2e" % (a[1200] - a[2500], a[2500] - a[7500], a[1200] - a[7500]))
print("  sigma(A1) needed for a 3-sigma separation: rubble/stony %.1e ; stony/iron %.1e ; rubble/iron %.1e" % ((a[1200] - a[2500]) / 3, (a[2500] - a[7500]) / 3, (a[1200] - a[7500]) / 3))
print("  size degeneracy: A1 of 5 m stony = A1 of %.1f m rubble = A1 of %.2f m iron" % (5 * 2500 / 1200, 5 * 2500 / 7500))
print("  JPL formal sigma(A1) of existing fits [au/d2] (object, H, arc d, n_obs, sigma, S/N):")
for r in sorted([r for r in rows if r["A1"] is not None and r["kind"].startswith("a") and r["neo"] == "Y"], key=lambda r: fl(r["A1_sigma"])):
    print(f"     {r['full_name'].strip():28s} H={r['H']:>6s} arc={r['data_arc']:>6s} nobs={r['n_obs_used']:5d} radar={(r['n_del_obs_used'] or 0)+(r['n_dop_obs_used'] or 0):2d} A1={fl(r['A1']):+.2e} sigma={fl(r['A1_sigma']):.1e} S/N={abs(fl(r['A1']))/fl(r['A1_sigma']):5.1f} NHATS={'Y' if r['pdes'] in nhd else 'n'}")
