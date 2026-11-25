"""Step 2: injection-recovery of a radial 1/r^2 acceleration (A1, solar radiation pressure) with GRSS 4.6.0.

For one object:
  (i)  real data: gravity-only (6p) fit, A1 (7p) fit, A1+A2 (8p) fit, all non-gravs started at zero;
  (ii) synthetic data at the REAL observation times, stations and weights. Truth orbit = real gravity-only
       best-fit elements + injected A1. Noiseless synthetic positions are obtained by evaluating GRSS's own
       observation model at the truth orbit (one pass of FitSimulation) and subtracting the residuals from the
       real positions, so light time, debiasing and station geometry are identical to the real fit.
       Noise models:
         gauss : independent Gaussian, covariance = s^2 * (per-observation covariance GRSS actually used in the
                 real fit: Veres 2017 weights, sqrt(N/4) de-weighting, timing inflation), s = real normalised
                 residual RMS of the accepted observations in the real A1 fit;
         wild  : the real residual vectors of the real A1 fit, multiplied by a random sign per same-station
                 same-night tracklet (keeps the real within-night correlation and the real tails).
       Observations rejected in the real A1 fit are left out of the synthetic sets.
  (iii) refit every trial with the same pipeline (outlier rejection on), A1 started at zero.
usage: fr_inject.py "<des>" [--ntrial 100] [--nproc 28] [--est a1|a1,a2] [--noise gauss wild] [--albedo 0.15] [--seed 7]
       [--tmin MJD --tmax MJD] [--tag TAG] [--dens 500 1200 2500 7500]
"""
import sys, os, json, time, argparse, importlib.util, multiprocessing as mp
spec = importlib.util.spec_from_file_location("fr_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fr_common.py"))
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("des")
ap.add_argument("--ntrial", type=int, default=100)
ap.add_argument("--nproc", type=int, default=28)
ap.add_argument("--est", default="a1")
ap.add_argument("--noise", nargs="*", default=["gauss", "wild"])
ap.add_argument("--albedo", type=float, default=0.15)
ap.add_argument("--seed", type=int, default=7)
ap.add_argument("--tmin", type=float, default=None)
ap.add_argument("--tmax", type=float, default=None)
ap.add_argument("--tag", default="")
ap.add_argument("--dens", nargs="*", type=float, default=[500.0, 1200.0, 2500.0, 7500.0])
ap.add_argument("--H", type=float, default=None)
args = ap.parse_args()
EST = [k for k in args.est.split(",") if k]

fit, libgrss, ver = C.import_grss(1)
des = args.des
raw, _, _ = C.fetch_sbdb(des)
el, cm, ng, meta = C.parse_sbdb(raw)
xml, _, _ = C.fetch_mpc_xml(des)
obs, log = C.load_obs(fit, des, xml, args.tmin, args.tmax)
if (obs["mode"] == "RAD").any():
    raise SystemExit("radar rows present; this script simulates optical only")
H = args.H if args.H is not None else meta["H"]
D = C.diameter_m(H, args.albedo)
tt = obs["obsTimeMJD"].astype(float)
arc = float(tt.max() - tt.min())
el6 = {k: el[k] for k in ("t",) + C.BASE}
print(f"== {des} GRSS {ver}: H {H}, D {D:.2f} m at albedo {args.albedo}; {len(obs)} optical rows, arc {arc:.1f} d; JPL model pars {meta['model_pars']}")

# ---------- (i) real-data fits
real = {}
r6, _ = C.run_fit(fit, el6, obs, ng, est=[]); real["6p"] = r6
r7, fs7 = C.run_fit(fit, el6, obs, ng, est=["a1"], keep=True); real["a1"] = r7
r8, _ = C.run_fit(fit, el6, obs, ng, est=["a1", "a2"]); real["a1+a2"] = r8
for lab, r in real.items():
    if "error" in r:
        print(f"[real {lab}] ERROR {r['error']}"); continue
    line = f"[real {lab:6s}] wall {r['wall_s']:.2f}s iters {r['n_iter']} conv {r['converged']} chi2 {r['chi2']:.2f} red {r['red_chi2']:.3f} rms_w {r['rms_w']:.3f} rej {r['n_rej']}/{r['n_rows']}"
    for k in r["est"]:
        line += f" | {k} {r['x'][k]:+.3e} +- {r['sig'][k]:.2e} (S/N {abs(r['x'][k])/r['sig'][k]:.2f})"
    print(line)
if fs7 is None or not r7.get("converged") or not r6.get("converged"):
    raise SystemExit("real fit failed or did not converge; cannot run injection")

