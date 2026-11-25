# Verification: orbit-fitting probe reproduced, plus injection-recovery, degrade and short-arc tests

Independent check of `orbit-tooling.md` (first round, 2026-11-20). Run on 2026-11-21, 09:35 to 10:20 local. Status: COMPLETE.

Work area: `data/research/probe-fit2`. Its `out/` JSON was kept; its `logs/` and `dl/` cached downloads were not.
Scripts: `data/research/scripts/fr_*.py`:
`fr_common.py` (helpers), `fr_fetch.py` (sequential cached downloads), `fr_repro.py` (step 1), `fr_inject.py` and `fr_summ.py` (step 2), `fr_null.py` (empirical null), `fr_degrade.py` (step 3), `fr_short.py` and `fr_cd3.py` (step 4), `fr_select.py` and `fr_pick.py` (samples from the local snapshots).

Network use: 75 MPC `get-obs` requests, 75 JPL `sbdb.api` requests, 2 JPL `sb_radar.api` requests, all strictly sequential with a 2 s pause, generic User-Agent, no failures.

## Bottom line

1. **The first-round probe reproduces.** GRSS 4.6.0 installs and runs as described. Six of the first round's eight JPL matches were rerun and reproduce to the printed digits (2001 YE4, 2009 BD, 2011 PT, 2012 LA, 2003 RM, 2026 QQ8). Two new objects (2011 MD, 2015 TC25) also match JPL within 0.3 combined sigma. Nyx and Aten (Gaia data) were not rerun.
2. **A uniform catalog of A1 (area-to-mass) and A2 posteriors with upper limits and measured detection efficiency is technically achievable on this machine.** 9,000 synthetic refits for 15 objects ran in under ten minutes of wall time. On arcs of 60 d to 10 yr, 8,499 of 8,500 synthetic fits converged; the real-data failures were one gravity-only fit (2021 ER, which converges once A2 is added) and one A1+A2 fit on a 17-year, 22-position arc (2007 XB23).
3. **It will be informative for few objects.** Of 16 NHATS objects with H >= 27, arc >= 60 d and no JPL A1, five have sigma(A1) at or below 3.5e-11 au/d^2 (can tell "below roughly 400 to 1,500 kg/m3" from "denser"); the other eleven constrain nothing physical. No object in the sample can separate rock (2,500) from metal (7,500 kg/m3).
4. **Arc length does not predict sensitivity.** Sigma(A1) spans a factor 250 inside the 60 to 190 day class and a factor 300 inside the 1 to 2 year class. The number of separate nights after a slow close approach decides it.
5. **Error bars: keep the formal ones, calibrate them, never rescale by reduced chi-square.** Formal sigmas are conservative by about 1.5 (empirical null on 30 real objects: standard deviation of A1/sigma is 0.64). Rescaled sigmas are overconfident (null standard deviation 1.34 to 1.59; false-alarm rate up to 46% in injection tests; 2009 BD truncated-arc intervals miss the long-arc value at 2.4 to 2.8 sigma).
6. **Short-arc non-convergence is fixable.** Fitting a Cartesian state instead of cometary elements converged 40 of 40 fits on arcs of 0.7 to 23 days, against 32 of 40 for the first-round configuration.
7. **2020 CD3 is only partly fixable.** The 95-day arc after escape fits cleanly (A1 = 1.67e-10 +- 0.20e-10, 8 sigma, 1.6 combined sigma from JPL). Adding the 2018 and 2019 precoveries from the captured phase fails in GRSS under every variant tried.

## 0. Setup, as run

