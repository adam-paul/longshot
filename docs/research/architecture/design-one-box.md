# Design: one box

Written 2026-11-24 for the architecture review. Status: **complete**. Limits are in section 17.

The brief: design the data backbone, the part that makes longshot a living system and not a snapshot, and name the first step. The stance I was given: the fewest moving parts that still do that. One machine, one embedded database file, scheduled jobs, raw responses kept on disk. So this file argues for what can be left out, and section 10 says what each omission costs.

Nothing here chooses the app's framework, server language or host. Section 11 says what the app reads. Section 15 lists what only the owner can decide.

Evidence tags:

- **[ran]** my own test today on the two JPL pulls on disk (`data/snapshots/2026-11-21`, `/2026-11-24`). The two scripts in the appendix print every [ran] number. Timings vary by a few tenths of a second between runs.
- **[doc]** a documentation page I read today through a summarising fetch. Quoted words are as the fetch returned them.
- **[colleague]** from one of today's five reports in this folder, not re-checked by me.
- **[judgement]** mine, with no measurement behind it.

No request went to a JPL API endpoint. I made no test request to any other service; the only outside reads were eight documentation pages (Sources).

Terms. The **reachable list** is JPL's NHATS list (7,231 asteroids). The **near-Earth table** is JPL's database of every near-Earth object (43,379). An **orbit solution** is JPL's current fit of an object's path; each new fit gets a new `orbit_id`. A **row version** is one upstream record as it stood between two pulls. A **run** is one ingest event: one execution of the job that attempted at least one request, or the release of one held response. A **hold** is a response that was archived and not ingested. An **edition** is a source's own build date, as opposed to the day we fetched it.

## 1. The design in short

1. **One command on one timer on one machine.** `longshot daily` asks JPL for its two bulk lists (2 requests, 18.4 MB down, 2.6 MB kept), writes each response to disk unchanged, appends one line per request to a journal, and replays the journal into one SQLite file.
2. **Two things are kept forever, and only two:** the raw responses and the journal of every request, including the ones that failed. They are append-only, and they are the only things that need a second copy.
3. **Everything else is built from those two and git, and can be deleted:** the database, every derived number, the data set the app reads. There are no migrations and no database backups. A schema change is "delete the file and replay", which took about one second per archived day today [ran].
4. **So very little has to be right before collecting starts:** what is asked of JPL, that raw bytes are kept even when rejected, and that every attempt leaves a journal line. Table shapes, the ledger's record format and the object key can all be changed later by replaying. This is where I part from the two reviews that want about ten record shapes fixed before any code.
5. **An outage cannot read as "not measured"** because "looked for and absent" exists only where a journal line says a source answered and the answer passed its checks. A failed request leaves a journal line and changes nothing else. Fifteen damaged-response cases produced no false "absent" [ran].
6. **Frozen science rides on two stamps kept apart:** a run number with a hash chain over the raw responses accepted so far, and a git tag for the method. A number shown today is remade by checking out the commit recorded for that run and replaying the journal up to it.

## 2. What I ran today

I built the core of this design as a 200-line standard-library script and replayed the two pulls through it. All rows are [ran].

| Test | Result |
|---|---|
| Replay the 21 November pull as run 1 | 0.98 s. 43,367 objects given keys, 50,596 row versions, file 65.8 MB |
| Replay the 24 November pull as run 2 | 0.72 s. 12 new objects, 578 new row versions, file grew 0.70 MB |
| The diff, read back from the store | Reachable list 7,229 to 7,231: 2026 VQ5 and 2026 WV1 joined, none left. Near-Earth table 43,367 to 43,379: 12 joined, none left. 342 near-Earth rows changed, all 342 with a new `orbit_id`; H changed on 37; no physical field changed; a fitted push value or its error changed on 5 (four asteroids and comet 2P). 222 reachable rows changed: 171 only in window start or brightness, 199 only in window and radar-opportunity fields, 23 with a new `orbit_id`, 7 in delta-v, 4 in H. 17 reachable rows sit on an older orbit than the near-Earth table shows |
| What a 3.4-day gap lost | Of the 341 changed orbits with a numeric id, 259 moved by one solution and 82 by two or more. If JPL numbers solutions consecutively, at least 82 solutions came and went unseen |
| "The reachable list as of run 1" | 7,229 rows in 1 to 2 ms. The same question of the near-Earth table with 94,553 versions stored: about 15 ms |
| Delete the file and rebuild | Identical tables |
| Kill the process (SIGKILL) just before commit, then rerun | The file reopened at run 1 with integrity intact; the rerun equals a clean two-run build |
| 15 single-fault copies of the 24 November pull, replayed as run 3 | 9 held (error body with status 200, truncated body, rows dropped with and without the count adjusted, a column emptied, a field dropped, version string changed, a duplicated row, a reachable designation the table lacks). 1 outage, nothing changed. 2 shuffles (key order, field order) accepted with zero changes. A new field accepted, every row re-versioned. One removal accepted and recorded. **One let through wrongly:** rotation periods multiplied by 60 were accepted as 2,189 changed rows. No case turned any cell into "looked for and absent" |
| A day when every near-Earth row changes | 1.5 s, file grows 54.5 MB |
| Compression of one day's two responses | xz: 2.57 MB in about 4 s. gzip: 3.48 MB in 0.3 s. Raw: 18.4 MB |
| The interpreter the project rules name | uv's CPython 3.12.13 carries SQLite 3.50.4 and `lzma`. Nothing in the spine needs a package |

Two things I learned only by running it:

- **Comets break the obvious alias rule.** A numbered asteroid's full name ends with its old designation in brackets (`433 Eros (A898 PA)`), which links the two names without a request. A comet's ends with its discoverer (`D/1766 G1 (Helfenzrieder)`), and six discoverer names are shared between rows (`SOHO` by six). My first run tied those comets together and crashed on a duplicate key. The bracket is an alias only where `kind` is `an`.
- **The unit-change case needs a guard my prototype lacked.** No physical field changed on any row in 3.4 days, and no row changed without a new `orbit_id`. So "more than a handful of rows changed with the same orbit" is a sharp signal, and section 6 makes it a hold.

## 3. What is kept and what is built

| | Where | Written by | Can it be remade? |
|---|---|---|---|
| Raw responses | `data/raw/` | the collector, once per response, then read-only | No. JPL shows only the current state [colleague, and doc: no past-date parameter] |
| Journal | `data/log/journal-<year>.ndjson` | appended by the job and by the owner's `release` command | No. It is the record of having looked, failures included |
| Forecast log (later) | `data/log/forecast-<year>.ndjson` | appended when a registered method makes or changes a prediction | No |
| Code, registries, method, annotations, resolutions | git | people and agents, by commit | From the remote |
| Database | `data/longshot.db` | `ingest`, from the journal and raw files | Yes, about 1 s per archived day [ran, two days only] |
| Data set the app reads | `data/export/` | `export`, from the database and a method tag | Yes |
| Status file, weekly digest | `data/status.json`, `data/digest/` | `report` | Yes |

What follows from making the database a build product:

