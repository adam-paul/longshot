# Ground truth and validation statistics for a probabilistic NEA prospect catalog

Research brief: "known answers" set + how to validate calibrated predictions when truth is tiny and biased.
Date of research: 2026-11-20. All API counts below were pulled that day.

Status tags used throughout:

- **[V]** verified today (I read the source or queried the API in this session)
- **[R]** recalled from memory, not re-checked today
- **[U]** uncertain, conflicting, or could not be verified

The downloaded tables and the scripts that produced the counts (files named `gt_*.py`) were not kept.

---

## 0. Bottom line

1. **Independent ("gold") truth is about 35 to 40 objects, and composition-gold is about a dozen.** Six NEAs have spacecraft-grade mass and composition (Eros, Itokawa, Ryugu, Bennu, Didymos/Dimorphos; Toutatis has a flyby but no mass). Thirteen asteroids were seen in space before impact; four of them produced recovered meteorites; exactly one (2008 TC3) has both a pre-impact spectrum and a recovered meteorite. Roughly 15 to 20 binary NEAs have usable direct bulk densities.
2. **2026 added three live truth sources.** Tianwen-2 has been at Kamo'oalewa since June/July 2026 (sample back November 2027). Hayabusa2 flew past Torifune on 5 July 2026 (no composition result published yet). Hera arrived at Didymos around 11 November 2026 (Dimorphos mass not yet measured). Two more imminent impactors were found in 2026 (2026 JN4, 2026 RW1), none in 2025.
3. **The target population is almost unlabelled.** NHATS has 7,226 objects today; 7,018 have H >= 22; median H is 26.2. JPL SBDB has a taxonomy for 23 of them, an albedo for 69, a Yarkovsky A2 for 169, a radial A1 for 18, a rotation period for 306. At least 226 are radar-detected. SsODNet holds about ten times more taxonomy than SBDB: about 220 NHATS objects, about 95 of them at H >= 22 (scaled from a 477-object sample, section 9). That is still 3% of the list.
4. **The labelled sets sit 7 to 8 magnitudes brighter than the targets.** Median H is 17.9 for SBDB taxonomy, 19.1 for SBDB albedos, against 26.2 for NHATS. Any classifier trained on them is extrapolating a factor of about 30 to 40 in diameter. The few label sets that reach small sizes (MANOS 210 objects, Lopez-Oquendo 2026 122 objects, Sanchez 2024 84 objects, the 13 impactors, 61 meteorite falls with orbits) are the ones that matter most.
5. **Two fresh cautionary cases, both NHATS objects and both mission targets:** 1998 KY26 went from about 30 m to 11 m (albedo about 0.5), and Kamo'oalewa went from a lightcurve model of 68 x 46 x 39 m to about 15 to 21 m (JWST) and about 20 m (Tianwen-2 image), with a spectrum that is less red than the 2021 one that started the lunar-origin idea. Sizes of tiny NEAs from H plus an assumed albedo were wrong by 2 to 3 times in both cases where we can check.
6. **Catalog "density" columns are not truth.** SsODNet's best-value densities for NEAs mix direct measurements with Yarkovsky-derived (model-dependent) ones and disagree with the radar-binary literature by up to 3 times for several objects (2002 CE26: 3.06 vs 0.9 g/cm3; Moshup: 1.27 vs 1.97; Toutatis: 0.73 from Yarkovsky vs 2.1 to 2.5 from its L-chondrite analogue). The truth table has to be curated by hand with provenance.
7. **Some classes cannot be validated at all on NEAs.** There is one radar-confirmed metal-rich NEA (1986 DA). There is no dark comet with a detected coma or volatile. The 3-micron detections on NEAs are mostly on S-types (surface OH from solar wind or impacts), not on carbonaceous bodies. "Hydrated" truth among NEAs is essentially Bennu, Ryugu and seven carbonaceous meteorite falls with orbits.
8. **Statistically, the gold set can falsify but cannot calibrate.** With 12 gold objects, a method that claims 90% and delivers 60% is caught only about 77% of the time. Calibration has to come from (a) silver labels with a sealed, importance-weighted hold-out, (b) end-to-end synthetic injection and "degrade a well-known object" tests, and (c) pre-registered predictions for objects that will get truth later.
9. **The strongest validation available is prospective.** Kamo'oalewa (sample November 2027), Dimorphos (Hera, 2026 to 2027), Torifune (flyby data still coming down), Apophis (2029), 1998 KY26 (2031), new impactors (about 2 per year lately), and every new spectrum published after the freeze date. Publishing predictions before those answers arrive is cheap, honest, and a natural feature for the website.

---

## 1. Truth tiers (proposed definitions)

| Tier | Definition | Use |
|---|---|---|
| Gold-A | Composition from returned sample or recovered meteorite; mass from spacecraft tracking | Final exam only. Never used to fit or tune. |
| Gold-B | Bulk density from a binary mutual orbit plus an independent size (radar or thermal); composition from in-situ instruments without a sample (Eros, Didymos, Toutatis) | Final exam for density; sanity check for class |
| Silver | Remote-sensing labels from a channel the method under test does not use: spectral taxonomy, thermal-IR albedo, radar SC/OC and radar albedo, fireball strength class | Training, cross-validation, sealed test set |
| Bronze | Model-dependent values from the same physics we want to test (Yarkovsky plus thermophysics densities, SRP densities with assumed size, H-derived diameters, dynamical source probabilities) | Comparison with prior art only. Never as truth. |

Every row of the truth table should carry: value, uncertainty, method, primary reference, tier, and a set of flags saying which of our channels it is independent of. This matters because the same object often has both a direct density and a Yarkovsky-derived one in the catalogs.

---

## 2. (a) Spacecraft-visited and sample-return NEAs

SBDB values are from the SBDB Query API today [V]. A2 is the JPL transverse non-gravitational parameter in au/d^2.

| Object | Mission and status | In NHATS (min dv km/s) | Taxonomy | Analogue and how it is known | Bulk density g/cm3 | pV | D km | P h | A2 in SBDB (snr) |
|---|---|---|---|---|---|---|---|---|---|
| 433 Eros | NEAR Shoemaker orbiter 2000 to 2001 | no | S | L or LL ordinary chondrite, from X-ray/gamma-ray spectrometers, no sample [R] | 2.67 [V] | 0.25 [V] | 16.84 | 5.27 | none (too large) |
| 25143 Itokawa | Hayabusa, sample returned 2010 | yes (9.41) | S(IV) | Equilibrated LL chondrite, from returned grains (Nakamura et al. 2011) [V] | 1.9 [V] | not in SBDB | 0.33 | 12.13 | -2.9e-14 +/- 7.2e-15 (4.0) |
| 162173 Ryugu | Hayabusa2, sample returned Dec 2020 | yes (8.25) | Cb | CI-like, from returned sample; much darker than CI meteorites [V] | 1.19 [V] | 0.045 | 0.896 | 7.63 | -2.5e-14 +/- 5.0e-15 (5.0) |
| 101955 Bennu | OSIRIS-REx, sample returned Sep 2023 | yes (7.00) | B | Aqueously altered carbonaceous, closest to CI and Ryugu, about 80 vol% phyllosilicates, volatile-rich, Na phosphates and evaporite salts [V] | 1.194 [V] | 0.044 | 0.484 | 4.296 | A2 field empty in SBDB [V]; reason not checked |
| 65803 Didymos and Dimorphos | DART impact 26 Sep 2022; Hera arrived about 11 Nov 2026, at 25 to 30 km | no | S | L/LL ordinary chondrite from spectra, no sample [R] | Didymos 2.60 +/- 0.14, Dimorphos 1.54 +/- 0.22 (Makadia et al. 2026, model-dependent split) [V]; SBDB still lists 2.17 [V]; Raducan 2024 gives Dimorphos < 2.4 [V] | not in SBDB | 0.78 and 0.15 | 2.26 | not listed |
| 4179 Toutatis | Chang'e-2 flyby 13 Dec 2012 at 770 m | no | Sk | L chondrite from spectra (Reddy 2012) [V] | no measured mass. 2.1 to 2.5 inferred from analogue [V]. SsODNet lists 0.73 from Yarkovsky (see section 7) [V] | 0.405 | 5.4 | tumbler, 176 | -7.7e-15 +/- 9.8e-16 (7.9) |
| 469219 Kamo'oalewa | Tianwen-2: rendezvous burn 7 June 2026, within 20 km by 6 July 2026; sampling pending; departure April 2027; capsule November 2027 | yes (6.11) | none in SBDB; "Sqw" in Zhang 2026 | Pre-2026: very red, lunar-like (2021). 2026: JWST NIRSpec spectrum distinctly less red, 0.93 um silicate band, D about 15 to 21 m (Sharkey et al. 2026). Zhang et al. 2026: band centre 1.001 +/- 0.028 um, LL chondrite, Flora family. Tianwen-2 first image: about 20 m long, jagged, monolith-like [V] | none yet | none | 0.015 to 0.021 | 0.467 (28 min) | -1.3e-13 +/- 1.8e-14 (7.2) |
| 98943 Torifune (2001 CC21) | Hayabusa2 flyby 5 July 2026 18:30 JST at about 5 km/s; ONC-T, TIR, NIRS3, LIDAR ran until just before closest approach; only part of the data is down | yes (8.99) | L (SBDB) | Not published. Images show an elongated two-lobed body [V] | none | none | about 0.5 [U] | 5.02 | +1.3e-14 +/- 5.7e-15 (2.3) |
| 1998 KY26 | Hayabusa2 rendezvous planned 2031 | yes (7.85) | Xe (Bolin 2025) | none yet | SsODNet lists 2.8 (+1.6/-1.0), attributed to a 2025 non-gravitational fit [U] | 0.52 (SBDB) | 0.011 | 0.0892 (5.35 min) | -2.2e-13 +/- 4.9e-14 (4.5); A1 and A3 also listed, both under 2 sigma |
| 99942 Apophis | OSIRIS-APEX arrives after the April 2029 flyby | yes (6.05) | Sq | LL-like from spectra [R] | none (2029) | 0.35 | 0.34 | 30.56 | -2.9e-14 +/- 1.9e-16 (153) |
| 3200 Phaethon | DESTINY+ launch slipped to 2028 [V] | no | B / F | none | 1.67 +/- 0.47 from Yarkovsky only (Hanus 2018) [V], bronze | 0.107 | 6.25 | 3.60 | -6.3e-15 +/- 1.2e-16 (52) |

