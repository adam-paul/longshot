# Method 0.1

Proposals until Adam freezes them. After that no number changes; a change is a new method version.

- Constants: `method/v0_1/priors.toml`, `missions.toml`, `observe.toml`, `ledger.toml`. Each constant has a `kind` and a `source` beside it.
- `ledger.toml` holds what counts towards a row before any of the rest: the lowest usable lightcurve grade (U 2-), how far two periods may differ (20%), the detection bar for a fitted push (3 sigma), the Spitzer signal-to-noise bar (5), the reflectivity ceiling (1), the rule for a fixed table older than the asteroid, the known-bad values and the bodies that no longer exist. `longshot/ledger.py` holds no threshold of its own.
- Kinds: **measured** from data on disk by a script in `tools/`; **quoted** from a file under `docs/research`, which names the published source; **judgement**, a choice made here, with the range it was chosen from.
- Script outputs: `method/v0_1/derivation/*.txt`.
- Data date: 2026-11-24 for JPL's two lists. Spitzer table as downloaded 2026-11-21; lightcurve database release 2023-10-01; Pravec's table fetched 2026-11-24; class labels built 2026-11-21.
- Tables below are written from the TOML files by `tools/method_doc_tables.py`. `tests/test_method_constants.py` fails if a file, a script and this document disagree.
- Checked 2026-11-25 with `tools/method_check.py`, which recomputes the constants with no code shared with the scripts below. What that check changed is listed in `docs/method-value.md` section 12.

```
uv run python -I tools/method_reflectivity.py     # reflectivity, H uncertainty
uv run python -I tools/method_spin.py             # spin shares
uv run python -I tools/method_class.py            # class shares, class-reflectivity link
uv run python -I tools/method_priors_toml.py      # writes priors.toml from the three above
uv run python -I tools/method_missions.py         # presets against the named targets, read from the pipeline's records
uv run python -I tools/method_doc_tables.py       # tables in this file
uv run python -I tools/method_check.py            # the checker's own recomputation of all five files
```

## 1. Size from brightness

D [m] = 1.329 × 10⁶ × 10^(−H/5) / √reflectivity.

Reflectivity is drawn from what Spitzer measured for near-Earth asteroids with a < 2 au: 1,576 objects (Trilling et al. 2010, 2016). `priors.toml` holds 21 quantiles from 2.5% to 97.5%; a draw interpolates log reflectivity between them and takes the end value outside them.

<!-- table:reflectivity -->
| Share of objects below | 2.5% | 5% | 25% | 50% | 75% | 95% | 97.5% |
|---|---|---|---|---|---|---|---|
| Reflectivity | 0.032 | 0.058 | 0.182 | 0.273 | 0.375 | 0.665 | 0.797 |
<!-- /table -->

H is drawn as normal(H, σ): σ is JPL's H_sigma where JPL gives one (4,970 of 7,231 list members), else 0.36 mag, their median. Size in metres at a given H, with σ = 0.36:

<!-- table:size -->
| H | 5% | 25% | 50% | 75% | 95% |
|---|---|---|---|---|---|
| 22 | 62 | 83 | 103 | 130 | 230 |
| 24 | 25 | 33 | 41 | 52 | 91 |
| 26.2 | 8.9 | 12 | 15 | 19 | 33 |
| 27.7 | 4.5 | 6.0 | 7.4 | 9.5 | 17 |
| 30 | 1.5 | 2.1 | 2.6 | 3.3 | 5.8 |
<!-- /table -->

When the class is measured and the size is not, reflectivity comes from the Spitzer objects whose class comes from a spectrum:

<!-- table:by_class -->
| Class | Objects | 5% | 50% | 95% |
|---|---|---|---|---|
| S (S, Q) | 286 | 0.133 | 0.287 | 0.500 |
| C (C, B, F, G) | 35 | 0.014 | 0.072 | 0.726 |
| X (X, E, M, P) | 38 | 0.027 | 0.174 | 0.831 |
| other | 52 | 0.093 | 0.329 | 0.742 |
<!-- /table -->

Untested:

- Fainter than H 25 this is extrapolation. The table has 3 objects at H 25 or fainter and 15 at H 24 or fainter; 5,402 of 7,231 list members (75%) are fainter than H 25.
- Whether fainter objects reflect more. The 15 at H 24–26 have a median reflectivity of 0.45, against 0.27 in every brighter band; at least 4 of the 15 are fits at a signal-to-noise under 5. If it is real, sizes fainter than H 24 are about a fifth smaller than this table gives.
- The held-out check in `docs/plan.md` Appendix A has not been run.
- The class tables are thin: C 35 objects, X 38. Their median H is 18–19, and 7 of the 411 are fainter than H 22. Mahlke 2022, the main class source, uses reflectivity as an input.
- Literature cards with a measured reflectivity and a class: 4 objects (S 2, C 2). Too few to use.

