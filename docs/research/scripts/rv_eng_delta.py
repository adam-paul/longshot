import json, sys, statistics
nh = json.load(open(sys.argv[1]))["data"]
sbj = json.load(open(sys.argv[2]))
F = sbj["fields"]; ix = {f:i for i,f in enumerate(F)}
sb = {r[ix["pdes"]]: r for r in sbj["data"]}
g = lambda o,f: sb[o["des"]][ix[f]]
# incremental-fetch size
for cut,label in (("2026-11-14","7 d"),("2026-10-21","31 d"),("2026-08-21","92 d"),("2025-11-21","1 yr")):
    n = sum(1 for o in nh if (g(o,"last_obs") or "") >= cut)
    print(f"NHATS with last_obs >= {cut} ({label}): {n}")
# all NEOs
for cut,label in (("2026-11-14","7 d"),("2026-10-21","31 d")):
    print(f"all NEOs last_obs >= {cut} ({label}):", sum(1 for r in sbj["data"] if (r[ix["last_obs"]] or "") >= cut))
# observation volume
nobs = [int(g(o,"n_obs_used") or 0) for o in nh]
print("NHATS sum n_obs_used", sum(nobs), "median", statistics.median(nobs), "max", max(nobs))
print("ADES XML estimate at 633 B/obs: %.0f MB" % (sum(nobs)*633/1e6))
allobs = [int(r[ix["n_obs_used"]] or 0) for r in sbj["data"]]
print("all NEO sum n_obs_used", sum(allobs), "-> %.1f GB at 633 B/obs" % (sum(allobs)*633/1e9))
# informative sets
arc = lambda o: float(g(o,"data_arc")) if g(o,"data_arc") not in (None,"") else None
H = lambda o: float(o["h"]) if o["h"] not in (None,"") else None
print("NHATS arc>1000 d:", sum(1 for o in nh if arc(o) and arc(o)>1000))
print("NHATS H>=27 & arc>=60:", sum(1 for o in nh if arc(o) and H(o) is not None and H(o)>=27 and arc(o)>=60))
a2 = [o for o in nh if g(o,"A2")]
a1 = [o for o in nh if g(o,"A1")]
print("NHATS with A2:", len(a2), "A2 S/N>=3:", sum(1 for o in a2 if g(o,"A2_sigma") and abs(float(g(o,"A2"))/float(g(o,"A2_sigma")))>=3), "A1:", len(a1))
neo_a2_sn3 = sum(1 for r in sbj["data"] if r[ix["kind"]].startswith("a") and r[ix["A2"]] and r[ix["A2_sigma"]] and abs(float(r[ix["A2"]])/float(r[ix["A2_sigma"]]))>=3)
print("NEA A2 S/N>=3:", neo_a2_sn3)
# of those 573, how many are NHATS; how many have radar obs; arcs
strong = [r for r in sbj["data"] if r[ix["kind"]].startswith("a") and r[ix["A2"]] and r[ix["A2_sigma"]] and abs(float(r[ix["A2"]])/float(r[ix["A2_sigma"]]))>=3]
nhset = {o["des"] for o in nh}
print("strong A2 in NHATS:", sum(1 for r in strong if r[ix["pdes"]] in nhset), "with radar:", sum(1 for r in strong if (r[ix["n_del_obs_used"]] or 0) or (r[ix["n_dop_obs_used"]] or 0)))
print("strong A2 sum n_obs_used:", sum(int(r[ix["n_obs_used"]] or 0) for r in strong), "median arc d:", statistics.median(float(r[ix["data_arc"]]) for r in strong))
print("strong A2 with DT or A1/A3 also set:", sum(1 for r in strong if r[ix["A1"]] or r[ix["A3"]] or r[ix["DT"]]))
# fixture candidates
for d in ["2009 BD","2011 AA37","2022 OB5","2026 QQ8","2020 CD3","2010 CW266","101955","469219","2011 MD","1998 KY26","2015 BM510","99942","2022 RD2","2024 PT5","2006 RH120","2016 TA56","2021 ER","2010 NU71","2013 NJ"]:
    o = next((x for x in nh if x["des"]==d), None)
    r = sb.get(d)
    if not r: print(d, "NOT IN SBDB"); continue
    print(d, "| NHATS" if o else "| not NHATS", "| name", r[ix["name"]], "| dv", o and o["min_dv"]["dv"], "| h", o and o["h"], "| occ", o and o["occ"], "| arc", r[ix["data_arc"]], "| nobs", r[ix["n_obs_used"]], "| rot", r[ix["rot_per"]], "| A1", r[ix["A1"]], "| A2", r[ix["A2"]], "| A3", r[ix["A3"]], "| diam", r[ix["diameter"]], "| first", r[ix["first_obs"]], "| obs_flag", o and o["obs_flag"], o and o["obs_start"])