Notes that matter for the plan:

- **Sizes of tiny targets were badly over-estimated before truth arrived.** 1998 KY26: 30 m to 11 m, rotation 10.7 min to 5.35 min (Santana-Ros et al. 2025, Nature Communications) [V]. Kamo'oalewa: 68 x 46 x 39 m from a lightcurve shape model in March 2026, then 15 to 21 m from JWST and about 20 m from the spacecraft four months later [V]. Both imply albedos far above the 0.14 to 0.18 that H-to-size conversions assume.
- **Kamo'oalewa is the only NHATS-sized object that will get sample-grade truth this decade,** and it already has a 7-sigma Yarkovsky detection. A density prediction from A2 plus the new size can be published now and scored in 2027 to 2028.
- **Bennu and Didymos have no A2 in the SBDB query output** even though both have published non-gravitational measurements (Chesley et al. 2014 for Bennu; Makadia et al. 2026 for Didymos). My guess is that JPL fits them with bespoke force models, but I did not confirm that. Either way, the SBDB A2 list (618 NEAs, 573 at 3 sigma or better, 351 at 5 sigma or better) is not the complete list of calibrators.
- **Yarkovsky-to-density has exactly one clean, out-of-sample success:** Chesley et al. 2014 predicted Bennu's density as 1.26 +/- 0.07 g/cm3 before arrival; the measured value is 1.19 [V].
- Main-belt flybys (Mathilde 1.3, Ida 2.6, Lutetia 3.4 g/cm3 [R]; Gaspra, Steins, Annefrank, Dinkinesh, Donaldjohanson without masses) are useful only as taxonomy-to-density anchors for priors, not as NEA validation.

---

## 3. (b) Asteroids detected in space before impact: complete list (13)

Sources: ESA NEOCC past-impactors list (13 entries today) [V]; Chow et al. 2026 Table 1 (11 as of 1 January 2026) [V]; Wikipedia list [V]; SBDB for H, class and number of observations used [V]. ESA states that 2025 had no imminent-impactor discoveries [V].

| # | Object | Impact (UTC) | Discoverer | H (SBDB) | Obs used (SBDB) | Size | Physical data taken before impact | What came down |
|---|---|---|---|---|---|---|---|---|
| 1 | 2008 TC3 | 2008-10-07 02:45:40 | Mt. Lemmon | 30.72 | 575 | 4.1 m | Reflectance spectrum 554 to 995 nm (WHT/ISIS), flat, F-class; lightcurves, P = 97 s [V] | Almahata Sitta: 47 stones / 3.95 kg in the first search, about 600 stones / 10.5 kg in all; polymict ureilite plus other lithologies [V]. In NHATS. |
| 2 | 2014 AA | 2014-01-02 03:05 +/- 6 min | Mt. Lemmon | 30.95 | 8 | 2 to 3 m | none (astrometry only) | Atlantic; infrasound only; nothing recovered [R] |
| 3 | 2018 LA | 2018-06-02 16:44:12 | Mt. Lemmon | 30.57 | 17 | 1.56 m | none; SkyMapper and ATLAS astrometry | Motopi Pan, 23 stones, howardite (HED), Vesta link [V] |
| 4 | 2019 MO | 2019-06-22 21:25:47 | ATLAS-MLO | 29.12 | 7 | 4 to 8 m (ESA); 4.7 m at pV 0.18 | none | Caribbean; about 5 to 6 kt; nothing recovered [V] |
| 5 | 2022 EB5 | 2022-03-11 21:22:45 | Konkoly (Sarneczky) | 31.33 | 176 | 1.4 to 3 m (ESA, from H); 5 to 6 m (Geng et al., from energy) [U] | astrometry and photometry only | Off Jan Mayen; infrasound about 4 kt vs 0.4 kt from H; nothing recovered [V] |
| 6 | 2022 WJ1 | 2022-11-19 08:26:40 | Mt. Lemmon | 33.58 | 51 | 0.4 to 0.6 m | Four-colour photometry with the 4.3 m Lowell Discovery Telescope: silicate-rich, S-type; fireball strength like an ordinary chondrite (Kareta et al. 2024) [V] | Southern Ontario, mostly into Lake Ontario; ESA says no meteorite recovered on land [V] |
| 7 | 2023 CX1 | 2023-02-13 02:59:13 | Konkoly | 32.72 | 331 | 0.72 +/- 0.06 m, 650 +/- 160 kg | Photometry: nearly spherical or P < 2 s (Egal et al. 2025) [V] | Saint-Pierre-le-Viger, L5-6; the only L chondrite tied to a pre-impact detection [V] |
| 8 | 2024 BX1 | 2024-01-21 00:32:38 | Konkoly | 32.71 | 321 | under 0.5 m (0.44 m) | Trail photometry: P = 2.5888 +/- 0.0002 s, fastest known rotator [V] | Ribbeck, aubrite, 1.75 kg; high albedo of E-types explains the H vs size mismatch [V] |
| 9 | 2024 RW1 | 2024-09-04 16:39:32 | Mt. Lemmon | 32.20 | 76 | 1.8 +/- 0.4 m assuming pV 0.07 (Ingebretsen 2025); Chow 2026 table gives 3.3 m [U] | APO 3.5 m griz colours: g-r 0.47, r-i 0.13, i-z -0.11; closest to B-type (C-complex) [V] | Off Luzon; 0.2 kt; nothing recovered |
| 10 | 2024 UQ | 2024-10-22 10:54:48 | ATLAS-HKO | 32.66 | 8 | about 0.9 m | none; reported only after impact | Eastern Pacific; nothing recovered [V] |
| 11 | 2024 XA1 | 2024-12-03 16:14:52 | Kitt Peak Bok | 32.95 | 60 | about 1 m | astrometry and photometry | Yakutia; strewn field computed (Gianotto 2025); no recovery reported [V] |
| 12 | 2026 JN4 | 2026-05-15 about 13:36 to 13:39 | JPL SynTrack (first by synthetic tracking) | 33.38 | 6 | 0.5 to 1.2 m | none; 2.7 h arc; one ZTF trail found afterwards | Between N Australia and New Guinea, corridor over 4,500 km; no instrumental fireball record, one eyewitness in Darwin. ESA first left it off its list, and lists it now [V] |
| 13 | 2026 RW1 | 2026-09-06 16:07:39 | Mt. Lemmon | 33.32 | 41 | 0.5 to 1.1 m | astrometry; Pan-STARRS 2 precovery; Zadko and LCO follow-up; no spectrum or lightcurve reported | Indian Ocean NW of Australia; fireball photographed from Broome at 780 km; first Aten-class impactor (SBDB class ATE); nothing recovered [V] |

What this set gives, and what it does not:

- **Meteorite in hand: 4 of 13** (2008 TC3, 2018 LA, 2023 CX1, 2024 BX1): a polymict ureilite, a howardite, an L5-6, an aubrite. Three of four are achondrites, against roughly 77% ordinary chondrites among falls with orbits (section 4). With N = 4 this is not a population statement, but it does warn that the tiny-impactor sample is not a miniature of the fall statistics.
- **Composition measured telescopically before impact: 3 of 13** (2008 TC3 spectrum; 2022 WJ1 and 2024 RW1 colours). **Both telescope data and a meteorite: 1** (2008 TC3).
- **Size truth independent of albedo** (from fireball energy or mass): 2008 TC3, 2022 WJ1, 2023 CX1, 2024 BX1, 2019 MO, 2022 EB5. These are the best checks on H-to-size at metre scale. 2022 EB5 shows a factor of about 10 mismatch between energy from H and energy from infrasound.
- **Arc lengths are hours.** None has a detectable non-gravitational term. They test the orbit-to-source and photometry channels, not the Yarkovsky or SRP channels.
- **Selection:** 10 of the first 11 struck the northern hemisphere, matching where the discovering telescopes are; Chow et al. 2026 simulate that 12 of 14 LSST-discovered impactors would be S-types because brighter objects are easier to catch [V]. The set is albedo-biased like every other optical sample.
- **Rate:** 4 in 2024, 0 in 2025, 2 in 2026. Rubin is predicted to add southern impactors. This is a slowly growing prospective test set.

---

## 4. (c) Meteorite falls with instrumentally determined orbits

