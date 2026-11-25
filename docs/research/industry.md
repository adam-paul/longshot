# Industry, economics and missions: what asteroid-mining practitioners need from a prospect catalog

Research date: 2026-11-20. Scope: knowledge needs, "value", existing ranking tools, company status, ground-truth missions, users.

Status tags used below:
- **[V]** verified today: I read the source (paper text, agency page, company page, or a public API) in this session.
- **[S]** seen today only in search-result summaries; primary page not read.
- **[R]** recalled from memory, not checked.
- **[U]** uncertain or could not be verified.

Numbers computed by me from a public API are marked "(my calculation)".

---

## 0. Bottom line

1. **Better remote characterization is not the binding constraint on the industry today.** The binding constraints are capital, spacecraft reliability, launch and vendor schedules, and the absence of a customer. For both active US companies, logistics decided the first target among candidates that passed a loose composition screen, or none: AstroForge required "not an S-type", then chose 2022 OB5 because it would be within 2 million km of Earth at flyby and rejected a target "with a higher chance of being metallic" [V]; Karman+ switched its first mission to Apophis, an S-type it calls "a dry ball of dirt", because a propulsion vendor slipped and Apophis topped its leaderboard for the new mid-2028 launch date [V].
2. **It is a real second-order bottleneck, for specific people.** Karman+ says rotation rate "is one of the bigger unknowns for any asteroid we target", with data for only "~10-15%" of the population [V]. AstroForge's CEO said of his own target "I would like more information on the asteroid" [V]. Elvis & Esty (2014) put a number on it: the count of assay probes needed scales as 1/P_rich, 22 probes at P_rich = 0.1 for 90% confidence, 4 at P_rich = 0.5 [V].
3. **A miner has already open-sourced most of the "fuse sparse existing data" pipeline.** Karman+ released *Prospector* (Apache-2.0, September 2026): it pulls SsODNet, Lowell astorb, Pravec's Ondřejov period table and MANOS spectra, and assigns each target a letter tier S/A/B/C/D from taxonomy, albedo, spin and cohesion [V]. What it does not do: probabilities, priors for uncharacterized objects ("Unknowns never promote"; an unmeasured body lands in tier C), density from non-gravitational accelerations, or validation of the tier against known answers. Karman+ also says the repository ships "a solver ladder and no calibrated inputs" [V]. That is the gap.
4. **The cautionary case already exists and is public.** AstroForge described 2022 OB5 as "up to 100 meters across" [V]. JPL lists H = 28.99, which NHATS converts to 2.8 to 12 m [V]. In January 2026 the 10.4-m GTC measured a rotation period of 1.542 minutes and an X-complex colour; the paper is titled "Accessible does not mean exploitable" [V].
5. **Value cannot be expressed in dollars per object and should not be.** The defensible forms are: a resource-confidence class borrowed from mining (Inferred / Indicated / Measured), physical quantities with distributions, Elvis's P_ore decomposition, and "probes saved". PGM grade cannot be estimated remotely at all: "there is no known way to remotely identify where an asteroid falls along the wide distributions of PGM grades" (Cannon, Gialich & Acain 2023; two of the three authors are AstroForge's founders) [V].

---

## a) Knowledge needs

### ASIME 2016 (Graps + 30 co-authors, arXiv:1612.00709, 81 pages) [V]

Questions came from Planetary Resources, Deep Space Industries and TransAstra. There are 30 miner questions in five groups plus 5 questions the scientists asked back.

The ones that bear on a remote prospect catalog (question numbers as in the paper):

- Q1. What asteroid properties do miners need to know, and what do we know? Galache's list, in his order: (1) size, (2) composition, (3) mass/density, (4) spin, (5) interior structure, (6) surface structure, (7) accurate orbit. Green separated "knowledge to get there" from "knowledge for mining" and stated "Delta-V is dominant factor for (current) low cost space missions".
- Q2. How can the rate of spectral characterisation be increased? "It lags far behind discovery rate, especially at smaller sizes (D < 300m)."
- Q3. How can we assess the number of NEOs of a given spectral type and size? Answer: do not rely on spectra; use survey colours and albedos as proxies. "There's a one-to-one correspondence between primitive ... composition and low albedo (geometric albedo < ~7.5%)", but low albedo does not guarantee hydration (Allende, Almahata Sitta).
- Q4. How many NEOs must be visited to test orbital distribution models? Green: "None." It should be done from the ground with spectral types and a known selection function.
- Q5, Q6. Does shape, or orbit, tell you composition? Shape: no. Orbit: only statistically, through source region; "it's impossible to assess the composition based solely on the orbit", because the dynamics are chaotic and types are more mixed at small sizes.
- Q7. What can be learned from Earth about internal structure (rubble pile versus monolith)?
- Q8. Which high-value telescopic studies are not being done for lack of funding?
- Q12, Q14, Q19, Q20. How to use the 3.1 µm band as a hydration indicator; conditions for free ice; surface signatures of subsurface water; how desiccated carbonaceous NEOs are as a function of their main-belt-to-NEO history.
- Q17, Q18. How well meteorites represent NEOs above 10 m; how well space weathering is understood.
- Q25. Is there a cohesion threshold below which a rubble pile is too risky to work on?
- Q32 (scientists to miners): what can be observed from the ground to avoid going to a useless target? Answers: thermal inertia is "an impossible task" for small bodies with current telescopes (Green, Rivkin); lightcurves are feasible, so "we would know what fast spinning bodies are not useful"; the 0.7 µm band is "a better bet and easier to observe" than 3.1 µm (Rivkin); Daniel Faber (DSI) wanted "the material that has the highest concentration of volatiles, specifically water".

The six Science Knowledge Gaps (SKGs) that came out of it:

1. Map meteorite classes to asteroid classes, especially for C-types.
2. Dedicated NEA discovery and follow-up: a 2 to 3 m telescope reaching V ~ 21 on short notice, because an NEA is best observed at discovery.
3. Granular dynamics in low gravity.
4. "A map of low delta-v, low synodic period and low-albedo NEOs as a first-cut."
5. "Determine if a NEO's dynamically predicted source regions is consistent with its actual physical characterizations", as a short-cut for small NEOs that cannot be measured spectroscopically.
6. Regolith particle size data, including with depth.

