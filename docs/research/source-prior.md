# Orbit -> source region -> family -> meteorite type as a compositional prior for NHATS objects

Research brief, 2026-11-20. Status tags: **[V]** = read in a primary source or computed from primary data in this session; **[R]** = recalled, not re-checked; **[U]** = uncertain.

## 0. Bottom line

1. **For the NHATS population the orbit-based source prior is, to a very good approximation, a constant.** I computed per-object source probabilities for all 7,220 NHATS objects with usable H from the two public model tables (NEOMOD and Granvik et al. 2018). In both, the nu6 resonance is the top source for more than 99.9% of NHATS objects, and the per-object probability vector barely moves: P(nu6) 10th-90th percentile is 0.72-0.88 (NEOMOD) or 0.61-0.76 (Granvik). The mutual information between orbit cell and albedo/taxonomy class inside NHATS is 0.003-0.005 bits, out of about 1.4 bits of class entropy (0.2-0.4%). [V, own computation]
2. **A direct recover-known-objects test gives no skill in the NHATS region.** Against 1,204 NEOs with an SBDB albedo, the best public orbit-only prior (Granvik 2018 + Morbidelli 2020 albedo categories) separates dark (pV < 0.1) from bright with AUC 0.63 over all NEOs, 0.50 for a < 2 au, and 0.47 for the 69 NHATS members with albedos. [V, own computation]
3. **The published models disagree with each other on the base rate far more than any one of them varies between NHATS objects.** P(dark or carbonaceous) for an NHATS-type object is about 5% (NEOMOD3 per-source dark fractions), 10% (Granvik/Morbidelli table), 25% (METEOMOD family model, hydrated-carbonaceous share), 39% (Marsset 2022 debiased taxonomy by escape route), and 67% (Lopez-Oquendo et al. 2026 debiased C/X for D < 150 m). Part of that spread is real disagreement and part is the difference between conditioning on H and conditioning on diameter (section 7.2).
4. **This has largely been done.** Published, downloadable machinery already maps (a, e, i, H) to escape-route probabilities (two models), to albedo-class probabilities (one table), and to asteroid-family and meteorite-class probabilities (METEOMOD web tool and tarball). MANOS has spent a decade measuring spectra and colours of exactly the NHATS-type population (about 400 objects) and its 2026 paper states that main-belt source region does not explain the taxonomy of small NEOs.
5. **Where the orbit does carry real information for low delta-v objects is the origin question, not the main-belt source question:** lunar ejecta, tidal-disruption fragments, and artificial objects all concentrate in the Earth-like corner. 87% of the NHATS objects with delta-v < 5 km/s sit inside the orbital box that Jedicke et al. use for lunar ejecta, and 46% of all NHATS objects sit in the region where NEOMOD2 under-predicts small NEOs by up to about 30%.
6. **Most defensible prior:** an H-binned empirical base rate with explicit (wide) uncertainty, taken from surveys of the same population, plus an origin mixture (main belt / lunar / artificial) that depends on Earth-likeness and size. Present it as a base rate, not as a per-object discriminator, and publish the null result.

## 1. What I actually ran (reproducible)

Data pulled today:

- JPL NHATS API, all objects (dv <= 12 km/s, dur <= 450 d): **7,226 objects**; 285 with min delta-v < 5 km/s among those with usable H. https://ssd-api.jpl.nasa.gov/nhats.api [V]
- JPL SBDB query API, all NEOs: 43,360 objects; taxonomy for 323 NEOs, albedo for 1,204. Among NHATS objects: 23 have any SBDB taxonomy, 69 have an albedo, and **0 of the 285 with delta-v < 5 km/s have a taxonomy**. https://ssd-api.jpl.nasa.gov/sbdb_query.api [V]
- NEOMOD binned model `input_model.dat` (Model136; 52 H bins 15-28, 42 a bins, 25 e bins, 22 i bins, 12 sources) and `give_me_prob.f`. https://www.boulder.swri.edu/~davidn/NEOMOD_Simulator/ [V]
- Granvik et al. 2018 low-resolution model file with albedo categories (773,280 cells, 7 escape routes, H 15-25). https://www.mv.helsinki.fi/home/mgranvik/data/Granvik+_2018_Icarus/ [V]
- METEOMOD tarball (55 family maps in a x i, 0.01 au x 1 deg bins, 1 m bodies). https://sirrah.troja.mff.cuni.cz/~mira/meteomod/ [V]

Scripts (not kept): `nhats_sources.py`, `nhats_granvik.py`, `info_gain.py`, `nhats_meteomod.py`, `nhats_meteomod_smooth.py`, `validate_known.py`. Per-object outputs (not kept): `nhats_neomod_sources.csv`, `nhats_granvik_sources.csv`, `nhats_meteomod.csv`.

Caveats on my own numbers: objects with H >= 28 (15% of NHATS) were clamped to the last NEOMOD H bin; objects with H > 25 (74% of NHATS) were clamped to the last Granvik H bin, which is an extrapolation outside that model's calibrated range. The Marsset-2022 mapping needs Hungaria and JFC rows that are not in their Table 4; I used placeholders (flagged in the script). SBDB taxonomy is a small subset of what exists (MITHNEOS, MANOS and others are not all in SBDB).

### 1.1 Source probabilities for NHATS objects [V]

| Sample | Model | nu6 | 3:1 | Hungaria | inner weak res. | all outer + JFC | top source = nu6 |
|---|---|---|---|---|---|---|---|
| NHATS all (7,220) | NEOMOD | 0.808 | 0.138 | 0.007 | 0.039 | < 0.01 | 7,218 of 7,220 |
| NHATS dv < 5 (285) | NEOMOD | 0.820 | 0.162 | 0.003 | 0.012 | < 0.005 | 285 of 285 |
| NHATS all (7,220) | Granvik 2018 | 0.696 | 0.086 | 0.215 | n/a | 0.003 | 7,216 of 7,220 |
| NHATS dv < 5 (285) | Granvik 2018 | 0.708 | 0.031 | 0.261 | n/a | 0.001 | 285 of 285 |
| All NEOs (43,070) | NEOMOD | 0.577 | 0.233 | 0.021 | 0.078 | 0.09 | 32,494 |
| All NEOs, H < 22 | NEOMOD | 0.318 | 0.274 | 0.047 | 0.141 | 0.22 | 5,818 of 11,630 |

