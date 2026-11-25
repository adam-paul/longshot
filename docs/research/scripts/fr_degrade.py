"""Step 3: degrade a known object. Cut the MPC astrometry to its first N days, refit (non-gravs from zero),
and test whether the truncated-arc interval for A1 covers (a) the full-arc value of the same model,
(b) the full-arc A1+A2 value (the model JPL adopted), (c) JPL's value.
The same-night de-weighting is recomputed on the truncated set, as a real short-arc fit would do.
usage: fr_degrade.py "<des>" --cuts 30 60 120 [--models a1 a1,a2] [--iters 20] [--no-radar]
"""
import sys, os, json, time, argparse, importlib.util, warnings, io, contextlib
warnings.filterwarnings("ignore")
spec = importlib.util.spec_from_file_location("fr_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fr_common.py"))
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("des")
ap.add_argument("--cuts", nargs="*", type=float, default=[30, 60, 120])
ap.add_argument("--models", nargs="*", default=["a1", "a1,a2"])
ap.add_argument("--iters", type=int, default=20)
ap.add_argument("--no-radar", action="store_true")
args = ap.parse_args()
fit, libgrss, ver = C.import_grss(1)
des = args.des
raw, _, _ = C.fetch_sbdb(des)
el, cm, ng, meta = C.parse_sbdb(raw)
xml, _, _ = C.fetch_mpc_xml(des)
full, _ = C.load_obs(fit, des, xml)
t0 = float(full["obsTimeMJDTDB"].min()); t1 = float(full["obsTimeMJDTDB"].max())
el6 = {k: el[k] for k in ("t",) + C.BASE}
jsig = {k: float(np.sqrt(cm[list(meta["cov_labels"]).index(k.upper()), list(meta["cov_labels"]).index(k.upper())])) for k in ("a1", "a2") if k in el}
D = C.diameter_m(meta["H"], 0.15)
use_radar = (not args.no_radar) and bool(meta["n_del"] or meta["n_dop"])
print(f"== {des}: H {meta['H']} (D {D:.1f} m at albedo 0.15); MPC rows {len(full)}, arc {t1-t0:.1f} d from MJD {t0:.2f}; JPL epoch {el['t']}, JPL arc {meta['data_arc']} d, radar used here: {use_radar}; JPL ng "
      + ", ".join(f"{k} {el[k]:+.3e}+-{jsig[k]:.2e}" for k in jsig))
res = {"des": des, "rows": []}
ref = {}
for cut in [None] + list(args.cuts):
    tmax = None if cut is None else t0 + cut
    obs, _ = C.load_obs(fit, des, xml, None, tmax)
    if use_radar:
        rad, _new = C.fetch_radar(des)
        import grss.fit.fit_radar as FR
        FR.get_radar_raw_data = lambda _d: rad
        with contextlib.redirect_stdout(io.StringIO()):
            obs = fit.add_radar_obs(obs, None, tmax, False)
    tt = obs["obsTimeMJD"].astype(float)
    nights = len(set(np.floor(tt + 0.5).astype(int)))
    for m in args.models:
        est = [k for k in m.split(",") if k]
        r, _ = C.run_fit(fit, el6, obs, ng, est=est, n_iter_max=args.iters)
        row = {"cut": cut, "model": m, "n_rows": len(obs), "arc_d": float(tt.max() - tt.min()), "nights": nights}
        if "error" in r:
            row["error"] = r["error"]; print(f"  cut {cut} [{m}] ERROR {r['error']}"); res["rows"].append(row); continue
        row.update({"conv": r["converged"], "n_iter": r["n_iter"], "red_chi2": r["red_chi2"], "n_rej": r["n_rej"], "wall": r["wall_s"],
                    "x": {k: r["x"][k] for k in est}, "sig": {k: r["sig"][k] for k in est}})
        if cut is None:
            ref[m] = row
        a, s = r["x"]["a1"], r["sig"]["a1"]
        s_resc = s * np.sqrt(r["red_chi2"])
        line = (f"  {'full' if cut is None else 'first %4.0f d' % cut:13s} [{m:5s}] rows {len(obs):4d} arc {row['arc_d']:6.1f} d nights {nights:3d} conv {str(r['converged']):5s} it {r['n_iter']:2d} "
                f"rej {r['n_rej']:3d} red {r['red_chi2']:.3f} | a1 {a:+.3e} +- {s:.2e} (S/N {abs(a)/s:5.2f}; rescaled sigma {s_resc:.2e})")
        if "a2" in est:
            line += f" a2 {r['x']['a2']:+.2e} +- {r['sig']['a2']:.1e}"
        if cut is not None:
            for lab, m2 in (("same-model full", m), ("A1+A2 full", "a1,a2")):
                if m2 in ref:
                    fa = ref[m2]["x"]["a1"]
                    z = (fa - a) / s; zr = (fa - a) / s_resc
                    row["z_" + lab.replace(" ", "_")] = z; row["zr_" + lab.replace(" ", "_")] = zr
                    line += f" | {lab} at {z:+.2f} s (formal), {zr:+.2f} s (rescaled)"
        if "a1" in jsig:
            zj = (el["a1"] - a) / s
            row["z_jpl"] = zj
            line += f" | JPL at {zj:+.2f} s"
        up = max(a, 0) + 3 * s
        row["rho_min_3s"] = 1.5 * C.SRP_1AU * C.MS2_TO_AUD2 / (D * up)
        line += f" | sigma(A/m) {C.amr_from_a1(s):.1e} m2/kg, rho > {row['rho_min_3s']:.0f} kg/m3 from the 3s upper limit"
        print(line, flush=True)
        res["rows"].append(row)
json.dump(res, open(os.path.join(C.OUT, "degrade_%s.json" % C.stem(des)), "w"), indent=1, default=float)