- **Meier's list (meteoriteorbits.info): 61 meteorites**, page last modified 2026-09-22 [V]. My parse of the table: H chondrites 19, L 19, LL 7 (one of them Benesov, LL3.5 plus H5), L/LL 2, carbonaceous 7 (Tagish Lake C2-ung, Maribo CM2, Sutter's Mill, Aguas Zarcas CM2, Flensburg C1-ung, Winchcombe CM2, Hillsborough CM1/2), achondrites 5 (howardites Motopi Pan and Saricicek, eucrite Bunburra Rockhole, aubrite Ribbeck, ureilite Almahata Sitta), enstatite chondrite 1 (Neuschwanstein EL6), iron 1 (Adalen, provisional). Ordinary chondrites are 47 of 61 (77%).
- **Machine-readable form:** the site has no CSV, but it is WordPress and the table is served as JSON at `https://www.meteoriteorbits.info/wp-json/wp/v2/pages/5` (field `content.rendered`, an HTML table of 61 rows with name, type, country, date, time, mass, a, e, i, argument of perihelion, node, each with uncertainty, and a reference key) [V]. Parsing takes about ten lines.
- **Granvik and Brown 2018 (Icarus 311, 271):** re-derived orbits for the 25 falls published up to 2016 and gave escape-route probabilities from the Granvik NEO model. Key methodological result: velocity precision better than about 0.1 km/s does not improve source identification [V].
- **Jenniskens and Devillepoix 2025 (MAPS, doi 10.1111/maps.14321):** review of 75 meteorites with trajectories, size, cosmic-ray exposure ages, and proposed family links (H chondrites to Koronis and Nele, LL to Flora, L to inner belt). Some links are disputed (Marsset et al. 2024 put L chondrites in Massalia) [V].
- **Broz et al. 2024 and Marsset et al. 2024 (Nature 634):** three young families (Karin, Koronis, Massalia) are argued to supply about 70% of falls (figure from a university summary, not checked against the paper) [U].

Caveats for use as truth:

1. The atmosphere is a filter. Shober et al. 2025 (Nature Astronomy), with 7,982 impacts and 540 potential falls, find that objects with small present or past perihelia are up to 10 times over-represented among falls, and that carbonaceous material mostly does not survive [V]. Lopez-Oquendo et al. 2026 reach the same conclusion from the asteroid side [V].
2. Sizes are decimetres to a few metres, below NHATS sizes by one to two orders of magnitude, but adjacent to the smallest NHATS objects.
3. The orbit is the orbit at impact, so by construction every one of these has a tiny Earth MOID. That is close to the NHATS selection (low delta-v means Earth-like orbits), which is a point in favour of this set.
4. The family assignments are bronze: they are other people's models of the same orbit-to-source channel.

---

## 5. (d) Fireball networks with orbits and physical classification

| Dataset | Size and content | Access | Caveats |
|---|---|---|---|
| European Fireball Network, Borovicka et al. 2022 (A&A 667, A157 and A158) | 824 fireballs, 2017 to 2018; orbit, photometric mass (about 5 g to 100 kg), end height, PE and the new pressure-resistance factor Pf with classes Pf-I to Pf-V. Pf-I (asteroidal) is 54% of the sample, Pf-III to V (cometary) 21%. 473 have aphelion under 4.9 au. 12 probable irons (5 confirmed by spectra), about 2.5% of the low-aphelion set. 16 meteorite-dropping candidates [V] | CDS catalogue J/A+A/667/A157, one row per fireball. Today the CDS FTP path returned a 404 page from this host and VizieR TAP timed out, so access needs re-testing [U] | Strength is a proxy, not mineralogy. Irons look weak in Pf because they ablate by melting. Two years, central Europe only. |
| Desert Fireball Network / Global Fireball Observatory | Largest photographic network (2.5 million km2); orbits to high precision | No public bulk orbit release found today; individual papers and collaboration requests [U] | Same strength-proxy limits |
| FRIPON (Colas et al. 2020) | About 4,000 meteoroids by 2020; DR1 is over 500 events seen by at least 6 cameras | fireball.fripon.org; data are "free of use for education or non commercial purpose only", and the page asks users to contact the team [V] | Licence may conflict with an open public catalogue |
| Shober et al. 2025 compilation | 7,982 impacts (EDMOND, CAMS, GMN, FRIPON, EFN) and 540 potential falls (GFO, EFN, FRIPON) [V] | Check the paper's data statement [U] | Mostly small meteoroids |
| CNEOS / US Government sensors | 1,074 events from 1988-04-15 to 2026-10-04; 602 with altitude; 363 with velocity vectors [V] | `https://ssd-api.jpl.nasa.gov/fireball.api?vel-comp=true`, open | No uncertainties. Velocity vectors are known to be unreliable for orbit work [R]. In today's pull, 9 of the 363 rows with vectors report a speed that differs from the norm of their own components by more than 0.2 km/s (largest gap 18 km/s) [V]. Only the brightest events; no composition. |

How fireballs can be used here: as a population-level check on the orbit-to-material prior at the small-size end (does the fraction of weak, cometary-like material rise with aphelion and fall with perihelion history the way the prior says), and for the iron fraction (a few percent at centimetre to decimetre size). They cannot validate per-object predictions for NHATS bodies.

---

## 6. (e) Radar

- **Detections:** the JPL list has 1,149 radar-detected NEAs (updated 2 June 2025) [V]. I parsed the list and matched 1,099 to SBDB: median H 21.1, 464 with H >= 22, and **at least 226 are NHATS objects**. This is by far the largest physical-data overlap with the target list after rotation periods. The list is names only.
- **Disc-integrated properties are published for far fewer:**
  - Benner et al. 2008 (Icarus 198, 294): circular polarisation ratio SC/OC for 214 NEAs; strong dependence on class, highest for E and V types; S and C indistinguishable [V].
  - Virkki et al. 2022 (PSJ 3, 222): 191 NEAs from Arecibo, December 2017 to December 2019; SC/OC for 112 (mean 0.37 +/- 0.23; 5 above 1.0, possible E-types); OC radar albedo for 41 (mean 0.21 +/- 0.11; 0.19 +/- 0.06 for 11 S-complex) [V].
  - PDS "Asteroid Radar V18.0" (EAR-A-5-DDR-RADAR-V18.0), a compilation of published detections and disc-integrated properties [V, metadata only].
  - L. Benner's web tables of NEA radar albedo and SC/OC rankings now redirect to a "missing" page [V]. There is no single live public table of "all NEAs with SC/OC and radar albedo". It has to be assembled from PDS plus Benner 2008 plus Virkki 2022 plus single-object papers.
- **Metal-rich NEAs:**
  - (6178) 1986 DA: radar albedo 0.58 (Ostro et al. 1991), the only NEA confirmed metal-rich by radar; spectrum matches about 85% metal plus 15% pyroxene; surface bulk density 3.79 (range 2.33 to 6.5) g/cm3; delivered through the 5:2 resonance (Sanchez et al. 2021) [V].
  - (843295) 2016 ED85: near-identical spectrum, no radar [V]. SBDB has no taxonomy for either of these two objects [V], a sign of how stale SBDB physical parameters are.
  - Virkki 2022 flag two (press: up to four) unusually high radar albedos; the designations were not in the sources I could read [U]. 2017 YE5 has a high radar albedo but is a low-density D-type equal-mass binary, so high radar albedo alone is not proof of metal [V].
  - (29075) 1950 DA is not a metal case: Rozitis, MacLennan and Emery 2014 (Nature, doi 10.1038/nature13632) found a bulk density near 1.7 g/cm3 (a later analysis quotes 1.0 to 2.4), a rubble pile held together by cohesion, with a low radar albedo similar to Lutetia's [V from the abstract and secondary accounts].
- **Consequence:** the "metal-rich" class has one confirmed positive among NEAs. A probability for that class cannot be calibrated against NEA truth. The only route is main-belt M and X types with radar (Shepard et al.) and, from 2029, Psyche.

---

## 7. (f) Bulk densities

### 7.1 Direct (gold)

| Object | Density g/cm3 | Basis | Source and status |
|---|---|---|---|
| Eros | 2.67 +/- 0.03 | spacecraft mass and shape | SBDB 2.67 [V] |
| Itokawa | 1.90 +/- 0.13 | spacecraft | SBDB 1.9 [V] |
| Ryugu | 1.19 +/- 0.02 | spacecraft | SBDB 1.19 [V] |
| Bennu | 1.19 | spacecraft | SBDB 1.194 [V] |
| Didymos | 2.60 +/- 0.14 | binary orbit, DART, occultations | Makadia et al. 2026 [V] |
| Dimorphos | 1.54 +/- 0.22 | momentum transfer argument, model-dependent; Hera will measure it | Makadia et al. 2026 [V] |
| (66391) Moshup, 1999 KW4 | 1.97 +/- 0.24 | radar binary | Ostro et al. 2006 [R]; SBDB 1.974 [V] |
| (185851) 2000 DP107 | 1.38 +/- 0.24 | radar binary | Naidu et al. 2015 [R]; SBDB 1.365 [V] |
| (175706) 1996 FG3 | 1.3 to 1.4 +/- 0.4 to 0.6 | lightcurve binary plus thermal size | Scheirich et al. 2015; SsODNet 1.36 +/- 0.42 [V] |
| (153591) 2001 SN263 | 1.1 +/- 0.2 to 0.4 | radar triple | Becker et al. 2015 [R]; SsODNet 1.12 +/- 0.41 [V] |
| (136617) 1994 CC | 2.1 +/- 0.6 to 0.7 | radar triple | Brozovic et al. 2011 [R]; SsODNet 2.08 +/- 0.71 [V] |
| (276049) 2002 CE26 | 0.9 (+0.5/-0.4) | radar binary | Shepard et al. 2006 [R]; SBDB 0.9 [V]; **SsODNet 3.06 +/- 1.19** [V] |
| (35107) 1991 VH | 1.5 +/- 0.5 | lightcurve binary | SsODNet [V] |
| (164121) 2003 YT1 | 1.6 +/- 1.0 | binary | SsODNet [V] |
| (3122) Florence | 1.77 +/- 0.09 (SsODNet); about 1.4 from radar [R] | radar triple | [U] |
| (3671) Dionysus | 1.1 (+0.2/-0.4) | lightcurve binary | SsODNet [V] |
| (494658) 2000 UG11 | 0.55 +/- 0.25 | radar binary | SsODNet [V] |
| (311066) 2004 DC | 2.5 (SsODNet, no error); 1.7 in the radar literature [R] | radar binary | [U] |
| (1862) Apollo | 2.05 +/- 0.35 (Ford et al. 2014, binary) vs 2.85 (+0.48/-0.68) (Rozitis et al. 2013, Yarkovsky) | two methods on one object | SsODNet and search [V] |