- **One backup rule.** Copy `data/raw/` and `data/log/` somewhere else and push git. Nothing else needs protecting.
- **No migrations.** An agent may change a table freely; the test is that a replay still gives the golden numbers.
- **A parser mistake found in 2028 is repairable.** Fix the adapter, rebuild, and the difference between the rebuilt past and what was published at the time is itself a record (the journal holds the hash of each day's published data set).
- **The schema is not a day-one decision.** The decisions that cannot be redone are these four:
  1. What the request asks for. The two pulls on disk did not ask for `spkid`, `soln_date` or `source`, and did not set `full-prec` [colleague]. JPL documents all four [doc]. Ask for them from the first automated pull, and write every parameter out, defaults included.
  2. Raw bytes are kept whether or not the response is accepted.
  3. Every attempt, failed or not, leaves a journal line with its UTC time.
  4. Collecting starts. Each day not collected is gone.

## 4. Files

```
longshot/                                git
  pyproject.toml  uv.lock                the spine lists no third-party package
  src/longshot/
    net.py            the one module that opens a connection: one request at a time, User-Agent, timeouts
    collect.py        registry -> request -> raw file -> journal line
    guards.py         checks on a stored response; returns accepted, or held with a report
    adapters/jpl_sbdb.py  jpl_nhats.py    stored response -> rows (later also -> claims). Never opens a connection
    ingest.py         journal + raw -> longshot.db, one transaction per run
    report.py         status, diff, weekly digest
    cli.py            longshot daily | replay | rebuild | status | diff | release | verify
  registry/sources.toml                  one entry per source (below)
  registry/fields.toml                   per source field: class id | orbit | value | clock; later, the property it maps to
  tests/                                 golden replay, mutations, crash, rebuild, import check
  ops/longshot-daily.service  .timer
data/                                    outside git
  raw/<source>/<year>/<utc>_r<run>_<sha12>.json.xz
  log/journal-<year>.ndjson
  longshot.db
  status.json   digest/<year>-W<week>.md
  export/<run>-m<method>-s<schema>/   export/current        not in the first step
```

- A raw file's name carries its UTC time, run number and the first 12 hex digits of its SHA-256, so the accepted pulls can be listed from file names alone if the journal were lost.
- Raw files are stored by date, not by content hash. JPL returns keys in a different order on every pull, so no two responses are byte-equal and there is nothing to deduplicate [colleague; my shuffle cases agree].
- A raw file is written to a temporary name inside `data/raw/`, synced, renamed, and only then is its journal line appended and synced. The system's temporary folder is never used: this machine clears it on reboot.
- The two pulls on disk are adopted as runs 1 and 2. The first has no header file, so its time is taken from the file timestamp (16:35 UT, 21 November) and marked as inferred.

A journal line, one JSON object each:

```
{"t":"request","run":412,"node":"<hostname>","at":"2026-12-03T10:00:07Z","source":"jpl.sbdb","method":"GET",
 "url":"…","params":{…every parameter…},"status":200,"headers":{…},"bytes":15793225,"sha256":"…","path":"raw/jpl.sbdb/2026/…","outcome":"ok"}
{"t":"verdict","run":412,"source":"jpl.sbdb","sha256":"…","verdict":"accepted","adapter":"jpl_sbdb@1","report":{…counts…}}
{"t":"release","run":415,"source":"jpl.sbdb","sha256":"…","by":"owner","reason":"…"}
{"t":"export","run":412,"code":"<git commit>","method":"0.1","schema":1,"sha256":"…"}
```

`outcome` is `ok`, `http_error`, `timeout` or `refused`. `verdict` is `accepted` or `held`. A rebuild honours the recorded verdicts and does not re-judge old responses, so it is deterministic whatever today's guards say.

A `sources.toml` entry holds: id; kind (`catalog`, `service` or `table`, which decides what absence means, section 7); URL and every parameter; cadence; change signal (`content`, `head` or `body-field`); the upstream version string expected; minimum gap between requests; the age at which a check counts as stale; licence class from `docs/plan.md` Appendix B; the citation sentence. This is the source registry another report asks for [colleague]. It is a file, not a system.

## 5. Tables

Six tables in the first step. This is what the prototype ran, plus the columns it stubbed.

```sql
CREATE TABLE run (                 -- the data-state clock
  run INTEGER PRIMARY KEY, started_at TEXT NOT NULL, code TEXT NOT NULL,   -- git commit
  chain TEXT NOT NULL );           -- sha256(previous chain | "source:body_sha256" of each response accepted in this run)

CREATE TABLE fetch (               -- the journal's request and verdict lines, one row per attempt
  fetch_id INTEGER PRIMARY KEY, run INTEGER NOT NULL, node TEXT, source TEXT NOT NULL,
  method TEXT NOT NULL, request TEXT NOT NULL, request_sha TEXT NOT NULL,   -- URL and every parameter
  scope TEXT NOT NULL,             -- '*' for a bulk list, else the object asked about
  at TEXT NOT NULL, http_status INTEGER, headers TEXT, body_sha256 TEXT, body_bytes INTEGER, raw_path TEXT,
  api_version TEXT, upstream_date TEXT,     -- the source's own stamp, if it has one; JPL's bulk lists have none
  outcome TEXT NOT NULL, verdict TEXT NOT NULL, report TEXT );

CREATE TABLE object (              -- our own key
  key TEXT PRIMARY KEY, first_des TEXT NOT NULL, first_run INTEGER NOT NULL, kind TEXT, merged_into TEXT );

CREATE TABLE alias (               -- every name any source has used, with the runs between which it held
  scheme TEXT NOT NULL,            -- 'des', 'number', 'name', 'spkid', later 'ssodnet'
  value TEXT NOT NULL, key TEXT NOT NULL, source TEXT NOT NULL, first_run INTEGER NOT NULL, closed_run INTEGER );
CREATE UNIQUE INDEX alias_live ON alias(scheme, value) WHERE closed_run IS NULL;

CREATE TABLE source_row (          -- one version of one upstream record, whole
  source TEXT NOT NULL, key TEXT NOT NULL, first_run INTEGER NOT NULL, closed_run INTEGER,
  sha TEXT NOT NULL,               -- of the row as sorted-key JSON, never of raw bytes
  changed TEXT,                    -- JSON list of the fields that differ from the previous version; NULL for the first
  row_json TEXT NOT NULL,          -- every field as received: '10.', '0.00', 'JPL 49', 'Kamo`oalewa'
  PRIMARY KEY (source, key, first_run) ) WITHOUT ROWID;

CREATE TABLE coverage (            -- what was looked at and answered. Written only for an accepted response
  run INTEGER NOT NULL, source TEXT NOT NULL,
  key TEXT NOT NULL DEFAULT '*',   -- '*' = the whole list was read and passed its guards
  outcome TEXT NOT NULL,           -- 'returned', 'unknown_to_source'
  PRIMARY KEY (run, source, key) ) WITHOUT ROWID;
```

Added in week two, when the first non-JPL source arrives. It is filled from `source_row` by the adapters, so it too is rebuilt:

```sql
CREATE TABLE claim (               -- one thing one source says about one property of one object
  claim_id INTEGER PRIMARY KEY, key TEXT NOT NULL, property TEXT NOT NULL, source TEXT NOT NULL,
  value_raw TEXT NOT NULL, unit_raw TEXT, value_num REAL, value_text TEXT,
  bound TEXT NOT NULL,             -- 'value', 'upper_limit', 'lower_limit'
  err_lo REAL, err_hi REAL, err_kind TEXT NOT NULL,     -- 'sigma', 'range', 'none_given', 'zero_as_received'
  qualifier TEXT,                  -- JSON: quality grade, method, force law, class scheme
  origin_ref TEXT, published TEXT, upstream_date TEXT,
  first_run INTEGER NOT NULL, closed_run INTEGER );
