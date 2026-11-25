#!/usr/bin/env python3
"""fm_tno_recent.py TNO_JSON
Lists bright distant objects (H<6, a>30 au) from a JPL SBDB query result, flags those with a designation year 2026
or an orbit solution dated on/after 2026-10-20, and computes current heliocentric distance from the elements (two-body).
Purpose: look for any newly designated large trans-Neptunian object that could be the Depue/Wolk/Farritor candidate."""
import json, sys, math, datetime
d = json.load(open(sys.argv[1]))
F = d["fields"]; rows = [dict(zip(F, r)) for r in d["data"]]
print("count", len(rows), "fields", F)
def r_now(row, jd_now):
    try:
        a=float(row["a"]); e=float(row["e"]); ma=math.radians(float(row["ma"])); ep=float(row["epoch"]); per=float(row["per_y"])*365.25
    except Exception: return None
    if e >= 1 or a <= 0: return None
    M = ma + 2*math.pi*(jd_now-ep)/per
    E = M
    for _ in range(60): E = E - (E - e*math.sin(E) - M)/(1 - e*math.cos(E))
    return a*(1 - e*math.cos(E))
jd_now = 2461365.5  # 2026-11-21
def diam(H, p): return 1329.0/math.sqrt(p)*10**(-0.2*H)
flag=[]
for r in rows:
    r["r_now"] = r_now(r, jd_now)
    sd = (r.get("soln_date") or "")[:10]
    if r["pdes"].startswith("2026") or sd >= "2026-10-20": flag.append(r)
flag.sort(key=lambda r: (r.get("soln_date") or ""))
print("\nDesignated in 2026 or orbit solution on/after 2026-10-20:", len(flag))
for r in flag:
    H=float(r["H"]); print(f'{r["pdes"]:>12} {str(r["name"] or ""):12} H={H:5.2f} a={float(r["a"]):7.1f} q={float(r["q"]):6.1f} i={float(r["i"]):5.1f} r_now={r["r_now"] and round(r["r_now"],1)} D(p=0.08..0.15)={diam(H,0.15):.0f}-{diam(H,0.08):.0f} km first={r["first_obs"]} last={r["last_obs"]} nobs={r["n_obs_used"]} arc={r["data_arc"]} cc={r["condition_code"]} soln={r["soln_date"]} prod={r["producer"]}')
print("\nObjects now beyond 70 au with H<5.5 (the 'twice as far as Pluto, quarter of its width' region):")
far=[r for r in rows if r["r_now"] and r["r_now"]>70 and float(r["H"])<5.5]
far.sort(key=lambda r:-r["r_now"])
for r in far:
    H=float(r["H"]); print(f'{r["pdes"]:>12} {str(r["name"] or ""):12} H={H:5.2f} a={float(r["a"]):7.1f} r_now={r["r_now"]:.1f} first={r["first_obs"]} last={r["last_obs"]} nobs={r["n_obs_used"]} soln={r["soln_date"]}')
