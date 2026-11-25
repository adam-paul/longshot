# Capability: what has been brought back from asteroids, and what could be

Research run of 2026-11-21 for the last rung of the difficulty ladder: "could today's technology bring any of it back". It covers what has flown, what is planned, what is only proposed, and the mass budget behind all three.

Status marks on every number:

- **[P]** primary source read today (agency, company, paper, filing).
- **[S]** secondary source read today (press, encyclopedia, a search summary of a primary).
- **[V]** read at source earlier today by the verification run (`verify-facts-missions.md`), not re-read by me.
- **[R]** recalled, not read today. Check before publishing.
- **[C]** my arithmetic from the inputs shown. The script is `data/research/scripts/budget.py`.

## 0. Bottom line

- **Demonstrated.** Three spacecraft have brought asteroid material to Earth: under 1 mg (Itokawa, 2010), 5.4 g (Ryugu, 2020) and 121.6 g (Bennu, 2023). About 127 g in all, for roughly $1.4 billion, each six to seven years after launch. All three asteroids are hundreds of metres across (about 330 to 900 m) and turn once in 4 to 12 hours.
- **Under way.** China's Tianwen-2 has been 20 km from an 18 m asteroid that turns every 28 minutes since July 2026. Its target is about 100 g, due on Earth in late November 2027. No contact with the surface has been reported. It is the first spacecraft to stay at an asteroid under 100 m.
- **Planned.** Two companies have funded missions with launch slots: AstroForge (rendezvous and imaging, March or April 2027) and Karman+ (kilogram-scale excavation at Apophis, launch mid-2028, nothing returned to Earth). Neither has reached an asteroid. AstroForge's first two spacecraft failed on communications before doing their jobs.
- **Proposed only.** Everything measured in tonnes: the 2012 Keck study (a 500 t asteroid to lunar orbit for $2.6 billion), NASA's Asteroid Redirect Mission (a boulder of about 13.5 t, cancelled in 2017), TransAstra's 100 t capture, Karman+'s 1 to 5 t of water and 100 t whole-asteroid return.
- **The gap.** From the largest sample to one tonne is about four orders of magnitude in mass. From the demonstrated cost ($8.4 million per gram) to the platinum price ($41.64 per gram on 21 November 2026) is about five. To a propellant price of $3 per gram in orbit it is about six.
- **Nothing has ever touched a fast-rotating asteroid, anchored to any asteroid, or processed asteroid material at one.** The only processing of asteroid material in space is a 2020 experiment on the space station in which microbes leached metals from small pieces of meteorite.

## 1. Sample returns to date

| Mission | Target (size, spin) | Returned | Launch to return | Cost | Cost per gram [C] |
|---|---|---|---|---|---|
| Hayabusa (JAXA) | Itokawa, 535 × 294 m [P1], mean about 330 m [R]; 12.1 h [R] | More than 1,500 particles under about 180 µm; "an exact mass ... is not recorded" [P1]. Commonly given as under 1 mg [S2] | 9 May 2003 to 13 June 2010, 7.1 years [P3] | About ¥20 billion over ten years, the project leader's figure [S4] | Not meaningful: over ¥20 billion per milligram |
| Hayabusa2 (JAXA) | Ryugu, about 1 km, 7.6 h [P1] | 5.424 ± 0.217 g [P5]; requirement 0.1 g [P1] | 3 December 2014 to 6 December 2020, 6.0 years [P1] | ¥28.9 billion total project cost, FY2010 to FY2021, in a 2012 ministry budget sheet (a plan figure, not a final account) [P7] | ¥5.3 billion; about $35 to 48 million at 150 to 110 yen per dollar |
| OSIRIS-REx (NASA) | Bennu, about 500 m, 4.3 h [P1] | 121.6 g; requirement 60 g [P8]. "The largest asteroid sample to be returned to Earth" [P1] | 8 September 2016 to 24 September 2023, 7.0 years [P9] | $1.02 billion over its lifetime, not inflation-adjusted [S10]. Launch service alone $183.5 million [S11]. Cost cap at selection about $850 million plus launch [S11] | $8.4 million |
| Tianwen-2 (CNSA), under way | Kamoʻoalewa, 18 ± 2 m, 27.9 min [V] | Target about 100 g [S12]. Nothing collected yet | Launched 29 May 2025 Beijing time [P13]; capsule due late November 2027 [S14]; 2.5 years if on time | No official figure found | – |

For scale, lunar sample returns:

| Programme | Returned | Cost | Cost per gram [C] |
|---|---|---|---|
| Apollo, six landings 1969 to 1972 | 382 kg [P15] | $25.8 billion then-year, $309 billion in 2025 dollars (Project Apollo, 1960 to 1973) [S16] | $67,500 then-year; about $809,000 in 2025 dollars |
| Luna 16, 20, 24 (1970 to 1976) | 101 g [S], 55 g, 170.1 g [S17]; 326 g in all [C] | Not published | – |
| Chang'e-5 (2020) | 1,731 g [P18] | Not published | – |
| Chang'e-6 (2024) | 1,935.3 g [P19] | Not published | – |

Notes:

- The three asteroid missions together returned about 127 g for about $1.4 billion (yen converted at 130 per dollar), near $11 million per gram [C].
- Each capsule was far heavier than its contents. OSIRIS-REx's capsule weighed about 50 kg and carried 0.12 kg; the spacecraft weighed 2,110 kg at launch [P9].
- Japan's Mars-moon mission MMX launched on 20 October 2026 and aims to bring Phobos material back in 2031 [S20] [P1]. It is not an asteroid mission, though Phobos may be a captured asteroid.
- The Smithsonian page gives the Luna total as 226.1 g, which does not match its own per-mission figures; 326 g is the sum [S17].
- These are science missions. They spent one to two years mapping and carried instruments a mining craft would not. Cost per gram is the demonstrated price, not a floor on what a purpose-built mission would pay.

## 2. Spacecraft that have touched or stayed at a small body

**Under about 100 m: one spacecraft has arrived, none has made contact.**

