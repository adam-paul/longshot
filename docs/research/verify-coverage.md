# Verification: coverage numbers (sizes, spin, labelled set, coverage table, NEOWISE gap)

Independent check of `catalogs.md` and of one claim in `new-surveys.md`. All checks ran on 2026-11-21. Status: **complete**, except where section 7 says otherwise.

Inputs: local snapshots `data/research/dl/catalogs/nhats.json` (7,229 objects today; the first round saw 7,226 on 2026-11-20) and `data/research/dl/catalogs/sbdb_neo.json` (43,158 near-Earth asteroids). Everything else was downloaded again today.

## 0. Bottom line

1. **The headline coverage numbers hold.** Objects with any composition-relevant measurement: **14 of 286** (delta-v < 5 km/s) and **37 of 726** (delta-v < 6) are reproduced exactly from 726 freshly fetched SsODNet ssoCards plus fresh tables. For all of NHATS my stratified estimate is **449 (95% interval 434 to 529)** against the first round's "about 455 (390 to 540)". 432 are known by name; the rest is the estimate for 5,835 unflagged objects from a random sample of 332.
2. **All 18 per-source counts in the first-round table replicate exactly** (SBDB fields, Mahlke, Sergeyev, MANOS, MITHNEOS, RATIR, Spitzer, LCDB, radar).
3. **The SsODNet bulk table could not be downloaded** (1.75 kB/s, then the connection dropped). There is still no exact all-NEA SsODNet column. For NHATS this no longer matters much: the targeted cards plus the random sample pin every channel.
4. **Sizes.** About **197 of 7,229** NHATS objects (2.7%) have an albedo-independent size. Of the **174** NHATS objects with a JPL non-gravitational parameter, **67 (39%)** have one, but only **1 of the 16** under 5 km/s and **6 of the 28** under 6 km/s. A density-times-diameter constraint therefore turns into a density for 4 in 10 overall and almost never for the cheapest targets.
5. **Spin.** SBDB lists a rotation period for 306 NHATS objects, but SBDB and SsODNet hold different objects: the union is **333 known, about 416 (366 to 531) estimated**; 44 (not 32) under 6 km/s and 20 (not 14) under 5 km/s. For H >= 24 between 70% and 96% of objects spin faster than 2.2 hours; for H >= 26 about two thirds to three quarters spin faster than 10 minutes. None of the 20 measured objects under 5 km/s has a period of an hour or more.
6. **Labelled set.** Published tables alone give **2,787** distinct NEAs with a spectral or colour class (2,318 with H < 22, 308 with 22 <= H < 25, 161 with H >= 25); **279** are NHATS members (117 / 79 / 83), rising to **302** (121 / 89 / 92) with SsODNet-only classes.
7. **NEOWISE gap.** SBDB stopped taking NEOWISE diameters at the 2019 compilation. 642 NEAs with a published NEOWISE fit have no SBDB diameter, 29 of them in NHATS. The first round's example 2020 JU is published (0.15 km, Masiero+2021). Of 35 NHATS objects with NEOWISE astrometry and no SBDB diameter, 14 already have a published fit, 8 have data only from after the last fit paper, 9 were detected earlier but never fitted.

## 1. Sizes

SBDB counts replicate: diameter 70 / 3 / 1 / 1,247 (all NHATS / delta-v < 6 / delta-v < 5 / all NEAs), A2 169 / 23 / 11 / 618, A1 18 / 12 / 10 / 21. 174 NHATS objects have A1 or A2.

### 1.1 Albedo-independent sizes in NHATS

