"""Deterministic samples from the local snapshots (no network). Writes probe-fit2/out/picks.json.
 srp   : every 5th of the NHATS objects with H>=27, arc>=60 d, no JPL A1 (sorted by arc), no radar
 short : NHATS objects with arc <= 24 d: 5 per arc bin (0-3, 3-7, 7-14, 14-24 d), numpy seed 11
 null  : NEAs with H<=21.5, arc 90-200 d, 60<=n_obs<=250, no radar, no non-grav: 30 by numpy seed 11
"""
import json, os, numpy as np
S=os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "data", "research"))  # data/research under the repository root
n=json.load(open(S+"/dl/catalogs/nhats.json"))["data"]
s=json.load(open(S+"/dl/catalogs/sbdb_neo.json"))
F=s["fields"]; rows={r[F.index("pdes")]:dict(zip(F,r)) for r in s["data"]}
def fl(x):
    try: return float(x)
    except Exception: return None
nh=[]
for x in n:
    r=rows[x["des"]]; H=fl(r["H"]) or fl(x["h"]); arc=fl(r["data_arc"])
    nh.append(dict(des=x["des"],H=H,arc=arc,n=r["n_obs_used"],rad=(r["n_del_obs_used"] or 0)+(r["n_dop_obs_used"] or 0),A1=r["A1"],A2=r["A2"],cond=r["condition_code"]))
srp=sorted([o for o in nh if o["H"] and o["arc"] and o["H"]>=27 and o["arc"]>=60 and o["A1"] is None and o["rad"]==0], key=lambda o:(o["arc"],o["des"]))
srp_pick=srp[::5]
rng=np.random.default_rng(11)
short=[]
for lo,hi in ((0,3),(3,7),(7,14),(14,24)):
    pool=sorted([o for o in nh if o["arc"] is not None and lo<o["arc"]<=hi and o["rad"]==0 and o["A1"] is None and o["A2"] is None], key=lambda o:o["des"])
    idx=rng.choice(len(pool), size=5, replace=False)
    short+= [dict(pool[i], bin="%d-%d"%(lo,hi)) for i in sorted(idx)]
    print("short pool", lo, hi, len(pool))
null=[]
for r in rows.values():
    H=fl(r["H"]); arc=fl(r["data_arc"])
    if H is None or arc is None or r["kind"] not in ("au","an"): continue
    if H<=21.5 and 90<=arc<=200 and 60<=(r["n_obs_used"] or 0)<=250 and not r["n_del_obs_used"] and not r["n_dop_obs_used"] and r["A1"] is None and r["A2"] is None:
        null.append(dict(des=r["pdes"],H=H,arc=arc,n=r["n_obs_used"],cond=r["condition_code"],q=fl(r["q"]),moid=fl(r["moid"])))
null.sort(key=lambda o:o["des"])
print("null pool", len(null))
idx=rng.choice(len(null), size=30, replace=False)
null_pick=[null[i] for i in sorted(idx)]
print("srp no-A1 no-radar:",len(srp),"-> pick",len(srp_pick)); [print("  ",o) for o in srp_pick]
print("short pick"); [print("  ",o) for o in short]
print("null pick"); [print("  ",o) for o in null_pick]
import os
os.makedirs(S+"/probe-fit2/out",exist_ok=True)
json.dump({"srp":srp_pick,"short":short,"null":null_pick}, open(S+"/probe-fit2/out/picks.json","w"), indent=1)