| Spacecraft | Body | What happened |
|---|---|---|
| Tianwen-2 (2026) | Kamoʻoalewa, 18 m, 27.9 min | At 20 km since about 2 July 2026 [V]; announced 6 July [P13]. "Conducting companion-flight exploration to prepare for sample return" on 13 October 2026 [V]. Three sampling modes on board: touch, hover and attach; the attach mode would be a first [S12]. No descent or sampling reported as of 21 November 2026 [S, two searches today]. At 2,700 kg/m³ the outward pull at its equator is about 19 times its gravity [C]. |
| NEA Scout (NASA, 2022) | 2020 GE, under 18 m [S] | A solar-sail CubeSat launched on Artemis I, 16 November 2022. "After launch, the project team was not able to communicate with the spacecraft" [P21]. |
| Odin (AstroForge, 2025) | 2022 OB5, 2 to 15 m, 1.5 min [V] | Meant to fly past in late 2025. Lost within days of launch (section 3). |
| Hayabusa2 extended mission | 1998 KY26, 11 m, about 5 min [P22] | Planned rendezvous in 2031. Abandoned in November 2026 after ion-engine failures; replaced by a fast flyby of 2015 BM510 in April 2028 [V]. |

ESO said in September 2025 that the 1998 KY26 visit would be "the first time a space mission encounters a tiny asteroid — all previous missions visited asteroids with diameters in the hundreds or even thousands of metres" [P22]. Tianwen-2 has since become the first.

**Larger bodies: what contact has taught.**

| Spacecraft | Body | What happened |
|---|---|---|
| NEAR Shoemaker (2001) | Eros, about 17 km | Soft landing at end of mission, not designed for it [R]. |
| Hayabusa (2005) | Itokawa, 535 m | Its hopper MINERVA missed the asteroid and went into solar orbit [S6]. At the first touchdown the craft "remained on the surface for about half an hour" unplanned, then "was commanded to make an emergency ascent"; the sampling projectiles probably did not fire; a fuel leak and loss of contact followed [P3]. The sample was dust that drifted into the collector. |
| Hayabusa2 (2018 to 2019) | Ryugu, about 1 km | Two hoppers (MINERVA-II1) reached the surface and moved by hopping, "the first probes ever to travel the surface of an asteroid"; a third rover failed before release [S6]. The MASCOT lander ran on battery for about 17 hours [R]. Two touch-and-go samplings worked. |
| Philae (2014) | Comet 67P, about 4 km | All three ways of holding on failed: the hold-down thruster did not arm, "the harpoons themselves did not fire", and the ice screws did not bite. It "did not secure itself to the comet, and it bounced to a new location", in shadow, and "completed 80% of its planned first science sequence before falling into hibernation ... when the primary battery was exhausted" about two and a half days later [P23]. |
| OSIRIS-REx (2020) | Bennu, about 500 m | The surface gave way like a fluid: the sampler arm "sank 1 1/2 feet into it within seconds", and "had the spacecraft not fired its thrusters to back away ... it would have sunk right into Bennu". Lab tests had "barely made a divot" [P24]. |
| DART (2022) | Dimorphos, about 160 m | A deliberate impact at about 6 km/s [R], on 26 September 2022 [P25]. Still the smallest body any spacecraft has touched. |
| Hera (2026) | Didymos and Dimorphos | Arrived November 2026; two CubeSats to be released "over the coming months" [V]. |

What follows from this record:

- **The one anchoring attempt failed.** Philae is the only attempt to fix a craft to a small body. Every asteroid sample so far came from a contact of seconds, with the spacecraft never at rest on the surface by design.
- **Surfaces have surprised the missions.** Bennu was boulder-strewn where a smooth surface was predicted [P1], and its surface had almost no strength [P24]. Ryugu and Itokawa were also rougher than expected [R].
- **Gravity is nearly absent on the targets.** A 15 m body of ordinary rock density has about four ten-millionths of Earth's gravity and an escape speed near 8 mm/s. A 60 m one: 3 cm/s [C].
- **Spin decides whether a surface exists to work on.** A body of density 2,000 kg/m³ turning faster than once in 2.3 hours pulls outward at its equator harder than its gravity pulls in (3.0 h at 1,200 kg/m³, 1.2 h for solid iron) [C]. At 15 m and a 10-minute period the outward pull is about 200 times gravity [C]. Loose material stays only with cohesion, or near the poles.
- **No spacecraft has touched an asteroid turning faster than once in about 4 hours.** Tianwen-2 would be the first.
- A 2026 paper on 2022 OB5 puts the bar for surface work at a period over one hour, which that object misses "by more than two orders of magnitude", and says fast rotators are at least 94% of objects fainter than H 26 [V].

## 3. Commercial attempts: stated against achieved

