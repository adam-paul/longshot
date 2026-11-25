# New and underused public survey data for characterizing NEAs: what is actually public on 2026-11-20

Researcher brief: area 4 of the prospect-catalog plan (new or underused public surveys). Written 2026-11-20.
Every claim carries a status: **[V]** verified today (source read or number computed in this session), **[R]** recalled from memory and not re-checked, **[U]** uncertain or could not be verified.

## 0. Bottom line

1. **None of the new surveys reaches the typical NHATS object.** The NHATS list holds 7,226 objects today with median H = 26.2 [V]. In a random sample of 1,000 of them, the median object has 37 astrometric observations over a 12.2-day arc; 75% have arcs under 30 days [V, computed from MPC]. An object that was only ever visible for two weeks is not in SPHEREx, Gaia, Euclid, TESS or NEOWISE, and no future release of those archives changes that.
   - SPHEREx: 0 of 328 random NHATS objects were brighter than predicted V = 18 in any SPHEREx frame covering their position (May 2025 to Oct 2026); 1 of 328 was brighter than V = 19 [V, computed with IRSA MOST]. SPHEREx per-channel 5-sigma depth is about AB 18.8 to 19 for a static source [V, Ivezic et al. 2022].
   - Gaia DR3: 445 NEAs in total, 104 with reflectance spectra, faintest H = 20.3; 8 NHATS objects, 3 with spectra [V, computed from Gaia TAP + SBDB]. DR4 will have 2.8 times as many objects overall but the same magnitude limit.
   - Rubin: 5 of 1,000 sampled NHATS objects have Rubin (X05) observations at the MPC today [V]. Rubin is the only one of these surveys deep enough (single visit r about 24) to reach decameter NEAs routinely, but the LSST started 2026-06-29 and the observatory was then offline from 2026-07-15 to 2026-10-27 [V].
2. **So the surveys matter in three narrower ways**: (a) Rubin multi-band photometry, already world-public through the MPC, for a small but fast-growing set of small NEAs; (b) SPHEREx and NEOWISE for the larger NEAs (H < 22), which include roughly 10 to 20 of the 199 NHATS objects with H < 22 and a few hundred NEAs overall, giving validation objects with real spectra and albedos; (c) Gaia DR4 (2 December 2026) as the calibration set for the orbit-to-source-region-to-taxonomy prior, not as NEA data.
3. **The clearest unexploited gap is SPHEREx on NEAs.** There is no public SPHEREx solar-system product; the official Solar System legacy catalog is scheduled for **May 2028** [V]; the only SPHEREx asteroid spectrum shown so far is 171 Ophelia in an LPSC 2026 abstract [V]. The images, a moving-object search tool and a cutout service are all public and worked today from a script [V]. I estimate about 200 NEAs with H < 20 (and about 10 NHATS objects) passed through SPHEREx frames brighter than V = 19 in the first 17 months [V, extrapolated from a 213-object sample].
4. **The cheapest real gain is NEOWISE.** About 2% of NHATS objects (20 of 1,000 sampled) have NEOWISE astrometry at the MPC, and 15 of those 20 have no diameter or albedo in JPL SBDB [V]. The final NEOWISE release (14 Nov 2024) is public; published thermal fits stop at reactivation year 7 (data to Dec 2020) as far as I could find [V for the search, U for completeness].

## 1. The target population, measured today

All numbers computed in this session from public APIs; files are in the download directory (section 12).

| Quantity | Value | Source |
|---|---|---|
| NHATS objects | 7,226 | JPL NHATS API |
| NHATS median H | 26.2 (range 15.7 to 34.1) | JPL NHATS API |
| NHATS with H < 22 | 199 | JPL NHATS API |
| NEAs in SBDB | 43,151 | JPL SBDB query API |
| NEAs with H < 20 | 4,810 | SBDB |
| NEAs with any taxonomy in SBDB (spec_B or spec_T) | 327 | SBDB |
| NHATS with taxonomy in SBDB | 23 | SBDB |
| NHATS with albedo / diameter in SBDB | 69 / 70 | SBDB |
| NHATS with rotation period in SBDB | 306 | SBDB |

MPC observation census, random sample of 1,000 NHATS objects (seed 42), via `https://data.minorplanetcenter.net/api/get-obs`:

| Quantity | Value |
|---|---|
| Median observations per object | 37 (mean 66) |
| Median arc | 12.2 days; 74.9% under 30 d; 11.6% over 1 yr |
| Objects with Catalina observations | 81.9% |
| Pan-STARRS F51/F52 | 51.9% (mostly w band; median 6 obs) |
| Mauna Kea follow-up (T09, 568, T12, T14) | 24.8% |
| ATLAS (T05, T08, M22, W68, R17) | 11.9% (median 8 obs; 4.6% have 10 or more) |
| ZTF (I41) | 8.1% (median 4 obs; 1.1% have 10 or more) |
| NEOWISE (C51) | 2.0% |
| DECam (W84) | 1.9% |
| Rubin (X05) | 0.5% (5 objects) |
| SkyMapper (Q55), Gaia (258) | 0 of 1,000 |
| Objects with photometry reported in 2 or more of u, g, r, i, z, y | 6.5% |

