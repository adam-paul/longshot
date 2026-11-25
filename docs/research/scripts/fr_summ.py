"""Summarise probe-fit2/out/inject_*_a1.json into one table (no fitting)."""
import json, glob, os, re, numpy as np
S=os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "data", "research"))  # data/research under the repository root
K=2.266e-7*1.5
rows=[]
for f in sorted(glob.glob(S+"/probe-fit2/out/inject_*_a1.json")):
    d=json.load(open(f)); des=d["des"]
    log=open(S+"/probe-fit2/logs/inject_%s_a1.log"%des.replace(" ","_")).read()
    m=re.search(r"tracklets (\d+), nights (\d+)",log)
    r7=d["real"]["a1"]; sm={(s["noise"],s["level"]):s for s in d["summary"]}
    sig=r7["sig"]["a1"]
    def g(n,l,k): return sm[(n,l)][k] if (n,l) in sm else float("nan")
    rows.append(dict(des=des,H=d["H"],D=d["D_m"],arc=d["arc_d"],n=d["n_accepted"],nights=int(m.group(2)),a1=r7["x"]["a1"],sig=sig,red=r7["red_chi2"],
        sd_g=g("gauss","null","std"),sd_w=g("wild","null","std"),rho3=K/(d["D_m"]*3*sig),
        fa_f=(g("gauss","null","det3"),g("wild","null","det3")),fa_r=(g("gauss","null","det3_resc"),g("wild","null","det3_resc")),
        d500=(g("gauss","rho500","det3"),g("wild","rho500","det3")),d1200=(g("gauss","rho1200","det3"),g("wild","rho1200","det3")),d2500=(g("gauss","rho2500","det3"),g("wild","rho2500","det3")),
        r500=(g("gauss","rho500","det3_resc"),g("wild","rho500","det3_resc")),r1200=(g("gauss","rho1200","det3_resc"),g("wild","rho1200","det3_resc")),
        ntrial=d["ntrial"],wall=d["wall_s"],perfit=float(np.median([t["wall"] for t in d["trials"] if "wall" in t]))))
rows.sort(key=lambda r:r["sig"])
print("| Object | H | D (m) | Arc (d) | Positions | Nights | Real A1 +- formal sigma (S/N) | True scatter gauss / wild | Density at formal 3 sigma (kg/m3) | False alarms formal; rescaled (g/w) | Detected at 500: formal g/w; rescaled g/w | at 1,200: formal g/w; rescaled g/w | at 2,500 formal g/w | Median s per fit |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for r in rows:
    print(f"| {r['des']} | {r['H']:.2f} | {r['D']:.1f} | {r['arc']:.0f} | {r['n']} | {r['nights']} | {r['a1']:+.2e} +- {r['sig']:.2e} ({abs(r['a1'])/r['sig']:.1f}) | {r['sd_g']:.1e} / {r['sd_w']:.1e} | {r['rho3']:.0f} | {r['fa_f'][0]:.2f}/{r['fa_f'][1]:.2f}; {r['fa_r'][0]:.2f}/{r['fa_r'][1]:.2f} | {r['d500'][0]:.2f}/{r['d500'][1]:.2f}; {r['r500'][0]:.2f}/{r['r500'][1]:.2f} | {r['d1200'][0]:.2f}/{r['d1200'][1]:.2f}; {r['r1200'][0]:.2f}/{r['r1200'][1]:.2f} | {r['d2500'][0]:.2f}/{r['d2500'][1]:.2f} | {r['perfit']:.2f} |")
print("n objects",len(rows),"; total synthetic fits",sum(len(json.load(open(f))["trials"]) for f in glob.glob(S+"/probe-fit2/out/inject_*_a1.json")))
pulls_g=[r['sd_g']/r['sig'] for r in rows]; pulls_w=[r['sd_w']/r['sig'] for r in rows]
print("true scatter / formal sigma: gauss median %.2f range %.2f-%.2f ; wild median %.2f range %.2f-%.2f"%(np.median(pulls_g),min(pulls_g),max(pulls_g),np.median(pulls_w),min(pulls_w),max(pulls_w)))
print("sigma<=3.5e-11:",[r["des"] for r in rows if r["sig"]<=3.5e-11])