- Johnston's Archive (updated 13 November 2026) lists **113 NEAs with companions** (10 Atens, 67 Apollos, 35 Amors, 1 Atira; 5 with two satellites) [V]. It does not tabulate densities. Only about 15 to 20 of these systems have a published density with an error under about 40%.
- Binary densities are system densities, dominated by a fast-rotating, top-shaped primary of 0.3 to 3 km. None is NHATS-sized. Fast-rotating primaries are a specific structural class (rubble piles near the spin limit), so this set is biased toward low density.

### 7.2 Model-dependent (bronze): Yarkovsky plus thermophysics

| Object | Density g/cm3 | Source |
|---|---|---|
| Bennu | 1.26 +/- 0.07 predicted, 1.19 measured | Chesley et al. 2014 [V] |
| Golevka | 2.7 (+0.4/-0.6) | Chesley et al. 2003; SBDB and SsODNet 2.7 [V] |
| (29075) 1950 DA | about 1.7, range 1.0 to 2.4 (Rozitis et al. 2014) [V, secondary]; SsODNet 2.32 +/- 0.54 from Dziadura 2023 [V] | two different answers from the same physics |
| Apollo | 2.85 (+0.48/-0.68) | Rozitis et al. 2013 [V] |
| Geographos | 2.1 (+0.55/-0.45) | Rozitis and Green 2014 via SsODNet [V] |
| Phaethon | 1.67 +/- 0.47 | Hanus et al. 2018 [V] |
| Castalia | 2.40 +/- 0.73 | Dziadura et al. 2023 via SsODNet [V] |
| Toutatis | 0.73 +/- 0.24 | Dziadura et al. 2023 via SsODNet [V]; contradicts 2.1 to 2.5 from its L-chondrite match. A slow tumbler breaks the standard Yarkovsky assumptions. |

- **Prior art to know:** Dziadura et al. 2023 (A&A 680, A77) fitted orbits for 446 NEAs with Gaia DR3 astrometry, obtained reliable A2 for 49, and computed bulk densities for those; the 2025 follow-up with the Gaia FPR reports 43 robust plus 9 new detections [V]. Greenberg et al. 2020 list 247 NEAs with Yarkovsky drifts [R]. So "Yarkovsky to density for many NEAs" has been done at the tens-of-objects level, with population-level assumptions for thermal inertia and obliquity. What has not been done is validating those densities against independent truth, and the Toutatis and 1950 DA rows show why that matters.
- **Calibration set for the Yarkovsky channel (independent density and at least 3-sigma A2):** Itokawa (4.0), Ryugu (5.0), Moshup (55), 2000 DP107 (15), 1996 FG3 (8), 2003 YT1 (64) from SBDB, plus Bennu and Didymos from the literature, plus Apollo if the binary density is taken as truth. **About 8 or 9 objects, all larger than 300 m.** Kamo'oalewa would be the first small one.

### 7.3 Solar-radiation-pressure objects

- SBDB lists a radial A1 for **21 NEAs**; 18 are in NHATS [V]. The clear SRP detections (A1 over 5 sigma) are 2009 BD (6.6), 2006 RH120 (17), 2012 LA (5.6), 2015 TC25 (7.6), 2020 CD3 (56), 2020 GE (14), 2021 GM1 (5.3), and **2026 QQ8** (13; H 31.4; new this year; NHATS minimum delta-v 3.35 km/s).
- Published densities: 2009 BD 2.9 or 1.7 depending on which of two size solutions is right (Spitzer gave a non-detection), 2011 MD 1.1 (+0.7/-0.5) with macroporosity at least 65% (Mommert et al. 2014) [V]; 2020 CD3 2.1 +/- 0.4 for an S-type assumption, area-to-mass about 6.9e-4 m2/kg (Fedorets et al. 2020) [V]; 2015 TC25 about 1 for D about 2.2 m [V].
- **There is no independent density for any SRP object.** SRP gives area-to-mass; the density needs a size, and the size needs an albedo or a thermal detection. What can be validated is (i) recovery of the published A1 values and (ii) discrimination of artificial objects, whose area-to-mass is an order of magnitude higher. The artificial-object problem is real: 2020 SO was a Centaur stage [R], and two 2026 preprints argue that 1998 KY26 itself could be the lost Phobos 1 spacecraft (arXiv 2606.01288, 2609.24283) [V that the preprints exist; U on the claim].

---

## 8. (g) Large label sets for hold-out testing

| Set | Size | Size range | Access | Bias notes |
|---|---|---|---|---|
| MITHNEOS (Binzel et al. 2019; Marsset et al. 2022) | over 1,000 NEOs with spectra; Marsset analysed 976; 491 new NIR spectra of 420 NEOs | 90% within 15 < H < 23, about 100 m to 3 km | smass.mit.edu [R] | Observed S+Q 66%, carbonaceous 23%; after albedo debiasing S+Q 42%, carbonaceous 48% [V]. Targeting favours PHAs, radar and mission targets. |
| MANOS (Devogele et al. 2019) | 210 NEOs with visible spectra [V] | mean H about 25, mission-accessible by design | Table 5 of the paper lists the classification per object; the spectra themselves were not released with the paper [V] | Q 27.1%, X 23.8%, S 16.7%, C 10.9%, K/L 9.0%, A 3.8% (S+Q 43.8 +/- 4.6%) [V]. Visible-only: X-complex unresolved without albedo. The single most relevant spectral set for NHATS. |
| NEOShield-2 (Perna et al. 2018) | 147 visible spectra | small NEAs | paper tables | [V for count] |
| NEOROCKS (Hromakina et al. 2021, 2023) | 93 objects with BVRI colours | mixed | paper tables | Colours only; most objects under 500 m are silicate, flagged by authors as a possible bias [V] |
| Sanchez et al. 2024 | 84 NIR spectra, 59 lightcurves | under 300 m, mean 126 m | paper | S-complex 66%, mostly LL-like; 83% from nu6 [V] |
| Lopez-Oquendo et al. 2026 (arXiv 2608.28779, PSJ accepted) | 122 NEOs with ZJHK colours and probabilistic classes | 5 to 150 m, median 60 m | not yet checked | Observed S about equal to C/X; debiased population dominated by dark bodies [V]. Newest and closest in size to NHATS. |
| Gaia DR3 reflectance spectra | 60,518 objects; **104 NEAs** by my cross-match | NEA H 9.2 to 19.6, median 15.8; 3 are NHATS | ESA Gaia TAP, `gaiadr3.sso_reflectance_spectrum` [V] | Useless for the targets directly; useful for the source families |
| SBDB taxonomy | 327 NEAs: S 183, X 48, C 21, Q 18, V 15, L 8, K 7, T 6, B 6, O 6, D 4 [V] | median H 17.9; only 12 with H >= 22 | SBDB Query API | Mixed Tholen and SMASS schemes; stale |
| Mahlke et al. 2022 taxonomy | 2,983 observations of 2,125 asteroids to build it; 6,038 observations of 4,526 asteroids classified; probabilistic classes [V] | all populations | CDS J/A+A/665/A26 | Uses albedo as an input, so it leaks if albedo is also a feature |
| NEOWISE diameters and albedos | 1,845 unique NEOs through 2020 (Masiero et al. 2021) [V]; final data release 14 November 2024 covers 10.6 years [V]; no final unique-NEO count found [U] | mostly over 100 m | PDS, IRSA | Thermal selection is much less albedo-biased than optical. Reactivation-era diameters carry about 30% error. |
| Spitzer (ExploreNEOs, NEOSurvey, NEOLegacy) | ExploreNEOs about 600 to 700, NEOSurvey 597, total target about 2,000 [V for programme sizes, U for final total] | reaches smaller sizes than NEOWISE | nearearthobjects.nau.edu | Single-band 4.5 um thermal fits; albedo errors of a factor of about 2 |
| SBDB albedos | 1,205 NEAs; median H 19.1; 143 with H >= 22; 40 with H >= 24 [V] | | SBDB Query API | Mixed provenance, some from 1994 |
| Rotation periods | 2,180 NEAs in SBDB (from LCDB); 306 in NHATS [V] | | LCDB | Not a composition label, but a strength constraint |