| Company | Stated | Achieved in space |
|---|---|---|
| **Planetary Resources** (2009 to 2018) | Arkyd space telescopes, then prospecting craft; "first asteroid prospecting mission by 2020" [S26] | Two small test satellites in Earth orbit: Arkyd-3 Reflight (released from the space station July 2015) and Arkyd-6 (January 2018, an infrared imager). A first Arkyd-3 was lost in a 2014 launch failure. The prospecting mission was "delayed indefinitely"; the company was bought by ConsenSys on 31 October 2018 [S26]. Nothing went beyond Earth orbit. |
| **Deep Space Industries** (2013 to 2018) | 25 kg FireFly prospectors "first ... launched in 2015"; from 2016, DragonFly craft "for round-trip visits that bring back samples" [S27] | None of its asteroid craft flew. Its water-fuelled thrusters flew on other firms' satellites. Bought by Bradford Space on 1 January 2019 [S28]. |
| **AstroForge** (2022 on) | Refine platinum-group metals in space and return them. No return mass found in any company page read today. A press summary quotes the chief executive: "the first amount of platinum back to Earth before end of this decade" [S, not read at source]. | **Brokkr-1** (6U CubeSat, April 2023): reached orbit, but the team "remained unable to close the command uplink" and the refinery was never switched on. Status: "Refinery Demonstration - NOT COMPLETED". Last contact 16 May 2024 [P29]. **Odin** (120 kg, $3.5 million, built in under ten months, launched 26 February 2025 with a lunar lander): a few signals, then silence; declared lost 6 March 2025; went past the Moon [P30] [P31]. **DeepSpace-2** (200 kg, about $10 million [V], Hall thrusters): not launched; now March or April 2027 [V]. Described in March 2025 as having "landing legs for its primary mission: landing on a metal[lic asteroid]" [P30]; in 2026 as a "rendezvous and imaging mission" with one monochrome camera [P32]. |
| **Karman+** (seed $20 million, 2025 [V]) | First mission: "capture kilogram-scale surface regolith", cost $10 to 15 million (2025 abstract) [P33]; it was $20 to 30 million in the 2024 abstract [P34]. Later: "Touch-and-Go" craft under 1,000 kg that "return 100s–1,000s of kg"; Corvus (700 kg) "delivers 1,000–5,000 kg of water to customers in GEO"; Roc (7,000 kg) to "return entire asteroids up to 100,000 kg" [P35]. | Nothing launched. First mission now mid-2028, to Apophis, "a technology demonstration, not a mining mission" [V]. Apophis is about 340 m and dry. Nothing comes back to Earth on this mission. |
| **TransAstra** | 2015 NASA concept study: "returns up to 100 tonnes of water from a near Earth asteroid using only a single Falcon 9", using a "TRL-1 solar thermal oven" [P36]. 2026: a study of capturing an asteroid of about 100 t, rendezvous "in 2028 or 2029" [S37]. | A 1 m capture bag operated inside the space station in 2025. A 10 m bag was inflated and closed on the ground in November 2026, with one of four drawstring gears failed [P38]. No spacecraft has flown to an asteroid. |
| **Origin Space** (China) | Asteroid mining | NEO-1 (2021), a 30 kg craft that tested a net in Earth orbit, and a small telescope; a second telescope was lost in a December 2024 launch failure [S39]. |
| **SpaceX** | S-1 of May 2026 lists asteroid mining among markets that "do not exist today" [V]. | Nothing asteroid-specific. |

Summary of the commercial record on 21 November 2026:

- Asteroids reached: none.
- Asteroid material touched, processed or returned: none.
- Spacecraft sent beyond Earth orbit toward an asteroid: one (Odin), lost.
- Both AstroForge failures were radio and power faults close to Earth. The asteroid-specific steps are untested by anyone commercial, which is different from having failed.
- Largest stated return against largest demonstrated: 100,000 kg against 0 kg commercially, and against 0.1216 kg by anyone.

## 4. The physics budget

### 4.1 The rocket equation in plain numbers [C]

Share of a spacecraft's starting mass that is left after a given velocity change:

| Propulsion | 1 km/s | 2 km/s | 4 km/s | 5 km/s | 6 km/s |
|---|---|---|---|---|---|
| Storable chemical (exhaust 3.1 km/s) | 73% | 53% | 28% | 20% | 15% |
| Hydrogen-oxygen (4.4 km/s) | 80% | 64% | 40% | 32% | 26% |
| Hall thruster (17.7 km/s) | 94% | 89% | 80% | 75% | 71% |
| Ion or high-power Hall (29.4 km/s) | 97% | 93% | 87% | 84% | 82% |

What is left has to include the spacecraft itself. Three points matter more than the table:

- **The cargo only rides the return leg.** JPL's round-trip figure runs from low Earth orbit and back to atmospheric entry [R]. Most of it is spent leaving Earth and matching the asteroid, before any cargo is aboard.
- **A worked chemical case, 5 km/s split as 4.2 out and 0.8 back.** Of 1,000 kg in low Earth orbit, 262 kg arrives. If the spacecraft is 150 kg of that, the remaining 112 kg of propellant can push about 240 kg of rock onto a return path. If the spacecraft is 200 kg, about 14 kg. At 203 kg, nothing.
- **At 6 km/s (4.8 out, 1.2 back)** the same tonne delivers 217 kg to the asteroid and returns cargo only if the spacecraft is under about 150 kg. **At 4 km/s (3.5 out, 0.5 back)** a 150 kg spacecraft could send home about 880 kg.

So with chemical propulsion and all propellant brought from Earth, the mass sent home per mass placed in low Earth orbit runs from zero to about one, and is decided by the return-leg velocity and the spacecraft's own mass. The cargo then needs a heat shield, or more propellant to stop in orbit; neither is in these figures.

Electric propulsion changes the table but adds time and a larger velocity bill, because a low-thrust craft spirals out. The Keck study's own numbers: 6.6 km/s to leave Earth orbit, 2.8 km/s to reach the asteroid, 0.17 km/s to come back [P40].

### 4.2 Mass returned per mass launched

| Case | Returned | Launched | Ratio | Status |
|---|---|---|---|---|
| Hayabusa2 | 0.0054 kg to Earth | about 600 kg [P41] | 0.000009 | Flown |
| OSIRIS-REx | 0.1216 kg to Earth | 2,110 kg [P9] | 0.00006 | Flown |
| NASA ARM, final reference design | 13,535 kg boulder to lunar orbit | 9,995 kg on a Delta IV Heavy to near-escape (5,500 dry, 4,095 xenon, 400 hydrazine) [P42] | 1.35 | Cancelled 2017 |
| Keck study 2012 | 500,000 kg whole asteroid to high lunar orbit | 18,000 kg in low Earth orbit, 12,000 kg of it xenon [P40] | 28; "70-to-1 or greater" in favourable cases | Paper |
| TransAstra APIS 2015 | 100,000 kg water to lunar orbit | One Falcon 9 [P36] | about 8 if the launch is 13 t [C, R] | Concept |
| Karman+ Corvus | 1,000 to 5,000 kg water to GEO | 700 kg spacecraft [P35] | 1.4 to 7 | Stated |
| Karman+ Roc | up to 100,000 kg | 7,000 kg spacecraft [P35] | up to 14 | Stated |
| Sonter 1998 | 1,000 t to low Earth orbit | under 5 t of equipment | "Mass multiplication factors above 100 are the initial aim" [P43] | Paper |
| Hein et al. 2020, conservative water case | 14.3 times spacecraft mass | 150 kg spacecraft | 14.3, assuming "propellant-less propulsion" [P44] | Paper |

