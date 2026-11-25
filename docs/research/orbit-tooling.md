# Orbit refitting with non-gravitational parameters: tooling, data, standards, cost, and a hands-on probe

Researcher brief: "can we refit asteroid orbits ourselves, with non-gravitational parameters, from public astrometry, using open-source software on one workstation?"
Date of all checks: 2026-11-20. Status tags: **[V]** verified today (source read or command run in this session), **[R]** recalled from memory and not checked, **[U]** uncertain.

## 0. Bottom line

1. **Yes, it works, today, on this workstation.** `uv pip install grss` took 5.6 s; first import downloaded 4.3 GB of SPICE kernels and the Eggl et al. (2020) debiasing tables in 2 min 27 s. With astrometry pulled live from the MPC API and radar from the JPL API, GRSS 4.6.0 recovered JPL's non-gravitational parameters for eight of nine test objects to within 1 combined sigma, in 0.2 to 22 s per fit on one core. A second, independent engine (layup 1.1.0, built on ASSIST/REBOUND) reproduced four of them. **[V]**
2. **For most NHATS objects there is nothing to fit.** 71.2% of the 7,226 NHATS objects have a data arc of 30 days or less, 83.0% have 90 days or less, 86.7% have a year or less. In a 64-object stratified pilot, no object with an arc under 90 days came within a factor of 77 of the sensitivity needed to see solar radiation pressure, and none with an arc under about 3 years could see Yarkovsky. The informative NHATS set is roughly 814 objects with arcs over 1,000 days (Yarkovsky) plus 74 objects with H >= 27 and an arc of 60 days or more (radiation pressure). **[V]**
3. **JPL and ESA already do this routinely.** JPL SBDB today lists A2 for 618 near-Earth asteroids (573 at S/N >= 3) and A1 for 21; 169 NHATS objects already carry a JPL A2 and 10 carry an A1 at S/N >= 3. ESA NEOCC runs an automated monthly pipeline (348 accepted detections in 2023). A fresh systematic search will yield few new detections, mostly at S/N 3 to 5 where the documented false-positive rate is highest. **[V]**
4. **The real gap is not "more detections".** It is (a) a uniform, open, reproducible catalog of A1/A2 *posteriors including non-detections* for every object with enough arc (JPL and NEOCC publish values only for objects where the parameter was adopted or accepted), (b) a detection efficiency measured by injection-recovery, which none of the published pipelines report, and (c) a per-object forecast of what future astrometry would turn a non-detection into a constraint. **[U]** that no such catalog exists; I did not find one.
5. **Correction to the brief:** arXiv 2502.13222 is *not* the ESA NEOCC pipeline paper. It is Fenucci et al. 2025 on (469219) Kamo'oalewa. The pipeline paper is Fenucci et al. 2024, arXiv 2311.10175 (A&A 682, A29). **[V]**

## 1. Hands-on probe

The work area was not kept; `data/research/` holds none of it. It held:

- `probe-orbit/.venv` (GRSS), `probe-orbit/.venv-layup` (layup), `probe-orbit/out/` (logs and JSON), `probe-orbit/pilot/` (64-object pilot).
- `scripts/probe_fit.py`, `scripts/pilot_fit.py`, `scripts/pilot_sample.py`, `scripts/pilot_summary.py`, `scripts/probe_layup.py`, `scripts/probe_layup_guess.py`, `scripts/mpc_fetch.py`, `scripts/sbdb_stats.py`, `scripts/ng_stats.py`.
- `downloads-orbit/` (SBDB and NHATS dumps, MPC ADES XML, NEOCC files, papers).

### 1.1 Installation

| Step | Result |
|---|---|
| `uv venv --python 3.12` + `uv pip install grss` | Worked first time, 5.6 s, binary wheel (GRSS 4.6.0, released 2026-10-26). Pulls astropy 8.0.3, astroquery 0.4.11, healpy, numba. |
| First `import grss` | Runs `grss.utils.initialize()`: downloads DE430, DE440, DE441 (3.31 GB), sb441-n16 (646 MB), Earth/Moon PCKs, and both debias tables. 2 min 27 s. Peak RSS 7.3 GB because each file is read fully into memory before writing. Venv ends at 5.3 GB. It shells out to `python`, so the venv's `bin` must be on PATH. |
| `uv pip install layup` (system Python 3.12) | **Failed.** No binary wheel; the source build needs Python headers (`Could NOT find Python (missing: Interpreter Development.Module)`) and `python3.12-dev` is not installed. |
| `layup` with a uv-managed Python (`UV_PYTHON_INSTALL_DIR` inside the probe dir, `--python-preference only-managed`) | Worked, 28 s build. `layup bootstrap` downloaded 1.4 GB in 46 s. No sudo needed. |

Every `import grss` re-runs the initialisation (internet check, kernel check, a fresh MPC observatory-code download once a day). Import costs about 1.6 s per process. A production pipeline should use long-lived workers.

### 1.2 Recovery of published values

GRSS runs: initial six elements from JPL SBDB, non-grav parameters started at **zero**, optical astrometry from the MPC `get-obs` API, Eggl et al. (2020) debiasing, Veres et al. (2017) weights, sqrt(N/4) same-night de-weighting, radar from the JPL radar API, DE440, single thread. layup runs: optical only, same debias and weights.

| Object | Par. | JPL SBDB (today) | GRSS (this session) | layup (this session) | Fit wall time (GRSS) |
|---|---|---|---|---|---|
| (480883) 2001 YE4 | A2 | -6.950e-14 +- 9.16e-16 (S/N 75.9) | -6.909e-14 +- 7.41e-16 (S/N 93.3), +0.35 sigma | -6.938e-14 +- 1.62e-15, own IOD, no JPL input | 21.7 s (6p), 12.8 s (7p); 450 optical + 7 radar, 24 yr |
| (499998) 2011 PT | A2 | -2.121e-13 +- 3.01e-14 (7.0) | -2.126e-13 +- 3.03e-14 (7.0), -0.01 sigma | -2.212e-13 +- 2.92e-14 (JPL warm start) | 0.9 s, 1.0 s; 200 obs, 6 yr |
| 2009 BD | A1 | 5.605e-11 +- 8.51e-12 (6.6) | 5.275e-11 +- 9.66e-12 | 5.433e-11 +- 7.29e-12 | 1.0 s (8p) |
| 2009 BD | A2 | -1.146e-12 +- 8.37e-14 (13.7) | -1.119e-12 +- 1.53e-13 | -1.157e-12 +- 1.22e-13 | |
| 2012 LA | A1 | 6.713e-11 +- 1.19e-11 (5.7) | 6.504e-11 +- 1.27e-11 | 7.472e-11 +- 1.18e-11 (JPL warm start) | 0.2 s |
| (523599) 2003 RM | A2 | 3.287e-12 +- 2.98e-14 (110) | 3.296e-12 +- 3.82e-14, +0.20 sigma | not run | 1.8 s; 409 obs |
| (3908) Nyx, with 75 Gaia FPR obs | A2 | 1.106e-14 +- 2.33e-15 (4.7) | 1.113e-14 +- 1.60e-15 (6.9) | not run | 7.3 s; 2,193 obs |
| (2062) Aten, with 234 Gaia FPR obs | A2 | -1.061e-14 +- 1.15e-15 (9.2) | -9.33e-15 +- 7.31e-16 (12.8), +0.94 sigma | not run | 19.6 s; 1,295 obs, 64 yr |
| 2026 QQ8 (NHATS, H 31.4, 92 d arc) | A1 | 1.306e-10 +- 1.00e-11 (13.0) | 1.353e-10 +- 9.63e-12 (14.1) | 1.463e-10 +- 1.70e-11 (JPL warm start) | 0.19 s; 63 obs |
| (101955) Bennu | A2 | not in SBDB (JPL uses a thermophysical model: AMRAT, RHO) | -4.660e-14 +- 2.43e-16 (S/N 192), i.e. da/dt = -19.45e-4 au/My | not run | 5.2 s; 603 optical + 29 radar |
| 2020 CD3 (NHATS, minimoon) | A1 | 1.357e-10 +- 2.50e-12 (54) | **failed**, no convergence | **failed** (IOD) | |

