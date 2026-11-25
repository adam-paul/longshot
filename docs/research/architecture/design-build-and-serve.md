# Design: build and serve

Written 2026-11-24 (my tests and web reads ran on 25 November UTC). Status: complete. Limits are in section 14.

A design for the data backbone of longshot. Its stance: separate the build from the service. A scheduled, deterministic build turns upstream data into versioned, immutable data sets. A small service reads the latest one and holds only what has to be live. Nothing here chooses the app's framework, server language or host; section 7.6 lists what that choice depends on.

Evidence tags:

- **[M]** my own test today on the two local JPL pulls (`data/snapshots/2026-11-21`, `/2026-11-24`). The appendix has the script or the method.
- **[D]** a page I read today through a summarising fetch. URLs are in Sources.
- **[C: file]** a finding from one of today's five colleague reports in this folder, not re-checked by me.
- **[E]** my estimate or inference.

No request went to a JPL API endpoint. I made no request to any other data service; I read seven documentation pages.

Words used with one meaning throughout:

- **Capture**: one upstream response, stored as received, with the request that produced it.
- **Archive**: every capture, plus a journal of every request attempt. Only ever added to.
- **Record**: a log of what this project decided and published. Only ever added to.
- **Store**: the pipeline's working database. Rebuilt from the archive and the record whenever needed.
- **Data state**: the store after a given accepted pull, named by a number and a hash.
- **Method**: the frozen science (priors, thresholds, presets, price scenario), a directory in git with a version.
- **Edition**: one immutable data set, built from one data state under one method. It is the only thing the app reads.
- **Service**: whatever serves the site. Not chosen.
- **Reachable list**: JPL's NHATS list. **Near-Earth table**: JPL's database of all near-Earth objects (SBDB).

## 1. The owner's questions, answered

| Question | Answer |
|---|---|
| "What kind of access we have to the APIs in a dynamic fashion" | None at page-view time, and none is needed. JPL's policy: "You may not embed these APIs in your website" and "submit only one API request at a time" [D]. No source offers a feed of changes or a "changed since" filter, and every source refreshes about once a day [C: upstream-orbits]. |
| "If the data can be updated on a regular basis with cron jobs" | Yes. Two requests a day fetch everything fast-moving for all 43,379 near-Earth objects. A full daily run is about 25 requests and 21 MB (section 4.2). |
| "Not looking to host a bunch of static data" | The project must hold its own copy: JPL forbids live use and keeps no history. The copy is rebuilt every day without a person, and the service on top can be as dynamic as he likes. What is immutable is each day's edition, and that is what makes a dynamic service safe to run alone. |
| "A serious project, not a snapshot in time" | Two things make it one. Every day's upstream state is kept, because it cannot be fetched later. And every number the site shows carries three stamps from which it can be rebuilt. |
| "What should our first step be" | Start the archive (section 11). It is the only work where a day's delay loses something for good. |

## 2. The shape

```
upstream --collect--> ARCHIVE --ingest--> STORE --build--> EDITION --publish--> current.json --> SERVICE
(network)             what they said      rebuildable      immutable                             reads one edition;
                                                                                                 owns the clock and
            RECORD: what we decided and published  <-- ingest, publish                           any visitor state
            git: code, source registry, method/ (frozen science), contract/
```

| Layer | Holds | Written by | Ever changed | If lost |
|---|---|---|---|---|
| Archive | Captures and the request journal | `collect` | No | Gone for good. Upstream keeps no history |
| Record | Accept and hold decisions, object keys minted, editions published, forecasts issued, outcomes confirmed | `ingest`, `publish`, a person | No | Gone for good |
| Store | Identity, upstream rows by version, coverage, claims | `ingest` | Only added to | Rebuilt by `replay` |
| Edition | What the app reads | `build` | No | Rebuilt by `build` |
| Service state | Visitor state, if any; which edition is current | The service | Yes | Its own backup; not the pipeline's concern |

Five rules:

1. **One direction.** The service has no code path to the archive, the store or any upstream. The build has no code path to visitor state.
2. **Two logs are the only irreplaceable data**: what upstream said (archive) and what we decided and published (record). Everything else is a function of those two and git.
3. **An edition is a pure function** of a data state, a method version, a schema version and a code commit. No network, no clock, no unseeded randomness.
4. **Only the service reads the clock.** Wording that depends on today's date is computed when a page is viewed, from dates stored in the edition.
5. **A failure before the edition can delay it. It cannot change what a published edition says.**

Where this departs from the plan and from the colleague reports:

- `plan.md` section 4 has a weekly refresh that "pulls only what changed" on the workstation. This design pulls both lists whole every day, anywhere a timer runs, and diffs locally. JPL sends no ETag or Last-Modified and shuffles key order between pulls [M].
- `review-data.md` keeps derived values in the store. Here derived values exist only in editions, so the store holds nothing but normalised upstream data and can always be rebuilt.
- Accept and hold decisions and minted object keys are written to the record, not re-decided on a rebuild. A guard tightened next year must not change what data state 412 was.

## 3. Storage

### 3.1 Files

```
longshot/                          the repository
  pipeline/collect/                the only code that imports a network library; standard library only
  pipeline/longshot/               ingest, build, publish, replay, digest; adapters/ one file per source
  registry/sources.toml            one entry per source (3.5)
  registry/properties.toml         property ids, units, value kinds, which entry row, clock-driven or not
  registry/annotations.toml        our notes on known-bad upstream values, matched on the raw value
  method/0.1/ ... + LOCK           frozen science; one directory and one git tag per version
  contract/schema-<n>.md           the edition contract (section 7); schema-0 is the first draft, before any method
  contract/kit/                    a fixture edition and the facts a front end must show from it
  ops/longshot-daily.{service,timer}, ops/runbook.md

data/                              outside git
  archive/journal.ndjson           one line per request attempt, successful or not
  archive/raw/<source>/<yyyy>/<mm>/<yyyymmddThhmmssZ>-<sha12>.json.xz
  record/record.ndjson             one line per decision or publication; each line carries the hash of the line before
  store/longshot.db                SQLite; deleted and rebuilt at will
  editions/<edition_id>/           manifest.json, page/*.ndjson.gz, open/*.ndjson.gz
  editions/current.json            the pointer the service follows
```

`archive/` and `record/` are mirrored off the machine under a rule that forbids delete and overwrite. Nothing is written to the system's temporary folder, which this workstation clears on reboot.

SQLite for the store is a proposal and needs the owner's yes. It is in Python's standard library, so it adds no package. The whole spine (collect, ingest, build, publish) needs no third-party package: `urllib`, `json`, `sqlite3`, `hashlib`, `lzma`, `tomllib`. The package list `AGENTS.md` asks for is only needed when the model stage starts.

### 3.2 The archive

A journal line, written after the capture file is safely on disk:

```json
{"seq": 1290, "source": "jpl.nhats", "scope": "all",
 "request": {"method": "GET", "url": "https://ssd-api.jpl.nasa.gov/nhats.api",
             "params": {"dv": "12", "dur": "450", "stay": "8", "launch": "2020-2045"}},
 "started_utc": "2026-12-20T10:00:38Z", "http_status": 200, "headers": {"date": "..."},
 "body_sha256": "3f9a...", "body_bytes": 2588379, "path": "raw/jpl.nhats/2026/12/20261220T100038Z-3f9a2c41d0aa.json.xz",
 "capture_check": "ok", "trigger": "primary", "collector": "0.1.0"}
```