Caveat: MPC-reported magnitudes are of mixed quality (many are unfiltered and tied to Gaia G; 0.1 to 0.5 mag errors are common). The census shows where images exist, not where good photometry exists. Rubin is the exception: its ADES records carry three-decimal magnitudes with `rmsMag` and a true filter name.

## 2. SPHEREx

### What is public [V]
- Launched 11 March 2025; survey started 1 to 2 May 2025; 102 channels, 0.75 to 5.0 micron, R = 41 to 135, 6.2 arcsec pixels, 113.6 s exposures, low-Earth Sun-synchronous orbit looking near 90 degrees solar elongation.
- **Level 2 spectral images** are released weekly ("Quick Release"), nominally within about two months of acquisition. QR1 (July 2025) is retired; QR2 (Oct 2025) is superseded and downloadable until Feb 2027; QR3 (weekly since Sept 2026) covers surveys 3 and 4.
- **DR1 was released 12 November 2026**: all survey 1 and 2 images reprocessed with the QR3 pipeline, plus the first **All-Sky Cube** (102 channels, 12,288 sky tiles per one secondary source). DOIs 10.26131/IRSA678 and IRSA679. DR1 plus QR3 are a uniformly processed set.
- Planned: High Reliability Source Catalog V1 in August 2027; DR2 in December 2027; Deep-field mosaics, ices, redshift and **the three legacy catalogs (stars/brown dwarfs, galaxy clusters, Solar System) in May 2028** (Bock et al. 2025, Table 4). The Solar System Object Catalog (SSOC) is curated at KASI; it will only cover objects with orbits known during the prime mission and is to go to IRSA and PDS.
- **No solar-system product of any kind is public today.** The IRSA SPHEREx page lists none. The IRSA Spectrophotometry Tool does forced photometry at fixed sky positions only.
- Tools that work for moving objects today: **IRSA MOST** has a `spherex` catalog and returns, for a named object, every Level 2 detector image that covers its predicted position, with predicted V, distances and phase [V, used]. The IBE cutout service works on Level 2 files (`...fits?center=RA,DECdeg&size=0.02deg`) [V, used]. Data are also in AWS S3.
- The pipeline's source mask already uses "the known Solar System object catalog", so pixels near known SSOs brighter than AB 19 are flagged in the FLAGS extension [V, Explanatory Supplement].

### Data volume [V unless marked]
- One Level 2 detector image is 65.4 MB (2040 x 2040 pixels; IMAGE, FLAGS, VARIANCE, ZODI, ePSF and WCS-WAVE extensions).
- A 12 x 12 pixel cutout is 3.95 MB, almost all of it the ePSF table. A few hundred frames per object is about 1 to 4 GB per object.
- The mission paper gives 20 GB/day science data volume. The full Level 2 archive must be of order 100 TB (about 3,600 detector images per day times 65 MB) [R/estimate]. A one-workstation project must work from cutouts, not bulk images.
- Eros: 954 detector images cover its position between 2025-06-25 and 2026-06-25, in three visibility windows, at predicted V = 11.0 to 14.2 [V].

### Sensitivity and what it means for NEAs
- Ivezic et al. 2022: mean 5-sigma depth per spectral element about 18.8 AB below 2.42 micron and 19.0 to 17.3 from 2.42 to 5 micron; forecast about 6,000 asteroids with SNR of 5 or more per element at 2.4 micron in a single visit (about 14,000 if four visits are co-added) and close to 100,000 with usable photometry. Their forecast table is main belt, Trojans and TNOs; NEAs get one example figure and no count [V].
- Lisse and Bauer 2024: limiting magnitude K about 19; a complete spectrum takes about 2 weeks to build; each object is seen in 3 to 5 epochs over two years; trailing becomes noticeable above about 80 arcsec/hour; objects faster than about 1.2 degrees/day "are likely to be identified but not fully characterized" by the forced-photometry pipeline [V].
- For NEAs the thermal tail takes over below 3 micron (Ivezic Fig. 10), so the 2.7 to 3.1 micron hydration band sits on a steep thermal slope and needs a thermal model to recover. What SPHEREx gives most robustly for an NEA is the 0.75 to 2.4 micron reflectance (1 and 2 micron silicate bands, slope) plus a 3.5 to 5 micron thermal flux that constrains size and albedo.

### How many NEAs are reachable (computed today with MOST)
Predicted V of the object in each SPHEREx frame covering its position, 2025-05-01 to about 2026-10-16:

| Sample | N | any frame | V < 18 | V < 19 | V < 20 | V < 21 |
|---|---|---|---|---|---|---|
| NHATS, random | 328 | 61.6% | 0 | 1 (0.3%) | 4 (1.2%) | 8 (2.4%) |
| NHATS, H < 22 (182 of 199 resolved) | 182 | 61.0% | 4 (2.2%) | 10 (5.5%) | 19 (10.4%) | 32 (17.6%) |
| All NEAs with H < 20, random | 213 | 93.4% | 6 (2.8%) | 9 (4.2%) | 26 (12.2%) | 50 (23.5%) |

