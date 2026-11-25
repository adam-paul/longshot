# Operations review: keeping longshot running, alone, for five years

Written 2026-11-24. A review of `docs/plan.md` and `DESIGN.md` from the seat of the one person who has to keep the thing alive. It chooses no web framework, server language or host for the app; where a choice is needed it says what the choice depends on.

How to read the evidence: "my test today" is something I ran on this machine or one request I made today; "read today" is a page I fetched today; "research, 21 Nov" is from the earlier reports and was not re-read; "my estimate" is a judgement with no measurement behind it. No request went to a JPL API endpoint; JPL figures come from the two local snapshots and from JPL's documentation pages.

## Bottom line

1. **The data is small and it moves slowly, except for one thing that is lost every day it is not saved.** Two requests a day to JPL capture everything fast-moving. Stored compressed, that is 2.6 MB a day and under 5 GB in five years (my test today). JPL's lists show only the current state, so each day's version exists once. The record of predictions depends on being able to show what was known on a given date. Collecting is the only part of this project where waiting costs something that cannot be bought back.
2. **Nothing is backed up.** The repository has no remote, no scheduled backup is configured on this machine, and the plan, the research, the 570 MB evidence archive and both snapshots sit on one disk (my test today).
3. **The workstation is not always on.** Over 41 days it was powered about 70% of the time. The plan's "weekly unattended refresh on this workstation" would fail silently in exactly the way an earlier reviewer warned about.
4. **Daily, not weekly.** JPL recomputes the reachable list daily, and its window fields are relative to the day it computed them. A table three days old had 11% of its "open now" windows wrong; ten days old, 17% (my test today). The plan's idea that the page can work out "open now" from stored dates does not hold.
5. **Split the scheduled work into three loops with different rules**: collect (daily, automatic, never stops, no model), derive and release a data refresh (automatic, guarded, method frozen), and method release (by hand, expert read, deposit). A missed collect is a permanent hole. A missed derive is a delay.
6. **"Not static" does not have to mean accounts.** The duties of a public service come almost entirely from the write path and from personal data. A read-only service over a versioned data set has close to none. Whether visitors' predictions are public and scored is the one product decision that sets the operating cost.
7. **Money is not the constraint.** The first three months cost $0–1 a month. Year two costs about $15–110 a year depending on the serving shape. Attention is the constraint, and the design should be judged by how many things can page one person.

## What I measured today

| Measurement | Result | Consequence |
|---|---|---|
| Raw bytes of the two pulls where nothing changed | Differ. JPL returns each record's keys in a different order per pull; row order was the same. 7,007 of 7,229 reachable rows are identical once parsed. | A hash of the raw file cannot say "unchanged". Change detection must parse, sort keys and compare. Raw bytes are still kept as the evidence. |
| Dates in the responses | None. No ETag, no Last-Modified, no data date in the body. NHATS `count` is a string (`'7231'`), SBDB's is an integer. | "Pull only what changed" is not possible for the bulk lists. The as-of date is the pull time. The validator must not assume types. |
| What the 222 changed reachable rows were | 171 changed only in window start or window brightness. 51 changed in anything else (19 window end only, 23 with a new orbit solution, 7 delta-v, 4 H). | Most of the "change" is the same window re-dated. A digest built on a naive diff would report about 220 changes every few days and stop being read. |
| Window start | On 21 Nov, 212 windows started "2026-11-21". On 24 Nov no window was open; 206 started "2026-11-27". | Window start is "next usable date from the day JPL ran", not a property of the object. The gap fits JPL's rule of dropping four days around full moon (research, 21 Nov, from JPL's observability page); full moon fell on about 24 Nov by my arithmetic. The API page does not define the field (read today). |
| Window brightness | For 110 objects with the same window end, the listed peak got fainter by a median 0.25 mag, up to 1.52; 26 by more than 0.5. | It is the peak over what is left of the window. A stored value overstates how bright a fading object still is. |
| A stale table's "open now" | Of 212 open on 21 Nov, closed after 1 day: 2. After 3 days: 24 (11%). 10 days: 36 (17%). 30 days: 90 (42%). | The plan's ten-day banner tolerates one "open now" in six being wrong. |
| H in JPL's full table | Changed for 37 objects in 3.4 days. | H alone sets the price tag for an unobserved object (a factor of four per magnitude), so the tag is a moving number and needs its own as-of date. |
| Physical fields | Non-null counts identical across pulls: diameter 1,266, albedo 1,209, rotation period 2,189, class 313 and 37, A1 69, A2 680. | A fall in any of these between two days is almost certainly a fault, not news. That is a cheap, sharp guard. |
| Identity | Every reachable designation joins to the full table (7,231 of 7,231). The full-table snapshot has no `spkid` column. | The plan's internal key is JPL's permanent id. The bulk query offers `spkid` and `soln_date` (read today); the first automated pull should ask for both. |
| Storage | 18.4 MB a day raw; 2.57 MB with xz; 0.94 GB a year; 4.7 GB in five years. | Keep every day's raw response whole. No delta scheme is needed. |
| Workstation uptime, 14 Oct to 24 Nov | 23 boots, powered 70%, 15 gaps over an hour, longest 6.3 days. On at 03:00 on 23 of 42 days. | A night-time timer would have fired on about half the days. A catch-up-on-boot timer would still have missed five days. |
| Backups on this machine | No git remote. No crontab. no backup tool configured. No restic or rclone configuration. One NVMe drive. | I looked in the usual places only; a backup made some other way would not show. |
| SsODNet bulk file (one HEAD request) | `Last-Modified: 22 Sep 2026`, an ETag, `Accept-Ranges: bytes`. | Unlike JPL, a cheap weekly check can tell when a new build exists, and the slow download can resume. The build has not changed in two months. |
| SsODNet card for Bennu (one request) | No cache headers; body carries `datetime 2026-09-14` and `version 1.2.4`. | The card dates itself. Monthly is frequent enough. |