Independent cross-check for 2001 YE4: ESA NEOCC's orbit file `480883.ke0`, downloaded today, gives A2 = -6.919e-14 au/d^2, S/N 95.19, da/dt = -50.45 +- 0.53 e-4 au/My. Four pipelines (JPL, NEOCC, GRSS, layup) agree within 1 sigma. **[V]**

What this does and does not show:

- The GRSS fits are not fully independent of JPL: they start from JPL's six elements. The non-grav parameters start at zero and are driven by the data. The layup fit of 2001 YE4 used no JPL input at all (own Gauss IOD from the raw ADES file).
- **Bennu is a warning about formal errors.** Our A2 converts (da/dt = 2 A2 (1-e^2) / (n p^2)) to -19.45e-4 au/My with a formal error of 0.5%. Chesley et al. (2014) published -19.0 +- 0.1 e-4 au/My, and the NEOCC table lists A2 = -4.52e-14 (da/dt -18.89e-4). We differ by 2 to 3%, about 4 to 6 times our formal sigma. At S/N near 200 the formal uncertainty understates pipeline-to-pipeline differences (data selection, radar treatment, perturber set; 151 of 603 optical observations had no star-catalog bias information). The Chesley abstract says the same: "The accuracy of this result depends critically on the fidelity of the observational and dynamical model." For density inference a 3% shift is irrelevant; for claims about agreement it is not.

### 1.3 Failures and traps found in the probe

1. **Outlier rejection eats the signal in the wrong model.** For 2001 YE4 the gravity-only fit "converged" by rejecting 72 of 450 observations; the A2 fit rejected 1. For Bennu the gravity-only fit rejected 490 of 603; for 2003 RM 148 of 409. A chi-square difference between two fits with different rejection masks is meaningless. Model comparison must freeze one mask (GRSS allows forced accept/reject through the `selAst` column: `a` and `d`).
2. **Reduced chi-square is far below 1.** Converged fits had reduced chi-square of 0.15 to 0.5. The Veres et al. weights are conservative for much of the archive. The layup source says the same and gives the example that 1I/'Oumuamua "fits gravity-only at 0.263 and carries an 8.7-sigma A1". Any threshold of the form "try non-gravs only if the gravity-only fit is bad" will miss real signals. Thresholds on delta chi-square are not calibrated probabilities.
3. **GRSS does not converge on many very short arcs.** In the pilot, 44 of 192 fits hit the 20-iteration cap. All were objects with arcs of 24 days or less (5 of 8 six-parameter fits failed for arcs of 3 days or less; none failed above 30 days). layup did converge on the one 1-day arc tried (2024 XB3, 19 observations), giving A2 = -4.5e-7 +- 3.8e-6, i.e. no information, as expected.
4. **Temporarily captured objects break both tools.** 2020 CD3 would not converge in GRSS even when started from JPL's own solution including A1 (initial RMS 11,558 arcsec; repeated "Downleg light time did not converge" warnings), and layup's IOD failed. 2020 CD3 and 2006 RH120 are among the lowest delta-v NHATS targets (3.57 and 3.97 km/s). They need special handling (geocentric state, epoch inside the arc, full-precision initial state).
5. **layup's IOD fails on Earth-like orbits.** Without an initial guess, 4 of 6 multi-apparition or close-approach objects failed (2011 PT, 2012 LA, 2026 QQ8, 2020 CD3: flag 3, chi-square 1e10 to 1e13). With a JPL warm start all three retried objects converged. The `initial_guess` argument expects a previous layup result; an external orbit has to be dressed with dummy `flag`, `csq`, `ndof`, `niter` columns. layup uses a `spawn` process pool, so driver scripts need an `if __name__ == "__main__"` guard (without it my first run hung for 10 minutes spawning workers).
6. **JPL API concurrency.** Running 6 workers in parallel produced 4 failed SBDB requests out of 64 (empty body, JSON decode error); all four succeeded when rerun one at a time. JPL's API terms say "submit only one API request at a time". My pilot unknowingly broke that rule; the production pipeline must not.

### 1.4 Pilot: 64 random NHATS objects, stratified by arc length

Sample: 8 objects in each of 8 arc bins, fixed seed. For each: gravity-only fit, A1-only fit, A2-only fit. Elapsed 65 s for 60 objects with 6 processes; total fit time 111.7 s for 192 fits (mean 0.58 s per fit, median far lower).

"Expected" magnitudes used as yardsticks: A1_exp = 1.7e-11 au/d^2 x (10 m / D) for a sphere of density 2,000 kg/m^3 (radiation pressure); A2_exp = 1.3e-12 au/d^2 x (10 m / D), the Bennu value scaled by 1/(D rho) (near-maximal Yarkovsky). D from H with albedo 0.14. A parameter is "detectable at 3 sigma" if its formal sigma is below one third of the expected value.

| Arc (days) | n | 6p non-converged | median fit time 6p / A2 | median sigma(A1)/A1_exp | detectable A1 | median sigma(A2)/A2_exp | detectable A2 |
|---|---|---|---|---|---|---|---|
| 0 to 3 | 8 | 5 | 0.25 / 0.27 s | 161,000 | 0 | 127,000 | 0 |
| 3 to 7 | 8 | 3 | 0.21 / 0.28 s | 1,630 | 0 | 20,500 | 0 |
| 7 to 14 | 8 | 2 | 0.18 / 0.44 s | 2,700 | 0 | 17,700 | 0 |
| 14 to 30 | 8 | 1 | 0.31 / 0.29 s | 711 | 0 | 3,500 | 0 |
| 30 to 90 | 8 | 0 | 0.12 / 0.15 s | 147 | 0 | 3,770 | 0 |
| 90 to 365 | 8 | 0 | 0.24 / 0.26 s | 34 | 1 (2026 QQ8) | 222 | 0 |
| 365 to 1,825 | 8 | 0 | 0.60 / 0.78 s | 52 | 0 | 8.1 | 0 |
| over 1,825 | 8 | 0 | 1.67 / 2.45 s | 73 | 0 | 0.81 | 2 |

