# Verification: observing-window feasibility ("observe this next" list)

Checker run of 2026-11-21. Status: COMPLETE.

Inputs: local NHATS snapshot (7,229 objects, fetched 2026-11-21), local SBDB snapshot (43,367 NEOs), JPL Horizons ephemerides and MPC observation records for a random sample of 130 objects (one request at a time), and primary web pages fetched today.

Tags: **[V]** computed or read today from a primary source; **[S]** search-result snippet or secondary source, not opened; **[E]** my estimate.

## Bottom line

1. **Return windows are few.** 59% of NHATS objects have a "next optical opportunity" listed, but 58% of those are flagged survey-recovery only: nobody can point at them. 1,786 objects (25%) have a pointable window before 2046. For delta-v < 6 km/s, pointable, brighter than V 22 and starting before 2030, the list is **21 objects**; 6 of them get brighter than V 20.
2. **The discovery apparition is where the volume is, and it is short.** About 650 NHATS objects are added per year (54 per month). In a 130-object sample of those first seen in 2024-2026, 5% (95% interval 2-10%) stayed brighter than V 18 for a day or more once two days had passed since first detection, 32% (24-40%) brighter than V 20, and 59% (50-67%) brighter than V 21. Median fading is 0.2, 4.0 and 4.8 mag after 1, 4 and 6 weeks.
3. **Rubin has not changed the discovery rate.** Monthly additions are flat since 2021 and lower in July-October 2026 than a year earlier. Rubin discovered 3 of the 130 sampled objects, all from July-August 2025 data reported later in batches, too late for any follow-up.
4. **Radar is off the table until 2028.** Goldstone's 70 m antenna has been offline since 2025-09-16 and its overhaul runs to October 2028. Arecibo opportunities in the NHATS table are dead entries.
5. **The gap is real but narrow.** NEOfixer scores astrometry for planetary defence only; ESA's priority list was switched off on 2025-08-07; MANOS picks targets by hand; the new LCO MuSCAT programme (1,000 small NEOs by end of 2027) selects on H > 25, V < 21 and age under 5 weeks, with no accessibility term. No public list ranks characterization targets by accessibility and by what the observation would settle.
6. **Realistic yield [E]:** with no telescope allocation, about 5-15 NHATS objects a year could gain a spin period (0-2 of them under 6 km/s) and almost none a colour. With a 2 m class partner or allocation, 20-60 a year (5-15 under 6 km/s). The ceiling set by geometry is about 200 a year at V < 20 (about 20 under 6 km/s).
7. **Recommendation:** publish the static return-window short list in the first release (it is one table and costs nothing). Make the daily discovery-apparition list a later phase, and only with an observing partner; the binding constraint is 2 m class telescope time within a week of discovery, not the list.

## 1. Future windows [V]

Script: `data/research/scripts/ow_windows.py`

