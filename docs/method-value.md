# Method 0.1: the price tag and the ladder

Proposals until Adam freezes them. After that no number changes; a change is a new method version.

- Constants: `method/v0_1/value.toml` (what is in the rock) and `method/v0_1/ladder.toml` (the five rungs).
- Evidence: `docs/research/value-inputs.md` and `capability.md`, as corrected by `verify-value-inputs.md` and `verify-capability.md` (check date 2026-11-21). Section 11 lists each correction and where it landed. One is applied only in part: the mix of metals in irons (section 5).
- Every derived number is printed by a script. `tests/test_method_value.py` fails if a file and a script disagree.

```
uv run python tools/value_inputs.py            # grades, prices, caps, spin limits, the record's arithmetic
uv run python tools/value_examples.py          # single-draw checks, the three worked examples, section 7's table
uv run python tools/value_examples.py --toml   # sections 10 and 11 of value.toml, printed
uv run python tools/value_examples.py --write  # the same, written into value.toml
uv run python -I tools/method_check.py         # the checker's own recomputation, sharing no code with the two above
uv run python -m unittest tests.test_method_value
```

`tools/value_examples.py` is the reference implementation: `longshot/value.py`, fed the same draws, must give the same figures.

## 1. What is counted

| Row | Counted | Not counted |
|---|---|---|
| Metal | The six platinum-group metals (platinum, palladium, rhodium, iridium, ruthenium, osmium) held in grains of iron-nickel metal, in kilograms. Dollars for five of them; osmium has no list price. | Platinum-group metal spread through dark clay-rich rock (2.9–4.0 ppm in CI and CM meteorites), bright enstatite rock or basalt. Nickel, cobalt, iron. |
| Water | Water bound in clay minerals, in tonnes. No dollars. | Ice. Hydrogen in organic matter. |

Every figure is for the whole body, in the rock, before any cost. Nothing is subtracted for digging, refining or the trip home, and no buyer is assumed.

The block is headed "Price tag", Adam's word. No sentence says "worth" or "value". No mean, median or expected value is computed or exported.

Do not conclude:

- That "no platinum-group metal in metal grains" means none in the rock. With dark rock counted the report's chance of none fell from 43% to 17%.
- That a figure here is recoverable. It is an upper bound on what a perfect process could separate.

## 2. Material by class and reflectivity

The joint draw gives each case a class (S, C, X, other), a reflectivity, a size and a density. Material follows class and reflectivity band. The bands are Tholen's: dark under 0.10, bright from 0.30 (as quoted by Moskovitz et al. 2026).

| Class | Band | Material | Share: low, central, high |
|---|---|---|---|
| S | any | H, L, LL chondrite | 0.25, 0.35, 0.40 of the class, fixed |
| C | dark | dark clay-rich rock; hydrated | 0.30, 0.50, 0.77 hydrated |
| C | mid, bright | nothing counted | – |
| X | dark | dark clay-rich rock; hydrated | 0.30 hydrated, fixed |
| X | mid | iron-rich; the rest enstatite chondrite | 0.10, 0.38, 0.60 iron-rich |
| X | bright | nothing counted (enstatite achondrite) | – |
| other | dark | dark clay-rich rock; hydrated | 0.30 hydrated, fixed |
| other | mid, bright | L-chondrite grade; the rest nothing counted | 0, 0.25, 0.50 with metal grains |

Sources:

- S split: between the mix among falls and the mix among kilometre-scale asteroids (`value-inputs.md` 5.2). Weak. LL-heavy, which lowers the grade.
- Hydrated share of dark C: 30 ± 5% show the 0.7 µm band (Rivkin 2012, in Rivkin & DeMeo 2019); 17 of 22 show the 2.7 µm band (Usui et al. 2019). Hydrated classes are dark: Ch median reflectivity 0.056 (163 objects), Cgh 0.065 (Mainzer et al. 2011, Table 1).
- Iron-rich share of mid-band X: 11 of 29 main-belt M-class asteroids are metal-dominated by radar (Shepard et al. 2015). Those are tens of kilometres across; 0.10–0.60 is the range the checker tested. Cross-check: irons are 4.4% of meteorite falls (49 of 1,102).
- "Other": of 205 near-Earth asteroids with a < 2 au, 43% are V or A (differentiated), 44% K, L or R (chondritic; whether the metal sits in grains is not known), 13% D, T or Z (dark).

Left out:

- A wrong class label. Colour and spectral surveys disagree on S/Q against the rest for 21% of 874 shared objects, and on four classes for 33% (`verify-prior-null.md`). An entry with a measured class prints the first figure.
- A C-class case that is not dark. Colour-based classes disagree with spectra for a third of shared objects, and 60% of the Spitzer C-types classed from a spectrum are dark against 19% of those classed from colours, so these count as holding neither metal grains nor water. If some are hydrated, the count holding no water is too high.
- Any change of the class mix with size beyond what the joint draw holds.

## 3. Grades

Grams of the six metals per tonne of rock, flat between the lowest and highest meteorite of each group in Horan et al. 2003, Table 1. Rhodium was not measured there; it is added at 0.30 × iridium.

| Material | ppm | Analyses | Note |
|---|---|---|---|
| H chondrite | 3.32–6.29 | 10 of 9 meteorites | Was 5.2–5.6 from three of the nine. One Rose City aliquot with no osmium value is left out. |
| L chondrite | 3.03–4.40 | 3 of 2 | Both heavily shocked; Chico is about 60% impact melt. |
| LL chondrite | 1.93–2.32 | 3 of 2 | Both unequilibrated type 3. |
| Enstatite chondrite | 1.84–5.47 | 11 of 9 | |
| Dark clay-rich rock | 2.92–3.95, not counted | 6 of 5 | Not in metal grains. |
| Iron-rich | table below × metal fraction 0.5–1.0 | | 1986 DA is about 85% metal; mesosiderites about half. |

Iron meteorites, total of six metals, 100% metal (Cannon, Gialich & Acain 2023, Table 2; ends from the text):

| Share of irons below | 0 | 10% | 20% | 30% | 40% | 50% | 60% | 70% | 80% | 90% | 100% |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ppm | 6 | 14.70 | 20.75 | 27.05 | 34.77 | 40.78 | 52.88 | 63.48 | 91.23 | 107.86 | 230 |

Left out:

- The spread inside a chondrite group. Two to nine meteorites set each range.
- What the atmosphere removes. Weak dark material is under-represented among meteorites and iron over-represented.
- Any link between grade and density.

Do not conclude:

- That an iron-rich asteroid has an iron meteorite's grade. Cannon et al.: the figures "should be interpreted as upper values because they represent 100% metal content", and there is "no known way to remotely identify" where a body falls.

## 4. Water

Water if hydrated: flat between 1.9% and 10.5% by weight, the range of indigenous water in CM chondrites (Lee et al. 2023). Inside it: Ryugu's sample, 6.84 ± 0.34% (Yokoyama et al. 2023); Bennu's, at most 7.5–8.5% if all its 0.84–0.95% hydrogen were water (Lauretta et al. 2024).

A case holds bound water only if its drawn reflectivity is under 0.10.

Left out:

- Ivuna's 12.73%: half of it is interlayer water, part of it picked up on Earth.
- 20% (Elvis 2014): no sample supports it.
- Dollars. Every published price found is for propellant, not water, in business cases from 2014 to 2020; one tonne of propellant takes about 1.5 tonnes of water (Kutter 2016). No buyer has restated any of them.

For scale: the space station received 3.3 t of water in a year (2011–12).

## 5. Prices

USGS Mineral Commodity Summaries 2026: yearly average list prices for 2021–2025 (2025 is an estimate). A lower bound uses each metal's lowest year, an upper bound its highest.

| Metal | Lowest year, $/troy oz | Highest year, $/troy oz | $/kg, low–high |
|---|---|---|---|
| Platinum | 960.70 (2024) | 1,200 (2025) | 30,887–38,581 |
| Palladium | 994.90 (2024) | 2,419.18 (2021) | 31,987–77,778 |
| Rhodium | 4,660.44 (2024) | 20,254.10 (2021) | 149,837–651,184 |
| Iridium | 4,400 (2025) | 5,158.40 (2021) | 141,463–165,846 |
| Ruthenium | 451.02 (2024) | 690 (2025) | 14,501–22,184 |
| Osmium | no list price | | kilograms only; 16% of the mass |

A kilogram of the six metals in ordinary-chondrite proportions is $43,314–$79,162.

Why not one day's quote: on 20 November 2026 platinum moved 3.5% between the dealer's 10am quote and the close, and stood 54% below its January record of $2,923. At that day's quotes the same kilogram is $88,289, 1.12 times the top of the band; iridium stood at twice its highest yearly average.

About three fifths of each dollar figure is iridium and rhodium. The world's mines supply about 7 and 22 tonnes of them a year.

**Iron.** The paper that gives the iron grades says chondritic proportions fail for irons: "Ru, Rh, and Pt roll over at higher Ir values … Pd is inversely correlated with Ir." It gives the real mix as a chart and a supplementary table that is not on disk, so the mix is bracketed by two mixes chosen here:

| End | Mix | $/kg |
|---|---|---|
| Low | no iridium, osmium or rhodium; platinum, ruthenium, palladium in CI proportions | 26,206 at the low prices |
| High | iridium 26%, as in Avce (59.5 of about 230 ppm), the richest iron the paper supports | 80,353 at the high prices |

The two mixes are a judgement, not the extremes of measured irons. Iridium at 26% with rhodium at its chondritic ratio to iridium is $111,095 per kg at the high prices, 1.38 times the high mix; platinum and ruthenium alone are $24,201 at the low prices, 0.92 times the low mix.

The checker asked for one of two things before a metal-rich dollar figure is shown: the mix fixed from that supplementary table, or the branch in kilograms only (`verify-value-inputs.md` section 4, objection 8). Neither is done. The iron-rich sentence leads with kilograms and says its dollars rest on an assumed mix. Open for Adam: kilograms only until the table is read.

Left out:

- Any effect of a sale on the price, beyond the cap in section 6.
- Prices after 2025. The band does not hold 20 November 2026.

## 6. Market rule

Each metal is priced only up to a tenth of one year's world mine supply (2025, IPA factsheets). Beyond that it counts as kilograms and no dollars, and the entry prints "Dollars count each metal only up to a tenth of a year's world mine supply."

| Metal | Mine supply, t | Cap, kg |
|---|---|---|
| Platinum | 178 | 17,800 |
| Palladium | 197 | 19,700 |
| Rhodium | 22 | 2,200 |
| Iridium | 7 | 700 |
| Ruthenium | 30 | 3,000 |

All five caps together: $1.65–3.83 billion. Iridium's is reached first: by an H-chondrite body above about 84 m, or an iron-rich one above about 33–42 m.

This is a choice, not a finding. The published alternative, Kargel's rule p′ = p (P′/P)^−0.60 as used by Sanchez et al. 2021, never stops adding dollars; the cap is the lower of the two.

## 7. Three scenarios, and where the placeholder inputs went

Each figure is computed three ways with the same random numbers. A lower bound ("over") uses low; an upper bound ("under") uses high; central is used only for the chance of nothing.

| | Low | Central | High |
|---|---|---|---|
| Iron-rich share of mid-band X | 0.10 | 0.38 | 0.60 |
| Metal grains in K, L, R ("other") | none | half | all |
| Hydrated share of dark C | 0.30 | 0.50 | 0.77 |
| Prices | lowest year | – | highest year |
| Metal mix in iron | no iridium | – | iridium 26% |
| Size from brightness | 3 times smaller | as drawn | as drawn |

The checker named three inputs as placeholders outside the printed ranges. Where each went:

- **Metal-rich share.** A range, 0.10–0.60. The count of iron-rich bodies prints as a band.
- **Dark-object reflectivity.** No fixed value. A case holds water only if its own drawn reflectivity is under 0.10, and that reflectivity sets its size. Of the two candidates, 0.05 falls inside the band and 0.13 outside it.
- **The size rule.** Sizes come from the joint draw (measured reflectivities, tied to class; `docs/method.md` section 1). Every lower bound from a brightness-based size also allows for a body 3 times smaller: both small targets measured since came out 2–3 times smaller than the working size (`docs/plan.md` 1.2), and the plan's one-size-rule alternative cuts water twelve to twenty times, a factor of 0.37–0.44 in diameter.

The checker's alternatives against this method, for H 26.2 (kilograms are the checker's dollars at $87,945 per kg):

| | Checker | This method |
|---|---|---|
| Three in four hold under | 23 kg | 20 kg |
| Nineteen in twenty hold under | 91 kg | 93 kg |
| Iron-rich, of 100 | 0.7, 2.8, 4.4 at shares 0.10, 0.38, 0.60 | 0.7 to 4.0 |
| Iron-rich bodies hold | 100–3,800 kg | 2.9–3,000 kg |
| Water, if any, as printed | 331–11,100 t | 13–7,800 t |
| Water, dark reflectivity 0.13 | 80–2,740 t | inside |
| Water, the plan's size rule | 16–1,670 t | inside |

Not inside: the top of the as-printed water range (this method's top is 0.70 of it; that model let water pass 13% by weight). The 5th–95th range of metal among bodies holding some is not exported: its top sits where ordinary and iron-rich bodies meet, so it moves with the class shares (186 kg here against 398 kg in the checker's 60% case, which used 23% X where the joint draw has 17.5%).

## 8. What an entry prints

One denominator: 100 asteroids like this one. The chance of nothing comes first. Metal figures count the zeros.