Reading: for a typical NHATS object (arc of days to weeks, a few dozen observations) the astrometry constrains A1 and A2 three to five orders of magnitude too weakly. Yarkovsky sensitivity only approaches the physical scale for arcs of several years. The single radiation-pressure detection is a 2 m object followed for three months.

## 2. Tools (question a)

Activity and licence fields come from the GitHub API today unless marked.

| Tool | What it is | Language, licence | Activity (2026) | Fits A1/A2/A3? Custom g(r)? | Force model | Astrometry model | Scripting | Verdict |
|---|---|---|---|---|---|---|---|---|
| **GRSS** (Makadia, Farnocchia, Chesley, Eggl; PSJ 6, 85, 2025; JOSS 10, 7861) | Propagator and batch least-squares orbit determination "for planetary defense" | C++ core, Python API; GPL-3.0 | v4.6.0 on 2026-10-26 ("nongrav DTs and full priors"); 74 PyPI releases since 2023 **[V]** | Yes: a1, a2, a3 and the delay dt are estimable; g(r) = alpha (r/r0)^-m [1+(r/r0)^n]^-k with fixed alpha, k, m, n, r0, so both 1/r^2 and the Marsden comet law **[V, code]**. Also impulsive events and a-priori constraints. | Sun, planets, Moon, 16 main-belt perturbers (DE430/431 or DE440/441 kernels), PPN/EIH relativity flags, J2 and spherical harmonics **[V, from kernels and library strings]**; IAS15-type Gauss-Radau integrator **[R]** | MPC ADES via `get-obs`; JPL radar API; Gaia DR3/FPR via astroquery; Eggl 2020 debias (low or high resolution); Veres 2017 weights with station rules; same-night de-weighting; Carpino-style outlier rejection (chi 3.0 reject, 2.8 recover); time-uncertainty inflation **[V, code and run]** | `fit.get_sbdb_info`, `fit.get_optical_obs`, `fit.add_radar_obs`, `fit.add_gaia_obs`, `fit.FitSimulation(...).filter_lsq()` | **Primary.** Authors are the JPL people who maintain the operational error models. Agreement with JPL measured today. Weak on very short arcs and captured objects. No IOD. |
| **layup** (Holman et al.; CfA/LINCC for Rubin) | "Orbit fitting at LSST scale": IOD (Gauss, Bernstein-Khushalani), Levenberg-Marquardt fit, prediction | Python + C++; MIT (depends on ASSIST and REBOUND, GPL-3.0) | v1.1.0 on 2026-09-21, pushed 2026-11-14 **[V]** | Yes: `fit_nongrav` = "A2", "A1A2A3", or "auto" (model ladder A2/A1/A3, then pairs, then all three; adopts if delta chi-square >= 9 per parameter and each parameter >= 3 sigma); `nongrav_gr` = [alpha, nm, nn, nk, r0]; per-apparition amplitudes for comets **[V, source]**. Python API only, not on the CLI. | ASSIST: Sun, Moon, planets, 16 massive asteroids from DE441 (uses de440s + sb441-n16), "the most significant gravitational harmonics and general relativistic corrections", variational equations **[V, ASSIST abstract]** | MPC 80-column and ADES (csv, psv, xml, hdf5); debias (same JPL table); Veres 2017 weights; radar delay/Doppler supported in the API **[V, source]**. I saw no outlier rejection in the run (all 450 observations used). | `layup orbitfit file ADES_xml -d -wd`, or `layup.orbitfit.orbitfit(data, cache_dir, fit_nongrav=...)` | **Second engine for cross-checks**, and the only one here with built-in IOD and batch parallelism. Needs a warm start for NEOs on Earth-like orbits. Young (repo created January 2025). |
| **ASSIST + REBOUND** (Holman et al. 2023; Rein) | Ephemeris-quality test-particle integrator with variational equations | C with Python; GPL-3.0 | REBOUND 5.2.3 on 2026-11-18; ASSIST pushed 2026-06-21 **[V]** | Propagates Marsden A1/A2/A3 with a g(r) law; fitting must be built on top (layup does this) | As above | None (propagator only) | Python | Use through layup or adam-assist, not directly. |
| **find_orb** (Bill Gray, Project Pluto) | Mature general-purpose orbit determination, very robust on short arcs; statistical ranging and Monte Carlo | C++; GPL-2.0 | Pushed 2026-11-18, 2,892 commits **[V]** | SRP (area-to-mass), comet A1/A2 with optional A3 and DT (Marsden-Sekanina), inverse-square A1/A2 for "rocks", a "Yarkovsky" along-track option **[V, force-model page]**. The author calls the non-grav code "messy" in a GitHub issue **[V, search snippet]**. | Planets and Moon; up to 300 BC-405 asteroid perturbers; J2 to J4 near planets, more Earth terms when close; Galilean and Saturnian satellites; Earth atmospheric drag; **relativity for the Sun only**; solar J2 not modelled **[V]** | FCCT14 debiasing; `sigma.txt` station weights; over-observing rule; blunder probability; ADES uncertainties **[V]**. Radar support not confirmed **[U]**. | Non-interactive `fo`; JSON and covariance output; B612's `adam_fo` wraps it for ADES input **[V, README]** | **Third opinion and short-arc/captured-object fallback.** Not the reference for A2 because of the reduced relativity model. Not tried today. |
| **OrbFit 5.0.8** (Pisa/SpaceDyS consortium; NEODyS) | The classic package; origin of NEODyS and (as Aegis) NEOCC | Fortran 95; GPL | Web page "last updated October 24, 2024"; gfortran builds are possible **[V]** | Yes: radiation pressure, Yarkovsky, cometary outgassing; covariance up to 10x10 **[V]** | Planets, Moon, 16 asteroids + Pluto, first-order PN relativity (as described for Aegis in Fenucci 2024) **[V for Aegis]** | Farnocchia 2015 debias, `vfcc17` weights, Carpino 2003 outlier rejection | Option files, Fortran binaries, `.rwo` residual files | Proven for exactly this job (Del Vigna 2018; Dziadura 2023, 2024 used an MPC-developed OrbFit). Painful to script; worth it only if a third rigorous engine is wanted. Not tried today. |
| **NEOs.jl / PlanetaryEphemeris.jl** (Perez-Hernandez, Benet; UNAM/MPC) | Jet-transport (Taylor) orbit determination and propagation | Julia; licence not asserted by GitHub **[U]**, MIT **[R]** | v0.35.0 on 2026-11-19 **[V]** | Published Apophis A2 fit (Commun. Earth Environ. 3, 10, 2022) **[V]**; general A1/A3 support **[U]** | DE430-based, 16 asteroids, PPN, J2 **[R]** | Optical and radar; debias and weights **[R]** | Julia scripts (`apophis.jl`) | Credible fourth engine; adds a Julia toolchain. Not tried. |
| **adam_core 0.8.0 / adam-assist 0.7.0** (B612 Asteroid Institute) | Orbit/observation data structures (Rust-backed); ASSIST propagator plug-in | Rust + Python; MIT per README | Both released 2026-11-10/11 **[V]** | adam-assist *propagates* A1/A2/A3 with custom g(r), regression-tested against Horizons "to tens-hundreds of metres over +-300 days"; DT and thermophysical Yarkovsky not supported **[V, README]**. Whether adam_core's OD *fits* non-gravs: **[U]** | ASSIST | ADES structures; SBDB and Horizons queries | Python | Useful plumbing (ADES tables, SBDB queries); not a tested non-grav fitter. |
| **precovery** (B612) | Fast search of indexed survey catalogs for detections along an orbit | Python; BSD-3 | Pushed 2026-10-19 | n/a | n/a | n/a | Python | Relevant only if the project hunts new precoveries; needs indexed survey data. |
| **mpcq** (B612) | Client for the Asteroid Institute's BigQuery replica of the MPC database | Python; MIT; v0.5.0 | Pushed 2026-11-19 | n/a | n/a | Returns ADES-compatible tables | Python | Bulk alternative to the MPC API; needs a Google Cloud account; queries billed to the user. |
| **kete** (IPAC, NEO Surveyor) | Survey simulation, fast propagation, FOV checks | Rust + Python; BSD-3; v1.1.4 on 2026-11-10 | Active | Propagates non-gravs incl. time-delayed and dust models; **no orbit fitting** in README or changelog as read today **[V for those two documents]** | N-body with non-gravs | n/a | Python | Not a fitter. Useful for "was this object in a survey's field" checks. |
| **OpenOrb / pyoorb** | Statistical ranging, least squares, ephemerides | Fortran; GPL-3.0; v1.3.0 (2023), pushed 2026-08 | Maintained, slow | No non-grav estimation **[R/U]** | Planets; limited | Basic | CLI, `pyoorb` | Not for this purpose. |
| **THOR**, **heliolinx**, **Sorcha** | Linking (THOR, heliolinx) and LSST survey simulation (Sorcha 1.2.1) | BSD-3 / BSD-3 / open | Active | n/a | n/a | n/a | n/a | Not fitters. Sorcha matters only for selection-effect modelling of Rubin. |

