# Verification: attempt to refute the round-1 novelty claims

Date: 2026-11-21. Independent check of ten "this has not been done" claims from the round-1 reports (mainly `novelty.md`). Status: COMPLETE for the searches listed in section 4; limits are stated there.

How to read the verdicts. "Confirmed" means I searched for a counter-example and found none. That is weaker than proof of absence, and section 4 says what I could not search. "Partly confirmed" means the claim survives only in a narrower form than stated; the narrower form is given.

Evidence flags: **[V]** I read the primary source in this session (full text unless noted). **[S]** search-engine summary only. **[R]** recalled, not checked.

## 1. Result in one table

| | Claim (short) | Verdict | What the plan may still say |
|---|---|---|---|
| A | No scored, out-of-sample calibration test of an orbit-based predictor of NEO class or albedo | Confirmed | Unchanged. Nearest work: Murray 2023 (main belt, held-out RMSE), Deshapriya 2023 (NEOs, no test). |
| B | No per-object composition probability joined to accessibility for the uncharacterized majority | Confirmed | Unchanged, but Deshapriya 2023 already publishes orbit-only predicted classes for some untyped NEOs. |
| C | No injection-recovery measurement for non-gravitational parameter detection | Partly confirmed | Only "no measured false-alarm rate, and no injection into real NEA astrometry at the orbit-fit stage". Synthetic-signal efficiency tests exist. |
| D | No public catalog of A2 or area-to-mass upper limits | Confirmed | Unchanged. Whole-population fits were run at least four times and only detections were published. |
| E | Yarkovsky maximum-efficiency density bound never applied across a population | Partly confirmed | Only "never used in the direction drift to density ceiling, as a composition screen". The same inequality is a standard population-wide quality filter. |
| F | No systematic, threshold-defined search for anomalous accelerations across all NEOs | Partly confirmed | True for the radial and out-of-plane components and for a published candidate list. False for the transverse component. |
| G | No ranking of accessible NEAs by information gain of a characterization observation | Confirmed | Unchanged. Cite Cortese 2017 and NEOfixer's "Benefit" term as the precedents. |
| H | No per-object probability of lunar or artificial origin for low delta-v NEAs | Partly confirmed | No per-object table exists. A conditional probability (Wu 2025) and one single-object odds estimate (Fenucci 2026) do. |
| I | No pooled, H-conditioned class base rate with between-survey variance | Partly confirmed | The pooled H-binned base rate is published (Moskovitz 2026, 831 objects). Only the between-survey variance is missing. |
| J | No systematic area-to-mass catalog for small NEAs | Confirmed | Unchanged. |

None of the ten was refuted outright. Four have to be reworded (C, E, F, I), and H has to cite two 2025 to 2026 papers.

## 2. Claim by claim

### A. Scored out-of-sample calibration of orbit-based class or albedo predictors. CONFIRMED

Searched: arXiv API (title, abstract, comments) for asteroid with "Brier", "reliability diagram", "log loss" (0 hits each); for (taxonomy or taxonomic) with near-Earth and machine learning, random forest or neural network (5 hits, all classifiers that take colors or spectra as input); for taxonomy with "orbital elements" and predict (1 hit, main belt); albedo with orbital elements and machine learning (1 hit, main belt). Web searches in the same terms. Full text of the four closest papers:

- **Deshapriya et al. 2023, A&A 674, A50** [V, via Internet Archive copy of the A&A PDF]. G-mode clustering of 14,132 NEO orbits, 1,566 with a known class (11%). Gives a table of (i, e, a) regimes where a "reasonable guess" of primitive or siliceous can be made. No held-out test and no score. The authors write: "more taxonomic data are needed to further verify the accuracy of this method", and note that the one independent datum they checked (2002 PD43 colors) "do not seem to match this prediction". Their "verification check" is a re-run with different orbit-quality cuts.
- **Murray 2023 (arXiv:2305.16392)** [V]. Neural-network ensemble predicting NEOWISE albedo from proper orbital elements, with a truncated-normal likelihood and a 20% validation split; about 37% lower error than a mean-albedo model. This is the closest thing to the proposed test, but it is main-belt only (proper elements do not exist for NEOs), scored by RMSE, with no calibration diagnostic.
- **Simon et al. 2026, A&A (arXiv:2610.07395, 5 Oct 2026)** [V]. Compares the orbits of H-, L- and LL-like NEOs (MITHNEOS spectra) with source-family probability maps. Residual maps are shown, and the paper says they are not meant "to provide statistically calibrated estimates of deficits or excesses".
- **López-Oquendo et al. 2026 (arXiv:2608.28779)** [V]. Reports accuracy, precision, recall, F1 and a confusion matrix, but for a classifier whose input is near-infrared colors. METEOMOD source families are assigned per object and not tested against the measured class.

