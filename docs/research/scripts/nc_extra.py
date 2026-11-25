#!/usr/bin/env python3
"""Extra numbers for the verification report: sensitivity of the claim-2 counts, the four screen candidates,
2022 OB5 seasonal term for bare rock, and the claim-6 radiation-pressure table.
Usage: python3 -I nc_extra.py <sbdb_neo.json> <nhats.json> <path to nc_thermal.py>
"""
import importlib.util, json, math, sys
spec = importlib.util.spec_from_file_location("nct", sys.argv[3]); nct = importlib.util.module_from_spec(spec); spec.loader.exec_module(nct)
K, K1, Q = 3.1282e-8, 2.2656e-7, 0.39
d = json.load(open(sys.argv[1])); rows = [dict(zip(d["fields"], r)) for r in d["data"]]
nh = {x["des"]: x for x in json.load(open(sys.argv[2]))["data"]}
fl = lambda x: float(x) if x not in (None, "") else None
Dh = lambda H, pv: 1329e3 * 10 ** (-H / 5) / math.sqrt(pv)
det = [r for r in rows if r["kind"].startswith("a") and r["A2"] is not None and abs(fl(r["A2"])) / fl(r["A2_sigma"]) >= 3]
nhd = [r for r in det if r["pdes"] in nh]

def cnt(rs, fac, nsig, pv, thr=4000, bond=None, dH=0.0):
    n = 0
    for r in rs:
        a2 = abs(fl(r["A2"])) - nsig * fl(r["A2_sigma"])
        if a2 <= 0:
            continue
        A = Q * pv if bond is None else bond(pv)
        if fac * K * (1 - A) / (Dh(fl(r["H"]) + dH, pv) * a2) < thr:
            n += 1
    return n

print("== claim 2 sensitivity: number of the %d NHATS A2 detections (S/N>=3) with rho_max < 4000 ==" % len(nhd))
print("   factor  nsig  pV=0.15  pV=0.30  pV=0.50")
for fac in (0.93, 1.0, 1.185, 1.3, 1.5, 1.541, 1.6, 2.0, 2.37):
    for ns in (0, 2):
        print("   %5.3f   %d    %5d    %5d    %5d" % (fac, ns, cnt(nhd, fac, ns, 0.15), cnt(nhd, fac, ns, 0.30), cnt(nhd, fac, ns, 0.50)))
print("   nominal pV=0.15 with (1-A) taken as (1-pV) instead of (1-0.39 pV):", cnt(nhd, 1.0, 0, 0.15, bond=lambda p: p))
print("   nominal pV=0.15 with A=0:", cnt(nhd, 1.0, 0, 0.15, bond=lambda p: 0.0))
print("   nominal pV=0.15, H + 0.4 mag (smaller body):", cnt(nhd, 1.0, 0, 0.15, dH=0.4), "; H - 0.4:", cnt(nhd, 1.0, 0, 0.15, dH=-0.4))
print("   conservative x1.5, -2 sigma, pV=0.30, H + 0.4 mag:", cnt(nhd, 1.5, 2, 0.30, dH=0.4))
print("   threshold 5000 instead of 4000: nominal pV .15:", cnt(nhd, 1.0, 0, 0.15, 5000), " conservative x1.5:", cnt(nhd, 1.5, 2, 0.30, 5000))
print("   all NEO detections (%d): nominal pV .15 %d ; conservative x1.5 %d ; x1.541 %d" % (len(det), cnt(det, 1, 0, .15), cnt(det, 1.5, 2, .30), cnt(det, 1.541, 2, .30)))
with_D = [r for r in nhd if fl(r["diameter"])]
print("   NHATS detections with an SBDB diameter:", len(with_D), "; with albedo:", sum(1 for r in nhd if fl(r["albedo"])))

print("\n== claim 4d: the four flagged objects (SBDB snapshot values; H-based sizes) ==")
for pd in ("883607", "428209", "2011 CL50", "2003 LN6"):
    r = next(x for x in rows if x["pdes"] == pd)
    a2 = abs(fl(r["A2"])); s = fl(r["A2_sigma"]); H = fl(r["H"])
    out = []
    for pv in (0.05, 0.15, 0.30, 0.60):
        Dm = Dh(H, pv)
        out.append("pV %.2f: D=%.0f m nominal %.0f, x1.5&-2s %.0f" % (pv, Dm, K * (1 - Q * pv) / (Dm * a2), 1.5 * K * (1 - Q * pv) / (Dm * (a2 - 2 * s))))
    print("  %-22s H=%.2f a=%s e=%s i=%s q=%s T_J=%s A2=%s+-%s S/N=%.1f nobs=%s arc=%s d NHATS=%s" % (r["full_name"].strip(), H, r["a"], r["e"], r["i"], r["q"], r["t_jup"], r["A2"], r["A2_sigma"], a2 / s, r["n_obs_used"], r["data_arc"], pd in nh))
    print("      " + " | ".join(out))