-- no UNIQUE(key, property, source): one paper can give two solutions (2009 BD)
```

That record is the one two colleagues specify, and I have nothing to add to it. My point is only that it does not block collecting.

What the six tables replace:

| Proposed elsewhere today | Here |
|---|---|
| `batch`, one per source per accepted ingest | `run`, plus `fetch.verdict`. One clock for all sources |
| `membership` | The live `jpl.nhats` rows. "Reachable as of run N" is a query; the list's parameters are in `fetch.request` |
| `derived`, `derived_input` | The export, rebuilt each run, each derived row naming its inputs. Past exports are remade by replay, not stored |
| A chained hash over canonical rows | A chain over raw response hashes. It does not change when a parser does, and anyone holding the raw files can check it |
| A content-addressed raw store | Files by date; the hash is in the name and the journal |
| `forecast`, `forecast_outcome` as tables of record | Files of record (section 8), loaded into the database for joining |

**The key.** `key` is ten base-32 characters from a hash of the first designation the object was ever seen under (`pk2ykfvaiv` for 2011 AA37). It is opaque, it never changes when JPL renames or numbers the object, and a rebuild mints the same key because the journal fixes what was seen first. A counter would shift every later key if one early alias decision were corrected. All 43,379 objects get a key, comets included, because it is the same single request; only reachable ones are shown.

**Size.** The first pull makes a 65.8 MB file, 60 MB of it row JSON with field names repeated in every row (804 bytes a near-Earth row, 364 a reachable row). After that it grew 0.70 MB in 3.4 days, about 75 MB a year at the measured rate [ran]. ESA's change log puts the median day at about 1.5 times this sample [colleague], so allow 110 MB a year, plus 55 MB for each day the whole catalogue changes. That is about 1 GB after five years if such a day comes twice a year.

## 6. The daily job

One timer, one service, one lock.

```
longshot-daily.timer     OnCalendar=*-*-* 10,22:00:00 UTC    Persistent=true    RandomizedDelaySec=300
longshot-daily.service   Type=oneshot   ExecStart=uv run --frozen longshot daily   EnvironmentFile=<outside the repository>
```

- 10:00 UT should be after JPL has caught up with the previous day's Minor Planet Center circular and before the next one, issued about 12:30 UT [colleague]. The catch-up time is an assumption; the count of reachable rows on an older orbit (17 today) in the first week's status files will test it.
- The 22:00 firing is the retry. It makes a request only for a source with no accepted pull for that UTC date, so a good day costs JPL two requests, not four.
- `Persistent=true` is systemd's catch-up: "useful to catch up on missed runs of the service when the system was powered down" [doc]. `UTC` and a list of hours are valid in the calendar expression [doc].
- The environment file holds the contact address for the User-Agent, the data path, the mirror path and the alert URL. None of them is in the repository.
- "One JPL request at a time" [doc] is met by construction: one process, holding a file lock, making requests in sequence five seconds apart.

Stages, in order. Each is safe to repeat, and a later stage failing cannot undo an earlier one.

| # | Stage | What it does |
|---|---|---|
| 0 | catch up | Ingest any journal run the database lacks. Normally none |
| 1 | collect | For each source due today with no accepted pull for this UTC date: request, raw file, journal line. Near-Earth table first, then the reachable list. One retry after 60 s on a timeout or 5xx; stop on 429 or 503 |
| 2 | mirror | Copy new raw files and the journal to the mirror path. Never delete there |
| 3 | judge and ingest | Run the guards; append the verdict; if accepted, ingest in one transaction |
| 4 | derive | Later: apply the frozen method to objects whose inputs changed. Empty in the first step |
| 5 | export | Later: build, check and publish the data set by one rename. Empty in the first step |
| 6 | report | Write `status.json`; on Mondays the digest; then signal the alert URL: success only if both lists were accepted today, the mirror copy verified and no hold is open |

**The daily work, sized from the measured churn.**

| | Requests a day | Downloaded | Kept |
|---|---|---|---|
| JPL reachable list | 1 | 2.6 MB | 0.29 MB |
| JPL near-Earth table | 1 | 15.8 MB as pulled today; larger with four more fields and full precision, not measured | 2.28 MB |
| Edition watch, from week one (below) | about 10, mostly HEAD | under 0.1 MB | headers in the journal |
| Alert signal | 1 | none | none |
| **Total** | **2 to JPL, about 11 elsewhere** | **18.5 MB** | **2.6 MB a day, 0.94 GB a year** |

In that download, about 100 near-Earth rows and 66 reachable rows differ from yesterday's, of which about 7 reachable rows differ outside the window and radar-opportunity fields; under one object a day joins the list [ran, from one 3.4-day interval]. That is about 170 new row versions and 0.2 MB of database a day. CPU: about 4 s to compress and 1 s to ingest [ran].

**Change detection.** JPL sends no ETag, no Last-Modified and no date in the body, and has no "changed since" filter [doc, colleague]. So both lists are pulled whole and compared here: parse; resolve each designation to our key; write the row as sorted-key JSON; hash it; store a new version only when the hash differs, with the list of changed fields. `fields.toml` then decides what counts as news:

- `clock` fields (window start, end, brightness, flag, and the four radar-opportunity fields) are stored and never reported. They account for 199 of the 222 changed reachable rows.
- `orbit` fields (the elements, epoch, fit statistics) are reported once per object as "new orbit solution", keyed on `orbit_id`.
- `value` fields (H, orbit quality, days tracked, delta-v, the physical fields, the fitted pushes) are the change list.
- A row whose request changed (fields added) is reported as "request changed", not as upstream news.

**Guards**, run on the stored response before anything is ingested:

1. The body parses, has `signature`, `data` and `count`, and has no top-level `message`, `error` or `code`. JPL documents error messages inside HTTP 200 [doc].
2. `signature.version` equals the registry's (`1.3` and `1.0` today). JPL: "You should always check the version field" [doc].
3. `count`, cast to a number, equals the rows received. The reachable list sends it as a string.
4. Every required field is present. A new field is accepted and flagged.
5. No designation appears twice.
6. The row count is within tolerance of the last accepted pull (placeholder: no more than 5 fewer, no more than 2% plus 40 more).
7. The filled count of each physical field has not fallen by more than 3. Today: 2,189 rotation periods, 1,266 diameters.
8. No more than 20 rows changed a physical field, and no more than 1% of rows changed while keeping their `orbit_id`. This is the guard the times-60 case showed was missing.
9. No more than 10% of rows changed at all. A whole-catalogue day is held for a person to look at.
10. Every reachable designation resolves in the near-Earth table; otherwise the reachable list is held until the table is accepted.
11. Warn only: canary values (Eros's period, Bennu on the list), a new shape of `orbit_id`, three days with no change at all.

The tolerances in 6 to 9 are placeholders from one interval. The first month of daily pulls sets them, and then the owner freezes them.

**When things fail.**

| What happens | What is written | What the store shows | Who hears |
|---|---|---|---|
| No answer, timeout, 5xx, 429 | A journal request line with the outcome | Nothing changes. The source's last-checked date ages | The 22:00 firing retries. No success signal; an alert after 36 h |
| The response fails a guard | The raw file, and a `held` verdict with the report | The last accepted data stay live | A failure signal that day |
| The next day's response passes | `accepted`, judged against the last accepted pull | Moves on. The held file stays in `raw/` as evidence | Success |
| The format changed for good | Every day is held, every day is archived | Stale, and says so | Failure daily until the adapter is fixed; then `longshot release` ingests the held pulls oldest first, each as its own run with its real fetch time |
| The machine is off all day | Nothing | A UTC date with no pull, listed in `status.json` | The alert service, after 36 h of silence |
| Killed or rebooted mid-run | Each raw file and journal line is either complete or absent; the transaction rolls back | The next firing catches up | Nobody needs to |

Two rules keep history append-only. A released pull becomes a new run; nothing is ever inserted into the past. And a held pull that a later accepted pull has already superseded is never ingested.

**The edition watch**, added in week one. Physical measurements have no change feed anywhere [colleague]. What exists is file dates on about ten static files (SsODNet's three, the lightcurve database, Pravec's table, MITHNEOS's three, ALCDEF's archive) and a build stamp inside any SsODNet record [colleague]. So the same collector makes about nine HEAD requests and fetches one SsODNet record a day, and records the headers in the journal. A changed date raises a line in the status file. It does not start a crawl: the first re-pull of SsODNet is run by hand, and automated only after it has been done once.

**The alert path** is one outbound request at the end of a good run to a dead-man's-switch address, and a failure variant when a hold is open. One such service takes a plain GET for success and `/fail` for failure [doc]. Which service is the owner's call. I would keep this one outside dependency, because a dead machine cannot report its own death.

## 7. The three states

For one source and one property of one object, as of run N:

1. A live claim exists: **measured** (a value or a limit).
2. Otherwise it depends on the source's kind:
   - `catalog` (JPL's two lists): the last accepted pull at or before N contains the object and the field is empty: **looked for and absent**, dated by that pull. The object is not in the near-Earth table: **not checked**. The reachable list is a query, so not being on it is itself an answer ("not on JPL's list as of this date"), not a gap.
   - `service` (SsODNet, one object at a time): the last `coverage` row for this object says `returned`: **looked for and absent**, dated by the source's edition and by our check. It says `unknown_to_source`, or there is no row: **not checked**.
   - `table` (one paper's table): the object is listed with an explicit blank or "no period found": absent, or a limit. The object is not listed: the source says nothing about it and takes no part.
3. An "absent" older than the source's stale-after age, or from an edition older than the object's first designation, is **not checked**. That is the rule another report derives from SsODNet being 71 days stale and blind to at least 144 reachable asteroids [colleague].

What an entry shows for a property: a measurement or limit if any source has one; the labelled guess only if every `catalog` and `service` source for that property says "absent"; otherwise "not checked", naming the sources and why. This gives the four display states in `DESIGN.md` section 3 from the three stored ones.

Why an outage cannot become "not measured": `coverage` rows are written only inside the transaction that ingests an accepted response. A failed request, an error body, a truncated file and a held response each write a `fetch` row and nothing else, and close no row version. The prototype's `state()` function is this rule for the catalogue case; across the 15 damaged responses no probe cell became "absent" [ran].

## 8. Frozen science on moving data

**Three stamps, never one "release".**

| Stamp | What it is | Changes |
|---|---|---|
| Data state | Run number N and `chain(N)` | Every run |
| Method version | A git tag (`method-0.1`): prior tables, thresholds, mission presets, price scenario, registries, and the code | By hand, at a gate |
| Schema version | The shape of the data set the app reads | When columns change |

The first two carry the science; the third is only the shape of what the app reads. Every data set and every page footer carries `data N (date) · method 0.1`.

- **Applying a frozen method is a pure function** of the database as of run N and the method's files: no network, no clock (dates are arguments), seeds taken from the object key and the method version. It runs every day, so a new object gets its prior from the frozen table the day it appears. Tuning a model never runs unattended. This narrows the plan's "nothing with a model in it runs in the weekly loop", which read strictly would leave new objects blank.
- **Predictions are stored when made.** When the registered method makes or changes a prediction for a question and an object, the run appends a line to `data/log/forecast-<year>.ndjson`: question id, object key, a probability per outcome, method tag, run, chain, a hash of the inputs. That file is kept forever, like the journal. Old predictions stay scorable because they were written down, not because old code still runs [colleague's point, and I agree].
- **A freeze** is one committed file naming the questions, the rule text, the method tag, `chain(N)` and the hash of the forecast log to that point. It is what gets deposited. The chain commits to the data state without publishing any restricted value.
- **Resolutions** are hand-confirmed lines in git: question, object key, outcome, the claim that settled it, and three dates (observed, published, first seen here).
- **A score** is a function of those two files. For each resolution the scorer takes the last forecast line whose run predates the earliest of the three dates, and refuses if there is none.
- **A rule-based forecast** ("any reachable asteroid of H 26 to 28 that gets a class") needs "was it reachable, and what was H, on that date". Both are queries on `source_row` by run.

**Reproducing a number shown on the site a year later:** the page gives the run and the method. The journal's `export` line for that run gives the code commit and the hash of the data set published. Check out the commit, `longshot rebuild --through N` into a scratch file, export with that method, compare hashes.

None of this is built in the first step. The first step supplies the two things it stands on: state as of any run, and the chain.

## 9. A reboot, and an upstream format change

**Reboot.** The timer catches up at next boot. The job is repeatable: it asks "is there an accepted pull for this source for this UTC date?" before any request. Files are renamed into place before their journal line is written. Ingest is one transaction. The SIGKILL test in section 2 is this case.

**Format change.** JPL: "API data formats can change without notice" [doc]. The version strings have not moved since September 2019 and August 2021 [doc] while the content drifts under them [colleague]. What the design does about each kind:

| Drift | Seen already? | Handling |
|---|---|---|
| Key order differs between pulls | Yes | Rows are compared as sorted-key JSON. Shuffle case: zero changes [ran] |
| `count` is a string in one list and a number in the other | Yes | Cast before comparing |
| `orbit_id` written as `49`, `JPL 49`, `E2026-TE5` and more | Yes; 20 objects flipped form in 3.4 days [colleague] | Stored as received. Compared as a number only for the lag count. A new shape is a status line |
| A field added | It will be, by us, on day one | Accepted; every row gets a new version once (54.5 MB); reported as "request changed" |
| A field dropped or renamed, a version string changed, rows missing, a column emptied | No | Held [ran] |
| A unit or precision change | No | Held by guard 8 |
| Every orbit moved to a new common epoch (30,476 rows share one today) | Predicted for late December [colleague, an inference] | Held by guard 8 or 9, released after a look |
| A default changes upstream (the launch-year range did in 2019 [doc]) | Once | Every parameter is sent explicitly: `dv=12`, `dur=450`, `stay=8`, `launch=2020-2045` |

In every case the raw response is archived that day. **A format change costs delay, never data.** The standing cost is that every adapter must go on reading every past form in `raw/`, so each time the request or a parser changes, one pull of the old form is pinned as a test.

## 10. What is left out, and what that costs

| Left out | Proposed in | Why it can wait | What waiting costs | Add it when |
|---|---|---|---|---|
| A second machine or a second scheduler | review-ops | A second firing on the same box covers a failed request. Raw files are mirrored | A day the box is dark is a hole. Measured cost of a 3.4-day hole: at least 82 orbit solutions unseen, and 12 open windows gone [ran, colleague]. Forecasts stay scorable: the last state before an observation is merely older | The host is chosen, or the status file shows more than a hole a fortnight |
| A locked bucket | review-ops | One mirror path gives a second copy | No protection against the owner's own mistake deleting both | Before the first deposit |
| Three separately locked environments | review-ops | The spine has no package to break. A test fails if anything but `net.py` imports a network library | When the method brings in numerical packages, a bad upgrade could stop the daily job | The first third-party package is proposed |
| A per-object JPL call for each changed reachable orbit (7 to 10 a day) | upstream-orbits | Nothing shown in the prototype needs the covariance or the force law | JPL overwrites an orbit when it refits. The covariance and force law of solutions that pass meanwhile are gone. If `full-prec` does not reach the fitted push values, so is their full precision | The density ceilings are built (R2), or sooner if the owner prefers not to lose it |
| ESA's change log as a cross-check; a weekly sweep of the Minor Planet Center's identifier service | upstream-orbits | Guards 8 and 9 catch a broken diff. A vanished row is rare (none in 3.4 days) and is resolved by hand with one request | An object the Minor Planet Center has withdrawn stays on show while JPL lists it (2026 JG2 today [colleague]) | Before a public address |
| Ten record shapes fixed before code | review-extend | Section 3: they can be changed by replay | A rebuild when they change, about a second per archived day | Never as a gate. Before the first freeze the key rule and the claim record should be settled |
| Stored history of derived values | review-data | A past data set is remade from the run and the commit | Minutes of compute to answer "what did we say then" | Rebuilds exceed about ten minutes |
| The literature watch | upstream-physical | arXiv's interface filters by submission date [doc], so past weeks can be searched when the watch starts | New papers are found late. 2026 QQ8's paper of 23 November is the live example [colleague] | Week three |
| A re-crawl of SsODNet on a schedule | review-data | It has not rebuilt in 71 days [colleague]; the watch says when it does | The old build's content for the 5,527 reachable objects whose record was never fetched is gone when it rebuilds | Before the first freeze: one full pull |
| "Open now" for observing windows | plan 5.3 | Two pulls do not show the pattern. The start date rolls with the calendar and across full moon [colleague] | Windows show as dated facts only | Two weeks of daily pulls exist |
| A workflow engine, a queue, an adapter framework, a server database, an interface layer | nobody today | One command and functions do it | Nothing | Not foreseen |

What cannot be left out, and why the design is not smaller: raw files and the journal (history); explicit requests (the launch-range default); sorted-key comparison (key order); our own key and aliases (numbering, comets); `coverage` (the three states); guards with holds (a column emptied upstream would otherwise read as nothing measured); the two stamps (frozen science); one mirror and one alert.

## 11. What the app reads

This is a contract, not a stack. It holds whatever serves the pages.

- **The app reads one thing: the current export.** It never opens `longshot.db`, the raw files or the network, and it never writes to the export.
- **An export is immutable and named by its three stamps:** `<run>-m<method>-s<schema>`. Publishing is one rename of `export/current`, and rolling back is one rename. If the app runs on another machine, publishing is one directory copy followed by the rename there.
- **`manifest.json`** carries: schema, method and run; `chain`; the time it was built; the hash of the contents; and for each source its edition date, last successful check, last change, stale-after age and licence class.
- **Tables**, by meaning:
  - `object`: key, display name, every alias (so an old name redirects), which populations it belongs to.
  - `row`: one per object and property: state (`measured`, `limit`, `prior`, `not_checked`), value as text and as bounds with a unit, the source led with, the original reference, edition date, checked date, and for `not_checked` the reason.
  - `claim`: every statement shown on an entry, after the licence filter.
  - `reach` and `window`: delta-v and trip figures with the orbit solution they were computed on; windows as dated facts with the as-of date.
  - `elimination`, `price`, `observe_next`: per object and preset or scenario, from the method.
  - `field`: one compact payload of redistributable columns for the picture of all asteroids.
  - `change`: dated events (joined, left, new orbit solution, value changed, first measurement), window fields excluded.
  - `record`: forecasts, resolutions, scores.
  - the registries: properties, sources, states, presets, scenarios.
- **Two licence views** come out of one filter: a page view that may show a single cited value, and an open view holding only redistributable values and the project's own products. Any download is served from the open view.
- **The app may** select, sort, filter and count; compare the manifest's dates with the clock to word a freshness banner; apply unit conversions the registry names. **It may not** compute or combine a probability or a range, sum probabilities over a filter, or say "open now" from a table more than two days old [colleague's rule; I adopt it].
- **Staleness is computed when a page is viewed**, from the manifest's dates. It must be true when every job is dead.
- **Visitor state, if there is any, lives in a separate store** that refers to object keys, question ids and run numbers. The pipeline never reads it.

The physical form is the one open point. The export step can write the same tables as one read-only SQLite file or as JSON files. Which one, and whether history views ("as of last March") are queries made on request or tables written ahead, depends on things only the stack conversation settles: whether the server can open a local file; whether pages are made on request; whether the app runs on this box; whether visitors write anything.

## 12. Extension points

- **A new source** is a `sources.toml` entry, one adapter function (stored response in, rows and claims out), and one stored sample with its expected output. A paper's table needs a mapping file, not code.
- **A new property** is a `fields.toml` mapping and a registry row.
- **A source asked one object at a time** (SsODNet) writes one packed raw file per crawl, one line per object, and one `coverage` row per object. The tables already hold it.
- **Per-object JPL detail** is a registry entry triggered by "reachable and `orbit_id` changed", with a daily cap so that a whole-catalogue day cannot start thousands of calls.
- **An identity sweep** through the Minor Planet Center's identifier service (100 designations a request [colleague]) writes aliases and merge records.
- **A second collector on another machine** is possible because journal lines carry `node` and the collector asks the store whether today is covered. It would need the mirror to become the meeting point. Not built.
- **The literature queue**: accepted entries are files in git and enter as a source of kind `table`.
- **An embargo list** of references whose claims are stored and kept out of every derivation until released. It must exist before the first ingest that feeds a prior [colleague].
- **A method release** adds a tag. A new mission type or price scenario is a configuration entry and a minor version.
- **The population** is already every near-Earth object. "Reachable" is one named query.

## 13. The first step

**Build `longshot daily` as far as archive and replay, prove it offline on the two pulls on disk, and start its timer the day the JPL contact address exists.**

It is the six tables, `net.py`, `collect.py`, `guards.py`, the two JPL adapters, `ingest.py`, `status` and `diff`. No package beyond the standard library, pending the owner's yes to SQLite. My estimate is one to two days of agent work; the prototype in the appendix is the core of it.

Done means:

1. `longshot replay data/snapshots` adopts the two pulls as runs 1 and 2 and `longshot diff 1 2` prints the figures in section 2's diff row. Those figures, with the four file hashes, are committed as the golden test.
2. The mutation suite passes: the 15 cases in section 2, with the times-60 case now held, each asserting that no cell becomes "looked for and absent".
3. Deleting the database and rebuilding gives identical tables. Killing the job mid-run and rerunning gives the same file.
4. A test fails if any module but `net.py` imports a network library.
5. The timer is installed and disabled. The day the address exists it is enabled, and the first live day makes three JPL requests, not two: the near-Earth table once in the old form and once with `spkid`, `soln_date`, `source` and `full-prec`, then the reachable list. The old-form pull against the 24 November pull measures the gap; the two forms against each other, minutes apart, show what the new request changes, including whether full precision reaches the fitted push values. Both are known before history accumulates.
6. `status.json` shows two accepted pulls for the day, the mirror copy verified, and the alert service has heard from it.

It deliberately leaves out: claims and properties, any source but JPL's two lists, priors, the export, the app, per-object calls, the edition watch, the digest, forecasts.

**The first two weeks.**

| When | What |
|---|---|
| Day 0, the owner, about an hour | The contact address and product name. Which machine. A mirror target and a git remote (the project is on one disk with no remote today [colleague]). Yes or no to SQLite and to daily in place of weekly |
| Days 1 to 2 | The first step, offline |
| The day the address exists | Timer on. Three requests, then two a day |
| Days 3 to 7 | `registry/fields.toml` with the four classes. The edition watch. The weekly digest. Claims for the dozen JPL properties the ledger shows, and the three states for them |
| Days 8 to 12 | The 1,704 SsODNet records in the research archive, ingested offline as one dated batch, and one paper table through a mapping file. This is the test of the claim record and of "not checked" for the other 5,527 objects |
| Days 12 to 14 | A first export, schema 0, for the ten fixture objects, with its manifest. A rebuild from the mirror copy, not the working disk. Guard tolerances reset from two weeks of real churn |
| Day 14 | The stack conversation, with a live archive and a real export on the table |

## 14. Weaknesses

1. **One machine is one point of failure for history.** If it is the workstation, about one day in eight would have been a hole on the last six weeks' record (five dark days in 41 [colleague]). A hole thins the history; it does not corrupt it. But it cannot be filled.
2. **Correctness rests on replay staying deterministic and affordable.** Every adapter must read every past form forever. Rebuild time grows with the archive: about six minutes per year of daily pulls, extrapolated from two pulls.
3. **Whole rows as JSON are simple and wasteful.** A whole-catalogue day costs 54.5 MB. A question about one field's history parses JSON. Fine at 100,000 versions; I have not tested millions.
4. **The key comes from the first designation seen.** If an early alias decision is later corrected, which of two merged keys survives could change on rebuild. Once anything public or frozen points at keys, merges need a pinned file in git. Two different objects hashing to the same ten characters is about one chance in a million at this size; the build would stop on it, not mis-join.
5. **Holds need a person.** With the owner away for three weeks, a format change means three weeks of archived, un-ingested days and a site that says it is stale. That is the intended failure, and it is still a stale site.
6. **The guard tolerances are placeholders** from one 3.4-day interval. Expect false holds in the first month. My prototype's guards let a unit change through until I added one, which says the list is not yet complete.
7. **Leaving out per-object calls loses data that cannot be fetched later** (section 10). I judged it not needed yet. That judgement is the one most worth overruling.
8. **It does nothing to make physical data faster.** Sizes, spins and classes stay dated, not current. The watch only says when a source has a new edition.
9. **The journal is a home-made convention.** A collector bug in write order could orphan a file. The file names and `longshot verify` are the safety net; a hand-rolled log is still more to get wrong than a database row.
10. **One UTC-day granularity.** A pull at boot can land at any hour, so the lag between JPL's two lists varies between runs.
11. **SQLite takes one writer.** That suits one job. It rules out putting visitor state in the same file, which section 11 forbids anyway.
12. **Nothing here was run against a live service.** The request additions, the response size at full precision and the 10:00 UT timing are untested.

## 15. Decisions needed from the owner

1. **The contact address and product name** for the User-Agent. It blocks the timer and nothing else.
2. **Which machine runs the timer now.** It needs to be on most days, with outbound HTTPS and about 1 GB of disk a year. My advice: start on whichever is on most often today instead of waiting for the host decision; moving later is copying two folders and enabling a timer.
3. **SQLite as the pipeline's working store, and a spine with no third-party packages.** This is the "propose the package list once" step in `AGENTS.md`: the list is empty.
4. **A mirror target** for `data/raw` and `data/log`, and a git remote.
5. **Daily in place of the plan's weekly**, at 10:00 UT with a 22:00 UT retry.
6. **An alert address**: a dead-man's-switch service, or something he already uses.
7. **Our own object key** in place of "JPL's permanent id" (plan Appendix B), and all 43,379 near-Earth objects keyed from day one.
8. **Per-object JPL calls: out for now, or in?** Out loses the covariance and force law of orbits that pass (section 10).
9. **Three JPL requests on the first live day**, to measure what full precision changes.
10. **May the role address subscribe to JPL's announcement list?** It is the only advance notice JPL gives [colleague], and it counts as outside contact under the project's rule.
11. With the stack conversation: the export's physical form, whether the app runs on this box, and whether visitors write anything.

## 16. What this changes in the plan

| Plan | Change |
|---|---|
| Section 4: "A weekly unattended refresh on this workstation that pulls only what changed" | Daily. Both lists pulled whole and compared here. The machine is the owner's choice |
| Section 4: "Nothing with a model in it runs in the weekly loop" | Nothing that tunes a model. The frozen method is applied every day |
| Section 5.3: window tabs read "open now" from stored dates | Dated facts with an as-of date |
| Appendix B, Data: "content-addressed, backed up, with only manifests committed" | Raw files by date; the journal is the manifest and lives with the data; git holds only the golden test's hashes |
| Appendix B, Identity: "The internal key is JPL's permanent id" | Our own key; every upstream name, JPL's included, is a dated alias |
| Appendix B, Ledger cells | Three states computed from claims and `coverage`, with the source's edition date and our check date |
| Appendix B, Release guard: "Staging first, then promote" | Guards at ingest, accept automatically, hold and tell the owner on failure. Staleness worded at viewing time |

## 17. Not verified

- Any live JPL behaviour: that `spkid`, `soln_date`, `source` and `full-prec` return as documented, the response size with them, whether `full-prec` reaches the fitted push values, and when JPL's daily batch finishes.
- The exact request behind the two pulls on disk. It is not recorded beside them, so "the old form" in the first step must come from the research scripts in the archive.
- That JPL numbers orbit solutions consecutively. The "82 unseen" figure assumes it.
- Rebuild speed and database growth are extrapolated from two pulls. The 1.5 times allowance is a colleague's reading of ESA's log.
- The workstation's uptime, the missing backup, ESA's and the Minor Planet Center's behaviour, SsODNet's staleness and the file dates behind the edition watch are colleagues' findings. I did not repeat them.
- systemd's catch-up behaviour is from its manual, not from a test on this machine. User timers here do outlive logout (`Linger=yes`, checked today).
- The prototype handles only JPL's two lists. `claim`, `service` and `table` sources, the export and the forecast log are designed here and not run.
- The effort estimate for the first step is mine.

## Sources

Read today (2026-11-24) through a summarising fetch:

- JPL API fair-use policy: https://ssd-api.jpl.nasa.gov/doc/index.php
- JPL near-Earth table query, fields and `full-prec`, error codes, no past-date parameter: https://ssd-api.jpl.nasa.gov/doc/sbdb_query.html
- JPL reachable-list interface, parameter defaults, version history, response codes: https://ssd-api.jpl.nasa.gov/doc/nhats.html
- systemd timers, `Persistent=`: https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html
- systemd calendar expressions, `UTC` and lists: https://www.freedesktop.org/software/systemd/man/latest/systemd.time.html
- SQLite, where it fits ("SQLite only supports one writer at a time per database file"): https://www.sqlite.org/whentouse.html
- A dead-man's-switch interface, success and `/fail` signals: https://healthchecks.io/docs/http_api/
- arXiv interface, `submittedDate` range filter: https://info.arxiv.org/help/api/user-manual.html

Not read by me today. Each is a colleague's finding from today, with the address their report gives:

- Minor Planet Center daily circular, issued about 12:30 UT (`upstream-orbits.md`): https://www.minorplanetcenter.net/mpec/RecentMPECs.html
- Minor Planet Center identifier service, 100 designations a request (`upstream-orbits.md`, `review-data.md`): https://docs.minorplanetcenter.net/mpc-ops-docs/apis/query-identifier/
- ESA's change log, median 152 objects refitted a day, and its record of 2026 JG2 (`upstream-orbits.md`): https://neo.ssa.esa.int/PSDB-portlet/download?file=updated_nea.lst
- JPL's announcement list (`upstream-orbits.md`, `review-ops.md`): https://ssd.jpl.nasa.gov/email_list.html
- JPL's window rules and full-moon gap (`review-data.md`): https://cneos.jpl.nasa.gov/nhats/obs.html
- SsODNet's build stamp of 14 September and its static files (`upstream-physical.md`): https://ssp.imcce.fr/webservices/ssodnet/api/ssocard/Bennu ; https://ssp.imcce.fr/data/ssoBFT-latest_Asteroid.parquet ; https://ssp.imcce.fr/data/ssodnet_biblio.json ; https://asterm.imcce.fr/public/ssodnet/sso_index.csv.gz
- The other files the edition watch would check (`upstream-physical.md`): https://minplanobs.org/MPInfo/datazips/LCLIST_PUB_CURRENT.zip ; http://space.asu.cas.cz/~ppravec/newres.txt ; http://smass.mit.edu/minus.html ; https://alcdef.org/docs/ALCDEF_ALL.zip
- 2026 QQ8's paper (`upstream-physical.md`): https://arxiv.org/abs/2611.31213
- The workstation's uptime and the absence of a backup or git remote (`review-ops.md`): local logs, no outside source.

Project files: `AGENTS.md`, `DESIGN.md`, `docs/plan.md`.

Local evidence: `data/snapshots/2026-11-21/{nhats,sbdb_neo}.json` (SHA-256 `94cde0355bc48db4…`, `3311f60ef11865da…`) and `data/snapshots/2026-11-24/` (`cb8182a3b6f3c175…`, `b5aaf277a0bb03a2…`).

## Appendix: the two scripts

Standard library only. Both are reproduced here in full; copies are in `onebox/` in `data/backbone-review-2026-11-24.tar.zst`. They write only to the output path given. Save them in one folder outside the repository and run from the repository root:

- `python3 -I onebox.py data/snapshots build/onebox/onebox.db` builds the six tables from the two pulls and prints the diff. It is the seed of the first step.
- `python3 -I checks.py data/snapshots build/onebox` replays the 15 damaged responses as run 3, kills an ingest before commit, and times the rest.

### onebox.py

```python
"""One-box prototype: replay the two JPL pulls on disk into one SQLite file, then report.
Standard library only.  python3 -I onebox.py data/snapshots build/onebox/onebox.db"""
import base64, hashlib, json, os, re, sqlite3, sys, time