| Size evidence | All NHATS (7,229) | dv < 6 (726) | dv < 5 (286) | All NEAs (43,158) |
|---|---|---|---|---|
| Spitzer NEO table (ExploreNEOs, NEOSurvey, NEOLegacy) | 112 | 4 | 0 | 2,124 |
| NEOWISE published fit, 12 tables (cryogenic to reactivation year 7, incl. "manually recovered") | 91 | 1 | 0 | 1,823 |
| Thermal infrared, Spitzer or NEOWISE tables | 177 | 5 | 0 | 3,434 |
| Thermal infrared incl. ssoCard thermal methods (NEATM, TPM) | 185 | 8 | 1 | not available |
| Radar size in ssoCard (Zambrano-Marin+2024, Brozovic+2018, Ostro+1999, Bondarenko+2019) | 11 | 2 | 2 | not available |
| Radar size in SBDB only (2012 XB112, 2.5 m from Goldstone bandwidth and 2.6 min period) | 1 | 1 | 1 | not counted |
| Spacecraft size (Bennu, Ryugu, Itokawa) | 3 | 0 | 0 | not counted |
| Occultation size | 0 | 0 | 0 | not counted |
| SBDB diameter, any method | 70 | 3 | 1 | 1,247 |
| Radar astrometry exists (not a size) | 232 | 25 | 12 | 1,110 |
| **Any albedo-independent size** | **197** | **11** | **4** | at least 3,462 |

The 197 is exact for the 1,394 objects fetched by criterion (every object with A1 or A2, a thermal-table entry, an SBDB diameter, radar astrometry, an SBDB period, any taxonomy or colour table entry, a number, or delta-v < 6). In the random sample of the other 5,835 objects, 0 of 332 have a diameter, so the remainder adds 0 (95% upper bound 67). One of the 197 is wrong and should be dropped: 2010 NU71 (H 22.7) carries 1.126 km from a main-belt table (Masiero+2011) in both SBDB and SsODNet.

By size: H < 22: 109 of 202 (54%); 22 <= H < 25: 68 of 1,620 (4.2%); 25 <= H < 28: 17 of 4,295 (0.4%); H >= 28: 3 of 1,106 (0.3%).

The four under 5 km/s: 2009 BD (4 m, Spitzer thermophysical model), 2014 WU200 (7 m, radar), 2016 RD34 (6 m, radar), 2012 XB112 (2.5 m, radar bandwidth). The radar values in SsODNet carry no uncertainty.

### 1.2 Objects with a non-gravitational parameter

| NHATS subset | N | With an albedo-independent size | Share |
|---|---|---|---|
| A1 or A2 | 174 | 67 | 39% |
| A2 | 169 | 67 | 40% |
| A2 at 3 sigma or better | 154 | 61 | 40% |
| A1 | 18 | 4 (2009 BD, 2011 MD, Apophis, 1998 KY26) | 22% |
| A1 at 3 sigma or better | 10 | 1 | 10% |
| A1 or A2, delta-v < 6 | 28 | 6 (2009 BD, 2011 MD, 2014 YD, 2001 QJ142, 613862, 2001 CQ36) | 21% |
| A1 or A2, delta-v < 5 | 16 | 1 (2009 BD) | 6% |
| A1 or A2, H < 22 | 57 | 41 | 72% |
| A1 or A2, 22 <= H < 25 | 76 | 22 | 29% |
| A1 or A2, 25 <= H < 28 | 31 | 3 (1998 KY26, 2011 EP51, 2011 MD) | 10% |
| A1 or A2, H >= 28 | 10 | 1 (2009 BD) | 10% |

Cards were fetched for 173 of the 174; the last, 2026 QQ8, is too new for SsODNet. 66 of the 67 sizes are thermal infrared (49 from Spitzer, 24 from NEOWISE, some both); the other is 1998 KY26 (radar and lightcurve shape). For all NEAs with A1 or A2 (623), 328 (53%) have a thermal-table size or SBDB diameter.

Objects with a strong non-gravitational signal and no size, delta-v < 5: 2026 QQ8, 2021 GM1, 2022 OB5, 2020 CD3, 2020 GE, 2021 VH2, 2023 YO1, 2006 RH120, 2025 PN7, 2020 WY, 2012 LA, 2015 TC25, 478784, 2007 XB23, 2020 PP1. For these the result stays a density-times-diameter product. (SsODNet lists published densities for 2012 LA and 2015 TC25, which rest on an assumed size.)