| Order | Sentence | Printed when |
|---|---|---|
| 1 | Of 100 like it, {n} hold no platinum-group metal in metal grains. | always. A measured class leaves a chance of nothing, because a label can be wrong and that rate is in the draws (`docs/method.md` section 3) |
| 2 | Counting those, three in four hold under {kg} ({$}) and nineteen in twenty under {kg} ({$}), in the rock, before any cost, at each metal's highest yearly average list price of 2021–2025. | the upper figure is above zero |
| 3 | Three in four hold over {kg} ({$}) and nineteen in twenty over {kg} ({$}), in the rock, before any cost, at each metal's lowest yearly average list price of 2021–2025, if it is no more than 3 times smaller than its brightness suggests. | fewer than 25 in 100 hold nothing; the nineteen-in-twenty half only when fewer than 5 in 100 do, which no labelled class reaches |
| 4 | {n} of the 100 would be iron-rich and hold {kg} ({$}). No observation from Earth tells which, and the dollar figures rest on an assumed mix of metals in irons. | at least 1 in 200 |
| 5 | Dollars count each metal only up to a tenth of a year's world mine supply. | the cap changes a printed figure by more than 5% |
| 6 | Of 100 like it, {n} hold no water bound in minerals. | always |
| 7 | Nine in ten of the rest hold {t}. | at least 20 draws hold water |
| 8 | As of 21 November 2026 we found nobody buying water in orbit. | always |

Figures print to one significant figure, two when the first digit is 1 or 2. An "under" figure rounds up and an "over" figure rounds down. A count is a band when its low and high scenarios differ. A dollar range whose low end is under $1,000 beside a high end in thousands or more prints both in figures, "$40 to $160,000": "$40 to $160 thousand" reads as forty thousand. One tonne is "1 tonne".

An asteroid a spacecraft brought a sample back from prints none of the sentences above. In their place: for Ryugu, "If the whole body matches the returned sample, it holds {t} of water", from the sample's 6.84 ± 0.34% and the mass range; for Bennu, the same as an upper limit, "and all its hydrogen is in water", from 0.84 to 0.95% hydrogen; for Itokawa, "No analysis of the returned sample is on file here, so no figure is given." The fourth rung prints the analysis itself. A body that no longer exists (2008 TC3) has no block.

The six uniform numbers are seeded as the joint draws were: by the object key, or, when nothing about the rock is measured, by its H and H error. Two unobserved asteroids of the same brightness print the same sentences.

Exports (`value.toml` section 7): `metal {p_nothing, p_nothing_lo, p_nothing_hi, kg {q05, q25, q75, q95}, usd {q05, q25, q75, q95}, capped}`, `iron_rich {p_lo, p_hi, kg {q05, q95}, usd {q05, q95}}`, `water {p_nothing, p_nothing_lo, p_nothing_hi, tonnes {q05, q95}}`, `basis`, `statements`, `statement_ids`. Metal quantiles are over all cases; `q05` and `q25` are 0 when more than 5 or 25 in 100 hold nothing. Water tonnes are over the cases with water.

Do not conclude:

- That the upper figure is what the asteroid holds. It is a bound nineteen cases in twenty stay under, at the highest prices of five years.
- That a wider range after an observation is an error. An X-type spectrum widens it: two unlike materials share the class.
- That an observation from Earth can make the range narrow. An S-type with a size good to 10% still spans a factor of 5 in kilograms and 10 in dollars: grade cannot be sensed remotely and no density is measured at this size.

## 9. Worked examples

Draws: a stand-in for the pipeline's joint draw (`value.toml` section 9, constants copied from `priors.toml` on 2026-11-25), 200,000 per example. The pipeline's figures for an object of this brightness differ by its random numbers and by JPL's stated error on that object's H.

### 9.1 H 26.2, nothing else measured

Sizes 8.9–33.5 m (5%–95%); 788–34,187 t. Classes: S 57.5%, C 13.8%, X 17.5%, other 11.2%.

One stony case by hand (check `example_1_stony`): reflectivity 0.273 gives 1,329,000 × 10^(−26.2/5) / √0.273 = 14.64 m; (π/6) × 14.64³ × 2,550 / 1000 = 4,189.5 t; H chondrite at 4.805 ppm holds 20.131 kg; at the high prices $1,594,032. In the low scenario the same case is 3 times smaller: 155.1 t, 0.745 kg, $32,285.

One dark case (check `example_1_dark`): reflectivity 0.05 gives 34.2 m; at 1,600 kg/m³, 33,511.7 t; hydrated at 6.2% holds 2,077.7 t of water; 3 times smaller, 76.9 t.