PULLS = [("2026-11-21", "2026-11-21T16:35:00Z"), ("2026-11-24", "2026-11-25T01:12:45Z")]
CLOCK = {"obs_start", "obs_end", "obs_mag", "obs_flag", "radar_snr_a", "radar_obs_a", "radar_snr_g", "radar_obs_g"}
VERSION = {"jpl.nhats": "1.3", "jpl.sbdb": "1.0"}
PHYSICAL = ("diameter", "albedo", "rot_per", "spec_B", "spec_T", "A2")
SCHEMA = """
CREATE TABLE run(run INTEGER PRIMARY KEY, started_at TEXT NOT NULL, code TEXT NOT NULL, chain TEXT NOT NULL);
CREATE TABLE fetch(fetch_id INTEGER PRIMARY KEY, run INTEGER NOT NULL, source TEXT NOT NULL, request TEXT NOT NULL,
  scope TEXT NOT NULL, at TEXT NOT NULL, http_status INTEGER, body_sha256 TEXT, body_bytes INTEGER, raw_path TEXT,
  api_version TEXT, outcome TEXT NOT NULL, verdict TEXT NOT NULL, report TEXT);
CREATE TABLE object(key TEXT PRIMARY KEY, first_des TEXT NOT NULL, first_run INTEGER NOT NULL, kind TEXT, merged_into TEXT);
CREATE TABLE alias(scheme TEXT NOT NULL, value TEXT NOT NULL, key TEXT NOT NULL, source TEXT NOT NULL,
  first_run INTEGER NOT NULL, closed_run INTEGER);
CREATE UNIQUE INDEX alias_live ON alias(scheme, value) WHERE closed_run IS NULL;
CREATE TABLE source_row(source TEXT NOT NULL, key TEXT NOT NULL, first_run INTEGER NOT NULL, closed_run INTEGER,
  sha TEXT NOT NULL, changed TEXT, row_json TEXT NOT NULL, PRIMARY KEY(source, key, first_run)) WITHOUT ROWID;
CREATE INDEX source_row_live ON source_row(source, key) WHERE closed_run IS NULL;
CREATE TABLE coverage(run INTEGER NOT NULL, source TEXT NOT NULL, key TEXT NOT NULL DEFAULT '*', outcome TEXT NOT NULL,
  PRIMARY KEY(run, source, key)) WITHOUT ROWID;
"""
canon = lambda o: json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
sha = lambda s: hashlib.sha256(s if isinstance(s, bytes) else s.encode()).hexdigest()
PAREN = re.compile(r"\(([^()]+)\)\s*$")
onum = lambda o: int(o.replace("JPL ", "")) if o and o.replace("JPL ", "").isdigit() else None