Between the best flown ratio and a ratio of one lie about four orders of magnitude; to the Keck figure, nearly six [C]. The comparison is unfair to the science missions, which were never built to maximise mass, and that is the point: nothing has been.

Every ratio above one depends on at least one of three things that have not been demonstrated:

1. **Moving raw rock, not product.** Keck and ARM deliver unprocessed asteroid to lunar orbit, not to Earth and not as water or metal.
2. **A target with a very small return velocity.** Keck's case needs 0.17 km/s, on an object chosen because its orbit brings it back to Earth by itself. At 1 km/s the same 500 t would need about 17 t of xenon, more than the spacecraft carries [C].
3. **Propellant made at the asteroid.** Sonter: "If the return transfer can be accomplished using part of the retrieved non-terrestrial mass as reaction mass" [P43]. Karman+: "The breakthrough is producing return fuel at the asteroid. Once we can extract thruster fuel from asteroid material, we break free from the rocket equation" [P35].

### 4.3 The studies, by their own account

- **Keck Institute study (Brophy et al., 2012)** [P40]. A 7 m, 500 t asteroid to high lunar orbit by 2025. One Atlas V; 40 kW solar-electric propulsion; 6 to 10 years of flight; "~$2.6B". The system could handle 250 to 1,300 t "to account for uncertainties in size and density". On what is known beforehand: from brightness alone there is "a factor of 20 uncertainty in the estimated mass". On targets: "only a few dozen of these are currently known. Fewer still have secure orbits and none of them have known spectral types"; about five good candidates a year were expected with a dedicated search. De-spin was sized for 1,100 t turning once a minute: 306 kg of propellant and 33 minutes.
- **TransAstra's APIS concept (2015)** [P36]. Its own summary on NASA's site says an earlier NASA-funded asteroid-mining team "could not find any scenario for a realistic commercial economic return from such a mission", and offers optical mining and water-fuelled return as the answer. The oven at its centre was rated "TRL-1", the lowest readiness level.
- **NASA Asteroid Redirect Mission.** In March 2015 NASA chose to lift a boulder off a large asteroid in preference to bagging a whole small one; press accounts give better-understood targets and more reusable technology as reasons, at about $100 million more [S45]. In August 2016 the robotic mission's cost cap rose "from $1.25 billion to $1.4 billion", excluding "the launch vehicle or the post-launch operations phase", with launch in December 2021 and a crew visit in 2026 [P46]. The final reference design returned a boulder of at most 13,535 kg from 2008 EV5, with 13 months at the asteroid and lunar capture in October 2026, nearly five years after launch [P42]; "approximately 20 t" appears as the design goal elsewhere [S]. The March 2017 budget: "To accommodate increasing development costs, the Budget cancels the multi-billion-dollar Asteroid Redirect Mission" [P47]; in context the rising costs are those of the Orion capsule and SLS rocket. Reporting also cites "lack of congressional support" [S48]. NASA's page says a December 2017 policy directive "ended the mission" [P49].
- **Sonter (1998 conference version of the 1997 paper)** [P43]. "Whilst outbound delta-v is not critical ... return delta-v must be minimised." Missions "taking longer than (say) three years will have to have very good" mass payback ratios for a positive present value. A first market of "about 1000 tonnes per year". He concludes mining is close to feasible; the mass ratios are aims, not results.
- **Hein, Matheson and Fries (2020)** [P44]. The decisive variable is throughput: kilograms processed per second per kilogram of equipment. For platinum, at one part in 100,000 of the rock, a break-even comparable to the water case "seems very high": the spacecraft "would need to be able to process the equivalent of its own mass within 3 seconds". Water for use in space looks viable in their model at an assumed price of $20,000 per kg. The water table's figures do not all reproduce from one another (the stated throughput gives about seven times the stated mass processed), so I quote the ratio only.
- **Jedicke et al. (2018)** [P50, abstract only; the paper is paywalled]. "There are likely thousands of H2O-rich NEOs larger than about 5 m diameter" within a return-trip velocity of about 3 km/s, but "the small, dark, low Δv NEOs are difficult or impossible to detect with Earth-based telescopes". It counts objects. It does not give a delivered-mass ratio in the abstract.

## 5. What would have to change, and who is working on it

