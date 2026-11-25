# Verification: recent mission and industry facts

Checker run of 2026-11-21, against primary sources. It checks claims made on 2026-11-20 in `industry.md`, `novelty.md` and `ground-truth.md`.

Verdict words: confirmed, partly confirmed, refuted, unverifiable. "Read" means I fetched the source myself today; summaries from a search engine are marked as such.

## Summary of verdicts

| # | Claim | Verdict | Main correction |
|---|---|---|---|
| 1a | Karman+ Prospector repository as described | Confirmed | It can promote a body with no measurements of its own (population spin prior); schema has an 11th column, `name` |
| 1b | CivLabs Atlas is a competing catalogue | Refuted (as a competitor); page content unverified | It is a 369-body hand-written location reference |
| 2 | AstroForge DeepSpace-2, IM-3, 28 candidates, 2022 OB5 paper | Confirmed | IM-3 is now "March/April 2027", not firmly Q1 |
| 3 | Karman+ mid-2028, Apophis, technology demonstration, $20M seed | Confirmed | none |
| 4 | Hayabusa2: Torifune flyby, 1998 KY26 dropped, 2015 BM510 | Confirmed | Briefing dated 17 November 2026; a degraded ion-engine mode still runs |
| 5 | Tianwen-2 at Kamo'oalewa; JWST size | Confirmed for arrival and JWST; no sampling or composition result exists yet | "First image suggests about 20 m" not verified |
| 6 | Hera arrived at Didymos in November 2026 | Confirmed | Exact arrival day not stated by ESA in what I read |
| 7 | TransAstra bag test 16 November 2026; SpaceX S-1 | Confirmed | S-1 mentions asteroid mining about 15 times, not in "one sentence"; the wording is "do not exist today" |
| 8 | ASIME 2016 and 2018 and the three quoted positions | Confirmed | none |
| 9 | Cannon, Gialich and Acain 2023 grades and statement | Confirmed | 90th percentile is 107.86 ppm; values are for 100% metal |
| 10 | Alessi and Jedicke 2026 lunar co-orbitals | Confirmed | 71 nominal, 1589 +/- 40 main-belt, about +/-5 orders of magnitude |
| 11 | Lopez-Oquendo 2026 and Moskovitz 2026 | Confirmed | none |
| 12 | Depue / Wolk / Farritor dwarf-planet candidate | Unverifiable; no designation or write-up found | A Rubin object matching the description, 2026 EE138, was published by the MPC on 27 October, two weeks earlier |

## 1. Karman+ Prospector and CivLabs Atlas

### 1a. Prospector repository: confirmed, with three corrections