Caveats:
- Spitzer sizes are single-band 4.5 micron fits with an assumed beaming parameter; NEOWISE reactivation fits carry about 30% diameter uncertainty (Masiero+2021).
- SsODNet has no diameter for 72 of the 112 NHATS objects in the Spitzer table. The first round's remark that SsODNet lacks NEOSurvey and NEOLegacy is confirmed.

## 2. Spin

### 2.1 Coverage

| Source | All NHATS | dv < 6 | dv < 5 | All NEAs |
|---|---|---|---|---|
| SBDB `rot_per` | 306 | 32 | 14 | 2,180 |
| LCDB (release of 2023-10-01), any quality / U >= 2 | 304 / 273 | 31 / 30 | 13 / 13 | 2,174 / 1,990 |
| SsODNet ssoCard spins | 231 known, about 314 estimated | 32 | 14 | not available |
| **Union** | **333 known, about 416 (366 to 531)** | **44** | **20** | at least 2,195 |

The first-round counts are confirmed, but it never took the union. SsODNet holds periods that SBDB and LCDB lack (Alarcon+2026, Beniyama+2022, Sanchez+2024 and others): 27 such objects among the 1,704 cards fetched and 5 of 332 in the random sample of the remainder, mostly 2024 to 2025 discoveries. Where both SBDB and SsODNet give a period (about 204 objects), 13 disagree by more than 20%, including factor-of-two aliases (2011 MD, 2015 RF36) and one gross conflict (2013 NJ: 250 h against 2.02 h).

### 2.2 Fast-rotator fractions among objects with a measured period

NHATS, union of all sources (333 objects):

| H bin | NHATS objects | with period | P < 2.2 h | P < 10 min | P >= 1 h | median P |
|---|---|---|---|---|---|---|
| < 18 | 4 | 4 | 0% | 0% | 100% | 13 h |
| 18–20 | 40 | 30 | 0% | 0% | 100% | 7.7 h |
| 20–22 | 158 | 51 | 16% | 4% | 92% | 7.5 h |
| 22–24 | 643 | 60 | 53% | 22% | 55% | 1.7 h |
| 24–26 | 2,443 | 96 | 91% | 42% | 22% | 12 min |
| 26–28 | 2,829 | 63 | 97% | 75% | 6% | 5.0 min |
| >= 28 | 1,106 | 29 | 100% | 93% | 3% | 2.2 min |
| all | 7,223 | 333 | 65% | 39% | 42% | 28 min |

All NEAs (SBDB periods, 2,180 objects) give the same picture: P < 2.2 h for 1% (H < 18), 3%, 16%, 63%, 89%, 93%, 100% (H >= 28); P < 10 min for 0%, 0%, 4%, 23%, 49%, 71%, 92%.

Delta-v < 6: 44 periods, 41 below 2.2 h (93%), 26 below 10 min (59%), 6 at an hour or longer. Delta-v < 5: 20 periods, all below 2.2 h, 15 below 10 min (75%), none at an hour or longer, median 2.8 min.

### 2.3 Correcting for objects whose period was not measured

A slow rotator watched for an hour yields no period, so the table above overstates fast rotation. Two surveys report all observed targets:

- **Alarcon, Licandro & Serra-Ricart 2026** (arXiv:2602.18562, accepted in A&A; abstract and HTML read today): 249 NEAs, H 22.0 to 29.8; 156 new fast rotators (P < 2.2 h), 87 below 10 min (the conclusions say 91). Fast-rotator share with all targets as denominator, lower bound (confirmed plus tentative) to upper bound (adding unknowns): **60.6 to 80.3%** for 22 < H < 24 (66 targets), **77.3 to 89.4%** for 24 < H < 26 (132), **94.1 to 96.1%** for H > 26 (51). Their LCDB and SsODNet reference values are 51.7%, 86.0%, 96.6%. Observing runs last 40 minutes to 2 hours. The first-round numbers are confirmed.
- **MANOS**, Thirouin+2016 and 2018, recomputed today from the VizieR tables: 228 distinct targets, 149 full periods, 33 lower limits, 46 flat lightcurves. Measured P < 2.2 h as a share of all targets: **11%** for H < 22 (4 of 35), **65%** for 22–24 (33 of 51), **70%** for 24–26 (59 of 84), **78%** for H >= 26 (45 of 58). Measured P < 10 min: 3%, 27%, 43%, 66%. Thirouin+2018 estimates that about half of the flat lightcurves are unresolved fast rotators and at least 43% are slow ones. Thirouin+2016 calls a target viable when delta-v (NHATS) is under 12 km/s and P exceeds 1 hour, and estimates that about 1,230 objects must be characterized to find 100. 84 MANOS photometry targets are in NHATS today, 61 with a full period.

