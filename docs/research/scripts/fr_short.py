"""Step 4: short arcs. For each object run 6-parameter and A1 fits under several start/step variants and report
convergence. usage: fr_short.py [--set short|srp|null] [--des "<des>" ...] [--variants base it100 ...] [--verbose]
Variants:
  base    cometary elements at the JPL covariance epoch, 20 iterations (the first-round configuration)
  it100   same, 100 iterations
  cart    barycentric Cartesian state at the JPL epoch
  mid     barycentric Cartesian state at the mid-point of the observed arc (JPL orbit propagated there by GRSS)
  damp    cometary, Gauss-Newton step scaled by 0.3, 0.5, 0.7 in the first three iterations, then 1
  half    cometary, every Gauss-Newton step scaled by 0.5, 60 iterations
  prior   cometary, a priori constraint on the six elements: JPL elements, 10 x JPL sigma
"""
import sys, os, json, time, argparse, importlib.util, warnings, io, contextlib
warnings.filterwarnings("ignore")
spec = importlib.util.spec_from_file_location("fr_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fr_common.py"))
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--set", default="short")
ap.add_argument("--des", nargs="*", default=None)
ap.add_argument("--variants", nargs="*", default=["base", "it100", "cart", "mid", "damp", "half", "prior"])
ap.add_argument("--est", nargs="*", default=["", "a1"])
ap.add_argument("--verbose", action="store_true")
ap.add_argument("--tag", default="")
args = ap.parse_args()
fit, libgrss, ver = C.import_grss(1)
from grss.utils import default_kernel_path

picks = json.load(open(os.path.join(C.OUT, "picks.json")))
objs = [{"des": d} for d in args.des] if args.des else picks[args.set]


def propagate(el, ng, t_target, de=440):
    """Barycentric Cartesian state at t_target (MJD TDB) of the orbit given by cometary elements el at el['t']."""
    sim = libgrss.PropSimulation("p", el["t"], de, default_kernel_path)
    sim.set_integration_parameters(t_target)
    p = libgrss.NongravParameters()
    p.a1 = 0.0; p.a2 = 0.0; p.a3 = 0.0; p.alpha = 1.0; p.k = 0.0; p.m = 2.0; p.n = 0.0; p.r0_au = 1.0
    b = libgrss.IntegBody("b", el["t"], 0.0, 0.0, [el[k] for k in C.BASE], p)
    b.caTol = 0.0
    sim.add_integ_body(b)
    if abs(t_target - el["t"]) < 1e-9:
        return list(sim.integBodies[0].initCart) if hasattr(sim.integBodies[0], "initCart") else None
    with contextlib.redirect_stdout(io.StringIO()):
        sim.integrate()
    return list(sim.xInteg)[:6]


rows = []
for o in objs:
    des = o["des"]
    try:
        raw, _, _ = C.fetch_sbdb(des); el, cm, ng, meta = C.parse_sbdb(raw); xml, _, _ = C.fetch_mpc_xml(des)
        obs, _ = C.load_obs(fit, des, xml)
    except Exception as e:
        print(f"{des}: LOAD ERROR {e!r}"); continue
    tt = obs["obsTimeMJDTDB"].astype(float)
    arc = float(tt.max() - tt.min()); tmid = float(0.5 * (tt.max() + tt.min()))
    nights = len(set(np.floor(obs["obsTimeMJD"].astype(float) + 0.5).astype(int)))
    el6 = {k: el[k] for k in ("t",) + C.BASE}
    sigj = np.sqrt(np.abs(np.diag(cm)))[:6]
    print(f"== {des}: H {meta['H']} arc {arc:.2f} d, {len(obs)} positions, {nights} nights; JPL epoch {el['t']} (arc MJD {tt.min():.2f}..{tt.max():.2f}), JPL cond {meta['condition_code']}", flush=True)
    for v in args.variants:
        for m in args.est:
            est = [k for k in m.split(",") if k]
            kw = dict(est=est, n_iter_max=20, quiet=not args.verbose)
            start = el6
            try:
                if v == "it100":
                    kw["n_iter_max"] = 100
                elif v == "cart":
                    st = propagate(el6, ng, el6["t"] + 1e-6)
                    start = {"t": el6["t"] + 1e-6, **dict(zip(("x", "y", "z", "vx", "vy", "vz"), st))}
                elif v == "mid":
                    st = propagate(el6, ng, tmid)
                    start = {"t": tmid, **dict(zip(("x", "y", "z", "vx", "vy", "vz"), st))}
                elif v == "damp":
                    kw["damp"] = lambda i: {1: 0.3, 2: 0.5, 3: 0.7}.get(i, 1.0)
                    kw["n_iter_max"] = 40
                elif v == "half":
                    kw["damp"] = lambda i: 0.5
                    kw["n_iter_max"] = 60
                elif v == "prior":
                    kw["prior"] = ({k: el6[k] for k in C.BASE}, {k: 10 * float(s) for k, s in zip(C.BASE, sigj)})
                r, _ = C.run_fit(fit, start, obs, ng, **kw)
            except Exception as e:
                r = {"error": repr(e)[:200]}
            row = {"des": des, "arc": arc, "n": len(obs), "nights": nights, "variant": v, "model": m or "6p", "bin": o.get("bin")}
            if "error" in r:
                row["error"] = r["error"]
                print(f"   {v:6s} [{m or '6p':3s}] ERROR {r['error'][:150]}", flush=True)
            else:
                row.update({"conv": r["converged"], "n_iter": r["n_iter"], "red": r["red_chi2"], "rms_w": r["rms_w"], "n_rej": r["n_rej"], "wall": r["wall_s"],
                            "rms_tail": r["rms_hist"][-4:], "warn": r["warn"][:2]})
                if "a1" in est:
                    row["a1"] = r["x"]["a1"]; row["s_a1"] = r["sig"]["a1"]
                print(f"   {v:6s} [{m or '6p':3s}] conv {str(r['converged']):5s} it {r['n_iter']:3d} rej {r['n_rej']:3d}/{r['n_rows']} red {r['red_chi2']:.3g} rms_w tail {['%.4f' % q for q in r['rms_hist'][-4:]]} wall {r['wall_s']:.2f}s"
                      + (f" a1 {r['x']['a1']:+.2e}+-{r['sig']['a1']:.1e}" if "a1" in est else "") + (f" WARN {r['warn'][0][:80]}" if r["warn"] else ""), flush=True)
                if args.verbose:
                    print(r.get("log", "")[-3000:])
            rows.append(row)
json.dump(rows, open(os.path.join(C.OUT, "short_%s%s.json" % (args.set if not args.des else "custom", args.tag)), "w"), indent=1, default=float)
# summary
print("\nSUMMARY: converged / attempted by variant and model")
for v in args.variants:
    for m in args.est:
        rr = [r for r in rows if r["variant"] == v and r["model"] == (m or "6p")]
        print(f"   {v:6s} [{m or '6p':3s}] {sum(1 for r in rr if r.get('conv'))}/{len(rr)}  errors {sum(1 for r in rr if 'error' in r)}")