def mint(des):  # our own key: opaque, and the same on every rebuild because it comes from the first designation seen
    return base64.b32encode(hashlib.sha256(("longshot-object:" + des).encode()).digest()).decode().lower()[:10]

def flat(r):
    o = {}
    for k, v in r.items():
        if isinstance(v, dict): o.update({k + "." + kk: vv for kk, vv in v.items()})
        else: o[k] = v
    return o

class Hold(Exception): pass

def read(source, body, prev_count, prev_nonnull):
    """Guards. Returns ({designation: row}, version, non-null counts) or raises Hold with the reason."""
    try: doc = json.loads(body)
    except ValueError: raise Hold("not_json")
    if not isinstance(doc, dict) or "data" not in doc or "signature" not in doc:
        raise Hold("error_in_body: keys=%s" % (sorted(doc)[:5] if isinstance(doc, dict) else type(doc).__name__))
    ver = doc["signature"].get("version")
    if ver != VERSION[source]: raise Hold("version %r != %r" % (ver, VERSION[source]))
    if int(doc["count"]) != len(doc["data"]): raise Hold("count %s != rows %d" % (doc["count"], len(doc["data"])))
    rows = {}
    if source == "jpl.sbdb":
        f = doc["fields"]
        for need in ("pdes", "full_name", "orbit_id", "H", "kind"):
            if need not in f: raise Hold("missing field " + need)
        for r in doc["data"]:
            if len(r) != len(f): raise Hold("row width")
            d = dict(zip(f, r)); rows[d["pdes"]] = d
    else:
        for r in doc["data"]:
            for need in ("des", "orbit_id", "min_dv", "h"):
                if need not in r: raise Hold("missing key " + need)
            rows[r["des"]] = flat(r)
    if len(rows) != len(doc["data"]): raise Hold("duplicate designation")
    if prev_count is not None and not (prev_count - 5 <= len(rows) <= prev_count * 1.02 + 40):
        raise Hold("row count %d vs %d" % (len(rows), prev_count))
    nonnull = {}
    if source == "jpl.sbdb":
        for k in PHYSICAL:
            nonnull[k] = sum(d.get(k) is not None for d in rows.values())
            if prev_nonnull and nonnull[k] < prev_nonnull[k] - 3: raise Hold("non-null %s fell %d -> %d" % (k, prev_nonnull[k], nonnull[k]))
    return rows, ver, nonnull