SKG 4 and SKG 5 are the project's channels (2) and (3), stated by the community ten years ago. The paper also noted: "The community does not yet have an asteroids physical properties database."

### ASIME 2018 (Graps + 43 co-authors, arXiv:1904.11831, 65 pages) [V]

Theme: composition. Questions came from Aten Engineering, Planetary Resources and DSI: 21 questions lettered a to u in four groups (potential targets; asteroid-meteorite links; in-situ measurements; laboratory measurements). Several revisit 2016. New ones include:

- (e) Can colour photometry give taxonomy comparable to 0.4 to 4.0 µm spectroscopy?
- (h, i, s) State of the art in matching (weathered) meteorite spectra to asteroid spectra, and software to do it.
- (k) "What is the current confidence that spectral class informs bulk composition?" Patrick Michel: "I don't think the current confidence is high." S-type/ordinary chondrite is verified (Itokawa); C-types were waiting on Ryugu and Bennu.
- (n) What must a probe carry to establish "with 100% confidence" that water is present, and how much?

The recorded mission-design discussion is the most candid part [V]:

- Green: "The DISCOVERY is the most important." Abell: "The number one, foundational here is the Discovery. Which needs a survey for low-delta-v objects."
- Bonin (DSI): "having a priori immaculate knowledge is going to take too long ... We want to go directly to Test missions ... expecting a high failure rate."
- Sercel (TransAstra): "The appropriate paradigm for asteroid mining is FISHING, not prospecting. Therefore you go from Discovery to follow up observations, and then directly to a full-scale mining mission."
- Michel: "30m size is borderline.. asteroid could be a really fast spinner."
- Bonin and Galache both said characterization data from missions is commercially valuable and would not be given away.

### Lewicki, Graps, Elvis, Metzger & Rivkin 2021 (decadal white paper, arXiv:2103.02435) [V]

- Frames the need in mining-industry terms: resources are classed Inferred, Indicated, Measured; feasibility goes Order of Magnitude, Preliminary, Detailed. "Asteroid resources are mostly in the Order of Magnitude stage."
- "Only a few percent of NEOs are anticipated to be rich in the hydrated minerals", citing Rivkin & DeMeo.
- "The need to find a few good asteroids means using in situ measurements of tens of candidates."
- Recommended activity [1]: "Enhanced access to asteroid data. Collating all existing and future data on asteroids, especially NEOs, into easily accessible public databases could speed up resource assessment", with interoperable APIs.
- "The near-term hurdles are mostly financial."

### The quantitative literature