| Requirement | Where it stands | Who is credibly working on it |
|---|---|---|
| **Launch price** | Falcon 9 list price $74 million in 2026 for up to 5.5 t to geostationary transfer orbit [S51]. Shared rides: $350,000 for 50 kg, then $7,000 per kg, to Sun-synchronous orbit [S52]. World average to low Earth orbit $3,868 per kg in 2025, down 96% since 1960; a Cambridge-led forecast gives $1,569 by 2030 and $273 by 2040 [S53]. Starship has no published price; one customer filing reportedly gives $90 million a launch [S54]. No list price exists for rides beyond Earth orbit; both AstroForge deep-space craft ride as secondary cargo on lunar-lander launches. | SpaceX; Blue Origin, Rocket Lab and others [R]. A 1991 investment model quoted by Sonter found "that launch cost (was) not a critical parameter" [P43]. Launch is a small part of a $10 million to $1 billion mission. |
| **In-orbit refuelling** | Storable propellant has been transferred in orbit for decades (space station resupply) [R]. Starship flew its first orbital mission on 28 September 2026 and has flown 15 times; ship-to-ship transfer has not been attempted [S55]. NASA's inspector general (10 March 2026): the test slipped from March 2025 to March 2026 and would miss that; it is "one of the most significant technical challenges" [S56]. Now planned for 2027 [S55]. US Space Force commercial refuelling demonstrations moved to 2027 [S57]. | SpaceX (which calls refuelling "essential to our lunar, Mars, asteroid mining, and other deep space ambitions" [V]); Astroscale, Orbit Fab, Northrop Grumman [S57]. |
| **Cheap deep-space spacecraft** | The three sample-return missions cost about $0.15 to 1 billion each. AstroForge built Odin for $3.5 million and lost it; DeepSpace-2 is about $10 million; Karman+ states $10 to 15 million. None has yet worked beyond Earth orbit. | AstroForge, Karman+. |
| **Autonomy near the target** | Demonstrated by agencies: DART steered itself into a 160 m body; OSIRIS-REx and Hayabusa2 descended on onboard navigation [R]. Commercial: none yet. | AstroForge (a 2027 autonomy test flight [V]); Karman+ ("optical navigation and onboard flight software" [P35]); CNSA at Kamoʻoalewa. |
| **Knowing spin and size before launch** | 21 of the 286 cheapest targets have a measured spin (the plan). Karman+ calls rotation "one of the bigger unknowns" [V]. AstroForge's first target turned out to spin every 92 seconds [V]. | Ground observers; this is where the site's "observe next" list applies. |
| **Holding on to a fast rotator** | Never done. One anchoring attempt on any small body, which failed (Philae). | CNSA: Tianwen-2's attach mode is the only flight hardware. TransAstra's bag avoids anchoring by enclosing the whole body. JPL gripper research [R]. |
| **Capturing and de-spinning a whole body** | Never done. Bags tested at 1 m in orbit and 10 m on the ground [P38]. Stopping the spin is cheap for the smallest bodies: a 6 m rock turning every two minutes carries about 2.5% of the angular momentum Keck designed for; a 15 m rock turning every minute carries five times it [C]. Enclosing a tumbling rock is the untested step. | TransAstra. |
| **Excavating in microgravity** | Grams, by seconds-long contact. OSIRIS-REx's nitrogen-jet sampler is the largest haul. Kilogram-scale is Karman+'s 2028 objective. | Karman+; CNSA. |
| **Processing in microgravity** | One experiment on real asteroid material: BioAsteroid (space station, 2020; published 2026), in which a fungus and a bacterium leached 18 of 44 elements, including palladium, from L-chondrite chips, with "large variability" [S58]. AstroForge's orbital refinery never ran [P29]. Solar-thermal water extraction is at ground-test level; NASA's own summary called the oven "TRL-1" in 2015 [P36]. | University of Edinburgh and Cornell; AstroForge; TransAstra; Karman+. |
| **Propellant made at the asteroid** | Never done. Water-fuelled thrusters have flown on small satellites [S28]; the water came from Earth. | Karman+, TransAstra. |
| **A buyer** | No current public price for water or metal in orbit; the only figures are from about 2016 (`industry.md`). | Outside this report. |

## 6. Timeline realism

| Who | Stated | Outcome |
|---|---|---|
| Deep Space Industries | January 2013: prospectors in 2015, sample returns from 2016 [S27] | Neither flew; acquired 2019. |
| Planetary Resources | Arkyd-6 "late 2015"; prospecting mission 2020 [S26] | Arkyd-6 flew January 2018; prospecting cancelled; acquired 2018. |
| NASA ARM | 2016: launch December 2021, crew 2026 [P46] | Cancelled 2017. |
| Keck study | Asteroid in lunar orbit "by 2025" [P40] | Not built. |
| AstroForge Brokkr-1 | Refinery demonstration in 2023 | Launched on time; payload never ran [P29]. |
| AstroForge Odin | January 2023: launch in the second half of 2023 [S59] | Launched February 2025, about 18 months late (the host mission slipped; the first vehicle failed vibration testing [P29]); lost in days. |
| AstroForge DeepSpace-2 | August 2024: launch in 2025, to dock with a metallic asteroid [S60]. June 2026: "this fall" [P61]. Company site today: "LAUNCHING 2027", with stale "fourth quarter of 2026" text on the same page [P32] | Not launched. About a year and a half of slip so far, and the task has narrowed from docking to imaging. |
| Karman+ | 2024: late 2026 [P34]. 2025: early 2027, done by mid-2028 [P33]. July 2026: launch mid-2028 [V] | Not launched. About 18 months of slip in two years; target changed to fit the launch date. |
| TransAstra | March 2026: rendezvous 2028 or 2029 [S37] | Bag ground-tested November 2026; no flight spacecraft announced. |
| Starship propellant transfer | March 2025, then March 2026 [S56] | Not attempted; 2027 [S55]. |
| Hayabusa2 at 1998 KY26 | Rendezvous 2031 | Abandoned November 2026 [V]. |
| Tianwen-2 | Launch 2025, return November 2027 | On its stated schedule so far. |
| For comparison: OSIRIS-REx, Hayabusa2 | Returns in 2023 and 2020 | On time. Hayabusa returned three years late after failures in flight [R]. |

Pattern: agency sample returns have mostly met their dates once launched. Every commercial date read today for a mission to an asteroid has slipped by one to two years or was never met, and no commercial date for returning material has a spacecraft behind it yet.

## 7. Recommendations for the site

### 7.1 Use four fixed words

- **Done**: a spacecraft has done it at a body of this size and spin class.
- **Under way**: a spacecraft is in flight to do it.
- **Planned**: funded hardware with a launch slot. Print the stated date and the date it was stated.
- **Proposed**: a paper, a study or a company statement.

State the rung for three amounts, because the answers differ: **grams** (a sample), **kilograms** (a demonstration), **tonnes** (mining or capture).

### 7.2 What sets the rung for one asteroid

Only its size and spin (measured or prior) and the fixed record above. Suggested classes, with the three sampled asteroids as the only anchors:

| Class | Grams | Kilograms | Tonnes |
|---|---|---|---|
| Over about 300 m, turning once in 4 h or slower | Done (three times) | Planned (Karman+ at Apophis, no return) | Proposed (ARM boulder, cancelled) |
| 30 to 300 m, slower than about 2 h | Not done at this size; method exists | Proposed | Proposed |
| Under 30 m, or faster than about 2 h | Under way (Tianwen-2) | Proposed | Proposed (whole-body capture, under about 10 m) |
| Faster than about 10 min | Never attempted | Never attempted | Proposed for capture only |
| Spin unknown | State the prior: most this small turn too fast for loose material to stay | | |