| | Low | Central | High |
|---|---|---|---|
| Hold no metal in grains | 35.9% | 33.3% | 30.5% |
| Metal, 75th and 95th of all cases | | | 20.10 kg, $1,591,768; 91.47 kg, $7,254,743 |
| Iron-rich | 0.66% | | 3.91% |
| Iron-rich bodies hold | 2.8 kg, $73,910 (5th) | | 2,912 kg, $224,508,424 (95th) |
| Hold no water | 97.0% | 95.9% | 94.3% |
| Water, if any | 12.6 t (5th) | | 7,916 t (95th) |

> Of 100 like it, 31 to 36 hold no platinum-group metal in metal grains.
> Counting those, three in four hold under 21 kg ($1.6 million) and nineteen in twenty under 100 kg ($8 million), in the rock, before any cost, at each metal's highest yearly average list price of 2021–2025.
> 1 to 4 of the 100 would be iron-rich and hold 2.8 kg to 3 tonnes ($70 thousand to $230 million). No observation from Earth tells which, and the dollar figures rest on an assumed mix of metals in irons.
> Of 100 like it, 94 to 97 hold no water bound in minerals.
> Nine in ten of the rest hold 12 to 8,000 tonnes.
> As of 21 November 2026 we found nobody buying water in orbit.

### 9.2 The same after a spectrum says S-type

A class is a label, and a label from a spectrum is taken as wrong, on S/Q against the rest, in 12.5 of 100 draws (`priors.toml` `[class.label_error]`; 21 of 100 for a label from colours). Those draws take a class from the other side. Classes: S 87.5%, C 3.5%, X 5.0%, other 4.0%. Reflectivity for the S draws is from the 286 spectrally classed S-types, whose median H is 18.4; at most 2 of them are fainter than H 24. Sizes 9.6–23.5 m; 1,064–17,206 t.

| | Low | Central | High |
|---|---|---|---|
| Hold no metal in grains | 10.0% | 9.0% | 8.0% |
| Metal, 25th of all cases | 0.21 kg, $8,966 | | |
| Metal, 75th and 95th | | | 22.93 kg, $1,815,823; 62.95 kg, $4,986,055 |
| Iron-rich | 0.25% | | 1.49% |
| Hold no water | 99.6% | 99.5% | 99.3% |
| Water, if any | 13.3 t (5th) | | 8,715 t (95th) |

> Of 100 like it, 8 to 10 hold no platinum-group metal in metal grains.
> Counting those, three in four hold under 23 kg ($1.9 million) and nineteen in twenty under 70 kg ($5 million), in the rock, before any cost, at each metal's highest yearly average list price of 2021–2025.
> Three in four hold over 200 g ($8 thousand), in the rock, before any cost, at each metal's lowest yearly average list price of 2021–2025, if it is no more than 3 times smaller than its brightness suggests.
> Up to 1 of the 100 would be iron-rich and hold 2.4 kg to 2.7 tonnes ($60 thousand to $220 million). No observation from Earth tells which, and the dollar figures rest on an assumed mix of metals in irons.
> Of 100 like it, 99 or more hold no water bound in minerals.
> Nine in ten of the rest hold 13 to 9,000 tonnes.
> As of 21 November 2026 we found nobody buying water in orbit.

The spectrum cut the chance of nothing from about a third to about a tenth and lowered the upper bound from $8 million to $5 million. It did not remove the zero: more than 1 draw in 20 holds nothing, so no figure is given as a nineteen-in-twenty floor. Before the review of 2026-11-25 the class was taken as certain, and this example printed "nineteen in twenty over 110 g ($5 thousand)" beside a sentence saying surveys disagree on the class for 21 of 100 asteroids. What is left is the label, then size, then which chondrite group, then density. How far the bound falls depends on the S-types' reflectivities holding at this brightness, which is untested.

The iron-rich range rests on the mislabelled draws alone, about 1 in 80, so at 20,000 draws it moves by up to 35%.

### 9.3 H 22.7 with a measured size of 60 m, good to 30%

The shape of 2001 CQ36. Sizes 39.2–92.0 m; 61,806–1,012,323 t. Size and H together give the reflectivity (about 0.41), so the class draw leans bright: S 61.5%, C 16.9%, X 11.2%, other 10.5%.

One stony case (check `example_3_stony`): (π/6) × 60³ × 2,550 / 1000 = 288,398.2 t; at 4.805 ppm, 1,385.753 kg; $60,024,891 at the low prices and $109,730,534 at the high.

One iron-rich case (check `example_3_iron_rich`): 60 m at 4,500 kg/m³ is 508,938 t; 75% metal at 40.78 ppm holds 15,565.869 kg. At the high mix 4,047 kg of that is iridium against a cap of 700 kg, so dollars stop at $695,661,991.