Independent confirmation: Alessi & Jedicke (2026) ran NEOMOD3 on 97 known Earth co-orbitals and got 78% nu6, 16% 3:1, 5% inner weak resonances, with only 5 objects having more than 1.5% probability for any other source. https://arxiv.org/abs/2604.13296 [V]

Note the disagreement between the two models on **Hungaria: 21.5% (Granvik) versus 0.7% (NEOMOD)** for the same objects. NEOMOD2 quotes an upper limit of 0.029 for the Hungaria weight at H = 28; Granvik's Hungaria share grows to 17.9% of 17 < H < 25 NEOs. This matters for composition because Hungaria is the nominal source of high-albedo E-type (aubrite-like) material.

### 1.2 Information content [V]

Mutual information I(orbit cell; X), in bits. "Class" entropies are 1.36-1.47 bits for three classes.

| Sample | I(orbit; source), NEOMOD | I(orbit; ER), Granvik | I(orbit; albedo class), Granvik+Morbidelli | P(pV <= 0.1) 5th-95th pct | I(orbit; dark/bright), NEOMOD x NEOMOD3 f_d | P(dark) 5th-95th pct |
|---|---|---|---|---|---|---|
| NHATS all | 0.042 | 0.043 | 0.0052 | 0.090-0.115 | 0.0027 | 0.043-0.086 |
| NHATS dv < 6 | 0.027 | 0.023 | 0.0025 | 0.089-0.103 | 0.0008 | 0.042-0.065 |
| NHATS dv < 5 | 0.020 | 0.021 | 0.0024 | 0.084-0.102 | 0.0004 | 0.042-0.057 |
| All NEOs | 0.622 | 0.583 | 0.080 | 0.083-0.277 | 0.068 | 0.045-0.416 |
| All NEOs H < 22 | 0.898 | 0.808 | 0.078 | 0.098-0.374 | 0.092 | 0.093-0.596 |
| All NEOs H >= 25 | 0.245 | 0.279 | 0.061 | 0.087-0.197 | 0.010 | 0.043-0.089 |

Ceiling even with a perfectly known escape route: using Marsset et al. 2022 debiased fractions and Granvik's population weights, I(ER; S/Q vs carbonaceous vs other) is 0.04-0.13 bits (3-9% of class entropy). The orbit only gives a blurred view of the ER, so the achievable number is lower.

### 1.3 Family-level model (METEOMOD) on NHATS orbits [V]

Re-implemented `compute_p` from the tarball's `meteomod.py` on the text maps (the pickled `maps.npz` was not loaded). For NHATS (a, i):

- Mean class shares: ordinary chondrite 0.68 (Massalia2 L 0.40, Koronis2 H 0.15, Flora LL 0.05, Karin H 0.045), hydrated carbonaceous 0.245 (Polana, Hoffmeister, Misa, Konig), HED 0.03, enstatite 0.013, metal-rich 0.011.
- At native resolution I(orbit; class) = 0.109 bits (8.5% of 1.28 bits), and P(hydrated carbonaceous) spans 0.10-0.47 (5th-95th pct). **About half of this is sampling noise in sparse maps:** rebinning to 0.05 au x 3 deg gives 0.061 bits, 0.1 au x 5 deg gives 0.045 bits, and for dv < 5 the figure falls to 0.009-0.045 bits. Each family map rests on about 10^3 particles and the maps were built for 1 m bodies.
- Only 32% of NHATS objects get a top-family probability above 0.5. Lopez-Oquendo et al. (2026) report the same thing for their sample (about 20% above 0.5) and note that METEOMOD and NEOMOD-family maps give very different answers for the same objects (54% Massalia versus about 80% Flora). https://arxiv.org/abs/2608.28779 [V]

### 1.4 Recover-known-objects test [V]

Predicting "dark" from orbit and H only. AUC 0.5 = no skill. Log-loss skill is relative to the plain base rate after a one-parameter recalibration.

| Label set | n | positives | AUC Granvik+Morbidelli | AUC NEOMOD x f_d | log-loss skill (Granvik) |
|---|---|---|---|---|---|
| Albedo pV < 0.1, all NEOs | 1,204 | 40.9% | 0.634 | 0.559 | +5.0% |
| Albedo, a < 2 au | 704 | 32.2% | 0.503 | 0.399 | -0.6% |
| Albedo, NHATS-like box (a 0.8-1.5, e < 0.3, i < 15) | 74 | 32.4% | 0.463 | 0.415 | -0.5% |
| Albedo, NHATS members | 69 | 36.2% | 0.474 | 0.433 | -0.5% |
| Taxonomy C+D vs S+V+other, all NEOs | 275 | 13.1% | 0.600 | 0.517 | +3.9% |
| Taxonomy, a < 2 au | 163 | 11.7% | 0.537 | 0.350 | +0.5% |

Semimajor axis alone does as well as the model (AUC 0.631 on the full albedo set). All the skill comes from a > 2 au objects, which are almost absent from NHATS. The albedo test is partly circular (both models were tuned on NEOWISE), so these are upper bounds.

## 2. (a) NEO source-region models