Source: the repository itself, cloned anonymously on 2026-11-21 (https://github.com/Karmanplus/prospector, head commit `48d464a`, "Prospector 0.4.3", 2026-09-15), and the GitHub API record for it.

| Item | First-round claim | What the repository shows |
|---|---|---|
| Exists, public | yes | Yes. `Karmanplus/prospector`, organisation account, not a fork. |
| Created | 2026-08-27 | `created_at` 2026-08-27T22:15:37Z. Confirmed. |
| Licence | Apache-2.0 | Apache-2.0 (`LICENSE`; `NOTICE` says "Copyright 2026 Karman+"). Confirmed. |
| Stars | 12 | 12 stars, 1 fork, 2 watchers, 1 open issue. Confirmed. |
| Activity | not stated | 5 commits in total, each a squashed release: 0.3.3 on 2026-09-08, then 0.4.0 to 0.4.3 all on 2026-09-15. Nothing pushed since 2026-09-15. 5 tags, no GitHub releases. The one issue (2026-10-29, an outside company asking about water as a propellant) has no reply. The one fork has no commits of its own. |
| Sources merged | SsODNet, Lowell astorb, Ondrejov periods, MANOS spectra | Confirmed. `sources/ssodnet.py` (through the `rocks` package: H, albedo, taxonomy, period, colours), `sources/astorb.py` (Lowell AstorbDB GraphQL: albedo, taxonomy, lightcurve period, tumbling flag, lightcurve quality code, and the whole spin catalogue), `sources/surveys.py` (Pravec's `newres.txt` for periods; the MANOS API at `manos.lowell.edu/api/v1/observations/statuses`, spectra only). Also JPL SBDB and Horizons for the population, and the Toliou, Granvik and Tsirvoulis 2021 minimum-perihelion table (about 1.3 GB). |
| Output | letter tier S/A/B/C/D | Confirmed. `tiers.py`: `TIER_ORDER = ("S", "A", "B", "C", "D")`. |
| "Unknowns never promote" | quoted | In the `tiers.py` docstring verbatim: "Unknowns never promote. A body with no measurements lands in ``C``". See correction 1. |
| Deterministic | yes | Confirmed. Fixed thresholds: albedo <= 0.1 counts as dark; cohesion 1 / 3 / 5 Pa; stability 0.9 / 0.7; a tumbler with period <= 5 h drops one tier; an M-type drops one tier. |
| Enrichment columns | `input_id`, `taxonomy`, `albedo`, `period_h`, `diameter_m`, `cohesion_pa`, `p_gt_pcrit`, `q_min_au`, `hydration_class`, `tier` | Confirmed, with one column missing from the first-round list: `name`. Exact order in `schema.py`: `input_id, name, tier, taxonomy, albedo, period_h, diameter_m, cohesion_pa, p_gt_pcrit, q_min_au, hydration_class`. Units: hours, metres, pascals, au. Accepted aliases: `period`, `diameter`, `cohesion`, `p_crit_cdf`, `q_min`, `hydra_class`. Extra columns are kept. `input_id` is the SBDB primary designation. |
| Publishes an output list | no | Confirmed. No target table, no leaderboard, no enrichment output. `data/` and `configs/` are git-ignored. The only shipped run is a vehicle sweep for the Dawn example. |
| "No calibrated inputs" | quoted | Karman+'s own phrase, in the release post of 2026-09-16: "Someone who clones the repository gets a solver ladder and no calibrated inputs." See correction 2. |

Corrections:

1. **"An unmeasured body lands in tier C" is what the docstring says, not what the code does in every case.** The structural test passes on either of two inputs: the cohesion that this body's own measured spin requires, or `p_gt_pcrit`, which is computed from the body's H and the period distribution of all catalogued bodies within 0.75 mag (a Johnson S_B fit to the AstorbDB spin catalogue). A body with only an H therefore gets a `p_gt_pcrit`, and `assign()` returns tier A when it is >= 0.9 and tier B when it is >= 0.7, with no measurement of the body itself. So Prospector already uses one population prior (spin by size), and that prior can promote. It has no population prior for composition: "valuable" needs a catalogued C/B/D taxonomy or a measured albedo <= 0.1.
2. **"No calibrated inputs" refers to the mission-design config library, not to composition.** The post says the library holds "our engine models, our vehicle definitions, our corrections to published measurements" and "never ships with the code, by deliberate design". The repository confirms a local overrides file (`enrichment-overrides.yaml`) through which an installation replaces catalogue values, or the computed tier itself. Karman+'s own overrides are not published.
3. **The repository does contain one tested statistical model.** The hydration classifier (classes H12, H3, H4, H5) is a small neural network fitted to 630 RELAB meteorite spectra; features are albedo, the 0.7 micron band depth and four principal-component scores in the Mahlke 2022 taxonomy. Its docstring reports "about 94% of the held-back test data right" and says at once that the number is generous, because 429 of the 630 spectra are H5 and H3 "came down to four test samples". It is tested on meteorites, not asteroids; it is display-only (it does not feed the tier); it needs a MANOS spectrum or SsODNet colours, and the optional `classy` package. `docs/validation.md` checks trajectories against four flown missions (Dawn, Psyche, Hayabusa2, DART). Nothing checks the tiers against known asteroids.

Other facts the first round did not report: characterization runs for "the 5,000 reachable targets nearest in delta-v" at a time; diameter uses the measured albedo, else the class median (Marsset), else 0.15; cohesion assumes density 2,000 kg/m3 and friction angle 32 degrees for every body; when sources disagree, "an explicitly preferred measurement wins; failing that, the last one in the list", in the order ssodnet, override, astorb, ondrejov; each measurement keeps its source label. The MANOS record is used only for its spectrum, not for MANOS's own taxonomy or period.

Release post (primary): https://www.karmanplus.com/prospector-rapid-prototyping-for-deep-space/ , Teun van den Dries, 2026-09-16 (read as raw page).

### 1b. CivLabs Atlas: not a competing catalogue

Source: https://civiemlabs.com/atlas/2022-ob5 (application shell and its script bundle, fetched 2026-11-21).

- CivLabs is a web application by Civiem LLC: a suite of space-engineering tools (requirements, schematics, mechanical design, a solar-system map, calculators, an assistant).
- Its own description of Atlas: "Location reference. What every place is and what it is good for (colonization, resources, transit, megaprojects), the solar system first, other stars and galaxies beside it, written and maintained by the people who use it." Status beta. The bundle states 369 catalogue records (361 bodies), "each with its own dossier and specifications", data revision of 2026-09-02, with community editing.
- So the 2022 OB5 page is one dossier in a 369-body, hand-written reference (planets, moons, dwarf planets, notable small bodies). It is not a per-object probabilistic catalogue of the mission-accessible list. The description of the companion map says "Candidate-scoring is a separate tool, later": a scoring tool is intended and not built.
- Limit: the site's `robots.txt` refuses AI agents by name and says the content is not to be used as a search-grounding corpus. I stopped at the application shell and did not read the 2022 OB5 dossier. What the dossier says about 2022 OB5 is unverified.

## 2. AstroForge: confirmed, with a later launch date

| Item | Verdict | Evidence |
|---|---|---|
| Mission is called DeepSpace-2 | Confirmed | AstroForge's own pages and posts use only "DeepSpace-2" (posts of 2025-09-16, 2026-06-03, 2026-06-15). |
| Formerly Vestri | Confirmed in substance | A Safran press release of 2025-08-10 still calls it "Vestri"; AstroForge's post of 2025-09-16 calls it DeepSpace-2. The rename post on X (id decodes to 2025-09-10) could not be read. |
| Not yet launched | Confirmed | AstroForge home page today: "Next mission. Launching Q1 2027. DeepSpace-2". The mission page header says "LAUNCHING 2027" while its body text still says "Launching in the fourth quarter of 2026" (stale). |
| Rides with IM-3, Q1 2027 | Partly confirmed | Intuitive Machines' third-quarter release, 2026-11-12: IM-3 "remains on track for a planned launch in the March/April timeframe". NASA's IM-3 page (updated 2026-10-21): "Early 2027". So the current company statement is March or April 2027, the end of Q1 or just after it. |
| "About 28 candidate asteroids", no fixed target, June 2026 | Confirmed | Aerospace America (AIAA), Aspen Pflughoeft, 2026-06-15: the target is one of "about 28 candidate asteroids" thought to be metal; "AstroForge will choose among them closer to launch"; it will "attempt to photograph the target asteroid and perhaps attempt to land, or at least crash into it"; cost "around $10 million"; 200 kg. A search summary quotes the CEO: "We will pick a target probably a couple days before launch, once we're on the pad" (not read at source). AstroForge's page says only "TARGET: Near-Earth metallic asteroid", rendezvous at T + 1 year, 20 million km from Earth. No source since June names a target. |
| 2022 OB5 "up to 100 meters" | Confirmed | SpaceNews, Jeff Foust, 2025-01-29: Gialich said it is "up to 100 meters across and not an S-type stony asteroid"; it "could be metallic"; within two million km of Earth at flyby; another candidate with a higher chance of being M-type was ruled out. |
| arXiv:2605.04784 | Confirmed | See below. |

**Alarcon et al. 2026** (read in full): "Accessible does not mean exploitable: HiPERCAM reveals the ultra-fast rotation of 2022 OB5". Authors: Miguel R. Alarcon, Javier Licandro, Miquel Serra-Ricart, David Garcia-Alvarez, Antonio Cabrera-Lavers. arXiv 2026-05-06; Icarus 117153 (2026), accepted 4 May 2026. https://arxiv.org/abs/2605.04784

- Measured: rotation period 1.542 +/- 0.001 min from five-band HiPERCAM photometry on the 10.4-m GTC, confirmed at 1.544 +/- 0.007 min with the Two-meter Twin Telescope on 2026-01-14.
- Class: featureless, moderately red, X-complex; best match Xc, next Xk. MANOS had reported Xe (Moskovitz et al. 2026); the authors do not see the 0.49 micron feature of Xe. Checked in the MANOS paper: MANOS observed 2022 OB5 on 2025-02-02, H 28.96, class Xe, and the z band is missing for it because the signal was too low.
- Size: "from about 2 m (albedo 0.7, H 29.5) to about 15 m (albedo 0.03, H 28.5)". The abstract calls it "sub-10-metre".
- Density "could plausibly span" 1,800 to 4,900 kg/m3, because E, M and P classes cannot be separated without an albedo.
- Centrifugal acceleration at the equator is at least 50 times surface gravity.
- Conclusion: the rotation "poses severe practical challenges for any surface operation with current technology, regardless of compositional interest"; fast rotators are at least 94% of objects with H > 26; the criterion P > 1 h for surface operations is failed "by more than two orders of magnitude"; "rotation period measurement is therefore an indispensable prerequisite for evaluating the resource potential of asteroid mission candidates".
- Local snapshot check: SBDB H = 28.99, 49 observations, 2022-07-28 to 2026-01-16, condition code 0. NHATS: 2.8 to 12 m, minimum round-trip delta-v 3.517 km/s. Matches the first round.

New, not in the first round: AstroForge now lists a second 2027 mission, "Autonomy-1", on the first Stoke Space launch, NASA-backed, "expected to gather scientific data about the sun" (TechCrunch, Tim Fernholz, 2026-09-22; AstroForge home page). It is not an asteroid mission.

## 3. Karman+: confirmed

Source: https://www.karmanplus.com/k-mission-1-99942-apophis/ , Teun van den Dries, published 2026-07-21 (raw page read).

- "our original launch in early 2027 slipped because our propulsion vendor could not deliver on time. We had to scramble to find a new slot, which ended up being a mid 2028 launch."
- "Our leaderboard of asteroid targets updated with this new launch and showed asteroid Apophis at the very top, as it is on its close approach to Earth right at the time that we hit Earth escape."
- "Apophis is a target of opportunity for us, we would prefer a C-type rubble pile with lots of water over the desert environment we'll likely find. But this first mission is a technology demonstration, not a mining mission with customers waiting for water."
- The post calls Apophis "an S-type asteroid (a dry ball of dirt)".
- $20M seed: TechCrunch, Ingrid Lunden, 2025-02-19: Karman+ "has now raised $20 million in a seed round", led by Plural and Hummingbird, first launch then aimed at 2027. I did not find a Karman+ page stating the figure; Plural's own post (2025-06-11) gives no amount.

## 4. Hayabusa2 extended mission: confirmed from the JAXA briefing document

Source (primary): JAXA Hayabusa2 extended mission team, press briefing document dated 2026-11-17, 27 pages, https://www.jaxa.jp/projects/files/youtube/hayabusa2-extended-mission/jaxa_doc01_20261117.pdf (read in full). Secondary: AstroArts, 2026-11-19, https://www.astroarts.co.jp/article/hl/a/14778_hayabusa2 .

- **Torifune flyby**: 2026-07-05 18:29 JST. About 744 m from the centre, about 400 m from the surface (JAXA: the closest flyby ever), relative speed 5.3 km/s, about 120 m from the aim point. Confirmed.
- **Ion engines**: orbit control toward the December 2027 Earth swing-by began on 9 July 2026. In mid-August the ion engine system discharged repeatedly and stopped working normally. Thrusters A, C and D had reached their limits earlier. Thruster B, the last one, had been run above its design flow since September 2023; its ion source short-circuited in August 2026 and took a power supply with it. A "cross" mode (B's neutraliser with D's ion source) works, but its remaining life cannot be predicted. Xenon is not the limit: 57.3 kg used, more than 9.2 kg left.
- **1998 KY26 dropped**: the leg to 1998 KY26 needs 650 m/s (over 10,000 hours of thrusting), about 200 m/s of it before the 2027 swing-by. JAXA judged that plan "difficult" and changed the destination. The chemical thrusters can give about 30 m/s reliably.
- **New target 2015 BM510**: flyby in April 2028; needs 24 m/s; orbit quality good (condition code 1); H 25.0; phase angle at flyby about 36 degrees; relative speed about 6 km/s; aim distance "a few hundred metres from the centre". Properties given by JAXA: D-type, 17 to 74 m, rotation period 0.81 h (about 49 minutes, lightcurve from Thirouin et al. 2016), perihelion 0.83 au, aphelion 1.06 au. Observable from Earth from late 2026 to early 2027. Orbit control from late October 2026 for one to two months.
- Other candidates listed: 2022 UT8 (May 2032, 27 m/s, poor orbit) and a second Torifune flyby (October 2031, 37 m/s).
- JAXA says this would be the first flyby of a body a few tens of metres across and the first visit to a D-type fast rotator. The onboard camera will see the asteroid only about 10 hours before the flyby (14 days for Torifune).
- Revised success criteria (page 25): reaching 2015 BM510 and passing within 300 km counts as success; beating ground-based resolution needs a pass within about 10 km. JAXA's simulated images assume a 50 m body: outline resolved at 5 km, boulders at 1 km and closer. So a "successful" flyby could still return little about size and shape.
- The document shows a visible spectrum for the D-type class but the extracted text names no source for it.
- "16 to 19 November" in the first round is the spread of press coverage. The briefing document is dated 17 November 2026.
- Local snapshot check: SBDB H = 25.04, rotation 0.806 h, no taxonomy, condition code 1. **2015 BM510 is on the NHATS list**: 17 to 76 m, minimum delta-v 5.910 km/s, next optical window 2027-01-01 to 2027-02-19 at magnitude 23.2. 1998 KY26 is also on it (11 to 51 m, 7.845 km/s).

## 5. Tianwen-2 and Kamo'oalewa: arrival and JWST size confirmed; no sampling or composition result

- **Arrival**: CNSA announced on 6 July 2026 that the probe reached its planned position 20 km from 2016 HO3 after about 400 days and about 1 billion km; the first image was taken on 2 July 2026 from about 20 km. Source: Xinhua, 2026-07-06, carrying the CNSA release, https://www.news.cn/tech/20260706/080a1fa3614640a3893284f94d7799d8/c.html (read). Approach milestones in June (first optical capture 6 June, 2,000 km on 19 June) come from a search summary of the same release. I did not find the release on cnsa.gov.cn itself.
- **Status**: Science and Technology Daily, 2026-10-13: the probe "is conducting companion-flight exploration to prepare for sample return". Three sampling modes are designed (touch, hover, attach). I found no report of a sampling attempt and no published composition, mass, density or shape result from the spacecraft as of 2026-11-21.
- **Sample return in November 2027**: partly confirmed. Sky and Telescope (2026-07-09) says "back on Earth by late November 2027"; the dates of 24 April 2027 departure and 29 November 2027 capsule return come from Wikipedia through a search summary. No CNSA page with these dates was found.
- **JWST** (arXiv:2606.24017v3, read): Sharkey, Reddy, Noonan, Kareta, Bauer, Holler, Kim, Conrad; v1 2026-06-22, v3 2026-10-19; accepted to ApJ Letters (doi 10.3847/2041-8213/aea6b6). NIRSpec, February 2026. "mean diameter of D = 18 +/- 2 m and best-fit visible albedo 0.59 (+0.25, -0.17), with models as low as 0.36 providing adequate model fits"; rotation period 27.9 minutes; axis ratio about 1.4 "(D about 15 to 21 m)". The 15 to 21 m figure is the spread of the two axes, not a second confidence interval. Spectrum less red than ground data, a faint 0.93 micron band, no 2 micron band, "similar to oldhamite-bearing enstatite-rich compositions".
- Not verified: the first-round statement that the first image "suggests about 20 m". Sky and Telescope says "only 27 meters" without a source.
- Local snapshot check: NHATS still lists 24 to 107 m (H 24.3). The JWST diameter is below the bottom of that range.

## 6. Hera: confirmed

- ESA, 2026-11-05, "Hera's first close-up view of Didymos asteroids": image from 60 km after a "two-year flight"; "Detailed images of both asteroids will be unveiled on 25 November". https://www.esa.int/articles/about-us/directorates/operations/space-safety/hera/hera-s-first-close-up-view-of-didymos-asteroids
- ESA, 2026-11-11, "Hera spacecraft in 'rectangular orbit' around target asteroids": Hera "has arrived at its target asteroids", "30-25 km" away, flying rectangular arcs of three and four days; closer "detailed characterisation" from about 20 km next month; CubeSats "over the coming months". https://www.esa.int/articles/hera-spacecraft-in-rectangular-orbit-around-target-asteroids
- Neither article gives the day of arrival. "About six months of operations" is not in either article.

## 7. TransAstra test and the SpaceX S-1

- **TransAstra**: confirmed. Company press release, Los Angeles, 2026-11-16: the 10-metre "Mantis" capture bag completed "over 11 days of testing": full-scale inflation, structural validation, imaging for rendezvous sensors and closure. Closure was tested "with only three of the four drawstring mechanisms after a prototype gear failed". A 1-metre bag flew on the ISS in 2025. The release does not give the NASA award, the "New Moon" mission dates or a target count. https://www.newswire.com/news/transastra-successfully-tests-10-meter-capture-bag-designed-to-capture-22889775
- **SpaceX S-1**: confirmed, and now read at source (the first round had only press coverage). Form S-1, filed 2026-05-20, https://www.sec.gov/Archives/edgar/data/1181412/000162828026036936/spaceexplorationtechnologi.htm
  - "Asteroid mining. We plan to pursue asteroid mining operations to extract metals and other critical resources from near-Earth and main-belt asteroids, providing abundant raw materials for space-based industries and reducing the need to launch mass from Earth."
  - Risk factors: "Others, including in-orbit manufacturing, passenger transport to the Moon, [...] and asteroid mining do not exist today." The phrase "do not currently exist" is in the heading of that risk factor: "Several of our anticipated market opportunities [...] are still emerging and evolving or do not currently exist, and such markets may not develop as we expect, or at all."
  - Correction: it is not "one sentence". The word "asteroid" appears 15 times: in the list of future markets, the summary bullet above, two risk factors, a statement that in-orbit refuelling of Starship "is essential to our lunar, Mars, asteroid mining, and other deep space ambitions", a statement that these markets are not counted in the $28.5 trillion market estimate but "could eventually represent multi-trillion-dollar economic opportunities", and a paragraph headed "Asteroid Mining" that names "platinum-group metals, rare earth elements, nickel, cobalt, iron and water" and says "some near-Earth objects [contain] concentrations of elements far exceeding typical terrestrial ore grades".

## 8. ASIME white papers: confirmed

- ASIME 2016: arXiv:1612.00709, Graps and 30 co-authors, 81 pages, v2 2017-01-16. Questions came from "Planetary Resources, Deep Space Industries and TransAstra". https://arxiv.org/abs/1612.00709
  - Knowledge gap 4 (page 7): "What is needed is a map of low delta-v, low synodic period and low-albedo NEOs as a first-cut to fine-tune the target possibilities." Page 64 credits the idea to Abell.
  - Page 66: Sercel "says that 'inclinations more than a couple of degrees are really problematic.'"
- ASIME 2018: arXiv:1904.11831, Graps and 43 co-authors, 65 pages, 2019-04-25. https://arxiv.org/abs/1904.11831
  - Page 58, Sercel: "The appropriate paradigm for asteroid mining is FISHING, not prospecting. Therefore you go from Discovery to follow up observations, and then directly to a full-scale mining mission."
  - Page 58, "Bonin (DSI's perspective)": "having a priori immaculate knowledge is going to take too long. We prioritize doing a large number of missions because we expect a high failure rate."
  - Same page: Bonin, "That knowledge is so commercial and valuable.. we want to monetize that knowledge"; Galache, "that is very valuable data, not to freely give away".

## 9. Cannon, Gialich and Acain 2023: confirmed

"Precious and structural metals on asteroids", Planetary and Space Science 225 (2023) 105608, accepted 24 November 2022. Cannon is at Colorado School of Mines; Gialich and Acain are at AstroForge. Read from the copy at https://www.mining.com/wp-content/uploads/2023/04/Precious-and-structural-metals-on-asteroids-.pdf (doi:10.1016/j.pss.2022.105608).

- Table 2, total platinum-group metals in iron meteorites: 10th percentile 14.70 ppm, 50th 40.78 ppm, 90th 107.86 ppm. Terrestrial deposits for comparison: 1.07, 3.86, 7.36 ppm.
- These are "upper values because they represent 100% metal content".
- "Even if an object has high Fe-Ni metal content [...], there is no known way to remotely identify where an asteroid falls along the wide distributions of PGM grades shown in Fig. 4. The complete range of percentiles should be kept in mind, and the 50th percentile values (Table 2) provide a better expectation than the 90th percentiles as in Kargel (1994)."

## 10. Alessi and Jedicke 2026: confirmed

"The steady-state population of Earth's co-orbitals of lunar provenance", arXiv:2604.13296v2, Icarus 455, 117109 (1 September 2026). Read in full.

- Text: "Our nominal prediction is that there are 71 Earth co-orbitals larger than 10 m diameter in the steady-state population that originated on the Moon's surface." The abstract says "at least about 70".
- Main-belt co-orbitals above 10 m from NEOMOD3: 1589 +/- 40 (abstract: "about 1600").
- Uncertainty: "approximately +/-5 orders of magnitude systematic uncertainty".
- The abstract ends by noting that co-orbitals interest "commercial asteroid mining ventures because they are the lowest delta-v targets".

## 11. Lopez-Oquendo 2026 and Moskovitz 2026: confirmed

- **arXiv:2608.28779** (read): Lopez-Oquendo, Trilling, Mommert, Marsset, "Probing the Taxonomic Diversity of the Small Near-Earth Object Population", 2026-08-28, accepted by PSJ. UKIRT-WFCAM, 2016 to 2024, 371 observation sequences, "probabilistic taxonomic classifications for 122 NEOs, with diameters ranging from 5 m to 150 m and a median size of 60 m". Observed: S-complex and CX-complex "in nearly equal proportions". Debiased: "dominated by dark, carbonaceous (CX-complex) bodies".
  - The two numbers the first round had only second-hand are in the text (page 12): "only about 20% of the sample yielded maximum source probabilities exceeding 50%", and METEOMOD assigns "the majority of objects in our sample (54%)" to the Massalia family, then Koronis 22%, Veritas 10%, Phaethon 4%.
- **arXiv:2603.15872** (read): Moskovitz, Kareta and 14 others, "NEO Colors from the Mission Accessible Near-Earth Object Survey (MANOS)", 2026-03-16, accepted by PSJ. griz colours for 189 NEOs. Abstract: S-complex "decreases by a factor of two from about 65% of the population at km-scales down to a third at sizes below about 50 m". Body text: S+Q "goes from 70% of the sample at H = 14, to 50% at H = 22, and to 35% at H = 28". So "65 to 70%" is fair.
  - Label noise, from the same paper: without lightcurve correction, 32 of 49 objects (65%) changed taxonomic type.

## 12. The Depue / Wolk / Farritor dwarf-planet candidate: no designation or write-up found; a possible identification

What I could and could not read:

- The X posts could not be read (the post id decodes to 2026-11-11 21:40 UTC). Everything I have on the claim is from an aggregator that quotes the posts: "it's about 1/4 the width of Pluto and orbits about twice as far (way past Neptune)"; "looks like it's about the 50th largest object in our solar system"; later the same day, "We found another, just as large." (huggingnews, 2026-11-11).
- claudestronomy.com today lists no minor-planet or dwarf-planet result, designation, MPC submission or write-up from the programme. Its listed results are exoplanets, brown dwarfs, white dwarfs and variable stars by other people.
- I found no professional comment on the claim, no designation attributed to the group, and no paper or repository.

New finding, from the Minor Planet Center and JPL (one query each, 2026-11-21):

- On 27 October 2026, fifteen days before the Depue announcement, the MPC published two large trans-Neptunian objects found in Rubin Observatory data with archival DECam detections: **2026 ED138** (MPEC 2026-U85) and **2026 EE138** (MPEC 2026-U86, https://www.minorplanetcenter.net/mpec/K26/K26U86.html). Rubin announced 2026 ED138 publicly the same day as a dwarf-planet candidate of 600 to 1,500 km at about 46 au.
- **2026 EE138 matches every public detail of the Depue description.** H = 3.96, which is about 595 km at albedo 0.13 (a quarter of Pluto's 2,376 km is 594 km). Semi-major axis 71.1 au, eccentricity 0.51, now about 71.5 au from the Sun (Pluto is now about 35.6 au, so "twice as far"). Its observations are 20 from Rubin (2026-03-09 to 2026-06-26) and 11 from DECam archive images from 2013-04-01 to 2020, so it sat in a public archive for over ten years. The MPEC credits the Rubin team (Bernardinelli, Eggl, Heinze, Holman, Juric, Kurlander, Moeyens, Napier, Nourbakhsh) and credits the DECam measurements to Juric and Holman.
- I cannot establish that the Depue object is 2026 EE138; that needs the posts or the group's coordinates. The two readings are: (a) it is 2026 EE138 or 2026 ED138, in which case it was already designated and credited to Rubin before the announcement, and the agent work is at most an independent recovery; or (b) it is a different object, in which case nothing matching it has appeared in JPL's list of 488 objects with H < 6 beyond 30 au. In that list the only large distant objects added since mid-October are the Rubin pair.
- Script: `data/research/scripts/fm_tno_recent.py`; data in `data/research/dl/facts-missions/jpl` and `data/research/dl/facts-missions/mpc`.

Verdict: the first-round statement (no designation, write-up or professional comment found) still holds. The claim itself remains unverified, and there is now a specific reason to doubt that it is a new discovery.

## Implications for the plan

1. **Prospector is confirmed as the nearest existing tool, and it is narrower than a catalogue.** It is deterministic, it publishes no table, it has had no commits since 15 September, and its tier is not tested against known asteroids. The plan's distinct contribution (calibrated class probabilities, a composition prior for unmeasured bodies, published per-object output, validation) is not in it.
2. **Correct the description of Prospector in the plan.** Do not say it uses no priors. It uses a population spin prior (period distribution by H) that can lift an unmeasured body to tier A or B, and a population minimum-perihelion prior for display. It has no composition prior.
3. **The Prospector column contract is real and small, but there is no documented import.** The columns are `input_id` (SBDB primary designation), `name`, `tier`, `taxonomy`, `albedo`, `period_h`, `diameter_m`, `cohesion_pa`, `p_gt_pcrit`, `q_min_au`, `hydration_class`; extra columns survive `normalize()`. The code has no loader for an outside table. What it does have is a per-object cache that it reads before going to the network: one single-row Parquet file per body at `data/enrichment/v3/<slug>__<first 8 hex of sha1(input_id)>.parquet`. A project could ship files in that layout, or a YAML in the overrides format (`abs_mag`, `albedo`, `taxonomy`, `period_h`, `tier`). Both are internal formats that Karman+ can change (the cache directory is already at "v3"). The first-round phrase "loads directly as a Prospector enrichment table" overstates it.
4. **A dated, pre-registrable test now exists: 2015 BM510.** It is on the NHATS list (H 25.0, 17 to 76 m), JAXA calls it a D-type with a 49-minute period, and Hayabusa2 is to fly past it in April 2028, aiming for a few hundred metres. It has an Earth observing window in January and February 2027. The project can publish its size, class and spin statement for this object before the flyby. The flyby gives size and shape at best, not mass, and it depends on a spacecraft with one degraded ion-engine mode, a faulty reaction wheel and a target first seen 10 hours out.
5. **1998 KY26 is no longer a future ground-truth object.** Remove it from any list of expected known answers.
6. **Kamo'oalewa remains the only decametre rendezvous target, with no spacecraft result yet.** The JWST diameter (18 +/- 2 m) is below NHATS's printed range (24 to 107 m). Use it as a calibration case for size intervals now; do not plan on a composition answer before late 2027.
7. **2022 OB5 stands as the worked example**: "up to 100 meters" from the company, 2 to 15 m from H, 1.5-minute rotation, X-complex with density anywhere from 1,800 to 4,900 kg/m3, and two surveys disagreeing on the subclass (Xe against Xc) with one band missing.
8. **Commercial schedules moved right again.** DeepSpace-2 is now tied to an IM-3 launch in March or April 2027 with no named target; Karman+ is mid-2028 at Apophis. No commercial mission will return data on a small accessible object before 2028.
9. **Do not cite the Depue claim as a discovery.** Cite it, if at all, as an unverified announcement, and note MPEC 2026-U86. It is a ready example of why "recover known objects first" has to include checking the MPC's recent circulars.
10. **CivLabs Atlas can be dropped from the list of competitors.** Respect its robots.txt: do not scrape it.

## What I did not verify

- The text of any post on X (AstroForge rename, Depue, Wolk).
- The CivLabs dossier for 2022 OB5.
- The CNSA original release and any official Tianwen-2 return date.
- The exact day Hera arrived, and "about six months of operations".
- The CEO quote about picking the target "a couple days before launch" (search summary only).
- The Payload article of 2026-06-05 and the NASA manager's statement of 2026-09-15 on IM-3 (superseded by the 12 November release).
- Whether a pre-filled Prospector cache actually loads in the running app (read from the code only; I did not run downloaded code).
- Who classified 2015 BM510 as D-type, and from what data.

## Files

- Scripts (prefix `fm_`): `data/research/scripts/fm_arxiv_ids.py`, `fm_tno_recent.py`, `fm_local_lookup.py`. The earlier `nr_getpdf.sh` was reused for arXiv PDFs.
- Downloads (untrusted): `data/research/dl/facts-missions` with subfolders `prospector-clone`, `github`, `jaxa`, `karman`, `civlabs`, `astroforge`, `im3`, `arxiv`, `sec`, `cannon`, `jpl`, `mpc`.
- Requests to JPL: two in total (one object lookup, one list query), sequential. Requests to the MPC: four, sequential (one was a malformed request that returned an error).
