# Verification of `capability.md` (the "bring it back" rung)

Checked on 2026-11-21 (a Saturday) by a sceptical checker. The report under test is `capability.md` in this folder.

## 0. Verdict

**The facts mostly hold. The display wording does not yet.**

- Of the 71 claims in the tables below, 54 were confirmed at a source I opened today (primary where one exists, secondary where marked), 7 needed a correction, 1 is refuted by the report's own sources, and 9 could not be confirmed in whole or in part. None of these reverses a conclusion.
- Every calculation was redone. Three small slips were found. None changes a number by more than a rounding step, except one example that mixes a 65 m object with the mass of a 60 m one.
- The main problems are in section 7 of the report, the text the site would print. Several of its sentences can still be quoted as point values or read as more than the sources say. Section 4 below lists 18 objections, and section 5 gives a replacement site-wide statement.

The three corrections that matter most:

1. **OSIRIS-REx's cost has two published totals from the same organisation**: $1.02 billion and $1.16 billion. Cost per gram is $8.4 to 9.5 million in the money of the day, and more in 2026 dollars. The site should print "about ten million dollars a gram", not "$8.4 million".
2. **"Designed on paper since 2012" is wrong by the report's own sources.** Sonter proposed returning 1,000 tonnes in 1997 and 1998. 2012 is the first costed study.
3. **"One is trying now" overstates Tianwen-2.** The spacecraft arrived 20 km from the asteroid in early July 2026. No sampling attempt has been reported, and no official source gives a date for one.

How each source was read:

- **P**: primary source opened by me today.
- **S**: secondary source opened by me today (press, encyclopedia, or a search summary where the page would not load).
- **L**: a copy of the primary saved earlier today by the researcher or the earlier verifier, read by me. Where I could download my own copy the file hashes matched, and those are marked P.
- **R**: recalled, not read today.

My script: `data/research/scripts/vc_arith.py`.

## 1. Claim checks

### 1.1 Sample returns

| # | Claim in the report | Result | Evidence | How read |
|---|---|---|---|---|
| 1 | OSIRIS-REx returned 121.6 g; requirement 60 g | Confirmed | "the bulk Bennu sample mass totals 4.29 ounces (121.6 grams)"; "at least 60 grams"; "NASA will preserve at least 70% of the sample". So about 36 g is open for analysis now. https://science.nasa.gov/blogs/osiris-rex/2024/02/15/nasa-announces-osiris-rex-bulk-sample-mass/ | P |
| 2 | Hayabusa2 returned 5.424 ± 0.217 g; requirement 0.1 g | Confirmed | JAXA curation: "5.424±0.217 g". Review: "minimum mission requirement was to return 100 mg". https://curation.isas.jaxa.jp/en/sample-curation/ryugu/ ; https://arxiv.org/abs/2604.22182 | P |
| 3 | Hayabusa: more than 1,500 particles; mass not recorded; "under 1 mg" | Confirmed, soft | Review: "An exact mass ... is not recorded, but an approximate value is 100µm" (a misprint). "Less than 1 milligram" is a conference tweet relayed by the Planetary Society, 16 March 2011. NASA's page still says "less than one gram". https://www.planetary.org/articles/2960 ; https://science.nasa.gov/mission/hayabusa/ | P, S |
| 4 | OSIRIS-REx cost $1.02 billion, not inflation-adjusted | **Corrected to a range** | The cost page says "$1.02 billion (not adjusted for inflation) over its lifetime". The same society's mission page says "projected to cost $1.16 billion over 15 years". Neither page says whether the extended mission is inside. Cost per gram: $8.4 million or $9.5 million. https://www.planetary.org/space-policy/cost-of-osiris-rex ; https://www.planetary.org/space-missions/osiris-rex | S, S |
| 5 | Launch service $183.5 million | Confirmed (secondary) | NASA release of 5 August 2013, read as a search summary: "valued at about $183.5 million". https://www.nasa.gov/news-release/nasa-selects-launch-services-contract-for-osiris-rex-mission | S |
| 6 | Hayabusa2 total project cost ¥28.9 billion, a 2012 plan figure | Confirmed | MEXT sheet: "総事業費289億円", fiscal years Heisei 22 to 33 (2010 to 2021). File dated 16 August 2012. https://www8.cao.go.jp/space/comittee/dai2/siryou2-17.pdf | P |
| 7 | Hayabusa cost about ¥20 billion, "the project leader's figure" | **Corrected (attribution)** | AFP: "costing less than 200 yen (two dollars) per Japanese citizen over 10 years (20 billion yen)". The sentence sits in a passage about Kawaguchi, but the bracketed figure is the reporter's. Call it a press figure. https://phys.org/news/2010-12-japan-low-cost-space-programme-limits.html | S |
| 8 | Launch and return dates; 7.1, 6.0, 7.0 years | Confirmed | Hayabusa 9 May 2003 to 13 June 2010 (NASA page). Hayabusa2 3 December 2014 to 6 December 2020 (JAXA). OSIRIS-REx 8 September 2016 to 24 September 2023 (press kit). https://global.jaxa.jp/projects/sas/hayabusa2/ ; https://science.nasa.gov/wp-content/uploads/2023/09/osirisrexpresskit-2023.pdf | P |
| 9 | Itokawa 535 × 294 m, mean 330 m, 12.1 h; Ryugu about 1 km, 7.6 h; Bennu about 500 m, 4.3 h | Confirmed | JPL database: Itokawa 0.33 km, 12.132 h; Ryugu 0.896 km, 7.633 h; Bennu 0.484 km, 4.296 h. The two recalled values are right. https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=25143&phys-par=1 | P |
| 10 | Apollo returned 382 kg | Confirmed | "382 kilograms (842 pounds)", six missions, 1969 to 1972. https://curator.jsc.nasa.gov/lunar/ | P |
| 11 | Apollo cost $25.8 billion then-year, $309 billion in 2025 dollars | Confirmed, with a flaw in the source | Main text gives both figures. The page's table footnote still says 2020 dollars. https://www.planetary.org/space-policy/cost-of-apollo | S |
| 12 | Luna 101 g, 55 g, 170.1 g; the Smithsonian total of 226.1 g is a slip | Confirmed | The page prints all four numbers; the three sum to 326.1 g. https://airandspace.si.edu/stories/editorial/revisiting-soviet-lunar-sample-return-missions | S |
| 13 | Chang'e-5 1,731 g; Chang'e-6 1,935.3 g | Confirmed | CNSA, 19 December 2020: "about 1,731 grams". State Council, 28 June 2024: "1,935.3 grams". https://www.cnsa.gov.cn/english/n6465652/n6465653/c6810963/content.html ; https://english.www.gov.cn/news/202406/28/content_WS667e2277c6d0868f4e8e8a54.html | P |
| 14 | OSIRIS-REx capsule about 50 kg; spacecraft 2,110 kg at launch | Confirmed | Press kit: capsule "About 110 pounds (50kg)"; "Wet Mass (fueled) at launch was: 4,650 pounds (2,110 kg)"; dry mass 880 kg. Same URL as row 8. | P |
| 15 | Hayabusa2 launch mass about 600 kg | Confirmed | "Approx. 600kg". https://global.jaxa.jp/projects/sas/hayabusa2/ | P |
| 16 | MMX launched 20 October 2026; Phobos sample due 2031 | Confirmed | ESA and Space.com, read as search results: lift-off 04:41 Japan time on 20 October 2026. https://www.esa.int/ESA_Multimedia/Images/2026/10/MMX_lifts_off_to_Mars_s_moon_Phobos | S |

