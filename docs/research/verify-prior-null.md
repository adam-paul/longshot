# Check: does an NEA's orbit carry class information for mission-accessible objects?

Independent check of `source-prior.md` (first round, 2026-11-20), written 2026-11-21. Everything here was recomputed today from the two local snapshots (`sbdb_neo.json`, `nhats.json`) and fresh downloads. No source-region model was used anywhere in the empirical test.

## Bottom line

1. **The first-round null holds, on about 2.5 times more albedos and ten times more taxonomic classes.** For NHATS members with a measured albedo (169) or a taxonomic class (266 to 278), classifiers trained on orbital elements predict the class no better than the plain class frequency. Every orbit-only skill estimate is zero or negative. The best of six model-and-training combinations gives -0.003 bits per object [95% interval -0.022, +0.015] for dark versus bright. Permutation tests agree: 54 contrasts, one with p < 0.05, which is what chance gives.
2. **The stronger evidence is the a < 2 au set, which contains every NHATS orbit** (all 7,229 NHATS objects have a < 2 au). With 1,680 to 2,088 labelled objects, orbit-only skill is +0.003 bits [-0.002, +0.008] for dark versus bright, 0.000 [-0.001, +0.001] for S/Q versus the rest, and -0.001 [-0.004, +0.003] for four classes. That is under 1% of the class entropy, with 95% upper limits of 0.3% to 2%.
3. **The pipeline does find the signal where one exists.** Over all NEAs, orbit alone removes 6.7% to 7.8% of the log loss for dark versus bright (AUC 0.66 to 0.67), none of it from inside a < 2 au. The observed dark fraction is flat at 14% to 17% across four semimajor-axis bins below 2 au, then rises to 28%, 47% and 80%.
4. **H carries more than orbit below 2 au, but H itself carries very little, and its albedo signal is mostly a survey artefact.** H-only skill is 2.3% of class entropy for dark versus bright and 0.5% for taxonomy. The albedo part appears only in NEOWISE-detected objects (4.4%) and vanishes in the Spitzer sample (0.2%), whose targets were picked from the optical catalogue. Inside NHATS neither H nor orbit shows measurable skill, and an H-binned table fitted on NHATS members alone is worse than a single frequency.
5. **The NHATS-only test is weak on its own.** Injection tests show it would catch orbit information of 0.10 bits (10% to 14% of class entropy) almost always, 0.05 bits in roughly half to nine-tenths of trials, and 0.02 bits in a minority. The real result excludes 0.10 bits and leaves 0.05 bits unlikely but possible. The tight limit comes from the a < 2 au set, where a 0.02-bit dependence would have been caught every time and is excluded.
6. **What this check cannot say.** Labelled NHATS members are much brighter than the NHATS list (median H 21.5 to 22.8 against 26.2). Only 21 labelled objects have delta-v under 6 km/s and 4 have delta-v under 5 km/s. For the smallest, most Earth-like objects, where lunar ejecta or artificial objects could make the orbit informative, the claim is untested.
7. **Two label traps surfaced.** Two published compilations carry class-average albedos that look like measurements (taxonomy in disguise). And the dark fraction of the same population is 31% in NEOWISE detections but 10% in Spitzer targets, so any base rate depends on which survey supplied the label.

## Verdicts

| Claim | Verdict | Evidence | Corrected or added value |
|---|---|---|---|
| Orbit adds no usable class information inside NHATS | **Confirmed**, within the stated sensitivity; untested for H >= 26 and delta-v < 6 km/s | Orbit-only skill <= 0 for all three labels, three models, two training regimes (Table A). Likelihood-ratio p = 0.59, 0.70, 0.82. 54 permutation contrasts, one below 0.05. | Inside NHATS: 0.10 bits excluded, 0.05 bits disfavoured. For a < 2 au, 95% upper limits of 0.013 bits (dark), 0.003 (S/Q), 0.014 (four classes). |
| H adds more than orbit | **Partly confirmed** | True for a < 2 au (H minus orbit: +0.011 bits [+0.003, +0.020] for dark; +0.008 [+0.001, +0.016] for four classes). Not measurable inside NHATS. False over all NEAs (orbit 0.052 bits, H 0.006). | H is worth 0.5% to 2.3% of class entropy below 2 au. The albedo part is a thermal-infrared selection effect (present in NEOWISE, absent in Spitzer). |
| Published base rates for dark or carbonaceous material at NHATS sizes span about 5% to 67% | **Partly confirmed** | The 67% is in Lopez-Oquendo et al. as stated. The per-source inputs for 5%, 10% and 39% are in the cited papers. But 5%, 10% and 39% are the researcher's own derivations, the 39% needs an invented Hungaria row, and the five numbers measure four different things. | Redone arithmetic: 5.4% to 5.8%, 10.0%, and 46% (not 39%) if only the published nu6 and 3:1J rows are used. Measured at fixed H: 10.1% dark [8.7, 11.7] for a < 2 au (Spitzer). |
| Mutual information 0.003 to 0.005 bits out of about 1.4 | **Partly confirmed** | Consistent with the report's own percentile ranges (I get 0.0005 to 0.002 bits for dark versus rest). It is a property of the two models, not a measurement. | Not measurable inside NHATS. Measured for a < 2 au: 0.003 bits [-0.002, +0.008]. The "1.4 bits" denominator fits only the three-class figure; the dark-or-bright entropy is 0.35 to 0.48 bits. |
| AUC 0.63 for all NEOs, 0.50 for a < 2 au, 0.47 for NHATS | **Confirmed** | I reproduced the label set to within one object (1,205 / 704 / 69 objects; 41.0 / 32.2 / 36.2% dark) and the semimajor-axis-only AUC (0.632 against 0.631). Direct classifiers on the larger set: 0.66 to 0.67, 0.53 to 0.55, 0.41 to 0.51. | The NHATS figure alone proved nothing: its standard error was 0.073. |
| nu6 is the top source for more than 99.9% of NHATS objects | **Partly confirmed** | Published per-object values: nu6 is the top source for 152 of the 156 distinct NHATS members (97.4%) listed in Marsset et al. 2022 or Sergeyev et al. 2023. I did not rerun the models. | 97% rather than 99.9% for the brighter members that have published values. |

## 1. The labelled set

One row per near-Earth asteroid in the SBDB snapshot (43,158 asteroids; 209 comets dropped) with at least one label. Orbital elements, H and Earth MOID come from SBDB; the Tisserand parameter is computed from a, e, i.

| Source | Kind | NEAs matched | Used as |
|---|---|---|---|
| NEOWISE team thermal fits (Mainzer 2011, 2012, 2014a, 2014b; Nugent 2015, 2016; Masiero 2017, 2018), VizieR | measured albedo | 1,161 | albedo, first choice |
| JPL SBDB albedo field | measured albedo (mostly NEOWISE) | 1,205 | albedo, second |
| Spitzer NEO table (Trilling et al.; GitHub mommermi/spitzerneos) | measured albedo | 2,124 | albedo, third |
| Sergeyev et al. 2023 (compiled albedo; colour classes) | albedo and colour-based class | 695 / 1,812 | albedo, fourth; class, low priority |
| Perna et al. 2016 (hazardous asteroids) | spectral class, literature albedo | 261 / 103 | class; albedo last |
| Mahlke et al. 2022 | spectral class | 1,165 | class, first choice |
| Marsset et al. 2022 (MITHNEOS near-infrared) | spectral class | 411 (351 usable in four classes) | class, second |
| Devogele et al. 2019 (MANOS) | spectral class | 209 | class, third |
| SBDB spec_B, spec_T | spectral class | 324 | class |
| Ieva et al. 2020, Deshapriya et al. 2023 | compiled class | 1,080 / 1,578 | class, after spectra |
| Tinaut-Ruano 2026 (Gaia), Erasmus 2017, Popescu 2018, Navarro-Meza 2024 | colour-based class | 19 / 18 / 5 / 68 | class, last |

Not obtained: Binzel et al. 2019 and Masiero et al. 2020, 2021 are not on VizieR. Binzel's classes enter indirectly through Mahlke 2022 and the two compilations (I did not check the overlap object by object). The SsODNet bulk table was not fetched (the first round measured it at a few kB/s).

Labels: (a) dark if pV < 0.10; (b) S/Q, C (C, B, F, G), X (X, E, M, P), other (A, D, K, L, O, R, T, V, Z); (c) S/Q versus the rest, which also uses objects only known as "C or X".