| Model | Sources | Size range and size dependence | Composition/albedo | Per-object access |
|---|---|---|---|---|
| Bottke et al. 2002, Icarus 156, 399 | 5: nu6, intermediate Mars-crossers, 3:1, outer belt, JFC. Shares roughly 37/25/23/8/6% [R]; outer belt + JFC about 15% [V via Granvik 2018] | Valid for H < 22; single power-law H distribution, no size dependence [V via Granvik 2018] | None | Superseded; implemented in ESA NEOPOP |
| Greenstreet et al. 2012, Icarus 217, 355 | Same 5; re-integration with about 6x more particles and 4x shorter steps; first Vatira and retrograde-NEA predictions; not recalibrated [V via Granvik 2018] | None | None | NEOSSat-1.0 orbital model [R] |
| Granvik et al. 2016 (Nature 530, 303), 2018 (Icarus 312, 181) | 7 escape routes: Hungaria, nu6 complex (incl. 4:1, 7:2), Phocaea, 3:1J, 5:2J complex (incl. 7:3, 8:3), 2:1J complex (incl. 9:4, 11:5), JFC [V] | Calibrated 17 < H < 25 on CSS 2005-2012; ER-specific H distributions. Shares for H < 17.5 / 21 / 25: nu6 39/49/38, 3:1 19/31/36, 5:2 17/12/0.1, Hungaria 11/5/24, Phocaea 7/3/0.02, 2:1 5/2/0.1% (Devogele et al. 2019, Table 3) [V]. Uncertainties for minor ERs reach 1-2 orders of magnitude at H > 23 [V] | Morbidelli et al. 2020 (Icarus 340, 113631) adds albedo categories on top; "low and high albedo NEOs are well mixed in orbital space", no significant size dependence [V] | Helsinki files: 802,000 synthetic NEOs, and a cell table with 7 ER probabilities + sigmas, P(pV <= 0.1), P(0.1 < pV <= 0.3), collision probability, MOID. Readme asks only for citation; no formal licence [V]. Also ESA NEOPOP v2.1 (Windows/Linux binaries; licence not stated on page) [V], and Lowell astorb (used by Moskovitz et al. 2026 to get per-object source regions) [V via paper] |
| NEOMOD, Nesvorny et al. 2023, AJ 166, 55 | 12: nu6, 3:1, 5:2, 7:3, 8:3, 9:4, 11:5, 2:1, inner-belt weak resonances, Hungarias, Phocaeas, JFCs [V] | 15 < H < 25, CSS 2005-2012, size-dependent source weights | None | SwRI simulator |
| NEOMOD2, Nesvorny et al. 2024a, Icarus 411, 115922 | Same 12 | 15 < H < 28, CSS G96 2013-2022. nu6 weight 0.06 +/- 0.03 at H = 15 and 0.60 +/- 0.02 at H = 28; 3:1 0.28 -> 0.31; Hungaria upper limit 0.029 at H = 28. **Excess of low-e orbits at a = 1-1.6 au growing with H (about 30% at H = 28)**, attributed to tidal disruption; fitted weight 0.3 +/- 0.05 at H = 28 [V] | None | `give_me_prob.f` + `input_model.dat` |
| NEOMOD3, Nesvorny et al. 2024b, Icarus 417, 116110 | Same 12 | Sizes 1 m-100 km; albedo extrapolated below 100 m | **Yes, albedo is modelled per source** (see below) | `neomod3_simulator.f` generates H, orbit, size, albedo |

NEOMOD3 albedo model [V, arXiv 2404.18805]: two Rayleigh components. Global fit: dark fraction f_d = 0.233 +/- 0.030, scales 0.029 and 0.170. "Complex" model with one dark fraction per source, preferred by delta ln Z = 15.9:

| Source | f_d | Source | f_d |
|---|---|---|---|
| nu6 | 0.037 (upper limit 0.054) | 2:1 | 0.599 |
| 3:1 | 0.069 (upper limit 0.103) | inner weak res. | 0.335 |
| 5:2 | 0.247 | Hungarias | 0.149 (upper limit 0.222) |
| 7:3 | 0.498 (unconstrained) | Phocaeas | 0.761 (authors flag as inconsistent with other evidence) |
| 8:3 | 0.721 | comets | 0.463 (unconstrained) |
| 9:4 | 0.498 (unconstrained) | 11:5 | 0.814 (lower limit 0.723) |

It rests on only 428 cryogenic NEOWISE detections. Mean albedo 0.135 for D > 1 km and 0.182 for D < 1 km; dark fraction 0.33 at 1-3 km and 0.18-0.23 at 0.1-0.3 km. The authors state that D < 100 m albedos are extrapolated, "may be too high", and that the dark-to-bright ratio assumption below 100 m "may be incorrect". Their D > 10 m impact interval (about 40 yr) is about 4x longer than the bolide-based one.

Access and licences [V]:

- SwRI directory contents (modified 2025-10-03; `model1.tar` 2026-07-11): `neomod3_simulator.f`, `neomod2_simulator.f`, `neomod_simulator.f`, `give_me_prob.f` ("gives source probabilities for a NEO with a, e, i, 15 < H < 28"), `diamod_simulator.f`, `magmod_simulator.f`, three 62 MB binned model files. **No licence text anywhere.** The server sends an incomplete TLS chain; I had to add the DigiCert intermediate to fetch it.
- No API exists for any of these. Per-object values come from a table lookup that takes a few lines of code (done here).
- METEOMOD: web forms `meteomod.php` (1 m bodies) and `neomod.php` (km bodies, family version) take a list of orbits and return family probabilities; tarball `meteomod.tar.gz` (18.7 MB, 2025-09-24) contains maps, flux table and Python source. No licence stated.

## 3. (b) The 2024 meteorite-source results

**Broz et al. 2024, Nature 634, 566** (arXiv 2403.08552) [V]:
- About 70% of falls come from three recent break-ups of D > 30 km bodies: Karin (5.8 Myr), Koronis2 (7.6 Myr) and Massalia2 (< about 40 Myr). Before this only about 6% of falls were tied to a source (Moon, Mars, Vesta).
- Model composition at 1 km (among S + V material): HED 12%, H 13%, L 11%, LL 63%. At 1 m: HED 6%, H 40%, L 47%, LL 7%.
- Kilometre-scale sources: Phocaea (H), Juno (L), Flora (LL). Metre-scale: Karin and Koronis2 (H), Massalia2 (L), Flora (LL).
- Mechanism: young families keep a steep size distribution for a few tens of Myr, so they dominate at metre sizes; after about 100 Myr the sub-km slope flattens to about -1.4.
- CM-like material from Veritas (8.3 Myr) should arrive about 3x more often than H chondrites; the implied atmospheric bias against CM is a factor of about 40.

**Marsset et al. 2024, Nature 634, 561** (arXiv 2403.08548) [V abstract]: L chondrites (more than 20% of falls) and the 466 Myr L-chondrite infall both come from the Massalia family; evidence is spectroscopy, the low-inclination orbits of L-like NEOs and the 1.4 deg dust band. The 40 Myr second event is from the companion paper and Broz's project page.