The snapshot rows above are reproduced by the script in the appendix, which reads only `data/snapshots/`. The appendix is the copy to keep until these checks become the collector's first tests; the same script is `repro.py` in `data/backbone-review-2026-11-24.tar.zst`. The uptime and backup rows come from `journalctl --list-boots`, `.git/config`, `crontab -l`, `gsettings get org.gnome.DejaDup periodic` and `lsblk`.

## 0. The plan, reviewed

What holds up and should stay: one module that may open a connection; every response written to a snapshot store; fits run by hand, off the scheduled loop; staging then promote; a release guard; the key is a permanent id and never a name; a cell is measured, looked-for-and-absent, or not checked; data out of git with manifests committed.

What I would change, each from a measurement above:

| Plan says | Change to | Why |
|---|---|---|
| Section 4: "A weekly unattended refresh on this workstation" | A daily collect that does not depend on the workstation being on | Uptime 70%, five dark days. JPL's list is recomputed daily ("the results of this daily analysis", CNEOS, read today), so daily matches upstream and is not redundant under JPL's fair-use wording. |
| Section 4: "pulls only what changed" | Always pull the two bulk lists whole; use the parsed diff to decide which per-object calls to make | No validators on the responses. About 7 reachable objects a day get a new orbit solution, so the per-object follow-up is under ten calls a day. |
| 5.3: "Day to day, with no rebuild: window tabs read 'open now' ... from stored dates" | Show the window as dated facts with the table's as-of date; say "open now" only when the table is under two days old | 11% wrong at three days. |
| Appendix B: "a banner when data are more than ten days old" | A freshness budget per source: windows 2 days, orbits and H 7 days, literature 90 days | One global number is too loose for windows and needlessly strict for a source whose build is two months old by design. |
| Appendix B: "Data. Outside git, content-addressed, backed up" | Raw responses stored by date and source, whole, compressed; content-addressing only for derived artefacts | Key order shuffles, so raw content hashes never repeat. At 2.6 MB a day there is nothing to deduplicate. "Backed up" currently describes nothing. |
| Appendix B: "a DOI per method release and per frozen forecast" | One deposit per freeze, holding every forecast and the input manifest | Zenodo counts uploading a very large number of records, whatever their size, as not fair use (read today). A record per forecast per object would be thousands. |
| Two jobs (weekly refresh; fits by hand) | Three loops: collect, derive, method release | The refresh mixes a step that must never be skipped with a step that should stop whenever a guard trips. |
| An earlier reviewer's guard: counts within −0.5% and +2% of the last release | Per-day tolerances, set from the first month of daily pulls and then frozen | −0.5% is 36 objects. Zero were removed in 3.4 days. One interval is not enough to set a number that gates releases. |

Two things the plan does not mention and should:

- **Metal prices are a feed too.** Every dollar figure moves 1.8 times between 2025 averages and 20 November 2026 prices (`DESIGN.md` section 7), and the one primary price source read so far was a dealer page after another failed to load (research, 21 Nov). Treat prices as a dated constant per method release, printed with its date, not as a daily input.
- **Each source adapter is a standing liability.** Appendix B expects about ten, "several with no stable machine route". On 20 November eight of the outside services had an access problem: down, slow, blocking scripts or serving an old version (research, `catalogs.md` section 2.4). My estimate is two to four hours a year for a stable adapter and more for a scraped one. The prototype should carry as few as it can.

## 1. Where the scheduled work can run

The work is tiny: two requests and about 18 MB a day, a few seconds of CPU. The orbit fitter is separate and is covered at the end of this section.

