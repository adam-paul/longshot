# Upstream sources for physical measurements: where they appear, how fast, and what signal each gives

Researcher brief: architecture review, upstream physical data. All checks ran on 2026-11-24 (local; 2026-11-25 01:15 to 01:40 UTC). Status: **complete**, except where section 12 says otherwise.

Tags: **[T]** read or tested today, with the URL in the row or in Sources. **[L]** computed today from the local JPL snapshots (`data/snapshots/2026-11-21`, `2026-11-24`) or from files in `data/research-data-2026-11-21.tar.zst`. **[P]** taken from the project's earlier research files, named. **[S]** a search-engine summary, page not opened. **[R]** recalled, not checked.

No request went to `ssd-api.jpl.nasa.gov`. No personal or project detail was sent anywhere. Section 13 lists the requests made. The scripts (`scripts/local_facts.py`, `scripts/pravec.py`, `scripts/pravec2.py`) are kept in `data/backbone-review-2026-11-24.tar.zst`; Pravec's table as read is `data/sources/pravec/newres-2026-11-24.txt`.

Terms used below: a *lightcurve* is brightness measured through a night, and its repeat time is the rotation period. *U* is the lightcurve community's quality grade for a period (3 secure, 2 probably right, 1 unreliable). A *card* is SsODNet's one-object summary of what the literature holds.

## 0. Bottom line

1. **No upstream publishes a change feed for physical measurements.** What exists is weaker: file dates on about ten static files, a build stamp inside each SsODNet card, an export date on each row of one observer's table, and the daily arXiv listing. Everything else is "pull again and compare".
2. **A physical measurement becomes public in the observer's own table or paper first, reaches SsODNet months later in irregular batches, and mostly never reaches JPL's database.** Examples measured today are in section 1.
3. **SsODNet has not been rebuilt for 71 days.** Every card fetched on 20, 21 and 24 November is stamped 2026-09-14; its bulk files are dated 2026-09-22; its name index knew none of the three later designations I tried. Its 2023 paper says the name index is updated weekly and plans monthly updates for the rest. At least 144 of the 7,231 reachable asteroids were first observed after its stamp, so it cannot know them. It has no change list, no version endpoint and no archive of earlier builds.
4. **One live table the project does not use changes its counts today.** Petr Pravec's Ondrejov results file holds rotation periods for 35 reachable asteroids that the project's 21 November union of JPL, the lightcurve database and 1,704 SsODNet cards does not hold. For 20 of them a SsODNet card confirms there is no spin; for 15 no card was ever fetched. Seven are under 6 km/s and four under 5 km/s, all seven confirmed today. One of them, 2023 RA4 (4.96 km/s), has a period of 2.35 hours at grade U 2, which would end the plan's statement that every measured period under 5 km/s is faster than 2.2 hours.
5. **The literature moves faster than any catalog, and a keyword search misses it.** Today's arXiv listing carries a paper giving colours, an area-to-mass ratio and size and density cases for 2026 QQ8. It is one of the ten fixture objects and has the lowest delta-v of all 7,231 on the list (3.35 km/s). Its abstract contains none of "near-Earth", "NEA" or "NEO". SsODNet does not know the object exists. Only a match on designations finds it.
6. **Sources fail in ways that look like answers.** Strasbourg's data centre (VizieR) has been degraded by what it calls a cybersecurity incident since at least 18 November. Its Harvard mirror returned HTTP 200 with an error message as the body. SsODNet returns 404 for an object it has never heard of. Each of these must become "not checked", and only a check of the body can tell.
7. **So the site can be current about orbits and tracking, and can only be dated about everything physical.** Section 9 classifies every input; section 10 says what each part of the site may claim.

## 1. What arrives, how fast: measured today

### 1.1 Arrival rates

| Channel | Rate seen | Evidence |
|---|---|---|
| JPL's physical fields (diameter, albedo, rotation period, class, colours, mass, density) | 0 changes in 3.4 days across 43,379 near-Earth objects | [L], and the brief's own diff |
| SsODNet | No rebuild between 2026-09-14 and 2026-11-24 | [T] section 2 |
| SsODNet's reference list | 4,321 distinct references; by publication year 2023: 78, 2024: 79, 2025: 195, 2026: 19 (to 14 September, 16 of the 19 about comets or centaurs) | [T] `ssodnet_biblio.json` |
| Pravec's Ondrejov table | 2,529 result rows; by year of last lightcurve 2023: 87, 2024: 92, 2025: 115, 2026: 57 (to 15 October). Reachable asteroids new to the project's union: 2023: 6, 2024: 10, 2025: 8, 2026: 10 | [T] `newres.txt`; [L] |
| TTT fast-rotator survey | 161 periods from 249 objects observed since late 2023, published once, in February 2026 | [T] arXiv:2602.18562 |
| Las Cumbres small-asteroid colour programme | A 10-object pilot in a 2025 conference abstract. No 2026 result found. Its portal lists targets, and every lightcurve row read says "No Analysis Done" | [P] `verify-obs-window.md`; [T] search and portal |
| Minor Planet Bulletin | Four issues a year, about the 21st of March, June, September and December. Issue 53-4 is 76 pages | [T] mpbulletin.org |
| arXiv, planetary science | 28 items in today's listing (14 new). About 7 a month match "near-Earth", "NEA" or "NEO" in the abstract (100 newest hits span October 2025 to November 2026), and about a third of those are off topic | [T] |
| MITHNEOS spectra | Six observing runs posted between September 2025 and May 2026; pages last changed 19 to 20 August 2026 | [T] smass.mit.edu |
| NEOWISE sizes | No new fit paper since 2021 | [P] `verify-coverage.md` |
| Radar | JPL's list of radar-detected objects says "Updated: 2025 June 2". One object (2026 TS) gained radar data in JPL's orbit table in the 3.4 days | [T], [L] |

### 1.2 How long one measurement takes to reach each place

| Object | What was measured, when | First public, machine-readable | In SsODNet (build of 14 Sep 2026) | In JPL's database (24 Nov 2026) |
|---|---|---|---|---|
| 2026 QQ8 (3.35 km/s, the lowest on the list; fixture) | Colours, area-to-mass ratio, size and density cases; observed 7 to 21 November 2026 | arXiv:2611.31213, submitted 23 November, listed 24 November: two days | Object unknown (404) | No physical field |
| 1999 AO10 (5.89 km/s) | Period 11.06 h, U 3, and a V−R colour; observed 12 to 13 February 2026 | Pravec's table, exported 23 March 2026: five weeks | No spin | No period |
| 2023 RA4 (4.96 km/s) | Period 2.3478 h, U 2; observed 15 to 18 October 2023 | Pravec's table, exported 14 November 2023 | No spin, three years on | No period |
| 2025 QP3 (5.66 km/s) | Period 2.219 h; two groups | Pravec's table, 25 September 2025; then arXiv 20 February 2026 (TTT) | Yes, from the TTT paper, with grade "U=3" | No period |
| TTT survey, 161 periods | Observed late 2023 to 2025 | arXiv 20 February 2026; journal 17 March 2026 | Yes, within six months of the journal date | Not seen (2025 QP3 has none) |
| 2026 TS (not on the list) | Period 75.8 s, observed and exported 15 October 2026; radar Doppler by 18 October | Pravec's table the same day | Not tested; designated after the index date | Radar entered the orbit between 21 and 24 November; no period |