### 2.4 Prior to use

| H | P(period < 2.2 h) | P(period < 10 min) |
|---|---|---|
| < 20 | about 0 | about 0 |
| 20–22 | 0.1 to 0.2 | under 0.05 |
| 22–24 | 0.5 to 0.8 | 0.2 to 0.3 |
| 24–26 | 0.7 to 0.9 | 0.4 to 0.5 |
| 26–28 | 0.8 to 0.97 | 0.65 to 0.75 |
| >= 28 | 0.8 to 1.0 | about 0.9 (29 objects) |

Lower ends come from all-target denominators, upper ends from measured periods. 75% of NHATS has H >= 25.

## 3. Labelled set for testing

Distinct NEAs with a spectral or colour-based class, matched through the SBDB NEA list. Tables (CfA VizieR mirror): Mahlke+2022 (1,165 NEAs), Sergeyev+2023 (1,812 classified, 467 "U"), Devogele+2019 MANOS (209), Marsset+2022 MITHNEOS (417), Navarro-Meza+2024 RATIR (73 above 50% probability, 160 below), Ieva+2020 compilation (1,080), Deshapriya+2023 compilation (1,578), Erasmus+2017 (25), Popescu+2019 (76), SBDB `spec_B`/`spec_T` (327).

| Label definition | H < 22 | 22 <= H < 25 | H >= 25 | All |
|---|---|---|---|---|
| **All NEAs**, population | 11,668 | 15,442 | 16,039 | 43,149 |
| Spectral class only | 1,079 | 185 | 139 | 1,403 |
| **Any class** (spectral, or colours with probability > 50%) | **2,318** | **308** | **161** | **2,787** |
| Also Sergeyev "U" and RATIR below 50% | 2,701 | 396 | 168 | 3,265 |
| **NHATS**, population | 202 | 1,620 | 5,401 | 7,223 |
| Spectral class only, tables | 72 | 51 | 74 | 197 |
| Any class, tables | 117 | 79 | 83 | 279 |
| **Any class, tables plus SsODNet cards** | **121** | **89** | **92** | **302** |
| **NHATS delta-v < 6**, population | 0 | 61 | 664 | 725 |
| Any class, tables plus cards | 0 | 7 | 18 | 25 |
| **NHATS delta-v < 5**, population | 0 | 12 | 273 | 285 |
| Any class, tables plus cards | 0 | 0 | 9 | 9 |

Notes:
- H is from SBDB; 9 NEAs (6 in NHATS) have no H.
- The NHATS figure of 302 is exact for the 1,394 objects fetched by criterion; 0 of 332 sampled remainder objects have a class (95% upper bound 67 more).
- SsODNet adds 23 classified NHATS objects that the tables lack (Sanchez+2024, Mommert+2016, Binzel+2019, single-object papers) and lacks 10 that the tables have. That is 8% on top of the tables, so the all-NEA labelled set is probably near 3,000; the first round's sampled SsODNet estimate was 2,950 (2,190 to 3,940).
- 1,597 of the 2,787 have two or more independent table sources, which is where label noise can be measured.
- Not parsed: Binzel+2019, Perna+2018, Sanchez+2024 and Lopez-Oquendo+2026 (122 small NEOs, arXiv:2608.28779, checked today) are not VizieR tables. Binzel and Perna are largely inside Mahlke+2022 and the two compilations.
- The LCDB class column is mostly assumed from orbit (Bennu is listed "S") and was not used.

