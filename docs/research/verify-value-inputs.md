# Verification of `value-inputs.md`

Check date: 2026-11-21. Checker's brief: do not trust the report; re-open primary sources; redo the arithmetic; object to the design where it could still mislead.

Tags: **[P]** primary source opened by me today (the paper's own text, the agency or dealer page, the code and the live API). **[S]** secondary source read today. **[R]** recalled only. Result words: confirmed, corrected, refuted, unverifiable.

How I checked: I downloaded about 30 sources afresh into my own folder (not the researcher's copies) and read the passages; I fetched the five Umicore price pages and the Asterank code and API myself; I re-ran the researcher's script; and I wrote an independent Monte Carlo and arithmetic check in separate code.

---

## 1. Verdict

**The sourced numbers are sound. The model numbers reproduce. The design still has four ways to mislead, and three inputs that set the headline figures are placeholders.**

1. **Prices, market sizes, meteorite concentrations, water contents, densities and the Asterank reconstruction are confirmed** against primary sources, with units and dates right. I found no troy-ounce or kilogram slip, and no pure-metal grade applied to bulk rock. Every worked example and every table from the Monte Carlo reproduces in my own code to two significant figures.
2. **Eight errors or overstatements need fixing before anything is displayed** (section 3). The largest: irons are 4.4% of meteorite falls, not 2%; "the only published forecast" of demand for water is one of at least three; the ULA prices are for rocket propellant, not water; the "launch ceiling" of $1,500–3,300/kg uses capacities that the quoted prices do not buy.
3. **Three placeholders control the figures a reader would quote**, and the report's printed ranges do not include them:
   - The top of the metal range ($14 million) is set by the share of metal-rich bodies. Moving one weak input (38% of M-types metal-rich, from 29 large main-belt asteroids) to 10% or 60% moves the top to $8 million or $35 million. Nothing else in the tag moves.
   - The water tonnage is set by the assumed reflectivity of dark objects. The report uses 0.05. The paper it cites for other classes gives 0.13 for near-Earth C-types, which cuts the water by a factor of four. The plan's own size rule cuts it by twelve to twenty.
   - The dollar value of a metal-rich body assumes meteoritic (CI) element proportions. The source for the grades (Cannon et al. 2023) says those proportions fail for irons. Iridium is 52% of the value, and iridium is the element that varies most.
4. **The recommended design is better than Asterank's and still quotable as a point value** (section 4). The "nine cases in ten" range excludes the 43% of zeros, so a reader will add "2 in 5" and "9 in 10" wrongly. Its upper end sits exactly where two unlike populations meet. "None, in the rock" is false for dark asteroids, which hold as much platinum-group metal per tonne as the stony ones. The water row multiplies water bound in rock at the asteroid by a price for refined propellant delivered to low orbit.

**What the typical tag will look like, stated plainly.** For an object known only by brightness H 26.2, on the report's model and 20 November 2026 dealer prices:

- Of 100 such asteroids, 43 hold no platinum-group metal in metal grains (17 hold almost none in any form). About 52 hold between $0.4 million and $14 million of it, in the rock, before any cost. About 3 hold less and about 3 hold more; five in six of those above are the metal-rich cases that cannot be told apart from Earth.
- Said one-sidedly, with the zeros counted: half hold under $0.6 million, three in four under $2 million, nineteen in twenty under $8 million, one in a hundred over $80 million (my calculation from the same model).
- About 89 in 100 hold no bound water. The rest hold 330 to 11,000 t if dark objects are as dark as the report assumes, 80 to 2,700 t at the reflectivity the cited survey gives, and 16 to 1,700 t under the plan's size rule.
- Nothing has been brought back from any asteroid for sale. 121.6 g is the most ever returned.
- Every dollar figure moves by a factor of 1.8 between 2025 average prices and 20 November 2026 prices, and by 3.5% between that morning's dealer quote and that evening's close.

---

## 2. Checks, by area

### 2.1 Prices, 20 November 2026

| Claim in the report | Result | Evidence | Source |
|---|---|---|---|
| Platinum $1,336/troy oz, Umicore 10am price, 20 Nov 2026; November average $1,481.67 | Confirmed [P] | Page reads "20 November 2026 Umicore 10am Price 1,336.0000"; "monthly average 1,481.6667". The same page shows $1,567 on 11 Nov, so the metal fell 15% in nine days. | https://pmm.umicore.com/en/prices/platinum/ |
| Palladium $912; average $1,004 | Confirmed [P] | "912.0000"; "monthly average 1,004.0000" | https://pmm.umicore.com/en/prices/palladium/ |
| Rhodium $8,950; average $9,113 | Confirmed [P] | "8,950.0000"; "9,113.3333" | https://pmm.umicore.com/en/prices/rhodium/ |
| Iridium $10,200; average $10,110 | Confirmed [P] | "10,200.0000"; "10,110.0000" | https://pmm.umicore.com/en/prices/iridium/ |
| Ruthenium $1,900; average $1,943 | Confirmed [P] | "1,900.0000"; "1,943.3333" | https://pmm.umicore.com/en/prices/ruthenium/ |
| $/kg conversions: 42,953; 29,321; 287,749; 327,938; 61,086 | Confirmed (my calculation) | Price × 1000 ÷ 31.1034768 g per troy ounce | – |
| Platinum closed at $1,289.60 on 20 Nov; down 21% in a month; 17-month low | Confirmed [S] | Trading Economics: 1,289.60, −4.30% on the day, −21.17% on the month, "lowest level since mid-June 2025", headline "Platinum Sinks to 17-Month Low". The 10am dealer quote and the close differ by 3.5% on the same day. | https://tradingeconomics.com/commodity/platinum |
| Platinum record "about $2,924" (section 0) and "about $2,923" (section 2.1) on 26 Jan 2026 | Corrected | Spot record $2,923/oz (WPIC; Trading Economics 2,923.70). Futures record $2,878–2,897. The report prints two values. Use $2,923, spot. | https://platinuminvestment.com/investment-research/perspectives/factors-underpinning-platinums-all-time-high-price-remain-entrenched |
| Palladium $893; down 18% in a month, 35% in a year | Confirmed [S] | 893.00; −18.07%; −35.45% | https://tradingeconomics.com/commodity/palladium |
| Rhodium cross-check $9,000 | Confirmed [S] | Headline 8,950 on 20 Nov; page summary text 9,000 | https://tradingeconomics.com/commodity/rhodium |
| Nickel $15,371/t on 20 Nov | Confirmed [S] | 15,370.75 | https://tradingeconomics.com/commodity/nickel |
| Cobalt $33,525/t on 19 Nov, and "$19.50–22.50/lb on 26 Oct (Fastmarkets)" in the same cell | Corrected | Both figures are real (I read both pages), and they disagree: $19.50–22.50/lb is $43,000–49,600/t, 28–48% above $33,525/t. They are different benchmarks (one aggregator's series against a trade-assessed price for standard-grade metal in a Rotterdam warehouse). The report lists them side by side without saying so. The cobalt market is $10.4 B on one and $13–15 B on the other. | https://tradingeconomics.com/commodity/cobalt ; https://www.fastmarkets.com/insights/recycled-battery-metal-markets-battle-headwinds-during-damp-lme-week/ |
| 2025 averages: Pt $1,200, Pd $1,100, Rh $5,800, Ir $4,400, Ru $690 | Confirmed [P] | USGS table, column "2025e" (estimates), footnote: "Engelhard unfabricated metal average annual prices" | https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-platinum-group.pdf |
| Nickel 2025 LME cash $15,000/t; cobalt $15/lb | Confirmed [P] | USGS tables | https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-nickel.pdf ; https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-cobalt.pdf |
| Osmium: no benchmark; "fixed in the 300-400$/oz range since the 2000's" | Confirmed [P] | IPA osmium factsheet, verbatim. Pricing osmium at $400/oz would add 2% to the mixed price. | https://ipa-news.com/assets/pdfs/factsheets/2026-05-ipa-osmium-factsheet.pdf |
| Mixed PGM price $87,945/kg on 20 Nov and $49,590/kg at 2025 averages; iridium half | Confirmed (my calculation) | 87,945; 49,590; ratio 1.773; iridium 51.8%. At the November average the mix is $89,952/kg. | – |
| Kitco bid $1,295 on 21 Nov; iridium $10,150 and ruthenium $1,850 on two price sites; Argus nickel $16,140 on 11 Nov | Unverifiable | Not re-opened. Umicore shows iridium at $10,200 on those days. | – |

Umicore's page carries its own warning: prices "are of pure statistical nature and must be looked at as indications only".

### 2.2 Market sizes

| Claim | Result | Evidence | Source |
|---|---|---|---|
| 2025 primary supply: Pt 178 t, Pd 197 t, Rh about 22 t, Ir about 7 t, Ru about 30 t | Confirmed [P] | "Global production in 2025 stood at 178 tonnes"; "about 197 tonnes"; "about 22 tonnes"; "around 7 tonnes"; "around 30 tonnes" (the ruthenium sheet also says refined output rose "to 31 tonnes in 2025") | IPA factsheets, May 2026: https://ipa-news.com/assets/pdfs/factsheets/2026-05-ipa-platinum-factsheet.pdf (and the palladium, rhodium, iridium, ruthenium sheets at the same address pattern) |
| USGS: Pt 170 t, Pd 190 t; nickel 3.9 Mt; cobalt 310,000 t; reserves over 76,000 t; 140 t recycled | Confirmed [P] | World totals "170,000" and "190,000" kg; "3,900,000"; "310,000"; ">76,000,000" kg; "About 140,000 kilograms of palladium and platinum were recovered globally" | USGS MCS 2026 (three PDFs above) |
| Five PGMs $23.9 B a year; nickel $60 B; cobalt $10.4 B | Confirmed (my calculation) | 7.65 + 5.78 + 6.33 + 2.30 + 1.83 = 23.9 | – |
| Demand 2025: 242 t Pt, 311 t Pd, 33 t Rh | Confirmed [P] | IPA sheets | as above |
| Osmium "hundreds of kilograms per year" | Confirmed [P] | verbatim | IPA osmium sheet |
| 434 t at 3.86 g/t is 112 Mt of ore; a 4,400 t body is 20 minutes of that | Confirmed (my calculation), with a caveat | 112.4 Mt; 20.6 minutes. 3.86 g/t is Cannon's median over "mining projects and exploration targets", not a production-weighted grade. IPA says 10 to 40 t of ore per ounce of platinum, which gives 4 to 17 minutes. "Under half an hour" is safe. | – |
| An independent cross-check | Confirmed | Nachtrieb & Smith 2026, Table III, start from 400 t a year at $60 M/t: $24 B a year. | https://arxiv.org/abs/2607.06806 |

### 2.3 What is in each kind of body

| Claim | Result | Evidence | Source |
|---|---|---|---|
| Cannon et al. 2023 Table 2 percentiles (14.70 … 40.78 … 107.86 ppm; terrestrial 1.07 … 3.86 … 7.36) | Confirmed [P] | Table read in full; all 18 values match | https://www.mining.com/wp-content/uploads/2023/04/Precious-and-structural-metals-on-asteroids-.pdf |
| "upper values because they represent 100% metal content"; range "~6 and 230 ppm"; 300 and 700 ppm "not supported"; "extreme endmember that may not exist in practice"; "no known way to remotely identify"; 50th "a better expectation"; 618 Ir, 548 Pt, 40 Rh measurements; nickel and cobalt "a non-starter" | Confirmed [P] | All found verbatim | same |
| Element mix in iron taken as CI proportions (section 5.2), giving $1,293 / $3,586 / $9,486 per tonne of metal | Corrected | The arithmetic is right. The assumption contradicts the source: "Ru, Rh, and Pt roll over at higher Ir values … such that using chondritic ratios would significantly overestimate PGM grades at the high end of Ir. Pd is inversely correlated with Ir." With iridium 52% of the dollar value, dollars per tonne of iron is not proportional to total PGMs. The spread of the metal-rich branch in dollars is wider than printed, by an amount that needs Cannon's supplementary table. | same, section 3.2 |
| Lognormal fit, median 40.78, sigma 0.78, mean 55 | Confirmed (my calculation) | sigma 0.7775; mean 55.2. The fit gives 78 ppm at the 80th percentile against the table's 91. | – |
| Horan et al. 2003 Table 1 values for the meteorites listed | Confirmed [P] | Every value in the researcher's script matches the table (ppb) | https://repository.geologyscience.ru/bitstream/handle/123456789/33788/Hora_03.pdf?sequence=1 |
| H chondrites "5.2–5.6 ppm" from "Forest Vale, Ochansk, Forest City"; design rule "uniform between the lowest and highest meteorite in each group" | Corrected | Table 1 holds nine H chondrites, not three. With all of them the range is **3.3–6.3 ppm**, $293–582 per tonne (Ceniceros 3.3; Sharps 6.2; Rose City 6.3; one Rose City aliquot of 0.126 g gave 112 ppb Ir against 843 in its replicate). The report used the three equilibrated ones without saying so. Effect on the tag: under 4% (my calculation), because size dominates. Effect on the claim "they show the level, not the spread": the table shows more spread than the report says. Both L chondrites are heavily shocked (S5, S6; Chico is about 60% impact melt); both LL are unequilibrated type 3. | same |
| Rhodium added at 0.30 × Ir; CI values from Lodders 2003 | Confirmed [R], cross-checked | Cannon quotes Ru/Ir = 1.471 from Lodders; the recalled values give 1.472. Rhodium is 14% of the H-chondrite dollar figure. | Cannon et al. 2023 |
| Vernazza et al. 2015 Table 1: metal 8.4 / 4.1 / 2 vol%; iron 28 / 22 / 19 wt% | Confirmed [P] | Table read | https://arxiv.org/abs/1611.08734 |
| Converted to 18 / 9 / 4.5 wt% metal; 29–31, 33–48, 43–52 ppm in the metal | Confirmed (my calculation) | 17.8, 9.1, 4.5. Grain densities are recalled. | – |
| $165–485 of PGMs per tonne of rock; Forest City $484 broken down | Confirmed (my calculation) | 250 + 73 + 69 + 66 + 27 = $484. Top becomes $582 with all H chondrites. | – |
| Yokoyama et al. 2023: Ryugu 6.84 ± 0.34 wt% H₂O (0.30 interlayer, 6.54 structural), H 0.94 ± 0.05 wt%; Ivuna 12.73 ± 0.63 (6.58, 6.15) | Confirmed [P] | All verbatim | https://eprints.lib.hokudai.ac.jp/repo/huscap/all/90313/Science.pdf |
| Lauretta et al. 2024: Bennu 0.84–0.95 wt% H, 4.5–4.7 wt% C | Confirmed [P] | "The sample is hydrated (0.84–0.95 wt.% H) and carbon-rich (4.5–4.7 wt.%" | https://arxiv.org/abs/2404.12536 |
| Lee et al. 2023: CM 1.9–10.5 wt%, mean 7.0 | Confirmed [S] | Abstract via search; the range covers falls and finds together | https://eprints.gla.ac.uk/308855 |
| Beck et al. 2021: 4.5 wt% average, 4 wt% uncertainty | Confirmed [P] | "5.0 wt.% (4.5 wt. %, excluding Ceres)"; "+/- 4 wt.%, 90 % confidence"; range 0 to 11.5 wt% over 20 objects | https://arxiv.org/abs/2011.00279 |
| Rivkin & DeMeo 2019: 30 ± 5%; 39 ± 10%; predicted 17 ± 3% Ch and 43 ± 6% C; observed 9.8 ± 3.3% or 23% of 230; "6% ± 3%"; 16 CM and 45 carbonaceous of 1,153 falls; "main driver of our overall uncertainty" | Confirmed [P] | All found. The same table has one more observed figure the report left out: "Ch fraction of C-complex NEOs … 4% (1 of 23)". | https://arxiv.org/abs/1812.02285 |
| Usui et al. 2019: 17 of 22 C-complex | Confirmed [P] | "Most C-complex asteroids (17 out of 22)" | https://arxiv.org/abs/1810.03828 |
| X split 15/31/53% (71 objects) and 10/32/57% (270) | Confirmed [P, as quoted by Moskovitz et al. 2026] | Verbatim in section 8 of that paper | https://arxiv.org/abs/2603.15872 |
| Reweighting to fixed brightness gives "about 56/33/11" | Corrected (minor) | With the report's own reflectivities (0.45, 0.15, 0.05) and exponent 1.3 I get 59/29/12. | – |
| "M firm" (section 5.2) | Overstated | Both samples are of objects much larger than the list's. Moskovitz's preferred reading of the rising X share at small sizes is more material from primitive families (Veritas, Polana, Eos). No reflectivity-resolved X sample exists at H 24–29. | Moskovitz et al. 2026 |
| S+Q 70% at H 14, 50% at H 22, 35% at H 28 | Confirmed [P] | Verbatim | same |
| Reflectivities "Thomas et al. 2011 values as quoted by Moskovitz" (Q/Sq 0.29, Xk 0.31, B 0.07, D 0.02), and "dark 0.05" | Corrected | The four quoted values are right. Thomas et al.'s own mean for near-Earth C-complex objects is **0.13** (+0.06/−0.05, five objects, range 0.052–0.17) [S, ADS abstract]. At 0.13 a dark object at H 26.2 is 21 m, not 34 m, and holds a quarter of the water: 80–2,700 t (my calculation). | https://ui.adsabs.harvard.edu/abs/2011AJ....142...85T |
| Shepard et al. 2015: 11 of 29 (38%) metal-dominated; 7 of the 11 hydrated | Confirmed [P abstract] | "38% of our sample (11 of 29) have radar albedos consistent with metal-dominated compositions" | https://experts.arizona.edu/en/publications/a-radar-survey-of-m-and-x-class-asteroids-iii-insights-into-their/ |
| 23% × 32% × 38% ≈ 2.8% metal-rich | Confirmed (my calculation); inputs weak | 2.80% | – |
| "Irons are about 2% of observed meteorite falls (49 of 1,102)" | **Refuted** | 49 ÷ 1,102 = 4.4%. The source's own table gives 4.6% (49 of 1,062 classified). Data current to 2012. | https://en.wikipedia.org/wiki/Meteorite_fall_statistics |
| 1986 DA: spectrum fits about 85% metal and 15% pyroxene | Confirmed [P abstract] | "~15% pyroxene and 85% metal" | https://arxiv.org/abs/2109.13950 |
| Carry 2012 Table 2 (meteorite densities) and Table 3 (S 2.72 ± 0.54, C 1.33 ± 0.58, Ch 1.41 ± 0.29, B 2.38 ± 0.45, X 1.85 ± 0.81, Xe 2.60 ± 0.20, Xk 4.22 ± 0.65, Xc 4.86 ± 0.81); near-Earth asteroids "seem to have a lower density" | Confirmed [P] | All values match. Not said in the report: the Xe figure rests on one asteroid, Xc on two, Xk on three. | https://arxiv.org/abs/1203.4336 |
| Nickel and cobalt contents of meteorites | Unverifiable | Recalled in the report; not checked by me | – |
| Class shares for H 24–29 from `source-prior.md`; "C stays near 10–15%" | Unverifiable | The project's own report; Moskovitz gives no number for C in the text | – |

### 2.4 Water in space and launch cost

| Claim | Result | Evidence | Source |
|---|---|---|---|
| ISS water 3.3 t for about $33 M a year (about $10,000/kg); Elvis $5,000/kg in low orbit and double at geostationary; launch "~US$10 k or more" in 2000 dollars; "would lose value if lower launch costs/kg emerge" | Confirmed [P] | All found | https://arxiv.org/abs/1312.4450 |
| Kutter 2016: $3 M, $1 M, $0.5 M per ton in low orbit, geostationary orbit, on the Moon; "makes no claim" | Confirmed [P], with a correction of kind | "propellant is purchased in LEO for $3M/ton, or GEO for $1M/ton or at the moon for $0.5M/ton". **It is a price for liquid oxygen and hydrogen propellant, not water.** The same paper: "we need to mine about 1.5 tons of water for each ton of propellant" and "we need to produce 5 tons of propellant on the moon for every ton needed in LEO". Its 2016 launch cost was "$4,000 to $10,000 per kilogram". | https://sciences.ucf.edu/class/wp-content/uploads/sites/23/2017/02/Cislunar-1000-Transporation-Space-2016.pdf |
| Sowers, Space.com, 29 June 2016: $3,000, $1,000 (L1, from talks with asteroid miners), $500 per kg | Confirmed [P for the article] | Each figure is for "propellant"; the article gives no price for water | https://www.space.com/33297-satellite-refueling-business-proposal-ula.html |
| "ULA's 2016 offer" (section 5.1) | Overstated | It was the break-even price in a business case for a stage (ACES) that ULA stopped developing in 2020 [S]. No offer is in force. | https://en.wikipedia.org/wiki/Advanced_Cryogenic_Evolved_Stage |
| Asterank "cost_to_orbit" 2,200 | Confirmed [P] | `estimate.py` | https://github.com/typpo/asterank/blob/master/data/pipeline/run/10_sbdb/estimate.py |
| Hein et al. 2020: water $20,000/kg, 5% yield, 150 kg, 5.9 years; platinum $40,449/kg and 254,582 kg | Confirmed [P] | Table 1 and section 3.3 | https://arxiv.org/abs/1810.03836 |
| Colvin, Crane & Lal: 6,000–10,000 t over 2030–2050, about $15 B; $2,000–3,000/kg to low orbit; $900–5,000/kg | Confirmed [S, abstract read through a summariser] | The demand is for propellant. The abstract gives no figure per year. | https://iafastro.directory/iac/archive/browse/IAC-19/E3/3/54880/ |
| "the one published demand forecast is 300 to 500 t a year from 2030 [P abstract]"; "the only published forecast" (section 5.1) | **Refuted** | 300–500 t a year is the researcher's division, not the paper's. And it is not the only forecast. Kutter 2016 sizes a plant for 210 t of propellant a year in low orbit, 1,050 t produced on the Moon and 1,575 t of water mined [P]. Jones et al. model 59 t a year for 14 years [P]. Kornuta et al. 2019 are quoted by a search summary as giving "450 metric tons of lunar derived propellant equating to 2450 metric tons of processed lunar water generating $2.4 billion of revenue annually" [S; I could not open a page carrying that sentence, the record below confirms only the paper]. All are proponents' or planners' scenarios; none is an order. | Kutter and Jones as above; https://www.osti.gov/biblio/1503160 (Kornuta record) |
| Jones et al.: lunar propellant "97% more expensive"; 59 t a year for 14 years | Confirmed [P] | Verbatim | https://ntrs.nasa.gov/api/citations/20205007564/downloads/ISRU-Paper3-Final.pdf |
| Metzger 2023: $2,000/kg; $30/kg; $119 and $436/kg | Confirmed [P] | "L0 = $2,000/kg"; "$119/kg and $436/kg to LEO, respectively" | https://arxiv.org/abs/2303.09011 |
| Orbit Fab, 30 Aug 2022: $20 M for up to 100 kg of hydrazine in geostationary orbit | Confirmed [P] | Page read; first availability stated as 2025 | https://www.orbitfab.com/news/hydrazine-fuel-price/ |
| No Orbit Fab delivery by November 2026 | Unverifiable | I found no report of a delivery and none of its absence | – |
| Falcon 9 list price $74 M in 2026, $70 M in 2025, $67 M in 2022, for up to 5.5 t to transfer orbit; Falcon Heavy $97 M; rideshare $6,500/kg; $15 M internal cost | Confirmed [S] | The explainer says these; a search confirms Spaceflight Now reported the 2026 price. SpaceX's sheet did not load for me either. The $15 M is an outside estimate. | https://keeptrack.space/deep-dive/how-much-does-a-falcon-9-launch-cost |
| "$3,250 at the 22.8 t expendable capacity"; ceiling "about $1,500–3,300/kg today" | Corrected | The arithmetic is right (74 ÷ 22.8 = 3,246; 97 ÷ 63.8 = 1,520). Both capacities are SpaceX's expendable figures [S]; the list prices are for flights that recover the boosters. The report says this for Falcon Heavy and not for Falcon 9. At about 17.5 t with recovery [R] the Falcon 9 figure is about $4,200/kg. On reported cost it is under $1,000. An honest statement is "roughly $1,000 to $4,000 per kg, depending on whether price or cost is meant, and none of it delivered to a customer's tank". | https://www.spacex.com/vehicles/falcon-9/ |
| Starship "stated targets $100–200/kg" | Unverifiable as a price | A target by the company. A July 2026 statement puts it "well below $100" with full reuse; one unconfirmed report of a $90 M contract works out near $600/kg [S]. | – |
| Year-dollars | Not handled in the report | The table sets 2000-dollar, 2011, 2016, 2019, 2022 and 2023 figures side by side. $3,000 in 2016 is about $4,200 in 2026 dollars (ratio about 1.39, unofficial calculators [S]). | – |

### 2.5 Earlier valuations

| Claim | Result | Evidence | Source |
|---|---|---|---|
| Asterank formula, tables, constants, the π r³ volume and the ÷6 × 10¹⁵ | Confirmed [P] | Code read in full. In Python 2, `4/3` is 1. Code mass ÷ true sphere mass = (10¹⁵ ÷ 6) ÷ (4/3 × 10¹²) = 125 exactly. | https://github.com/typpo/asterank/blob/master/data/pipeline/run/10_sbdb/scoring.py |
| The five values and "reproduces to every digit" | Confirmed [P], independently | I queried the live API and recomputed in my own code: Ryugu 82,756,156,358.85; Bennu 669,957,009.28; Didymos 62,253,881,855.74; Davida 1.5383 × 10¹⁹; Psyche 27,673,419,946.67. All equal the API's values to the last digit. C-type $0.0086213/kg, hydrogen 99.71%; X $0.0010022/kg, cobalt 99.78%. | https://www.asterank.com/api/asterank |
| "platinum plays no part" | Corrected (minor) | True for C, X, Xe and Xk. The table gives Xc 0.005% platinum (9% of its value) and O 1.25% platinum, at the code's "$2 per kg". | `estimate.py` |
| About page: "Mining costs are factored in as a flat percentage of potential value"; "The overwhelming majority of asteroids have no spectral classification" | Confirmed [P] | Both verbatim | https://www.asterank.com/about |
| Psyche "$10,000 quadrillion" is Elkins-Tanton's own, from 2017, and she calls it meaningless | Confirmed [S] | Coverage read via search; one outlet prints $100,000 quadrillion | https://science.howstuffworks.com/psyche-16-asteroid.htm |
| Elvis 2014: 2.36 million t; 23.6 t; $1.18 B; $0.8–8.8 B; 50 m body $150 M; 4% M-type, halved; "ore" definition | Confirmed [P] | All found. His $50,000/kg is "approximate present Pt prices" of 2013. | https://arxiv.org/abs/1312.4450 |
| Nachtrieb & Smith 2026: "100 ppm to as high as 187 ppm"; trillions; price falls by over 75% | Confirmed [P], one part unverifiable | Table III: price 60 to 11 M$/t (−82%). "15 years" is not in the text I could read. It is a preprint in physics.soc-ph, not peer reviewed. | https://arxiv.org/abs/2607.06806 |
| JORC Code 2012, clause 51 | Confirmed [P] | Quotation is accurate. Two notes. The last sentence ("little or no relationship to economic viability…") is guideline text, not Code text. The 2012 edition is still the one in force; a "JORC Code 2026" was in final approval in 2026 with no effective date as of the committee's August 2026 update, so the clause number may change. | https://jorc.org/docs/jorc_code2012.pdf ; https://www.jorc.org/code-update |
| NI 43-101 paragraph 2.3(1)(c) "restricts" gross-value disclosure | Confirmed [S] | The wording is "must not disclose … the gross value of metal or mineral in a deposit". A replacement instrument was proposed in June 2025; I did not find its status. | https://www.osc.ca/en/SecuritiesLaw_ni_20110408_43-101_repeal-replacement.htm |
| "I found no peer-reviewed critique of asteroid valuations" for 2024–2026 | Partly | Not a critique of valuations, but missed: Trigo-Rodríguez et al., accepted by MNRAS in late 2025, on the mining potential of carbonaceous-chondrite parent bodies. Its abstract is hedged ("might be promising"); its press release says mining them is "far from viable" [S]. | https://arxiv.org/abs/2510.27373 |
| A valuation the report did not list | Added | Sanchez et al. 2021, the paper the report cites for 1986 DA's composition, also prices it: "1986 DA could be worth a total of ∼$11.65 trillion", using Kargel's "good 90th percentile" grades (the practice Cannon criticises), a surface density assumed for the whole body, and Kargel's price-deflation rule p′ = p (P′/P)^−0.60 [P]. That rule is a published alternative to the report's arbitrary 10% market cap. | https://arxiv.org/abs/2109.13950 |
| Gilmour & Herd 2020; Kargel's LL figures; Lewicki et al. 2021; Alarcón et al. 2026 | Unverifiable | Secondary in the report; not re-opened | – |

### 2.6 Densities and returned mass

| Claim | Result | Evidence | Source |
|---|---|---|---|
| Sphere masses and volumes in section 4 and the examples | Confirmed (my calculation) | 1,767 m³; 3,004 / 4,418 / 6,008 t; 552 t; 35,343 t; 113,097 m³; 565,487 t | – |
| Implied voids: Itokawa 41%, Didymos 21%, Dimorphos 53%, Bennu/Ryugu 47% or 26% | Confirmed (my calculation) | From the stated densities | – |
| Direct densities (Itokawa 1.90, Bennu 1.19, Ryugu 1.19, Eros 2.67, Didymos 2.60, Dimorphos 1.54) and the decametre set | Unverifiable today | Not re-opened. The first four match my recall. The Didymos pair is one 2026 model-dependent result that Hera, now in orbit there, will replace. | project's `ground-truth.md` |
| "A fast spin excludes loose rubble, so a measured period under about two hours pushes a body toward the upper half of its row" | **Refuted by the report's own table** | The report gives no source. Its section 4 lists 2011 MD at 1.1 g/cm³ with at least 65% voids; that object turns in about 12 minutes [R]. Small cohesion holds a fast-spinning rubble pile together. | – |
| Most asteroid material ever returned is 121.6 g | Confirmed [P] | "the bulk Bennu sample mass totals 4.29 ounces (121.6 grams)"; the requirement was 60 g. This is the returned and weighed mass, not a collected estimate. | https://science.nasa.gov/blogs/osiris-rex/2024/02/15/nasa-announces-osiris-rex-bulk-sample-mass/ |
| "a mission costing about $1 billion" | Confirmed [S] | $1.02 billion over the mission's life, not adjusted for inflation | https://www.planetary.org/space-policy/cost-of-osiris-rex |
| Expiry of that record | Added | Tianwen-2 reached Kamoʻoalewa on 4 July 2026, has not reported a sample, plans at least 100 g and a capsule landing on 29 November 2027 [S]. The figure needs an "as of" date. | https://en.wikipedia.org/wiki/Tianwen-2 |

---

## 3. Arithmetic and logic

I re-ran the researcher's `value_tag.py` (it prints the report's numbers) and wrote `vv_check.py` and `vv_mc.py` independently (one million draws, different random stream, rejection instead of reweighting for the density ceiling).

**Reproduced, no error found:**

- Every hand calculation in sections 0, 2.2 and 6.
- Example 1: chance of none 42.6%; $0.36 M / $0.87 M / $1.7 M / $3.3 M / $14.5 M; water chance of none 88.8%, 331–11,100 t. All-cases mean $4.2 M, 68% of it from the metal-rich 2.8%. Water mean 381 t, $381 M at $1,000/kg.
- Example 2: $0.32 M to $5.7 M; diameter 10–23 m.
- Example 3: $20 M / $89 M / $595 M without the ceiling; $20 M / $87 M / $424 M with it; metal-rich share 2.8% to 1.3%.
- The response table (5.6), the plan-rule comparison ($0.15 M–$18 M; 16–1,670 t) and the brightness table (section 7).

**Errors:**

1. **Irons in falls: "about 2% (49 of 1,102)".** 49 ÷ 1,102 is 4.4%. The cross-check on the 2.8% metal-rich share still holds loosely, and Elvis's "comparable to that in meteorite falls" is the better-sourced statement.
2. **"under 1 in 10, if the class is wrong" (Example 2)**, argued from "at least 3 of the 24" disagreeing. 3 ÷ 24 is 12.5%, more than 1 in 10, and "at least". The printed chance is not supported by the figure given for it.
3. **Nickel and cobalt "worth less per kilogram than 1% of the cost of putting a kilogram into orbit".** Cobalt at $33.5/kg is more than 1% of $3,250, and both exceed 1% of $1,520. The comparison is also the wrong one for a return scenario.
4. **Launch ceiling.** $74 M ÷ 22.8 t divides a recovered-booster price by an expendable capacity. The report flags this for Falcon Heavy and not for Falcon 9, then builds "about $1,500–3,300/kg" from both.
5. **H-chondrite range.** The rule "lowest and highest meteorite in each group" was applied to three of the nine H chondrites in the cited table. Stated range 5.2–5.6 ppm; table range 3.3–6.3 ppm.
6. **X split at fixed brightness.** 56/33/11 printed; 59/29/12 from the stated inputs.
7. **Platinum record** printed as both $2,924 and $2,923.
8. **Colvin tagged "[P abstract]" for "300 to 500 t a year".** The abstract has no annual figure, and the tonnes are propellant.
9. **Water row units.** Tonnes of water bound in rock are multiplied by prices for refined propellant delivered to low orbit or L1. By the source's own ratios that overstates by 1.5 before transport and by about 7.5 after it (1.5 t of water per tonne of propellant; 5 t produced per tonne delivered, for the Moon).
10. **"Narrowed from a factor of 40 to a factor of 18" (Example 2).** That depends on the report's placeholder size spread (10–23 m). Under the plan's size rule (7.5–30 m) an S-type spans $0.14 M to $11 M, a factor of about 80 (my calculation). The plan also records that brightness-based sizes were 2 to 3 times too large for both small targets later measured.

**Sensitivities the report did not run (my calculation, same model otherwise):**

| Change | Metal, 5th–95th if any | Water, 5th–95th if any |
|---|---|---|
| As printed | $0.36 M – $14.5 M | 331 – 11,100 t |
| Metal-rich share of M-types 10% instead of 38% | $0.36 M – $8.4 M | same |
| Metal-rich share 60% | $0.36 M – $35 M | same |
| Dark reflectivity 0.13 instead of 0.05 | same | 80 – 2,740 t |
| Plan's size rule for every class | $0.15 M – $18 M | 16 – 1,670 t |
| All nine H chondrites | $0.35 M – $14.3 M | same |
| Density ceiling 5,000 kg/m³ at H 26.2 | $0.35 M – $8.9 M | same |

The lower end and the middle are stable. The top of the metal range and the whole water range are not.

---

## 4. Objections to the recommended design

1. **The "nine cases in ten" range will be added to "2 in 5" wrongly.** The range is conditional on there being something. It covers 51% of all cases, not 90%. Print one denominator: "Of 100 such asteroids: 43 none; 52 between $0.4 million and $14 million; 3 less; 3 more."
2. **The upper end is the least stable number in the tag and the one that will be quoted.** 2.9% of all cases exceed $14 million and 84% of those are metal-rich. The 95th percentile sits on the join between two unlike populations, so it swings from $8 million to $35 million on one weak input. Show the two populations as two bars: the ordinary case (about 55 in 100, $0.3–6 million) and the metal-rich case (about 3 in 100, $9–330 million, cannot be identified from Earth).
3. **Withholding every central value makes the top the headline.** With no "typical" figure on the page, "up to $14 million" is the only thing left to quote. A one-sided statement cannot be turned into "worth $X": "3 in 4 hold less than $2 million; 19 in 20 less than $8 million; 1 in 100 more than $80 million." These count the zeros.
4. **"None … in the rock" is false for dark asteroids.** CI and CM meteorites carry 2.9–4.0 ppm, more than LL chondrites. The row drops them on a recoverability test (not in metal grains) while its label says "in the rock". With all PGMs counted the chance of none is 17%, not 43%. Pick one and name it: "in metal grains" or "in the rock".
5. **The page prints the figure JORC clause 51 prohibits, with a dollar sign beside each asteroid.** The stated defence (the range shows how small it is) holds only if the reader also sees a cost. Lead with kilograms and tonnes. Give dollars as a second line labelled "metal content at list prices", never "worth" or "value".
6. **Cost marks on the same axis invite subtraction.** A range ending at $14 million to the right of a "$10 million probe" mark reads as profit. That mark is a company's stated build cost for a 200 kg prospecting spacecraft that has not flown (its predecessor was lost within days) [S, the project's `industry.md`], and it is not a mining mission. Keep the $1 billion mark, which is a real mission that returned 121.6 g, and drop or relabel the other.
7. **One day's dealer quote is too fragile to be "the price".** On the chosen day platinum fell 3.5% between the 10am quote and the close; it had fallen 15% in nine days and 54% from January's record. Iridium and ruthenium stood at 2.3 and 2.8 times their 2025 averages. Use a stated multi-year band (low, average, high) and let it widen the range, or at least the month's average. Say on the page that half of the dollar figure is iridium, a 7-tonne-a-year market with no exchange price.
8. **The metal-rich branch is priced with element proportions its own source rejects.** Fix this from Cannon's supplementary data before any metal-rich figure is displayed, or show that branch in kilograms only.
9. **The water row should not carry dollars.** Its tonnage moves by a factor of four to twenty on the size model. Its prices are for propellant, in 2016 dollars, from a business case whose vehicle was never built. Its cap rests on a claim ("the only forecast") that is wrong. Capped at 2,000 t the row still prints "$1–6 billion" at $3,000/kg, and that number is nothing more than cap times price. Show tonnes, and beside them a physical comparison: the space station received 3.3 t in a year; the published scenarios run from 59 to 500 t a year of propellant.
10. **"$100/kg" as a named price point is a company's target presented as a scenario.** If kept, label it "not achieved".
11. **Row 3 says what 121.6 g "would fetch".** It would not fetch 44 cents. Meteorites and returned samples sell or are held for far more than their metal [R]. Say "contains 44 cents of platinum-group metal". The $26 water figure puts a hypothetical price into the one row described as not hypothetical. Add "as of" and the date, since a second sample is due in November 2027.
12. **The fixed axis from $1 to $1 trillion makes a factor-of-40 range look narrow** (1.6 of 12 decades) and leaves nine empty decades pointing at "trillion". Consider ending the axis where the list's largest case ends.
13. **"Almost certainly some" for an S-type reads as good news.** It means mine-grade rock (2–6 ppm) with the metal as grains making up 4–18% of the stone. Moskovitz et al. also show that colour classes shift at small sizes (shock darkening can move S to X or C), so the stated chance of a wrong class needs its own tested number.
14. **The spin rule should go.** The report gives no source for "fast spin pushes density up", and its own table contradicts it.
15. **The 10% market cap is arbitrary.** A published deflation rule exists (Kargel 1994, as used by Sanchez et al. 2021). Either would be a choice; the page should say which and why.
16. **Whole-number frequencies overstate what is known.** "2 in 5" rests on class shares that surveys put 10 points apart, and S+Q falls from 50% at H 22 to 35% at H 28 while the model holds the mix fixed. Print the chance as a band ("between 1 in 3 and 1 in 2") until the project's own prior is tested.

Parts of the design I checked and would keep: the three levels (in the rock, separable at best, recovered by anyone); no ranking by dollars; no field named value; physical units beside dollars; the price date inside the sentence; the old range shown behind the new; saying when an observation widens the range.

---

## 5. Not verified

- The second-source price checks (Kitco, two iridium and ruthenium sites, Argus nickel).
- Gilmour & Herd 2020, Kargel's LL figures, Lewicki et al. 2021, Alarcón et al. 2026.
- Nickel and cobalt contents of meteorites; grain densities used in the metal conversion; pore-space figures.
- Direct asteroid densities and the decametre set (taken from the project's earlier report).
- Whether 1986 DA is the only radar-confirmed metal-rich near-Earth asteroid.
- Whether Orbit Fab has delivered fuel; any Starship price.
- "15 years" in Nachtrieb & Smith.
- The class shares from `source-prior.md`, the 94% figure and the list medians from `plan.md`.
- The Falcon 9 payload with booster recovery (about 17.5 t) is my recall.
- Kornuta et al. 2019: the quoted sentence came from a search summary; no page I could open carried it. Thomas et al. 2011 was read as an abstract through search, not as the full paper.

---

## 6. Files

- My scripts: data/research/scripts/vv_check.py , data/research/scripts/vv_mc.py , data/research/scripts/vv_mc2.py (run with `uv run --no-project --with numpy python <file>`).
- My downloads (untrusted): data/research/downloads/verify-value
- Report checked: docs/research/value-inputs.md
