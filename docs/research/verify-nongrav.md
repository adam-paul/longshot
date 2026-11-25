# Verification: non-gravitational numbers, density bound, anomalies

Independent check of `nongrav.md` and `orbit-tooling.md` (round 1, 2026-11-20). Checked 2026-11-21. Status: complete.

Inputs: today's snapshots `data/research/dl/catalogs/sbdb_neo.json` (43,367 NEOs) and `data/research/dl/catalogs/nhats.json` (7,229 objects); 11 JPL SBDB object records, 23 ESA NEOCC orbit files, 12 SsODNet ssoCards and 17 arXiv PDFs fetched today (one request at a time) into `data/research/dl/nongrav-check/`. Scripts are `nc_*.py` in `data/research/scripts/`. Every number needed is repeated here.

## Verdicts at a glance

| # | Claim | Verdict | Correction |
|---|---|---|---|
| 1 | 174 NHATS objects with a fitted parameter (A1 18, A2 169, A3 7); 16 of 286 under 5 km/s; 154 A2 at 3 sigma | Confirmed | none |
| 2a | rho_max = 3.128e-8 (1-A)/(D \|A2\|), maximum 0.2071 at Theta = sqrt(2) | Confirmed | none |
| 2b | Finite-size maximum 0.2455 | Confirmed | It is a peak at R/l = 4.0, not a general allowance: see table in section 2.2 |
| 2c | Roughness allowance 1.3; "conservative bound = 1.5 x nominal" | Partly | 1.3 matches Rozitis & Green's own peak-to-peak figure only for Bond albedo up to about 0.2; shape adds 10 to 25% that the first round left out |
| 2d | 118 of 154 nominal; 11 of 154 conservative | 118 confirmed; 11 partly | With the factor 1.5 as stated the count is 15. 11 needs the factor 1.541 the first-round script used |
| 3 | Measured densities sit below the bound; 2000 WO107 violates it | Confirmed for 11 objects; WO107 partly | WO107 is 1.29 times the nominal bound but only 0.9 sigma, and inside the conservative bound |
| 4a | 2022 OB5: A2 = -1.66e-12 at 26 sigma; NEOCC negative area-to-mass; 1.542 min, X-complex | Confirmed | none |
| 4b | 1998 KY26: A3 2.70e-11 +/- 0.65e-11 published versus 1.69e-12 +/- 1.12e-12 at JPL | Numbers confirmed; reading refuted | Source is Seligman 2024 (PNAS), not 2023. "No paper says so" is wrong: Farnocchia et al. 2025 (ApJL 993, L9). The out-of-plane term has not been shown to vanish |
| 4c | 2020 GE: A1 implies density under 0.55 g/cm3; artificial candidate? | Arithmetic confirmed; not a known artificial candidate | It was the NEA Scout mission target and a 2024 Goldstone radar target |
| 4d | Screen flags 2016 TA56, 2006 VC, 2011 CL50, 2003 LN6; in the literature? | Screen reproduced; literature status mixed | 2011 CL50 is in Fenucci 2024 as a rejected detection; 2003 LN6 is an accepted NEOCC detection; the other two are in no paper I could find |
| 5 | Pools 814 / 651, 74 / 63, 38 of 286 | Confirmed | none |
| 6 | A1 = 2.266e-7 C_R (A/m); rho = 1.5/((A/m) D) | Confirmed | none |

## 1. Counts: confirmed

`nc_counts2.py` on today's snapshots. NHATS has grown by three objects since yesterday (7,229); nothing else moved.

| Quantity | Claimed | Recount |
|---|---|---|
| NHATS with any of A1/A2/A3 in SBDB | 174 | 174 (78 numbered, 96 unnumbered) |
| A1 / A2 / A3 | 18 / 169 / 7 | 18 / 169 / 7 |
| With delta-v under 4 / 5 / 6 / 8 km/s | 8 of 40 / 16 of 286 / 28 of 726 / 65 of 2,196 | 8 of 40 / 16 of 286 / 28 of 726 / 65 of 2,197 |
| NHATS A2 at 3 sigma or better | 154 | 154 (106 at 5 sigma) |
| NHATS A1 at 3 sigma or better | 11 (nongrav), 10 (orbit-tooling) | 10; 2011 MD sits at 2.96 from the rounded catalogue values |
| NEO asteroids with A2; at 3 / 5 / 10 sigma | 618; 573 / 351 / 146 | 618; 573 / 351 / 146 |
| NEO asteroids with any parameter; sign of A2 | 623; 445 negative, 173 positive | 623; 445, 173 |

The 16 under 5 km/s: 2026 QQ8, 2021 GM1, 2022 OB5, 2020 CD3, 2020 GE, 2021 VH2, 2023 YO1, 2006 RH120, 2025 PN7, 2020 WY, 2012 LA, 2015 TC25, (478784), 2009 BD, 2007 XB23, 2020 PP1.