The thresholds are judgement calls from three data points and must be labelled so. Tianwen-2 will move the third row one way or the other within months; the page should carry a date.

### 7.3 Per-asteroid wording, one or two sentences

- Large slow rotator: "Grams have been returned from three asteroids of this kind, at roughly $0.15 to 1 billion a mission. Nothing larger than a sample has been brought back from any asteroid."
- Mid-sized slow rotator: "No spacecraft has touched an asteroid this small; the sampling method that worked on three larger ones should apply if the spin is as slow as reported. Returning more than grams has only been proposed."
- Small or fast: "No spacecraft has touched an asteroid this small or this fast. One is trying now at an 18 m asteroid (Tianwen-2, result due 2027)."
- Spin unknown: add "Its spin has not been measured, and that decides which of these applies."

### 7.4 The site-wide statement

> Three spacecraft have brought pieces of asteroids to Earth: about 127 grams in total, for about $1.4 billion. The largest haul, 121.6 grams from Bennu, cost about $8 million a gram and took seven years; platinum sold for about $42 a gram on 21 November 2026. All three asteroids were hundreds of metres wide and slow-turning; a typical reachable asteroid is about 15 m, most that small with a measured spin turn in minutes, and no spacecraft has touched one like it. One is trying now. No company has reached an asteroid. Bringing back tonnes has been designed on paper since 2012 and never built: it is four orders of magnitude beyond the largest sample in mass, and five to six in cost per kilogram.

Corrections to the plan: section 5.1 says "about 120 grams". Use 121.6 g for the largest single return and about 127 g for all three.

### 7.5 The ladder for three example objects

Rung 4 (worth) belongs to the value report and is left as a pointer.

**A typical 15 m object, spin unmeasured**

1. *Found again?* From its orbit record. (Measured.)
2. *Reached?* Round trip of so many km/s on the best date. One spacecraft has ever stayed at an asteroid under 100 m, and it got there in July 2026.
3. *Big and slow enough to work on?* About 15 m from brightness alone, likely between 5 and 30 m, so between about 130 and 28,000 tonnes of rock, most likely near 3,500. Gravity under a millionth of Earth's; a 1 cm/s push leaves for good. Spin not measured: most asteroids this small turn in minutes, and at ten minutes the surface at the equator is flung outward 200 times harder than gravity holds it. (Prior.)
4. *Worth anything?* See the price range.
5. *Could any of it be brought back?* **Grams: under way, not done.** The three samples returned so far came from asteroids 20 to 60 times wider that turn in hours; a Chinese spacecraft is attempting it now at an 18 m asteroid that turns every 28 minutes. **Kilograms: proposed.** **Tonnes: proposed.** At about 3,500 tonnes the whole object is nearly three times the largest mass any capture study has designed for (1,300 tonnes).

**A 60 m slow rotator (for example 2011 AA37, about 65 m, 10-hour period graded unreliable)**

1. *Found again?* Yes. (Measured.)
2. *Reached?* 5.85 km/s. No spacecraft has visited an asteroid this small and stayed, other than the one above.
3. *Big and slow enough?* About 230,000 tonnes if ordinary rock. At a 10-hour spin, gravity beats the outward pull nearly twenty to one, so loose material can lie on it; escape speed about 3 cm/s. The spin is one uncertain measurement. (Measured, low confidence.)
4. *Worth anything?* See the price range.
5. *Could any of it be brought back?* **Grams: not done at this size; the method is done.** Touch-and-go sampling has worked three times on asteroids 5 to 15 times wider, each mission costing about $0.15 to 1 billion and six to seven years from launch for at most 122 grams. **Kilograms: proposed** (one company named this object as a reference target in 2023; its first flight now goes elsewhere and returns nothing). **Tonnes: proposed.** NASA designed a mission to lift a 13.5-tonne boulder off a larger asteroid and cancelled it in 2017.

**A 6 m object a capture mission might bag**

1. *Found again?* Often not: many this faint were tracked for days. (Measured.)
2. *Reached?* Among the cheapest, around 4 km/s.
3. *Small enough to take whole?* About 230 tonnes if rock; from brightness alone the mass is uncertain by a factor of about 20. The 2012 Keck design could move 250 to 1,300 tonnes. If it turns every two minutes its surface moves at 16 cm/s; stopping that takes under 10 kg of propellant, but nothing has ever enclosed a tumbling rock. (Prior.)
4. *Worth anything?* See the price range.
5. *Could any of it be brought back?* **Grams: under way** (as above). **The whole object: proposed.** No spacecraft has captured, bagged or towed an asteroid. The only one ever moved was a 160 m moonlet nudged by a deliberate crash (DART, 2022). A 10 m bag was inflated and closed on the ground in November 2026 and a 1 m bag inside the space station in 2025. The one costed design needed 18 tonnes in orbit, six to ten years and $2.6 billion to park a rock like this in lunar orbit, not on Earth. NASA dropped the whole-asteroid version in 2015 and the programme in 2017.

## 8. Ways this could mislead

- **Cost per gram is not the cost of mining.** It divides a science mission's whole budget by a by-product. It is the only demonstrated number, so print it as "what it has cost so far".
- **Returned to where.** Earth's surface (the samples), lunar orbit (Keck, ARM, TransAstra) and geostationary orbit (Karman+) are different deliveries. A ratio of 28 to lunar orbit is not 28 to a buyer.
- **Raw rock is not product.** 500 t of asteroid is not 500 t of water or metal. One kilogram of platinum-group metal at the median iron-meteorite grade means processing about 25 t of pure metal [C, grade from `industry.md`].
- **The worked rocket-equation cases are sensitive.** A 50 kg change in spacecraft mass moves the answer from 240 kg to 14 kg. The split between legs is my assumption; JPL publishes the total, and real missions let the launcher supply part of it.
- **"Planned" decays.** Every commercial date has moved. Print the date a plan was stated.
- **The size and spin classes rest on three sampled asteroids.** They are not physical limits.
- **Failure is not evidence of impossibility, and neither is its absence.** The commercial losses were radio faults near Earth. Nobody commercial has yet met the asteroid-specific problems.
- **This will date quickly.** Tianwen-2 could attempt contact any week; DeepSpace-2 and Hera's CubeSats act in 2027. The rung needs a "last checked" date.
- **Soft inputs.** Hayabusa's mass is unrecorded; Hayabusa2's cost is a plan figure; Hayabusa's is a quoted remark; OSIRIS-REx's is not inflation-adjusted and comes from a society's compilation of NASA budgets; Chinese and Soviet costs are unpublished; yen conversions depend on the year chosen.
- **Company cost claims are claims.** Karman+ states "a 10,000x reduction in cost per kilogram of asteroid material compared to traditional deep space missions" [P35]. Applied to OSIRIS-REx that would be about $840,000 per kg, still 280 times a $3,000 per kg propellant price [C].