### 1.2 Tianwen-2

| # | Claim | Result | Evidence | How read |
|---|---|---|---|---|
| 17 | Launched 29 May 2025 Beijing time; 20 km from the asteroid since early July 2026 | Confirmed, wording too strong | CNSA release dated 6 July 2026: reached "距离小行星20千米处"; image of 2 July from about 20 km. It shows arrival. Nothing I found says the craft is still at 20 km in November. https://www.cnsa.gov.cn/n6758823/n6758838/c10760422/content.html | P |
| 18 | Kamoʻoalewa is 18 ± 2 m and turns every 27.9 minutes | Confirmed | "mean diameter of D=18±2 m"; "rotation period of 27.9 minutes" (JWST, February 2026). Press still prints 27 m (Sky & Telescope, 9 July 2026). JPL's database gives 0.467 h. https://arxiv.org/abs/2606.24017 | P |
| 19 | Sample target about 100 g | Confirmed (secondary) | Shanghai Observer: "此次采样目标约为100克". Wikipedia: "≥100 g", citing a Chinese engineering paper. No CNSA page found. https://news.qq.com/rain/a/20260707A01T5Y00 ; https://en.wikipedia.org/wiki/Tianwen-2 | S |
| 20 | Capsule due late November 2027 | **Unverifiable at a primary source** | Sky & Telescope: "by late November 2027". Wikipedia: 29 November 2027, departure 24 April 2027. The Shanghai Observer article says only "about three years later". No CNSA date. https://skyandtelescope.org/astronomy-news/tianwen-2-arrives-at-quasi-moon-kamo%CA%BBoalewa-returns-images/ | S |
| 21 | No descent or sampling reported as of 21 November 2026 | Confirmed as far as a search can | An extended search today found no report. Wikipedia: the craft is "scouting for a sampling site". https://en.wikipedia.org/wiki/Tianwen-2 | S |
| 22 | Three sampling modes; attach would be a first | Confirmed (secondary) | "触碰、悬停、附着三套采样模式"; attach is called the main plan. Same Shanghai Observer URL. | S |

### 1.3 Contact with small bodies