The TTT paper's data statement reads: "The derived rotational parameters and the calibrated photometric measurements for all objects presented in this work will be made available to the community through the LCDB." The public LCDB has not changed since 1 October 2023 (section 3.1). The declared deposit route for the largest recent set of small-asteroid periods is therefore closed to the public, and SsODNet took the paper directly.

## 2. SsODNet

Operated by LTE at Paris Observatory (formerly IMCCE). The acknowledgement text and the contact address both say LTE [T].

### 2.1 Entry points and the signal each gives

| Entry point | URL | Signal for change | Seen today |
|---|---|---|---|
| Card, one object | `https://ssp.imcce.fr/webservices/ssodnet/api/ssocard/<id>` | Body fields `ssocard.version` (data model) and `ssocard.datetime` (build time). No `ETag` or `Last-Modified` header | 13 cards returned 200, all `1.2.4` and `2026-09-14T23:00:01+00:00`, including objects first observed in July, August and early September 2026. About 1.2 to 1.5 s each |
| Card, unknown object | same | HTTP 404 with `{"name": "...", "error": "No SSO named '...' found in SsODNet.quaero index"}` | 2026 QQ8, 2026 SA8, 2026 TA6, 2026 VQ5 |
| Card, batch | POST a text file of names to `ssocard.php?q=` (documented) | as above | Not tested |
| Name index | `https://api.ssodnet.imcce.fr/quaero/1/sso?q=...` | Each record has `"updated"` | 2026 RC: `"updated":"2026-09-14"`. 2026 TA6: `{"total":0,"data":[]}` |
| Name index, bulk | `https://asterm.imcce.fr/public/ssodnet/sso_index.csv.gz` (found in the `rocks` source) | `Last-Modified`, `ETag` | 36,937,766 bytes, 22 Sep 2026 09:39 GMT |
| Bulk table, all asteroids | `https://ssp.imcce.fr/data/ssoBFT-latest_Asteroid.parquet` | `Last-Modified`, `ETag` | 855,759,463 bytes, 22 Sep 2026 12:47 GMT |
| Same, text | `.../ssoBFT-latest_Asteroid.ecsv.bz2` | same | 568,176,143 bytes, same date |
| Reference list | `https://ssp.imcce.fr/data/ssodnet_biblio.json` | `Last-Modified`, `ETag`, and a `datetime` field inside | 4,475,450 bytes, 22 Sep 2026; inside: `2026-09-14 08:30:01` |
| Field dictionary | `https://ssp.imcce.fr/data/metadata_asteroid.json` | `Last-Modified`, `ETag` | 15 Oct 2026 |
| Per-property history | `.../api/datacloud.php?-name=id:<id>&-resource=spins&-mime=json` | None; entries carry no date | 2025 QP3: one spin entry with `period_flag: "U=3"` |
| Status | `.../api/getAvailability.php?-mime=json` | None useful | `"availability":"Dev. in progress"`, contact vossp.lte@obspm.fr |
| All cards in one archive | `.../api/ssocard/ssoCard-latest_Asteroid.tar.bz2` (named in the `rocks` source) | n/a | 404 |

All [T]. The documentation pages for the service, the card and the bulk table state no update schedule, no changelog, no rate limit and no licence.

### 2.2 How often it is rebuilt

- Stated: "The name resolver quaero is updated weekly to follow SSO discoveries. We plan on monthly updates for the others applications" (Berthier et al. 2023, conclusions) [T]. The `rocks` documentation says "new observations are ingested on a weekly basis" and advises running `rocks status` "regularly (e.g. once a month)" [T].
- Observed: nothing newer than 14 to 22 September 2026 at any entry point, on 20 and 21 November [P] and again today [T]. That is 71 days for the cards and 63 for the bulk files.
- No page explains the gap. I did not find a notice of a pause.

### 2.3 How new objects appear

Through the weekly name index, when it runs. Today the index stops in mid-September: 2026 RC (first observed 2 September) is known, 2026 SA8 (second half of September) is not. 2026 QQ8 was first observed on 19 August and is still unknown, so the cut-off follows the date a designation was issued, not the date of first observation. From the local snapshot, 144 reachable asteroids were first observed after 14 September 2026 [L]; that is a floor on the number SsODNet cannot answer for today.

A new object's card holds only an orbit and H. 2026 NM, 2026 PC, 2026 QT and 2026 RC each returned 4.9 kB with `absolute_magnitude` as the only physical entry [T].

### 2.4 Change list, version endpoint

Neither exists [T, by reading the three documentation pages and the `rocks` client source]. The client has no freshness logic: `rocks status` counts the cached files and offers to download them again.

Two substitutes:

- **The file dates.** One HEAD request each on the bulk table, the reference list and the name index says whether a rebuild has happened. Three requests a day cost nothing.
- **The reference list as a change list by proxy.** `ssodnet_biblio.json` lists every paper SsODNet has ingested, by dataset, with bibcodes. Comparing two copies gives the papers added by a rebuild. It does not say which objects changed.