| Subset | Albedo (dark) | Four classes (S/Q, C, X, other) | S/Q vs rest | Median H of labelled objects |
|---|---|---|---|---|
| All NEAs | 3,120 (714, 22.9%) | 2,713 (1,613 / 502 / 278 / 320) | 2,777 | 19.2 to 19.5 |
| a < 2 au | 2,088 (333, 15.9%) | 1,680 (1,031 / 274 / 170 / 205) | 1,713 | 19.5 to 19.9 |
| NHATS members | 169 (35, 20.7%) | 266 (150 / 40 / 43 / 33) | 278 | 21.5 (albedo), 22.8 (class) |
| NHATS-like box (a 0.8 to 1.3 au, e < 0.3, i < 10 deg) | 98 (17) | 150 (89 / 22 / 28 / 11) | 156 | 22.0 to 23.4 |
| NHATS, H >= 24 | 25 (7) | 105 (52 / 15 / 26 / 12) | 112 | 24.7 to 25.9 |
| NHATS, delta-v < 6 km/s | 6 | 15 | 16 | too few to test |
| NHATS, delta-v < 5 km/s | 0 | 4 | 4 | too few to test |

For scale: the NHATS list has 7,229 objects, median H 26.2, 88% with H >= 24, 726 with delta-v < 6 km/s and 286 with delta-v < 5 km/s. Half of NHATS (50.1%) lies in the box, and 99.9% of the delta-v < 6 km/s objects do.

**Trap 1: class-average albedos.** The Deshapriya et al. 2023 table has an albedo for 1,868 NEAs. For 458 of them no other source has a measurement, and those 458 take only nine distinct values (0.26 for 286 S- and Q-types, 0.049 for C and B, 0.105 for X, and so on). They are assigned from the taxonomic class. Ieva et al. 2020 does the same: its "average albedo" column has eight distinct values over 1,081 objects, one per class. I excluded both. Had I kept them, the albedo label would have been taxonomy in disguise for 13% of the set and for 96 of the NHATS members.

**Trap 2: the label depends on the survey.** For a < 2 au, 31.1% of NEOWISE-fitted objects are dark (212 of 681) against 10.1% of Spitzer objects (159 of 1,574). Where both measured the same object (326), they agree on dark or bright 91% of the time. So the gap is mostly selection, not measurement: NEOWISE detects by thermal flux (size), while Spitzer made pointed observations of NEOs already in the optical catalogue (brightness). I did not re-read the Spitzer target-selection rules today.

**Label noise.** Colour-based classes (Sergeyev) disagree with spectral classes (Mahlke) for 21% of 874 shared objects on S/Q versus rest, and for 33% on four classes. Among NEOWISE albedos with spectral classes, 93% of C types and 6% of S types are dark; with Spitzer albedos and colour classes it is 25% and 6%. Noise of this size weakens any real signal. It cannot create the null.

## 2. Method

- Features: a, e, i, q, Tisserand parameter, Earth MOID ("orbit"); H; or both.
- Models: L2 logistic regression (strength chosen by inner cross-validation), k-nearest-neighbour (k chosen by inner cross-validation, shrunk to the prior), gradient-boosted trees (shallow, early stopping). Features are rank-transformed for the first two.
- Baselines, fitted on training folds only: the class frequency, and the class frequency in seven fixed H bins (edges 16, 18, 20, 22, 24, 26) shrunk toward the overall frequency.
- Protocol: stratified 5-fold cross-validation, repeated 10 times (20 times for the two small subsets). Two training regimes for subsets: inside the subset only, and pooled (subset training folds plus every labelled NEA outside the subset, with a subset indicator).
- Scores: log loss in bits per object and multi-class Brier score. Skill is baseline minus model, so positive means the model is better. Intervals are 95% paired bootstraps over objects (4,000 resamples).
- "Best of six" picks the largest point estimate among three models and two regimes. That choice flatters the model, so it is the conservative figure for a null claim.
- Cross-checks by other routes: per-feature AUC, likelihood-ratio tests of nested logistic models, a binned mutual-information estimate with its permutation bias, permutation nulls for the cross-validated skill, and injection-recovery with synthetic labels.

## 3. Results

### 3.1 Positive control: all NEAs

Orbit alone gives +0.052 to +0.060 bits per object for dark versus bright (6.7% to 7.8% of the 0.776-bit class entropy), AUC 0.66 to 0.67. It holds inside each survey (NEOWISE only +0.040 bits, Spitzer only +0.023 bits) and strengthens when ambiguous albedos are dropped (+0.076 bits, AUC 0.71). The first-round figure for the published models was AUC 0.63 and +5.0%. So the models and a direct fit agree on how much the orbit knows over the whole population. It is also close to the models' own internal figure (0.068 bits for all NEOs in the first-round table).

Taxonomy shows far less: +0.001 to +0.006 bits (at most 0.3%) for four classes. The samples differ (taxonomy needs a bright target; a third of the albedos come from an infrared-selected survey), so the two labels are not measuring the same thing.

Dark fraction by semimajor axis, all 3,120 albedos: 14% (a < 1.0), 17% (1.0 to 1.3), 16% (1.3 to 1.6), 16% (1.6 to 2.0), 28% (2.0 to 2.5), 47% (2.5 to 3.0), 80% (above 3.0 au). C-complex fraction: 13%, 16%, 16%, 17%, 19%, 25%, 43%.

### 3.2 a < 2 au

No orbit skill for any label or model (Table A). The likelihood-ratio test does detect a faint association for albedo (p = 0.0006; about 0.006 bits after subtracting the chance expectation, 1% of class entropy), none for S/Q versus rest (p = 0.56), and a marginal one for four classes (p = 0.02). The albedo association is strongest in Earth MOID (AUC 0.435 [0.40, 0.47]: dark objects have smaller MOID). It sits in the Spitzer sample (AUC 0.42 [0.38, 0.47], and 0.38 to 0.48 within each H quartile), not in NEOWISE (0.49 [0.44, 0.54]). I have not established whether it is physical or an effect of observing geometry on the Spitzer thermal fits (low-MOID objects are observed close and at high phase angle). Either way it is worth about 0.005 bits and gives no measurable out-of-sample skill.

### 3.3 NHATS members and the NHATS-like box

No orbit skill (Tables A, B, E). The same holds for spectra-only classes, for each albedo survey on its own, and for clear-cut albedos (Table D).

One reading aid for Table B: in the small subsets "orbit+H against the H-binned frequency" is positive (for example +0.037 bits in the box). That is not orbit skill. The H-binned table is worse than the flat frequency there, and a heavily regularised model wins simply by ignoring H. The like-for-like contrast (orbit+H against H only, same model) is zero.

### 3.4 What could have been detected

Likelihood-ratio tests give a formal 95% upper limit on the orbit information (if the dependence is monotonic in the six rank-transformed elements) and the level detectable with 80% power:

| Subset | Label | n | p (orbit) | 95% upper limit (bits; % of entropy) | Detectable with 80% power (bits; % of entropy) |
|---|---|---|---|---|---|
| a < 2 au | dark | 2,088 | 0.0006 | 0.013 (2.0%) | 0.005 (0.7%) |
| a < 2 au | S/Q vs rest | 1,713 | 0.56 | 0.003 (0.3%) | 0.006 (0.6%) |
| a < 2 au | four classes | 1,680 | 0.024 | 0.014 (0.9%) | 0.009 (0.5%) |
| NHATS | dark | 169 | 0.59 | 0.033 (4.4%) | 0.058 (7.9%) |
| NHATS | S/Q vs rest | 278 | 0.70 | 0.015 (1.5%) | 0.035 (3.6%) |
| NHATS | four classes | 266 | 0.82 | 0.015 (0.9%) | 0.055 (3.3%) |
| Box | dark | 98 | 0.52 | 0.063 (9.5%) | 0.100 (15%) |
| Box | S/Q vs rest | 156 | 0.85 | 0.015 (1.5%) | 0.063 (6.4%) |
| Box | four classes | 150 | 0.49 | 0.065 (4.1%) | 0.097 (6.1%) |
| NHATS, H >= 24 | S/Q vs rest | 112 | 0.32 | 0.077 (7.7%) | 0.088 (8.8%) |
| NHATS, H >= 24 | four classes | 105 | 0.65 | 0.069 (3.9%) | 0.138 (7.9%) |

Where the upper limit is below the 80%-power level, quote the power level: it is the honest statement of what the sample could have shown.

Injection-recovery gives the same picture without assuming a functional form. I replaced the real labels with synthetic ones that depend on the real orbits by a known amount (a smooth trend in semimajor axis, or a pattern confined to the low-e, low-i corner), kept the real sample size and class balance, and ran the same cross-validation 40 times per setting. "Chance of detection" is the share of trials whose skill exceeds the 95th percentile of the no-signal trials (normal approximation; Table F gives the stricter "interval excludes zero" rate).