| | Low | Central | High |
|---|---|---|---|
| Hold no metal in grains | 36.3% | 33.6% | 31.0% |
| Metal, 75th and 95th of all cases | | | 1,402.32 kg, $111,045,067; 3,750.80 kg, $296,684,059 |
| Iron-rich | 0.25% | | 1.33% |
| Iron-rich bodies hold | 7,391 kg, $193,683,105 (5th) | | 221,999 kg, $3,834,217,400 (95th, capped) |
| Hold no water | 99.7% | 99.5% | 99.3% |
| Water, if any | 16,292 t (5th) | | 165,576 t (95th) |

> Of 100 like it, 31 to 36 hold no platinum-group metal in metal grains.
> Counting those, three in four hold under 1.5 tonnes ($120 million) and nineteen in twenty under 4 tonnes ($300 million), in the rock, before any cost, at each metal's highest yearly average list price of 2021–2025.
> Up to 1 of the 100 would be iron-rich and hold 7 to 230 tonnes ($190 million to $4 billion). No observation from Earth tells which, and the dollar figures rest on an assumed mix of metals in irons.
> Dollars count each metal only up to a tenth of a year's world mine supply.
> Of 100 like it, 99 or more hold no water bound in minerals.
> Nine in ten of the rest hold 16,000 to 170,000 tonnes.
> As of 21 November 2026 we found nobody buying water in orbit.

The measured size moved the upper figures up 40 to 70 times against 9.1. The water cases are the few draws over about 120 m, the only ones dark enough at this brightness.

Agreement to expect from `value.py` on the same draws: at 20,000 draws, counts within 1 of 100 and other figures within 15% (35% for the iron-rich range of 9.2). At 2,000 draws the tail figures move by up to 30%.

## 10. The ladder

Five rungs, in `longshot/types.py` order. Each is measured, a prior, or unknown.

| Rung | States | Reads |
|---|---|---|
| Found again | code 5 or better; worse; no orbit code; gone. Then one sentence only when JPL's own test says the code is not enough: a window only a survey could use, or none through 2045 | orbit code, the orbit gate, the flag on JPL's next window |
| Reached | round trip on file; none. "Launch date not on file." | delta-v of the cheapest round trip |
| Workable | what the spin means for loose material: slow; near the limit; fast; a period graded unreliable; sources disagree across 2.2 h; not measured; limit only; not checked | the period the spin row rests on |
| Anything in it | sampled (the analysis); estimated from class and brightness; from its size, where that is measured and the class is not; from brightness alone; surface not checked | the surface and size rows, the returned sample |
| Brought back | done three times, by space agencies; not yet attempted; proposed | size range and spin against the record below |

A rung says what the rows above it do not. The orbit code's window, the trip's days, the size and mass ranges, the period and the price tag's sentences are each printed once, in their row or block; before the review of 2026-11-25 every entry printed at least one of them twice. Tianwen-2 is named on the second rung, with the source of the size: "at Kamoʻoalewa (18 ± 2 m, JWST)". The same 18 ± 2 m is on Kamoʻoalewa's own size row, from `registry/curated.toml`.

**Spin.** The outward pull at the equator of a sphere equals its gravity at a period of √(3π / (G × density)): 3.01 hours for rock of 1,200 kg/m³, 1.82 hours for 3,300 kg/m³. Faster than that the entry prints the ratio, (limit / period)², as a range: 15 to 40 for Kamoʻoalewa (27.9 minutes), 5,000 to 14,000 for 2022 OB5 (92.5 seconds).

**The last rung.** Size and spin classes against what has flown:

| Size range | Spin | Sentence opens |
|---|---|---|
| all of it 300 m or more | 4 hours or slower | Grams: done three times, by space agencies, on asteroids of this size and spin |
| all of it 300 m or more | not measured | Grams: done three times, by space agencies, on asteroids of this size that turn once in 4.3 to 12.1 hours |
| all of it 300 m or more | faster than 4 hours | Grams: not yet attempted on an asteroid that turns this fast |
| straddles 300 m | any | Grams: done three times … on asteroids 330 to 900 m across, and not yet attempted on a smaller one |
| top end 160–300 m | any | Grams: not yet attempted at this size |
| under 160 m | under 10 minutes | Grams: not yet attempted. As of 21 November 2026 we found no spacecraft that has approached an asteroid turning this fast |
| under 160 m | otherwise | Grams: not yet attempted. As of 21 November 2026 we found no spacecraft that has touched an asteroid this small |