How JPL defines the window (https://cneos.jpl.nasa.gov/nhats/obs.html): ephemeris to 2045; peak V must reach 24.0 or brighter; solar elongation above 60 degrees; 3-sigma plane-of-sky uncertainty below 1.5 degrees over 3 days; at least 5 degrees from the galactic equator; 4 days around full moon excluded. Objects that fail the uncertainty test get a second pass that simulates chance rediscovery by a survey (limit V 21.5 at elongation above 70 degrees, or V 24.0 inside the Rubin footprint). The API marks these `obs_flag = "S"`, "survey recovery possible" (https://ssd-api.jpl.nasa.gov/doc/nhats.html). The table lists only the next window per object, so counts for later years are lower bounds.

- 7,229 objects; median H 26.2; median arc 12 days. The first-round figures hold.
- 4,262 (59%) have a next window listed; 2,967 (41%) have none before 2046.
- 2,476 of the 4,262 (58%) are survey-recovery only. **1,786 objects (24.7%) have a normal, pointable window.** The flag follows orbit quality: no object with condition code 0-3 is flagged S; 2,339 of 2,655 windowed objects with code 6-9 are.
- 212 windows are open today; 70 of those belong to objects discovered since August 2026.
- Peak V of listed windows: median 22.8, range 13.6 to 24.0. Median window length 34 days (quartiles 16 and 61).

Objects whose next window starts before a date (all windows, S included):

| Subset | objects | any window | before 2028 | before 2030 | before 2035 |
|---|---|---|---|---|---|
| all | 7,229 | 4,262 | 771 | 1,553 | 2,709 |
| delta-v < 6 km/s | 726 | 383 | 49 | 90 | 193 |
| delta-v < 5 km/s | 286 | 121 | 14 | 27 | 51 |

Peak brightness of those windows (V < 20 / 20-22 / 22-24 / fainter):

| Subset | before 2028 | before 2030 | before 2035 |
|---|---|---|---|
| all | 73 / 189 / 507 / 2 | 133 / 384 / 1,033 / 3 | 221 / 660 / 1,824 / 4 |
| delta-v < 6 | 4 / 16 / 29 / 0 | 10 / 23 / 57 / 0 | 22 / 45 / 126 / 0 |
| delta-v < 5 | 2 / 4 / 8 / 0 | 3 / 5 / 19 / 0 | 4 / 10 / 37 / 0 |

By orbit condition code (0-2 / 3-5 / 6-9):

| Subset | before 2028 | before 2030 | before 2035 |
|---|---|---|---|
| all | 337 / 122 / 312 | 559 / 256 / 738 | 749 / 474 / 1,486 |
| delta-v < 6 | 15 / 22 / 12 | 24 / 35 / 31 | 49 / 71 / 73 |
| delta-v < 5 | 4 / 9 / 1 | 10 / 12 / 5 | 16 / 21 / 14 |

Pointable (non-S) windows only, cumulative, V < 20 / V < 22 / any:

| Subset | before 2028 | before 2030 | before 2035 |
|---|---|---|---|
| all | 57 / 199 / 585 | 90 / 333 / 995 | 114 / 443 / 1,427 |
| delta-v < 6 | 3 / 15 / 41 | 6 / 21 / 65 | 11 / 37 / 125 |
| delta-v < 5 | 2 / 6 / 14 | 3 / 8 / 24 | 4 / 10 / 38 |

Pointable windows by start year (next window only):

| Year | pointable | peak V < 22 | V < 20 | V < 20 and no period in SBDB | V < 18 | delta-v < 6 and V < 22 | delta-v < 6 and V < 20 |
|---|---|---|---|---|---|---|---|
| 2027 | 329 | 86 | 26 | 19 | 5 | 8 | 2 |
| 2028 | 236 | 85 | 24 | 16 | 3 | 5 | 3 |
| 2029 | 174 | 49 | 9 | 5 | 3 | 1 | 0 |
| 2030 | 135 | 41 | 11 | 10 | 0 | 4 | 1 |

So return apparitions offer about 25 objects a year brighter than V 20 across the whole list, and 2 or 3 a year under 6 km/s.

### Radar

- 213 objects list a Goldstone opportunity (SNR 10 or more) between now and 2045: 58 before 2030, 113 before 2035. Under 6 km/s: 29 in total, 10 before 2030, 15 before 2035. Under 5 km/s: 12. Median listed SNR 56; 87 at SNR 100 or more.
- 566 list an Arecibo opportunity; 581 list either. Arecibo collapsed in 2020, so those entries are dead. The first-round figure "582 objects have a Goldstone or Arecibo SNR" is right to within one object but overstates the real opportunity by a factor of 2.7.
- **Goldstone's DSS-14 is offline.** It over-rotated on 2025-09-16; NASA's 2026-06-05 statement says it "will remain offline" through a planned overhaul "expected to be completed by October 2028" (https://www.nasa.gov/directorates/somd/space-communications-navigation-program/nasa-concludes-antenna-mishap-investigation-releases-report/). Limited observations might start in April 2028, and a bistatic DSS-13 to Green Bank link runs at about a tenth of the sensitivity [S]. Of the 213 Goldstone entries, 35 fall before October 2028 (7 under 6 km/s) and are probably lost. From October 2028 to 2034 there are 78 (8 under 6 km/s: 2016 EP84, 2009 CV, 2019 GM1, 2014 YN, 2020 OM6, 2001 CQ36, 2020 VV, 2007 YF).

### Short list: delta-v < 6 km/s, window starts before 2030, peak V < 22

33 objects match at any orbit quality. 12 are survey-recovery only, which leaves **21 with a pointable window**. I use JPL's own pointing test (the non-S flag) as "recoverable": it is the plane-of-sky uncertainty at the window, which is what an observer needs. Requiring condition code 5 or better instead also gives 21, but a different 21: it admits three S-flagged objects (2020 XF, 2016 BS67, 2022 DD2) and drops three recently discovered objects with code 6 (2026 VD9, 2026 VY17, 2026 MF2). 18 objects pass both tests; 9 have code 0-2.

Of the 21: 6 peak brighter than V 20 (2026 VD9, 2026 HT, 2009 HC, 2000 SG344, 2015 BG92, 2009 CV); 7 windows are open today; SBDB lists a rotation period for 4 and a spectral type or albedo for none. SBDB's physical fields are stale, so check SsODNet and LCDB before calling any of these uncharacterized.

| Object | H | size m (NHATS) | delta-v | OCC | window | peak V | arc d | period (SBDB) | Goldstone |
|---|---|---|---|---|---|---|---|---|---|
| 2012 TF79 | 27.4 | 6-26 | 4.38 | 3 | 2026-11-21 to 2027-05-11 | 20.9 | 67 | - | - |
| 2018 LQ2 | 25.0 | 17-78 | 5.84 | 0 | 2026-11-21 to 2027-01-19 | 21.5 | 3,111 | 0.47 h | - |
| 2011 AA37 | 22.9 | 46-205 | 5.85 | 0 | 2026-11-21 to 2027-03-20 | 21.7 | 5,783 | 10 h | - |
| 2025 VG5 | 26.7 | 8-35 | 5.37 | 2 | 2026-11-21 to 2026-12-13 | 21.9 | 365 | - | - |
| 2026 VC6 | 27.0 | 7-31 | 5.93 | 5 | 2026-11-21 to 2026-12-07 | 21.9 | 13 | - | - |
| 2026 VD9 | 25.2 | 16-70 | 5.44 | 6 | 2026-11-21 to 2026-12-27 | 18.9 | 14 | - | 2026-11, SNR 13 (antenna offline) |
| 2026 VY17 | 27.3 | 6-28 | 5.42 | 6 | 2026-11-21 to 2026-12-10 | 21.2 | 2 | - | - |
| 2026 FU | 27.6 | 5-23 | 4.14 | 5 | 2027-02-09 to 2027-03-28 | 22.0 | 5 | - | 2036-09, SNR 22,000 |
| 2026 HT | 24.2 | 25-113 | 4.64 | 4 | 2027-02-12 to 2027-07-15 | 17.5 | 57 | - | 2027-03, SNR 15 (antenna offline) |
| 2009 HC | 24.6 | 20-91 | 4.44 | 0 | 2027-04-02 to 2027-07-06 | 18.0 | 6,041 | - | 2027-04, SNR 140 (antenna offline) |
| 2015 JD3 | 25.5 | 14-62 | 4.84 | 4 | 2027-05-06 to 2027-12-21 | 21.1 | 76 | - | - |
| 2026 MF2 | 25.7 | 12-56 | 5.28 | 6 | 2027-06-21 to 2027-10-04 | 21.4 | 21 | - | - |
| 2025 PN7 | 26.4 | 9-41 | 4.05 | 0 | 2027-07-07 to 2027-09-25 | 21.4 | 4,651 | - | - |
| 2018 MQ5 | 24.1 | 26-118 | 5.77 | 3 | 2027-11-16 to 2028-07-12 | 21.8 | 154 | - | - |
| 2012 EC | 23.3 | 39-173 | 5.91 | 0 | 2027-11-19 to 2028-01-30 | 21.6 | 3,937 | - | 2038-06, SNR 280 |
| 2022 BA6 | 26.4 | 9-40 | 5.53 | 5 | 2028-01-02 to 2028-02-02 | 21.5 | 30 | - | 2028-02, SNR 18 (antenna offline) |
| 2000 SG344 | 24.7 | 20-89 | 3.55 | 3 | 2028-04-28 to 2028-09-11 | 19.1 | 507 | - | 2028-05, SNR 58 (antenna may be back) |
| 2015 BG92 | 25.1 | 17-74 | 5.17 | 4 | 2028-06-16 to 2029-03-06 | 19.0 | 39 | 0.179 h | - |
| 2013 WA44 | 23.4 | 37-165 | 5.30 | 0 | 2028-10-13 to 2029-10-10 | 20.3 | 5,628 | 0.35 h | - |
| 2009 CV | 24.3 | 24-108 | 5.95 | 0 | 2028-11-23 to 2029-03-03 | 19.1 | 2,708 | - | 2029-03, SNR 46 |
| 2020 OK5 | 25.4 | 14-65 | 4.90 | 2 | 2029-06-29 to 2030-04-06 | 21.2 | 207 | - | - |

The 12 survey-recovery entries that also match on delta-v, date and brightness: 2019 UO1, 2020 SN6, 2007 WA, 2020 XF, 2020 OG, 2016 BS67, 2009 WC106, 2009 WR52, 2014 MP, 2021 KP1, 2022 DD2, 2006 HE2. They are candidates for "watch the survey feeds", not for pointing.

## 2. Discovery apparitions, 2024-2026 [V]

Scripts: `data/research/scripts/ow_fetch_sample.py` and `ow_discovery.py` in the same directory.

Method. 1,880 NHATS objects have an SBDB first observation on or after 2024-01-01 (median H 26.6, median arc 8 days; 192 under 6 km/s, 78 under 5 km/s). I drew 130 at random (seed 20261121) and fetched for each a geocentric Horizons ephemeris from 60 days before to 120 days after first observation at 4-hour steps (V, sky rate, distance, elongation), and its MPC observation records. "Usable" below means solar elongation of 60 degrees or more. Moon, weather, declination and galactic latitude are not applied, so every number is an upper bound for a single site. Intervals are 95% Wilson intervals on 130 objects.

Check on the ephemeris magnitudes: the median reported magnitude on the first night is 20.9, against 21.1 predicted; the object-by-object difference has median -0.24 mag (quartiles -0.40 and -0.10), which is the usual offset of survey bands from V.

### How bright, for how long, how fast

| Quantity | 25th pct | median | 75th pct |
|---|---|---|---|
| V at first observation (ephemeris) | 19.8 | 21.1 | 21.8 |
| Brightest usable V at or after first observation | 18.9 | 19.9 | 21.1 |
| Brightest magnitude any observer reported (MPC) | 18.2 | 19.2 | 20.4 |
| Days from first observation to peak brightness | -0.7 | +2.8 | +10.8 |
| Distance at first observation, au | 0.02 | 0.04 | 0.07 |
| Sky rate at first observation, arcsec/min | 2.4 | 6.4 | 17.6 |
| Sky rate at peak brightness, arcsec/min | 7.8 | 21 | 69 |
| Sky rate while brighter than V 20, arcsec/min | 13 | 21 | 40 |
| Sky rate while brighter than V 18, arcsec/min | 54 | 71 | 166 |
| Fading after 1 week, mag | -0.5 | +0.2 | +2.1 |
| Fading after 2 weeks, mag | -0.2 | +1.7 | +4.1 |
| Fading after 4 weeks, mag | +1.5 | +4.0 | +6.1 |
| Fading after 6 weeks, mag | +2.5 | +4.8 | +7.2 |

This replicates Galache et al. 2015 (arXiv:1504.00712), who give typical fading of 0.5, 3.5 and 5 mag after 1, 4 and 6 weeks. In 22 of 130 (17%) the object had been usable and more than 0.5 mag brighter before it was first detected.

Fraction of new NHATS objects that stay brighter than a limit, and for how long:

| Limit | ever, after first detection | 1 day or more after first detection | 1 day or more, starting 2 days after first detection | 3 days or more, starting 2 days after | median usable days for those that reach it (whole apparition) |
|---|---|---|---|---|---|
| V < 18 | 13% (17) | 5.4% (7) | **4.6% (6); 2.1-9.7%** | 3.8% (5) | 1.5 |
| V < 19 | 28% (36) | 18% (24) | 12% (16); 7.7-19% | 8.5% (11) | 2.2 |
| V < 20 | 52% (68) | 47% (61) | **32% (41); 24-40%** | 22% (28) | 4.8 |
| V < 21 | 73% (95) | 71% (92) | **58% (76); 50-67%** | 45% (58) | 9.8 |
| V < 22 | 94% (122) | 92% (119) | 84% (109); 77-89% | 78% (101) | 17 |

The "starting 2 days after" columns allow for the designation to be announced and an observer to react. The result does not depend much on where the clock starts: in 22% of objects the discovery-flagged observation came more than a day after the first one (precoveries), and counting from that observation instead gives 5.4% / 34% / 64% at one day's lag and 4.6% / 29% / 55% at two days' lag for V < 18 / 20 / 21. Median usable days over all 130 objects are 0 for V < 18 and V < 19, 2.0 for V < 20, 7.8 for V < 21 and 17 for V < 22. For those that get brighter than V 20, the last usable moment brighter than V 20 comes a median 3.9 days after first detection (quartiles 1.8 and 11.8).

Answers to the brief:

- **Lightcurve with a 0.4-1 m telescope (V < 18): about 5% of new NHATS objects (2-10%), or roughly 30 a year (14-63).** They move at a median 71 arcsec/min while that bright, so the telescope must track at the object's rate and use exposures of seconds. Requiring under 30 arcsec/min as well leaves 2 of 130. None of the 59 sampled objects with H of 27 or more qualified: the six that did have H 24.6-26.8. A 10 m object is essentially never a small-telescope lightcurve target.
- **Colours with a 2-4 m telescope (V < 20 to 21): 32% to 59%, or roughly 200 to 380 a year.** For 3 days or more: 22% to 45%.
- Under 6 km/s (10.2% of new objects, 66 a year), if brightness is independent of delta-v: about 3 a year at V < 18, 21 at V < 20, 39 at V < 21. The sample has only 10 such objects (1, 3 and 5 of them qualify), so this is an assumption, not a measurement.
- One of the six V < 18 objects, 2025 EF4, did get an amateur lightcurve (Birtwhistle, Minor Planet Bulletin 52-4), so the route works when the object is bright.
- Astrometric follow-up is not the gap: the median sampled object has 31 observations from 7 stations.

### Monthly additions and Rubin

NHATS objects by SBDB first-observation date:

| Year | objects | per month |
|---|---|---|
| 2020 | 567 | 47 |
| 2021 | 645 | 54 |
| 2022 | 612 | 51 |
| 2023 | 603 | 50 |
| 2024 | 639 | 53 |
| 2025 | 700 | 58 |
| 2026 to 21 Nov | 541 | 48 (Jan-Oct mean); 63 in the first 21 days of November |

Monthly counts swing from 21 to 99 with season. NHATS objects are a steady 21% of all NEOs first observed (3,002 in 2024, 3,156 in 2025, 2,511 so far in 2026). July-October 2026 had 175 new NHATS objects against 250 in July-October 2025 and 238 in 2024; all NEOs: 839 against 1,206 and 1,160. I did not look for the cause of that drop.

**Rubin has not raised the rate.**

- Discovery stations in the sample: Pan-STARRS 2 (F52) 36, Mt. Lemmon (G96) 30, V00 14, Pan-STARRS 1 (F51) 13, Catalina (703) 10, others 24, **Rubin (X05) 3** (2.3%; 0.8-6.6%). Four of 130 have any Rubin observation (3.1%), in line with the first round's 5 of 1,000 across all years.
- The three Rubin discoveries (2025 OP4, 2025 OE342, 2025 PN160) were first observed in July-August 2025, before the survey began, at V 21.4-22.8, with arcs of 10-11 days. Two have no observation from any other station. They reached the MPC in later batches, so no one could follow them up.
- Rubin's own posts: submissions to the MPC were in ad hoc batches in February 2026, with "roughly weekly" promised (https://www.rubin.community/t/rubin-solar-system-february-2026-updates/11640). The LSST began on 2026-06-29 (https://survey-strategy.lsst.io/progress). A storm stopped work in mid-July; a forum topic "Rubin Observatory is back on sky!" is dated 2026-10-29; the camera was shut down again on 2026-11-15 and "we remain in that state for now" (https://www.rubin.community/t/rubin-status-november-17-2026/12959). By those dates the survey has run for about five weeks in total.
- Consequence for the plan: when Rubin does report daily, its discoveries will arrive at V 22-24, beyond every route in section 5 except 4-8 m time. Rubin will add objects, not follow-up targets.

## 3. What each observation buys for a 10 m object

A 10 m object has H of about 27.7 at albedo 0.15 (26.6 at 0.40, 28.9 at 0.05). At 30 degrees phase it is V 18 at 0.006 au (2.5 lunar distances), V 20 at 0.016 au (6 lunar distances), V 21 at 0.025 au (10 lunar distances) and V 22 at 0.040 au [E, from the H-G relation with G = 0.15].

| Observation | What it settles | Brightness and telescope needed | Evidence |
|---|---|---|---|
| Rotation lightcurve | Period and amplitude; tumbling. Decides whether a spacecraft can work at the surface. The TTT survey puts the fast-rotator share at 94-96% for H > 26 | V < 17-18 with 0.4-0.8 m; V 18-20 with 2 m; V up to about 21-22 with 4 m. Exposures of seconds, so aperture matters more than for slow rotators | TTT survey: 249 NEAs observed, 161 periods, 0.8 m for H > 22 and 2 m for H > 24, needs S/N > 20 for 30 min (arXiv:2602.18562) [V]. Galache 2015 asks for a 4 m or larger for fast-cadence lightcurves within days [V]. Birtwhistle, 0.4 m: 29 NEA lightcurves a year [V]. 2022 OB5: 1.542 min from the 10.4 m GTC (first round) |
| Visible colours | S, C, X, V complex. Cannot split the X complex | V < 21 with 2 m and a simultaneous multi-band camera (S/N 10 in 7 min); V < 22 with 4 m. Sequential filters need a lightcurve correction for fast rotators | LCO MuSCAT pilot (EPSC-DPS2025-997) [V]; MANOS colours, V below about 22 on 4 m telescopes, 151 of 189 objects needed a lightcurve correction (arXiv:2603.15872) [V]; Seimei 3.8 m three-band video of three sub-minute rotators (arXiv:2606.17047) [V] |
| Thermal infrared | Albedo, hence size, hence the E/M/P split of the X complex | Space only at this size. Spitzer detected 2011 MD (about 6 m) at 2.2 sigma and did not detect 2009 BD; Spitzer ended in 2020. Today that means JWST discretionary time, or NEO Surveyor after its 2027 launch | Mommert et al. 2014, arXiv:1406.5253 [S] |
| Polarimetry | Albedo without a thermal measurement | Needs several phase angles and V below about 17 on a 1-2 m polarimeter [E]. Done for 2023 DZ2 (30 m, bright flyby): albedo 0.49, E type | Reddy et al. 2024, PSJ 5, 141 [S] |
| Radar | Size, spin, shape hints, circular polarization ratio (a metal and roughness indicator), and astrometry that secures the orbit for decades | Objects under 140 m are detectable only within about 10 lunar distances; 90% of radar targets with H > 22 are targets of opportunity within days to weeks of discovery. Goldstone is offline to 2028 | Goldstone small-NEA paper [S]; Naidu et al. 2016, arXiv:1604.01080: Goldstone observed 24% of the NEAs it could have [V]; section 1 for the outage |
| Astrometry at a second apparition | Orbit quality (condition code 6-8 down to 0-2), which decides whether the object is a target at all; with a long enough arc, the solar-radiation-pressure area-to-mass ratio, hence a density estimate | Recovery at V 22-24 needs 2-8 m. The area-to-mass ratio has been detected only for a handful of objects with H > 27 that had Earth encounters (2009 BD: 2.97 +/- 0.33 e-4 m2/kg) | Micheli et al. 2012, arXiv:1106.0564; Del Vigna et al. 2018, arXiv:1805.05947 [S] |

The useful ordering for a 10 m target is: lightcurve first (cheap, and a sub-minute period rules the object out for surface work), colours second, astrometry at return third. Thermal and radar data are not obtainable on request.

## 4. Who already does this

| Programme | What it does | Accessibility-aware? | Composition-aware? | Status | Source |
|---|---|---|---|---|---|
| NEOfixer (Catalina) | Priority = Importance x Confidence x Benefit x Urgency / Cost. Importance is "from a planetary defense perspective": size from H, MOID, impact probability. Benefit is orbit improvement. Objects with q > 1.3 au score zero | No. No mention of NHATS, delta-v, lightcurves, spectra or radar | No | Live | https://neofixer.arizona.edu/faq/how-does-neofixer-assign-priority [V] |
| ESA NEOCC Priority List | Astrometric follow-up priority | No | No | **Decommissioned 2025-08-07**: "no longer available. Users are invited to refer to the NEOfixer service" | https://neo.ssa.esa.int/system-updates [V]; the old URL returns Not Found today |
| MANOS (Lowell) | Lightcurves, colours, spectra of small NEOs. Priority to delta-v < 6 km/s (their own delta-v, not NHATS), H > 20, MOID < 0.05 au, predicted V below about 22. Targets "usually picked in the hours before the start of each observing night". 4 m class nights "scheduled months in advance", which the authors say limits rapid response | Yes, by hand | It measures it | Colour-paper data run 2014-04-24 to 2025-02-06 over 83 nights; site says 523 objects in "first generation MANOS". No 2026 status found; the target summary page shows no public table | arXiv:2603.15872 [V]; https://manos.lowell.edu/overview/goals [V] |
| LCO NEO Follow-up Network (NEOexchange) | Ten 1 m telescopes at four sites; astrometry, lightcurves, spectra; "focused on" radar targets and NHATS targets | Yes, as a stated focus | It measures it | Portal has 2026 target pages [S] | arXiv:2102.10144 [V] |
| LCO MuSCAT rapid response (Cantelas, Trilling, Lister, Moskovitz et al.) | Four-band simultaneous colours on the 2 m telescopes. Selection: designated within the last 5 weeks, V < 21, H > 25, rate under 1,000 arcsec/h. Automated target selection, requests and reduction. Pilot: 10 NEOs, November 2024 to February 2025. Aim: rough taxonomy for about 1,000 very small NEOs through the end of 2027B | **No** | It measures it | Running; no 2026 results found | https://meetingorganizer.copernicus.org/EPSC-DPS2025/EPSC-DPS2025-997.html [V] |
| TTT fast-rotator survey (IAC) | Daily list of observable NEAs from Horizons; H > 22 to the 0.8 m units, H > 24 to the 2 m. 249 observed, 161 periods | No | No (unfiltered) | Running | arXiv:2602.18562 [V] |
| NEOROCKS (EU, 2020 to mid-2023) | Colours for 93 NEOs from a 1.2 m; a Rapid Response Experiment in spring 2022 observed 5 objects | No | It measured it | Ended. Results paper for the experiment listed as "in preparation" | Hromakina et al. 2023, MNRAS 520, 3143 [V] |
| IAWN campaigns | One named object at a time: 1999 KW4 (2019), 2019 XS (2021), Apophis (2021), 2005 LW3 (2022), 2023 DZ2 (2023, rapid-response characterization), 2024 YR4, 2025 FA22, 3I/ATLAS | No | No | About one a year | https://iawn.net/obscamp/ [V] |
| Pravec group (Ondrejov) with NASA Goddard | Lightcurves of mission targets: 82 asteroids, 15 of them planned or possible targets, including for Karman+'s High Frontier. H 12.6 to 26.8 | Yes | No | July 2026 abstract | https://ntrs.nasa.gov/citations/20260004003 [V] |
| Karman+ | No telescope programme found. Targets chosen "primarily based on accessibility, absolute magnitude as a proxy for size, and rotation period"; primary 2022 DC5, backup 2021 UH2. Relies on others' photometry | Yes | Limited | Private leaderboard; Prospector code public (first round) | https://meetingorganizer.copernicus.org/EPSC-DPS2025/EPSC-DPS2025-1407.html [V] |
| AstroForge | No telescope programme found. A summary of a company post points to the 4.3 m Lowell Discovery Telescope | - | - | Unverifiable | [S] |
| Rubin-era rapid characterization | No dedicated programme found beyond the LCO MuSCAT and TTT work above. Rubin's own outputs are colours and periods from survey data (Greenstreet et al. 2026: 76 objects with periods, one NEO) | - | - | - | [S] |

**The gap.** Three things do not exist in public: (1) a daily list of characterization targets, as opposed to astrometry targets; (2) an accessibility term in any automated ranking (the LCO MuSCAT selection would take a 12 km/s object over a 4.5 km/s one if both pass H, V and age); (3) a statement of what the observation would settle for that object (for example "period unknown; a sub-10-minute period removes it from the surface-operations list"). NHATS supplies the window dates for returns but nothing for the discovery apparition, where the object is in the table for days before it fades.

The gap is narrow, though. The people who would use the list already run their own selection, and two of them (LCO, MANOS) already weight accessibility by hand. The most likely useful form is an input to their queues, not a new service competing with NEOfixer.

## 5. Routes to observations for an unaffiliated team

| Route | Aperture and reach | Cost | Fit | Source |
|---|---|---|---|---|
| iTelescope | 0.43-0.61 m common; up to 0.74 and 0.85 m in Chile. Lightcurves to about V 17 [E] | Plans from $39.95 to $489.95 per 28 days; a 0.43 m costs $89-179 per hour depending on plan; billed per session or per exposure | Works for the 30 or so objects a year brighter than V 18; needs rate tracking | Rates from a search snippet of the vendor's undated page [S]; telescope list and billing rules [V] https://www.itelescope.net/telescope-rates-premium ; the live price page refused the fetch |
| Telescope Live | 0.6 m (CHI-1, 110 credits per hour) and 0.7 m (SPA-2, 120 credits per hour) | About $1.40 per credit, so about $150-170 per hour | As above; moving-target support not confirmed | [S] |
| Slooh | Not stated on the pricing page | $4.95 a month to $499 a year | Education product; custom moving-target scheduling not stated. Not a route | https://www.slooh.com/pricing [V] |
| LCO director's discretionary time | 0.4 m, 1 m, 2 m (MuSCAT) | Free if awarded | **Best fit.** "Investigators worldwide (through the Heising-Simons funded Open Access time) are eligible to submit proposals for discretionary time", funded for 2026B-2028B; proposals "may be submitted at any time", decisions typically in under a week; the time expires at the end of the semester | https://lco.global/observatory/proposal/process/ [V] |
| Nordic Optical Telescope fast track | 2.56 m | "Open to anybody"; non-Nordic users pay 1,670 euro per 10-hour night pro rata; 4 hours at most; answer within 2 weeks | Fits return windows, not discovery apparitions | https://www.not.iac.es/observing/service/ [V] |
| Other 2-4 m discretionary time | - | - | Not checked today | - |
| Amateur lightcurve observers | 0.3-0.5 m. One observer (Great Shefford) publishes 29 NEA lightcurves a year, all during close approaches | Free | Real capacity for bright fly-bys; these observers already pick from the NEO confirmation page and close-approach lists | https://birtwhistle.org.uk/Results.htm [V] |
| Minor Planet Mailing List | Announcement channel | Free | Could not open the group page today (HTTP 402); activity not verified | - |
| BAA Asteroids and Remote Planets Section | Astrometry and photometry by members | Free | A channel to observers, not a queue | [S] |
| AAVSO | Variable stars | - | No asteroid programme found | [S] |
| Unistellar planetary-defence network | 11 cm telescopes; current targets peak at V 13-14.5 | Free | Too shallow for NHATS objects, apart from rare very close passes | https://science.unistellar.com/planetary-defense/missions/ [V] |
| claudestronomy.com | - | - | The page offers credits and small grants and says: "if a candidate earns telescope time, we can help you ask for it." No telescope time of its own, no application form; contact is by email or text | https://claudestronomy.com [V] |

## 6. Conclusion with numbers

Supply (geometry only, elongation 60 degrees or more, per year):

| | all NHATS | delta-v < 6 km/s |
|---|---|---|
| New objects | about 650 | about 66 |
| Discovery apparition, V < 18 for a day or more (small telescope lightcurve) | 30 (14-63) | about 3 |
| Discovery apparition, V < 20 for a day or more (2 m lightcurve, 2-4 m colours) | 205 (157-260) | about 21 |
| Discovery apparition, V < 21 for a day or more (2 m simultaneous colours) | 380 (325-433) | about 39 |
| Return window, pointable, peak V < 20 (2027-2028 average) | 25 | 2-3 |
| Return window, pointable, peak V < 22 (2027-2028 average) | 85 | 5-8 |

Demand side, for scale: one amateur site delivers 29 NEA lightcurves a year; the TTT survey has 161 periods from 249 objects; the LCO MuSCAT pilot did 10 objects in 3.5 months and aims for about 330 a year; MANOS lists 523 objects for its first generation, about 50 a year if that spans a decade [E].

Realistic yield from a public list [E]:

- **No telescope allocation** (amateurs and bought small-telescope time pick it up): 5-15 NHATS objects a year gain a spin period, 0-2 of them under 6 km/s. Colours: close to none, because under V 18 there are only about 30 objects a year and amateurs rarely take calibrated multi-band data on fast movers.
- **With a 2 m class route** (LCO discretionary time, or the LCO MuSCAT or TTT teams taking the accessibility ranking as an input): 20-60 a year gain a period or a colour, 5-15 of them under 6 km/s. This assumes a single-site availability factor near 0.3-0.5 for weather, declination and moon, and a period success rate near the TTT's 65%.
- **Ceiling:** about 200 a year at V < 20, about 20 a year under 6 km/s.

Is it worth a later phase? Yes, in two parts with different costs.

1. **Static return-window table: put it in the first release.** It is a filter on data the project already holds (section 1). It is honest about the answer: 21 pointable objects under 6 km/s before 2030, 6 of them brighter than V 20.
2. **Daily discovery-apparition list: a later phase, and conditional.** The computation is small (about 2 new NHATS objects a day; one ephemeris each). It only produces measurements if someone with a 1-2 m telescope acts within about 4 days, the median time a V < 20 object stays that bright after first detection. Before building it, ask the LCO MuSCAT and TTT teams whether they would take an accessibility-and-information-value ranking as an input. If neither would, the list changes little.

Do not plan on radar before late 2028, on Rubin as a source of follow-up targets, or on thermal data at all.

## Limits of this check

- The discovery-apparition numbers rest on 130 objects. The under-6 km/s subset has 10, so its per-year figures assume brightness is independent of delta-v.
- "Usable" ignores moon, weather, declination, galactic latitude and twilight. A single site sees perhaps a third to a half of it.
- Ephemerides are geocentric; topocentric rates at closest approach are higher.
- The NHATS table gives one window per object, so return-window counts after about 2029 are lower bounds.
- "No period in SBDB" is not "no period known": SBDB lists none for any of the 1,880 objects first seen in 2024-2026, though at least one (2025 EF4) has a published lightcurve.
- Not verified today: MANOS activity in 2026; AstroForge's telescope use; iTelescope and Telescope Live current prices (vendor price pages refused the fetch); Minor Planet Mailing List activity; discretionary-time rules at telescopes other than LCO and the Nordic Optical Telescope; the exact dates of Rubin's July-October 2026 outage (a mid-July storm stop and an "back on sky" post dated 2026-10-29 are consistent with the first round's 07-15 to 10-27).
- The yield figures in section 6 are my estimates, not measurements.

## Files

- Scripts: `data/research/scripts/ow_windows.py`, `ow_fetch_sample.py`, `ow_discovery.py` (same directory).
- Outputs: `data/research/out-ow/` (`ow_windows_summary.json`, `ow_shortlist.tsv`, `ow_shortlist_anyocc.tsv`, `ow_discovery_summary.json`, `ow_discovery_objects.json`).
- Downloads: `data/research/dl/obs-window/` (`sample.json`, `horizons/`, `mpc/`, `web/`).
- The tables above carry the numbers.

## Sources

- NHATS API and observability rules: https://ssd-api.jpl.nasa.gov/doc/nhats.html ; https://cneos.jpl.nasa.gov/nhats/obs.html
- JPL Horizons API: https://ssd.jpl.nasa.gov/api/horizons.api ; MPC observations API: https://data.minorplanetcenter.net/api/get-obs
- Goldstone outage: https://www.nasa.gov/directorates/somd/space-communications-navigation-program/nasa-concludes-antenna-mishap-investigation-releases-report/
- Galache et al. 2015: https://arxiv.org/abs/1504.00712
- NEOfixer: https://neofixer.arizona.edu/faq/how-does-neofixer-assign-priority
- ESA NEOCC system updates: https://neo.ssa.esa.int/system-updates
- MANOS: https://arxiv.org/abs/2603.15872 ; https://manos.lowell.edu/overview/goals ; https://arxiv.org/abs/1607.03517
- LCO: https://arxiv.org/abs/2102.10144 ; https://meetingorganizer.copernicus.org/EPSC-DPS2025/EPSC-DPS2025-997.html ; https://lco.global/observatory/proposal/process/
- TTT survey: https://arxiv.org/abs/2602.18562 ; Seimei: https://arxiv.org/abs/2606.17047
- NEOROCKS: https://academic.oup.com/mnras/article/520/2/3143/7017844
- IAWN campaigns: https://iawn.net/obscamp/ ; https://iawn.net/obscamp/2023DZ2/
- Mission-target lightcurves: https://ntrs.nasa.gov/citations/20260004003 ; Karman+: https://meetingorganizer.copernicus.org/EPSC-DPS2025/EPSC-DPS2025-1407.html
- Radar capabilities: https://arxiv.org/abs/1604.01080
- Rubin: https://www.rubin.community/t/rubin-solar-system-february-2026-updates/11640 ; https://www.rubin.community/t/rubin-status-november-17-2026/12959 ; https://www.rubin.community/t/rubin-observatory-status/12397 ; https://survey-strategy.lsst.io/progress
- Routes: https://www.itelescope.net/telescope-rates-premium ; https://support.itelescope.net/support/solutions/articles/222670-how-much-does-each-telescope-cost-to-use- ; https://www.slooh.com/pricing ; https://www.not.iac.es/observing/service/ ; https://birtwhistle.org.uk/Results.htm ; https://science.unistellar.com/planetary-defense/missions/ ; https://claudestronomy.com
