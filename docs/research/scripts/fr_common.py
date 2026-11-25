"""Shared helpers for the fr_* orbit-fit verification scripts (GRSS 4.6.0).

Load with importlib from an explicit path; do not put the scripts directory on sys.path.
All network fetches are sequential, cached on disk, and carry only a generic client name.
"""
import os, sys, json, time, io, contextlib, hashlib, pickle
import urllib.request, urllib.parse

# the unpacked research archive, data/research under the repository root (AGENTS.md)
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "data", "research"))
P2 = os.path.join(ROOT, "probe-fit2")
DL_MPC = os.path.join(P2, "dl", "mpc")
DL_SBDB = os.path.join(P2, "dl", "sbdb")
DL_RADAR = os.path.join(P2, "dl", "radar")
OUT = os.path.join(P2, "out")
UA = "orbit-fit-check/0.1 (python-urllib)"

AU_M = 1.495978707e11
# solar radiation pressure at 1 au: S0/c with S0 = 1361 W/m^2
SRP_1AU = 1361.0 / 299792458.0            # N/m^2
MS2_TO_AUD2 = 86400.0 ** 2 / AU_M         # 1 m/s^2 in au/d^2


def stem(des):
    return des.replace(" ", "_")


def import_grss(threads=1):
    """Import GRSS with OMP threads pinned (grss.utils.initialize() sets OMP_NUM_THREADS=cpu_count)."""
    vbin = os.path.dirname(sys.executable)
    os.environ["PATH"] = vbin + os.pathsep + os.environ.get("PATH", "")
    real = os.cpu_count
    os.cpu_count = lambda: threads
    try:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            from grss import fit, libgrss
            import grss
    finally:
        os.cpu_count = real
    os.environ["OMP_NUM_THREADS"] = str(threads)
    return fit, libgrss, grss.__version__


def fetch_mpc_xml(des, pause=2.0):
    """One MPC get-obs request per designation, cached. Returns (path, fetched_now, seconds)."""
    os.makedirs(DL_MPC, exist_ok=True)
    path = os.path.join(DL_MPC, stem(des) + ".xml")
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return path, False, 0.0
    body = json.dumps({"desigs": [des], "output_format": ["XML"]}).encode()
    req = urllib.request.Request("https://data.minorplanetcenter.net/api/get-obs", data=body, method="GET",
                                 headers={"Content-Type": "application/json", "User-Agent": UA})
    t = time.time()
    with urllib.request.urlopen(req, timeout=120) as r:
        raw = r.read()
    dt = time.time() - t
    d = json.loads(raw)[0]
    with open(path, "w") as f:
        f.write(d["XML"])
    time.sleep(pause)
    return path, True, dt


def fetch_sbdb(des, pause=2.0):
    """One JPL SBDB request (sequential), cached. Returns (dict, fetched_now, seconds)."""
    os.makedirs(DL_SBDB, exist_ok=True)
    path = os.path.join(DL_SBDB, stem(des) + ".json")
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return json.load(open(path)), False, 0.0
    url = "https://ssd-api.jpl.nasa.gov/sbdb.api?" + urllib.parse.urlencode(
        {"sstr": des, "cov": "mat", "phys-par": "true", "full-prec": "true"})
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    t = time.time()
    with urllib.request.urlopen(req, timeout=120) as r:
        raw = r.read()
    dt = time.time() - t
    d = json.loads(raw)
    if "orbit" not in d:
        raise RuntimeError("SBDB returned no orbit for %s: %s" % (des, str(d)[:200]))
    with open(path, "wb") as f:
        f.write(raw)
    time.sleep(pause)
    return d, True, dt


def fetch_radar(des, pause=2.0):
    """One JPL sb_radar request (sequential), cached raw JSON."""
    os.makedirs(DL_RADAR, exist_ok=True)
    path = os.path.join(DL_RADAR, stem(des) + ".json")
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return json.load(open(path)), False
    url = "https://ssd-api.jpl.nasa.gov/sb_radar.api?" + urllib.parse.urlencode({"des": des})
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        raw = r.read()
    with open(path, "wb") as f:
        f.write(raw)
    time.sleep(pause)
    return json.loads(raw), True