Overlaps inside SBDB that set the size of cross-channel tests [V]: taxonomy and at-least-3-sigma A2: 63 NEAs. Albedo and 3-sigma A2: 118. Taxonomy and albedo: 142. Radar-detected and taxonomy: 100. Radar-detected and 3-sigma A2: 156.

Selection biases to model explicitly:

1. **Albedo bias in every optical sample.** At fixed size, bright objects are over-represented by a factor (pV_x / pV_y)^(2.5 beta), beta = (alpha - 1)/5 (Marsset et al. 2022) [V]. That correction alone moves S+Q from 66% to 42%.
2. **Targeting bias.** Spectra are taken of PHAs, radar targets, mission candidates and bright apparitions. Marsset's correction does not address this, and the paper says so [V].
3. **Size shift.** Composition fractions change with size: MANOS finds fewer S+Q and more X at H about 25; Lopez-Oquendo 2026 finds a dark-dominated debiased population at 5 to 150 m. The class prior for NHATS is therefore not the class mix of the training set. This is label shift, on top of covariate shift.
4. **Apparition geometry.** Small objects are observed only at close approach and high phase angle, which reddens spectra and changes colours.
5. **Label noise and scheme mixing.** S vs Q is a weathering state, not a composition. The X-complex is E, M and P, which are three different materials separable only by albedo. Taxonomy is not composition: "C-type" does not say hydrated or not.
6. **Albedo used twice.** If albedo is a feature and the label comes from a taxonomy that used albedo (Tholen E/M/P, Mahlke 2022), the test is partly circular.

---

## 9. Coverage of the target list (NHATS), measured today

From the NHATS API (default constraints) and SBDB [V]:

| Quantity | Count |
|---|---|
| NHATS objects | 7,226 |
| with H >= 22 | 7,018 |
| median H | 26.2 (API size range 10 to 45 m at the median) |
| minimum delta-v under 6 / under 5 / under 4 km/s | 726 / 286 / 40 |
| SBDB taxonomy | 23 |
| SBDB albedo / diameter | 69 / 70 |
| SBDB taxonomy or albedo or diameter | 82 |
| SBDB rotation period | 306 |
| SBDB A2 (any) / A2 at 3 sigma or better | 169 / 154 |
| SBDB A1 | 18 |
| JPL radar-detected (lower bound) | 226 |
| radar-detected and A2 / radar-detected and rotation period | 41 / 96 |
| Gaia DR3 reflectance spectrum | 3 |

SsODNet check [V]. I pre-selected the 650 NHATS objects that have any physical parameter in SBDB, or a radar detection, or H < 22, and pulled their ssoCards from the IMCCE API. The server was slow, so 477 of the 650 were retrieved before I stopped (the missing 173 are somewhat fainter, median H 25.0 against 23.8).

| In the 477 retrieved | Count |
|---|---|
| with a taxonomic class in SsODNet | 168 (135 from spectra, 33 from photometry) |
| of those, also classified in SBDB | 19 |
| by H bin, classified / retrieved | H < 20: 31/40; 20 to 22: 71/125; 22 to 25: 35/162; H >= 25: 31/150 |
| class mix (first letter) | S 88, X 21, C 18, L 10, Q 6, K 5, A 4, V 4, M 4, D 2, B 2, P 2, E 1, R 1 |
| with an albedo | 101, of which 97 are flagged "Computed property" (derived, not an independent thermal measurement) |
| with colours | 130 |
| with a thermal inertia | 15 |
| with a density | 11: 4 from Yarkovsky drift, 3 from radiation pressure, 1 from both, 2 "computed", 1 from a binary |

Scaling by H bin to all 650 gives **about 220 NHATS objects with a taxonomic class in SsODNet, about 95 of them at H >= 22**. That is roughly ten times SBDB's 23, and still only 3% of the list (about 1.4% of the H >= 22 objects). It is a lower bound, because NHATS objects outside my pre-selection were not queried. Two warnings from the same sample: nearly all SsODNet albedos for these objects are derived values, and 8 of the 11 densities come from the non-gravitational channels this project wants to test.

Gold and near-gold objects that are themselves on the NHATS list [V]: Itokawa, Ryugu, Bennu, Kamo'oalewa, Torifune, Apophis, 1998 KY26, Nereus, 1996 FG3, 2008 EV5, 1989 UQ, 2008 TC3, 2009 BD, 2011 MD, 2012 LA, 2015 TC25, 2020 CD3, 2006 RH120, 2020 GE, 2026 QQ8, 2000 SG344, and the "inner dark comets" 2005 VL1, 2010 RF12, 2010 VL65, 2013 XY20, 2016 GW221, 2016 NJ33.

Note that the bulk SsODNet table (`ssoBFT-latest_Asteroid.parquet`, 856 MB, last modified 22 September 2026, 266 columns) already contains per-object `taxonomy.*`, `albedo`, `density`, `yarkovsky.*`, `source_regions.*` (seven escape regions) and `delta_v` columns [V for the schema]. It is the obvious starting table for channel 3, and it means a per-object source-region probability is already public. Today the file downloaded at about 4 kB/s from this host, so I could not count the whole NEA population from it.

---

## 10. (h) Active or volatile-bearing NEAs

| Object or set | What is known | Truth value for us |
|---|---|---|
| Bennu | Global 2.7 um hydration band; particle ejection events; sample is hydrated and volatile-rich [V/R] | Gold positive for "hydrated carbonaceous" |
| Ryugu | Weak, narrow 2.72 um OH band; sample CI-like, partly dehydrated surface [R] | Gold positive, weaker surface signal |
| (3200) Phaethon | Brightens at perihelion (0.14 au), sodium emission, Geminid parent, B/F type [V] | Active, but thermally driven; not a water-ice indicator |
| (4015) Wilson-Harrington | Coma seen once in 1949, never again [V] | Dormant comet, positive by history |
| (3552) Don Quixote | TJ = 2.32, D-type, pV 0.03, 19 km; activity detected in the near-infrared [V] | Dormant or weakly active comet |
| Dormant comet candidates | Mommert et al. 2015: 23 NEAs with comet-like orbits and pV <= 0.064; 0.3 to 3.3% of NEAs with H <= 21; about 9% of those over 1 km [V]. SBDB today: 2,107 NEAs with TJ < 3, of which 110 have a measured albedo under 0.1 [V] | Silver; about 100 objects; all large |
| Dark comets | 14 objects (Seligman et al. 2023, 2024) [V]. "Outer" (H 16 to 21, comet-like orbits): 2003 RM, 1998 FR11, 2001 ME1, 2005 UY6, 2012 UR158. "Inner" (H 25 to 30, near-circular orbits, all NHATS-like): 1998 KY26, 2005 VL1, 2006 RH120, 2010 RF12, 2010 VL65, 2016 NJ33, 2013 BA74, 2013 XY20, 2016 GW221. The outer ones are defined by a large transverse A2 (2003 RM at 75 sigma); the inner ones mostly by an out-of-plane A3 at 4 to 11 sigma. SBDB today lists A3 for 9 NEAs [V]. | **No confirmed positive.** No coma or gas has been detected on any of them; dust limits are 0.1 to 10 kg/s [V]. The authors note the size split is partly a selection effect. |
| 3-micron hydration on NEAs | McGraw et al. 2022: 8 of 29 NEAs show a band, all 8 are S-complex, linked to aphelion beyond 2.06 au. McGraw et al. 2026: 4 of 15, band depth rises as inclination falls. Earlier: Eros and Ganymed (Rivkin et al. 2018) [V] | About 45 NEAs observed, about 14 detections, almost all on S-types: surface OH from solar wind or exogenic carbonaceous material, not bulk water. Carbonaceous NEAs are too faint and too thermally bright at 3 um for ground-based detection. |

Status of the dark-comet idea as a channel: the flagship object, 1998 KY26, now has an Xe-type spectrum, an albedo near 0.5 and an 11 m size [V]; its A3 was 4.2 sigma in the 2024 paper and is 1.7e-12 +/- 1.1e-12 (1.5 sigma) in SBDB today, after the 2024 apparition astrometry [V]; Bolin et al. 2025 suggest shedding of dust grains by fast rotation instead of water [V]. A detection that faded when more data arrived is exactly the failure a pre-registered significance threshold is meant to catch. 2006 RH120's "anomalous" acceleration is dominated by a radial term consistent with radiation pressure on a metre-sized body. So the dark-comet set is a list of unexplained residuals, some of which have since been explained or are in doubt. It supports an anomaly flag, not a calibrated probability of volatiles.

---

## 11. Methodology: validating calibrated probabilities with tiny, biased truth

### 11.1 What the numbers allow

- **Gold set as a falsification test.** If the catalogue claims 90% for the top class and the true hit rate is p, then with N gold objects a 5% one-sided test rejects with probability: N = 8: 0.45 (p = 0.7), 0.68 (0.6), 0.86 (0.5). N = 12: 0.51, 0.77, 0.93. N = 20: 0.76, 0.95, 0.99. So a dozen gold objects catch gross over-confidence most of the time and nothing subtler [computed today].
- **Reliability diagrams need tens of objects per bin.** Standard error of an observed frequency at p = 0.8 is 0.089 for n = 20, 0.057 for n = 50, 0.040 for n = 100. Four usable bins need 150 to 400 test objects. Only silver labels reach that.
- **Skill detection.** If per-object log-score differences have a spread of about 0.6 bits, a mean gain is detectable at 3 sigma when it exceeds 0.26 bits (N = 50), 0.18 (N = 100), 0.10 (N = 300). The class entropy of the population prior is about 1.3 to 1.5 bits for a four-class split, so 0.1 bits is a modest but real improvement.
- **Density interval coverage.** With N = 18 direct densities, a claimed 68% interval is rejected only if 7 or fewer, or 17 or more, contain the truth. Coverage can be sanity-checked, not tuned.