## 4. Coverage table

Composition-relevant means the first-round definition: taxonomy, colours, albedo, density or mass, thermal inertia, radar circular-polarization ratio, phase function.

### 4.1 Delta-v < 6 and < 5: exact

Every one of the 726 objects was requested from SsODNet (713 cards, 13 unknown to SsODNet, as the first round reported; all cards dated 2026-09-14).

| Channel | dv < 6: SsODNet / tables / union | dv < 5: SsODNet / tables / union | First round (SsODNet) |
|---|---|---|---|
| Taxonomy | 24 / 16 / 25 | 9 / 4 / 9 | 24, 9 |
| Albedo | 7 / 6 / 10 | 3 / 0 / 3 | 7, 3 |
| Diameter | 7 / 7 / 11 | 3 / 1 / 4 | 7, 3 |
| Rotation period | 32 / 32 / 44 | 14 / 14 / 20 | 32, 14 |
| Colours | 17 / 14 / 19 | 3 / 4 / 4 | 17, 3 |
| Density | 5 / 0 / 5 | 4 / 0 / 4 | 5, 4 |
| Thermal inertia | 1 / – / 1 | 1 / – / 1 | 1, 1 |
| Radar polarization ratio | 4 / – / 4 | 2 / – / 2 | 4, 2 |
| Phase function | 1 / – / 1 | 1 / – / 1 | 1, 1 |
| Yarkovsky (SsODNet) against SBDB A2 | 7 / 23 / 23 | 3 / 11 / 11 | 7 vs 23, 3 vs 11 |
| Source regions | 53 / – / 53 | 11 / – / 11 | 53, 11 |
| **Any composition-relevant** | **34 / 22 / 37** | **13 / 5 / 14** | 34 / 21 / **37** and 13 / 5 / **14** |

Class mix of the 24 SsODNet-classified objects under 6 km/s: S 10, X 7, Q 2, M 2, V 1, K 1, U 1, identical to the first round. The 37 objects are the same list as in `catalogs.md` section 2.3. "Tables" here means the published tables of sections 1 and 3 plus SBDB; mine include NEOWISE years 4 to 7 and two taxonomy compilations that the first round did not use, hence 22 against 21.

### 4.2 All NHATS: exact floor plus stratified estimate

Known by name = union of the tables (exact for all 7,229) and 1,704 cards. Estimate = known part for the 1,394 objects fetched by criterion, plus the sample rate (332 random objects, seed 20261121) times the 5,835 objects that have no flag in any table.

| Channel | Tables only, exact | Known by name | Estimate (95% interval) | First round |
|---|---|---|---|---|
| Taxonomy | 279 | 302 | 302 (302 to 369) | SsODNet about 294 (240–361) |
| Albedo | 181 | 196 | 196 (196 to 263) | SsODNet about 122; SBDB 69 |
| Measured diameter | 182 | 197 | 197 (197 to 264) | SsODNet about 122; SBDB 70 |
| Rotation period | 306 | 333 | 416 (366 to 531) | 306; SsODNet about 272 |
| Colours | 230 | 246 | 246 (246 to 313) | SsODNet about 239 |
| Density | 3 | 15 | 15 (15 to 82) | about 20 (11–43) |
| Thermal inertia | – | 18 | 18 (18 to 85) | about 5 |
| Radar polarization ratio | – | 40 | 57 (42 to 137) | about 34 (19–62) |
| Phase function | – | 21 | 21 (21 to 88) | about 19 (9–44) |
| Yarkovsky in SsODNet | – | 132 | 149 (132 to 230) | about 96 (67–139) |
| Yarkovsky, SBDB A2 or SsODNet | 169 | 202 | 219 (204 to 299) | not given |
| Source regions (SsODNet) | – | 534 | 1,479 (1,264 to 1,737) | about 1,624 (1,498–1,758) |
| **Any composition-relevant** | **387** | **432** | **449 (434 to 529)** | **about 455 (390–540); floor 360** |