| Subset | Label | n | Smooth trend: chance of detection at 0.01 / 0.02 / 0.05 / 0.10 bits (best model) | Corner pattern: 0.05 / 0.10 bits (best model) | Smallest injected level that the real result excludes at p < 0.05 in all three models |
|---|---|---|---|---|---|
| a < 2 au | dark | 2,088 | 99% / 100% / 100% / 100% | 100% / 100% | 0.02 bits smooth; 0.05 bits corner |
| a < 2 au | S/Q vs rest | 1,713 | 95% / 100% / 100% / 100% | 100% / 100% | 0.02 bits smooth; 0.05 bits corner |
| NHATS | dark | 169 | 16% / 28% / 69% / 96% | 48% / 85% | 0.10 bits smooth; corner not excluded (trees alone exclude 0.10) |
| NHATS | S/Q vs rest | 278 | 40% / 71% / 91% / 100% | 50% / 93% | 0.10 bits smooth (0.05 in two of three); corner 0.10 in two of three |
| Box | dark | 98 | 4% / 20% / 48% / 77% | 47% / 76% | none (0.10 smooth in two of three) |
| Box | S/Q vs rest | 156 | 8% / 38% / 55% / 91% | 48% / 82% | 0.10 bits smooth |

For scale, 0.10 bits is 10% to 14% of the class entropy and 0.02 bits is 2% to 3%.

So: inside NHATS, orbit information of about 0.10 bits is ruled out and 0.05 bits is unlikely; nothing smaller can be seen there. Smaller effects are ruled out only by the a < 2 au set, on the assumption that NHATS orbits behave like the rest of a < 2 au (the NHATS and non-NHATS halves of a < 2 au give the same null). The box with albedo labels (98 objects, 17 dark) and anything at H >= 24 with albedo labels (25 objects) are too small to conclude anything on their own.

### 3.5 Is H the better predictor?

| Subset | Label | Orbit only | H only | Orbit minus H |
|---|---|---|---|---|
| All NEAs | dark | +0.052 [+0.037, +0.067] | +0.006 [+0.001, +0.010] | +0.046 [+0.030, +0.063] |
| All NEAs | four classes | +0.006 [-0.001, +0.012] | +0.001 [-0.002, +0.005] | +0.004 [-0.003, +0.011] |
| a < 2 au | dark | +0.003 [-0.002, +0.008] | +0.014 [+0.006, +0.023] | -0.011 [-0.020, -0.003] |
| a < 2 au | S/Q vs rest | -0.000 [-0.001, +0.001] | +0.004 [-0.001, +0.010] | -0.005 [-0.010, +0.001] |
| a < 2 au | four classes | -0.001 [-0.004, +0.003] | +0.008 [+0.000, +0.015] | -0.008 [-0.016, -0.001] |
| NHATS | dark | -0.003 [-0.008, +0.000] | -0.008 [-0.018, +0.002] | +0.004 [-0.007, +0.015] |
| NHATS | four classes | -0.003 [-0.007, +0.001] | -0.003 [-0.013, +0.006] | +0.001 [-0.009, +0.010] |

(Logistic regression, bits per object, skill against the class frequency.)

- Below 2 au, H beats orbit, but by 0.005 to 0.011 bits. H is worth 2.3% of class entropy for albedo and 0.5% for taxonomy (1.0% with spectra only).
- **The albedo part is selection.** For a < 2 au, H-only skill is +0.039 bits [+0.017, +0.062] (AUC 0.65) in NEOWISE-fitted objects and +0.001 [-0.002, +0.004] (AUC 0.53) in Spitzer objects. Dark fraction by H bin (under 16, 16 to 18, 18 to 20, 20 to 22, 22 to 24, 24 to 26): NEOWISE 2%, 20%, 32%, 41%, 43%, 36%; Spitzer 2%, 8%, 10%, 10%, 19%, 10%. A thermal survey detects a faint-H object only if it is large for its H, which means dark. A catalogue object is drawn the way a Spitzer target was, so the Spitzer row is the relevant one. (A second mechanism could add to it: albedo is computed from H, so an error in H makes a faint-looking object look dark as well. The flat Spitzer row suggests this is minor.)
- **The taxonomy part is real in direction and small.** For a < 2 au the S/Q fraction is 71% (H < 16), 68%, 61%, 59%, 62%, 45% (H 24 to 26, n = 119) and 57% (H >= 26, n = 82). The X fraction is 5% to 11% below H 24 and 25% and 18% in the last two bins. This matches Devogele et al. 2019 and the direction of Moskovitz et al. 2026 (S+Q falling with H at 2.9 sigma, X rising at 2.8 sigma; confirmed in the paper), though my last bin is flatter than their fit.
- Inside NHATS, H shows nothing measurable, and the H-binned frequency fitted on NHATS members alone loses to the flat frequency (-0.022, -0.010 and -0.024 bits for the three labels), because the bins are thin.

## 4. Audit of the first-round method

**Mutual information.** As described, it is the information implied by each model's own per-cell probabilities, averaged over NHATS orbits. That has four consequences.

- It is free of small-sample estimator bias, because nothing is counted. I checked the order of magnitude from the report's own percentile ranges: P(dark) spanning 0.043 to 0.086 implies about 0.002 bits, and 0.090 to 0.115 implies about 0.0005 bits. The report's 0.0027 and (three-class) 0.0052 are consistent.
- It measures how much the models' predictions vary, not how much nature varies. It is near zero by construction once one source dominates. Its weak points: 74% of NHATS objects were clamped to the Granvik model's last H bin and 15% to NEOMOD's; neither model has a lunar, tidal or artificial source; the two models disagree on Hungaria by a factor of 30.
- The METEOMOD figure is different: it comes from sparse maps (about 1,000 particles each), so it has the bias. Rebinning cut it from 0.109 to 0.045 bits, which is what bias does. No null was subtracted, so "at most about 0.05 bits" is still an overestimate of unknown size. For comparison, a 12-cell binned estimate on my 169 NHATS albedos returns 0.077 bits, of which 0.053 is pure bias (permutation mean).
- Minor error: "0.003 to 0.005 bits out of about 1.4" mixes a three-class figure (entropy 1.36 bits) with a two-class one (entropy 0.35 bits at a 6% dark fraction). The two-class ratio is about 0.8%, not 0.2%. The conclusion is unaffected.

**AUC test.** I rebuilt the label set from the SBDB albedo field: 1,205 objects (41.0% dark), 704 with a < 2 au (32.2%), 69 NHATS members (36.2%), 74 in their box (32.4%). These match the report (1,204 / 704 / 69 / 74). Semimajor axis alone gives AUC 0.632 (report: 0.631).

- **The NHATS test was underpowered.** With 69 objects and 25 dark, the standard error of an AUC near 0.5 is 0.073. The reported 0.474 has a 95% interval of about 0.33 to 0.62, which includes the all-NEO value. The a < 2 au test (704 objects, standard error 0.023) is the one that carried the conclusion.
- **It tested two models, not the orbit.** A model can score 0.5 because it is wrong. The direct fit here closes that gap.
- **One number was overlooked.** The NEOMOD-based predictor scored AUC 0.399 for a < 2 au. That is 4.3 standard errors below 0.5: an anti-prediction, not noise. The cause is H. The model says fainter objects are brighter-surfaced (more nu6); the SBDB albedo set, being NEOWISE-dominated, has fainter objects darker (AUC of H alone is 0.638 in that set). So the test was confounded with H through a selection effect, and "orbit and H" skill could not be read from it.
- The one-parameter recalibration was fitted on the scored data. With one parameter the optimism is negligible.
- "Class" meant an albedo class. Albedo is not composition: in my set 43% of X-complex objects with an albedo are dark, and 15% of the "other" group.

**nu6.** Not rerun. Published per-object values agree in substance. Across Marsset et al. 2022 (Granvik 2018 probabilities) and Sergeyev et al. 2023, 156 distinct NHATS members have a published most-probable source, and nu6 is the top one for 152 (97.4%). The four exceptions are 2015 DP155 and 755140 (5:2J in Marsset; Sergeyev lists 2015 DP155 as nu6) and 10302 and 495021 (2:1J in Sergeyev). The mean nu6 probability among the Marsset members is about 0.81. These are among the brighter members (H below about 25 in the Marsset table), so they do not test the clamped bins.

## 5. The base-rate claim