## 9. Not verified

- No Tianwen-2 report later than 13 October 2026 was found. A sampling attempt since then cannot be ruled out. The November 2027 return date has no CNSA source.
- Hayabusa's "under 1 mg" is from a talk write-up; the 2026 review prints "100µm", probably a misprint for 100 µg.
- Itokawa's period and mean size, Hayabusa's three-year delay, MASCOT's 17 hours, DART's impact speed, NEAR's landing, the Falcon 9 v1.1 capacity and the exact definition of JPL's round-trip velocity are recalled.
- The OSIRIS-REx launch price and cost cap, the Luna 16 mass, ARM's "approximately 20 t" and the 2023 Odin launch date come from search summaries of primary documents I did not open.
- The Falcon 9 and rideshare prices come from third-party pages citing SpaceX's price sheet, which would not load. The Starship price is a second-hand report of a filing.
- AstroForge's "platinum before the end of the decade" is a quotation in a search summary; no return mass or date is on the company pages I read.
- Jedicke et al. 2018 was read in abstract only; Sonter in its 1998 conference version, not the 1997 journal paper.
- GAO's 2017 assessment of ARM would not download; the cost cap is from JPL's 2016 release.
- TransAstra's March 2026 release was read only as a search summary (the host returned an error).
- I did not check whether Japan published a final Hayabusa2 cost.

## Sources