Do not conclude:

- That a size from brightness is a measurement. The 5%–95% range spans a factor of 3.7.
- That the spread is nature's alone. It holds Spitzer's measurement error and the error in H at the time: 17 objects fit a reflectivity above 1, and with signal-to-noise of 5 or more the 97.5% value is 0.66, not 0.80.
- Anything for the 6 list members with no H. They get no size.
- That small targets follow the table. The two measured since, 1998 KY26 and Kamoʻoalewa, came out 2–3 times smaller than assumed (`AGENTS.md`).

## 2. Spin from brightness

Chance that an asteroid with no measured period turns faster than each threshold: central value (low–high).

<!-- table:spin -->
| H | under 2.2 h | under 1 h | under 10 min |
|---|---|---|---|
| under 20 | 0.01 (0.00–0.10) | 0.01 (0.00–0.10) | 0.0009 (0.00–0.10) |
| 20–22 | 0.15 (0.12–0.17) | 0.07 (0.04–0.09) | 0.05 (0.03–0.06) |
| 22–24 | 0.65 (0.49–0.80) | 0.46 (0.43–0.49) | 0.24 (0.22–0.26) |
| 24–26 | 0.80 (0.70–0.89) | 0.71 (0.65–0.76) | 0.45 (0.39–0.50) |
| 26–28 | 0.87 (0.76–0.98) | 0.85 (0.76–0.93) | 0.67 (0.63–0.70) |
| 28 and fainter | 0.94 (0.88–1.00) | 0.94 (0.88–1.00) | 0.93 (0.88–0.97) |
<!-- /table -->

Each band has up to five estimates of the share: MANOS measured-fast over all its targets, with or without a period (Thirouin et al. 2016, 2018; 228 targets); Alarcon et al. 2026 low and high over all its targets (2.2 h only; 249 targets); and the share among measured periods graded U 2 or 3 in the lightcurve database and Pravec's table, for list members (312 periods) and for all near-Earth asteroids (2,187). Low is the smallest, high the largest, central the midpoint. For 2.2 h:

<!-- table:spin_from -->
| H | low from | high from |
|---|---|---|
| under 20 | floor | list members measured, 95% upper limit (0 of 36) |
| 20–22 | MANOS all targets (3 of 25) | list members measured (9 of 53) |
| 22–24 | list members measured (31 of 63) | Alarcon all targets, high (66 targets) |
| 24–26 | MANOS all targets (58 of 83) | Alarcon all targets, high (132 targets) |
| 26–28 | MANOS all targets (39 of 51) | list members measured (44 of 45) |
| 28 and fainter | MANOS all targets (7 of 8) | list members measured (20 of 20) |
<!-- /table -->

Brighter than H 20, 36 of 44 list members have a reliable period, so central is the measured share for all near-Earth asteroids. One of 1,143 of those turns in under ten minutes, so that share is 0.0009, not 0: a chance that rounds to nothing is not nothing.

The lightcurve database flags 76 near-Earth periods as limits ('>' a minimum, '<' a maximum), 32 of them graded U 2 or better. A limit is counted only at a threshold it decides: a lower limit at or above the threshold is slow, an upper limit at or below it is fast, and any other is left out of that threshold's count. Read as measured periods, as they first were, they moved five cells by up to 0.02.

Untested:

- All of it. The known periods set the prior and favour fast rotators, so it is scored only on periods published after the freeze; about 30 are needed (`docs/plan.md` section 3.3).
- That spin is independent of size, reflectivity and class at a given H. The draw assumes it.
- H 28 and fainter: the low rests on 8 MANOS targets, the high on 20 measured list members.

Do not conclude:

- That low–high is a confidence interval. It is the spread between denominators.
- That measured-only shares are always the upper end. At H 22–24 the all-target MANOS share is above the measured share for list members.
- That a draw has a period. It has a category: under 10 min, 10 min to 1 h, 1 h to 2.2 h, 2.2 h or slower.
- That every measured period under 5 km/s is faster than 2.2 h. 15 of 16 reliable ones are; 2023 RA4 turns in 2.35 h (Pravec, U 2).

## 3. Class from brightness