Caveat: the bulk query returns two significant figures (A2 of 2020 GE is "-1.9e-12"; the object record gives -1.9398e-12). Counts near a threshold can move by one when full precision is used.

## 2. The density bound

### 2.1 Formula: confirmed

Re-derived from the heat equation in `nc_thermal.py`, without using the first round's formula:

- Linearised surface condition on a homogeneous sphere, dipole term only. The temperature dipole is (alpha F/2)/(4 eps sigma T_av^3) / (1 + lambda psi(z)), with z = sqrt(-i) R/l, psi(z) = z j1'(z)/j1(z), lambda = Theta/(sqrt2 R/l).
- Lambertian recoil gives a transverse acceleration a_t = (4/9)(1-A) Phi |W| cos(gamma), W = Im[1/(1 + lambda psi)], Phi = 3F/(2 D rho c).
- For R much larger than l this reduces to |W| = 0.5 Theta/(1 + Theta + 0.5 Theta^2), with maximum (sqrt2 - 1)/2 = 0.20711 at Theta = sqrt2.
- With L_sun = 3.828e26 W: |A2|max = 3.1282e-8 (1-A)/(D[m] rho[kg/m3]) au/d2, so rho_max = 3.128e-8 (1-A)/(D |A2|). A is the Bond albedo.

This matches equations 1 to 3 of Vokrouhlicky et al. 2015 (arXiv:1502.01249, text read today): da/dt_diurnal = -(8/9)(alpha Phi/n) W cos(gamma), da/dt_seasonal = (4/9)(alpha Phi/n) W sin^2(gamma), W = -kappa1 Theta/(1 + 2 kappa2 Theta + kappa3 Theta^2), all kappa = 1/2 for large bodies. The review's sentences "often allows strict upper bounds on rho (e.g., Chesley et al., 2003)" and "surface roughness can increase the Yarkovsky force by tens of percent, owing mainly to the beaming" are both there.

### 2.2 Finite size: 0.2455 confirmed, and it is a narrow peak

My Bessel-function solution and the closed form the first round "recalled" agree to 1e-12 over R/l from 0.05 to 30, so the recalled formula is the exact linear solution. Maximum of |W| over Theta at fixed R/l:

| R/l | 0.4 | 1.0 | 1.6 | 2.5 | 4.0 | 6.3 | 10 | 16 | 25 | 40 | 100 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| max \|W\| | 0.008 | 0.049 | 0.114 | 0.206 | **0.2455** | 0.236 | 0.226 | 0.220 | 0.215 | 0.212 | 0.209 |
| relative to 0.2071 | 0.04 | 0.24 | 0.55 | 1.00 | 1.185 | 1.14 | 1.09 | 1.06 | 1.04 | 1.02 | 1.01 |

Global maximum 0.24549 at R/l = 4.01, Theta = 1.76. So:

- A body not much larger than the skin depth has a maximum efficiency between 0 and 1.185 times the large-body value, depending on R/l. It exceeds the large-body value by more than 5% only for D between about 5 and 40 skin depths, and it falls below it for D under 5 skin depths (steeply: one quarter at D = 2 l).
- Diurnal skin depths are 0.4 mm to 6 cm (1.5-minute to 5-hour rotation, regolith to solid rock) and 0.18 m for iron at 5 hours. For NHATS-size bodies (D of 2 m or more) the diurnal enhancement therefore applies only to slow rotators of bare rock or metal (tens of hours or longer). For everything else the diurnal factor is 1.00 to 1.04.
- The seasonal skin depth is 0.2 m (regolith), 2.4 m (solid rock), 7.7 m (iron). The peak sits at D of about 19 m for rock and 62 m for iron.

### 2.3 Can the seasonal term, roughness or shape exceed the bound?