| Figure in the report | Source check | Finding |
|---|---|---|
| 5% (NEOMOD3 per-source dark fractions) | NEOMOD3 Table 4 read from the paper: nu6 0.037, 3:1 0.069, inner 0.335, Hungaria 0.149; global 0.233 +/- 0.030; 428 NEOWISE objects; delta ln Z = 15.9. All as reported. | The 5% is not in the paper. With the report's own source weights I get 5.4% to 5.8%. The paper itself quotes 25 +/- 15% dark for 1 < a < 2 au (its Section 4.2). |
| 10% (Granvik and Morbidelli table) | Morbidelli et al. 2020 Table 1: nu6 0.120, 3:1 0.144, Hungaria 0.021. | Derived, not published. I get 10.0% with the report's weights. The two models disagree by a factor of 3 on the nu6 dark fraction (0.037 against 0.120). |
| 25% (METEOMOD, hydrated carbonaceous) | Not rechecked (model files not re-downloaded). | Unverifiable here. It is a share of 1 m bodies by family, not a dark fraction. |
| 39% (Marsset 2022 by escape route) | Table 4 read from the paper: debiased carbonaceous (B + C/P + D) 45.3% for nu6, 51.1% for 3:1J, 66.0% for 5:2J, 88.4% for 2:1J, 24.4% for Phocaea. All as reported. The table has no Hungaria or JFC row. | 39% follows only if the missing Hungaria row is set near 14%. Using the published nu6 and 3:1J rows alone gives 46%. The observed (not debiased) nu6 figure is 20%. |
| 67% (Lopez-Oquendo 2026) | Paper text: 122 NEOs, 5 to 150 m, median 60 m; observed S 40.4 +/- 7%, C/X 43.9 +/- 7%; after debiasing S 23%, C/X 67% (67.9% in Figure 6; 68.7% for D < 40 m). As reported. | "C/X" includes X-types, which need not be dark or carbonaceous. The authors call the correction first-order and say their bias metric "should be interpreted qualitatively". |

So the sources say what the report says they say. But "base rates span 5% to 67%" overstates the disagreement about any one quantity. The 5% and 10% are dark fractions at fixed H; 39% (or 46%) and 67% are fractions at fixed size after debiasing; 67% counts X with C; 25% is a different population. The report's own section 7.2 makes the H-versus-size point.

What the labelled data say, at fixed H and with their selection effects:

- Dark fraction, a < 2 au, Spitzer (optically selected): 10.1% [8.7, 11.7] (159 of 1,574). This agrees with the 10% figure and is about twice the 5% figure.
- Dark fraction, a < 2 au, NEOWISE (size selected): 31.1% [27.7, 34.8] (212 of 681). This is the size-conditioned view.
- NHATS members: dark 20.7% [14.9, 27.6] pooled (35 of 169); 14.3% [8.4, 22.2] Spitzer; 35.5% [23.7, 48.7] NEOWISE.
- NHATS members, four classes: S/Q 56.4% [50.2, 62.4], C 15.0% [11.0, 19.9], X 16.2% [12.0, 21.2], other 12.4%. At H >= 24 (105 objects): S/Q 50%, C 14%, X 25%, other 11%.

## 6. What this means for the plan

1. **Drop the orbit-to-class chain as a per-object discriminator for NHATS.** The prior is a base rate. Publish the null, with the sensitivity stated (Section 3.4).
2. **Keep H in the prior only as a smooth, pooled trend from taxonomy.** Expect about 0.5% to 1% of class entropy. Do not fit H bins on NHATS members alone, and do not learn albedo against H from NEOWISE detections without a selection model.
3. **Fix what "dark fraction" means before quoting one.** At fixed H the data support roughly 10% to 15%; at fixed size roughly 30% or more. The two differ by a factor of about three in the same population.
4. **Label hygiene is a work item.** Exclude class-average albedos (Deshapriya 2023, Ieva 2020) and check every aggregator for the same thing. Treat colour-based classes as noisy (21% to 33% disagreement with spectra). Record which survey supplied each label.
5. **Pre-registered thresholds must match the sample.** With 169 to 278 labelled NHATS members, a held-out test sees orbit effects of about 0.05 to 0.10 bits and nothing smaller. At H >= 24 there are 105 to 112 class labels and 25 albedos. A calibration test "on objects with known answers" can be run for a < 2 au in general, not for the faint bulk of NHATS.
6. **The Earth-like corner is still open.** Four labelled objects have delta-v under 5 km/s. Whether the orbit says anything about lunar or artificial origin there is a separate question that this check did not reach.

## 7. Limits of this check

- Labels are biased toward bright, well-observed objects and are noisy. Noise weakens a real signal; it does not explain a null this consistent across label types and surveys.
- All intervals treat objects as independent. Objects from one survey share systematics.
- I looked at six model-and-regime combinations and several subsets. No positive result here depends on picking one; the positive results (all NEAs, a >= 2 au) appear in every model.
- The first-round scripts are gone, so the audit of their mutual-information code is from the description and from reproducing their inputs and outputs, not from reading the code.

## Files

- Scripts: `data/research/scripts/pn_build.py` (labels), `pn_cv.py` (cross-validation, permutation, injection), `pn_univar.py` (AUC, likelihood-ratio, binned information), `pn_sources_check.py` (label cross-tab, upper limits), `pn_nu6_dedup.py` (nu6 cross-check), `pn_inject_power.py`, `pn_tables.py`, `pn_summary.py`, `pn_run.sh`. The older `pn_build_labels.py` (from the interrupted attempt) is superseded by `pn_build.py`.
- Outputs: `data/research/out-prior-null/` (`labels.csv`, `build.log`, `cv/`, `perm/`, `inject/`, `univar.txt`, `sources_check.txt`, `nu6_dedup.txt`, `tables.md`).
- Downloads: `data/research/dl/prior-null/` (`spitzer/`, `vizier/`, `papers/`).

## Sources

- Spitzer NEO table: https://github.com/mommermi/spitzerneos
- VizieR (CfA mirror), `https://vizier.cfa.harvard.edu/viz-bin/asu-tsv?-source=<catalogue>`: J/A+A/665/A26 (Mahlke 2022), J/A+A/679/A148 (Sergeyev 2023), J/AJ/158/196 (Devogele 2019), J/AJ/163/165 (Marsset 2022), J/AJ/151/11 (Perna 2016), J/A+A/644/A23 (Ieva 2020), J/A+A/674/A50 (Deshapriya 2023), J/A+A/711/A167 (Tinaut-Ruano 2026), J/A+A/617/A12 (Popescu 2018), J/AJ/154/162 (Erasmus 2017), J/AJ/167/163 (Navarro-Meza 2024), J/ApJ/743/156, J/ApJ/760/L12, J/ApJ/784/110, J/ApJ/792/30 (Mainzer 2011 to 2014), J/ApJ/814/117, J/AJ/152/63 (Nugent 2015, 2016), J/AJ/154/168, J/AJ/156/60 (Masiero 2017, 2018)
- NEOMOD3 (Nesvorny et al. 2024): https://arxiv.org/abs/2404.18805
- Morbidelli et al. 2020: https://arxiv.org/abs/2001.03550
- Marsset et al. 2022: https://arxiv.org/abs/2202.13796
- Lopez-Oquendo et al. 2026: https://arxiv.org/abs/2608.28779
- Moskovitz et al. 2026: https://arxiv.org/abs/2603.15872

## Appendix: full tables

Skill is baseline log loss minus model log loss in bits per object, with a 95% paired bootstrap interval and, in brackets, the percent of baseline loss removed. "Pooled training" means the model also saw every labelled NEA outside the subset.

### Table A. Orbit only against the class frequency (log-loss skill, bits per object [95% interval] and percent of baseline loss)