def load_state(con):
    """Everything ingest needs is read back from the file, so a restart needs no memory of the last run."""
    st = {"alias": dict(con.execute("SELECT value, key FROM alias WHERE scheme='des' AND closed_run IS NULL")), "chain": "0" * 64}
    for source in VERSION:
        live = dict(con.execute("SELECT key, sha FROM source_row WHERE source=? AND closed_run IS NULL", (source,)))
        st[source] = {"live": live, "count": len(live) or None, "nonnull": None}
        if source == "jpl.sbdb" and live:
            nn = dict.fromkeys(PHYSICAL, 0)
            for (j,) in con.execute("SELECT row_json FROM source_row WHERE source=? AND closed_run IS NULL", (source,)):
                d = json.loads(j)
                for k in nn: nn[k] += d.get(k) is not None
            st[source]["nonnull"] = nn
    r = con.execute("SELECT chain FROM run ORDER BY run DESC LIMIT 1").fetchone()
    if r: st["chain"] = r[0]
    return st

def ingest(con, run, at, bodies):
    """One run, one transaction. bodies: {source: bytes or None}. A held or missing response changes nothing but `fetch`."""
    st = load_state(con); cur = con.cursor(); stats = {}; accepted = []; amap = st["alias"]
    cur.execute("BEGIN")
    for source in ("jpl.sbdb", "jpl.nhats"):          # sbdb first: every reachable designation must resolve to an object
        body = bodies.get(source)
        if body is None:
            cur.execute("INSERT INTO fetch(run,source,request,scope,at,outcome,verdict) VALUES(?,?,?,?,?,?,?)",
                        (run, source, "GET (not recorded)", "*", at, "timeout", "none")); stats[source] = "no response"; continue
        try:
            rows, ver, nonnull = read(source, body, st[source]["count"], st[source]["nonnull"])
            if source == "jpl.nhats":
                unknown = [d for d in rows if d not in amap]
                if unknown: raise Hold("designation unknown to the near-Earth table: %s" % unknown[:3])
        except Hold as h:
            cur.execute("INSERT INTO fetch(run,source,request,scope,at,http_status,body_sha256,body_bytes,outcome,verdict,report)"
                        " VALUES(?,?,?,?,?,?,?,?,?,?,?)", (run, source, "GET (not recorded)", "*", at, 200, sha(body), len(body), "ok", "held", str(h)))
            stats[source] = "HELD: " + str(h); continue
        cur.execute("INSERT INTO fetch(run,source,request,scope,at,http_status,body_sha256,body_bytes,api_version,outcome,verdict)"
                    " VALUES(?,?,?,?,?,?,?,?,?,?,?)", (run, source, "GET (not recorded)", "*", at, 200, sha(body), len(body), ver, "ok", "accepted"))
        accepted.append(source + ":" + sha(body))
        live = st[source]["live"]; seen = set(); n_new = n_chg = n_real = n_obj = wrote = 0
        for des, d in rows.items():
            key = amap.get(des)
            prov = PAREN.search(d["full_name"] or "") if source == "jpl.sbdb" and d["kind"] == "an" else None  # comets put a discoverer here
            if key is None and prov: key = amap.get(prov.group(1))                 # numbered since we last saw it
            if key is None:
                key = mint(des); n_obj += 1
                cur.execute("INSERT INTO object(key,first_des,first_run,kind) VALUES(?,?,?,?)", (key, des, run, d["kind"]))
            for name in {des} | ({prov.group(1)} if prov else set()):
                if name not in amap:
                    amap[name] = key; cur.execute("INSERT INTO alias(scheme,value,key,source,first_run) VALUES('des',?,?,?,?)", (name, key, source, run))
            c = canon(d); s = sha(c); seen.add(key); old = live.get(key)
            if old == s: continue
            changed = None
            if old is None: n_new += 1
            else:
                (oj,) = cur.execute("SELECT row_json FROM source_row WHERE source=? AND key=? AND closed_run IS NULL", (source, key)).fetchone()
                o = json.loads(oj); changed = sorted(k for k in set(o) | set(d) if o.get(k) != d.get(k))
                cur.execute("UPDATE source_row SET closed_run=? WHERE source=? AND key=? AND closed_run IS NULL", (run, source, key))
                n_chg += 1; n_real += bool(set(changed) - CLOCK)
            cur.execute("INSERT INTO source_row(source,key,first_run,sha,changed,row_json) VALUES(?,?,?,?,?,?)",
                        (source, key, run, s, changed and json.dumps(changed), c)); wrote += len(c); live[key] = s
        gone = [k for k in live if k not in seen]
        cur.executemany("UPDATE source_row SET closed_run=? WHERE source=? AND key=? AND closed_run IS NULL", [(run, source, k) for k in gone])
        cur.execute("INSERT INTO coverage(run,source,key,outcome) VALUES(?,?,'*','returned')", (run, source))
        stats[source] = dict(rows=len(rows), new=n_new, changed=n_chg, changed_outside_clock_fields=n_real, gone=len(gone), new_objects=n_obj, json_bytes=wrote)
    cur.execute("INSERT INTO run VALUES(?,?,?,?)", (run, at, "prototype", sha(st["chain"] + "|" + "|".join(sorted(accepted)))))
    cur.execute("COMMIT")
    return stats

def state(con, des, source, field, run):
    """The three ledger states for one field of one catalogue source, as of a run."""
    k = con.execute("SELECT key FROM alias WHERE scheme='des' AND value=?", (des,)).fetchone()
    r = k and con.execute("SELECT row_json FROM source_row WHERE source=? AND key=? AND first_run<=? AND (closed_run IS NULL OR closed_run>?)",
                          (source, k[0], run, run)).fetchone()
    c = con.execute("SELECT max(run) FROM coverage WHERE source=? AND key='*' AND outcome='returned' AND run<=?", (source, run)).fetchone()[0]
    if not r or c is None: return "not checked"
    v = json.loads(r[0]).get(field)
    return ("measured %s" % v if v is not None else "looked for and absent") + " (as of run %d)" % c

