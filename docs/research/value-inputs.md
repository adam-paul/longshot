# Value inputs: what an honest price range per asteroid needs

Research date: 2026-11-21 (a Saturday; the last trading day was Friday 20 November). Scope: concentrations, prices and market sizes, how earlier valuations were built, densities, and a recommended design for the price tag with three worked examples.

Status tags on every number:

- **[P]** primary source read today (the paper's own text, an agency or dealer page, the code itself).
- **[S]** secondary source read today (press report, a search-result summary, another paper quoting it, or one of this project's earlier reports).
- **[R]** recalled, not checked today.
- "(my calculation)" marks arithmetic I did from sourced inputs.

Terms used below: **PGM**, the six platinum-group metals (platinum Pt, palladium Pd, rhodium Rh, iridium Ir, ruthenium Ru, osmium Os). **ppm**, parts per million by mass, the same as grams per tonne. **Ordinary chondrite**, the commonest stony meteorite (groups H, L, LL by falling iron content), the material of S-type asteroids. **Carbonaceous chondrite** (CI, CM), dark clay-rich meteorite, the material of many C-type asteroids. **H**, absolute magnitude, the brightness from which size is guessed. **In the rock**, what is physically there before anything is dug, refined, moved or sold.

---

## 0. Bottom line

1. **A typical reachable asteroid holds very little.** Almost every asteroid is made of rock that carries 2 to 5.5 ppm of PGMs, about the grade of a working platinum mine on Earth, in a body of a few thousand tonnes. At dealer prices on 20 November 2026 that is $165 to $485 of PGMs per tonne of rock [P, my calculation], so a 15 m stony asteroid of about 4,400 t holds roughly $0.7 to $2 million, in the rock, before any cost. World PGM mines dig that much ore in about 20 minutes (my calculation: 434 t of PGMs a year at the median ore grade of 3.86 g/t is about 112 million t of ore).
2. **The tag for an unmeasured asteroid is a function of its brightness only.** For H 26.2 (the list's median, about 15 m if stony) my model gives, for metal: about 2 chances in 5 of none in separable form, otherwise $0.4 million to $14 million in the rock (9 cases in 10). For water: about 9 chances in 10 of none, otherwise 300 to 11,000 t bound in minerals. (That water figure assumes a dark object of a given brightness is larger than a stony one; with one size rule for every class it is 16 to 1,700 t.) Each magnitude of H changes every figure by a factor of 4.
3. **The figure that matters is the last one.** The most asteroid material ever returned is 121.6 g [S]. As median-grade iron meteorite that is 5 milligrams of PGMs, worth about 44 cents (my calculation).
4. **Prices are not a fixed input.** Platinum set a record of about $2,924 an ounce on 26 January 2026 and was $1,290 to $1,336 on 20 November [S, P]. Iridium and ruthenium are at 2.3 and 2.8 times their 2025 averages [P]. The same asteroid's metal was worth 44% less at 2025 average prices (my calculation).
5. **Asterank's numbers can be reproduced to the last digit from its public code, and they are not prices times contents.** Every C-type is valued at $0.0086 per kg, 99.7% of it from "hydrogen"; every X-type at $0.0010 per kg, 99.8% of it from cobalt; platinum plays no part. Where no measured mass exists the code's mass is 125 times that of a sphere of the stated size and density (section 3.1).
6. **The mining industry's own reporting code forbids the number this page would print if it is done carelessly.** JORC clause 51: in-ground financial valuations "must not be reported" because they have "little or no relationship to economic viability" [P]. The design in section 5 is built around that objection.
7. **Water is where an honest tag can still go wrong.** Any hypothetical price per kilogram, multiplied by a dark asteroid's water, gives billions: at $1,000/kg Ryugu's water would be "$31 trillion", 370 times Asterank's figure (my calculation: 4.5 × 10¹¹ kg [R] × 6.84 wt% × $1,000). No one buys water in orbit, the one published demand forecast is 300 to 500 t a year from 2030 [P abstract], and launch from Earth caps the price. Water should be shown in tonnes first, with dollars capped by a stated market.

---

## 1. What is in each kind of body

### 1.1 PGMs in iron meteorites (Cannon, Gialich & Acain 2023) [P]

Full text read today. Table 2, total of six PGMs, from a statistical sampling of iron meteorite groups (10 meteorites drawn per group, 100 repeats; 618 Ir and 548 Pt measurements, 40 for Rh):

| Percentile | Iron meteorites, ppm | Terrestrial deposits, ppm |
|---|---|---|
| 10th | 14.70 | 1.07 |
| 20th | 20.75 | 2.39 |
| 30th | 27.05 | 3.40 |
| 40th | 34.77 | 3.62 |
| 50th | 40.78 | 3.86 |
| 60th | 52.88 | 4.19 |
| 70th | 63.48 | 5.40 |
| 80th | 91.23 | 6.00 |
| 90th | 107.86 | 7.36 |

What they apply to, in the paper's words:

- They are for **100% metal**: "should therefore be interpreted as upper values because they represent 100% metal content".
- Full range "between ~6 and 230 ppm". The highest supportable value is about 230 ppm (the IIAB iron Avce, 59.5 ppm Ir). Earlier figures of 300 ppm (Kargel 1994) and 700 ppm (implied by Elvis 2014's "up to 100 ppm Ir") "are not supported by actual measurements".
- "The pure metallic asteroid is now seen as an extreme endmember that may not exist in practice." "A spacecraft sent to an X-Complex asteroid is likely to encounter an unknown proportion of metals and silicates."
- "There is no known way to remotely identify where an asteroid falls along the wide distributions of PGM grades."
- "The 50th percentile values provide a better expectation than the 90th percentiles as in Kargel (1994)."
- Mix of the six: "Pt and Ru account for more than half the total budget. Ir, Os, and Pd are present in lower amounts, and Rh is by far the least abundant." The paper gives no numerical split in the text (it is a pie chart, Fig. 3f).
- Nickel and cobalt: more concentrated in some asteroids than in the best ores on Earth, but with 2.7 million t of nickel and 170 thousand t of cobalt mined a year, "returning these metals to Earth is a non-starter".

A lognormal with median 40.78 ppm and sigma 0.78 (in natural log) passes through the 10th and 90th percentiles (my fit); its mean is about 55 ppm.

### 1.2 PGMs in ordinary chondrites

**Bulk rock**, Horan et al. 2003, Table 1, isotope dilution, in ppb [P]. Rhodium was not measured; I add it at 0.30 times iridium (the CI ratio, Lodders 2003 [R]; Cannon quotes the same table's Ru/Ir of 1.471, which matches my recalled values).

| Group | Meteorites in the table | Os | Ir | Ru | Pt | Pd | Total of six, ppm (my calculation) |
|---|---|---|---|---|---|---|---|
| H | Forest Vale, Ochansk, Forest City | 810–860 | 731–762 | 1,105–1,188 | 1,504–1,611 | 813–913 | 5.2–5.6 |
| L | Farmington, Chico (two aliquots) | 497–696 | 442–628 | 607–970 | 867–1,295 | 486–625 | 3.0–4.4 |
| LL | Semarkona (two aliquots), Chainpur | 289–351 | 261–317 | 401–537 | 514–672 | 346–443 | 1.9–2.3 |
| CI | Orgueil, Ivuna | 429–459 | 406–456 | 609–652 | 829–858 | 529–563 | 2.9–3.1 |
| CM | Murchison, Murray, Mighei | 569–662 | 544–613 | 741–851 | 1,041–1,067 | 577–619 | 3.7–4.0 |
| EH | Indarch, Adhi Kot, St. Sauveur, St. Mark's | 501–666 | 469–611 | 734–907 | 963–1,246 | 835–919 | 3.6–4.5 |
| EL | Daniel's Kuil, Yilmia, Blithfield, Pillistfer | 277–828 | 254–749 | 367–1,168 | 503–1,528 | 360–921 | 1.8–5.4 |

These are two to four meteorites per group, so they show the level, not the spread. The point that matters for the site: **every undifferentiated (chondritic) body, stony or dark, carries about 2 to 5.5 ppm**. Class moves the grade by a factor of under three. Only differentiated bodies depart from it: irons upward by roughly 3 to 50 times, and the silicate achondrites (aubrites, basaltic HED meteorites) downward to effectively nothing [R].

**Metal fraction.** Vernazza et al. 2015, Table 1, equilibrated ordinary chondrites: metal 8.4 vol% (H), 4.1 vol% (L), 2 vol% (LL); total iron 28, 22, 19 wt% [P]. Converted with metal at 7.9 g/cm³ and grain densities of 3.72, 3.56 and 3.54 g/cm³ [R], that is about **18, 9 and 4.5 wt% metal** (my calculation). Kargel 1994 gave 1.2 to 5.3% for LL [S, earlier report]. I could not open Dunn et al. 2010, the source Cannon uses for his Fig. 5 (the repository blocks automated reading).

**PGMs in that metal.** Cannon, citing Horan et al. 2009: metal grains "host the vast majority of the PGM budget" [P]. Dividing bulk by metal fraction gives about **29–31 ppm in H metal, 33–48 in L, 43–52 in LL** (my calculation), which is the 30th to 60th percentile of iron meteorites. Gilmour & Herd 2020 found in-place averages similar across the three groups, where older bulk-metal studies found H < L < LL [S]. Kargel's 50 to 220 ppm "precious metals" in LL metal [S] is the high end and counts more elements.

So an S-type asteroid is a low-grade ore (2–5.5 ppm) that carries a high-grade concentrate (30–50 ppm) as 4 to 18% of its mass. To bring home one kilogram of PGMs someone must process 180 to 520 t of rock (my calculation).

**Nickel and cobalt.** Iron meteorites are typically 5–10 wt% nickel and about 0.5 wt% cobalt; ordinary chondrites about 1.0–1.7 wt% nickel in bulk [R, not checked today]. At $15.4/kg and $33.5/kg these are worth less per kilogram than 1% of the cost of putting a kilogram into orbit, so no return scenario can include them. They should appear on the page as tonnes, not dollars.

### 1.3 Water and hydrogen

| Material | Value | Source | Tag |
|---|---|---|---|
| Ivuna (CI) | 12.73 ± 0.63 wt% H₂O: 6.58 ± 0.32 interlayer, 6.15 ± 0.30 structural | Yokoyama et al. 2023 | [P] |
| Ryugu sample | 6.84 ± 0.34 wt% H₂O: 0.30 ± 0.01 interlayer, 6.54 ± 0.32 structural; total H 0.94 ± 0.05 wt% | same | [P] |
| Bennu sample | 0.84–0.95 wt% H; 4.5–4.7 wt% C | Lauretta et al. 2024 | [P] |
| Bennu as water | at most 7.5–8.5 wt% if all H were water; less, since part is organic | my calculation (× 8.94) | |
| CM chondrites | 1.9–10.5 wt% indigenous water, mean 7.0; falls pick up weight-percent water from air within days | Lee et al. 2023 | [S] |
| CI and CM, older literature | "~10% by mass", individual samples "~2–25%" | Rivkin & DeMeo 2019, citing Jarosewich 1990 | [P for the quotation] |
| C-complex main-belt asteroids, remote | 4.5 wt% average, method uncertainty 4 wt% | Beck et al. 2021 | [P abstract] |
| Elvis 2014 assumption | 20 wt% (10% hydrated + 10% ice) in a quarter of carbonaceous bodies | Elvis 2014 | [P] |

Yokoyama et al. read Ryugu's missing interlayer water as "loss of interlayer water to space". The two returned samples agree near 7 wt%. A defensible distribution for a hydrated carbonaceous near-Earth asteroid is a median of 6 wt% with nine cases in ten between 2 and 13 wt%; 20 wt% is not supported by any sample.

**What fraction is hydrated at all.**

- Rivkin & DeMeo 2019 [P]: among main-belt C-complex asteroids, 30 ± 5% show the 0.7 µm band (Rivkin 2012) and 45–50% in Fornasier et al. 2014; they adopt 39 ± 10% for the inner belt. Feeding that through delivery models predicts 17 ± 3% of near-Earth objects in the hydrated Ch class and 43 ± 6% C-complex.
- The same paper, on what is observed: C-complex is 9.8 ± 3.3% of near-Earth objects (Stuart & Binzel 2004) or 23% of 230 (Carry et al. 2016), which "suggest a Ch fraction of 6% ± 3%". Meteorite falls give less still: 16 CM and 45 carbonaceous out of 1,153 falls, "less than 2% of NEOs are CM and only 4% of NEOs are carbonaceous". They call the gap "the main driver of our overall uncertainty".
- The 0.7 µm band undercounts: Usui et al. 2019 found the 2.7 µm band in 17 of 22 large C-complex asteroids with AKARI [P], and both sampled near-Earth asteroids were hydrated without showing a 0.7 µm band [R].
- Later than 2019: Lewicki et al. 2021, "only a few percent of NEOs are anticipated to be rich in the hydrated minerals" [S, earlier report]. I found no 2022–2026 survey of hydration among near-Earth asteroids.

For an object known only by its brightness, the chance of any hydrated minerals is **between 3% and 17%**, and I use 11% (section 5.2).

### 1.4 What an "X-type" could be

- The X complex is defined by a featureless spectrum. Tholen split it by reflectivity: E above 0.3, M 0.1–0.3, P below 0.1 [P, via Moskovitz et al. 2026].
- Proportions among near-Earth X-types with a measured reflectivity: 15% E, 31% M, 53% P (71 objects, Sergeyev et al. 2023); 10%, 32%, 57% for 270 main-belt and near-Earth objects (NEOWISE) [P, as quoted by Moskovitz et al. 2026]. Those samples favour big, dark objects. At a fixed brightness bright objects are over-represented; weighting by reflectivity^1.3 (a size-distribution slope of 2.6) turns 15/31/53 into about 56/33/11 (my calculation). **The M share is about a third either way; the E and P shares are not known to better than a factor of three.**
- M is not metal. Shepard et al. 2015: 11 of 29 main-belt M-class asteroids (38%) have radar reflectivities "consistent with metal-dominated compositions", and 7 of those 11 also show a hydration band [P abstract]. Cannon lists what else an X-type can be: metal-rich enstatite chondrites, H chondrites, CH and CB chondrites, pallasites and mesosiderites [P].
- E is bright enstatite rock (aubrite-like), with almost no PGMs [R]. P is dark primitive material like C-types.
- Among near-Earth asteroids, (6178) 1986 DA is the only one confirmed metal-rich by radar; its spectrum fits about 85% metal and 15% pyroxene [S].
- Densities span the whole range: Carry 2012 gives X 1.85 ± 0.81, Xe 2.60 ± 0.20, Xk 4.22 ± 0.65, Xc 4.86 ± 0.81 g/cm³ for large asteroids [P].

Chained together: of an unmeasured small asteroid, about 23% X × 32% M × 38% metal-dominated ≈ **2.8% metal-rich** (my calculation; plausible range 1–5%). Elvis 2014 reached 4% M-type by a similar route and halved it for richness [P]. Irons are about 2% of observed meteorite falls (49 of 1,102, [S]), a sample that favours strong material.

### 1.5 Class base rates used below

From Moskovitz et al. 2026 [P]: S plus Q falls from 70% at H 14 to 50% at H 22 and 35% at H 28; X rises; C stays near 10–15%. From this project's `source-prior.md` [S]: for H 24–29, S+Q 35–45%, X 20–25%, C 11–15%, B+D about 5%, V about 5%, others 10–15%; debiased population estimates run from 23% to 42% stony and should not be used for a single object picked by brightness.

Used here, normalised: stony (ordinary chondrite) 41%, X 23%, C 13%, B and D 5%, V 5%, other 13%.

---

## 2. Prices and markets

### 2.1 Metals, with dates

| Metal | Price, 20 Nov 2026 | In $/kg (my calculation) | Cross-check | 2025 average (USGS) | Tag |
|---|---|---|---|---|---|
| Platinum | $1,336/troy oz (Umicore 10am); November average to date $1,481.67 | 42,953 | $1,289.60 close (Trading Economics); Kitco bid $1,295 on 21 Nov | $1,200 | [P], [S] |
| Palladium | $912/troy oz; November average $1,004 | 29,321 | $893 (Trading Economics) | $1,100 | [P], [S] |
| Rhodium | $8,950/troy oz; November average $9,113 | 287,749 | $9,000 (Trading Economics) | $5,800 | [P], [S] |
| Iridium | $10,200/troy oz; November average $10,110 | 327,938 | $10,150 on 11 and 19 Nov (two price sites, via search) | $4,400 | [P], [S] |
| Ruthenium | $1,900/troy oz; November average $1,943 | 61,086 | $1,850 on 19 Nov (via search) | $690 | [P], [S] |
| Osmium | no benchmark price | – | "fixed in the 300-400$/oz range since the 2000's" on the old Engelhard sheet; priced per transaction | – | [P] |
| Nickel | $15,371/t on 20 Nov (Trading Economics); LME three-month $16,140/t on 11 Nov (Argus, via search) | 15.4 | | $15,000/t LME cash | [S], [P] for 2025 |
| Cobalt | $33,525/t on 19 Nov (Trading Economics); metal $19.50–22.50/lb on 26 Oct (Fastmarkets, via search) | 33.5 | | $15/lb LME cash ($33,070/t) | [S], [P] for 2025 |

How unstable these are:

- Platinum: record of about $2,923 on 26 January 2026; down 21% in the past month; "17-month low" on 18 November [S, Trading Economics and search].
- Palladium: down 18% in a month and 35% in a year [S].
- Iridium and ruthenium are at 2.3 and 2.8 times their 2025 averages (my calculation from the table).
- A mix of the six PGMs in meteoritic (CI) proportions, osmium unpriced, is worth **$87,945/kg on 20 November 2026 and $49,590/kg at 2025 averages** (my calculation). Iridium alone is half of the first figure.

Johnson Matthey's price table would not load ("MetalPrice Api Failed"), so the snapshot is Umicore's.

### 2.2 Size of each market

| Metal | World primary (mine) supply, 2025 | Dollars a year at 20 Nov 2026 prices (my calculation) | Source | Tag |
|---|---|---|---|---|
| Platinum | 178 t (IPA/SFA); 170 t (USGS) | $7.6 B | IPA factsheet May 2026; USGS MCS 2026 | [P] |
| Palladium | 197 t (IPA/SFA); 190 t (USGS) | $5.8 B | same | [P] |
| Rhodium | about 22 t | $6.3 B | IPA factsheet | [P] |
| Iridium | about 7 t | $2.3 B | IPA factsheet | [P] |
| Ruthenium | about 30 t | $1.8 B | IPA factsheet | [P] |
| Osmium | "of the order of hundreds of kilograms per year"; not reported by companies | a few million | IPA factsheet | [P] |
| Five PGMs together | 434 t | **$23.9 B** | | |
| Nickel | 3.9 million t | $60 B | USGS MCS 2026 | [P] |
| Cobalt | 310,000 t | $10.4 B | USGS MCS 2026 | [P] |

Also from the same sources [P]: total demand in 2025 was 242 t platinum, 311 t palladium and 33 t rhodium, the difference being recycling; about 140 t of platinum and palladium were recovered from scrap; world PGM reserves exceed 76,000 t.

What selling an asteroid's metal would do:

- A 15 m stony asteroid holds about 20 kg of PGMs, 0.005% of a year's supply. No effect.
- A 60 m metal-rich body (4,500 kg/m³, 75% metal) at the median grade holds 15.6 t, including 2.2 t of iridium, **31% of a year's world iridium supply**; at the 90th percentile 5.7 t, 82% (my calculation). The iridium market cannot absorb that at $10,200 an ounce.
- Hein et al. 2020 [P]: platinum demand is inelastic, so price falls faster than supply rises; a venture "would only be economically feasible" if space platinum displaced terrestrial platinum one for one. Nachtrieb & Smith 2026 [P] model the opposite sequence: a profit boom, then prices fall by over 75% in 15 years once supply has moved off Earth. Both agree the price is not a constant.

### 2.3 Water in space: every published price or cost I found

| Who, when | Figure | Where | Basis | Tag |
|---|---|---|---|---|
| Actual, 2011–12 | about $10,000/kg (3.3 t for about $33 M a year) | water delivered to the ISS | J. McDowell, private communication in Elvis 2014 | [P for Elvis] |
| Elvis 2014 | $5,000/kg; $10,000/kg | low Earth orbit; geostationary orbit | half of a launch cost of "~US$10 k or more" per kg (2000 dollars); "would lose value if lower launch costs/kg emerge" | [P] |
| Kutter (ULA) 2016, conference paper | $3,000/kg; $1,000/kg; $500/kg (as $3M, $1M, $0.5M per ton) | low Earth orbit; geostationary orbit; lunar surface | the price at which lunar propellant in low orbit beats ULA launching its own; "makes no claim whether it is economically feasible to mine and process lunar propellants for $500,000 per ton" | [P] |
| Sowers (ULA), Space.com, 29 June 2016 | $3,000/kg; $1,000/kg; $500/kg | low Earth orbit; Earth–Moon L1; lunar surface | "willing to pay"; the L1 figure came from talks with asteroid miners | [P for the article] |
| Asterank code | $2,200/kg "cost_to_orbit" | unspecified | a constant | [P] |
| Hein, Matheson & Fries 2020 | $20,000/kg | cislunar, unspecified | an assumption in the scenario table, with 5% water yield | [P] |
| Colvin, Crane & Lal 2019/2020 | delivered cost $2,000–3,000/kg; manufacturing cost $900–5,000/kg | low Earth orbit; lunar orbit | techno-economic model; "comparable" to Falcon Heavy. Demand 6,000–10,000 t over 2030–2050, about $15 B | [P abstract] |
| Jones et al. (NASA Langley) 2019 | lunar propellant "97% more expensive than Earth-based propellant" | cislunar | cost model, 59 t a year for 14 years | [P, as summarised in their 2020 paper] |
| Metzger 2023 | launch $2,000/kg now, falling to $30/kg (optimistic) or $119–436/kg in 30 years | low Earth orbit | learning-curve model; argues lunar propellant can still compete | [P] |
| Orbit Fab, 30 Aug 2022 | $20 M for up to 100 kg of hydrazine ($200,000/kg) | geostationary orbit | a list price for a service; no commercial delivery had flown by November 2026 | [P], [S] |

No buyer has restated any of these. Colvin's two figures imply an average of $1,500–2,500/kg (my calculation). Every one is tied to the launch price of its year.

### 2.4 Launch cost, the ceiling

| Vehicle | Price | Per kg to low Earth orbit (my calculation) | Tag |
|---|---|---|---|
| Falcon 9 | $74 M list in 2026 (up to 5.5 t to transfer orbit with booster recovery); $70 M in 2025; $67 M in 2022 | $3,250 at the 22.8 t expendable capacity; $13,450/kg to transfer orbit | [S] |
| Falcon 9, reported internal cost | $15 M per reused flight | under $1,000 | [S] |
| Falcon Heavy | $97 M since March 2022 | $1,520 at 63.8 t, a capacity that price does not buy | [S] |
| Rideshare | $6,500/kg (2023), about $7,000/kg (2026) | | [S] |
| Starship | no published price; stated targets $100–200/kg | | [S] |

SpaceX's own price sheet returned a 404 today; these come from a dated explainer (25 October 2026) that cites it. Water in low orbit cannot be worth more than about **$1,500–3,300/kg today**, and that ceiling falls with every launch-price cut. In 2014 the same reasoning gave $5,000; in 2016, $3,000.

---

## 3. How earlier valuations were computed, and why they failed

### 3.1 Asterank [P: code and live data read today]

Source: `scoring.py` and `estimate.py` in the public repository, and the live API.

- value = mass × Σ (class table percentage × constant per kg).
- Mass: from a measured GM where JPL has one; otherwise from a diameter, or from H with reflectivity 0.15 if there is no diameter, times a density of 1.38 (C-like), 2.71 (S-like), 5.32 (M) or 2 g/cm³.
- Composition: one fixed table per spectral class. "X", "Xe" and "Xk" are all given 88% iron, 10% nickel, 0.5% cobalt and no platinum. S-types are given silicates priced at 1e-25 dollars per kg. "?" is empty.
- Prices are constants in the code, not market prices: platinum "2", cobalt "0.20", hydrogen "3.658", water "0.01", nickel "0.00002" dollars per kg.
- profit = value/12 × closeness/3417.5 × 12/delta-v. The About page says "Mining costs are factored in as a flat percentage of potential value."

I re-implemented the arithmetic and it reproduces the API's values to every digit:

| Object | Asterank value | Mass the code used | Per kg | Where the value comes from | Code mass ÷ real mass (real masses recalled) |
|---|---|---|---|---|---|
| Ryugu (Cg, H 19.3, no diameter on file) | $82,756,156,359 | 9.6 × 10¹² kg | $0.008621 | hydrogen, 99.7% | 21 |
| Bennu (B, measured GM) | $669,957,009 | 7.8 × 10¹⁰ kg | $0.008597 | hydrogen, 100% | 1.1 |
| Didymos (Xk, 0.78 km) | $62,253,881,856 | 6.2 × 10¹³ kg | $0.001002 | cobalt, 99.8% | about 110–120 |
| Davida (C, 270 km) | $15.4 quintillion | 1.8 × 10²¹ kg | $0.008621 | hydrogen, 99.7% | about 50 |
| Psyche (X, measured GM) | $27,673,419,947 | mass × 10⁻⁶ (a penalty for bodies over 10¹⁸ kg) | $0.001002 | cobalt, 99.8% | – |

What this shows:

- The diameter branch computes volume as π r³ (the code is Python 2, where 4/3 is 1) and multiplies by density/6 × 10¹⁵. The result is exactly 125 times the mass of a sphere of that diameter and density. Whether intended or not, most headline values carry it.
- Ryugu is "worth" 124 times Bennu, though the two are near-identical bodies and Ryugu is six times heavier, because Bennu's mass came from a measurement and Ryugu's from the diameter branch.
- No uncertainty anywhere; the About page itself says "the overwhelming majority of asteroids have no spectral classification".

### 3.2 The "quintillion" figures for Psyche [S]

The $10,000 quadrillion (10¹⁹ dollars) figure is Lindy Elkins-Tanton's own, from about 2017: the mass of iron in a 226 km body times the market price of iron. Press reports quote her calling it meaningless and a fun exercise. It is the same construction as Asterank's with a different price list (Asterank itself shows $27.7 billion for Psyche). Later density work points to more rock and pore space than a metal body [S]. I read search summaries of the coverage, not the original interview.

### 3.3 Elvis 2014 [P]

- Formula: number of ore bodies = P_ore × N(>M_min), with P_ore = P_type × P_rich × P_acc × P_eng, and value Λ = ε M C λ (extraction efficiency × mass × concentration × price).
- PGM case: a 100 m body at 4,500 kg/m³ is 2.36 million t; at 10 ppm that is 23.6 t; at $50,000/kg, $1.18 B. The spread of grades gives $0.8 B to $8.8 B. "Such a large range of values could greatly change the profitability of a venture." A 50 m body: $150 M.
- He says he assumes no price effect, that efficiency "is unlikely to be 100%", sets P_eng to 1 for lack of a way to estimate it, and calls the results "highly uncertain".
- Criticised by Cannon et al. 2023 for the iridium figure (a misreading of Kargel) and by the samples for the 20 wt% water.
- His definition is the useful part: "ore" is "commercially profitable material, and not merely a high concentration of a resource".

### 3.4 Hein, Matheson & Fries 2020 [P]

Profit per spacecraft, driven by throughput (kilograms processed per second per kilogram of spacecraft), number of spacecraft and mission cadence. Platinum anchor: $40,449/kg and 254,582 kg a year, with a linear demand curve and inelastic demand. Water: $20,000/kg, 5% yield, 150 kg spacecraft; the conservative case breaks even in 5.9 years. The paper's own limit: every price and cost in the table is an assumption.

### 3.5 Cannon, Gialich & Acain 2023 [P]

Replaced Kargel's 90th-percentile grades with a measured distribution, compared it with terrestrial ore grades rather than crustal averages, and said plainly that grade cannot be sensed remotely and that pure-metal asteroids may not exist. It prices nothing. Two of the three authors founded AstroForge.

### 3.6 2024–2026

- Nachtrieb & Smith, July 2026 preprint [P]: a market model, friendly to mining. It still quotes grades of "100 ppm to as high as 187 ppm", the top decile of Cannon's distribution, and "trillions of dollars" for a 1 km metal body.
- Alarcón et al. 2026 on the first commercial target, titled "Accessible does not mean exploitable" [S, earlier report].
- The 2025–2026 pieces my searches returned beyond these were blog and trade-press articles; I found no peer-reviewed critique of asteroid valuations from those years, and did not use the blogs.

### 3.7 What the careful authors treat as a defensible figure of merit

- **Grade and tonnage with a confidence class**, as in mining: Inferred, Indicated, Measured (Cannon; Lewicki et al. 2021 [S]: asteroid resources are "mostly in the Order of Magnitude stage").
- **Counts, not prices**: how many bodies pass every filter (Elvis), how many probes it takes to find one (Elvis & Esty [S]).
- **Cost against the competing supply**: delivered cost per kg versus launch from Earth (Colvin; Metzger's ratios), or versus a mine on Earth.
- **Expected net present value** of a stated mission, with the chance of failure in it (Sonter [S]).
- **Not gross in-ground value.** JORC Code 2012, clause 51 [P]: "The publication of in situ or 'in ground' financial valuations breaches the principles of the Code ... Such in situ or in ground financial valuations must not be reported by companies in relation to Exploration Results, Mineral Resources or deposit size. The use of such financial valuations (usually quoted in dollars) has little or no relationship to economic viability, value or potential returns to investors." Canada's NI 43-101, paragraph 2.3(1)(c), restricts disclosure of the "gross value of metal or mineral in a deposit" [S; the rule text returned 403].

---

## 4. Bulk density and porosity, to turn a size into a mass

**Meteorites** (Carry 2012, Table 2, average bulk density in g/cm³) [P]: H 3.42 ± 0.18, L 3.36 ± 0.16, LL 3.22 ± 0.22; CI 1.60 ± 0.03, CM 2.25 ± 0.08, CO 3.03 ± 0.19, CV 2.79 ± 0.06; EH 3.47 ± 0.21, EL 3.46 ± 0.32; HED 3.25 ± 0.26; pallasites 4.76 ± 0.10, mesosiderites 4.35 ± 0.02; iron hexahedrites 7.37 ± 0.14, octahedrites 7.14 ± 0.13. Pore space inside the rock: about 35% for CI, 23% for CM and CR, around 10% for most other classes, up to 30% in individual stones [S].

**Asteroids by class** (Carry 2012, Table 3, estimates better than 20%) [P]: S 2.72 ± 0.54, C 1.33 ± 0.58, Ch 1.41 ± 0.29, B 2.38 ± 0.45, X 1.85 ± 0.81, Xe 2.60 ± 0.20, Xk 4.22 ± 0.65, Xc 4.86 ± 0.81. These are bodies tens to hundreds of km across. The paper notes that near-Earth asteroids "seem to have a lower density" than main-belt ones in both the C and S complexes.

**Near-Earth asteroids measured directly** [S, this project's `ground-truth.md`]: Itokawa 1.90 ± 0.13; Bennu 1.19; Ryugu 1.19 ± 0.02; Didymos 2.60 ± 0.14; Dimorphos 1.54 ± 0.22 (model-dependent); Eros 2.67 ± 0.03; radar binaries from 0.55 to 2.1. None is under about 150 m.

**Implied large-scale voids** (1 − bulk density ÷ meteorite density; my calculation): Itokawa 41% against LL; Didymos about 21%; Dimorphos about 53%; Bennu and Ryugu 47% against CM or 26% against CI.

**Decametre bodies, all indirect** [S, same file]: 2011 MD 1.1 (+0.7/−0.5) with voids of at least 65%; 2009 BD 2.9 or 1.7 depending on the size solution; 2020 CD3 2.1 ± 0.4 if stony; 2015 TC25 about 1. Each needs an assumed size.

**Recommended ranges for 5–30 m bodies** (my judgement from the above; flat within the range):

| Kind | kg/m³ | Low end | High end |
|---|---|---|---|
| Stony (S, Q) | 1,700–3,400 | rubble like Itokawa or Dimorphos | a single block at meteorite density |
| Dark (C, B, D, P) | 900–2,300 | Bennu, Ryugu and lighter | a single block of CM |
| Bright enstatite (E) | 2,000–3,300 | rubble | a block |
| M, silicate-dominated | 2,000–3,500 | rubble | a block of enstatite chondrite |
| M, metal-rich | 3,000–7,500 | porous mix (1986 DA surface 3.79, range 2.33–6.5 [S]) | solid iron |
| Unknown class | about 1,200–3,300 (5th–95th), median 2,300 | | 2–3% chance above 3,500 |

A fast spin excludes loose rubble, so a measured period under about two hours pushes a body toward the upper half of its row. The effect on mass is under a factor of 1.5, and I have not sourced a number for it.

Mass of a sphere: (π/6) × D³ × density. At 15 m the volume is 1,767 m³: 3,000 t at 1,700 kg/m³, 4,400 t at 2,500, 6,000 t at 3,400. Halving or doubling the diameter changes mass eightfold: 550 t at 7.5 m, 35,300 t at 30 m. **Size, not density or class, sets the width of every range below.**

---

## 5. Recommended design

### 5.1 Three named rows, in this order

**Row 1. "Metal, at today's prices."**

- Counts: the five PGMs with a market (Pt, Pd, Rh, Ir, Ru) that sit in grains of iron-nickel metal, the form a magnet and a furnace could in principle separate. PGMs spread through dark clay-rich rock, bright enstatite rock or basalt count as nothing.
- Price: one dated dealer snapshot per method release (here Umicore, 20 November 2026), printed with its date. Osmium, nickel and cobalt are shown as mass only.
- Excluded, and said so on the page: digging, refining, the trip home, and any effect on the price.
- Market cap: each metal is priced only up to 10% of one year's world mine supply (17.8 t Pt, 19.7 t Pd, 2.2 t Rh, 0.7 t Ir, 3 t Ru; about $2.4 B in all). Above that the page prints the tonnage and "more than the market could absorb at this price". The 10% is my choice and should be stated as a choice. It only binds for metal-rich bodies above roughly 40 m.

**Row 2. "Water, at a hypothetical orbit price."**

- Counts: water bound in clay minerals, in tonnes. Tonnes are the primary figure.
- Price points, each named: $100/kg (the stated Starship target, if met, which would then be the ceiling); $1,000/kg (ULA's 2016 figure for high orbit); $3,000/kg (ULA's 2016 offer for low orbit, and roughly today's Falcon 9 ceiling).
- Demand cap: dollars are computed for at most 2,000 t, five years of the middle of the only published forecast (300–500 t a year from 2030, Colvin et al.). Beyond that the page prints "more than the forecast market would buy in five years".
- Printed with it: "Nobody buys water in orbit today."

**Row 3. "Brought back, with what has flown."**

- Not hypothetical. The most asteroid material ever returned is 121.6 g, by a mission costing about $1 billion [S].
- For every object the row reads: nothing. Shown beneath: what 121.6 g of this object's likeliest material would fetch. For iron at the median grade, 5 mg of PGMs, about $0.44; for H chondrite, 6 cents; as water at 7 wt% and $3,000/kg, about $26 (my calculation).

### 5.2 Every assumption, in one table

| Assumption | Value used here | Basis | Confidence |
|---|---|---|---|
| Size from H | D = 1,329 km × 10^(−H/5) ÷ √reflectivity; H uncertain by 0.4 mag | standard relation | The project's own tested size model must replace my reflectivities |
| Reflectivity by kind (median; spread in ln) | stony 0.25 (0.35); dark 0.05 (0.45); E 0.45 (0.3); M 0.15 (0.35); V 0.35 (0.3); other 0.2–0.25 (0.4) | Thomas et al. 2011 values as quoted by Moskovitz 2026 (Q/Sq 0.29, Xk 0.31, B 0.07, D 0.02) and the Tholen limits [P]; spreads are my guess | Placeholder |
| Class shares at H 24–29 | stony 41%, X 23%, C 13%, B+D 5%, V 5%, other 13% | section 1.5 | Surveys disagree by ±10 points |
| X split E / M / P | 35 / 32 / 33% (tested from 15/31/53 to 56/33/11) | section 1.4 | M firm; E and P not |
| Metal-rich given M | 38% | Shepard et al. 2015, large main-belt bodies | Untested at this size |
| Stony split H / L / LL | 25 / 35 / 40% | between the fall mix and the kilometre-scale mix [S] | Weak |
| PGM value per tonne of rock | uniform between the lowest and highest meteorite in each group (section 6) | Horan et al. 2003 | 2–4 meteorites per group |
| Grades for the other kinds | dark rock: CI or CM at even odds (counted only in the "all PGMs" line, not the metal row); M silicate-dominated: EH or EL at even odds; E, V: nothing | Horan et al. 2003; my assignment of meteorite to class | Weak |
| Iron grade | lognormal, median 40.78 ppm, sigma 0.78, limits 6–230 ppm | Cannon et al. 2023 | Good for meteorites; untested for asteroids |
| Metal share of a metal-rich body | 50–100% | 1986 DA about 85% [S]; mesosiderites about half | Weak |
| Element mix in iron | CI proportions | Lodders 2003 [R] | Cannon shows irons depart from this at high grade |
| "Other" classes | 9 points chondritic at L-like grade, 4 points with nothing | my simplification | Weak |
| Density | section 4 table | section 4 | No direct measurement below 150 m |
| Any hydrated minerals | 50% of C, B, D; 30% of P; 0 otherwise (tested 30–77%) | section 1.3 | Factor of two |
| Water if hydrated | lognormal, median 6 wt%, 90% within 2–13 wt% | Ryugu, Bennu, CM, CI | Reasonable |

### 5.3 How to express it

- **The chance of nothing first, as a frequency**: "2 in 5", "9 in 10". "Nothing" is defined per row: no metal grains carrying PGMs; no hydrated minerals; no return.
- **Then the range, given that there is something**: the 5th to 95th percentile, worded "nine cases in ten", with the 25th–75th drawn as the darker part of the bar.
- **Scale**: log dollars, one fixed axis for every asteroid and every row, $1 to $1 trillion, so entries can be compared by eye and a factor of ten is always the same width.
- **Fixed marks on that axis**, each sourced: about $10 million (the builder's stated cost of the cheapest deep-space prospecting probe, [S, `industry.md`]); about $1 billion (the mission that returned 121.6 g); $24 billion (a year of world PGM mine supply).
- **Rounding**: one significant figure, in words ("$400 thousand to $14 million").
- **Physical units beside the dollars**: kilograms of PGMs, tonnes of water, tonnes of rock. They do not move when prices do.
- **Price sensitivity in one line**: "At 2025 average prices: 44% less."

### 5.4 So that it cannot be quoted as a point value

1. **Publish no central value.** No median, no mean, no "expected value", in the page, the CSV or the API. The mean is the dangerous one: for Example 1 it is $4 million for metal against a typical case under $2 million, because the 3% of metal-rich cases carry two thirds of it. For water at $1,000/kg, uncapped, the all-cases mean is about $380 million for an object that has no water nine times in ten (my calculation). That is the Asterank failure reproduced with better inputs.
2. **The data schema has no field named value.** It has `p_nothing`, `q05`, `q25`, `q75`, `q95`, `scenario_id`, `price_date`, `method_version`. Anyone who wants a single number has to make it themselves.
3. **The sentence is one unit.** Scenario name, price date and "in the rock" sit inside the same element as the figures, so a screenshot or a copied line carries them: "Metal, at 20 Nov 2026 prices: 2 in 5 none. Otherwise $400 thousand to $14 million in the rock."
4. **No ranking by dollars.** Tables sort on the chance of nothing, on mass, or on reach. There is no "most valuable asteroids" list.
5. **Row 3 is always on screen with Rows 1 and 2**, never behind a click.
6. **The method page quotes JORC clause 51** and says why the page prints a range anyway: to show how wide and how small it is.
7. **A "what this is not" line**: not a valuation, not a forecast of revenue, not advice.

### 5.5 "In the rock" and "recoverable" must be separate

Yes, and as three levels, not two:

1. **In the rock**: what is physically there (Rows 1 and 2).
2. **The most a perfect process could separate**: for metal, the PGMs in metal grains; for water, the bound water. In this design that is how Rows 1 and 2 are already defined, so the page should say that the row is an upper bound on anything recoverable.
3. **Recovered by anyone, ever**: Row 3.

I recommend against a fourth, "recoverable with a future efficiency of x%". Any x is invented, and the invented number would be the one quoted.

### 5.6 How the range should respond to an observation

From the model in 5.2, for H 26.2 (my calculation; 400,000 draws per case):

| What is known | Metal: chance of none | Metal: otherwise, 5th–95th | Water: chance of none | Water: otherwise | What changed |
|---|---|---|---|---|---|
| Brightness only | 43% | $0.36 M – $14 M (a factor of 40) | 89% | 330 – 11,000 t | – |
| + a rotation period | 43% | the same, at most 1.5 times higher | 89% | the same | Nothing in the rock. It moves the "can it be worked on" rung. |
| + S-type spectrum | under 10% (only if the class is wrong) | $0.3 M – $5.7 M (a factor of 18) | about 100% | – | The zero and the top tail go; the middle barely moves |
| + C-type spectrum | about 100% | – | 50% (30–77%) | 330 – 11,000 t | Metal row empties; water becomes a coin flip |
| + X-type spectrum, no reflectivity | 68% | $1.1 M – $190 M | 90% | 330 – 11,000 t | Wider, not narrower: two unlike kinds in one class |
| + X-type with reflectivity 0.1–0.3 | under 10% | $1.1 M – $190 M, in two clumps | about 100% | – | 38% chance of the metal-rich clump ($9 M – $330 M) |
| + S-type and a size good to 10% | under 10% | $0.5 M – $3 M (a factor of 6) | about 100% | – | The narrowest a telescope can make it |
| + a density ceiling near 5,000 kg/m³ | 43% | $0.35 M – $9 M: top of the range down by 30–40% | 89% | the same | Halves the 3% metal-rich share; removes solid iron only |

Rules that follow:

- **One model, redrawn.** An observation replaces a prior with a measurement and every row is recomputed from the same draws. Class, reflectivity, size and density must be drawn together, because a dark object of the same brightness is twice as wide and eight times the volume.
- **A range may widen.** An X-type spectrum does that. The page should say so, not hide it.
- **Show the old range behind the new one**, as the plan already does for forecasts.
- **A floor.** No observation from Earth makes the metal range narrower than about a factor of six, because grade cannot be sensed remotely and density is not measured at this size. That floor should be printed.
- **The order of leverage** is size, then class, then reflectivity within X, then density. Spin changes nothing in the rock.

---

## 6. Three worked examples

Shared inputs (all my calculation from sections 1 and 2):

- PGM value per tonne of rock on 20 November 2026: H $459–484; L $272–393; LL $166–203; CI $256–282; CM $335–369; EH $305–389; EL $160–474. At 2025 average prices each is 44% lower.
- How one of those is built, for the H chondrite Forest City: Ir 762 mg/t × $327.9/g = $250; Ru 1,188 × $61.1 = $73; Pt 1,611 × $43.0 = $69; Rh 229 × $287.7 = $66; Pd 913 × $29.3 = $27; total $484 per tonne (osmium, 860 mg/t, unpriced).
- Iron meteorite metal: $1,293, $3,586 and $9,486 per tonne at the 10th, 50th and 90th percentile (grade × $87,945 per kg of mixed PGMs).
- Size from H 26.2: 7.65 m ÷ √reflectivity, so 15.3 m at 0.25, 19.7 m at 0.15, 34.2 m at 0.05, 11.4 m at 0.45.

### Example 1. H 26.2, nothing else measured ("about 15 m")

By hand, for the commonest case and the two that matter:

- **Stony (41%)**: 15 m, volume (π/6) × 15³ = 1,767 m³; at 2,500 kg/m³, 4,418 t. As LL: 4,418 × $166–203 = $0.73–0.90 M. As H: 4,418 × $459–484 = $2.0–2.1 M. If it is really 7.5 m: 552 t, $0.09–0.27 M. If 30 m: 35,343 t, $5.9–17 M.
- **Metal-rich (2.8%)**: 19.7 m, 4,003 m³; at 4,500 kg/m³, 18,014 t; 75% metal at 40.78 ppm = 551 kg of PGMs; × $87,945 = $48 M.
- **Dark and hydrated (about 11%)**: 34.2 m, 20,945 m³; at 1,400 kg/m³, 29,323 t; at 6 wt%, 1,760 t of water.

From the full draw:

| | 5th | 25th | 50th | 75th | 95th |
|---|---|---|---|---|---|
| Diameter, m | 9.9 | 13.5 | 17.3 | 25.1 | 43.8 |
| Mass, t | 1,260 | 3,210 | 6,830 | 17,800 | 72,400 |
| Metal row, if any (57% of cases) | $0.36 M | $0.88 M | $1.7 M | $3.3 M | $14 M |
| All PGMs in the rock, in any form (83% of cases) | $0.42 M | $1.2 M | $2.7 M | $7.6 M | $34 M |
| Water, if any (11% of cases), t | 330 | 950 | 1,950 | 4,000 | 11,100 |

- The diameter range is wider at the top than the plan's "half to double", because a dark object of this brightness is about twice as wide as a stony one. My reflectivities are placeholders. Run instead with the plan's rule (median 15 m, nine in ten between 7.5 and 30 m, the same for every class), the metal row becomes $0.15 M – $18 M and the water row 16 – 1,700 t (my calculation). Water in tonnes therefore moves about twelvefold on one modelling choice, whether size is tied to class. The joint draw is the right one in principle (plan, Appendix C) and is untested at this brightness.
- Stony cases alone: $0.32 M – $5.7 M. Metal-rich cases alone: $8.8 M – $334 M.
- Water in dollars, uncapped: $0.33–11 B at $1,000/kg. Capped at 2,000 t: $33–200 M at $100/kg, $0.33–2 B at $1,000/kg, $1–6 B at $3,000/kg. Half of the hydrated cases hit the cap.

**The tag:**

> Metal, at 20 Nov 2026 prices: 2 in 5 none. Otherwise $400 thousand to $14 million in the rock (nine cases in ten); about 4 to 160 kg of platinum-group metals.
> Water, at a hypothetical orbit price: 9 in 10 none. Otherwise 300 to 11,000 tonnes bound in minerals. Nobody buys water in orbit today.
> Brought back, with what has flown: nothing. The most ever returned from any asteroid is 121.6 grams.

(The kilogram range is the dollar range divided by $87,945/kg, my calculation.)

### Example 2. The same object after a spectrum says S-type

- Only the stony branch remains. Diameter 10–23 m (5th–95th), median 15.3 m; mass 1,280–17,100 t, median 4,700 t.
- Metal row: $0.32 M, $0.74 M, $1.3 M, $2.4 M, $5.7 M at the 5th, 25th, 50th, 75th and 95th percentiles.
- By hand at the centre: 4,700 t × $166–484 per tonne = $0.78–2.3 M.
- Water: nothing.
- Chance of no metal: the model says zero. Sources disagree on the class of at least 3 of the 24 classified objects under 6 km/s (plan, 1.2), so the page should print "under 1 in 10, if the class is wrong".

**The tag:** "Metal: almost certainly some. $300 thousand to $6 million in the rock, as grains making up 4 to 18% of the stone. Water: none."

What the spectrum did: removed the zero, removed the top (from $14 M to $6 M), narrowed the range from a factor of 40 to a factor of 18, and left the middle where it was. The remaining width is size (a factor of about 13 in mass), then which chondrite group (a factor of 3), then density (a factor of 2).

### Example 3. A 60 m object with a density ceiling near 5,000 kg/m³

This is the shape of 2001 CQ36 in the plan: two size estimates near 60 m with about 30% errors, class unknown.

By hand:

- Volume at 60 m: (π/6) × 60³ = 113,097 m³. With ±30% on diameter (42–78 m): 38,800–248,500 m³.
- Mass ceiling from the drift: 113,097 × 5,000 = 565,000 t. Without it, solid iron would be 848,000 t.
- If stony at 2,500 kg/m³: 282,700 t × $166–484 = $47–137 M.
- If metal-rich at 4,500 kg/m³ and 75% metal: 381,700 t of metal; at 14.7, 40.8 and 107.9 ppm that is 5.6, 15.6 and 41.2 t of PGMs, or $0.49 B, $1.4 B and $3.6 B at today's prices. The median case holds 2.2 t of iridium, 31% of a year's world supply, so the market cap in Row 1 binds.
- If dark and hydrated at 1,400 kg/m³: 158,300 t; at 6 wt%, 9,500 t of water, about the whole of the 20-year demand forecast (6,000–10,000 t).

From the full draw:

| | No density information | Ceiling at 5,000 kg/m³ |
|---|---|---|
| Share of metal-rich cases | 2.8% | 1.3% |
| Metal row: chance of none | 43% | 43% |
| Metal row, if any: 5th / 50th / 95th | $20 M / $90 M / $600 M | $20 M / $87 M / $420 M |
| Metal-rich cases alone | $0.23 B – $9.7 B | $0.18 B – $7.4 B |
| Mass, 5th–95th | 63,500 t – 1.03 Mt | 63,300 t – 1.00 Mt |
| Water: chance of none; otherwise | 89%; 2,000–54,000 t | the same |

**The tag:** "Metal: 2 in 5 none. Otherwise $20 million to $400 million in the rock. Water: 9 in 10 none; otherwise 2,000 to 54,000 tonnes, more than the forecast market would buy in five years. Brought back: nothing."

What each observation did:

- The **measured size** moved everything up about 50-fold against Example 1 (60 m against a likely 15–17 m is 40 to 64 times the volume) and replaced the brightness-based spread with the stated ±30%.
- The **density ceiling** did little: it halved a 3% branch and took about 30% off the top of the range. It rules out solid iron and not a porous metal-rich body, as the plan already says. The page should state that a ceiling near 5,000 kg/m³ is uninformative for the 97% of cases that were never dense.
- Not modelled: a size from thermal infrared also gives a reflectivity, which would settle dark against bright and so change the class shares. For the real object that reading should be used.

---

## 7. What the typical tag will look like

Stated plainly: for about 94% of the list the tag will be the three sentences of Example 1, with the numbers slid by brightness and nothing else.

| H | Likely mass, t (5th–95th) | Metal, if any (57% of cases) | Water, if any (11% of cases), t |
|---|---|---|---|
| 24.0 | 26,000 – 1.5 M | $7 M – $300 M | 7,000 – 230,000 |
| 25.0 | 6,600 – 380,000 | $2 M – $77 M | 1,700 – 58,000 |
| 26.2 (list median) | 1,300 – 73,000 | $0.4 M – $14 M | 330 – 11,000 |
| 27.7 (median under 5 km/s) | 160 – 9,000 | $45 thousand – $1.8 M | 42 – 1,400 |
| 29.0 | 26 – 1,500 | $7 thousand – $0.3 M | 7 – 230 |

(my calculation; same model.)

- The chances of nothing do not change with brightness in this model. They would only if the class mix is given a brightness dependence.
- For the cheapest targets (median H 27.7) the metal figure is tens of thousands to under two million dollars, in a rock of a few hundred to a few thousand tonnes.
- The whole list's metal row tops out near a few hundred million dollars except for the 1–3% of cases that are metal-rich, and those cannot be identified from Earth.
- Row 3 is the same on every page.

---

## 8. Ways this misleads

1. **A dollar range still invites a quotation of its top end.** "Up to $14 million" will be written. The defences are in 5.4 and are not complete.
2. **"In the rock" is not value.** JORC forbids the figure for that reason. The page prints it to show its size, and must say so.
3. **The water row can out-inflate Asterank.** Uncapped, at $1,000/kg, any 30 m dark rock is "worth $2 billion" and Ryugu "$31 trillion". The price is hypothetical, the market does not exist, and the caps are my choices.
4. **Today's prices are a moving input.** The mixed-PGM price rose 77% between the 2025 average and 20 November 2026 while platinum fell by more than half from its January peak. Iridium, a 7-tonne-a-year market, is half the total.
5. **Meteorites are not asteroids.** Grades come from what survived the atmosphere and was picked up. Weak dark material is under-represented by a factor of 15 or more [S], and iron is over-represented.
6. **The class shares are for brightness-selected surveys of larger objects.** At H above 25 they are extrapolation, and surveys disagree by 10 points or more.
7. **The X-type branch carries almost all the upside and is the least known.** The 38% metal-dominated share is from 29 main-belt bodies tens of kilometres across.
8. **Sizes from brightness were 2 to 3 times too large for both small mission targets later measured directly** (plan, 1.2). A factor of 2.5 in size is a factor of 16 in every figure here.
9. **Two to four meteorites per group** set the stony grades. The spread within a group is wider than my ranges.
10. **The "nothing" definitions are choices.** Counting PGMs in dark rock as nothing for metal is defensible (they are not in separable grains) and debatable. With the other choice the chance of nothing for metal falls from 43% to 17%.
11. **Independence is assumed where it should not be**: grade and density, class and size beyond the reflectivity link.
12. **My model is a sketch.** The reflectivities, their spreads and the flat density ranges are placeholders for the project's own tested size and class model. Tying size to class or not changes the water tonnage twelvefold (Example 1).

---

## 9. Not verified, and open

- Rhodium in chondrites and the element mix in irons rest on recalled CI ratios (Lodders 2003). Cannon's supplementary tables would give the real mix by iron group.
- Metal weight fractions are my conversion from volume fractions; Dunn et al. 2010 and Jarosewich 1990 were not readable.
- Nickel and cobalt contents of meteorites are recalled.
- Launch prices are from a secondary explainer; SpaceX's sheet was unreachable. The $15 M internal cost is press reporting.
- Trading Economics and the two price sites are aggregators. The dealer snapshot (Umicore) is the only primary price read; Johnson Matthey's table failed to load.
- The Psyche origin story is from search summaries.
- The NI 43-101 wording is from a regulator's notice via search, not the rule text.
- Colvin et al. was read as an abstract through a summariser; the journal version may differ.
- Shepard et al. 2015 was read as an abstract. How its 38% transfers to 20 m bodies is unknown.
- The pore-space figures by meteorite class and the direct asteroid densities are from secondary sources, the latter from this project's earlier report.
- Small-body grain and bulk densities for aubrites were not looked up; the E-type row is a judgement.
- I did not find a 2022–2026 hydration survey of near-Earth asteroids, or a peer-reviewed 2024–2026 critique of valuations beyond those listed.
- The 10% market cap, the 2,000 t water cap and the three water price points are proposals.
- Open for Adam: whether the metal row counts only PGMs in metal grains (stricter, 43% nothing) or all PGMs (17% nothing); whether water shows dollars at all; and whether the three axis marks are the right ones.

---

## 10. Sources

Papers and codes

- Cannon, Gialich & Acain 2023, Planet. Space Sci. 225, 105608: https://www.mining.com/wp-content/uploads/2023/04/Precious-and-structural-metals-on-asteroids-.pdf (doi:10.1016/j.pss.2022.105608) [P]
- Horan et al. 2003, Chem. Geol. 196, 5: https://repository.geologyscience.ru/bitstream/handle/123456789/33788/Hora_03.pdf?sequence=1 [P]
- Vernazza et al. 2015, ordinary chondrite parent bodies: https://arxiv.org/abs/1611.08734 [P]
- Dunn et al. 2010 (not readable): https://repository.si.edu/handle/10088/20464
- Gilmour & Herd 2020 (via search): https://cosmochemistry-papers.com/2020/03/04/in-situ-analysis-of-platinum-group-elements-in-equilibrated-ordinary-chondrite-kamacite-and-taenite/ [S]
- Yokoyama et al. 2023 (Ryugu, Ivuna): https://eprints.lib.hokudai.ac.jp/repo/huscap/all/90313/Science.pdf [P]
- Lauretta et al. 2024 (Bennu): https://arxiv.org/abs/2404.12536 [P]
- Lee et al. 2023 (CM water): https://eprints.gla.ac.uk/308855 [S]
- Beck et al. 2021: https://arxiv.org/abs/2011.00279 [P abstract]
- Usui et al. 2019 (AKARI): https://arxiv.org/abs/1810.03828 [P]
- Rivkin & DeMeo 2019: https://arxiv.org/abs/1812.02285 [P]
- Moskovitz et al. 2026 (MANOS colours): https://arxiv.org/abs/2603.15872 [P]
- Shepard et al. 2015 (radar, M class): https://experts.arizona.edu/en/publications/a-radar-survey-of-m-and-x-class-asteroids-iii-insights-into-their/ [P abstract]
- Sanchez et al. 2021 (1986 DA): https://arxiv.org/abs/2109.13950 [S]
- Carry 2012, Density of asteroids: https://arxiv.org/abs/1203.4336 [P]
- Meteorite pore space (via search): https://ntrs.nasa.gov/citations/20230000872 ; https://stars.library.ucf.edu/facultybib2010/1610 [S]
- Elvis 2014: https://arxiv.org/abs/1312.4450 [P]
- Hein, Matheson & Fries 2020: https://arxiv.org/abs/1810.03836 [P]
- Nachtrieb & Smith 2026: https://arxiv.org/abs/2607.06806 [P]; coverage https://phys.org/news/2026-11-asteroid-platinum-good-news-earth.html [S]
- Metzger 2023: https://arxiv.org/abs/2303.09011 [P]
- Kutter 2016, Cislunar-1000: https://sciences.ucf.edu/class/wp-content/uploads/sites/23/2017/02/Cislunar-1000-Transporation-Space-2016.pdf [P]
- Sowers in Space.com, 29 June 2016: https://www.space.com/33297-satellite-refueling-business-proposal-ula.html [P]
- Colvin, Crane & Lal, IAC-19 abstract: https://iafastro.directory/iac/archive/browse/IAC-19/E3/3/54880/ [P abstract]
- Jones et al. (NASA Langley), cost breakeven of lunar propellant: https://ntrs.nasa.gov/api/citations/20205007564/downloads/ISRU-Paper3-Final.pdf [P]
- JORC Code 2012: https://jorc.org/docs/jorc_code2012.pdf [P]
- NI 43-101 notice: https://www.osc.ca/en/SecuritiesLaw_ni_20110408_43-101_repeal-replacement.htm [S]
- Asterank About: https://www.asterank.com/about [P]; code https://github.com/typpo/asterank/blob/master/data/pipeline/run/10_sbdb/scoring.py and https://github.com/typpo/asterank/blob/master/data/pipeline/run/10_sbdb/estimate.py [P]; API https://www.asterank.com/api/asterank [P]
- Psyche figure, coverage: https://space.com/psyche-metal-asteroid-composition ; https://science.howstuffworks.com/psyche-16-asteroid.htm [S]

Prices and markets

- Umicore daily prices, 20 November 2026: https://pmm.umicore.com/en/prices/platinum/ ; https://pmm.umicore.com/en/prices/palladium/ ; https://pmm.umicore.com/en/prices/rhodium/ ; https://pmm.umicore.com/en/prices/iridium/ ; https://pmm.umicore.com/en/prices/ruthenium/ [P]
- Trading Economics: https://tradingeconomics.com/commodity/platinum ; https://tradingeconomics.com/commodity/palladium ; https://tradingeconomics.com/commodity/rhodium ; https://tradingeconomics.com/commodity/nickel ; https://tradingeconomics.com/commodity/cobalt [S]
- Kitco platinum: https://www.kitco.com/charts/platinum [S]
- Iridium and ruthenium cross-checks (via search): https://www.dailymetalprice.com/metalpricecharts.php?c=ir&u=oz&d=10&x=USD ; https://www.cooksongold.com/metalprices/ [S]
- Platinum record, January 2026 (via search): https://platinuminvestment.com/investment-research/perspectives/factors-underpinning-platinums-all-time-high-price-remain-entrenched [S]
- Nickel and cobalt, November and October 2026 (via search): https://www.argusmedia.com/en/news-and-insights/latest-market-news/2902973-lme-futures-prices-mostly-up-in-officials ; https://www.fastmarkets.com/insights/lithium-cobalt-markets-cautious-on-chinas-demand-lme-week-2026/ [S]
- USGS Mineral Commodity Summaries, February 2026: https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-platinum-group.pdf ; https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-nickel.pdf ; https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-cobalt.pdf [P]
- International Platinum Group Metals Association factsheets, May 2026 (SFA Oxford): https://ipa-news.com/assets/pdfs/factsheets/2026-05-ipa-platinum-factsheet.pdf ; https://ipa-news.com/assets/pdfs/factsheets/2026-05-ipa-palladium-factsheet.pdf ; https://ipa-news.com/assets/pdfs/factsheets/2026-05-ipa-rhodium-factsheet.pdf ; https://ipa-news.com/assets/pdfs/factsheets/2026-05-ipa-iridium-factsheet.pdf ; https://ipa-news.com/assets/pdfs/factsheets/2026-05-ipa-ruthenium-factsheet.pdf ; https://ipa-news.com/assets/pdfs/factsheets/2026-05-ipa-osmium-factsheet.pdf [P]
- Johnson Matthey price page (failed to load): https://matthey.com/products-and-markets/pgms-and-circularity/pgm-management
- Launch prices: https://keeptrack.space/deep-dive/how-much-does-a-falcon-9-launch-cost [S]
- Orbit Fab price, 30 August 2022: https://www.orbitfab.com/news/hydrazine-fuel-price/ [P]; status in November 2026: https://newspaceeconomy.ca/2026/11/16/orbital-refueling-propellant-delivery-services.md [S]
- OSIRIS-REx sample mass: https://science.nasa.gov/blogs/osiris-rex/2024/02/15/nasa-announces-osiris-rex-bulk-sample-mass/ ; cost: https://www.planetary.org/space-policy/cost-of-osiris-rex [S]
- Meteorite fall counts: https://en.wikipedia.org/wiki/Meteorite_fall_statistics [S]

This project's earlier reports, used as secondary sources: `docs/research/industry.md`, `docs/research/source-prior.md`, `docs/research/ground-truth.md`, `docs/plan.md`.

Scripts (every parameter they use is in section 5.2):

- data/research/scripts/value_tag.py (worked examples; run with `uv run --no-project --with numpy python value_tag.py`)
- data/research/scripts/asterank_repro.py (reproduces six Asterank values)

Downloaded papers and data (untrusted): data/research/downloads/value