| Subset | Label | n | Class counts | Class entropy (bits) | Logistic regression | k-nearest-neighbour | Boosted trees | Best of six (model, training set) | AUC range |
|---|---|---|---|---|---|---|---|---|---|
| All NEAs | dark (pV < 0.10) | 3120 | 2406/714 | 0.776 | +0.052 [+0.037, +0.067] (+6.7%) | +0.052 [+0.039, +0.066] (+6.7%) | +0.060 [+0.045, +0.075] (+7.8%) | trees: +0.060 [+0.045, +0.075] (+7.8%) | 0.66-0.67 |
| All NEAs | S/Q vs rest | 2777 | 1136/1641 | 0.976 | +0.002 [-0.002, +0.005] (+0.2%) | +0.002 [-0.002, +0.007] (+0.3%) | +0.005 [-0.001, +0.011] (+0.5%) | trees: +0.005 [-0.001, +0.011] (+0.5%) | 0.52-0.53 |
| All NEAs | S/Q, C, X, other | 2713 | 1613/502/278/320 | 1.597 | +0.006 [-0.001, +0.012] (+0.3%) | +0.001 [-0.008, +0.010] (+0.1%) | +0.005 [-0.004, +0.015] (+0.3%) | logistic: +0.006 [-0.001, +0.012] (+0.3%) |  |
| a < 2 au | dark (pV < 0.10) | 2088 | 1755/333 | 0.633 | +0.003 [-0.002, +0.008] (+0.5%) | -0.001 [-0.006, +0.004] (-0.1%) | -0.001 [-0.006, +0.004] (-0.1%) | logistic: +0.003 [-0.002, +0.008] (+0.5%) | 0.53-0.55 |
| a < 2 au | S/Q vs rest | 1713 | 672/1041 | 0.966 | -0.000 [-0.001, +0.001] (-0.0%) | -0.004 [-0.009, +0.001] (-0.4%) | -0.004 [-0.008, -0.000] (-0.4%) | logistic: -0.000 [-0.001, +0.001] (-0.0%) | 0.49-0.51 |
| a < 2 au | S/Q, C, X, other | 1680 | 1031/274/170/205 | 1.564 | -0.001 [-0.004, +0.003] (-0.0%) | -0.007 [-0.017, +0.004] (-0.4%) | -0.007 [-0.016, +0.003] (-0.4%) | logistic: -0.001 [-0.004, +0.003] (-0.0%) |  |
| NHATS members | dark (pV < 0.10) | 169 | 134/35 | 0.736 | -0.003 [-0.008, +0.000] (-0.5%) | -0.033 [-0.059, -0.010] (-4.5%) | -0.050 [-0.084, -0.018] (-6.8%) | trees, pooled training: -0.003 [-0.022, +0.015] (-0.4%) | 0.41-0.51 |
| NHATS members | S/Q vs rest | 278 | 124/154 | 0.992 | -0.004 [-0.008, -0.001] (-0.5%) | -0.018 [-0.037, -0.000] (-1.8%) | -0.037 [-0.056, -0.018] (-3.8%) | logistic: -0.004 [-0.008, -0.001] (-0.5%) | 0.46-0.49 |
| NHATS members | S/Q, C, X, other | 266 | 150/40/43/33 | 1.676 | -0.003 [-0.007, +0.001] (-0.2%) | -0.054 [-0.097, -0.013] (-3.2%) | -0.058 [-0.102, -0.014] (-3.5%) | logistic: -0.003 [-0.007, +0.001] (-0.2%) |  |
| NHATS-like box | dark (pV < 0.10) | 98 | 81/17 | 0.666 | -0.007 [-0.015, +0.001] (-1.0%) | -0.041 [-0.110, +0.018] (-6.1%) | -0.073 [-0.135, -0.015] (-11.0%) | logistic, pooled training: +0.004 [-0.025, +0.031] (+0.6%) | 0.41-0.55 |
| NHATS-like box | S/Q vs rest | 156 | 64/92 | 0.977 | -0.019 [-0.036, -0.006] (-1.9%) | -0.018 [-0.036, +0.000] (-1.9%) | -0.061 [-0.097, -0.026] (-6.2%) | logistic, pooled training: -0.001 [-0.013, +0.011] (-0.1%) | 0.44-0.49 |
| NHATS-like box | S/Q, C, X, other | 150 | 89/22/28/11 | 1.581 | -0.007 [-0.016, +0.001] (-0.4%) | -0.057 [-0.098, -0.018] (-3.6%) | -0.150 [-0.217, -0.084] (-9.5%) | logistic: -0.007 [-0.016, +0.001] (-0.4%) |  |

### Table B. H only against the class frequency, and orbit against H

| Subset | Label | H-binned frequency vs class frequency | H only, logistic vs class frequency | Best H-only of six | Orbit+H vs H-binned frequency, logistic | Best orbit+H vs H-binned of six | Orbit+H vs H only, same model, logistic | Orbit only minus H only, logistic (positive = orbit better) |
|---|---|---|---|---|---|---|---|---|
| All NEAs | dark (pV < 0.10) | +0.005 [-0.000, +0.010] (+0.6%) | +0.006 [+0.001, +0.010] (+0.7%) | logistic: +0.006 [+0.001, +0.010] (+0.7%) | +0.070 [+0.053, +0.087] (+9.1%) | trees: +0.070 [+0.054, +0.086] (+9.1%) | +0.069 [+0.052, +0.086] | +0.046 [+0.030, +0.063] |
| All NEAs | S/Q vs rest | +0.001 [-0.003, +0.005] (+0.1%) | +0.001 [-0.001, +0.004] (+0.1%) | logistic: +0.001 [-0.001, +0.004] (+0.1%) | +0.007 [+0.000, +0.013] (+0.7%) | trees: +0.009 [+0.002, +0.016] (+0.9%) | +0.006 [+0.000, +0.012] | +0.000 [-0.005, +0.005] |
| All NEAs | S/Q, C, X, other | -0.001 [-0.008, +0.005] (-0.1%) | +0.001 [-0.002, +0.005] (+0.1%) | logistic: +0.001 [-0.002, +0.005] (+0.1%) | +0.015 [+0.005, +0.024] (+0.9%) | logistic: +0.015 [+0.005, +0.024] (+0.9%) | +0.012 [+0.004, +0.020] | +0.004 [-0.003, +0.011] |
| a < 2 au | dark (pV < 0.10) | +0.013 [+0.005, +0.022] (+2.1%) | +0.014 [+0.006, +0.023] (+2.3%) | logistic, pooled training: +0.015 [+0.006, +0.024] (+2.3%) | +0.003 [-0.004, +0.010] (+0.4%) | logistic: +0.003 [-0.004, +0.010] (+0.4%) | +0.002 [-0.003, +0.007] | -0.011 [-0.020, -0.003] |
| a < 2 au | S/Q vs rest | +0.002 [-0.005, +0.010] (+0.2%) | +0.004 [-0.001, +0.010] (+0.5%) | logistic: +0.004 [-0.001, +0.010] (+0.5%) | +0.002 [-0.004, +0.007] (+0.2%) | logistic: +0.002 [-0.004, +0.007] (+0.2%) | -0.001 [-0.004, +0.002] | -0.005 [-0.010, +0.001] |
| a < 2 au | S/Q, C, X, other | +0.007 [-0.006, +0.020] (+0.4%) | +0.008 [+0.000, +0.015] (+0.5%) | logistic: +0.008 [+0.000, +0.015] (+0.5%) | +0.001 [-0.010, +0.012] (+0.1%) | logistic: +0.001 [-0.010, +0.012] (+0.1%) | +0.000 [-0.006, +0.006] | -0.008 [-0.016, -0.001] |
| NHATS members | dark (pV < 0.10) | -0.022 [-0.048, +0.002] (-3.0%) | -0.008 [-0.018, +0.002] (-1.0%) | logistic, pooled training: +0.005 [-0.015, +0.027] (+0.7%) | +0.012 [-0.011, +0.034] (+1.5%) | k-NN, pooled training: +0.023 [-0.012, +0.056] (+3.1%) | -0.003 [-0.012, +0.006] | +0.004 [-0.007, +0.015] |
| NHATS members | S/Q vs rest | -0.010 [-0.034, +0.014] (-1.0%) | -0.001 [-0.010, +0.008] (-0.1%) | k-NN, pooled training: +0.005 [-0.009, +0.020] (+0.6%) | +0.005 [-0.018, +0.029] (+0.5%) | trees, pooled training: +0.011 [-0.011, +0.033] (+1.1%) | -0.004 [-0.012, +0.004] | -0.004 [-0.013, +0.006] |
| NHATS members | S/Q, C, X, other | -0.024 [-0.070, +0.022] (-1.4%) | -0.003 [-0.013, +0.006] (-0.2%) | k-NN, pooled training: +0.004 [-0.030, +0.036] (+0.2%) | +0.021 [-0.025, +0.068] (+1.2%) | trees, pooled training: +0.022 [-0.015, +0.062] (+1.3%) | +0.000 [-0.008, +0.009] | +0.001 [-0.009, +0.010] |
| NHATS-like box | dark (pV < 0.10) | -0.044 [-0.086, -0.005] (-6.5%) | -0.008 [-0.023, +0.005] (-1.1%) | logistic, pooled training: +0.004 [-0.018, +0.028] (+0.6%) | +0.037 [+0.001, +0.078] (+5.2%) | logistic, pooled training: +0.045 [-0.003, +0.098] (+6.4%) | +0.001 [-0.012, +0.016] | +0.001 [-0.014, +0.017] |
| NHATS-like box | S/Q vs rest | -0.007 [-0.051, +0.033] (-0.8%) | -0.001 [-0.002, -0.000] (-0.1%) | k-NN, pooled training: +0.007 [-0.013, +0.028] (+0.8%) | -0.006 [-0.049, +0.038] (-0.6%) | trees, pooled training: +0.008 [-0.032, +0.049] (+0.8%) | -0.012 [-0.024, -0.003] | -0.018 [-0.035, -0.005] |
| NHATS-like box | S/Q, C, X, other | -0.042 [-0.113, +0.029] (-2.7%) | -0.003 [-0.009, +0.001] (-0.2%) | logistic: -0.003 [-0.009, +0.001] (-0.2%) | +0.036 [-0.035, +0.104] (+2.2%) | logistic: +0.036 [-0.035, +0.104] (+2.2%) | -0.002 [-0.010, +0.005] | -0.004 [-0.012, +0.005] |

