"""Step 1: reproduce JPL non-gravitational parameters with GRSS 4.6.0 from MPC astrometry (+ JPL radar).
Initial six elements from JPL SBDB (covariance epoch); every non-grav parameter starts at ZERO.
usage: fr_repro.py "<designation>" [--threads N] [--models a2 a1,a2 ...] [--no-radar] [--tmin MJD] [--tmax MJD] [--tag TAG]
Needs cached MPC XML and SBDB JSON (fr_fetch.py). Writes probe-fit2/out/repro_<des><tag>.json
"""
import sys, os, json, time, argparse, importlib.util, io, contextlib
t00 = time.time()
spec = importlib.util.spec_from_file_location("fr_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fr_common.py"))
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("des")
ap.add_argument("--threads", type=int, default=1)
ap.add_argument("--models", nargs="*", default=None)
ap.add_argument("--no-radar", action="store_true")
ap.add_argument("--tmin", type=float, default=None)
ap.add_argument("--tmax", type=float, default=None)
ap.add_argument("--tag", default="")
ap.add_argument("--de", type=int, default=440)
ap.add_argument("--gr", default="auto", help="auto: JPL g(r) if listed else inverse-square; marsden: Marsden comet law when JPL lists no g(r) parameters")
args = ap.parse_args()

t = time.time()
fit, libgrss, ver = C.import_grss(args.threads)
t_import = time.time() - t
des = args.des
raw, _, _ = C.fetch_sbdb(des)
el, cm, ng, meta = C.parse_sbdb(raw)
if args.gr == "marsden" and "ALN" not in meta["model_pars"]:
    ng.update({"alpha": 0.1112620426, "k": 4.6142, "m": 2.15, "n": 5.093, "r0_au": 2.808})
print("   g(r) used:", {k: ng[k] for k in ("alpha", "k", "m", "n", "r0_au")})
xml, _, _ = C.fetch_mpc_xml(des)
t = time.time()
obs, log = C.load_obs(fit, des, xml, args.tmin, args.tmax)
t_obs = time.time() - t
n_opt = len(obs)
n_rad = 0
if not args.no_radar and (meta["n_del"] or meta["n_dop"]):
    rad, new = C.fetch_radar(des)
    import grss.fit.fit_radar as FR
    FR.get_radar_raw_data = lambda _d: rad
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        obs = fit.add_radar_obs(obs, args.tmin, args.tmax, True)
    n_rad = len(obs) - n_opt
    log += buf.getvalue()
tt = obs["obsTimeMJD"].astype(float)
jpl_ng = [k for k in ("a1", "a2", "a3") if k in el]
print(f"== {des}  GRSS {ver}  threads={args.threads}  import {t_import:.2f}s  obs prep {t_obs:.2f}s")
print(f"   MPC optical rows {n_opt}, radar rows {n_rad}, arc {tt.max()-tt.min():.1f} d ({tt.min():.2f}..{tt.max():.2f}); "
      f"JPL: orbit {meta['orbit_id']} soln {meta['soln_date']} n_obs {meta['n_obs_used']} del/dop {meta['n_del']}/{meta['n_dop']} arc {meta['data_arc']} d, epoch MJD {el['t']}")
print("   " + " | ".join(l.strip() for l in log.splitlines() if l.strip()))
jsig = {k: float(np.sqrt(cm[list(meta["cov_labels"]).index(k.upper()), list(meta["cov_labels"]).index(k.upper())])) for k in jpl_ng}
print("   JPL non-grav:", {k: (el[k], jsig[k], round(abs(el[k]) / jsig[k], 1)) for k in jpl_ng})

models = [m.split(",") if m else [] for m in (args.models if args.models is not None else ["", ",".join(jpl_ng)])]
res = {"des": des, "grss": ver, "threads": args.threads, "t_import_s": round(t_import, 2), "t_obs_prep_s": round(t_obs, 2),
       "n_optical": n_opt, "n_radar": n_rad, "arc_d": float(tt.max() - tt.min()), "jpl": {"epoch": el["t"], "ng": {k: el[k] for k in jpl_ng},
       "sig": jsig, "meta": meta}, "fits": {}, "tmin": args.tmin, "tmax": args.tmax}
el6 = {k: el[k] for k in ("t",) + C.BASE}
for est in models:
    est = [k for k in est if k]
    label = "+".join(est) if est else "6p"
    r, fs = C.run_fit(fit, el6, obs, ng, est=est, de=args.de, quiet=False)
    res["fits"][label] = {k: v for k, v in r.items() if k != "log"}
    if "error" in r:
        print(f"[{label}] ERROR {r['error']}"); continue
    print(f"[{label:8s}] wall {r['wall_s']:6.2f}s iters {r['n_iter']:2d} conv {r['converged']} chi2 {r['chi2']:.2f} red {r['red_chi2']:.4f} "
          f"rms_w {r['rms_w']:.3f} rejected {r['n_rej']}/{r['n_rows']}")
    for k in est:
        v, s = r["x"][k], r["sig"][k]
        line = f"      {k} = {v:+.4e} +- {s:.3e} (S/N {abs(v)/s:.1f})"
        if k in jsig:
            line += f" | JPL {el[k]:+.4e} +- {jsig[k]:.3e} (S/N {abs(el[k])/jsig[k]:.1f}) | diff {(v-el[k])/np.hypot(s, jsig[k]):+.2f} comb-sigma, {(v-el[k])/jsig[k]:+.2f} JPL-sigma, ratio {v/el[k]:.3f}, sigma ratio {s/jsig[k]:.2f}"
        if k == "a1":
            line += f" | A/m = {C.amr_from_a1(v):.2e} +- {C.amr_from_a1(s):.1e} m2/kg (C_R=1)"
        print(line)
res["t_total_s"] = round(time.time() - t00, 2)
print(f"   total wall {res['t_total_s']} s")
json.dump(res, open(os.path.join(C.OUT, "repro_%s%s.json" % (C.stem(des), args.tag)), "w"), indent=1, default=float)