| # | Claim | Result | Evidence | How read |
|---|---|---|---|---|
| 23 | NEA Scout: no contact after launch on 16 November 2022 | Confirmed | "After launch, the project team was not able to communicate with the spacecraft." The page does not give the target's size; "under 18 m" was not re-read. https://science.nasa.gov/mission/nea-scout/ | P |
| 24 | ESO on 1998 KY26: 11 m, five minutes, "first time a space mission encounters a tiny asteroid" | Confirmed | Release of 18 September 2025. https://www.eso.org/public/news/eso2515/ | P |
| 25 | Hayabusa2 dropped 1998 KY26 in November 2026; flyby of 2015 BM510 in April 2028 | Confirmed | Japanese press on a JAXA report of 16 November 2026 and a briefing on the 17th; Space.com: "No more asteroid landing". https://sorae.info/astronomy/20261118-hayabusa2.html ; https://news.mynavi.jp/techplus/article/20261121-5374323/ | S |
| 26 | Philae: thruster, harpoons and screws all failed; 80% of first sequence | Confirmed | "the harpoons themselves did not fire"; "did not secure itself to the comet, and it bounced"; "completed 80%". https://www.esa.int/About_Us/ESAC/Rosetta_and_Philae_one_year_since_landing_on_a_comet | P |
| 27 | Bennu: arm "sank 1 1/2 feet into it within seconds" | Confirmed | University of Arizona, 7 July 2022. https://news.arizona.edu/news/osiris-rex-scientists-taking-asteroid-sample-was-punching-ball-pit | P |
| 28 | Hayabusa touchdown: half an hour on the surface, emergency ascent, projectiles probably not fired, MINERVA lost | Confirmed | NASA page: "remained on the surface for about half an hour"; "it is not clear that the bullets were fired". https://science.nasa.gov/mission/hayabusa/ | P |
| 29 | MINERVA-II1 "the first probes ever to travel the surface of an asteroid"; a third rover failed before release | Confirmed | Wikipedia; the third "failed before deployment, but was released ... anyway". https://en.wikipedia.org/wiki/MINERVA-II | S |
| 30 | DART struck Dimorphos (160 m) on 26 September 2022 at about 6 km/s | Confirmed | NASA page gives the date and "530 feet (160 meters)". Speed 6.14 km/s from a search summary of the Nature paper. https://science.nasa.gov/mission/dart/ | P, S |
| 31 | Hera arrived in November 2026 | Confirmed | ESA, 11 November 2026: "has arrived at its target asteroids", "30-25 km away". https://www.esa.int/articles/hera-spacecraft-in-rectangular-orbit-around-target-asteroids | P |
| 32 | A 2026 paper sets the bar for surface work at a period over one hour; fast rotators are at least 94% of objects fainter than H 26 | Confirmed, attribution corrected | Alarcon et al.: "the rotation-period criterion P > 1 h considered viable for surface operations (Thirouin et al., 2016)". The criterion is Thirouin's, quoted by the 2026 paper. The 94% is cited from a second Alarcon paper. https://arxiv.org/abs/2605.04784 | P |

Side finding on row 32. The same paper says the outward pull on 2022 OB5 exceeds gravity by "nearly two orders of magnitude" (a ratio of 50 or more). Its own inputs give about 5,500 (my calculation: 3π / (G × 3,000 kg/m³ × (92.5 s)²)). The paper's surface gravity is about 100 times too high. The site should not quote that ratio from the paper.

### 1.4 Companies

