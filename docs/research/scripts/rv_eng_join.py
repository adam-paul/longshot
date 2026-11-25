import json, sys, re, statistics
nh = json.load(open(sys.argv[1]))["data"]
sbj = json.load(open(sys.argv[2]))
F = sbj["fields"]; ix = {f:i for i,f in enumerate(F)}
sb = {}
dups = 0
for r in sbj["data"]:
    k = r[ix["pdes"]]
    if k in sb: dups += 1
    sb[k] = r
print("SBDB rows", len(sbj["data"]), "unique pdes", len(sb), "dup pdes", dups)
kinds = {}
for r in sbj["data"]:
    kinds[r[ix["kind"]]] = kinds.get(r[ix["kind"]],0)+1
print("kinds", kinds)
miss = [o["des"] for o in nh if o["des"] not in sb]
print("NHATS", len(nh), "not in SBDB by des==pdes:", len(miss), miss[:20])
# designation shapes
shapes = {}
for o in nh:
    d = o["des"]
    if re.fullmatch(r"\d+", d): s = "numbered"
    elif re.fullmatch(r"\d{4} [A-Z]{2}\d*", d): s = "provisional"
    else: s = "other:"+d
    shapes[s] = shapes.get(s,0)+1
print("des shapes", {k:v for k,v in shapes.items() if not k.startswith("other")}, [k for k in shapes if k.startswith("other")][:20])
# named
named = [(o["des"], sb[o["des"]][ix["name"]]) for o in nh if o["des"] in sb and sb[o["des"]][ix["name"]]]
print("named NHATS:", len(named), [n for n in named if not n[1].isascii()][:10])
nonascii_full = [o["fullname"] for o in nh if not o["fullname"].isascii()]
print("non-ascii fullnames", nonascii_full[:10])
# counts
def dv(o): return float(o["min_dv"]["dv"])
def H(o):
    return float(o["h"]) if o["h"] not in (None,"") else float("nan")
print("dv<5", sum(dv(o)<5 for o in nh), "dv<6", sum(dv(o)<6 for o in nh), "dv<7", sum(dv(o)<7 for o in nh))
arcs = []
for o in nh:
    r = sb.get(o["des"])
    if r and r[ix["data_arc"]] not in (None,""):
        arcs.append(float(r[ix["data_arc"]]))
print("median arc", statistics.median(arcs), "n with arc", len(arcs), "missing arc", len(nh)-len(arcs))
print("median H", statistics.median(H(o) for o in nh if o["h"] not in (None,"")), "NHATS h null:", [o["des"] for o in nh if o["h"] in (None,"")][:10], sum(1 for o in nh if o["h"] in (None,"")))
print("NHATS null field counts:", {k: sum(1 for o in nh if o.get(k) in (None,"")) for k in nh[0].keys()})
print("SBDB null among NHATS:", {f: sum(1 for o in nh if sb[o["des"]][ix[f]] in (None,"")) for f in ("H","data_arc","condition_code","first_obs","last_obs","rms","n_obs_used","epoch","two_body")})
# elimination table
def rows(lim):
    s = [o for o in nh if dv(o) < lim]
    b = [o for o in s if H(o) < 24]
    out = [len(s), len(b)]
    for label, test in [("occ<=5", lambda o: int(o["occ"])<=5), ("occ<=4", lambda o:int(o["occ"])<=4), ("occ<=6", lambda o:int(o["occ"])<=6), ("occ<=3", lambda o:int(o["occ"])<=3)]:
        g = [o for o in b if test(o)]
        p = [o for o in g if sb[o["des"]][ix["rot_per"]] not in (None,"")]
        slow = [o for o in p if float(sb[o["des"]][ix["rot_per"]]) > 2.2]
        out.append((label, len(g), len(p), len(slow), [ (o["des"], sb[o["des"]][ix["rot_per"]], o["h"]) for o in slow][:8]))
    return out
for lim in (5,6,7):
    print(lim, rows(lim))
# occ of nhats vs sbdb condition_code
diff = sum(1 for o in nh if o["des"] in sb and str(sb[o["des"]][ix["condition_code"]]) != o["occ"])
print("occ != condition_code:", diff)
# orbit_id mismatch between nhats and sbdb snapshot (staleness)
od = sum(1 for o in nh if o["des"] in sb and str(sb[o["des"]][ix["orbit_id"]]).replace("JPL ","") != o["orbit_id"])
print("orbit_id differs NHATS vs SBDB:", od)
# H differs
hd = sum(1 for o in nh if o["des"] in sb and sb[o["des"]][ix["H"]] and abs(float(sb[o["des"]][ix["H"]]) - H(o))>0.05)
print("H differs >0.05:", hd)
# A2 present, law fields
print("has DT field in SBDB:", "DT" in ix, "; g(r) fields present:", [f for f in F if f.lower() in ("alpha","k","m","n_ng","r0","ngmodel")])
a2 = sum(1 for r in sbj["data"] if r[ix["A2"]] and r[ix["kind"]].startswith("a"))
a1 = sum(1 for r in sbj["data"] if r[ix["A1"]] and r[ix["kind"]].startswith("a"))
print("A2 asteroids", a2, "A1 asteroids", a1)
# first_obs since 2026-11-10 in NHATS
new = sum(1 for o in nh if o["des"] in sb and (sb[o["des"]][ix["first_obs"]] or "") >= "2026-11-10")
print("NHATS first_obs >= 2026-11-10:", new)
# yearly NHATS additions by designation year
yr = {}
for o in nh:
    m = re.match(r"(\d{4}) ", o["des"])
    if m: yr[m.group(1)] = yr.get(m.group(1),0)+1
print({k:yr[k] for k in sorted(yr) if k>="2019"})
# two-file count
print("files at 2/object:", 2*len(nh), "3/object:", 3*len(nh))