Not open source, for context: JPL's operational software, UCLA's IDOS (built on JPL MONTE; Greenberg et al. 2020), ESA's Aegis (SpaceDyS; Fenucci et al. 2024).

## 3. Data access (question b)

| Source | How | Measured or stated | Terms |
|---|---|---|---|
| **MPC Observations API** | `GET https://data.minorplanetcenter.net/api/get-obs` with JSON body `{"desigs": ["2011 PT"], "output_format": ["XML","OBS80","ADES_DF","OBS_DF"]}`. One designation per request. | 0.6 to 1.7 s per object; 2001 YE4 returned 450 `<optical>` ADES records (285 kB). Only 50 of 450 carry `rmsRA`/`rmsDec`; 8 carry `uncTime`. **[V]** | The documentation page states no rate limit or usage policy **[V]**. Ask the MPC helpdesk before pulling tens of thousands of objects. |
| **MPC bulk files** | `https://www.minorplanetcenter.net/iau/ECS/MPCAT-OBS/NumObs.txt.gz` (9.1 GB), `UnnObs.txt.gz` (456 MB), 80-column | **Both last modified 2026-06-03**, i.e. 5.5 months stale today **[V, HTTP headers]**. `NEA.txt` orbits are current (2026-11-20). | Public. |
| **MPC replicated PostgreSQL (via SBN, Univ. of Maryland)** | Logical replication to *your own* PostgreSQL server; you give SBN an IP address and subscribe to two publications. No public query endpoint. | Example hardware "SSD - 4 TB, RAM 32-48 GB"; must be online 24 h/day; initial download within 3 days; Postgres 14+; schema is a beta release. **[V]** | "non-exclusive, non-transferable, non-sublicensable", internal use; ToS v1.0 (2023-09-28). Overkill for one workstation. |
| **Asteroid Institute BigQuery replica** | Subscribe to the Analytics Hub listing; query with `mpcq` | "complete replica of the MPC database" incl. `public_obs_sbn` **[V, README/docs]** | Billed to your Google Cloud account. |
| **JPL SBDB** | `sbdb_query.api` (bulk fields) and `sbdb.api?sstr=...&cov=mat&full-prec=true` (orbit, covariance, model parameters) | One `sbdb_query` call returned all 43,360 NEOs with arc, n_obs, condition code, A1/A2/A3 and sigmas in 1.2 s (3.9 MB). **[V]** | "You agree to submit only one API request at a time"; cache results; automated clients "must send a valid, application-specific User-Agent header with product name, version, and contact information" **[V]**. The contact detail is a decision for the project owner. |
| **JPL radar astrometry** | `https://ssd-api.jpl.nasa.gov/sb_radar.api` (all) or `?des=...` | One call returns everything: 4,715 delay/Doppler records for 1,131 objects, latest epoch 2026-06-27; API version 1.1 **[V]**. 232 NHATS objects and 192 of the A2 objects have radar astrometry in their JPL fit. | Same JPL terms. |
| **Gaia SSO astrometry** | TAP tables `gaiadr3.sso_observation`, `gaiafpr.sso_observation`; GRSS `fit.add_gaia_obs(obs_df, ..., gaia_dr='gaiafpr')` handles the per-transit covariance (random + systematic) and Gaia's geocentric position **[V, code and run: 75 obs for Nyx, 234 for Aten]** | FPR holds astrometry for 446 NEOs, about 50 mas average uncertainty (Dziadura et al. 2024) **[V]** | **The Gaia archive goes down 25 November 2026 12:00 CET and DR4 is released 2 December 2026 12:00 CET** (live archive notice printed by astroquery today; ESA release page: "Gaia DR4 (based on 66 months of data) 2 December 2026") **[V]**. GRSS will need the DR4 table name. What DR4 adds for NEAs beyond the FPR: **[U]**. |
| **Star-catalog debiasing** | `https://ssd.jpl.nasa.gov/ftp/ssd/debias/debias_2018.tgz` (9.9 MB) and `debias_hires2018.tgz` (156 MB; 595 MB unpacked), last modified 2023-03-01 **[V]** | Implemented in GRSS, layup, OrbFit/Aegis, JPL; find_orb implements the earlier FCCT14 tables **[V]** | Public. For Bennu, 151 of 603 observations had catalog codes with no bias entry (ATLAS2, GSC, UNK). |
| **Weights** | Veres et al. 2017 (arXiv 1703.03479) | Implemented in GRSS (`apply_weighting_scheme`, with station rules), layup (`astrometric_uncertainty_Veres2017`), OrbFit/Aegis (`errmod = 'vfcc17'` in NEOCC `.rwo` headers) **[V]** | |
| **ESA NEOCC per-object files** | `https://neo.ssa.esa.int/PSDB-portlet/download?file=<desig>.rwo` (every observation with weight, bias, residual, chi, selection flag) and `.ke0/.ke1/.eq0/.eq1` (orbit with A2 or A/m, S/N, da/dt, covariance) | `480883.rwo`: 474 lines; `480883.ke0` contains "SNR A2 95.19", "da/dt [1E-4 au/My] -5.0448459E+01 +/- 5.2996399E-01" **[V]** | No authentication; "experimental", may change without notice; no stated rate limit. A free per-observation reference to diff our weights and rejections against. |