| # | Claim | Result | Evidence | How read |
|---|---|---|---|---|
| 33 | Brokkr-1: uplink never closed, refinery "NOT COMPLETED", last contact 16 May 2024 | Confirmed | Company post of 30 July 2024. It says "toaster-sized Cubesat"; "6U" and the April 2023 launch are not on that page. https://www.astroforge.com/updates-collection/an-update-on-mission-1-mission-2-same-name-new-vehicle-new-standard-for-space-exploration | P |
| 34 | Odin: 120 kg, $3.5 million, under ten months, launched 26 February 2025 | Confirmed, with a limit | "We built Odin in less than ten months at a cost of approximately $3.5 million." That is the build cost of the spacecraft. Launch and operations are not in it; press quotes the company at "less than $7 million" for the mission (search summary, not read). https://www.astroforge.com/updates-collection/odint-mission-debrief | P |
| 35 | Odin "declared lost 6 March 2025" | **Corrected** | The company's words on 6 March 2025: "The chance of talking with Odin is minimal". It did not say "lost". Same URL. | P |
| 36 | DeepSpace-2: 200 kg, Hall thrusters, one monochrome camera, "rendezvous and imaging"; landing legs dropped from the description; launch Q1 2027 | Confirmed | March 2025: "Landing legs for its primary mission: landing on a metallic asteroid". Mission page today: "Rendezvous and imaging mission", "LAUNCHING 2027", stale "fourth quarter of 2026". Home page: "Launching Q1 2027". NASA lists the host mission as "Early 2027". https://www.astroforge.com/deepspace-2 ; https://www.astroforge.com/ ; https://www.nasa.gov/event/clps-flight-intuitive-machines-im-3 | P |
| 37 | DeepSpace-2 costs about $10 million | Unverifiable today | From a trade-press article the earlier verifier read. No company page states a cost. | not read |
| 38 | AstroForge states no return mass; "platinum back to Earth before end of this decade" | Confirmed as a press quotation | Search results carry the phrase from 2022 and 2023 interviews. No mass, and no company page repeats it. https://www.nbcnews.com/science/space/startups-are-still-keen-mine-space-rocks-rcna68256 | S |
| 39 | DeepSpace-2 was to launch in 2025 and dock with a metallic asteroid | Confirmed | Space.com, 21 August 2024: "aims to launch its third mission in 2025"; "dock with a metallic near-Earth asteroid". https://www.space.com/asteroid-mining-astroforge-docking-mission-2025 | S |
| 40 | Karman+ first mission: "kilogram-scale" regolith; $10 to 15 million (2025), $20 to 30 million (2024); launch slipped from late 2026 to early 2027 | Confirmed | Both abstracts read. https://meetingorganizer.copernicus.org/EPSC-DPS2025/EPSC-DPS2025-1407.html ; https://meetingorganizer.copernicus.org/EPSC2024/EPSC2024-587.html | P |
| 41 | Karman+ now mid-2028, Apophis, "a technology demonstration, not a mining mission" | Confirmed | Company post, 21 July 2026: "a mid 2028 launch". The slip is blamed on a propulsion vendor. https://www.karmanplus.com/k-mission-1-99942-apophis/ | P |
| 42 | "Nothing comes back to Earth on this mission" | Unverifiable | Neither the post nor the abstracts mention a return. It is a fair inference, not a stated fact. Apophis at 0.34 km and Sq class is confirmed (JPL database); "dry" is an inference from the class. | P for what is absent |
| 43 | Karman+ later craft: "100s–1,000s of kg"; Corvus 700 kg, "1,000–5,000 kg of water to customers in GEO"; Roc 7,000 kg, "up to 100,000 kg"; "10,000x reduction" | Confirmed | All on the FAQ page. https://www.karmanplus.com/faq/ | P |
| 44 | TransAstra 2015: "up to 100 tonnes of water ... single Falcon 9"; "TRL-1 solar thermal oven"; earlier team "could not find any scenario" | Confirmed | NASA page, 7 May 2015. The exact wording is "a single Falcon 9 v1.1 launch", and delivery is to lunar distant retrograde orbit. https://www.nasa.gov/directorates/stmd/niac/niac-studies/apis-asteroid-provided-in-situ-supplies-100mt-of-water-from-a-single-falcon-9/ | P |
| 45 | TransAstra 10 m bag test, 16 November 2026; three of four drawstrings; 1 m bag on the station in 2025 | Confirmed | The release gives no asteroid mass and no mission date. https://www.newswire.com/news/transastra-successfully-tests-10-meter-capture-bag-designed-to-capture-22889775 | P |
| 46 | TransAstra 2026 study: about 100 t, rendezvous 2028 or 2029 | Confirmed (secondary) | Search summary of the 18 March 2026 release and its coverage. https://www.wboc.com/online_features/press_releases/transastra-launches-new-moon-study-to-capture-and-relocate-a-near-earth-asteroid/article_ac091ed4-6bfd-5843-9afe-61fce784afe6.html | S |
| 47 | Planetary Resources: two test satellites in Earth orbit; prospecting "delayed indefinitely"; bought 31 October 2018 | Confirmed | Wikipedia. https://en.wikipedia.org/wiki/Planetary_Resources | S |
| 48 | Deep Space Industries: FireFly 25 kg in 2015; DragonFly from 2016; none flew; bought 1 January 2019 | Confirmed, one addition | The 2013 announcement also states a return mass the report omits: DragonFlies "will return 60 to 150 lbs" (27 to 68 kg). Achieved: none. https://nss.org/deep-space-industries-offers-competition-for-planetary-resources-in-mining-asteroids/ ; https://en.wikipedia.org/wiki/Deep_Space_Industries | S |
| 49 | Origin Space: NEO-1, 30 kg, net test, 2021; a second telescope lost in December 2024 | Partly confirmed | NEO-1 launched 27 April 2021, 30 kg (search results). I found nothing on a December 2024 loss: unverifiable. https://aviationweek.com/space/commercial-space/china-plans-leo-net-capture-demo | S |
| 50 | "Two companies have funded missions with launch slots" | Unverifiable as a count | At least one other resources startup (ExLabs) has announced a 2028 Apophis mission (SpaceNews headline in search results; the page returned an error). Whether it is funded was not checked. Say "the two companies examined here". https://spacenews.com/exlabs-plans-mission-to-rendezvous-with-asteroid-apophis | S |

### 1.5 Studies