- `uv venv --python 3.12 .venv` (CPython 3.12.13), `uv pip install grss`: GRSS 4.6.0, under 1 s from the uv cache.
- First `import grss`: 2 min 45 s wall, peak resident memory 7.30 GB (`/usr/bin/time -v`: 7,296,592 kB), venv 5.3 GB afterwards. It downloaded both debias tables, DE430, sb431-n16s, DE440, sb441-n16s, DE441 (3.31 GB), sb441-n16 (646 MB), four Earth/Moon PCKs. First-round figures confirmed.
- Later imports cost 1.5 to 3.5 s per process. The venv `bin` must be on PATH (GRSS shells out to `python`). Every import sets `OMP_NUM_THREADS` to the CPU count; the helper pins it to 1 before forking workers.
- CPU: AMD Ryzen 9 9950X, 16 physical cores, 32 threads. "32 cores" means 32 hardware threads. With 28 worker processes a fit takes about 1.4 times its single-process time.
- All fits unless stated: initial six elements from JPL SBDB at the covariance epoch, every non-gravitational parameter started at zero, MPC `get-obs` ADES XML, Eggl 2020 low-resolution debias, Veres 2017 weights, sqrt(N/4) same-night de-weighting, DE440, one thread, GRSS default outlier rejection (chi 3.0 / 2.8), 1/r^2 law.
- A bug in the helper restored from the interrupted attempt was fixed before any number below was produced: its "gravity-only" fit kept JPL's A1/A2 as fixed values. By code reading, GRSS's own `get_sbdb_info` invites the same mistake (it returns JPL's non-grav values in `nongrav_info`, and `FitSimulation` holds any non-estimated value fixed), so a pipeline that passes that dictionary unchanged to a "gravity-only" fit is not fitting gravity only.
- GRSS source read (`fit_simulation.py`): plain Gauss-Newton, no step control; convergence when weighted RMS changes by less than 1e-4 or all corrections are below 1e-3 sigma; outlier rejection starts after a first convergence; numerical partials by default (analytic ones exist behind `analytic_partials`).

## 1. Reproduction of published values

Command: `fr_repro.py "<des>" --models "" a1 a2 a1,a2`. Results: `data/research/probe-fit2/out/repro_*.json` (the logs were not kept).

| Object | Data used | Model | GRSS today | JPL SBDB today | Difference | Fit wall time |
|---|---|---|---|---|---|---|
| (480883) 2001 YE4 | 450 optical + 7 radar, 8,762 d | A2 | -6.9086e-14 +- 7.41e-16 (S/N 93.3) | -6.9496e-14 +- 9.16e-16 | +0.35 combined sigma | 21.6 s gravity-only, 12.7 s A2 |
| 2009 BD | 190 optical, 886 d | A1+A2 | A1 5.275e-11 +- 9.66e-12; A2 -1.119e-12 +- 1.53e-13 | A1 5.605e-11 +- 8.51e-12; A2 -1.146e-12 +- 8.37e-14 | -0.26 and +0.15 | 0.96 s |
| 2011 MD (new) | 1,559 optical, **74.2 d** | A1+A2 | A1 7.667e-11 +- 2.52e-11 (S/N 3.0); A2 +4.1e-11 +- 3.6e-11 | A1 7.429e-11 +- 2.48e-11; A2 -6.3e-13 +- 3.8e-12 | A1 +0.07; sigma(A2) 9.5 times JPL's | 2.5 s |
| 2011 MD (new) | same | A1 | 8.183e-11 +- 2.49e-11 = A/m (3.61 +- 1.10)e-4 m2/kg, C_R = 1 | | +0.21 | 2.2 s |
| 2015 TC25 (new) | 46 optical + 2 Doppler, 562 d | A1+A2 | A1 1.545e-10 +- 2.61e-11 (S/N 5.9); A2 -4.31e-12 +- 3.22e-12 | A1 1.599e-10 +- 2.13e-11; A2 -5.27e-12 +- 2.77e-12 | -0.16 and +0.23 | 0.93 s |
| (499998) 2011 PT | 200 optical, 2,300 d | A2 | -2.1259e-13 +- 3.03e-14 | -2.1212e-13 +- 3.01e-14 | -0.01 | 3.0 s |
| 2012 LA | 98 optical, 179 d | A1 | 6.504e-11 +- 1.27e-11 | 6.713e-11 +- 1.19e-11 | -0.12 | 0.40 s |
| 2026 QQ8 | 73 optical, 93 d (63 yesterday) | A1 | 1.333e-10 +- 8.5e-12 (S/N 15.6) | 1.306e-10 +- 1.00e-11 | +0.21 | 0.34 s |
| (523599) 2003 RM | 409 optical, 7,402 d | A2, Marsden comet law | 3.2964e-12 +- 3.82e-14 | 3.2869e-12 +- 2.98e-14 | +0.20 | 3.5 s |
| (523599) 2003 RM | same | A2, 1/r^2 law | **2.1003e-12 +- 2.44e-14** | | -31 | 3.5 s |

Every first-round number rerun here is reproduced, with the same timings. Notes that matter for the plan:

1. **2003 RM matches JPL only under the comet law.** JPL's record for 2003 RM lists A2 and no g(r) parameters; by JPL convention that means the Marsden water-ice law, and GRSS's `get_sbdb_info` silently applies it. Under 1/r^2 the same data give an A2 that is 0.64 times as large, with the same chi-square (178.9 against 176.3). The first-round table did not say this. SBDB A2 values are not all on one law, and the bulk snapshot does not carry the g(r) fields, so the law of each of the 618 A2 values is unknown without per-object queries.
2. **2011 MD: the public arc is 74 days, JPL's is 967 days.** The MPC returns 1,559 positions from 2011-06-21 to 2011-09-03. JPL uses 532 observations to 2014-02-12 (the 2014 Spitzer detection). A1 and its sigma are the same either way; sigma(A2) is 9.5 times larger from public data.
3. **Published 2011 MD value.** Micheli et al. 2014 (arXiv 1403.6033) give A/m = (0.32 +- 0.06)e-3 m2/kg, 5 sigma, from their own formal error bars plus 0.05 arcsec. Public data with Veres weights give (3.4 to 3.6) +- 1.1 e-4: same value, 3.0 to 3.3 sigma. The published precision is not reproducible from the MPC file because the authors' per-observation uncertainties are not in it (0 of 1,559 records carry `rmsRA`).
4. **Model choice moves A1 by more than its error bar.** 2009 BD: A1-only 8.47e-11 +- 8.6e-12, A1+A2 5.28e-11 +- 9.7e-12 (3.3 sigma apart, a factor 1.6 in implied density). 2015 TC25: A2-only gives a 9-sigma value 3.6 times JPL's A2. 2011 CL50 (JPL A2, 10-year arc): A1-only gives A1 = -8.4e-10 +- 1.4e-10, a 5.9-sigma result with the wrong sign; with A1+A2 the A2 is 4.88e-12 +- 3.5e-13 (JPL 4.38e-12 +- 2.9e-13, +1.1 combined sigma). 2007 XB23 (22 positions over 17 years): A1-only gives 5.2e-9 +- 1.7e-9, a formal 3.1-sigma unphysical value.
5. Reduced chi-square of converged fits: 0.07 (2011 MD) to 0.29. The standard weights are conservative (first-round claim confirmed).
6. Outlier rejection under the wrong model (first-round claim confirmed): gravity-only fit of 2001 YE4 rejects 72 of 457, the A2 fit 1; 2003 RM 148 of 409 against 4; 2015 TC25 7 of 48 against 0.
7. The data move. For 2026 QQ8 the MPC returned 73 positions today against 63 in the first-round run; 2022 RD2 and 2021 ER have positions at the MPC that JPL's current solutions do not use (section 2.3).

## 2. Injection-recovery

### 2.1 Method (what was actually done)

GRSS's `simulated_obs` option places a fictitious geocentric station, so it was not used. Instead (`fr_inject.py`):

1. Real data: gravity-only, A1, and A1+A2 fits.
2. Truth orbit = real gravity-only best-fit elements plus an injected A1. One evaluation of GRSS's own observation model at the truth orbit (zero-length step) gives residuals; subtracting them from the real positions gives noiseless synthetic positions at the real times and stations with the real debias values. Self-check: residuals of the noiseless set at the truth orbit are below 3e-10 arcsec.
3. Two noise models. "gauss": independent Gaussian, covariance = s^2 times the per-observation covariance GRSS used in the real fit, s = real normalised residual RMS (0.29 to 0.95). "wild": the real residual vectors of the real A1 fit, each same-station same-night tracklet multiplied by a random sign (keeps real within-night correlation and tails). Observations rejected in the real fit are left out.
4. Refit each trial with the same pipeline, A1 from zero, outlier rejection on.
5. Injected A1 = 2.266e-7 x 1.5 / (rho x D) au/d^2 (sphere, C_R = 1), D from H at albedo 0.15, for 500, 1,200, 2,500, 7,500 kg/m3 and zero.
6. Detection = abs(A1)/sigma >= 3, with the formal sigma, or with the formal sigma times sqrt(reduced chi-square) ("rescaled").

Neither noise model contains errors correlated between nights (station timing offsets, catalog zone errors). False-alarm rates from injection are lower bounds; section 2.4 tests real data.

### 2.2 Three objects, 100 trials per case (1,000 fits per object)

Chosen by hand for different arc structure. Clustering (days from first observation): 2022 NX1: 168 positions in days 0 to 31, 3 on day 56, 2 on day 142. 2020 VN1: 143 in days 0 to 17, 3 in days 453 to 474, 1 on day 500. 2015 XX169: 40 in days 0 to 4, 13 in days 362 to 367, 4 on day 730.

Fraction of trials with a 3-sigma detection, written formal / rescaled:

| Injected density (kg/m3) | 2022 NX1 (8.4 m, 142 d, 24 nights): gauss | wild | 2020 VN1 (8.9 m, 500 d, 18 nights): gauss | wild | 2015 XX169 (11.4 m, 730 d, 7 nights): gauss | wild |
|---|---|---|---|---|---|---|
| none (false alarms) | 0.00 / 0.01 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / **0.18** | 0.00 / 0.00 | 0.00 / 0.00 |
| 7,500 | 0.00 / 0.01 | 0.00 / 0.00 | 0.00 / 0.03 | 0.00 / 0.10 | 0.00 / 0.00 | 0.00 / 0.00 |
| 2,500 | 0.00 / 0.04 | 0.00 / 0.00 | 0.00 / 0.06 | 0.00 / 0.28 | 0.00 / 0.01 | 0.00 / 0.00 |
| 1,200 | 0.00 / 0.31 | 0.00 / 0.19 | 0.00 / 0.28 | 0.00 / 0.39 | 0.00 / 0.00 | 0.00 / 0.00 |
| 500 | 0.20 / 0.98 | 0.09 / 1.00 | 0.02 / 1.00 | 0.13 / 0.94 | 0.00 / 0.00 | 0.00 / 0.00 |

Formal sigma(A1): 3.17e-11, 3.50e-11, 6.47e-10. Scatter of recovered A1 (gauss / wild): 1.67e-11 / 1.05e-11; 1.32e-11 / 2.59e-11; 2.49e-10 / 1.80e-10. Recovered A1 is unbiased (mean within 0.15 formal sigma of the injected value). All 3,000 fits converged; 17 to 34 s wall per object on 28 processes.

Joint A1+A2 estimation (50 trials per case): 2020 VN1: sigma(A1) 3.71e-11; with wild noise the scatter of A1 equals the formal sigma (pull standard deviation 1.0) and the rescaled rule gives **46% false alarms**. 2022 OC3: wild pull standard deviation 0.6 to 0.7, rescaled false alarms 4%.

### 2.3 Wider sample: 13 more objects by a fixed rule

Rule (`fr_pick.py`): the 62 NHATS objects with H >= 27, arc >= 60 d, no JPL A1 and no radar, sorted by arc, every fifth. 50 trials per case. 12 of the 13 completed (2021 ER: gravity-only fit did not converge, see below). Sorted by formal sigma, with the three hand-picked objects included:

| Object | H | D (m) | Arc (d) | Positions | Nights | Real-data A1 +- formal sigma (S/N) | True scatter, gauss / wild | Density giving exactly 3 formal sigma (kg/m3) | Detected at 500, formal (g/w) | at 1,200, formal (g/w) | at 2,500, formal (g/w) | s per fit |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 PT5 | 27.45 | 11.1 | 190 | 409 | 74 | +1.98e-11 +- 6.63e-12 (3.0) | 3.1e-12 / 4.9e-12 | 1,539 | 1.00 / 1.00 | 0.94 / 0.78 | 0.02 / 0.04 | 1.45 |
| 2022 RD2 | 28.58 | 6.6 | 170 | 46 | 14 | +8.83e-11 +- 1.72e-11 (5.1) | 9.0e-12 / 1.1e-11 | 996 | 1.00 / 1.00 | 0.16 / 0.28 | 0 / 0 | 0.77 |
| 2022 NX1 | 28.07 | 8.3 | 142 | 172 | 24 | +7.08e-11 +- 3.17e-11 (2.2) | 1.7e-11 / 1.1e-11 | 429 | 0.20 / 0.09 | 0 / 0 | 0 / 0 | 0.47 |
| 2022 OC3 | 28.83 | 5.9 | 1,299 | 82 | 12 | +5.82e-11 +- 3.24e-11 (1.8) | 1.4e-11 / 2.1e-11 | 594 | 0.92 / 0.76 | 0 / 0 | 0 / 0 | 3.07 |
| 2020 VN1 | 27.93 | 8.9 | 500 | 146 | 18 | +2.21e-11 +- 3.50e-11 (0.6) | 1.3e-11 / 2.6e-11 | 363 | 0.02 / 0.13 | 0 / 0 | 0 / 0 | 0.77 |
| 2020 SQ | 27.26 | 12.1 | 567 | 52 | 13 | -2.1e-11 +- 9.56e-11 (0.2) | 7.9e-11 / 3.3e-11 | 98 | 0 / 0 | 0 / 0 | 0 / 0 | 1.09 |
| 2011 CL50 (A2 object, A1-only model is wrong) | 27.30 | 11.9 | 3,628 | 130 | 23 | -8.38e-10 +- 1.42e-10 (5.9, spurious) | 1.3e-10 / 2.9e-10 | 67 | 0 / 0.22 | 0 / 0.18 | 0 / 0.26 | 11.0 |
| 2020 SP | 27.10 | 13.0 | 171 | 32 | 8 | -8.3e-11 +- 1.57e-10 (0.5) | 6.8e-11 / 4.8e-11 | 55 | 0 / 0 | 0 / 0 | 0 / 0 | 0.77 |
| 2019 GM1 | 27.25 | 12.2 | 1,090 | 39 | 7 | -8.8e-11 +- 4.75e-10 (0.2) | 1.4e-10 / 1.0e-10 | 20 | 0 / 0 | 0 / 0 | 0 / 0 | 2.11 |
| 2018 TS4 | 27.60 | 10.4 | 125 | 28 | 6 | +1.8e-10 +- 5.95e-10 (0.3) | 2.4e-10 / 1.3e-10 | 18 | 0 / 0 | 0 / 0 | 0 / 0 | 0.61 |
| 2021 VF11 | 27.24 | 12.2 | 69 | 30 | 11 | +3.7e-10 +- 6.26e-10 (0.6) | 3.3e-10 / 4.2e-10 | 15 | 0 / 0 | 0 / 0 | 0 / 0 | 0.57 |
| 2015 XX169 | 27.40 | 11.4 | 730 | 57 | 7 | -2.7e-10 +- 6.47e-10 (0.4) | 2.5e-10 / 1.8e-10 | 15 | 0 / 0 | 0 / 0 | 0 / 0 | 0.97 |
| 2020 VV | 27.28 | 12.0 | 61 | 78 | 21 | -1.5e-09 +- 1.68e-09 (0.9) | 8.4e-10 / 4.8e-10 | 6 | 0 / 0 | 0 / 0 | 0 / 0 | 0.42 |
| 2007 XB23 (A2 object, 17-year arc, A1-only model is wrong) | 27.10 | 13.0 | 6,208 | 20 | 5 | +5.25e-09 +- 1.70e-09 (3.1, spurious) | 9.9e-10 / 1.9e-09 | 5 | 0 / 0 | 0 / 0 | 0 / 0 | 11.3 |
| 2023 GC2 | 27.29 | 12.0 | 369 | 21 | 5 | +1.0e-08 +- 1.05e-08 (1.0) | 6.4e-09 / 2.8e-09 | 1 | 0 / 0 | 0 / 0 | 0 / 0 | 1.07 |

Over these 15 objects (9,000 synthetic fits; non-converged: 1 of 8,500 on arcs up to 10 years, 55 of 500 on 2007 XB23): false alarms with the formal rule were zero in every correctly specified case, and 14% with wild noise in the mis-specified case 2011 CL50 (A1-only model on an object with a real A2). True scatter divided by formal sigma: median 0.50 (gauss) and 0.34 (wild), range 0.22 to 2.0.

Reading:

- Five of 16 objects (the 15 above plus 2021 ER) reach sigma(A1) <= 3.5e-11. Only one (2024 PT5: 409 positions on 74 nights) would detect a 1,200 kg/m3 body at formal 3 sigma. None detects 2,500 kg/m3.
- With the formal rule the pipeline is safe but blunt. With the rescaled rule it finds 500 kg/m3 nearly always and 1,200 kg/m3 in 19 to 39% of trials on the better objects, at the cost of false-alarm rates up to 18% (A1 only) and 46% (A1+A2).
- Three real-data results in this small sample are not in JPL SBDB and show what a uniform run will surface:
  - **2024 PT5**: A1 = +1.98e-11 +- 0.66e-11, A/m = (8.8 +- 2.9)e-5 m2/kg, formal 3.0 sigma. Agrees with the Bolin et al. value (7.0e-5) quoted in the first-round summary and disagrees with zero at 3 formal sigma.
  - **2022 RD2** (minimum delta-v 3.5 km/s): A1 = +8.8e-11 +- 1.7e-11 (5.1 formal sigma), A/m = 3.9e-4 m2/kg, about 580 kg/m3 at albedo 0.15. **It rests on one position.** The MPC holds a single 2023-01-17 position from station T12 that JPL's solution (dated 2024-10-10, 45 observations, 84-day arc) does not use. Without it: A1 = 7.2e-11 +- 4.3e-11 (1.7 sigma); without the last two single positions: no constraint. One web search found no publication.
  - **2021 ER** (H 27.0, two apparitions: 94 positions in March-April 2021, 11 in March 2026): the gravity-only fit does not converge and rejects 13 of 105; with A2 the fit converges, A2 = -1.76e-12 +- 0.15e-12 (S/N 11.6). JPL lists a gravity-only orbit with RMS 0.77 arcsec, the highest in the sample. Two apparitions give one along-track constraint, so this needs the frozen-mask comparison and a second engine before it means anything.
- 2022 NX1: A1 = +7.1e-11 +- 3.2e-11 is 2.2 formal sigma, 4.4 rescaled sigma and 6.7 times the wild-noise scatter. The catalog must show the posterior, not a flag.

### 2.4 Empirical null on real data (new; the first round recommended it and did not run it)

`fr_null.py`: 30 near-Earth asteroids drawn with a fixed seed from the 283 with H <= 21.5, arc 90 to 200 d, 60 to 250 observations, no radar, no JPL non-grav. Their diameters are 190 to 730 m at albedo 0.15, so the expected A1 (0.5 to 1.8e-12 at 1,000 kg/m3) is 100 to 10,000 times below their sigma(A1). Any "signal" is noise. All 120 fits (gravity-only, A1, A2, A1+A2) converged, median 0.6 s each. In the joint A1+A2 fit the standard deviations of A1/sigma and A2/sigma are 0.71 and 0.80.

| Statistic over 30 objects | mean | standard deviation | max abs | count >= 2 (Gaussian expectation 1.4) | count >= 3 (expectation 0.08) |
|---|---|---|---|---|---|
| A1 / formal sigma | +0.23 | 0.64 | 2.11 | 1 | 0 |
| A1 / rescaled sigma | +0.48 | 1.34 | 3.98 | 3 | 1 |
| A2 / formal sigma | +0.06 | 0.75 | 1.66 | 0 | 0 |
| A2 / rescaled sigma | +0.09 | 1.59 | 3.09 | 7 | 1 |

Reading: on real data the true error is about 0.64 (A1) to 0.75 (A2) of the formal sigma, with a statistical uncertainty of 13% on those factors. White-noise simulation would have said 0.45. The rescaled sigma understates the error by 1.3 to 1.6 and produces 3-sigma false alarms in 1 of 30 objects for each parameter. Limits of this test: 30 objects; these are distant objects (MOID mostly 0.1 to 0.3 au), not slow close approachers, so trailing and timing errors are milder than for NHATS targets. The mean of +0.23 for A1 is 2 standard errors from zero; worth watching in a larger sample.

## 3. Degrade a known object

`fr_degrade.py "<des>" --cuts 30 60 120 300`. Cut by time since first observation; de-weighting recomputed on the cut set; non-gravs from zero.

2009 BD (119 positions in days 0 to 9.8, 3 in days 275 to 289, 68 in days 867 to 886). Reference: full-arc A1+A2 fit, A1 = 5.275e-11 +- 9.65e-12.

| Cut | Actual arc, positions, nights | Model | A1 +- formal sigma | Reference sits at (formal / rescaled sigma) |
|---|---|---|---|---|
| first 30, 60 or 120 d (identical data) | 9.8 d, 119, 9 | A1 | -2.30e-10 +- 3.02e-10 | +0.94 / +2.43 |
| | | A1+A2 | +2.48e-10 +- 9.84e-10 | -0.20 / -0.52 |
| first 300 d | 289 d, 122, 11 | A1 | +3.73e-11 +- 1.43e-11 (S/N 2.6) | +1.08 / +2.84 |
| | | A1+A2 | +3.36e-11 +- 6.58e-11 | +0.29 / +0.76 |

2011 MD (1,543 positions in days 0 to 11.8, 13 in days 41 to 47, 3 in days 69 to 74). Reference: full public arc, A1 = 8.18e-11 +- 2.49e-11; JPL 7.43e-11 +- 2.48e-11.

| Cut | Actual arc, positions, nights | A1 +- formal sigma (A1 model) | Full-arc value at (formal / rescaled) | JPL value at (formal) |
|---|---|---|---|---|
| first 30 d | 11.8 d, 1,543, 12 | -1.1e-11 +- 4.70e-10 | +0.20 / +0.74 | +0.18 |
| first 60 d | 47.3 d, 1,556, 15 | +9.02e-11 +- 3.81e-11 (S/N 2.4) | -0.22 / -0.80 | -0.42 |
| first 120 d = full | 74.2 d, 1,559, 17 | +8.18e-11 +- 2.49e-11 (S/N 3.3) | 0 | -0.30 |

Two extra objects with strong published signals: 2026 QQ8 (full 93 d: 1.333e-10 +- 8.5e-12): first 30 d (16.6 d, 5 nights) 7.8e-10 +- 1.2e-9, full value at -0.54 sigma; first 60 d (50.7 d, 7 nights) 1.47e-10 +- 9.6e-11, at -0.14. 2012 LA (full 179 d: 6.50e-11 +- 1.27e-11): first 30 d 1.43e-9 +- 1.57e-9 (-0.87); first 60 d -4.7e-11 +- 1.9e-10 (+0.59); first 120 d 6.42e-11 +- 2.8e-11 (+0.03).

Reading:

- **The formal interval covered the long-arc value in all 13 truncated fits** (largest offset 1.08 formal sigma).
- The rescaled interval missed at more than 2 sigma in 3 of 13 (2.43 and 2.84 on 2009 BD, 2.82 on the 2011 MD 30-day A1+A2 fit), against an expectation of 0.6.
- One caveat: the full-arc A1-only value of 2009 BD (8.47e-11) is 3.3 formal sigma from the 300-day A1-only value. That is model error in the full-arc A1-only fit (Yarkovsky absorbed into A1), not a short-arc coverage failure.
- Real arcs are clumps. "First 30, 60, 120 days" is one data set for 2009 BD.
- For 2011 MD, 13 positions on days 41 to 47 cut sigma(A1) by a factor 12 and 3 more on days 69 to 74 by another 1.5. The first 12 days, with 1,543 positions, carry no radiation-pressure information (density above 28 kg/m3).

## 4. Short arcs and 2020 CD3

### 4.1 Short arcs: fixable

`fr_short.py`: 20 NHATS objects, five drawn with a fixed seed from each arc bin (0 to 3, 3 to 7, 7 to 14, 14 to 24 d); actual arcs 0.7 to 23 d, 12 to 96 positions. Gravity-only and A1 fits, seven variants each (280 fits).

| Variant | Gravity-only converged | A1 converged |
|---|---|---|
| Cometary elements at JPL epoch, 20 iterations (first-round configuration) | 17 / 20 | 15 / 20 |
| Same, 100 iterations | 19 / 20 | 18 / 20 |
| **Barycentric Cartesian state at JPL epoch** | **20 / 20** | **20 / 20** |
| **Cartesian state at mid-arc epoch** | **20 / 20** | **20 / 20** |
| Cometary, damped first three steps (0.3, 0.5, 0.7) | 18 / 20 | 16 / 20 |
| Cometary, every step halved, 60 iterations | 19 / 20 | 16 / 20 |
| Cometary, a priori constraint at 10 times JPL sigma | 17 / 20 | 16 / 20 |

- The first-round failure rate is reproduced (8 of 40, 20%; first round 23%). All eight failures were on arcs of 12 days or less.
- The cause is the cometary-element parametrisation with full Gauss-Newton steps: the weighted RMS oscillates at the 1e-3 to 1e-1 level along the poorly determined direction and never meets the tolerance.
- Cartesian fits converged in a median of 4 iterations (maximum 11), 0.06 to 0.4 s each, and give the same weighted RMS and the same A1 +- sigma as the cometary fit wherever that one converged (two gravity-only fits, 2014 JY30 and 2015 YT1, differ only because the cometary run rejected one or two more positions). Epoch choice made no difference (JPL's covariance epoch already lies inside these arcs). Damping and priors did not help.
- These objects still carry no dynamical information: sigma(A1) from 6e-10 to 2e-5 au/d^2, which is 6 to 200,000 times the physical scale of 1e-10. But the label can now be a measured, converged upper limit instead of "fit failed".
- Caveats: 40 of 40 gives a 95% upper bound of about 7% on the failure rate, not zero. The start was JPL's orbit, which was fitted to the same data; a cold start needs initial orbit determination (not tested).

### 4.2 2020 CD3: the post-escape arc fits, the captured phase does not

`fr_cd3.py`. Public data: 5 positions on 2018-05-09, 7 in January 2019, 132 from 2020-02-15 to 2020-05-20.

| Attempt | Result |
|---|---|
| JPL elements and JPL A1, residuals only (cometary or Cartesian) | Unweighted RMS 11,544 arcsec (first round: 11,558). JPL's own solution does not reproduce the observations when propagated in GRSS. |
| Cometary, full arc, A1 from JPL value | 20 iterations, no convergence, RMS 154 arcsec |
| Cometary, full arc, A1 from zero | Crash: `get_ca_or_impact_time: Root must be bracketed` |
| Cartesian at JPL epoch, full arc, A1 from zero | 30 iterations, no convergence, RMS 22 arcsec |
| **Cartesian, 2020 apparition only (132 positions, 95 d), A1 from zero** | **Converged in 4 iterations, 0.5 s, 1 rejected, reduced chi-square 0.29. A1 = 1.675e-10 +- 2.03e-11 (S/N 8.2); JPL full-arc 1.357e-10 +- 2.5e-12; +1.55 combined sigma** |
| Then adding January 2019 (139 positions), numerical or analytic partials | No convergence in 40 iterations; weighted RMS stalls at 2.76 (reduced chi-square 7.8) |
| Then adding May 2018 (full arc) | No convergence (RMS 270 arcsec), or `SVD did not converge` with analytic partials |

Conclusion: label such objects "fitted on the heliocentric arc only; captured phase not modelled", with the wider error bar (here 8 times JPL's). Whether the stall is GRSS's Earth gravity model during repeated perigee passes or chaos defeating Gauss-Newton was not resolved in the time box. layup was not retested.

## 5. Conclusions

### 5.1 Is the uniform catalog technically achievable here? Yes.

- Measured per-fit time, one core: 0.06 to 0.5 s (arcs under 30 d), 0.3 to 1.5 s (60 d to 2 yr), 2 to 3 s (3 to 4 yr), 5 to 11 s (5 to 17 yr), 13 to 22 s (24 yr with radar).
- Measured throughput: 1,000 injection fits in 17 to 34 s on 28 processes for sub-2-year arcs (about 30 to 60 fits per second).
- Budget: five models for each of 7,229 NHATS objects is about 7 core-hours, 15 to 20 minutes of wall time. Injection-recovery at 1,000 fits per object for the 74 radiation-pressure candidates is about 20 core-hours, under an hour. For the roughly 800 multi-apparition objects at 200 fits per object it is 8 to 11 hours.
- Data access is the slow step: one MPC request per object took 0.6 to 2.5 s (75 of 75 succeeded); JPL per-object requests must be sequential.
- What makes it a catalog rather than a pile of fits: Cartesian parametrisation (converges on every arc tried), A1+A2 fitted jointly, formal covariance kept, a calibration factor from an empirical null, injection-recovery per object with the tracklet sign-flip noise model, and explicit flags (below).

### 5.2 Density discrimination for a 5 to 10 m object

For D = 7.5 m, A1 is 9.1e-11 (500 kg/m3), 3.8e-11 (1,200), 1.8e-11 (2,500), 6.0e-12 (7,500).

| | 100-day class (61 to 190 d; 7 sampled objects) | 2-year class (369 to 730 d; 4 sampled objects) |
|---|---|---|
| Formal sigma(A1), range | 6.6e-12 to 1.7e-9 | 3.5e-11 to 1.0e-8 |
| Formal sigma(A1), median | 1.6e-10 | about 3.7e-10 |
| Typical object | no constraint (density above about 50 kg/m3) | no constraint |
| Best object | 2024 PT5: 1,200 kg/m3 detected in 78 to 94% of trials; 2,500 in 2 to 4% | 2020 VN1: 500 kg/m3 detected in 2 to 13% of trials (formal rule) |
| Rock against metal (2,500 against 7,500) | not separable in any object | not separable in any object |
| Yarkovsky (A2) | none | sigma(A2) 4e-12 to 2e-11, above the expected maximum of about 2e-12; useful only from about 5 years |

- A 2-year arc is not better than a 100-day arc for radiation pressure. What helps is many separate nights during and after a slow close approach, and a few late faint positions (2011 MD, 2022 RD2). Arcs of 3 to 5 years start to add A2 (2022 OC3: sigma(A2) 1.5e-12; 2021 ER: 1.5e-13).
- The realistic per-object statement is an upper limit on area-to-mass. For about a third of the H >= 27, arc >= 60 d set it excludes densities below roughly 400 to 1,500 kg/m3 at albedo 0.15; for the rest it excludes at most artificial-object values: an area-to-mass of 1e-2 m2/kg (A1 = 2.3e-9) would be a 3-formal-sigma signal on 12 of the 15 sampled objects, and 1e-3 m2/kg on 5.
- Area-to-mass becomes density only through a size. An albedo between 0.05 and 0.5 moves D by a factor 3.2 and the density by the same factor, whatever the precision of A1.
- With calibrated (0.65 times formal) error bars the detection thresholds above improve by about a third: still not enough for 2,500 kg/m3 anywhere in the sample.

### 5.3 Traps

1. **Rescaling the covariance by reduced chi-square.** Overconfident on every test: null standard deviation 1.34 to 1.59, injection false alarms up to 46%, truncated-arc misses at 2.4 to 2.8 sigma.
2. **White-noise injection overstates sensitivity and understates false alarms.** Use the tracklet sign-flip model and calibrate against a real-data null drawn from objects that resemble the targets.
3. **Formal sigma is conservative by about 1.5**, so "3 sigma formal" is about 4.7 sigma. A fixed formal threshold throws away real detections (2024 PT5, 2022 NX1 sit at 2 to 3 formal sigma).
4. **A1-only or A2-only models on multi-apparition arcs** produce confident wrong numbers (2009 BD, 2011 CL50, 2007 XB23, 2015 TC25).
5. **Single-observation dependence.** 2022 RD2 goes from 5.1 to 1.7 sigma when one position is removed. Leave-one-tracklet-out must be part of every entry.
6. **Selecting by arc length.** "H >= 27 and arc >= 60 d" (74 objects) is about one-third informative. Select by formal sigma(A1) from a first-pass fit.
7. **g(r) law.** JPL's A2 for 2003 RM is on the comet law; under 1/r^2 it is 0.64 times as large with the same fit quality. Record the law with every value; do not mix.
8. **Public data differ from JPL's data in both directions** (2011 MD: JPL has 2014 positions the MPC does not; 2022 RD2, 2021 ER, 2026 QQ8: the MPC has positions JPL's solution does not use). "Matches JPL" is a moving target; snapshot both with dates.
9. **GRSS specifics.** Cometary-element fits fail on short arcs (use Cartesian). `get_sbdb_info` keeps JPL's non-gravs fixed in a "gravity-only" fit and applies the comet law when JPL lists none. Every import resets `OMP_NUM_THREADS` to all CPUs. Gravity-only fits on objects with real non-gravs "converge" by rejecting data (2001 YE4 72 of 457, 2003 RM 148 of 409) or do not converge (2021 ER).
10. **Captured objects.** Only the heliocentric part of the arc can be fitted with this tool.
11. **Clumped arcs.** Truncation tests, forecasts and "arc" columns should be expressed in nights and visits, not days.

## Verdicts on first-round claims

| Claim | Verdict | Evidence |
|---|---|---|
| GRSS 4.6.0 installs with `uv pip install grss`; first import downloads about 4.3 GB in about 2.5 min, peak about 7 GB RAM | Confirmed | 2 min 45 s, 7.30 GB peak, venv 5.3 GB |
| GRSS matched JPL within 1 sigma on 8 of 9 objects, seconds per fit | Partly confirmed | 6 of the 8 rerun and reproduced exactly; Nyx and Aten not rerun. The 2003 RM match holds only under the Marsden comet law, which the first round did not state |
| 2001 YE4: A2 -6.909e-14 +- 7.41e-16, 21.7 s and 12.8 s | Confirmed | -6.9086e-14 +- 7.407e-16; 21.6 s and 12.7 s |
| 2009 BD: A1 5.275e-11 +- 9.66e-12, A2 -1.119e-12 +- 1.53e-13 | Confirmed | identical |
| Gravity-only fit of 2001 YE4 rejects 72 of 450; 2003 RM 148 of 409 | Confirmed | 72 of 457 (optical plus radar); 148 of 409 |
| Reduced chi-square 0.15 to 0.5 | Confirmed, range wider | 0.07 to 0.5 for adequate models |
| GRSS hits its iteration cap on arcs of 24 days or less (23% of pilot fits) | Confirmed, and fixable | 8 of 40 (20%), all at 12 days or less; 0 of 40 with a Cartesian state |
| GRSS fails on 2020 CD3 even from JPL's solution; initial RMS 11,558 arcsec | Confirmed, partly fixable | 11,544 arcsec; post-escape 95-day arc converges; captured phase does not |
| 74 NHATS objects with H >= 27 and arc >= 60 d, 63 without a JPL A1 | Confirmed | 74 and 63 from the local snapshots |
| 618 near-Earth asteroids with a JPL A2, 21 with A1 | Confirmed | 618 and 21 from the local snapshot |
| "The informative NHATS set is ... 74 objects with H >= 27 and an arc of 60 days or more (radiation pressure)" | Refuted as stated | 5 of 16 sampled are informative; 11 of 16 have sigma(A1) above 9e-11 |
| Injection-recovery cost about 2 s per fit | Confirmed for multi-year arcs; 0.4 to 1.5 s for sub-2-year arcs | section 2 |
| 2011 MD published area-to-mass (3.2 +- 0.6)e-4 m2/kg (Micheli et al. 2014) | Confirmed as published; not reproducible at that precision from public data | arXiv 1403.6033; this work (3.4 to 3.6) +- 1.1 e-4 |

## Not done

- Nyx and Aten with Gaia astrometry; layup; find_orb; any cold start without JPL elements.
- Radar-bearing objects in injection (the script simulates optical only).
- A null sample of slow close approachers (the real analogue of NHATS targets).
- 2021 ER injection skipped because its gravity-only fit does not converge. Injection on the two JPL-A2 objects in the sample (2011 CL50, 2007 XB23) used an A1-only model and is shown only as a mis-specification example.

## Sources

- JPL SBDB API (per-object records fetched today): https://ssd-api.jpl.nasa.gov/sbdb.api
- JPL radar astrometry API: https://ssd-api.jpl.nasa.gov/sb_radar.api
- MPC observations API: https://data.minorplanetcenter.net/api/get-obs
- GRSS 4.6.0 source as installed (`grss/fit/fit_simulation.py`, `fit_utils.py`, `fit_optical.py`, `utils.py`): https://github.com/rahil-makadia/grss
- Micheli, Tholen, Elliott 2014, 2011 MD: https://arxiv.org/abs/1403.6033
- Local snapshots: `data/research/dl/catalogs/nhats.json`, `data/research/dl/catalogs/sbdb_neo.json`
