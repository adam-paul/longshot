# Plan: what public data can say about reachable asteroids

Written 2026-11-21 from two days of agent research, an independent check of it, and two rounds of review, then amended with the direction Adam gave that day (section 6). No project work has started. Section 7 lists what is still unverified. `DESIGN.md` overrides this file on anything about the site.

**Outcome.** The search for a missed signal came up empty. Nothing in public data says what a typical reachable asteroid is made of, and better targeting is not what holds asteroid mining back. What the research does support is a smaller project: a public ledger of what is and is not known about each reachable asteroid, with probabilities tested where known answers exist (the brighter quarter of the list), which objects can be ruled out as targets today, and which single observation would settle the most.

**Direction agreed.** Build a prototype first and show it before asking anyone for anything. Keep the research depth: the orbit test and the orbit refits stay on the roadmap as what a grant or more time would add. Lead with realism: the difficulty, the error bars, the likely unrecoverability, and what would have to change. Still open: the app's stack and where its state lives (`DESIGN.md`), the name, and a role email address for JPL's interface.

## Terms

- **Reachable asteroids**: JPL's NHATS list, the near-Earth asteroids a spacecraft could visit on a round trip of at most 450 days. 7,229 objects today.
- **Delta-v**: the total velocity change that round trip needs, at the best launch date. Lower is cheaper.
- **H**: absolute magnitude, the only size indicator most of these objects have. Lower H is brighter and bigger. Using reflectivities measured for about 1,600 larger near-Earth asteroids, H 22 is most likely about 100 m and H 24 about 40 m. Carrying the same conversion below the measured range gives about 15 m at H 26.2 (the list's median) and about 7 m at H 27.7 (the median under 5 km/s). About nine in ten measured objects fall between half and double the figure.
- **Class**: the colour or spectrum family (S stony, C dark and carbon-rich, X ambiguous between metal and two kinds of rock). It is the nearest thing to a composition label a telescope gives, and a loose one.
- **Drift**: a slow change in an orbit caused by the asteroid shedding heat unevenly. For a given size a lighter body drifts faster, so a large drift puts a ceiling on density. A small one proves nothing.
- **Radiation pressure**: the direct push of sunlight, measurable only on bodies a few metres across.
- **Sigma**: a measured value divided by its own error bar. Three is the usual bar for a detection.
- **Prior, base rate**: what is typical for asteroids of that brightness, used when nothing has been measured for this one.
- **Magnitude**: brightness in the sky; bigger is fainter. About 18 is the limit for a small telescope to time a rotation, about 20 for a 2-metre one, and 21–22 needs a 4-metre one.
- **Lightcurve**: brightness measured through a night. Its repeat time is the rotation period.
- **Karman+, AstroForge, TransAstra**: asteroid-mining start-ups. None has yet reached an asteroid.

## 1. What the research found

### 1.1 The ideas from 17 November

| Idea | Verdict | Why |
|---|---|---|
| Guess the class from the orbit | Fails wherever it can be tested; untested for the smallest | On about 1,700–2,100 asteroids with a known class or reflectivity, orbiting where every reachable asteroid does, the orbit improved the guess by nothing measurable. A smooth effect of 2–3% of what there is to know would have been caught, and one confined to the most Earth-like orbits at 5–8%. Those asteroids are far larger than the targets; only 21 of them are under 6 km/s. |
| Orbit drift as a density test | Survives, narrower than I said | 154 reachable asteroids have a measured drift, mostly the larger and costlier ones (9 are under 5 km/s). Only 61 have a measured size, so for the rest the result is density times diameter. Depending on the assumed reflectivity and safety margin, the drift excludes solid iron for roughly 15–85 of them and a porous metal-rich body for 3–27. The objects with the tightest ceilings are also the ones whose drift is most likely not thermal at all. |
| A set of known answers | Survives, small | About 12 near-Earth asteroids have a known composition: large bodies visited by spacecraft, and four metre-sized ones that hit Earth and left meteorites. About 18 have a directly measured density, none below about 150 m. None is the size of a typical target. |
| New surveys (Gaia, SPHEREx, Rubin) | Do not reach the targets | Gaia's 2022 release holds 8 reachable asteroids, and its next release on 2 December has the same brightness limit. None of 328 sampled was predicted bright enough for SPHEREx when it passed. Rubin has barely started. |

### 1.2 What turned up instead

- **Size and spin decide more than class, and both are poorly known.** All 21 measured rotation periods under 5 km/s are faster than 2.2 hours, the rate at which rubble with no cohesion would be flung off a body of ordinary rock density, and 16 are faster than 10 minutes. Fast spins are the easiest to measure, so the true share is lower, and slight cohesion lets small bodies spin faster and keep their surface. It is a screening line for surface work, not a physical limit. Nothing under 5 km/s is brighter than H 24.2, so each is most likely under 40 m, though about five of the 286 probably exceed it and nobody knows which. Both small mission targets later measured directly came out 2–3 times smaller than the working size. Correction, 24 November: a table not used in this count (Pravec's) adds four measured periods under 5 km/s, one of them 2.35 hours (2023 RA4), so the first sentence no longer holds as stated.
- **For the cheapest targets, tracking data says about as much as every other source, which is little.** Of the 286 under 5 km/s, 14 have any composition-related measurement and 21 a measured spin. 38 have enough tracking to look for radiation pressure (9 already have a JPL value), and trial fits suggest about a dozen would show anything. For those the result is mass per unit of area. With a size it tells very light from denser; the size is known for one of them. It cannot tell rock from metal. A mission that bags a whole small asteroid needs that number. That is the only sense in which there was something in the dynamics.
- **The orbit may still say where the cheapest ones came from.** About a third of the under-5 km/s list approaches Earth slower than 2.4 km/s. One 2025 paper puts the chance of lunar origin as high as 30% for such objects; other estimates are far lower, and some may be spent rocket stages. This corner is exactly where the orbit test has no data.
- **What the few measured ones are.** The 24 objects under 6 km/s with a class on file are the bright, easy ones: mostly stony or ambiguous, none firmly carbon-rich, and sources disagree on at least three of them.

### 1.3 On the premise

On this evidence, better targeting is not what would kickstart the industry. The binding constraints are money, spacecraft reliability and launch slips; SpaceX's own filing says these markets "do not exist today". The first missions are technology tests that filter on a guessed class and then choose by launch date and distance. Two company voices at a 2018 workshop argued against prospecting first. One called the right model "fishing, not prospecting": discovery, telescope follow-up, then straight to mining.

The missions after those do want more information:

- Karman+ calls rotation rate "one of the bigger unknowns for any asteroid we target".
- AstroForge's chief executive said of his own target, "I would like more information on the asteroid". In January 2025 the company called it "up to 100 meters"; public brightness already put it at 3–12 m, and it was later measured to spin every 92 seconds.

What they are asking for is measurements. This project makes none unless the observing requests in WP6 succeed. It shows which are missing and which would settle the most.

On water against metal: for metal, the grade of platinum-group metals has "no known way" to be identified remotely, by a 2023 paper two AstroForge founders co-wrote. For water there are usable signs (a dark surface, one absorption band), but the reachable objects are too faint for them today and only a few percent of near-Earth asteroids are expected to be hydrated.

### 1.4 What that leaves: elimination, with the unknowns kept

Candidates cannot be detected, but the list can be narrowed, provided "not measured" is kept apart from "ruled out". A sketch for one mission type, surface work on a larger body:

| | Under 5 km/s | Under 6 km/s | Under 7 km/s |
|---|---|---|---|
| All reachable | 286 | 726 | 1,388 |
| Brighter than H 24 (most likely 40 m or more) | 0 | 10 | 46 |
| Fainter, but probably 40 m or more because some surfaces are dark | about 5 | about 20–30 | about 50–65 |
| *Of those brighter than H 24:* orbit good enough to find again | 0 | 9 | 42 |
| Spin measured, slower than 2.2 hours | 0 | 1 | 7 |
| Spin measured, faster than 2.2 hours | 0 | 1 | 5 |
| Spin never measured | 0 | 7 | 30 |

- Size comes from brightness, so the first cut is a probability, not a measurement. Three of the ten under 6 km/s have measured sizes: about 105 m, 60 m and 33 m.
- The slow rotators under 7 km/s include Apophis, Bennu and 2008 EV5, so the filter finds answers already known. It also misses two targets Karman+ has named: one needs 7.2 km/s and one is slightly too faint. The real version must pass both or explain why.
- The one slow rotator under 6 km/s, 2011 AA37 (about 65 m), has a 10-hour period its source database grades as unreliable. Karman+ named it as a reference target in 2023.
- Of the seven never measured under 6 km/s, the spin prior says one to four are slow. Only one returns before 2030, at magnitude 21.6, beyond a 2-metre telescope. The rest wait until 2031–2037.
- 2001 CQ36 (5.8 km/s) shows drift and size working together. A 17-sigma drift and two size estimates near 60 m put its density below about 4,600–5,200 kg/m³ under the cautious rule in Appendix A. If the drift is thermal, that rules out solid iron and not a porous metal-rich body. Its spin is unmeasured and it cannot be observed again until 2031.
- Two unmeasured objects come within small-telescope reach soon. 2024 YP9 (about 80 m, 6.9 km/s) peaks near magnitude 17.2 in early December. 2026 HT, the brightest object under 5 km/s, peaks near 17.5 around March 2027, though its orbit rests on 57 days of tracking and it may need finding again first.

For a mission that bags a whole small asteroid, the size test runs the other way: 127 objects under 5 km/s are H 28 or fainter (roughly 6 m and under), 98 with a findable orbit.

These counts are a sketch from JPL's fields and fixed cut-offs. The real version uses probabilities and sourced thresholds per mission type.

## 2. Who it is for

| User | What they would take | Test of whether it is used |
|---|---|---|
| People curious about this frontier, including the claudestronomy community | An honest picture of each target: what is known, what it might be worth, how hard it is, and what would change that | They come back, argue with a prediction, or go and observe one |
| Observers with telescope time | A list of reachable asteroids ranked by what one lightcurve or colour would settle, with windows and brightness | A survey team says it would take the ranking as an input to its queue |
| Small mission teams with candidate lists | Per-object probabilities for size and spin, a mass range, and which candidates are already ruled out | One team compares it with its own list |
| Journalists, investors, anyone checking a claim | One plain sentence per object, with sources | It gets cited against a claim |

What already exists: a French service, SsODNet, lists what has been measured for each asteroid, and Karman+'s open-source Prospector sorts candidates into fixed tiers that have not been tested against known asteroids. Two literature searches found nothing that gives the unmeasured majority a tested entry, or that ranks reachable asteroids by what one observation would settle.

## 3. Science plan

### 3.1 Aim

For every reachable asteroid, state what is actually known, with probabilities tested against known answers where answers exist, and marked as untested extrapolation for the three quarters of the list fainter than H 25. Narrow the list by elimination. Say which single observation would most change each answer. Keep score in public as new data arrive.

### 3.2 Work packages

| Package | What it produces | Release | Limit |
|---|---|---|---|
| WP0 Foundations | Dated snapshots of every input, one identity per asteroid, the table of known answers, the written test protocol, the priors frozen as method 0.1 | Prototype, then R1 | – |
| WP1 Ledger | For all 7,229: what is measured, by whom, with conflicts shown, and a labelled prior where nothing is | Prototype | About 94% of entries hold nothing bearing on composition |
| WP2 Elimination and "observe next" | Per mission type: known pass, known fail, or untested with a probability. Untested objects ranked by what one observation would settle and when it is possible. A price range per object under named scenarios | Prototype | 21 objects under 6 km/s can be pointed at before 2030 brighter than magnitude 22; 6 are within reach of a 2-metre telescope |
| WP3 Orbit test | A reproduction of the class-from-orbit test, then one run on labels no analysis has read | R2 | The unread tables have not been obtained; there may be too few |
| WP4 Forecasts and density ceilings | The frozen priors scored as other people's observations arrive; density ceilings from JPL's published drifts | R2 | One to three mission results by 2030; real scoring depends on one outside survey |
| WP5 Dynamics catalogue | Our own refit of drift and radiation pressure: a value, an upper limit, or "this tracking carries no information" | R3 | About 180 objects yield a physical statement, and JPL already lists most |
| WP6 New observations | Messages to four or five observing groups and one free telescope request | R1; paid time later | Without new observations, 0–2 rotation periods a year arrive under 6 km/s |

Appendix C has the detail.

### 3.3 Validation in brief

The rules follow claudestronomy's standards: recover known objects first, inject fake signals to measure what a method can see, fix thresholds before looking, publish nulls and code, and have a fresh agent attack each result. Appendix A has the bars. The points that matter for deciding:

- Only results on labels nobody has analysed are called pre-registered. The trial analysis of 21 November already ran on about 2,700 labelled asteroids, so rerunning it there is a reproduction.
- Every bar that gates a release has a number that could fail. Where no test is possible yet, the page says "untested".
- Size from brightness is checked on a held-out half of the roughly 200 measured sizes before R1. Spin from brightness cannot be tested on the 330 known periods, which favour fast rotators and were used to set the prior. It is scored only on periods published after the freeze, a few a year, and is labelled untested until about 30 exist.
- A class predictor that misses its bar is published as a null. A fitter that misses its bar is not published; the failure is.
- A human expert reads each release before it goes public.

### 3.4 What this will not claim

- No single-number valuations. A price appears only as a range under a named scenario, with the chance of nothing printed first.
- No metal detection. The method sees dense objects worst.
- No water for small reachable objects. None of the small asteroids with unexplained accelerations has shown gas or dust.
- No composition for an individual small object beyond the base rate, until someone observes it.

### 3.5 Releases, gates and effort

Effort is my rough estimate in days like 20–21 November: agents running most of the day, you answering at gates.

| Release | Contents | Gate | Effort |
|---|---|---|---|
| R0 (private) | About ten awkward objects through every stage, offline from frozen snapshots, to one test page | Every fixture value matches its paper | 2–4 days |
| Prototype | WP1 and WP2 on existing catalogs, price ranges, provisional priors and an empty record, on an unlisted address marked as a prototype | Fixture values match primary papers; no source outage shows as "nothing measured"; the size bar is met | 6–10 days |
| R1 (public launch) | The rest of WP0, the WP6 messages and request, permission emails answered or the affected values removed | An expert has read it. Then the protocol and frozen priors are deposited and the site goes public | 4–6 days |
| R2 | WP3, WP4 | The confirmatory run is logged once and its verdict published whichever it is; expert read | 4–7 days |
| R3 | WP5 | JPL reproduction, upper-limit and false-alarm bars met; the second fitting program runs on the fixtures; expert read | 15–25 days |
| R4 | Dynamics joined into the mission requirements; figures a reader can move | Expert read | 5–10 days |

The prototype is what gets shown first, to claudestronomy and anyone else, with the later releases as what a grant or more time could add: telescope time for the "observe next" list, the confirmatory orbit test, the orbit refits, and keeping the record running to 2030. Outside interest is asked for after the prototype, not before. Whether to go on to R3 is decided at the R2 gate.

### 3.6 Risks

- **The ledger is mostly prior.** For about 94% of objects it will say that nothing bearing on composition has been measured. That is the result, and it is harder to get attention for than a ranking of targets.
- **It gets blanker over time.** About 650 reachable asteroids are found a year against 5–15 that gain a rotation period.
- **Others may publish first.** An author of one of the standard models of where near-Earth asteroids come from is building versions per class, and he co-authors Karman+'s conference abstracts. Gaia's release on 2 December will bring drift papers on the brighter asteroids within months.
- **A nearly-right fitter invents discoveries.** The trial run produced two formal 5–11 sigma signals that rest on one observation or one pairing of observations.
- **Agent-run science is distrusted right now**, with some reason. The Minor Planet Center, the clearing house for asteroid observations, warned in October against submitting automated results "without understanding or verifying them".
- **No expert may agree to read it.** Section 6 asks what should happen then.

## 4. Implementation plan

- **Home.** This repository, private until R1 passes.
- **Language.** Python through uv, because the orbit fitter and every astronomy library are Python.
- **Two jobs.** A weekly unattended refresh on this workstation that pulls only what changed and runs no fits. Fits are run by hand per method release. Nothing with a model in it runs in the weekly loop.

- **Web stack, look, copy, interface and hosting.** See `DESIGN.md`, which overrides anything this plan says about the site.

Appendix B has the build notes.

## 5. Presentation plan

Written before `DESIGN.md`, which wins wherever this section differs. The site is white on black, so the ink-on-paper wording below is superseded, and the page table predates the prototype stage in 3.5.

### 5.1 The shape

- **The entry is the unit.** Every reachable asteroid gets the same sheet: reach, tracking, size, spin, surface, sunlight push. A measurement is drawn in solid ink with its source. A limit is hatched. A prior is an outline as wide as the ignorance, holding the measured values of the most similar objects, with a tab saying which observation would fill it and when that is possible.
- **An example entry, 2026 HT.** Reach 4.6 km/s, solid. Tracking 57 days, solid. Size about 25–80 m, outline, from brightness alone. Spin, outline: most objects this bright turn too fast to hold rubble. Surface, outline: the base rate. Sunlight push: this tracking carries no information. Its tab reads "one night's lightcurve, small telescope, around March 2027".
- **Each entry ends in a difficulty ladder.** Can it be found again; can it be reached, and when; is it big enough and slow enough to work on; is it worth anything; could today's technology bring any of it back. Each rung is measured, a prior, or unknown. The last rung is stated plainly: the largest sample ever returned from an asteroid is 121.6 grams, and all three missions together returned about 127.
- **A price, as a range.** Under named scenarios (metal returned to Earth at today's prices; water sold in orbit at a hypothetical price), each entry shows the chance it is worth nothing, then a range. For nearly every asteroid the range is the same and very wide until someone observes it. The inputs sit on the page with their sources.
- **The voice is a report from a distant frontier.** It leads with the difficulty: the error bars, the likely unrecoverability, the limits of today's tools. It is neither a pitch nor a debunking, and it says what would have to change.
- **The front page is one sentence and one picture.** "7,229 asteroids are within reach of a spacecraft. For about 6,800 of them, nothing about what they are made of has been measured." Under it, every object drawn by cost against size, pale where only brightness is known and inked where something is measured. The cheap-and-big corner is almost empty, and the visitor sees that without clicking. Pointing at a dot shows its name and one sentence; clicking opens its entry.
- **Every claim prints what would prove it wrong.** Three claims sit under the picture, each with its evidence and a "wrong if" line: where it can be tested, the orbit says nothing about the rock, and for the smallest it is untested; almost nothing is measured; under 6 km/s almost nothing is known to be workable.
- **A record page.** Frozen predictions on a time axis to 2030, with the observing windows and survey releases that can settle them. Settled ones show the old outline behind the new ink and the word inside or outside. A miss looks the same as a hit.

Elimination thresholds are fixed presets, not sliders, so a visitor cannot loosen a cut until something survives.

### 5.2 Pages

| Page | What it holds | Ships |
|---|---|---|
| Front | The sentence, the picture, three claims, what changed this week, the next dated answer | R1; the orbit claim reads "reproduced on labels already analysed; confirmatory test due" until R2 |
| The guide (the ledger as pages) | One entry per asteroid; lists by cost band; the elimination table per mission type; the untested objects that can be observed | R1; sunlight-push rows show JPL's published values until R3 |
| The record | Predictions, due dates, outcomes; the orbit test and what it could not see | R2; at R1 it lists what will be predicted and when the truth arrives |
| Method and data | The protocol, versions, downloads, sources and licences | R1 |

### 5.3 What changes, and how often

- Day to day, with no rebuild: window tabs read "open now" or "opens in 9 days" from stored dates.
- Week to week: about 12 new entries, nearly blank. An outline turns to ink about once a month. Most weeks the line will read "12 new entries, nothing measured".
- Year to year, once the record is running: one to three named predictions resolve by 2030, the first no earlier than late 2027. The share of blank rows will rise, and that race between discovery and follow-up is shown as a result.

In the prototype a visitor can sort, filter, pick a mission type and open an entry. Figures a reader can manipulate come later, though one could come early (5.4).

### 5.4 The other two designs

- **An explorable article**: one long page that argues the case with six hand-made figures on the real data. It is the most persuasive form and the most craft. I would take two of its figures at R4: one where the reader tries to predict class from orbit and fails, and one where deleting a few nights of tracking erases a measurement. The first needs only the orbit test, so it could ship with R2 if you want something to move sooner.
- **A scoreboard-first site**, organized around dated bets. Its discipline is adopted above. As the whole site it has too little to show before late 2027.

## 6. Decisions

**Settled with Adam on 21 November.**

- *Go, prototype first.* Build something to demonstrate before contacting anyone. No message goes to claudestronomy, observers, licence holders or reviewers until the prototype exists. The pitch then, in his words: "your grant could expand this to XYZ, or improve ABC".
- *Depth stays.* The orbit test, the forecasts and the orbit refits remain on the roadmap after the prototype. The fun and the research depth can coexist.
- *Realism is the stance.* The difficulty, the error bars, the likely unrecoverability, the extreme uncertainty, and the limits of current tools and motivation. A distant frontier, and maybe not an impossible one.
- *Price tags, with error bars.* This reverses the earlier draft, which had no dollar figures. How a dollar line is shown, if at all, is open (`DESIGN.md` section 7).
- *Targets.* "Agreed on targeting, but I also sort of like the open-endedness of it." The "observe next" list stays as one thread among several.
- *Skipped.* The 20 December conference abstract, and the rush to catch 2024 YP9.

**Proposed, not yet answered.** Non-commercial research framing. Surface work and whole-body capture as the first two mission types. The site's shape is in `DESIGN.md`.

**Open.**

- The web stack. The look and the copy rules are now set in `DESIGN.md`; the app's stack and where its state lives are not.
- A repository name, and whether it stays private until the public launch.
- A role email address (not a personal one) as the contact JPL's interface requires.
- Papers: a site alone, or also a short note that Adam would author.
- If no expert agrees to read the public launch: stay private, or go up marked as not externally read.

**Effort to each point**, in days like 20–21 November, my estimates:

| To reach | Agent work in all |
|---|---|
| Prototype (R0 and the prototype) | 8–14 days |
| Public launch (R1) | 12–20 days |
| Orbit test, forecasts, density ceilings (R2) | 16–27 days |
| Orbit refits and figures a reader can move (R3, R4) | 36–62 days |

The 0.7 GB of data snapshots behind the numbers here is in `data/research-data-2026-11-21.tar.zst`, outside git.

## 7. Not yet verified

- The claim that nobody has published a scored test of this kind rests on searches without a full-text index.
- The orbit test says nothing about the smallest, most Earth-like objects. One faint link did show among larger ones (darker objects come slightly closer to Earth's orbit, about 1%, possibly an artefact of one survey); it did not improve predictions.
- Sizes from brightness are untested fainter than H 25: the measured sample has three objects there.
- The three unread label tables have not been obtained, and their overlap with the labels already analysed is unknown.
- The outside survey that could score class forecasts has reported a 10-object pilot and no 2026 results. No comparable stream exists for spin.
- The two soon-observable targets rest on JPL's peak magnitudes; no detailed position forecast was run.
- The 2.2-hour line and the other mission thresholds are not yet sourced; the supporting literature was recalled by a reviewer, not read.
- Yields are extrapolations from small samples: about a dozen radiation-pressure limits (5 of 16 sampled), about 180 physical statements, 0–2 periods a year under 6 km/s (10 sampled).
- The lunar-origin share (88–97 of 286) uses my approximate formula, and the 30% figure is one paper's upper value.
- The iron-exclusion counts, the "probably 40 m or more" row and the 2001 CQ36 ceiling are reviewers' recomputations; the last uses two size estimates with about 30% errors.
- The counts of known compositions and densities and the SPHEREx figure are first-round, single-agent results.
- The fitter has not been started from scratch without JPL's orbit, and the second fitting program has not been retested.
- The 2015 BM510 flyby is uncertain (a degraded engine), and the Tianwen-2 return date has only secondary sources.
- That only the fitting worker must be GPL is a reviewer's reading, not legal advice.
- Whether claudestronomy funds this kind of work.
- The price figures come from a model with three placeholder inputs, and the checkers list corrections to make before anything is displayed (`docs/research/verify-value-inputs.md`, `docs/research/verify-capability.md`).
- The effort figures are my estimates.
- Three of the recovered first-round reports are incomplete after the machine rebooted mid-research (`nongrav.md` most of all); the agents' structured summaries are complete.

## Appendix A. Validation protocol

Written for the expert reader and the deposit. Numbers are proposals to fix before any confirmatory run. Terms not in the main glossary: *bit*, the score unit for a probability forecast (one bit is one yes-or-no question answered); *au*, the Earth–Sun distance; *force law*, the assumed way a push weakens with distance from the Sun; *null objects*, asteroids too big to show either push; *anomaly flag*, a drift too large to be thermal.

**Three sets of known answers.**

- *Exhibit set*: the dozen known compositions and about 18 direct densities. The ledger must reproduce their published values. The ledger's withheld-truth predictions are shown beside each truth. It is not a pass bar: twelve objects cannot pass or fail a ledger whose strongest class claim is about 55%.
- *Development labels*: about 2,700 classes and 3,100 reflectivities, already analysed on 21 November.
- *Confirmatory labels*: three 2024–2026 surveys of small asteroids (84, 122 and 189 objects before overlaps), less any object already among the development labels and, for each predictor, less any object it was built from, plus anything published after the freeze. The list of designations is fixed and hashed in R1, before the ledger ingests any class. Until the R2 run those objects' classes stay out of the priors and show on the site as "measured, held for the test". If fewer than about 150 unseen objects remain, R2 publishes the reproduction only and the confirmatory test waits for new labels.

**The deposit** (Zenodo or OSF, for an outside date) fixes: the class scheme and label mapping; one primary endpoint and its baseline; split rules and seeds; the interval method; every number below; the list of predictors; the rule for choosing null objects; the density-ceiling factor, the density values that define "solid iron" and "metal-rich", and the reflectivity assumed for brightness-based sizes; a rule for tumbling objects; the fit protocol; the forecast fields; the commit of the scoring script; hashes of the input snapshots. Later changes are numbered amendments, deposited the same way.

| Channel | Bar |
|---|---|
| Class predictors | Mean log-score gain in bits per object over the class frequency, four classes, objects below 2 au, interval by bootstrap within label source. The verdict is given once, on all confirmatory objects: "works" if the whole 95% interval is above 0.05 bits; "no usable information" if the whole interval is below; otherwise "unresolved", with the number of objects that would resolve it. The same figure is printed for three H bands, which decide nothing. A known real effect is run as a positive control. |
| Size from H | Objects with an independent size are split in half by a hash. On the held-out half the stated 68% and 95% ranges contain the measured size at binomially consistent rates (for the 88 objects at H 22 and fainter together: 51–68 inside the 68% range and at least 79 inside the 95% range). These sizes have been looked at, so this is a check, not a blind test. At H 25 and fainter there are 20 such objects, enough to catch only a gross failure. |
| Spin from H | One probability per H band for: under 10 minutes; under 1 hour; under 2.2 hours; 2.2 hours or more; observed for an hour with no period found. Log score on periods published after the freeze, against a flat rate and against Prospector's prior. |
| Orbit fits | JPL's 573 drift values and 11 positive radiation-pressure values at 3 sigma or better are split in half by a hash and settings tuned on one half only. On the other, under JPL's force law for each object: median difference at most 0.5 combined sigma; at least 95% within 2; every object beyond 3 explained or counted as a failure. ESA's values compared where both publish. |
| Detections | One model per object by a written rule; drift and radiation pressure fitted jointly. The threshold is set so the expected number of false detections over every object and term fitted in the release is at most one (about 4.0 sigma if all 7,229 objects are fitted for two terms). The false-alarm rate at that threshold is measured on at least 300 null objects that resemble the targets and reported with its 95% upper limit. The release prints "N new detections, about F expected false, at most U"; if U is more than half of N they are published as candidates. Each detection survives removal of any one night and any one station, and is confirmed by the second fitting program. |
| Upper limits | Under injected signals and truncated tracking, the stated 95% limit holds in at least 90% of trials for at least 9 objects in 10. |
| Density ceiling | The model factor is fixed in the deposit (1.5 with a measured size, 1.8 from brightness) and counts are printed for 1.3, 1.5 and 2.0. "Excluded" is stated only at the drift minus 2 sigma and only without an anomaly flag. The eleven objects with independent densities are a consistency check, already run with none above the ceiling. Validity below 300 m is assumed, and every output says so. |
| Forecasts | Each has: the quantity and its outcomes; a probability per outcome or a full distribution, never a range; what resolves it; the version scored, which is the last one whose inputs predate the resolving observation; the scoring rule and reference forecast; a void date. |

## Appendix B. Build notes

- **Start with a fixture slice.** About ten objects, each a distinct failure mode: 2011 AA37 (unreliable period, window open now), 2009 BD (joint fit; the only cheap object with both a fitted push and a size, and that size has two competing solutions), 2022 OB5 (period missing from the databases), 2026 QQ8 (new, unknown to SsODNet, tracking data changing daily), 2020 CD3 (captured by Earth; defeats the fitter), 2010 CW266 (no H, one-day arc), Kamoʻoalewa (name spelled differently per source), Bennu (known answer), 2010 NU71 (known-bad upstream size), 2013 NJ (two sources disagree by a factor of 100 on its period).
- **Network.** One module may open a connection. It enforces each service's limit (JPL allows one request at a time and requires a contact address) and writes every response to the snapshot store. Fits run offline from snapshots.
- **Data.** Outside git, content-addressed, backed up, with only manifests committed. Snapshots are under 1 GB; the fitter's files are about 5 GB.
- **Identity.** The internal key is JPL's permanent id. An alias table holds every designation. Joins never use names. Page addresses derive from the key, and a renamed object gets a redirect.
- **Ledger cells.** Each (object, property, source) is measured, looked for and absent, or not checked. A source outage is the third state, never "nothing measured".
- **Licences.** Any value from any source may appear on the site and in its data files. Every source is cited once, with the citation it asks for, on the method page. The project's own products (priors, fits, limits, rankings, forecasts) are CC BY. A data deposit with a DOI is a separate decision, not yet made. The first release uses no Gaia data.
- **Fitter.** GRSS is GPL-3.0. It runs behind a subprocess boundary, so only that worker need be GPL. A second fitting program (layup) is added at R3 for cross-checks behind the same boundary; it was tried on four objects in the first research round and not since.
- **Fit protocol.** Fit position-and-velocity states, not orbital elements (this fixed every short-arc failure in trials). Fit both pushes jointly. Start from the fitter's own error bars; never rescale them from fit residuals or by one global factor; adjust them per object only from that object's own injection tests, and record both. Record the force law with every value. Treat Earth-captured objects as a declared exception.
- **Site build.** Superseded by `DESIGN.md` sections 6 and 8: the site is likely not static, and its stack and host are open. Kept from this note: no probability is computed in the browser; any bulk download carries a schema and manifest and only values that may be redistributed; a DOI per method release and per frozen forecast.
- **Release guard.** Staging first, then promote. Hold a release if object counts, measured values or null rates move outside tolerances. Show each source's date on every page, with a banner when data are more than ten days old.
- **Rules for coding agents**, in the repository: never edit the protocol or a threshold to pass a gate; no network outside the one module; never fit against a live service; every number in a public claim traces to a script output.
- **Effort notes.** R1 is the largest integration job: about ten source adapters, several with no stable machine route. A full first pull takes 6–12 hours at polite rates and later pulls are incremental. Computing is not a constraint; the whole dynamics run with its tests is tens of core-hours. About 420 of JPL's detections and the null sample lie outside the reachable list; they are fitted for validation only, and their data pull is part of R3.
- **Watch list.** The Minor Planet Center changes its submission format on 30 December 2026; the fitter has frequent releases, so it is pinned and upgraded only against the full fixture set.

The full reviewer notes, including a suggested repository layout, are in `docs/research/summaries-review.md` and `docs/research/summaries-recheck.md`.

## Appendix C. Work-package detail

**WP1. The ledger.** SsODNet already merges most of the literature. This adds the Spitzer sizes it lacks, JPL's fitted drift and radiation-pressure values, the union of rotation-period sources with their quality grades, and explicit entries where nothing is measured. Where nothing is measured the entry carries priors drawn from one joint model. Reflectivity is the shared unknown: it sets size from H, it is tied to class, and the density ceiling scales with size. So the model draws all of them together and never multiplies separate probabilities. Every base rate is stated for objects of a given brightness, not a given size.

**WP2. Elimination and "observe next".** Each mission type is a set of requirements on size, spin and orbit quality, with thresholds taken from cited sources. The spin requirement is set per mission type: a density-dependent line for surface work, none for capture or a flyby. Each mission type must pass the targets companies have publicly named for it, or the page explains each miss. The table sorts on the probability of meeting every requirement and carries a mass range in tonnes, a launch-year filter, and a label: measured, inferred from this object's data, or population prior. "Observe next" ranks the untested objects by how much one lightcurve or one colour would change that probability, joined to when the object can next be pointed at.

**WP3. The orbit test.** The reproduction runs on the labels already analysed. The confirmatory run uses the sealed labels described in Appendix A. Origin (main belt, Moon, rocket stage) for the most Earth-like orbits is an open question, not a test: only two or three objects have a known origin. The ledger flags the slow-approach objects, carries a wide prior, and records what would tell the cases apart (mass per unit area for a rocket stage, colours for lunar rock).

**WP4. Forecasts and density ceilings.** Forecasts are registered as rules ("any reachable asteroid of H 26–28 that gets a class: …"), so they cover objects not yet discovered.

- The stream that can show whether class probabilities are right on average: a funded survey aiming at colours for about 1,000 small new asteroids by end of 2027, roughly 100 reachable ones a year if it delivers.
- One real disagreement to settle: observed samples put the stony share of small asteroids between about a third and 66%, and one bias-corrected estimate is 23%. Two rival tables, both stated for a given brightness, get registered and the stream decides.
- Named cases: Apophis's density (2029, the only firm one); Kamoʻoalewa's density, if China's Tianwen-2 mission, now at that 18 m asteroid, publishes a mass; the size of 2015 BM510, if Hayabusa2's April 2028 flyby succeeds. These can show whether stated ranges held. They are too few to show whether the probabilities are right on average.
- Density ceilings from JPL's 154 published drifts ship here, under the rule fixed in the deposit.

**WP5. The dynamics catalogue.** The open-source GRSS fitter matched JPL's values on eight trial objects, starting from JPL's own orbits, so that shows the tool works, not that it is independent.

- First reproduce JPL's published detections on a held-out half.
- Then give each reachable asteroid a value, an upper limit, or "this tracking carries no information". About 83% of the list was tracked for under 90 days. On the trial sample the share yielding any physical statement is nearer 2–3%.
- Publish the upper limits. At least five groups have run such fits over large samples, three of them over every known object, and none published a full table of limits.
- Say what each limit means. A drift limit makes no density statement by itself. A radiation-pressure limit gives a floor on density times diameter.
- Refit every claimed new detection with the second fitting program. If it cannot be made to run, new detections are published as candidates only.
- Worked cases, each a test that may fail: 2022 OB5 (a large drift found by both JPL and ESA on a 92-second rotator, cause unresolved); 1998 KY26 (two published values that disagree); 2022 RD2 (a possible new detection resting on one observation); and two where the method should work, 2020 GE and 2001 CQ36.

**WP6. New observations.** Early and cheap: one message each to the groups that take lightcurves of small asteroids, asking whether they would use the ranking, and one request for discretionary time at Las Cumbres Observatory, which is free and open to anyone, for the objects with windows in the next six months. Paid time and a daily list of new discoveries come later, and only with a partner.

## Evidence index

All in `docs/research/`:

- `summaries-round1.md`, `summaries-verification.md`, `summaries-review.md`, `summaries-recheck.md`: each agent's structured findings, with sources.
- Research, 20 November: `nongrav.md`, `source-prior.md`, `catalogs.md`, `new-surveys.md`, `industry.md`, `ground-truth.md`, `orbit-tooling.md`, `presentation.md`, `novelty.md`.
- Verification, 21 November: `verify-prior-null.md`, `verify-nongrav.md`, `verify-fit-repro.md`, `verify-coverage.md`, `verify-facts-missions.md`, `verify-facts-venues.md`, `verify-novelty.md`, `verify-obs-window.md`.
- Price and capability inputs, 21 November: `value-inputs.md`, `capability.md`, `verify-value-inputs.md`, `verify-capability.md`; summary in `summaries-realism.md`.
- `scripts/`: the analysis scripts that survived or were written after the reboot. The full set, with the data they read, is in the data archive.

The elimination table, the size conversions in Terms and the lunar-origin count were computed for this draft from the 21 November JPL snapshots and are not in those files.