### 11.2 Hold-out design without leakage

1. **Split by object, not by measurement.** The same NEA appears in MITHNEOS, NEOWISE, SBDB, SsODNet and LCDB. All rows for one designation go to one side.
2. **Group by dynamical cluster.** Pairs, binaries' components and objects in the same tight orbital cluster go together; otherwise an orbit-based prior is tested on near-duplicates.
3. **Channel hold-out.** For each channel, run "this channel alone" and "all channels but this one". A channel is credited only with what it adds over the others. The label channel is always masked: when the label is spectral taxonomy, every spectrum-derived feature (colours, slopes, taxonomy-dependent albedo priors) is removed from the inputs.
4. **No bronze as truth.** Yarkovsky-derived densities, H-derived diameters and family assignments are excluded from truth even when a catalogue presents them as "best values".
5. **In-sample priors are declared.** The debiased class fractions per escape route (Marsset et al. 2022) were derived from MITHNEOS. Testing an orbit-to-class prior on MITHNEOS objects is in-sample. Test it on MANOS, Sanchez 2024, Lopez-Oquendo 2026, NEOROCKS and later spectra, or refit the fractions inside each training fold.
6. **Temporal hold-out.** Freeze inputs at a date. Everything published after it (new MITHNEOS and MANOS spectra, Rubin colours, SPHEREx, new impactors, mission results) is test data that could not have leaked.
7. **Stratify by size.** Report every metric separately for H < 20, 20 to 22, 22 to 25, over 25. The catalogue's value is in the last two bins; a good score driven by the first two is not evidence.

### 11.3 Scoring