**Broz et al. 2024, A&A 689, A183** (arXiv 2406.19727) [V]:
- 38 families modelled. CM/CR from Veritas (then Konig); CI from Polana (largest), with Euphrosyne, Clarissa, Misa, Hoffmeister each at least 10%; CO/CV/CK from Eos (about 1% of modelled carbonaceous flux but more than 30% of carbonaceous falls).
- Kilometre-sized CI-like NEOs: Polana about 58 bodies, Euphrosyne 39, Themis 10. CM-like: Adeona 22, Dora 7. M-type: Brasilia 13, Tina 4.
- Polana is the likely source of both Ryugu and Bennu.
- Pre-atmospheric metre-scale flux of carbonaceous material is "about the same" as ordinary chondrites, against 80% versus 4.4% of falls.

**How solid.** The L-Massalia and H-Karin/Koronis links have three independent supports (spectra, dust bands, fall orbits and cosmic-ray exposure ages). The quantitative metre-scale shares rest on extrapolating family size distributions across three orders of magnitude with a collisional model; the authors list uncertainties of 10-30% on individual factors. The carbonaceous-equals-ordinary flux claim cannot be checked against meteorites by construction.

**Follow-ups, 2025-2026** [V unless noted]:
- Jenniskens & Devillepoix 2025, MAPS 60, 928-973: 75 falls with orbits (81 by April 2025 per EPSC-DPS2025-146). Agrees on H chondrites from Koronis clusters (about 6, 11-14 and 83 Ma). **Disagrees on L chondrites: assigns them to the Hertha (Nysa) family, and puts some H chondrites (about 35 Ma CRE age) at Massalia.** HEDs from Vesta itself, not the family. So the family-level mapping is not settled, even where the class-level mapping is. https://meetingorganizer.copernicus.org/EPSC-DPS2025/EPSC-DPS2025-146.html
- Shober et al. 2025, Nature Astronomy (arXiv 2504.10690): 7,982 impacts and 540 potential falls from 19 networks. Thermal stress at low perihelion removes weak material before entry; meteoroids with q near 1 au are weaker than low-q ones, linked to tidal-disruption debris.
- Marsset et al. 2026, A&A 710, A389: LL chondrites have several parent bodies; Nysa (S-type part) supplies LL3, Flora supplies LL5-6.
- Simon et al. 2026 (arXiv 2610.07395, A&A accepted): in MITHNEOS S-complex NEOs, LL6-7 is 57.9%, H 20.1%, L 13.8%, LL3 8.2% overall; below about 100 m (N = 53) the H and L shares rise on low-inclination orbits, toward the fall mix.
- Sanchez et al. 2024, PSJ 5, 131: an inconvenient counter-example. 84 small NEOs (mean 126 m): of 56 ordinary-chondrite-like objects, 8% H, 31% L, 61% LL, which is the kilometre-scale mix, not the fall mix.
- Moskovitz et al. 2026 and Lopez-Oquendo et al. 2026 (section 4) support the idea that small NEOs are less S-dominated.
- I found no formal published rebuttal of the Nature papers. Broz et al. 2026 (A&A 708, A162) exists and is cited by Simon et al.; I did not read it.

## 4. (c) Existing links between NEO taxonomy and source region

**Is there a published "class probability given orbit" predictor? Yes, several partial ones:**

1. Granvik 2018 cell table with Morbidelli 2020 albedo categories: P(pV <= 0.1) and P(0.1 < pV <= 0.3) per (a, e, i, H) cell. Public.
2. NEOMOD3: albedo mixture per source, generative; a per-object value is the sum over sources of p_j x f_d,j.
3. METEOMOD: P(family | a, i) with each family labelled by meteorite class, which amounts to P(meteorite class | orbit) for 1 m bodies. Public web tool and tarball.
4. Marsset et al. 2022: debiased taxonomy fractions per escape route, to be multiplied by Granvik ER probabilities (their Table 7 lists ER probabilities per object).
5. Dotson et al. (NASA Ames; used in the PDC 2025 exercise): a Bayesian network that infers taxonomy, density, porosity and strength from albedo and population priors for a single threatening object. This is the closest prior art to the project's fusion idea. https://cneos.jpl.nasa.gov/pd/cs/pdc25/PDC25-Epoch2-physical_properties.pdf [V that it exists; details not read]

What I did not find: a per-object catalogue for NHATS, or any published out-of-sample calibration test of these predictors.

**Numbers on how much the orbit carries.**

Marsset et al. 2022, AJ 163, 165 (arXiv 2202.13796), Table 4, debiased percentages [V]. Sample: 491 new spectra of 420 NEOs plus Binzel 2019; about 90% within 15 < H < 23; ERs from Granvik 2018.

| Escape route | S/Q | C/P | B | D | V | carbonaceous (B+C/P+D) |
|---|---|---|---|---|---|---|
| nu6 | 44.4 (+5.7/-5.9) | 33.7 | 7.4 | 4.2 | 1.7 | 45.3 |
| 3:1J | 43.3 +/- 5.6 | 34.3 | 8.3 | 8.5 | 1.1 | 51.1 |
| 5:2J | 29.8 +/- 3.7 | 47.7 | 4.0 | 14.3 | 0.5 | 66.0 |
| 2:1J | 7.2 +/- 2.0 | 59.9 | 23.4 | 5.1 | 0.0 | 88.4 |
| Phocaea | 69.1 +/- 10.5 | 18.2 | 3.4 | 2.8 | 3.8 | 24.4 |

Overall: observed S/Q 66% falls to 42% after debiasing; carbonaceous rises from 23% to 48%. The paper says the two dominant routes, **nu6 and 3:1J, "exhibit very similar distributions with one another (Pearson correlation coefficient of 99.8%)"**. Since those two routes carry 95% or more of the NHATS source probability, the escape-route chain has no leverage there. Even between nu6 and 5:2J the likelihood ratio for "carbonaceous" is only 1.46.

Other surveys:

- Binzel et al. 2019, Icarus 324, 41 (MITHNEOS, more than 1,000 NEOs) [V abstract]: 60% S, 20% C, 20% other, "remarkably constant" from 10 km to 100 m, with unaccounted bias below about 500 m. **"Mission accessible asteroids (delta-V <= 7 km/s) ... appear to be a representative mix of the overall NEO population, consistent with strong dynamical mixing."** LL chondrites prefer nu6, H chondrites the 3:1 region, L weakly the outer belt.
- Devogele et al. 2019, AJ 158, 196 (MANOS spectra) [V]: 210 NEOs, mean H about 25, mean delta-v 5.7 km/s, mean MOID 0.03 au. Q 27.1%, X 23.8%, S 16.7%, C 10.9%, K 8.6%; S+Q 43.8 +/- 4.6% against 52% in MITHNEOS and NEOSHIELD-2; A-type 3.8 +/- 1.3%. They attribute the changes to fewer Phocaeas and more Hungarias at small size, and note that low-MOID objects "may have an increased likelihood to have lost the memory of their source regions".
- Moskovitz et al. 2026 (arXiv 2603.15872, PSJ accepted) [V]: griz colours for 189 MANOS NEOs (median H 23.9); combined with MITHNEOS and NEOSHIELD-2, 831 objects. **S+Q falls from about 70% at H = 14 to about 50% at H = 22 and about 35% at H = 28 (2.9 sigma); X-complex rises (2.8 sigma); C stays near 15%.** Source region from Granvik is "exclusively" nu6 at small sizes, yet S+Q falls, so "source region is not necessarily the dominant contributing factor". Preferred explanation: young primitive families (Veritas, Polana, Eos) contribute more at small sizes. Seven objects with delta-v < 4 km/s: 2019 SU3 Xk, 2021 GK1 B, 2022 BX5 D (reddest known NEO), 2022 DX B, 2022 NX1 Q, 2024 PT5 Sq (lunar), 2024 RZ3 Xk. Only 13 S-type and 8 X-type objects at H > 27.
- Lopez-Oquendo et al. 2026 (arXiv 2608.28779, PSJ accepted) [V]: UKIRT ZJHK colours for 122 NEOs, 5-150 m, median 60 m. Observed S 40.4 +/- 7%, C/X 43.9 +/- 7%, D 5.3 +/- 3%, A 5.2 +/- 3%. First-order debiased: S 23%, C/X 67%.
- Sanchez et al. 2024 [V]: S-complex 66%, C/X 17%, other 17% for small NEOs; 83% from nu6, 16% from 3:1. They introduce an "Sx" class of weak-band S-like objects that other surveys may count as C or X.
- Perna et al. 2018, P&SS 157, 82 (NEOSHIELD-2): 147 spectra, mean H about 22; C/X about 27% and D about 7% as quoted by Lopez-Oquendo et al. [V secondary].
- DeMeo & Binzel 2008, Icarus 194, 436: about 8% of NEOs are dormant comets by combined Tisserand and albedo/taxonomy criteria [R; the 2006 thesis version says 16%]. Irrelevant to NHATS (no JFC probability there).
- Lin et al. 2018, P&SS (92 NEAs photometric taxonomy): exists; I could not retrieve its numbers today [U].

## 5. (d) The low delta-v population

How Earth-like is NHATS [V, own computation]: median for dv < 5 km/s is a = 1.02 au, e = 0.083, i = 2.2 deg; 74% have H >= 27. Inside Jedicke's lunar-ejecta box (a 0.8-1.2, e < 0.2, i < 5 deg): 13% of all NHATS, 76% of dv < 6, **87% of dv < 5**. Inside the NEOMOD2 excess region (1 < a < 1.6, q 0.9-1.1, i < 10 deg): 46% of all NHATS.

Three non-main-belt-delivery explanations compete in this corner:

**Lunar ejecta.**
- Sharkey et al. 2021 (Commun. Earth Environ. 2, 231): Kamo'oalewa's red spectrum best matched by lunar-like silicates. Castro-Cisneros et al. 2023 (same journal, 4, 372): rare dynamical pathways from the Moon to quasi-satellite orbits exist. Jiao et al. 2024 (Nature Astronomy): proposes Giordano Bruno crater (22 km, 1-10 Myr). [V via search summaries]
- 2024 PT5 (H 27.45): Kareta et al. 2025 conclude lunar ejecta (pyroxene-rich, matches lunar samples, no asteroid type); Bolin et al. 2025 prefer lunar over inner main belt. https://arxiv.org/abs/2412.10264 [V via search]
- Jedicke et al. 2025 (Icarus 438, 116587; arXiv 2504.17985) [V abstract]: lunar ejecta can account for the whole observed bound/minimoon population, but the prediction carries "many orders of magnitude" of uncertainty. States that spectra of 2020 CD3, 2024 PT5 and Kamo'oalewa are more consistent with lunar basalts than with main-belt types.
- Alessi & Jedicke 2026 (Icarus; arXiv 2604.13296) [V]: nominal **71 lunar co-orbitals larger than 10 m versus about 1,600 from the main belt (NEOMOD3)**, so about 4% nominal, with "approximately +/- 5 orders of magnitude systematic uncertainty". "Main belt objects dominat[e] the high e and i ... and lunar ejecta predominant when e -> 0 and i -> 0". NEOMOD3 predicts 6 co-orbitals above 100 m where 12 are known. Lunar-origin co-orbitals have much shorter lifetimes than the 25,000 yr of main-belt ones.
- Against, for Kamo'oalewa: Fenucci et al. 2026 (A&A accepted; arXiv 2601.08923): the main belt supplies 1.23 +/- 0.13 Kamo'oalewa-like quasi-satellites on average against 0.042 from Giordano Bruno. Zhang et al. 2026 (arXiv 2603.28102, under revision at Nature Communications): band centre 1.001 +/- 0.028 micron, LL-chondrite composition with heavy space weathering, Flora family via nu6. [V abstracts]

**Tianwen-2 at Kamo'oalewa** [V from Sky & Telescope, SpaceNews summaries, Wikipedia]: rendezvous burn about 7 June 2026; within 20 km on 2-4 July 2026; CNSA released the first image on 6 July 2026. The body is roughly 16-27 m across (sources differ), smaller than expected, and looks like a single jagged fragment with few boulders. **No composition result and no sampling attempt had been reported in anything I could find as of today.** Departure is planned for April 2027 and capsule return for late November 2027. One press quote (Granvik) reads the image as favouring an asteroidal origin; that is an opinion on one low-resolution frame, not a result.

