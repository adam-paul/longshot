# Novelty and prior-art sweep, searched by application

Date of sweep: 2026-11-20. Scope: anything that already does what the proposed "NEA prospect catalog" would do (per-object, probabilistic composition class, density and resource relevance for mission-accessible near-Earth asteroids, validated against known answers, produced by AI agents on public data, published as an interactive site).

Status flags used below:

- **[V]** verified today: I fetched the primary page, abstract, PDF or API in this session.
- **[S]** search-summary only: a search engine's summary of the primary source, not the source itself. Treat numbers as likely right but unconfirmed.
- **[R]** recalled from memory, not checked.
- **[U]** could not verify.

## 0. Bottom line

1. **No one has published the exact product** (a per-object composition posterior joined to NHATS accessibility, with stated calibration). I found no such catalog in arXiv title/abstract searches (ten queries, 2011 to Nov 2026), EPSC/DPS 2025 and 2026 abstracts, company material, or agency products.
2. **Every ingredient exists, most of them from the people who would referee this.** Probabilistic taxonomy from partial data (Mahlke 2022; Mommert 2016; Dotson & Mathias 2017), orbit to source region to family to meteorite class (Granvik 2018; Brož 2024 and the public METEOMOD tool), orbit plus size to taxonomy to water for low-delta-v NEOs (Jedicke 2018), population counts of hydrated and ore-bearing NEOs (Elvis 2014; Rivkin & DeMeo 2019; USGS 2017), Yarkovsky densities for about 50 NEAs (Dziadura 2023), metal-rich flags from thermal data (Harris & Drube 2014), and interactive ranking sites (Asterank since 2012; ECOCEL 2022).
3. **The measured answer for the target population already exists and it is awkward for priors.** MANOS has spectra for 210 and colors for 189 mission-accessible small NEOs. The S-complex fraction falls from about 65% at km scale to about one third below 50 m, and X-complex rises. The UKIRT survey (122 NEOs, 5 to 150 m) says the debiased small population is dominated by dark C/X objects. Sanchez 2024 (84 spectra, under 300 m) says 66% S-complex. The "known answers" disagree with each other.
4. **Orbit-only priors are known to be weak**, and the people who built the models say so. NEO orbit space is "well mixed" in albedo (Morbidelli 2020). Applied to small NEOs, METEOMOD gave a maximum source probability above 50% for only about 20% of objects (López-Oquendo 2026) [S]. For NHATS-like orbits the source posterior is nearly the same for every object (about 83% nu6 in Sanchez 2024).
5. **The defensible open parts are about calibration and forecasting, not about a new physical method**: (a) a scored, held-out test of how much information orbit, H and sparse data really add for small NEOs, null result included; (b) a time-stamped forward forecast for the NHATS list, scored as Rubin, NEO Surveyor, SPHEREx and Euclid labels arrive; (c) the joined, public, uncertainty-first catalog itself, with an "observe this next" ranking.
6. **AI-agent minor-planet work in 2026 is discovery claims with no published validation.** Depue, Wolk and Farritor's dwarf-planet candidates have no designation, write-up or professional comment that I could find. The Minor Planet Center's October 2026 newsletter warns about AI-assisted submissions. No agent-driven work on asteroid composition or resources was found.
7. **One framing claim in the brief will not survive a referee**: "none of the 286 has a taxonomy class in SBDB" is true (I re-ran it today) but SBDB holds a spectral type for only 327 of 43,360 NEOs. The literature has over 1,000 spectroscopic and thousands of photometric classifications. The claim has to be re-made against SsODNet, MANOS, UKIRT and Sergeyev 2023 before it is used.

## 1. Baseline numbers re-checked today

