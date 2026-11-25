import json, sys, math, statistics as st
base = sys.argv[1]
n = json.load(open(base + "/nhats.json"))["data"]
s = json.load(open(base + "/sbdb_neo.json"))
F = s["fields"]; idx = {f:i for i,f in enumerate(F)}
sb = {}
for r in s["data"]:
    sb[r[idx["pdes"]]] = r
def f(x):
    try: return float(x)
    except: return None
rows = []
miss = 0
for o in n:
    des = o["des"]
    r = sb.get(des)
    if r is None:
        miss += 1
        continue
    rows.append(dict(des=des, dv=f(o["min_dv"]["dv"]), h=f(o["h"]), H=f(r[idx["H"]]), Hsig=f(r[idx["H_sigma"]]),
                     cc=r[idx["condition_code"]], arc=f(r[idx["data_arc"]]), rot=f(r[idx["rot_per"]]),
                     a=f(r[idx["a"]]), e=f(r[idx["e"]]), i=f(r[idx["i"]]), q=f(r[idx["q"]]),
                     A1=f(r[idx["A1"]]), A1s=f(r[idx["A1_sigma"]]), A2=f(r[idx["A2"]]), A2s=f(r[idx["A2_sigma"]]),
                     occ=o["occ"], obs_flag=o.get("obs_flag"), obs_start=o.get("obs_start"), obs_mag=f(o.get("obs_mag")),
                     nobs=r[idx["n_obs_used"]], diam=f(r[idx["diameter"]]), alb=f(r[idx["albedo"]]), first=r[idx["first_obs"]], last=r[idx["last_obs"]]))
print("NHATS", len(n), "matched", len(rows), "missing", miss)
for lim in (5,6,7):
    sub = [x for x in rows if x["dv"] < lim]
    b = [x for x in sub if x["h"] is not None and x["h"] < 24]
    print("dv<%d: %d ; H<24: %d" % (lim, len(sub), len(b)), end=" ; ")
    for ccmax in (3,4,5,6):
        g = [x for x in b if x["cc"] is not None and int(x["cc"]) <= ccmax]
        print("cc<=%d: %d" % (ccmax, len(g)), end=" ")
    g = [x for x in b if x["cc"] is not None and int(x["cc"]) <= 5]
    wp = [x for x in b if x["rot"] is not None]
    slow = [x for x in wp if x["rot"] > 2.2]
    print("; with period (of H<24): %d ; slow: %d" % (len(wp), len(slow)))
    if lim == 6:
        for x in b: print("   ", x["des"], "H", x["h"], "dv", x["dv"], "cc", x["cc"], "arc", x["arc"], "rot", x["rot"], "obs", x["obs_start"], x["obs_mag"], x["obs_flag"])
# arcs
arcs = [x["arc"] for x in rows]
none = sum(1 for a in arcs if a is None)
le90 = sum(1 for a in arcs if a is not None and a <= 90)
print("dv<7 with H:", sum(1 for x in rows if x["dv"]<7 and x["h"] is not None))
print("arc None", none, "arc<=90", le90, "frac (None or <=90)", (none+le90)/len(rows))
for lim in (30, 60, 90, 180, 365, 1000):
    print("  arc<=%d or none: %.3f" % (lim, (none + sum(1 for a in arcs if a is not None and a <= lim))/len(rows)))
print("arc>1000:", sum(1 for a in arcs if a is not None and a > 1000))
print("H>=27 & arc>=60:", sum(1 for x in rows if x["h"] is not None and x["h"]>=27 and x["arc"] is not None and x["arc"]>=60))
# under 5: H distribution
u5 = [x for x in rows if x["dv"] < 5 and x["h"] is not None]
print("dv<5 without H:", sum(1 for x in rows if x["dv"]<5 and x["h"] is None), "; all without H:", sum(1 for x in rows if x["h"] is None))
hs = sorted(x["h"] for x in u5)
print("dv<5 n", len(u5), "H min", hs[0], "median", st.median(hs))
for lo,hi in ((24,24.5),(24.5,25),(25,25.5),(25.5,26),(26,27),(27,28),(28,40)):
    print("   H %.1f-%.1f: %d" % (lo,hi,sum(1 for h in hs if lo<=h<hi)))
# expected number >55 m under albedo mixture (Wright 2016-like: 25% dark Rayleigh peak 0.03, 75% bright peak 0.168)
import random
random.seed(1)
def draw_pv(fd=0.253, sd=0.030, sb_=0.168):
    # Rayleigh with mode sigma
    sig = sd if random.random() < fd else sb_
    return sig*math.sqrt(-2*math.log(1-random.random()))
def D(h, pv): return 1329e3/math.sqrt(pv)*10**(-h/5)
for label, fd in (("fixed-size-like 25% dark", 0.253), ("fixed-H-like 10% dark", 0.10)):
    for thr in (55, 50, 40):
        tot = 0.0
        for x in u5:
            c = 0; N = 4000
            for _ in range(N):
                pv = max(draw_pv(fd), 0.01)
                if D(x["h"], pv) > thr: c += 1
            tot += c/N
        print(label, "expected count D>%d m among dv<5: %.1f" % (thr, tot))
# Opik encounter speed
def U(a,e,i):
    T = 1/a + 2*math.sqrt(a*(1-e*e))*math.cos(math.radians(i))
    v = 3 - T
    return 29.78*math.sqrt(v) if v > 0 else 0.0
for lim in (4,5,6,12.1):
    sub = [x for x in rows if x["dv"] < lim]
    us = [U(x["a"],x["e"],x["i"]) for x in sub]
    print("dv<%s n=%d: U<2.4: %d ; U<1.5: %d ; U<3: %d ; median U %.2f" % (lim, len(sub), sum(1 for u in us if u<2.4), sum(1 for u in us if u<1.5), sum(1 for u in us if u<3), st.median(us)))
print("max a in NHATS:", max(x["a"] for x in rows))
for d in ("2016 TA56","883607","2022 OB5","1998 KY26","2022 RD2","2020 GE","2011 AA37","2024 PT5","2021 ER","2015 BM510","469219","2016 HO3"):
    hit = [x for x in rows if x["des"]==d]
    r = sb.get(d)
    print(d, "in NHATS:", bool(hit), (hit[0]["dv"], hit[0]["h"], hit[0]["cc"], hit[0]["arc"], hit[0]["rot"], hit[0]["nobs"], hit[0]["first"], hit[0]["last"], hit[0]["A1"], hit[0]["A2"], hit[0]["A2s"]) if hit else (r[idx["a"]], r[idx["e"]], r[idx["i"]], r[idx["H"]], r[idx["A2"]], r[idx["A2_sigma"]]) if r else None)