- **Classes:** multiclass logarithmic score (in bits) as the primary metric, Brier score as secondary; both are proper scoring rules (Gneiting and Raftery 2007). Report skill relative to baselines, with bootstrap intervals resampled by object.
- **Baselines, fixed in advance:** B0, the debiased population class mix for the object's size bin; B1, orbit only (escape-route probabilities times per-route debiased class fractions); B2, "always the majority class". A published orbit-only benchmark exists: a random forest on orbital elements reached about 53% spectral-type accuracy in one AI-agent study (arXiv 2510.26887) [V that the figure is reported; I did not check which population it was run on].
- **Calibration:** reliability diagram with per-bin intervals; expected calibration error; for densities and other continuous outputs, PIT histogram, CRPS, and central-interval coverage at 68% and 95%. For stated upper bounds (Yarkovsky density caps), the violation rate.
- **Noisy labels.** Silver labels are themselves uncertain (S vs Q, X-complex, visible-only spectra). Either score against soft labels (the class probabilities that Mahlke-style classifiers output) or restrict the sealed test to labels from full visible-plus-near-infrared spectra and report how many objects that leaves. A method cannot be shown to be better calibrated than its labels are accurate, so the label error rate sets a floor on measurable miscalibration.
- **Noisy labels.** Silver labels are themselves uncertain (S vs Q, X-complex, visible-only spectra). Either score against soft labels (the class probabilities that Mahlke-style classifiers output) or restrict the sealed test to labels from full visible-plus-near-infrared spectra and report how many objects that leaves. A method cannot be shown to be better calibrated than its labels are accurate, so the label error rate sets a floor on measurable miscalibration.
- **Guard against gamed metrics.** The LSST photo-z challenge (Schmidt et al. 2020) showed that ensemble calibration metrics can look fine for a useless estimator and recommended a per-object loss when truth is available. Always pair calibration with a per-object proper score.
- **Selection-bias correction.** Estimate weights w = p_target(x) / p_labelled(x) over H, orbit, and discovery circumstances with a domain classifier (the photo-z community's nearest-neighbour reweighting, Lima et al. 2008, is the direct analogue), cap the weights, and report the effective sample size next to every weighted metric. If the effective N at H > 24 falls under about 30, say that the metric is not measurable there.
- **Label shift.** The class mix differs between labelled and target sets. Treat the debiased class mix by size as an explicit prior that can be swapped, and show how the catalogue changes under two or three plausible priors (Marsset 2022; MANOS; Lopez-Oquendo 2026). Black-box shift estimation (Lipton et al. 2018) is the standard tool if a formal estimate is wanted.

### 11.4 The catalogue-fusion analogue of injection-recovery

1. **Synthetic population, end to end.** Draw objects from a debiased population model (NEOMOD3 provides orbits, sizes and albedos, Nesvorny et al. 2024), assign class by escape route, density by class, spin and thermal properties from priors; pass them through the real observational selection (survey cadence, magnitude limits, astrometric noise, the observed distribution of arc lengths and numbers of observations for NHATS objects); produce mock catalogue rows with the same missingness as the real ones; run the pipeline blind; score. This is simulation-based calibration (Talts et al. 2018) applied to the whole pipeline, and it is how RAVEN trains and tests exoplanet validation (synthetic planets and eight false-positive scenarios injected into real light curves; AUC over 97%; 91% accuracy on 1,361 pre-classified TOIs; 97% precision at 66% recall for threshold 0.9) [V].
2. **Degrade a known object.** Take objects with long arcs and independent truth (Bennu, Itokawa, Ryugu, Apophis, Golevka, 2000 DP107, Moshup) and cut their data down to what a typical NHATS object has: one or two apparitions, 30 to 100 observations, no radar. Re-run the orbit fit and the inference. The posterior should widen and still cover the full-data answer. This is the closest thing to injecting a signal into real data, and it uses real systematics.
3. **Synthetic signals in real astrometry.** Add a known A2 or A1 to the real residuals of objects that should have none (kilometre-sized NEAs), refit, and measure recovery and false-alarm rates as a function of arc and observation count.
4. **Negative controls.** Objects where the answer must be null: A2 for bodies over 5 km; "volatile acceleration" for main-belt objects; artificial objects (2020 SO and similar) that must come out as extreme area-to-mass outliers and not as low-density asteroids; time-scrambled astrometry.
5. **Recover known objects first.** Reproduce JPL's A2 for the 351 NEAs with snr >= 5 and the 21 A1 values before deriving anything new; reproduce published taxonomy for objects with spectra from colours alone.

### 11.5 Pre-registration and null results

- Register, before any model is fitted: the class scheme and the mapping from taxonomy to class; the truth table with tiers; the sealed test list (publish a hash of the designations and reveal later); baselines; metrics; thresholds for "works"; the stratification bins; the stopping rule. A dated git tag plus a Zenodo or OSF deposit is enough.
- Publish each channel's result whether or not it clears the bar, with the same figures. A channel whose skill interval includes zero is reported as "no detectable information at this sample size", with the sample size that would be needed.
- Fresh-agent adversarial review should be given the truth table and asked to find leakage paths specifically (shared provenance between a feature and a label).

### 11.6 How comparable projects did it

- **Mahlke et al. 2022:** unsupervised latent-variable model; probabilistic classes that widen when wavelength coverage or albedo is missing; validated by comparison with earlier taxonomies and by class-degeneracy analysis, not by held-out truth, because there is no truth for taxonomy [V for the description from the abstract; R for the validation detail].
- **Marsset et al. 2022:** analytic albedo debiasing in two H bins, validated by showing that debiased NEO fractions per escape route match the main belt near each route (for example nu6: S+Q 44.4% debiased vs 40.5% in the belt) [V]. External consistency, not hold-out.
- **NEOMOD (Nesvorny et al. 2023 to 2024):** forward model fitted to Catalina detections with a detailed bias model, then to NEOWISE albedos; an independent debiased population built from ATLAS (arXiv 2409.10453) is the natural external comparison [V that both exist; R on how closely they agree]. The authors note that only 428 cryogenic NEOWISE detections constrain the albedo model and that it is extrapolated below 100 m [V].
- **ExoMiner (Valizadegan et al. 2022):** supervised; reports recall at fixed 99% precision (93.6%), and shows an existing validator would have mis-validated 21.9% of known false positives [V].
- **RAVEN (2025):** as above; synthetic training set to cover parameter space the labelled set does not reach, then an external labelled test set [V].
- **Chesley et al. 2014 on Bennu:** a published quantitative prediction scored by a later spacecraft. This is the model for the prospective part of this project.

---

## 12. Recommended validation protocol

**Step 0. Build the truth table** (a deliverable in its own right). One row per object and quantity, with value, error, method, reference, tier, independence flags. Start from sections 2 to 10. Resolve the conflicts listed there by going to the primary papers.

**Step 1. Fix the class scheme and label mapping.** For example: stony (S, Q, V, A, K, L and OC/HED analogues), carbonaceous (C, B, Ch, D, P with pV under 0.1), metal-rich or enstatite (M and E, which need albedo or radar to separate), other. State which taxonomic classes are ambiguous and score them as partial credit or exclude them, decided in advance.

**Step 2. Seal the test sets.**
- Gold exam (never touched): the roughly 12 composition-gold objects and the roughly 18 direct densities.
- Silver sealed test: stratified by H bin and class, grouped by object and dynamical cluster. It needs at least 150 objects at H >= 22. My rough estimate is that 400 to 500 distinct NEAs at H >= 22 have any spectral or colour class (MANOS 210, Lopez-Oquendo 122, parts of NEOShield-2, Sanchez 2024, NEOROCKS and the MITHNEOS tail, with overlaps) [U], so the sealed share at small sizes has to be about a third, larger than the 20% that suffices for bright objects.
- Prospective list: every NHATS object, with predictions frozen and timestamped.

**Step 3. Recover knowns.** JPL A2 and A1 values; published taxonomy from colours; Bennu's density from pre-2018 data only.

**Step 4. Synthetic and degradation tests** (section 11.4), with pass thresholds fixed in advance.

**Step 5. Cross-validated development on the silver training portion,** with channel-ablation runs.

**Step 6. One-shot evaluation on the sealed silver test, then the gold exam.** No changes afterwards without a new version number and a new sealed set.

**Step 7. Publish everything,** including channels that failed, and keep a public scoreboard of prospective predictions.

Prospective truth calendar (what to register now, and when it gets scored):

| Object or stream | Truth expected | When | What to predict now |
|---|---|---|---|
| Kamo'oalewa | Close-range mapping, then returned sample | Mapping to April 2027; capsule November 2027 | Class (LL-like vs lunar-like), bulk density from the 7-sigma A2 and the new 15 to 21 m size |
| Dimorphos and Didymos | Mass of Dimorphos from Hera radio science and the Juventas gravimeter; requirement 10%, goal 1%; CubeSats deploy early 2027; closest passes about 1 km in June to July 2027 [V for the plan, no result date published] | 2027 | Dimorphos density (published expectation 1.54 +/- 0.22) |
| Torifune | Hayabusa2 flyby results: NIRS3 (1.8 to 3.2 um, OH), thermal imager, shape | When JAXA publishes | Class analogue for an L-type, presence or absence of a hydration band |
| Apophis | OSIRIS-APEX after April 2029 | 2029 to 2030 | Bulk density from the 153-sigma A2 |
| 1998 KY26 | Hayabusa2 rendezvous | 2031 | Class (enstatite-like vs carbonaceous), density |
| New imminent impactors | Fireball strength, sometimes meteorites | 0 to 4 per year lately | Class probabilities from the orbit alone, registered within hours |
| New spectra and colours | MITHNEOS, MANOS, Rubin, SPHEREx, JWST | Continuous | Class probabilities for every NHATS object, frozen and timestamped |

Prospective truth calendar (what to register now, and when it gets scored):

| Object or stream | Truth expected | When | What to predict now |
|---|---|---|---|
| Kamo'oalewa | Close-range mapping, then returned sample | Mapping to April 2027; capsule November 2027 | Class (LL-like vs lunar-like), bulk density from the 7-sigma A2 and the new 15 to 21 m size |
| Dimorphos and Didymos | Mass of Dimorphos from Hera radio science and the Juventas gravimeter; requirement 10%, goal 1%; CubeSats deploy early 2027; closest passes about 1 km in June to July 2027 [V for the plan, no result date published] | 2027 | Dimorphos density (published expectation 1.54 +/- 0.22) |
| Torifune | Hayabusa2 flyby results: NIRS3 (1.8 to 3.2 um, OH), thermal imager, shape | When JAXA publishes | Class analogue for an L-type, presence or absence of a hydration band |
| Apophis | OSIRIS-APEX after April 2029 | 2029 to 2030 | Bulk density from the 153-sigma A2 |
| 1998 KY26 | Hayabusa2 rendezvous | 2031 | Class (enstatite-like vs carbonaceous), density |
| New imminent impactors | Fireball strength, sometimes meteorites | 0 to 4 per year lately | Class probabilities from the orbit alone, registered within hours |
| New spectra and colours | MITHNEOS, MANOS, Rubin, SPHEREx, JWST | Continuous | Class probabilities for every NHATS object, frozen and timestamped |

### Minimum result that counts as "this channel works"

For a **class-probability channel** (orbit-to-source prior; sparse colours and albedo; new survey photometry):

1. On the sealed silver test, importance-weighted mean log-score gain over baseline B0 of at least 0.10 bits per object, bootstrap 95% interval excluding zero, and the same sign in the H >= 22 stratum.
2. Reliability: in each probability bin holding at least 30 objects, observed frequency within 0.10 of predicted.
3. Gold exam: no gold object's true class given less than 5% probability, and mean log score better than B0 (direction only; no significance is claimed at N of about 12).
4. End-to-end synthetic test: stated 68% and 95% credible sets contain the injected truth 68 +/- 8% and 95 +/- 4% of the time.

For the **Yarkovsky density channel:**

1. Recovery: the pipeline's A2 agrees with JPL's within 2 combined sigma for at least 90% of the 351 NEAs with snr >= 5.
2. Degradation: for the truncated-arc tests, 68% and 95% intervals cover the full-arc value at the stated rates over at least 200 trials.
3. Truth: for the 8 or 9 objects with independent density and a 3-sigma A2, the stated 95% upper bound is violated at most once, and the RMS of log10(predicted / true) is under 0.3 dex. Toutatis and other tumblers must be either handled or excluded by a rule written in advance.
4. Prospective: predictions for Kamo'oalewa, Apophis and 1998 KY26 published before their truth arrives.

For the **SRP channel:** recover the published A1 for the eight clear detections within 2 sigma; flag every known artificial object in a blind mixed list; report area-to-mass, and report density only as a function of an explicit size prior.

For the **dark-comet or volatile channel:** there is no truth to pass. It may ship only as an anomaly flag with a false-alarm rate measured on negative controls, not as a probability of volatiles.

A channel that misses these bars is reported as a null result with its measured interval.

---

## 13. What has already been done, what will not work, where the gap is

Already done by others:

- Per-object escape-route probabilities and delta-v for all NEAs are in SsODNet's bulk table [V].
- Debiased class fractions per escape route (Marsset et al. 2022) and, in 2026, source regions per taxonomic class (Dorsey and Granvik, EPSC 2026 abstract) [V]. The abstract states the limit plainly: an individual NEO cannot be traced to a source, and per-object source estimates over-weight the dominant sources.
- Yarkovsky-to-density for about 50 NEAs (Dziadura et al. 2023, 2025) [V].
- Probabilistic taxonomy with missing data (Mahlke et al. 2022) [V].
- Small-NEO debiased composition (MANOS 2019; Lopez-Oquendo et al. 2026) [V].

Will not work, or will mislead:

- Calibrating on gold truth alone (N too small).
- Treating taxonomy as composition, especially X-complex and "C equals water".
- Using catalogue densities as truth.
- Validating a metal-rich probability on NEAs (one confirmed positive).
- Validating a volatile probability from non-gravitational residuals (zero confirmed positives; flagship case in doubt).
- Trusting H-derived sizes for tens-of-metres objects (2 of 2 checked cases off by 2 to 3 times).
- Quoting an overall accuracy dominated by H < 22 objects.

The real gap:

- Nobody has published a per-object, calibrated, scored catalogue for the mission-accessible list, with sealed tests and prospective predictions. The pieces exist; the validation layer and the truth table do not.
- A curated NEA truth table with tiers and independence flags does not exist publicly.
- The radar-detected NHATS subset (at least 226 objects) has not been mined systematically for SC/OC and radar-albedo class hints.

---

## 14. Things I could not verify

- The CDS copy of the 824-fireball catalogue (404 page and TAP timeout from this host today).
- The smass.mit.edu access path for MITHNEOS spectra (connection refused from this host today).
- The designations of the high-radar-albedo NEAs in Virkki et al. 2022.
- The "Farnocchia 2025" reference behind SsODNet's 1998 KY26 density.
- Whether DFN/GFO orbits are publicly downloadable in bulk.
- A final NEOWISE unique-NEO count after the November 2024 release.
- Whether any 2022 WJ1 meteorite was recovered after the ESA page was written.
- Several classic densities are quoted from memory and cross-checked only against SBDB or SsODNet (marked [R]).

---

## Sources

Missions and spacecraft truth
- JAXA press release, Hayabusa2 Torifune flyby (6 July 2026): https://global.jaxa.jp/press/2026/07/20260706-3_e.html
- Sci.News on Torifune images: https://www.sci.news/space/hayabusa-2-close-up-images-asteroid-torifune-14902.html
- Planetary Society, Tianwen-2 arrival (24 June 2026): https://www.planetary.org/articles/chinas-tianwen-2-mission-has-probably-arrived-at-a-quasi-moon-of-earth
- Astronomy.com, Tianwen-2 arrives (15 July 2026): https://www.astronomy.com/space-exploration/tianwen-2-arrives-at-target-asteroid-kamo%CA%BBoalewa/
- Sky and Telescope, Tianwen-2 images: https://skyandtelescope.org/astronomy-news/tianwen-2-arrives-at-quasi-moon-kamo%ca%bboalewa-returns-images/
- Sharkey et al. 2026, JWST characterisation of Kamo'oalewa: https://arxiv.org/abs/2606.24017
- Zhang et al. 2026a, Kamo'oalewa LL composition: https://arxiv.org/abs/2603.28102
- Zhang et al. 2026b, Kamo'oalewa shape and regolith: https://arxiv.org/abs/2603.28107
- ESA, Hera in rectangular orbit around Didymos (11 November 2026): https://www.esa.int/articles/hera-spacecraft-in-rectangular-orbit-around-target-asteroids
- Makadia et al. 2026, Didymos heliocentric deflection and densities: https://pmc.ncbi.nlm.nih.gov/articles/PMC12965290
- Raducan et al. 2024, Dimorphos properties: https://arxiv.org/abs/2403.00667
- Reddy et al. 2012, Toutatis composition: https://arxiv.org/abs/1210.2853
- Santana-Ros et al. 2025, 1998 KY26 (Nature Communications): https://doi.org/10.1038/s41467-025-63697-4 ; ESO release https://eso.org/public/news/eso2515/
- Bolin et al. 2025, 1998 KY26 Keck and Gemini: https://arxiv.org/abs/2501.17156
- Phobos 1 hypothesis preprints: https://arxiv.org/abs/2606.01288 , https://arxiv.org/abs/2609.24283
- Tasker, Connolly, Tachibana 2026, sample-return review: https://arxiv.org/abs/2604.22182
- Bennu vs Ryugu vs CI: https://pmc.ncbi.nlm.nih.gov/articles/PMC12708356
- Chesley et al. 2014 Bennu Yarkovsky density (cited in): https://www.aanda.org/10.1051/0004-6361/202347342

Imminent impactors
- ESA NEOCC past impactors: https://neo.ssa.esa.int/past-impactors ; 2026 JN4 https://neo.ssa.esa.int/past-impactors/2026jn4 ; 2026 RW1 https://neo.ssa.esa.int/past-impactors/2026rw1
- ESA NEOCC newsletter June 2026: https://neo.ssa.esa.int/documents/d/guest/newsletter-june-2026
- Wikipedia list of predicted impacts: https://en.wikipedia.org/wiki/List_of_predicted_asteroid_impacts_on_Earth
- Chow et al. 2026, imminent impactors and LSST: https://arxiv.org/abs/2603.05587
- Jenniskens et al. 2009, 2008 TC3: https://www.doi.org/10.1038/NATURE07920
- Kareta et al. 2024, 2022 WJ1: https://arxiv.org/abs/2411.14595
- Egal et al. 2025, 2023 CX1: https://arxiv.org/abs/2509.12362
- Spurny et al. 2024, 2024 BX1 / Ribbeck: https://arxiv.org/abs/2403.00634
- Devogele et al. 2024, trail photometry and 2.5888 s rotation: https://arxiv.org/abs/2404.04142
- Ingebretsen et al. 2025, 2024 RW1: https://arxiv.org/abs/2505.23736
- Gianotto et al. 2025, 2024 XA1: https://arxiv.org/abs/2502.09712
- 2018 LA / Motopi Pan: https://www.knmi.nl/research/publications/the-impact-and-recovery-of-asteroid-2018-la
- Watchers.news on 2026 RW1: https://watchers.news/2026/09/07/asteroid-2026-rw1-impacts-earth-over-indian-ocean-september-6-2026-13th-predicted-impactor/

Meteorites and fireballs
- Meier, meteorites with photographic orbits: https://www.meteoriteorbits.info/ ; JSON https://www.meteoriteorbits.info/wp-json/wp/v2/pages/5
- Granvik and Brown 2018: https://arxiv.org/abs/1804.07229
- Jenniskens and Devillepoix 2025: https://dfn.gfo.rocks/documents/papers_reprints/Jenniskens_2025_review_meteorite_sources.pdf
- Marsset et al. 2024, Massalia and L chondrites: https://ui.adsabs.harvard.edu/abs/2024Natur.634..561M
- Shober et al. 2025: https://arxiv.org/abs/2504.10690
- Borovicka et al. 2022 I and II: https://arxiv.org/abs/2209.11186 , https://arxiv.org/abs/2209.11254 ; CDS https://cdsarc.cds.unistra.fr/ftp/J/A+A/667/A157
- FRIPON: https://arxiv.org/abs/2012.00616 ; https://fireball.fripon.org/list_pipeline.php
- Global Fireball Observatory: https://arxiv.org/abs/2004.01069
- CNEOS fireballs: https://cneos.jpl.nasa.gov/fireballs/intro.html ; API https://ssd-api.jpl.nasa.gov/fireball.api

Radar, densities, non-gravitational
- JPL radar-detected asteroids: https://echo.jpl.nasa.gov/asteroids/ (list at https://echo.jpl.nasa.gov/asteroids/alldetections.html)
- Virkki et al. 2022: https://www.helsinki.fi/en/news/space/arecibo-observatory-scientists-publish-major-study-near-earth-asteroids ; DOI 10.3847/PSJ/ac8b72
- Benner et al. 2008: https://experts.arizona.edu/en/publications/near-earth-asteroid-surface-roughness-depends-on-compositional-cl/
- PDS Asteroid Radar V18.0: https://catalog.data.gov/dataset/asteroid-radar-v18-0-a0dec
- Sanchez et al. 2021, 1986 DA and 2016 ED85: https://arxiv.org/abs/2109.13950
- Johnston's Archive, asteroids with satellites: https://www.johnstonsarchive.net/astro/asteroidmoons.html
- Pravec binary parameters (archived): https://webarchiv.lib.cas.cz:443/wayback/20200705035848/http://www.asu.cas.cz/~asteroid/binastdata.htm
- Dziadura et al. 2023: https://ui.adsabs.harvard.edu/abs/2023A&A...680A..77D ; follow-up https://web3.arxiv.org/pdf/2411.09750
- Hanus et al. 2018, Phaethon density: https://ui.adsabs.harvard.edu/abs/2018A&A...620L...8H
- Rozitis et al. 2013, Apollo: https://www.arxiv.org/abs/1305.3109
- Mommert et al. 2014, 2009 BD: https://www.doi.org/10.1088/0004-637X/786/2/148 ; 2011 MD: https://arxiv.org/abs/1406.5253
- Fedorets et al. 2020, 2020 CD3: https://arxiv.org/abs/2011.10380
- Seligman et al. 2023, dark comets: https://arxiv.org/abs/2212.08115 ; Seligman et al. 2024: https://www.arxiv.org/abs/2412.07603
- Taylor et al. 2024, strong non-gravitational accelerations: https://arxiv.org/abs/2410.06874
- SsODNet ssoCard API: https://ssp.imcce.fr/webservices/ssodnet/api/ssocard/Bennu ; bulk table https://ssp.imcce.fr/data/ssoBFT-latest_Asteroid.parquet

Label sets
- Binzel et al. 2019, MITHNEOS: https://arxiv.org/abs/2004.05090
- Marsset et al. 2022, debiased MITHNEOS: https://arxiv.org/abs/2202.13796
- Devogele et al. 2019, MANOS: https://arxiv.org/abs/1909.04788
- Perna et al. 2018, NEOShield-2: https://arxiv.org/abs/1803.08953
- Hromakina et al. 2023, NEOROCKS: https://arxiv.org/abs/2302.01165
- Sanchez et al. 2024, small NEOs: https://arxiv.org/abs/2404.18263
- Lopez-Oquendo et al. 2026: https://arxiv.org/abs/2608.28779
- Mahlke et al. 2022: https://arxiv.org/abs/2203.11229
- Masiero et al. 2021, NEOWISE years 6 and 7: https://iopscience.iop.org/article/10.3847/PSJ/ac15fb ; NEOWISE releases https://irsa.ipac.caltech.edu/data/WISE/docs/release/NEOWISE/
- Trilling et al. 2016, NEOSurvey: https://arxiv.org/abs/1608.03673
- Mommert et al. 2015, dormant comets: https://arxiv.org/abs/1508.04116
- McGraw et al. 2022: https://experts.nau.edu/en/publications/3-%CE%BCm-spectroscopic-survey-of-near-earth-asteroids/ ; McGraw et al. 2026: https://arxiv.org/abs/2602.00430
- Jewitt and Hsieh 2022, active asteroids: https://ar5iv.labs.arxiv.org/html/2203.01397
- Gaia TAP: https://gea.esac.esa.int/tap-server/tap
- JPL SBDB Query API: https://ssd-api.jpl.nasa.gov/sbdb_query.api ; NHATS API: https://ssd-api.jpl.nasa.gov/nhats.api

Methodology
- Dorsey and Granvik 2026, EPSC abstract: https://meetingorganizer.copernicus.org/EPSC2026/EPSC2026-1111.html
- Nesvorny et al. 2024, NEOMOD3: https://arxiv.org/abs/2404.18805 ; ATLAS debiased population: https://arxiv.org/abs/2409.10453
- RAVEN: https://arxiv.org/abs/2509.17645
- ExoMiner: https://arxiv.org/abs/2111.10009
- Denario project (orbit-only taxonomy at about 53%): https://arxiv.org/abs/2510.26887
- Schmidt et al. 2020, photo-z PDF evaluation: https://arxiv.org/abs/2001.03621
- Lima et al. 2008, reweighting: https://arxiv.org/abs/0801.3822
- Lipton et al. 2018, label shift: https://arxiv.org/abs/1802.03916
- Talts et al. 2018, simulation-based calibration: https://arxiv.org/abs/1804.06788
- Guo et al. 2017, calibration: https://arxiv.org/abs/1706.04599
- Gneiting and Raftery 2007, proper scoring rules: https://doi.org/10.1198/016214506000001437