- Every parameter is sent and stored, defaults included. The four values above are today's documented defaults [D]; the launch range has changed once before, in 2019 [D].
- `capture_check` is a shape test only: status 200, the body is JSON, it has a `data` list, the declared count equals the rows after a cast (the reachable list sends its count as a string [M]), and no error key. Values: `ok`, `suspect:<why>`, `failed:<why>`. A suspect body is still stored.
- `trigger` is `primary`, `backstop`, `manual` or `import`. The two existing pulls enter as `import`, with the first pull's time taken from its file timestamp and marked inferred.
- Paths are by source and UTC time. The folder now named `2026-11-24` holds a pull made on 25 November UTC [M].
- Compression is xz from the standard library: 2.57 MB a day for the two lists against 3.48 MB with gzip [M]. The hash is of the uncompressed bytes.

### 3.3 The record

One file, typed lines, each with a line number `n` and `prev`, the sha256 of the line before:

| `kind` | Written when | Fields that matter |
|---|---|---|
| `batch` | `ingest` accepts a capture | `batch_seq`, `fetch_seq`, `source`, `adapter`, `rows_sha256`, `state_hash` |
| `hold` | a guard fails | `fetch_seq`, `source`, `guard`, `report` |
| `release` | a person clears a hold | `fetch_seq`, `by`, `note` |
| `mint` | a new object key is issued | `object_id`, the alias that caused it, `batch_seq` |
| `merge`, `withdraw` | identity changes | both keys, the capture that is the evidence |
| `edition` | `publish` swaps the pointer, or rolls it back | `edition_id`, `manifest_sha256`, `action` |
| `issue` | a published edition changes a forecast for an object | `forecast_id`, `object_id`, probabilities, `inputs_sha256`, `edition_id` |
| `resolution` | a person confirms an outcome | question, object, outcome, the claim that settled it, three dates, `confirmed_by` |

`state_hash(N) = sha256(state_hash(N-1) + source + rows_sha256(N))`, where `rows_sha256` covers every row of the capture in sorted-key form. It commits to what upstream said, not to how an adapter read it, so a parser fix never changes a data state. The prototype computed four such states from the two pulls in under a second each [M].

### 3.4 The store

The tables follow `review-data.md` section 4.3, which I adopt with the changes marked. Its `statement` is called `claim` here, as in `review-extend.md`.

```sql
CREATE TABLE fetch (seq INTEGER PRIMARY KEY, source TEXT, scope TEXT, request TEXT, started_utc TEXT,
  http_status INTEGER, body_sha256 TEXT, body_bytes INTEGER, path TEXT, capture_check TEXT, trigger TEXT);
                                   -- an index of archive/journal.ndjson; the journal is the truth
CREATE TABLE batch (batch_seq INTEGER PRIMARY KEY, fetch_seq INTEGER, source TEXT, as_of_utc TEXT,
  adapter_version TEXT, rows_sha256 TEXT, state_hash TEXT);      -- one tick of the data-state clock
CREATE TABLE hold (fetch_seq INTEGER PRIMARY KEY, source TEXT, guard TEXT, report TEXT,
  opened_utc TEXT, released_utc TEXT, released_by TEXT, note TEXT);
CREATE TABLE object (object_id INTEGER PRIMARY KEY, minted_batch INTEGER, first_designated TEXT,
  lifecycle TEXT, merged_into INTEGER);   -- designated | numbered | missing_upstream | withdrawn | merged
CREATE TABLE alias (object_id INTEGER, scheme TEXT, value TEXT, normalized TEXT, source TEXT,
  is_primary INTEGER, first_batch INTEGER, closed_batch INTEGER);
                                   -- scheme: provisional | number | name | jpl.spkid | mpc.packed | ssodnet.id
CREATE UNIQUE INDEX alias_live ON alias(scheme, normalized) WHERE closed_batch IS NULL;
CREATE TABLE population (population_id TEXT PRIMARY KEY, rule TEXT, params TEXT, upstream_version TEXT);
CREATE TABLE membership (population_id TEXT, object_id INTEGER, first_batch INTEGER, closed_batch INTEGER);
CREATE TABLE source_row (source TEXT, object_id INTEGER, row_sha256 TEXT, row_json TEXT, upstream_date TEXT,
  first_batch INTEGER, closed_batch INTEGER, PRIMARY KEY (source, object_id, first_batch));
CREATE TABLE coverage (batch_seq INTEGER, source TEXT, object_id INTEGER,   -- 0 = the whole list was read
  outcome TEXT,                    -- answered | unknown_to_source.  There is no 'error' value: see section 5
  source_edition TEXT, source_edition_date TEXT, PRIMARY KEY (batch_seq, source, object_id));
CREATE TABLE window_episode (object_id INTEGER, episode INTEGER, first_seen_start TEXT, first_seen_batch INTEGER,
  jpl_start TEXT, end_date TEXT, peak_mag_first TEXT, peak_mag_last TEXT, orbit_id TEXT,
  last_seen_batch INTEGER, closed_batch INTEGER, close_reason TEXT,         -- ended | vanished | replaced
  PRIMARY KEY (object_id, episode));
CREATE TABLE claim (claim_id INTEGER PRIMARY KEY, object_id INTEGER, property TEXT, source TEXT,
  source_edition TEXT, origin_ref TEXT, value_raw TEXT, unit_raw TEXT, value_num REAL, value_text TEXT,
  bound TEXT, err_lo REAL, err_hi REAL, err_kind TEXT, qualifier TEXT, upstream_date TEXT, published TEXT,
  licence_class TEXT, embargo TEXT, first_batch INTEGER, closed_batch INTEGER, close_reason TEXT,
  adapter_version TEXT);           -- an index over source_row; dropped and rebuilt when an adapter changes
```

Points that differ from, or add to, `review-data.md`:

- **`object` covers all 43,379 near-Earth objects**, keyed by the project's own number. Keys are minted once and written to the record, so a rebuild reuses them and never mints again. "Reachable" is a row in `population` with JPL's rule and parameters. Two objects joined the reachable list in 3.4 days; one of them, 2026 VQ5, was already in the near-Earth table three days earlier [M], so it had a key before it had an entry.
- **`source_row` is the durable normalised layer; `claim` is an index over it.** Orbital elements live only in `source_row`. If an adapter misread a field, the fix rebuilds `claim` from `source_row`; nothing upstream said is lost.
- **`window_episode`** keeps the first start date ever seen for each observing window, because JPL rewrites it. The rule: a new row continues the same window if its start is not after the previous end; otherwise the old window closed. On the two pulls that rule sorts the 216 changed window starts into 192 re-dated and 24 closed [M].
- **No derived values.** Priors, probabilities, price ranges and rankings are computed by `build` and exist only in editions.

### 3.5 The source registry

`registry/sources.toml`, one entry per source and per release of a source, as `upstream-physical.md` and `review-extend.md` both ask:

```toml
[jpl.nhats]
kind = "bulk"                      # bulk | per_object | table | signal | own
url = "https://ssd-api.jpl.nasa.gov/nhats.api"
params = { dv = "12", dur = "450", stay = "8", launch = "2020-2045" }
change_signal = "content"          # header | body_field | content
expect_version = "1.3"
cadence = "daily"
stale_after_days = 2
min_interval_s = 2                 # and never two requests to one host at once
licence_class = "..."              # from plan.md Appendix B; not restated here
supplies = ["delta_v", "min_duration", "n_trajectories", "window", "radar_opportunity"]
clock_driven = ["obs_start", "obs_mag", "obs_end", "obs_flag", "radar_snr_a", "radar_obs_a", "radar_snr_g", "radar_obs_g"]
status = "live"                    # live | frozen | retired
```