| # | Claim | Result | Evidence | How read |
|---|---|---|---|---|
| 51 | Keck 2012: 7 m, about 500 t, high lunar orbit by about 2025; 18,000 kg in low Earth orbit; 12,000 kg xenon; 40 kW; 28-to-1, "70-to-1 or greater"; 6 to 10 years; about $2.6 billion; 250 to 1,300 t; factor of 20 in mass; "only a few dozen" known; de-spin 1,100 t at one turn a minute, 306 kg, 33 minutes; velocity changes 6.6, 2.8 and 0.17 km/s | Confirmed | Every figure found in the saved copy. Caltech's server fails certificate checks, so I could not download my own copy. The return figure is "160 m/s" in the text and "170 m/s" elsewhere. The cost is in 2012 money and "does not include the cost of propellant" for the prime contractor estimate. https://kiss.caltech.edu/final_reports/Asteroid_final_report.pdf | L |
| 52 | "1,300 tonnes is the largest mass any capture study has designed for" | **Corrected** | The same Keck report lists trajectories returning 1,800 t and 3,600 t from 2000 SG344 (its Table 6). And only one capture study was read. Say "the Keck capture hardware was sized for 250 to 1,300 t". | L |
| 53 | ARM reference design: boulder 13,535 kg; 9,995 kg at launch (5,500 dry, 4,095 xenon, 400 hydrazine); 13 months at the asteroid; lunar capture October 2026 | Confirmed | Table 9 and Table 8 of the paper: launch 26 December 2021, 385 days allocated at the asteroid, lunar capture 31 October 2026. https://ntrs.nasa.gov/api/citations/20170010282/downloads/20170010282.pdf | P |
| 54 | ARM cost cap raised "from $1.25 billion to $1.4 billion", without launch or operations; launch December 2021; crew 2026 | Confirmed | JPL release of 15 August 2016. https://www.jpl.nasa.gov/news/nasa-asteroid-redirect-mission-completes-design-milestone/ | P |
| 55 | ARM: boulder chosen over whole asteroid in March 2015 at about $100 million more; cancelled in the 2018 budget; "lack of congressional support"; ended by directive in December 2017 | Confirmed | Space.com, 25 March 2015; budget blueprint: "To accommodate increasing development costs, the Budget cancels the multi-billion-dollar Asteroid Redirect Mission"; Space.com, 14 June 2017; JPL page. The "approximately 20 t" design goal was not found in anything I read: unverifiable. https://www.nasa.gov/sites/default/files/atoms/files/2018_blueprint_nasa.pdf ; https://www.jpl.nasa.gov/missions/asteroid-redirect-robotic-mission-arrm | P, S |
| 56 | Sonter 1998: "Mass multiplication factors above 100 are the initial aim"; return velocity "must be minimised"; three years; launch cost "not a critical parameter" | Confirmed, one mislabel | All four quotations are in the paper. But the ratio table puts "under 5 t of equipment" in the "Launched" column. The paper says "total processing system mass of less than 5 tonnes". That is the mining plant, not the launched mass. https://nss.org/wp-content/uploads/2023/05/the-technical-and-economic-feasibility-of-mining-the-near-earth-asteroids.pdf | P |
| 57 | Hein et al.: bootstrapping factor 14.3 for a 150 kg craft; "propellant-less propulsion"; water at $20,000 per kg; platinum needs "its own mass within 3 seconds"; the table does not reproduce | Confirmed | Table 1 and the text. The stated throughput gives 298,080 kg processed against the table's 42,944 kg, a factor of 6.9, as the report says. https://arxiv.org/abs/1810.03836 | P |
| 58 | Jedicke et al. 2018, abstract | Confirmed | "likely thousands of H2O-rich NEOs larger than about 5 m"; "difficult or impossible to detect". No mass ratio in the abstract. https://scholarsmine.mst.edu/geosci_geo_peteng_facwork/1362/ | P (abstract) |
| 59 | JPL's round-trip figure runs from low Earth orbit; most of it is spent before any cargo is aboard (recalled) | Confirmed by example | JPL's interface lists four parts: Earth departure, arrival, departure from the asteroid, Earth return. Its example for 2000 SG344: 3.256 + 0.128 + 0.217 + 0.000 = 3.601 km/s. The return leg is 6% of the total. https://ssd-api.jpl.nasa.gov/doc/nhats.html | P |
| 71 | Bringing back tonnes "has been designed on paper since 2012" (site-wide statement) | **Refuted** | The report's own source, Sonter's 1998 paper, sizes a mission "to return 1000 tonnes to LEO". 2012 is the first costed study, not the first design. Same Sonter URL as row 56. | P |

### 1.6 Prices, launch and refuelling

| # | Claim | Result | Evidence | How read |
|---|---|---|---|---|
| 60 | Platinum $1,295.00 per ounce, $41.64 per gram, 21 November 2026 | Confirmed, date note | Kitco at 20:08 New York time on 21 November 2026: bid $1,295.00 per troy ounce, 41.64 per gram, 41,635.86 per kilo. The unit conversion is right (1,295 / 31.1035). 21 November is a Saturday, so this is the close of Friday 20 November. https://www.kitco.com/charts/liveplatinum.html | P |
| 61 | Propellant "at $3 per gram in orbit" | Unverifiable here | The report gives no source or date. `industry.md` traces $3,000 per kg in low Earth orbit to a ULA statement of about 2016, with no buyer since. It is a ten-year-old offer, not a price. | not read |
| 62 | Falcon 9 list price $74 million in 2026 for up to 5.5 t to geostationary transfer orbit | Confirmed (secondary) | KeepTrack, citing SpaceX's price sheet through Spaceflight Now, February 2026. SpaceX's own page would not load for me either. https://keeptrack.space/deep-dive/how-much-does-a-falcon-9-launch-cost | S |
| 63 | Shared rides $350,000 for 50 kg, then $7,000 per kg | Unverifiable at source | The same article calls $7,000 "a secondary-source estimate". Other 2026 pages give $6,000 to $6,500. SpaceX's rideshare page returned no text. https://newspaceeconomy.ca/2026/02/27/spacex-rideshare-pricing-as-of-february-2026-what-it-costs-whats-included-and-how-buyers-budget-a-mission/ | S |
| 64 | World average $3,868 per kg to low Earth orbit in 2025; down 96% since 1960; $1,569 by 2030; $273 by 2040 | Confirmed | Cambridge release of 14 July 2026 on a PNAS Nexus paper. The release does not say which year's dollars, or how the average is weighted. https://www.cam.ac.uk/stories/space-cargo-costs-set-to-plummet | S |
| 65 | Starship: one filing gives $90 million a launch | Confirmed (secondary), narrower than stated | It is one customer's contract price (Voyager, for a launch in 2028 or 2029), not a list price. https://www.fool.com/investing/2026/03/21/how-much-will-a-spacex-starship-launch-cost/ | S |
| 66 | Starship: first orbital mission 28 September 2026; 15 flights; ship-to-ship transfer not attempted, now 2027 | Confirmed | Wikipedia as of 14 November 2026: "launched 15 times"; Flight 14 "the first Starship mission to reach Earth orbit"; transfer flights listed for the first quarter of 2027. https://en.wikipedia.org/wiki/List_of_Starship_launches | S |
| 67 | Inspector general, 10 March 2026: transfer test slipped from March 2025 to March 2026; "one of the most significant technical challenges" | Partly confirmed | The slip dates are in Wikipedia, citing report IG-26-004. The quoted phrase is not in the article the report cites, and I did not find it elsewhere: unverifiable. https://en.wikipedia.org/wiki/Starship_Propellant_Transfer_Demonstration | S |
| 68 | US Space Force refuelling demonstrations "moved to 2027"; Astroscale, Orbit Fab, Northrop Grumman | **Corrected** | The cited article says "two commercial servicing missions planned for 2027": Astroscale (propellant transfer) and Starfish Space (a tug, not refuelling). It reports no slip and does not name Orbit Fab or Northrop Grumman. https://satnews.com/2026/09/26/u-s-space-force-schedules-2027-on-orbit-servicing-missions-with-astroscale-u-s-and-starfish-space/ | S |
| 69 | BioAsteroid: fungus and bacterium leached 18 of 44 elements, including palladium, from L-chondrite, with "large variability" | Partly confirmed | L-chondrite, the fungus, palladium and the December 2020 flight are confirmed. "18 of the 44" appears only in a Gizmodo article. "Large variability" is in neither page the report cites. https://astrobiology.com/2026/02/03/microbial-biomining-from-asteroidal-material-onboard-the-international-space-station/ ; https://gizmodo.com/iss-experiment-reveals-the-secret-ingredient-for-asteroid-mining-microbes-2000724479 | S |
| 70 | SpaceX filing: asteroid mining among markets that "do not exist today"; refuelling "essential" | Confirmed | Both sentences are in the saved copy of the S-1. https://www.sec.gov/Archives/edgar/data/1181412/000162828026036936/spaceexplorationtechnologi.htm | L |