Still in progress elsewhere: Dorsey & Granvik, EPSC2026-1111 (class-specific NEO source models) [S]. No write-up found.

### B. Per-object composition probability joined to accessibility. CONFIRMED

- Jedicke et al. 2018 [S, abstract]: synthetic population, no per-object values for real NHATS objects. Full text not read.
- Deshapriya et al. 2023 [V]: does publish per-object *predicted* classes for untyped NEOs (Table A.11: 36 untyped members of one cluster "whose taxonomy is predicted to be of S-complex"; catalog at CDS J/A+A/674/A50). These are labels, not probabilities, on comet-like or very eccentric orbits, with no accessibility field.
- Sergeyev et al. 2023 [V, abstract]: 7,401 classified, "We classify 42 NEOs that are mission-accessible". Measured colors, not the uncharacterized majority.
- López-Oquendo et al. 2026 [V]: per-object class probabilities for 122 small NEOs from measured colors; not joined to delta-v.
- Xie et al. 2021 (Acta Astronautica 181) [S]: unclassified asteroids are assumed to be all water-bearing, or all metal-bearing, as two scenarios.
- NEOexchange / LCO (Lister et al. 2021, arXiv:2102.10144) [V]: ingests NHATS targets for characterization; no composition estimate.
- Karman+ [S]: selection by accessibility, H and rotation period. No "Prospector" catalog found under that name.
- Tianwen-2 and other Chinese target-selection work: arXiv returns only Kamo'oalewa characterization papers; one Chinese-language web search returned nothing relevant.
- Not re-fetched by me: Asterank, ECOCEL, USGS ASTRA, NEOROCKS database status (round 1 read the first three).

### C. Injection-recovery for non-gravitational detection. PARTLY CONFIRMED

Synthetic-signal tests that exist:

- **Taylor, Seligman, Holman, Vereš, Farnocchia, Micheli et al. 2024 (arXiv:2410.06874)** [V]. "we inject synthetic tracklets of hypothetical nongravitationally-accelerating NEOs into the Minor Planet Center orbit identification algorithms". 214 NEOs with multi-apparition recoveries; linked fraction relative to gravity-only by magnitude and direction; a significant fraction fails at |A| >= 1e-8 au/d2. An injection-recovery efficiency measurement at the linking stage.
- **White 2026, M.S. thesis, Marshall University** [S, repository abstract]. Sorcha survey simulator modified to add accelerations; 2,000 simulated bodies, heliolinx linking; a 1,000-object high-acceleration run where linking drops off between 1e-5 and 1e-4 au/d2 for A1, 1e-6 and 1e-5 for A2, 1e-4 and 1e-3 for A3. https://mds.marshall.edu/etd/2060
- **Levine, Rubin Community Workshop 2024 talk, "Detecting Non-Gravitational Acceleration in Near-Earth Objects with the LSST"** [S; two search summaries agree, the page itself refused connections]. Described as injection-recovery with Sorcha mock observations followed by orbit fitting, over ten years and over one apparition. No paper found. This is the nearest thing to the plan's test, on simulated Rubin data.
- **Hung, Tholen, Farnocchia & Spoto 2023 (arXiv:2310.00055)** [V]. OrbFit-simulated astrometry with an assumed A2; fits A2 and its uncertainty; gives the minimum arc for detection as a function of arc length and semimajor axis. Main belt, idealized 0.1 arcsec noise and cadence. 134 real main-belt asteroids, no reliable detection.
- **Desmars 2015 (arXiv:1501.01873)** [V]. Monte Carlo on observations, bootstrap and random hold-out to test the drift uncertainty; states the wrong-sign probability as 15.9% at S/N = 1 and 2.3% at S/N = 2 (a Gaussian statement, not a measured rate); simulated observations for the Gaia forecast.
- Greenberg et al. 2020 [V]: F-test p < 0.05 plus refits with early astrometry removed. Fenucci et al. 2024 [V]: 25 of 373 flagged spurious by an isolated-tracklet test. Neither injects signals.

