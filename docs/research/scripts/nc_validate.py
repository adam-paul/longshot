#!/usr/bin/env python3
"""Claim 3: nominal Yarkovsky density bound vs independently measured densities.
A2 from the fresh SBDB snapshot (or NEOCC for Bennu); D, albedo, density from SsODNet ssoCards / SBDB (hard-coded below
from the files saved under dl/nongrav-check, see report).  Usage: python3 -I nc_validate.py <sbdb_neo.json>
"""
import json, math, sys
K = 3.1282e-8
Q = 0.39
d = json.load(open(sys.argv[1]))
rows = {r[d["fields"].index("pdes")]: dict(zip(d["fields"], r)) for r in d["data"]}
SIG = 5.670374419e-8

def eta_linear(gamma, P_h, a_au, A, obl_deg, eps=0.9):
    S = 1361.2 / a_au ** 2
    Ts = ((1 - A) * S / (eps * SIG)) ** 0.25
    th = gamma * math.sqrt(2 * math.pi / (P_h * 3600)) / (eps * SIG * Ts ** 3)
    w = 0.5 * th / (1 + th + 0.5 * th * th)
    return th, w / 0.20711 * abs(math.cos(math.radians(obl_deg)))

# name, pdes, D[m], sigD, pV, rho, rho_minus, rho_plus, how the density was measured, override (A2, sigma) or None
objs = [
    ("Bennu", "101955", 484.44, 0.3, 0.044, 1194, 3, 3, "spacecraft (SBDB)", (4.60476e-14, 4.60476e-14 / 191.42)),   # NEOCC ke1 today
    ("Ryugu", "162173", 896, 4, 0.045, 1190, 20, 20, "spacecraft (SBDB)", (2.487268e-14, 5.013e-15)),
    ("Itokawa", "25143", 330, 11, 0.27, 1900, 130, 130, "spacecraft (SBDB); ssoCard 1929+-253", (2.855044e-14, 7.198e-15)),
    ("1996 FG3", "175706", 1670, 48, 0.03, 1364, 419, 418, "binary, mutual events (ssoCard)", None),
    ("Hermes", "69230", 800, 37, 0.234, 1810, None, None, "binary (ssoCard, no error)", None),
    ("1994 AW1", "385186", 861, 25, 0.209, 1400, 500, 500, "binary, radar (ssoCard)", None),
    ("Sekhmet", "5381", 1221, 64, 0.243, 1980, 650, 650, "binary, radar (ssoCard)", None),
    ("2003 YT1", "164121", 1143, 127, 0.469, 1624, 1040, 1040, "binary, radar mass / NEATM size (ssoCard)", None),
    ("Moshup", "66391", 1335, 48, 0.219, 1268, 439, 815, "binary (ssoCard); Ostro+2006: 1970+-240", None),
    ("Apollo", "1862", 1200, None, 0.45, 2050, 350, 350, "binary, radar (ssoCard)", None),
    ("2000 DP107", "185851", 960, 43, 0.091, 998, 236, 236, "binary, radar mass / NEATM size (ssoCard); Naidu+2015: 1381+-244", None),
    ("2000 WO107", "153201", 510, 83, 0.129, 4800, 630, 340, "contact-binary spin limit, model dependent (Krugly+2025)", (1.564280e-14, 3.248e-15)),
]
print("%-11s %7s %10s %5s %8s %8s %6s %6s  %s" % ("object", "D[m]", "|A2|", "S/N", "rho_max", "rho", "ratio", "+-", "density source"))
for name, pd, D, sD, pv, rho, rm, rp, how, ov in objs:
    r = rows[pd]
    if ov:
        a2, s = ov
    elif r["A2"] is not None:
        a2, s = abs(float(r["A2"])), float(r["A2_sigma"])
    else:
        print("%-11s no A2 in SBDB snapshot" % name); continue
    rmax = K * (1 - Q * pv) / (D * a2)
    fr = math.sqrt((s / a2) ** 2 + ((sD or 0) / D) ** 2)
    ratio = rho / rmax
    # 1-sigma error of the ratio from A2, D and density
    er = ratio * math.sqrt(fr ** 2 + (((rm or 0) + (rp or 0)) / 2 / rho) ** 2)
    print("%-11s %7.0f %10.3e %5.1f %8.0f %8.0f %6.2f %6.2f  %s | SBDB: D=%s alb=%s A2=%s" % (name, D, a2, a2 / s, rmax, rho, ratio, er, how, r["diameter"], r["albedo"], r["A2"]))

print("\nlinear-theory efficiency predicted from measured thermal inertia, spin and obliquity vs efficiency measured (rho/rho_max):")
for name, gamma, P, a, A, obl, meas in (("Bennu", 300, 4.296061, 1.1264, 0.017, 177.6, 0.866), ("Ryugu", 225, 7.63262, 1.1909, 0.018, 171.6, 0.863), ("Itokawa", 700, 12.132, 1.3241, 0.105, 178.5, 0.636)):
    th, e = eta_linear(gamma, P, a, A, obl)
    print("   %-8s Gamma=%4d P=%6.3f h obliquity=%5.1f: Theta=%.2f predicted eta=%.2f measured=%.2f measured/predicted=%.2f" % (name, gamma, P, obl, th, e, meas, meas / e))

print("\nother objects the screen puts low (not independent densities):")
for name, pd, D, pv in (("Toutatis (SBDB D = 5.4 km is the long axis)", "4179", 5400, 0.157), ("Toutatis (Chang'e-2 equivalent D 2.725 km)", "4179", 2725, 0.157), ("Phaethon (SBDB D 6.25 km)", "3200", 6250, 0.107), ("Phaethon (TPM D 5.165 km)", "3200", 5165, 0.117)):
    r = rows[pd]; a2 = abs(float(r["A2"])); s = float(r["A2_sigma"])
    print("   %-45s |A2|=%.2e S/N=%.1f nominal rho_max=%.0f ; x1.5 and -2 sigma: %.0f | A1=%s" % (name, a2, a2 / s, K * (1 - Q * pv) / (D * a2), 1.5 * K * (1 - Q * pv) / (D * (a2 - 2 * s)), r["A1"]))