- Scaling the last row to the 4,810 NEAs with H < 20: about 200 NEAs brighter than V = 19 in at least one frame (rough 95% range 90 to 380), about 590 brighter than V = 20, in the first 17 months. Most of those have 10 or more such frames.
- Caveats: MOST's header shows magnitude parameters "H, 0.00", so it may use G = 0 and predict about 0.3 to 0.5 mag too faint at phase 60 to 90 degrees; read the table one half-bin brighter. Predicted V is not detected flux: it ignores trailing, rotation and colour. Binning 102 channels into about 6 bands gains roughly 1.5 mag, which is what makes the V < 20 column usable.
- NHATS objects with the best SPHEREx coverage (pilot targets): (424482) V = 14.2 on 2025-06-04 at 0.024 au; (3361) Orpheus V = 15.4 on 2025-11-17; (612356) V = 16.5; (884793) 172 frames at V < 18; (387733) 76 frames at V < 19; (837134), (612227), (433953), (350523), (138175).
- A 9 m NHATS object can appear (2026 MA1, H 27.2, V = 18.8 at 0.005 au on 2026-06-19, 8 frames), but at that distance it moves tens of arcsec per minute and trails across many pixels and wavelengths.

### What has been published [V]
- Refereed solar-system SPHEREx papers so far are about interstellar comet 3I/ATLAS (water ice absorption, CO2 coma; Lisse et al. 2025, 2026).
- LPSC 2026 abstract 1833 (Lisse et al.): first reductions for 3I/ATLAS, **(171) Ophelia** and the zodiacal cloud. Ophelia (130 km C type) shows "a hint of a 2.7 um absorption and strong thermal emission beyond 3.3 um" after correcting with SOLO light curves. That is the only SPHEREx asteroid spectrum, and the only 3-micron claim, I could find.
- SOLO (arXiv:2602.08037): a dedicated ground light-curve system at Sierra Remote Observatories built to give about 1,000 calibrated asteroid light curves per year for the SSOC. The team considers rotation correction a hard enough problem to build a telescope for it.
- An arXiv API search for SPHEREx with asteroid terms on 2026-11-20 returns no asteroid-spectrum paper.
- NASA Space Apps 2026 (14 to 15 November 2026) ran a "Planet X and SPHEREx" challenge; several GitHub hackathon repos claim per-asteroid spectral extraction. Hackathon quality, but it shows the idea is in the open.
- Related code: SPIFF (Gagne; SPHEREx photometry for fast proper-motion stars), Xcavation (forced photometry on QR2), kete (Dahlen et al. 2025; predicts known minor bodies in survey images; a dependency of the SPHEREx pipeline).

### How hard to do ourselves
Moderate. Steps: MOST lookup per object; cutouts; Horizons position at mid-exposure from the spacecraft's position (parallax matters for close NEAs; the header has spacecraft state vectors); PSF or aperture photometry on a 6.2 arcsec, undersampled PSF using the supplied ePSF; wavelength at the object's pixel from WCS-WAVE; background from the same sky in other frames (the asteroid has moved on); reject frames where a star sits under the object; correct for distance, phase and rotation; fit reflectance plus thermal model. The first four are routine. Background confusion at 6 arcsec and rotation/phase correction without a light curve are the real difficulties. Validation is easy: Eros, Ganymed, Phaethon and many main-belt objects with ground 0.8 to 4 micron spectra are in the same data.

## 3. Gaia DR4 and the Focused Product Release

- **DR4 is scheduled for 2 December 2026, 12:00 CET**; the ESA archive is down from 25 November for the switch [V, ESA news 2026-10-08]. It covers 66 months (25 July 2014 to 20 January 2020). Total size about 400 TB against 10 TB for DR3 [V].
- Solar-system tables (ESA DR4 content page, last updated 14 Sept 2026) [V]:
  - `sso_source`: 436,551 objects (DR3: 158,152).
  - `sso_observation`: 60,542,356 rows, 13 GB, one row per CCD transit, epoch astrometry and photometry.
  - `sso_reflectance_spectrum`: 436,551 rows, 13 MB, mean BP/RP reflectance spectra (DR3: 60,518 objects).
  - `sso_xp_epoch_spectrum`: 8,656,146 epoch BP/RP spectra, 6.9 GB, via DataLink. New in DR4.
  - `sso_alerts`: 22,476 rows.
  - Performance-verification tables: `asteroid_family_proper_elements`, `astrometric_satellite_detections`, `astrometric_satellite_phys_model`, `onboard_sso_af_detection`.
- DR4 papers listed by ESA [V]: "Dynamical and physical properties of small bodies from epoch astrometry"; "Asteroid families as seen by Gaia"; "Reflectance spectra and taxonomy of Solar System small bodies"; "Physical properties of small Solar System bodies from G, BP, and RP photometry". No titles with Yarkovsky or NEA in them; no arXiv links yet. More than 60 papers are expected with the release.
- **The NEA count in DR4 is not published.** DR3 measured today: 445 NEAs, 104 with reflectance spectra, median H 16.8, faintest H 20.3; 8 NHATS objects (1943 Anteros, 363505, 35107, 226554, 163000, 10302, 136618, 162173 Ryugu), 3 with spectra [V]. A reasonable guess for DR4 is 1,000 to 1,500 NEAs [U].
- **FPR (10 October 2023)**: 66-month astrometry for the DR3 object set, 156,823 objects (156,762 orbits), orbit precision on average 20 times better than DR3 [V]. This is the dataset behind Dziadura et al. 2023, "The Yarkovsky effect and bulk density of near-Earth asteroids from Gaia DR3" (446 NEAs) [V for existence, R for content].
- Gap for this project: essentially none of the NHATS list is in Gaia. The value is (i) the 7-fold larger reflectance sample for building the family and source-region taxonomy prior down to smaller main-belt sizes, (ii) the DPAC family table, (iii) epoch astrometry for Yarkovsky on the larger NEAs. All three will be worked hard by the DPAC papers and a large community in December; novelty has a short shelf life.
- DR5: not before the end of 2030 [V].