What remains unpublished, as far as I can find: a measured false-alarm rate for A1, A2 or A3; and injection into the real residuals of real short-arc NEAs at the orbit-fit stage.

### D. Catalog of A2 or area-to-mass upper limits. CONFIRMED

Whole-population fits were run and only the detections were tabulated:

- Nugent et al. 2012 [V]: "We measured the semi-major axis drift rate of all 1,252 numbered NEAs"; tables list 54.
- Desmars 2015 [V]: 10,953 NEAs fitted; table lists 46.
- Dziadura et al. 2023 [V]: 446 NEAs fitted, 389 rejected; table "include[s] only accepted and marginal objects".
- Fenucci et al. 2024 [V]: 5,308 candidates fitted; accepted detections at CDS and on the NEOCC portal.
- Greenberg et al. 2020 [V]: 600 candidates, 283 rejected at p > 0.05; machine-readable table is the 247 detections.

Fragments that do exist: Dziadura et al. 2022 (Icarus 383, 115040) tabulates A2, sigma and S/N for all 42 of its candidates, non-detections included [V, in the thesis]; Del Vigna et al. 2018 lists 24 marginal cases [V]; JPL SBDB itself carries 45 NEA A2 values below 3 sigma (13 below 2 sigma) and 9 A1 values below 3 sigma [my count from today's snapshot, script `nr_sbdb_ng.py`]. No source gives upper limits on area-to-mass ratio.

### E. Yarkovsky maximum-efficiency density bound across a population. PARTLY CONFIRMED

The inequality has been applied to whole samples three times, always with an assumed density and as a quality filter:

- Desmars 2015 [V]: xi = |da/dt| / (da/dt)max, with (da/dt)max = 10^(0.2H - 6.85) au/My, applied to all 10,953 NEAs; keeps xi <= 3.
- Greenberg et al. 2020 [V]: Yarkovsky efficiency for 247 NEAs with density from SBDB, from taxonomic type, or 2470 kg/m3; median 0.12 (+0.16/-0.06); values above 0.5 flagged; three or four above 1 called unphysical (the paper gives both counts).
- Fenucci et al. 2024 [V]: every S/N >= 3 detection compared with the 95th percentile of a Monte Carlo maximum drift (obliquity at 0 or 180 deg, density from a population model); 88 of 461 fail.

And Yarkovsky to density, as point estimates, across a sample:

- **Dziadura et al. 2023, A&A 680, A77** [V, text as reproduced in the author's PhD thesis]. Densities "for all accepted and marginally accepted results" (57), ten dropped as physically implausible, the rest shown as a histogram "grouped according to taxonomic class". Compared with three literature densities.

Not found: the bound run in the direction "measured drift and size give a density ceiling", reported per object as a test of a high-density (metal) hypothesis. Nugent et al. 2012 state the idea in a sentence ("constraints on composition (i.e. metal vs. rock)") and do not carry it out.

### F. Systematic search for anomalous accelerations; the July 2026 JPL proposal. PARTLY CONFIRMED

- The July 2026 item is **Farnocchia, Hainaut, Seligman et al., "Non-gravitational acceleration indicative of cometary activity of near-Earth object", Nature Astronomy 10, 1283-1291**, received 6 March, accepted 4 June, published 10 July 2026, open access [V]. https://www.nature.com/articles/s41550-026-02913-7
- It is a one-object paper (1998 SH2: A2 = (-1.4 +/- 0.1)e-11 m/s2, found after a failed Goldstone track, then a tail imaged). It has no catalog-wide search, no thresholds and no list. Its only population statement: "as of late 2025 there are 2009 known near-Earth asteroids with a Jupiter Tisserand parameter between 2 and 3 ... 285 of these objects ... are classified as potentially hazardous asteroids ... the most promising candidates for future detections of activity" [V].
- The "screen all NEOs" idea is one sentence in the NASA/JPL press release: "By analyzing the motion of all near-Earth objects using precision astrometry data, researchers may reveal more comets that were previously designated as asteroids" [V, astrobiology.com reprint, 19 July 2026].
- Status: no paper, abstract or product found. arXiv author searches for Farnocchia and Seligman from 2025-01 to today return nothing of the kind.
- For the transverse component, systematic threshold-defined searches exist, of the whole NEA list (Desmars 2015, 10,953 objects; Fenucci 2024, 5,308 candidates drawn from 32,396 NEAs, re-run monthly at ESA NEOCC) and of pre-selected samples (Greenberg 2020, 600; Del Vigna 2018, 538). Each produces a set of significant drifts too large for Yarkovsky (88 of the 461 with S/N >= 3 in Fenucci 2024). They are filed as spurious; Fenucci et al. say of two that the cause "is likely due to outgassing".
- Not published: the same for the radial and out-of-plane components (where the small "inner dark comets" appear); a list of the rejects presented as candidates; any efficiency or false-alarm statement. Seligman et al. 2023 and 2024 report 7 + 7 objects and do not describe how the population was screened [V].

### G. Ranking by information gain of a characterization observation. CONFIRMED

- NEOfixer [V]: "Final priority is estimated by multiplying Importance * Confidence * Benefit * Urgency, and dividing by Cost." Benefit compares "the current sky-plane uncertainties to the expected astrometric accuracy". That is an expected-uncertainty-reduction ranking, for astrometry only. No spectra, colors or lightcurves enter. https://neofixer.arizona.edu/faq/how-does-neofixer-assign-priority
- Cortese, Perozzi, Micheli et al. 2017, Meteoritics & Planetary Science 52, 522 [S; publisher and repository pages refused access]: a published priority list for NEA *physical* observations with Importance and Urgency scores, delta-v among the columns, posted on the NEOShield-2 portal. A ranking for characterization with accessibility in it, but not by what would be learned.
- MANOS [V, Moskovitz 2026]: rules (delta-v < 6 km/s, H > 20, MOID < 0.05 au, V <~ 22).
- LCO NEOexchange [V]: merit function on time since last seen, arc, V, H, digest2 score and declination for unconfirmed candidates; NHATS objects are taken as characterization targets without a value ranking.
- Rubin follow-up: Wagg et al. 2024 (arXiv:2408.12517) [V, abstract] prioritises confirmation follow-up (predicts Rubin self-recovery with 68% accuracy). Astrometric.
- ESA NEOCC priority list [S]: astrometric, being retired in favour of NEOfixer.
- A code-repository issue proposing value-of-information ranking of NEO observations for orbit and impact decisions exists (github.com/Luminous-Dynamics/symthaea, issue 11112) [S]. Not composition, not published work.
- Not checked: IAWN campaign target selection.

### H. Per-object probability of lunar or artificial origin. PARTLY CONFIRMED

- **Wu et al. 2025 (arXiv:2510.23155)** [V]: encounter speed below 2.4 km/s occurs for 2.8% of lunar-origin asteroids against 0.05% of NEAs; "a newly discovered NEA with v_inf < 2.4 km/s may have a probability as high as 30% of being of lunar origin", with lunar-origin objects at <~1% of all NEAs. A conditional probability on one feature.
- **Fenucci et al. 2026 (arXiv:2601.08923)** [V, abstract]: for Kamo'oalewa-like objects, 1.23 +/- 0.13 expected from the main belt against 0.042 from Giordano Bruno ejecta. That is a single-object odds statement (about 3% for that crater).
- **Alessi & Jedicke 2026 (arXiv:2604.13296)** [V]: >~70 lunar co-orbitals above 10 m (orders-of-magnitude uncertainty) against 1589 +/- 40 from the main belt; 97 known co-orbitals with per-object NEOMOD3 main-belt source probabilities; seven named as "likely to have a main belt provenance". No per-object lunar probability.
- New, and it changes the test set: **Fedorets et al. 2026 (arXiv:2610.17981, 13 Oct 2026)** [V, abstract]: the lunar-like spectrum of Kamo'oalewa "was recently found to be flawed"; quasi-satellite 2025 PN7 is B-type; "Our results therefore still support an asteroid-belt origin for most of Earth's QSs." Zhang et al. 2026 (arXiv:2603.28102) title: Kamo'oalewa "probably develops an Itokawa-compositional but ultra-highly space-weathered surface" [V, title]. Tianwen-2 was due at Kamo'oalewa in summer 2026 (per Alessi & Jedicke); I did not look for encounter results.
- Artificial origin: JPL Scout gives a 0 to 100 "geocentric" score, for unconfirmed objects only, and says its scores are "meant to identify interesting objects rather than provide a rigorous probability assessment" [V]. Nothing per-object for designated NEAs.

### I. Pooled, H-conditioned base rate with between-survey variance. PARTLY CONFIRMED

- **Moskovitz et al. 2026 (arXiv:2603.15872), section 7, figures 9 and 10** [V]. Pools NEOSHIELD2, MANOS spectra and colors, and MITHNEOS visible data: "classifications for a total of 831 objects with robust sampling from H = 13 to H = 29". Fractions per 2-magnitude bin, 30 to 156 objects per bin, Poisson errors of 1 to 6%. S+Q: 70% at H = 14, 50% at H = 22, 35% at H = 28; linear-regression p = 0.004 (S+Q) and 0.005 (X).
- Missing from it: any between-survey variance term. The surveys barely overlap in H (MITHNEOS below 20, NEOSHIELD2 20 to 22, MANOS above 22), so survey and size are confounded and the variance could not have been estimated from that pool. Near-infrared surveys (Sanchez 2024, UKIRT) and NEOROCKS were left out on purpose. Not debiased.
- López-Oquendo et al. 2026 [V]: 40.4 +/- 7% S-type below 150 m; notes the disagreement with Sanchez 2024; cites one more small-NEO survey (Ngwane et al. 2026), which I did not read.

### J. Systematic area-to-mass catalog. CONFIRMED

- Fenucci et al. 2024 [V]: radiation pressure "has been detected through orbit determination only on a short list of NEAs", and adds one (2021 GM1, 0.2564 +/- 0.0257 m2/t).
- Del Vigna et al. 2018 [V]: tried the H > 24 members of a 538-object sample; four detections.
- JPL SBDB today [my count]: 21 NEAs carry A1, 12 at 3 sigma or better, 18 of the 21 on the NHATS list. 623 NEAs (1.44% of 43,158) carry any non-gravitational parameter; 174 of them are NHATS objects, which reproduces the round-1 figure.
- arXiv searches on "area-to-mass" with asteroid return only single-object papers.

## 3. Work from 2025 to 2026 that could overtake parts of the plan

| When | What | Touches |
|---|---|---|
| 2 Dec 2026 (in 11 days) | **Gaia DR4**, 66 months of data [V, ESA release page]. Dziadura et al. 2024 already got 43 robust NEA detections from the interim release and expect many more. | D, E, F: a wave of Yarkovsky papers within months |
| 12 Nov 2026 | Euclid DR1 survey paper on arXiv (2611.17040) [V, title]. Dorsey & Granvik expect Euclid near-infrared classes for about 1e4 NEOs. | A, I: new labels |
| Sept to Oct 2026 | Dorsey & Granvik EPSC2026-1111 (talk, 9 Sept) [S]; Simon et al. 2026 (arXiv:2610.07395) with new Brož et al. 2026 family maps [V] | A: the orbit-to-class prior is being rebuilt by its owners |
| 2026 | Moskovitz 2026; López-Oquendo 2026; Ngwane 2026 | I |
| July 2026 | Farnocchia et al., Nature Astronomy, plus the JPL "analyse all NEOs" sentence | F |
| 2024 to 2026 | Levine talk; White thesis; Taylor et al. 2024. All from or near the Seligman group, all on injected accelerations in Rubin-style simulations | C: a refereed Rubin injection-recovery paper is plausible soon |
| June 2025 | Kurlander et al. (arXiv:2506.02487): full simulated LSST solar-system catalog made public (127,000 NEOs) [V, abstract] | C: a ready test bed, and a competitor's |
| 2025 to 2026 | Wu 2025; Jedicke 2025; Alessi & Jedicke 2026; Fenucci 2026 (two papers); Fedorets 2026; Tianwen-2 at Kamo'oalewa | H |
| May 2026 | Tinaut-Ruano, Mahlke et al. (arXiv:2605.06838): taxonomy of 14,042 asteroids from Gaia DR3 spectra [V, title] | labels for the "what is known" table |

Named authors with nothing relevant found on arXiv in 2025 to 2026: Devogèle, Thirouin, Micheli, Makadia, Nesvorný (beyond co-authorships above), Sanchez. Author-name queries are noisy, so this is weak evidence.

## 4. What I could not do

- **No full-text search engine.** OpenAlex refused keyless requests (daily budget exhausted), Semantic Scholar returned 429, NASA ADS needs a key. Coverage is therefore arXiv title and abstract search, general web search, and full-text reading of the candidates those surfaced. A paper that scores a predictor in its body without saying so in the abstract could have been missed. This matters most for claim A.
- **Conference archives were not searched systematically.** EPSC was reached through web search restricted to the Copernicus site; LPSC, ACM, PDC, DDA and IAC only through general web search.
- Not read in full: Jedicke et al. 2018; Cortese et al. 2017 (403 and 401); the Levine talk page (connection refused, no archive copy); the White thesis body; Ngwane et al. 2026.
- A&A blocked direct downloads. Deshapriya 2023 was read from an Internet Archive copy, Dziadura 2023 from the reproduction in the author's thesis.
- No claim here was tested by computation except the SBDB counts.

## 5. Sources

Primary sources read:
- https://www.nature.com/articles/s41550-026-02913-7 (Farnocchia et al. 2026)
- https://astrobiology.com/2026/07/19/nasa-study-finds-near-earth-asteroid-is-actually-comet/ (JPL release reprint)
- https://arxiv.org/abs/2410.06874 (Taylor et al. 2024)
- https://arxiv.org/abs/2310.00055 (Hung et al. 2023)
- https://arxiv.org/abs/1501.01873 (Desmars 2015)
- https://arxiv.org/abs/2311.10175 (Fenucci et al. 2024)
- https://arxiv.org/abs/1708.05513 (Greenberg et al. 2020)
- https://arxiv.org/abs/1805.05947 (Del Vigna et al. 2018)
- https://arxiv.org/abs/1204.5990 (Nugent et al. 2012)
- https://arxiv.org/abs/1212.4812 (Farnocchia et al. 2013)
- https://arxiv.org/abs/2411.09750 (Dziadura et al. 2024)
- https://bip.amu.edu.pl/__data/assets/pdf_file/0026/517058/Dziadura-Karolina_rozprawa-doktorska.pdf (Dziadura thesis, contains Dziadura 2022 and 2023)
- https://arxiv.org/abs/2212.08115 ; https://arxiv.org/abs/2412.07603 (Seligman et al. 2023, 2024)
- https://web.archive.org/web/2024id_/https://www.aanda.org/articles/aa/pdf/2023/06/aa45316-22.pdf (Deshapriya et al. 2023)
- https://arxiv.org/abs/2305.16392 (Murray 2023)
- https://arxiv.org/abs/2610.07395 (Simon et al. 2026)
- https://arxiv.org/abs/2608.28779 (López-Oquendo et al. 2026)
- https://arxiv.org/abs/2603.15872 (Moskovitz et al. 2026)
- https://arxiv.org/abs/2510.23155 (Wu et al. 2025)
- https://arxiv.org/abs/2604.13296 (Alessi & Jedicke 2026)
- https://arxiv.org/abs/2102.10144 (Lister et al. 2021, NEOexchange)
- https://neofixer.arizona.edu/faq/how-does-neofixer-assign-priority
- https://cneos.jpl.nasa.gov/scout/intro.html
- https://www.cosmos.esa.int/web/gaia/release

Abstracts only: arXiv 2601.08923, 2610.17981, 2504.17985, 2408.12517, 2309.03555, 2506.02487, 2512.17191, 2605.27683, 2406.19727.

Search summaries only: https://mds.marshall.edu/etd/2060 (White 2026); https://project.lsst.org/meetings/rubin-2024/node/74 (Levine 2024); https://onlinelibrary.wiley.com/doi/full/10.1111/maps.12810 (Cortese et al. 2017); https://meetingorganizer.copernicus.org/EPSC2026/EPSC2026-1111.html; https://scholarsmine.mst.edu/geosci_geo_peteng_facwork/1362 (Jedicke et al. 2018).

Scripts and downloads:
- data/research/scripts/nr_arxiv.py (arXiv API queries), with query lists nr_q1.tsv to nr_q4.tsv in the same directory
- data/research/scripts/nr_axml.py (parse saved arXiv results)
- data/research/scripts/nr_getpdf.sh (fetch and convert PDFs)
- data/research/scripts/nr_grep.py (context search in paper text)
- data/research/scripts/nr_sbdb_ng.py (SBDB non-gravitational counts)
- data/research/scripts/nr_openalex.py (written, unusable: service refused)
- data/research/dl/novelty-refute (arxiv/, pdf/, web/)