`collect` reads it for what to fetch and how politely. `ingest` reads it for guards. `build` copies each source's freshness facts into the edition, and the service prints them. A static table from a paper is an entry of kind `table` plus a mapping file, not code.

### 3.6 Sizes

| Thing | Measured | Per year at that rate |
|---|---|---|
| Two JPL lists, raw | 18.4 MB a pull [M] | – |
| Same, in the archive | 2.57 MB a pull with xz [M] | 0.94 GB |
| Store, both lists, all 43,379 objects, two pulls | 52.9 MB [M] | – |
| Store growth | 0.50 MB over the 3.4 days [M] | about 55 MB |
| Edition, JPL sources only: 43,379 objects, 80,562 claims, 108,465 checks, 7,231 windows | 36.5 MB as text, 1.71 MB gzipped, built in 1.0 s [M] | 0.6 GB if every one were kept |
| One payload for the field of all reachable asteroids (key, name, delta-v, H, three flags) | 77 kB gzipped [M] | – |

The edition figures are from a throwaway prototype with no model stage; they will grow with sources and derived tables [E]. Nothing here is a storage problem at any size discussed.

## 4. Jobs and schedule

### 4.1 Commands

One command-line program, `longshot`, with one verb per stage. Each stage reads files or the store and writes files or the store, so each can be run and tested alone.

| Verb | Reads | Writes | Network | Clock |
|---|---|---|---|---|
| `collect` | registry, archive | archive | yes, the only one | yes, to stamp captures |
| `diff` | two captures | a report | no | no |
| `ingest` | archive, registry, record | store, record | no | no |
| `build` | store as of a batch, method, registry | an edition directory | no | no |
| `publish` | an edition, the previous edition | record, `current.json` | only to copy files, if the service is elsewhere | yes, to stamp the record line |
| `replay` | archive, record | a fresh store | no | no |
| `digest` | the `change` tables of the week's editions | one message | to send it | yes |

`collect` and the rest are separate environments. The collector has no dependency beyond the standard library, so nothing the model or the orbit fitter installs can stop the daily pull [C: review-ops].

### 4.2 The daily run

`longshot-daily.timer`, 10:00 UTC, with `Persistent=true` so a run missed while the machine was off fires at the next boot [D]. `OnCalendar` accepts the literal `UTC` [D]. The time is from `upstream-orbits.md`: late enough for JPL to have caught up with yesterday's Minor Planet Center circular, before today's at about 12:30 UTC. It is an assumption to confirm from the first week's counts of reachable rows that lag the table (16 and 17 in the two pulls [M]). A timer unit is the form the job takes on any Linux machine, this workstation included; on a hosted scheduler the same command runs from that scheduler. Where it runs is the owner's decision (section 13, item 2).

| Step | What | Requests | Download |
|---|---|---|---|
| 1 | `collect`: the reachable list and the near-Earth table, whole | 2 | 18.4 MB |
| 2 | `diff` against the last good captures; `ingest` | 0 | – |
| 3 | `collect`: JPL's single-object record for each reachable object that is new or has a new orbit solution. 23 in 3.4 days [M]; capped at 30 a day, the rest waits | 7–10 | under 0.1 MB [C: upstream-orbits] |
| 4 | `collect`: the Minor Planet Center identifier service, for designations that appeared or vanished | 0–1 | small |
| 5 | `collect`: ESA's change log, as a private cross-check on step 2 | 1 | 2.25 MB [C: upstream-orbits] |
| 6 | `collect`: change signals for slow sources: about ten HEAD requests, one SsODNet card for its build date, the arXiv listing | about 12 | under 0.5 MB [C: upstream-physical] |
| 7 | `ingest` the follow-ups; `build`; `publish` | 0 | – |
| 8 | Ping the dead-man's check, only after confirming today's captures are in the archive | 1 | – |

**A typical day: about 25 requests, 21 MB down, 3 MB added to the archive, a few seconds of computing.** JPL sees 9 to 12 requests, one at a time, at least two seconds apart.

- Step 3's list comes from `diff` on captures, not from the store. Collection never waits for anything downstream of the archive.
- `collect` is idempotent: before each request it asks the archive "is there a good capture of this source for this UTC day?" A second trigger elsewhere runs `collect --only-if-missing` six hours later. The archive, not either scheduler, decides.
- If `ingest`, `build` or `publish` fails, step 8 still pings when the captures are good, and raises a separate alert for the failure. A missed build is a delay. A missed capture is a hole.
- With `full-prec` and three more fields (`spkid`, `soln_date`, `source`) the near-Earth response will be larger than 15.8 MB. By how much is not known; no JPL call was allowed.

### 4.3 Other cadences

| When | What | Requests |
|---|---|---|
| Weekly | The whole reachable list through the identifier service, to catch objects withdrawn upstream that JPL still lists (2026 JG2 today [C: upstream-orbits]); JPL's radar table; `digest` | 73 + 1 |
| On a signal | SsODNet rebuilt: re-read its cards for the reachable list, on its own timer so it cannot delay the daily run. It has not rebuilt since 14 September [C: upstream-physical] | about 7,100, two hours at one a second |
| Monthly | Hash the upstream documentation pages; an agent proposes edits to the capability facts and a person approves | about 15 |
| Quarterly | `replay` from the off-machine copy and compare state hashes with the record | 0 |
| By hand | A method release; orbit fits; clearing a hold; confirming a forecast outcome | – |

### 4.4 Change detection

- Compare parsed rows with keys sorted, never response bytes. 0 of 7,229 reachable rows match as bytes between the pulls and 7,007 match once sorted [M].
- For the near-Earth table, a new orbit solution number is a complete key for orbit changes: all 342 changed rows have one [M]. Compare it as a number after stripping the `JPL ` prefix, and count the forms the parser does not recognise (21 on the list, 177 in the table [M]).
- Fields the registry marks `clock_driven` are stored and kept out of every change list. 192 of the 222 changed reachable rows changed only in window fields [M].
- The size of the real signal: 342 near-Earth rows in 3.36 days is 102 a day; ESA's log gives a median of 152, a 90th percentile of 255 and a maximum of 462 [C: upstream-orbits]. On the reachable list, 23 new orbits, 7 changed delta-v values and 4 changed H values in 3.4 days [M].

### 4.5 What happens when something breaks

| Event | What the pipeline does | What the site shows | Recovery |
|---|---|---|---|
| Machine off at 10:00 UTC | Timer fires at boot; the backstop trigger covers a whole day off | Yesterday's edition, with its date | None needed. With no backstop, a whole day off is a permanent one-day gap; this workstation was dark five whole days in the last 41 [C: review-ops] |
| Reboot during `collect` | The capture is written to a `.part` file, synced, renamed, and only then journalled. A `.part` file is swept at the next start | Unchanged | Rerun |
| Reboot during `ingest` | One SQLite transaction per batch; it rolls back | Unchanged | Rerun |
| Reboot during `build` or `publish` | The edition is built in a temporary directory and renamed; the pointer is replaced by rename | Unchanged | Rerun |
| JPL down, slow, or answering with an error page | Journal line `failed` or `suspect`; back off; two more tries 30 minutes apart; then the backstop. No batch, no coverage row | Yesterday's values with yesterday's date; a notice once a source passes its age limit | None |
| JPL changes a field name, a type, a unit or the version string | The capture is archived as usual. A guard fails at `ingest`: a source hold. Other sources carry on and editions keep building | That source's values, dated at the last good pull | Fix the adapter, add the capture as a test fixture, release the hold. Held captures are ingested in order, so the history has no gap |
| The meaning of a field changes with no change of shape | Caught only by range and median guards, canary objects and the monthly documentation hash | Possibly wrong values | See weaknesses |
| A day when everything is refitted | Follow-ups stay capped at 30; the release check holds the edition for a person. ESA refitted 46,027 entries on 30 July 2026 [C: upstream-orbits] | Yesterday's edition | A person looks and releases |
| A bad edition is published | – | – | `publish --rollback` writes the previous id to the pointer and a line to the record |
| The disk dies | – | The service keeps its last edition | Restore archive and record; `replay`; `build` |
| The owner is away three months | Captures and editions continue while guards pass. Holds never clear themselves | Dates age; notices appear with no job running | Read the holds; release or fix |