print("\n== 2022 OB5: seasonal term for bare rock (exact finite-size linear solution) ==")
SIG = 5.670374419e-8
a_au, per_d = 1.0262, 379.70
nn = 2 * math.pi / (per_d * 86400)
Ts = ((1 - 0.06) * 1361.2 / a_au ** 2 / (0.9 * SIG)) ** 0.25
for lab, Kc, rhoC in (("porous rock K=0.1", 0.1, 2000 * 750), ("solid rock K=2.5", 2.5, 2800 * 800), ("iron K=40", 40.0, 7800 * 450)):
    gam = math.sqrt(Kc * rhoC)
    l_n = math.sqrt(Kc / (rhoC * nn))
    th_n = gam * math.sqrt(nn) / (0.9 * SIG * Ts ** 3)
    om = 2 * math.pi / 92.5
    th_d = gam * math.sqrt(om) / (0.9 * SIG * Ts ** 3)
    wd = nct.W_large(th_d)
    row = []
    for Dm in (3, 5, 8, 12):
        ws = nct.W_sphere(Dm / 2 / l_n, th_n)
        # eta = max over obliquity of (2 Wd c + Ws (1-c^2)) / (2*0.20711)
        best = max((2 * wd * c + ws * (1 - c * c)) / (2 * 0.20711) for c in [i / 1000 for i in range(1001)])
        row.append("D=%d m: W_s=%.3f eta_max=%.3f" % (Dm, ws, best))
    print("  %-18s Gamma=%5.0f l_n=%.2f m Theta_n=%.3f Theta_d=%.1f W_d/Wmax=%.3f | %s" % (lab, gam, l_n, th_n, th_d, wd / 0.20711, "; ".join(row)))
print("  required eta = rho D |A2| / (3.128e-8 (1-A)):")
for Dm in (3, 5, 8, 12):
    pv = (1329e3 * 10 ** (-28.99 / 5) / Dm) ** 2
    print("     D=%2d m (pV=%.3f): " % (Dm, pv) + ", ".join("rho=%d: %.2f" % (rho, rho * Dm * 1.657e-12 / (K * (1 - Q * pv))) for rho in (1200, 2000, 2500, 3300, 5000, 7500)))

print("\n== claim 6: A1 [au/d2] = 2.2656e-7 C_R * 1.5/(rho D) ==")
for cr in (1.0, 1.2):
    for Dm in (5, 10):
        print("  C_R=%.1f D=%2d m: " % (cr, Dm) + "; ".join("%s %d: AMR=%.2e A1=%.2e" % (lab, rho, 1.5 / (rho * Dm), K1 * cr * 1.5 / (rho * Dm)) for lab, rho in (("iron", 7500), ("stone", 3300), ("stone", 2500), ("rubble", 2000), ("rubble", 1200))))
print("  class ratios in A1 at fixed D: rubble/stone %.2f-%.2f ; stone/iron %.2f-%.2f ; rubble/iron %.2f-%.2f" % (2500 / 2000, 3300 / 1200, 7500 / 3300, 7500 / 2500, 7500 / 2000, 7500 / 1200))
print("  at fixed H, A1 scales as sqrt(pV)/rho: " + "; ".join("%s (pV %.2f, rho %d): %.3f" % (l, p, r, math.sqrt(p) / r * 1000) for l, p, r in (("dark rubble", 0.05, 1600), ("C rubble dense", 0.05, 2000), ("S rubble", 0.22, 1600), ("S monolith", 0.22, 2900), ("E-type stone", 0.50, 2900), ("metal", 0.15, 7500))))
for sl, lab in ((math.log(2) / 2, "factor 2 = 2-sigma range (sigma_lnD=0.35)"), (math.log(2), "factor 2 = 1 sigma (sigma_lnD=0.69)"), (0.10, "measured size, 10%")):
    out = []
    for nm, r1, r2 in (("rubble|stone edges", 2000, 2500), ("rubble|stone centres", 1600, 2900), ("stone|iron edges", 3300, 7500), ("stone|iron centres", 2900, 7500), ("rubble|iron centres", 1600, 7500)):
        sep = math.log(r2 / r1)
        need = (sep / 3) ** 2 - sl ** 2
        out.append("%s: ln ratio %.2f, sep with perfect A1 %.1f sigma, f(A1) for 3 sigma: %s" % (nm, sep, sep / sl, ("%.0f%%" % (100 * math.sqrt(need))) if need > 0 else "impossible"))
    print("  size uncertainty: %s\n      " % lab + "\n      ".join(out))