| Paper | What it did | Numbers to carry | Status |
|---|---|---|---|
| Sonter 1997 (Acta Astronautica; thesis and IAF version hosted by NSS) | Linked delta-v, rocket equation and mining plant mass to an economic test. | "Approximately 10% of NEAs are more accessible than the Moon"; targets with outbound delta-v under 6 km/s and return departure under 2 km/s; "long synodic periods militate against multiple-return mining missions"; "the Expectation (probabilistic) value of the Net Present Value is a crucial unifying concept". | [V] abstract on nss.org |
| Sanchez & McInnes 2011 (J. Spacecraft & Rockets 48, 153) | Statistical map of NEA mass reachable below a transfer-energy threshold. | No per-object output. "Objects with a diameter of order tens of meters to a few hundred meters ... could potentially be the first targets"; exploitable mass is dominated by the few largest reachable objects. | [V] |
| Elvis 2014 (Planet. Space Sci.; arXiv:1312.4450) | N_ore = P_ore × N(>M_min), with P_ore = P_type × P_rich × P_acc × P_eng. | PGMs: P_type 4%, P_rich 50%, P_acc 2.5% at delta-v ≤ 4.5 km/s, so P_ore = 5×10⁻⁴; D_min 100 m; about 10 ore-bearing NEOs. Water: P_type 0.1, P_rich 25% (at ~20 wt%), P_acc 3%, P_ore ≈ 8×10⁻⁴; D_min 18 m; ~9,000 among 10 million; 18 above 100 m. | [V] |
| Elvis & Esty 2014 (Acta Astronautica; arXiv:1312.4452) | How many assay probes to find one ore body. | P_rich = 0.1: 22 probes for 90% confidence, 44 for 99%. P_rich = 0.5: 4 probes. Concludes that better pre-probe characterization is the cost-effective step. | [V] |
| Andrews et al. 2015 (Acta Astronautica 108, 106) | NPV analysis of one specific mining architecture. | Figure of merit: NPV. | [V] via Hein's description only |
| Calla, Fries & Welch 2018 (arXiv:1808.05099) | Water mining with <500 kg spacecraft, 100 kg water per trip. | $113.6M per unit; break-even needs more than 100 spacecraft operating over 5 years. | [V] abstract |
| Jedicke et al. 2018 (Planet. Space Sci. 159, 28) | Number of water-bearing NEOs versus return-trip delta-v to lunar DRO. | "Likely thousands of H₂O-rich NEOs larger than about 5 m" with return-trip delta-v ≲ 3 km/s; count rises steeply with delta-v; these objects are on Earth-like orbits and are hard to detect (inside Earth's orbit or long synodic periods). | [V] abstract paraphrase |
| Rivkin & DeMeo 2019 (JGR Planets; arXiv:1812.02285) | Hydrated NEO count using Ch class as proxy. | 700 ± 350 hydrated objects meeting the accessibility criterion with no size floor; 26 to 80 larger than 1 km. | [S] |
| Hein, Matheson & Fries 2020 (Acta Astronautica 168, 104; arXiv:1810.03836) | Profit model with reuse, learning curves, multiple spacecraft; platinum supply-demand model. | Drivers: throughput rate (kg/s per kg of spacecraft), number of spacecraft per mission, mission cadence. "Platinum mining requires very high throughput rates"; water to cislunar space "seems to be economically viable". Platinum anchor point: $40,449/kg and 254,582 kg/yr. Water price assumed $20,000/kg, water fraction 0.05. | [V] |
| Colvin, Crane & Lal 2020 (Acta Astronautica 176, 298) | Economics of asteroid water as propellant, 2030 to 2050. | Water is "the only asteroid-derived resource that may become economical"; demand 6,000 to 10,000 t over 20 years, about $15B; delivered to LEO at $2,000 to 3,000/kg, comparable to Falcon Heavy. | [S] |
| Cannon, Gialich & Acain 2023 (Planet. Space Sci. 225, 105608) | Meteorite grades of 83 elements against terrestrial ore. | See section b. | [V] |
| Alarcón et al. 2026 (Icarus 117153; arXiv:2605.04784) | First photometric characterization of the first commercial prospecting target. | See section d. Fast rotators are "≳94% of objects with H>26"; "rotation period measurement is therefore an indispensable prerequisite". | [V] |

Other 2023 to 2026 target-selection work found [S]: a fuzzy multi-criteria framework for boulder-capture targets (Aerospace 2025, doi:10.3390/aerospace12090800); target selection for in-orbit sample collection (Acta Astronautica 2023); Trigo-Rodríguez et al. (arXiv:2510.27373, MNRAS accepted) on metals and rare earths in carbonaceous chondrites [V, abstract]. None produces a probabilistic per-object catalog.

### Which properties matter, in what order

This is my synthesis from ASIME, Karman+'s published criteria, Alarcón 2026 and NHATS data. It is a gate sequence, not a weighting.

1. **A usable orbit.** If the object cannot be found again, nothing else matters. Of 7,226 NHATS objects today, 5,046 (69.8%) have orbit condition code 6 or worse and only 984 (13.6%) have 0 to 2. Among the 286 with minimum round-trip delta-v ≤ 5 km/s, 74 have OCC ≥ 6 and 57 have OCC ≤ 2 (my calculation from the NHATS API) [V].
2. **Reachability in the available launch window.** Outbound and return delta-v, time of flight, window frequency (synodic period), and distance from Earth at encounter for communications. This is what actually decided both AstroForge's and Karman+'s first targets. Sercel: "inclinations more than a couple of degrees are really problematic" [V].
3. **Size**, because it sets the business case and the mission type. Elvis: 100 m minimum for PGMs, 18 m for water. Karman+ wanted a rubble pile "with a diameter measured in hundreds of meters" [V]. TransAstra wants about 100 t, a few metres across, to enclose whole in a 10-m bag [S for the mass, V for the bag]. The 286 lowest-delta-v NHATS objects have median H = 27.7; only 2 could exceed 100 m even at the dark end of the albedo range, and none is certainly above 30 m (my calculation) [V].
4. **Spin state.** Period and tumbling gate any surface operation. Karman+ ranks "slow rotation, and not tumbling" under ease of excavation and uses the 2.2 h spin barrier [V]. Alarcón uses P > 1 h as the criterion and finds 2022 OB5 fails it "by more than two orders of magnitude" [V].
5. **Composition class and hydration state.** C/B/D complex or albedo ≤ 0.1 for water; X/M for metal; plus thermal history (minimum past perihelion) for dehydration. This is where the catalog's novel channels apply.
6. **Structure**: rubble pile versus monolith, regolith presence, cohesion. Mostly not knowable remotely except through spin limits.
7. **Binarity.** Complicates proximity operations but yields a mass. Minor for target choice.
8. **Grade**: water wt%, PGM ppm. Not knowable remotely. Needs in-situ assay.

---

## b) Value

### Why price-times-mass fails

- Asterank's own About page: value is "based on the mass of a given asteroid and its spectral type", mining cost is a flat percentage of value, and "the overwhelming majority of asteroids have no spectral classification" [V]. Mass comes from an assumed diameter and density; composition from a class-to-meteorite lookup; price from today's exchange.
- Hein et al.: with realistic price elasticity, a platinum venture "would only be economically feasible when the quantity of platinum from space would substitute an equal quantity of terrestrial platinum" [V].
- A 2026 preprint (Nachtrieb & Smith, arXiv:2607.06806, "Will AstroForge Collapse the PGM Market?") argues price falls toward the cost of asteroid mining only after supply has moved off-world [V, abstract]. The dispute itself shows the dollar figure is a scenario, not a property of the object.

### Best published concentrations

**PGMs in iron meteorites** (Cannon et al. 2023, Table 2, total of six PGMs, 100% metal) [V]:

| Percentile | Iron meteorites, ppm | Terrestrial deposits, ppm |
|---|---|---|
| 10th | 14.70 | 1.07 |
| 50th | 40.78 | 3.86 |
| 90th | 107.86 | 7.36 |

- Highest expected value is about 230 ppm (IIAB Avce). Kargel's (1994) method, which scaled from Ir at chondritic ratios, gave "over 300 ppm total PGM which are no longer supported".
- Elvis's "up to 100 ppm Ir" is called a misreading of Kargel; the richest irons have about 50 to 60 ppm Ir.
- These are upper values: "a spacecraft sent to an X-Complex asteroid is likely to encounter an unknown proportion of metals and silicates"; "the pure metallic asteroid is now seen as an extreme endmember that may not exist in practice".
- Use the 50th percentile, not the 90th, as the expectation.

**Ordinary chondrites.** Kargel 1994 (JGR 99, 21129): LL chondrites contain 1.2 to 5.3% Fe-Ni metal carrying 50 to 220 ppm precious metals [S]. That is about 0.6 to 12 ppm in bulk rock (my calculation), so the metal must be separated to beat terrestrial ore. H chondrites carry roughly 15 to 19 wt% metal [R].

**Water.**

| Material | Value | Source | Status |
|---|---|---|---|
| Ivuna (CI) | 12.73 ± 0.63 wt% total H₂O, of which 6.58 interlayer and 6.15 structural | Yokoyama et al. 2023, Science | [V] |
| Ryugu sample | 6.84 ± 0.34 wt% total H₂O (0.30 interlayer, 6.54 structural); total H 0.94 ± 0.05 wt% | same | [V] |
| Bennu sample | 0.84 to 0.95 wt% H; 4.5 to 4.7 wt% C | Lauretta et al. 2024 | [V] |
| Bennu, H₂O-equivalent | at most about 7.5 to 8.5 wt% if all H were water; less, since part is organic | my calculation (×8.94) | |
| CM chondrites, whole rock | 1.9 to 10.5 wt% indigenous water, mean 7.0 | Lee et al. 2023 | [S] |
| CI mass loss to 1000 °C | 28.5 to 31.8 wt%, includes non-water volatiles | King et al. 2015 | [S] |
| C-complex asteroids, remote | about 4.5 ± 4 wt% | Beck et al. 2021 | [S] |

The two returned samples sit near 7 wt%, a third of the 20 wt% Elvis assumed for "rich" bodies, and Ryugu lost almost all interlayer water in space. A catalog should use about 5 to 8 wt% as the central value for a hydrated carbonaceous NEA and treat 10 wt% or more as the optimistic tail.

### Which market comes first

- Published techno-economics converge on in-space water before Earth-return PGMs (Hein 2020; Colvin 2020; Sonter 1997) [V/S].
- Industry is split. AstroForge: PGMs to Earth. Karman+: water, with itself as first customer for GEO satellite life extension. TransAstra: bulk capture for propellant and materials. [V]
- The only public price points are ULA's from about 2016: $3,000/kg in LEO, $1,000/kg at L1, $500/kg on the lunar surface [S]. No current buyer has restated them.
- The Moon competes. Metzger (2023, arXiv:2303.09011) argues lunar propellant can beat Earth launch [S]. Sanchez & McInnes note asteroids give access "at an incremental level of energy" while the Moon always costs its escape velocity [V].
- SpaceX's May 2026 S-1 lists a plan to "pursue asteroid mining operations to extract metals and other critical resources from near-Earth and main-belt asteroids" and says such markets "do not currently exist" [V via press report; S-1 itself not read].
- NASA's SBAG reported in March 2020 that for its goals document an "ISRU section was planned, but interest dwindled from community" [V].

### Figures of merit used in architecture studies

- Expected net present value (Sonter; Andrews).
- Mass payback ratio, mass returned per mass launched (Lewis, O'Leary; cited by Hein) [V].
- Break-even time and profit per kg of spacecraft, driven by throughput rate (Hein; Calla).
- Number of ore bodies N_ore and number of assay probes N_assay (Elvis; Elvis & Esty).
- Count of water-bearing objects below a return-trip delta-v (Jedicke).
- Delivered cost per kg against Earth launch (Colvin); "gear ratio on cost" G and production mass ratio φ (Metzger).

### Recommended per-object "value" block, with no dollars

1. **Resource-confidence class**: Inferred / Indicated / Measured, with nearly everything Inferred or lower. Show which observation would promote it.
2. **Physical endowment as distributions**: mass (from size and density posteriors); recoverable water in tonnes = mass × P(hydrated) × water fraction × extraction efficiency; Fe-Ni metal in tonnes; PGM in kg using the Cannon grade distribution, flagged as not remotely constrainable.
3. **Elvis factors** per object: P_type, P_rich, P_acc, P_eng, with intervals, and their product.
4. **Probes saved**: N_assay for a candidate list drawn from the catalog versus a blind list.
5. **Delivered-mass ratio** to one stated reference destination (for example lunar DRO), from return delta-v.
6. Optionally a propellant-equivalent range at $500 to $3,000/kg, labelled as a scenario from a 2016 statement.

---

## c) Existing ranking tools

| Tool | Method | Flaw for this purpose | Status |
|---|---|---|---|
| **Asterank** (Ian Webster; bought by Planetary Resources May 2013) | Value = mass × composition inferred from spectral class × market price; accessibility from delta-v (Benner) and orbit shape; profit with mining cost as a flat percentage. | No uncertainty. Most objects have no spectral class. Ignores market response, extraction, spin, size error. Source of the "trillions" headlines. | [V] |
| **JPL NHATS** | Daily round-trip trajectory search over all NEAs; limits delta-v ≤ 12 km/s, duration ≤ 450 d, stay ≥ 8 d [R, consistent with API output]. Gives H, size range from H, OCC, next optical and radar windows. | Accessibility only. Size is a factor-of-four range from assumed albedo. No composition, spin or density. 7,226 objects today, 286 at ≤ 5 km/s. | [V] API |
| **NEOfixer** (Catalina Sky Survey, public since March 2022) | Scores every NEO and NEOCP object per observer by Importance × Benefit, Cost and Urgency for astrometric follow-up. | Planetary-defence astrometry. No resource or characterization term. | [S] |
| **ESA NEOCC Priority List** | CAT index from MOID, sky uncertainty and recovery difficulty; classes Urgent to Low. | Same scope. Being phased out; ESA points users to NEOfixer. | [S] |
| **MANOS** (Lowell; Moskovitz, Thirouin, Devogele) | Lightcurves and spectra of low-delta-v sub-km NEOs. 228 lightcurves in the 4-year paper; 189 NEOs with griz colours in a 2026 paper (arXiv:2603.15872). Estimated ~1,230 NEOs must be characterized to find 100 viable mission targets. | Observations, not a ranking. This is the main validation set for small accessible NEOs and the main dependency of Karman+'s hydration classifier. | [S]; API seen in Prospector code [V] |
| **Karman+ Asteroid Leaderboard** | "A weighted list of targets we like", several hundred objects: reachability (window flexibility, delta-v, time of flight), ease of excavation (size, slow rotation, not tumbling), attractiveness (repeat visits, spectral profile). | Private. Weights unpublished. | [V] |
| **Karman+ Prospector** (github.com/Karmanplus/prospector, Apache-2.0, created 2026-08-27, 12 stars) | Delta-v screen, then "enrichment": merges SsODNet, astorb, Ondřejov, MANOS; diameter from H and class-median albedo (default 0.15); expected minimum past perihelion from Toliou, Granvik & Tsirvoulis 2021; P(period > critical period) from a Johnson S_B fit to periods of similar-H bodies; cohesion; letter tier. | Deterministic. Unknown stays unknown. M-types demoted one tier. No orbit-to-source-region composition prior, no density from Yarkovsky, no calibration test. Ships no data or output list. | [V] code read |
| **AstroForge** | "About 28 candidate asteroids" thought to be metallic; chooses near launch. Based on "proprietary observations". | Private; first public target had its size overstated by about tenfold. | [V] |
| **TransAstra** | About 250 known small NEAs as potential capture targets, expects ~260 more of ≤ 20 m from Rubin; Sutter telescopes and Theia software for detection. | Private; detection-led. | [V] Gizmodo |
| **Planetary Resources / DSI era** | PR used Asterank publicly and planned Arkyd prospecting telescopes; DSI planned Prospector-1. PR was acquired by ConsenSys, DSI by Bradford Space (2019) [S]. Neither published a target list with uncertainties. | Defunct. | [S]/[R] |
| **SpaceMiningData.com** | Independent directory of missions, organisations and asteroids named in mission records; JSON/CSV under CC BY 4.0; dataset rebuilt 2026-11-20. | A record of who is going where, not a prospect ranking. | [V] |
| CivLabs "Atlas" | Has a per-object page for 2022 OB5. | JavaScript-only; I could not read it. | [U] |

**Is a probabilistic, validated prospect catalog already public? No.** I found none. The nearest things are Prospector (public code, deterministic tiers, no published table), MANOS (public observations) and the statistical population papers (Elvis, Jedicke, Rivkin & DeMeo, Sanchez & McInnes), which give counts, not per-object posteriors.

---

## d) Companies, as of 20 November 2026

### AstroForge (Huntington Beach, CA)

- **Vestri has not launched.** It was renamed DeepSpace-2 in September 2025 [S]. It rides the Falcon 9 carrying Intuitive Machines' IM-3 lander [V]. NASA's Moon Base manager said on 15 September 2026 that IM-3 launches in "the first part of 2027"; IM's CEO said "the first quarter of 2027" [V]. Wikipedia lists NET Q1 2027 [V].
- Spacecraft: 200 kg, Safran Hall-effect propulsion, assembly finished early June 2026, about $10M self-funded, CEO puts success odds at 70 to 80% [V].
- **Target is not fixed.** In June 2026 the company said it has "about 28 candidate asteroids" thought to be metallic and will choose closer to launch; the mission may photograph the asteroid and "attempt to land on it or crash into it" [V]. Whether 2022 OB5 remains the target is unconfirmed [U].
- History: Brokkr-1 (April 2023) failed on communications; Odin launched 26 February 2025 on IM-2, cost $3.5M, lost within days [V]. Funding about $55M including a $40M Series A [V].
- **How they picked 2022 OB5** (SpaceNews, 29 January 2025) [V]: it "could be metallic"; it is "not an S-type"; it would be within 2 million km of Earth at the flyby, allowing higher data rates; another asteroid "with a higher chance of being metallic" was rejected for being farther away. The estimate came from "proprietary observations". Gialich said it is "up to 100 meters across", that the company did not know whether it is M-type, and "a great way to get more information before launch is to announce which one it is". Scientists had objected to the target being secret.
- **What public data say** [V]: JPL SBDB H = 28.99, 49 observations, arc 2022 to 2026, condition code 0, a = 1.03 au, e = 0.055, i = 2.76°. NHATS: size 2.8 to 12 m, minimum round-trip delta-v 3.517 km/s, among the most accessible objects known. No taxonomy in SBDB.
- **Alarcón et al. 2026** (GTC/HiPERCAM, 14 January 2026) [V]: rotation period 1.542 ± 0.001 min; diameter between about 2 m (albedo 0.7) and 15 m (albedo 0.03); Bus-DeMeo Xc, next best Xk; MANOS had reported Xe. E, M and P classes cannot be separated without albedo, so bulk density could be anywhere from about 1,800 to 4,900 kg/m³. Equatorial centrifugal acceleration is about 50 times surface gravity. Surface operations are "highly challenging with current technology, regardless of the compositional interest".
- Their own paper (Cannon, Gialich & Acain 2023) says PGM grade cannot be determined remotely [V].

### Karman+ (Denver, CO)

- $20M seed, 19 February 2025 [V]. Water, not metals; itself as first customer.
- Schedule: 2026, then February 2027 on Transporter-19 [S], then **mid-2028** after the propulsion vendor could not deliver [V].
- **First mission now targets (99942) Apophis** (post of 21 July 2026) [V]. "This first mission is a technology demonstration, not a mining mission." They "would prefer a C-type rubble pile with lots of water". Apophis came top of the leaderboard because its April 2029 Earth approach matches the new launch date.
- Earlier reference targets (2023 payload call): (341843) 2008 EV5, carbonaceous, about 400 m, well characterized; and 2011 AA37, about which "almost nothing is known" [V]. NHATS today: 2008 EV5 minimum delta-v 6.29 km/s; 2011 AA37 5.85 km/s, H = 22.9 [V].
- EPSC 2024 abstract: "few candidates have spectra, and even fewer are confirmed carbonaceous"; unknowns are whether regolith exists on bodies tens of metres across, and tensile strength and density if monolithic; mission cost $20 to 30M [V].
- February 2026 update: rotation rate "is one of the bigger unknowns for any asteroid we target"; only "~10-15%" of the population has rotation data, with an error band "from ~1% all the way up to 100%"; "return missions target slow-rotating, C-type rubble piles that contain water" [V].
- July 2025: "We won't know exact size, rotation, tumbling, surface conditions or exact composition until we get actually there" [V].

### TransAstra (Los Angeles, CA)

- 16 November 2026: finished an 11-day ground test of the 10-m "Mantis" capture bag (inflation, structure, sensor imaging, closure; one of four drawstring gears failed) [V]. A 1-m bag was tested on the ISS in October 2025 [V].
- "New Moon": capture a roughly 100 t, house-sized NEA and move it to a stable orbit; study with UCF, Purdue and JPL due May 2026; first retrieval "as early as 2028" [S, V for the 2028 date]. NASA awarded $2.5M for the bag [V].
- Target pool: about 250 known small NEAs; about 260 more expected from Rubin [V].
- Says nothing public about composition requirements for the first capture. The bag is designed to tolerate tumbling. This is Sercel's "fishing" model.

### Others

- **Asteroid Mining Corporation** (UK): Companies House shows active with overdue filings; a director left in August 2025; an October 2024 MoU with ispace to carry the SCAR-E robot to the Moon. No 2026 news found [S/U].
- **Origin Space** (China): listed as active in directories; NEO-1 (2021) was a debris-capture test and Yangwang-1 a small space telescope. No 2026 news found [S/U].
- **SpaceX**: one sentence of intent in its S-1 [V via press].
- **New entrants**: none with announced asteroid funding found in 2026 [S]. Aureon Space Systems (Japan) is in ESRIC's start-up programme [S]. Starpath and Interlune are lunar.

---

## e) Missions that supply ground truth

| Mission | Target | Status on 2026-11-20 | Use as known answer |
|---|---|---|---|
| **Tianwen-2** (CNSA) | (469219) Kamoʻoalewa | At the asteroid: 20 km on 2 July 2026, announced 6 July. Sampling window July 2026 to April 2027; departure 24 April 2027; capsule 29 November 2027 [V]. No report of a sampling attempt found [U]. | The first rendezvous with a decametre fast rotator. Sample composition in late 2027. |
| | | JWST (Sharkey et al., arXiv:2606.24017, v3 19 Oct 2026): diameter 18 ± 2 m, albedo about 0.59 (0.36 also fits), period 27.9 min, spectrum less red than ground data, resembles enstatite-rich material [V]. First image suggests about 20 m, half the smallest ground estimate [V]. Earlier claims: lunar ejecta; LL-chondrite-like [S]. NHATS still lists 24 to 107 m [V]. | A live example of a 2 to 5 times size error and an unsettled class on a well-observed small NEA. |
| **Hayabusa2#** (JAXA) | (98943) Torifune | Flyby 5 July 2026 at 744 m from centre, 5.3 km/s; contact binary [V]. Pre-flyby: Sq type, 465 ± 15 m, albedo 0.216 [S]. | Shape and class check for a large S-type. No mass. |
| | 1998 KY26 | **Abandoned.** Announced 16 to 19 November 2026 after the last healthy ion engine failed in August [V]. | The planned 2031 rendezvous with an ~11 m, ~5 min rotator is gone. |
| | 2015 BM510 | New target: flyby April 2028 at about 6 km/s, a few hundred metres; 17 to 74 m; period about 49 min; reported D-type [V, AstroArts]. SBDB: H = 25.04, rotation 0.806 h, no taxonomy [V]. | A flyby only, but a small fast rotator. |
| **Hera** (ESA) | Didymos / Dimorphos | Arrived early November 2026; first close view from 60 km published 5 November; at 25 to 30 km from 11 November; Dimorphos images due 25 November; about six months of operations [V]. | Mass and density of both bodies, interior radar: the best density ground truth for a small S-type binary. |
| **OSIRIS-APEX** (NASA) | Apophis | Cruising; rendezvous shortly after the 13 April 2029 flyby; funded for 2026 to 2027, reviewed yearly [S]. | S-type, 340 m. |
| **Ramses** (ESA/JAXA) | Apophis | Approved November 2025; CDR passed February 2026; launch April 2028, arrival February 2029 [S]. | Before-and-after of the Earth encounter. |
| **DESTINY+** (JAXA) | Phaethon; Apophis flyby | Launch Japanese FY2028 on H3 with Ramses; Apophis flyby about February 2029; Phaethon in FY2030 [S]. | B-type active asteroid. |
| **Psyche** (NASA) | (16) Psyche | Mars flyby 15 May 2026; arrival August 2029 [S]. | The test of "M-type means metal". |
| **Lucy** (NASA) | Trojans | Entered the Trojan region October 2026; Eurybates 11 or 12 August 2027 [S]. | Not NEA-relevant. |
| **NEO Surveyor** (NASA) | survey | Launch no earlier than September 2027 [V]. | Thermal diameters and albedos for dark NEOs; the biggest future input. |
| **M-Argo** (ESA) | small fast rotator, to be chosen | Not launched; listings say 2027 [U]. | Unclear. |
| Commercial | DeepSpace-2: NET Q1 2027, target to be chosen. Karman+: mid-2028, Apophis. TransAstra: 2028 or later. | | Data will be proprietary unless released. |

Ground truth for objects of 5 to 30 m, the bulk of the accessible list, will consist of Kamoʻoalewa and little else before 2028.

---

## f) Who would use a public prospect catalog, and in what form

**Users, most likely first**

1. **Observers with telescope time** (MANOS, the IAC group that observed 2022 OB5, IRTF users). They need a ranked answer to "which accessible object should I observe at its next window, and what would it settle?" NHATS already gives the windows.
2. **Small mission teams** choosing among hundreds of candidates: Karman+ (leaderboard), AstroForge (28 candidates), TransAstra (250), M-Argo, university cubesats. Their own tools show what they consume.
3. **Planetary scientists** testing source-region-to-composition links (ASIME SKG 5).
4. **Journalists, investors, policy analysts** who need a check on company claims. The 2022 OB5 size claim could have been checked from H alone.
5. **Agencies.** Interest is weak. NHATS exists for human exploration. SBAG dropped its ISRU section for lack of community interest [V]. NASA's ISRU priorities are lunar and Mars surface [S]. Luxembourg's ESRIC is mostly lunar [S]. I found no agency asking for an asteroid ISRU target list in 2024 to 2026.

**Form**

- **Fields.** Start from Prospector's published enrichment contract, since one company reads exactly these [V]: `input_id` (SBDB primary designation), `taxonomy`, `albedo`, `period_h`, `diameter_m`, `cohesion_pa`, `p_gt_pcrit`, `q_min_au`, `hydration_class`, `tier`. Add: class probabilities (metal-rich, stony, carbonaceous-hydrated, other), density posterior, Yarkovsky/SRP detection status, orbit condition code, NHATS delta-v and duration, next optical and radar windows, resource-confidence class, and provenance per value.
- **Uncertainty.** Class probabilities that sum to one; quantiles (5, 16, 50, 84, 95) for continuous values; a flag separating measured, inferred from this object's data, and population prior. Karman+'s rule is worth copying: missing data must read as unknown, not as a failed test.
- **Every measurement kept with its source**, not merged silently; Prospector does this [V].
- **Cadence.** NHATS recomputes daily [V]. Daily or weekly ingest of orbits and new measurements; versioned model releases a few times a year with a changelog; frozen, dated snapshots for pre-registered predictions.
- **Formats.** CSV/Parquet and JSON, an API, CC BY licence, one page per object. A file that loads directly as a Prospector enrichment table would give the project its first external user at almost no cost.
- **The page should say what would change the answer**: which single observation (lightcurve, albedo, 0.7 µm band, radar) moves the object most, and when it is next observable.

---

## Reasons this part of the project could fail or mislead

1. Early missions choose targets on launch date and communications distance, so a composition catalog may change no decision before about 2028.
2. The value drivers (PGM grade, water wt%, regolith mechanics) cannot be sensed remotely. A class probability is a weak proxy, and X-complex objects are degenerate between metal (M), enstatite (E) and primitive (P) without an albedo.
3. The accessible population is tiny objects: median H 27.7 for delta-v ≤ 5 km/s. At least 94% of H > 26 objects are fast rotators, and 70% of NHATS has a poor orbit. The honest output may be "almost nothing here is workable", which is a null result worth publishing but not a prospect list.
4. Validation mismatch. Known answers are mostly bodies above 300 m (Bennu, Ryugu, Itokawa, Eros, Didymos, Torifune, Apophis). For decametre bodies there are Kamoʻoalewa and 2022 OB5, and Hayabusa2 just lost 1998 KY26. Calibration claimed on large bodies does not transfer.
5. Even the best-observed small NEA was badly wrong before a spacecraft or JWST looked (Kamoʻoalewa size and class). Stated uncertainty must be wide enough to have covered that case.
6. Redundancy. Karman+ has open-sourced the fusion pipeline; MANOS holds the spectra; AstroForge and TransAstra keep private lists. The new contribution must be the priors, the density channel and the validation, or it adds little.
7. Any "value" number will be quoted without its caveats, as Asterank's was.
8. No customer exists. SpaceX says the market does not currently exist; SBAG found little community interest in ISRU.
9. Agent-compiled catalogs can propagate secondary-source errors. Several of today's search summaries carried wrong or stale dates (launch years, a "2026" NEO Surveyor launch). Every catalog value needs a primary source.

## Open questions

- Has AstroForge fixed the DeepSpace-2 target, and is it still 2022 OB5?
- Will CNSA publish Kamoʻoalewa's mass and bulk density before the November 2027 sample return? Has a sampling attempt happened?
- What terms govern reuse of MANOS spectra and the Ondřejov table in a redistributed catalog?
- Would Karman+ compare its leaderboard against an external catalog, or accept a probabilistic enrichment backend?
- What is CivLabs Atlas?
- Current status of Asteroid Mining Corporation and Origin Space.
- M-Argo's launch date and target.
- How many objects ≤ 20 m has Rubin added to the accessible list in its first year? Karman+ claims discoveries rose from "5-10 per week" to "5-10 per day" [V, company claim].

---

## Sources

Papers and white papers
- ASIME 2016 white paper: https://arxiv.org/abs/1612.00709
- ASIME 2018 white paper: https://arxiv.org/abs/1904.11831
- Lewicki et al. 2021 decadal white paper: https://arxiv.org/abs/2103.02435
- Elvis 2014, How many ore-bearing asteroids?: https://arxiv.org/abs/1312.4450
- Elvis & Esty 2014, How many assay probes: https://arxiv.org/abs/1312.4452
- Jedicke et al. 2018: https://scholarsmine.mst.edu/geosci_geo_peteng_facwork/1362 (doi:10.1016/j.pss.2018.04.005)
- Sonter, technical and economic feasibility: https://nss.org/?p=29711
- Sanchez & McInnes 2011: https://strathprints.strath.ac.uk/29192/1/McInnes_CR_Pure_An_Asteroid_Resource_Map_for_Near_Earth_space_12_Jan_2011.pdf
- Hein, Matheson & Fries: https://arxiv.org/abs/1810.03836
- Calla, Fries & Welch: https://arxiv.org/abs/1808.05099
- Andrews et al. (IAC version): https://iafastro.directory/iac/archive/browse/IAC-13/D1/4/19713/
- Colvin, Crane & Lal (IAC version): https://iafastro.directory/iac/archive/browse/IAC-19/E3/3/54880/
- Metzger 2023: https://arxiv.org/abs/2303.09011
- Cannon, Gialich & Acain 2023: https://www.mining.com/wp-content/uploads/2023/04/Precious-and-structural-metals-on-asteroids-.pdf (doi:10.1016/j.pss.2022.105608)
- Kargel 1994 abstract record: https://stafforini.com/works/kargel-1994-metalliferous-asteroids-potential/
- Rivkin & DeMeo, How many hydrated NEOs: https://arxiv.org/abs/1812.02285
- Yokoyama et al. 2023 (Ryugu): https://eprints.lib.hokudai.ac.jp/repo/huscap/all/90313/Science.pdf
- Lauretta et al. 2024 (Bennu): https://arxiv.org/abs/2404.12536
- Alarcón et al. 2026 (2022 OB5): https://arxiv.org/abs/2605.04784
- Sharkey et al. 2026 (Kamoʻoalewa, JWST): https://arxiv.org/abs/2606.24017
- Nachtrieb & Smith 2026: https://arxiv.org/abs/2607.06806
- Trigo-Rodríguez et al. 2025: https://arxiv.org/abs/2510.27373
- MANOS colours 2026: https://arxiv.org/abs/2603.15872
- Fuzzy multi-criteria target selection: https://doi.org/10.3390/aerospace12090800

Tools and data
- JPL NHATS API (queried 2026-11-20): https://ssd-api.jpl.nasa.gov/nhats.api ; documentation https://ssd-api.jpl.nasa.gov/doc/nhats.html ; intro https://cneos.jpl.nasa.gov/nhats/intro.html
- JPL SBDB API (queried 2026-11-20): https://ssd-api.jpl.nasa.gov/sbdb.api
- Asterank About: https://www.asterank.com/about
- NEOfixer: https://neofixer.arizona.edu/faq/how-does-neofixer-assign-priority
- ESA NEOCC priority list help: https://neo.ssa.esa.int/priority-list/help
- Karman+ Prospector repository: https://github.com/Karmanplus/prospector
- MANOS: https://manos.lowell.edu/
- SpaceMiningData: https://spaceminingdata.com/missions/astroforge-odin.html
- CivLabs Atlas (unreadable): https://civiemlabs.com/atlas/2022-ob5

Companies
- SpaceNews, AstroForge target, 2025-01-29: https://spacenews.com/astroforge-announces-asteroid-target-for-upcoming-mission/
- The Space Review, new wave of asteroid mining ventures, 2025-03-17: https://www.thespacereview.com/article/4955/1
- Aerospace America, AstroForge second attempt, 2026-06-15: https://aerospaceamerica.aiaa.org/astroforge-preps-for-second-attempt-at-reaching-an-asteroid/
- Payload, DeepSpace-2 complete, 2026-06-05: https://payloadspace.com/astroforge-completes-its-deepspace-2-spacecraft/
- Aerospace America, IM-3 slip, 2026-09-15: https://aerospaceamerica.aiaa.org/nasa-expects-one-lunar-launch-this-year-moon-base-manager-says/
- Wikipedia IM-3: https://en.wikipedia.org/wiki/IM-3 ; AstroForge: https://en.wikipedia.org/wiki/AstroForge ; 2022 OB5: https://en.wikipedia.org/wiki/2022_OB5
- AstroForge rename post: https://x.com/AstroForge/status/1965811774281937390
- Karman+ Apophis post, 2026-07-21: https://www.karmanplus.com/k-mission-1-99942-apophis/
- Karman+ leaderboard post, 2025-07-25: https://www.karmanplus.com/asteroid-leaderboard/
- Karman+ Prospector post, 2026-09-16: https://www.karmanplus.com/prospector-rapid-prototyping-for-deep-space/
- Karman+ update, 2026-02-27: https://www.karmanplus.com/k-update/
- Karman+ payload call: https://www.karmanplus.com/high-frontier-payloads/
- Karman+ EPSC 2024 abstract: https://meetingorganizer.copernicus.org/EPSC2024/EPSC2024-587.html
- TransAstra capture bag test, 2026-11-16: https://www.newswire.com/news/transastra-successfully-tests-10-meter-capture-bag-designed-to-capture-22889775
- Gizmodo on New Moon, 2026-03-19: https://gizmodo.com/nasa-backed-startup-to-try-ingenious-asteroid-mining-idea-just-bag-it-2000735650
- SpaceX prospectus coverage: https://www.themarketreporter.co.uk/companies/news/1092680/spacex-prospectus-eyes-moon-refuelling-life-on-mars-and-asteroid-mining-1092680.html ; S-1 (not read, too large): https://www.sec.gov/Archives/edgar/data/1181412/000162828026036936/spaceexplorationtechnologi.htm
- Asteroid Mining Corporation, Companies House: https://find-and-update.company-information.service.gov.uk/company/10085157
- Origin Space: https://en.wikipedia.org/wiki/Origin_Space
- ULA propellant prices: https://www.space.com/33297-satellite-refueling-business-proposal-ula.html
- MIT Technology Review, asteroid mining bubble: https://www.technologyreview.com/2019/06/26/134510/asteroid-mining-bubble-burst-history/

Missions and agencies
- Tianwen-2: https://en.wikipedia.org/wiki/Tianwen-2 ; https://www.astronomy.com/space-exploration/tianwen-2-arrives-at-target-asteroid-kamo%CA%BBoalewa/ ; https://www.planetary.org/articles/chinas-tianwen-2-mission-has-probably-arrived-at-a-quasi-moon-of-earth
- Hayabusa2 retarget: https://www.astroarts.co.jp/article/hl/a/14778_hayabusa2 ; https://www.nikkei.com/article/DGXZQOSG1741Y0X11C26A1000000/ ; Torifune flyby plan https://www.isas.jaxa.jp/en/topics/004151.html ; https://en.wikipedia.org/wiki/Hayabusa2
- Hera: https://www.esa.int/articles/about-us/directorates/operations/space-safety/hera/hera-s-first-close-up-view-of-didymos-asteroids ; https://en.wikipedia.org/wiki/Hera_(space_mission)
- Ramses: https://www.esa.int/articles/ramses-esa-s-mission-to-asteroid-apophis
- DESTINY+: https://destiny.isas.jaxa.jp/2024-10-15-15-26
- OSIRIS-APEX: https://science.nasa.gov/mission/osiris-apex/ (status via search summaries)
- Psyche Mars flyby: https://www.jpl.nasa.gov/news/nasas-psyche-mission-aces-mars-flyby-targets-metal-rich-asteroid/
- Lucy: https://science.nasa.gov/blogs/lucy/2026/10/28/nasas-lucy-reaches-trojan-asteroid-region-5-years-after-launch/
- NEO Surveyor: https://science.nasa.gov/mission/neo-surveyor/
- M-Argo: https://en.wikipedia.org/wiki/M-Argo
- SBAG presentation, March 2020: https://science.nasa.gov/wp-content/uploads/2023/04/SBAG_BurattiPACMarch2020.pdf
- Luxembourg Space Resources Week 2026: https://gouvernement.lu/en/actualites/toutes_actualites/communiques/2026/05-mai/07-delles-lsa.html