| Fact | Value | Status | Source |
|---|---|---|---|
| NHATS objects (default limits: dv <= 12 km/s, dur <= 450 d) | 7,226 | [V] | https://ssd-api.jpl.nasa.gov/nhats.api |
| NHATS objects with minimum round-trip dv < 5 km/s | 286 | [V] | same |
| ... dv < 4 km/s / < 6 / < 8 | 40 / 726 / 2,196 | [V] | same |
| Median H of NHATS list; count with H >= 24; H >= 26 | 26.2; 6,386; 3,970 | [V] | same |
| NHATS objects with a spectral type in JPL SBDB (spec_B or spec_T) | 23 of 7,226 | [V] | https://ssd-api.jpl.nasa.gov/sbdb_query.api?fields=pdes,spec_B,spec_T,albedo,diameter,H&sb-group=neo |
| ... among the 286 with dv < 5 | 0 taxonomy, 0 albedo | [V] | same |
| ... among the 726 with dv < 6 | 0 taxonomy, 2 albedo | [V] | same |
| All NEOs in SBDB / with any SBDB spectral type / with SBDB albedo | 43,360 / 327 / 1,209 | [V] | same |
| Lowest-dv NHATS entries today | 2026 QQ8 (3.345 km/s, H 31.4, a temporarily captured minimoon), 2021 GM1, 2023 FY3, 2022 RD2, 2022 OB5 (3.517, AstroForge's named Odin target), 2000 SG344, 2020 CD3 (minimoon), 2024 PT5 (reported lunar ejecta) | [V] | NHATS API; see sections 3 and 5 for the object notes |

The NHATS API also returns the next optical observing window (obs_start, obs_end, obs_mag) and radar SNR fields per object. NHATS is already a "when can I characterize it" service. It has no composition field. [V]

An older benchmark: Popescu et al. 2019 wrote that NHATS then listed 1,382 targets and fewer than 5% had a compositional characterization. [S] https://arxiv.org/pdf/1905.12997

## 2. (a) Probabilistic or learned composition from sparse or indirect data

| Work | What it did | Objects | Validation | Public? | Overlap with the project |
|---|---|---|---|---|---|
| Mahlke, Carry & Mattei 2022, A&A 665, A26 ("classy") | Taxonomy by mixture of common factor analysers. Classifies partial spectra (visible only, NIR only, or both), uses albedo, gives probabilistic class assignments. 17 classes. | 2,983 observations of 2,125 asteroids | Cluster recovery against previous taxonomies | Classes at CDS; Python tool | High for the "fuse sparse spectra and albedo" channel. It is the reference implementation. [V] https://arxiv.org/abs/2203.11229 |
| Dotson & Mathias 2017 (NASA Ames), "A Framework for Inferring Taxonomic Class of Asteroids" | Bayes: P(class given albedo) from population class fractions (prior) and per-class albedo distributions (likelihood). Stated purpose: prioritizing objects and threat assessment. | Method abstract | Not described in abstract | NTRS abstract | High for the albedo-only channel. [V] https://ntrs.nasa.gov/citations/20170009812 |
| Dotson, Wheeler, Rumpf, Mathias 2019 to 2023 (Ames asteroid property inference network) | Bayesian network linking albedo, taxonomy, diameter, porosity, grain density, bulk density, strength. Used in the PDC 2021, 2023 and 2025 hypothetical-impact exercises. | Per-object, for impact scenarios | Exercise use; no peer-reviewed paper found | Conference abstracts and slides | High in structure: this is "per-object probabilistic class and density from sparse data" for planetary defence. [S] https://ui.adsabs.harvard.edu/abs/2020AGUFMNH0370002D/abstract , https://cneos.jpl.nasa.gov/pd/cs/pdc25/PDC25-Epoch2-physical_properties.pdf |
| Deshapriya et al. 2023, A&A 674, A50 | Asks whether an NEO's class can be guessed at discovery from orbit alone. G-mode clustering of orbital elements; gives orbital regimes mapped to "primitive" (B, C, D) or "siliceous" (S, Q). | NEO dataset at CDS (J/A+A/674/A50) | Dynamical model check; no probabilistic scoring reported in the abstract | Catalog at CDS | Direct hit on channel 2 at the rule level. Not calibrated probabilities. [S] https://www.aanda.org/articles/aa/abs/2023/06/aa45316-22/aa45316-22.html |
| Jedicke et al. 2018, PSS 159, 28 | Combined an NEO orbit and size model, NEO provenance, and the taxonomy of main-belt sources to get **taxonomic mix as a function of NEO orbit and size**, then assigned classes to a synthetic low-dv population and applied meteorite-analog water contents. | Synthetic population; "likely thousands of H2O-rich NEOs larger than about 5 m" with return-trip dv below about 3 km/s | Agreement with measured C to S ratio among small NEOs | Paper only | Very high. This is the project's channel 2 plus resource step, done at population level in 2018. It does not give per-object posteriors for real NHATS objects. [V abstract] https://scholarsmine.mst.edu/geosci_geo_peteng_facwork/1362 |
| Granvik et al. 2018 NEO model; ESA NEOPOP | Per-object probability of escape from 7 source regions (nu6, 3:1, 5:2, 2:1, Hungaria, Phocaea, JFC). NEOPOP writes source and albedo per synthetic object. | All NEO orbits | Debiased fit to Catalina | Public generator | The standard source-region prior. [S] https://neo.ssa.esa.int/neo-population-generator |
| Morbidelli et al. 2020, Icarus 340 | Debiased NEO albedo distribution on top of Granvik 2018. "Low and high albedo NEOs are well mixed in orbital space", with a trend to higher albedo at small semimajor axis. Reference albedo 0.147. | Fit to NEOWISE | NEOWISE | Paper | Gives the albedo prior by orbit and says how weak it is. [V abstract] https://arxiv.org/abs/2001.03550 |
| Nesvorný et al. 2024, NEOMOD3, Icarus 417 | Debiased size and albedo model. Albedo as two Rayleigh distributions (scale about 0.03 and 0.17). Evidence that smaller NEOs have higher mean albedo. Albedo below 100 m is extrapolated. | Fit to NEOWISE plus Catalina | Survey fits | Public simulator | Same role as above, newer. [S] https://arxiv.org/abs/2404.18805 |
| Binzel et al. 2019 (MITHNEOS), Icarus 324 | Spectra for more than 1,000 NEOs; taxonomy against escape-region probabilities. | >1,000 NEOs | Survey | Data public | The core training and test set. [V abstract] https://arxiv.org/abs/2004.05090 |
| Marsset et al. 2022, AJ 163, 165 | Debiased compositional distribution: S and Q fractions fall and carbonaceous fractions rise with escape-route distance from the Sun. D-type excess from 5:2. | 491 spectra of 420 NEOs plus Binzel 2019 | Bias correction | CDS | Establishes the orbit to composition gradient the project wants to use. [V abstract] https://arxiv.org/abs/2202.13796 |
| Dorsey & Granvik, EPSC2026-1111 | Building **class-specific NEO orbit models** so each taxonomic class gets a probabilistic source assessment. States that tracing a single NEO back is impossible, that about 1,000 NEOs have spectroscopic taxonomy, that LSST will give griz for about 4,000 NEOs with D >= 10 m, and Euclid NIR taxonomy for about 10^4 NEOs with i >= 15 deg. | In progress | n/a | Abstract | A live competitor on the orbit to class prior, by the author of the NEO model (who is also a co-author on Karman+ abstracts, see section 3). [V] https://meetingorganizer.copernicus.org/EPSC2026/EPSC2026-1111.html |
| Brož et al. 2024, A&A 689, A183, and METEOMOD web tool | Contributions of 38 families to metre- and km-sized NEOs. Adeona is the main source of CM-like NEOs; Polana and Euphrosyne of CI-like. METEOMOD takes (a, e, i) and returns a probability per source for about 50 families grouped by meteorite class (H, L, LL, CM, CI, CO/CV/CK, M, E). Code downloadable. | Any orbit | Meteorite falls with orbits | Yes | **This is channel 2 as a public tool already.** Built for metre-size bodies. [S paper] https://arxiv.org/abs/2406.19727 ; [V tool] https://sirrah.troja.mff.cuni.cz/~mira/meteomod/meteomod.php |
| López-Oquendo, Trilling, Mommert, Marsset 2026 (accepted PSJ) | UKIRT ZJHK rapid-response survey 2016 to 2024, ML classifier with probabilistic classes, debiased by size. Observed sample about half S, half C/X; debiased population dominated by C/X. Applied METEOMOD per object. | 122 NEOs, about 5 to 150 m, median 60 m | Debiasing; meteorite fall statistics | arXiv | The closest existing "probabilistic classes for decametre NEOs plus per-object source family" paper. Reported that only about 20% of objects had a maximum source probability above 50%, and 54% pointed to Massalia [S for those two numbers]. [V abstract] https://arxiv.org/abs/2608.28779 |
| Mommert et al. 2016, AJ 151, 98; Erasmus et al. 2017 | Rapid-response NIR colors with ML giving a probability per taxon (86 NEOs); KMTNet VRI for 39 NEAs, 31 confidently classed. | 86; 39 | Compared with spectral libraries | Papers | Established probabilistic photometric taxonomy for tiny NEOs a decade ago. [S] https://arxiv.org/abs/1602.06000 , https://arxiv.org/pdf/1709.03305 |
| Sergeyev, Carry et al. 2023, A&A 679, A148 | Taxonomy for planet-crossing asteroids from SDSS, SkyMapper, Gaia and ground colors; predicts class mix in the main-belt source regions. | 7,401 "NEOs" (includes Mars-crossers and some Hungarias); **42 mission-accessible** | Against spectral reference set | CDS | The catalog-fusion channel at scale. Only 42 mission-accessible objects, which shows how little the surveys reach the NHATS regime. [V abstract] https://arxiv.org/abs/2309.03555 |
| Devogèle et al. 2019, AJ 158, 196 (MANOS spectra) | Visible spectra of mission-accessible small NEOs. S+Q 43.8 +/- 4.6%, X-complex 23.8 +/- 3.3%, A-type 3.8 +/- 1.3%. | 210 NEOs, mean H about 25, mean dv about 5.7 km/s | Survey | Paper | **Ground truth for the target population.** [V abstract] https://arxiv.org/abs/1909.04788 |
| Moskovitz, Kareta et al. 2026 (accepted PSJ; MANOS colors) | griz colors with lightcurve correction. S-complex about 65% at km scale to about one third below 50 m; X-complex increases. Authors argue for a real compositional gradient with size. | 189 NEOs | Combined with other surveys | arXiv | Same. Also shows label noise: the 2025 abstract reports the C fraction moving from 10 +/- 5% to 27 +/- 7% without lightcurve correction, and one object fit as Cgh at one epoch and Q at another. [V] https://arxiv.org/abs/2603.15872 , https://meetingorganizer.copernicus.org/EPSC-DPS2025/EPSC-DPS2025-1338.html |
| Sanchez et al. 2024 (accepted PSJ) | NIR spectra and photometry of small NEOs. About 66% S-complex, mostly LL-like; 83% from nu6, 16% from 3:1, 1% from 5:2. Logistic-regression class probabilities for H, L, LL. | 84 spectra, 59 photometry, all under 300 m | Survey | arXiv | Shows the source posterior is nearly constant for small NEOs. [V abstract] https://arxiv.org/abs/2404.18263 |
| McGraw, Thomas, Emery, Rivkin 2026 (and 2022) | 3-micron spectroscopy of NEOs. 4 of 15 (2026) and 8 of 29 (2022) show an OH/H2O band, on S-complex and V-type objects. Band presence tied to large aphelion (Q > 2.06 au) and low inclination (all < 27 deg, most < 14 deg). | 15 + 29 NEOs | Direct detection | arXiv | An **orbit-based predictor of surface hydration** already exists. It is on nominally anhydrous classes, which breaks the "hydrated = carbonaceous" shortcut. [V abstract] https://arxiv.org/abs/2602.00430 |
| Penttilä et al. 2021; Klimczak et al. 2021, 2022; Korda et al. 2022; Murray 2023; Carruba et al. | Neural or classical ML taxonomy from spectra or survey colors; NN mineral composition from spectra; NN albedo from main-belt proper elements (37% lower albedo error than a mean-albedo model); Carruba's ML work is on families and resonances, not composition. | Main belt mostly | Cross-validation | Mixed | Method prior art; none targets NEOs without photometry. [S] https://www.aanda.org/articles/aa/abs/2021/05/aa38545-20/aa38545-20.html , https://www.frontiersin.org/articles/10.3389/fspas.2021.767885/pdf , https://arxiv.org/abs/2210.01006 , https://arxiv.org/abs/2305.16392 , https://arxiv.org/pdf/2110.06611 |

What is missing from all of the above: a proper-scoring-rule evaluation (log loss, Brier score, reliability diagram) of class probabilities for NEOs when the input is orbit and H only, or orbit, H and one sparse datum. I found none. That is a search result, not a proof of absence.

## 3. (b) Mining target selection and ranking

| Work | What it did | Objects | Validation | Public? | Overlap |
|---|---|---|---|---|---|
| Asterank (I. Webster, 2012; acquired by Planetary Resources May 2013) | Interactive site ranking asteroids by value, accessibility, profit. Value from mass and spectral type; accessibility from delta-v and orbit; mining cost a flat fraction of value. Its own page says "The overwhelming majority of asteroids have no spectral classification" and that estimates are imperfect. | SBDB/MPC-wide | Accessibility compared with the 2012 Keck study | Open source (GitHub, MIT) | **The interactive-website precedent.** Deterministic, no uncertainty, famous for trillion-dollar figures. The project must be visibly different. [V] https://www.asterank.com/about , https://github.com/typpo/asterank |
| ECOCEL (Kovalenko et al. 2022, PSS, 105463) | Online mission-planning database: composition from spectral class and meteorite analogs, trajectories 2020s to 2050. | 326 spectrally characterized asteroids | n/a | Site reported offline in 2023 | Composition plus accessibility, but only where a spectrum exists. [V secondary] https://phys.org/news/2023-05-asteroid-miner-database.html |
| USGS ASTRA (Keszthelyi et al. 2017, OFR 2017-1041; co-authors include Trilling, Moskovitz, Grundy) | Feasibility test of the USGS three-part mineral assessment on NEOs. Each asteroid is a "deposit" of type carbonaceous, metal-rich or stony. 428 objects with dv < 7 km/s and H < 18; unclassified objects assigned a class at random with prior 27% C, 34% M, 39% S (Stuart & Binzel 2004); Monte Carlo of 100,000 runs for total water and metallic iron. Explicitly "not a usable assessment"; "huge and unquantified uncertainties"; no economic model. | 428 known + up to 43 undiscovered | None | Report public | Same three-way class scheme and the same "assign a prior to the unclassified" step, at population level, for km-size objects. A resource-side referee will cite it. [V slides] https://gsa.confex.com/gsa/2017AM/webprogram/Handout/Paper306866/Keszthelyi_Resources_GSA2017.pdf , https://www.usgs.gov/centers/gggsc/science/astra-asteroid-resource-assessment , https://pubs.usgs.gov/publication/ofr20171041 |
| Elvis 2014, PSS 91, 20 | "How many ore-bearing asteroids?" About 1 in 2,000 NEOs for platinum-group metals (dv < 4.5 km/s, D > 100 m): about 10 objects. Water: about 1 in 1,100, about 9,000 objects down to 18 m, about 18 above 100 m. | Population | None; "highly uncertain" | Paper | Population framing. [V abstract] https://arxiv.org/abs/1312.4450 |
| Elvis & Esty 2014, Acta Astronautica 96, 227 | Number of assay probes needed to find one ore-bearing asteroid (roughly 10 to 20 for 90% confidence); argues better prior remote characterization sharply improves this. | Population | n/a | Paper | The value-of-information argument for a prior catalog was made in 2014. [S] https://arxiv.org/pdf/1312.4452 |
| Rivkin & DeMeo 2019, JGR Planets | Ch class as proxy for hydrated. 53 +/- 27 Ch NEOs above 1 km; 17 +/- 9 of them more accessible than the lunar surface; 700 +/- 350 hydrated accessible objects with no size limit. No per-object list. | Population | Literature fractions | Paper | Population framing; names the proxy problem. [V abstract] https://arxiv.org/abs/1812.02285 |
| Harris & Drube 2014, ApJL 785, L4 | NEATM beaming parameter eta as a metal indicator. Filter eta > 2.0 and 0.15 < p_IR <= 0.30 on WISE NEOs. | **18 candidate NEOs**, D 0.36 to 3.05 km. Of the 10 with a published class, 7 are S or Q. | Eta against radar albedo for 12 NEOs | Table in paper | The metal-rich channel. None of the 18 is in the decametre NHATS regime, and most typed candidates are S or Q, so the flag is "high thermal inertia", not "metal". [V PDF] https://arxiv.org/abs/1403.6346 |
| Sanchez et al. 2021, PSJ 2, 205 | 1986 DA and 2016 ED85 as metal-rich NEAs (about 85% metal, 15% silicate), delivered via 5:2. | 2 | Spectra, radar | Paper | Known-answer objects for a metal class. [S] https://arxiv.org/abs/2109.13950 |
| Binzel et al. 2004, MAPS 39, 351 | "Dynamical and compositional assessment of NEO mission targets": 234 objects with best-case dv < 7 km/s; taxonomy for 44. | 234 | n/a | Paper | The original accessibility-plus-composition table. [S] |
| Sanchez & McInnes 2011, JSR 48, 153 | "Asteroid resource map for near-Earth space": accessible mass as a function of delta-v from an NEO population model. | Population | n/a | Paper | Accessibility-resource map without composition. [S] https://strathprints.strath.ac.uk/29192/ |
| Hinkle et al. 2014 to 2015 (DPS, LPSC abstracts) | "Taxonomic distribution of mission-accessible small NEAs". Published as Devogèle et al. 2019. | see above | | | The brief's "Hinkle 2015 Icarus" does not appear to exist as a paper. [S] https://ui.adsabs.harvard.edu/abs/2015LPI....46.1029H/abstract |
| Ramírez et al. 2025, Aerospace 12, 800; Mereta & Izzo 2018; Xie et al. 2021 (Acta Astronautica 181, 249) | Fuzzy multi-criteria ranking for boulder capture (dv, synodic period, rotation, orbit quality; composition left out, as its reviewers noted); trajectory-model sensitivity of target rankings; long-term mining target evaluation. | 143 pre-selected targets (Mereta & Izzo) | n/a | Papers | Rankings exist; none carries composition probability. [S; Xie U] https://www.mdpi.com/2226-4310/12/9/800 , https://arxiv.org/abs/1802.02418 |
| Cannon, Gialich & Acain 2023, PSS 225, 105608; Trigo-Rodríguez et al. 2025/2026, MNRAS; Nachtrieb & Smith 2026 | Metal grades from meteorites (AstroForge-funded); mining potential of carbonaceous chondrites; PGM market model. | Meteorites | Lab | Papers | Grade models, not target selection. [S, S, V] https://arxiv.org/abs/2510.27373 , https://arxiv.org/abs/2607.06806 |
| ASIME 2016 and 2018 white papers (Graps et al.) | Asteroid miners' questions answered by scientists; science knowledge gaps on survey, surface, subsurface, composition. | n/a | n/a | arXiv | The community statement of what miners need to know. Must be cited. [V abstract] https://arxiv.org/abs/1612.00709 , https://arxiv.org/abs/1904.11831 |
| Smith, Lincoln & Weisbin 2011 (JPL, AIAA SPACE) | Bayesian decision analysis of how many robotic surveyors to send before a human NEA mission, using suitability statistics from more than 1,200 asteroids. | >1,200 | n/a | NTRS | Bayesian target-suitability reasoning, 2011. [V] https://ntrs.nasa.gov/citations/20120015820 |

Company practice, as far as it is public:

- **AstroForge** named 2022 OB5 as the Odin target (NHATS dv 3.517 km/s, H 29.0) and describes its 2026 to 2027 target only as "a near-Earth M-type". It says it uses ground telescopes including the 4.3 m Lowell Discovery Telescope for astrometry and spectroscopy of candidates, and that it will choose among candidates near launch. No published criteria or probabilities. [S] https://www.space.com/space-exploration/tech/space-mining-company-astroforge-identifies-asteroid-target-for-odin-launch-next-month ; [V] https://www.tipranks.com/news/private-companies/astroforge-emphasizes-data-driven-asteroid-target-selection
- **Karman+** (High Frontier, Transporter 19, early 2027): primary target 2022 DC5, backup 2021 UH2. Selection by accessibility, absolute magnitude and rotation period. Its 2024 abstract says few candidates have spectra, few are confirmed carbonaceous, and classes disagree between studies. Mikael Granvik is a co-author of the 2025 abstract. [V] https://meetingorganizer.copernicus.org/EPSC-DPS2025/EPSC-DPS2025-1407.html , https://meetingorganizer.copernicus.org/EPSC2024/EPSC2024-587.html
- **Planetary Resources and Deep Space Industries** (defunct): pass/fail filters; DSI wanted albedo <= 0.10, preferably <= 0.06. [S] https://www.digitaltrends.com/cool-tech/how-planetary-resources-selects-asteroid-mining-targets/
- Fedorets (EPSC2026-271) proposes Earth's temporary satellites as mining test targets. [V] https://meetingorganizer.copernicus.org/EPSC2026/EPSC2026-271.html

Not found: any catalog, public or commercial, that attaches a composition probability to each accessible object.

## 4. (c) Non-gravitational accelerations, thermal inertia and dynamics as composition indicators

- **Yarkovsky to density is already done on samples.** Dziadura et al. 2023 (A&A 680, A77) fit A2 for 446 NEAs with Gaia DR3 astrometry, report reliable A2 for 49 NEAs (10 new) and bulk densities for them. A 2024 follow-up with the Gaia FPR reports 43. Earlier: Nugent et al. 2012 (54 NEAs), Del Vigna et al. 2018 (87 reliable detections), Chesley et al. 2014 (Bennu, 1260 +/- 70 kg/m3). [S] https://www.aanda.org/articles/aa/abs/2023/12/aa47342-23/aa47342-23.html , https://arxiv.org/pdf/2411.09750 , https://arxiv.org/pdf/1805.05947
- **Yarkovsky to thermal inertia**: ASTERIA (Novaković, Fenucci et al. 2024, PSJ) gives thermal inertia for 38 NEAs, 31 sub-km, and is described as the only method for small fast rotators. The composition link is indirect (porosity, cohesion). [S] https://arxiv.org/pdf/2311.03479
- **Radiation pressure to area-to-mass ratio**: 2009 BD (AMR 2.97 +/- 0.33 e-4 m2/kg, density about 640 kg/m3 for an assumed albedo), 2011 MD, 2020 CD3. Del Vigna 2018: radiation pressure detected only for H > 27 objects with Earth encounters; 4 accepted detections out of 10 candidates. A1 is also the natural-versus-artificial discriminator. [S] https://arxiv.org/pdf/1106.0564 , https://arxiv.org/pdf/1805.05947
- **Dark comets**: Seligman et al. 2023 (six objects: 1998 KY26, 2005 VL1, 2016 NJ33, 2010 VL65, 2016 RH120, 2010 RF12), Farnocchia et al. 2023, Seligman et al. 2024 (two populations), Taylor et al. 2024 (dynamical origins). [V] https://arxiv.org/abs/2212.08115 ; [S] https://arxiv.org/abs/2412.07603 , https://arxiv.org/abs/2407.01839
- **The volatile reading is contested, this month.** Hansen & Hirabayashi (arXiv 6 Nov 2026, Icarus) find orbit-averaged temperatures everywhere in 1998 KY26 well above sublimation across 13 thermal models, and conclude an acceleration alone does not show volatiles. [V] https://arxiv.org/abs/2611.10275
- **Artificial-object confusion is live**: papers in 2025 and 2026 argue 2005 VL1 is Venera 2 and 1998 KY26 is Phobos 1 (and rebuttals). The October 2026 MPC newsletter notes 2026 QQ8 was judged natural partly from radiation-pressure analysis. [V titles] https://arxiv.org/abs/2503.03552 , https://arxiv.org/abs/2606.01288 ; [V] https://buttondown.com/MPC_newsletter/archive/newsletter-october-2026
- **Thermal eta to metal**: Harris & Drube 2014, section 3 above.
- **Orbit to hydration**: McGraw et al. 2022, 2026, section 2 above.
- **Rubin has this on its list**: the LSST Solar System roadmap NEO priority 8 is detection and characterization of non-gravitational forces including Yarkovsky and radiation pressure. [V] https://ar5iv.labs.arxiv.org/html/1802.01783

Not found: any use of A1 or A2 as an explicit *resource* indicator, or a catalog-wide density screen of NHATS-size objects with injection-recovery. The professionals who measure these effects (JPL, NEODyS, ESA NEOCC) publish the accelerations but not a density or composition inference per object.

## 5. (d) AI-agent astronomy on minor planets, 2025 to 2026

**claudestronomy.com and sister sites** [V]: run by macrogrants, a California nonprofit incorporated 10 Oct 2026 (501(c)(3) pending), director Will DePue; review board includes Luke Farritor. Claudestronomy says it is seeded with $100,000 (the macrogrants home page says $50,000); codexstronomy, grokstronomy and geministronomy say $50,000 each. Grants typically $500 to $25,000. The stated rules match the project brief: recover known objects first, injection-recovery with false positives calibrated separately, write down thresholds before new data, publish calibrated nulls, fresh-agent adversarial review plus review by people who know the data, publish code. The "work that inspires this" list is all exoplanets, brown dwarfs, white dwarfs and variables. **No minor-planet result is listed on any of the four sites**, though "asteroids, comets, interstellar visitors" is a named target area. https://claudestronomy.com , https://macrogrants.com/ , https://codexstronomy.com , https://grokstronomy.com , https://geministronomy.com

**The Depue, Wolk, Farritor dwarf-planet candidates** [V that the coverage says this; U for the underlying claim]: announced on X on 11 Nov 2026 alongside the $100,000 grant. Claimed: a trans-Neptunian object "about 1/4 the width of Pluto" orbiting "about twice as far", about the 50th largest known solar-system object, unnoticed in archives for over 10 years; a second "just as large". Found with Claude and Codex agents over a few weeks in public archive images, in a search that began as a Planet 9 hunt. Every account I could read is an aggregator (huggingnews, BigGo, archynewsy, emergent.sh). None gives a designation, an archive name, a Minor Planet Center submission, a method, a false-positive rate, or a quote from a professional astronomer. One says "Wolk is currently working to confirm the findings". Collaborator names vary between outlets ("Josh Wall"). I could not read the X posts themselves. https://huggingnews.com/ai/will-depue-discovers-potential-new-dwarf-planet-using-claude-ai-08da1fba , https://huggingnews.com/ai/will-depue-finds-second-potential-dwarf-planet-in-public-space-archive-99c7ee2e , https://finance.biggo.com/news/e12740074a117d6b , https://www.archynewsy.com/will-depue-uses-ai-agents-to-find-asteroid-and-dwarf-planet-candidates/ , https://twitter.com/willdepue/status/2120632732107907471

This is a different object from **2026 ED138**, the Rubin dwarf-planet candidate (about 47 au, 600 to 1,500 km) found by Matthew Holman on 13 Oct 2026 with a conventional search code, announced by MPEC on 27 Oct 2026, with DECam precoveries to 2016 and amateur precoveries to 1954. No AI agent involvement is reported. [V] https://www.sciencenews.org/article/halloween-astronomers-dwarf-planet

**Other agent activity** [V that the sites say this; claims unconfirmed]:
- **Ilvarra** (ilvarra.com), a self-described autonomous agent "running on Claude": says it found unreported moving objects in 2014 Blanco/DECam images, submitted 24 unmatched objects and a possible Centaur at 15 to 27 au to the MPC in October 2026, and shows an MPC receipt. Known-object matching is described; no injection-recovery, no detection efficiency, no designations. https://ilvarra.com/
- A hobbyist ("SirMeeseekz") let Claude operate rented remote telescopes and reports 57 astrometric positions of eight asteroids sent to the MPC. https://shazoo.ru/2026/11/05/193538/claude-sam-arenduet-teleskopy-v-cili-ispanii-i-iute-i-snimaet-tumannosti-ii-uze-otpravil-57-zamerov-asteroidov-v-centr-malyx-planet
- Academic agent papers are benchmarks or toolkits outside small bodies: Stargazer (radial-velocity fitting; agents often fit well statistically but recover wrong physics), ASTER (exoplanet retrievals), and LLMs on the GTOC 12 asteroid-mining trajectory problem (good plans, failed implementations). https://arxiv.org/abs/2604.15664 , https://meetingorganizer.copernicus.org/EPSC2026/EPSC2026-276.html , https://arxiv.org/abs/2602.03630

**Professional reaction** [V]:
- The MPC's October 2026 newsletter has a section "Data integrity in the Age of Automation and AI". It welcomes AI-assisted tools, then says "observers are responsible for ensuring that their submissions are accurate, reliable, and scientifically meaningful" and "Using an automated tool should never mean submitting results without understanding or verifying them." It announces "more rigorous requirements" for observatory codes and observing programs, notes that archival astrometry programs are reviewed by a Singletons and Archival Review Committee, and complains about long AI-written helpdesk tickets (asks for about 250 words). https://buttondown.com/MPC_newsletter/archive/newsletter-october-2026
- AAS Journals now require an AI-usage disclosure statement on all new submissions (effective autumn 2026). https://journals.aas.org/?p=4629
- Science ran "The Last Astronomers" (4 June 2026) on the field's unease; Hogg's "Why do we do astrophysics?" (arXiv 2602.10181) argues against both unrestricted adoption and bans. [S] https://arxiv.org/abs/2602.10181
- I found **no professional comment, positive or negative, on the Depue claims**. That is absence in my searches, not evidence of silence.

**Finding for the plan**: no AI-agent work on asteroid composition, taxonomy or resources was found. The project would be the first agent-run effort in minor-planet *physical characterization* that I can identify. It also would not need to submit anything to the MPC, which removes the main friction point. The reputational environment is wary, and the nearest neighbours are unverified discovery claims.

## 6. (e) Community and agency products that already serve characterization-for-access

| Product | What it provides | Composition? | Status | Source |
|---|---|---|---|---|
| NHATS (JPL/GSFC) | Round-trip trajectories, dv, duration, size range from H, next optical and radar observing windows | No | Live, 7,226 objects | [V] https://ssd-api.jpl.nasa.gov/doc/nhats.html |
| NEOfixer (Catalina, Arizona) | Per-site follow-up priority from importance, existence confidence, urgency, cost, benefit; "guided exclusively by planetary defense concerns"; about 100 observatories | No; astrometry only | Live, open API | [S] https://neofixer.arizona.edu/faq/how-does-neofixer-assign-priority |
| ESA NEOCC Priority List | Objects most in need of astrometric follow-up | No | Being decommissioned; ESA recommends NEOfixer | [S] https://neo.ssa.esa.int/priority-list |
| MANOS (Lowell) | Spectra (210), colors (189), lightcurves of low-dv sub-km NEOs | Yes, measured | Ongoing since 2013 | [V] section 2 |
| MITHNEOS | About 1,350 spectra of more than 1,000 NEOs; 3-micron campaign | Yes, measured | Ongoing | [S] https://meetingorganizer.copernicus.org/EPSC-DPS2025/EPSC-DPS2025-1016.html |
| NEOROCKS (EU H2020, 2020 to mid-2023) | Physical-properties database for small NEOs | Yes | Database was consortium-only in 2023; move to ASI-SSDC planned; current public status unconfirmed | [S] https://cordis.europa.eu/project/id/870403/reporting |
| Cortese, Perozzi et al., "An efficient algorithm for prioritizing NEA physical observations" (INAF) | Ranking of NEAs for physical characterization | Prioritization only | Published | [S title and abstract fragment] https://openaccess.inaf.it/handle/20.500.12386/29051 |
| NEO Surveyor | Thermal-IR diameters for 200,000 to 300,000 new objects, some as small as about 10 m; Abell et al. predict many low-dv targets using NHATS algorithms | Sizes; albedo where visible data exist | Launch no earlier than Sept 2027 | [V] https://meetingorganizer.copernicus.org/EPSC-DPS2025/EPSC-DPS2025-460.html |
| Rubin LSST SSSC roadmap (Schwamb et al. 2018) | NEO priorities: (2) colors and phase coverage, "probing the color distribution of ten-meter scale objects"; (4) orbit, H and taxonomy distributions; (7) rotation; (8) non-gravitational forces. No mention of mission targets or resources. | Planned | Survey running; first Rubin discoveries in 2026 | [V] https://ar5iv.labs.arxiv.org/html/1802.01783 |
| USGS ASTRA | Assessment method feasibility | Class prior only | Completed 2017, no follow-on found | [V] section 3 |
| NASA ISRU Envisioned Future Priorities; ESA Space Resources Strategy (2019) | Lunar-first roadmaps; asteroids appear as a knowledge gap, not a programme | No | n/a | [S] https://www.nasa.gov/wp-content/uploads/2023/06/live-isru-efp-new-3-21-23-tagged-1.pdf , https://exploration.esa.int/web/moon/-/61369-esa-space-resources-strategy |

Gap visible in this table: the follow-up brokers rank by orbit need, the characterization surveys choose targets by observability and delta-v, and nobody publishes a ranking by "how much would observing this object change what we believe about its composition, weighted by accessibility".

## 7. Verdict

### Already done. Do not claim as new.

1. Probabilistic taxonomy from partial spectra, colors or albedo (Mahlke 2022; Mommert 2016; Erasmus 2017; Dotson & Mathias 2017; López-Oquendo 2026).
2. Per-object source-region probabilities from an orbit (Granvik 2018; NEOMOD), and per-object family and meteorite-class probabilities (METEOMOD, public code).
3. Orbit and size to taxonomy to water content for low-dv NEOs, at population level (Jedicke 2018). Rule-level orbit to class at discovery (Deshapriya 2023).
4. Population counts of hydrated, water-ore and metal-ore accessible NEOs (Elvis 2014; Rivkin & DeMeo 2019; Keszthelyi 2017).
5. The measured class mix of the mission-accessible small NEOs (MANOS 2019, 2026; UKIRT 2026; Sanchez 2024).
6. Catalog-scale color taxonomy for planet-crossers (Sergeyev 2023, 7,401 objects).
7. Yarkovsky densities and thermal inertias for tens of NEAs (Dziadura 2023; Novaković 2024); radiation-pressure area-to-mass for a handful; dark comets as a class (Seligman 2023).
8. Metal-rich candidate flags from thermal data (Harris & Drube 2014, 18 NEOs).
9. Interactive value-ranking and mission-planning sites (Asterank; ECOCEL).
10. AI agents trawling archives for new minor planets (Depue et al.; Ilvarra), without published validation.

### Incremental. Useful, but a referee will call it engineering.

- Running the above tools over the NHATS list and joining the outputs.
- A "what is actually known" table for the 7,226 from SsODNet, MANOS, UKIRT, Sergeyev 2023, NEOWISE and Spitzer, replacing the stale SBDB fields. Low novelty, high utility, and required before any "uncharacterized" claim.
- A size-dependent class prior that uses the MANOS trend.
- The website.

### Open, ranked by how defensible the novelty claim is.

1. **A scored calibration audit of indirect composition priors for small NEOs, plus a time-stamped forward forecast.** Hold out MANOS, UKIRT, Sanchez 2024 and MITHNEOS labels; predict class from orbit and H alone, then add each sparse datum; report log loss, Brier score and reliability curves against the base rate and against Jedicke-style, Granvik/NEOMOD and METEOMOD priors. Then freeze per-object probabilities for the NHATS list and score them as Rubin (griz for about 4,000 NEOs with D >= 10 m), Euclid (about 10^4 NEOs), SPHEREx and NEO Surveyor produce labels. I found no published proper-scoring evaluation of this kind. It is defensible even if the answer is "orbit adds almost nothing", which the existing literature suggests is likely. This is the claim I would lead with.
2. **The joined public catalog with uncertainty and an information-value ranking** ("which accessible objects are worth a spectrum, and when is the window"). No existing product does it: NHATS has no composition, Asterank and ECOCEL are deterministic and limited to typed objects, NEOfixer is astrometry-only, the NEOCC list is being retired. Defensible as a product. Its scientific weight depends on item 1.
3. **Handling non-main-belt provenance at the very top of the list.** The lowest-dv objects include minimoons (2026 QQ8, 2020 CD3), reported lunar ejecta (2024 PT5; Kamo'oalewa), and possible artificial objects. Granvik, NEOMOD and METEOMOD have no lunar source. Alessi & Jedicke 2026 estimate about 70 or more lunar-origin Earth co-orbitals above 10 m against about 1,600 main-belt co-orbitals from NEOMOD3, with orders-of-magnitude uncertainty, and note commercial mining interest. A prior that includes a lunar and an artificial class for Earth-like orbits is not something I found. Medium defensibility: small numbers, partly covered by Kareta 2025 and Alessi & Jedicke 2026.
4. **Non-gravitational accelerations as a catalog-wide density or volatile screen for NHATS-size objects.** Partly done on samples; the inference is degenerate (thermal properties, obliquity, size, shape), radiation pressure is detectable only for H > 27 objects with Earth encounters, and the volatile reading of dark comets was directly challenged in November 2026. Low to medium defensibility. Best framed as a filter (natural or artificial, plausible density range), not as a composition measurement.
5. **Agent-run, pre-registered process applied to physical characterization.** No precedent found. It is a process claim, not a science claim, and it carries reputational risk from the neighbouring unverified discovery announcements.

### The three papers a referee is most likely to say were ignored

1. **Jedicke, Sercel, Gillis-Davis, Morenz & Gertsch 2018**, "Availability and delta-v requirements for delivering water extracted from near-Earth objects to cis-lunar space", PSS 159, 28. It already builds taxonomy as a function of NEO orbit and size and converts it to water for low-dv objects. Cite with Rivkin & DeMeo 2019.
2. **Devogèle et al. 2019** (AJ 158, 196) **and Moskovitz et al. 2026** (PSJ, arXiv 2603.15872), the MANOS spectra and colors. They are the measured answer for the target population and show the class mix changes with size, which undermines any prior taken from km-scale NEOs or the main belt.
3. **Brož et al. 2024** (A&A 689, A183; with the companion Nature papers by Brož et al. and Marsset et al. 2024 on ordinary-chondrite families [R]) and the METEOMOD tool. This is the orbit to family to meteorite chain, already public, already applied per object to small NEOs by López-Oquendo et al. 2026.

Close runners-up, all of which should be in the reference list: Deshapriya et al. 2023 (orbit-only class guess at discovery); Dotson & Mathias 2017 and the Ames inference network; Morbidelli et al. 2020 and Nesvorný et al. 2024 (albedo by orbit); Keszthelyi et al. 2017 (USGS); Mahlke et al. 2022; Sergeyev et al. 2023; Harris & Drube 2014; Elvis 2014; the ASIME white papers.

## 8. Ways this part of the project fails or misleads

1. **The prior collapses to the base rate.** NHATS orbits are Earth-like; source posteriors barely differ between objects. A catalog of 7,226 near-identical probability vectors is not a prospect catalog.
2. **The base rate is disputed and size-dependent.** Three recent surveys of small NEOs give S-dominated, about one-third S, and C/X-dominated answers. "Validated against known answers" depends on which survey is treated as truth, and on debiasing choices.
3. **Labels are noisy.** Four-band colors do not always give a unique class; lightcurve correction moves the C fraction from 10% to 27%; the same object has been typed Cgh and Q.
4. **Class is not composition, and composition is not resource.** X-complex is degenerate without albedo (E, M, P). Hydration is seen on S and V types (McGraw 2026). Ch is a proxy. Low-perihelion heating can dehydrate carbonaceous material. Surface OH is not bulk water.
5. **The validation set thins out exactly where the targets are.** Median NHATS H is 26.2. MANOS mean H is about 25. Typed objects at H > 27 number in the tens.
6. **The "none characterized" framing is an SBDB artifact** and will be caught.
7. **The lowest-dv objects may not be main-belt asteroids at all** (lunar ejecta, minimoons, spacecraft hardware).
8. **Non-gravitational signals are not composition.** See section 4.
9. **The metal channel does not reach the targets.** Harris & Drube's 18 candidates are 0.36 to 3 km, and NEOWISE has almost no decametre NHATS objects (0 of 286 with dv < 5 have an SBDB albedo).
10. **Being scooped or superseded.** Dorsey & Granvik are building class-specific NEO models now; Karman+ employs the relevant expertise; Rubin and Euclid labels arrive within one to three years. The forward-forecast framing turns this from a threat into the test.
11. **The Asterank trap.** An interactive ranking with point values and no visible uncertainty will be dismissed on sight by the people whose opinion matters.
12. **Agent provenance.** The MPC and AAS have both tightened expectations in autumn 2026. Disclosure and human sign-off need to be explicit.

## 9. What I could not verify

- The X posts by Depue and Wolk (primary source). Mirror returned HTTP 451.
- Whether any Depue or Ilvarra object has received an MPC designation.
- A&A pages for Deshapriya 2023 and Dziadura 2023 (HTTP 403); numbers are from search summaries.
- USGS OFR 2017-1041 full text (HTTP 403); numbers are from the GSA 2017 slides by the same authors, which I read in full.
- Xie et al. 2021 (Acta Astronautica 181, 249): citation only.
- The Geoscience Canada 2019 review reporting "seven and three potentially viable NEA targets" for water and PGEs (HTTP 403).
- The METEOMOD statistics in López-Oquendo 2026 (20% above 50%; 54% Massalia): from a search summary of the PDF, not the abstract.
- Current public status of the NEOROCKS and ECOCEL databases.
- The NEOCC Priority List decommissioning notice: quoted by search summary; my direct fetch returned 404.
- How many NHATS objects have a class anywhere in the literature outside SBDB. This is the single most useful number still missing.

## Sources

Agency and survey products
- https://ssd-api.jpl.nasa.gov/nhats.api
- https://ssd-api.jpl.nasa.gov/doc/nhats.html
- https://ssd-api.jpl.nasa.gov/sbdb_query.api?fields=pdes,spec_B,spec_T,albedo,diameter,H&sb-group=neo
- https://neofixer.arizona.edu/faq/how-does-neofixer-assign-priority
- https://neo.ssa.esa.int/priority-list
- https://neo.ssa.esa.int/neo-population-generator
- https://cordis.europa.eu/project/id/870403/reporting
- https://openaccess.inaf.it/handle/20.500.12386/29051
- https://ar5iv.labs.arxiv.org/html/1802.01783
- https://meetingorganizer.copernicus.org/EPSC-DPS2025/EPSC-DPS2025-460.html
- https://meetingorganizer.copernicus.org/EPSC-DPS2025/EPSC-DPS2025-1016.html
- https://www.nasa.gov/wp-content/uploads/2023/06/live-isru-efp-new-3-21-23-tagged-1.pdf
- https://exploration.esa.int/web/moon/-/61369-esa-space-resources-strategy
- https://www.usgs.gov/centers/gggsc/science/astra-asteroid-resource-assessment
- https://pubs.usgs.gov/publication/ofr20171041
- https://gsa.confex.com/gsa/2017AM/webprogram/Handout/Paper306866/Keszthelyi_Resources_GSA2017.pdf

Composition from sparse or indirect data
- https://arxiv.org/abs/2203.11229 (Mahlke 2022)
- https://ntrs.nasa.gov/citations/20170009812 (Dotson & Mathias 2017)
- https://ui.adsabs.harvard.edu/abs/2020AGUFMNH0370002D/abstract (Dotson et al. 2020)
- https://cneos.jpl.nasa.gov/pd/cs/pdc25/PDC25-Epoch2-physical_properties.pdf
- https://www.aanda.org/articles/aa/abs/2023/06/aa45316-22/aa45316-22.html (Deshapriya 2023)
- https://scholarsmine.mst.edu/geosci_geo_peteng_facwork/1362 (Jedicke 2018)
- https://arxiv.org/abs/2001.03550 (Morbidelli 2020)
- https://arxiv.org/abs/2404.18805 (NEOMOD3)
- https://arxiv.org/abs/2004.05090 (Binzel 2019)
- https://arxiv.org/abs/2202.13796 (Marsset 2022)
- https://meetingorganizer.copernicus.org/EPSC2026/EPSC2026-1111.html (Dorsey & Granvik 2026)
- https://arxiv.org/abs/2406.19727 (Brož 2024)
- https://sirrah.troja.mff.cuni.cz/~mira/meteomod/meteomod.php (METEOMOD)
- https://arxiv.org/abs/2608.28779 (López-Oquendo 2026)
- https://arxiv.org/abs/1602.06000 (Mommert 2016)
- https://arxiv.org/pdf/1709.03305 (Erasmus 2017)
- https://arxiv.org/abs/2309.03555 (Sergeyev 2023)
- https://arxiv.org/abs/1909.04788 (Devogèle 2019)
- https://arxiv.org/abs/2603.15872 (Moskovitz 2026)
- https://meetingorganizer.copernicus.org/EPSC-DPS2025/EPSC-DPS2025-1338.html
- https://arxiv.org/abs/2404.18263 (Sanchez 2024)
- https://arxiv.org/abs/2602.00430 (McGraw 2026)
- https://arxiv.org/pdf/1905.12997 (Popescu 2019)
- https://arxiv.org/abs/2410.06390 (Beniyama 2024)
- https://arxiv.org/abs/1804.07229 (Granvik & Brown 2018)
- https://arxiv.org/abs/2512.17191 (Deam 2025)
- https://www.aanda.org/articles/aa/abs/2021/05/aa38545-20/aa38545-20.html (Penttilä 2021)
- https://www.frontiersin.org/articles/10.3389/fspas.2021.767885/pdf (Klimczak 2021)
- https://arxiv.org/abs/2210.01006 (Korda 2022)
- https://arxiv.org/abs/2305.16392 (Murray 2023)
- https://arxiv.org/pdf/2110.06611 (Carruba 2021 review)

Target selection and resources
- https://www.asterank.com/about ; https://github.com/typpo/asterank
- https://phys.org/news/2023-05-asteroid-miner-database.html (ECOCEL)
- https://arxiv.org/abs/1312.4450 (Elvis 2014)
- https://arxiv.org/pdf/1312.4452 (Elvis & Esty 2014)
- https://arxiv.org/abs/1812.02285 (Rivkin & DeMeo 2019)
- https://arxiv.org/abs/1403.6346 (Harris & Drube 2014)
- https://arxiv.org/abs/2109.13950 (Sanchez 2021)
- https://strathprints.strath.ac.uk/29192/ (Sanchez & McInnes 2011)
- https://ui.adsabs.harvard.edu/abs/2015LPI....46.1029H/abstract (Hinkle 2015 abstract)
- https://www.mdpi.com/2226-4310/12/9/800 (Ramírez 2025)
- https://arxiv.org/abs/1802.02418 (Mereta & Izzo 2018)
- https://arxiv.org/abs/2510.27373 (Trigo-Rodríguez 2025)
- https://arxiv.org/abs/2607.06806 (Nachtrieb & Smith 2026)
- https://arxiv.org/abs/1612.00709 ; https://arxiv.org/abs/1904.11831 (ASIME)
- https://ntrs.nasa.gov/citations/20120015820 (Smith et al. 2011)
- https://meetingorganizer.copernicus.org/EPSC-DPS2025/EPSC-DPS2025-1407.html ; https://meetingorganizer.copernicus.org/EPSC2024/EPSC2024-587.html (Karman+)
- https://www.space.com/space-exploration/tech/space-mining-company-astroforge-identifies-asteroid-target-for-odin-launch-next-month
- https://www.tipranks.com/news/private-companies/astroforge-emphasizes-data-driven-asteroid-target-selection
- https://www.digitaltrends.com/cool-tech/how-planetary-resources-selects-asteroid-mining-targets/
- https://meetingorganizer.copernicus.org/EPSC2026/EPSC2026-271.html (Fedorets 2026)
- https://arxiv.org/abs/2604.13296 (Alessi & Jedicke 2026)
- https://arxiv.org/abs/2412.10264 (Kareta 2025, 2024 PT5)

Non-gravitational and thermal
- https://www.aanda.org/articles/aa/abs/2023/12/aa47342-23/aa47342-23.html (Dziadura 2023)
- https://arxiv.org/pdf/2411.09750 (Dziadura 2024)
- https://arxiv.org/pdf/1805.05947 (Del Vigna 2018)
- https://arxiv.org/pdf/1204.5990 (Nugent 2012)
- https://arxiv.org/pdf/2311.03479 (ASTERIA)
- https://arxiv.org/pdf/1106.0564 (Micheli 2012)
- https://arxiv.org/abs/2212.08115 (Seligman 2023)
- https://arxiv.org/abs/2412.07603 (Seligman 2024)
- https://arxiv.org/abs/2407.01839 (Taylor 2024)
- https://arxiv.org/abs/2611.10275 (Hansen & Hirabayashi 2026)
- https://arxiv.org/abs/2503.03552 ; https://arxiv.org/abs/2606.01288 (artificial-object claims)

AI agents and community reaction
- https://claudestronomy.com ; https://codexstronomy.com ; https://grokstronomy.com ; https://geministronomy.com ; https://macrogrants.com/
- https://huggingnews.com/ai/will-depue-discovers-potential-new-dwarf-planet-using-claude-ai-08da1fba
- https://huggingnews.com/ai/will-depue-finds-second-potential-dwarf-planet-in-public-space-archive-99c7ee2e
- https://finance.biggo.com/news/e12740074a117d6b
- https://www.archynewsy.com/will-depue-uses-ai-agents-to-find-asteroid-and-dwarf-planet-candidates/
- https://emergent.sh/news/claude-ai-discovers-new-dwarf-planet-solar
- https://twitter.com/willdepue/status/2120632732107907471 (not readable by me)
- https://www.sciencenews.org/article/halloween-astronomers-dwarf-planet (2026 ED138)
- https://ilvarra.com/
- https://shazoo.ru/2026/11/05/193538/claude-sam-arenduet-teleskopy-v-cili-ispanii-i-iute-i-snimaet-tumannosti-ii-uze-otpravil-57-zamerov-asteroidov-v-centr-malyx-planet
- https://buttondown.com/MPC_newsletter/archive/newsletter-october-2026
- https://journals.aas.org/?p=4629
- https://arxiv.org/abs/2602.10181 (Hogg 2026)
- https://arxiv.org/abs/2604.15664 (Stargazer)
- https://meetingorganizer.copernicus.org/EPSC2026/EPSC2026-276.html (ASTER)
- https://arxiv.org/abs/2602.03630 (LLMs on GTOC 12)

Local working files (untrusted downloads and scripts, not kept)
- nhats_default.json
- sbdb_neo_spec.json
- nhats_count.py
- nhats_spec.py
- arxiv_q.py