# ---------- base table: accepted rows of the real A1 fit, with the covariance GRSS actually used
ob = fs7.obs.copy()
covs = np.array([np.asarray(c) for c in fs7.obs_cov])
ob["n_c11"] = covs[:, 0, 0]; ob["n_c12"] = covs[:, 0, 1]; ob["n_c22"] = covs[:, 1, 1]
ob["r_ra"] = ob["resRA"].astype(float); ob["r_dec"] = ob["resDec"].astype(float)
acc = ~ob["selAst"].isin(["D", "d"])
ob = ob[acc].reset_index(drop=True)
# tracklet ids: same station, within 8 h of the first observation of the batch (GRSS de-weighting rule)
trk = np.zeros(len(ob), dtype=int); t0 = ob["obsTimeMJD"].values[0]; cur = 0
stn = ob["stn"].values; tm = ob["obsTimeMJD"].values
for i in range(1, len(ob)):
    if not (tm[i] - t0 < 8 / 24 and stn[i] == stn[i - 1]):
        cur += 1; t0 = tm[i]
    trk[i] = cur
ob["trk"] = trk
chi = np.array([np.array([a, b]) @ np.linalg.inv(np.array([[c11, c12], [c12, c22]])) @ np.array([a, b])
                for a, b, c11, c12, c22 in zip(ob.r_ra, ob.r_dec, ob.n_c11, ob.n_c12, ob.n_c22)])
s_scale = float(np.sqrt(chi.sum() / (2 * len(ob))))
print(f"   accepted rows {len(ob)} of {len(acc)}, tracklets {cur+1}, nights {len(set(np.floor(tm).astype(int)))}; real normalised residual RMS s = {s_scale:.3f}; "
      f"median sigRA {np.median(ob.sigRA):.2f}\" median |res| {np.median(np.hypot(ob.r_ra, ob.r_dec)):.2f}\"")

# ---------- truth orbits and noiseless synthetic positions
truth_el = {"t": r6["t"], **{k: r6["x"][k] for k in C.BASE}}
levels = [("null", 0.0, None)] + [("rho%d" % rho, C.a1_from_density(rho, D), rho) for rho in sorted(args.dens, reverse=True)]
BASES = {}
for name, a1inj, rho in levels:
    rr, fsT = C.run_fit(fit, truth_el, ob, ng, est=[], n_iter_max=1, reject=False, keep=True, fixed={"a1": a1inj}, damp=lambda i: 0.0)
    b = fsT.obs.copy()
    b["ra"] = b["ra"] - b["resRA"] / (3600.0 * b["cosDec"])
    b["dec"] = b["dec"] - b["resDec"] / 3600.0
    b["selAst"] = "A"
    BASES[name] = b
# self-check: noiseless set must give ~zero residuals at the truth orbit
name, a1inj, rho = levels[-1]
rr, fsC = C.run_fit(fit, truth_el, BASES[name], ng, est=[], n_iter_max=1, reject=False, keep=True, fixed={"a1": a1inj}, damp=lambda i: 0.0)
print(f"   self-check ({name}, A1 {a1inj:.3e}): max |residual| of noiseless set at truth = {np.nanmax(np.abs(fsC.obs[['resRA','resDec']].values)):.2e} arcsec")
# displacement caused by the largest injection relative to gravity-only truth (arcsec, at fixed elements)
d = np.hypot((BASES[name]["ra"].values - BASES["null"]["ra"].values) * 3600 * BASES["null"]["cosDec"].values,
             (BASES[name]["dec"].values - BASES["null"]["dec"].values) * 3600)
print(f"   sky displacement of {name} vs gravity-only at fixed elements: median {np.median(d):.3f}\" max {d.max():.2f}\"")


def trial(task):
    lname, a1inj, noise, j = task
    rng = np.random.default_rng([args.seed, [l[0] for l in levels].index(lname), {"gauss": 1, "wild": 2}[noise], j])
    b = BASES[lname].copy()
    n = len(b)
    if noise == "gauss":
        z = rng.standard_normal((n, 2))
        c11 = b.n_c11.values; c12 = b.n_c12.values; c22 = b.n_c22.values
        l11 = np.sqrt(c11); l21 = c12 / l11; l22 = np.sqrt(np.maximum(c22 - l21 ** 2, 0))
        nra = s_scale * (l11 * z[:, 0]); ndec = s_scale * (l21 * z[:, 0] + l22 * z[:, 1])
    else:
        ntrk = int(b.trk.max()) + 1
        sgn = rng.choice([-1.0, 1.0], size=ntrk)[b.trk.values]
        nra = sgn * b.r_ra.values; ndec = sgn * b.r_dec.values
    b["ra"] = b["ra"] + nra / (3600.0 * b["cosDec"])
    b["dec"] = b["dec"] + ndec / 3600.0
    r, _ = C.run_fit(fit, truth_el, b, ng, est=EST)
    if "error" in r:
        return {"level": lname, "noise": noise, "j": j, "error": r["error"]}
    o = {"level": lname, "noise": noise, "j": j, "conv": r["converged"], "n_iter": r["n_iter"], "n_rej": r["n_rej"],
         "red_chi2": r["red_chi2"], "wall": r["wall_s"]}
    for k in EST:
        o[k] = r["x"][k]; o["s_" + k] = r["sig"][k]
    return o