Every entry then prints: "Kilograms or tonnes: proposed since the 1990s, first costed in 2012 at $2.6 billion (2012 dollars) for about 500 tonnes to lunar orbit, never built." Bennu, Ryugu and Itokawa print their own sample; Kamoʻoalewa prints Tianwen-2's status.

The 300 m, 4 hour, 160 m and 10 minute lines come from three sampled asteroids and one impact. They are judgement, not physical limits.

The record, as of 2026-11-21:

| Fact | What | Recheck |
|---|---|---|
| Hayabusa (JAXA), Itokawa, 330 m, 12.1 h | more than 1,500 particles, under a milligram; 2003–2010; about ¥20 billion, a press figure | 2027-11-21 |
| Hayabusa2 (JAXA), Ryugu, 896 m, 7.6 h | 5.424 ± 0.217 g; 2014–2020; ¥28.9 billion, a 2012 plan figure | 2027-11-21 |
| OSIRIS-REx (NASA), Bennu, 484 m, 4.3 h | 121.6 g; 2016–2023; $1.02–1.16 billion, about ten million dollars a gram in the money of the day | 2027-11-21 |
| Tianwen-2 (CNSA), Kamoʻoalewa, 18 m, 27.9 min | not yet attempted; one spacecraft is in position. Reached 20 km in July 2026; no sampling attempt reported and no official date for one | 2026-12-21, then monthly |
| DART (NASA), Dimorphos, 160 m | struck at about 6 km/s, 2022: the smallest body touched | 2027-11-21 |
| Companies | we found none that has reached an asteroid | 2027-03-31 |
| Sonter 1997–98 | 1,000 t to low Earth orbit, proposed | 2027-11-21 |
| Keck study 2012 | about 500 t to lunar orbit, $2.6 billion (2012 dollars): the first costed design, never started | 2027-11-21 |
| NASA Asteroid Redirect Mission | a boulder of up to 13.5 t, capped at $1.4 billion without launch or operations (2016), cancelled 2017 | 2027-11-21 |

One tonne is 8,000 times the largest sample. The two costed designs are 110,000 and 4 million times it.

Left out:

- When the cheapest round trip launches. JPL's bulk list gives delta-v and duration only; the rung says "Launch date not on file". A per-object call would give it: a gap for the next pull.
- Material handled at an asteroid and not returned. One company plans kilogram-scale excavation at Apophis after a mid-2028 launch; its pages state no return.
- Costs in one year's money. Each mission is given in its own currency and decade; no total is printed.

Do not conclude:

- That orbit code 5 or better means a telescope can be pointed at it. JPL's own test is the flag on the window, and the two disagree for some objects of code 4 to 6 (`verify-obs-window.md` section 1).
- That ten million dollars a gram is a cost of mining. It is a science mission's whole budget divided by a by-product.
- That "not yet attempted" means it cannot be done, or that "done" means it is routine: three missions, two with near-losses.
- That a statement beginning "we found no" is proof. It is a search, dated.

## 11. Corrections applied

From `verify-value-inputs.md`:

| Correction | Here |
|---|---|
| Irons are 4.4% of falls, not 2% | cross-check on the iron-rich share, section 2 |
| "Under 1 in 10, if the class is wrong" is unsupported | replaced by the measured 21 in 100 |
| Nickel and cobalt against 1% of launch cost | not carried; neither metal is counted |
| Launch ceiling of $1,500–3,300/kg | not carried; water has no dollars |
| H chondrites 5.2–5.6 ppm | 3.32–6.29, section 3 |
| X split 56/33/11 at fixed brightness | not carried; the split comes from each draw's reflectivity |
| Platinum record printed two ways | $2,923, spot, 26 January 2026 |
| "300 to 500 t a year", "the only published forecast" | not carried |
| Water tonnes multiplied by a propellant price | no dollars on water, section 4 |
| "Narrowed from a factor of 40 to 18" | not carried |
| "None, in the rock" for dark asteroids | the row is "in metal grains", section 1 |
| Iron priced at chondritic proportions | applied in part: two bracketing mixes chosen here, not the measured mix and not kilograms only (section 5) |
| One day's dealer quote as the price | five yearly averages, section 5 |
| Dark reflectivity 0.05 | no fixed value, section 7 |
| Metal-rich share a point | a range, section 7 |
| The 10% cap unstated as a choice | stated, with the alternative, section 6 |
| A fast spin raises density | dropped; spin changes nothing in the rock |
| 121.6 g "would fetch" 44 cents | "would contain 2 to 13 milligrams" (10th–90th percentile iron) |
| "Nine cases in ten" beside "2 in 5" | one denominator; one-sided sentences, section 8 |