Share of each class among asteroids of a given brightness, not a given size: central (low–high), in percent.

<!-- table:class -->
| H | Labelled objects | S (S, Q) | C (C, B, F, G) | X (X, E, M, P) | other |
|---|---|---|---|---|---|
| under 20 | 879 | 64% (55–70) | 15% (9–21) | 9% (9–11) | 13% (11–15) |
| 20–22 | 468 | 60% (50–68) | 20% (8–30) | 8% (7–9) | 12% (11–16) |
| 22–24 | 142 | 65% (40–71) | 17% (7–30) | 10% (3–18) | 8% (7–13) |
| 24–26 | 111 | 48% (35–66) | 15% (11–15) | 25% (20–34) | 12% (9–12) |
| 26–28 | 80 | 57% (35–66) | 14% (4–15) | 18% (18–25) | 11% (11–17) |
| 28 and fainter | 80 | 57% (35–61) | 14% (4–15) | 18% (18–25) | 11% (11–17) |
<!-- /table -->

Central is the share among every class label on disk for near-Earth asteroids with a < 2 au (1,680 objects; Mahlke 2022, Sergeyev 2023, Ieva 2020, Deshapriya 2023, Marsset 2022, Perna 2016 and others). H 26–28 and H 28 and fainter share one estimate. Low and high are the smallest and largest share among: spectra only; colours and compilations only; list members with a class on a literature card; and the survey figures quoted in `docs/research/source-prior.md` sections 4, 7 and 8.1 and `verify-prior-null.md` section 5 (Binzel 2019, Devogele 2019, Moskovitz 2026, Lopez-Oquendo 2026 as observed, Sanchez 2024). An on-disk sample under 30 objects sets no bound. `priors.toml` names the estimate behind each bound.

Class is tied to reflectivity through the Spitzer objects with a spectral class. Share of each class in each reflectivity bin:

<!-- table:link -->
| Reflectivity | under 0.10 | 0.10–0.20 | 0.20–0.30 | 0.30–0.45 | 0.45 and over |
|---|---|---|---|---|---|
| S (S, Q), 286 objects | 0.02 | 0.19 | 0.36 | 0.34 | 0.09 |
| C (C, B, F, G), 35 objects | 0.60 | 0.06 | 0.09 | 0.09 | 0.17 |
| X (X, E, M, P), 38 objects | 0.37 | 0.21 | 0.08 | 0.13 | 0.21 |
| other, 52 objects | 0.06 | 0.21 | 0.15 | 0.29 | 0.29 |
| all Spitzer objects | 0.10 | 0.19 | 0.28 | 0.27 | 0.15 |
<!-- /table -->

The joint draw, in order: H; reflectivity; size; class, with weight `joint_weight` × the share above for the drawn reflectivity; density; mass; spin. A measured quantity replaces its step. `joint_weight` is solved so that the classes drawn return the central shares, to within 0.1 of a percentage point, and the sizes drawn stay those of section 1.

A measured class is a label, and labels are wrong at a known rate. In the joint draw a label is on the wrong side of S/Q against the rest in 21 of 100 draws when it comes from colours (colour-based classes disagree with spectral ones for 21% of 874 shared objects, `docs/research/verify-prior-null.md`) and in 12.5 of 100 otherwise (sources disagree on the class of at least 3 of 24 classified objects under 6 km/s; `verify-value-inputs.md` section 4). A mislabelled draw takes a class from the other side, by the same weights, and that class's reflectivity. An asteroid a spacecraft brought a sample back from has no label error. Before, a measured class was taken as certain, and 164 S/Q entries printed a nineteen-in-twenty floor in dollars with a zero chance of nothing.

Untested:

- Every share fainter than H 26: 80 labelled objects in all.
- The upper bound on C fainter than H 26 (15%). It is the project's own pooled figure; the checker could not confirm it in a survey paper (`verify-value-inputs.md` section 2.3, last row).
- The confirmatory labels of `docs/plan.md` Appendix A have not been obtained.
- Colour-based classes disagree with spectra for 21% of shared objects on S/Q against the rest and 33% on four classes (`verify-prior-null.md` section 1).

Do not conclude:

- That a class is a composition. X covers metal and two kinds of rock.
- That these are shares at a given size. Debiased population figures (stony 23%–42%) answer that question and are not used here (`source-prior.md` section 7.2).
- That the orbit adds anything. On 1,680–2,088 labelled objects below 2 au it improved the guess by nothing measurable (`verify-prior-null.md`).