## 4. Vera C. Rubin Observatory / LSST

### Status [V, RTN-011 v10 dated 2026-11-19, and Rubin community forum]
- Rubin Operations began 2025-10-25. **The LSST was formally declared started on 2026-06-29.**
- An extreme weather event took the observatory offline for about 3.5 months, **2026-07-15 to 2026-10-27**. Back on sky 29 Oct; back to the LSST 9 Nov; on 15 Nov the camera was shut down after a coolant-system fault and was still down on 17 Nov with no restart date.
- **DR1: expectation window July to November 2028** (about 24 months after survey start), and its content is "under discussion" because of the lost time. The old six-month DR1 was dropped.
- DP1 (30 June 2025; LSSTComCam, about 2,000 exposures, 7 small fields): SSObject has 431 objects (93 new), SSSource 5,988 rows.
- DP2: "Early DP2" released 27 July 2026 (LSSTCam April 2025 to January 2026; coadds over about 3,000 deg2, single-epoch catalogs over about 15,000 deg2); complete DP2 due 15 December 2026. In both DP1 and DP2 the solar-system tables come from cross-matching DiaSources to known MPC orbits, not from the full Solar System Processing pipeline.
- **DP1 and DP2 are for data-rights holders only** (US and Chile scientists, named international in-kind members).
- **Alerts are world-public with no proprietary period.** They started 2026-02-24 (about 800,000 on the first night) and go to seven full-stream brokers: ALeRCE, AMPEL, ANTARES, Babamul, Fink, Lasair, Pitt-Google; SNAPS and POI are downstream. Alerts are produced only where templates exist. Moving-object alert packets may lack history, and phase-curve parameters are null for now.
- **Prompt Products Database (PPDB)**: delivery target 2026-11-30, holding all alert data from about September 2025 plus `mpc_orbits`, `SSObject`, `SSSource`. "Access to the PPDB service requires data rights, but the data are public. Users without data rights can access the same data via the alert brokers."
- **MPC**: "Solar System discoveries will be reported to the Minor Planet Center on an ad-hoc basis during Early Operations." Daily automated submission has not started. Rubin's data policy says alerts and solar-system data at the MPC are public; the observatory code is X05.
- Pixel data have an 80-hour embargo and then are for data-rights holders.

### What Rubin has delivered on asteroids [V]
- First Look (June 2025): 2,104 new asteroids including 7 NEOs.
- April 2026 MPC batch: over 11,000 new asteroids (about 600 later linked to earlier objects), 33 new NEOs, about one million observations including more than 80,000 known objects, from about six weeks of data.
- First Look light curves and colours (ApJL 2026): 76 objects, 19 superfast rotators, 3 under 5 minutes.
- arXiv:2609.29841 (Carruba et al., Sept 2026): periods, griz colours and taxonomies from Science Validation data, described as preliminary.
- arXiv:2610.07584 (Oct 2026): DP2 solar-system catalog, 66 super-fast rotators, two bodies over 2 km with periods near 5 minutes.
- Kurlander et al. 2025 yield forecast: 127,000 NEOs, 5.09 million main-belt asteroids over ten years, with griz colours and light curves; about 70% of main-belt discoveries in the first two years.
- I found no paper using Rubin photometry for NEA composition.

### What the public can use today (tested)
The MPC observation API returns Rubin records with filter, magnitude to 0.001, `rmsMag`, and astrometric uncertainties. Example: Rubin discovery 2025 MN45 has 580 X05 observations (Lr 205, Lg 119, Li 113, plus g, r, i, u) over 2025-04-22 to 2025-05-04 [V].

NHATS objects with Rubin data in the 1,000-object sample [V]:

| Object | H | Rubin observations | Dates |
|---|---|---|---|
| 2025 GH1 | 25.5 | 102 (u 52, r 29, i 12, g 9) | 2025-05-03 to 2025-06-21 |
| (847431) | 21.5 | 18 (r 7, i 6, z 5) | 2025-07-04 to 2025-08-28 |
| 2025 OU2 | 26.1 | 4 (z 2, i 1, r 1) | 2025-06-21 to 2025-09-14 |
| 2025 XP2 | 27.8 | 3 (r 2, z 1) | 2025-12-21 |
| 2019 UY3 | 23.9 | 2 (g) | 2025-07-22 |

That is 0.5% of the sample, so about 35 NHATS objects overall (Poisson range roughly 10 to 80), nearly all from commissioning data. A full pull of all 7,226 NHATS objects from the MPC API takes about 1.5 hours with four polite workers (measured: 1,000 objects in about 12 minutes).

### Gap and limits
- The gap: nobody has yet turned Rubin's public MPC photometry into colours for mission-accessible NEAs. It costs almost nothing to do and to keep updated.
- Limits: colours come from non-simultaneous filters, and small NEAs rotate fast with large amplitudes. The MANOS colour paper (arXiv:2603.15872) shows that uncorrected light-curve variation can change individual classifications and bias ensembles. Visible colours separate S, C, X and V complexes at best; they say nothing about hydration. And the flow of data depends on an observatory that has had about three weeks of survey observing so far.