## 4. Method standards (question c)

### 4.1 How each group decides a detection is real

| Study | Software | Funnel | Significance | Physical plausibility | Robustness checks |
|---|---|---|---|---|---|
| Farnocchia et al. 2013 (arXiv 1212.4812) | JPL software, cross-checked with OrbFit ("agreement at better than the 1-sigma level") | All known NEAs to 21 reliable + 16 weaker | S/N >= 3 ("more robust against changes in the observation weighting") | S = abs(A2 / A2_exp) < 1.5, with A2_exp scaled from Bennu by 1/D | Ad hoc weights for pre-CCD data (Apollo: 10 arcsec for 1930-1950, 3 arcsec for 1950-1990); isolated precoveries listed and flagged; 5 observations per night effective |
| Del Vigna et al. 2018 (arXiv 1805.05947) | OrbFit | 538 objects (519 with sigma(a) < 3e-9 au) to 101 with S/N >= 3 to **87 accepted, 24 marginal, 14 rejected** | S/N >= 3; marginal 2.5 to 3 | S <= 2, Bennu-scaled with density by taxonomy; S much less than 1 is allowed | Rejects detections that hinge on isolated old observations unless remeasured; SRP fitted for H > 24 (4 detections) |
| Greenberg et al. 2020 (arXiv 1708.05513) | IDOS on JPL MONTE (not open) | 600 candidates (sensitivity metric s_Y >= 2) to 317 to 257 to **247** | F-test between 6- and 7-parameter fits, p <= 0.05 ("approximately ... a two-standard-deviation detection threshold") | Yarkovsky efficiency xi inspected afterwards (median 0.12) | Refit without the 10 earliest observations (60 objects rejected); refit without pre-1965 data (8 flagged); arc >= 5 years; outliers: chi-square > 8 in a fit-drop-add loop, redone with Yarkovsky in the model |
| Fenucci et al. 2024, ESA NEOCC (arXiv 2311.10175) | Aegis | 32,396 NEAs to **5,308 candidates** (sigma(a) < 1e-5 au and sigma(a) < arc x Y_M) to 461 with S/N >= 3 to 373 passing the physical test to **348 accepted** (25 killed by the isolated-tracklet test) | S/N = abs(A2/sigma) >= 3 | abs(da/dt) - 1.645 sigma < Y_M, where Y_M is the 95th percentile of the maximum Yarkovsky drift from 500,000 Monte Carlo draws of D, rho, P, thermal inertia (SsODNet values where they exist, population models otherwise) | Isolated tracklet = one observatory, under 15 days, at least 5 years from neighbours; remove, refit, require S/N >= 3 still (exception list for remeasured data and Pan-STARRS). 10 arcsec weights before 1890, 5 arcsec before 1950. Rerun after every monthly MPC update. |
| Dziadura et al. 2023 (A&A 680, A77) and 2024 (arXiv 2411.09750) | OrbFit (MPC-developed version) + Gaia DR3 / FPR | 446 NEAs to **49** (DR3, 10 new) and **43** (FPR, 9 additional) | S/N > 3; marginal > 2.5 | S <= 2 | Full Gaia covariance; DR3 vs FPR comparison. The 2023 paper already converts A2 to bulk density. |
| Seligman et al. 2023 (arXiv 2212.08115), Farnocchia et al. 2023 | JPL | Case studies ("dark comets") | A1, A2, A3 all estimated together "to avoid underestimating the uncertainty" | Acceleration exceeds Yarkovsky/SRP scale; A3 has no radiation-based explanation | Found by chasing residual biases at new apparitions; remeasurement of old images; deep imaging for activity |
| layup `fit_nongrav="auto"` (for reference, not a science standard) | layup | per object | delta chi-square >= 9 per added parameter and each >= 3 sigma, tried only if gravity-only reduced chi-square > 1.5 | none | none |

Agreement between centres: NEOCC vs JPL on 270 common objects gave a slope of 1.00 and chi < 2 for all but two objects (2003 AF23, 65717). JPL then listed 333 A2 values (308 at S/N >= 3); 54 JPL objects were not in the NEOCC list. **[V]**

### 4.2 Documented false-positive traps

1. **A blind search is mostly noise.** Farnocchia et al. 2013: "For SNR > 3 we have 67% spurious detections, for 2 < SNR < 3 we have 88%" before the physical filter. **[V]**
2. **Isolated old tracklets.** Signals carried by a few precovery positions (Palomar DSS 1950s, Siding Spring 1970s): 1992 BF (valid only after the 1953 plates were remeasured; the remeasurements "are not available in the MPC database"), 1999 FK21, 2001 MQ3, 1989 UQ, 1999 FA, 2004 QT24, 2002 AW, 1992 SL, Mithra, 2000 ET70. NEOCC: 69 of 373 candidates had isolated tracklets; 25 were judged spurious. **[V]**
3. **Pre-CCD astrometry.** (433) Eros (S/N about 5, obliquity near 89 degrees, so the detection must be wrong) and (1036) Ganymed (unphysical efficiency of 4.12; vanishes when pre-1950 data are dropped). **[V]**
4. **Weighting-scheme dependence.** (175706) 1996 FG3: the signal "disappears when the weighting scheme proposed in Veres et al. (2017) is applied" (Del Vigna 2018). Detections near S/N 3 flip between centres for this reason (Fenucci 2024). **[V]**
5. **Timing errors.** Important for fast-moving objects near close approach (Farnocchia et al. 2022, cited in Fenucci 2024). NEOCC's automated runs did not yet use the ADES timing fields in 2023; 2011 MD needed relaxed weights during its flyby. In our 2001 YE4 sample only 8 of 450 observations report a time uncertainty. **[V]**
6. **Wrong physics, real acceleration.** Radiation pressure aliases into A2 on tiny objects (2009 BD, 2011 MD, 2012 LA, 2012 TC4, 2015 TC25, 2021 GM1 fail the Yarkovsky test until A/m is added); outgassing or mass loss (2003 RM, 2006 RH120, 4015 Wilson-Harrington); and accelerations small enough to pass as Yarkovsky cannot be told apart "unless there are proofs of such phenomena obtained from detailed studies of the single object" (Fenucci 2024). **[V]**
7. **Missing data that the reference centre has.** NEOCC could not reproduce JPL's Didymos (S/N 16 vs 2.57) or Phaethon (S/N 8.3) detections because occultation, spacecraft and Gaia astrometry "are not reported by the MPC". **[V]**
8. **Detections that flip.** Kamo'oalewa was flagged spurious by NEOCC (2023) and by Hu et al. (2023), then confirmed at S/N about 14 after new astrometry and a remeasured 2004 SDSS precovery (Fenucci et al. 2025, arXiv 2502.13222). Several of Del Vigna's 2018 rejections (2002 AW, 1999 FA, 1996 FG3, 2005 TG50) now carry an A2 in JPL SBDB. **[V]**
9. **Outlier rejection under the wrong model** and **conservative weights** (section 1.3, found in this session). **[V]**
10. **Multiplicity.** Testing about 10,000 objects for three parameters at a two-sided 3-sigma threshold gives about 27 chance detections per parameter even with perfect Gaussian errors, which astrometric errors are not. None of the published pipelines reports an injection-recovery efficiency or an empirical false-alarm rate; the physical-plausibility filter stands in for both.