def table_hash(con):
    h = hashlib.sha256()
    for t in ("run", "fetch", "object", "alias", "source_row", "coverage"):
        for row in con.execute("SELECT * FROM %s ORDER BY 1,2,3" % t): h.update(repr(row).encode())
    return h.hexdigest()

def build(snap, db, upto=2):
    if os.path.exists(db): os.remove(db)
    con = sqlite3.connect(db, isolation_level=None); con.executescript(SCHEMA); out = []
    for i, (d, at) in enumerate(PULLS[:upto], 1):
        bodies = {"jpl.nhats": open(f"{snap}/{d}/nhats.json", "rb").read(), "jpl.sbdb": open(f"{snap}/{d}/sbdb_neo.json", "rb").read()}
        t = time.time(); s = ingest(con, i, at, bodies); out.append((i, round(time.time() - t, 2), os.path.getsize(db), s))
    return con, out

def report(con):
    q = lambda s, *a: con.execute(s, a).fetchall()
    for src in ("jpl.nhats", "jpl.sbdb"):
        n1 = q("SELECT count(*) FROM source_row WHERE source=? AND first_run<=1 AND (closed_run IS NULL OR closed_run>1)", src)[0][0]
        n2 = q("SELECT count(*) FROM source_row WHERE source=? AND closed_run IS NULL", src)[0][0]
        joined = [r[0] for r in q("SELECT o.first_des FROM source_row r JOIN object o ON o.key=r.key WHERE r.source=? AND r.first_run=2 AND r.changed IS NULL", src)]
        left = q("SELECT count(*) FROM source_row r WHERE source=? AND closed_run=2 AND NOT EXISTS(SELECT 1 FROM source_row n WHERE n.source=r.source AND n.key=r.key AND n.first_run=2)", src)[0][0]
        print(src, "rows as of run 1:", n1, "| run 2:", n2, "| joined:", joined if len(joined) < 5 else len(joined), "| left:", left)
    ch = [(s, set(json.loads(c))) for s, c in q("SELECT source, changed FROM source_row WHERE first_run=2 AND changed IS NOT NULL")]
    nh = [c for s, c in ch if s == "jpl.nhats"]; sb = [c for s, c in ch if s == "jpl.sbdb"]
    print("near-Earth rows changed:", len(sb), "| with a new orbit_id:", sum("orbit_id" in c for c in sb), "| H:", sum("H" in c for c in sb),
          "| a physical field:", sum(bool(c & {"diameter", "albedo", "rot_per", "spec_B", "spec_T", "GM", "density", "BV", "UB"}) for c in sb),
          "| a fitted push or its error:", sum(bool(c & {"A1", "A2", "A3", "A1_sigma", "A2_sigma", "A3_sigma"}) for c in sb))
    print("reachable rows changed:", len(nh), "| only window start or brightness:", sum(c <= {"obs_start", "obs_mag"} for c in nh),
          "| only window and radar-opportunity fields:", sum(c <= CLOCK for c in nh), "| new orbit_id:", sum("orbit_id" in c for c in nh),
          "| delta-v:", sum("min_dv.dv" in c for c in nh), "| H:", sum("h" in c for c in nh))
    jumps = {"+1": 0, "+2 or more": 0, "not numeric": 0}
    for pj, nj in q("SELECT p.row_json, n.row_json FROM source_row n JOIN source_row p ON p.source=n.source AND p.key=n.key AND p.closed_run=n.first_run"
                    " WHERE n.first_run=2 AND n.source='jpl.sbdb'"):
        a, b = onum(json.loads(pj)["orbit_id"]), onum(json.loads(nj)["orbit_id"])
        jumps["not numeric" if a is None or b is None else "+1" if b - a == 1 else "+2 or more"] += 1
    print("orbit solution number moved by:", jumps)
    lag = sum(1 for nj, sj in q("SELECT n.row_json, s.row_json FROM source_row n JOIN source_row s ON s.key=n.key AND s.source='jpl.sbdb' AND s.closed_run IS NULL"
                                " WHERE n.source='jpl.nhats' AND n.closed_run IS NULL")
              if None not in (onum(json.loads(nj)["orbit_id"]), onum(json.loads(sj)["orbit_id"])) and onum(json.loads(nj)["orbit_id"]) != onum(json.loads(sj)["orbit_id"]))
    print("reachable rows computed on an older orbit than the near-Earth table shows:", lag)
    print("objects:", q("SELECT count(*) FROM object")[0][0], "| aliases:", q("SELECT count(*) FROM alias")[0][0], "| row versions:", q("SELECT count(*) FROM source_row")[0][0])
    for des, f in (("2011 AA37", "rot_per"), ("2022 OB5", "rot_per"), ("101955", "diameter")): print("  state", des, f, "->", state(con, des, "jpl.sbdb", f, 2))

if __name__ == "__main__":
    snap, db = sys.argv[1].rstrip("/"), sys.argv[2]
    con, out = build(snap, db)
    for i, secs, size, s in out:
        print("run", i, "| seconds", secs, "| file bytes", size)
        for k, v in s.items(): print("   ", k, v)
    report(con); h = table_hash(con); con.close()
    con2, _ = build(snap, db + ".again"); print("rebuild from scratch gives identical tables:", table_hash(con2) == h)
```

Output today:

```
run 1 | seconds 0.98 | file bytes 65769472
    jpl.sbdb {'rows': 43367, 'new': 43367, 'changed': 0, 'changed_outside_clock_fields': 0, 'gone': 0, 'new_objects': 43367, 'json_bytes': 34869663}
    jpl.nhats {'rows': 7229, 'new': 7229, 'changed': 0, 'changed_outside_clock_fields': 0, 'gone': 0, 'new_objects': 0, 'json_bytes': 2631219}
run 2 | seconds 0.72 | file bytes 66469888
    jpl.sbdb {'rows': 43379, 'new': 12, 'changed': 342, 'changed_outside_clock_fields': 342, 'gone': 0, 'new_objects': 12, 'json_bytes': 287289}
    jpl.nhats {'rows': 7231, 'new': 2, 'changed': 222, 'changed_outside_clock_fields': 23, 'gone': 0, 'new_objects': 0, 'json_bytes': 84300}
jpl.nhats rows as of run 1: 7229 | run 2: 7231 | joined: ['2026 VQ5', '2026 WV1'] | left: 0
jpl.sbdb rows as of run 1: 43367 | run 2: 43379 | joined: 12 | left: 0
near-Earth rows changed: 342 | with a new orbit_id: 342 | H: 37 | a physical field: 0 | a fitted push or its error: 5
reachable rows changed: 222 | only window start or brightness: 171 | only window and radar-opportunity fields: 199 | new orbit_id: 23 | delta-v: 7 | H: 4
orbit solution number moved by: {'+1': 259, '+2 or more': 82, 'not numeric': 1}
reachable rows computed on an older orbit than the near-Earth table shows: 17
objects: 43379 | aliases: 47253 | row versions: 51174
  state 2011 AA37 rot_per -> measured 10. (as of run 2)
  state 2022 OB5 rot_per -> looked for and absent (as of run 2)
  state 101955 diameter -> measured 0.48444 (as of run 2)
rebuild from scratch gives identical tables: True
```

### checks.py

```python
"""Mutation, crash, size and timing checks against onebox.py (same folder). Standard library only.
python3 -I checks.py data/snapshots build/onebox"""
import gzip, json, lzma, os, random, signal, sqlite3, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); SNAP, OUT = sys.argv[1].rstrip("/"), sys.argv[2].rstrip("/")
exec(compile(open(os.path.join(HERE, "onebox.py")).read().split('if __name__ == "__main__":')[0], "onebox.py", "exec"))
S = SNAP + "/2026-11-24/"; nh, sb = open(S + "nhats.json", "rb").read(), open(S + "sbdb_neo.json", "rb").read()

if len(sys.argv) > 3 and sys.argv[3] == "child":           # ingest run 2 into an existing file; stall before COMMIT if DIE is set
    real = sqlite3.Cursor.execute
    class Cur(sqlite3.Cursor):
        def execute(self, sql, *a):
            if sql == "COMMIT" and os.environ.get("DIE"): print("READY", flush=True); time.sleep(60)
            return real(self, sql, *a)
    con = sqlite3.connect(OUT + "/crash.db", isolation_level=None, factory=type("C", (sqlite3.Connection,), {"cursor": lambda self: Cur(self)}))
    ingest(con, 2, PULLS[1][1], {"jpl.nhats": nh, "jpl.sbdb": sb}); sys.exit(0)

def m(body, fn):
    d = json.loads(body); fn(d); return json.dumps(d).encode()
def col(d, name): return d["fields"].index(name)
def drop40(d): del d["data"][100:140]
def drop1000(d): del d["data"][100:1100]; d["count"] = len(d["data"])
def empty_col(d):
    for r in d["data"]: r[col(d, "rot_per")] = None
def drop_field(d):
    i = col(d, "orbit_id"); d["fields"].pop(i); [r.pop(i) for r in d["data"]]
def ver(d): d["signature"]["version"] = "1.1"
def dup(d): d["data"].append(list(d["data"][5])); d["count"] += 1
def shuffle_keys(d):
    rnd = random.Random(1)
    for i, r in enumerate(d["data"]):
        ks = list(r); rnd.shuffle(ks); d["data"][i] = {k: r[k] for k in ks}
    rnd.shuffle(d["data"])
def reorder_fields(d):
    o = list(range(len(d["fields"]))); random.Random(2).shuffle(o)
    d["fields"] = [d["fields"][i] for i in o]; d["data"] = [[r[i] for i in o] for r in d["data"]]