## 5. Euclid

- Q1 (19 March 2025): 63 deg2 [V]. No Q1 solar-system paper found in the arXiv listing.
- **"DR1-Foundation" released 12 November 2026**: about 1,900 deg2 of the Wide Survey (14% of the final area), observations from spring 2024 to spring 2025, 1.7 million GB. Full DR1 with clusters and weak lensing is due mid-2027 (one source says June 2027) [V].
- No solar-system catalogue, flags or SSO paper appear on the DR1 pages (27 DR1 papers listed, none on moving objects) [V].
- Published Euclid SSO work [V]: a detection pipeline on simulated VIS images (arXiv:2501.05023; expects more than 10^5 SSOs even though the survey stays more than 15 degrees from the ecliptic); "Asteroid rotation periods from the Euclid Ecliptic Survey" (arXiv:2604.25652; a calibration-phase campaign on 23 to 31 December 2023; 23,000 observations of 2,321 known asteroids; 889 periods; open catalogue). An EPSC-DPS 2025 abstract reports that 47% of streaks in that dataset are unknown objects, including some NEAs.
- No NISP Y, J, H colour or taxonomy result for asteroids has been published as far as I could find [V for the search].
- Relevance to NEAs: low. The survey avoids the ecliptic, each field is seen once, fast movers trail in the 565 s VIS exposures [R for exposure time], and there is no SSO product. Not worth building on for this project.

## 6. NEOWISE

- Survey operations ended **1 August 2024**; decommissioned 8 August 2024; **final data release 14 November 2024** [V].
- Final release content: 26,888,166 single-exposure image sets; 199,762,421,143 source detections; 21.3 sky coverages over 10.6 years; a "known solar system object possible association list" (predictions, explicitly not vetted detections); MPC-confirmed tracklets with **1,632,566 infrared detections of 44,597 objects** in the reactivation mission [V].
- Published diameters and albedos: PDS "NEOWISE Diameters and Albedos V2.0" (2019) covers cryogenic through reactivation year 3; Masiero et al. papers cover years 4 to 5 (2020; 189 NEOs) and years 6 to 7 (2021). A DPS 2024 abstract (McFadden, Mainzer, Masiero et al.) describes updated main-belt fits. **I found no publication of thermal fits for reactivation years 8 to 11 (December 2020 to July 2024)** in web or arXiv author searches [V for the search; U whether an in-press paper exists].
- Myers et al. 2025 (arXiv:2504.00905): practical processing and colour-correction lessons for NEA data from three objects; "nearly half of the available observations should be discarded after proper processing". Myers et al. 2024 (arXiv:2410.24101) found inconsistencies between simple thermal model results from SpeX and NEOWISE for NEAs.
- "Dual-band albedo" work continues on main-belt families (arXiv:2605.23347; the ratio of visible to infrared albedo as a surface-freshness tracer in 154 families). The 3.4 micron albedo ratio as a taxonomy proxy dates from Mainzer et al. 2011 and needs a W1 detection dominated by reflected light, which small NEAs near 1 au rarely give [R].
- **NHATS reach (computed)**: 20 of 1,000 sampled NHATS objects have C51 observations at the MPC, so about 145 of 7,226. Only 5 of those 20 have a diameter in SBDB. Examples without one: 2020 JU (H 20.8, 203 NEOWISE observations), (489486) (58), 2015 DP155 (31), (429389) (13), (163000) (10), (895813) (10). SBDB is not a complete index of published NEOWISE results, so each must be checked against the Masiero tables and the IRSA "NEOWISE Small Bodies Catalog" before being called new.
- Tractability: high. MOST supports every NEOWISE year; the single-exposure source table can be queried per object; NEATM fitting is standard and open-source (ATM, kete).
- unWISE and CatWISE are static-sky coadds and catalogs that remove or smear moving objects; I found no asteroid-mining result from them. They are useful only as background maps for forced photometry [R].

## 7. ZTF and ATLAS

- ZTF: DR24 released 22 January 2026 (public data March 2018 to 22 October 2025); DR25 due 20 January 2027; "ZTF 3 runs between Jan 1, 2025 and Dec 31, 2026" [V]. No solar-system data product is listed in the releases; moving-object photometry lives in the alert stream (via brokers) and in MPC submissions (I41, with g, r, i).
- Fink SSO (Carry et al. 2024, arXiv:2403.20179): sHG1G2 phase-curve fits for 122,675 objects from 13.2 million ZTF g and r observations, with programmatic access [V from search result; the Fink API timed out from this machine today, so access is unverified].
- SNAPS (Trilling et al. 2023): SNAPShot1 has 5,458,459 observations of 31,693 asteroids from ZTF, July 2018 to May 2020; now a downstream Rubin broker [V from search result].
- IRSA MOST supports ZTF, but one NHATS object over 7.5 years did not return within 240 s today [V]. Use kete or the brokers for bulk work.
- ATLAS: SSCAT-2 phase curves for 301,272 asteroids in orange and 280,953 in cyan, **including 771 NEAs** (arXiv:2503.05412) [V]. The public forced-photometry server accepts a minor-planet designation and does PSF photometry on every archival exposure covering the predicted position; a typical main-belt query takes about 20 minutes [V from search results]. I could not confirm a public download location for SSCAT-2 [U].
- CATCH (PDS Small Bodies Node) searches ATLAS images from all four sites by moving-target name, with cutouts and an API [V].
- NHATS reach: 11.9% have ATLAS observations and 8.1% ZTF, but the median counts are 8 and 4. Only 4.6% and 1.1% have 10 or more points, too few for a phase curve; a single c minus o or g minus r colour at one epoch is all that most would give.