The orbit solution number is a format change happening now with no version bump: it appears as `49` and as `JPL 49`, and 20 objects flipped form between the pulls [C: review-data]. JPL's policy says formats "can change without notice" [D]. The archive-first order is what makes that survivable.

## 5. The three ledger states

`plan.md` Appendix B: each (object, property, source) is measured, looked for and absent, or not checked. Nothing in the plan stores the act of looking [C: review-data]. Here it is the `coverage` table, and the state is computed at build time, never stored.

```
cell(object, property, source) as of data state N:
  a live claim exists                                    -> value        (a measurement or a limit, by `bound`)
  else take the newest coverage row for (source, object) at or before N;
       for a bulk list, the row for the whole list
    there is none                                        -> not checked: never asked
    outcome is unknown_to_source                         -> not checked: source does not know the object
    the source's edition predates the object's designation -> not checked: source older than the object
    the check is older than the source's stale_after     -> not checked: stale
    otherwise                                            -> looked for and absent, with both dates
```

For a source that stamps its own build, such as SsODNet, a check stays fresh for as long as the daily signal confirms the build has not changed; its age is counted from the last such confirmation, not from the day the object's card was read.

Why an outage cannot show as "not measured":

1. A failed request writes a journal line and nothing else.
2. A held batch writes a record line and nothing else. No claim is closed and no coverage row is written.
3. So during an outage the newest coverage row is the last good one, and it only gets older. An outage can turn "absent" into "not checked: stale". It cannot turn anything into "absent".
4. A value can become "absent" only through an accepted batch in which the source answered and the value was gone. A guard holds any batch in which the count of filled values for a physical field falls; those counts were identical across the two pulls (1,266 diameters, 1,209 reflectivities, 2,189 periods [M]).
5. `publish` refuses an edition in which any cell became "absent" from a source with no accepted batch since the previous edition.
6. The tests in `review-data.md` section 5.3 damage a real pull thirteen ways, one at a time. Each asserts that no cell becomes "absent".
7. The service computes data-age notices when a page is viewed, from dates inside the edition. They stay true when every job is dead.

The four states an entry row shows (`DESIGN.md` section 3) are computed from the cells by a rule in the method, because "which sources must have answered" is a judgement:

```
any source has a value the rule accepts      -> measured, or limit; one claim leads, all are listed
else every source for that row is absent     -> guess, labelled "not measured", with the sources and dates
else                                         -> not checked, with which sources and why
```

The edition ships the row state and every cell behind it, so a page can print "no measurement in JPL (today) or SsODNet (build of 14 September); literature queue not run". SsODNet does not know at least 144 reachable asteroids first observed after its last build [C: upstream-physical]; under this rule their SsODNet cells read "not checked", which is correct.

## 6. Current data, frozen science

### 6.1 Three stamps

| Stamp | Example | Changes | Who changes it |
|---|---|---|---|
| Data state | `412`, with a chained hash | Every accepted batch, several a day | The timer, through the guards |
| Method version | `0.1`, a git tag and a hash of `method/0.1/` | At a gate: expert read, deposit | The owner |
| Schema version | `1` | When the contract's tables or columns change | The owner |

An edition id is the three together plus a rebuild count: `d000412.m0.1.s1.r1`. Every page footer prints the data date and the method version. Before any method exists the method stamp is `m0`: upstream values and states only.

### 6.2 The method

`method/0.1/` holds the prior tables by H band, the mission thresholds and presets, the row rules, the price scenario with its date, the list of references held back for the confirmatory test, and `LOCK`, a file of hashes. A test fails if a hash differs from `LOCK`; changing the science means a new directory and a new version. That turns the rule in `AGENTS.md` ("never change one, or the protocol, to pass a gate") into a two-file change anyone can see.

`build` applies the frozen method to the latest data state on every run. It tunes nothing. A new object gets its prior the day it appears. An object whose H moved gets the row of the frozen table its new H falls in. H changed for 37 objects in 3.4 days [M], so this happens daily. `plan.md` section 4 says "nothing with a model in it runs in the weekly loop"; the rule that works is narrower: nothing that fits or tunes runs unattended.

Derivations take their random seed from the object key, the method version and the property, so two builds give the same bytes.

### 6.3 Forecasts

- A **forecast rule** is part of a method release and is deposited with it: the question, the outcomes, the frozen probability table, what resolves it, the void date, the reference forecast.
- A **forecast issue** is what the site said about one object on one date: probabilities, the hash of the inputs, the edition. `publish` appends a record line only when that object's inputs changed. This is a primary record, not something to recompute.
- A **resolution** is appended by a person: the outcome, the claim that settled it, and three dates (observed, published, first seen here).
- A **score** is computed by `build` from the two. It takes the last issue whose data state is earlier than the earliest of the three dates. It refuses to score if there is none, or if the settling claim's reference is among that issue's inputs.

Old forecasts stay scorable because they are stored lines, not because old code still runs [C: review-extend]. Claims from held-back references are stored and dated but carry `embargo`, and `build` leaves them out of every derivation until the method releases them; the page shows "measured, held for the test".

### 6.4 Reproducing a number the site showed

1. The page shows the edition id.
2. The record has that edition's line with the hash of its manifest. The manifest names the data state and its hash, the method tag and its lock hash, the code commit and the hash of the lockfile.
3. If the edition's files are still kept, read the value. Editions referenced by a deposit, a forecast freeze or a correction are kept for good; others for 30 days.
4. Otherwise: check out the commit, `uv sync --frozen`, `longshot replay --to 412` (or query the existing store as of batch 412), `longshot build --batch 412 --method 0.1`.
5. Compare the table hashes with the manifest.

Two runs of the prototype in separate processes gave identical table hashes [M]. A test does steps 4 and 5 on every change to the pipeline.

## 7. The serving contract

### 7.1 What the service is given

A directory per edition and one pointer:

```
editions/d000412.m0.1.s1.r1/manifest.json
editions/d000412.m0.1.s1.r1/page/<table>.ndjson.gz     everything a page may show, one cited value at a time
editions/d000412.m0.1.s1.r1/open/<table>.ndjson.gz     only what may be redistributed, plus the project's own products
editions/current.json                                  {"edition_id": "...", "manifest_sha256": "..."}
```

```json
{"edition_id": "d000412.m0.1.s1.r1", "schema_version": "1.0",
 "data_state": {"batch_seq": 412, "state_hash": "...", "as_of_utc": "2026-12-20T10:00:52Z"},
 "method": {"version": "0.1", "tag": "method-0.1", "lock_sha256": "...", "deposit": null},
 "code": {"commit": "...", "uv_lock_sha256": "...", "adapters": {"jpl.nhats": "3", "jpl.sbdb_query": "2"}},
 "previous": {"edition_id": "d000410.m0.1.s1.r1", "manifest_sha256": "..."},
 "sources": [{"source": "jpl.nhats", "last_ok_check_utc": "2026-12-20T10:00:38Z", "last_change_utc": "...",
              "edition": "1.3", "edition_date": null, "stale_after_days": 2, "open_hold": false, "status": "live"},
             {"source": "ssodnet.ssocard", "edition": "1.2.4", "edition_date": "2026-09-14", "stale_after_days": 90, "...": "..."}],
 "views": {"page": {"claim": {"rows": 80562, "sha256": "..."}}, "open": {}},
 "counts": {"objects": 43379, "reachable": 7231}}
```