| | Owner's workstation | Scheduled job on a code host | Small rented server | Managed platform |
|---|---|---|---|---|
| Money | $0 | $0. GitHub Free includes $12 of compute a month for private repositories; a two-minute daily job is about $0.12–0.36. Public repositories are free on standard runners (read today). | $4–7 a month. DigitalOcean: $4 for 512 MiB and 10 GiB, $6 for 1 GiB and 25 GiB. Hetzner: €5.49–6.49 for 1 vCPU and 1 GB in Europe, €5.99 for 2 vCPU and 4 GB, €17.99 for the smallest US plan, all before VAT (read today). | $1–5 a month. Render: $1 minimum per cron job. Cloudflare Workers: free plan allows 10 ms of CPU per run, which cannot parse a 16 MB file; paid is $5 a month. Fly: $2.19 a month for an always-on 256 MB machine (read today). |
| Fails silently when | The machine is off (30% of the time, days at a stretch). An OS upgrade breaks the Python environment, as the 26.04 upgrade did. The disk dies. | The schedule is delayed or dropped: "some queued jobs may be dropped" under load. In a public repository the schedule is switched off after 60 days with no repository activity. Failure notices go only "to the user who last modified the cron syntax" (GitHub docs, read today). | The card on file expires. The disk fills. An unpatched service is taken over. A provider incident. | The free allowance or the price changes. The platform retires the product. The job outgrows a memory limit (128 MB per Worker). |
| Keeps data where | Local disk, so it also needs an off-machine copy | Nowhere: runners are wiped. Needs a bucket. Project rule keeps data out of git. | Local disk plus a bucket | Mostly nowhere (Render cron jobs "can't provision or access a persistent disk"). Needs a bucket. |
| Secrets | A mode-600 environment file outside the repository, loaded by the timer unit | The host's encrypted secrets. Log redaction "is not guaranteed" (read today). | A root-owned environment file. The server itself is now something to secure. | The platform's secret store |
| Standing chores | None beyond what the desk already needs | Almost none | Security updates, reboots, key rotation, renewals | Reading the platform's change notices |
| Also good for | Fits, development, a second copy of the store | Tests on committed fixtures | Serving the site later, if that is the direction | Serving the site later, if that is the direction |

Notes on the table:

- The Hetzner pages marked every plan "currently unavailable" when fetched. I could not tell whether that is a real shortage or the page failing to load stock without a script.
- The 60-day rule is documented for public repositories. The repository is due to go public at the launch, and a quiet public repository is exactly the "leave it for three months" case. A collector that lives on a code host should sit in its own private repository, or have a second trigger.
- Shared runners share outbound addresses with other tenants. JPL "may rate-limit, throttle, or block access" (read today). Whether it blocks by address I do not know.
- User-level timers already survive logout on this machine (`Linger=yes`), and a timer with `Persistent=true` runs a missed job at the next boot (systemd manual, read today).

**What this adds up to.** No single place is reliable enough alone, and the job is cheap enough to have two triggers. Make the collector idempotent and make the store the source of truth: "is there a good snapshot for today?" One trigger is the primary. The other runs later in the day and pulls only if today's snapshot is missing, which keeps JPL at two requests a day and never two at once. A dead-man's switch watches the store, not either trigger (section 3). Which place is primary is a small decision that can be reversed in an afternoon, because the collector is one script and three environment variables.

**The orbit fitter.** GRSS needs a 5.3 GB environment, downloads 4.3 GB on first import, peaks at 7.3 GB of memory, and opens connections on every import (research, 21 Nov). It runs by hand per method release, for tens of core-hours. It belongs on the workstation and nowhere else: a hosted runner has 14 GB of disk and 8–16 GB of memory (read today), so it would fit, but it would re-download the kernels on every run and there is no reason to pay that. What matters operationally is that the fitter never shares an environment with the daily loop. Three separately locked environments: the collector with no dependencies beyond the standard library, the pipeline, and the fitter behind its subprocess boundary. Then nothing the fitter drags in can stop the daily pull. The kernels are public and can be re-downloaded, so they are not backed up; their hashes go in the manifest of every fit.

**The contact address.** JPL requires "a valid, application-specific User-Agent request header that includes correct product name, version, and contact information" (read today), and the repository rule is no automated JPL call until one exists. This is the smallest decision with the largest unblock. It should be a role address that forwards to an inbox the owner reads, for three reasons: JPL's policy says to contact them if a block affects legitimate use, so this address is how a block gets resolved; the same address serves the "tell us what we missed" line that section 5 needs; and accounts opened under a role address can be handed over. A forwarding alias on a domain costs about $12 a year for the domain ($11.81 for a .com at one registrar, read today) and nothing for forwarding at at least one DNS host (Cloudflare lists Email Routing on its free plan, read today). An alias on a domain he already owns costs nothing. Kept in an environment variable, it never appears in the repository.