def parse_sbdb(raw):
    """Same parsing as grss.fit.get_sbdb_info, from a cached SBDB JSON (no extra requests).
    Returns elements dict (t = covariance epoch MJD TDB; angles in rad), covariance, nongrav dict, meta."""
    import numpy as np
    orb = raw["orbit"]
    cov = orb.get("covariance")
    if cov is not None:
        epoch_mjd = float(cov["epoch"]) - 2400000.5
        if epoch_mjd == float(orb["epoch"]) - 2400000.5:
            elem = orb["elements"]
        else:
            elem = cov["elements"]
    else:
        epoch_mjd = float(orb["epoch"]) - 2400000.5
        elem = orb["elements"]
    full = {e["name"]: float(e["value"]) for e in elem if e["value"] is not None}
    el = {"t": epoch_mjd}
    for k in ("e", "q", "tp", "om", "w", "i"):
        v = full[k]
        if k == "tp":
            v -= 2400000.5
        if k in ("om", "w", "i"):
            v *= np.pi / 180
        el[k] = v
    labels = cov["labels"] if cov is not None else []
    if cov is not None:
        cm = np.array(cov["data"]).astype(float)
        cm[3:6, :] *= np.pi / 180
        cm[:, 3:6] *= np.pi / 180
    else:
        cm = np.zeros((6, 6))
    mp = {p["name"]: float(p["value"]) for p in orb.get("model_pars", [])}
    mps = {p["name"]: (float(p["sigma"]) if p.get("sigma") not in (None, "") else None) for p in orb.get("model_pars", [])}
    keymap = {"A1": "a1", "A2": "a2", "A3": "a3", "DT": "dt", "ALN": "alpha", "NK": "k", "NM": "m", "NN": "n", "R0": "r0_au"}
    # inverse-square default (GRSS's own default is the Marsden comet law; not wanted for asteroids)
    ng = {"a1": 0.0, "a2": 0.0, "a3": 0.0, "dt": 0.0, "alpha": 1.0, "k": 0.0, "m": 2.0, "n": 0.0, "r0_au": 1.0}
    for K, k in keymap.items():
        if K in mp:
            ng[k] = mp[K]
        if K in labels:
            el[k] = mp[K]
    H = None; alb = None
    for p in raw.get("phys_par", []) or []:
        if p["name"] == "H":
            H = float(p["value"])
        if p["name"] == "albedo":
            alb = float(p["value"])
    ng["radius"] = 0.0 if H is None else 1329 * 10 ** (-0.2 * H) / (2 * (alb or 0.125) ** 0.5) * 1e3
    meta = {"H": H, "albedo": alb, "orbit_id": orb.get("orbit_id"), "soln_date": orb.get("soln_date"),
            "first_obs": orb.get("first_obs"), "last_obs": orb.get("last_obs"), "data_arc": orb.get("data_arc"),
            "n_obs_used": orb.get("n_obs_used"), "n_del": orb.get("n_del_obs_used"), "n_dop": orb.get("n_dop_obs_used"),
            "condition_code": orb.get("condition_code"), "rms": orb.get("rms"), "model_pars": mp, "model_sig": mps,
            "cov_labels": labels, "comment": orb.get("comment"), "pe_used": orb.get("pe_used")}
    return el, cm, ng, meta