- **Seasonal term: no.** Its coefficient is half the diurnal one. With both terms, |da/dt| is proportional to 2 W_d |cos gamma| + W_s sin^2(gamma). If W_s is at most W_d the maximum is at |cos gamma| = 1 and equals the diurnal bound. If the seasonal wave sits at its finite-size peak (0.2455) while the diurnal one is at 0.2071, the maximum is 1.4% higher, at |cos gamma| = 0.84. The seasonal term alone reaches at most 0.59 of the bound.
- **Non-linearity: lowers it.** A non-linear solution for a smooth large sphere (each latitude as its own conduction problem with the T^4 boundary condition; `nc_nonlinear.py`, harmonic balance) gives a maximum equivalent W of 0.1925 at Theta = 1.60, which is 0.93 of the linear value. A separate time-stepping solver (`nc_nonlinear_fd.py`) reproduces the facet integrals to 0.05%.
- **Roughness: yes, by about 25 to 55% at the peak.** Rozitis & Green 2012 (arXiv:1203.1464): beaming "enhances the Yarkovsky orbital drift by typically tens of percent but it can be as much as a factor of two". The factor of two is at low thermal inertia and high Bond albedo, where the smooth-surface drift is small. What matters for a bound is the maximum over thermal inertia. Reading their Fig. 8b (1 km, 2,500 kg/m3, 6 h, 1 au, zero obliquity; reading error about 3%): smooth peaks 54.5, 42.5, 30 m/yr and fully rough peaks 68, 58, 46.5 m/yr for Bond albedo 0.1, 0.3, 0.5. Peak-to-peak enhancement: **1.25, 1.36, 1.55**. Real asteroids have Bond albedo below about 0.2 (geometric albedo 0.5), so 1.3 is a fair figure for 100% crater coverage.
- **Unresolved discrepancy.** The linear bound for that test body is 79.5 (1-A) m/yr, i.e. 71.5, 55.6, 39.7. Their smooth peaks are 0.76 of it at all three albedos, where my non-linear sphere gives 0.93. Their rough peaks are 0.95, 1.04, 1.17 of the linear bound. I could not find the cause of the 18% gap between the two smooth-surface numbers (their value is an average over 11 irregular shapes). So the ceiling carries a model uncertainty of about 20% that the first round did not state.
- **Shape: yes, by 10 to 25% when the diameter comes from brightness.** Rozitis & Green found irregular shapes of equal volume differ from a sphere by about 10%. But a diameter from H measures cross-section, and a non-spherical body has less volume than the sphere with the same mean cross-section: 0.90 for axes 2:1:1, 0.78 for 3:1:1, 0.87 for 1:1:0.5, 0.85 for Itokawa's axes (my computation). The true density can exceed the spherical rho_max by the inverse of that. The first round's allowance does not include this.
- **Hard ceiling.** If all absorbed power left as one Lambertian lobe along the track the efficiency would be 2/3, which is 7.2 times the nominal bound. Nothing physical gets near it, but it is the only strict limit.

**What the measured bodies show.** Predicted efficiency from each body's measured thermal inertia, spin and obliquity (linear theory), against the measured rho/rho_max: Bennu 0.95 predicted, 0.87 measured; Ryugu 0.99 and 0.86; Itokawa 0.73 and 0.64. Measured over predicted is 0.91, 0.87, 0.87. The linear bound was not exceeded by any of the three, two of which sit at nearly ideal thermal parameter and obliquity.

**Recommended wording for pre-registration.** Efficiency ceiling = 0.092 (1-A) times f, with f treated as uncertain: 1.0 (linear), 0.76 to 0.93 (smooth non-linear), up to about 1.2 to 1.3 (rough, Bond albedo up to 0.3), times up to 1.185 for small slow rotators of bare rock, times 1.1 to 1.25 when D is from H. A ceiling of 1.5 for measured sizes and about 1.8 for H-based sizes covers these. The first round's 1.5 is defensible for measured sizes, by a different mix of reasons than it gave.

### 2.4 The counts: 118 confirmed, 11 depends on an unstated factor

`nc_screen.py`, `nc_extra.py`. D from H, Bond albedo = 0.39 times geometric albedo, 154 NHATS objects with A2 at 3 sigma.

- Nominal, geometric albedo 0.15, rho_max under 4,000: **118** (confirmed). 90 at albedo 0.30, 139 at 0.05.
- Conservative as described in the brief (bound times 1.5, |A2| minus 2 sigma, albedo 0.30): **15**, not 11.
- Conservative with the factor the first-round script actually used, (0.2455/0.2071) times 1.3 = 1.541: **11** (reproduced). Four objects sit between the two factors: 2020 GE, Apophis, 2012 EY11, 1994 CJ1.

Sensitivity of the conservative count (|A2| minus 2 sigma, albedo 0.30) to the factor: 1.3 gives 27; 1.5 gives 15; 1.541 and 1.6 give 11; 2.0 gives 7; 2.37 gives 3. At albedo 0.50 the factor 1.5 gives 8. An H error of +0.4 mag takes 15 to 8. Raising the density threshold to 5,000 gives 34. Only 20 of the 154 have a diameter in SBDB. The honest statement is "between 3 and about 30, most likely 10 to 15".

**The 11 are mostly the anomalies.** The 11 are 2006 RH120, 2011 CL50, 2004 JN1, 2003 LN6, 2001 BB16, 2008 DB, 2008 NP3, 2018 KC2, 2002 BF25, 2000 EE104, 1993 BX3. ESA NEOCC publishes no non-gravitational model today for six of them (2006 RH120, 2011 CL50, 2004 JN1, 2008 NP3, 2008 DB, 2018 KC2; orbit files read today), and Fenucci et al. 2024 Table B.3 lists those six plus 2001 BB16 as JPL detections that exceed the modelled maximum Yarkovsky drift. The same statistic drives "metal excluded" and "too fast to be Yarkovsky". The window in which the bound is informative and the detection is still credibly thermal is narrow, a factor of about 2 to 3 in |A2| times D.