## 2. Serving

### What a stateful public service commits one person to

| Duty | Read-only service | Plus a write path, no accounts | Plus accounts |
|---|---|---|---|
| Uptime | Down means down; nothing is lost | Down means submissions are lost unless the page retries | Same, plus sign-in |
| Backups | None. The service holds nothing that is not rebuilt from the data set. | The visitor store is irreplaceable from its first row. Backups and a restore drill from day one. | Same, plus credentials |
| Abuse | Scraping. The licence rule already requires that the whole data set is never handed out, so rate limits and caching are needed anyway. | Spam and stuffing. Free text needs moderation; structured input (pick an outcome, give a probability) does not. | Account takeover, fake accounts |
| Personal data | Whatever the host logs | None if the store holds only a random token and the prediction, and no address log is joined to it | Email addresses at the least: deletion requests, breach notices, a privacy notice, password resets that need outbound mail |
| Patching | A process exposed to the internet, forever | Same, with a larger surface | Same, larger again |
| Billing risk | A usage-priced host turns a scraper into a bill. A flat price or a hard cap is safer for one person. | Same | Same |

On data protection, briefly and not as legal advice. The EU regulation reaches a controller outside the Union when processing relates to "the offering of goods or services, irrespective of whether a payment of the data subject is required" to people in the Union; "mere accessibility" of a site is not enough to show that intention (GDPR Article 3 and Recital 23, read today). California's law applies to for-profit businesses over thresholds such as $25 million in revenue or 100,000 residents' data (Attorney General's page, read today). A hobby site that keeps no personal data is outside most of this. A site that keeps email addresses for an international community is not obviously outside it. The cheap answer is to keep none: no accounts, no email, no names, no third-party scripts (the design already rules out web fonts), and no analytics that set identifiers.

### One fact that constrains "state in the browser"

Safari deletes "all of a website's script-writable storage after seven days of Safari use without user interaction on the site" (WebKit, read today). The record's predictions resolve between late 2027 and 2030. So browser storage is fine for the view, filters and selections, and cannot hold a prediction for a year. A visitor's prediction that has to survive needs to live in something the visitor keeps (a link or a file that encodes it) or on the server.

### What "not hosting a bunch of static data" could mean

It could mean three different things, and they have different answers:

1. **Not a frozen export that rots.** The data must refresh without him. Every shape below satisfies this; it is a property of the collect and derive loops, not of how pages are served.
2. **Not thousands of generated files as the product.** He wants a database that is queried, and pages made on request. That is shape B.
3. **Not holding copies of upstream data at all.** This one is not available. JPL forbids embedding its interface in a site and allows one request at a time, so visitors cannot be served from JPL. And the record needs dated history that JPL does not keep. The copy he must hold is small: 2.6 MB a day.

### The honest options between "files on a CDN" and "live proxy"

| Shape | What it is | Duties | Fits when |
|---|---|---|---|
| A. Generated files, regenerated on a schedule | Static to the host, not static in content. Interaction and state live in the page. | Nearly none | State is only the view and private, short-lived choices |
| B. Read-only service over a versioned data set | The pipeline publishes data set version N as one artefact; the service opens it read-only; a release is an atomic swap and a rollback is a swap back. Pages and queries are made on request, so the as-of date and window wording are always computed at the moment of viewing. | A process to keep up and patch; nothing to back up | He wants queries and request-time pages, and no visitor data on the server |
| C. B plus a small write path | A second, separate, append-only store for visitors' predictions, keyed by a random token. No accounts, no free text. A lighter variant stores only a hash and a timestamp, and the visitor keeps the prediction itself as a link: the server can later confirm it was made before the answer, and holds nothing readable. | B plus backups, rate limits and a short privacy note | Visitors' predictions must outlive a browser, or be compared in public |
| D. C plus accounts | Sign-in, profiles, recovery | Everything in the table above | Only if identity across devices is the point |
| E. Live proxy to upstream | Ruled out by JPL's terms, and it would make JPL's outages the site's outages | n/a | Never |

A sixth shape, shipping a whole database file to the browser and querying it there, is ruled out by the licence classes: several sources may be shown one value at a time and not redistributed in bulk.

What the choice between A, B and C depends on, in the order I would ask:

- Are visitors' predictions public and scored against each other, private to the visitor, or absent? Public needs C. Private can be a link the visitor keeps, on A or B.
- Does the field of 7,231 asteroids need server-side queries? It does not need them for size: delta-v, H and a state flag for every object is a few hundred kilobytes of the project's own and JPL's public fields.
- Is he willing to run a process at all, and where? If a small server exists anyway, it can run the collector too, and B costs nothing extra.
- His own opinions on the stack, which have not been asked for.

Whatever the shape, two rules keep the serving side disposable: the app takes every scientific value from the data set and computes none (already in `DESIGN.md` section 8), and visitor state, if any, lives in a separate store that the data release never touches.

## 3. Monitoring and alarms one person will read

The rule: silence when things are fine, one routine message a week, and a short list of things allowed to interrupt.

- **Dead-man's switch on the store.** The collector pings a check after it has verified that a good snapshot for today exists. No ping within 36 hours raises an alert. A free plan covers 20 checks (healthchecks.io, read today). There is no daily "all good" email; those are filtered and forgotten within a month.
- **A snapshot is good only if** the status is 200, the body parses, there is no `error` key (JPL documents 200 responses that carry an error message, read today), `signature.version` matches the expected value (NHATS 1.3, SBDB query 1.0 in both snapshots), the field list is unchanged, the count equals the number of rows, the count is within tolerance of yesterday's, and a handful of canary objects are present with their known values (Eros in the full table, Bennu and Apophis on the reachable list). A pull that fails any test is kept in a quarantine folder and the source stays on its last good snapshot.
- **Stale-data banner, computed at viewing time** from the as-of dates inside the data set, against the budgets in section 0. It must not depend on any job running, because its purpose is to be true when every job is dead. If the owner disappears for a year, the site says so by itself.
- **Holds.** A source hold: the snapshot was rejected, the site carries on with the last good one and shows its age. A release hold: the data set was built and not promoted, because counts moved outside tolerance, a measured value disappeared, a non-null count fell, or a fixture changed. Holds never clear themselves and never get loosened by an agent; that rule is already in `AGENTS.md`.
- **Weekly digest, one message.** Objects added and removed. Values that became measured, which is the actual news. Real orbit and delta-v changes, from the parsed diff with window re-dating filtered out. Windows opening in the next 30 days under 6 km/s (13 today, my test). Each source's age. Open holds. Store size. Date of the last restore drill. The plan's front page wants "what changed this week"; the same generator should produce both, so the digest is not a second thing to maintain.
- **Allowed to interrupt:** no good snapshot in 36 hours; a canary or schema failure; a release hold; a failed backup check; a domain or certificate within 30 days of expiry; any error on the write path, once there is one.
- **Two free signals from JPL itself.** CNEOS runs a "NHATS email daily notification service" and SSD runs an `ssd-announce` list for "significant changes" to its services, a message every few months (both read today). Subscribing means sending one email to JPL's list server, which is the owner's call under the no-outside-contact rule.

Proposed starting tolerances, to be replaced after a month of daily pulls and then frozen by the owner: hold if the reachable count falls by more than 5 or rises by more than 40 in a day; hold if any physical non-null count falls at all.

## 4. Backups and recovery

| Irreplaceable | Why | Where it should live |
|---|---|---|
| Raw upstream responses, by date | JPL's lists show only the current state, and I found no way to ask for an earlier one. Whether SsODNet keeps old builds I did not check; assume not. | A bucket with a lock rule that forbids delete and overwrite, plus a mirror on the workstation |
| Frozen forecasts, their input manifests, and the deposit receipts | The record is worthless if a forecast could have been edited | Git, the locked bucket, and an outside deposit that gives a date nobody here controls |
| Hand-kept files: resolution records, thresholds, the errata log, mission dates | Human judgement, not derivable | Git, with a remote |
| Visitor state, if the server ever holds any | Cannot be asked for again | Its own store, with its own backup and drill |
| The 21 November research archive | Holds responses and downloads as of that week | One more copy off this disk |

| Rebuildable | From what |
|---|---|
| Every derived data set version | Raw snapshots, the code at a commit, a lockfile |
| The site | A data set version and the app |
| Fit outputs | Observation snapshots, configuration, the pinned fitter; tens of core-hours |
| The fitter's 5 GB environment | Public kernels; keep hashes only |
| Secrets | Re-issued; the runbook says where each one comes from |

Costs: Cloudflare R2 is $0.015 per GB-month with 10 GB free and locks by prefix; Backblaze B2 is $6.95 per TB-month with 10 GB free (both read today). Five years of raw snapshots fit inside either free allowance. R2's page does not say whether locks are available on the free tier.

Recovery only counts if it is rehearsed. The drill, once a quarter: on a clean checkout, pull the store, rebuild the current release from raw snapshots, and compare hashes with what is being served. That requires the build to be deterministic (sorted keys, no clock inside the artefact, pinned dependencies), which is worth deciding on day one because it is hard to add later. The same drill is the "come back after three months" procedure in section 6.

Target: lose at most one day of upstream history; rebuild the site within a day.

## 5. The cost of being wrong in public

Ranked by how likely and how damaging, for a site whose whole stance is honesty about what is known.

1. **A wrong "not measured".** Most likely and most corrosive. The research already found a published lightcurve that JPL's database does not show, a period missing from every database, and a literature service two months behind. Guards: a blank is allowed only when the run record shows that source was fetched successfully and the object was resolved in it; otherwise the cell is "not checked". Canaries per source. Every blank lists which sources were checked and when. A corrections address on every entry and a public, dated corrections log.
2. **A stale window.** Most frequent, and the one a stranger might act on with telescope time. Guards: daily pull; the window shown with its as-of date; "open now" only under two days of age; brightness labelled as the peak in the remaining window as of that date.
3. **A prediction scored against the wrong version.** Rare, and fatal to the record. Guards: a forecast is an immutable file with a hash, deposited outside before any resolving observation could exist; it is keyed by permanent id; the scoring script takes a forecast hash and a resolution record and refuses to score if any input snapshot is dated after the observation, or if the resolving value already appears in the forecast's inputs; the resolution record carries three dates (observed, published, first seen here). Run the whole freeze, resolve and score cycle once with a made-up resolution before the first real freeze.
4. **A value attached to the wrong object.** The research found one upstream (a kilometre-sized diameter on an H 22.7 object). Guards: joins by id only; a plausibility flag when a size and H disagree by more than the population allows.
5. **A bulk download that republishes a source that did not allow it.** Guard: a build-time check that anything downloadable contains only fields of the "redistributable" class.

Belongs in the first version, before any unlisted address: the four cell states with run records; canaries; as-of dates and age-gated wording; versioned releases with an atomic swap and a rollback; the release hold; the corrections address and log; the licence check. Does not belong in the first version: accounts, a write path, anything about high availability.

## 6. Bus factor and handover

The test: leave it for three months, come back, and be running in an afternoon.

What makes that true by construction:

- The collector keeps archiving whether or not anything else works. The three months are never lost; they are replayed.
- A tripped guard leaves the site on its last good release with an honest age on it. Nothing is published without passing the guards, so neglect produces staleness, not errors.
- Nothing scheduled depends on the fitter, the workstation alone, or a public repository's activity.

Documentation, all short:

- A one-page runbook: what runs where; how to tell it is alive; how to restart each loop; what each hold means and how to clear it; how to restore; where each secret is issued; how to shut the project down cleanly (a final deposit, and a site that says it is frozen).
- A yearly chores list: domain renewal and the card behind it; key rotation; re-reading JPL's fair-use page, since "API data formats can change without notice"; the Python version (3.12 reaches end of life in October 2028, recalled, not checked today); a fitter upgrade against the full fixture set; a review of the tolerances.
- Every account under the role address, so the project can be handed over or archived by someone else.

Tests that carry the knowledge:

- The ten fixture objects, offline, with golden outputs.
- A contract test per source against a recorded real response: fields, types, version. The two snapshots here are the first recordings.
- A property test: no combination of source failures can produce "not measured".
- A determinism test: the same inputs give the same bytes.
- A replay test: 90 archived days run through the pipeline from cold and arrive at the current release. This is the handover test and the restore drill at once.
- The scoring refusal test from section 5.
- A fake clock in every test that touches window wording or age banners. Date-dependent text is where a quiet project rots first.

## 7. Recommended operating shape

### First three months (nothing public)

- **Collect:** daily, two JPL bulk requests, with `spkid` and `soln_date` added to the full-table query. A weekly HEAD on SsODNet's bulk file and a card refresh when it changes. Two triggers in two places, the second pulling only if today's snapshot is missing.
- **Store:** one private bucket, raw responses under a locked prefix, mirrored to the workstation. The repository gets a private remote.
- **Watch:** one dead-man's switch; one weekly digest.
- **Derive:** on the workstation, offline, from the store. This is where the fixture slice and the prototype pipeline get built, as `AGENTS.md` already orders.
- **Serve:** nothing. No server, no site.
- **Money:** $0–1 a month. Up to $12 once, if the role address needs a new domain.
- **Attention (my estimate):** about a day of agent work to build and wire, an hour of the owner's for accounts, the address and secrets. Then five minutes a week reading the digest, unless something interrupts.

### Year two (public, the record running)

- **Collect:** unchanged. It should be the oldest, dullest code in the project.
- **Derive:** data refreshes build, pass the guards and promote themselves, with the method frozen. Method releases never promote themselves: by hand, expert read, deposit, as the plan says.
- **Serve:** the lowest shape that satisfies the answer on visitors' predictions. B or A by default; C only when that feature is decided; D only for a reason nobody has given yet.
- **Record:** forecasts bundled per freeze and deposited; the locked bucket holds the same files.
- **Quarterly:** the replay and restore drill, and a dependency bump against the fixtures.
- **Money:** about $12 a year for a domain, $0–7 a month for serving, under $1 a month for storage. $15–110 a year.
- **Attention (my estimate):** 10–15 minutes a week on the digest; about two hours a month on holds and broken sources once ten adapters exist; half a day a quarter on the drill and upgrades. Method releases are science work and are counted in the plan, not here.

## 8. The right first step

Three things, in this order. The first two need no design decision.

1. **Get the project off one disk today.** A private remote for the repository; one off-machine copy of `data/`. An hour.
2. **Decide the contact address.** Five minutes if it is an alias on a domain he owns. It unblocks every automated call and is needed again for corrections and for holding accounts.
3. **Build the collector and its store, and switch it on.** One module, standard library only, about two hundred lines: pull, validate, write raw plus a manifest, write a parsed diff, ping the switch, and once a week send the digest. It can be written and tested today with no network, by replaying the two snapshots as recorded responses. It is the "one module that may open a connection" that the repository rules already call for, built first.

Why this before the fixture slice or the stack question: it is the only part where delay loses something for good; it depends on no decision about the app; and a month of its output answers the owner's actual question, how dynamic the data really is and what breaks, with a daily series in place of one 3.4-day interval. It also produces the numbers the release guard needs before those numbers are frozen. The fixture slice and the stack conversation proceed in parallel and lose nothing by it.

## Questions for the owner

1. What does "not static" mean to you: data that refreshes itself, pages made on request from a database, or holding no copy of upstream data? The third is not possible; the first two are both cheap.
2. Are visitors' own predictions public and compared, private to the visitor, or not in scope? This sets the operating cost more than any other choice.
3. Are you willing to run a process on a machine you patch, or should everything scheduled and served run on something you do not administer?
4. Which address goes in the User-Agent, and may it also be the public corrections address later?
5. Is there a backup of this workstation that I did not find?
6. May the collector subscribe the role address to JPL's two mailing lists?
7. Which code host and which storage provider do you already have accounts with? The figures here are GitHub's, Cloudflare's and Backblaze's because those are what I checked, not because they are chosen.

## Not verified

- Change rates rest on two pulls and one interval. Tolerances are placeholders until a month of pulls exists.
- That the window gap on 24 November is the full-moon rule is an inference. JPL's API page does not define `obs_start`, `obs_end` or `obs_mag`.
- Whether JPL blocks by address, and what it considers "unnecessarily frequent". Two requests a day seems well inside the wording; nobody has asked JPL.
- The bulk query documents a `full-prec` option (read today). Whether it restores the digits the research found missing from the push values was not tested, since no JPL call was allowed.
- That neither JPL list can be asked for an earlier state. I found no history parameter on the two documentation pages I read; I did not search further.
- Hetzner's "currently unavailable" on every plan.
- Whether R2 bucket locks and Backblaze's object lock are free.
- GitHub's 60-day rule is documented for public repositories; I did not test whether private ones are exempt in practice.
- The data-protection paragraph is a reading of two pages, not advice.
- Every attention figure is my estimate.

## Sources

Read today (2026-11-24) unless marked.

- JPL fair-use policy: https://ssd-api.jpl.nasa.gov/doc/
- NHATS API fields and response codes: https://ssd-api.jpl.nasa.gov/doc/nhats.html
- SBDB query fields (`spkid`, `soln_date`, `full-prec`): https://ssd-api.jpl.nasa.gov/doc/sbdb_query.html
- NHATS daily processing: https://cneos.jpl.nasa.gov/nhats/intro.html
- NHATS mailing lists: https://cneos.jpl.nasa.gov/nhats/subscribe.html
- SSD announcements list: https://ssd.jpl.nasa.gov/email_list.html ; example announcement https://ssd.jpl.nasa.gov/announcements/an20250929.html
- JPL observability rules (research, 21 Nov, not re-read): https://cneos.jpl.nasa.gov/nhats/obs.html
- SsODNet bulk file and card (one request each, my test): https://ssp.imcce.fr/data/ssoBFT-latest_Asteroid.parquet ; https://ssp.imcce.fr/webservices/ssodnet/api/ssocard/Bennu
- GitHub scheduled workflows: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
- GitHub Actions billing: https://docs.github.com/en/billing/concepts/product-billing/github-actions
- GitHub runner sizes: https://docs.github.com/en/actions/reference/runners/github-hosted-runners
- GitHub Actions limits: https://docs.github.com/en/actions/reference/limits
- GitHub secrets: https://docs.github.com/en/actions/concepts/security/secrets
- DigitalOcean droplets: https://www.digitalocean.com/pricing/droplets
- Hetzner cloud: https://www.hetzner.com/cloud/regular-performance/ ; https://www.hetzner.com/cloud/cost-optimized/
- Fly.io pricing: https://docs.fly.io/about/pricing
- Render cron jobs: https://render.com/docs/cronjobs
- Cloudflare Workers pricing and limits: https://developers.cloudflare.com/workers/platform/pricing/ ; https://developers.cloudflare.com/workers/platform/limits/
- Cloudflare R2 pricing and bucket locks: https://developers.cloudflare.com/r2/pricing/ ; https://developers.cloudflare.com/r2/buckets/bucket-locks/
- Backblaze B2 pricing: https://www.backblaze.com/cloud-storage/pricing
- healthchecks.io plans: https://healthchecks.io/pricing/
- Cloudflare Email Routing: https://developers.cloudflare.com/email-routing/
- .com price at one registrar: https://porkbun.com/tld/com
- systemd timers: https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html
- Zenodo limits and fair use: https://support.zenodo.org/help/en-gb/1-upload-deposit/80-what-are-the-size-limitations-of-zenodo
- Safari's seven-day storage cap: https://webkit.org/blog/10218/full-third-party-cookie-blocking-and-more/
- GDPR Article 3 and Recital 23: https://gdpr-info.eu/art-3-gdpr/ ; https://gdpr-info.eu/recitals/no-23/
- California Consumer Privacy Act scope: https://oag.ca.gov/privacy/ccpa
- Local evidence: `data/snapshots/2026-11-21` and `2026-11-24`; `journalctl --list-boots`; `.git/config`; `docs/research/verify-facts-venues.md` sections 9, 10 and 12; `catalogs.md` section 2.4; `orbit-tooling.md` section 1.1; `summaries-review.md` lines 154 and 228–234.

## Appendix: reproducing the snapshot measurements

Standard library only. Save as a file outside the repository and run it from the repository root with `python3 -I`. Output on 2026-11-24: 7,007 rows identical once parsed; 222 changed, 171 in window start or brightness only; of 212 windows open on 21 Nov, 2, 24, 36 and 90 closed after 1, 3, 10 and 30 days; earliest window start in the 24 Nov pull 2026-11-27; H changed for 37; no `spkid` column; non-null counts equal in both pulls; 2.57 MB a day with xz.

```python
# Run from the repository root: python3 -I repro.py
import json, lzma, datetime as dt
A, B = "data/snapshots/2026-11-21/", "data/snapshots/2026-11-24/"
raw = {p: open(p, "rb").read() for p in (A + "nhats.json", B + "nhats.json", A + "sbdb_neo.json", B + "sbdb_neo.json")}
na, nb, sa, sb = (json.loads(raw[p]) for p in raw)
J = lambda v: json.dumps(v, sort_keys=True)
ma = {r["des"]: r for r in na["data"]}; mb = {r["des"]: r for r in nb["data"]}
both = set(ma) & set(mb)
changed = {d: {k for k in ma[d] if J(ma[d][k]) != J(mb[d].get(k))} for d in both}
changed = {d: ks for d, ks in changed.items() if ks}
print("raw files equal:", raw[A + "nhats.json"] == raw[B + "nhats.json"], "| rows identical once parsed:", len(both) - len(changed))
print("changed rows:", len(changed), "| window start or brightness only:", sum(ks <= {"obs_start", "obs_mag"} for ks in changed.values()))
D = dt.date.fromisoformat; t0 = dt.date(2026, 11, 21)
opened = [r for r in ma.values() if r.get("obs_start") and D(r["obs_start"]) <= t0 <= D(r["obs_end"])]
for lag in (1, 3, 10, 30):
    print(f"open on 21 Nov: {len(opened)}; closed after {lag} d:", sum(D(r["obs_end"]) < t0 + dt.timedelta(days=lag) for r in opened))
print("earliest window start in the 24 Nov pull:", min(r["obs_start"] for r in mb.values() if r.get("obs_start")))
ix = {k: i for i, k in enumerate(sb["fields"])}
xa = {r[ix["pdes"]]: r for r in sa["data"]}; xb = {r[ix["pdes"]]: r for r in sb["data"]}
print("H changed:", sum(xa[d][ix["H"]] != xb[d][ix["H"]] for d in set(xa) & set(xb)), "| spkid column:", "spkid" in ix)
for k in ("diameter", "albedo", "rot_per", "spec_B", "spec_T", "A1", "A2"):
    print(" non-null", k, sum(r[ix[k]] is not None for r in xa.values()), sum(r[ix[k]] is not None for r in xb.values()))
print("reachable not in full table:", sum(d not in xb for d in mb), "| count types:", type(nb["count"]).__name__, type(sb["count"]).__name__)
x = sum(len(lzma.compress(raw[p])) for p in (B + "nhats.json", B + "sbdb_neo.json"))
print(f"xz per day {x/1e6:.2f} MB; per year {x*365/1e9:.2f} GB")
```