Count over rows 1 to 71. Corrected: 4, 7, 32, 35, 52, 56, 68. Refuted: 71. Unverifiable in whole or in part: 20, 37, 42, 49, 50, 61, 63, 67, 69. The other 54 are confirmed, some with a note.

## 2. Arithmetic, redone

Everything in the report marked [C] was recomputed from the stated inputs.

| Report figure | My result | Verdict |
|---|---|---|
| Rocket table, four rows | Reproduces from specific impulses of 320, 450, 1,800 and 3,000 s | **Label slip.** The headers say exhaust speeds of 3.1 and 17.7 km/s. The cells were computed at 3.138 and 17.65. At 3.1 exactly, the 1 and 6 km/s cells are 72% and 14%, not 73% and 15%. Print the specific impulse or fix the header. |
| 5 km/s case: 262 kg arrives; 150 kg craft sends home about 240 kg; 200 kg craft 14 kg; nothing at 203 kg | 262.3; 236.6; 14.5; break-even 203.3 kg | Correct |
| 6 km/s case: 217 kg arrives; cargo only under about 150 kg | 216.6; break-even 147.8 kg | Correct |
| 4 km/s case: 150 kg craft sends home about 880 kg | 879.4 | Correct |
| Mass ratios: 0.000009; 0.00006; 1.35; 28; about 8; 1.4 to 7; 14 | 9.0e-6; 5.8e-5; 1.354; 27.8; 7.6; 1.43 to 7.14; 14.3 | Correct |
| "About four orders" to a ratio of one; "nearly six" to Keck | 4.24; 5.69 | Correct |
| Cost per gram: $8.4 million; ¥5.3 billion; $35 to 48 million; $67,500; $809,000 | 8.39 million; 5.33 billion; 35.5 to 48.4 million; 67,539; 808,901 | Correct for the inputs. See row 4 above for the input. |
| $1.4 billion and "near $11 million per gram" for all three | $1.396 billion; $10.99 million | Correct for the inputs. The inputs mix currencies and decades (section 4, objection 3). |
| Luna total 326 g | 326.1 g | Correct |
| 121.6 g to one tonne: "about four" orders | 3.92 | Correct. To 100 t it is 5.9, to 500 t it is 6.6. |
| Cost gap: "about five" to platinum, "about six" to $3 per gram | 5.30; 6.45 | Correct |
| Gravity: 15 m gives four ten-millionths of Earth's and escape near 8 mm/s; 60 m gives 3 cm/s | 4.3e-7 and 7.9 mm/s; 3.2 cm/s | Correct at 2,000 kg/m³. The density is not stated beside the numbers. |
| Spin limits: 2.3 h at 2,000; 3.0 h at 1,200; 1.2 h for iron | 2.33; 3.01; 1.18 | Correct |
| 15 m at ten minutes: outward pull about 200 times gravity | 196 at 2,000 kg/m³; 119 at 3,300 | Correct for one density. "A hundred times or more" covers the range. |
| Kamoʻoalewa: 19 times | 18.7 at 2,700 kg/m³ | Correct |
| 15 m example: 130 to 28,000 t, "most likely near 3,500" | 131; 28,274; 3,534, all at 2,000 kg/m³ | Arithmetic correct. The range holds density fixed. With 1,200 to 3,300 kg/m³ it is 80 to 47,000 t. |
| 60 m example: "2011 AA37, about 65 m" and "about 230,000 tonnes" | 60 m gives 226,000 t; 65 m gives 288,000 t | **Mixed inputs.** The mass belongs to 60 m, the name to 65 m. |
| 60 m: gravity beats outward pull "nearly twenty to one" at 10 h | 18.4 | Correct |
| 6 m: about 230 t; surface speed 16 cm/s at two minutes; under 10 kg to stop it | 226 t; 15.7 cm/s; 7.6 kg | Correct for a uniform sphere with a 2 m thruster arm. |
| De-spin: 2.5% and five times the Keck case | 2.5%; 4.9 | Correct against Keck's 1.7 million N·m·s |
| Keck at 1 km/s return: about 17 t of xenon for 500 t | 17.5 t | **Formula slip in the script, same answer.** It multiplies the mass at arrival (which still includes xenon) by the burn fraction. Using dry mass plus rock gives 17.5 t against 17.1 t. |
| Hein: stated throughput gives about seven times the stated mass processed | 6.9 | Correct |
| One kilogram of platinum-group metal needs about 25 t of pure metal | 24.5 t at 40.78 parts per million | Correct, and correctly labelled as pure metal. For bulk stony rock at 0.6 to 12 parts per million (`industry.md`) it is 80 to 1,700 t. |
| Karman+ claim applied to OSIRIS-REx: $840,000 per kg, 280 times $3,000 | 838,816; 279.6 | Correct |
| Years from launch to return: 7.1, 6.0, 7.0, 2.5 | 7.10, 6.01, 7.04, 2.50 | Correct |
| "20 to 60 times wider" and "5 to 15 times wider" | 22 to 60; 5.5 to 15 | Correct, using Itokawa's mean of 330 m |

