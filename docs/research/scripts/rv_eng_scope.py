import json, sys
nh = json.load(open(sys.argv[1]))["data"]
sbj = json.load(open(sys.argv[2]))
F = sbj["fields"]; ix = {f:i for i,f in enumerate(F)}
sb = {r[ix["pdes"]]: r for r in sbj["data"]}
def arc(o):
    v = sb[o["des"]][ix["data_arc"]]
    return float(v) if v not in (None,"") else 0.0
for t in (30,60,90,365,1000):
    print("NHATS arc >=", t, "d:", sum(arc(o)>=t for o in nh))
strong = {r[ix["pdes"]] for r in sbj["data"] if r[ix["kind"]].startswith("a") and r[ix["A2"]] and r[ix["A2_sigma"]] and abs(float(r[ix["A2"]])/float(r[ix["A2_sigma"]]))>=3}
cand = {o["des"] for o in nh if arc(o)>1000} | {o["des"] for o in nh if o["h"] and float(o["h"])>=27 and arc(o)>=60}
print("candidates (arc>1000 or H>=27&arc>=60):", len(cand), "plus 573 validation ->", len(cand|strong))
print("NHATS arc>=30 plus validation:", len({o["des"] for o in nh if arc(o)>=30}|strong))
# growth headroom
n=len(nh); print("files now", 2*n, "headroom", 20000-2*n, "years at 650/yr x2:", round((20000-2*n)/1300,1))
print("1 file/object + 256 shards:", n+256, "years to 20000 at 650/yr:", round((20000-n-256)/650,1))
print("10,500 NEAs at 2 files:", 21000)