## 8. TESS and Kepler/K2

- TESS: Pal et al. 2020 (TSSYS-DR1, 9,912 light curves, bright main-belt and Trojans); McNeill et al. 2023 (3,492 reliable periods); Vavilov and Carry 2025 (periods for 4,521 asteroids from TSSYS-DR1) [V from search results].
- 21 arcsec pixels, 30-minute (later 10-minute and 200-second) full-frame cadence and a limit near V = 19 to 20 mean main-belt work only. I found no TESS or K2 NEA light-curve catalogue [V for the search]. Rotation periods are not composition. Not a channel for this project.

## 9. DECam, DES, Pan-STARRS, SkyMapper, HSC, VST, UKIRT: archival serendipity

- **Already done for NEAs**: Sergeyev et al. 2023 (A&A 679, A148) combined SDSS, SkyMapper, Gaia reflectance spectra and ground compilations into taxonomic classes for **7,401 NEOs**, with new SDSS photometry for 470 NEOs and **42 mission-accessible NEOs** classified, plus source regions [V]. This is the direct prior art for "fuse existing colours for planet-crossers".
- SkyMapper DR3: 205,515 known SSOs, 880,528 observations, 97% complete to V = 18 (Sergeyev et al. 2022) [V]. Zero NHATS objects in my sample have SkyMapper astrometry at the MPC.
- NOIRLab Source Catalog: CANFind found 527,055 tracklets in NSC DR1 (Fasbender and Nidever 2021); a NOIRLab talk gives 628,211 tracklets and 4.68 million moving-object measurements in 7 filters for DR2; the colour paper was "in preparation" in 2024 [V from search results]. There is also a DECam Asteroid Database at Astro Data Lab from the DECam NEO Survey.
- DES: Jupiter Trojan colours for 547 L5 objects (Pan et al. 2022). No NEA colour catalogue found [V].
- VST/OmegaCAM: Saifollahi et al. 2023 recovered 196 NEO appearances out of 968 predicted in the ESO archive; "detectability 0.05 per NEO"; 20% automatic recovery; 0.1 mag photometry; three objects removed from the risk list [V]. This is the best measured estimate of what archival mining yields.
- UKIRT: 31 NEOs with serendipitous J and K detections in the UKIRT Hemisphere Survey (2024) [V].
- Pan-STARRS: 52% of sampled NHATS objects have F51/F52 astrometry, almost all in the wide w band (one filter, no colour). CATCH indexes 17.6 million PS1 DR2 skycell images (2009 to 2015), 12.6 million SkyMapper DR4 images, Catalina, Spacewatch, LONEOS, NEAT and ATLAS [V].
- HSC: no NEA colour product found; not searched in depth [U].
- Verdict: for NHATS-class objects the windows are days to weeks around discovery, the discovery surveys are single-band, and the multi-band archives rarely happened to point there. Saifollahi's 5% per-object detectability is the realistic expectation. The multi-band part (SDSS, SkyMapper) has been mined. Low priority.

## 10. JWST and HST archives; NEO Surveyor; NEOMIR

- JWST on small NEAs: 2024 YR4 only, as far as I found. Diameter 60 +/- 7 m, albedo 8 to 18% from NIRCam plus MIRI (March 2025); recovered again on 26 February 2026 at V about 30.5, ruling out a 2032 lunar impact (arXiv:2605.20498) [V].
- JWST serendipity: 138 decameter main-belt asteroids in about 10,000 archival MIRI images by synthetic tracking (Burdanov et al. 2025, Nature 638) [V]. These are unlinked detections with no orbits.
- **Dark comets: I found no JWST result and could not confirm an approved programme.** 1998 KY26 cannot be observed by JWST between March 2025 and November 2027 (Nature Communications 2025, s41467-025-63697-4; revised diameter 11 +/- 2 m). A November 2026 thermal study (arXiv:2611.10275) argues volatiles are unlikely to survive in KY26. Hayabusa2 arrives in 2031 [V].
- HST: Hubble Asteroid Hunter found 1,701 trails in 1,316 archival images, 1,031 unidentified (Kruk et al. 2022, 2024) [V]. Unlinked main-belt objects; no NEA value.
- **NEO Surveyor: launch no earlier than September 2027** on a Falcon 9; five-year baseline survey in two thermal-infrared bands [V, JPL mission page]. It will give diameters for small NEOs at scale, after this project's first release.
- **NEOMIR (ESA)**: still in Phase A study, potential launch early 2030s; first science workshop held 15 to 16 September 2026 [V].

## 11. Ranking

Score = information about composition or water x accessible NEAs reached x how unexploited x tractable on one workstation. Each factor 1 (low) to 5 (high); the product is only a sorting aid.

