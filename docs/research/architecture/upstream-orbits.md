# Upstream access for orbits, tracking and observing windows

Written 2026-11-24 for the architecture review. It answers one question: what live access exists to the fast-moving data (orbits, tracking, observing windows), and what is the cheapest correct way to keep a local copy current. Physical measurements are in `upstream-physical.md`.

Evidence is of three kinds, marked throughout: **[test]** my own test today, on the two local snapshots or by a single request to a non-JPL service; **[doc]** a documentation or terms page read today; **[21 Nov]** taken from this project's earlier research files and not re-read at the source. Section 11 lists every URL. No request went to a JPL API endpoint. No personal or project detail was sent anywhere.

## 1. The answer

**All of this data can be kept current by a scheduled job. None of it needs a live call when a visitor loads a page, and JPL forbids that anyway.** Every source refreshes about once a day, driven by one event: the Minor Planet Center's Daily Orbit Update, a circular issued around 12:30 UT.

- **Two requests a day keep the whole list-level picture current**, for all 43,379 near-Earth objects and not only the 7,231 reachable ones: JPL's reachable list (2.6 MB) and JPL's near-Earth table (15.8 MB). JPL offers no "changed since" filter, no paging need, and no cache headers, so the job downloads both and compares them with yesterday's.
- **About 7 to 10 more requests a day cover the detail the bulk table leaves out** (the force law behind a fitted push, the orbit's covariance, alternate designations), one per reachable object whose orbit was replaced.
- **A typical day for the reachable list is 11 to 24 requests and about 21 MB.** Section 6 writes the run out.
- **There is no push channel worth building on.** Email is the only push any of the three agencies offers.
- **Nobody upstream keeps history.** JPL shows only the current orbit and overwrites it. The project's own dated snapshots are the only record of what was known when, and the forecasts depend on that record. It cannot be backfilled.

Three things I did not expect, all from today's tests:

1. **The Minor Planet Center's daily circular predicts JPL's changes exactly.** The 24 November circular lists new observations for 184 objects. 182 of them had a new JPL orbit by the evening pull and the other 2 were new to JPL.
2. **ESA publishes a timestamped change log that JPL lacks.** One file, `updated_nea.lst`, records which objects ESA refitted and when, back to 5 June 2026, with removals. It matched 338 of the 338 asteroid orbit changes JPL made between the two pulls.
3. **JPL's reachable list still carries an object the Minor Planet Center has withdrawn.** 2026 JG2 is on the list today. The Minor Planet Center's identifier service does not know the designation, and ESA logged its removal on 5 June 2026.

## 2. Terms used here

- **Orbit solution**: one fit of an object's orbit to its observations. JPL gives each a new id (`orbit_id`) and replaces the old one.
- **MPC**: the Minor Planet Center, which receives every observation and assigns designations.
- **MPEC**: one of the MPC's electronic circulars. The **Daily Orbit Update** is the once-a-day circular listing new observations and orbits.
- **NEOCP**: the MPC's confirmation page, where new candidates sit before they get a designation.
- **Reachable list**: JPL's NHATS list. **Near-Earth table**: JPL's database (SBDB) restricted to near-Earth objects.
- **Sunlight push**: the two fitted effects of sunlight on an orbit (drift and radiation pressure). **Force law**: the assumed way that push weakens with distance from the Sun.

## 3. What the two snapshots show [test]

The pulls were at 16:35 UT on 21 November and 01:12 UT on 25 November, 3.36 days apart. I re-ran the diff and it reproduces the counts in the brief. What it adds:

| Finding | Number | What it means for the sync |
|---|---|---|
| Byte hash of each response | Differs | The key order inside each reachable-list record changed between pulls. Hash parsed rows, never the response. |
| Row order | Stable for all common rows, both lists | New rows are appended. Do not rely on it. |
| Near-Earth rows changed | 342 | |
| ...of which have a new `orbit_id` | 342 | `orbit_id` is a complete change key for the orbit fields in this sample. |
| ...of which have a new last-observation date | 216 | The last-observation date misses 126 of 342 changes. 2011 AA37 gained three observations made on 2 August and reported on 24 November. |
| Physical fields changed | 0 | Confirms the brief. |
| `orbit_id` shapes | `659`, `JPL 732`, `E2024-YN8`, `E2026W95`, `MPO508629`, `JPL K273/32` and more | Treat it as an opaque string. The near-Earth table writes newer solutions as `JPL 732` where the reachable list writes `732`, so strip the prefix before comparing the two. The `E` forms name an MPC circular: orbits JPL took from the MPC and has not refitted (21 reachable objects). |
| Reachable-list rows changed | 222 | |
| ...window start changed | 216 | 204 of these are one edit: `2026-11-21` became `2026-11-27` on every window already open. 12 are windows that closed. |
| ...changed, ignoring window start and brightness | 51 | The real churn is about 15 rows a day. |
| Reachable rows one orbit behind the near-Earth table | 16, then 17 | The trajectory search runs later than the orbit update. |
| Objects added to the reachable list | 2 | One new discovery (2026 WV1). One known object whose new orbit just qualified (2026 VQ5, one trajectory at 11.989 km/s). |

Two consequences need stating plainly.

**The window start JPL publishes for an open window is a rolling date, not when the window opened.** It moved from the first pull's date to 27 November, a date after the second pull. JPL's rules exclude the days around full moon, and the Moon was full on 24 November, which would explain the jump; that reading is my inference. The site must keep the first start date it ever saw for each window and ignore later changes to it.

**The reachable list lags the orbit table by a day, and for some objects longer.** All 14 reachable objects in the 24 November circular had a new orbit in the near-Earth table 12.7 hours later, and all 14 still showed the old orbit in the reachable list. Two others (2019 YS3, 2026 DM15) were one solution behind at both pulls. JPL's page says the software "automatically processes new NEAs and those with updated orbit solutions" and calls it a "daily analysis" [doc]. The per-object mode returns a `computed` date [doc].

## 4. What each service offers

### 4.1 JPL

One policy covers every JPL interface below [doc; wording quoted on 21 Nov]: one request at a time; cache instead of re-requesting; back off on errors; automated clients "must provide a valid, application-specific User-Agent request header that includes correct product name, version, and contact information"; no embedding in a website; formats "can change without notice", so check the `version` field. The page is undated and I could not establish when the User-Agent rule appeared.

| Service | What it returns | Cadence | Changed-since or paging | Size | Version |
|---|---|---|---|---|---|
| Reachable list, bulk (`nhats.api`) | Per object: delta-v, duration, trajectory count, orbit id, orbit quality, H, size range, next window, radar opportunities | Daily batch, a day behind the orbit table [test] | None. Filters only on delta-v, duration, stay, launch years, H, orbit quality | 2.6 MB | 1.3, September 2019 |
| Reachable list, one object (`nhats.api?des=`) | The same, plus the full best trajectories and a `computed` date | Per object, when its orbit changes | – | Not measured | same |
| Near-Earth table, bulk (`sbdb_query.api`) | Any documented field for every match. Fields exist for `spkid`, `soln_date` (when the orbit was fitted), `source`, `producer`, element uncertainties, and a `full-prec` switch | Horizons' manual says its copy "is updated hourly with new objects and orbit solutions" [doc]. Measured: complete within 12.7 hours of the circular | `limit` and `limit-from` page results. No date filter: `soln_date`, `last_obs` and `orbit_id` are not in the list of fields that can be constrained [doc] | 15.8 MB as pulled | 1.0, August 2021 |
| One object (`sbdb.api`) | Full precision; covariance; every model parameter including the force law; physical values with reference and notes; alternate designations and alternate SPK-IDs; close approaches; radar; discovery | Same as above | – | 2.2–6.5 kB in 14 responses saved on 21 November; the options they were requested with are not recorded | 1.3, September 2021 |
| Radar measurements (`sb_radar.api`) | Every delay and Doppler record, or one object's. A `modified` field can be added to the output | Not stated | No filter on `modified` | One request for all: 4,715 records [21 Nov] | 1.1, February 2022 |
| Close approaches (`cad.api`) | Date, distance and its range, speed, orbit id | Not stated | Date range, `limit`, `limit-from` | Default: Earth, 60 days ahead, within 0.05 au | 1.5, March 2023 |
| Scout | Candidates on the NEOCP: orbit samples, ratings, ephemerides | "Updated every 15 minutes" [doc] | – | Small | 1.3, September 2021 |
| Sentry | Impact-risk list. Has a removed-objects mode with removal dates | Not stated | `days` filters on days since last observation | Small | 2.0, July 2021 |
| Horizons | Ephemerides, state vectors, elements, SPK files, one target per request | Hourly [doc] | – | 220 kB per object in 131 ephemerides saved on 21 November | 1.3, June 2025 |

**What the bulk table cannot return** [doc]: the force-law constants behind A1, A2 and A3; the covariance; references and notes on physical values; alternate designations. The snapshots also lack `spkid`, `soln_date`, `source` and full precision, but only because the pulls did not ask for them. Whether `full-prec` applies to the fitted push values is not documented and could not be tested today.

**No bulk file or mirror replaces these calls.** JPL's page of bulk element files served unfilled template text today [doc]. NASA's NeoWs is not a mirror: it reported 63,136 near-Earth objects where JPL has 43,379 [test].

**Scout and Sentry are not needed.** An object on the confirmation page has no designation and cannot be on the reachable list. Scout's own documentation gives no link from a temporary name to the later designation; the MPC does (4.2).

**Horizons is the wrong tool for windows across the list.** At 220 kB an object, recomputing windows for the reachable list is 7,231 requests and about 1.6 GB, one request at a time. JPL already publishes the next window. ESA publishes a 30-day ephemeris for every near-Earth asteroid in one file, daily (`allnea_30d.eph`) [doc; not downloaded].

### 4.2 Minor Planet Center

Limit on every API endpoint: "not more than 5 requests per second", with HTTP 429 and possible IP blocking [doc]. The static files state no limit. "Data from the MPC's database is made freely available to the public" [doc].

| Service | What it gives | Today [test unless marked] |
|---|---|---|
| Daily Orbit Update circular | New orbits and a "New observations" section | Issued every day from 18 to 24 November. 24 November: issued 12:28 UT, 2.8 MB of HTML, about 33,500 orbits, 934 observation lines for 184 objects, all 184 near-Earth |
| `NEA.txt` | One line per near-Earth asteroid: elements, orbit quality, observation count, arc, the circular the orbit came from, last-observation date | 43,220 lines, 8.8 MB, 19 s. Carries `ETag` and `Last-Modified` (24 November 15:01 UT), so an unchanged file costs one small request. 191 lines cite the 24 November circular |
| `DAILY.DAT` | Orbits from the latest circular, all asteroid classes | 6.8 MB, modified 12:56 UT |
| `MPCORB.DAT.gz` | Every asteroid orbit | 94.8 MB, modified 12:56 UT |
| Extended JSON files | The same as JSON | Stale: `nea_extended.json.gz` last modified 18 November |
| Observations API (`get-obs`) | Every published observation of one object | One designation per request [doc]. 2011 AA37: 207 observations, 399 kB as JSON rows, 1.2 s. Each row has a permanent `obsid` and the circular it was published in (`ref`), and no timestamp. The three observations from that morning's circular were present 13 hours later |
| Orbits API (`get-orb`) | The MPC's own fit, one object per request [doc] | 2022 OB5: 11.9 kB, 0.6 s. Format `mpc_orb` version 0.7. Includes a fitted drift term with a 7-by-7 covariance, a `fitting_datetime`, and residual files |
| Identifier API (`query-identifier`) | Resolves any designation to the primary one, with secondary designations | Up to 100 per request [doc]. Six ids in 2.0 s. Results in section 5 |
| Lists API (`list`) | Named groups such as `neos`, up to 50,000 per request | No list of recently changed objects, and no date filter [doc] |
| Circulars API (`mpecs`) | Circulars naming an object | Cannot list circulars since a date, and does not search the Daily Orbit Update text [doc] |
| Confirmation page feed | Current candidates | `neocp.json` 12.8 kB, 51 objects, modified within the minute, with `ETag`. The "previous objects" page lists the last 100 with temporary name, final designation, circular and time |
| Bulk observation files | Every observation | "Complete through the 2026 APR. 14 batch": seven months stale. Mid-month files are from November 2025. 9.1 GB for numbered objects [21 Nov] |
| Replicated database | A live Postgres copy, by logical replication through the Small Bodies Node | Needs a 4 TB SSD, 32–48 GB of memory, and a server online all day. Licence is for "internal purposes". The MPC "strongly advise[s]" against it and replicas that fall behind are dropped [doc]. Its observation table has `created_at` and `updated_at` columns, and there are tables for deleted and redesignated observations, marked partially populated [doc] |
| MAQI | Query interface to that copy | A login page with no sign-up. Beta, by request to the Small Bodies Node [doc] |
| Asteroid Institute BigQuery copy | The same data in Google BigQuery | Queries billed to the user; described as updated in real time. Search result only, not opened |

**Which gives a daily list of objects whose observations changed?** The Daily Orbit Update circular, in its "New observations" section. `NEA.txt` gives the same list from a cacheable file, as the lines whose reference names the new circular. The replicated database gives it by query, at a cost out of proportion to this project. Nothing else does: the bulk files are months stale and the observations API takes one object at a time.

### 4.3 ESA's coordination centre (NEOCC)

Plain HTTPS downloads, no login. ESA says the interface "may be modified, changed, or removed at any moment without advance warning" [doc]. No rate limit is stated. Responses carry no `ETag` or `Last-Modified` [test].

| File | Contents | Today [test] |
|---|---|---|
| `updated_nea.lst` | A running log: a timestamp, then the objects refitted at that moment; "Removed" blocks for objects dropped | 2.25 MB, 72,602 lines, 1,460 timestamps from 5 June 2026 to 00:45 UT on 25 November, half an hour before I fetched it. The large block lands between 13:00 and 13:31 UT on most days |
| `neo_kc.cat` | Full-precision elements for every near-Earth asteroid, with a flag for a fitted sunlight push | Slow: 6.3 MB in 120 s, then my timeout. About 8.5 MB in full by row size |
| `<name>.ke1` and three sibling formats | One object's orbit: elements, covariance, fitted area-to-mass ratio and drift, their signal-to-noise | `2022OB5.ke1`: 3 kB in 0.6 s, with both push terms and an 8-by-8 covariance |
| `<name>.rwo` | Every observation with its weight, bias, residual and rejection flag | Not fetched today [21 Nov] |
| `allnea_30d.eph` | 30-day ephemeris, all objects, daily | Listed [doc]; not fetched |

**Is it a usable second source?** Technically yes, for both.

- *Orbits*: an independent fit of every near-Earth asteroid, refreshed on the same daily trigger as JPL's.
- *Sunlight push*: in the 32,348 rows I received, ESA flags a fitted push for 390 objects, 103 of them reachable. JPL has one for 618 of the same rows. 326 are in both, 64 are ESA's alone and 292 are JPL's alone. The MPC's orbits API is a third source for some.

**The terms limit what can be shown.** ESA's general terms allow "personal non-commercial use" and say ESA "does not grant the right to resell or redistribute" without "prior written authorisation" [doc]. A 2021 news item says the centre "encourages you to make use of these data to develop or to support your NEO-related projects" [doc]. So: free to use as an internal cross-check and change signal; displaying its values on a public site needs a written yes.

### 4.4 Push and event channels

| Channel | What arrives | Use |
|---|---|---|
| MPC circulars by email, with an option for the Daily Orbit Update [test] | Each circular as mail | A trigger at best; the same content is one request away |
| JPL `nhats` list: a "daily notification service" [doc] | Not described on the page | Unknown until subscribed |
| JPL `ssd-announce` list [doc] | Significant changes to JPL's services, "infrequent" | Subscribe. This is the only advance notice JPL gives |
| MPC newsletter and status page [test] | Format changes, outages | Subscribe and poll the status page |
| ESA system-status page [doc] | A dated changelog | Poll |
| Rubin alert stream through brokers [21 Nov] | Individual detections, not orbits | Not a substitute. Rubin still reports to the MPC in ad hoc batches |
| MPC database replication | Row-level changes, continuously | The only true push. Ruled out by its cost and licence |

**Nothing beats polling once a day.** No service offers a webhook, a feed with entries per object, or a "since" parameter. I found no RSS link on the MPC's circulars page [test].

## 5. How a deletion or a redesignation shows up [test]

JPL's lists have no removal notice. A row just stops appearing. Four real cases, from ESA's "Removed" log and one request to the MPC's identifier service:

| Designation | ESA logged removal | MPC identifier says | In JPL's near-Earth table today |
|---|---|---|---|
| 2026 NA1 | 11 July 2026 | Now a secondary designation of 2007 AA2 | Absent: merged into the other object |
| 2010 HZ23 | 30 June 2026 | Still primary; gained secondary 2025 YK10 | Absent: no longer near-Earth after the link |
| 2011 WE | 27 October 2026 | Not found | Absent: withdrawn |
| 2026 JG2 | 5 June 2026 | Not found | **Present, and on the reachable list.** Five observations over one day in May |

So a row vanishing from JPL can mean merged, reclassified, or withdrawn, and only the MPC's identifier service says which. A withdrawn object can also stay in JPL's lists for months.

Numbering is the fourth case: the designation changes from `2016 HO3` to `469219`. The bulk row's full name keeps the old designation in brackets, so the link can be made without a request. JPL's single-object interface offers alternate SPK-IDs, which means an SPK-ID is not guaranteed to stay an object's only id; my recollection, not re-verified today, is that it changes at numbering. The plan keys identity on "JPL's permanent id". That should become the project's own key with an alias table holding every designation and every SPK-ID seen.

The two catalogs also disagree at the edges on any given day: 1 of 7,231 reachable objects and 24 of 43,170 JPL near-Earth asteroids are not in the MPC's file by designation, and 74 of the MPC's are not in JPL's.

## 6. The daily sync, written out

Proposed. One run a day at about 10:00 UT. That is late enough for JPL's trajectory batch to have caught up with yesterday's circular and before today's is issued. The catch-up time is an assumption to confirm from the first week's logs: the measured lag is "more than 12.7 hours".

Every JPL request goes one at a time through a single queue, with a pause between requests, and stops on HTTP 503 or 429.

| Step | Request | Count | Size | Change detection |
|---|---|---|---|---|
| 1 | JPL reachable list, bulk | 1 | 2.6 MB | Parse; hash each row with keys sorted; compare by designation. A new orbit id means the trajectories were recomputed. Window start and brightness are compared separately (section 3) |
| 2 | JPL near-Earth table, bulk, with `spkid`, `soln_date` and `source` added | 1 | 15.8 MB | Compare by designation. New `orbit_id` is the orbit change key. Hash the physical fields separately, since those can change without a new orbit |
| 3 | Check the `version` field of both, the field lists and the row counts against yesterday | 0 | – | Stop and alert on any difference in version or fields |
| 4 | JPL single object, for each reachable object that is new or has a new orbit id | 7–10 typical, up to about 30 | a few kB each | Stores full precision, covariance, the force law, alternate ids |
| 5 | JPL reachable list, one object, for each whose list row has a new orbit id | 0–10 | Not measured | Only if the site shows trajectory detail beyond the bulk row |
| 6 | MPC identifier, for every designation that vanished or appeared | 1 (up to 100 ids) | small | Sorts vanished rows into merged, reclassified, withdrawn |
| 7 | ESA `updated_nea.lst` | 1 | 2.25 MB | Every asteroid in step 2's diff should appear in the log since the last run, and the reverse. Read the "Removed" blocks |
| 8 | Write the run's manifest: counts, hashes, versions, the number of reachable rows behind the orbit table | 0 | – | Feeds the release guard in the plan's Appendix B |

Weekly, or when step 2 shows a change in an object's radar counts (one did, 2026 TS): the radar table, 1 request. Weekly: the whole reachable list through the MPC identifier, 73 requests, to catch cases like 2026 JG2.

**Totals.**

| | Requests a day | Volume a day |
|---|---|---|
| Reachable list alone | 11–24 | About 21 MB: 18.4 MB of JPL bulk, 2.25 MB from ESA, under 0.2 MB of single objects |
| All near-Earth objects, list-level | The same 2 bulk requests already cover them | Same |
| All near-Earth objects, with a single-object call per changed orbit | 105–160 typical; about 470 on the busiest day in ESA's log | About 22 MB |
| The same, plus the MPC's observations for each changed object | 210–320 | Not measured |

How busy a day gets, from ESA's log since 27 August: a median of 152 objects refitted a day, 54 at the 10th percentile, 255 at the 90th, 462 at most, and no day without an entry. The 102 a day in the brief's measurement is a quiet stretch. The reachable list is about 7% of the changes (24 of 342).

Stored compressed, the two JPL responses come to 3.5 MB a day (measured with gzip on the local files), about 1.3 GB a year. Whether JPL compresses responses on the wire was not tested.

A first fill of single-object detail is 7,231 requests for the reachable list: two to four hours at one request every one or two seconds. For all near-Earth objects it is not needed. The bulk table covers them, and only the 686 objects with a fitted push (174 reachable) need the single-object call for the force law.

**What cannot be kept current automatically.**

- Physical measurements. None changed in 3.4 days, and JPL's physical fields are a poor source for them (`upstream-physical.md`).
- When an open window opened. JPL overwrites it; only the project's own history has it.
- Yesterday's orbit. Once replaced it is gone from JPL.
- The trajectory figures for an object whose orbit just changed, for about a day, and for a few objects indefinitely. The site should say which orbit each figure was computed on.
- Whether a withdrawn object should stay on the site. That needs a rule from the owner.
- A day when everything changes. ESA refitted 46,027 entries on 30 July 2026 when it changed reference frame [test, doc]. JPL recomputed its whole catalog for a new planetary ephemeris in April 2021 [doc]. Per-object follow-up must be resumable and capped, and the release guard will hold such a day for a person to look at.
- A format change. JPL promises none will be announced.
- Candidates not yet designated. They are out of scope until the MPC names them.

## 7. Stability over the last two years, and what to watch

**JPL.** The interfaces have been still. No version number of the list, table, single-object, radar, close-approach, Scout or Sentry interface has changed since March 2023, and the reachable list's since September 2019 [doc]. The one announcement in the period: on 29 September 2025, the Horizons terminal interface began moving from clear text to TLS, with clear text kept "until at least October 1, 2026"; the HTTP interfaces were not affected [doc]. I found no record of an outage, and JPL's news pages load by script and could not be read. What a version number does not protect against is visible in the data: at least six shapes of orbit id in one column, and key order that differs between pulls [test].

**Minor Planet Center.** Busy, and openly logged. The status page has 125 entries [test]. In the last two years: database upgrades (February and March 2025); MPChecker taken offline after requests from "thousands" of IP addresses (January 2025); three power outages at its data centre (September 2025); its ingestion system moved to AWS (12 November 2025); ingestion problems (December 2025); processing delays (April and May 2026); network downtime (July 2026). Format and practice changes in progress [doc]: submissions with duplicated timestamps rejected from 12 November 2026; only the 2022 version of the submission format from 30 December 2026; comet designation practice changes from 7 December 2026; a new packed form for designations beyond 15,500 in a half-month, built for Rubin; the old search page being replaced. The orbit format is at version 0.7 and the orbit table in the replicated database is "partially populated". Two of its files were stale today (4.2).

**ESA.** Its changelog [doc] shows new fitting software in March 2025, the priority list switched off in August 2025, an MPC monthly update only partly processed in September 2025, and the switch of reference frame on 30 July 2026 that refitted every object.

**What a maintainer should monitor**, in order of how often it will fire:

1. The age of each source's newest data. The plan already asks for a banner past ten days.
2. Rows changed per day against the running median. A jump is a whole-catalog refit or a broken parser.
3. Agreement between JPL's diff and ESA's log. Today it is 338 of 338. A drop means one side is down or changed.
4. The count of reachable rows behind the orbit table. Normal is 16 or 17.
5. Row counts, field lists, and the `version` field in every JPL response.
6. Any orbit id or designation the parser has not seen the shape of.
7. HTTP 429 and 503 rates, and any sign of blocking.
8. The `ssd-announce` list, the MPC newsletter and status page, and ESA's status page.

## 8. What this means for the design

- **"Dynamic" here means a daily job and a store, not live calls.** Nothing upstream changes faster than daily except the confirmation page, which is out of scope. JPL's terms rule out calling it from the browser. So the app's freshness is set by the job, whatever serves the pages.
- **The plan's weekly refresh should be daily for the list-level pull.** It costs two requests. A new object is brightest in its first days (median fading of 4 magnitudes in four weeks, per `verify-obs-window.md`), so a weekly refresh shows a new target after its best window has gone. Fits stay manual, as the plan says.
- **Start archiving before building anything else.** History is the one input that cannot be recovered later, and the forecasts are scored on "the last [version] whose inputs predate the resolving observation". The archive is 3.5 MB a day.
- **The stack choice depends on these facts, and they do not pick a stack.** The job needs: a host that is on every day; outbound HTTPS from a stable address, since the MPC blocks by IP and JPL asks for a contact; a disk that persists (about 1.3 GB a year of raw responses); a scheduler that guarantees one JPL request at a time; and somewhere to raise an alert. Whether that host is also the one serving the app, and whether the app reads the job's store directly or a published data set, is the owner's call.
- **Roles for the three agencies.** JPL is the source of what is displayed. The MPC supplies identity and the reason anything changed. ESA is a cross-check and a second fit, not shown publicly without permission.
- **The two existing snapshots are a ready-made test.** A diff engine fed 21 and 24 November must report 2 added, 0 removed, 342 new orbit ids, 222 changed reachable rows of which 51 are real, and 17 rows behind.

## 9. Decisions for the owner

1. **A contact address and a product name for the User-Agent.** No automated JPL call can be made until this exists, so it blocks the archive and everything after it. The plan already asks for a role address.
2. **Where the daily job runs.** It needs a machine that is on every day. This is tied to the app's host, which is not chosen.
3. **Daily or weekly.** The plan says weekly. This report recommends daily for the two bulk pulls.
4. **How far per-object detail goes.** The reachable list only (7 to 10 calls a day), or every near-Earth object with a fitted push as well (686 objects, needed for the plan's validation set in R3).
5. **Whether to store the MPC's observations now.** They are needed only for the project's own orbit fits (R3). Starting now costs about 7,231 requests once and 7 to 10 a day.
6. **Whether to ask ESA for written permission** to show its values, or keep it as an internal cross-check.
7. **What the site does with an object the MPC has withdrawn and JPL still lists** (2026 JG2 today), and with one that drops off the reachable list after a new orbit.
8. **Which address subscribes** to `ssd-announce`, the MPC's circulars and newsletter, and JPL's daily `nhats` notification.

## 10. Not checked

- Any live JPL behaviour: whether `full-prec` reaches the fitted push values, whether responses can be compressed, the size of a single-object response with covariance, when the trajectory batch finishes, and whether an SPK-ID changes at numbering.
- When JPL's fair-use policy took its present form. The page is undated and the web archive was unreachable.
- JPL's announcement index and Horizons news, which load by script.
- ESA's `allnea_30d.eph` and the last quarter of `neo_kc.cat`.
- The MPC's `list` endpoint, the Asteroid Institute's BigQuery copy, and MAQI beyond its login page.
- Whether ESA truncates `updated_nea.lst`. It reaches back 5.7 months today.
- The test scripts were temporary and are not in the repository. Each test is described closely enough here to repeat.

## 11. Sources

Read today through a page fetch unless marked. "Own request" means one direct request from this machine today.

**JPL**
- Fair-use policy and list of interfaces: https://ssd-api.jpl.nasa.gov/doc/ (exact wording as quoted in `../verify-facts-venues.md`, 21 November)
- Reachable list: https://ssd-api.jpl.nasa.gov/doc/nhats.html ; https://cneos.jpl.nasa.gov/nhats/intro.html ; https://cneos.jpl.nasa.gov/nhats/subscribe.html
- Near-Earth table: https://ssd-api.jpl.nasa.gov/doc/sbdb_query.html ; https://ssd-api.jpl.nasa.gov/doc/sbdb_filter.html
- One object: https://ssd-api.jpl.nasa.gov/doc/sbdb.html
- Radar: https://ssd-api.jpl.nasa.gov/doc/sb_radar.html
- Close approaches: https://ssd-api.jpl.nasa.gov/doc/cad.html
- Scout: https://ssd-api.jpl.nasa.gov/doc/scout.html ; https://cneos.jpl.nasa.gov/scout/intro.html
- Sentry: https://ssd-api.jpl.nasa.gov/doc/sentry.html
- Horizons: https://ssd-api.jpl.nasa.gov/doc/horizons.html ; https://ssd.jpl.nasa.gov/horizons/manual.html (first half read)
- Announcements: https://ssd.jpl.nasa.gov/email_list.html ; https://ssd.jpl.nasa.gov/announcements/an20250929.html ; https://ssd.jpl.nasa.gov/announcements/an20210412a.html
- Bulk element files (template text only): https://ssd.jpl.nasa.gov/sb/elem_tables.html
- Window rules: https://cneos.jpl.nasa.gov/nhats/obs.html (as quoted in `../verify-obs-window.md`, 21 November)
- NeoWs count, own request: https://api.nasa.gov/neo/rest/v1/stats

**Minor Planet Center**
- Interface documentation: https://docs.minorplanetcenter.net/mpc-ops-docs/apis/ and its pages `get-obs/`, `get-orb/`, `list/`, `summary/`, `mpecs/`, `query-identifier/`, `get-obs-neocp/`
- Limits: https://docs.minorplanetcenter.net/mpc-ops-docs/faqs/
- Orbit files, own request: https://www.minorplanetcenter.net/iau/MPCORB.html ; headers of `NEA.txt`, `DAILY.DAT`, `MPCORB.DAT.gz` under https://www.minorplanetcenter.net/iau/MPCORB/ ; headers of `nea_extended.json.gz`, `daily_extended.json.gz`, `neocp.json` under https://www.minorplanetcenter.net/Extended_Files/ ; https://www.minorplanetcenter.net/iau/NEO/neocp.txt
- `NEA.txt` in full, own request: https://www.minorplanetcenter.net/iau/MPCORB/NEA.txt
- Circulars, own requests: https://www.minorplanetcenter.net/mpec/RecentMPECs.html ; https://www.minorplanetcenter.net/mpec/K26/K26W95.html
- Bulk observations, own request: https://www.minorplanetcenter.net/iau/ECS/MPCAT-OBS/MPCAT-OBS.html
- Status, own requests: https://www.minorplanetcenter.net/mpcops/mpcstatus/ ; https://minorplanetcenter.net/iau/info/MPCOpStatus.html
- Email sign-up, own request: https://www.minorplanetcenter.net/mpcops/signup/mpecs/
- Previous confirmation-page objects, own request: https://www.minorplanetcenter.net/mpcops/neocp/neocp_prev_des/
- Interface tests, own requests: https://data.minorplanetcenter.net/api/get-obs (2011 AA37) ; https://data.minorplanetcenter.net/api/get-orb (2022 OB5) ; https://data.minorplanetcenter.net/api/query-identifier (six ids)
- Replicated database: https://sbnmpc.astro.umd.edu/MPC_database/replication-info.shtml ; https://docs.minorplanetcenter.net/mpc-ops-docs/data-and-services/replicated-tables-intro/ ; `.../replicated-tables-schema/` ; `.../schema/obs-sbn/` ; https://maqi.astro.umd.edu/
- Newsletters: https://buttondown.com/MPC_newsletter/archive/newsletter-october-2026/ ; `.../newsletter-september-2026/` ; `.../newsletter-march-april-2026/`
- Designation formats: https://docs.minorplanetcenter.net/mpc-ops-docs/designations/packed-designations/ ; `.../provisional-designations/`
- BigQuery copy (search result only): https://mpcq.readthedocs.io/en/latest/bigquery_dataset.html

**ESA**
- Automated access: https://neo.ssa.esa.int/computer-access ; https://neo.ssa.esa.int/python-interface ; https://neo.ssa.esa.int/-/automated-data-access-to-esa-s-neocc-portal
- Files, own requests: https://neo.ssa.esa.int/PSDB-portlet/download?file=updated_nea.lst ; `...?file=neo_kc.cat` (partial) ; `...?file=2022OB5.ke1`
- Changelog: https://neo.ssa.esa.int/system-status
- Terms: https://neo.ssa.esa.int/terms-conditions ; https://www.esa.int/Services/Terms_and_conditions