The manifest holds no build time, so the same inputs give the same manifest. The publish time is in the record.

### 7.2 Tables

A table is a text file of one JSON object per line, keys sorted, rows sorted by key. Its hash is of the uncompressed bytes.

| Table | One row per | Columns that matter | From |
|---|---|---|---|
| `object` | near-Earth object | `object_id`, `primary_designation`, `number`, `name`, `lifecycle` | first edition |
| `alias` | name any source has used | `normalized`, `scheme`, `object_id`, `is_primary` | first edition |
| `population`, `population_member` | named population; member | `population_id`, `rule`, `params`, `as_of_utc`; `object_id` | first edition |
| `property`, `state`, `source` | registry entry | ids, units, meanings, which entry row a property belongs to, `clock_driven` | first edition |
| `claim` | thing a source says | `object_id`, `property`, `source`, `origin_ref`, `value_raw`, `value_num`, `bound`, `err_lo`, `err_hi`, `err_kind`, `qualifier`, `source_edition_date`, `first_seen_utc`, `licence_class`, `held_for_test` | first edition |
| `check` | (object, property, source) | `outcome` (value, absent, not_checked), `reason`, `source_edition_date`, `last_ok_check_utc` | first edition |
| `window` | object with a listed window | `first_seen_start`, `jpl_start`, `end_date`, `peak_mag`, `flag`, `as_of_utc`, `orbit_id` | first edition |
| `change` | change since the previous edition | `object_id`, `kind`, `property`, `from`, `to`; clock-driven fields never appear | first edition |
| `field` | reachable object | `object_id`, delta-v, H, state flags; redistributable columns only | first edition |
| `row` | (object, entry row) | `state`, `lead_claim_id`, `lo`, `hi`, `unit`, `guess`, sources checked and not | method 0.1 |
| `ladder`, `elimination`, `observe_next`, `price` | rung; (object, mission type, preset); rank; (object, scenario) | states, probabilities, ranges, never a central value | method 0.1 |
| `preset`, `mission_type`, `scenario`, `fact` | registry entry; dated capability fact | thresholds; `as_of`, `last_checked` | method 0.1 |
| `forecast`, `forecast_issue`, `resolution`, `score` | rule; issue; outcome; score | as in 6.3 | the release that starts the record |

Dates sit on every `claim` and `check` row, so every table's hash changes daily even when little changed [M]. "What changed" is the `change` table, never a comparison of hashes.

### 7.3 Packing

The contract is the tables and the manifest. What the service physically opens is a *packing* of them, produced by a small step chosen together with the stack and checked against the manifest by exporting it back:

| Packing | Asks of the service | Gives | Costs |
|---|---|---|---|
| One SQLite file per edition, opened read-only | A runtime that can open SQLite, and a local disk | Queries at request time; a release is one file swapped. Two packs of the same tables were byte-identical on this machine [M]. SQLite documents its file format as stable and supported to 2050 [D] | A process to keep running |
| One document per object plus a few list payloads | Anything that serves files | No process | 7,231 or more files per edition; clock wording must run in the browser; the page view is exposed one file at a time and needs a rate limit somewhere |
| Loaded into the service's own database at publish | A database server | Science and visitor state in one query engine | A loader and a migration per schema change; a release is no longer a swap |

I do not choose one. The pipeline's work is the same for all three.

### 7.4 Publish and rollback

1. `build` writes the edition under a temporary name, checks it, renames it.
2. `publish` runs the release checks: the invariants of section 5; row counts against the previous edition; fixture facts; no restricted value in `open/`. Starting tolerances are placeholders from `review-ops.md` (hold if the reachable count falls by more than 5 or rises by more than 40 in a day; hold on any fall in a filled physical count), to be set from the first month of pulls and then frozen by the owner.
3. Pass: append the `edition` line to the record, copy the edition to where the service reads, then replace `current.json` last.
4. Fail: a release hold. The pointer does not move, an alert is raised, and nothing clears it but a person.
5. The service notices the pointer changed, checks the manifest hash, switches, and keeps the previous edition open. Rollback is the pointer written back, with a record line.

### 7.5 What the service must, may and may not do

Must:

- Take every scientific value from one edition, and print that edition's data date and method version.
- Compute, when a page is viewed: each source's age against `stale_after_days`, and window wording.
- Keep visitor state, if any, in its own store, referring to `object_id`, `forecast_id` and `edition_id`.
- Serve bulk downloads and any machine interface from `open/` only.

May: select, sort, filter and count exported rows; compare stored dates with the clock; apply a conversion the edition names, such as a unit.

May not: call an upstream; combine or derive a probability or a range; sum probabilities over a visitor's filter; write to an edition; hand out `page/` tables whole. Every filter combination the interface offers is an exported preset [C: review-extend].

One exception, only if visitors ever make scored predictions: the service applies one published scoring function to a visitor's prediction and the edition's `resolution` table, checked against test vectors in `contract/kit/`.

### 7.6 What is live, and what the stack choice depends on

Live in the service, and nowhere else:

- **Window wording.** JPL's start date for an open window is the next usable night from the day JPL ran, not the day the window opened: 187 objects moved from 21 to 27 November between the pulls, across the full moon [M; the cause is inferred, C: review-data]. So the service says "open now" or "next usable night 27 Nov" only when the reachable list's last good pull is under two days old, and otherwise prints the dated facts. Of 212 windows open at the first pull, 2 had ended a day later, 5 after two days and 24 after three [M].
- **Data-age notices**, per source, from the manifest.
- **Visitor state**, if the owner wants any.
- **Which edition is current.**

What the stack choice turns on. None of these is answered here:

1. Do visitors make predictions, and if so are they kept by the visitor (a link or a file) or stored and compared? Only the last needs a server-side write store. Safari deletes script-writable storage after seven days without a visit, so browser storage cannot hold a prediction that resolves in 2028 [C: review-ops].
2. Is history ("as of last March", an object's delta-v over time) queried on request, or written into each edition as a table?
3. Do the build and the service share a machine? If so the service opens `editions/` directly. If not, editions travel, and the service's freshness is the build machine's uptime.
4. Is clock wording computed on the server or in the browser? Either satisfies the contract.
5. Is the owner willing to run and patch a process?
6. The field of all reachable asteroids is one 77 kB payload [M]; it does not need a query engine for its size.

## 8. One person and coding agents

- **Stages with file inputs and outputs.** An agent works in one stage; the review is the change in that stage's output on the fixtures.
- **Tests that carry the rules.** The two pulls as golden fixtures, with the appendix script as the oracle. The thirteen single-fault mutations. Kill tests for the atomic writes. `replay` compared with the record. Build twice, compare hashes. An import check: only `pipeline/collect/` imports `urllib`, `http` or `socket`. The `LOCK` check. The scoring refusal. A conformance kit for any front end: a fixture edition for the ten objects in `plan.md` Appendix B and the facts each entry must show, including window wording under a fake clock.
- **What an agent may never do**: clear a hold, edit `method/*/LOCK`, edit or delete anything under `archive/` or `record/`, or loosen a guard to make a batch pass. The first three are also blocked by the off-machine lock.
- **What can interrupt the owner**: no good capture in 36 hours; a hold; a failed backup check. Everything else is the weekly digest, built from the `change` tables, which also feed the front page's "what changed this week" [C: review-ops].
- **Three environments**: the collector (no packages), the pipeline, the orbit fitter. The fitter stays on the workstation and off every timer.

## 9. Extension points

| To add | Touch | Do not touch |
|---|---|---|
| A source | A registry entry, an adapter (or a mapping file for a static table), one stored sample with its expected claims | Any table definition |
| A new release of a source (Gaia DR4 after DR3) | A registry entry; claims from both coexist | Old claims |
| A property | A row in `registry/properties.toml` | Schema |
| A mission type, a preset, a price scenario | A method entry and a minor method version | Code, unless the formula is new |
| A wider population (all near-Earth objects shown) | A `population` row; the objects already have keys | Identity |
| The project's own analyses (orbit refits, colours) | A source of kind `own`, carrying its method version; shown beside JPL's values | JPL's claims |
| A table in the edition | A minor schema version; a service ignores tables it does not know | Existing tables |
| A second front end, or a redesign | Pass `contract/kit/` | The pipeline |
| A different packing | A packer, verified against the manifest | The contract |
| Visitor predictions | A service-side store keyed by the public ids; the scoring exception | The pipeline |
| A second place to run `collect` | The same script with `--only-if-missing` | The archive layout |
| History views | A `history` table in the edition, or keep more editions | The store |
| Outside proof of dates | Deposit the record's latest line hash with each method release | The record format |

## 10. Not built yet

- The joint model, priors, elimination, "observe next", the price range. They are the prototype's science and come after the spine, as functions inside `build`.
- A live SsODNet crawl, the literature review queue, and adapters beyond JPL's two lists, the 1,704 SsODNet cards already on disk and one static table.
- The orbit fitter and everything in WP5.
- The app, and any packing, until the stack is chosen.
- A visitor-state store, accounts, comments.
- Forecast issues and scores. The record file and its line kinds exist from the first day; nothing writes `issue` lines until a method registers forecasts.
- A cache of derived values keyed by input hash. Needed only if the model makes a full rebuild slow.
- A workflow engine, a queue, plug-in discovery, an API layer, a DOI per edition, a retention policy for the archive.
- Display of the 36,000 near-Earth objects outside the reachable list. They are keyed and archived, not shown.

## 11. First step, and the first two weeks

### The first step: start the archive

Build `collect`, `diff` and the archive, offline, and prove them on the two pulls already on disk. Switch the timer on the day a contact address exists.

Done looks like this. Items 1–5 need no decision from the owner and no network.

1. `data/archive/` holds the two existing pulls as four captures with journal lines, imported by copying; the originals are untouched.
2. `longshot diff` on those captures prints the appendix numbers: 7,229 to 7,231 reachable with 2 added and 0 removed; 43,367 to 43,379 near-Earth; 342 near-Earth rows changed, all with a new orbit solution, none in a physical field; 222 reachable rows changed, 192 of them only in window fields and 23 with a new orbit; 16 then 17 reachable rows behind the table.
3. Damaged responses (cut short, an HTML page, a 200 that carries an error, a count that does not match, an empty list) are each archived and marked suspect, never good.
4. Killing `collect` mid-write and rerunning leaves no partial file and exactly one journal line per attempt.
5. A test proves only `pipeline/collect/` imports a network library.
6. With the address: the first live capture sends every parameter explicitly and adds `spkid`, `soln_date` and `source` to the near-Earth request, and `full-prec` after one by-hand comparison of the response size and of the digits it restores.
7. Seven consecutive UTC days each have a good capture of both lists; the dead-man's check has been pinged each day; `archive/` and `record/` have a copy off this machine.

What it leaves out on purpose: the store and its schema, object keys, claims, guards beyond the shape test, every other source, single-object calls, any model, any edition, any app. It shows nothing on a screen. Its output is a daily series in place of one 3.4-day interval, which is the evidence every later tolerance and schedule in this design is waiting for.

If the address takes more than a day or two, each day's pull can be made by hand through the same code path, as the two existing ones were. That is the owner's call under the repository's rule on JPL calls.

### The first two weeks

Agent-days are my estimates, in the plan's sense of a day.

1. **Day 0, the owner, about an hour.** Give the repository a private remote and put one copy of `data/` off this disk; nothing is backed up today [C: review-ops]. Choose the JPL contact address and product name.
2. **Days 1–2.** The first step above. Timer on.
3. **Days 2–5.** The store: `fetch`, `batch`, `hold`, `object` and `alias` for all 43,379, `population`, `membership`, `source_row`, `coverage`, `window_episode`; the record file; the guards of `review-data.md` section 5.1; `replay`. Acceptance: replaying the November captures reproduces the appendix numbers, and deleting the store and replaying gives the same state hashes.
4. **Days 4–7.** `contract/schema-0.md`, two pages, written before the code that fills it. `build` and `publish` for method `m0`: `object`, `alias`, `population`, `claim`, `check`, `window`, `change`, `field` and the registries, for both November data states and each new day. Acceptance: build twice, same hashes; a published edition rebuilt from its manifest matches.
5. **Days 6–9.** Two more sources from the research archive: the 1,704 SsODNet cards as one dated batch, and one static table through a mapping file. Acceptance: the ten fixture objects show the right state in every cell; the 5,527 reachable objects with no card read "not checked" for SsODNet; the thirteen mutations pass.
6. **Days 8–10.** The weekly digest, the dead-man's check, the one-page runbook, and the change signals of step 6 in section 4.2, logged only.
7. **Days 10–14.** Read the first ten or more daily diffs. Confirm or move the 10:00 UTC run time from the lag counts. Propose release tolerances for the owner to freeze. Then hold the stack conversation, with a daily-refreshing edition on disk, the contract, and the six questions of section 7.6.

After that the plan's own order resumes: the fixture slice through the model, then all reachable objects, as functions inside `build`.

## 12. Weaknesses

1. **The site is at most as fresh as the last build.** With a daily build and JPL's own day of lag on the reachable list, a change can take up to two days to appear. That is acceptable for orbits and sizes. It is the reason "open now" is gated by age.
2. **A correction waits for a build.** An edition cannot be patched. Fixing a wrong value means an annotation, a build and a publish: minutes when the build machine is up, and this workstation is up 70% of the time [C: review-ops].
3. **The boundary leaks in one place.** If visitors' predictions are scored, the service has to do arithmetic the build cannot do ahead of time (section 7.5). I have kept it to one function; it is still science running outside the build.
4. **Determinism is a discipline, and agents will break it**: dictionary order, float formatting, a library upgrade that changes random draws. The tests catch it on the day. They do not make a 2026 edition rebuildable in 2031 if its locked packages no longer install. Mitigation: editions that a deposit or a forecast depends on are kept as files, so rebuilding is a second proof and not the only one.
5. **An adapter fix rewrites the claim index for the past.** The data states do not change, and old editions rebuild at their own commit, but "what did we believe on that date" is answered by the record and kept editions, not by today's store.
6. **A change of meaning with no change of shape goes through.** If JPL silently changed a unit by a small factor, range and median guards might not trip. Canaries and the monthly documentation hash are thin protection.
7. **Four layers and seven verbs for one person.** A script that writes a JSON file would be a tenth of this. The extra is paid for by one requirement: forecasts frozen in advance and scored later. If the owner drops the record, the record file, the stamps and half the tests can go.
8. **Daily full rebuild.** It takes a second for JPL's tables [M]. Nobody knows what the joint model costs for 7,231 objects; if it is minutes the build is still fine, and if it is hours it needs the cache in section 10.
9. **Dates between deposits are self-attested.** The record's hash chain shows the file was not edited after the fact only to someone who saw an earlier hash. The off-machine lock and a deposit per method release are the outside witnesses, and they are sparse.
10. **Two hosts mean a transport nobody has designed.** If the build runs on the workstation and the service elsewhere, something copies editions out, and I have only said "pointer last".
11. **The evidence is thin.** Every rate rests on one 3.4-day interval plus ESA's log. The run time, the follow-up cap, the tolerances and the window rule are placeholders until a month of captures exists. The window rule has seen one full moon.
12. **The archive holds responses that may not be redistributed.** It and the store must stay private, and the service must never expose `page/` files directly. That is a rule the app has to keep, whatever it is built with.

## 13. Decisions for the owner

1. **The JPL contact address and product name.** Blocks all automated collection. JPL requires "a valid, application-specific User-Agent request header that includes correct product name, version, and contact information" [D].
2. **Where the timer runs, where a second trigger runs, and where alerts go.** The job needs a machine that is on every day, a disk that persists, and one JPL request at a time. Not tied to the app's host.
3. **Where `archive/` and `record/` are mirrored**, and a private remote for the repository.
4. **SQLite as the pipeline's working store.** No package; still a choice.
5. **The project's own object key for all 43,379 near-Earth objects**, with "reachable" as a named population, replacing "the internal key is JPL's permanent id" in `plan.md` Appendix B. That id is not in either pull [M].
6. **Visitors' predictions: none, kept by the visitor, or stored and compared.** This sets what the service must hold more than anything else.
7. **History: queried on request or written into each edition.**
8. **Does "no mean, median or expected value anywhere, the data files included" bind the edition's own tables?** It decides how a distribution is encoded.
9. **The row rule when a source has not been checked**: show "not checked" alone, or "not checked" with the population guess beneath it. The edition carries both either way.
10. **What happens to an object upstream has withdrawn but JPL still lists** (2026 JG2 today [C: upstream-orbits]).

Changes this design would make to the project's documents, for the owner to accept or not; I have edited none of them:

- `plan.md` section 4: daily, not weekly; pull whole and diff, not "only what changed"; "nothing that fits or tunes runs unattended"; three loops (collect, build and publish, method release).
- `plan.md` section 5.3: window wording is computed when viewed and gated by the table's age.
- `plan.md` Appendix B: identity; ledger cells backed by coverage; the release guard as source holds plus a release hold; data dates per source in place of one ten-day banner.
- `AGENTS.md`: "then all 7,229" becomes "then every reachable object in the data state"; the first thing built is the collector.
- `DESIGN.md` section 8: "a versioned data set with a schema" becomes the edition contract of section 7.

## 14. Not verified

- Any live JPL behaviour: the size of a full-precision response, whether `full-prec` restores the digits of the fitted push values, when the daily trajectory batch finishes, whether JPL's object id changes at numbering.
- That 10:00 UTC is the right hour. It is `upstream-orbits.md`'s proposal from a measured lag of "more than 12.7 hours".
- The window rule beyond these two pulls, and the full-moon explanation, which is inferred.
- That two SQLite packs are byte-identical across SQLite versions or machines. I tested one machine, SQLite 3.46.1.
- Every figure tagged [C]. I read the five reports; I did not repeat their requests.
- The prototype had no guards, no claims table in the store and no model. Its timings are floors.
- All effort figures are estimates.
- The documentation pages were read through a summarising fetch. Quoted words are as the fetch returned them.

## Sources

Read by me today (2026-11-24 local, 25 November UTC):

- JPL fair-use policy: https://ssd-api.jpl.nasa.gov/doc/
- JPL near-Earth table query (`fields`, `full-prec`, `spkid`, `soln_date`, `source`, version 1.0, error codes): https://ssd-api.jpl.nasa.gov/doc/sbdb_query.html
- JPL reachable list (parameters and defaults, version history, error codes): https://ssd-api.jpl.nasa.gov/doc/nhats.html
- systemd timers (`Persistent=`, a running unit is not restarted): https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html
- systemd calendar events (the `UTC` suffix): https://www.freedesktop.org/software/systemd/man/latest/systemd.time.html
- SQLite long-term support and file-format stability: https://www.sqlite.org/lts.html
- SQLite read-only and immutable open modes: https://www.sqlite.org/uri.html

Not read by me. Taken from the colleague reports of today, which say what they read and tested:

- `upstream-orbits.md`: the daily cadence of every source and the Minor Planet Center's Daily Orbit Update (https://www.minorplanetcenter.net/mpec/RecentMPECs.html); the identifier service, 100 designations a request (https://docs.minorplanetcenter.net/mpc-ops-docs/apis/query-identifier/); ESA's change log and its terms (https://neo.ssa.esa.int/PSDB-portlet/download?file=updated_nea.lst, https://neo.ssa.esa.int/terms-conditions); JPL's single-object record (https://ssd-api.jpl.nasa.gov/doc/sbdb.html); JPL's "daily analysis" (https://cneos.jpl.nasa.gov/nhats/intro.html); 2026 JG2.
- `upstream-physical.md`: SsODNet's build date and the 144 objects it cannot know (https://ssp.imcce.fr/webservices/ssodnet/api/ssocard/Bennu); the change signals for slow sources; the arXiv listing.
- `review-data.md`: the table definitions adopted in 3.4, the guards, the thirteen mutations, the orbit-number format flip; JPL's full-moon rule for windows (https://cneos.jpl.nasa.gov/nhats/obs.html).
- `review-ops.md`: workstation uptime, the absence of backups, the dead-man's check, the starting tolerances; Safari's seven-day storage rule (https://webkit.org/blog/10218/full-third-party-cookie-blocking-and-more/).
- `review-extend.md`: the may and may-not list for the app, exported presets, forecasts as stored records.

## Appendix: the tests behind the [M] numbers

### A. The oracle for `longshot diff`

Standard library only. Run from the repository root: `python3 -I backbone_check.py data/snapshots`. It is reproduced in full; a copy is `bs/backbone_check.py` in `data/backbone-review-2026-11-24.tar.zst`.

```python
import json, sys, re, datetime as dt
B = sys.argv[1].rstrip("/") + "/"
def load(d): return json.load(open(B + d + "/nhats.json")), json.load(open(B + d + "/sbdb_neo.json"))
(n1, s1), (n2, s2) = load("2026-11-21"), load("2026-11-24")
F = s1["fields"]; assert F == s2["fields"]
def flat(r):
    o = {}
    for k, v in r.items():
        if isinstance(v, dict): o.update({k + "." + kk: vv for kk, vv in v.items()})
        else: o[k] = v
    return o
canon = lambda o: json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
N1 = {r["des"]: flat(r) for r in n1["data"]}; N2 = {r["des"]: flat(r) for r in n2["data"]}
S1 = {r[1]: dict(zip(F, r)) for r in s1["data"]}; S2 = {r[1]: dict(zip(F, r)) for r in s2["data"]}
print("A reachable", len(N1), "->", len(N2), "added", sorted(set(N2) - set(N1)), "removed", sorted(set(N1) - set(N2)))
print("B near-Earth", len(S1), "->", len(S2), "added", len(set(S2) - set(S1)), "removed", len(set(S1) - set(S2)))
sc = {k: {f for f in F if S1[k][f] != S2[k][f]} for k in S1 if k in S2}; sc = {k: v for k, v in sc.items() if v}
PHYS = {"diameter", "diameter_sigma", "albedo", "rot_per", "GM", "density", "BV", "UB", "spec_B", "spec_T"}
print("C near-Earth rows changed", len(sc), "| new orbit_id", sum("orbit_id" in v for v in sc.values()), "| on the reachable list", sum(k in N2 for k in sc),
      "| physical values", sum(len(v & PHYS) for v in sc.values()), "| H", sum("H" in v for v in sc.values()))
nc = {k: {f for f in set(N1[k]) | set(N2[k]) if N1[k].get(f) != N2[k].get(f)} for k in N1 if k in N2}; nc = {k: v for k, v in nc.items() if v}
WIN = {"obs_start", "obs_end", "obs_mag", "obs_flag"}
print("D reachable rows changed", len(nc), "| identical once keys are sorted", sum(canon(N1[k]) == canon(N2[k]) for k in N1 if k in N2),
      "| only obs_start or obs_mag", sum(v <= {"obs_start", "obs_mag"} for v in nc.values()), "| only window fields", sum(v <= WIN for v in nc.values()),
      "| new orbit_id", sum("orbit_id" in v for v in nc.values()), "| delta-v", sum("min_dv.dv" in v for v in nc.values()), "| h", sum("h" in v for v in nc.values()))
num = lambda o: int(m.group(1)) if (m := re.fullmatch(r"(?:JPL )?(\d+)", o or "")) else None
for tag, N, S in (("pull 1", N1, S1), ("pull 2", N2, S2)):
    print("E", tag, "reachable rows on a different orbit number from the table",
          sum(num(N[k]["orbit_id"]) is not None and num(S[k]["orbit_id"]) is not None and num(N[k]["orbit_id"]) != num(S[k]["orbit_id"]) for k in N),
          "| orbit ids of an unknown shape (list, table)", sum(num(r["orbit_id"]) is None for r in N.values()), sum(num(r["orbit_id"]) is None for r in S.values()))
D = dt.date.fromisoformat; same = closed = 0
for k in nc:
    a, b = N1[k], N2[k]
    if (a["obs_start"], a["obs_end"]) == (b["obs_start"], b["obs_end"]) or a["obs_start"] is None: continue
    if b["obs_start"] is not None and D(b["obs_start"]) <= D(a["obs_end"]): same += 1
    else: closed += 1
print("F window rule (same window if the new start is not after the old end): same window re-dated", same, "| window closed", closed)
P1 = dt.date(2026, 11, 21); op = [r for r in N1.values() if r["obs_start"] and D(r["obs_start"]) <= P1 <= D(r["obs_end"])]
print("G open at pull 1", len(op), "| ended 1, 2, 3 days later", [sum(D(r["obs_end"]) < P1 + dt.timedelta(days=x) for r in op) for x in (1, 2, 3)],
      "| open at pull 2 by JPL's dates", sum(bool(r["obs_start"]) and D(r["obs_start"]) <= dt.date(2026, 11, 25) <= D(r["obs_end"]) for r in N2.values()))
print("H filled physical fields, both pulls", {f: (sum(r[f] is not None for r in S1.values()), sum(r[f] is not None for r in S2.values())) for f in ("diameter", "albedo", "rot_per")})
R1 = {r["des"]: r for r in n1["data"]}; R2 = {r["des"]: r for r in n2["data"]}
print("I identical as written, key order kept", sum(json.dumps(R1[k]) == json.dumps(R2[k]) for k in R1 if k in R2),
      "| added reachable objects already in the table at pull 1", {k: k in S1 for k in sorted(set(N2) - set(N1))},
      "| window start moved 21 -> 27 Nov", sum(N1[k]["obs_start"] == "2026-11-21" and N2[k]["obs_start"] == "2026-11-27" for k in nc),
      "| count types", type(n2["count"]).__name__, type(s2["count"]).__name__)
```

Output on 2026-11-24:

```
A reachable 7229 -> 7231 added ['2026 VQ5', '2026 WV1'] removed []
B near-Earth 43367 -> 43379 added 12 removed 0
C near-Earth rows changed 342 | new orbit_id 342 | on the reachable list 24 | physical values 0 | H 37
D reachable rows changed 222 | identical once keys are sorted 7007 | only obs_start or obs_mag 171 | only window fields 192 | new orbit_id 23 | delta-v 7 | h 4
E pull 1 reachable rows on a different orbit number from the table 16 | orbit ids of an unknown shape (list, table) 21 175
E pull 2 reachable rows on a different orbit number from the table 17 | orbit ids of an unknown shape (list, table) 21 177
F window rule (same window if the new start is not after the old end): same window re-dated 192 | window closed 24
G open at pull 1 212 | ended 1, 2, 3 days later [2, 5, 24] | open at pull 2 by JPL's dates 0
H filled physical fields, both pulls {'diameter': (1266, 1266), 'albedo': (1209, 1209), 'rot_per': (2189, 2189)}
I identical as written, key order kept 0 | added reachable objects already in the table at pull 1 {'2026 VQ5': True, '2026 WV1': False} | window start moved 21 -> 27 Nov 187 | count types str int
```

That neither response carries an ETag or Last-Modified header is from `data/snapshots/2026-11-24/nhats.headers` and `sbdb.headers`, which I read; the first pull has no header files.

The colleague reports count "real" changes on the reachable list three ways (51, 30, and 222 less 199). Line D gives the definitions: 171 rows changed only in window start or brightness, 192 only in the four window fields, and 23 have a new orbit.

### B. The sizing prototype

A 120-line standard-library script, run twice in separate processes with different `PYTHONHASHSEED` values. Not kept; the method is:

1. Compress each raw file with `lzma` and with `gzip`.
2. Load both pulls into a SQLite file as four batches (near-Earth table then reachable list, per pull): one `object` row and one alias per designation, one `source_row` per distinct sorted-key row, with the previous version closed when a row changes; `membership` for the reachable list; the chained `state_hash` of section 3.3.
3. Build edition tables as of the last batch, as sorted-key JSON lines: `object` for every near-Earth object; for each reachable object, fifteen properties from the near-Earth table as `claim` and `check` rows and five from the reachable list as claims; `window`; `field`.
4. Hash each table; gzip it; build twice and compare.
5. Insert the lines into a new SQLite file, `VACUUM`, hash the file; do it twice and compare.

Output:

```
archive nhats.json: raw 2.59 MB | xz 0.29 MB | gzip 0.40 MB
archive sbdb_neo.json: raw 15.79 MB | xz 2.28 MB | gzip 3.08 MB
batch 1 jpl.sbdb_query 2026-11-21: rows 43367 new 43367 changed 0   | 0.4 s | store 48.8 MB
batch 2 jpl.nhats 2026-11-21:      rows 7229  new 7229  changed 0   | 0.0 s | store 52.7 MB
batch 3 jpl.sbdb_query 2026-11-24: rows 43379 new 12    changed 342 | 0.3 s | store 53.1 MB
batch 4 jpl.nhats 2026-11-24:      rows 7231  new 2     changed 222 | 0.0 s | store 53.2 MB
store after 4 batches: 52.9 MB; grew 0.50 MB for the second pull
edition table object: 43379 rows, 4.11 MB, gzip 0.398 MB
edition table population_member: 7231 rows, 0.32 MB, gzip 0.022 MB
edition table claim: 80562 rows, 17.54 MB, gzip 0.733 MB
edition table check: 108465 rows, 13.35 MB, gzip 0.386 MB
edition table window: 7231 rows, 0.96 MB, gzip 0.089 MB
edition table field: 7231 rows, 0.26 MB, gzip 0.077 MB
edition as of batch 4: 36.5 MB, gzip 1.71 MB, built in 1.0 s
state hashes and table hashes identical across the two processes
sqlite pack: 39.2 MB | two packs byte-identical: True
```

Python 3.14.4 and SQLite 3.46.1, the workstation's own; the pipeline itself is to run on a uv-managed 3.12.