## 5. Scale and cost (question d)

### 5.1 The population (JPL SBDB and NHATS APIs, queried today)

| | All NEOs (43,360; 43,151 asteroids) | NHATS (7,226) | NHATS, delta-v < 5 km/s (286) |
|---|---|---|---|
| Median data arc | 22 days | 12 days | 14 days |
| Arc <= 7 days | 29.3% | 36.1% | 30.1% |
| Arc <= 30 days | 56.6% | 71.3% (5,151) | 65.4% |
| Arc <= 90 days | 68.7% | 81.7% | 76.2% |
| Arc <= 365 days | 73.2% | 85.4% | 85.3% |
| Arc > 1,000 days | 10,487 asteroids (24.3%) | 814 (11.3%) | about 30 |
| Arc > 10 years | 16.3% | 6.3% (454) | 2.8% (8) |
| Median observations used | 42 | 37 | 44 |
| Fewer than 30 observations | 14,027 | 2,741 (37.9%) | |
| Condition code 0 | 8,817 | 645 | 19 |
| Radar astrometry in JPL fit | 1,115 | 232 | 12 |
| JPL A2 present | 618 asteroids (573 at S/N >= 3; 351 >= 5; 146 >= 10) | 169 (154 at S/N >= 3; 18 of those with delta-v < 6) | 11 |
| JPL A1 present | 21 asteroids (12 at S/N >= 3) | 18 (10 at S/N >= 3) | 10 |
| JPL A3 present | 9 asteroids | 7 | 1 |

For the JPL A2 objects: data arc minimum 179 days (only the radiation-pressure objects are under 1,000 days: 2006 RH120, 2009 BD, 2011 MD, 2012 LA, 2015 TC25, 2023 YO1), 5th percentile 2,966 days (8 years), median 8,027 days (22 years); H from 12.8 to 29.5, median 21.3; 192 have radar; only 63 of the S/N >= 3 objects have a taxonomy in SBDB and 125 a diameter.

**Answer to "for what fraction of NHATS is there no non-grav information at all":** at least 83% (arc of 90 days or less, or unknown) carry none for either channel, on the evidence of the pilot. For Yarkovsky the figure is about 89% (arc under 1,000 days). The candidate pools are:

- Yarkovsky: 814 NHATS objects with arc over 1,000 days, of which 651 have no JPL A2; 549 with arc over 2,900 days (399 without JPL A2). With delta-v under 6 km/s: 52 (35 without A2).
- Radiation pressure: 74 NHATS objects with H >= 27 and arc >= 60 days (63 without a JPL A1); 135 with H >= 26 and arc >= 180 days. With delta-v under 6 km/s, H >= 27, arc >= 60 days: 53.

Across all near-Earth asteroids the Yarkovsky pool is about 10,500 (arc over 1,000 days), of which 7,517 with arcs over 2,900 days have no JPL A2. For comparison NEOCC selected 5,308 candidates in 2023.

### 5.2 Compute

Measured, GRSS, one core (numerical partials: 1 + 2 x n_parameters propagations per iteration, so 13, 15 and 19 for 6, 7 and 9 parameters):

| Case | Per fit |
|---|---|
| Arc under 1 year, a few dozen observations (typical NHATS) | 0.1 to 0.5 s |
| 1 to 5 year arc, about 100 observations | 0.6 to 1 s |
| Over 5 years, 100 to 800 observations | 1.5 to 5.4 s |
| 24 years, 457 observations with radar; 64 years, 1,295 observations | 13 to 22 s |

Budget (order of magnitude):

- **All 7,226 NHATS objects**, eight fits each (6p; A1; A2; A1+A2; A1+A2+A3; plus frozen-mask refits) at a population mean of about 0.3 to 0.6 s: 5 to 10 core-hours, **10 to 20 minutes on 32 cores**. Pointless for the 83% without information, but cheap enough to do for completeness and to report honest "no constraint" entries.
- **All 43,000 NEAs**, ten fits each at a mean of about 1 s: about 120 core-hours, **about 4 hours on 32 cores**.
- **Robustness refits** (drop isolated tracklets, drop the first apparition, drop pre-1990 data, alternative weights) for the 10,500 multi-apparition objects: another 100 to 150 core-hours.
- **Injection-recovery** on the informative NHATS set (888 objects x 50 injected amplitudes x 2 fits x about 2 s): about 50 core-hours, 1.5 hours on 32 cores. For all 10,500 multi-apparition NEAs: about 600 core-hours, 19 hours on 32 cores.

Compute is not the constraint. Data acquisition is: one MPC request per object at about 1 to 2 s gives 2 to 4 hours for NHATS and 12 to 24 hours for all NEAs if done politely in sequence, and JPL calls must be strictly sequential. Disk: about 7 GB for both environments and kernels.

## 6. Recommendation

### 6.1 Toolchain