def load_obs(fit, des, xml_path, tmin=None, tmax=None, verbose=False):
    """GRSS optical pipeline as used by the first-round probe: Eggl 2020 low-res debias,
    Veres 2017 weights, sqrt(N/4) same-night de-weighting, no elimination."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        obs = fit.get_optical_obs(des, xml_path, tmin, tmax, True, True, False, 4, True)
    if verbose:
        print(buf.getvalue())
    return obs, buf.getvalue()


def diameter_m(H, albedo=0.15):
    return 1329e3 / albedo ** 0.5 * 10 ** (-0.2 * H)


def a1_from_density(rho, D, cr=1.0):
    """A1 [au/d^2] (radial, 1/r^2, at 1 au) of a sphere of diameter D [m] and bulk density rho [kg/m^3]."""
    amr = 1.5 / (rho * D)
    return cr * SRP_1AU * amr * MS2_TO_AUD2


def amr_from_a1(a1, cr=1.0):
    """Area-to-mass ratio [m^2/kg] from A1 [au/d^2]."""
    return a1 / (cr * SRP_1AU * MS2_TO_AUD2)


BASE = ("e", "q", "tp", "om", "w", "i")


def run_fit(fit, el, obs_df, ng, est=(), start=None, n_iter_max=20, de=440, reject=True, prior=None,
            quiet=True, keep=False, fixed=None, damp=None, crit=None, analytic=False):
    """One GRSS least-squares fit. el: dict with t and state keys (cometary or cartesian).
    est: non-grav keys to estimate (started at 0 unless start gives values).
    ng: model dict (g(r) law, radius). A1/A2/A3 in it are IGNORED: every non-estimated non-grav
    amplitude is zero unless given in `fixed` (so a "6p" fit is truly gravity-only).
    prior: (prior_est dict, prior_sig dict) a priori constraints on estimated keys.
    damp: None, or a function(iteration_index) -> factor applied to the Gauss-Newton step.
    crit: None or [chi_reject, chi_recover].
    Returns (result dict, FitSimulation or None)."""
    import numpy as np
    x0 = {"t": el["t"]}
    keys = [k for k in ("x", "y", "z", "vx", "vy", "vz") if k in el] or list(BASE)
    for k in keys:
        x0[k] = el[k]
    for k in est:
        x0[k] = 0.0 if start is None else float(start.get(k, 0.0))
    n = len(x0) - 1
    cov0 = np.eye(n) * 1e-20
    ngf = dict(ng)
    for k in ("a1", "a2", "a3", "dt"):
        ngf[k] = 0.0
    if fixed:
        ngf.update(fixed)
    t = time.time()
    buf = io.StringIO()
    out = {"est": list(est), "n_par": n}
    try:
        with contextlib.redirect_stdout(buf):
            fs = fit.FitSimulation(x0, obs_df.copy(), cov0, n_iter_max=n_iter_max, de_kernel=de, nongrav_info=ngf)
            fs.reject_outliers = reject
            fs.analytic_partials = bool(analytic)
            if crit is not None:
                fs.reject_criteria = list(crit)
            if prior is not None:
                fs.prior_est, fs.prior_sig = prior
            if damp is not None:
                orig = fs._get_lsq_state_correction
                def damped(partials, residuals, _o=orig, _fs=fs):
                    return _o(partials, residuals) * damp(_fs.n_iter)
                fs._get_lsq_state_correction = damped
            fs.filter_lsq(verbose=not quiet)
    except Exception as e:  # noqa
        out.update({"error": repr(e)[:300], "wall_s": round(time.time() - t, 3), "log": buf.getvalue()[-2000:]})
        return out, None
    it = fs.iters[-1]
    ks = list(fs.x_nom.keys())
    sig = np.sqrt(np.abs(np.diag(fs.covariance)))
    out.update({"wall_s": round(time.time() - t, 3), "n_iter": int(fs.n_iter), "converged": bool(fs.converged),
                "chi2": float(it.chi_squared), "red_chi2": float(it.reduced_chi_squared),
                "rms_w": float(it.weighted_rms), "rms_u": float(it.unweighted_rms),
                "n_rej": int(fs.num_rejected), "n_scalar": int(fs.n_obs), "n_rows": int(len(fs.obs)),
                "x": {k: float(fs.x_nom[k]) for k in ks}, "sig": {k: float(s) for k, s in zip(ks, sig)},
                "t": float(fs.t_sol), "rms_hist": [float(i.weighted_rms) for i in fs.iters[1:]],
                "warn": [l for l in buf.getvalue().splitlines() if "WARN" in l or "did not converge" in l][:5]})
    if not quiet:
        out["log"] = buf.getvalue()
    return out, (fs if keep else None)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()