| Rank | Opportunity | Info | Reach (NHATS-class) | Unexploited | Tractable | Product | Note |
|---|---|---|---|---|---|---|---|
| 1 | Rubin ugrizy photometry from the MPC (and broker alerts) for NEAs, continuously updated | 2 | 2 now, 4 by 2028 | 5 | 5 | 100 to 200 | Only survey that reaches decameter NEAs; kilobytes of data |
| 2 | NEOWISE final-release thermal fits for NHATS and other NEAs lacking diameters | 3 | 2 (about 145 NHATS) | 3 | 5 | 90 | Diameter also converts a Yarkovsky drift into a density |
| 3 | SPHEREx forced spectrophotometry of NEAs that were bright in 2025 to 2027 | 5 | 1 (about 10 to 20 NHATS; about 200 to 600 NEAs) | 5 | 3 | 75 | Highest information per object; official catalog not until May 2028 |
| 4 | Gaia DR4 reflectance spectra and family table as the prior's calibration set | 3 | 1 direct, high indirect | 2 | 5 | 30 | Feeds channel 2; crowded field after 2 December |
| 5 | ATLAS and ZTF colours and phase slopes for NHATS objects | 1 | 2 | 3 | 4 | 24 | Median 8 and 4 points per object |
| 6 | Archival serendipity (DECam, PS1, SkyMapper, VST, HSC) | 2 | 1 | 2 | 2 | 8 | 5% detectability; multi-band part already mined |
| 7 | Euclid, TESS, K2, HST, JWST archives | 1 to 3 | 0 to 1 | varies | 2 | under 5 | Case studies only |