### Table C. Brier-score skill (multi-class Brier, sum of squared errors; positive = better than baseline)

| Subset | Label | Brier, class frequency | Brier, H-binned | Orbit only vs frequency, logistic | H only vs frequency, logistic | Orbit+H vs H-binned, logistic | Orbit+H vs H-binned, trees |
|---|---|---|---|---|---|---|---|
| All NEAs | dark (pV < 0.10) | 0.3530 | 0.3505 | +0.030 [+0.022, +0.038] (+8.6%) | +0.003 [+0.001, +0.005] (+0.8%) | +0.040 [+0.031, +0.049] (+11.4%) | +0.039 [+0.030, +0.048] (+11.2%) |
| All NEAs | S/Q vs rest | 0.4835 | 0.4829 | +0.001 [-0.001, +0.004] (+0.3%) | +0.001 [-0.001, +0.002] (+0.2%) | +0.004 [+0.000, +0.009] (+0.9%) | +0.006 [+0.001, +0.011] (+1.3%) |
| All NEAs | S/Q, C, X, other | 0.5879 | 0.5881 | +0.002 [-0.000, +0.004] (+0.4%) | +0.000 [-0.001, +0.001] (+0.0%) | +0.005 [+0.002, +0.009] (+0.9%) | +0.006 [+0.002, +0.010] (+1.0%) |
| a < 2 au | dark (pV < 0.10) | 0.2681 | 0.2631 | +0.001 [-0.001, +0.003] (+0.3%) | +0.006 [+0.002, +0.009] (+2.1%) | +0.001 [-0.001, +0.004] (+0.5%) | -0.001 [-0.004, +0.001] (-0.6%) |
| a < 2 au | S/Q vs rest | 0.4768 | 0.4751 | -0.000 [-0.001, +0.001] (-0.0%) | +0.003 [-0.001, +0.007] (+0.6%) | +0.001 [-0.003, +0.005] (+0.2%) | -0.003 [-0.007, +0.001] (-0.7%) |
| a < 2 au | S/Q, C, X, other | 0.5717 | 0.5699 | -0.000 [-0.001, +0.001] (-0.1%) | +0.002 [-0.000, +0.005] (+0.4%) | +0.001 [-0.003, +0.004] (+0.1%) | -0.002 [-0.006, +0.001] (-0.4%) |
| NHATS members | dark (pV < 0.10) | 0.3284 | 0.3387 | -0.002 [-0.003, +0.000] (-0.5%) | -0.004 [-0.009, +0.001] (-1.2%) | +0.005 [-0.005, +0.016] (+1.6%) | -0.015 [-0.030, -0.000] (-4.4%) |
| NHATS members | S/Q vs rest | 0.4942 | 0.5007 | -0.003 [-0.005, -0.001] (-0.6%) | -0.001 [-0.007, +0.006] (-0.1%) | +0.003 [-0.012, +0.020] (+0.7%) | -0.011 [-0.027, +0.005] (-2.2%) |
| NHATS members | S/Q, C, X, other | 0.6180 | 0.6246 | -0.001 [-0.002, +0.000] (-0.2%) | -0.001 [-0.005, +0.003] (-0.2%) | +0.006 [-0.009, +0.019] (+0.9%) | -0.016 [-0.033, -0.000] (-2.6%) |
| NHATS-like box | dark (pV < 0.10) | 0.2873 | 0.3038 | -0.002 [-0.005, +0.000] (-0.8%) | -0.004 [-0.011, +0.002] (-1.3%) | +0.014 [+0.001, +0.028] (+4.5%) | -0.010 [-0.028, +0.011] (-3.1%) |
| NHATS-like box | S/Q vs rest | 0.4841 | 0.4878 | -0.008 [-0.014, -0.003] (-1.6%) | -0.001 [-0.001, -0.000] (-0.2%) | -0.002 [-0.030, +0.025] (-0.4%) | -0.029 [-0.060, +0.002] (-6.0%) |
| NHATS-like box | S/Q, C, X, other | 0.5868 | 0.5962 | -0.002 [-0.006, +0.000] (-0.4%) | -0.001 [-0.003, +0.000] (-0.2%) | +0.007 [-0.016, +0.030] (+1.2%) | -0.045 [-0.072, -0.020] (-7.6%) |

### Table D. Sensitivity variants (logistic regression, trained inside the subset; log-loss skill in bits)

| Run | n | Class counts | Orbit only vs frequency | H only vs frequency | Orbit+H vs H-binned | AUC orbit / H |
|---|---|---|---|---|---|---|
| All NEAs, dark, NEOWISE fits only | 1161 | 690/471 | +0.040 [+0.019, +0.061] (+4.2%) | +0.030 [+0.014, +0.046] (+3.1%) | +0.068 [+0.042, +0.094] (+7.2%) | 0.63 / 0.62 |
| All NEAs, dark, Spitzer only | 2124 | 1835/289 | +0.023 [+0.010, +0.036] (+4.0%) | -0.000 [-0.001, +0.001] (-0.0%) | +0.026 [+0.013, +0.039] (+4.5%) | 0.63 / 0.53 |
| All NEAs, dark, clear labels | 2549 | 2030/519 | +0.076 [+0.055, +0.097] (+10.4%) | +0.005 [-0.000, +0.009] (+0.6%) | +0.100 [+0.076, +0.123] (+13.7%) | 0.71 / 0.55 |
| a < 2 au, dark, NEOWISE fits only | 681 | 469/212 | -0.003 [-0.004, -0.001] (-0.3%) | +0.039 [+0.017, +0.062] (+4.4%) | +0.004 [-0.014, +0.021] (+0.5%) | 0.46 / 0.65 |
| a < 2 au, dark, Spitzer only | 1574 | 1415/159 | +0.000 [-0.004, +0.005] (+0.1%) | +0.001 [-0.002, +0.004] (+0.2%) | +0.002 [-0.004, +0.008] (+0.4%) | 0.55 / 0.53 |
| a < 2 au, dark, clear labels | 1741 | 1532/209 | +0.001 [-0.004, +0.007] (+0.3%) | +0.014 [+0.005, +0.024] (+2.7%) | +0.000 [-0.006, +0.007] (+0.1%) | 0.55 / 0.62 |
| NHATS, dark, NEOWISE fits only | 62 | 40/22 | -0.107 [-0.232, -0.019] (-11.4%) | -0.014 [-0.054, +0.013] (-1.5%) | +0.024 [-0.033, +0.079] (+2.4%) | 0.42 / 0.52 |
| NHATS, dark, Spitzer only | 112 | 96/16 | -0.008 [-0.023, +0.003] (-1.4%) | -0.002 [-0.007, +0.002] (-0.4%) | +0.024 [-0.004, +0.058] (+3.9%) | 0.50 / 0.41 |
| NHATS, dark, clear labels | 142 | 114/28 | -0.019 [-0.044, +0.002] (-2.7%) | -0.004 [-0.008, +0.000] (-0.5%) | +0.007 [-0.027, +0.043] (+1.0%) | 0.48 / 0.46 |
| a < 2 au, S/Q vs rest, spectra only | 967 | 330/637 | +0.001 [-0.005, +0.006] (+0.1%) | +0.007 [-0.002, +0.016] (+0.7%) | -0.002 [-0.013, +0.008] (-0.3%) | 0.54 / 0.57 |
| NHATS, S/Q vs rest, spectra only | 205 | 88/117 | -0.002 [-0.004, +0.000] (-0.2%) | -0.003 [-0.007, +0.001] (-0.3%) | +0.000 [-0.032, +0.033] (+0.0%) | 0.47 / 0.51 |
| a < 2 au, four classes, spectra only | 950 | 637/86/114/113 | +0.004 [-0.004, +0.012] (+0.3%) | +0.014 [+0.001, +0.027] (+1.0%) | -0.006 [-0.025, +0.013] (-0.4%) |  |
| NHATS, four classes, spectra only | 202 | 117/21/40/24 | -0.003 [-0.006, +0.001] (-0.2%) | -0.004 [-0.012, +0.002] (-0.3%) | +0.008 [-0.064, +0.082] (+0.5%) |  |
| a >= 2 au, dark | 1032 | 651/381 | +0.063 [+0.037, +0.088] (+6.6%) | +0.026 [+0.010, +0.043] (+2.8%) | +0.072 [+0.044, +0.100] (+7.8%) | 0.67 / 0.61 |
| a >= 2 au, S/Q vs rest | 1064 | 464/600 | +0.005 [-0.004, +0.014] (+0.5%) | -0.000 [-0.001, -0.000] (-0.0%) | +0.007 [-0.005, +0.020] (+0.8%) | 0.56 / 0.48 |
| a >= 2 au, four classes | 1033 | 582/228/108/115 | +0.006 [-0.005, +0.016] (+0.3%) | -0.001 [-0.001, -0.000] (-0.0%) | +0.012 [-0.006, +0.030] (+0.8%) |  |
| H >= 22 (any orbit), dark | 227 | 145/82 | +0.031 [-0.012, +0.076] (+3.3%) | -0.002 [-0.013, +0.007] (-0.2%) | +0.048 [-0.005, +0.098] (+5.0%) | 0.63 / 0.49 |
| H >= 22 (any orbit), S/Q vs rest | 466 | 201/265 | -0.001 [-0.004, +0.002] (-0.1%) | -0.002 [-0.003, -0.000] (-0.2%) | -0.003 [-0.017, +0.012] (-0.3%) | 0.52 / 0.48 |
| H >= 22 (any orbit), four classes | 434 | 254/72/64/44 | -0.002 [-0.007, +0.002] (-0.1%) | -0.003 [-0.006, -0.000] (-0.2%) | +0.003 [-0.018, +0.025] (+0.2%) |  |
| NHATS and H >= 24, dark | 25 | 18/7 | -0.064 [-0.178, +0.023] (-7.3%) | -0.033 [-0.090, +0.007] (-3.8%) | -0.018 [-0.147, +0.090] (-2.0%) | 0.47 / 0.30 |
| NHATS and H >= 24, S/Q vs rest | 112 | 58/54 | -0.008 [-0.022, +0.002] (-0.8%) | -0.012 [-0.033, +0.004] (-1.2%) | -0.015 [-0.047, +0.018] (-1.5%) | 0.49 / 0.53 |
| NHATS and H >= 24, four classes | 105 | 52/15/26/12 | -0.012 [-0.029, -0.000] (-0.7%) | -0.009 [-0.023, +0.001] (-0.5%) | +0.001 [-0.061, +0.063] (+0.1%) |  |