## 3. Validation on objects with independent densities

`nc_validate.py`. A2 from SBDB today (Bennu from NEOCC, since JPL's Bennu solution carries AMRAT and RHO = 1,191.5 kg/m3, confirmed), D and density from SsODNet ssoCards and SBDB, read today.

| Object | D (m) | \|A2\| (au/d2), S/N | rho_max | Density, source | Ratio | First round |
|---|---|---|---|---|---|---|
| Bennu | 484 | 4.605e-14, 191 | 1,378 | 1,194, spacecraft | 0.87 +/- 0.01 | 0.87 |
| Ryugu | 896 | 2.487e-14, 5.0 | 1,379 | 1,190, spacecraft | 0.86 +/- 0.17 | 0.87 |
| Itokawa | 330 | 2.855e-14, 4.0 | 2,971 | 1,900, spacecraft | 0.64 +/- 0.17 | 0.65 |
| 1996 FG3 | 1,670 | 1.2e-14, 8.0 | 1,543 | 1,364, binary | 0.88 +/- 0.29 | 0.88 |
| Hermes | 800 | 1.2e-14, 7.1 | 2,961 | 1,810, binary | 0.61 | 0.61 |
| 1994 AW1 | 861 | 1.4e-14, 7.4 | 2,384 | 1,400, binary radar | 0.59 +/- 0.23 | 0.59 |
| Sekhmet | 1,221 | 5.4e-15, 4.9 | 4,295 | 1,980, binary radar | 0.46 +/- 0.18 | 0.46 |
| 2003 YT1 | 1,143 | 6.4e-15, 64 | 3,494 | 1,624, binary radar | 0.46 +/- 0.30 | 0.46 |
| Moshup | 1,335 | 6.1e-15, 56 | 3,513 | 1,268 (ssoCard) to 1,970 (Ostro 2006) | 0.36 to 0.56 | 0.36 to 0.56 |
| Apollo | 1,200 | 3.7e-15, 19 | 5,809 | 2,050, binary radar | 0.35 +/- 0.06 | 0.35 |
| 2000 DP107 | 960 | 9.6e-15, 16 | 3,274 | 998 (ssoCard) | 0.30 +/- 0.08 | 0.30 to 0.42 |
| 2000 WO107 | 510 +/- 83 | 1.564e-14, 4.8 | 3,724 | 4,800 (+340/-630) | 1.29 +/- 0.36 | 1.32 |

**Confirmed: the eleven objects with spacecraft or binary densities sit below the nominal bound**, the best-measured ones at 0.64 to 0.87. Sizes differ between SBDB and SsODNet for several binaries (1996 FG3: 1.196 against 1.67 km; 2003 YT1: 1.717 against 1.143 km); no choice turns any of them into a violation.

**2000 WO107: not established as a violation.**

- The density exceeds the nominal bound by 29% (I get 3,724 kg/m3 where the first round got 3,640).
- The bound itself is 3,724 +/- 980 (A2 is a 4.8 sigma detection, the diameter is +/- 16%). The excess is 0.9 sigma.
- The conservative bound is 5,590 at nominal A2 and above 8,600 at |A2| minus 2 sigma. The density is inside it. Roughness at the Rozitis & Green level (1.25 to 1.36) alone covers it.
- The density is not a mass measurement. Krugly et al. 2025 (A&A 702, A170, read today) set gravitational attraction between two ellipsoidal lobes, treated as point masses, equal to the centrifugal force. They state that two spheres instead of flattened lobes would give a density about 3 times lower.
- NEOCC does reject the detection: -23.52 +/- 4.22 against a modelled maximum of 15.80 (1e-4 au/Myr; Table B.3, confirmed), and its orbit file is gravity-only today.

So the metal known-answer test is uninformative, which is how the first round's own text reads; the word "violation" in the summary overstates it.

**Two more tensions the first round did not list** (neither has an independent density, so they are not validation cases):

- **Toutatis.** SBDB's "diameter" is 5.4 km, the long axis. With that the nominal bound is 706 kg/m3; with the Chang'e-2 equivalent diameter of 2.725 km it is 1,400. JPL's fit also carries a negative A1 at 3.3 sigma. SsODNet lists a "Yarkovsky" density of 727 for it.
- **Phaethon.** Nominal bound 761 (SBDB 6.25 km) or 917 (5.165 km) from JPL's current A2 of -6.3e-15 at 52 sigma, against the published 1,670 +/- 470, which was itself derived from an older, 40% smaller drift. Phaethon is active at perihelion.

Both show that SBDB diameters are heterogeneous and that the screen flags well-known objects.

## 4. The four anomalies

### 4a. 2022 OB5: confirmed, and the density statement is weaker than it looks

Primary values read today:

- JPL solution 16 (2026-01-17, 49 observations, 2022-07-28 to 2026-01-16, no radar): A2 = -1.6572e-12 +/- 6.49e-14 au/d2 (25.5 sigma). H = 28.99 +/- 0.42. No A1.
- NEOCC orbit file: area-to-mass ratio -0.2373 +/- 0.0549 m2/t (negative, 4.3 sigma), A2 = -1.871e-12 (S/N 24.95), da/dt = -786.6 +/- 31.5 (1e-4 au/Myr), correlation between the two parameters +0.80. The sign convention is the usual one (2020 GE's is +0.823 and JPL's A1 is positive).
- Alarcon et al. 2026 (Icarus 117153, arXiv:2605.04784, text read): P = 1.542 +/- 0.001 min, "moderately red, consistent with the X-complex", density "poorly constrained", 1,800 to 4,900 kg/m3. No mention of any non-gravitational term.

Density implied if the drift is thermal (albedo set by H = 28.99 at each size):

| D (m) | albedo | rho_max nominal | times 1.5, \|A2\| - 2 sigma |
|---|---|---|---|
| 3 | 0.50 | 5,070 | 8,260 |
| 4 | 0.28 | 4,210 | 6,840 |
| 5 | 0.18 | 3,510 | 5,720 |
| 6 | 0.12 | 2,990 | 4,870 |
| 8 | 0.070 | 2,300 | 3,740 |
| 10 | 0.045 | 1,860 | 3,020 |
| 12 | 0.031 | 1,550 | 2,530 |

Equivalently rho times D is at most about 1.5e4 to 1.9e4 kg/m2. Iron (7,500) is excluded at every size from 3 m up on the nominal bound and from 4 m up on the conservative one.

Is it plausible for radiation forces?

- In magnitude, yes. A 5 m body of 2,500 kg/m3 needs 71% of the maximum efficiency; 3 m and 1,200 kg/m3 needs 24%.
- Given the 92.5 s rotation, only with a very insulating surface. The thermal parameter is 0.084 times the thermal inertia, so the efficiency is 0.99 of maximum at 15 SI, 0.72 at 50, 0.45 at 100, 0.25 at 200, 0.06 at 1,000. Needing 25 to 90% of maximum means thermal inertia under about 200 to 30 SI.
- For bare rock the diurnal term is dead and the seasonal one, with finite size, takes over. Maximum total efficiency: 0.04 to 0.22 for solid rock (D 3 to 12 m), 0.14 for porous rock, 0.005 to 0.07 for iron. That would mean a density under about 700 kg/m3 at 3 m and under about 340 at 12 m, which is not credible. Centrifugal acceleration at the equator is about 6,600 times self-gravity, so loose regolith cannot be assumed.
- The alternative is that the transverse term is absorbing something else. NEOCC's negative area-to-mass ratio is 5 to 9 sigma away from any physical value for a 5 m body (+0.9e-11 to +5.7e-11 au/d2 in A1, against -5.4e-11 +/- 1.2e-11). JPL and NEOCC differ in A2 by 2.2 sigma purely because one includes a radial term.

Reading: the 26 sigma is a formal number on 49 observations. The object is the same puzzle as 2016 GE1 and 2011 PT (fast rotators needing dust-like thermal inertia), with a fit-degeneracy warning on top. It cannot carry a "metal excluded" statement until a constrained joint fit is done.

### 4b. 1998 KY26: numbers confirmed, the reading is wrong

- **Published values.** Seligman et al. **2024** (PNAS, arXiv:2412.07603, table read): A1 = 1.60e-10 +/- 8.77e-11, A2 = -1.38e-13 +/- 5.67e-14, A3 = 2.70e-11 +/- 6.45e-12 (4.19 sigma). The brief attributes this to Seligman et al. 2023; that paper (PSJ, arXiv:2212.08115, Table 1) gives A3 = 3.20e-11 +/- 1.15e-11 (2.8 sigma, printed as 3).
- **Current JPL.** Solution 36, computed 2024-05-07 by D. Farnocchia, 85 optical plus 2 delay and 2 Doppler, 1998-05-31 to 2024-05-06: A1 = 3.66e-11 +/- 3.87e-11 (0.95 sigma), A2 = -2.196e-13 +/- 4.87e-14 (4.5 sigma), A3 = 1.686e-12 +/- 1.121e-12 (1.5 sigma). NEOCC fits A2 only: -2.731e-13, S/N 7.4.
- **Size and albedo.** D = 11 +/- 2 m, albedo 0.52 +/- 0.08, P = 0.089193 h (SBDB, citing Santana-Ros et al. 2025, Nat. Commun. 16, 8275).
- **Hansen & Hirabayashi 2026** (arXiv:2611.10275, Icarus 463, 117361, text read): orbit-averaged temperatures of about 212 K or more against a 145 K threshold; 1% ice by mass lost in 2,065 years, or 62 years at the rate the acceleration would need.
- **What the first round missed.** Hansen & Hirabayashi cite **Farnocchia, Vokrouhlicky, Santana-Ros, Bartczak, Micheli & Chesley 2025, "Radiation forces and trajectory of Hayabusa2# target 1998 KY26", ApJL 993, L9** (doi 10.3847/2041-8213/ae10b8): solar radiation pressure on an oblate spheroid plus thermal emission, with a pole of (37.7, -56.4) degrees inside the photometric pole region, fits the astrometry including the out-of-plane part, and no outgassing is needed. I could not open the paper (HTTP 403); this is from two papers that cite it. The first round's statement "I found no paper stating that the out-of-plane term has collapsed" is therefore wrong in substance: the JPL group published the reinterpretation a year ago.
- **The term has not been shown to vanish.** A preprint (Hibberd, Crowl & Loeb, arXiv:2609.24283, not peer reviewed, find_orb, default weights) fits all 260 measurements and gets A1 = 4.81e-11 +/- 5.35e-11, A2 = -2.07e-13 +/- 0.45e-13, A3 = **1.18e-11 +/- 0.13e-11 (9 sigma)**. A1 and A2 agree with JPL; A3 is seven times JPL's and 5.9 combined sigma away. The public JPL solution uses 85 optical observations and stops on 2024-05-06, so it is probably stale for this object (my inference).

So this is not a clean "4.2 sigma fell to 1.5 sigma" case. It is a case where the dark-comet reading was replaced by a radiation-force model by the same group, and where the public catalogue value disagrees with a fit to the full data. With D = 11 m the A2 needs 27% of maximum efficiency at 2,800 kg/m3 (confirmed).

### 4c. 2020 GE: arithmetic confirmed; no sign it is a known artificial candidate

- JPL solution 24 (2024-11-26; 58 optical, 3 delay, 4 Doppler; 2020-03-29 to 2024-11-22): A1 = 1.7638e-10 +/- 1.26e-11 (14.0 sigma), A2 = -1.9398e-12 +/- 2.18e-14 (88.8 sigma). H = 28.17 +/- 0.45. NEOCC: area-to-mass 0.823 +/- 0.038 m2/t, A2 = -1.936e-12 (S/N 154). The two centres agree.
- Area-to-mass ratio 6.5e-4 m2/kg (C_R = 1.2) to 7.8e-4 (C_R = 1.0). Density for a sphere at C_R = 1.2: 167, 290, 410, 530 kg/m3 at albedo 0.05, 0.15, 0.30, 0.50. "Under 0.55 g/cm3 for albedo up to 0.5" holds at nominal H. It is not robust to H: with H + 0.45 and A1 - 2 sigma at albedo 0.5 it is 760.
- The size-free statement is rho times D = 2,300 kg/m2 (1,900 to 2,800 over the C_R range). |A2|/A1 = 0.011, and the A1-based rho times D needs only 15% of the Yarkovsky maximum to produce the A2. The two terms are mutually consistent as radiation forces.
- Literature and context: the JPL radar team's planning page says 2020 GE "was the previous target for NASA's Near-Earth Asteroid Scout mission", H 28.2, "roughly 10 meters", and that the September 2024 echoes had "a very narrow bandwidth suggesting slow rotation". Radar astrometry is from Goldstone (20 and 21 September 2024) and Canberra (23 September). I found no paper or page proposing an artificial origin.
- My own checks against an artificial origin: its area-to-mass ratio is more than ten times below that of spent upper stages (order 1e-2 m2/kg for 2020 SO; recalled, not re-verified). JPL's close-approach table has it passing Earth at 0.0028 au on 1962-10-03 and at about 0.010 au in 1932, with none of the approaches ending at Earth. The backward propagation assumes constant A1 and A2 for 90 years, so this is suggestive only.

2020 GE is the lowest-density member of the radiation-pressure set, by a factor of about 2 below 2011 MD, 2012 LA and 2015 TC25 on the same arithmetic.

### 4d. The crude dark-comet screen: reproduced; literature status differs by object

Rerun on today's 573 detections (bound times 1.541, |A2| minus 2 sigma, albedo 0.6 or the SBDB diameter): the same nine objects need under 1,000 kg/m3: 2012 UR158, 2016 TA56, 2005 UY6, 2003 RM, 1998 SH2, 2001 ME1, 1998 FR11, 2006 RH120, 2006 VC. Under 2,000 adds eight: 2008 NP3, Phaethon, Toutatis, 2000 AA6, 2011 CL50, 2009 FD, 2007 YJ, 2002 BF25. 2003 LN6 and 2004 JN1 do **not** pass that criterion (2003 LN6 is at 2,700); the first round reached them with the nominal bound instead, without saying so.

| Object | JPL today | NEOCC today | In the literature? |
|---|---|---|---|
| (883607) 2016 TA56 | A2 = -3.186e-12 +/- 3.58e-13 (8.9 sigma), 94 obs, solution 23 made by hand by D. Farnocchia on 2026-06-17. a 2.69, e 0.78, i 32 deg, q 0.59, T_J 2.69. Bound 7 to 36 kg/m3 | gravity only | Not in any paper I could search (Seligman 2023, 2024; Taylor 2023, 2024 a, b; Farnocchia 2023; Fenucci 2024; Greenberg 2020; Del Vigna 2018; arXiv "dark comet" listing; web). The hand-made JPL solution three weeks before the 1998 SH2 paper shows the JPL group knows it. Whether the Nature Astronomy paper names it: unverifiable (paywalled) |
| (428209) 2006 VC | A2 = +6.45e-13 +/- 1.75e-13 (3.7 sigma), automatic solution | gravity only | Not found. A 3.7 sigma outlier among 618 fitted values is weak |
| 2011 CL50 | A2 = +4.38e-12 +/- 2.93e-13 (14.9 sigma), solution of 2022 | gravity only | Yes: Fenucci et al. 2024 Table B.3, 1,950 +/- 139 against a maximum of 341 (1e-4 au/Myr), rejected. Not called a dark comet anywhere I found |
| 2003 LN6 | A2 = +7.44e-13 +/- 1.55e-14 (48 sigma) | **accepted**: A2 = +7.02e-13, S/N 41 | Passes NEOCC's physical test. Nominal bound 1,030 kg/m3 at albedo 0.15. It is a strong ordinary detection of a light or small body, not an anomaly |

2016 TA56 is the only one of the four that is both strong and unpublished, and it is on a comet-like orbit, the same kind of object as 1998 SH2.

## 5. Pools: confirmed

| Quantity | Claimed | Recount |
|---|---|---|
| NHATS, arc over 1,000 d | 814 | 814 |
| of those, no JPL A2 | 651 | 651 |
| NHATS, arc over 2,900 d; no A2 | 549; 399 | 550; 400 |
| NHATS, H at least 27 and arc at least 60 d | 74 | 74 |
| of those, no JPL A1 | 63 | 63 |
| of the 286 under 5 km/s: H at least 27 and arc at least 60 d | 38 | 38 (29 without A1) |
| of the 286 under 5 km/s: arc over 1,000 d | 19 | 19 (13 without A2) |
| H at least 26 / 27 / 28 with arc at least 100 d | 149 / 59 / 19 | 149 / 59 / 19 |
| H at least 27 with arc under 60 d | 97% | 96.9% (2,297 of 2,371) |
| Median arc; median H | 12 d; 26.2 | 12 d; 26.2 |

93 NHATS objects have no arc value in SBDB (arcs under a day). Counting them as short gives 72.6% with arcs of 30 days or less; orbit-tooling's 71.2% left them out.

## 6. Radiation pressure: constants confirmed

A1 = L_sun/(4 pi c) times C_R (A/m) = **2.2656e-7** C_R (A/m)[m2/kg] au/d2; the same number follows from the solar constant (1361.2 W/m2 gives 4.54e-6 N/m2 at 1 au). For a sphere A/m = 3/(2 rho D), so rho = 1.5/((A/m) D).

A1 in au/d2 (C_R = 1.0; multiply by 1.2 for C_R = 1.2):

| D | iron 7,500 | stone 3,300 | stone 2,500 | rubble 2,000 | rubble 1,200 |
|---|---|---|---|---|---|
| 5 m | 9.1e-12 | 2.06e-11 | 2.72e-11 | 3.40e-11 | 5.66e-11 |
| 10 m | 4.5e-12 | 1.03e-11 | 1.36e-11 | 1.70e-11 | 2.83e-11 |

- Ratios at fixed size: rubble to stone 1.25 to 2.75; stone to iron 2.27 to 3.0; rubble to iron 3.75 to 6.25.
- With a measured size (10%): a 3 sigma split needs A1 to about 17% for rubble against stone (class centres), 25 to 30% for stone against iron, 50% for rubble against iron. Rubble at 2,000 against stone at 2,500 cannot be split at all.
- With size from H uncertain by a factor of about 2: if that factor is the full plus-or-minus 2 sigma range, only rubble against iron can reach 3 sigma, and it needs A1 to 38%; stone against iron tops out at 2.4 to 2.7 sigma with a perfect A1. If the factor is 1 sigma, nothing separates. A1 precision better than about 15% buys nothing until the size is measured.
- At fixed H, A1 scales as sqrt(albedo)/rho, so the order scrambles: bright stone 0.24, S-type monolith 0.16, dark rubble 0.14, metal 0.05 (relative units). Metal stays lowest by a factor of 2 to 5. Rubble against monolith is degenerate with albedo.
- Existing formal uncertainties on A1 are 0.8e-11 to 2.9e-11 (2020 CD3 alone reaches 2.5e-12). A 5 m iron body (0.9e-11) is below one sigma in a typical fit. Splitting stone from iron at 5 m needs about 6e-12, at 10 m about 3e-12.
- The first round's "iron body of 5 m has 6e-5 m2/kg" corresponds to 5,000 kg/m3; for 7,500 it is 4.0e-5.

## New findings

1. The published roughness figure supports the first round's 1.3 only at the peak and only for Bond albedo up to about 0.2; the abstract's "factor of two" is not the number to use. Two smooth-surface non-linear estimates of the ceiling (0.76 and 0.93 of linear) disagree by 18%.
2. A diameter from H biases the spherical bound low by 10 to 25% for ordinary elongations. This allowance was missing.
3. Six of the eleven "robust metal exclusions" are detections ESA NEOCC does not accept as Yarkovsky.
4. Bennu, Ryugu and Itokawa reach 0.87 to 0.91 of the efficiency linear theory predicts from their measured properties: a three-point calibration of the model against ground truth.
5. 1998 KY26: Farnocchia et al. 2025 (ApJL 993, L9) already explains the out-of-plane acceleration with radiation forces, and a full-data preprint fit still finds A3 at 9 sigma, seven times the SBDB value. The SBDB solution dates from May 2024.
6. 2020 GE was the NEA Scout target and was detected by radar in September 2024 (slow rotation). Its two fitted terms are mutually consistent as radiation forces with rho times D = 2,300 kg/m2.
7. 2016 TA56 has a hand-made JPL solution from June 2026 and a comet-like orbit (T_J 2.69). It is the strongest unpublished candidate, and the JPL group has it.
8. SBDB diameters mix definitions (Toutatis 5.4 km is the long axis). Toutatis and Phaethon fall under 1,500 kg/m3 nominal and will be flagged by any screen.
9. For bare iron (thermal inertia about 12,000 SI) the diurnal efficiency is under 10% of the ceiling for rotation periods up to about 5 hours (0.5% at 1.5 minutes), about 20% at 50 hours and 50% at 500 hours; the seasonal term adds at most 7% for bodies under 12 m (skin depth 7.7 m). A small, fast-rotating bare-metal body should show almost no drift.

## What could not be verified

- Farnocchia et al. 2025 (ApJL) and Farnocchia et al. 2026 (Nature Astronomy) full texts: both blocked. Their content here is second-hand.
- Whether the 1998 KY26 out-of-plane term is 1.7e-12 or 1.2e-11 with all data: needs a refit; the orbit-fitting environment was wiped.
- The cause of the 18% gap between Rozitis & Green's smooth-surface peak and mine.
- Independent densities for the binaries were taken as catalogued in SsODNet, not re-read in the original papers.
- The area-to-mass ratio of 2020 SO used for comparison is from memory.

## Sources

- JPL SBDB object API, `https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=<des>&phys-par=1&full-prec=1` (11 objects); close-approach API `cad.api` (2020 GE, 2022 OB5); radar API `sb_radar.api` (2020 GE).
- ESA NEOCC orbit files, `https://neo.ssa.esa.int/PSDB-portlet/download?file=<des>.ke1` (23 objects).
- SsODNet ssoCards, `https://ssp.imcce.fr/webservices/ssodnet/api/ssocard/<name>` (12 objects).
- Vokrouhlicky et al. 2015, https://arxiv.org/abs/1502.01249. Rozitis & Green 2012, https://arxiv.org/abs/1203.1464 (Fig. 8b).
- Fenucci et al. 2024, https://arxiv.org/abs/2311.10175 (Table B.3). Krugly et al. 2025, https://arxiv.org/abs/2508.04535.
- Seligman et al. 2023, https://arxiv.org/abs/2212.08115; Seligman et al. 2024, https://arxiv.org/abs/2412.07603.
- Alarcon et al. 2026, https://arxiv.org/abs/2605.04784. Hansen & Hirabayashi 2026, https://arxiv.org/abs/2611.10275. Hibberd, Crowl & Loeb 2026, https://arxiv.org/abs/2609.24283.
- Farnocchia et al. 2025, https://doi.org/10.3847/2041-8213/ae10b8 (not opened). Farnocchia et al. 2026, https://doi.org/10.1038/s41550-026-02913-7 (not opened).
- Goldstone planning page, https://echo.jpl.nasa.gov/asteroids/sep2024.goldstone.planning.html.
- Scripts: `nc_counts2.py` (claims 1, 5), `nc_thermal.py` (derivation, finite size, constants), `nc_nonlinear.py` and `nc_nonlinear_fd.py` (non-linear ceiling), `nc_screen.py` and `nc_extra.py` (claims 2, 4, 6), `nc_validate.py` (claim 3), `nc_sbdb_show.py`, `nc_ssocard_show.py`.
