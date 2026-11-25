import json, sys, math
base = sys.argv[1]
n = json.load(open(base + "/nhats.json"))
print("signature:", n.get("signature"))
n = n["data"]
s = json.load(open(base + "/sbdb_neo.json"))
F = s["fields"]; idx = {f:i for i,f in enumerate(F)}
sb = {r[idx["pdes"]]: r for r in s["data"]}
def f(x):
    try: return float(x)
    except: return None
nh = {o["des"]: o for o in n}
for d in ("162173","101955","25143","99942","341843","175706","65803","2000 SG344","2008 HU4","2009 BD","2011 MD","2006 RH120","2020 CD3","2014 WX202"):
    o = nh.get(d); r = sb.get(d)
    print(d, (r[idx["name"]] if r else None), "NHATS" if o else "not in NHATS", (o["min_dv"], o["h"], o["min_size"], o["max_size"]) if o else "")
# the nine H<24 dv<6 objects: windows
print()
for o in n:
    h = f(o["h"]); dv = f(o["min_dv"]["dv"])
    if h is not None and h < 24 and dv < 6:
        r = sb[o["des"]]
        print(o["des"], "H", h, "dv", dv, "cc", r[idx["condition_code"]], "rot", r[idx["rot_per"]], "| next window", o.get("obs_start"), "to", o.get("obs_end"), "peak V", o.get("obs_mag"), "flag", repr(o.get("obs_flag")), "| A2", r[idx["A2"]], r[idx["A2_sigma"]], "diam", r[idx["diameter"]])
# metal-exclusion counts across thresholds / factors
rows = []
for o in n:
    r = sb[o["des"]]
    A2 = f(r[idx["A2"]]); s2 = f(r[idx["A2_sigma"]]); H = f(r[idx["H"]])
    if A2 is None or s2 is None or s2 == 0 or H is None: continue
    if abs(A2)/s2 < 3: continue
    rows.append((o["des"], abs(A2), s2, H, f(r[idx["diameter"]])))
print("\nNHATS A2>=3 sigma:", len(rows), "with SBDB diameter:", sum(1 for x in rows if x[4]))
def rho_max(A2, H, pv):
    D = 1329e3/math.sqrt(pv)*10**(-H/5)
    return 3.128e-8*(1-0.39*pv)/(D*A2)
print("nominal pv 0.15, <4000:", sum(1 for d,a,s_,H,dm in rows if rho_max(a,H,0.15) < 4000))
for pv in (0.30, 0.50):
    for fac in (1.3, 1.5, 1.541, 1.8, 2.0, 2.37):
        out = []
        for T in (3400, 4000, 5000, 7500):
            c = sum(1 for d,a,s_,H,dm in rows if a-2*s_ > 0 and fac*rho_max(a-2*s_, H, pv) < T)
            out.append("T<%d: %d" % (T, c))
        print("pv %.2f factor %.3f | " % (pv, fac) + " ; ".join(out))
# Hsigma distribution for NHATS
hs = [f(sb[o["des"]][idx["H_sigma"]]) for o in n]
hs = sorted(x for x in hs if x is not None)
print("\nH_sigma available for", len(hs), "of", len(n), "median", hs[len(hs)//2], "p10", hs[len(hs)//10], "p90", hs[9*len(hs)//10])
u5 = [f(sb[o["des"]][idx["H_sigma"]]) for o in n if f(o["min_dv"]["dv"]) < 5]
u5 = sorted(x for x in u5 if x is not None)
print("dv<5 H_sigma median", u5[len(u5)//2], "n", len(u5))
# A1 counts
a1 = [(r[idx["pdes"]], f(r[idx["A1"]]), f(r[idx["A1_sigma"]])) for r in s["data"] if r[idx["kind"]].startswith("a") and f(r[idx["A1"]]) is not None]
print("NEA with A1:", len(a1), ">=3 sigma:", sum(1 for d,a,sg in a1 if sg and abs(a)/sg >= 3), "negative A1:", [(d,a,sg) for d,a,sg in a1 if a < 0])