### Table E. Permutation nulls (300 shuffles; trained inside the subset; skill in bits)

| Subset, label | n | Contrast | Observed | Null mean | Null 95th pct | p |
|---|---|---|---|---|---|---|
| dark.box | 98 | lr_orb vs freq | -0.0036 | -0.0125 | +0.0101 | 0.316 |
| dark.box | 98 | gbt_orb vs freq | -0.0617 | -0.0346 | +0.0228 | 0.807 |
| dark.box | 98 | lr_orbH vs lr_H | +0.0009 | -0.0018 | +0.0172 | 0.472 |
| dark.box | 98 | gbt_orbH vs gbt_H | -0.0230 | -0.0008 | +0.0582 | 0.734 |
| dark.box | 98 | lr_orbH vs Hbin | +0.0303 | +0.0335 | +0.0615 | 0.601 |
| dark.nhats | 169 | lr_orb vs freq | -0.0025 | -0.0052 | +0.0031 | 0.409 |
| dark.nhats | 169 | gbt_orb vs freq | -0.0606 | -0.0259 | +0.0146 | 0.950 |
| dark.nhats | 169 | lr_orbH vs lr_H | +0.0056 | -0.0017 | +0.0099 | 0.146 |
| dark.nhats | 169 | gbt_orbH vs gbt_H | -0.0289 | +0.0150 | +0.0609 | 0.987 |
| dark.nhats | 169 | lr_orbH vs Hbin | +0.0132 | +0.0120 | +0.0292 | 0.452 |
| sq.box | 156 | lr_orb vs freq | -0.0023 | -0.0096 | +0.0015 | 0.252 |
| sq.box | 156 | gbt_orb vs freq | -0.0531 | -0.0305 | +0.0116 | 0.781 |
| sq.box | 156 | lr_orbH vs lr_H | -0.0024 | -0.0064 | +0.0021 | 0.445 |
| sq.box | 156 | gbt_orbH vs gbt_H | -0.0103 | -0.0147 | +0.0356 | 0.382 |
| sq.box | 156 | lr_orbH vs Hbin | +0.0066 | +0.0025 | +0.0201 | 0.415 |
| sq.nhats | 278 | lr_orb vs freq | -0.0070 | -0.0039 | +0.0015 | 0.771 |
| sq.nhats | 278 | gbt_orb vs freq | -0.0429 | -0.0256 | -0.0061 | 0.944 |
| sq.nhats | 278 | lr_orbH vs lr_H | -0.0047 | -0.0026 | +0.0046 | 0.728 |
| sq.nhats | 278 | gbt_orbH vs gbt_H | +0.0235 | +0.0016 | +0.0211 | 0.043 |
| sq.nhats | 278 | lr_orbH vs Hbin | +0.0075 | +0.0033 | +0.0138 | 0.236 |
| tax4.box | 150 | lr_orb vs freq | -0.0073 | -0.0055 | +0.0082 | 0.668 |
| tax4.box | 150 | gbt_orb vs freq | -0.1436 | -0.1135 | -0.0360 | 0.708 |
| tax4.box | 150 | lr_orbH vs lr_H | -0.0054 | -0.0016 | +0.0087 | 0.764 |
| tax4.box | 150 | gbt_orbH vs gbt_H | -0.0498 | -0.0297 | +0.0494 | 0.661 |
| tax4.box | 150 | lr_orbH vs Hbin | +0.0221 | +0.0418 | +0.0670 | 0.917 |
| tax4.nhats | 266 | lr_orb vs freq | -0.0072 | -0.0035 | +0.0030 | 0.870 |
| tax4.nhats | 266 | gbt_orb vs freq | -0.0521 | -0.0757 | -0.0453 | 0.133 |
| tax4.nhats | 266 | lr_orbH vs lr_H | -0.0049 | -0.0006 | +0.0079 | 0.860 |
| tax4.nhats | 266 | gbt_orbH vs gbt_H | -0.0131 | -0.0154 | +0.0232 | 0.429 |
| tax4.nhats | 266 | lr_orbH vs Hbin | +0.0231 | +0.0243 | +0.0410 | 0.545 |

All permutation tests: 54 contrasts, 1 with p < 0.05, smallest p = 0.043.

### Table F. Injection-recovery (synthetic labels on the real orbits; mean log-loss skill of the orbit-only model and the share of 40 trials whose 95% interval excludes zero)

