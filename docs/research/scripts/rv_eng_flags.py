import json, sys, collections
nh = json.load(open(sys.argv[1]))["data"]
sbj = json.load(open(sys.argv[2]))
F = sbj["fields"]; ix = {f:i for i,f in enumerate(F)}
c = collections.Counter((repr(o["obs_flag"]), o["obs_start"] is None) for o in nh)
print("obs_flag x obs_start-null:", dict(c))
print("occ values:", dict(collections.Counter(o["occ"] for o in nh)))
print("types: n_via_traj", type(nh[0]["n_via_traj"]).__name__, "h", type(nh[0]["h"]).__name__, "occ", type(nh[0]["occ"]).__name__)
print("orbit_id samples NHATS:", [o["orbit_id"] for o in nh[:5]], "SBDB:", [r[ix["orbit_id"]] for r in sbj["data"][:3]+sbj["data"][-3:]])
# search for TA56-like
print([ (r[ix["pdes"]], r[ix["full_name"]], r[ix["class"]], r[ix["A2"]]) for r in sbj["data"] if "TA56" in r[ix["pdes"]] or "TA5" in r[ix["pdes"]] and r[ix["pdes"]].startswith("2016")][:10])
# names with non-alnum chars
odd = [(r[ix["pdes"]], r[ix["name"]]) for r in sbj["data"] if r[ix["name"]] and not r[ix["name"]].replace(" ","").replace("-","").isalnum()]
print("names with punctuation:", len(odd), odd[:15])
# pdes forms in SBDB (comets etc.)
import re
forms = collections.Counter()
for r in sbj["data"]:
    d = r[ix["pdes"]]
    if re.fullmatch(r"\d+", d): forms["numbered"]+=1
    elif re.fullmatch(r"\d{4} [A-Z]{2}\d*", d): forms["prov"]+=1
    else: forms["other"]+=1
print(forms, [r[ix["pdes"]] for r in sbj["data"] if not re.fullmatch(r"\d+|\d{4} [A-Z]{2}\d*", r[ix["pdes"]])][:12])
# numbered objects in NHATS: full_name includes provisional?
ex = [sbj["data"][i][ix["full_name"]] for i in range(len(sbj["data"])) if sbj["data"][i][ix["pdes"]] in ("469219","101955","99942","613862")]
print(ex)
# rot_per precision oddities among NHATS
sb = {r[ix["pdes"]]: r for r in sbj["data"]}
print("NHATS diam present:", sum(1 for o in nh if sb[o["des"]][ix["diameter"]]), "rot:", sum(1 for o in nh if sb[o["des"]][ix["rot_per"]]))
# H mismatch magnitude
import statistics
d = [abs(float(sb[o["des"]][ix["H"]])-float(o["h"])) for o in nh if o["h"] and sb[o["des"]][ix["H"]]]
print("H diff NHATS vs SBDB: n>0.05", sum(x>0.05 for x in d), "n>0.3", sum(x>0.3 for x in d), "max", max(d))
# does H<24 membership change depending on which H?
a = {o["des"] for o in nh if o["h"] and float(o["h"])<24}
b = {o["des"] for o in nh if sb[o["des"]][ix["H"]] and float(sb[o["des"]][ix["H"]])<24}
print("H<24 by NHATS:", len(a), "by SBDB:", len(b), "sym diff:", len(a^b))