After a rebuild, the choices are to fetch every card again (about 7,100 requests; about two hours at one a second, [P] and consistent with today's timings) or to read the bulk table. The bulk table accepts range requests (`206`, `Accept-Ranges: bytes`), so a client can read the 329 kB footer and then only the columns it needs, and an interrupted download can resume [T]. Speeds today were 18 to 147 kB/s (65 kB tail, 3 MB head, the 4.5 MB reference list at 74 kB/s), so the whole file would take roughly 1.6 to 3 hours. On 20 and 21 November it ran at 0.6 to 9 kB/s and dropped [P].

### 2.5 What it had ingested by 14 September 2026

From the reference list [T]:

- Spin: 3,303 references. By year 2022: 43, 2023: 35, 2024: 30, 2025: 153, 2026: 5. Of the 153 dated 2025, 91 are Minor Planet Bulletin papers and 30 are telegrams (CBET). So SsODNet reads the Bulletin itself and does not depend on the frozen lightcurve database.
- It reads the Bulletin in batches, with a hole. Bulletin references in the spin list by year: 2019: 130, 2020: 83, 2021: 49, 2022: 0, 2023: 0, 2024: 1, 2025: 91, 2026: 0. The public LCDB covers the Bulletin to about mid-2023. So periods published in the Bulletin from late 2023 through 2024, and all of 2026 so far, are probably in no aggregator. That is an inference from the reference counts; I did not test an object.
- Taxonomy: 344 references, none dated 2026. Colours: 194, with 12 dated 2026, all comets or a centaur.
- In: Alarcon+2026 (TTT), Sanchez+2024, Masiero+2021, Trilling+2010 and 2016. Navarro-Meza+2024 (RATIR) is listed under taxonomy, though `catalogs.md` found its colours absent from the cards.
- Not in: Moskovitz+2026 (MANOS colours for 189 objects, arXiv March 2026), Ngwane+2026 (PSJ 7, 5), López-Oquendo+2026 (arXiv late August 2026). These are the three small-asteroid surveys the plan holds back as confirmatory labels.
- No reference to Pravec's web table. The seven objects in section 3.2 have no spin in their cards.

### 2.6 Terms

No licence. An acknowledgement sentence and a citation of Berthier et al. 2023 are requested, plus the original papers [T]. The card endpoint sends `Access-Control-Allow-Origin: *` [T], so a browser could call it directly; the plan's rule that the app serves its own snapshot still stands, because the service is slow, unversioned and currently stale.

## 3. Lightcurves and rotation periods

### 3.1 Sources

| Source | State today | Access and signal | Terms | Evidence |
|---|---|---|---|---|
| LCDB (Warner, Harris, Pravec) | Frozen. "The latest release is dated 2023 October 1." No future release announced | `https://minplanobs.org/MPInfo/datazips/LCLIST_PUB_CURRENT.zip`: `Last-Modified: 01 Oct 2023`, `ETag`, 39,966,552 bytes. The page says to ping the file's timestamp and that "once a week is more than enough" | "Copyright (c) 2021 by Brian D. Warner. All rights reserved." | [T] |
| ALCDEF (raw photometry deposited by observers) | Live. 24,822 objects, 387,575 lightcurve blocks, 11,179,369 observations; "Last update: 2026-11-24 10:50:32" | Web forms only, no API. Per-object search by POST works from a script and returns the number of lightcurve blocks with first and last dates (Apophis: 42, 2005-01-08 to 2021-03-31; 2022 OB5: no match). Full archive `https://alcdef.org/docs/ALCDEF_ALL.zip`: 135,505,325 bytes, `Last-Modified: 28 Apr 2025`, 19 months behind the database. A form exports blocks "added or edited on/after" a date, limited to the last 90 days; my scripted POST returned HTTP 500 twice | "All rights reserved." Data policy: data are public; "the end-user agrees to use the data strictly for its intended purpose: to aid in scientific research", and not for "commercial gain, solicitation, advertising". No citation rule, nothing on automated access | [T] |
| Minor Planet Bulletin | Live, quarterly. Latest: 53-4 (October to December 2026), pages 219 to 294 | PDF per issue (`https://mpbulletin.org/issues/MPB_53-4.pdf`, 20,455,087 bytes, `Last-Modified: 08 Sep 2026`). No table of results. "All MPB papers are indexed in the ADS" | No licence stated for papers | [T] |
| Pravec, Ondrejov "prepublished" results | Live. File changed 15 October 2026; the group's index page changed 23 November | One fixed-width text file, `http://space.asu.cas.cz/~ppravec/newres.txt` (1,316,778 bytes), with `Last-Modified` and `ETag`. The format is documented at `newres.htm`. Each row carries period, error, amplitude, U, lightcurve dates, absolute magnitude, the analyst and a "Date of the export" | None stated. The page calls the results "prepublished" | [T] |
| TTT fast-rotator survey (IAC) | One paper so far: 249 objects, 161 periods | The paper's tables; the paper names LCDB as the data route. In SsODNet since the 14 September build | CC BY on arXiv | [T] |
| Las Cumbres colour programme (MuSCAT) | Aim: about 1,000 very small asteroids by end of 2027. Published: a 10-object pilot | Nothing machine-readable yet. The follow-up portal `https://neoexchange.lco.global/` shows 352 characterization targets and a lightcurve summary whose rows read "No Analysis Done" | n/a | [P], [T] |
| JPL database `rot_per` | One value, no grade, no date | In the bulk list already pulled | n/a | [P]; counts match LCDB closely (306 against 304 on the list), so it probably follows LCDB and is frozen with it. That is an inference |

### 3.2 Pravec's table against the project's holdings

Matched by number or designation against JPL's list of near-Earth objects [L]:

- 2,529 result rows; 1,063 rows concern 856 near-Earth objects; 127 reachable asteroids have a period in the table.
- 37 of the 127 have no period in JPL's database.
- 35 of the 127 have no period in the project's union of 21 November (`data/research/dl/coverage-exact/spin_periods.json`: JPL, LCDB and 1,704 SsODNet cards). 33 of them are graded U 2 or better. By delta-v: 4 under 5 km/s, 7 under 6, 12 under 7. 20 of the 35 turn slower than 2.2 hours.
- All 35 are missing from JPL and LCDB. For SsODNet, 20 are confirmed missing (7 cards fetched today, 13 held from 21 November) and 15 are "not checked", because the earlier research never fetched their cards. The appendix marks each.
- The union held 333 periods on the list, 44 under 6 km/s and 20 under 5 [P `verify-coverage.md`]. With this table: up to 368 on the list (353 if SsODNet turns out to hold all 15 unchecked ones), and 51 and 24 under 6 and 5 km/s, both confirmed.

The seven under 6 km/s, none of them in JPL, in LCDB or in a SsODNet card (five cards fetched today, two more above):

| Object | Delta-v (km/s) | H | Period | U | Observed | Exported |
|---|---|---|---|---|---|---|
| 2026 AC4 | 3.79 | 26.1 | 8.4 min | 1 | January 2026 | 27 Jan 2026 |
| 2023 SO11 | 4.06 | 26.7 | 2.5 min | 2 | October 2023 | 14 Nov 2023 |
| 2026 EL2 | 4.87 | 26.1 | 19.9 min | 3 | March 2026 | 26 Mar 2026 |
| 2023 RA4 | 4.96 | 24.7 | 2.35 h, amplitude 1.2 mag | 2 | October 2023 | 14 Nov 2023 |
| 2023 RO49 | 5.86 | 24.4 | 87 s | 2 | October 2023 | 14 Nov 2023 |
| 1999 AO10 | 5.89 | 24.3 | 11.06 h | 3 | February 2026 | 23 Mar 2026 |
| 2025 QV5 | 5.98 | 27.4 | 2.04 h | 3 | August 2025 | 9 Sep 2025 |

Effects on the plan:

- Section 1.2 says all 21 measured periods under 5 km/s are faster than 2.2 hours. 2023 RA4 is slower, by a little, at U 2. The sentence needs the object or a caveat.
- Section 1.4's table has "Spin measured" rows only for objects brighter than H 24. 1999 AO10 is H 24.3 with a secure 11-hour period under 6 km/s: just outside the cut, and exactly the kind of slow rotator the surface-work screen looks for.
- WP6 says "0–2 rotation periods a year arrive under 6 km/s". This one group delivered three in 2026 (one of them graded unreliable) and three in 2023.
- The table is unrefereed and has no stated terms. LCDB has cited such entries as web results [R]. Showing a value from it on a public page needs the group's permission, which the no-contact rule defers.

### 3.3 Where each programme's results first become machine-readable

- Pravec's group: its own text file, the day of the analysis to a few weeks later.
- TTT: the journal paper's tables. Not LCDB in practice.
- Amateur and small-observatory work: the Minor Planet Bulletin PDF each quarter, then an ADS record, then SsODNet in a batch about a year later. The raw photometry may be in ALCDEF sooner.
- Las Cumbres colours: not yet anywhere.
- Rubin: papers on preview data [P `new-surveys.md`], and the raw magnitudes through the Minor Planet Center (section 4).

ALCDEF gives a state the ledger does not have yet: "photometry exists, no period published". It is cheap to ask per object.

## 4. Photometry inside astrometry (Minor Planet Center records)

One request today for 2026 VQ5, a reachable asteroid added to the list between the two snapshots (first observed 5 November) [T]:

- 109 records. The latest was taken at 22:47 UTC on 24 November, under three hours before the request. This channel is live to the hour.
- 108 carry a magnitude, 88 an uncertainty (`rmsmag`), 53 a photometric catalog (`photcat`).
- Bands: `G` (unfiltered, tied to Gaia) for most stations; ATLAS orange 22; V or Vj 20; Pan-STARRS w 4; `Gr` 4; ZTF g 1 and r 1.
- Fields: `mag`, `band`, `rmsmag`, `photcat`, `photap`, `logsnr`, `exp`, `stn`, `obstime`, `obsid`, `trkid`, `trksub`, `ref`. No created or updated time on a record.
- The API takes one designation per request and has no "since" parameter [T docs]. The Center's FAQ sets 5 requests a second [P `verify-facts-venues.md`].

Rubin (station X05) reports real filters (u, g, r, i, z) with magnitudes to 0.001 and uncertainties [P, replicated 21 November]. About 0.5% of reachable asteroids had any X05 record [P]. Rubin's submissions are ad hoc, not daily [P], and the camera has been shut down since 15 November with no return date in the status post of 17 November, which has no later reply [T].

Is it a live channel for colours? For brightness, yes. For colours a page can show, no. What it lacks:

1. **Simultaneity.** Filters are taken minutes to days apart, on bodies that mostly turn in minutes with amplitudes up to a magnitude. The 2026 MANOS colour paper says colours "measured without accounting for lightcurve variations can significantly influence the results for individual objects" [T arXiv:2603.15872]; 151 of its 189 objects needed a lightcurve correction [P].
2. **A common system.** Most magnitudes are a by-product of position measurement: mixed bands, mixed reference catalogs, half without a stated catalog, a fifth without an uncertainty, no stated aperture.
3. **A change signal.** No record timestamps and no "since". The trigger has to come from JPL's list: `n_obs_used` or `last_obs` changed (216 near-Earth objects in 3.4 days, per the brief), then one request per changed object. `obsid` makes the merge exact.
4. **A class.** Turning multi-band magnitudes into a class probability is a model. It belongs in a method release, not in the unattended refresh.

What it can give automatically: per object, which bands exist, how many nights, the scatter, and whether Rubin has seen it. That is a "photometry exists" flag, like ALCDEF's.

## 5. Sizes and albedos

| Source | Nature | Signal | Evidence |
|---|---|---|---|
| NEOWISE, PDS bundle 2.0 | Static since 2019-03-11; covers the cryogenic phases and reactivation years 1 to 3. No newer version mentioned | None needed | [T] `sbn.psi.edu/pds/resource/neowisediam.html` |
| NEOWISE, later years | Three papers (2020, 2020, 2021), tables at the journal. No fit paper for years 8 to 11. Mission over; final image release 14 November 2024 | A new paper, found by the literature watch | [P] `verify-coverage.md` |
| Spitzer | Static: one CSV on GitHub, last push January 2020; the telescope ended in 2020 | GitHub `ETag` | [T], [P] |
| NEO Surveyor | Not launched. IPAC's page today: "launch date of no later than June 2028"; NASA and JPL pages on 21 November: no earlier than September 2027 [P]. IPAC "works with the IAU Minor Planet Center and NASA Planetary Data System" to release detections and physical characterizations. A 2024 talk gives images and source lists every six months through IRSA and tracklets yearly [S]. No public schedule for a diameter product | A dated watch item, nothing to build | [T] `ipac.caltech.edu/project/neo-surveyor` |
| Radar | JPL's list: 1,310 objects, 1,149 near-Earth asteroids, "Updated: 2025 June 2" (file changed 23 January 2026). The Goldstone schedule page changed last on 7 October 2025. Sizes, spin bounds and polarization ratios are published only in papers | The counts `n_del_obs_used` and `n_dop_obs_used` in JPL's bulk list say radar data exist: 232 reachable asteroids today, one object changed in 3.4 days | [T], [L] |
| JPL database diameter and albedo | Not updated from NEOWISE since 2019 | n/a | [P] |
| SsODNet | Carries NEOWISE through 2021 and part of Spitzer; "best" albedo is usually computed from diameter and H | Section 2 | [P], [T] |

Sizes are the slowest channel. Between now and NEO Surveyor's first products, new sizes for small reachable asteroids come from single-object papers (radar, JWST, thermal modelling), a few a year. Today's 2026 QQ8 paper is one.

## 6. Taxonomy and spectra

**VizieR.** Not testable today [T]:

- `https://cds.unistra.fr/`, "Last updated November 18, 2026": "CDS is experiencing a cybersecurity incident within its network of servers located in Strasbourg." It lists the portal, table upload, cross-match and "the VizieR publishing registry" as unavailable and points to mirrors (IDIA, CfA Harvard, NAOJ, China-VO), noting that large catalogs are not on all mirrors.
- TAP at `tapvizier.cds.unistra.fr` timed out twice at 60 s. `cdsarc.cds.unistra.fr` and `vizier.cds.unistra.fr` returned a "Page unavailable" page with status 404.
- The Harvard mirror answered a table request with HTTP 200 and the body "The database is not currently reachable ... Postgres connect error". The NAOJ mirror did not connect. The Harvard host has no TAP service at the usual path.
- So I could not test TAP metadata or how to detect a new table. From memory [R]: the TAP schema lists tables without an insertion date; CDS publishes a list of catalogs added in the last 30 days (`cats30.htx`; a cached copy seen by the search engine was dated 13 June 2026 [S]); each catalog's ReadMe ends with dated history lines. Check this when CDS is back.

A VizieR table is one paper's table, static once published. The project does not need to watch VizieR. It needs to learn that a paper exists (section 7) and then fetch its table once, from CDS or from the journal. Not every paper deposits: the MANOS colour paper names no archive, and the NEOWISE 2020 to 2021 tables are at the journal only [P].

**MITHNEOS** (`http://smass.mit.edu/minus.html`, HTTP only) [T]. Live: "All spectroscopic observations obtained in this joint campaign are being made publicly available in near-real time via this website." Latest run sp344, 8 May 2026; page "Last modified 2026 May 28"; the observing-circumstances spreadsheet and the change log say "Last updated 19 Aug 2026"; all three files have `Last-Modified: 20 Aug 2026`. "Spectra presented here are considered to be in the public domain and may be freely used for any purpose." It posts spectra, not classes. Classifying them (for instance with `classy`) is a model step.

**MANOS** [P, T]. The site states no licence and has a login. Results arrive as papers.

**Gaia DR4.** Release 2 December 2026, 12:00 CET; the archive closes from 25 November 12:00 CET [P]. The DR4 page ("Last update: 14 September 2026") lists `sso_source` and `sso_reflectance_spectrum` at 436,551 rows each, `sso_observation` at 60,542,356 rows, and one new table, `sso_xp_epoch_spectrum` (8,656,146 records, through DataLink) [T]. Access is by TAP at `gea.esac.esa.int`. For this project it is one query on 2 December for how many reachable asteroids appear (8 in DR3 [P]), and then a static source until DR5, not before the end of 2030 [P]. The licence is non-commercial [P]; the plan's first release uses no Gaia data.

## 7. The literature as the trigger

### 7.1 arXiv

- **Listing feed.** `https://rss.arxiv.org/rss/astro-ph.EP`, one request, 123 kB, with an `ETag`; no listing on Saturday or Sunday. Today: 28 items, of which 14 new, 6 cross-listed, 8 replacements [T].
- **API.** `https://export.arxiv.org/api/query` searches titles, abstracts, authors and comments, not full text. One request returned the 100 newest of 915 matches in 4 s [T].
- **Terms.** "make no more than one request every three seconds, and limit requests to a single connection at a time." Metadata are CC0. E-prints may be stored "for your own personal use, or for research purposes" and may not be served from your own servers [T].
- **Full text.** Recent papers have an HTML version (`arxiv.org/html/<id>`), which a script can search for designations (done today for three papers).

### 7.2 NASA ADS

- **Key.** Needed. It is a token generated from a free account's settings page and sent as `Authorization: Bearer <token>` [T]. I have no key, so nothing below was tested.
- **Limit.** 5,000 queries a day per endpoint, reported in response headers [T].
- **Fields.** `body` ("extracted fulltext minus acknowledgements section", searchable, not retrievable), `entdate` (when ADS created the record), `fulltext_mtime`, `bibstem` (journal), `data` (linked archives) [T].
- **Terms.** "Users may not perform systematic downloads of articles, abstracts, or tables of contents for any purpose". For the API: "You won't try to create a partial or full copy of the data", "You also shouldn't redistribute any data you obtain from our services to third-parties", and "If you need to download and store ADS data returned by the API on a regular basis, you should contact us first." [T]. So ADS can tell the project that a paper exists. The site stores the bibcode and DOI and links out; it does not republish ADS abstracts.
- ADS covers what arXiv does not: the Minor Planet Bulletin, telegrams, and journal papers never posted to arXiv.

### 7.3 Is a keyed weekly search workable?

Yes, and the load is small. Three things decide whether it works:

1. **Match designations, not topics.** Today's 2026 QQ8 paper would be missed by "near-Earth" and found by its designation.
2. **Normalise how designations are typeset.** Titles today read "2026 QQ$_8$", "2022 OB$_5$" and "2001 WN$_{...}$". A plain pattern reads these as "2026 QQ" and "2022 OB" (my first pass did). 5,730 of the 7,231 reachable asteroids have a designation ending in digits and can be typeset this way [L]. The 200 numbered ones appear as a number, a name, or both, with variant spellings (Kamoʻoalewa). The alias table in the plan's Appendix B is the right tool; it needs a text-normalising step in front of it.
3. **Read the body, not only the abstract.** Survey papers name their objects in tables.

A workable shape (proposed):

- Daily: one request for the planetary-science listing. Match titles and abstracts against the alias table. For matches, and for papers passing a loose topic filter, fetch the HTML full text three seconds apart and match again in the body.
- Weekly, with an ADS key: query by `entdate` for the Bulletin, the telegrams and the main journals; optionally one `body:"<designation>"` query for each of the 726 objects under 6 km/s, which fits inside one day's limit.
- Quarterly: the Bulletin issue itself, about the 21st of March, June, September and December.
- Output: a queue. Each entry is a paper, an object, the matched passage, and a proposed property and value with the sentence it came from. An agent drafts the entry. A person accepts or rejects it. Nothing enters the ledger from this path without that step, because reading a value out of prose is the part most likely to be wrong.

Expected load, from today's samples: one to three papers a week to look at, most weeks none or one touching a reachable asteroid, plus a quarterly Bulletin pass. The estimate rests on about 7 keyword matches a month and one designation hit in today's 14 new papers; a month of running would replace it with a count.

SsODNet's reference list closes the loop: when a queued paper later appears in `ssodnet_biblio.json`, the hand-entered value can be compared with SsODNet's.

## 8. Prices and capability facts

### 8.1 Platinum-group metal prices

| Source | Metals, cadence | Machine-readable | May the site use it? | Evidence |
|---|---|---|---|---|
| USGS Mineral Commodity Summaries data release | All five the model uses (Pt, Pd, Rh, Ir, Ru [P `verify-value-inputs.md`]), yearly averages; 2026 edition, DOI 10.5066/P1WKQ63T, release date shown as September 18, 2026 | "separate table files (entities) in CSV format" | Yes: "This work is marked with CC0 1.0 Universal." | [T] |
| World Bank commodity prices ("Pink Sheet") | Platinum only among these; monthly, through October 2026; "Updated on November 03, 2026"; "Next update: December 2, 2026" | XLSX at a URL that contains a per-edition identifier; `Last-Modified: 03 Nov 2026` | Probably. The page links the Bank's dataset terms and its CC BY licence page; I did not find the licence sentence itself | [T] |
| IMF primary commodity prices | Platinum and palladium, monthly; an API is listed | Yes | Terms not read | [S] |
| LBMA platinum and palladium prices | Daily. Administered by ICE Benchmark Administration since 1 July 2026 | Through licensed vendors | A licence from the administrator is required "to obtain, use or redistribute" the data | [S] LPPM and ICE notices |
| Johnson Matthey base prices | Daily, all five | A page; its table failed to load on 20 November [P] | No: "Any use of the Prices without the prior consent of Johnson Matthey Plc is prohibited." | [T] |
| Umicore | Daily; the source of the 20 November figures | A page | Terms not read | [P] |

So one licensable, machine-readable source covers all five metals, and it is yearly. Daily prices for rhodium, iridium and ruthenium exist only on dealer pages whose owners forbid reuse or have not been asked.

A proposal that fits: every dollar figure names its price scenario and date. The default scenario is the latest USGS yearly average, refreshed once a year. A second, dated scenario may be a dealer snapshot entered by hand with written permission. `DESIGN.md` section 7 already says each figure moves by a factor of 1.8 between 2025 averages and 20 November 2026 prices, and by a factor of four per magnitude of brightness, so a monthly or daily price feed would add precision the estimate does not have.

### 8.2 "What has been brought back" and other capability facts

These change a few times a decade and have no machine source. Proposed handling:

- One facts file under version control. Each fact has: the sentence shown; the source URL; the quoted passage; `as_of` (the date the fact was true at source); `last_checked`; and `recheck_by`, set from a known event where there is one (Tianwen-2's capsule is due late November 2027 on secondary sources [P]; Hayabusa2's flyby of 2015 BM510 is April 2028 [P]).
- A monthly scheduled check in which an agent reruns a fixed list of searches (missions in flight, the companies named on the site) and proposes edits. A person approves each change. If nothing changed, only `last_checked` moves.
- A tripwire to bring a check forward: the last-edit time of the relevant Wikipedia articles, from one request to the public MediaWiki API. Today: Hayabusa2 edited 20 November 2026 ("Replaced the flyby to 2015 BM510"), Tianwen-2 on 1 November, AstroForge on 7 November [T]. Wikipedia is the trigger for a look, never the source shown.
- The page prints the date in the sentence, as the plan already proposes ("As of 21 November 2026, three spacecraft have...").

## 9. Classification of every input

Three classes. **A**: refreshed automatically, with a machine signal. **B**: a scheduled check whose result a person or an agent reviews before the ledger changes. **C**: curated by hand, shown with a "last checked" date.

| Input the site shows | Source | Class | How often, by what signal |
|---|---|---|---|
| Which asteroids are reachable; delta-v; trip length; next observing window and its brightness; radar outlook | JPL's reachable list, one request | A | Daily. No `ETag` or `Last-Modified`, so compare content with the previous pull; `orbit_id` per object. About 220 objects changed in 3.4 days, nearly all in the window fields |
| Orbit quality code, days tracked, observation counts, first and last observation, H, the fitted sunlight-push values and their errors | JPL's table of all near-Earth objects, one request | A | Daily. Signals per object: `orbit_id`, `last_obs`, `n_obs_used`. The bulk list rounds the push values and drops the force law [P], so a changed value needs one per-object request (4 objects in 3.4 days) |
| Radar data exist | Same table, `n_del_obs_used` and `n_dop_obs_used` | A | With the daily pull |
| Raw positions and magnitudes; which bands; whether Rubin has seen it | Minor Planet Center, one request per object | A | On trigger: only objects whose JPL counts changed (about 7 a day on the list). No signal of its own |
| "Photometry exists, no period published" | ALCDEF per-object search | A, after a terms check | Weekly, for objects observed in the last few months. The research-only terms need a decision first |
| Size, albedo, class, colours, spin with grade, density, thermal inertia, radar polarization, drift, as the literature has them | SsODNet | A for detection, lagging at source | Daily: three HEAD requests and one card. On a change: re-pull, and diff the reference list. The value shown carries SsODNet's build date, not the fetch date |
| Whether SsODNet knows the object at all | SsODNet 404 against its name-index date | A | Derived: an object designated after the index date is "not checked" for every SsODNet row |
| Rotation periods not in SsODNet | Pravec's table | A for detection, B for entry | Daily HEAD (`Last-Modified`, `ETag`); new rows by export date. Rows have free-text remarks (lower limits, split grades), so a new row is reviewed once. Public display waits for permission |
| Rotation periods and colours from amateurs | Minor Planet Bulletin | B | Quarterly, about the 21st of March, June, September, December |
| LCDB | One ZIP | A | Weekly HEAD. Unchanged since 1 October 2023; one day it may change |
| New sizes, classes, spins, densities in papers | arXiv listing; ADS with a key | B | Daily listing matched on designations; weekly ADS; an agent drafts, a person accepts (section 7.3) |
| NEOWISE and Spitzer sizes; the VizieR tables already used (Mahlke, Sergeyev, MANOS, MITHNEOS 2022, RATIR) | Paper tables | C, one-time | Ingest once, pinned by hash. A new table arrives only through the literature watch. Keep local copies: CDS is down today |
| MITHNEOS spectra | smass.mit.edu | B | Monthly HEAD on three files. New spectra need classifying, which is a method step |
| Gaia DR4 | ESA archive TAP | C, one-time | One query after 2 December 2026. Non-commercial class |
| NEO Surveyor; Rubin data releases; the Las Cumbres colour programme | Mission and programme pages | C | A dated watch item each, rechecked quarterly |
| Metal prices | USGS data release | B, close to A | Yearly: a new edition has a new DOI, so a person points the pipeline at it |
| Metal prices, dated dealer snapshot | Dealer page | C | By hand, with permission, labelled with its date |
| What has been brought back; missions under way; company status; launch prices | Agency and company pages | C | Monthly agent check, person approves; `as_of` and `last_checked` on each fact |
| Mission-type thresholds; the priors; the known-answer set | The project's own method release | C | Versioned with the method, changed only by a numbered release |
| The record of predictions | Internal, resolved by the rows above | B | A resolving observation arrives through SsODNet's diff or the literature queue; a person confirms the resolution |

## 10. What the site can honestly claim

**Current, to the day, without a person:**

- Which asteroids are on the list, their delta-v, and when each can next be observed.
- How well each is tracked: days observed, number of observations, orbit quality, JPL's fitted sunlight-push values.
- That raw photometry or radar data exist for an object.

The honest label is "JPL solution N, fetched today". If the daily pull fails, the label must age by itself: the page shows the date of the last successful pull, not today's date.

**Dated at source, checked daily, but not current:**

- Every measured size, albedo, class, colour, spin and density that comes through SsODNet. The label is "SsODNet build of 14 September 2026; checked 24 November 2026". Two dates, because the first can be ten weeks older than the second.
- Periods from Pravec's table: "exported 23 March 2026".

**Only "last checked":**

- Every "not measured" on the site. It is a statement about sources, and it is only as good as the oldest source behind it. The honest form is "no measurement in SsODNet (build of 14 September 2026), JPL (today) or the literature queue (last run 23 November 2026)". For an object designated after SsODNet's build, the SsODNet part is "not checked", and if the literature queue has not run since the object was designated, the whole row is "not checked".
- Prices: "USGS average for 2025".
- Capability facts: "as of 21 November 2026; last checked ...".

**Never claimable:** that a measurement does not exist. 1999 AO10's 11-hour period existed in public for eight months while JPL and SsODNet both said nothing. The ledger's four states already allow for this; what is missing is the date that scopes each "not measured".

Two consequences for the data model, both proposals:

1. **Each ledger cell carries two dates and a source edition**: the upstream's own build or edition date, and the time of the project's last successful check. `plan.md` Appendix B has "show each source's date on every page"; this makes it per cell and makes "not measured" depend on it.
2. **"Not measured" is computed, not stored.** It is true for (object, property) only when every source for that property was checked successfully, each source's edition is later than the object's designation date, and none returned a value. Otherwise the cell is "not checked". Today that rule would turn the SsODNet-backed rows of at least 144 objects from "not measured" to "not checked", which is the correct reading.

## 11. What this means for the first step (proposed, within this brief)

None of this depends on the app's stack, language or host, and none of it chooses one.

1. **Build the source registry before any adapter.** One declarative list of sources. For each: the URLs; the change signal (header, body field, or content comparison); the expected cadence; the age at which it counts as stale; its licence class; the time of the last successful check; the edition last seen. The freshness labels in section 10 are read straight from it. It is small, and it is the piece that turns a snapshot into something maintained.
2. **Run change detection alone for two weeks before fixing the schema.** Daily: the two JPL requests, the HEAD requests of sections 2, 3 and 6 (about ten), and the arXiv listing. Keep every response. The JPL part needs the contact address that is still an open decision (`DESIGN.md` section 10); until it is set, the JPL pulls stay manual and the rest can run. One daily pull of the two JPL lists is 18.4 MB raw and 2.6 to 3.6 MB compressed with zstd [L], so a year of daily copies is about 1 to 1.3 GB. This replaces the 3.4-day sample with real rates, and it would catch SsODNet's next rebuild and show what one changes.
3. **Check bodies, not status codes.** Each adapter decides "answered", "does not know this object" or "failed" from the content. Today's cases: HTTP 200 with a database error (Harvard VizieR mirror), HTTP 404 with a maintenance page (CDS), HTTP 404 with a JSON "not in index" (SsODNet), HTTP 500 (ALCDEF export).
4. **Add Pravec's table to the ledger's inputs** for the offline prototype, in a "cite and show single values, permission pending" class, and rerun the spin counts.
5. **Add 2026 QQ8's new paper and 1999 AO10 to the fixture slice.** They are the two live cases of "public, and in no catalog".
6. **Keep the unattended loop free of models**, as `plan.md` section 4 says. Colours from mixed photometry, classes from MITHNEOS spectra and values read out of papers all go through a review or a method release.

What the choice of where the refresh runs depends on (not decided here): it needs outbound HTTPS, a scheduler, a few megabytes a day of durable storage, and somewhere a person sees the review queue. A machine that reboots or is upgraded will miss runs (this workstation clears its temporary folder on reboot [P `AGENTS.md`]); the registry's last-success times make a missed run visible wherever it runs.

## 12. Not verified, and limits

- ADS: no key, so no query was run. Field names and limits are from its documentation. Whether `body:"2011 AA37"` matches the way designations are typeset in full text is untested.
- VizieR TAP and its new-catalog listing: CDS is down. The description in section 6 is recalled.
- ALCDEF's "added on/after" export: HTTP 500 to a scripted POST, twice. It may work from a browser. I stopped after two tries.
- SsODNet's batch card upload and its bulk-table column layout were not tested. No full download was made.
- Why SsODNet has not rebuilt since September is unknown. I found no notice.
- That JPL's `rot_per` follows LCDB is an inference from near-equal counts.
- Pravec's table: matching is by number or designation against JPL's list; a few rows with unusual identifiers may be missed. I did not open the lightcurve plots. The U column and the remark sometimes differ slightly ("U = 2+ or 3-" beside a 3). Terms are unstated.
- The 35 "new to the union" objects were checked against the 21 November union file, which held 1,704 SsODNet cards, not all 7,231. Twenty have a card on file with no spin (7 fetched today, 13 from 21 November). The other 15 never had a card fetched, so SsODNet may hold a period for some of them; I did not fetch 15 more cards.
- World Bank and IMF licence sentences were not found on the pages read. The LBMA licence rule and the NEO Surveyor release cadence are from search summaries.
- I did not open the USGS CSV files. That they carry yearly prices for all five metals rests on the data-release page ("price" among the statistics) and on the PDF chapter read on 21 November.
- The Bulletin hole in section 2.5 is inferred from reference counts by year.
- Rubin's status is from the 17 November post; I found nothing later. The Rubin plan document (RTN-011) returned only its abstract to my fetch; its details are from `verify-facts-venues.md`.
- The weekly literature load is an estimate from one day's listing and one keyword query.
- Arrival rates in section 1.1 for the Las Cumbres programme and NEOWISE rest on the earlier research plus one search each.

## 13. Requests made

All single and sequential, one to three seconds apart, in runs of five or fewer.

- SsODNet hosts (`ssp.imcce.fr`, `api.ssodnet.imcce.fr`, `asterm.imcce.fr`): 17 card requests (Bennu; 2026 QQ8, SA8, TA6, VQ5, NM, PC, QT, RC; 1999 AO10; 2026 AC4, EL2; 2025 QP3, QV5; 2023 SO11, RA4, RO49), 2 name-index queries, 1 per-property query, 1 status query, 7 HEAD requests, the 4.5 MB reference list, and 2 range requests on the bulk table (65 kB and 3 MB).
- ALCDEF: 2 page loads, 2 export POSTs (both 500), 3 search POSTs, 1 HEAD. LCDB: 1 HEAD. Minor Planet Bulletin: 2 HEAD.
- Pravec: the results file, the index page, the format page.
- Minor Planet Center: 1 observation request (2026 VQ5).
- arXiv: 1 API query, 1 listing feed, 3 HTML papers, 1 PDF.
- CDS: 2 TAP attempts (timed out), 2 page requests (404). Harvard mirror: 2. NAOJ mirror: 1 (no connection).
- MIT (MITHNEOS): 1 page, 4 HEAD. JPL radar web pages (not the API): 2. World Bank: 1 file. Wikipedia API: 1. GitHub raw files: 8.
- Documentation and policy pages through the fetch tool: about 30.

## Appendix. The 35 reachable asteroids with a period in Pravec's table and none in the project's union

So the count can be redone without my working scripts. Input: `newres.txt` as fetched today (kept as `data/sources/pravec/newres-2026-11-24.txt`) (`Last-Modified: Thu, 15 Oct 2026 10:25:38 GMT`, 1,316,778 bytes, SHA-256 `9bfb83693d8cd36f7e2d8b0f8afae2dcc02600f0527884d083e8ef627b9c8da3`). Method: parse each result row by the documented fixed layout; map the identifier (number in brackets, or provisional designation) to JPL's primary designation through the 24 November near-Earth-object table; keep reachable-list members with a non-zero period; per object keep the row with the highest U, then the latest year; drop objects with any period in `data/research/dl/coverage-exact/spin_periods.json` of 21 November. Delta-v and H are from the 24 November reachable list. "Year" is the year of the last lightcurve in the row.

| Object | Delta-v (km/s) | H | Period | U | Year | SsODNet card |
|---|---|---|---|---|---|---|
| 2026 AC4 | 3.791 | 26.1 | 8.36 min | 1 | 2026 | no spin (fetched today) |
| 2023 SO11 | 4.058 | 26.7 | 2.54 min | 2 | 2023 | no spin (fetched today) |
| 2026 EL2 | 4.866 | 26.1 | 19.9 min | 3 | 2026 | no spin (fetched today) |
| 2023 RA4 | 4.956 | 24.7 | 2.35 h | 2 | 2023 | no spin (fetched today) |
| 2023 RO49 | 5.856 | 24.4 | 87 s | 2 | 2023 | no spin (fetched today) |
| 1999 AO10 | 5.885 | 24.3 | 11.1 h | 3 | 2026 | no spin (fetched today) |
| 2025 QV5 | 5.981 | 27.4 | 2.04 h | 3 | 2025 | no spin (fetched today) |
| 2025 VD24 | 6.139 | 21.8 | 4.27 min | 3 | 2026 | not checked |
| 2025 WN1 | 6.225 | 24.5 | 1.52 h | 2 | 2025 | not checked |
| 2023 RK44 | 6.245 | 23.7 | 5.77 h | 2 | 2023 | not checked |
| 2024 AP2 | 6.507 | 24.6 | 31.6 min | 2 | 2024 | not checked |
| 2024 WT | 6.864 | 27.2 | 76.2 s | 2 | 2024 | not checked |
| 2013 PA7 | 7.465 | 22.7 | 18 h | 2 | 2024 | not checked |
| 2022 DX4 | 7.619 | 24.8 | 1.1 h | 1 | 2022 | not checked |
| 2024 TX13 | 7.771 | 24.6 | 10.3 h | 3 | 2024 | no spin (card of 21 Nov) |
| 612227 | 7.786 | 20.2 | 4.89 h | 2 | 2025 | no spin (card of 21 Nov) |
| 2025 QV9 | 7.787 | 25.1 | 84 h | 2 | 2025 | no spin (card of 21 Nov) |
| 350523 | 8.035 | 21.2 | 32.7 h | 3 | 2025 | no spin (card of 21 Nov) |
| 2024 FP3 | 8.075 | 26.1 | 15.3 min | 3 | 2024 | not checked |
| 2020 KT4 | 8.429 | 23.2 | 99.1 s | 3 | 2023 | not checked |
| 2012 XF55 | 8.630 | 22.8 | 15.3 h | 2 | 2025 | not checked |
| 778852 | 8.702 | 20.5 | 5.44 h | 3 | 2024 | no spin (card of 21 Nov) |
| 2011 MW1 | 9.027 | 22.3 | 11.7 h | 3 | 2024 | no spin (card of 21 Nov) |
| 2015 MB54 | 9.252 | 24.0 | 7.14 min | 3 | 2024 | no spin (card of 21 Nov) |
| 2022 EZ6 | 9.546 | 23.5 | 4.68 h | 2 | 2026 | not checked |
| 2023 XJ2 | 9.740 | 24.3 | 79 h | 2 | 2023 | no spin (card of 21 Nov) |
| 2017 SL14 | 10.109 | 23.1 | 109 h | 3 | 2026 | not checked |
| 2026 BC2 | 10.562 | 22.6 | 10.4 h | 2 | 2026 | not checked |
| 2025 QO7 | 10.813 | 27.0 | 2.68 min | 2 | 2025 | not checked |
| 450300 | 11.430 | 20.7 | 2.06 h | 2 | 2026 | no spin (card of 21 Nov) |
| 837134 | 11.485 | 19.8 | 3.52 h | 3 | 2026 | no spin (card of 21 Nov) |
| 187040 | 11.607 | 19.2 | 20.6 h | 3 | 2025 | no spin (card of 21 Nov) |
| 612786 | 11.681 | 21.4 | 13.2 h | 3 | 2026 | no spin (card of 21 Nov) |
| 139622 | 11.792 | 18.5 | 17 h | 3 | 2024 | no spin (card of 21 Nov) |
| 2024 BT2 | 11.897 | 23.1 | 2.3 h | 3 | 2024 | not checked |

The U value is the table's own column. All 35 lack a period in JPL's table and in LCDB. For SsODNet: 7 cards were fetched today and 13 were among the 1,704 cards of 21 November, all without a spin; 15 objects never had a card fetched, so SsODNet is "not checked" for them.

## Sources

Read or tested on 2026-11-24 unless marked.

SsODNet
- Service page, card and bulk-table documentation: https://ssp.imcce.fr/webservices/ssodnet/ ; https://ssp.imcce.fr/webservices/ssodnet/api/ssocard/ ; https://ssp.imcce.fr/webservices/ssodnet/api/ssobft/
- Card: https://ssp.imcce.fr/webservices/ssodnet/api/ssocard/Bennu ; name index: https://api.ssodnet.imcce.fr/quaero/1/sso ; per-property: https://ssp.imcce.fr/webservices/ssodnet/api/datacloud.php ; status: https://ssp.imcce.fr/webservices/ssodnet/api/getAvailability.php
- Static files: https://ssp.imcce.fr/data/ssoBFT-latest_Asteroid.parquet ; https://ssp.imcce.fr/data/ssoBFT-latest_Asteroid.ecsv.bz2 ; https://ssp.imcce.fr/data/ssodnet_biblio.json ; https://ssp.imcce.fr/data/ssodnet.bib ; https://ssp.imcce.fr/data/metadata_asteroid.json ; https://asterm.imcce.fr/public/ssodnet/sso_index.csv.gz
- Berthier et al. 2023: https://arxiv.org/abs/2209.10697 (PDF read for the update statements)
- rocks documentation and source: https://rocks.readthedocs.io/en/latest/ ; https://rocks.readthedocs.io/en/latest/cli.html ; https://raw.githubusercontent.com/maxmahlke/rocks/master/rocks/cache.py (also `cli.py`, `index.py`, `ssodnet.py`)

Lightcurves
- LCDB: https://minplanobs.org/mpinfo/php/lcdb.php ; https://minplanobs.org/MPInfo/datazips/LCLIST_PUB_CURRENT.zip
- ALCDEF: https://alcdef.org/ ; https://alcdef.org/php/alcdef_dataPolicy.html ; https://alcdef.org/php/alcdef_briefHistory-1.html ; https://alcdef.org/php/alcdef_GenerateALCDEFPage.php ; https://alcdef.org/docs/ALCDEF_ALL.zip
- Minor Planet Bulletin: https://mpbulletin.org/ ; https://mpbulletin.org/issues/MPB_53-4.pdf
- Pravec: http://space.asu.cas.cz/~ppravec/ ; http://space.asu.cas.cz/~ppravec/newres.htm ; http://space.asu.cas.cz/~ppravec/newres.txt (the `www.asu.cas.cz` address redirects here)
- TTT survey, Alarcon, Licandro & Serra-Ricart 2026: https://arxiv.org/abs/2602.18562 ; https://arxiv.org/html/2602.18562v1
- Las Cumbres portal: https://neoexchange.lco.global/ ; https://neoexchange.lco.global/summary/lc/ ; https://neoexchange.lco.global/characterization/ ; pilot abstract https://meetingorganizer.copernicus.org/EPSC-DPS2025/EPSC-DPS2025-997.html (search summary)

Astrometry and photometry
- MPC observations API: https://docs.minorplanetcenter.net/mpc-ops-docs/apis/get-obs/ ; https://data.minorplanetcenter.net/api/get-obs
- Rubin status post: https://www.rubin.community/t/rubin-status-november-17-2026/12959 ; plan document https://rtn-011.lsst.io/
- MANOS colours, Moskovitz et al. 2026: https://arxiv.org/abs/2603.15872

Sizes and albedos
- NEOWISE PDS bundle: https://sbn.psi.edu/pds/resource/neowisediam.html
- NEO Surveyor at IPAC: https://www.ipac.caltech.edu/project/neo-surveyor ; 2024 talk (search summary) https://cor.gsfc.nasa.gov/copag/meetings/AAS_Jan2024/presentations/tdamm-sig/4_Cutri_TDAMM-SIG_NEOSurveyor-AAS243.pdf
- Spitzer table: https://raw.githubusercontent.com/mommermi/spitzerneos/master/spitzerneos.csv
- JPL radar pages: https://echo.jpl.nasa.gov/asteroids/alldetections.html ; https://echo.jpl.nasa.gov/asteroids/goldstone_asteroid_schedule.html

Taxonomy and spectra
- CDS notice: https://cds.unistra.fr/ ; TAP https://tapvizier.cds.unistra.fr/TAPVizieR/tap/sync ; Harvard mirror https://vizier.cfa.harvard.edu/viz-bin/asu-tsv ; listing of recent catalogs (search summary) https://cdsarc.cds.unistra.fr/ftp/cats/META/cats30.htx
- MITHNEOS: http://smass.mit.edu/minus.html ; http://smass.mit.edu/data/spex/change_log/changeLog.rtf
- MANOS: https://manos.lowell.edu/
- Gaia DR4: https://www.cosmos.esa.int/web/gaia/dr4

Literature
- arXiv listing: https://rss.arxiv.org/rss/astro-ph.EP ; API: https://export.arxiv.org/api/query ; terms: https://info.arxiv.org/help/api/tou.html
- 2026 QQ8 paper, Bolin et al.: https://arxiv.org/abs/2611.31213
- ADS API: https://raw.githubusercontent.com/adsabs/adsabs-dev-api/master/README.md ; terms: http://adsabs.github.io/help/terms/ ; fields: http://adsabs.github.io/help/search/comprehensive-solr-term-list

Prices and facts
- USGS data release: https://www.usgs.gov/data/mineral-commodity-summaries-2026-data-release (DOI 10.5066/P1WKQ63T)
- World Bank: https://www.worldbank.org/en/research/commodity-markets ; https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx ; https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets
- Johnson Matthey: https://matthey.com/products-and-markets/pgms-and-circularity/pgm-management/base-price-trading-disclaimer
- LBMA and ICE notices (search summary): https://www.lppm.com/news/lbma-platinum-and-palladium-price-actions_2097.html ; https://www.ice.com/publicdocs/iba/IBA_LBMA_Platinum_and_Palladium_Price_auctions_and_administer_LBMA_Platinum_and_Palladium_Price_benchmarks_on_and_from_1_July_2026.pdf
- IMF commodity prices (search summary): https://data.imf.org/en/datasets/IMF.RES:PCPS
- Wikipedia API: https://en.wikipedia.org/w/api.php

Project files used: `docs/plan.md`, `DESIGN.md`, `AGENTS.md`, `docs/research/catalogs.md`, `docs/research/verify-coverage.md`, `docs/research/verify-facts-venues.md`, `docs/research/verify-obs-window.md`, `docs/research/new-surveys.md`, `docs/research/verify-value-inputs.md`, `docs/research/verify-capability.md`; `data/snapshots/2026-11-21` and `2026-11-24`; `data/research/dl/coverage-exact/spin_periods.json` from the data archive.
