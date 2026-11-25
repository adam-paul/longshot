"""Empirical null: fit A1 (and A2) on real objects where no measurable radiation-pressure signal can exist
(H <= 21.5, i.e. D >= 150 m: expected A1 below 3e-12 au/d^2) with arcs of 90-200 d, and look at the distribution of
A1/sigma. If the error model were exact, A1/sigma_formal would be N(0,1).
usage: fr_null.py [--set null] [--nproc 16]
"""
import sys, os, json, time, argparse, importlib.util, warnings, multiprocessing as mp
warnings.filterwarnings("ignore")
spec = importlib.util.spec_from_file_location("fr_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fr_common.py"))
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
import numpy as np
ap = argparse.ArgumentParser()
ap.add_argument("--set", default="null")
ap.add_argument("--nproc", type=int, default=16)
args = ap.parse_args()
fit, libgrss, ver = C.import_grss(1)
picks = json.load(open(os.path.join(C.OUT, "picks.json")))[args.set]


def one(o):
    des = o["des"]
    try:
        raw, _, _ = C.fetch_sbdb(des); el, cm, ng, meta = C.parse_sbdb(raw); xml, _, _ = C.fetch_mpc_xml(des)
        obs, _ = C.load_obs(fit, des, xml)
    except Exception as e:
        return {"des": des, "error": repr(e)[:200]}
    tt = obs["obsTimeMJD"].astype(float)
    el6 = {k: el[k] for k in ("t",) + C.BASE}
    out = {"des": des, "H": meta["H"], "arc": float(tt.max() - tt.min()), "n": len(obs),
           "nights": len(set(np.floor(tt + 0.5).astype(int))), "D": C.diameter_m(meta["H"], 0.15)}
    for m in ("", "a1", "a2", "a1,a2"):
        est = [k for k in m.split(",") if k]
        r, _ = C.run_fit(fit, el6, obs, ng, est=est, n_iter_max=30)
        key = m or "6p"
        if "error" in r:
            out[key] = {"error": r["error"]}; continue
        out[key] = {"conv": r["converged"], "it": r["n_iter"], "red": r["red_chi2"], "chi2": r["chi2"], "n_rej": r["n_rej"], "wall": r["wall_s"],
                    **{k: r["x"][k] for k in est}, **{"s_" + k: r["sig"][k] for k in est}}
    return out


with mp.get_context("fork").Pool(args.nproc) as pool:
    res = pool.map(one, picks, chunksize=1)
json.dump(res, open(os.path.join(C.OUT, "null_%s.json" % args.set), "w"), indent=1, default=float)
print("des          H     D_m   arc   n  nights | 6p red  rej | A1 +- sigma (S/N formal, S/N rescaled) rej | A2 S/N formal, rescaled | A1 expected at 1000 kg/m3")
z1 = []; z1r = []; z2 = []; z2r = []
for r in res:
    if "error" in r:
        print(r["des"], "ERROR", r["error"]); continue
    a = r["a1"]; b = r["a2"]; g = r["6p"]
    if "error" in a or "error" in b or "error" in g or not a["conv"] or not b["conv"]:
        print(f"{r['des']:11s} not converged or error: 6p {g.get('conv')} a1 {a.get('conv')} a2 {b.get('conv')}"); continue
    s1 = a["a1"] / a["s_a1"]; s1r = s1 / np.sqrt(a["red"]); s2 = b["a2"] / b["s_a2"]; s2r = s2 / np.sqrt(b["red"])
    z1.append(s1); z1r.append(s1r); z2.append(s2); z2r.append(s2r)
    print(f"{r['des']:11s} {r['H']:5.2f} {r['D']:6.0f} {r['arc']:5.0f} {r['n']:4d} {r['nights']:3d} | {g['red']:.3f} {g['n_rej']:3d} | {a['a1']:+.2e} +- {a['s_a1']:.1e} ({s1:+.2f}, {s1r:+.2f}) {a['n_rej']:3d} | {s2:+.2f}, {s2r:+.2f} | {C.a1_from_density(1000, r['D']):.1e}")
for lab, z in (("A1 formal", z1), ("A1 rescaled", z1r), ("A2 formal", z2), ("A2 rescaled", z2r)):
    z = np.array(z)
    print(f"{lab:12s}: n {len(z)} mean {z.mean():+.2f} sd {z.std(ddof=1):.2f} max|z| {np.abs(z).max():.2f}  |z|>=2: {int((np.abs(z)>=2).sum())}  |z|>=3: {int((np.abs(z)>=3).sum())}  (Gaussian expectation for n={len(z)}: {0.0455*len(z):.1f} and {0.0027*len(z):.2f})")