SsODNet alone: about 403 objects with any composition-relevant data (385 known), against the first round's 411. Three first-round point estimates sit below what I can now list by name: thermal inertia (18, not about 5), radar polarization ratio (at least 40, not about 34) and SsODNet Yarkovsky (at least 132, not about 96). None changes a conclusion. Of the 18 thermal inertias, 11 are derived from the Yarkovsky drift, 5 from thermophysical models and 2 from spacecraft; of the 15 densities, only 2 are binary-orbit masses and 3 come from spacecraft, the other 10 rest on solar radiation pressure or Yarkovsky plus an assumed size.

### 4.3 All NEAs: tables only (no ssoBFT)

Exact from the published tables and SBDB: taxonomy 2,787; colours 2,466; albedo 3,450; measured diameter 3,462; rotation period 2,180; A2 618; radar astrometry 1,110; any composition-relevant 5,136 (first round: 4,872 with fewer tables). Nothing seen contradicts the first round's sampled all-NEA SsODNet estimates; they could not be tightened.

## 5. NEOWISE gap

**SBDB's diameter field stopped ingesting NEOWISE results at the 2019 PDS compilation (through reactivation year 3).**

| NEOWISE table | NEAs in table | of which have an SBDB diameter |
|---|---|---|
| Mainzer+2011 (cryogenic) | 417 | 413 |
| Mainzer+2012 (3-band and post-cryogenic) | 114 | 114 |
| Mainzer+2014 (tiny NEOs) | 105 | 104 |
| Nugent+2015, Nugent+2016 (years 1, 2) | 199, 202 | 199, 202 |
| Masiero+2017 (year 3), Masiero+2018 (short-arc) | 170, 116 | 170, 116 |
| Masiero+2020a, year 4 / year 5 | 187 / 183 | 67 / 61 |
| Masiero+2020b (299 manually recovered) | 298 | 75 |
| Masiero+2021, year 6 / year 7 | 199 / 173 | 82 / 51 |

- 1,823 NEAs have a published NEOWISE fit (Masiero+2021 states 1,845 unique NEOs); 642 have no SBDB diameter. Of the 656 whose only fits are in the 2020 and 2021 papers, 19 have one.
- NHATS: 91 objects have a published NEOWISE fit, 62 have an SBDB diameter, **29 do not**: 138404, 163000, 163081, 363067, 380128, 453563, 467336, 471240, 483422, 489486, 501647, 512245, 612227, 613829, 674590, 875863, 2006 QQ23, 2010 EN44, 2016 YC8, 2016 YF8, 2017 BM3, 2017 DC36, 2018 WD1, 2019 CL2, 2019 ER1, 2019 FD, 2019 JU5, 2020 JU, 2020 UF2.
- SsODNet has ingested the 2020 and 2021 papers (cards cite Masiero+2020a, 2020b, 2021), and also He+2024, an independent NEATM analysis of WISE data for small NEAs.
- 62 of the 70 NHATS diameters in SBDB belong to objects in the NEOWISE tables (58 carry the identical value).

**Check of NHATS objects with NEOWISE astrometry (MPC code C51) and no SBDB diameter.** I queried MPC for the 70 brightest NHATS objects without an SBDB diameter, including the six first-round examples; 35 have C51 observations.

| Outcome | Count | Objects |
|---|---|---|
| Published NEOWISE fit exists, absent from SBDB | 14 | 2020 JU (203 detections; 0.15 to 0.16 km, Masiero+2021), 489486 (0.54 to 0.81 km), 163000 (0.45 km), 163081, 363067, 138404, 2006 QQ23, 512245, 875863, 612227, 453563, 380128, 483422, 467336 |
| No published fit; detections from 2021 or later, after the last fit paper | 8 | 895813, 139622, 98943, 163364, 329437, 613403, 523813, 350751 |
| No published fit; five or more detections, all before 2021 | 9 | 2015 DP155 (31 detections in 2018), 429389, 387816, 424482, 458452, 481394, 309214, 208023, 2017 AG21 |
| Fewer than five detections | 4 | 517103, 382758, 675603, 2021 AV4 |