**Tidal-disruption fragments.** Granvik & Walsh 2024 (ApJL; arXiv 2312.08247): CSS-based models under-predict NEAs with perihelia at Earth's and Venus's distances; the excess matches tidal-disruption predictions [V abstract]. NEOMOD2 finds the same excess for 25 < H < 28 and attributes it to disruption of D > 50 m rubble piles [V]. Chow & Brown 2025 (arXiv 2501.03308): 14 decameter impactors show no evidence of recent (< 10^4 yr) disruption, weak evidence for older; sources about 70% nu6, 20% Hungaria, 10% 3:1 [V abstract]. Composition implication: fragments inherit the parent's class but are biased to weak rubble piles; Shober et al. argue this favours carbonaceous material.

**Artificial objects.** 2020 SO (Surveyor 2 Centaur, identified through solar radiation pressure and low relative velocity; Battle et al. 2024, PSJ), J002E3 (Apollo 12 S-IVB), WT1190F, and 2018 CN41 (Tesla Roadster upper stage, announced by the MPC on 2 January 2025 and deleted within a day) [V via search]. 2020 SO is not in today's NHATS list [V]. Moskovitz et al. note that for 2022 BX5 an 18-day arc is too short to rule out an artificial origin from radiation pressure alone.

**How a prior should treat this.**
- Split by origin first: P(origin | a, e, i, H) over {main belt, lunar, artificial}, then P(class | origin, H). Do not let the main-belt source models speak for the Earth-like corner; they contain neither a lunar nor a tidal source, and they already miss the observed counts there.
- Lunar weight: rising toward e -> 0, i -> 0, a -> 1 and toward small size (no plausible lunar object above roughly 100 m; Cruithne-size objects are excluded). Population anchor about 4% for co-orbitals overall, with a hyperprior spanning roughly 0.1% to 50% in the extreme corner. The empirical anchor is thin: of the handful of spectrally characterised objects in this corner, one (2024 PT5) is widely accepted as lunar, one or two more are claimed (2020 CD3, Kamo'oalewa, the latter now disputed).
- Lunar material means anhydrous basaltic or feldspathic silicate: stony, no hydrated minerals, low metal. It belongs in the catalogue's "other stony" bin with a resource note, not in "S-type".
- Artificial weight: non-zero for H > 27, very low Earth-relative velocity and short arcs; the area-to-mass channel (channel 1 of the project) is the discriminator.

## 6. (e) Meteorite falls and fireballs as labelled data

| Dataset | Size | Body size | Labels | Access | Status |
|---|---|---|---|---|---|
| meteoriteorbits.info (Meier) | **61 falls with published orbits** as of 2026-09-22: 19 H (+1 mixed), 19 L, 6 LL (+2 L/LL), 7 carbonaceous, 5 achondrites (2 HED, 1 eucrite, 1 ureilite, 1 aubrite), 1 EL6, 1 iron (provisional) | mostly 0.1-few m | meteorite class | web table (a, e, i, node, peri, mass, reference); no licence stated | [V] |
| Jenniskens & Devillepoix 2025 review | 75 falls (81 by April 2025) | same | class, CRE age, proposed family | paper tables | [V secondary] |
| Granvik & Brown 2018, Icarus 311, 271 | 25 falls, ER probabilities | same | class | paper Table 5 | [V] |
| Imminent impactors (ESA NEOCC) | **13** as of 2026-09-24; 4 with recovered, classified meteorites: 2008 TC3 (ureilite), 2018 LA (HED), 2023 CX1 (L), 2024 BX1 (aubrite) | 0.5-8 m | telescope orbit + lab class | ESA and CNEOS pages | [V count; classes V via meteoriteorbits.info] |
| Borovicka et al. 2022, A&A 667, A157/A158 (European Network) | 824 fireballs, 2017-2018; 473 with aphelion < 4.9 au, 336 of them sporadic | 10^-4 to 10^2 kg (cm to about 0.4 m) | strength class Pf-I..V from peak dynamic pressure; Pf-I 54%; probable irons 2.5% of asteroidal-orbit fireballs (3.6% of sporadic) | CDS J/A+A/667/A157. **CDS returned "page unavailable" and the TAP endpoint timed out today, so I could not confirm access** | [V paper; access U] |
| Brown et al. 2016, Icarus 266, 96 | 59 metre-scale airbursts | 1-20 m | strength proxy (height of peak brightness) | paper | [V via search] |
| CNEOS fireballs (US Government sensors) | **1,074 events 1988-04-15 to 2026-10-04; 363 with velocity vectors** | 0.5-20 m | energy, height, velocity; no class | https://ssd-api.jpl.nasa.gov/fireball.api | [V] |
| Chow & Brown 2025 | 14 decameter impactors | about 10 m | orbit, ER probabilities | paper | [V abstract] |
| Shober et al. 2025 | 7,982 impacts, 540 potential falls | cm to m | orbit, survival | paper/networks | [V] |

Granvik & Brown's own table shows the degeneracy at fall level: Pribram H5 70% 3:1; Lost City H5 69% nu6; Chelyabinsk LL5 80% nu6; Tagish Lake C2 82% nu6; Novato L6 89% nu6; Sutter's Mill CM2 36% nu6, 31% 3:1, 26% JFC; Bunburra Rockhole eucrite 68% nu6; Almahata Sitta ureilite 70% nu6. Nearly every class peaks at nu6 or 3:1. [V]

Can these train an orbit -> material model for metre-scale bodies? Only weakly.

- **Useful property:** Earth impactors are selected by collision probability, which favours low relative velocity and q near 1 au. That is the same orbital selection as accessibility, so falls sample NHATS-like orbit space better than telescopic surveys do.
- **Sample size:** 61 labelled falls across about 8 classes. A model with more than one or two free parameters will overfit.
- **Atmospheric and pre-atmospheric filtering:** carbonaceous material is under-represented among falls by a factor of 15-40 (Broz et al. 2024; Lopez-Oquendo et al. 2026 give "at least 15"). The filter depends on orbit (entry speed, perihelion history), so it biases the orbit-class relation and not only the base rate.
- **Memory:** family assignments work for falls whose semimajor axis is still near the delivery resonance (for example H chondrites at a = 2.5-2.8 au, low i pointing to Koronis). Bodies that have evolved to a near 1 au have lost that memory.
- **Strength is not composition:** Pf cannot identify irons (they spread over Pf 0.1-0.6) and Pf-II mixes asteroidal and cometary material.
- **CNEOS velocities** are known to be unreliable for a sizeable minority of events [R: Devillepoix et al. 2019].
- The four typed imminent impactors are three achondrites and one L chondrite. With n = 4 this proves nothing, but it is a warning against assuming metre-scale Earth-approachers follow the 80% ordinary-chondrite fall statistics.

Best use: an external check of the base rates and of the origin mixture at metre scale, with an explicit survival model. Not a training set for per-object prediction.

## 7. (f) The size problem

**Evidence that the mix is the same at all sizes.** Binzel 2019 (constant from 10 km to 100 m); Marsset 2022 ("argues against any strong composition change with size ... between about 5 km down to about 100 m"); Morbidelli 2020 (no significant albedo-size dependence); Sanchez 2024 (S-complex 66% below 300 m; LL-dominated).

**Evidence that it changes.**
- Source mix certainly changes: nu6 weight 0.06 at H = 15 versus 0.60 at H = 28 (NEOMOD2). NEOMOD2 also quotes the first NEOMOD paper as finding the main inner resonances contributing about 30% of NEOs at H = 15 and about 80% at H = 25 (the start of that sentence was cut in my copy, so the exact set of resonances is [U]).
- Taxonomy: S+Q about 70% at H = 14 to about 35% at H = 28, X-complex rising (Moskovitz 2026, 831 objects); S+Q 43.8% at mean H 25 (Devogele 2019); S 40%, C/X 44% observed below 150 m (Lopez-Oquendo 2026).
- Within the S-complex: LL-dominated at km scale, shifting toward H and L below about 100 m (Simon 2026), as Broz 2024 predicts (LL 63% at 1 km, 7% at 1 m).
- NEOWISE points the other way on albedo: small NEOs are on average brighter (NEOMOD3), which fits "more nu6 = more S" and conflicts with "more dark primitives".

**Reconciling these.** The rising X-complex is not necessarily dark. X splits by albedo into E (> 0.3), M (0.1-0.3) and P (< 0.1); among larger objects with albedos P is the majority (53-57%, Moskovitz 2026), but the split for small low delta-v NEOs is unmeasured. Devogele attributed the X excess to Hungaria-derived E-types, which would be bright and enstatite-rich. Sanchez argues some "X" are weak-band ordinary chondrites. So the single least-known quantity for this project is **what the roughly 20-25% X-complex among H > 24 low delta-v objects is made of**, and that is also where any metal-rich objects are hiding. Independent base rates for metal: irons are about 2.5-3.6% of asteroidal fireballs at cm-dm scale and irons plus stony-irons about 5-6% of falls.

### 7.2 H-conditioned versus size-conditioned rates

A catalogue entry is defined by its H, not its diameter. At fixed H a dark object is larger and therefore rarer, so P(dark | H) is several times lower than P(dark | D). With albedos 0.05 and 0.20 and a cumulative size slope near 2.6, the dark-to-bright ratio differs by roughly a factor of 6 between the two conditionings. That is the likely reason the Granvik/Morbidelli table gives about 10% dark per H cell while 36% of the 69 NHATS members with an SBDB albedo (mostly thermal-infrared detections, which select by size rather than brightness) are dark, and why Lopez-Oquendo's 44% observed C/X becomes 67% debiased. I have not checked the provenance of each SBDB albedo, so treat the 36% as indicative. The per-object prior must use the H-conditioned rate, which is close to the observed, un-debiased fractions in H-matched surveys. Debiased fractions answer a different question (what the population is made of at a given size) and should only be used for population statements. Getting this wrong would bias every dark-class probability in the catalogue by a factor of several.

## 8. Conclusion

### 8.1 Most defensible construction

1. **Origin layer.** P(origin | a, e, i, H, arc, A1) over main belt, lunar ejecta, artificial. Informative only in the Earth-like corner; hyperpriors wide and stated.
2. **Main-belt layer = H-binned empirical base rate, not a per-object source chain.** A Dirichlet over classes for each H bin (for example H < 22, 22-25, 25-28, > 28), fitted to the pooled, H-matched observed samples: MANOS spectra (210) and colours (189), UKIRT (122), NEOSHIELD-2 (147), Sanchez (84), MITHNEOS for the large end. Indicative values for H 24-29: S+Q 35-45%, X-complex 20-25% (composition unresolved), C-complex 11-15%, B+D about 5%, V about 5%, A/K/L/O/R 10-15%. The Dirichlet concentration should reflect survey-to-survey disagreement, which is larger than Poisson error (for example Sanchez 66% S versus MANOS 35-44%).
3. **Carry the source models as a documented sensitivity, not as the prior.** Report for each object the Granvik, NEOMOD and METEOMOD vectors side by side. Use them to flag the rare NHATS objects where they do differ from the pack (a > 2 au, high inclination, non-zero JFC or outer-belt probability).
4. **Class -> density and resource relevance** through meteorite analogues, with the X-complex and lunar branches kept explicit.
5. **State the conditioning.** Per-object probabilities are H-conditioned; the joint posterior over class, albedo and diameter follows from the class albedo distributions.

### 8.2 Realistic discriminating power

- Inside NHATS, orbit -> class information is 0.003-0.005 bits from escape-route models and at most about 0.05 bits from the family-level model after removing map noise; AUC about 0.5 on the available labels. Expect zero measurable skill over the H-binned base rate.
- Over the whole NEO population: AUC about 0.60-0.63, log-loss skill about 4-5%, all of it from a > 2 au.
- The prior's contribution to the catalogue is a calibrated starting point and honest width. Per-object discrimination has to come from the other channels (colours, albedo, non-gravitational accelerations).
- The one place the orbit may move a posterior appreciably is P(lunar) and P(artificial) for the few hundred most Earth-like objects.

### 8.3 Validation

1. **Known-object recovery, pre-registered.** Hold out NEOs with spectra or albedos; metric = log-loss and Brier skill against the H-binned base rate, with reliability diagrams, stratified by H and by a < 2 au versus a > 2 au. Pre-register the expectation of no skill for a < 2 au; a non-null result there would itself be news. Use SsODNet and the survey tables for a larger label set than SBDB's 323.
2. **Injection-recovery.** Draw synthetic NEOs from the NEOMOD3 simulator (source, orbit, albedo known), impose NHATS-like and survey-like selection, and check the pipeline recovers the injected orbit-albedo relation where one exists and returns a null where none was injected. Also inject a lunar population with Alessi-Jedicke orbital distributions at known fractions and test recovery of the fraction.
3. **Cross-model disagreement** as a published product: Hungaria 21.5% versus 0.7%; P(dark) 5% versus 10% versus 25% versus 39%.
4. **Metre-scale external check:** predicted class mix for Earth impactors versus the 61 falls and 13 imminent impactors, with an explicit survival model and its uncertainty.
5. **Forward tests with dated predictions:** P(lunar) and class for Kamo'oalewa before the Tianwen-2 sample returns (November 2027); class predictions for low delta-v objects with upcoming apparitions (2022 DX in 2028, 2021 GK1 in 2029, 2019 SU3 in 2032, per Moskovitz Table 7); Rubin colours and NEO Surveyor albedos as they arrive.
6. **Fresh-agent adversarial review** of the H-versus-D conditioning and of every pooled base rate.

## Sources

- JPL NHATS API: https://ssd-api.jpl.nasa.gov/nhats.api
- JPL SBDB query API: https://ssd-api.jpl.nasa.gov/sbdb_query.api
- JPL fireball API: https://ssd-api.jpl.nasa.gov/fireball.api
- NEOMOD simulator directory: https://www.boulder.swri.edu/~davidn/NEOMOD_Simulator/ (redirects to https://www2.boulder.swri.edu/~davidn/NEOMOD_Simulator/)
- NEOMOD (Nesvorny et al. 2023): https://arxiv.org/abs/2306.09521
- NEOMOD2 (Nesvorny et al. 2024a): https://arxiv.org/abs/2312.09406
- NEOMOD3 (Nesvorny et al. 2024b): https://arxiv.org/abs/2404.18805
- Granvik et al. 2018: https://arxiv.org/abs/1804.10265 ; data https://www.mv.helsinki.fi/home/mgranvik/data/Granvik+_2018_Icarus/
- Morbidelli et al. 2020: https://arxiv.org/abs/2001.03550
- ESA NEOPOP: https://neo.ssa.esa.int/neo-population-generator
- METEOMOD: https://sirrah.troja.mff.cuni.cz/~mira/meteomod/ ; https://sirrah.troja.mff.cuni.cz/~mira/meteomod/meteomod.php ; https://sirrah.troja.mff.cuni.cz/~mira/neomod/neomod.php
- Broz et al. 2024 Nature: https://arxiv.org/abs/2403.08552 ; https://ui.adsabs.harvard.edu/abs/2024Natur.634..566B
- Marsset et al. 2024 Nature: https://arxiv.org/abs/2403.08548 ; https://ui.adsabs.harvard.edu/abs/2024Natur.634..561M
- Broz et al. 2024 A&A: https://arxiv.org/abs/2406.19727
- Marsset et al. 2026 A&A (Nysa, LL): https://arxiv.org/abs/2602.08732
- Simon et al. 2026: https://arxiv.org/abs/2610.07395
- Jenniskens 2025 EPSC abstract: https://meetingorganizer.copernicus.org/EPSC-DPS2025/EPSC-DPS2025-146.html ; review PDF https://dfn.gfo.rocks/documents/papers_reprints/Jenniskens_2025_review_meteorite_sources.pdf
- Shober et al. 2025: https://arxiv.org/abs/2504.10690
- Marsset et al. 2022: https://arxiv.org/abs/2202.13796
- Binzel et al. 2019: https://arxiv.org/abs/2004.05090
- Devogele et al. 2019: https://arxiv.org/abs/1909.04788
- Moskovitz et al. 2026: https://arxiv.org/abs/2603.15872
- Lopez-Oquendo et al. 2026: https://arxiv.org/abs/2608.28779
- Sanchez et al. 2024: https://arxiv.org/abs/2404.18263
- Perna et al. 2018: https://arxiv.org/abs/1803.08953
- PDC25 physical properties (Dotson et al. model): https://cneos.jpl.nasa.gov/pd/cs/pdc25/PDC25-Epoch2-physical_properties.pdf
- Jedicke et al. 2025: https://arxiv.org/abs/2504.17985
- Alessi & Jedicke 2026: https://arxiv.org/abs/2604.13296
- Fenucci et al. 2026: https://arxiv.org/abs/2601.08923
- Zhang et al. 2026: https://arxiv.org/abs/2603.28102
- Kareta et al. 2025 (2024 PT5): https://arxiv.org/abs/2412.10264
- Jiao et al. 2024: https://www.nature.com/articles/s41550-024-02258-z
- Tianwen-2 arrival: https://skyandtelescope.org/astronomy-news/tianwen-2-arrives-at-quasi-moon-kamo%ca%bboalewa-returns-images/ ; https://spacenews.com/tianwen-2-arrives-at-asteroid-kamooalewa-first-image-revealed/ ; https://en.wikipedia.org/wiki/Tianwen-2
- Granvik & Walsh 2024: https://arxiv.org/abs/2312.08247
- Chow & Brown 2025: https://arxiv.org/abs/2501.03308
- Battle et al. 2024 (2020 SO): https://aasnova.org/2024/04/17/how-to-tell-space-rocks-from-space-junk/
- 2018 CN41 deletion: https://www.astronomy.com/science/astronomers-just-deleted-an-asteroid-because-it-turned-out-to-be-elon-musks-tesla-roadster/
- Granvik & Brown 2018: https://arxiv.org/abs/1804.07229
- meteoriteorbits.info: https://www.meteoriteorbits.info/
- ESA past impactors: https://neo.ssa.esa.int/past-impactors
- Borovicka et al. 2022: https://arxiv.org/abs/2209.11186 ; https://arxiv.org/abs/2209.11254 ; catalogue https://cdsarc.cds.unistra.fr/viz-bin/cat/J/A+A/667/A157
- Brown et al. 2016: https://arxiv.org/abs/1511.07479