How I would use this in the plan:
- Build the catalog so that its direct-evidence layer is fed by three live sources from day one: MPC ADES photometry (which carries Rubin, ATLAS, ZTF, Pan-STARRS bands), NEOWISE thermal fits, and SBDB/SsODNet literature values.
- Run SPHEREx as a separate, bounded sub-project on the larger NEAs with a pre-registered validation set (objects with ground-based 0.8 to 2.5 micron and 3 micron spectra), and publish its null result if the photometry does not close. It produces validation objects for the catalog and an interesting stand-alone result.
- Treat Gaia DR4 as an input to the prior (another researcher's channel 2), not as NEA data.
- State plainly on the website that for about 95% of NHATS objects the posterior is the prior.

## 12. Files produced in this session

Downloads (not kept):
- `nhats_all.json` (JPL NHATS list), `sbdb_neo.json` (43,151 NEAs with H, taxonomy, albedo, diameter, period)
- `nhats_mpc_census.jsonl` and `.w0` to `.w3` (station and band counts for 1,000 NHATS objects)
- `most_random.jsonl.w*`, `most_bright.jsonl.w*`, `most_nea20.jsonl.w*` (SPHEREx coverage by predicted V)
- `gaia_dr3_sso_source.csv` (158,152 rows)
- `mpc_2025MN45.json` (example Rubin ADES records), `eros_cut2.fits` (example SPHEREx cutout), `most_eros.out`
- PDFs and text: `rtn011.pdf`, `lpsc2026_1833.pdf`, `lisse2024_ssoc.pdf`, `ivezic2022.pdf`, `bock2025_spherex.pdf`, `spherex_expsupp.pdf`

Scripts: `nhats_mpc_census2.py` and `nhats_spherex_most.py` are in `data/research/scripts/`; `ns_census_stats.py`, `ns_most_stats.py`, `ns_gaia_x.py` and `most_parse.py` were not kept.

## 13. Things I could not verify

- Whether a JWST dark-comet programme exists or has data.
- The number of NEAs in Gaia DR4 (not published before release).
- Whether NEOWISE thermal fits for reactivation years 8 to 11 are published or in press.
- Fink SSO API access (connection timed out today) and a public download location for ATLAS SSCAT-2.
- Whether IRSA MOST's predicted V uses G = 0 (the header suggests so).
- The total size of the SPHEREx Level 2 archive (my 100 TB figure is an estimate).
- HSC and Pan-STARRS multi-band NEA products (searched briefly, found none).

## Sources

SPHEREx
- https://irsa.ipac.caltech.edu/Missions/spherex.html
- https://irsa.ipac.caltech.edu/data/SPHEREx/docs/overview_dr1.html
- https://irsa.ipac.caltech.edu/data/SPHEREx/docs/overview_qr.html
- https://caltech-ipac.github.io/spherex-archive-documentation/spherex-data-releases/
- https://spherex.caltech.edu/page/data-products
- https://spherex.caltech.edu/news/spherex-data-release-1-dr1-is-now-available-at-irsa
- https://irsa.ipac.caltech.edu/data/SPHEREx/docs/SPHEREx_Expsupp.pdf
- https://arxiv.org/abs/2511.02985 (Bock et al., The SPHEREx Satellite Mission; Table 4)
- https://arxiv.org/abs/2511.15823 (SPHEREx pipeline paper)
- https://www.hou.usra.edu/meetings/lpsc2026/pdf/1833.pdf (Lisse et al., LPSC 2026)
- https://arxiv.org/abs/2402.08705 (Lisse and Bauer, SSOC for planetary defense)
- https://faculty.washington.edu/ivezic/Publications/SPHERExAsteroids2021.pdf (Ivezic et al. 2022, Icarus 371, 114696)
- https://arxiv.org/abs/2602.08037 (SOLO)
- https://arxiv.org/abs/2512.07318 and https://arxiv.org/abs/2508.15469 (3I/ATLAS)
- https://irsa.ipac.caltech.edu/applications/MOST/ and https://astroquery.readthedocs.io/en/latest/ipac/irsa/most.html
- https://arxiv.org/abs/2604.22012 (SPIFF), https://pypi.org/project/xcavation/, https://arxiv.org/abs/2509.04666 (kete)
- https://github.com/shrestha-droid/spherex-moving-sky (Space Apps 2026 example)

Gaia
- https://www.cosmos.esa.int/web/gaia/dr4
- https://www.cosmos.esa.int/web/gaia/dr4-papers
- https://www.cosmos.esa.int/web/gaia/release
- https://www.cosmos.esa.int/web/gaia/news
- https://www.cosmos.esa.int/web/gaia/fpr and https://www.cosmos.esa.int/web/gaia/fpr-sso-updated-astrometry
- https://ui.adsabs.harvard.edu/abs/2023A&A...680A..77D (Dziadura et al. 2023)
- https://gea.esac.esa.int/tap-server/tap (queried)

Rubin
- https://rtn-011.lsst.io/ (RTN-011 v10.0, 2026-11-19)
- https://dp2.lsst.io/index.html
- https://dp1.lsst.io/products/catalogs/ss_object.html
- https://rubinobservatory.org/for-scientists/resources/early-science
- https://rubinobservatory.org/for-scientists/data-products/alerts-and-brokers
- https://www.rubin.community/c/news/7 and https://www.rubin.community/t/rubin-status-november-17-2026/12959
- https://rubinobservatory.org/news/rubin-first-look/swarm-asteroids
- https://www.aura-astronomy.org/blog/2026/04/02/early-data-from-nsf-doe-vera-c-rubin-observatory-reveals-over-11000-new-asteroids/
- https://iopscience.iop.org/article/10.3847/2041-8213/ae2a30 (First Look light curves and colours)
- https://arxiv.org/abs/2609.29841, https://arxiv.org/abs/2610.07584, https://arxiv.org/abs/2506.02487
- https://data.minorplanetcenter.net/api/get-obs (queried)

Euclid
- https://www.cosmos.esa.int/web/euclid/euclid-dr1
- https://www.cosmos.esa.int/web/euclid/dr1-papers
- https://observatoiredeparis.psl.eu/euclid-dr1-foundation-first.html
- https://arxiv.org/abs/2604.25652, https://arxiv.org/abs/2501.05023
- https://meetingorganizer.copernicus.org/EPSC-DPS2025/EPSC-DPS2025-1399.html

NEOWISE
- https://irsa.ipac.caltech.edu/Missions/wise.html
- https://irsa.ipac.caltech.edu/data/WISE/docs/release/NEOWISE/
- https://sbn.psi.edu/pds/resource/neowisediam.html
- https://arxiv.org/abs/2107.07481, https://arxiv.org/abs/2002.07941
- https://baas.aas.org/pub/2024n8i212p04/release/1
- https://arxiv.org/abs/2504.00905, https://arxiv.org/abs/2410.24101, https://arxiv.org/abs/2605.23347

ZTF, ATLAS, TESS
- https://www.ztf.caltech.edu/ztf-public-releases.html
- https://arxiv.org/abs/2403.20179 (Fink sHG1G2), https://arxiv.org/abs/2302.01239 (SNAPS)
- https://arxiv.org/abs/2503.05412 (ATLAS SSCAT-2 phase curves), https://arxiv.org/abs/2404.04657
- https://github.com/lukeshingles/atlasserver
- https://arxiv.org/abs/2001.05822 (TSSYS-DR1), https://arxiv.org/abs/2501.07189

Archives and NEA taxonomy prior art
- https://arxiv.org/abs/2309.03555 (Sergeyev et al. 2023)
- https://arxiv.org/abs/2110.11656 (SkyMapper SSOs)
- https://arxiv.org/abs/2303.03164 (Saifollahi et al. 2023)
- https://arxiv.org/abs/2109.00088 (CANFind), https://datalab.noirlab.edu/dad.php
- https://arxiv.org/abs/2211.10719 (DES Trojans)
- https://arxiv.org/abs/2407.17613 (UHS)
- https://catch.astro.umd.edu/about
- https://arxiv.org/abs/2603.15872 (MANOS colours), https://arxiv.org/abs/2608.28779 (UKIRT small NEOs), https://arxiv.org/abs/2404.18263 (Sanchez et al. 2024)

JWST, HST, future missions
- https://arxiv.org/abs/2605.20498, https://iopscience.iop.org/article/10.3847/2515-5172/adc6f0 (2024 YR4)
- https://arxiv.org/abs/2502.01744 (Burdanov et al. 2025)
- https://www.nature.com/articles/s41467-025-63697-4 (1998 KY26)
- https://arxiv.org/abs/2611.10275
- https://arxiv.org/abs/2202.00246, https://arxiv.org/abs/2401.02605 (Hubble Asteroid Hunter)
- https://www.jpl.nasa.gov/missions/near-earth-object-surveyor
- https://neo.ssa.esa.int/-/neomir-science-workshop-2026, https://meetingorganizer.copernicus.org/EPSC-DPS2025/EPSC-DPS2025-1329.html

JPL APIs queried
- https://ssd-api.jpl.nasa.gov/nhats.api
- https://ssd-api.jpl.nasa.gov/sbdb_query.api