| Subset, label prevalence | n | Injected pattern | Injected information (bits) | Oracle skill | Logistic: mean skill, detected | k-NN | Trees |
|---|---|---|---|---|---|---|---|
| dark.a2 (16% positive) | 2088 | smooth in a | 0.00 | -0.000 | -0.001, 0% | -0.004, 0% | -0.004, 0% |
| dark.a2 (16% positive) | 2088 | smooth in a | 0.01 | +0.010 | +0.008, 70% | +0.005, 18% | +0.002, 5% |
| dark.a2 (16% positive) | 2088 | smooth in a | 0.02 | +0.020 | +0.018, 98% | +0.014, 88% | +0.010, 48% |
| dark.a2 (16% positive) | 2088 | smooth in a | 0.05 | +0.053 | +0.051, 100% | +0.043, 100% | +0.039, 100% |
| dark.a2 (16% positive) | 2088 | smooth in a | 0.10 | +0.100 | +0.098, 100% | +0.086, 100% | +0.085, 100% |
| dark.a2 (16% positive) | 2088 | low e low i corner | 0.00 | -0.000 | -0.001, 0% | -0.005, 0% | -0.004, 0% |
| dark.a2 (16% positive) | 2088 | low e low i corner | 0.01 | +0.009 | +0.002, 12% | +0.001, 2% | -0.000, 2% |
| dark.a2 (16% positive) | 2088 | low e low i corner | 0.02 | +0.018 | +0.005, 28% | +0.006, 28% | +0.007, 40% |
| dark.a2 (16% positive) | 2088 | low e low i corner | 0.05 | +0.049 | +0.020, 98% | +0.025, 98% | +0.035, 100% |
| dark.a2 (16% positive) | 2088 | low e low i corner | 0.10 | +0.103 | +0.046, 100% | +0.060, 100% | +0.088, 100% |
| dark.box (17% positive) | 98 | smooth in a | 0.00 | -0.004 | -0.015, 0% | -0.039, 0% | -0.038, 0% |
| dark.box (17% positive) | 98 | smooth in a | 0.01 | +0.004 | -0.009, 0% | -0.036, 0% | -0.031, 0% |
| dark.box (17% positive) | 98 | smooth in a | 0.02 | +0.012 | -0.003, 0% | -0.028, 0% | -0.017, 2% |
| dark.box (17% positive) | 98 | smooth in a | 0.05 | +0.044 | +0.017, 12% | -0.007, 0% | +0.001, 0% |
| dark.box (17% positive) | 98 | smooth in a | 0.10 | +0.097 | +0.052, 12% | +0.037, 12% | +0.039, 12% |
| dark.box (17% positive) | 98 | low e low i corner | 0.00 | -0.006 | -0.012, 0% | -0.037, 0% | -0.049, 0% |
| dark.box (17% positive) | 98 | low e low i corner | 0.01 | +0.006 | -0.014, 0% | -0.038, 0% | -0.027, 0% |
| dark.box (17% positive) | 98 | low e low i corner | 0.02 | +0.007 | -0.009, 0% | -0.037, 0% | -0.020, 0% |
| dark.box (17% positive) | 98 | low e low i corner | 0.05 | +0.048 | -0.015, 0% | -0.024, 2% | -0.005, 2% |
| dark.box (17% positive) | 98 | low e low i corner | 0.10 | +0.093 | -0.002, 5% | +0.007, 8% | +0.034, 12% |
| dark.nhats (21% positive) | 169 | smooth in a | 0.00 | -0.004 | -0.005, 0% | -0.026, 0% | -0.030, 0% |
| dark.nhats (21% positive) | 169 | smooth in a | 0.01 | +0.006 | -0.003, 0% | -0.018, 0% | -0.024, 0% |
| dark.nhats (21% positive) | 169 | smooth in a | 0.02 | +0.015 | -0.000, 0% | -0.008, 0% | -0.014, 2% |
| dark.nhats (21% positive) | 169 | smooth in a | 0.05 | +0.047 | +0.028, 8% | +0.009, 2% | +0.009, 5% |
| dark.nhats (21% positive) | 169 | smooth in a | 0.10 | +0.104 | +0.076, 48% | +0.064, 50% | +0.069, 45% |
| dark.nhats (21% positive) | 169 | low e low i corner | 0.00 | -0.004 | -0.007, 0% | -0.022, 0% | -0.027, 0% |
| dark.nhats (21% positive) | 169 | low e low i corner | 0.01 | +0.005 | -0.010, 0% | -0.023, 0% | -0.028, 0% |
| dark.nhats (21% positive) | 169 | low e low i corner | 0.02 | +0.014 | -0.004, 0% | -0.018, 0% | -0.022, 0% |
| dark.nhats (21% positive) | 169 | low e low i corner | 0.05 | +0.048 | +0.000, 0% | -0.008, 0% | +0.007, 10% |
| dark.nhats (21% positive) | 169 | low e low i corner | 0.10 | +0.099 | +0.013, 0% | +0.006, 2% | +0.045, 25% |
| sq.a2 (61% positive) | 1713 | smooth in a | 0.00 | -0.000 | -0.001, 0% | -0.004, 0% | -0.005, 0% |
| sq.a2 (61% positive) | 1713 | smooth in a | 0.01 | +0.009 | +0.007, 42% | +0.004, 10% | -0.000, 5% |
| sq.a2 (61% positive) | 1713 | smooth in a | 0.02 | +0.021 | +0.020, 98% | +0.016, 85% | +0.010, 42% |
| sq.a2 (61% positive) | 1713 | smooth in a | 0.05 | +0.048 | +0.045, 100% | +0.039, 100% | +0.034, 100% |
| sq.a2 (61% positive) | 1713 | smooth in a | 0.10 | +0.097 | +0.095, 100% | +0.086, 100% | +0.081, 100% |
| sq.a2 (61% positive) | 1713 | low e low i corner | 0.00 | -0.000 | -0.000, 0% | -0.004, 0% | -0.004, 0% |
| sq.a2 (61% positive) | 1713 | low e low i corner | 0.01 | +0.011 | +0.001, 5% | +0.001, 0% | -0.001, 0% |
| sq.a2 (61% positive) | 1713 | low e low i corner | 0.02 | +0.019 | +0.004, 12% | +0.006, 35% | +0.006, 22% |
| sq.a2 (61% positive) | 1713 | low e low i corner | 0.05 | +0.050 | +0.014, 88% | +0.022, 100% | +0.031, 98% |
| sq.a2 (61% positive) | 1713 | low e low i corner | 0.10 | +0.100 | +0.028, 100% | +0.050, 100% | +0.077, 100% |
| sq.box (59% positive) | 156 | smooth in a | 0.00 | -0.003 | -0.010, 0% | -0.022, 0% | -0.032, 0% |
| sq.box (59% positive) | 156 | smooth in a | 0.01 | +0.004 | -0.009, 0% | -0.018, 0% | -0.027, 0% |
| sq.box (59% positive) | 156 | smooth in a | 0.02 | +0.019 | +0.005, 2% | -0.004, 2% | -0.009, 0% |
| sq.box (59% positive) | 156 | smooth in a | 0.05 | +0.046 | +0.016, 0% | +0.012, 2% | +0.007, 5% |
| sq.box (59% positive) | 156 | smooth in a | 0.10 | +0.106 | +0.081, 45% | +0.063, 45% | +0.063, 40% |
| sq.box (59% positive) | 156 | low e low i corner | 0.00 | -0.003 | -0.010, 0% | -0.024, 0% | -0.040, 0% |
| sq.box (59% positive) | 156 | low e low i corner | 0.01 | +0.006 | -0.008, 0% | -0.019, 0% | -0.038, 0% |
| sq.box (59% positive) | 156 | low e low i corner | 0.02 | +0.014 | -0.009, 0% | -0.016, 0% | -0.024, 0% |
| sq.box (59% positive) | 156 | low e low i corner | 0.05 | +0.046 | -0.003, 0% | -0.008, 0% | -0.007, 8% |
| sq.box (59% positive) | 156 | low e low i corner | 0.10 | +0.094 | -0.001, 0% | -0.003, 0% | +0.020, 10% |
| sq.nhats (55% positive) | 278 | smooth in a | 0.00 | -0.002 | -0.004, 0% | -0.020, 0% | -0.026, 0% |
| sq.nhats (55% positive) | 278 | smooth in a | 0.01 | +0.009 | +0.001, 0% | -0.007, 0% | -0.022, 0% |
| sq.nhats (55% positive) | 278 | smooth in a | 0.02 | +0.020 | +0.013, 5% | +0.003, 10% | -0.013, 0% |
| sq.nhats (55% positive) | 278 | smooth in a | 0.05 | +0.046 | +0.033, 28% | +0.021, 15% | -0.002, 0% |
| sq.nhats (55% positive) | 278 | smooth in a | 0.10 | +0.100 | +0.084, 88% | +0.072, 92% | +0.044, 18% |
| sq.nhats (55% positive) | 278 | low e low i corner | 0.00 | -0.001 | -0.003, 0% | -0.018, 0% | -0.027, 0% |
| sq.nhats (55% positive) | 278 | low e low i corner | 0.01 | +0.006 | -0.004, 0% | -0.019, 0% | -0.025, 0% |
| sq.nhats (55% positive) | 278 | low e low i corner | 0.02 | +0.015 | +0.001, 0% | -0.010, 0% | -0.017, 0% |
| sq.nhats (55% positive) | 278 | low e low i corner | 0.05 | +0.043 | +0.003, 2% | -0.001, 0% | -0.011, 2% |
| sq.nhats (55% positive) | 278 | low e low i corner | 0.10 | +0.097 | +0.019, 18% | +0.023, 18% | +0.019, 5% |

Contrast names in Table E: `lr` = logistic regression, `gbt` = boosted trees; `orb` = orbit only, `orbH` = orbit plus H, `H` = H only; `freq` = class frequency, `Hbin` = H-binned frequency.