1. **Primary fitter: GRSS** (pin 4.6.0), driven from Python, long-lived worker processes, one object per task, `OMP_NUM_THREADS=1`, 32 workers.
2. **Second engine: layup** (pin 1.1.0) on the informative subset, warm-started from the GRSS solution, for every claimed detection. Agreement between two code bases with different integrators (GRSS's own vs ASSIST/REBOUND) is the cheapest strong check available.
3. **External comparators, not engines:** JPL SBDB values and sigmas; ESA NEOCC `.ke0` and `.rwo` files; published tables (Greenberg 2020, Del Vigna 2018, Fenucci 2024, Dziadura 2023/2024).
4. **Fallbacks:** find_orb (`fo`) for short arcs and captured objects; OrbFit only if a third rigorous engine is needed.
5. **Data layer:** snapshot everything to disk with retrieval timestamps and hashes. One `sbdb_query` call for population fields; one `sb_radar` call for all radar; MPC `get-obs` per object (ADES XML); NEOCC `.rwo` for the validation and candidate sets; Gaia FPR now and DR4 after 2 December 2026. Never fit against a live API.
6. **Fit protocol (pre-register before the population run):**
   - Fit 6p, +A2, +A1, +A1+A2, +A1+A2+A3 with 1/r^2; freeze the outlier mask from the richest converged model before comparing chi-squares.
   - Detection requires S/N >= 3 **and** delta chi-square under a common mask **and** survival of: isolated-tracklet removal (NEOCC definition), first-apparition removal, pre-1990 removal, and the second engine.
   - Physical test: compare with the Monte Carlo distribution of expected Yarkovsky drift and expected A/m (NEOCC's Y_M approach), reported as a probability rather than a pass/fail.
   - Publish the posterior for every attempted object, including "no information" and upper limits.
   - Injection-recovery: inject synthetic A1/A2 into each object's real observation times and error model; report the 50% and 90% recovery amplitudes per object. This is the piece the literature lacks.
   - Empirical null: the distribution of fitted S/N for parameters with no expected signal (e.g. A3 on ordinary multi-apparition asteroids, and A2 on objects whose predicted Yarkovsky is far below sensitivity) calibrates the false-alarm rate.

### 6.2 Realistic scope

- **Stage 0, validation (days):** reproduce the tiers below.
- **Stage 1, NHATS informative set (about 890 objects):** 814 multi-apparition objects for A2 and 74 small long-arc objects for A1. Expect to re-derive the 169 + 18 existing JPL values, add upper limits for the other roughly 700, and perhaps a handful of new marginal signals.
- **Stage 2, all multi-apparition NEAs (about 10,500):** a uniform A2 posterior catalog. This is where the 573 JPL detections live and where a density-relevant population statistic is possible; it is also needed as a calibration sample because only 154 NHATS objects have an A2 detection.
- **Stage 3, the other 6,300 NHATS objects:** record "arc too short" with the measured sensitivity and the forecast of what observation would change that. No fits claimed.

What the catalog can honestly say per NHATS object from this channel: for about 2% a measured A2 or A/m; for about 10% an upper limit; for about 87% nothing.

### 6.3 Validation set (recover first)

Values are JPL SBDB today unless noted.

- **Tier 0, already recovered in this session:** (480883) 2001 YE4; (499998) 2011 PT; 2009 BD (A1 and A2); 2012 LA (A1); (523599) 2003 RM; (3908) Nyx; (2062) Aten; 2026 QQ8 (A1).
- **Tier 1, high S/N Yarkovsky, mostly with radar:** (99942) Apophis (-2.902e-14, S/N 153 to 156; 7,370 observations); (101955) Bennu (compare with Chesley et al. 2014, -19.0 +- 0.1 e-4 au/My; expect a 2 to 3% offset); 1998 SD9 (-2.87e-13, S/N 109 to 112); (363027); (524522) 2002 VE68 (S/N 77); (33342) 1998 WT24; (164121) 2003 YT1; (2340) Hathor (-2.96e-14, S/N 47); (437844) 1999 MN (3.78e-14, S/N 23); (85953) 1999 FK21 (-1.28e-14, S/N 20; depends on 1971 precovery); (6489) Golevka (-1.22e-14, S/N 8.4; the first detection); (152563) 1992 BF (-2.69e-14, S/N 39; a known trap, since it relies on remeasured 1953 positions).
- **Tier 2, optical-only, S/N 5 to 15, under 300 observations (119 objects in SBDB today):** e.g. 152828, 154590, 216985, 251732, 276770, 326354, 337252, 380818, 397326, 399308, 408982, 410622, 416002, 422638, 424392, 450237, 450300, 452334, 452639, 452807. Cheap, numerous, and the regime where the pipeline will actually operate.
- **Tier 3, radiation pressure:** 2009 BD, 2011 MD, 2012 LA, 2012 TC4, 2015 TC25, 2020 GE, 2021 GM1, 2021 VH2, 2020 WY, 2026 QQ8; hard cases 2020 CD3 and 2006 RH120.
- **Tier 4, dark comets and A3:** 2003 RM, 1998 KY26, 2005 VL1, 2016 NJ33, 2010 VL65, 2010 RF12, 2006 RH120, 2016 GW221, 2013 XY20, 2013 BA74, 2012 UR158 (A2 = -7.2e-12 at S/N 118), 1998 SH2 (reported 2026). The dark-comet status of 1998 KY26 is contested.
- **Tier 5, negative controls the pipeline must reject or flag:** (433) Eros; (1036) Ganymed; (4015) Wilson-Harrington; 2010 KP10; (308635) 2005 YU55; (139359) 2001 ME1; (142561) 2002 TX68; (192563) 1998 WZ6; (4486) Mithra; (39565) 1992 SL; (260141) 2004 QT24; (162421) 2000 ET70; 2011 XC.
- **Tier 6, known limits:** (65803) Didymos and (3200) Phaethon cannot be matched from MPC data alone.

## 7. What has already been done, and where the gap is

Already done by others:

- Systematic A2 search over all NEAs, automated, monthly: ESA NEOCC (Fenucci et al. 2024). JPL maintains A2 for 618 NEAs and A1 for 21. NEODyS does the same with OrbFit.
- Yarkovsky to bulk density with Gaia astrometry: Dziadura et al. 2023.
- Radiation pressure to area-to-mass on the smallest objects: Micheli et al. 2012, 2013, 2014; Mommert et al. 2014; Del Vigna et al. 2018; Fenucci et al. 2024 (2021 GM1).
- Dark comets: Seligman et al. 2023, the 2024 PNAS paper (14 objects), Farnocchia et al. 2023 and 2026.

Not found (so, candidate gaps; **[U]** until a literature specialist confirms):

- A public catalog of A1 and A2 *posteriors or upper limits* for objects without a detection.
- Injection-recovery detection efficiencies for any Yarkovsky or radiation-pressure pipeline.
- A fully open, rerunnable pipeline (JPL, IDOS and Aegis are closed; OrbFit is open but the published runs are not scripted for reuse).
- Per-object forecasts of the astrometry needed to reach a detection, aimed at the mission-accessible list.

## 8. Ways this part fails or misleads

- The channel is silent for 83 to 89% of NHATS objects and will stay silent until they are re-observed; many will not be recovered for decades.
- For the remaining objects, JPL and NEOCC have already extracted the strong signals. New "detections" from a fresh pipeline will cluster at S/N 3 to 5 with a majority-spurious prior.
- A2 gives density only through a degenerate product with obliquity, thermal inertia, size and rotation; a detection bounds density from above, a non-detection bounds nothing without an obliquity prior. A1 gives area-to-mass, which needs a size (albedo) to become density.
- Formal uncertainties are not the error: reduced chi-square of 0.2 to 0.5 from conservative weights on one side, a 2 to 3% inter-pipeline offset at S/N 200 on the other.
- The weak points of an automated run are exactly what agents cannot fix: remeasuring old plates, timing errors without reported uncertainties, astrometry that never reached the MPC.
- Tool fragility: GRSS short-arc non-convergence (23% of pilot fits), both engines failing on 2020 CD3, layup IOD failures, a one-maintainer GPL-3 package as the primary engine.
- Starting from JPL elements makes "independent" a qualified word. A truly independent result needs layup's IOD or find_orb for the initial orbit.
- Service terms: JPL's one-request-at-a-time rule and User-Agent contact requirement; no documented MPC API policy; stale MPC bulk files; NEOCC interface "experimental".

## 9. Open questions

1. Will the project identify itself to JPL (User-Agent with contact details), as the API terms require for automated clients? This needs the owner's decision.
2. Is GPL-3.0 (GRSS, ASSIST, REBOUND) acceptable for the published pipeline?
3. Does MPC accept about 43,000 sequential `get-obs` calls, or should the BigQuery replica (paid) or a helpdesk-arranged bulk pull be used? Bulk files were last refreshed in June 2026.
4. Should the catalog publish upper limits and "no information" entries for every object? I recommend yes; it is the part nobody else provides.
5. What does Gaia DR4 (2 December 2026) add for NEAs beyond the FPR's 446, and how fast will JPL, NEOCC and the Poznan group refit?
6. Can GRSS's short-arc and captured-object failures be fixed by fitting Cartesian states at a mid-arc epoch, or must those objects go to find_orb? Not resolved in the time box (one Cartesian attempt on 2020 CD3 crashed inside GRSS).
7. How is the current NEOCC Yarkovsky list best obtained in bulk? The portal news item (2024-02-12) says "more than 340 positive detections", updated monthly, but the computer-access page lists no dedicated file; per-object `.ke0` files do carry A2 and S/N.

## Sources

Software and documentation
- GRSS repository: https://github.com/rahil-makadia/grss
- GRSS documentation and examples: https://rahil-makadia.github.io/grss/ , https://rahil-makadia.github.io/grss/fit.html , https://rahil-makadia.github.io/grss/tests/python/fit/farnocchia.html
- GRSS on PyPI: https://pypi.org/project/grss/
- GRSS papers: https://doi.org/10.3847/PSJ/adbc88 , https://joss.theoj.org/papers/10.21105/joss.07861
- layup: https://github.com/Smithsonian/layup , https://layup.readthedocs.io , https://meetingorganizer.copernicus.org/EPSC-DPS2025/EPSC-DPS2025-979.html
- ASSIST: https://github.com/matthewholman/assist , https://arxiv.org/abs/2303.16246
- REBOUND: https://github.com/hannorein/rebound
- find_orb: https://github.com/Bill-Gray/find_orb , https://projectpluto.com/force.htm , https://projectpluto.com/find_orb.htm
- OrbFit: http://adams.dm.unipi.it/orbfit/
- NEOs.jl: https://github.com/PerezHz/NEOs.jl , https://github.com/PerezHz/PlanetaryEphemeris.jl
- adam_core, adam-assist, adam_fo, precovery, mpcq: https://github.com/B612-Asteroid-Institute/adam_core , https://github.com/B612-Asteroid-Institute/adam-assist , https://github.com/B612-Asteroid-Institute/adam_fo , https://github.com/B612-Asteroid-Institute/precovery , https://github.com/B612-Asteroid-Institute/mpcq
- kete: https://github.com/Caltech-IPAC/kete
- OpenOrb: https://github.com/oorb/oorb ; THOR: https://github.com/moeyensj/thor ; heliolinx: https://github.com/heliolinx/heliolinx ; Sorcha: https://github.com/dirac-institute/sorcha

Data services
- MPC Observations API: https://docs.minorplanetcenter.net/mpc-ops-docs/apis/get-obs/ , endpoint https://data.minorplanetcenter.net/api/get-obs
- MPC bulk observations: https://www.minorplanetcenter.net/iau/ECS/MPCAT-OBS/NumObs.txt.gz , https://www.minorplanetcenter.net/iau/ECS/MPCAT-OBS/UnnObs.txt.gz
- MPC database replication via SBN: https://sbnmpc.astro.umd.edu/MPC_database/replication-info.shtml
- JPL API terms: https://ssd-api.jpl.nasa.gov/doc/index.php
- JPL SBDB: https://ssd-api.jpl.nasa.gov/sbdb.api , https://ssd-api.jpl.nasa.gov/sbdb_query.api
- JPL NHATS: https://ssd-api.jpl.nasa.gov/nhats.api
- JPL radar astrometry: https://ssd-api.jpl.nasa.gov/sb_radar.api
- JPL debiasing tables: https://ssd.jpl.nasa.gov/ftp/ssd/debias/debias_2018.tgz , https://ssd.jpl.nasa.gov/ftp/ssd/debias/debias_hires2018.tgz
- ESA NEOCC computer access: https://neo.ssa.esa.int/computer-access ; example files https://neo.ssa.esa.int/PSDB-portlet/download?file=480883.ke0 , https://neo.ssa.esa.int/PSDB-portlet/download?file=480883.rwo
- ESA NEOCC Yarkovsky news item: https://neo.ssa.esa.int/-/neocc-provides-up-to-date-determinations-of-the-yarkovsky-effect
- Gaia release schedule: https://www.cosmos.esa.int/web/gaia/release

Papers
- Fenucci et al. 2024, NEOCC automated Yarkovsky procedure: https://arxiv.org/abs/2311.10175
- Fenucci et al. 2025, Kamo'oalewa (this is arXiv 2502.13222): https://arxiv.org/abs/2502.13222
- Greenberg et al. 2020: https://arxiv.org/abs/1708.05513
- Del Vigna et al. 2018: https://arxiv.org/abs/1805.05947
- Farnocchia et al. 2013: https://arxiv.org/abs/1212.4812
- Dziadura et al. 2023: https://ui.adsabs.harvard.edu/abs/2023A&A...680A..77D ; Dziadura et al. 2024: https://arxiv.org/abs/2411.09750
- Seligman et al. 2023, dark comets: https://arxiv.org/abs/2212.08115 ; two populations: https://www.pnas.org/doi/10.1073/pnas.2406424121 ; misidentification: https://arxiv.org/abs/2410.06874 ; 1998 SH2 news: https://phys.org/news/2026-07-asteroid-unexplained-orbital-shift-dark.html
- Veres et al. 2017: https://arxiv.org/abs/1703.03479
- Eggl et al. 2020: https://arxiv.org/abs/1909.04558
- Chesley et al. 2014, Bennu: https://arxiv.org/abs/1402.5573
- Perez-Hernandez and Benet 2022, Apophis: cited in https://github.com/PerezHz/NEOs.jl