From `verify-capability.md`:

| Correction | Here |
|---|---|
| OSIRIS-REx cost has two totals (row 4) | $1.02–1.16 billion; "about ten million dollars a gram" |
| Hayabusa's ¥20 billion is a press figure (row 7) | so labelled |
| The one-hour bar is Thirouin et al. 2016's (row 32) | so attributed; the paper's ratio for 2022 OB5 is not quoted |
| Odin was not "declared lost" (row 35) | the company's own words |
| "1,300 t is the largest any study designed for" (row 52) | "sized for 250 to 1,300 tonnes" |
| Sonter's 5 t is the plant, not the launch (row 56) | so noted |
| Refuelling demonstrations "moved to 2027" (row 68) | not carried; the ladder does not use it |
| "Designed on paper since 2012" (row 71, refuted) | "proposed since the 1990s, first costed in 2012" |
| "One is trying now", "under way" | "not yet attempted; one spacecraft is in position", dated |
| "127 grams for $1.4 billion" | no sum across currencies and decades |
| "Four orders of magnitude" | 8,000, 110,000 and 4 million times |
| "Not done at this size; method exists" | "not yet attempted at this size" |
| Point masses in the examples | ranges only |
| Universal negatives | "we found", with the date |

## 12. Check of 2026-11-25

`tools/method_check.py` recomputes all five files with no code shared with the scripts that wrote them; `tests/test_method_check.py` spoils each constant in turn and requires the check to fail. Reproduced without change: the reflectivity quantiles and the 0.71 size ratio from the Spitzer table, every unit conversion, every single-draw check, and all three worked examples at 200,000 draws.

Changed:

| File | Was | Now | Why |
|---|---|---|---|
| `missions.toml` | 1,300 t "is the largest mass any capture hardware has been sized for" | the top of one design's range; one study read | the claim `verify-capability.md` row 52 corrected, in other words |
| `missions.toml` | 2022 DC5: 30 m or wider "in every draw", 1.0 | 0.999 of draws | the grid stopped at 1.8 sigma in H; a million random draws give 0.999 |
| `missions.toml` | 2011 AA37 size 0.998; 2009 BD at 100 t 0.65; 2011 MD 63–817 t | 0.997; 0.64; 64–817 t | the same grid, now 121 steps in H |
| `missions.toml`, `method.md` | "No spacecraft has touched…", "Nothing has ever enclosed…" | "As of 21 November 2026 we found no…" | `verify-capability.md` objection 14 |
| `value.toml` | "Nobody buys water in orbit." | "As of 21 November 2026 we found nobody buying water in orbit." | the same objection; the space station's water is launched by its own agencies |
| `value.toml` | the iron mix "is bounded" | two bracketing mixes, a judgement; what lies outside them is printed | they are not the extremes of measured irons |
| `value.toml` | iron-rich sentence: "the dollar range is wide because the mix of metals in irons is not settled" | "the dollar figures rest on an assumed mix of metals in irons" | the range is wide mostly from size and grade; the mixes add a factor of 3 |
| `value.toml` | "a third of colour-based C labels disagree with spectra" | a third of shared objects, on four classes | the source gives no figure for C labels alone |
| `value.toml` | Z counted with V and A as differentiated (0.44, 0.44, 0.12) | Z counted with D and T as dark (0.43, 0.44, 0.13) | Z is the reddest primitive class; no share used in a draw moves |
| `value.toml` | iridium and rhodium "trade about 7 and 22 tonnes a year" | mines supply that much | the figures are mine supply |
| `value.toml` | worked examples without their inputs | `inputs` beside each | an example could not be recomputed from the file |
| `ladder.toml` | orbit code 5 or better: "good enough to point a telescope at"; worse: "a survey would have to find it again first"; "Next visible…" for any window | the code against the line of 5; one window sentence each for pointable, survey-only and none | JPL's pointing flag and the orbit code disagree for some objects of code 4 to 6 |
| `ladder.toml` | Tianwen-2's target period in minutes only | minutes and hours | every other fact is in hours |
| `priors.toml`, `method.md` | joint weights return the central shares "exactly" | to within 0.1 of a percentage point | solved on bin counts, drawn through 21 quantiles |
| `method.md` | | two more lines under Untested: fainter objects may reflect more; the 15% bound on C fainter than H 26 is unconfirmed | both were in the derivation and not in the document |

Not changed, and open for Adam: dollars on the iron-rich sentence (section 5); the fixed H, L, LL split, when the one survey of small stony asteroids found 8%, 31%, 61% (Sanchez et al. 2024, `source-prior.md`); the spin sentence on the workable rung prints one count where the prior is a range.
