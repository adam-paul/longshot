#!/usr/bin/env python3
"""Summarise SsODNet ssoCards for SBDB NEO asteroids with A2: spins, diameters, densities, taxonomy.

Usage: ssocard_stats.py sbdb_ng_all.json ssocards_dir
"""
import json
import math
import os
import sys
from collections import Counter

sb = json.load(open(sys.argv[1]))
d = sys.argv[2]
F = sb["fields"]
rows = [dict(zip(F, r)) for r in sb["data"]]
rows = [r for r in rows if r["neo"] == "Y" and r["kind"].startswith("a")]
K = 3.1282e-08  # rho_max = K (1-A) / (D[m] |A2|)

n_card = 0
n_num = sum(1 for r in rows if r["kind"] == "an")
have = dict(spin=0, diam=0, dens=0, tax=0, ti=0, spin_diam=0, spin_diam_a2=0)
diam_methods = Counter()
tax_complex = Counter()
out = []
for r in rows:
    fn = os.path.join(d, r["pdes"].replace(" ", "_") + ".json")
    if not (os.path.exists(fn) and os.path.getsize(fn) > 100):
        continue
    try:
        c = json.load(open(fn))
    except Exception:  # noqa: BLE001
        continue
    n_card += 1
    p = (c.get("parameters") or {}).get("physical") or {}

    def val(k):
        x = p.get(k)
        return x.get("value") if isinstance(x, dict) else None

    def methods(k):
        x = p.get(k)
        m = x.get("method") if isinstance(x, dict) else None
        return sorted({str(mm.get("label")) for mm in m if isinstance(mm, dict)}) if isinstance(m, list) else []

    spins = p.get("spins") or []
    if isinstance(spins, dict):
        spins = list(spins.values()) if all(isinstance(v, dict) for v in spins.values()) else [spins]
    poles = []
    for s in spins:
        if not isinstance(s, dict):
            continue
        lat = s.get("lat"); lon = s.get("long")
        if isinstance(lat, dict):
            lat = lat.get("value")
        if isinstance(lon, dict):
            lon = lon.get("value")
        tech = s.get("technique") or ",".join(str(mm.get("label")) for mm in (s.get("method") or []) if isinstance(mm, dict))
        if lat is not None and lon is not None:
            poles.append((lon, lat, tech))
    D = val("diameter"); rho = val("density"); ti = val("thermal_inertia")
    tax = p.get("taxonomy") or {}
    tcl = tax.get("complex") if isinstance(tax, dict) else None
    alb = val("albedo")
    a2 = float(r["A2"]) if r["A2"] is not None else None
    a2s = float(r["A2_sigma"]) if r["A2_sigma"] is not None else None
    if poles:
        have["spin"] += 1
    if D:
        have["diam"] += 1
        for m in methods("diameter"):
            diam_methods[m] += 1
    if rho:
        have["dens"] += 1
    if tcl:
        have["tax"] += 1
        tax_complex[tcl] += 1
    if ti:
        have["ti"] += 1
    if poles and D:
        have["spin_diam"] += 1
        if a2 is not None and a2s and abs(a2) / a2s >= 3:
            have["spin_diam_a2"] += 1
    out.append(dict(pdes=r["pdes"], name=c.get("name"), H=r["H"], D=D, alb=alb, rho=rho, rho_m=methods("density"), tax=tcl, ti=ti, poles=poles, a2=a2, a2s=a2s))

print(f"NEO asteroids with NG params in SBDB: {len(rows)} (numbered: {n_num}); ssoCards read: {n_card}")
print("have:", have)
print("diameter methods:", dict(diam_methods.most_common(12)))
print("taxonomy complexes:", dict(tax_complex.most_common(20)))

print("\n--- objects with pole + diameter + A2 (SNR>=3): density upper bound vs SsODNet density ---")
print("name | H | D km | tax | n_poles | lat(s) | A2 | snr | rho_max (linear, F=0.207, |cos|=1) | SsODNet rho (methods)")
for o in out:
    if o["poles"] and o["D"] and o["a2"] is not None and o["a2s"] and abs(o["a2"]) / o["a2s"] >= 3:
        A = 0.39 * (o["alb"] or 0.15)
        rmax = K * (1 - A) / (o["D"] * 1000 * abs(o["a2"]))
        lats = ",".join(f"{pp[1]:.0f}" for pp in o["poles"][:4])
        print(f"{o['name'] or o['pdes']} | {o['H']} | {o['D']:.3f} | {o['tax']} | {len(o['poles'])} | {lats} | {o['a2']:.2e} | {abs(o['a2'])/o['a2s']:.1f} | {rmax:.0f} | {o['rho']} {o['rho_m']}")

print("\n--- objects with SsODNet density (any) and A2 SNR>=3 ---")
viol = 0; nn = 0
for o in out:
    if o["rho"] and o["D"] and o["a2"] is not None and o["a2s"] and abs(o["a2"]) / o["a2s"] >= 3:
        A = 0.39 * (o["alb"] or 0.15)
        rmax = K * (1 - A) / (o["D"] * 1000 * abs(o["a2"]))
        nn += 1
        flag = "VIOLATES" if o["rho"] > rmax else ""
        if flag:
            viol += 1
        print(f"  {o['name'] or o['pdes']:22s} D={o['D']:.3f} km tax={o['tax']} rho={o['rho']:.0f} {o['rho_m']} rho_max={rmax:.0f} ratio={o['rho']/rmax:.2f} {flag}")
print("n with density:", nn, " violations of linear bound:", viol)

print("\n--- M / metal-related taxonomy among cards ---")
for o in out:
    if o["tax"] and o["tax"] in ("M", "X", "E", "P", "Xk", "Xe", "Xc"):
        A = 0.39 * (o["alb"] or 0.15)
        rmax = K * (1 - A) / (o["D"] * 1000 * abs(o["a2"])) if (o["D"] and o["a2"]) else float("nan")
        print(f"  {o['name'] or o['pdes']:22s} tax={o['tax']} D={o['D']} alb={o['alb']} A2={o['a2']} snr={abs(o['a2'])/o['a2s'] if o['a2'] and o['a2s'] else None} rho_max={rmax:.0f}")