tasks = [(name, a1inj, noise, j) for noise in args.noise for name, a1inj, rho in levels for j in range(args.ntrial)]
t = time.time()
with mp.get_context("fork").Pool(args.nproc) as pool:
    outs = pool.map(trial, tasks, chunksize=2)
wall = time.time() - t
print(f"   {len(tasks)} synthetic fits on {args.nproc} processes: {wall:.1f} s wall, median per-fit {np.median([o['wall'] for o in outs if 'wall' in o]):.2f} s, "
      f"errors {sum(1 for o in outs if 'error' in o)}, non-converged {sum(1 for o in outs if o.get('conv') is False)}")

summary = []
print(f"   estimating {EST}; detection = |A1|/sigma_formal >= 3; 'pos' = A1/sigma >= +3; 'resc' = sigma rescaled by sqrt(reduced chi2)")
print("   noise level      rho   A1_inj     A/m_inj   n  conv  mean(A1)    median     std(A1)   mean(sig)  pull_sd  det3   pos3   det3_resc  inj/sig")
for noise in args.noise:
    for name, a1inj, rho in levels:
        oo = [o for o in outs if o["noise"] == noise and o["level"] == name and "error" not in o]
        cv = [o for o in oo if o["conv"]]
        if not cv:
            print(f"   {noise:5s} {name:8s} no converged trials"); continue
        a = np.array([o["a1"] for o in cv]); sg = np.array([o["s_a1"] for o in cv]); rc = np.array([o["red_chi2"] for o in cv])
        snr = a / sg
        row = {"noise": noise, "level": name, "rho": rho, "a1_inj": a1inj, "amr_inj": C.amr_from_a1(a1inj), "n": len(oo), "n_conv": len(cv),
               "mean": float(a.mean()), "median": float(np.median(a)), "std": float(a.std(ddof=1)), "mean_sig": float(sg.mean()),
               "pull_sd": float(((a - a1inj) / sg).std(ddof=1)), "det3": float((np.abs(snr) >= 3).mean()), "pos3": float((snr >= 3).mean()),
               "det3_resc": float((np.abs(snr) / np.sqrt(rc) >= 3).mean()), "inj_over_sig": float(a1inj / sg.mean()),
               "mean_rej": float(np.mean([o["n_rej"] for o in cv]))}
        if "a2" in EST:
            a2 = np.array([o["a2"] for o in cv]); s2 = np.array([o["s_a2"] for o in cv])
            row.update({"a2_mean": float(a2.mean()), "a2_std": float(a2.std(ddof=1)), "a2_mean_sig": float(s2.mean()), "a2_det3": float((np.abs(a2 / s2) >= 3).mean())})
        summary.append(row)
        print(f"   {noise:5s} {name:8s} {str(rho):>6s} {a1inj:9.2e} {row['amr_inj']:9.2e} {len(oo):3d} {len(cv):4d} {row['mean']:+10.2e} {row['median']:+10.2e} {row['std']:9.2e} {row['mean_sig']:9.2e} "
              f"{row['pull_sd']:7.2f} {row['det3']:6.2f} {row['pos3']:6.2f} {row['det3_resc']:9.2f} {row['inj_over_sig']:8.2f}"
              + (f" | a2 mean {row['a2_mean']:+.2e} std {row['a2_std']:.2e} det3 {row['a2_det3']:.2f}" if "a2" in EST else ""))
res = {"des": des, "H": H, "albedo": args.albedo, "D_m": D, "arc_d": arc, "n_rows": int(len(obs)), "n_accepted": int(len(ob)), "n_tracklets": int(cur + 1),
       "s_scale": s_scale, "real": real, "levels": [(n, a, r) for n, a, r in levels], "est": EST, "ntrial": args.ntrial, "summary": summary,
       "wall_s": wall, "trials": outs, "tmin": args.tmin, "tmax": args.tmax}
json.dump(res, open(os.path.join(C.OUT, "inject_%s_%s%s.json" % (C.stem(des), "+".join(EST), args.tag)), "w"), indent=1, default=float)