## 3. The six failure types the brief named

- **Prices without dates or in the wrong unit.** Platinum is right in both. The $3 per gram propellant figure has neither a date nor a source in this report. The $2.6 billion Keck cost and the ARM cost cap carry no year.
- **Pure-metal grades applied to bulk rock.** Not found. The one grade used is labelled "pure metal".
- **Different year-dollars compared directly.** Found three times: (a) the $1.4 billion sum of 2003 to 2023 costs in two currencies at one exchange rate; (b) "$8 million a gram" in the money of 2011 to 2023 set beside a 2026 platinum price; (c) Keck's 2012 dollars beside 2025 and 2026 mission prices. The gaps are five orders of magnitude, so no conclusion moves, but the site should say which year each figure is in.
- **Collected, returned and analysed confused.** Not found. All masses are "returned". Worth adding: at least 70% of the Bennu sample is in storage.
- **Company claims reported as achievements.** Not found in the tables. One slip the other way: Odin's $3.5 million is a build cost, and section 5 of the report sets it beside whole-mission figures for DeepSpace-2 and Karman+.
- **More confidence than the source.** Found: "declared lost" (row 35); "the project leader's figure" (row 7); "1,300 t is the largest any study designed for" (row 52); "moved to 2027" (row 68); "18 of 44" and "large variability" (row 69); "one is trying now" (section 4); "the method ... should apply" (section 4).

## 4. Objections to the recommended design