- [P1] Tasker, Connolly and Tachibana, "The science from asteroid sample return missions", arXiv:2604.22182 (24 April 2026): https://arxiv.org/abs/2604.22182
- [S2] Planetary Society write-up of a 2011 conference talk (via search): https://www.planetary.org/articles/2960
- [P3] NASA, Hayabusa mission page: https://science.nasa.gov/mission/hayabusa/
- [S4] AFP via Phys.org, December 2010: https://phys.org/news/2010-12-japan-low-cost-space-programme-limits.html
- [P5] JAXA curation centre, Ryugu sample: https://curation.isas.jaxa.jp/en/sample-curation/ryugu/
- [S6] Wikipedia, MINERVA rovers: https://en.wikipedia.org/wiki/MINERVA-II
- [P7] MEXT budget sheet for Hayabusa2 in Cabinet Office committee papers (2012): https://www8.cao.go.jp/space/comittee/dai2/siryou2-17.pdf
- [P8] NASA, bulk sample mass, 15 February 2024: https://science.nasa.gov/blogs/osiris-rex/2024/02/15/nasa-announces-osiris-rex-bulk-sample-mass/
- [P9] NASA, OSIRIS-REx sample return press kit, 2023: https://science.nasa.gov/wp-content/uploads/2023/09/osirisrexpresskit-2023.pdf
- [S10] Planetary Society, cost of OSIRIS-REx: https://www.planetary.org/space-policy/cost-of-osiris-rex
- [S11] NASA launch contract release, 2013 (via search): https://www.nasa.gov/news-release/nasa-selects-launch-services-contract-for-osiris-rex-mission ; cost cap from https://ntrs.nasa.gov/api/citations/20150000808/downloads/20150000808.pdf (via search)
- [S12] Shanghai Observer via Tencent News, 7 July 2026: https://news.qq.com/rain/a/20260707A01T5Y00
- [P13] CNSA, 6 July 2026: https://www.cnsa.gov.cn/n6758823/n6758838/c10760422/content.html
- [S14] Sky & Telescope, 9 July 2026: https://skyandtelescope.org/astronomy-news/tianwen-2-arrives-at-quasi-moon-kamo%CA%BBoalewa-returns-images/
- [P15] NASA curation, lunar samples: https://curator.jsc.nasa.gov/lunar/
- [S16] Planetary Society, cost of Apollo: https://www.planetary.org/space-policy/cost-of-apollo
- [S17] Smithsonian National Air and Space Museum, 16 December 2020: https://airandspace.si.edu/stories/editorial/revisiting-soviet-lunar-sample-return-missions ; Luna 16 from https://en.wikipedia.org/wiki/Luna_16 (via search)
- [P18] CNSA, 19 December 2020: https://www.cnsa.gov.cn/english/n6465652/n6465653/c6810963/content.html
- [P19] State Council of China, 28 June 2024: https://english.www.gov.cn/news/202406/28/content_WS667e2277c6d0868f4e8e8a54.html
- [S20] ESA, MMX launch (via search): https://www.esa.int/ESA_Multimedia/Images/2026/10/MMX_lifts_off_to_Mars_s_moon_Phobos
- [P21] NASA, NEA Scout: https://science.nasa.gov/mission/nea-scout/
- [P22] ESO release eso2515, 18 September 2025: https://www.eso.org/public/news/eso2515/
- [P23] ESA, Rosetta and Philae one year on: https://www.esa.int/About_Us/ESAC/Rosetta_and_Philae_one_year_since_landing_on_a_comet
- [P24] University of Arizona and NASA, 7 July 2022: https://news.arizona.edu/news/osiris-rex-scientists-taking-asteroid-sample-was-punching-ball-pit
- [P25] NASA, DART: https://science.nasa.gov/mission/dart/
- [S26] Wikipedia, Planetary Resources: https://en.wikipedia.org/wiki/Planetary_Resources
- [S27] National Space Society reprint of the January 2013 announcement: https://nss.org/deep-space-industries-offers-competition-for-planetary-resources-in-mining-asteroids/
- [S28] Wikipedia, Deep Space Industries: https://en.wikipedia.org/wiki/Deep_Space_Industries
- [P29] AstroForge, "An update on Missions 1 and 2", 30 July 2024: https://www.astroforge.com/updates-collection/an-update-on-mission-1-mission-2-same-name-new-vehicle-new-standard-for-space-exploration
- [P30] AstroForge, Odin debrief, 6 March 2025: https://www.astroforge.com/updates-collection/odint-mission-debrief
- [P31] AstroForge, Odin mission page: https://www.astroforge.com/odin-mission
- [P32] AstroForge, DeepSpace-2 page: https://www.astroforge.com/deepspace-2
- [P33] Karman+ abstract, EPSC-DPS 2025: https://meetingorganizer.copernicus.org/EPSC-DPS2025/EPSC-DPS2025-1407.html
- [P34] Karman+ abstract, EPSC 2024: https://meetingorganizer.copernicus.org/EPSC2024/EPSC2024-587.html
- [P35] Karman+ FAQ: https://www.karmanplus.com/faq/
- [P36] NASA NIAC, APIS study summary, 2015: https://www.nasa.gov/directorates/stmd/niac/niac-studies/apis-asteroid-provided-in-situ-supplies-100mt-of-water-from-a-single-falcon-9/
- [S37] TransAstra "New Moon" release, 18 March 2026 (via search): https://www.wboc.com/online_features/press_releases/transastra-launches-new-moon-study-to-capture-and-relocate-a-near-earth-asteroid/article_ac091ed4-6bfd-5843-9afe-61fce784afe6.html
- [P38] TransAstra release, 16 November 2026: https://www.newswire.com/news/transastra-successfully-tests-10-meter-capture-bag-designed-to-capture-22889775
- [S39] Origin Space profiles (via search): https://www.factoriesinspace.com/origin-space
- [P40] Keck Institute for Space Studies, "Asteroid Retrieval Feasibility Study", 2 April 2012: https://kiss.caltech.edu/final_reports/Asteroid_final_report.pdf
- [P41] JAXA, Hayabusa2: https://global.jaxa.jp/projects/sas/hayabusa2/
- [P42] McGuire et al., ARRM reference trajectory, AAS 17-585: https://ntrs.nasa.gov/api/citations/20170010282/downloads/20170010282.pdf
- [P43] Sonter, 1998 IAF congress paper: https://nss.org/wp-content/uploads/2023/05/the-technical-and-economic-feasibility-of-mining-the-near-earth-asteroids.pdf
- [P44] Hein, Matheson and Fries, arXiv:1810.03836: https://arxiv.org/abs/1810.03836
- [S45] Space.com and others on ARM Option B, March 2015 (via search): https://www.space.com/28934-nasa-asteroid-capture-mission-boulder.html
- [P46] JPL release, 2016: https://www.jpl.nasa.gov/news/nasa-asteroid-redirect-mission-completes-design-milestone/
- [P47] FY2018 budget blueprint, NASA section: https://www.nasa.gov/sites/default/files/atoms/files/2018_blueprint_nasa.pdf
- [S48] SpaceNews via Space.com, 14 June 2017: https://www.space.com/37196-nasa-closing-out-asteroid-redirect-mission.html
- [P49] JPL, ARRM page: https://www.jpl.nasa.gov/missions/asteroid-redirect-robotic-mission-arrm
- [P50] Jedicke et al. 2018, abstract: https://scholarsmine.mst.edu/geosci_geo_peteng_facwork/1362/ (doi 10.1016/j.pss.2018.04.005)
- [S51] KeepTrack, citing SpaceX's price sheet through Spaceflight Now, February 2026: https://keeptrack.space/deep-dive/how-much-does-a-falcon-9-launch-cost
- [S52] New Space Economy, February 2026 (via search): https://newspaceeconomy.ca/2026/02/27/spacex-rideshare-pricing-as-of-february-2026-what-it-costs-whats-included-and-how-buyers-budget-a-mission/
- [S53] University of Cambridge, 14 July 2026: https://www.cam.ac.uk/stories/space-cargo-costs-set-to-plummet
- [S54] Motley Fool, March 2026 (via search): https://www.fool.com/investing/2026/03/21/how-much-will-a-spacex-starship-launch-cost/
- [S55] Wikipedia, list of Starship launches (as of 14 November 2026): https://en.wikipedia.org/wiki/List_of_Starship_launches ; https://en.wikipedia.org/wiki/Starship_Propellant_Transfer_Demonstration
- [S56] Coverage of NASA OIG report IG-26-004, 10 March 2026 (via search): https://spaceflightnow.com/2026/03/10/nasa-inspector-general-assesses-agencys-management-of-moon-lander-risk/
- [S57] Satnews, 26 September 2026 (via search): https://satnews.com/2026/09/26/u-s-space-force-schedules-2027-on-orbit-servicing-missions-with-astroscale-u-s-and-starfish-space/
- [S58] University of Edinburgh, 18 February 2026: https://www.ph.ed.ac.uk/news/2026/microbes-harvest-metals-from-meteorites-aboard-space-station-26-02-18 ; https://astrobiology.com/2026/02/03/microbial-biomining-from-asteroidal-material-onboard-the-international-space-station/
- [S59] Intuitive Machines release, 24 January 2023 (via search): https://www.businesswire.com/news/home/20230124005210/en
- [S60] Space.com, 21 August 2024: https://www.space.com/asteroid-mining-astroforge-docking-mission-2025
- [P61] AstroForge, "We Built the Spacecraft", 3 June 2026: https://www.astroforge.com/updates-collection/we-built-the-spacecraft
- Platinum price: Kitco, bid $1,295.00 per ounce, $41.64 per gram, 21 November 2026 19:56 New York time [P]: https://www.kitco.com/charts/liveplatinum.html
- [V] items: `verify-facts-missions.md` in this folder, which lists its own sources.
