"""Step 4b: 2020 CD3 (temporarily captured). Bounded set of experiments.
usage: fr_cd3.py [exp ...]   exps: base cartjpl stage
"""
import sys, os, json, time, importlib.util, warnings, io, contextlib
warnings.filterwarnings("ignore")
spec = importlib.util.spec_from_file_location("fr_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fr_common.py"))
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
import numpy as np
fit, libgrss, ver = C.import_grss(1)
from grss.utils import default_kernel_path
des = "2020 CD3"
raw, _, _ = C.fetch_sbdb(des); el, cm, ng, meta = C.parse_sbdb(raw); xml, _, _ = C.fetch_mpc_xml(des)
obs, log = C.load_obs(fit, des, xml)
tt = obs["obsTimeMJDTDB"].astype(float)
A1J = meta["model_pars"]["A1"]; A1S = meta["model_sig"]["A1"]
el6 = {k: el[k] for k in ("t",) + C.BASE}
print(f"== {des}: {len(obs)} positions MJD {tt.min():.2f}..{tt.max():.2f}; JPL epoch {el['t']}, JPL A1 {A1J:.4e} +- {A1S:.2e}, n_obs {meta['n_obs_used']}, rms {meta['rms']}")
print("   JPL elements:", {k: el6[k] for k in C.BASE})
exps = sys.argv[1:] or ["base", "cartjpl", "stage"]
ANALYTIC = "analytic" in exps
DAMP = (lambda i: 0.5) if "half" in exps else None


def propagate(el, a1, t_target, de=440):
    sim = libgrss.PropSimulation("p", el["t"], de, default_kernel_path)
    sim.set_integration_parameters(t_target)
    p = libgrss.NongravParameters()
    p.a1 = a1; p.a2 = 0.0; p.a3 = 0.0; p.alpha = 1.0; p.k = 0.0; p.m = 2.0; p.n = 0.0; p.r0_au = 1.0
    b = libgrss.IntegBody("b", el["t"], 0.0, 0.0, [el[k] for k in C.BASE], p)
    b.caTol = 0.0
    sim.add_integ_body(b)
    with contextlib.redirect_stdout(io.StringIO()):
        sim.integrate()
    return list(sim.xInteg)[:6]


def show(label, r):
    if "error" in r:
        print(f"[{label}] ERROR {r['error']} | {r.get('log','')[-300:]}"); return
    s = f"[{label}] conv {r['converged']} it {r['n_iter']} rej {r['n_rej']}/{r['n_rows']} red {r['red_chi2']:.3g} rms_w {r['rms_w']:.3f} rms_u {r['rms_u']:.3f}\" wall {r['wall_s']:.1f}s rms_hist {['%.3g' % q for q in r['rms_hist'][:3]]}..{['%.3g' % q for q in r['rms_hist'][-3:]]}"
    if "a1" in r["x"]:
        v, sg = r["x"]["a1"], r["sig"]["a1"]
        s += f" | a1 {v:+.4e} +- {sg:.2e} (S/N {abs(v)/sg:.1f}); JPL {A1J:.4e} +- {A1S:.2e}; diff {(v-A1J)/np.hypot(sg, A1S):+.2f} comb-sigma"
    if r["warn"]:
        s += f" | WARN x{len(r['warn'])}: {r['warn'][0][:70]}"
    print(s, flush=True)


if "base" in exps:
    # first-round configuration: cometary at the JPL epoch
    r, _ = C.run_fit(fit, el6, obs, ng, est=[], fixed={"a1": A1J}, n_iter_max=1, reject=False, damp=lambda i: 0.0)
    show("cometary, JPL elements + JPL A1 fixed, residuals only", r)
    r, _ = C.run_fit(fit, el6, obs, ng, est=["a1"], start={"a1": A1J}, n_iter_max=20)
    show("cometary, A1 est from JPL value, full arc", r)
    r, _ = C.run_fit(fit, el6, obs, ng, est=["a1"], n_iter_max=20)
    show("cometary, A1 est from zero, full arc", r)
if "cartjpl" in exps:
    st = propagate(el6, A1J, el6["t"] + 1e-6)
    c0 = {"t": el6["t"] + 1e-6, **dict(zip(("x", "y", "z", "vx", "vy", "vz"), st))}
    r, _ = C.run_fit(fit, c0, obs, ng, est=[], fixed={"a1": A1J}, n_iter_max=1, reject=False, damp=lambda i: 0.0)
    show("cartesian at JPL epoch, JPL A1 fixed, residuals only", r)
    r, _ = C.run_fit(fit, c0, obs, ng, est=["a1"], start={"a1": A1J}, n_iter_max=30)
    show("cartesian at JPL epoch, A1 est from JPL value, full arc", r)
    r, _ = C.run_fit(fit, c0, obs, ng, est=["a1"], n_iter_max=30)
    show("cartesian at JPL epoch, A1 est from zero, full arc", r)
if "stage" in exps:
    # staged: fit the 2020 apparition only (Cartesian, epoch inside it), then add earlier clusters one at a time
    st = propagate(el6, A1J, el6["t"] + 1e-6)
    cur = {"t": el6["t"] + 1e-6, **dict(zip(("x", "y", "z", "vx", "vy", "vz"), st))}
    a1cur = 0.0
    for label, tmin in (("2020 apparition only (MJD >= 58890)", 58890.0), ("+ 2019 Jan precovery (MJD >= 58400)", 58400.0), ("+ 2018 May precovery (full arc)", None)):
        o, _ = C.load_obs(fit, des, xml, tmin, None)
        for est, startv in ((["a1"], {"a1": a1cur}),):
            r, _ = C.run_fit(fit, cur, o, ng, est=est, start=startv, n_iter_max=60 if DAMP else 40, analytic=ANALYTIC, damp=DAMP)
            show(f"stage {label}; A1 start {a1cur:.2e}; {len(o)} positions", r)
        if "error" not in r and r["converged"]:
            cur = {"t": r["t"], **{k: r["x"][k] for k in ("x", "y", "z", "vx", "vy", "vz")}}
            a1cur = r["x"]["a1"]
        else:
            print("   stage did not converge; continuing from the previous converged state")