## 4. Density and mass

Mass [t] = (π/6) × D³ × density / 1000.

<!-- table:density -->
| Class | kg/m³, flat within the range | Kind |
|---|---|---|
| S | 1,700–3,400 | quoted |
| C | 900–2,300 | quoted |
| X, reflectivity under 0.10 | 900–2,300 | quoted |
| X, 0.10–0.30, not metal-rich | 2,000–3,500 | quoted |
| X, 0.10–0.30, metal-rich (38% of that bin) | 3,000–7,500 | quoted |
| X, 0.30 and over | 2,000–3,300 | quoted |
| other | 1,200–3,300 | judgement |
<!-- /table -->

Ranges are those of `docs/research/value-inputs.md` section 4, from Carry 2012 and the direct densities in `ground-truth.md` section 7.1. An X draw takes its density from its drawn reflectivity (Tholen's P, M, E split). 38% metal-rich among M is Shepard et al. 2015, 11 of 29 main-belt asteroids.

A bulk density on file replaces the class range in the draw: JPL's for Bennu, Ryugu and Itokawa, or a literature card's from radiation pressure or drift. Bennu's mass is then 60 to 88 million tonnes (5th to 95th) from its measured size and 1,194 kg/m³, not 58 to 140 million from the range for class C. A density a card computed from other values is on file and not used.

Untested:

- All of it at this size. The research found no near-Earth asteroid under about 150 m with a directly measured density (`docs/plan.md` section 1.1).
- The 38%. `verify-value-inputs.md` calls it a placeholder and gives 10%–60%.
- The row for "other", which the research does not give.

Do not conclude:

- That class sets the mass range. Size does: a factor of 3.7 in size is a factor of about 50 in mass.
- That a fast spin means a dense body. 2011 MD, about 1.1 g/cm³, turns in about 12 minutes (`verify-value-inputs.md` section 2.6).

## 5. Missions

A gate is pass or fail when a measurement decides it: the measured value clears the threshold by two of its stated sigma. Otherwise it is untested, with the share of the object's joint draws that pass. A mission fails if any gate fails, passes if every gate passes, and is otherwise untested with the share of draws that pass every gate.

- Stated errors are one sigma (JPL's `diameter_sigma`, Spitzer's `d1sigl` and `d1sigu`, a literature card's `error`, the ± of Pravec's table). A measured value is drawn from its stated error, each side its own width, with no clamp. Read as the whole range, as it first was, the one-sigma range decided 17 of 381 size gates with the threshold inside two sigma.
- A size with no stated error decides a gate only when the threshold is a factor of 2 away, and is drawn log-normally with two sigma equal to that factor. Before, 2 of the 3 capture passes rested on such sizes.
- An untested chance is never stored or printed as 0 or 1. With 2,000 draws it is held between 0.0005 and 0.9995, and prints as "under 1%" or "over 99%". So an untested mission always has an observation ranked.
- A body `ledger.toml` lists as gone fails every mission, with the reason, and has no window, price tag or observation: 2008 TC3, which entered the atmosphere on 7 October 2008.

Surface work (on a larger body):

<!-- table:gates_surface -->
| Gate | Preset | Range in the sources | Kind |
|---|---|---|---|
| Orbit condition code ≤ 5 | at most 5 | 2–5 | judgement |
| Diameter ≥ 30 m | at least 30 m | 18–100 m | judgement |
| Spin period ≥ 2.2 h | at least 2.2 h | 1–3 h | judgement |
<!-- /table -->

Whole-body capture (of a small body):

<!-- table:gates_capture -->
| Gate | Preset | Range in the sources | Kind |
|---|---|---|---|
| Orbit condition code ≤ 5 | at most 5 | 2–5 | judgement |
| Diameter ≤ 10 m | at most 10 m | 7–10 m | judgement |
| Mass ≤ 1,300 t | at most 1,300 t | 100–1,300 t | judgement |
<!-- /table -->

- Orbit: JPL's orbit condition code, 0 best to 9 worst. 2,180 of 7,231 list members have code 5 or better; 212 of 286 under 5 km/s. The gate is labelled for what it tests, the code. It is not JPL's own test of whether a telescope can be pointed: JPL flags the next window of 137 of the 2,180 survey-recovery-only (130 at code 5, 7 at code 4) and lists no window for 575. For those 137 the gate passes and its text says "JPL finds its position too uncertain to point at". Whether they should pass is Adam's call.
- Spin, surface work: the period at which gravity and the outward pull balance at the equator of a sphere with no cohesion, P = √(3π / (G × density)). 2.2 h at 2,250 kg/m³; 2.3 h at 2,000; 3.0 h at 1,200; 1.2 h for solid iron.
- A period decides the spin gate if it is graded U 2 or 3, or is published with no grade on file, whichever source holds it. A period graded under 2 does not.
- A number JPL holds with no grade that another source gives only as a limit is a copy of that limit without its sign: it is kept on file, not used, and the limit decides. 12 list members; for 6 of them the copy had decided the spin gate.
- When a fixed table and two other sources disagree, and one of the two cites a reference dated after the table's edition, the newer period is used and the two stay in conflict (1998 KY26: 5.35 minutes, not the 10.7 of the 2023 lightcurve database).
- When periods in use fall on both sides of 2.2 h, by value or by two sigma of a stated range, no period decides: the gate is untested with the prior for its brightness (2013 NJ: 250 h against 2.02 h).
- A measured size that implies a reflectivity under 0.005 or over 1, for every H within two sigma of its error, does not decide a gate. 2010 NU71's 1.126 km at H 22.7, from a main-belt table, implies 0.0012; the next lowest among the list members with a size in use is 0.020. No size in use is over the ceiling: Kamoʻoalewa's 18 m implies 1.03 at JPL's H and 0.53 two sigma fainter.
- A Spitzer fit counts only at a signal-to-noise of 5 or more in its 4.5 micron band, and never with a fitted reflectivity over 1. Under that bar it stays on file, not used. Six list members had carried a used size with a fitted reflectivity of 1.07 to 1.40, each at signal-to-noise 0.9 to 3.3.
- Mass, capture: no list member but the three sampled asteroids has a measured mass. The gate passes when a measured size, two sigma up, at 7,500 kg/m³ is under the ceiling, fails when it is over at 900 kg/m³ two sigma down, and is otherwise untested. A bulk density on file (15 list members; 12 from a model of the push, not a measured mass) replaces the class range in the draws and so narrows the chance. It does not decide the gate.
- When a source for a gate was not checked, the gate's text says not checked, never not measured.
- Not gated: delta-v (a filter the visitor sets), class, tumbling, and spin for capture. The Keck design allowed up to one turn a minute; the priors have no figure for periods that short.

Presets against the targets companies have named. Surface work:

<!-- table:named_surface -->
| Target | Result | Gates | Why |
|---|---|---|---|
| 2008 EV5 | pass | findable pass, size pass, spin pass | Orbit code 0. 344 m (338 to 350, one sigma; literature card, MacLennan et al. 2022). 3.72 h, graded U 2 (Pravec's table). |
| 2011 AA37 | untested, 0.3485 | findable pass, size untested, spin untested | Not a known pass. Its only period, 10 h, is graded unreliable (Pravec's table: U column 1, remark 'U = 1+ or 2-'), so the spin gate falls back to the prior for H 22.9: 0.35 that it turns once in 2.2 h or slower. No size is measured; from brightness it is 41–149 m (5th-95th), 30 m or wider in 0.997 of draws. Orbit code 0. |
| 2022 DC5 | untested, 0.9975 | findable pass, size untested, spin pass | Not a known pass only because no size is measured: at H 22.93 and a class S from colours, a label taken as wrong in 21 of 100 draws, it is 42–163 m (5th-95th), 30 m or wider in 0.9975 of draws. Orbit code 1. 9.675 h, graded U 3 (Pravec's table). It needs 7.24 km/s, which is a filter here, not a gate. |
| 2021 UH2 | untested, 0.3235 | findable pass, size untested, spin pass | A probable miss on size. No size is measured; at H 25.08 it is 14–57 m (5th-95th), 30 m or wider in 0.32 of draws (0.82 at the 18 m end of the range). Karman+ chose it on brightness as a stand-in for size, on reach and on rotation period. Orbit code 1. 3.8 h, graded U 2- (Pravec's table, from its remark). |
| Apophis | pass | findable pass, size pass, spin pass | Orbit code 0. 340 m (300 to 380, one sigma; literature card, Brozović et al. 2018): 260 m at two sigma. 30.56 h (JPL). The lightcurve database flags it a tumbler, which is not gated. |
<!-- /table -->

Capture:

<!-- table:named_capture -->
| Target | Result | Gates | Why |
|---|---|---|---|
| 2009 BD | pass | findable pass, size pass, mass pass | Orbit code 1. 4 ± 1 m from a thermal model (Mommert et al. 2014, literature card); the paper's other solution, 2.9 m, also passes. At 6 m, two sigma above, and 7,500 kg/m³ it is 850 t, under the ceiling whatever it is made of. At the 100 t end of the range it would be untested, 0.64. |
| 2011 MD | untested, 0.9995 | findable pass, size pass, mass untested | Not a known pass only because its mass is not measured: 6 ± 2 m (Mommert et al. 2014, literature card) is 10 m at two sigma, which at solid-iron density would be 3,900 t. With the density on its literature card, about 750 kg/m³ from radiation pressure and a 2.2-sigma thermal detection, it is 4.6–380 t (5th-95th), under 1,300 t in every draw; a chance is never recorded as 1, so 0.9995. The density narrows the draws and decides no gate. Orbit code 2. |
<!-- /table -->

Untested:

- Every threshold. As of 21 November 2026 we found no spacecraft that has touched an asteroid under about 160 m, or enclosed one of any size (`docs/research/capability.md` section 2).
- The 30 m line. No source states a minimum size for surface work; 30 m is one speaker's "borderline".

Do not conclude:

- That a pass is a target. A pass means three screening lines are met by measurement.
- That 2.2 h is a physical limit. Slight cohesion lets a small body turn faster and keep its surface.
- That "untested, over 99%" is a pass. 2022 DC5 has no measured size.
- That "Orbit condition code ≤ 5: pass" means it can be found again. See the note on the orbit gate above.

## 6. Observe next

How much one observation would settle, for one object and one mission type, is the expected drop in the uncertainty of the pass-or-fail outcome when the result of one gate becomes known, in bits:

gain = H₂(p) − q × H₂(p / q), with H₂(x) = −x log₂ x − (1 − x) log₂(1 − x).

- p: share of the object's joint draws that pass every gate.
- q: share that pass the gate the observation resolves. A rotation lightcurve resolves the spin gate; a size or reflectivity measurement resolves the size gate.
- The gain is 0 when the mission is already pass or fail, when that gate is already decided, or when the mission has no such gate.
- An object's entry gives the mission type and observation with the largest gain; a tie goes to the lightcurve.
- The list is ordered by what can be observed: asteroids a telescope can be pointed at first, then those only a survey could recover, then those with no window through 2045; within each by the year the window opens, then by gain. By gain alone it opened with a 2037 window and a survey-only object.
- When a source for the row the observation would settle was not checked, the entry and the list say so ("Not checked: SsODNet."): the measurement may already exist there.

<!-- table:gain -->
| p | q | Gain, bits | Case |
|---|---|---|---|
| 0.5 | 0.5 | 1.00 | the gate is the only open question, an even bet |
| 0.1 | 0.1 | 0.47 | the gate is the only open question, one chance in ten |
| 0.25 | 0.5 | 0.31 | two open gates, each an even bet |
| 0.36 | 0.36 | 0.94 | 2011 AA37, surface work, a lightcurve (its size gate is all but certain) |
| 0.315 | 1 | 0.00 | 2021 UH2, surface work, a lightcurve (its period is already measured) |
| 0.315 | 0.315 | 0.90 | 2021 UH2, surface work, a size |
<!-- /table -->

What it takes, by the peak brightness JPL predicts for the next window:

<!-- table:needs_lightcurve -->
| Peak magnitude V | A lightcurve needs |
|---|---|
| up to 18 | small telescope |
| 18 to 20 | 2 m class telescope |
| 20 to 22 | 4 m class telescope |
| fainter than 22 | telescope larger than 4 m |
<!-- /table -->

<!-- table:needs_size -->
| Peak magnitude V | A size or reflectivity needs |
|---|---|
| up to 17 | 1–2 m polarimeter or infrared space telescope |
| fainter than 17 | infrared space telescope |
<!-- /table -->

A window counts as pointable when JPL lists one and does not flag it survey-recovery-only. Windows are JPL's as of the data date; none is listed past 2045.

Untested:

- The peak magnitudes. They are JPL's; no detailed position forecast was run (`docs/plan.md` section 7).
- The telescope classes. They are the brightness ranges of `docs/research/verify-obs-window.md` section 3, not a time estimate for any telescope.

Do not conclude:

- That a high gain means the observation will be made. Thermal and radar data are not obtainable on request, and Goldstone is offline until October 2028.
- That the gain counts everything learned. A size also narrows the mass of a capture target; a period can show tumbling. Neither is counted.
- That a lightcurve helps a capture target. Capture has no spin gate, so its gain there is 0.