1. **"$8 million a gram" is a point value on a soft input.** The numerator is $1.02 or $1.16 billion, not inflation-adjusted, and may or may not hold the extended mission. Print "about ten million dollars a gram, in the money of the day" and link both totals.
2. **The platinum comparison invites the wrong reading.** Bennu's sample is carbon-rich rock, not platinum. Say it directly: had all 121.6 g been pure platinum, it would have sold for about $5,000 (121.6 × $41.64).
3. **"127 grams for $1.4 billion" adds unlike things.** ¥20 billion of 2003 to 2010, ¥28.9 billion planned in 2012, and dollars of 2011 to 2023, all at 130 yen per dollar, a rate that held in neither Japanese mission's years (recalled). Give each mission in its own currency, or a range of $1.4 to 1.6 billion.
4. **"Four orders of magnitude" is the gap to one tonne only.** The proposals named in the same paragraph are 100 t and 500 t: six to seven orders. State both ends.
5. **"Under way" will be read as "being done".** No sampling attempt has been reported, CNSA has published no date for one, and the craft could leave in April 2027 without trying. Use "not yet attempted; one spacecraft is in position" and date it.
6. **One 28-minute asteroid cannot stand for everything "under 30 m or faster than 2 h".** Outward pull goes as one over the period squared. A two-minute rotator pulls about 200 times harder than Kamoʻoalewa. The per-asteroid sentence for "small or fast" should not cite Tianwen-2 for objects turning in under about ten minutes.
7. **"Kilograms: Planned (Karman+ at Apophis, no return)" sits under a rung about bringing material back.** Split the rung in two: handled at the asteroid, and returned. Returned kilograms are "proposed" everywhere.
8. **"Not done at this size; method exists" and "should apply" are the researcher's inference.** No source says touch-and-go works at 60 m. Print "not tried at this size".
9. **The worked examples still print point masses.** "Most likely near 3,500 tonnes", "about 230,000 tonnes", "about 230 tonnes". Each comes from one assumed brightness-to-size conversion and one assumed density. The two examples also treat uncertainty differently: a factor of 216 in one, "a factor of about 20" in the other. For 2011 AA37 the JPL database has no diameter at all: H = 22.9 gives 45 to 200 m (my calculation, albedo 0.6 to 0.03), or about 100,000 to 8.6 million tonnes. Print ranges only.
10. **"Under 10 kg of propellant" to stop a 6 m rock is a new point value.** It assumes a uniform sphere, spin about one axis and a rigid grip. The only published figure is Keck's 306 kg for 1,100 t.
11. **The ratio table has one "Ratio" column for things that cannot be compared.** Delivered to Earth, lunar orbit or geostationary orbit; counted from low Earth orbit, from near-escape, or from spacecraft mass; raw rock or water. Sonter's 5 t is plant mass. Hein's 14.3 assumes no propellant. If the site shows it, each row needs "of what, from where, to where".
12. **"From zero to about one" gives the optimistic end equal weight.** The 240 kg case needs a craft of 150 kg per tonne in low Earth orbit, including the stage that leaves Earth, the tanks, the collector and the return hardware. OSIRIS-REx was 880 kg dry of 2,110 kg, with its launcher doing the departure. Print the break-even instead: for the report's own split and a storable engine, nothing comes back at 5 km/s unless the dry mass is under about 20% of the mass in orbit, and at 6 km/s under 15%.
13. **"Done" hides how thin the record is.** Three missions, all by agencies, two with near-losses (Hayabusa's failed sampler and lost contact; OSIRIS-REx nearly sinking). Print "done three times, by space agencies".
14. **Universal negatives need a date and "that we found".** "The only processing", "nothing has ever anchored", "no company has reached", "no list price exists". I found no counter-example, but none of these can be proved by a search.
15. **"Launch is a small part of a $10 million to $1 billion mission" is editorial.** OSIRIS-REx's launch was 16 to 18% of its cost. The supporting quotation is from a 1991 model, second-hand.
16. **"Designed on paper since 2012" is wrong** (verdict, point 2).
17. **The site-wide statement drops the caveat the report itself makes**: cost per gram is a science mission's whole budget divided by a by-product. Without it the sentence is quotable as "asteroid material costs $8 million a gram".
18. **The schedule pattern rests on small counts.** "Agency sample returns have mostly met their dates" is two of three; Hayabusa was three years late. Say so in the same sentence.

## 5. A site-wide statement that survives these checks

> As of 21 November 2026, three spacecraft have brought asteroid material to Earth: 121.6 grams from Bennu, 5.4 grams from Ryugu and under a milligram from Itokawa. The missions cost about $1.0 to 1.2 billion, ¥29 billion and ¥20 billion in the money of their day, and each took six to seven years from launch. For the largest sample that is about ten million dollars a gram, counting the whole mission, which was built for science and not for mass. Had that sample been pure platinum it would have sold for about $5,000. All three asteroids are 300 to 900 m across and turn once in 4 to 12 hours. A typical reachable asteroid is about 15 m. Of the few that small with a measured spin, most turn in minutes. No spacecraft has touched one. One has been beside an 18 m asteroid since July 2026 and has not reported a sampling attempt. No company has reached an asteroid. Returning tonnes has been proposed since at least the 1990s. Two designs were costed: a 2012 study at $2.6 billion (2012 dollars) for about 500 tonnes to lunar orbit, and NASA's Asteroid Redirect Mission, capped in 2016 at $1.4 billion without launch or operations, for a boulder of up to about 13.5 tonnes. The first was never started and the second was cancelled in 2017. One tonne is four orders of magnitude more than the largest sample. The proposals are six to seven.

Per-asteroid sentences, revised:

- Large slow rotator: "Grams have been returned from three asteroids of this kind, by space agencies, at ¥20 billion to $1.2 billion a mission. Nothing larger than a sample has been brought back from any asteroid."
- Mid-sized slow rotator: "No spacecraft has touched an asteroid this small. Returning anything from one has not been tried."
- Small, turning in tens of minutes or slower: "No spacecraft has touched an asteroid this small. One has been beside an 18 m asteroid since July 2026; no sampling attempt had been reported by 21 November 2026."
- Turning in under about ten minutes: "No spacecraft has approached an asteroid that turns this fast. Its surface is flung outward a hundred times or more harder than gravity holds it."
- Spin unknown: keep the report's sentence.

## 6. Not verified by me

- Keck figures were read in the researcher's saved copy only (certificate failure at Caltech).
- The exchange rates of 2003 to 2021 and the "three years late" for Hayabusa are recalled.
- DeepSpace-2's $10 million, the ARM "approximately 20 t", 2020 GE "under 18 m", MASCOT's 17 hours, Arkyd-6 "late 2015", the January 2023 Odin launch date (the release returned an error) and Origin Space's December 2024 loss.
- The inspector general's report itself; the SpaceX price sheet and rideshare page.
- Whether Tianwen-2 has moved from 20 km, and any CNSA date for sampling or return.
- I did not adjust any cost for inflation.

## 7. Sources opened today

Listed in the tables above beside each claim. Downloads (untrusted) are in `data/research/dl/vc`. File hashes of my copies of the ARM paper, the OSIRIS-REx press kit, Sonter, Hein and the budget blueprint match the researcher's copies.