def new_field(d): d["fields"].append("spkid"); [r.append("20000000") for r in d["data"]]
def times60(d):
    i = col(d, "rot_per")
    for r in d["data"]:
        if r[i] is not None: r[i] = str(float(r[i]) * 60)
def unknown_des(d): d["data"].append(dict(d["data"][0], des="2099 ZZ99")); d["count"] = str(len(d["data"]))
def drop_one(d): d["data"].pop(10); d["count"] = str(len(d["data"]))

CASES = [("outage: no response from either list", {}),
 ("table: HTTP 200 with an error body", {"jpl.sbdb": b'{"message":"internal error","code":"500"}', "jpl.nhats": nh}),
 ("table: truncated body", {"jpl.sbdb": sb[:5_000_000], "jpl.nhats": nh}),
 ("table: 40 rows dropped, count kept", {"jpl.sbdb": m(sb, drop40), "jpl.nhats": nh}),
 ("table: 1,000 rows dropped, count adjusted", {"jpl.sbdb": m(sb, drop1000), "jpl.nhats": nh}),
 ("table: rotation-period column emptied", {"jpl.sbdb": m(sb, empty_col), "jpl.nhats": nh}),
 ("table: orbit_id field dropped", {"jpl.sbdb": m(sb, drop_field), "jpl.nhats": nh}),
 ("table: version string changed", {"jpl.sbdb": m(sb, ver), "jpl.nhats": nh}),
 ("table: one row duplicated", {"jpl.sbdb": m(sb, dup), "jpl.nhats": nh}),
 ("list: key order and row order shuffled", {"jpl.sbdb": sb, "jpl.nhats": m(nh, shuffle_keys)}),
 ("table: field order shuffled", {"jpl.sbdb": m(sb, reorder_fields), "jpl.nhats": nh}),
 ("table: a new field appears", {"jpl.sbdb": m(sb, new_field), "jpl.nhats": nh}),
 ("table: periods multiplied by 60", {"jpl.sbdb": m(sb, times60), "jpl.nhats": nh}),
 ("list: a designation the table does not have", {"jpl.sbdb": sb, "jpl.nhats": m(nh, unknown_des)}),
 ("list: one object removed", {"jpl.sbdb": sb, "jpl.nhats": m(nh, drop_one)})]
PROBE = [(d, f) for d in ("2011 AA37", "2022 OB5", "101955", "2026 QQ8", "2013 NJ", "2010 CW266") for f in ("rot_per", "diameter", "H")]
bad = 0
for name, bodies in CASES:
    con, _ = build(SNAP, OUT + "/mut.db"); size0 = os.path.getsize(OUT + "/mut.db")
    before = {p: state(con, p[0], "jpl.sbdb", p[1], 2).split(" (")[0] for p in PROBE}; v0 = con.execute("SELECT count(*) FROM source_row").fetchone()[0]
    t = time.time(); st = ingest(con, 3, "2026-11-26T10:00:00Z", bodies); secs = time.time() - t
    after = {p: state(con, p[0], "jpl.sbdb", p[1], 3).split(" (")[0] for p in PROBE}; v1 = con.execute("SELECT count(*) FROM source_row").fetchone()[0]
    false_absent = [p for p in PROBE if before[p] != after[p] and after[p].startswith("looked for and absent")]
    short = {s.split(".")[1]: (v if isinstance(v, str) else "accepted, %d new, %d changed, %d gone" % (v["new"], v["changed"], v["gone"])) for s, v in st.items()}
    print("%-44s %s | versions %d -> %d | false 'absent': %d" % (name, short, v0, v1, len(false_absent)))
    if "new field" in name:
        t = time.time(); n = con.execute("SELECT count(*) FROM source_row WHERE source='jpl.sbdb' AND first_run<=2 AND (closed_run IS NULL OR closed_run>2)").fetchone()[0]
        print("   whole-catalogue day: %.1f s, file +%.1f MB | table as of run 2: %d rows in %.0f ms" % (secs, (os.path.getsize(OUT + "/mut.db") - size0) / 1e6, n, (time.time() - t) * 1e3))
    bad += len(false_absent); con.close()
print("false 'absent' over all cases:", bad)
con, _ = build(SNAP, OUT + "/clean.db"); clean = table_hash(con)
t = time.time(); n = con.execute("SELECT count(*) FROM source_row WHERE source='jpl.nhats' AND first_run<=1 AND (closed_run IS NULL OR closed_run>1)").fetchone()[0]
print("reachable list as of run 1: %d rows in %.0f ms" % (n, (time.time() - t) * 1e3)); con.close()
con, _ = build(SNAP, OUT + "/crash.db", upto=1); con.close()
p = subprocess.Popen([sys.executable, "-I", __file__, SNAP, OUT, "child"], stdout=subprocess.PIPE, env=dict(os.environ, DIE="1"), text=True)
assert p.stdout.readline().strip() == "READY"; os.kill(p.pid, signal.SIGKILL); p.wait()
c = sqlite3.connect(OUT + "/crash.db"); print("after SIGKILL before COMMIT: runs", c.execute("SELECT count(*) FROM run").fetchone()[0], "| row versions",
      c.execute("SELECT count(*) FROM source_row").fetchone()[0], "| integrity", c.execute("PRAGMA integrity_check").fetchone()[0]); c.close()
subprocess.run([sys.executable, "-I", __file__, SNAP, OUT, "child"], check=True)
c = sqlite3.connect(OUT + "/crash.db"); print("after rerun: runs", c.execute("SELECT count(*) FROM run").fetchone()[0], "| equals a clean two-run build:", table_hash(c) == clean)
for label, f in (("xz", lambda b: lzma.compress(b, preset=6)), ("gzip", lambda b: gzip.compress(b, 6))):
    t = time.time(); n = len(f(nh)) + len(f(sb)); print("one day's two responses, %s: %.2f MB in %.1f s (raw %.1f MB)" % (label, n / 1e6, time.time() - t, (len(nh) + len(sb)) / 1e6))
```

Output today:

```
outage: no response from either list         {'sbdb': 'no response', 'nhats': 'no response'} | versions 51174 -> 51174 | false 'absent': 0
table: HTTP 200 with an error body           {'sbdb': "HELD: error_in_body: keys=['code', 'message']", 'nhats': 'accepted, 0 new, 0 changed, 0 gone'} | versions 51174 -> 51174 | false 'absent': 0
table: truncated body                        {'sbdb': 'HELD: not_json', 'nhats': 'accepted, 0 new, 0 changed, 0 gone'} | versions 51174 -> 51174 | false 'absent': 0
table: 40 rows dropped, count kept           {'sbdb': 'HELD: count 43379 != rows 43339', 'nhats': 'accepted, 0 new, 0 changed, 0 gone'} | versions 51174 -> 51174 | false 'absent': 0
table: 1,000 rows dropped, count adjusted    {'sbdb': 'HELD: row count 42379 vs 43379', 'nhats': 'accepted, 0 new, 0 changed, 0 gone'} | versions 51174 -> 51174 | false 'absent': 0
table: rotation-period column emptied        {'sbdb': 'HELD: non-null rot_per fell 2189 -> 0', 'nhats': 'accepted, 0 new, 0 changed, 0 gone'} | versions 51174 -> 51174 | false 'absent': 0
table: orbit_id field dropped                {'sbdb': 'HELD: missing field orbit_id', 'nhats': 'accepted, 0 new, 0 changed, 0 gone'} | versions 51174 -> 51174 | false 'absent': 0
table: version string changed                {'sbdb': "HELD: version '1.1' != '1.0'", 'nhats': 'accepted, 0 new, 0 changed, 0 gone'} | versions 51174 -> 51174 | false 'absent': 0
table: one row duplicated                    {'sbdb': 'HELD: duplicate designation', 'nhats': 'accepted, 0 new, 0 changed, 0 gone'} | versions 51174 -> 51174 | false 'absent': 0
list: key order and row order shuffled       {'sbdb': 'accepted, 0 new, 0 changed, 0 gone', 'nhats': 'accepted, 0 new, 0 changed, 0 gone'} | versions 51174 -> 51174 | false 'absent': 0
table: field order shuffled                  {'sbdb': 'accepted, 0 new, 0 changed, 0 gone', 'nhats': 'accepted, 0 new, 0 changed, 0 gone'} | versions 51174 -> 51174 | false 'absent': 0
table: a new field appears                   {'sbdb': 'accepted, 0 new, 43379 changed, 0 gone', 'nhats': 'accepted, 0 new, 0 changed, 0 gone'} | versions 51174 -> 94553 | false 'absent': 0
   whole-catalogue day: 1.5 s, file +54.5 MB | table as of run 2: 43379 rows in 15 ms
table: periods multiplied by 60              {'sbdb': 'accepted, 0 new, 2189 changed, 0 gone', 'nhats': 'accepted, 0 new, 0 changed, 0 gone'} | versions 51174 -> 53363 | false 'absent': 0
list: a designation the table does not have  {'sbdb': 'accepted, 0 new, 0 changed, 0 gone', 'nhats': "HELD: designation unknown to the near-Earth table: ['2099 ZZ99']"} | versions 51174 -> 51174 | false 'absent': 0
list: one object removed                     {'sbdb': 'accepted, 0 new, 0 changed, 0 gone', 'nhats': 'accepted, 0 new, 0 changed, 1 gone'} | versions 51174 -> 51174 | false 'absent': 0
false 'absent' over all cases: 0
reachable list as of run 1: 7229 rows in 1 ms
after SIGKILL before COMMIT: runs 1 | row versions 50596 | integrity ok
after rerun: runs 2 | equals a clean two-run build: True
one day's two responses, xz: 2.57 MB in 3.6 s (raw 18.4 MB)
one day's two responses, gzip: 3.48 MB in 0.3 s (raw 18.4 MB)
```