11 of the 21 without a NEOWISE fit have a Spitzer diameter. Of the six first-round examples, three are already published (2020 JU, 489486, 163000) and three are not (2015 DP155, 429389, 895813).

No thermal-fit paper for reactivation years 8 to 11 turned up in two searches; the PDS bundle (version 2.0, 2019-03-11) covers through year 3.

Reading: the first round is right that SBDB lacks these diameters and wrong to treat that as a measure of what is unknown. If about 145 NHATS objects have NEOWISE astrometry (its estimate from 20 of 1,000), 91 already have published fits, so the pool for new fits is nearer 50 than 110. That figure inherits the first round's sampling error (95 to 225).

## 6. Verdicts on first-round claims

| Claim | Verdict | Evidence |
|---|---|---|
| 14 of 286 (delta-v < 5) have any composition-relevant measurement | Confirmed | 14, same objects |
| 37 of 726 (delta-v < 6) | Confirmed | 37, same objects; SsODNet alone 34 |
| About 455 of 7,226 (390 to 540) for all NHATS | Confirmed | 449 (434 to 529); 432 known by name |
| Exact floor of 360 from tables alone | Confirmed, low | 387 with NEOWISE years 4 to 7 and two compilations added |
| Taxonomy 9 / 24 / about 294 | Confirmed | 9 / 24 (25 with tables) / 302 |
| 18 per-source counts (SBDB, VizieR tables, Spitzer, LCDB, radar) | Confirmed | all equal |
| SsODNet delta-v < 6 column (13 channels) and the 13 objects unknown to SsODNet | Confirmed | all equal |
| ssoBFT served under 10 kB/s | Confirmed | 1.75 kB/s, then dropped |
| Rotation period for 306 / 32 / 14 | Partly | true of SBDB; union with SsODNet is about 416 / 44 / 20 |
| SsODNet thermal inertia about 5; polarization ratio about 34; Yarkovsky about 96 in NHATS | Refuted as point values | at least 18, 40 and 132 |
| Alarcon+2026: 249 NEAs, 156 new fast rotators, 87 under 10 min | Confirmed | abstract and Table 1 |
| SsODNet lacks most Spitzer NEOSurvey/NEOLegacy results | Confirmed | 72 of 112 NHATS Spitzer objects have no card diameter |
| 2010 NU71 mis-association | Confirmed | 1.126 km at H 22.7 in SBDB and SsODNet |
| new-surveys: most NHATS objects with C51 astrometry have no SBDB diameter (15 of 20); 2020 JU | Partly | plausible (a third to three quarters), but 14 of 35 checked, including 2020 JU, already have published fits |
| new-surveys: published fits stop at year 7 | Confirmed as far as searchable | no later paper found |
| NEOWISE years 4 to 7 "paper tables on VizieR" | Refuted (CfA mirror) | keyword search lists nothing after Masiero+2018, though the mirror holds 2025 catalogues; journal tables are at content.cld.iop.org |

## 7. Not reached, and limits

- No ssoBFT, so no exact all-NEA SsODNet counts and no all-NEA labelled-set figure that includes SsODNet-only classes.
- MP3C, Gaia DR3 and ESA NEOCC were not fetched again. They were not needed to reproduce 37 and 14.
- Binzel+2019, Perna+2018, Sanchez+2024 and Lopez-Oquendo+2026 tables were not parsed.
- Radar and thermal method labels are SsODNet's; I did not open the underlying papers. Alarcon+2026 and the Thirouin papers were read through a summarizing fetch of the arXiv pages, the MANOS fractions were computed from the tables.
- The C51 check used the 70 brightest NHATS objects without an SBDB diameter, not a random sample; IRSA was not queried.
- The remainder estimate rests on 332 sampled objects: a channel with zero sample hits has a 95% upper bound of 67 more objects.
- SsODNet cards are dated 2026-09-14; 22 of 1,726 requested NHATS objects are unknown to it. NHATS itself gained 24 objects first observed since 2026-11-10.

