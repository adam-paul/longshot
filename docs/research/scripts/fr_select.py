"""List NHATS objects with H >= 27, data arc >= 60 d (JPL SBDB snapshot), flag those without a JPL A1.
usage: fr_select.py  (reads the local snapshots only; no network)"""
import json, os, statistics
S=os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "data", "research"))  # data/research under the repository root
n=json.load(open(S+"/dl/catalogs/nhats.json"))["data"]
s=json.load(open(S+"/dl/catalogs/sbdb_neo.json"))
F=s["fields"]; rows={r[F.index("pdes")]:dict(zip(F,r)) for r in s["data"]}
print("nhats",len(n))
hs=[float(x["h"]) for x in n if x["h"]]
print("median H", statistics.median(hs))
arcs=[]; miss=0; cand=[]
for x in n:
    r=rows.get(x["des"])
    if r is None:
        miss+=1; continue
    try: arc=float(r["data_arc"])
    except Exception: arc=None
    arcs.append(arc if arc is not None else 0)
    Hs = r["H"] if r["H"] else x["h"]
    if Hs is None: continue
    H=float(Hs)
    if arc is not None and H>=27 and arc>=60:
        cand.append((x["des"],H,arc,r["n_obs_used"],r["n_del_obs_used"],r["n_dop_obs_used"],r["A1"],r["A1_sigma"],r["A2"],r["A2_sigma"],r["first_obs"],r["last_obs"],r["condition_code"],x["min_dv"]["dv"],r["rms"],r["a"],r["e"],r["i"]))
print("missing in sbdb",miss,"median arc",statistics.median(arcs))
print("H>=27 & arc>=60:",len(cand),"; no A1:",sum(1 for c in cand if c[6] is None), "; no A1 and no A2:",sum(1 for c in cand if c[6] is None and c[8] is None))
cand.sort(key=lambda c:c[2])
print("des,H,arc,n_obs,n_del,n_dop,A1,A1s,A2,A2s,first,last,cond,min_dv,rms,a,e,i")
for c in cand: print(c)