## 8. Files

Paths below are relative to `data/research/`.

- Scripts, `scripts/`: `cx_lib.py` (matching), `cx_fetch_vizier.sh`, `cx_vizier_find.sh`, `cx_fetch_cards_list.py`, `cx_card_list.py`, `cx_card_list3.py`, `cx_card_list4.py`, `cx_cards.py`, `cx_sizes.py`, `cx_sizes2.py`, `cx_neowise_extra.py`, `cx_neowise_gap.py`, `cx_c51_census.py`, `cx_spin.py`, `cx_manos_spin.py`, `cx_labels.py`, `cx_union.py`, `cx_replicate.py`, `cx_local_basics.py`.
- Downloads, `dl/coverage-exact/`: `cards/` (1,704 ssoCards and `_status.tsv`), `vizier/` (19 catalogues), `neowise_extra/` (Masiero 2020a, 2020b, 2021 tables), `spitzer/`, `lcdb/`, `mpc/c51_census.jsonl`, `jpl/`.
- Results, `dl/coverage-exact/out/`: `union_report.txt`, `sizes_report.txt`, `spin_report.txt`, `labels_report.txt`, `neowise_gap_report.txt`, `cards_summary.txt`; per-object tables `sizes_nhats.tsv`, `cards_flags.json`, `labels.json`, `table_flags.json`, `spin_periods.json` one level up.

## Sources

- SsODNet ssoCard API: https://ssp.imcce.fr/webservices/ssodnet/api/ssocard/ ; bulk table https://ssp.imcce.fr/data/ssoBFT-latest_Asteroid.parquet
- CfA VizieR mirror: https://vizier.cfa.harvard.edu/viz-bin/asu-tsv (J/ApJ/743/156, J/ApJ/760/L12, J/ApJ/784/110, J/ApJ/814/117, J/AJ/152/63, J/AJ/154/168, J/AJ/156/60, J/A+A/665/A26, J/A+A/679/A148, J/AJ/158/196, J/AJ/163/165, J/AJ/167/163, J/A+A/644/A23, J/A+A/674/A50, J/AJ/154/162, J/A+A/627/A124, J/AJ/152/163, J/ApJS/239/4, J/AJ/169/256)
- Masiero+2020a, PSJ 1, 5, doi:10.3847/PSJ/ab7820: https://content.cld.iop.org/journals/2632-3338/1/1/5/revision1/psjab7820t1_mrt.txt (and t3)
- Masiero+2020b, PSJ 1, 9, doi:10.3847/PSJ/ab8638: https://content.cld.iop.org/journals/2632-3338/1/1/9/revision1/psjab8638t1_mrt.txt
- Masiero+2021, PSJ 2, 162, doi:10.3847/PSJ/ac15fb: https://content.cld.iop.org/journals/2632-3338/2/4/162/revision1/psjac15fbt1_mrt.txt (and t3); https://arxiv.org/abs/2107.07481
- NEOWISE PDS bundle page: https://sbn.psi.edu/pds/resource/neowisediam.html
- Spitzer NEO table: https://raw.githubusercontent.com/mommermi/spitzerneos/master/spitzerneos.csv
- LCDB: https://minplanobs.org/MPInfo/datazips/LCLIST_PUB_CURRENT.zip
- MPC observations API: https://data.minorplanetcenter.net/api/get-obs
- JPL SBDB API (two single-object lookups): https://ssd-api.jpl.nasa.gov/sbdb.api
- Alarcon, Licandro & Serra-Ricart 2026: https://arxiv.org/abs/2602.18562
- Thirouin+2016: https://arxiv.org/abs/1607.03517 ; Thirouin+2018: https://arxiv.org/abs/1809.03549
- Lopez-Oquendo+2026: https://arxiv.org/abs/2608.28779
- Crossref (DOI lookup): https://api.crossref.org/works
